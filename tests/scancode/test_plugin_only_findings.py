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

from os.path import dirname
from os.path import join

import pytest

from commoncode.testcase import FileDrivenTesting
from scancode.cli_test_utils import run_scan_click
from scancode.cli_test_utils import check_json_scan


class TestHasFindings(FileDrivenTesting):

    test_data_dir = join(dirname(__file__), 'data')

    @pytest.mark.scanslow
    def test_scan_only_findings(self):
        test_dir = self.extract_test_tar('plugin_only_findings/basic.tgz')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin_only_findings/basic.expected.json')
        run_scan_click(['-clip', '--only-findings', '--json', result_file, test_dir])
        check_json_scan(expected_file, result_file, remove_file_date=True, regen=False)

    def test_scan_only_findings_with_errors(self):
        test_file = self.get_test_loc('plugin_only_findings/errors.json')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin_only_findings/errors.expected.json')
        run_scan_click(['--from-json', test_file, '--only-findings',
                        '--json-pp', result_file])
        check_json_scan(expected_file, result_file, remove_file_date=True, regen=False)

    def test_scan_only_findings_with_only_info(self):
        test_dir = self.extract_test_tar('plugin_only_findings/basic.tgz')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin_only_findings/info.expected.json')
        run_scan_click(['--info', '--only-findings', '--json', result_file, test_dir])
        check_json_scan(expected_file, result_file, remove_file_date=True, regen=False)
