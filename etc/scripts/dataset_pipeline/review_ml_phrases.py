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

from train_model import extract_spans
from train_model import first_subword_positions
from train_model import ID2LABEL

# far enough below the real emission scores to take a label out of the running,
# finite so the forward algorithm never ends up with inf minus inf
PIN_PENALTY = 10000.0

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
