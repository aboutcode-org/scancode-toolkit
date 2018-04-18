#
# Copyright (c) 2017 nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/scancode-toolkit/
# The ScanCode software is licensed under the Apache License version 2.0.
# Data generated with ScanCode require an acknowledgment.
# ScanCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# When you publish or redistribute any data created with ScanCode or any ScanCode
# derivative work, you must accompany this data with the following acknowledgment:
#
#  Generated with ScanCode and provided on an "AS IS" BASIS, WITHOUT WARRANTIES
#  OR CONDITIONS OF ANY KIND, either express or implied. No content created from
#  ScanCode should be considered or used as legal advice. Consult an Attorney
#  for any legal advice.
#  ScanCode is a free software code scanning tool from nexB Inc. and others.
#  Visit https://github.com/nexB/scancode-toolkit/ for support and download.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import codecs
from collections import OrderedDict
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
                OrderedDict([
                    ('import_path', u'code.google.com/p/go-netrc/netrc'),
                    ('revision', u'28676070ab99'),
                    ('comment', None)
                ]),
                OrderedDict([
                    ('import_path', u'github.com/kr/binarydist'),
                    ('revision', u'3380ade90f8b0dfa3e363fd7d7e941fa857d0d13'),
                    ('comment', None)
                ])
        ]}
        gd = godeps.Godep()
        gd.loads(test)
        results = gd.as_dict()
        assert expected == results

    def check_package(self, test_file, expected_file, regen=False):
        test_loc = self.get_test_loc(test_file)
        results = godeps.parse(location=test_loc)
        expected_loc = self.get_test_loc(expected_file)
        if regen:
            with codecs.open(expected_loc, 'wb', encoding='utf-8') as ex:
                json.dump(results, ex, indent=2)
        with codecs.open(expected_loc, encoding='utf-8') as ex:
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
