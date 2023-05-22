# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import io
import json
import os

from commoncode.testcase import FileDrivenTesting

from scancode.cli_test_utils import check_jsonlines_scan
from scancode.cli_test_utils import run_scan_click
from scancode_config import REGEN_TEST_FIXTURES


test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


def test_jsonlines():
    test_dir = test_env.get_test_loc('json/simple')
    result_file = test_env.get_temp_file('jsonline')
    run_scan_click(['-i', test_dir, '--json-lines', result_file])
    expected = test_env.get_test_loc('json/simple-expected.jsonlines')
    check_jsonlines_scan(
        test_env.get_test_loc(expected), result_file,
        remove_file_date=True, regen=REGEN_TEST_FIXTURES)


def test_jsonlines_with_package_and_license():
    test_dir = test_env.get_test_loc('common/manifests')
    result_file = test_env.get_temp_file('jsonline')
    run_scan_click(['-clip', test_dir, '--json-lines', result_file])
    expected = test_env.get_test_loc('common/manifests-expected.jsonlines')
    check_jsonlines_scan(
        test_env.get_test_loc(expected), result_file,
        remove_file_date=True, regen=REGEN_TEST_FIXTURES)


def test_jsonlines_with_timing():
    test_dir = test_env.get_test_loc('json/simple')
    result_file = test_env.get_temp_file('jsonline')
    run_scan_click(['-i', '--timing', test_dir, '--json-lines', result_file])

    with io.open(result_file, encoding='utf-8') as res:
        file_results = [json.loads(line) for line in res]

    first_line = True
    for res in file_results:
        if first_line:
            # skip header
            first_line = False
            continue
        scan_timings = res['files'][0]['scan_timings']

        if not res['files'][0]['type'] == 'file':
            # should be an empty dict for dirs
            assert not scan_timings
            continue

        assert scan_timings

        for scanner, timing in scan_timings.items():
            assert scanner in ('info',)
            assert timing
