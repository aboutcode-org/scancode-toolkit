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

from scancode.api import get_licenses
from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from scancode_config import REGEN_TEST_FIXTURES

test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

"""
These tests spawn new process as if launched from the command line.
"""


def test_license_detection_api_works():
    test_loc = test_env.get_test_loc('plugin_license/scan/e2fsprogs/e2fsprogs-copyright')
    detections = list(get_licenses(location=test_loc))
    assert detections


def test_license_detection_plugin_works():
    test_dir = test_env.get_test_loc('plugin_license/scan/e2fsprogs/', copy=True)
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--strip-root',
        '--verbose',
        '--json', result_file,
        test_dir,
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('plugin_license/scan/e2fsprogs-expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


def test_license_option_reports_license_expressions():
    test_dir = test_env.get_test_loc('plugin_license/license-expression/scan', copy=True)
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--strip-root',
        '--verbose',
        '--json', result_file,
        test_dir,
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('plugin_license/license-expression/scan.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


def test_license_option_reports_license_expressions_spdx_nuget():
    test_dir = test_env.get_test_loc('plugin_license/license-expression/spdx-expressions.txt', copy=True)
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-text',
        '--license-text-diagnostics',
        '--license-diagnostics',
        '--strip-root',
        '--verbose',
        '--json', result_file,
        test_dir,
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('plugin_license/license-expression/spdx-expressions.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)



def test_license_option_reports_license_texts():
    test_dir = test_env.get_test_loc('plugin_license/text/scan', copy=True)
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-text',
        '--license-text-diagnostics',
        '--license-diagnostics',
        '--strip-root',
        '--verbose',
        '--json', result_file,
        test_dir,
    ]

    run_scan_click(args)
    test_loc = test_env.get_test_loc('plugin_license/text/scan.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


def test_license_option_reports_license_texts_diag():
    test_dir = test_env.get_test_loc('plugin_license/text/scan', copy=True)
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-text',
        '--license-text-diagnostics',
        '--license-diagnostics',
        '--strip-root',
        '--verbose',
        '--json', result_file,
        test_dir,
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('plugin_license/text/scan-diag.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


def test_license_option_reports_license_texts_long_lines():
    test_dir = test_env.get_test_loc('plugin_license/text_long_lines/scan', copy=True)
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-text',
        '--license-text-diagnostics',
        '--license-diagnostics',
        '--strip-root',
        '--verbose',
        '--json', result_file,
        test_dir,
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('plugin_license/text_long_lines/scan.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


def test_license_option_reports_license_texts_diag_long_lines():
    test_dir = test_env.get_test_loc('plugin_license/text_long_lines/scan', copy=True)
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-text',
        '--license-text-diagnostics',
        '--license-diagnostics',
        '--strip-root',
        '--verbose',
        '--json', result_file,
        test_dir,
    ]
    run_scan_click(args)
    test_loc = test_env.get_test_loc('plugin_license/text_long_lines/scan-diag.expected.json')
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


@pytest.mark.scanslow
def test_reindex_licenses_works():
    from licensedcode.cache import get_index
    get_index(force=True)
    get_index(force=True, index_all_languages=True)


@pytest.mark.scanslow
def test_scan_license_with_url_template():
    test_dir = test_env.get_test_loc('plugin_license/license_url/scan/', copy=True)
    result_file = test_env.get_temp_file('json')
    args = [
        '--license',
        '--license-url-template', 'https://example.com/urn:{}',
        '--json-pp', result_file,
        test_dir,
    ]
    test_loc = test_env.get_test_loc('plugin_license/license_url/license_url.expected.json')
    run_scan_click(args)
    check_json_scan(test_loc, result_file, regen=REGEN_TEST_FIXTURES)


@pytest.mark.scanslow
def test_detection_does_not_timeout_on_sqlite3_amalgamation():
    test_dir = test_env.extract_test_tar('plugin_license/sqlite/sqlite.tgz')
    result_file = test_env.get_temp_file('json')
    expected_file = test_env.get_test_loc('plugin_license/sqlite/sqlite.expected.json')
    # we use the default 120 seconds timeout
    run_scan_click(['-l', '--license-text', '--license-text-diagnostics', '--json-pp', result_file, test_dir])
    check_json_scan(expected_file, result_file, remove_file_date=True, regen=REGEN_TEST_FIXTURES)


@pytest.mark.scanslow
def test_detection_is_correct_in_legacy_npm_package_json():
    test_dir = test_env.get_test_loc('plugin_license/package/package.json')
    result_file = test_env.get_temp_file('json')
    expected_file = test_env.get_test_loc('plugin_license/package/package.expected.json')
    run_scan_click(['-lp', '--json-pp', result_file, test_dir])
    check_json_scan(expected_file, result_file, remove_uuid=True, remove_file_date=True, regen=REGEN_TEST_FIXTURES)
