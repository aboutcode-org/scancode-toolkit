#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from copy import copy
from os import path

import pytest

from commoncode.testcase import FileDrivenTesting

from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from scancode_config import REGEN_TEST_FIXTURES
from summarycode.summarizer import remove_from_tallies
from summarycode.summarizer import get_primary_language
from summarycode.summarizer import get_holders_from_copyright


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
        check_json_scan(expected_file, result_file, remove_uuid=True, remove_file_date=True, regen=REGEN_TEST_FIXTURES)

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
        check_json_scan(expected_file, result_file, remove_uuid=True, remove_file_date=True, regen=REGEN_TEST_FIXTURES)

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
        check_json_scan(expected_file, result_file, remove_uuid=True, remove_file_date=True, regen=REGEN_TEST_FIXTURES)

    def test_summary_single_file_with_origin_info(self):
        test_dir = self.get_test_loc('summary/single_file/codebase')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('summary/single_file/single_file.expected.json')
        run_scan_click([
            '-clip',
            '--summary',
            '--classify',
            '--json-pp', result_file, test_dir
        ])
        check_json_scan(expected_file, result_file, remove_uuid=True, remove_file_date=True, regen=REGEN_TEST_FIXTURES)

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
        check_json_scan(expected_file, result_file, remove_uuid=True, remove_file_date=True, regen=REGEN_TEST_FIXTURES)

    def test_summary_with_package_data(self):
        test_dir = self.get_test_loc('summary/with_package_data/codebase')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('summary/with_package_data/with_package_data.expected.json')
        run_scan_click([
            '-clip',
            '--summary',
            '--classify',
            '--json-pp', result_file, test_dir
        ])
        check_json_scan(expected_file, result_file, remove_uuid=True, remove_file_date=True, regen=REGEN_TEST_FIXTURES)

    def test_summary_without_package_data(self):
        test_dir = self.get_test_loc('summary/without_package_data/codebase')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('summary/without_package_data/without_package_data.expected.json')
        run_scan_click([
            '-clip',
            '--summary',
            '--classify',
            '--json-pp', result_file, test_dir
        ])
        check_json_scan(expected_file, result_file, remove_uuid=True, remove_file_date=True, regen=REGEN_TEST_FIXTURES)

    def test_summary_multiple_package_data(self):
        test_dir = self.get_test_loc('summary/multiple_package_data/codebase')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('summary/multiple_package_data/multiple_package_data.expected.json')
        run_scan_click([
            '-clip',
            '--summary',
            '--classify',
            '--json-pp', result_file, test_dir
        ])
        check_json_scan(expected_file, result_file, remove_uuid=True, remove_file_date=True, regen=REGEN_TEST_FIXTURES)

    def test_summary_use_holder_from_package_resource(self):
        test_dir = self.get_test_loc('summary/use_holder_from_package_resource/codebase')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('summary/use_holder_from_package_resource/use_holder_from_package_resource.expected.json')
        run_scan_click([
            '-clip',
            '--summary',
            '--classify',
            '--json-pp', result_file, test_dir
        ])
        check_json_scan(expected_file, result_file, remove_uuid=True, remove_file_date=True, regen=REGEN_TEST_FIXTURES)

    def test_summary_clear_holder(self):
        test_dir = self.get_test_loc('summary/holders/clear_holder')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('summary/holders/clear_holder.expected.json')
        run_scan_click([
            '-clip',
            '--summary',
            '--classify',
            '--json-pp', result_file, test_dir
        ])
        check_json_scan(expected_file, result_file, remove_uuid=True, remove_file_date=True, regen=REGEN_TEST_FIXTURES)

    def test_summary_combined_holders(self):
        test_dir = self.get_test_loc('summary/holders/combined_holders')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('summary/holders/combined_holders.expected.json')
        run_scan_click([
            '-clip',
            '--summary',
            '--classify',
            '--json-pp', result_file, test_dir
        ])
        check_json_scan(expected_file, result_file, remove_uuid=True, remove_file_date=True, regen=REGEN_TEST_FIXTURES)

    def test_summary_without_copyright_or_holders(self):
        test_dir = self.get_test_loc('summary/summary_without_holder/pip-22.0.4/')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('summary/summary_without_holder/summary-without-holder-pypi.expected.json')
        run_scan_click([
            '-lp',
            '--summary',
            '--classify',
            '--json-pp', result_file, test_dir
        ])
        check_json_scan(expected_file, result_file, remove_uuid=True, remove_file_date=True, regen=REGEN_TEST_FIXTURES)


    def test_remove_from_tallies(self):
        tallies = [
            {
                'value': 'apache-2.0',
                'count': 5,
            },
            {
                'value': 'mit',
                'count': 2,
            },
            {
                'value': 'gpl-3.0',
                'count': 1,
            }
        ]

        test_entry_1 = {
            'value': 'apache-2.0',
            'count': 5,
        }
        expected_1 = [
            {
                'value': 'mit',
                'count': 2,
            },
            {
                'value': 'gpl-3.0',
                'count': 1,
            }
        ]
        result_1 = remove_from_tallies(test_entry_1, copy(tallies))
        assert(result_1, expected_1)

        test_entry_2 = [
            {
                'value': 'mit',
                'count': 2,
            },
            {
                'value': 'gpl-3.0',
                'count': 1,
            }
        ]
        expected_2 = [
            {
                'value': 'apache-2.0',
                'count': 5,
            },
        ]
        result_2 = remove_from_tallies(test_entry_2, copy(tallies))
        assert(result_2, expected_2)

        test_entry_3 = 'apache-2.0'
        expected_3 = [
            {
                'value': 'mit',
                'count': 2,
            },
            {
                'value': 'gpl-3.0',
                'count': 1,
            }
        ]
        result_3 = remove_from_tallies(test_entry_3, copy(tallies))
        assert(result_3, expected_3)

    def test_get_primary_language(self):
        language_tallies = [
            {
                'value': 'Python',
                'count': 5,
            },
            {
                'value': 'Java',
                'count': 2,
            },
            {
                'value': 'C++',
                'count': 1,
            }
        ]
        expected_1 = 'Python'
        result_1 = get_primary_language(language_tallies)
        assert(result_1, expected_1)

    def test_get_holders_from_copyright(self):
        test_copyright = 'Copyright (c) 2017, The University of Chicago. All rights reserved.'
        expected_1 = ['The University of Chicago']
        result_1 = get_holders_from_copyright(test_copyright)
        assert(result_1, expected_1)

        test_copyrights = [
            'Copyright (c) 2017, The University of Chicago. All rights reserved.',
            'Copyright (c) MIT',
            'Copyright (c) Apache Software Foundation',
        ]
        expected_2 = ['The University of Chicago', 'MIT', 'Apache Software Foundation']
        result_2 = get_holders_from_copyright(test_copyrights)
        assert(result_2, expected_2)
