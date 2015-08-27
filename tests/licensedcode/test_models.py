#
# Copyright (c) 2015 nexB Inc. and others. All rights reserved.
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

from __future__ import absolute_import, print_function

import os

from commoncode.testcase import FileBasedTesting
from textcode.analysis import Token
from licensedcode import models


class TestLicense(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_load_license(self):
        test_dir = self.get_test_loc('models/licenses')
        lics = models.load_licenses(test_dir)
        # one license is obsolete and not loaded
        self.assertEqual([u'apache-2.0',
                          u'bsd-ack-carrot2',
                          u'w3c-docs-19990405'],
                         sorted(lics.keys()))

        self.assertTrue(all(isinstance(l, models.License)
                            for l in lics.values()))
        # test a sample of a licenses field
        self.assertTrue('1994-2002 World Wide Web Consortium'
                        in lics[u'w3c-docs-19990405'].text)

    def test_get_texts(self):
        test_dir = self.get_test_loc('models/licenses')
        lics = models.load_licenses(test_dir)
        for lic in lics.values():
            self.assertTrue('distribut' in lic.text.lower())

    def test_get_rules_from_license_texts(self):
        test_dir = self.get_test_loc('models/licenses')
        lics = models.load_licenses(test_dir)
        rules = [r for r in models.get_rules_from_license_texts(lics)]
        self.assertEqual(4, len(rules))
        for rule in rules:
            self.assertTrue('distribut' in rule.text.lower())


class TestRule(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def create_test_file(self, text):
        tf = self.get_temp_file()
        with open(tf, 'wb') as of:
            of.write(text)
        return tf

    def test_create_template_rule(self):
        ttr = models.Rule(text_file=self.create_test_file(u'A one. A {{}}two. A three.'), template=True)
        toks = [
            Token(start=0, start_line=0, start_char=0, end_line=0, end_char=8, end=2, gap=5, value=u'a one a', length=3),
            Token(start=3, start_line=0, start_char=13, end_line=0, end_char=25, end=5, gap=0, value=u'two a three', length=3)
        ]
        assert toks == list(ttr.get_tokens())
        for i in range(len(toks)):
            self.assertEqual(toks[i], ttr.tokens[i])

    def test_create_plain_rule(self):
        ftr = models.Rule(text_file=self.create_test_file('A one. A two. A three.'))
        toks = [
            Token(start=0, start_line=0, start_char=0, end_line=0, end_char=12, end=3, gap=0, value=u'a one a two', length=4),
            Token(start=1, start_line=0, start_char=2, end_line=0, end_char=15, end=4, gap=0, value=u'one a two a', length=4),
            Token(start=2, start_line=0, start_char=7, end_line=0, end_char=21, end=5, gap=0, value=u'a two a three', length=4),
        ]
        self.assertEqual(toks, list(ftr.get_tokens()))
        for i in range(len(toks)):
            self.assertEqual(toks[i], ftr.tokens[i])

    def test_load_rules(self):
        test_dir = self.get_test_loc('models/rules')
        rules = models.load_rules(test_dir)
        # one license is obsolete and not loaded
        assert 3 == len(rules)
        assert all(isinstance(r, models.Rule) for r in rules)
        # test a sample of a licenses field
        expected = [[u'lzma-sdk-original'], [u'gpl-2.0'], [u'oclc-2.0']]
        assert sorted(expected) == sorted(r.licenses for r in rules)

    def test_template_rule_is_loaded_correctly(self):
        test_dir = self.get_test_loc('models/rule_template')
        rules = models.load_rules(test_dir)
        assert 1 == len(rules)
        rule = rules[0]
        assert rule.template

    def test_rule_identifier_includes_rule_type(self):
        r1 = models.Rule(text_file=self.create_test_file('Some text'), template=True)
        r2 = models.Rule(text_file=self.create_test_file('Some text'), template=False)
        assert models.rule_identifier(r1) != models.rule_identifier(r2)

    def test_rule_identifier_ignores_small_text_differences(self):
        r1 = models.Rule(text_file=self.create_test_file('Some text'), template=False)
        r2 = models.Rule(text_file=self.create_test_file(' some  \n  text '), template=False)
        assert models.rule_identifier(r1) == models.rule_identifier(r2)

    def test_rule_identifier_includes_structure(self):
        r1 = models.Rule(text_file=self.create_test_file('Some text'), license_choice=False)
        r2 = models.Rule(text_file=self.create_test_file('Some text'), license_choice=True)
        assert models.rule_identifier(r1) != models.rule_identifier(r2)
