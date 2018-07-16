#
# Copyright (c) 2017 nexB Inc. and others. All rights reserved.
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

from commoncode.testcase import FileDrivenTesting
from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from scancode.cli_test_utils import load_json_result

test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


def test_json_pretty_print():
    test_dir = test_env.get_test_loc('json/simple')
    result_file = test_env.get_temp_file('json')
    args = ['-clip', test_dir, '--json-pp', result_file]
    run_scan_click(args)
    expected = test_env.get_test_loc('json/simple-expected.jsonpp')
    check_json_scan(test_env.get_test_loc(expected), result_file, strip_dates=True, regen=False)


def test_json_compact():
    test_dir = test_env.get_test_loc('json/simple')
    result_file = test_env.get_temp_file('json')
    run_scan_click(['-clip', test_dir, '--json', result_file])
    with open(result_file, 'rb') as res:
        assert len(res.read().splitlines()) == 1
    expected = test_env.get_test_loc('json/simple-expected.json')
    check_json_scan(test_env.get_test_loc(expected), result_file, strip_dates=True, regen=False)


def test_scan_output_does_not_truncate_copyright_json():
    test_dir = test_env.get_test_loc('json/tree/scan/')
    result_file = test_env.get_temp_file('test.json')
    run_scan_click(['-clip', '--strip-root', test_dir, '--json-pp', result_file])
    expected = test_env.get_test_loc('json/tree/expected.json')
    check_json_scan(test_env.get_test_loc(expected), result_file, strip_dates=True, regen=False)


def test_scan_output_does_not_truncate_copyright_with_json_to_stdout():
    test_dir = test_env.get_test_loc('json/tree/scan/')
    result_file = test_env.get_temp_file('test.json')
    args = ['-clip', '--strip-root', test_dir, '--json-pp', result_file]
    run_scan_click(args)
    expected = test_env.get_test_loc('json/tree/expected.json')
    check_json_scan(test_env.get_test_loc(expected), result_file, strip_dates=True, regen=False)


def test_scan_output_for_timestamp():
    test_dir = test_env.get_test_loc('json/simple')
    result_file = test_env.get_temp_file('json')
    run_scan_click(['-clip', test_dir, '--json', result_file])
    result_json = load_json_result(result_file)
    assert "scan_start" in result_json
