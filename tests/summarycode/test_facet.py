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

from scancode.cli_test_utils import run_scan_click
from scancode.cli_test_utils import check_json_scan
from scancode_config import REGEN_TEST_FIXTURES


class TestFacet(FileDrivenTesting):

    test_data_dir = join(dirname(__file__), 'data')

    def test_facet_cli_option(self):
        test_dir = self.get_test_loc('facet/cli')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('facet/cli.expected.json')
        run_scan_click([
            '--facet', 'dev=*.c',
            '--facet', 'tests=*/tests/*',
            '--facet', 'data=*.json',
            '--facet', 'docs=*/docs/*',
            '--json-pp', result_file, test_dir])
        check_json_scan(expected_file, result_file, remove_file_date=True, regen=REGEN_TEST_FIXTURES)
