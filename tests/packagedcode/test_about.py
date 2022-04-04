#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os.path

from packagedcode import about
from packages_test_utils import PackageTester
from scancode_config import REGEN_TEST_FIXTURES
from scancode.cli_test_utils import run_scan_click
from scancode.cli_test_utils import check_json_scan


class TestAbout(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_can_detect_aboutfile(self):
        test_file = self.get_test_loc('about/aboutfiles/apipkg.ABOUT')
        assert about.AboutFileHandler.is_datafile(test_file)

    def test_parse_about_file_home_url(self):
        test_file = self.get_test_loc('about/aboutfiles/apipkg.ABOUT')
        package = about.AboutFileHandler.parse(test_file)
        expected_loc = self.get_test_loc('about/apipkg.ABOUT-expected')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_about_file_homepage_url(self):
        test_file = self.get_test_loc('about/aboutfiles/appdirs.ABOUT')
        package = about.AboutFileHandler.parse(test_file)
        expected_loc = self.get_test_loc('about/appdirs.ABOUT-expected')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_scan_cli_works(self):
        test_file = self.get_test_loc('about/aboutfiles')
        expected_file = self.get_test_loc('about/aboutfiles.expected.json')
        result_file = self.get_temp_file('results.json')
        run_scan_click(['--package', test_file, '--json', result_file])
        check_json_scan(
            expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES
        )
