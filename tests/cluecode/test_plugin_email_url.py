#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 AND CC-BY-4.0
#
# Visit https://aboutcode.org and https://github.com/nexB/scancode-toolkit for
# support and download. ScanCode is a trademark of nexB Inc.
#
# The ScanCode software is licensed under the Apache License version 2.0.
# The ScanCode open data is licensed under CC-BY-4.0.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os

import click

from commoncode.testcase import FileDrivenTesting

from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click

test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


def test_scan_email():
    test_dir = test_env.get_test_loc('plugin_email_url/files')
    result_file = test_env.get_temp_file('json')
    args = ['--email', '--strip-root', test_dir, '--json', result_file]
    run_scan_click(args)
    check_json_scan(test_env.get_test_loc('plugin_email_url/emails.expected.json'), result_file)


def test_scan_email_with_threshold():
    test_dir = test_env.get_test_loc('plugin_email_url/files')
    result_file = test_env.get_temp_file('json')
    args = ['--email', '--strip-root', '--max-email', '2', test_dir, '--json', result_file]
    run_scan_click(args)
    check_json_scan(test_env.get_test_loc('plugin_email_url/emails-threshold.expected.json'), result_file)


def test_scan_url():
    test_dir = test_env.get_test_loc('plugin_email_url/files')
    result_file = test_env.get_temp_file('json')
    args = ['--url', '--strip-root', test_dir, '--json', result_file]
    run_scan_click(args)
    check_json_scan(test_env.get_test_loc('plugin_email_url/urls.expected.json'), result_file)


def test_scan_url_with_threshold():
    test_dir = test_env.get_test_loc('plugin_email_url/files')
    result_file = test_env.get_temp_file('json')
    args = ['--url', '--strip-root', '--max-url', '2', test_dir, '--json', result_file]
    run_scan_click(args)
    check_json_scan(test_env.get_test_loc('plugin_email_url/urls-threshold.expected.json'), result_file)
