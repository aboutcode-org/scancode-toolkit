#
# Copyright (c) 2018 nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/scancode-toolkit/
# The ScanCode software is licensed under the Apache License version 2.0.
# Data generated with ScanCode require an acknowledgment.
# ScanCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# When you publish or redistribute any data created with ScanCode or any ScanCode
# derivative work, you must accompany this data with the following acknowledgment:
#
#  Generated with ScanCode and provided on an "AS IS" BASIS, WITHOUT WARRANTIES
#  OR CONDITIONS OF ANY KIND, either express or implied. No content created from
#  ScanCode should be considered or used as legal advice. Consult an Attorney
#  for any legal advice.
#  ScanCode is a free software code scanning tool from nexB Inc. and others.
#  Visit https://github.com/nexB/scancode-toolkit/ for support and download.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os

import click
click.disable_unicode_literals_warning = True
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
