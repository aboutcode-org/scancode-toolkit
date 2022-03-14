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

from commoncode.testcase import FileDrivenTesting

from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from scancode.plugin_mark_source import is_source_directory
from scancode_config import REGEN_TEST_FIXTURES


class TestMarkSource(FileDrivenTesting):

    test_data_dir = join(dirname(__file__), 'data')

    def test_is_source_directory_above_threshold(self):
        files_count = 10
        src_count = 9
        assert is_source_directory(src_count, files_count)

    def test_is_source_directory_below_threshold(self):
        files_count = 10
        src_count = 5
        assert not is_source_directory(src_count, files_count)

    def test_scan_mark_source_without_info(self):
        test_dir = self.extract_test_tar('plugin_mark_source/JGroups.tgz')
        result = run_scan_click(
            ['--mark-source', test_dir, '--json', '-'], expected_rc=2)
        expected = 'Error: The option --mark-source requires the option(s) --info and is missing --info.'
        assert expected in result.output

    def test_scan_mark_source_with_info(self):
        test_dir = self.extract_test_tar('plugin_mark_source/JGroups.tgz')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin_mark_source/with_info.expected.json')
        run_scan_click(['--info', '--mark-source', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, regen=REGEN_TEST_FIXTURES)
