#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import io
import json
import os

from commoncode.testcase import FileBasedTesting

from packagedcode import godeps
from scancode_config import REGEN_TEST_FIXTURES


class TestGodeps(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_basic(self):
        test = '''
        {
        "ImportPath": "github.com/kr/hk",
        "GoVersion": "go1.1.2",
        "Deps": [
                {
                    "ImportPath": "code.google.com/p/go-netrc/netrc",
                    "Rev": "28676070ab99",
                    "Comment": null
                },
                {
                    "ImportPath": "github.com/kr/binarydist",
                    "Rev": "3380ade90f8b0dfa3e363fd7d7e941fa857d0d13",
                    "Comment": null
                }
            ]
        }'''

        expected = {
            'packages': [],
            'import_path': u'github.com/kr/hk',
            'go_version': u'go1.1.2',
            'dependencies': [
                dict([
                    ('import_path', u'code.google.com/p/go-netrc/netrc'),
                    ('revision', u'28676070ab99'),
                    ('comment', None)
                ]),
                dict([
                    ('import_path', u'github.com/kr/binarydist'),
                    ('revision', u'3380ade90f8b0dfa3e363fd7d7e941fa857d0d13'),
                    ('comment', None)
                ])
        ]}
        gd = godeps.Godep()
        gd.loads(test)
        results = gd.to_dict()
        assert results == expected

    def test_godeps_loads_with_unknown_top_level_fields(self):
        test = '''
        {
            "ImportPath": "github.com/example/repo",
            "GoVersion": "go1.16",
            "ExtraField": "extra_value",
            "UnknownNumber": 42
        }'''
        gd = godeps.Godep()
        gd.loads(test)
        assert gd.import_path == 'github.com/example/repo'
        assert gd.go_version == 'go1.16'

    def test_godeps_parse_deps_with_unknown_fields(self):
        test = '''
        {
            "ImportPath": "github.com/example/repo",
            "Deps": [
                {
                    "ImportPath": "github.com/pkg/errors",
                    "Rev": "v0.9.1",
                    "Comment": "tagged release",
                    "ExtraMetadata": "custom_data",
                    "VCS": "git"
                }
            ]
        }'''
        gd = godeps.Godep()
        gd.loads(test)
        assert len(gd.dependencies) == 1
        dep = gd.dependencies[0]
        assert dep.import_path == 'github.com/pkg/errors'
        assert dep.revision == 'v0.9.1'
        assert dep.comment == 'tagged release'

    def test_godeps_loads_with_null_deps(self):
        test = '{"ImportPath": "github.com/example/repo", "Deps": null}'
        gd = godeps.Godep()
        gd.loads(test)
        assert gd.dependencies == []

    def test_godeps_handler_parse_skips_empty_or_whitespace_import_path(self):
        test = '''
        {
            "ImportPath": "github.com/example/repo",
            "Deps": [
                {"ImportPath": "", "Rev": "123"},
                {"ImportPath": "   ", "Rev": "456"},
                {"Rev": "789"},
                {"ImportPath": "github.com/valid/dep", "Rev": "abc"}
            ]
        }'''
        test_file = self.get_temp_file()
        with open(test_file, 'w') as f:
            f.write(test)

        packages = list(godeps.GodepsHandler.parse(test_file))
        assert len(packages) == 1
        package = packages[0]
        assert len(package.dependencies) == 1
        dep = package.dependencies[0]
        assert dep.purl == 'pkg:golang/github.com/valid/dep'
        assert dep.extracted_requirement == 'abc'

    def test_godeps_loads_malformed_and_non_dict_json(self):
        gd = godeps.Godep()
        assert gd.loads('') == gd
        assert gd.loads('   ') == gd
        assert gd.loads('invalid json {') == gd
        assert gd.loads('[1, 2, 3]') == gd
        assert gd.loads('null') == gd


    def check_parse(self, test_file, regen=REGEN_TEST_FIXTURES):
        """
        Test godeps parsing and package data creation
        """

        test_loc = self.get_test_loc(test_file)

        expected_parse_file = f'{test_file}-expected'
        expected_loc = self.get_test_loc(expected_parse_file)
        results = godeps.parse(location=test_loc)

        if regen:
            with open(expected_loc, 'w') as ex:
                json.dump(results, ex, indent=2)
        with io.open(expected_loc, encoding='utf-8') as ex:
            expected = json.load(ex)
        assert sorted(results.items()) == sorted(expected.items())

        expected_package_file = f'{test_file}-expected-package'
        expected_loc = self.get_test_loc(expected_package_file)
        results = list(godeps.GodepsHandler.parse(location=test_loc))
        results_mapping = [r.to_dict() for r in results]

        if regen:
            with open(expected_loc, 'w') as ex:
                json.dump(results_mapping, ex, indent=2)
        with io.open(expected_loc, encoding='utf-8') as ex:
            expected = json.load(ex)

        assert results_mapping == expected

    def test_godeps_godeps_godeps_json_comments(self):
        self.check_parse('godeps/comments/Godeps.json')

    def test_godeps_godeps_godeps_json_full(self):
        self.check_parse('godeps/full/Godeps.json')

    def test_godeps_godeps_godeps_json_full2(self):
        self.check_parse('godeps/full2/Godeps.json')

    def test_godeps_godeps_godeps_json_medium(self):
        self.check_parse('godeps/medium/Godeps.json')

    def test_godeps_godeps_godeps_json_medium2(self):
        self.check_parse('godeps/medium2/Godeps.json')

    def test_godeps_godeps_godeps_json_mini(self):
        self.check_parse('godeps/mini/Godeps.json')

    def test_godeps_godeps_godeps_json_package1(self):
        self.check_parse('godeps/package1/Godeps.json')

    def test_godeps_godeps_godeps_json_package2(self):
        self.check_parse('godeps/package2/Godeps.json')

    def test_godeps_godeps_godeps_json_package3(self):
        self.check_parse('godeps/package3/Godeps.json')

    def test_godeps_godeps_godeps_json_simple(self):
        self.check_parse('godeps/simple/Godeps.json')
