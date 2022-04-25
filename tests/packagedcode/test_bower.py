#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os.path

from packagedcode import bower
from packages_test_utils import PackageTester
from scancode_config import REGEN_TEST_FIXTURES


class TestBower(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_is_manifest_bower_json(self):
        test_file = self.get_test_loc('bower/basic/bower.json')
        assert bower.BowerJsonHandler.is_datafile(test_file)

    def test_parse_bower_json_basic(self):
        test_file = self.get_test_loc('bower/basic/bower.json')
        package = bower.BowerJsonHandler.parse(test_file)
        expected_loc = self.get_test_loc('bower/basic/expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_bower_json_list_of_licenses(self):
        test_file = self.get_test_loc('bower/list-of-licenses/bower.json')
        package = bower.BowerJsonHandler.parse(test_file)
        expected_loc = self.get_test_loc('bower/list-of-licenses/expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_bower_json_author_objects(self):
        test_file = self.get_test_loc('bower/author-objects/bower.json')
        package = bower.BowerJsonHandler.parse(test_file)
        expected_loc = self.get_test_loc('bower/author-objects/expected.json')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_end2end_bower_scan_is_moved_to_parent(self):
        from scancode.cli_test_utils import check_json_scan
        from scancode.cli_test_utils import run_scan_click

        test_file = self.get_test_loc('bower/scan')
        expected_file = self.get_test_loc('bower/scan-expected.json')
        result_file = self.get_temp_file('results.json')
        run_scan_click(['--package', test_file, '--json-pp', result_file])
        check_json_scan(expected_file, result_file, regen=REGEN_TEST_FIXTURES)
