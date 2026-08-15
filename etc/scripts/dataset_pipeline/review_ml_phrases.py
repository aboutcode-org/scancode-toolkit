# review the required phrases the tagger predicts before they touch a rule
# predict scores every phrase and files it, review walks the uncertain ones past
# a maintainer, apply injects what came back accepted
# a wrong required phrase silently drops a real license detection, so nothing is
# written on the model's word alone
import json
import os
import sys
import tempfile
from pathlib import Path

import click

# transformers pulls in keras otherwise and blows up on keras 3
os.environ.setdefault('USE_TF', '0')

sys.path.insert(0, str(Path(__file__).parent))

from licensedcode.required_phrases import find_phrase_spans_in_text
from licensedcode.required_phrases import RequiredPhraseRuleCandidate

from add_ml_phrases import load_model
from add_ml_phrases import MIN_SINGLE_TOKEN_LEN
from add_ml_phrases import MIN_TOKENS
from add_ml_phrases import select_rules
from add_ml_phrases import words_from_text
from train_model import extract_spans
from train_model import first_subword_positions
from train_model import ID2LABEL

# far enough below the real emission scores to take a label out of the running,
# finite so the forward algorithm never ends up with inf minus inf
PIN_PENALTY = 10000.0

HISTOGRAM_BINS = 20

# tiers a phrase can land in, and the decision each one starts life with
AUTO = 'auto'
REVIEW = 'review'
LOW = 'low'

PENDING = 'pending'
APPROVED = 'approved'
REJECTED = 'rejected'
DROPPED = 'dropped'

# what a record and a phrase entry must carry, checked when reading a file that
# may have been hand edited
RECORD_KEYS = ('identifier', 'license_expression', 'truncated', 'phrases')
PHRASE_KEYS = ('text', 'predicted_text', 'confidence', 'tier', 'decision')


def phrase_sort_key(phrase):
    """Longest first, the order required phrases are applied in elsewhere"""
    return -len(phrase), phrase


def new_phrase(text, confidence, tier, decision):
    """A phrase entry, built here so every record shares one key order

    predict appends records and review rewrites them, and json keeps the order
    it read, so setting it once here is enough to keep the two in step
    """
    return {
        'text': text,
        'predicted_text': text,
        'confidence': confidence,
        'tier': tier,
        'decision': decision,
    }


def new_record(rule, phrases, truncated):
    """One rule's worth of predictions"""
    return {
        'identifier': rule.identifier,
        'license_expression': rule.license_expression,
        'truncated': truncated,
        'phrases': sorted(phrases, key=lambda phrase: phrase_sort_key(phrase['text'])),
    }


def check_keys(record, number, path):
    """Complain about the line at fault rather than dying somewhere later"""
    for key in RECORD_KEYS:
        if key not in record:
            raise click.ClickException(f'{path} line {number}: no {key!r}')

    for phrase in record['phrases']:
        for key in PHRASE_KEYS:
            if key not in phrase:
                raise click.ClickException(f'{path} line {number}: phrase has no {key!r}')


def read_review_file(path):
    """Records from a review file"""
    records = []

    with open(path, encoding='utf-8') as lines:
        for number, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            try:
                record = json.loads(line)
            except ValueError as e:
                raise click.ClickException(f'{path} line {number}: {e}')

            check_keys(record, number, path)
            records.append(record)

    return records


def write_review_record(handle, record):
    """One record, one line"""
    handle.write(json.dumps(record) + '\n')


def write_review_file(path, records):
    """Replace the review file with these records

    Written to a temporary file next to it and moved into place, so a decision
    already recorded survives a crash mid rewrite
    """
    handle = tempfile.NamedTemporaryFile(
        mode='w',
        encoding='utf-8',
        dir=os.path.dirname(os.path.abspath(path)),
        suffix='.tmp',
        delete=False,
    )
    try:
        with handle:
            for record in records:
                write_review_record(handle, record)
        os.replace(handle.name, path)
    except Exception:
        os.unlink(handle.name)
        raise


def span_confidence(crf, word_emissions, tags, mask, free, span):
    """How sure the CRF is that this span is tagged the way it decoded it

    Viterbi hands back one best path and no scores, so score that path twice:
    once as it stands, once with every label but the decoded one pinned out of
    reach at the span's words. The path score is the same in both and cancels,
    which leaves log Z(pinned) - log Z(free), the share of the probability mass
    held by every path that tags this span this way
    """
    start, end = span
    pinned = word_emissions.clone()
    floor = float(word_emissions.min()) - PIN_PENALTY

    for position in range(start, end + 1):
        label = int(tags[0, position])
        keep = float(pinned[0, position, label])
        pinned[0, position] = floor
        pinned[0, position, label] = keep

    constrained = crf(pinned, tags, mask=mask, reduction='none')
    # detached because the crf parameters carry grad and we only want the number
    confidence = float((free - constrained).detach().exp())
    return min(max(confidence, 0.0), 1.0)


def tag_and_score(tagger, tokenizer, max_length, words):
    """The phrases the tagger predicts for one rule, each with a confidence

    This repeats what add_ml_phrases.predict_phrases does, because that returns
    the phrase texts only and PhraseTagger.predict_words offers no way to get
    the emissions back out. Calling either as well would mean running the
    backbone a second time for every rule
    """
    import torch

    encoding = tokenizer(
        words,
        is_split_into_words=True,
        truncation=True,
        max_length=max_length,
        return_tensors='pt',
    )
    positions = first_subword_positions(encoding.word_ids())
    # nothing to tag, so leave the backbone alone
    if not positions:
        return [], False

    with torch.no_grad():
        emissions = tagger.emissions(encoding['input_ids'], encoding['attention_mask'])
        word_emissions = emissions[:, positions]
        mask = torch.ones(
            word_emissions.shape[:2],
            dtype=torch.bool,
            device=emissions.device,
        )
        decoded = tagger.crf.decode(word_emissions, mask=mask)[0]
        tags = torch.tensor([decoded], device=emissions.device)
        # the same for every span of this rule, so pay for it once
        free = tagger.crf(word_emissions, tags, mask=mask, reduction='none')

        labels = [ID2LABEL.get(int(label), 'O') for label in decoded]
        truncated = len(labels) < len(words)

        # two spans can give the same text, keep the one we are surest of
        confidences = {}
        for start, end in extract_spans(labels):
            # extract_spans closes whatever is still open at the end, so on a
            # truncated rule that last span is a phrase cut in half
            if truncated and end == len(labels) - 1:
                continue

            text = ' '.join(words[start:end + 1])
            confidence = span_confidence(
                tagger.crf, word_emissions, tags, mask, free, (start, end),
            )
            if confidence > confidences.get(text, 0.0):
                confidences[text] = confidence

    return list(confidences.items()), truncated


def new_predict_counts():
    """What a predict run tallies

    add_ml_phrases.new_counts is the injection tally and half of it means
    nothing here, apply reuses that one instead
    """
    return dict(rules=0, truncated=0, rejected=0, not_found=0, auto=0, review=0, low=0)


def check_thresholds(auto_threshold, review_threshold):
    """Both in range and the right way round, before anything expensive starts"""
    for name, value in (
        ('--auto-threshold', auto_threshold),
        ('--review-threshold', review_threshold),
    ):
        if not 0.0 <= value <= 1.0:
            raise click.ClickException(f'{name} is {value}, it must be between 0 and 1')

    if review_threshold > auto_threshold:
        raise click.ClickException(
            f'--review-threshold {review_threshold} is above '
            f'--auto-threshold {auto_threshold}, nothing would ever be reviewed'
        )


def tier_for(confidence, auto_threshold, review_threshold):
    """The tier a confidence lands in and the decision it starts with"""
    if confidence >= auto_threshold:
        return AUTO, AUTO
    if confidence >= review_threshold:
        return REVIEW, PENDING
    return LOW, DROPPED


def is_injectable(rule, phrase, counts):
    """True if scancode would take this phrase, counting the ones it would not

    is_good goes first because find_phrase_spans_in_text reads the first token
    of the normalized phrase and raises when there is none
    """
    candidate = RequiredPhraseRuleCandidate.create(rule.license_expression, phrase)
    if not candidate.is_good(rule, MIN_TOKENS, MIN_SINGLE_TOKEN_LEN):
        counts['rejected'] += 1
        return False

    # the words came from NFKC normalized text but the markers go into the raw
    # text, so check the phrase can still be found there
    if not find_phrase_spans_in_text(rule.text, phrase):
        counts['not_found'] += 1
        return False

    return True


def print_histogram(confidences):
    """Where the confidences actually fell

    The thresholds are guesses until someone looks at this
    """
    counted = [0] * HISTOGRAM_BINS
    for confidence in confidences:
        counted[min(int(confidence * HISTOGRAM_BINS), HISTOGRAM_BINS - 1)] += 1

    width = 1.0 / HISTOGRAM_BINS
    click.echo('\nconfidence spread')
    for index, count in enumerate(counted):
        low = index * width
        click.echo(f'  {low:.2f} - {low + width:.2f} : {count}')


@click.group()
@click.help_option('-h', '--help')
def cli():
    """Review the required phrases the phrase tagger predicts, then inject them"""


@cli.command()
@click.option('--model', required=True,
              help='Trained model directory, or a huggingface repo id to download')
@click.option('--review-file', required=True, type=click.Path(dir_okay=False),
              help='Where to write the predictions, must not exist yet')
@click.option('--license-expression', default=None,
              help='Only tag rules for this license expression, example: apache-2.0')
@click.option('--auto-threshold', default=0.95, show_default=True, type=float,
              help='Confidence at or above which a phrase skips review, provisional')
@click.option('--review-threshold', default=0.60, show_default=True, type=float,
              help='Confidence below which a phrase is dropped, provisional')
@click.option('--limit', default=0, type=int,
              help='Stop after this many rules, 0 does all of them')
@click.option('-v', '--verbose', is_flag=True, default=False,
              help='Print the phrases predicted for each rule')
@click.help_option('-h', '--help')
def predict(model, review_file, license_expression, auto_threshold, review_threshold,
            limit, verbose):
    """Predict required phrases and file them for review

    The confidence is how much of its own probability mass the model puts on a
    span, not proof the phrase is right. is_good and the review pass are what
    keep a bad phrase out of a rule. Both thresholds are starting points until
    the confidences of the final checkpoint have been looked at
    """
    check_thresholds(auto_threshold, review_threshold)
    if os.path.exists(review_file):
        raise click.ClickException(
            f'{review_file} exists already, move or delete it: predict appends a '
            f'record per rule and a second run would double them up'
        )

    try:
        tagger, tokenizer, max_length = load_model(model, hf_token=os.environ.get('HF_TOKEN'))
    except ImportError as e:
        raise click.ClickException(f'{e}, install etc/requirements-ml.txt')

    selected = select_rules(license_expression=license_expression)
    rules = [rule for expression in selected.values() for rule in expression]
    click.echo(f'tagging {len(rules)} rules in {len(selected)} license expressions')
    if limit:
        rules = rules[:limit]

    counts = new_predict_counts()
    confidences = []

    # written as we go, a full pass takes hours and a crash should not cost all of it
    with open(review_file, 'w', encoding='utf-8') as out:
        for rule in rules:
            counts['rules'] += 1
            words = words_from_text(rule.text)
            scored, truncated = tag_and_score(tagger, tokenizer, max_length, words)
            if truncated:
                counts['truncated'] += 1

            phrases = []
            for text, confidence in scored:
                if not is_injectable(rule, text, counts):
                    continue

                tier, decision = tier_for(confidence, auto_threshold, review_threshold)
                counts[tier] += 1
                confidences.append(confidence)
                phrases.append(new_phrase(text, round(confidence, 4), tier, decision))

            if not phrases:
                continue

            if verbose:
                click.echo(f'  {rule.identifier}: {[phrase["text"] for phrase in phrases]}')

            write_review_record(out, new_record(rule, phrases, truncated))

    click.echo(f"\nrules processed  : {counts['rules']}")
    click.echo(f"  truncated      : {counts['truncated']}")
    click.echo(f"phrases filed    : {counts[AUTO] + counts[REVIEW] + counts[LOW]}")
    click.echo(f"  auto           : {counts[AUTO]}")
    click.echo(f"  review         : {counts[REVIEW]}")
    click.echo(f"  low            : {counts[LOW]}")
    click.echo(f"  rejected       : {counts['rejected']}")
    click.echo(f"  not found      : {counts['not_found']}")
    click.echo(f'\nreview file      : {review_file}')

    if confidences:
        print_histogram(confidences)


if __name__ == '__main__':
    cli()
