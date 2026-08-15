# review the required phrases the tagger predicts before they touch a rule
# predict scores every phrase and files it, review walks the uncertain ones past
# a maintainer, apply injects what came back accepted
# a wrong required phrase silently drops a real license detection, so nothing is
# written on the model's word alone
import json
import os
import tempfile

import click

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
