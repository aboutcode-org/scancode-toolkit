# runs the trained phrase tagger over license rules and marks the required
# phrases it predicts with {{ }}
# the rules are written in place, so regen the index afterwards
import json
import os
import sys
import unicodedata
from pathlib import Path

import click

# transformers pulls in keras otherwise and blows up on keras 3
os.environ.setdefault('USE_TF', '0')

sys.path.insert(0, str(Path(__file__).parent))

from licensedcode.models import get_rules_by_expression
from licensedcode.required_phrases import add_required_phrase_to_rule
from licensedcode.required_phrases import find_phrase_spans_in_text
from licensedcode.required_phrases import RequiredPhraseRuleCandidate
from licensedcode.required_phrases import validate_and_reindex
from licensedcode.tokenize import get_existing_required_phrase_spans
from licensedcode.tokenize import required_phrase_splitter

from train_model import extract_spans
from train_model import ID2LABEL
from train_model import LABELS
from train_model import MAX_LENGTH
from train_model import MODEL_NAME

# the minima gen-new-required-phrases-rules uses to call a phrase good enough
MIN_TOKENS = 2
MIN_SINGLE_TOKEN_LEN = 5

# scancode leaves rule texts longer than this alone
MAX_RULE_TEXT = 4000


class InferenceConfig:
    """The few settings PhraseTagger reads when it is built

    aux_ce_weight stays 0 so no class weight buffer is created, we are not
    computing a loss here
    """
    aux_ce_weight = 0

    def __init__(self, model_name, use_crf, max_length):
        self.model_name = model_name
        self.use_crf = use_crf
        self.max_length = max_length


def load_model(model, hf_token=None):
    """Tokenizer and tagger with the trained weights, ready to predict

    ``model`` is a local directory or a huggingface repo id
    """
    from safetensors.torch import load_file
    from transformers import AutoTokenizer

    from phrase_model import PhraseTagger

    model_dir = Path(model)
    if not model_dir.is_dir():
        from huggingface_hub import snapshot_download
        model_dir = Path(snapshot_download(repo_id=model, token=hf_token))

    config_file = model_dir / 'train_config.json'
    if config_file.exists():
        saved = json.loads(config_file.read_text())
    else:
        # older runs did not save it, fall back to how we always trained
        click.echo(f'no train_config.json in {model_dir}, using the training defaults')
        saved = {}

    labels = saved.get('labels', LABELS)
    if len(labels) != len(LABELS):
        raise click.ClickException(
            f'this checkpoint has {len(labels)} labels, expected the BIOES {len(LABELS)}'
        )

    config = InferenceConfig(
        model_name=saved.get('model_name', MODEL_NAME),
        use_crf=saved.get('use_crf', True),
        max_length=saved.get('max_length', MAX_LENGTH),
    )
    if not config.use_crf:
        raise click.ClickException('this tool expects the CRF model')

    tokenizer = AutoTokenizer.from_pretrained(str(model_dir), use_fast=True)
    if not tokenizer.is_fast:
        raise click.ClickException('need a fast tokenizer for word_ids, got a slow one')

    tagger = PhraseTagger(config)
    tagger.load_state_dict(load_file(str(model_dir / 'model.safetensors')), strict=True)
    # only needed while training and it warns under no_grad
    tagger.backbone.gradient_checkpointing_disable()
    tagger.eval()

    return tagger, tokenizer, config.max_length


def predict_phrases(tagger, tokenizer, max_length, words):
    """Phrases the tagger predicts for one rule"""
    import torch

    encoding = tokenizer(
        words,
        is_split_into_words=True,
        truncation=True,
        max_length=max_length,
        return_tensors='pt',
    )
    word_ids = encoding.word_ids()

    with torch.no_grad():
        predicted = tagger.predict_words(
            encoding['input_ids'],
            encoding['attention_mask'],
            word_ids,
        )

    tags = [ID2LABEL.get(int(label), 'O') for label in predicted]
    truncated = len(tags) < len(words)
    return phrases_from_tags(tags, words, truncated=truncated), truncated


def words_from_text(text):
    """Words for the model, tokenized the way build_dataset.py does it"""
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = unicodedata.normalize('NFKC', text)
    return required_phrase_splitter(text)


def is_updatable(rule):
    """True if this rule can take new required phrases

    Same checks as get_updatable_rules_by_expression, and also skip rules that
    already have phrases: their {{ }} are tokens too, so they would shift every
    word after them and the tags would not line up with the text
    """
    if rule.is_from_license:
        return False

    if len(rule.text) > MAX_RULE_TEXT:
        return False

    # covers required phrase rules, false positives, tiny texts and more
    if not rule.is_approx_matchable:
        return False

    if rule.skip_for_required_phrase_generation:
        return False

    return not get_existing_required_phrase_spans(rule.text)


def select_rules(license_expression=None):
    """Rules that can take new required phrases, by license expression

    get_updatable_rules_by_expression reloads every rule file each time it is
    called and skips everything when passed None, so load the rules once here
    and do the filtering in memory
    """
    rules_by_expression = get_rules_by_expression()

    if license_expression:
        rules = rules_by_expression.get(license_expression)
        if not rules:
            raise click.ClickException(f'no rules for license expression: {license_expression}')
        rules_by_expression = {license_expression: rules}

    selected = {}
    for expression, rules in rules_by_expression.items():
        updatable = [rule for rule in rules if is_updatable(rule)]
        if updatable:
            selected[expression] = updatable

    return selected


def phrases_from_tags(tags, words, truncated=False):
    """Predicted phrase texts for one rule, longest first

    On a truncated rule we drop a span that runs to the last tag: extract_spans
    closes whatever is still open at the end, so the phrase would be cut short
    """
    phrases = set()
    for start, end in extract_spans(tags):
        if end >= len(words):
            continue
        if truncated and end == len(tags) - 1:
            continue
        phrases.add(' '.join(words[start:end + 1]))

    # longest first, same order required phrases are applied in elsewhere
    return sorted(phrases, key=lambda phrase: (-len(phrase), phrase))


def inject(rule, phrases, counts, dry_run=False, verbose=False):
    """Mark the good phrases in one rule, True if the rule was written"""
    # read the source before the loop, add_required_phrase_to_rule overwrites it
    source = f'{rule.source} ml_model' if rule.source else 'ml_model'
    written = False

    for phrase in phrases:
        candidate = RequiredPhraseRuleCandidate.create(rule.license_expression, phrase)
        if not candidate.is_good(rule, MIN_TOKENS, MIN_SINGLE_TOKEN_LEN):
            counts['rejected'] += 1
            continue

        # the words come from NFKC normalized text but we mark up the raw text,
        # so check the phrase can still be found there
        if not find_phrase_spans_in_text(rule.text, phrase):
            counts['not_found'] += 1
            continue

        updated = add_required_phrase_to_rule(
            rule=rule,
            required_phrase=phrase,
            source=source,
            debug=verbose,
            dry_run=dry_run,
        )
        if updated:
            counts['injected'] += 1
            written = True
        else:
            counts['skipped'] += 1

    return written


def process_rules(
    tagger,
    tokenizer,
    max_length,
    license_expression=None,
    dry_run=False,
    limit=0,
    verbose=False,
):
    """Predict and mark phrases in every eligible rule, return the counts"""
    counts = dict(rules=0, truncated=0, rejected=0, not_found=0, injected=0, skipped=0, written=0)

    selected = select_rules(license_expression=license_expression)
    total = sum(len(rules) for rules in selected.values())
    click.echo(f'tagging {total} rules in {len(selected)} license expressions')

    for expression, rules in selected.items():
        if verbose:
            click.echo(f'{expression}: {len(rules)} rules')

        for rule in rules:
            if limit and counts['rules'] >= limit:
                click.echo(f'stopping at {limit} rules')
                return counts

            counts['rules'] += 1
            words = words_from_text(rule.text)
            if not words:
                continue

            phrases, truncated = predict_phrases(tagger, tokenizer, max_length, words)
            if truncated:
                counts['truncated'] += 1

            if not phrases:
                continue

            if verbose:
                click.echo(f'  {rule.identifier}: {phrases}')

            if inject(rule, phrases, counts, dry_run=dry_run, verbose=verbose):
                counts['written'] += 1

    return counts


@click.command()
@click.option('--model', required=True,
              help='Trained model directory, or a huggingface repo id to download')
@click.option('--license-expression', default=None,
              help='Only tag rules for this license expression, example: apache-2.0')
@click.option('--dry-run', is_flag=True, default=False,
              help='Predict and check phrases but do not save any rule')
@click.option('--limit', default=0, type=int,
              help='Stop after this many rules, 0 does all of them')
@click.option('--validate', is_flag=True, default=False,
              help='Validate all rules and licenses at the end')
@click.option('--reindex', is_flag=True, default=False,
              help='Rebuild and cache the license index at the end')
@click.option('-v', '--verbose', is_flag=True, default=False,
              help='Print the phrases predicted for each rule')
@click.help_option('-h', '--help')
def main(model, license_expression, dry_run, limit, validate, reindex, verbose):
    """Add required phrases to license rules using the trained phrase tagger"""
    tagger, tokenizer, max_length = load_model(model, hf_token=os.environ.get('HF_TOKEN'))

    counts = process_rules(
        tagger=tagger,
        tokenizer=tokenizer,
        max_length=max_length,
        license_expression=license_expression,
        dry_run=dry_run,
        limit=limit,
        verbose=verbose,
    )

    click.echo('')
    click.echo(f"rules processed  : {counts['rules']}")
    click.echo(f"  truncated      : {counts['truncated']}")
    click.echo(f"phrases injected : {counts['injected']}")
    click.echo(f"  rejected       : {counts['rejected']}")
    click.echo(f"  not found      : {counts['not_found']}")
    click.echo(f"  nothing to add : {counts['skipped']}")
    click.echo(f"rules written    : {counts['written']}")

    if dry_run:
        click.echo('dry run, no rules were saved')
    elif counts['written']:
        if validate or reindex:
            validate_and_reindex(validate=validate, reindex=reindex, verbose=verbose)
        if not reindex:
            click.echo('run scancode-reindex-licenses to pick up the new required phrases')


if __name__ == '__main__':
    main()
