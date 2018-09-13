#
# Copyright (c) 2018 nexB Inc. and others. All rights reserved.
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
from __future__ import unicode_literals

from os.path import dirname
from os.path import join

from commoncode.testcase import FileDrivenTesting
from scancode.cli_test_utils import run_scan_click
from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import check_jsonlines_scan


class TestScanSummary(FileDrivenTesting):

    test_data_dir = join(dirname(__file__), 'data')

    def test_copyright_summary_base(self):
        test_dir = self.get_test_loc('copyright_summary/scan')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('copyright_summary/summary.expected.json')
        run_scan_click(['-c', '--summary', '--json-pp', result_file, test_dir])
        check_json_scan(expected_file, result_file, strip_dates=True, regen=False)

    def test_copyright_summary_with_details(self):
        test_dir = self.get_test_loc('copyright_summary/scan')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('copyright_summary/summary_details.expected.json')
        run_scan_click(['-c', '--summary-with-details', '--json-pp', result_file, test_dir])
        check_json_scan(expected_file, result_file, strip_dates=True, regen=False)

    def test_copyright_summary_with_details_plain_json(self):
        test_dir = self.get_test_loc('copyright_summary/scan')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('copyright_summary/summary_details.expected2.json')
        run_scan_click(['-c', '--summary-with-details', '--json', result_file, test_dir])
        check_json_scan(expected_file, result_file, strip_dates=True, regen=False)

    def test_copyright_summary_does_not_crash(self):
        test_dir = self.get_test_loc('copyright_summary/scan2')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('copyright_summary/summary2.expected.json')
        run_scan_click(['-c', '--summary', '--json-pp', result_file, test_dir])
        check_json_scan(expected_file, result_file, strip_dates=True, regen=False)

    def test_full_summary_base(self):
        test_dir = self.get_test_loc('full_summary/scan')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('full_summary/summary.expected.json')
        run_scan_click(['-clip', '--summary', '--json-pp', result_file, test_dir])
        check_json_scan(expected_file, result_file, strip_dates=True, regen=False)

    def test_full_summary_with_details(self):
        test_dir = self.get_test_loc('full_summary/scan')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('full_summary/summary_details.expected.json')
        run_scan_click(['-clip', '--summary-with-details', '--json-pp', result_file, test_dir])
        check_json_scan(expected_file, result_file, strip_dates=True, regen=False)

    def test_copyright_summary_key_files(self):
        test_dir = self.get_test_loc('copyright_summary/scan')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('copyright_summary/summary_key_files.expected.json')
        run_scan_click(
            ['-c', '-i', '--classify', '--summary', '--summary-key-files',
             '--json-pp', result_file, test_dir])

        check_json_scan(expected_file, result_file, strip_dates=True, regen=False)

    def test_full_summary_key_files(self):
        test_dir = self.get_test_loc('full_summary/scan')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('full_summary/summary_key_files.expected.json')
        run_scan_click(
            ['-cli', '--classify', '--summary', '--summary-key-files',
             '--json-pp', result_file, test_dir])
        check_json_scan(expected_file, result_file, strip_dates=True, regen=False)

    def test_full_summary_key_files_json_lines(self):
        test_dir = self.get_test_loc('full_summary/scan')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('full_summary/summary_key_files-details.expected.json-lines')
        run_scan_click(
            ['-cli', '--classify', '--summary', '--summary-key-files',
             '--json-lines', result_file, test_dir])
        check_jsonlines_scan(expected_file, result_file, regen=False)

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
        check_json_scan(expected_file, result_file, strip_dates=True, regen=False)

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
        check_json_scan(expected_file, result_file, strip_dates=True, regen=False)
