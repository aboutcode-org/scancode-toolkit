# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import csv
import io
import json
import os

import pytest
from commoncode.testcase import FileDrivenTesting

from formattedcode.output_csv import flatten_scan
from scancode.cli_test_utils import run_scan_click
from scancode.cli_test_utils import run_scan_plain
from scancode_config import REGEN_TEST_FIXTURES


test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


def load_scan(json_input):
    """
    Return a list of scan results loaded from a json_input, either in
    ScanCode standard JSON format or the data.js html-app format.
    """
    with io.open(json_input, encoding='utf-8') as jsonf:
        scan = jsonf.read()

    scan_results = json.loads(scan)
    scan_results = scan_results['files']
    return scan_results


def check_json(result, expected_file, regen=REGEN_TEST_FIXTURES):
    if regen:
        with io.open(expected_file, 'w', encoding='utf-8') as reg:
            reg.write(json.dumps(result, indent=4, separators=(',', ': ')))
    with io.open(expected_file, encoding='utf-8') as exp:
        expected = json.load(exp)
    assert result == expected


def check_csvs(result_file, expected_file,
               ignore_keys=('date', 'file_type', 'mime_type', 'package_uid'),
               regen=REGEN_TEST_FIXTURES):
    """
    Load and compare two CSVs.
    `ignore_keys` is a tuple of keys that will be ignored in the comparisons.
    """
    result_fields, results = load_csv(result_file)
    if regen:
        import shutil
        shutil.copy2(result_file, expected_file)
    expected_fields, expected = load_csv(expected_file)
    assert result_fields == expected_fields
    # then check results line by line for more compact results
    for exp, res in zip(sorted(expected , key=lambda d: d.items()), sorted(results , key=lambda d: d.items())):
        for ign in ignore_keys:
            exp.pop(ign, None)
            res.pop(ign, None)
        assert res == exp


def load_csv(location):
    """
    Load a CSV file at location and return a tuple of (field names, list of rows as
    mappings field->value).
    """
    with io.open(location) as csvin:
        reader = csv.DictReader(csvin)
        fields = reader.fieldnames
        values = sorted(reader, key=lambda d: d.items())
        return fields, values


def test_flatten_scan_minimal():
    test_json = test_env.get_test_loc('csv/flatten_scan/minimal.json')
    scan = load_scan(test_json)
    headers = dict([
        ('info', []),
        ('license', []),
        ('copyright', []),
        ('email', []),
        ('url', []),
        ('package', []),
    ])
    result = list(flatten_scan(scan, headers))
    expected_file = test_env.get_test_loc('csv/flatten_scan/minimal.json-expected')
    check_json(result, expected_file, regen=REGEN_TEST_FIXTURES)


def test_flatten_scan_can_process_path_with_and_without_leading_slash():
    test_json = test_env.get_test_loc('csv/flatten_scan/path_with_and_without_leading_slash.json')
    scan = load_scan(test_json)
    headers = dict([
        ('info', []),
        ('license', []),
        ('copyright', []),
        ('email', []),
        ('url', []),
        ('package', []),
    ])
    result = list(flatten_scan(scan, headers))
    expected_file = test_env.get_test_loc('csv/flatten_scan/path_with_and_without_leading_slash.json-expected')
    check_json(result, expected_file)

    
@pytest.mark.scanslow
def test_can_process_live_scan_for_packages_with_root():
    test_dir = test_env.get_test_loc('csv/packages/scan')
    result_file = test_env.get_temp_file('csv')
    args = ['--package', test_dir, '--csv', result_file]
    run_scan_plain(args)
    expected_file = test_env.get_test_loc('csv/packages/expected.csv')
    check_csvs(result_file, expected_file, regen=REGEN_TEST_FIXTURES)


def test_output_can_handle_non_ascii_paths():
    # very small file with selective attributes just to test unicode, no need
    # run scan again, update manually if required
    test_file = test_env.get_test_loc('csv/unicode.json')
    result_file = test_env.get_temp_file(extension='csv', file_name='test_csv')
    run_scan_click(['--from-json', test_file, '--csv', result_file])
    with io.open(result_file, encoding='utf-8') as res:
        results = res.read()
    assert 'han/据.svg' in results


def test_csv_minimal():
    test_dir = test_env.get_test_loc('csv/srp')
    result_file = test_env.get_temp_file('csv')
    expected_file = test_env.get_test_loc('csv/srp.csv')
    args = ['--copyright', test_dir, '--csv', result_file]
    run_scan_click(args)
    check_csvs(result_file, expected_file)


@pytest.mark.scanslow
def test_flatten_scan_full():
    test_json = test_env.get_test_loc('csv/flatten_scan/full.json')
    scan = load_scan(test_json)
    headers = dict([
        ('info', []),
        ('license', []),
        ('copyright', []),
        ('email', []),
        ('url', []),
        ('package', []),
    ])
    result = list(flatten_scan(scan, headers))
    expected_file = test_env.get_test_loc('csv/flatten_scan/full.json-expected')
    check_json(result, expected_file)


@pytest.mark.scanslow
def test_flatten_scan_key_ordering():
    test_json = test_env.get_test_loc('csv/flatten_scan/key_order.json')
    scan = load_scan(test_json)
    headers = dict([
        ('info', []),
        ('license', []),
        ('copyright', []),
        ('email', []),
        ('url', []),
        ('package', []),
    ])
    result = list(flatten_scan(scan, headers))
    expected_file = test_env.get_test_loc('csv/flatten_scan/key_order.expected.json')
    check_json(result, expected_file)


@pytest.mark.scanslow
def test_flatten_scan_with_no_keys_does_not_error_out():
    # this scan has no results at all
    test_json = test_env.get_test_loc('csv/flatten_scan/no_keys.json')
    scan = load_scan(test_json)
    headers = dict([
        ('info', []),
        ('license', []),
        ('copyright', []),
        ('email', []),
        ('url', []),
        ('package', []),
    ])
    result = list(flatten_scan(scan, headers))
    expected_headers = dict([
        ('info', []),
        ('license', []),
        ('copyright', []),
        ('email', []),
        ('url', []),
        ('package', []),
    ])
    assert headers == expected_headers
    assert result == []


@pytest.mark.scanslow
def test_flatten_scan_can_process_package_license_when_license_value_is_null():
    test_json = test_env.get_test_loc('csv/flatten_scan/package_license_value_null.json')
    scan = load_scan(test_json)
    headers = dict([
        ('info', []),
        ('license', []),
        ('copyright', []),
        ('email', []),
        ('url', []),
        ('package', []),
    ])
    result = list(flatten_scan(scan, headers))
    expected_file = test_env.get_test_loc('csv/flatten_scan/package_license_value_null.json-expected')
    check_json(result, expected_file)


@pytest.mark.scanslow
def test_csv_tree():
    test_dir = test_env.get_test_loc('csv/tree/scan')
    result_file = test_env.get_temp_file('csv')
    expected_file = test_env.get_test_loc('csv/tree/expected.csv')
    args = ['--copyright', test_dir, '--csv', result_file]
    run_scan_click(args)
    check_csvs(result_file, expected_file)


@pytest.mark.scanslow
def test_can_process_live_scan_with_all_options():
    test_dir = test_env.get_test_loc('csv/livescan/scan')
    result_file = test_env.get_temp_file('csv')
    args = ['-clip', '--email', '--url', '--strip-root', test_dir, '--csv', result_file]
    run_scan_plain(args)
    expected_file = test_env.get_test_loc('csv/livescan/expected.csv')
    check_csvs(result_file, expected_file, regen=REGEN_TEST_FIXTURES)


@pytest.mark.scanslow
def test_can_process_live_scan_for_packages_strip_root():
    test_dir = test_env.get_test_loc('csv/packages/scan')
    result_file = test_env.get_temp_file('csv')
    args = ['--package', '--strip-root', test_dir, '--csv', result_file]
    run_scan_plain(args)
    expected_file = test_env.get_test_loc('csv/packages/expected-no-root.csv')
    check_csvs(result_file, expected_file, regen=REGEN_TEST_FIXTURES)


@pytest.mark.scanslow
def test_output_contains_license_expression():
    # very small file with selective attributes just to test license_expressions,
    # no need to run scan again, update manually if required
    test_file = test_env.get_test_loc('csv/expressions/scan.json')
    result_file = test_env.get_temp_file('csv')
    args = ['--from-json', test_file, '--csv', result_file]
    run_scan_plain(args)
    expected_file = test_env.get_test_loc('csv/expressions/expected.csv')
    check_csvs(result_file, expected_file, regen=REGEN_TEST_FIXTURES)


@pytest.mark.scanslow
def test_output_handles_non_standard_data():
    # non standard data from other tool, update manually if required
    test_file = test_env.get_test_loc('csv/non-standard/identified.json')
    result_file = test_env.get_temp_file('csv')
    args = ['--from-json', test_file, '--csv', result_file]
    run_scan_plain(args)
    expected_file = test_env.get_test_loc('csv/non-standard/identified.csv')
    check_csvs(result_file, expected_file, regen=REGEN_TEST_FIXTURES)
