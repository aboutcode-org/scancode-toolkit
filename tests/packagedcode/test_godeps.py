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

import io
import json
import os

from commoncode.testcase import FileBasedTesting
from packagedcode import godeps


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
                    "Rev": "28676070ab99"
                },
                {
                    "ImportPath": "github.com/kr/binarydist",
                    "Rev": "3380ade90f8b0dfa3e363fd7d7e941fa857d0d13"
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
        assert expected == results

    def check_package(self, test_file, expected_file, regen=False):
        test_loc = self.get_test_loc(test_file)
        results = godeps.parse(location=test_loc)
        expected_loc = self.get_test_loc(expected_file)
        if regen:
            wmode = 'w'
            with open(expected_loc, wmode) as ex:
                json.dump(results, ex, indent=2)
        with io.open(expected_loc, encoding='utf-8') as ex:
            expected = json.load(ex)
        assert sorted(expected.items()) == sorted(results.items())

    def test_godeps_godeps_godeps_json_comments(self):
        self.check_package(
            'godeps/Godeps.json-comments',
            'godeps/expected/Godeps.json-commentsexpected.json')

    def test_godeps_godeps_godeps_json_full(self):
        self.check_package(
            'godeps/Godeps.json-full',
            'godeps/expected/Godeps.json-fullexpected.json')

    def test_godeps_godeps_godeps_json_full2(self):
        self.check_package(
            'godeps/Godeps.json-full2',
            'godeps/expected/Godeps.json-full2expected.json')

    def test_godeps_godeps_godeps_json_medium(self):
        self.check_package(
            'godeps/Godeps.json-medium',
            'godeps/expected/Godeps.json-mediumexpected.json')

    def test_godeps_godeps_godeps_json_medium2(self):
        self.check_package(
            'godeps/Godeps.json-medium2',
            'godeps/expected/Godeps.json-medium2expected.json')

    def test_godeps_godeps_godeps_json_mini(self):
        self.check_package(
            'godeps/Godeps.json-mini',
            'godeps/expected/Godeps.json-miniexpected.json')

    def test_godeps_godeps_godeps_json_package1(self):
        self.check_package(
            'godeps/Godeps.json-package1',
            'godeps/expected/Godeps.json-package1expected.json')

    def test_godeps_godeps_godeps_json_package2(self):
        self.check_package(
            'godeps/Godeps.json-package2',
            'godeps/expected/Godeps.json-package2expected.json')

    def test_godeps_godeps_godeps_json_package3(self):
        self.check_package(
            'godeps/Godeps.json-package3',
            'godeps/expected/Godeps.json-package3expected.json')

    def test_godeps_godeps_godeps_json_simple(self):
        self.check_package(
            'godeps/Godeps.json-simple',
            'godeps/expected/Godeps.json-simpleexpected.json')
