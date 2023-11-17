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


def test_validate_license_library_returns_errors():
    from licensedcode.models import InvalidLicense
    from licensedcode.cache import get_index
    licenses_dir = test_env.get_test_loc('additional_licenses/validate_licenses')
    with pytest.raises(InvalidLicense):
        get_index(force=True, additional_directory=licenses_dir)


"""
These tests need to have an extra "additional licenses" plugin install to work.
They will fail when spawned locally therefore we use a special Pytest marker
so that they run only in the CI to avoid problems.
"""

# Testing an additional directory only
@pytest.mark.scanplugins
def test_detection_with_additional_license_directory():
    # Before running this test you need to reindex the licenses with
    # the directory tests/licensedcode/data/additional_licenses/additional_dir/
    test_file = test_env.get_test_loc('additional_licenses/additional_license_directory_test.txt')
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-references',
        '--strip-root',
        '--verbose',
        '--json', result_file,
        test_file,
    ]
    run_scan_click(args)
    expected_loc = test_env.get_test_loc('additional_licenses/additional_license_directory_test.expected.json')
    check_json_scan(expected_loc, result_file, regen=REGEN_TEST_FIXTURES)


# Testing an additional plugin only
@pytest.mark.scanplugins
def test_detection_with_additional_license_plugin():
    # Before running this test you need to install the plugin at
    # the directory tests/licensedcode/data/additional_licenses/additional_plugin_1/
    # and reindex the licenses.
    test_file = test_env.get_test_loc('additional_licenses/additional_license_plugin_test.txt')
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-references',
        '--strip-root',
        '--verbose',
        '--json', result_file,
        test_file,
    ]
    run_scan_click(args)
    expected_loc = test_env.get_test_loc('additional_licenses/additional_license_plugin_test.expected.json')
    check_json_scan(expected_loc, result_file, regen=REGEN_TEST_FIXTURES)


# Testing an additional directory and two additional plugins together
@pytest.mark.scanplugins
def test_detection_with_additional_license_combined():
    # Before running this test you need to install the plugins at
    # the directory tests/licensedcode/data/additional_licenses/additional_plugin_1/
    # the directory tests/licensedcode/data/additional_licenses/additional_plugin_2/
    # and reindex the licenses with
    # the directory tests/licensedcode/data/additional_licenses/additional_dir/
    test_file = test_env.get_test_loc('additional_licenses/additional_license_combined_test.txt')
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-references',
        '--strip-root',
        '--verbose',
        '--json', result_file,
        test_file,
    ]
    run_scan_click(args)
    expected_loc = test_env.get_test_loc('additional_licenses/additional_license_combined_test.expected.json')
    check_json_scan(expected_loc, result_file, regen=REGEN_TEST_FIXTURES)

