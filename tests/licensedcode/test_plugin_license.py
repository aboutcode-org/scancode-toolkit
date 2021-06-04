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

test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

"""
These tests spawn new process as if launched from the command line.
"""


def test_license_option_reports_license_expressions():
    test_dir = test_env.get_test_loc('plugin_license/license-expression/scan', copy=True)
    result_file = test_env.get_temp_file('json')
    args = ['--license', '--strip-root', test_dir, '--json', result_file, '--verbose']
    run_scan_click(args)
    test_loc = test_env.get_test_loc('plugin_license/license-expression/scan.expected.json')
    check_json_scan(test_loc, result_file, regen=False)


def test_license_option_reports_license_texts():
    test_dir = test_env.get_test_loc('plugin_license/text/scan', copy=True)
    result_file = test_env.get_temp_file('json')
    args = ['--license', '--license-text', '--strip-root', test_dir, '--json', result_file, '--verbose']
    run_scan_click(args)
    test_loc = test_env.get_test_loc('plugin_license/text/scan.expected.json')
    check_json_scan(test_loc, result_file, regen=False)


def test_license_option_reports_license_texts_diag():
    test_dir = test_env.get_test_loc('plugin_license/text/scan', copy=True)
    result_file = test_env.get_temp_file('json')
    args = ['--license', '--license-text', '--license-text-diagnostics', '--strip-root', test_dir, '--json', result_file, '--verbose']
    run_scan_click(args)
    test_loc = test_env.get_test_loc('plugin_license/text/scan-diag.expected.json')
    check_json_scan(test_loc, result_file, regen=False)


def test_license_option_reports_license_texts_long_lines():
    test_dir = test_env.get_test_loc('plugin_license/text_long_lines/scan', copy=True)
    result_file = test_env.get_temp_file('json')
    args = ['--license', '--license-text', '--strip-root', test_dir, '--json', result_file, '--verbose']
    run_scan_click(args)
    test_loc = test_env.get_test_loc('plugin_license/text_long_lines/scan.expected.json')
    check_json_scan(test_loc, result_file, regen=False)


def test_license_option_reports_license_texts_diag_long_lines():
    test_dir = test_env.get_test_loc('plugin_license/text_long_lines/scan', copy=True)
    result_file = test_env.get_temp_file('json')
    args = ['--license', '--license-text', '--license-text-diagnostics', '--strip-root', test_dir, '--json', result_file, '--verbose']
    run_scan_click(args)
    test_loc = test_env.get_test_loc('plugin_license/text_long_lines/scan-diag.expected.json')
    check_json_scan(test_loc, result_file, regen=False)


def test_reindex_licenses_works():
    args = ['--reindex-licenses']
    run_scan_click(args)


@pytest.mark.scanslow
def test_scan_license_with_url_template():
    test_dir = test_env.get_test_loc('plugin_license/license_url', copy=True)
    result_file = test_env.get_temp_file('json')
    args = ['--license', '--license-url-template', 'https://example.com/urn:{}',
             test_dir, '--json-pp', result_file]
    test_loc = test_env.get_test_loc('plugin_license/license_url.expected.json')
    run_scan_click(args)
    check_json_scan(test_loc, result_file)


@pytest.mark.scanslow
def test_detection_does_not_timeout_on_sqlite3_amalgamation():
    test_dir = test_env.extract_test_tar('plugin_license/sqlite/sqlite.tgz')
    result_file = test_env.get_temp_file('json')
    expected_file = test_env.get_test_loc('plugin_license/sqlite/sqlite.expected.json')
    # we use the default 120 seconds timeout
    run_scan_click(['-l', '--license-text', '--json-pp', result_file, test_dir])
    check_json_scan(expected_file, result_file, remove_file_date=True, regen=False)


@pytest.mark.scanslow
def test_detection_is_correct_in_legacy_npm_package_json():
    test_dir = test_env.get_test_loc('plugin_license/package/package.json')
    result_file = test_env.get_temp_file('json')
    expected_file = test_env.get_test_loc('plugin_license/package/package.expected.json')
    run_scan_click(['-lp', '--json-pp', result_file, test_dir])
    check_json_scan(expected_file, result_file, remove_file_date=True, regen=False)
