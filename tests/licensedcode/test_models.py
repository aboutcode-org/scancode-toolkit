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

from collections import OrderedDict
import json
import os

from commoncode.testcase import FileBasedTesting

from licensedcode import cache
from licensedcode import index
from licensedcode import models
from licensedcode.models import Rule

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


def check_json(expected, results, regen=False):
    if regen:
        with open(expected, 'wb') as ex:
            json.dump(results, ex, indent=2, separators=(',', ': '))
    with open(expected) as ex:
        expected = json.load(ex, object_pairs_hook=OrderedDict)
    assert expected == results


class TestLicense(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_load_license(self):
        test_dir = self.get_test_loc('models/licenses')
        lics = models.load_licenses(test_dir)
        # Note: one license is obsolete and not loaded. Other are various exception/version cases
        results = sorted(l.to_dict() for l in lics.values())
        expected = self.get_test_loc('models/licenses.load.expected.json')
        check_json(expected, results)

    def test_dump_license(self):
        test_dir = self.get_test_loc('models/licenses', copy=True)
        lics = models.load_licenses(test_dir, with_deprecated=True)
        for l in lics.values():
            l.dump()
        lics = models.load_licenses(test_dir, with_deprecated=True)
        # Note: one license is obsolete and not loaded. Other are various exception/version cases
        results = sorted(l.to_dict() for l in lics.values())
        expected = self.get_test_loc('models/licenses.dump.expected.json')
        check_json(expected, results)

    def test_relocate_license(self):
        test_dir = self.get_test_loc('models/licenses')
        lics = models.load_licenses(test_dir, with_deprecated=True)
        new_dir = self.get_temp_dir('relocate_lics')
        for l in lics.values():
            l.relocate(new_dir)

        lics = models.load_licenses(new_dir, with_deprecated=True)
        # Note: one license is obsolete and not loaded. Other are various exception/version cases
        results = sorted(l.to_dict() for l in lics.values())
        expected = self.get_test_loc('models/licenses.expected.json')
        check_json(expected, results)

    def test_relocate_license_with_key(self):
        test_dir = self.get_test_loc('models/licenses')
        lics = models.load_licenses(test_dir, with_deprecated=True)
        new_dir = self.get_temp_dir('relocate_lics')
        for l in lics.values():
            l.relocate(new_dir, new_key='new_key-' + l.key)

        lics = models.load_licenses(new_dir, with_deprecated=True)
        # Note: one license is obsolete and not loaded. Other are various exception/version cases
        results = sorted(l.to_dict() for l in lics.values())
        expected = self.get_test_loc('models/licenses-new-key.expected.json')
        check_json(expected, results)

    def test_License_text(self):
        test_dir = self.get_test_loc('models/licenses')
        lics = models.load_licenses(test_dir)
        for lic in lics.values():
            assert 'distribut' in lic.text.lower()

    def test_build_rules_from_licenses(self):
        test_dir = self.get_test_loc('models/licenses')
        lics = models.load_licenses(test_dir)
        rules = models.build_rules_from_licenses(lics)
        results = sorted(r.to_dict() for r in rules)
        expected = self.get_test_loc('models/license_rules.expected.json')
        check_json(expected, results)

    def test_validate_license_library(self):
        errors, warnings, infos = models.License.validate(
            cache.get_licenses_db(), verbose=True)
        assert {} == errors
        assert {} == warnings
        assert infos

    def test_validate_license_library_can_return_errors(self):
        test_dir = self.get_test_loc('models/validate')
        lics = models.load_licenses(test_dir)
        errors, warnings, infos = models.License.validate(
            lics, no_dupe_urls=True, verbose=True)
        expected_errors = {
            'GLOBAL': [
                'Duplicate texts in multiple licenses:apache-2.0: TEXT, bsd-ack-carrot2: TEXT',
                'Duplicate short name:GPL 1.0 in licenses:gpl-1.0-plus, gpl-1.0',
                'Duplicate name:GNU General Public License 1.0 in licenses:gpl-1.0-plus, gpl-1.0'],
            'bsd-ack-carrot2': [
                'No short name',
                'No name',
                'No category',
                'No owner'],
            'gpl-1.0': [
                'Unknown license category: GNU Copyleft.\nUse one of these valid categories:\n'
                'Commercial\nCopyleft\nCopyleft Limited\nFree Restricted\nHardware License\n'
                'Patent License\nPermissive\nProprietary Free\nPublic Domain\nUnstated License'],
            'w3c-docs-19990405': [
                'Unknown license category: Permissive Restricted.\nUse one of these valid categories:\n'
                'Commercial\nCopyleft\nCopyleft Limited\nFree Restricted\nHardware License\n'
                'Patent License\nPermissive\nProprietary Free\nPublic Domain\nUnstated License']
        }

        assert expected_errors == errors
        expected_warnings = {
            'gpl-1.0': [
                'Some empty text_urls values',
                'Some empty other_urls values',
                'Homepage URL also in text_urls',
                'Homepage URL also in other_urls',
                'Homepage URL same as faq_url',
                'Homepage URL same as osi_url',
                'osi_url same as faq_url',
                'Some duplicated URLs']
        }

        assert expected_warnings == warnings

        expected_infos = {'w3c-docs-19990405': [u'No license text']}
        assert expected_infos == infos

    def test_load_licenses_fails_if_directory_contains_orphaned_files(self):
        test_dir = self.get_test_loc('models/orphaned_licenses')
        try:
            list(models.load_licenses(test_dir))
            self.fail('Exception not raised')
        except Exception as e:
            assert 'Some License data or text files are orphaned' in str(e)


class TestRule(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_create_rule_ignore_punctuation(self):
        test_rule = models.Rule(stored_text='A one. A {{}}two. A three.')
        expected = ['one', 'two', 'three']
        assert expected == list(test_rule.tokens())
        assert 3 == test_rule.length

    def test_create_plain_rule_with_text_file(self):

        def create_test_file(text):
            tf = self.get_temp_file()
            with open(tf, 'wb') as of:
                of.write(text)
            return tf

        test_rule = models.Rule(text_file=create_test_file('A one. A two. A three.'))
        expected = ['one', 'two', 'three']
        assert expected == list(test_rule.tokens())
        assert 3 == test_rule.length

    def test_load_rules(self):
        test_dir = self.get_test_loc('models/rules')
        rules = list(models.load_rules(test_dir))
        assert all(isinstance(r, models.Rule) for r in rules)
        results = sorted(r.to_dict() for r in rules)
        expected = self.get_test_loc('models/rules.expected.json')
        check_json(expected, results)

    def test_dump_rules(self):
        test_dir = self.get_test_loc('models/rules', copy=True)
        rules = list(models.load_rules(test_dir))
        for r in rules:
            r.dump()

        rules = list(models.load_rules(test_dir))
        results = sorted(r.to_dict() for r in rules)
        expected = self.get_test_loc('models/rules.expected.json')
        check_json(expected, results)

    def test_spdxrule(self):
        rule = models.SpdxRule(
            license_expression='mit OR gpl-2.0',
            stored_text='mit OR gpl-2.0',
            length=12,
        )
        try:
            rule.dump()
            raise Exception('SpdxRule cannot be dumped')
        except NotImplementedError:
            pass

        try:
            rule.load()
            raise Exception('SpdxRule cannot be dumped')
        except NotImplementedError:
            pass

        assert not rule.is_small
        assert rule.relevance == 100

    def test_spdxrule_with_invalid_expression(self):
        try:
            models.SpdxRule(
                license_expression='mit OR gpl-2.0 AND',
                stored_text='mit OR gpl-2.0',
                length=12,
            )
        except Exception as e:
            ex = str(e)
            assert 'Unable to parse License rule expression: ' in ex
            assert 'ExpressionError: AND requires two or more licenses as in: MIT AND BSD' in ex

    def test_template_rule_is_loaded_correctly(self):
        test_dir = self.get_test_loc('models/rule_template')
        rules = list(models.load_rules(test_dir))
        assert 1 == len(rules)

    def test_rule_len_is_computed_correctly(self):
        test_text = '''zero one two three
            four {{gap1}}
            five six seven eight nine ten'''
        r1 = models.Rule(stored_text=test_text)
        list(r1.tokens())
        assert 12 == r1.length

    def test_rule_templates_are_ignored(self):
        test_text = '''{{gap0}}zero one two three{{gap2}}'''
        r1 = models.Rule(stored_text=test_text)
        assert ['gap0', 'zero', 'one', 'two', 'three', 'gap2'] == list(r1.tokens())

    def test_rule_tokens_are_computed_correctly_ignoring_templates(self):
        test_text = '''I hereby abandon any{{SAX 2.0 (the)}}, and Release all of {{the SAX 2.0 }}source code of his'''
        rule = models.Rule(stored_text=test_text, license_expression='public-domain')

        rule_tokens = list(rule.tokens())
        expected = [
            'i', 'hereby', 'abandon', 'any', 'sax', '2', '0', 'the', 'and',
            'release', 'all', 'of', 'the', 'sax', '2', '0', 'source', 'code',
            'of', 'his'
        ]
        assert expected == rule_tokens

    def test_compute_thresholds_occurences(self):
        minimum_coverage = 0.0
        length = 54
        high_length = 11

        results = models.compute_thresholds_occurences(minimum_coverage, length, high_length)
        expected_min_cov = 0.0
        expected_min_matched_length = 4
        expected_min_high_matched_length = 3
        expected = expected_min_cov, expected_min_matched_length, expected_min_high_matched_length
        assert expected == results

        length_unique = 39
        high_length_unique = 7

        results = models.compute_thresholds_unique(
            minimum_coverage, length, length_unique, high_length_unique)
        expected_min_matched_length_unique = 4
        expected_min_high_matched_length_unique = 3
        expected = expected_min_matched_length_unique, expected_min_high_matched_length_unique
        assert expected == results


    def test_Thresholds(self):
        r1_text = 'licensed under the GPL, licensed under the GPL'
        r1 = models.Rule(text_file='r1', license_expression='apache-1.1', stored_text=r1_text)
        r2_text = 'licensed under the GPL, licensed under the GPL' * 10
        r2 = models.Rule(text_file='r1', license_expression='apache-1.1', stored_text=r2_text)
        _idx = index.LicenseIndex([r1, r2])

        results = models.compute_thresholds_occurences(r1.minimum_coverage, r1.length, r1.high_length)
        expected_min_cov = 80
        expected_min_matched_length = 8
        expected_min_high_matched_length = 4
        expected = expected_min_cov, expected_min_matched_length, expected_min_high_matched_length
        assert expected == results

        results = models.compute_thresholds_unique(
            r1.minimum_coverage, r1.length, r1.length_unique, r1.high_length_unique)
        
        expected_min_matched_length_unique = 3
        expected_min_high_matched_length_unique = 2
        expected = expected_min_matched_length_unique, expected_min_high_matched_length_unique
        assert expected == results

        results = models.compute_thresholds_occurences(r2.minimum_coverage, r2.length, r2.high_length)
        expected_min_cov = 0.0
        expected_min_matched_length = 4
        expected_min_high_matched_length = 3
        expected = expected_min_cov, expected_min_matched_length, expected_min_high_matched_length
        assert expected == results

        results = models.compute_thresholds_unique(
            r2.minimum_coverage, r2.length, r2.length_unique, r2.high_length_unique)
        expected_min_matched_length_unique = 4
        expected_min_high_matched_length_unique = 1
        expected = expected_min_matched_length_unique, expected_min_high_matched_length_unique
        assert expected == results

    def test_compute_relevance_does_not_change_stored_relevance(self):
        rule = models.Rule(stored_text='1', license_expression='public-domain')
        rule.relevance = 13
        rule.has_stored_relevance = True
        rule.length = 1000
        rule.compute_relevance()
        assert 13 == rule.relevance

    def test_compute_relevance_is_hundred_for_false_positive(self):
        rule = models.Rule(stored_text='1', license_expression='public-domain')
        rule.relevance = 13
        rule.has_stored_relevance = False
        rule.is_false_positive = True
        rule.length = 1000
        rule.compute_relevance()
        assert 100 == rule.relevance

    def test_compute_relevance_is_hundred_for_negative(self):
        rule = models.Rule(stored_text='1')
        rule.is_negative = True
        rule.relevance = 13
        rule.has_stored_relevance = False
        rule.is_false_positive = False
        rule.length = 1000
        rule.compute_relevance()
        assert 100 == rule.relevance

    def test_compute_relevance_is_using_rule_length(self):
        rule = models.Rule(stored_text='1', license_expression='some-license')
        rule.relevance = 13
        rule.has_stored_relevance = False
        rule.is_false_positive = False

        rule.length = 1000
        rule.compute_relevance()
        assert 100 == rule.relevance

        rule.length = 21
        rule.compute_relevance()
        assert 100 == rule.relevance

        rule.length = 20
        rule.compute_relevance()
        assert 100 == rule.relevance

        rule.length = 18
        rule.compute_relevance()
        assert 100 == rule.relevance

        rule.length = 17
        rule.compute_relevance()
        assert 94 == rule.relevance

        rule.length = 16
        rule.compute_relevance()
        assert 88 == rule.relevance

        rule.length = 15
        rule.compute_relevance()
        assert 83 == rule.relevance

        rule.length = 14
        rule.compute_relevance()
        assert 77 == rule.relevance

        rule.length = 13
        rule.compute_relevance()
        assert 72 == rule.relevance

        rule.length = 12
        rule.compute_relevance()
        assert 66 == rule.relevance

        rule.length = 11
        rule.compute_relevance()
        assert 61 == rule.relevance

        rule.length = 10
        rule.compute_relevance()
        assert 55 == rule.relevance

        rule.length = 8
        rule.compute_relevance()
        assert 44 == rule.relevance

        rule.length = 5
        rule.compute_relevance()
        assert 27 == rule.relevance

        rule.length = 2
        rule.compute_relevance()
        assert 11 == rule.relevance

        rule.length = 1
        rule.compute_relevance()
        assert 5 == rule.relevance

        rule.length = 0
        rule.compute_relevance()
        assert 0 == rule.relevance

    def test_rule_must_have_text(self):
        data_file = self.get_test_loc('models/rule_no_text/mit.yml')
        try:
            Rule(data_file=data_file)
            self.fail('Exception not raised.')
        except Exception as  e:
            assert str(e).startswith('Invalid rule without its corresponding text file')

    def test_rule_cannot_contain_extra_unknown_attributes(self):
        data_file = self.get_test_loc('models/rule_with_extra_attributes/sun-bcl.yml')
        text_file = self.get_test_loc('models/rule_with_extra_attributes/sun-bcl.RULE')

        expected = 'data file has unknown attributes: license_expressionnotuce'
        try:
            Rule(data_file=data_file, text_file=text_file)
            self.fail('Exception not raised.')
        except Exception as  e:
            assert expected in str(e)
