# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

"""Build a BIOES dataset from required phrases marked in license rules."""

from collections import Counter
import hashlib
import json
from pathlib import Path
import unicodedata

import click

from licensedcode.models import load_rules
from licensedcode.models import rules_data_dir as default_rules_data_dir
from licensedcode.required_phrases import get_required_phrase_verbatim
from licensedcode.tokenize import get_existing_required_phrase_spans
from licensedcode.tokenize import required_phrase_splitter


def get_rule_type(rule):
    """Return the first license rule type set on ``rule``."""
    for flag in rule.license_flag_names:
        if getattr(rule, flag):
            return flag
    if rule.is_false_positive:
        return 'is_false_positive'
    return 'unknown'


def tag_tokens(text):
    """Return rule text tokens and their required phrase BIOES labels."""
    tokens = []
    labels = []
    in_phrase = False
    phrase_length = 0

    for token in required_phrase_splitter(text):
        if token == '{{':
            in_phrase = True
            phrase_length = 0
            continue

        if token == '}}':
            if in_phrase and phrase_length:
                labels[-1] = 'S-REQ' if phrase_length == 1 else 'E-REQ'
            in_phrase = False
            phrase_length = 0
            continue

        tokens.append(token)
        if in_phrase:
            labels.append('B-REQ' if phrase_length == 0 else 'I-REQ')
            phrase_length += 1
        else:
            labels.append('O')

    return tokens, labels


def build_record(rule):
    """Return a dataset record for an eligible annotated rule, or None."""
    if (
        rule.is_required_phrase
        or rule.is_false_positive
        or rule.is_license_intro
        or rule.is_license_clue
        or rule.is_deprecated
        or not rule.license_expression
        or not rule.text
    ):
        return

    text = rule.text.replace('\r\n', '\n').replace('\r', '\n')
    text = unicodedata.normalize('NFKC', text)

    # Fail on invalid nested, empty, or dangling required phrase markers.
    get_existing_required_phrase_spans(text)
    if not any(get_required_phrase_verbatim(text)):
        return

    tokens, bioes_labels = tag_tokens(text)
    return {
        'identifier': rule.identifier,
        'license_expression': rule.license_expression or '',
        'rule_type': get_rule_type(rule),
        'text': text.replace('{{', '').replace('}}', ''),
        'tokens': tokens,
        'bioes_labels': bioes_labels,
    }


def split_records(records, common_expression_threshold=50):
    """
    Return train, validation, and test records using a hybrid split.

    Keep rare license expressions in one split. Distribute records from common
    expressions by identifier so each split represents their varied rule text.
    """
    expression_counts = Counter(
        record['license_expression']
        for record in records
    )
    common_expressions = {
        expression
        for expression, count in expression_counts.items()
        if count >= common_expression_threshold
    }

    rare_expressions = sorted(
        (
            expression
            for expression in expression_counts
            if expression not in common_expressions
        ),
        key=lambda expression: (-expression_counts[expression], expression),
    )
    rare_record_count = sum(
        expression_counts[expression]
        for expression in rare_expressions
    )
    targets = {
        'train': 0.8 * rare_record_count,
        'val': 0.1 * rare_record_count,
        'test': 0.1 * rare_record_count,
    }
    assigned_counts = {name: 0 for name in targets}
    rare_assignments = {}

    for expression in rare_expressions:
        split = min(
            targets,
            key=lambda name: assigned_counts[name] / targets[name],
        )
        rare_assignments[expression] = split
        assigned_counts[split] += expression_counts[expression]

    splits = {name: [] for name in targets}
    for record in records:
        expression = record['license_expression']
        if expression in common_expressions:
            identifier = record['identifier'].encode('utf-8')
            bucket = int(hashlib.md5(identifier).hexdigest(), 16) % 100
            if bucket < 80:
                split = 'train'
            elif bucket < 90:
                split = 'val'
            else:
                split = 'test'
        else:
            split = rare_assignments[expression]

        splits[split].append(record)

    return splits


@click.command()
@click.option(
    '--rules-dir',
    type=click.Path(exists=True, file_okay=False),
    default=None,
    help='Path to rules directory (defaults to the ScanCode rules directory).',
)
@click.option(
    '--output-dir',
    type=click.Path(file_okay=False),
    default='dataset-output',
    help='Output directory for train, validation, and test JSONL files.',
)
def main(rules_dir, output_dir):
    """Extract marked required phrases into a BIOES training dataset."""
    rules_path = Path(rules_dir or default_rules_data_dir)
    rule_files = sorted(rules_path.glob('*.RULE'))
    records = []

    click.echo(f'scanning rules from: {rules_path}')
    for rule in load_rules(rules_data_dir=str(rules_path)):
        record = build_record(rule)
        if record:
            records.append(record)

    splits = split_records(records)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for split_name, records_in_split in splits.items():
        split_file = output_path / f'{split_name}.jsonl'
        with split_file.open('w', encoding='utf-8') as output:
            for record in records_in_split:
                output.write(json.dumps(record, ensure_ascii=False) + '\n')

    click.echo('\ndone')
    click.echo(f'  rules scanned: {len(rule_files)}')
    click.echo(f'  annotated: {len(records)}')
    click.echo(
        f'  train: {len(splits["train"])}  '
        f'val: {len(splits["val"])}  '
        f'test: {len(splits["test"])}'
    )
    click.echo(f'  output: {output_path}')


if __name__ == '__main__':
    main()
