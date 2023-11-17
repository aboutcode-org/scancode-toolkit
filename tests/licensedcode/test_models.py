#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
from unittest import TestCase as TestCaseClass

from commoncode.testcase import FileBasedTesting

from licensedcode import index
from licensedcode import models
from licensedcode.models import get_key_phrase_spans
from licensedcode.models import InvalidRule
from licensedcode.models import Rule
from licensedcode.models import rules_data_dir
from licensedcode.spans import Span
from licensedcode_test_utils import create_rule_from_text_and_expression
from licensedcode_test_utils import create_rule_from_text_file_and_expression
from scancode.cli_test_utils import check_json

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')



def as_sorted_mapping_seq(licenses, include_text=False):
    """
    Given a `licenses` iterator of to_dict()'able objects, return a sorted list
    of these.
    """
    return sorted((l.to_dict(include_text=include_text) for l in licenses), key=lambda x: tuple(x.items()))


class TestLicense(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_load_license(self):
        test_dir = self.get_test_loc('models/licenses')
        lics = models.load_licenses(test_dir)
        # Note: one license is obsolete and not loaded. Other are various exception/version cases
        results = as_sorted_mapping_seq(lics.values())
        expected = self.get_test_loc('models/licenses.load.expected.json')
        check_json(expected, results)

    def test_dump_license(self):
        test_dir = self.get_test_loc('models/licenses', copy=True)
        lics = models.load_licenses(licenses_data_dir=test_dir, with_deprecated=True)
        for l in lics.values():
            l.dump(licenses_data_dir=test_dir)
        lics = models.load_licenses(licenses_data_dir=test_dir, with_deprecated=True)
        # Note: one license is obsolete and not loaded. Other are various exception/version cases
        results = as_sorted_mapping_seq(lics.values())
        expected = self.get_test_loc('models/licenses.dump.expected.json')
        check_json(expected, results)

    def test_dump_license_file(self):
        test_dir = self.get_test_loc('models/licenses', copy=True)
        test_dir_dump = self.get_test_loc('models/license_file_dump')
        lics = models.load_licenses(licenses_data_dir=test_dir, with_deprecated=True)
        lic_example = lics["apache-2.0"]
        lic_example.dump(licenses_data_dir=test_dir_dump)
        lics_from_dump = models.load_licenses(licenses_data_dir=test_dir_dump, with_deprecated=True)
        lic_example_from_dump = lics_from_dump["apache-2.0"]
        # Note: one license is obsolete and not loaded. Other are various exception/version cases
        before_dump = as_sorted_mapping_seq(licenses=[lic_example], include_text=True)
        after_dump = as_sorted_mapping_seq(licenses=[lic_example_from_dump], include_text=True)
        assert before_dump == after_dump

    def test_License_text(self):
        test_dir = self.get_test_loc('models/licenses')
        lics = models.load_licenses(licenses_data_dir=test_dir)
        for lic in lics.values():
            assert 'distribut' in lic.text.lower()

    def test_build_rules_from_licenses(self):
        test_dir = self.get_test_loc('models/licenses')
        licenses_by_key = models.load_licenses(licenses_data_dir=test_dir)
        rules = models.build_rules_from_licenses(licenses_by_key=licenses_by_key)
        results = as_sorted_mapping_seq(rules)
        expected = self.get_test_loc('models/license_rules.expected.json')
        check_json(expected, results)

    def test_validate_license_library_data(self):
        errors, warnings, infos = models.License.validate(
            licenses=models.load_licenses(with_deprecated=False),
            verbose=False,
            thorough=True,
        )
        assert errors == {}
        assert warnings == {}
        assert infos

    def test_validate_license_library_can_return_errors(self):
        test_dir = self.get_test_loc('models/validate')
        lics = models.load_licenses(test_dir, check_consistency=False)
        errors, warnings, infos = models.License.validate(
            lics,
            no_dupe_urls=True,
            verbose=False,
        )

        expected_errors = {
            'GLOBAL': [
                'Duplicate texts in multiple licenses: apache-2.0: TEXT, bsd-ack-carrot2: TEXT',
                'Duplicate short name (ignoring case): gpl 1.0 in licenses: gpl-1.0, gpl-1.0-plus',
                'Duplicate name (ignoring case): gnu general public license 1.0 in licenses: gpl-1.0, gpl-1.0-plus'],
            'bsd-ack-carrot2': [
                'No short name',
                'No name',
                'No category: Use "Unstated License" if not known.',
                'No owner: Use "Unspecified" if not known.',
                'No SPDX license key'],
            'foo-2.0': ['Unknown language: foobar', 'No SPDX license key'],
            'gpl-1.0': [
                'Unknown license category: GNU Copyleft.\nUse one of these valid categories:\n'
                'CLA\nCommercial\nCopyleft\nCopyleft Limited\nFree Restricted\n'
                'Patent License\nPermissive\nProprietary Free\nPublic Domain\nSource-available\nUnstated License',
                'No SPDX license key'],
            'w3c-docs-19990405': [
                'Unknown license category: Permissive Restricted.\nUse one of these valid categories:\n'
                'CLA\nCommercial\nCopyleft\nCopyleft Limited\nFree Restricted\n'
                'Patent License\nPermissive\nProprietary Free\nPublic Domain\nSource-available\nUnstated License',
                'No SPDX license key'],
        }

        assert errors == expected_errors

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

        assert warnings == expected_warnings

        expected_infos = {
            'foo-2.0': ['No license text'],
            'w3c-docs-19990405': ['No license text'],
        }
        assert infos == expected_infos

    def test_load_licenses_fails_if_file_contains_empty_yaml_frontmatter(self):
        test_dir = self.get_test_loc('models/licenses_without_frontmatter')
        try:
            list(models.load_licenses(test_dir))
            self.fail('Exception not raised')
        except Exception as e:
            assert 'Cannot load License with empty YAML frontmatter' in str(e)

    def test_load_licenses_fails_if_file_contains_empty_text(self):
        test_dir = self.get_test_loc('models/licenses_without_text')
        try:
            list(models.load_licenses(test_dir))
            self.fail('Exception not raised')
        except Exception as e:
            assert 'only deprecated, generic or unknown licenses can exist without text' in str(e)

    def test_license_file_is_computed_correctly(self):
        licenses_data_dir = self.get_test_loc('models/data_text_files/licenses')
        licenses = models.load_licenses(licenses_data_dir)
        lic = licenses['gpl-1.0']
        assert lic.license_file(licenses_data_dir=licenses_data_dir).startswith(licenses_data_dir)

    def test_rule_from_license_have_text_file_and_data_file_are_computed_correctly(self):
        licenses_data_dir = self.get_test_loc('models/data_text_files/licenses')
        licenses = models.load_licenses(licenses_data_dir=licenses_data_dir)
        lic = licenses['gpl-1.0']
        rule = models.build_rule_from_license(license_obj=lic)

        assert rule.rule_file(
            licenses_data_dir=licenses_data_dir,
            rules_data_dir=None,
        ).startswith(licenses_data_dir)


class TestRule(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_validate_license_rules_data(self):
        list(models.get_rules(validate=True, validate_thorough=True))

    def test_create_rule_ignore_punctuation(self):
        test_rule = create_rule_from_text_and_expression(text='A one. A two. A three.')
        expected = ['one', 'two', 'three']
        assert list(test_rule.tokens()) == expected
        assert test_rule.length == 3

    def test_create_plain_rule_with_text_file(self):

        def create_test_file(text):
            tf = self.get_temp_file()
            with open(tf, 'w') as of:
                of.write(text)
            return tf

        test_rule = create_rule_from_text_file_and_expression(text_file=create_test_file('A one. A two. A three.'))
        expected = ['one', 'two', 'three']
        assert list(test_rule.tokens()) == expected
        assert test_rule.length == 3

    def test_load_rules(self):
        test_dir = self.get_test_loc('models/rules')
        rules = list(models.load_rules(test_dir))
        assert all(isinstance(r, models.Rule) for r in rules)
        results = as_sorted_mapping_seq(rules)
        expected = self.get_test_loc('models/rules.expected.json')
        check_json(expected, results)

    def test_rules_have_only_one_flag_of_bool_type(self):
        rules = list(models.load_rules(rules_data_dir))
        rule_errors = []

        for r in rules:
            rule_flags = [
                r.is_license_text,
                r.is_license_notice,
                r.is_license_reference,
                r.is_license_tag,
                r.is_license_intro,
                r.is_license_clue,
                r.is_false_positive,
            ]
            number_of_flags_set = 0
            for rule_flag in rule_flags:
                if not type(rule_flag) == bool:
                    # invalid type
                    rule_errors.append(r.rule_file)
                    break

                if rule_flag is True:
                    number_of_flags_set += 1
                elif rule_flag is False:
                    continue

                if number_of_flags_set not in (0, 1):
                    rule_errors.append(r.rule_file)
                    break

        assert rule_errors == []

    def test_dump_rules(self):
        test_dir = self.get_test_loc('models/rules', copy=True)
        rules = list(models.load_rules(test_dir))
        for r in rules:
            r.dump(rules_data_dir=test_dir)

        rules = list(models.load_rules(test_dir))
        results = as_sorted_mapping_seq(rules)
        expected = self.get_test_loc('models/rules.expected.json')
        check_json(expected, results)

    def test_dump_rule_file(self):
        test_dir = self.get_test_loc('models/rules', copy=True)
        test_dir_dump = self.get_test_loc('models/rule_file_dump')
        rules = list(models.load_rules(test_dir))
        rules.sort(key=lambda x: x.identifier)
        rule_example = rules.pop()
        rule_example.dump(rules_data_dir=test_dir_dump)
        rule_from_dump = list(models.load_rules(test_dir_dump))
        rule_from_dump.sort(key=lambda x: x.identifier)
        rule_example_from_dump = rule_from_dump.pop()
        # Note: one license is obsolete and not loaded. Other are various exception/version cases
        before_dump = as_sorted_mapping_seq(licenses=[rule_example], include_text=True)
        after_dump = as_sorted_mapping_seq(licenses=[rule_example_from_dump], include_text=True)
        assert before_dump == after_dump

    def test_spdxrule(self):
        rule = models.SpdxRule(
            license_expression='mit OR gpl-2.0',
            text='mit OR gpl-2.0',
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
                text='mit OR gpl-2.0',
                length=12,
            )
        except Exception as e:
            ex = str(e)
            assert 'Unable to parse Rule license expression:' in ex
            assert 'ExpressionError: AND requires two or more licenses as in: MIT AND BSD' in ex

    def test_template_rule_is_loaded_correctly(self):
        test_dir = self.get_test_loc('models/rule_template')
        rules = list(models.load_rules(test_dir))
        assert len(rules) == 1

    def test_rule_len_is_computed_correctly(self):
        test_text = '''zero one two three
            four gap1
            five six seven eight nine ten'''
        r1 = create_rule_from_text_and_expression(text=test_text)
        list(r1.tokens())
        assert r1.length == 12

    def test_rule_templates_are_ignored(self):
        test_text = '''gap0 zero one two three gap2'''
        r1 = create_rule_from_text_and_expression(text=test_text)
        assert list(r1.tokens()) == ['gap0', 'zero', 'one', 'two', 'three', 'gap2']

    def test_rule_tokens_are_computed_correctly_ignoring_templates(self):
        test_text = '''I hereby abandon any SAX 2.0 (the), and Release all of the SAX 2.0 source code of his'''
        rule = create_rule_from_text_and_expression(text=test_text, license_expression='public-domain')

        rule_tokens = list(rule.tokens())
        expected = [
            'i', 'hereby', 'abandon', 'any', 'sax', '2', '0', 'the', 'and',
            'release', 'all', 'of', 'the', 'sax', '2', '0', 'source', 'code',
            'of', 'his'
        ]
        assert rule_tokens == expected

    def test_compute_thresholds_occurences(self):
        minimum_coverage = 0.0
        length = 54
        high_length = 11

        results = models.compute_thresholds_occurences(minimum_coverage, length, high_length)
        expected_min_cov = 0.0
        expected_min_matched_length = 4
        expected_min_high_matched_length = 3
        expected = expected_min_cov, expected_min_matched_length, expected_min_high_matched_length
        assert results == expected

        length_unique = 39
        high_length_unique = 7

        results = models.compute_thresholds_unique(
            minimum_coverage, length, length_unique, high_length_unique)
        expected_min_matched_length_unique = 4
        expected_min_high_matched_length_unique = 3
        expected = expected_min_matched_length_unique, expected_min_high_matched_length_unique
        assert results == expected

    def test_Thresholds(self):
        r1_text = 'licensed under the GPL, licensed under the GPL'
        r1 = create_rule_from_text_and_expression(license_expression='apache-1.1', text=r1_text)
        r2_text = 'licensed under the GPL, licensed under the GPL' * 10
        r2 = create_rule_from_text_and_expression(license_expression='apache-1.1', text=r2_text)
        _idx = index.LicenseIndex([r1, r2])

        results = models.compute_thresholds_occurences(r1.minimum_coverage, r1.length, r1.high_length)
        expected_min_cov = 80
        expected_min_matched_length = 8
        expected_min_high_matched_length = 4
        expected = expected_min_cov, expected_min_matched_length, expected_min_high_matched_length
        assert results == expected

        results = models.compute_thresholds_unique(
            r1.minimum_coverage, r1.length, r1.length_unique, r1.high_length_unique)

        expected_min_matched_length_unique = 3
        expected_min_high_matched_length_unique = 2
        expected = expected_min_matched_length_unique, expected_min_high_matched_length_unique
        assert results == expected

        results = models.compute_thresholds_occurences(r2.minimum_coverage, r2.length, r2.high_length)
        expected_min_cov = 0.0
        expected_min_matched_length = 4
        expected_min_high_matched_length = 3
        expected = expected_min_cov, expected_min_matched_length, expected_min_high_matched_length
        assert results == expected

        results = models.compute_thresholds_unique(
            r2.minimum_coverage, r2.length, r2.length_unique, r2.high_length_unique)
        expected_min_matched_length_unique = 4
        expected_min_high_matched_length_unique = 1
        expected = expected_min_matched_length_unique, expected_min_high_matched_length_unique
        assert results == expected

    def test_compute_relevance_does_not_change_stored_relevance(self):
        rule = create_rule_from_text_and_expression(text='1', license_expression='public-domain')
        rule.relevance = 13
        rule.has_stored_relevance = True
        rule.length = 1000
        rule.set_relevance()
        assert rule.relevance == 13
        assert rule.has_stored_relevance

    def test_compute_relevance_changes_stored_relevance_for_long_rules(self):
        rule = create_rule_from_text_and_expression(text='abcd ' * 18, license_expression='public-domain')
        rule.relevance = 100
        rule.has_stored_relevance = True
        rule.length = 18
        rule.set_relevance()
        assert rule.relevance == 100
        assert not rule.has_stored_relevance

    def test_compute_relevance_does_not_change_stored_relevance_for_short_rules(self):
        rule = create_rule_from_text_and_expression(text='abcd ' * 18, license_expression='public-domain')
        rule.relevance = 100
        rule.has_stored_relevance = True
        rule.length = 17
        rule.set_relevance()
        assert rule.relevance == 100
        assert rule.has_stored_relevance

    def test_compute_relevance_does_not_update_stored_relevance(self):
        rule = create_rule_from_text_and_expression(text='abcd ' * 17, license_expression='public-domain')
        rule.relevance = 100
        rule.has_stored_relevance = True
        rule.length = 17
        rule.set_relevance()
        assert rule.relevance == 100
        assert rule.has_stored_relevance

    def test_compute_relevance_does_not_update_stored_relevance_for_short_rules(self):
        rule = create_rule_from_text_and_expression(text='abcd ' * 17, license_expression='public-domain')
        rule.relevance = 99
        rule.has_stored_relevance = True
        rule.length = 18
        rule.set_relevance()
        assert rule.relevance == 99
        assert rule.has_stored_relevance

    def test_compute_relevance_does_update_stored_relevance_for_short_rules(self):
        rule = create_rule_from_text_and_expression(text='abcd ' * 17, license_expression='public-domain')
        rule.relevance = 94
        rule.has_stored_relevance = True
        rule.length = 17
        rule.set_relevance()
        assert rule.relevance == 94
        assert not rule.has_stored_relevance

    def test_compute_relevance_does_not_update_stored_relevance_for_short_rules_if_computed_differs(self):
        rule = create_rule_from_text_and_expression(text='abcd ' * 16, license_expression='public-domain')
        rule.relevance = 94
        rule.has_stored_relevance = True
        rule.length = 16
        rule.set_relevance()
        assert rule.relevance == 94
        assert rule.has_stored_relevance

    def test_compute_relevance_is_hundred_for_false_positive(self):
        rule = create_rule_from_text_and_expression(text='1', license_expression='public-domain')
        rule.relevance = 13
        rule.has_stored_relevance = False
        rule.is_false_positive = True
        rule.length = 1000
        rule.set_relevance()
        assert rule.relevance == 100

    def test_compute_relevance_is_using_rule_length(self):
        rule = create_rule_from_text_and_expression(text='1', license_expression='some-license')
        rule.relevance = 13
        rule.has_stored_relevance = False
        rule.is_false_positive = False

        rule.length = 1000
        rule.set_relevance()
        assert rule.relevance == 100

        rule.length = 21
        rule.set_relevance()
        assert rule.relevance == 100

        rule.length = 20
        rule.set_relevance()
        assert rule.relevance == 100

        rule.length = 18
        rule.set_relevance()
        assert rule.relevance == 100

        rule.length = 17
        rule.set_relevance()
        assert rule.relevance == 94

        rule.length = 16
        rule.set_relevance()
        assert rule.relevance == 88

        rule.length = 15
        rule.set_relevance()
        assert rule.relevance == 83

        rule.length = 14
        rule.set_relevance()
        assert rule.relevance == 77

        rule.length = 13
        rule.set_relevance()
        assert rule.relevance == 72

        rule.length = 12
        rule.set_relevance()
        assert rule.relevance == 66

        rule.length = 11
        rule.set_relevance()
        assert rule.relevance == 61

        rule.length = 10
        rule.set_relevance()
        assert rule.relevance == 55

        rule.length = 8
        rule.set_relevance()
        assert rule.relevance == 44

        rule.length = 5
        rule.set_relevance()
        assert rule.relevance == 27

        rule.length = 2
        rule.set_relevance()
        assert rule.relevance == 11

        rule.length = 1
        rule.set_relevance()
        assert rule.relevance == 5

        rule.length = 0
        rule.set_relevance()
        assert rule.relevance == 0

    def test_rule_must_have_text(self):
        rule_file = self.get_test_loc('models/rule_no_text/mit.RULE')
        try:
            Rule.from_file(rule_file=rule_file)
            self.fail('Exception not raised.')
        except InvalidRule as  e:
            assert 'Cannot load rule with empty text' in str(e)

    def test_rule_cannot_contain_extra_unknown_attributes(self):
        rule_file = self.get_test_loc('models/rule_with_extra_attributes/sun-bcl.RULE')

        expected = 'data file has unknown attributes: license_expressionnotuce'
        try:
            Rule.from_file(rule_file=rule_file)
            self.fail('Exception not raised.')
        except Exception as  e:
            assert expected in str(e)

    def test_load_rules_loads_file_content_at_path_and_not_path_as_string(self):
        rule_dir = self.get_test_loc('models/similar_names')
        rules = list(models.load_rules(rule_dir))
        result = [' '.join(list(r.tokens())[-4:]) for r in  rules]
        assert not any([r == 'rules proprietary 10 rule' for r in result])

    def test_Rule__validate_with_false_positive_rule(self):
        rule_dir = self.get_test_loc('models/rule_validate')
        rule = list(models.load_rules(rule_dir))[0]
        assert list(rule.validate()) == []

    def test_Rule__validate_with_invalid_language(self):
        rule_dir = self.get_test_loc('models/rule_validate_lang')
        validations = []
        for rule in sorted(models.load_rules(rule_dir)):
            validations.extend(rule.validate())
        expected = [
            'Unknown language: foobar',
            'Invalid rule is_license_* flags. Only one allowed.',
            'At least one is_license_* flag is needed.',
            'Invalid rule is_license_* flags. Only one allowed.',
            'At least one is_license_* flag is needed.',
        ]
        assert validations == expected

    def test_key_phrases_yields_spans(self):
        rule_text = (
            'This released software is {{released}} by under {{the MIT license}}. '
            'Which is a license originating at Massachusetts Institute of Technology (MIT).'
        )
        rule = models.Rule(license_expression='mit', text=rule_text)
        key_phrase_spans = list(rule.build_key_phrase_spans())
        assert key_phrase_spans == [Span(4), Span(7, 9)]

    def test_key_phrases_raises_exception_when_markup_is_not_closed(self):
        rule_text = (
            'This released software is {{released}} by under {{the MIT license. '
            'Which is a license originating at Massachusetts Institute of Technology (MIT).'
        )
        rule = models.Rule(license_expression='mit', text=rule_text)

        try:
            list(rule.build_key_phrase_spans())
            raise Exception('Exception should be raised')
        except InvalidRule:
            pass

    def test_rule_text_file_and_data_file_are_computed_correctly(self):
        rule_dir = self.get_test_loc('models/data_text_files/rules')
        rules = list(models.load_rules(rule_dir))
        rule = rules[0]
        assert rule.rule_file(rules_data_dir=rule_dir).startswith(rule_dir)


class TestGetKeyPhrases(TestCaseClass):

    def test_get_key_phrases_yields_spans(self):
        text = (
            'This released software is {{released}} by under {{the MIT license}}. '
            'Which is a license originating at Massachusetts Institute of Technology (MIT).'
        )

        key_phrase_spans = get_key_phrase_spans(text)
        assert list(key_phrase_spans) == [Span(4), Span(7, 9)]

    def test_get_key_phrases_raises_exception_key_phrase_markup_is_not_closed(self):
        text = 'This software is {{released by under the MIT license.'
        try:
            list(get_key_phrase_spans(text))
            raise Exception('Exception should be raised')
        except InvalidRule:
            pass

    def test_get_key_phrases_ignores_stopwords_in_positions(self):
        text = 'The word comma is a stop word so comma does not increase the span position {{MIT license}}.'
        key_phrase_spans = get_key_phrase_spans(text)
        assert list(key_phrase_spans) == [Span(11, 12)]

    def test_get_key_phrases_yields_spans_without_stop_words(self):
        text = 'This released software is {{released span}} by under {{the MIT quot license}}.'
        key_phrase_spans = get_key_phrase_spans(text)
        assert list(key_phrase_spans) == [Span(4), Span(7, 9)]

    def test_get_key_phrases_does_not_yield_empty_spans(self):
        text = 'This released software {{comma}} is {{}} by under {{the MIT license}}.'
        try:
            list(get_key_phrase_spans(text))
            raise Exception('Exception should be raised')
        except InvalidRule:
            pass

    def test_get_key_phrases_only_considers_outer_key_phrase_markup(self):
        text = 'This released {{{software under the MIT}}} license.'
        key_phrase_spans = get_key_phrase_spans(text)
        assert list(key_phrase_spans) == [Span(2, 5)]

    def test_get_key_phrases_ignores_nested_key_phrase_markup(self):
        text = 'This released {{software {{under the}} MIT}} license.'
        try:
            list(get_key_phrase_spans(text))
            raise Exception('Exception should be raised')
        except InvalidRule:
            pass
