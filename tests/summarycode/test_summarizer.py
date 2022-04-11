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

    def test_end2end_summary_and_classify_works_with_empty_dir_and_empty_values(self):
        test_dir = self.extract_test_tar('summary/end-2-end/bug-1141.tar.gz')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('summary/end-2-end/bug-1141.expected.json')
        run_scan_click([
            '-clip',
            '--summary',
            '--classify',
            '--json-pp', result_file, test_dir
        ])
        check_json_scan(expected_file, result_file, remove_instance_uuid=True, remove_file_date=True, regen=REGEN_TEST_FIXTURES)

    def test_summary_license_ambiguity_unambiguous(self):
        test_dir = self.get_test_loc('summary/license_ambiguity/unambiguous')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('summary/license_ambiguity/unambiguous.expected.json')
        run_scan_click([
            '-clip',
            '--summary',
            '--classify',
            '--json-pp', result_file, test_dir
        ])
        check_json_scan(expected_file, result_file, remove_file_date=True, regen=REGEN_TEST_FIXTURES)

    def test_summary_license_ambiguity_ambiguous(self):
        test_dir = self.get_test_loc('summary/license_ambiguity/ambiguous')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('summary/license_ambiguity/ambiguous.expected.json')
        run_scan_click([
            '-clip',
            '--summary',
            '--classify',
            '--json-pp', result_file, test_dir
        ])
        check_json_scan(expected_file, result_file, remove_file_date=True, regen=REGEN_TEST_FIXTURES)

    def test_summary_simple_single_file_with_origin_info(self):
        test_dir = self.get_test_loc('summary/simple/single_file')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('summary/simple/single_file.expected.json')
        run_scan_click([
            '-clip',
            '--summary',
            '--classify',
            '--json-pp', result_file, test_dir
        ])
        check_json_scan(expected_file, result_file, remove_file_date=True, regen=REGEN_TEST_FIXTURES)

    def test_summary_conflicting_license_categories(self):
        test_dir = self.get_test_loc('summary/conflicting_license_categories/codebase')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('summary/conflicting_license_categories/conflicting_license_categories.expected.json')
        run_scan_click([
            '-clip',
            '--summary',
            '--classify',
            '--json-pp', result_file, test_dir
        ])
        check_json_scan(expected_file, result_file, remove_file_date=True, regen=REGEN_TEST_FIXTURES)

    def test_summary_simple_with_package_data(self):
        test_dir = self.get_test_loc('summary/simple/with_package_data')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('summary/simple/with_package_data.expected.json')
        run_scan_click([
            '-clip',
            '--summary',
            '--classify',
            '--json-pp', result_file, test_dir
        ])
        check_json_scan(expected_file, result_file, remove_file_date=True, regen=REGEN_TEST_FIXTURES)

    def test_summary_simple_without_package_data(self):
        test_dir = self.get_test_loc('summary/simple/without_package_data')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('summary/simple/without_package_data.expected.json')
        run_scan_click([
            '-clip',
            '--summary',
            '--classify',
            '--json-pp', result_file, test_dir
        ])
        check_json_scan(expected_file, result_file, remove_file_date=True, regen=REGEN_TEST_FIXTURES)
