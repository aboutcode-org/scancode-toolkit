# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import json

from click.testing import CliRunner
import pytest

from licensedcode.models import InvalidRule
from licensedcode.models import Rule
from licensedcode.tokenize import InvalidRuleRequiredPhrase

from etc.scripts.dataset_pipeline.build_dataset import build_record
from etc.scripts.dataset_pipeline.build_dataset import main
from etc.scripts.dataset_pipeline.build_dataset import split_records
from etc.scripts.dataset_pipeline.build_dataset import tag_tokens


def make_rule(
    identifier='mit_test.RULE',
    license_expression='mit',
    text='Licensed under the {{MIT License}}.',
    **kwargs,
):
    is_license_notice = kwargs.pop('is_license_notice', True)
    return Rule(
        identifier=identifier,
        license_expression=license_expression,
        text=text,
        is_license_notice=is_license_notice,
        **kwargs,
    )


def test_tag_tokens_assigns_bioes_labels():
    tokens, labels = tag_tokens(
        'Use {{MIT}} or the {{Apache License Version}} terms.'
    )

    assert tokens == [
        'Use', 'MIT', 'or', 'the', 'Apache', 'License', 'Version', 'terms'
    ]
    assert labels == [
        'O', 'S-REQ', 'O', 'O', 'B-REQ', 'I-REQ', 'E-REQ', 'O'
    ]


def test_build_record_returns_normalized_rule_data():
    rule = make_rule(text='Licensed under the {{ＭＩＴ License}}.\rTerms')

    record = build_record(rule)

    assert record == {
        'identifier': 'mit_test.RULE',
        'license_expression': 'mit',
        'rule_type': 'is_license_notice',
        'text': 'Licensed under the MIT License.\nTerms',
        'tokens': ['Licensed', 'under', 'the', 'MIT', 'License', 'Terms'],
        'bioes_labels': ['O', 'O', 'O', 'B-REQ', 'E-REQ', 'O'],
    }


def test_build_record_skips_unannotated_rules_and_rejects_invalid_markers():
    assert build_record(make_rule(text='Licensed under the MIT License.')) is None
    assert build_record(make_rule(text='')) is None
    assert build_record(make_rule(is_required_phrase=True)) is None

    invalid_texts = (
        'Empty {{}} marker',
        'Opening {{dangling marker',
        'Closing dangling}} marker',
        'Valid {{MIT}} and {{dangling',
    )
    for text in invalid_texts:
        with pytest.raises(InvalidRuleRequiredPhrase):
            build_record(make_rule(text=text))


@pytest.mark.parametrize(
    'rule',
    [
        make_rule(
            license_expression=None,
            is_license_notice=False,
            is_false_positive=True,
        ),
        make_rule(is_license_notice=False, is_license_intro=True),
        make_rule(is_license_notice=False, is_license_clue=True),
        make_rule(is_deprecated=True),
    ],
)
def test_build_record_skips_rules_that_are_not_training_targets(rule):
    assert build_record(rule) is None


def test_split_records_uses_the_hybrid_split_deterministically():
    records = [
        {
            'identifier': f'common_{index}.RULE',
            'license_expression': 'common',
        }
        for index in range(50)
    ]
    for expression in ('rare-a', 'rare-b', 'rare-c'):
        records.extend(
            {
                'identifier': f'{expression}_{index}.RULE',
                'license_expression': expression,
            }
            for index in range(5)
        )

    splits = split_records(records)

    assert splits == split_records(records)
    assert sum(len(split) for split in splits.values()) == len(records)
    split_by_identifier = {
        record['identifier']: name
        for name, split in splits.items()
        for record in split
    }
    assert split_by_identifier['common_20.RULE'] == 'train'
    assert split_by_identifier['common_43.RULE'] == 'val'
    assert split_by_identifier['common_3.RULE'] == 'test'
    assert split_by_identifier['rare-a_0.RULE'] == 'train'
    assert split_by_identifier['rare-b_0.RULE'] == 'val'
    assert split_by_identifier['rare-c_0.RULE'] == 'test'

    for expression in ('rare-a', 'rare-b', 'rare-c'):
        containing_splits = [
            name
            for name, split in splits.items()
            if any(record['license_expression'] == expression for record in split)
        ]
        assert len(containing_splits) == 1


def test_main_writes_the_complete_dataset(tmp_path):
    rules_dir = tmp_path / 'rules'
    output_dir = tmp_path / 'dataset'
    rules_dir.mkdir()

    rules = [
        make_rule(
            identifier='mit_test.RULE',
            license_expression='mit',
            text='Licensed under the {{MIT License}}.',
        ),
        make_rule(
            identifier='apache_test.RULE',
            license_expression='apache-2.0',
            text='Licensed under the {{Apache License}}.',
        ),
        make_rule(
            identifier='bsd_test.RULE',
            license_expression='bsd-new',
            text='Licensed under the {{BSD License}}.',
        ),
        make_rule(
            identifier='unmarked_test.RULE',
            text='Licensed under the MIT License.',
        ),
        make_rule(
            identifier='required_phrase_test.RULE',
            text='MIT License',
            is_required_phrase=True,
        ),
    ]
    for rule in rules:
        rule.dump(str(rules_dir))

    result = CliRunner().invoke(
        main,
        ['--rules-dir', str(rules_dir), '--output-dir', str(output_dir)],
    )

    assert result.exit_code == 0, result.output
    split_files = sorted(path.name for path in output_dir.glob('*.jsonl'))
    assert split_files == ['test.jsonl', 'train.jsonl', 'val.jsonl']

    records = []
    for split_file in output_dir.glob('*.jsonl'):
        records.extend(
            json.loads(line)
            for line in split_file.read_text(encoding='utf-8').splitlines()
        )

    assert {record['identifier'] for record in records} == {
        'apache_test.RULE',
        'bsd_test.RULE',
        'mit_test.RULE',
    }
    assert all(len(record['tokens']) == len(record['bioes_labels']) for record in records)
    assert all('{{' not in record['text'] and '}}' not in record['text'] for record in records)


def test_main_fails_when_a_rule_cannot_be_loaded(tmp_path):
    rules_dir = tmp_path / 'rules'
    output_dir = tmp_path / 'dataset'
    rules_dir.mkdir()
    (rules_dir / 'broken.RULE').write_text('', encoding='utf-8')

    result = CliRunner().invoke(
        main,
        ['--rules-dir', str(rules_dir), '--output-dir', str(output_dir)],
    )

    assert isinstance(result.exception, InvalidRule)
    assert 'broken.RULE' in str(result.exception)
    assert not output_dir.exists()
