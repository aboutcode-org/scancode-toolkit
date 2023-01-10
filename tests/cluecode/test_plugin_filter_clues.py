#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os

from commoncode.testcase import FileDrivenTesting

from cluecode.plugin_filter_clues import Detections
from cluecode.plugin_filter_clues import is_empty
from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click

from scancode_config import REGEN_TEST_FIXTURES


test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


def test_is_empty_():
    assert is_empty([])
    assert is_empty(Detections())
    assert not is_empty(Detections(copyrights=['Foo']))
    assert not is_empty(Detections(holders=['Foo']))
    assert not is_empty(Detections(emails=['Foo']))
    assert not is_empty(Detections(authors=['Foo']))
    assert not is_empty(Detections(urls=['Foo']))


def test_scan_plugin_filter_clues_for_rule():
    # this test fies is a copy of apache-1.1_63.RULE that contains
    # several emails, authors, urls and copyrights
    # it has been modified to include more unrelated clues
    test_dir = test_env.get_test_loc('plugin_filter_clues/files/LICENSE')
    result_file = test_env.get_temp_file('json')
    args = ['-clieu', '--filter-clues', test_dir, '--json', result_file]
    run_scan_click(args)
    expected = test_env.get_test_loc('plugin_filter_clues/filtered-expected.json')
    check_json_scan(expected, result_file, remove_file_date=True, regen=REGEN_TEST_FIXTURES)


def test_scan_plugin_filter_clues_does_not_filter_incorrectly():
    # this test fies is a copy of pygres-2.2_1.RULE that contains
    # several emails, authors, urls and copyrights that have all been modified
    # to differ from the one in the license rule
    test_dir = test_env.get_test_loc('plugin_filter_clues/files/LICENSE2')
    result_file = test_env.get_temp_file('json')
    args = ['-clieu', '--filter-clues', test_dir, '--json', result_file]
    run_scan_click(args)
    expected = test_env.get_test_loc('plugin_filter_clues/filtered-expected2.json')
    check_json_scan(expected, result_file, remove_file_date=True, regen=REGEN_TEST_FIXTURES)


# Regression on types tracked in https://github.com/nexB/typecode/issues/21
def test_scan_plugin_filter_clues_for_license():
    # this test fies is a copy of pcre.LICENSE that contains
    # several emails, authors, urls
    test_dir = test_env.get_test_loc('plugin_filter_clues/files/LICENSE3')
    result_file = test_env.get_temp_file('json')
    args = ['-clieu', '--filter-clues', test_dir, '--json', result_file]
    run_scan_click(args)
    expected = test_env.get_test_loc('plugin_filter_clues/filtered-expected3.json')
    check_json_scan(expected, result_file, remove_file_date=True, regen=REGEN_TEST_FIXTURES)
