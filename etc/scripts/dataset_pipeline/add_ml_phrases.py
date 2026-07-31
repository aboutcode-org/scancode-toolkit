# runs the trained phrase tagger over license rules and marks the required
# phrases it predicts with {{ }}
# the rules are written in place, so regen the index afterwards
import sys
import unicodedata
from pathlib import Path

import click

sys.path.insert(0, str(Path(__file__).parent))

from licensedcode.models import get_rules_by_expression
from licensedcode.required_phrases import add_required_phrase_to_rule
from licensedcode.required_phrases import find_phrase_spans_in_text
from licensedcode.required_phrases import RequiredPhraseRuleCandidate
from licensedcode.tokenize import get_existing_required_phrase_spans
from licensedcode.tokenize import required_phrase_splitter

from train_model import extract_spans

# the minima gen-new-required-phrases-rules uses to call a phrase good enough
MIN_TOKENS = 2
MIN_SINGLE_TOKEN_LEN = 5

# scancode leaves rule texts longer than this alone
MAX_RULE_TEXT = 4000


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
