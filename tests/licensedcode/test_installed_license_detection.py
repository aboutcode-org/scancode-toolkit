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

"""
These tests spawn new process as if launched from the command line.
"""


@pytest.mark.scanslow
def test_detection_with_single_installed_external_license():
    test_dir = test_env.get_test_loc('plugin_license/installed_licenses/scan', copy=True)
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--strip-root',
        '--verbose',
        '--json', result_file,
        test_dir,
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('plugin_license/installed_licenses/scan.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


@pytest.mark.scanslow
def test_detection_with_single_installed_external_rule():
    test_dir = test_env.get_test_loc('plugin_license/installed_rules/scan', copy=True)
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--strip-root',
        '--verbose',
        '--json', result_file,
        test_dir,
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('plugin_license/installed_rules/scan.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)
