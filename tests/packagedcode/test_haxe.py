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
from commoncode.resource import Codebase
from packages_test_utils import PackageTester


class TestHaxe(PackageTester):
    test_data_dir = path.join(path.dirname(__file__), 'data')

    def test_parse_basic(self):
        test_file = self.get_test_loc('haxe/basic/haxelib.json')
        expected_loc = self.get_test_loc('haxe/basic/haxelib.json.expected')
        package = haxe.parse(test_file)
        self.check_package(package, expected_loc)

    def test_parse_basic2(self):
        test_file = self.get_test_loc('haxe/basic2/haxelib.json')
        expected_loc = self.get_test_loc('haxe/basic2/haxelib.json.expected')
        package = haxe.parse(test_file)
        self.check_package(package, expected_loc)

    def test_parse_deps(self):
        test_file = self.get_test_loc('haxe/deps/haxelib.json')
        expected_loc = self.get_test_loc('haxe/deps/haxelib.json.expected')
        package = haxe.parse(test_file)
        self.check_package(package, expected_loc)

    def test_parse_tags(self):
        test_file = self.get_test_loc('haxe/tags/haxelib.json')
        expected_loc = self.get_test_loc('haxe/tags/haxelib.json.expected')
        package = haxe.parse(test_file)
        self.check_package(package, expected_loc)

    def test_root_dir(self):
        test_file = self.get_test_loc('haxe/tags/haxelib.json')
        test_dir = self.get_test_loc('haxe/tags')
        codebase = Codebase(test_dir)
        manifest_resource = codebase.get_resource_from_path(test_file, absolute=True)
        proot = haxe.HaxePackage.get_package_root(manifest_resource, codebase)
        assert proot.location == test_dir
