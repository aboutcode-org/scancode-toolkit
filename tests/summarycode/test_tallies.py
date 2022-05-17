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


class TestTallies(FileDrivenTesting):

    test_data_dir = path.join(path.dirname(__file__), 'data')

    def test_copyright_summary_base(self):
        test_dir = self.get_test_loc('tallies/copyright_tallies/scan')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('tallies/copyright_tallies/tallies.expected.json')
        run_scan_click(['-c', '--tallies', '--json-pp', result_file, test_dir])
        check_json_scan(expected_file, result_file, remove_file_date=True, regen=REGEN_TEST_FIXTURES)

    def test_copyright_summary_with_details(self):
        test_dir = self.get_test_loc('tallies/copyright_tallies/scan')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('tallies/copyright_tallies/tallies_details.expected.json')
        run_scan_click(['-c', '--tallies-with-details', '--json-pp', result_file, test_dir])
        check_json_scan(expected_file, result_file, remove_file_date=True, regen=REGEN_TEST_FIXTURES)

    def test_copyright_summary_with_details_plain_json(self):
        test_dir = self.get_test_loc('tallies/copyright_tallies/scan')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('tallies/copyright_tallies/tallies_details.expected2.json')
        run_scan_click(['-c', '--tallies-with-details', '--json', result_file, test_dir])
        check_json_scan(expected_file, result_file, remove_file_date=True, regen=REGEN_TEST_FIXTURES)

    def test_copyright_summary_does_not_crash(self):
        test_dir = self.get_test_loc('tallies/copyright_tallies/scan2')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('tallies/copyright_tallies/tallies2.expected.json')
        run_scan_click(['-c', '--tallies', '--json-pp', result_file, test_dir])
        check_json_scan(expected_file, result_file, remove_file_date=True, regen=REGEN_TEST_FIXTURES)

    def test_full_summary_base(self):
        test_dir = self.get_test_loc('tallies/full_tallies/scan')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('tallies/full_tallies/tallies.expected.json')
        run_scan_click(['-clip', '--tallies', '--json-pp', result_file, test_dir])
        check_json_scan(expected_file, result_file, remove_uuid=True, remove_file_date=True, regen=REGEN_TEST_FIXTURES)

    def test_full_summary_with_details(self):
        test_dir = self.get_test_loc('tallies/full_tallies/scan')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('tallies/full_tallies/tallies_details.expected.json')
        run_scan_click(['-clip', '--tallies-with-details', '--json-pp', result_file, test_dir])
        check_json_scan(expected_file, result_file, remove_uuid=True, remove_file_date=True, regen=REGEN_TEST_FIXTURES)

    def test_copyright_summary_key_files(self):
        test_dir = self.get_test_loc('tallies/copyright_tallies/scan')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('tallies/copyright_tallies/tallies_key_files.expected.json')
        run_scan_click(
            ['-c', '-i', '--classify', '--tallies', '--tallies-key-files',
             '--json-pp', result_file, test_dir])

        check_json_scan(expected_file, result_file, remove_file_date=True, regen=REGEN_TEST_FIXTURES)

    def test_full_summary_key_files(self):
        test_dir = self.get_test_loc('tallies/full_tallies/scan')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('tallies/full_tallies/tallies_key_files.expected.json')
        run_scan_click(
            ['-cli', '--classify', '--tallies', '--tallies-key-files',
             '--json-pp', result_file, test_dir])
        check_json_scan(expected_file, result_file, remove_file_date=True, regen=REGEN_TEST_FIXTURES)

    def test_full_summary_key_files_json_lines(self):
        test_dir = self.get_test_loc('tallies/full_tallies/scan')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('tallies/full_tallies/tallies_key_files-details.expected.json-lines')
        run_scan_click(
            ['-cli', '--classify', '--tallies', '--tallies-key-files',
             '--json-lines', result_file, test_dir])
        check_jsonlines_scan(expected_file, result_file, remove_file_date=True, regen=REGEN_TEST_FIXTURES)

    def test_full_summary_by_facet(self):
        test_dir = self.get_test_loc('tallies/full_tallies/scan')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('tallies/full_tallies/tallies_by_facet.expected.json')
        run_scan_click([
            '-clpieu',
            '--facet', 'dev=*.java',
            '--facet', 'dev=*.cs',
            '--facet', 'dev=*ada*',
            '--facet', 'data=*.S',
            '--facet', 'tests=*infback9*',
            '--facet', 'docs=*README',
            '--tallies',
            '--tallies-by-facet',
            '--json-pp', result_file, test_dir
        ])
        check_json_scan(expected_file, result_file, remove_uuid=True, remove_file_date=True, regen=REGEN_TEST_FIXTURES)

    def test_end2end_summary_and_classify_works_with_empty_dir_and_empty_values(self):
        test_dir = self.extract_test_tar('tallies/end-2-end/bug-1141.tar.gz')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('tallies/end-2-end/bug-1141.expected.json')
        run_scan_click([
            '-clip',
            '--classify',
            '--facet', 'dev=*.java',
            '--tallies',
            '--tallies-key-files',
            '--json-pp', result_file, test_dir
        ])
        check_json_scan(expected_file, result_file, remove_uuid=True, remove_file_date=True, regen=REGEN_TEST_FIXTURES)

    def test_summary_with_packages_reports_packages_with_files(self):
        test_dir = self.get_test_loc('tallies/packages/scan')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('tallies/packages/expected.json')
        run_scan_click([
            '--package',
            '--tallies',
            '--json-pp', result_file, test_dir
        ])
        check_json_scan(expected_file, result_file, remove_uuid=True, remove_file_date=True, regen=REGEN_TEST_FIXTURES)
