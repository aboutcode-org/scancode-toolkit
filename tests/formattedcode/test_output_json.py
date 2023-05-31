# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os

import pytest

from commoncode.testcase import FileDrivenTesting

from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from scancode_config import REGEN_TEST_FIXTURES



test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


def test_json_pretty_print():
    test_dir = test_env.get_test_loc('json/simple')
    result_file = test_env.get_temp_file('json')
    args = ['-clip', test_dir, '--json-pp', result_file]
    run_scan_click(args)
    expected = test_env.get_test_loc('json/simple-expected.jsonpp')
    check_json_scan(expected, result_file, remove_file_date=True, regen=REGEN_TEST_FIXTURES)


def test_json_compact():
    test_dir = test_env.get_test_loc('json/simple')
    result_file = test_env.get_temp_file('json')
    run_scan_click(['-clip', test_dir, '--json', result_file])
    with open(result_file, 'rb') as res:
        assert len(res.read().splitlines()) == 1
    expected = test_env.get_test_loc('json/simple-expected.json')
    check_json_scan(expected, result_file, remove_file_date=True, regen=REGEN_TEST_FIXTURES)


def test_json_with_extracted_license_statements():
    test_dir = test_env.get_test_loc('common/manifests')
    result_file = test_env.get_temp_file('json')
    run_scan_click(['-clip', test_dir, '--json', result_file])
    expected = test_env.get_test_loc('common/manifests-expected.json')
    check_json_scan(expected, result_file, remove_file_date=True, regen=REGEN_TEST_FIXTURES)


@pytest.mark.scanslow
def test_scan_output_does_not_truncate_copyright_json():
    test_dir = test_env.get_test_loc('json/tree/scan/')
    result_file = test_env.get_temp_file('test.json')
    run_scan_click(['-clip', '--strip-root', test_dir, '--json-pp', result_file])
    expected = test_env.get_test_loc('json/tree/expected.json')
    check_json_scan(expected, result_file, remove_file_date=True, regen=REGEN_TEST_FIXTURES)


@pytest.mark.scanslow
def test_scan_output_does_not_truncate_copyright_with_json_to_stdout():
    test_dir = test_env.get_test_loc('json/tree/scan/')
    result_file = test_env.get_temp_file('test.json')
    args = ['-clip', '--strip-root', test_dir, '--json-pp', result_file]
    run_scan_click(args)
    expected = test_env.get_test_loc('json/tree/expected.json')
    check_json_scan(expected, result_file, remove_file_date=True, regen=REGEN_TEST_FIXTURES)


@pytest.mark.scanslow
def test_scan_output_for_timestamp():
    import json

    test_dir = test_env.get_test_loc('json/simple')
    result_file = test_env.get_temp_file('json')
    run_scan_click(['-clip', test_dir, '--json', result_file])
    result_json = json.loads(open(result_file).read())
    header = result_json['headers'][0]
    assert 'start_timestamp' in header
    assert 'end_timestamp' in header
