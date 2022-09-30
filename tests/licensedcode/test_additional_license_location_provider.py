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
These tests need to have an extra "additional licenses" plugin install to work.
They will fail when spaned locally therefore we use a special Pytest marker
so that they run only in the CI to avoid problems.
"""


@pytest.mark.scanplugins
def test_additional_license_location_provider__works_with_simple_plugin():
    test_file = test_env.get_test_loc('additional_license_location_provider/test_file.txt')
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-text',
        '--strip-root',
        '--verbose',
        '--json-pp', result_file,
        test_file,
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc(
        test_path='additional_license_location_provider/test_file.txt.expected.json',
        must_exist=False,
    )
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)

