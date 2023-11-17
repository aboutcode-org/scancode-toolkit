#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from os.path import dirname
from os.path import join

import pytest
from commoncode.testcase import FileDrivenTesting

from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from scancode_config import REGEN_TEST_FIXTURES


class TestHasFindings(FileDrivenTesting):

    test_data_dir = join(dirname(__file__), 'data')

    @pytest.mark.scanslow
    def test_scan_only_findings(self):
        test_dir = self.extract_test_tar('plugin_only_findings/basic.tgz')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin_only_findings/basic.expected.json')
        run_scan_click(['-clip', '--only-findings', '--json', result_file, test_dir])
        check_json_scan(expected_file, result_file, remove_file_date=True, regen=REGEN_TEST_FIXTURES)

    def test_scan_only_findings_with_errors(self):
        # Run a -cie scan with --timeout 0.01 to regenerate this scan result
        test_file = self.get_test_loc('plugin_only_findings/errors.json')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin_only_findings/errors.expected.json')
        run_scan_click(['--from-json', test_file, '--only-findings',
                        '--json-pp', result_file])
        check_json_scan(expected_file, result_file, remove_file_date=True, regen=REGEN_TEST_FIXTURES)

    def test_scan_only_findings_with_only_info(self):
        test_dir = self.extract_test_tar('plugin_only_findings/basic.tgz')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin_only_findings/info.expected.json')
        run_scan_click(['--info', '--only-findings', '--json', result_file, test_dir])
        check_json_scan(expected_file, result_file, remove_file_date=True, regen=REGEN_TEST_FIXTURES)
