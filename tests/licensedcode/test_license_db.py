#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
import pytest
from pathlib import Path

from licensedcode.license_db import generate
from commoncode.testcase import FileBasedTesting
from commoncode.testcase import FileDrivenTesting
from scancode.cli_test_utils import load_both_and_check_json
from scancode.cli_test_utils import run_scan_click
from scancode_config import REGEN_TEST_FIXTURES


class LicenseDbTest(FileBasedTesting):

    test_data_dir = os.path.join(os.path.dirname(__file__), 'data/license_db')

    def test_generate_license_dump_from_license_data(self):
        
        licenses = self.get_test_loc('licenses')
        licenses_dump = self.get_test_loc('license_dump')

        generate(build_location=licenses_dump, licenses_data_dir=licenses, test=True)

        license_index_json = self.get_test_loc('license_dump/index.json')
        license_index_yaml = self.get_test_loc('license_dump/index.yml')
        license_index_html = self.get_test_loc('license_dump/index.html')
        
        index_json_path = Path(license_index_json)
        index_html_path = Path(license_index_html)
        index_yaml_path = Path(license_index_yaml)

        assert index_html_path.exists()
        assert index_json_path.exists()
        assert index_yaml_path.exists()

        expected_license_index_json = self.get_test_loc('index.json-expected.json')
        load_both_and_check_json(expected_license_index_json, license_index_json, regen=REGEN_TEST_FIXTURES)

class LicenseDBScanTest(FileDrivenTesting):

    @pytest.mark.scanslow
    def test_license_dump_option_works(self):
        license_dump_dir = self.get_temp_dir()
        args = ['--get-license-data', license_dump_dir]
        run_scan_click(args)
