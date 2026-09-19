# Run the trained phrase tagger over license rules and mark its predictions.
from dataclasses import dataclass
import json
import os
import sys
import unicodedata
from numbers import Integral
from pathlib import Path

import click

# Avoid importing TensorFlow through Transformers.
os.environ.setdefault("USE_TF", "0")

sys.path.insert(0, str(Path(__file__).parent))

from licensedcode.models import rules_data_dir
from licensedcode.required_phrases import add_required_phrase_to_rule
from licensedcode.required_phrases import find_phrase_spans_in_text
from licensedcode.required_phrases import get_base_rules_by_expression
from licensedcode.required_phrases import RequiredPhraseRuleCandidate
from licensedcode.tokenize import get_existing_required_phrase_spans
from licensedcode.tokenize import required_phrase_splitter

from train_model import extract_spans
from train_model import first_subword_positions
from train_model import ID2LABEL
from train_model import load_final_model


MIN_TOKENS = 2
MIN_SINGLE_TOKEN_LEN = 5
MAX_RULE_TEXT = 4000


@dataclass(frozen=True)
class PhrasePrediction:
    """One predicted required phrase."""

    text: str
    start_word: int
    end_word: int
    confidence: float


@dataclass(frozen=True)
class PredictionResult:
    """Predictions and tokenization details for one rule."""

    words: tuple[str, ...]
    phrases: tuple[PhrasePrediction, ...]
    truncated: bool


def load_model(model, hf_token=None):
    """Load and validate a local or Hugging Face Final_Model."""
    model_dir = Path(model)
    if not model_dir.is_dir():
        from huggingface_hub import snapshot_download

        model_dir = Path(snapshot_download(repo_id=model, token=hf_token))

    tagger, tokenizer = load_final_model(model_dir, offline=True)
    config = json.loads((model_dir / "train_config.json").read_text(encoding="utf-8"))
    return tagger, tokenizer, config["max_length"]


def words_from_text(text):
    """Return words tokenized as they are in the training dataset."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return required_phrase_splitter(unicodedata.normalize("NFKC", text))


def is_updatable(rule):
    """Return True if a rule can receive predicted required phrases."""
    if rule.is_from_license:
        return False
    if len(rule.text) > MAX_RULE_TEXT:
        return False
    if not rule.is_approx_matchable:
        return False
    if rule.skip_for_required_phrase_generation:
        return False
    return not get_existing_required_phrase_spans(rule.text)


def select_rules(license_expression=None):
    """Return eligible rules grouped by license expression."""
    try:
        rules_by_expression = get_base_rules_by_expression(license_expression)
    except KeyError:
        raise click.ClickException(
            f"No rules for license expression: {license_expression}"
        ) from None

    selected = {}
    for expression, rules in rules_by_expression.items():
        updatable = [rule for rule in rules if is_updatable(rule)]
        if updatable:
            selected[expression] = updatable
    return selected


def _word_counts(word_ids):
    counts = {}
    for word_id in word_ids:
        if word_id is not None:
            counts[word_id] = counts.get(word_id, 0) + 1
    return counts


def encode_words(tokenizer, words, max_length):
    """Encode the longest complete-word prefix and report truncation."""
    call = dict(is_split_into_words=True, add_special_tokens=True)
    full = tokenizer(words, truncation=False, **call)
    encoding = tokenizer(words, truncation=True, max_length=max_length, **call)

    full_counts = _word_counts(full.word_ids())
    retained_counts = _word_counts(encoding.word_ids())
    covered_words = max(retained_counts, default=-1) + 1
    complete_words = covered_words

    if covered_words and retained_counts[covered_words - 1] != full_counts[covered_words - 1]:
        complete_words -= 1
        encoding = tokenizer(words[:complete_words], truncation=False, **call)

    if not complete_words:
        raise ValueError("Tokenizer retained no complete words")
    if len(encoding["input_ids"]) > max_length:
        raise ValueError("Complete-word encoding exceeds the model maximum length")

    return encoding, complete_words < len(words)


def span_confidence(crf, word_emissions, tags, mask, free, span):
    """Return the CRF probability mass agreeing with one decoded span."""
    start, end = span
    pinned = word_emissions.clone()
    floor = float(word_emissions.min()) - 10000.0

    for position in range(start, end + 1):
        label = int(tags[0, position])
        keep = float(pinned[0, position, label])
        pinned[0, position] = floor
        pinned[0, position, label] = keep

    constrained = crf(pinned, tags, mask=mask, reduction="none")
    confidence = float((free - constrained).detach().exp())
    return min(max(confidence, 0.0), 1.0)


def predict_rule(tagger, tokenizer, max_length, text):
    """Return phrase predictions for rule text without changing a rule."""
    import torch

    words = words_from_text(text)
    if not words:
        return PredictionResult(words=(), phrases=(), truncated=False)

    encoding, truncated = encode_words(tokenizer, words, max_length)
    word_ids = encoding.word_ids()
    positions = first_subword_positions(word_ids)
    device = next(tagger.parameters()).device
    input_ids = torch.tensor([encoding["input_ids"]], dtype=torch.long, device=device)
    attention_mask = torch.tensor(
        [encoding["attention_mask"]],
        dtype=torch.long,
        device=device,
    )

    with torch.inference_mode():
        emissions = tagger.emissions(input_ids, attention_mask)
        word_emissions = emissions[:, positions].float()
        mask = torch.ones(
            word_emissions.shape[:2],
            dtype=torch.bool,
            device=word_emissions.device,
        )
        decoded = tagger.crf.decode(word_emissions, mask=mask)[0]
        tags = torch.tensor([decoded], device=word_emissions.device)
        free = tagger.crf(word_emissions, tags, mask=mask, reduction="none")
        labels = [ID2LABEL[int(label)] for label in decoded]
        predictions = [
            PhrasePrediction(
                text=" ".join(words[start : end + 1]),
                start_word=start,
                end_word=end,
                confidence=span_confidence(
                    tagger.crf,
                    word_emissions,
                    tags,
                    mask,
                    free,
                    (start, end),
                ),
            )
            for start, end in extract_spans(labels)
        ]

    predictions.sort(key=lambda prediction: (prediction.start_word, prediction.end_word))
    return PredictionResult(
        words=tuple(words),
        phrases=tuple(predictions),
        truncated=truncated,
    )


def phrases_from_tags(tags, words):
    """Return unique predicted phrase texts, longest first."""
    phrases = {
        " ".join(words[start : end + 1])
        for start, end in extract_spans(tags)
    }
    return sorted(phrases, key=lambda phrase: (-len(phrase), phrase))


def predict_phrases(tagger, tokenizer, max_length, words):
    """Return predicted phrases and whether the rule was truncated."""
    if not words:
        return [], False

    import torch

    encoding, truncated = encode_words(tokenizer, words, max_length)
    word_ids = encoding.word_ids()
    input_ids = torch.tensor([encoding["input_ids"]], dtype=torch.long)
    attention_mask = torch.tensor([encoding["attention_mask"]], dtype=torch.long)

    with torch.no_grad():
        predicted = tagger.predict_words(input_ids, attention_mask, word_ids)

    word_count = len(set(word_id for word_id in word_ids if word_id is not None))
    if len(predicted) != word_count:
        raise ValueError("Model returned a different number of labels than encoded words")

    tags = []
    for label in predicted:
        if isinstance(label, bool) or not isinstance(label, Integral) or label not in ID2LABEL:
            raise ValueError(f"Model returned an invalid label ID: {label!r}")
        tags.append(ID2LABEL[int(label)])

    return phrases_from_tags(tags, words), truncated


def new_counts():
    return dict(
        rules=0,
        truncated=0,
        rejected=0,
        not_found=0,
        injected=0,
        skipped=0,
        written=0,
    )


def inject(rule, phrases, counts, dry_run=False, verbose=False):
    """Validate and add predicted phrases, writing the rule at most once."""
    candidates = []
    for phrase in phrases:
        candidate = RequiredPhraseRuleCandidate.create(rule.license_expression, phrase)
        if not candidate.is_good(rule, MIN_TOKENS, MIN_SINGLE_TOKEN_LEN):
            counts["rejected"] += 1
            continue
        if not find_phrase_spans_in_text(rule.text, phrase):
            counts["not_found"] += 1
            continue
        candidates.append(phrase)

    if not candidates:
        return False

    original_text = rule.text
    original_source = rule.source
    source = f"{original_source} ml_model" if original_source else "ml_model"

    for phrase in candidates:
        updated = add_required_phrase_to_rule(
            rule=rule,
            required_phrase=phrase,
            source=source,
            debug=verbose,
            dry_run=True,
        )
        if updated:
            counts["injected"] += 1
        else:
            counts["skipped"] += 1

    if rule.text == original_text:
        return False
    if not dry_run:
        rule.dump(rules_data_dir)
    return True


def process_rules(
    selected,
    tagger,
    tokenizer,
    max_length,
    dry_run=False,
    limit=0,
    verbose=False,
):
    """Predict and mark phrases in selected rules and return run counts."""
    counts = new_counts()
    total = sum(len(rules) for rules in selected.values())
    click.echo(f"Tagging {total} rules in {len(selected)} license expressions")

    for expression, rules in selected.items():
        if verbose:
            click.echo(f"{expression}: {len(rules)} rules")

        for rule in rules:
            if limit and counts["rules"] >= limit:
                click.echo(f"Stopping at {limit} rules")
                return counts

            counts["rules"] += 1
            words = words_from_text(rule.text)
            phrases, truncated = predict_phrases(tagger, tokenizer, max_length, words)
            if truncated:
                counts["truncated"] += 1
            if not phrases:
                continue

            if verbose:
                click.echo(f"  {rule.identifier}: {phrases}")
            if inject(rule, phrases, counts, dry_run=dry_run, verbose=verbose):
                counts["written"] += 1

    return counts


@click.command()
@click.option(
    "--model",
    required=True,
    help="Final model directory or Hugging Face repository.",
)
@click.option(
    "--license-expression",
    help="Only update rules for this license expression.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Predict and validate phrases without saving rules.",
)
@click.option(
    "--limit",
    default=0,
    type=click.IntRange(min=0),
    help="Stop after this many rules; zero processes all rules.",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Print predictions for each rule.",
)
@click.help_option("-h", "--help")
def main(model, license_expression, dry_run, limit, verbose):
    """Add model-predicted required phrases to license rules."""
    selected = select_rules(license_expression=license_expression)
    if not selected:
        click.echo("No eligible rules found")
        return

    tagger, tokenizer, max_length = load_model(
        model,
        hf_token=os.environ.get("HF_TOKEN"),
    )
    counts = process_rules(
        selected=selected,
        tagger=tagger,
        tokenizer=tokenizer,
        max_length=max_length,
        dry_run=dry_run,
        limit=limit,
        verbose=verbose,
    )

    click.echo(f"\nrules processed  : {counts['rules']}")
    click.echo(f"  truncated      : {counts['truncated']}")
    click.echo(f"phrases injected : {counts['injected']}")
    click.echo(f"  rejected       : {counts['rejected']}")
    click.echo(f"  not found      : {counts['not_found']}")
    click.echo(f"  nothing to add : {counts['skipped']}")
    click.echo(f"rules written    : {counts['written']}")

    if dry_run:
        click.echo("Dry run: no rules were saved")
    elif counts["written"]:
        click.echo("Run scancode-reindex-licenses to use the new required phrases")


if __name__ == "__main__":
    main()
