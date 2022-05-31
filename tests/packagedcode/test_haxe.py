#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from os import path

from packagedcode import haxe
from packages_test_utils import PackageTester
from scancode_config import REGEN_TEST_FIXTURES


class TestHaxe(PackageTester):
    test_data_dir = path.join(path.dirname(__file__), 'data')

    def test_is_manifest_haxelib_json(self):
        test_file = self.get_test_loc('haxe/basic/haxelib.json')
        assert haxe.HaxelibJsonHandler.is_datafile(test_file)

    def test_parse_basic(self):
        test_file = self.get_test_loc('haxe/basic/haxelib.json')
        expected_loc = self.get_test_loc('haxe/basic/haxelib.json.expected')
        package = haxe.HaxelibJsonHandler.parse(test_file)
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_basic2(self):
        test_file = self.get_test_loc('haxe/basic2/haxelib.json')
        expected_loc = self.get_test_loc('haxe/basic2/haxelib.json.expected')
        package = haxe.HaxelibJsonHandler.parse(test_file)
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_deps(self):
        test_file = self.get_test_loc('haxe/deps/haxelib.json')
        expected_loc = self.get_test_loc('haxe/deps/haxelib.json.expected')
        package = haxe.HaxelibJsonHandler.parse(test_file)
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_tags(self):
        test_file = self.get_test_loc('haxe/tags/haxelib.json')
        expected_loc = self.get_test_loc('haxe/tags/haxelib.json.expected')
        package = haxe.HaxelibJsonHandler.parse(test_file)
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)
