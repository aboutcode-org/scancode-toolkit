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

    def test_parse_null_contributors_and_dependencies(self):
        json_data = {
            'name': 'test-pkg',
            'version': '1.0.0',
            'contributors': None,
            'dependencies': None,
        }
        package = haxe.HaxelibJsonHandler._parse(json_data)
        assert package.name == 'test-pkg'
        assert package.parties == []
        assert package.dependencies == []

    def test_parse_string_and_dict_contributors(self):
        json_data = {
            'name': 'test-pkg',
            'version': '1.0.0',
            'contributors': 'single_dev',
        }
        package = haxe.HaxelibJsonHandler._parse(json_data)
        assert len(package.parties) == 1
        assert package.parties[0].name == 'single_dev'
        assert package.parties[0].url == 'https://lib.haxe.org/u/single_dev'

        json_data_dict = {
            'name': 'test-pkg',
            'version': '1.0.0',
            'contributors': [{'name': 'dev_in_dict'}],
        }
        package_dict = haxe.HaxelibJsonHandler._parse(json_data_dict)
        assert len(package_dict.parties) == 1
        assert package_dict.parties[0].name == 'dev_in_dict'
        assert package_dict.parties[0].url == 'https://lib.haxe.org/u/dev_in_dict'

    def test_parse_list_dependencies(self):
        json_data = {
            'name': 'test-pkg',
            'version': '1.0.0',
            'dependencies': ['dep1', 'dep2'],
        }
        package = haxe.HaxelibJsonHandler._parse(json_data)
        assert len(package.dependencies) == 2
        dep1, dep2 = package.dependencies
        assert dep1.purl == 'pkg:haxe/dep1'
        assert dep1.extracted_requirement is None
        assert dep1.scope == 'dependencies'
        assert dep1.is_runtime is True
        assert dep1.is_optional is False
        assert dep1.is_pinned is False

        assert dep2.purl == 'pkg:haxe/dep2'
        assert dep2.extracted_requirement is None
        assert dep2.scope == 'dependencies'

    def test_parse_dependencies_version_constraints(self):
        json_data = {
            'name': 'test-pkg',
            'version': '1.0.0',
            'dependencies': {
                'pinned_dep': '1.2.3',
                'range_dep': '>= 2.0.0',
                'empty_dep': '',
            },
        }
        package = haxe.HaxelibJsonHandler._parse(json_data)
        assert len(package.dependencies) == 3
        deps = {d.purl: d for d in package.dependencies}

        pinned = deps['pkg:haxe/pinned_dep@1.2.3']
        assert pinned.extracted_requirement == '1.2.3'
        assert pinned.is_pinned is True
        assert pinned.scope == 'dependencies'

        ranged = deps['pkg:haxe/range_dep']
        assert ranged.extracted_requirement == '>= 2.0.0'
        assert ranged.is_pinned is False
        assert ranged.scope == 'dependencies'

        empty = deps['pkg:haxe/empty_dep']
        assert empty.extracted_requirement is None
        assert empty.is_pinned is False
        assert empty.scope == 'dependencies'

    def test_parse_string_tags(self):
        json_data = {
            'name': 'test-pkg',
            'version': '1.0.0',
            'tags': 'foo, bar, baz',
        }
        package = haxe.HaxelibJsonHandler._parse(json_data)
        assert package.keywords == ['foo', 'bar', 'baz']

