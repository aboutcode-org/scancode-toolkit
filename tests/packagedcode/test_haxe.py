#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 AND CC-BY-4.0
#
# Visit https://aboutcode.org and https://github.com/nexB/scancode-toolkit for
# support and download. ScanCode is a trademark of nexB Inc.
#
# The ScanCode software is licensed under the Apache License version 2.0.
# The ScanCode open data is licensed under CC-BY-4.0.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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
        assert test_dir == proot.location
