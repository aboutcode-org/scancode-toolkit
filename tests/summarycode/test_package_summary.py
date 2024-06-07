#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import pytest
from os import path

from commoncode.testcase import FileDrivenTesting
from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from scancode_config import REGEN_TEST_FIXTURES
from summarycode.package_summary import PackageSummary

class TestPackageSummary(FileDrivenTesting):
    test_data_dir = path.join(path.dirname(__file__), 'data')

    def test_package_summary_plugin(self):
        test_dir = self.get_test_loc('package_summary/basic-plugin-testing/codebase/') 
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('package_summary/basic-plugin-testing/expected.json')
        
        # Run the scan with the package summary option
        run_scan_click([
            '--package-summary',
            '--json-pp', result_file, test_dir
        ])
        
        check_json_scan(expected_file, result_file, remove_uuid=True, remove_file_date=True, regen=REGEN_TEST_FIXTURES)
