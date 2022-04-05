#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#


from os import path

import pytest

from commoncode.testcase import FileDrivenTesting

from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import check_jsonlines_scan
from scancode.cli_test_utils import run_scan_click
from scancode_config import REGEN_TEST_FIXTURES


pytestmark = pytest.mark.scanslow


class TestScanSummary(FileDrivenTesting):

    test_data_dir = path.join(path.dirname(__file__), 'data')

    def test_copyright_license_summary_base(self):
        test_dir = self.get_test_loc('summary/copyright/scan')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('summary/copyright/scan.expected.json')
        run_scan_click(['-cl', '--summary', '--classify', '--license-clarity-score', '--json-pp', result_file, test_dir])
        check_json_scan(expected_file, result_file, remove_file_date=True, regen=REGEN_TEST_FIXTURES)

    def test_copyright_summary_does_not_crash(self):
        test_dir = self.get_test_loc('summary/copyright/scan2')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('summary/copyright/scan2.expected.json')
        run_scan_click(['-cl', '--summary', '--classify', '--license-clarity-score', '--json-pp', result_file, test_dir])
        check_json_scan(expected_file, result_file, remove_file_date=True, regen=REGEN_TEST_FIXTURES)

    def test_full_summary_base(self):
        test_dir = self.get_test_loc('summary/full/scan')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('summary/full/scan.expected.json')
        run_scan_click(['-clip', '--summary', '--classify', '--license-clarity-score', '--json-pp', result_file, test_dir])
        check_json_scan(expected_file, result_file, remove_instance_uuid=True, remove_file_date=True, regen=REGEN_TEST_FIXTURES)

    def test_full_summary_json_lines(self):
        test_dir = self.get_test_loc('summary/full/scan')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('summary/full/scan.expected.json-lines')
        run_scan_click(
            ['-cli', '--summary', '--classify', '--license-clarity-score',
             '--json-lines', result_file, test_dir])
        check_jsonlines_scan(expected_file, result_file, remove_file_date=True, regen=REGEN_TEST_FIXTURES)

    def test_end2end_summary_and_classify_works_with_empty_dir_and_empty_values(self):
        test_dir = self.extract_test_tar('summary/end-2-end/bug-1141.tar.gz')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('summary/end-2-end/bug-1141.expected.json')
        run_scan_click([
            '-clip',
            '--summary',
            '--classify',
            '--license-clarity-score',
            '--json-pp', result_file, test_dir
        ])
        check_json_scan(expected_file, result_file, remove_instance_uuid=True, remove_file_date=True, regen=REGEN_TEST_FIXTURES)

    def test_summary_with_packages_reports_packages_with_files(self):
        test_dir = self.get_test_loc('summary/packages/scan')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('summary/packages/scan.expected.json')
        run_scan_click([
            '--package',
            '--summary',
            '--classify',
            '--license-clarity-score',
            '--json-pp', result_file, test_dir
        ])
        check_json_scan(expected_file, result_file, remove_instance_uuid=True, remove_file_date=True, regen=REGEN_TEST_FIXTURES)
