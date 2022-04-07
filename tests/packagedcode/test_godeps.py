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
