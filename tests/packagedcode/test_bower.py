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


class TestBower(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_bower_json_basic(self):
        test_file = self.get_test_loc('bower/basic/bower.json')
        package = bower.parse(test_file)
        expected_loc = self.get_test_loc('bower/basic/expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_bower_json_list_of_licenses(self):
        test_file = self.get_test_loc('bower/list-of-licenses/bower.json')
        package = bower.parse(test_file)
        expected_loc = self.get_test_loc('bower/list-of-licenses/expected.json')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_bower_json_author_objects(self):
        test_file = self.get_test_loc('bower/author-objects/bower.json')
        package = bower.parse(test_file)
        expected_loc = self.get_test_loc('bower/author-objects/expected.json')
        self.check_package(package, expected_loc, regen=False)
