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
from scancode.cli_test_utils import run_scan_click
from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import check_jsonlines_scan

pytestmark = pytest.mark.scanslow


class TestScanSummary(FileDrivenTesting):

    test_data_dir = path.join(path.dirname(__file__), 'data')

    def test_copyright_summary_base(self):
        test_dir = self.get_test_loc('copyright_summary/scan')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('copyright_summary/summary.expected.json')
        run_scan_click(['-c', '--summary', '--json-pp', result_file, test_dir])
        check_json_scan(expected_file, result_file, remove_file_date=True, regen=False)

    def test_copyright_summary_with_details(self):
        test_dir = self.get_test_loc('copyright_summary/scan')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('copyright_summary/summary_details.expected.json')
        run_scan_click(['-c', '--summary-with-details', '--json-pp', result_file, test_dir])
        check_json_scan(expected_file, result_file, remove_file_date=True, regen=False)

    def test_copyright_summary_with_details_plain_json(self):
        test_dir = self.get_test_loc('copyright_summary/scan')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('copyright_summary/summary_details.expected2.json')
        run_scan_click(['-c', '--summary-with-details', '--json', result_file, test_dir])
        check_json_scan(expected_file, result_file, remove_file_date=True, regen=False)

    def test_copyright_summary_does_not_crash(self):
        test_dir = self.get_test_loc('copyright_summary/scan2')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('copyright_summary/summary2.expected.json')
        run_scan_click(['-c', '--summary', '--json-pp', result_file, test_dir])
        check_json_scan(expected_file, result_file, remove_file_date=True, regen=False)

    def test_full_summary_base(self):
        test_dir = self.get_test_loc('full_summary/scan')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('full_summary/summary.expected.json')
        run_scan_click(['-clip', '--summary', '--json-pp', result_file, test_dir])
        check_json_scan(expected_file, result_file, remove_file_date=True, regen=False)

    def test_full_summary_with_details(self):
        test_dir = self.get_test_loc('full_summary/scan')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('full_summary/summary_details.expected.json')
        run_scan_click(['-clip', '--summary-with-details', '--json-pp', result_file, test_dir])
        check_json_scan(expected_file, result_file, remove_file_date=True, regen=False)

    def test_copyright_summary_key_files(self):
        test_dir = self.get_test_loc('copyright_summary/scan')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('copyright_summary/summary_key_files.expected.json')
        run_scan_click(
            ['-c', '-i', '--classify', '--summary', '--summary-key-files',
             '--json-pp', result_file, test_dir])

        check_json_scan(expected_file, result_file, remove_file_date=True, regen=False)

    def test_full_summary_key_files(self):
        test_dir = self.get_test_loc('full_summary/scan')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('full_summary/summary_key_files.expected.json')
        run_scan_click(
            ['-cli', '--classify', '--summary', '--summary-key-files',
             '--json-pp', result_file, test_dir])
        check_json_scan(expected_file, result_file, remove_file_date=True, regen=False)

    def test_full_summary_key_files_json_lines(self):
        test_dir = self.get_test_loc('full_summary/scan')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('full_summary/summary_key_files-details.expected.json-lines')
        run_scan_click(
            ['-cli', '--classify', '--summary', '--summary-key-files',
             '--json-lines', result_file, test_dir])
        check_jsonlines_scan(expected_file, result_file, remove_file_date=True, regen=False)

    def test_full_summary_by_facet(self):
        test_dir = self.get_test_loc('full_summary/scan')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('full_summary/summary_by_facet.expected.json')
        run_scan_click([
            '-cli',
            '--facet', 'dev=*.java',
            '--facet', 'dev=*.cs',
            '--facet', 'dev=*ada*',
            '--facet', 'data=*.S',
            '--facet', 'tests=*infback9*',
            '--facet', 'docs=*README',
            '--summary',
            '--summary-by-facet',
            '--json-pp', result_file, test_dir
        ])
        check_json_scan(expected_file, result_file, remove_file_date=True, regen=False)

    def test_end2end_summary_and_classify_works_with_empty_dir_and_empty_values(self):
        test_dir = self.extract_test_tar('end-2-end/bug-1141.tar.gz')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('end-2-end/bug-1141.expected.json')
        run_scan_click([
            '-clip',
            '--classify',
            '--facet', 'dev=*.java',
            '--summary',
            '--summary-key-files',
            '--json-pp', result_file, test_dir
        ])
        check_json_scan(expected_file, result_file, remove_file_date=True, regen=False)

    def test_summary_with_packages_reports_packages_with_files(self):
        test_dir = self.get_test_loc('packages/scan')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('packages/expected.json')
        run_scan_click([
            '--package',
            '--summary',
            '--json-pp', result_file, test_dir
        ])
        check_json_scan(expected_file, result_file, remove_file_date=True, regen=False)
