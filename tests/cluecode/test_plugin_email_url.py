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

from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from scancode_config import REGEN_TEST_FIXTURES


test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


def test_scan_email():
    test_dir = test_env.get_test_loc('plugin_email_url/files')
    result_file = test_env.get_temp_file('json')
    args = ['--email', '--strip-root', test_dir, '--json', result_file]
    run_scan_click(args)
    check_json_scan(test_env.get_test_loc('plugin_email_url/emails.expected.json'), result_file, regen=REGEN_TEST_FIXTURES)


def test_scan_email_with_threshold():
    test_dir = test_env.get_test_loc('plugin_email_url/files')
    result_file = test_env.get_temp_file('json')
    args = ['--email', '--strip-root', '--max-email', '2', test_dir, '--json', result_file]
    run_scan_click(args)
    check_json_scan(test_env.get_test_loc('plugin_email_url/emails-threshold.expected.json'), result_file, regen=REGEN_TEST_FIXTURES)


def test_scan_url():
    test_dir = test_env.get_test_loc('plugin_email_url/files')
    result_file = test_env.get_temp_file('json')
    args = ['--url', '--strip-root', test_dir, '--json', result_file]
    run_scan_click(args)
    check_json_scan(test_env.get_test_loc('plugin_email_url/urls.expected.json'), result_file, regen=REGEN_TEST_FIXTURES)


def test_scan_url_with_threshold():
    test_dir = test_env.get_test_loc('plugin_email_url/files')
    result_file = test_env.get_temp_file('json')
    args = ['--url', '--strip-root', '--max-url', '2', test_dir, '--json', result_file]
    run_scan_click(args)
    check_json_scan(test_env.get_test_loc('plugin_email_url/urls-threshold.expected.json'), result_file, regen=REGEN_TEST_FIXTURES)
