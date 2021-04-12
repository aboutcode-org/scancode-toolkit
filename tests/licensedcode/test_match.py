# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#
import os

from commoncode.testcase import FileBasedTesting
from licensedcode import cache
from licensedcode import index
from licensedcode.index import LicenseIndex
from licensedcode.match import filter_contained_matches
from licensedcode.match import filter_overlapping_matches
from licensedcode.match import get_full_matched_text
from licensedcode.match import LicenseMatch
from licensedcode.match import merge_matches
from licensedcode.match import reportable_tokens
from licensedcode.match import restore_non_overlapping
from licensedcode.match import tokenize_matched_text
from licensedcode.match import Token
from licensedcode import models
from licensedcode.models import Rule
from licensedcode.models import load_rules
from licensedcode.spans import Span

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


class TestLicenseMatchBasic(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_LicenseMatch_equality(self):
        r1 = Rule(stored_text='r1', license_expression='apache-2.0 OR gpl')
        m1_r1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))
        m2_r1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))

        assert m1_r1 == m2_r1
        assert not (m1_r1 != m2_r1)

        r2 = Rule(stored_text='r1', license_expression='apache-2.0 OR gpl')
        m3_r2 = LicenseMatch(rule=r2, qspan=Span(0, 2), ispan=Span(0, 2))

        assert r1 == r2
        assert m1_r1 == m3_r2

    def test_LicenseMatch_equality_2(self):
        r1 = Rule(stored_text='r1', license_expression='apache-2.0 OR gpl')
        m1_r1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))
        r2 = Rule(stored_text='r2', license_expression='gpl OR apache-2.0')
        m2_r2 = LicenseMatch(rule=r2, qspan=Span(0, 2), ispan=Span(0, 2))

        assert r1.licensing is r2.licensing
        assert r1 != r2
        assert r1.license_expression != r2.license_expression
        assert r1.license_expression_object == r2.license_expression_object
        assert str(r1.license_expression_object.simplify()) == str(r2.license_expression_object.simplify())

        assert m1_r1 == m2_r2
        assert not (m1_r1 != m2_r2)

        assert r2.same_licensing(r2)
        assert m1_r1.qspan == m2_r2.qspan
        assert m1_r1.ispan == m2_r2.ispan
        r3 = Rule(stored_text='r3', license_expression='gpl OR apache-2.0')
        m3_r3 = LicenseMatch(rule=r3, qspan=Span(0, 2), ispan=Span(0, 3))

        assert m2_r2 != m3_r3

        r4 = Rule(stored_text='r3', license_expression='gpl1 OR apache-2.0')
        m4_r4 = LicenseMatch(rule=r4, qspan=Span(0, 2), ispan=Span(0, 3))

        assert m3_r3 != m4_r4

    def test_LicenseMatch_not_equal(self):
        r1 = Rule(text_file='r1', license_expression='apache-1.0 OR gpl')
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))
        r2 = Rule(text_file='r2', license_expression='gpl OR apache-2.0')
        m2 = LicenseMatch(rule=r2, qspan=Span(0, 2), ispan=Span(0, 2))

        assert m1 != m2

        r3 = Rule(text_file='r3', license_expression='apache-1.0 OR gpl')
        m3 = LicenseMatch(rule=r3, qspan=Span(0, 2), ispan=Span(0, 2))

        assert m1 == m3

        r4 = Rule(text_file='r4', license_expression='apache-1.0 OR gpl')
        m4 = LicenseMatch(rule=r4, qspan=Span(1, 2), ispan=Span(1, 2))

        assert not m1 == m4

    def test_LicenseMatch_equals(self):
        rule = Rule(text_file='r1', license_expression='apache-2.0 OR gpl')
        m1 = LicenseMatch(rule=rule, matcher='chunk1', qspan=Span(0, 7), ispan=Span(0, 7), start_line=1, end_line=1)
        m2 = LicenseMatch(rule=rule, matcher='chunk2', qspan=Span(0, 7), ispan=Span(0, 7), start_line=1, end_line=1)
        assert m1 == m2

        m3 = LicenseMatch(rule=rule, matcher='chunk3', qspan=Span(16, 23), ispan=Span(0, 7), start_line=3, end_line=3)
        assert m1 != m3

    def test_LicenseMatch_comparisons(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0 OR gpl')
        contained1 = LicenseMatch(rule=r1, qspan=Span(0, 5), ispan=Span(0, 5))
        contained2 = LicenseMatch(rule=r1, qspan=Span(1, 4), ispan=Span(1, 4))
        same_span1 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))
        same_span2 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))
        before_after = LicenseMatch(rule=r1, qspan=Span(8, 9), ispan=Span(8, 9))
        touching = LicenseMatch(rule=r1, qspan=Span(7, 7), ispan=Span(7, 7))
        overlaping = LicenseMatch(rule=r1, qspan=Span(4, 7), ispan=Span(4, 7))

        assert same_span1 == same_span2
        assert same_span1 in same_span2

        assert same_span1.overlap(same_span2)
        assert same_span2.overlap(same_span1)

        assert contained1 not in same_span1
        assert same_span1 not in contained1

        assert contained1.overlap(same_span2)
        assert contained1.surround(contained2)

        assert contained2 in same_span2
        assert contained2 in contained1

        assert contained2.overlap(overlaping)

        assert overlaping.overlap(contained2)
        assert overlaping.overlap(same_span1)
        assert not overlaping.overlap(before_after)

        assert before_after.is_after(same_span1)
        assert before_after.is_after(touching)
        assert before_after.is_after(contained1)

    def test_combine_raise_TypeError_for_matches_of_different_rules(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0 OR gpl')
        r2 = Rule(text_file='r2', license_expression='apache-2.0 OR gpl2')

        m1 = LicenseMatch(rule=r1, qspan=Span(0, 5), ispan=Span(0, 5))
        m2 = LicenseMatch(rule=r2, qspan=Span(1, 6), ispan=Span(1, 6))

        try:
            m1.combine(m2)
        except TypeError:
            pass

    def test_combine_matches_with_same_rules(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0 OR gpl')

        m1 = LicenseMatch(rule=r1, qspan=Span(0, 5), ispan=Span(0, 5))
        m2 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))

        match = m1.combine(m2)
        assert match.qspan == Span(0, 6)
        assert match.ispan == Span(0, 6)

    def test_combine_matches_cannot_combine_matches_with_same_licensing_and_different_rules(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0 OR gpl')
        r2 = Rule(text_file='r2', license_expression='apache-2.0 OR gpl')

        m1 = LicenseMatch(rule=r1, qspan=Span(0, 5), ispan=Span(0, 5))
        m2 = LicenseMatch(rule=r2, qspan=Span(1, 6), ispan=Span(1, 6))

        try:
            m1.combine(m2)
            self.fail('Should fail')
        except TypeError:
            pass

    def test_LicenseMatch_small(self):
        r1_text = u'licensed under the GPL, licensed under the GPL distribute extent of law'
        small_rule = Rule(text_file='small_rule', license_expression='apache-1.1', stored_text=r1_text)

        r2_text = u'licensed under the GPL, licensed under the GPL re distribute extent of law' * 10
        long_rule = Rule(text_file='long_rule', license_expression='apache-1.1', stored_text=r2_text)

        _idx = index.LicenseIndex([small_rule, long_rule])

        test = LicenseMatch(rule=small_rule, qspan=Span(0, 10), ispan=Span(0, 10), hispan=Span(12))
        assert test.is_small()
        test = LicenseMatch(rule=small_rule, qspan=Span(0, 10), ispan=Span(0, 10), hispan=Span(11, 12))
        assert test.is_small()

        test = LicenseMatch(rule=small_rule, qspan=Span(10, 11, 12), ispan=Span(10, 11, 12), hispan=Span(11, 12))
        assert test.is_small()

        test = LicenseMatch(rule=small_rule, qspan=Span(1, 6), ispan=Span(1, 6))
        assert test.is_small()

        test = LicenseMatch(rule=long_rule, qspan=Span(0, 10), ispan=Span(0, 10), hispan=Span(12))
        assert test.is_small()

        test = LicenseMatch(rule=long_rule, qspan=Span(5, 10), ispan=Span(5, 10), hispan=Span(5, 6))
        assert test.is_small()

        test = LicenseMatch(rule=small_rule, qspan=Span(1, 10), ispan=Span(1, 10), hispan=Span(3, 6))
        assert not test.is_small()

    def test_LicenseMatch_score_is_not_100_with_aho_match_and_extra_unknown_token_hash_match(self):
        text = (
            'this file is licensed under the GPL license version2 only '
            'or any other version. You can redistribute this file under '
            'this or any other license.')
        r1 = Rule(text_file='r1', license_expression='apache-1.1', stored_text=text)
        idx = index.LicenseIndex([r1])

        querys = (
            'this file is licensed under the GPL license version2 only '
            +' big ' +
            'or any other version. You can redistribute this file under '
            'this or any other license.')

        match = idx.match(query_string=querys)[0]
        assert match.score() < 100

    def test_LicenseMatch_score_is_not_100_with_aho_match_and_extra_unknown_token_seq_match(self):
        text = (
            'this file is licensed under the GPL license version2 only '
            'or any other version. You can redistribute this file under '
            'this or any other license.')
        r1 = Rule(text_file='r1', license_expression='apache-1.1', stored_text=text)
        idx = index.LicenseIndex([r1])

        querys = (
            'this file is licensed under the GPL license version2 only '
            +' is ' +
            'or any other version. You can redistribute this file under '
            'this or any other license.')

        match = idx.match(query_string=querys)[0]
        assert match.score() < 100

    def test_LicenseMatch_score_is_not_100_with_aho_match_and_extra_unknown_token_aho_match(self):
        text = (
            'this file is licensed under the GPL license version2 only '
            'or any other version. You can redistribute this file under '
            'this or any other license.')
        r1 = Rule(text_file='r1', license_expression='apache-1.1', stored_text=text)
        idx = index.LicenseIndex([r1])

        querys = (
            'this this file is licensed under the GPL license version2 only '
            +' big ' +
            'or any other version. You can redistribute this file under '
            'this or any other license. that')

        match = idx.match(query_string=querys)[0]
        assert match.score() < 100


class TestMergeMatches(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_merge_does_merge_non_contiguous_matches_in_sequence(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0 OR gpl')
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))
        m2 = LicenseMatch(rule=r1, qspan=Span(4, 6), ispan=Span(4, 6))
        m5 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))

        results = merge_matches([m1, m2, m5])
        assert results == [LicenseMatch(rule=r1, qspan=Span(0, 6), ispan=Span(0, 6))]

    def test_merge_does_not_merge_overlapping_matches_of_different_rules_with_different_licensing(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0 OR gpl')
        r2 = Rule(text_file='r2', license_expression='apache-2.0 OR gpl2')

        m1 = LicenseMatch(rule=r1, qspan=Span(0, 5), ispan=Span(0, 5))
        m2 = LicenseMatch(rule=r2, qspan=Span(1, 6), ispan=Span(1, 6))

        assert merge_matches([m1, m2]) == [m1, m2]

    def test_merge_does_merge_overlapping_matches_of_same_rules_if_in_sequence(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0 OR gpl')

        m1 = LicenseMatch(rule=r1, qspan=Span(0, 5), ispan=Span(0, 5))
        m2 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))

        assert merge_matches([m1, m2]) == [LicenseMatch(rule=r1, qspan=Span(0, 6), ispan=Span(0, 6))]

    def test_merge_does_not_merge_overlapping_matches_of_same_rules_if_in_sequence_with_gaps(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0 OR gpl')
        r1.length = 50

        m1 = LicenseMatch(rule=r1, qspan=Span(1, 3), ispan=Span(1, 3))
        m2 = LicenseMatch(rule=r1, qspan=Span(14, 20), ispan=Span(4, 10))

        expected = [LicenseMatch(rule=r1, qspan=Span(1, 3) | Span(14, 20), ispan=Span(1, 10))]
        results = merge_matches([m1, m2])
        assert results == expected

    def test_merge_does_not_merge_overlapping_matches_of_same_rules_if_in_sequence_with_gaps_for_long_match(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0 OR gpl')
        r1.length = 20
        m1 = LicenseMatch(rule=r1, qspan=Span(1, 10), ispan=Span(1, 10))
        m2 = LicenseMatch(rule=r1, qspan=Span(14, 20), ispan=Span(14, 20))

        expected = [LicenseMatch(rule=r1, qspan=Span(1, 10) | Span(14, 20), ispan=Span(1, 10) | Span(14, 20))]
        results = merge_matches([m1, m2])
        assert results == expected

    def test_merge_does_not_merge_overlapping_matches_of_same_rules_if_in_not_sequence(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0 OR gpl')

        m1 = LicenseMatch(rule=r1, qspan=Span(1, 3), ispan=Span(1, 3))
        m2 = LicenseMatch(rule=r1, qspan=Span(14, 20), ispan=Span(1, 3))

        matches = merge_matches([m1, m2])
        assert sorted(matches) == sorted([m1, m2])

    def test_merge_does_not_merge_contained_matches_of_different_rules_with_same_licensing(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0 OR gpl')
        r2 = Rule(text_file='r2', license_expression='apache-2.0 OR gpl')

        m1 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))
        m2 = LicenseMatch(rule=r2, qspan=Span(1, 6), ispan=Span(1, 6))

        matches = merge_matches([m1, m2])
        assert sorted(matches) == sorted([m1, m2])

    def test_files_does_filter_contained_matches_of_different_rules_with_same_licensing(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0 OR gpl')
        r2 = Rule(text_file='r2', license_expression='apache-2.0 OR gpl')

        m1 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))
        m2 = LicenseMatch(rule=r2, qspan=Span(1, 6), ispan=Span(1, 6))

        matches, discarded = filter_contained_matches([m1, m2])
        assert matches == [m2]
        assert discarded == [m1]

    def test_merge_does_not_merge_overlaping_matches_with_same_licensings(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0 OR gpl')
        r2 = Rule(text_file='r2', license_expression='apache-2.0 OR gpl')

        overlap = LicenseMatch(rule=r1, qspan=Span(0, 5), ispan=Span(0, 5))
        same_span1 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))
        same_span2 = LicenseMatch(rule=r2, qspan=Span(1, 6), ispan=Span(1, 6))

        result = merge_matches([overlap, same_span1, same_span2])
        expected = [
            LicenseMatch(rule=r1, qspan=Span(0, 6), ispan=Span(0, 6)),
            LicenseMatch(rule=r2, qspan=Span(1, 6), ispan=Span(1, 6)),
        ]
        assert sorted(result) == sorted(expected)

    def test_filter_contained_matches_only_filter_contained_matches_with_same_licensings(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0 OR gpl')
        r2 = Rule(text_file='r2', license_expression='apache-2.0 OR gpl')

        overlap = LicenseMatch(rule=r1, qspan=Span(0, 5), ispan=Span(0, 5))
        same_span1 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))
        same_span2 = LicenseMatch(rule=r2, qspan=Span(1, 6), ispan=Span(1, 6))

        matches, discarded = filter_contained_matches([overlap, same_span1, same_span2])
        assert matches == [overlap, same_span1]
        assert discarded

    def test_filter_overlaping_matches_does_filter_overlaping_matches_with_same_licensings(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0 OR gpl')
        r2 = Rule(text_file='r2', license_expression='apache-2.0 OR gpl')

        overlap = LicenseMatch(rule=r1, qspan=Span(0, 5), ispan=Span(0, 5))
        same_span1 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))
        same_span2 = LicenseMatch(rule=r2, qspan=Span(1, 6), ispan=Span(1, 6))

        matches, discarded = filter_overlapping_matches([overlap, same_span1, same_span2])
        assert matches == [overlap]
        assert discarded

    def test_filter_contained_matches_prefers_longer_overlaping_matches(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0 OR gpl')
        r2 = Rule(text_file='r2', license_expression='apache-2.0 OR gpl')

        overlap = LicenseMatch(rule=r1, qspan=Span(0, 5), ispan=Span(0, 5))
        same_span1 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))
        same_span2 = LicenseMatch(rule=r2, qspan=Span(1, 8), ispan=Span(1, 8))

        matches, discarded = filter_contained_matches([overlap, same_span1, same_span2])
        assert matches == [overlap, same_span2]
        assert discarded

    def test_filter_overlapping_matches_prefers_longer_overlaping_matches(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0 OR gpl')
        r2 = Rule(text_file='r2', license_expression='apache-2.0 OR gpl')

        overlap = LicenseMatch(rule=r1, qspan=Span(0, 5), ispan=Span(0, 5))
        same_span1 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))
        same_span2 = LicenseMatch(rule=r2, qspan=Span(1, 8), ispan=Span(1, 8))

        matches, discarded = filter_overlapping_matches([overlap, same_span1, same_span2])
        assert matches == [same_span2]
        assert discarded

    def test_merge_contiguous_touching_matches_in_sequence(self):
        r1 = Rule(stored_text='r1', license_expression='apache-2.0 OR gpl')
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))
        m2 = LicenseMatch(rule=r1, qspan=Span(3, 6), ispan=Span(3, 6))

        result = merge_matches([m1, m2])
        match = result[0]
        assert match == LicenseMatch(rule=r1, qspan=Span(0, 6), ispan=Span(0, 6))

    def test_merge_contiguous_contained_matches(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0 OR gpl')
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))
        m2 = LicenseMatch(rule=r1, qspan=Span(3, 6), ispan=Span(3, 6))
        m5 = LicenseMatch(rule=r1, qspan=Span(7, 8), ispan=Span(7, 8))

        result = merge_matches([m1, m2, m5])
        assert result == [LicenseMatch(rule=r1, qspan=Span(0, 8), ispan=Span(0, 8))]

    def test_merge_should_not_merge_repeated_matches_out_of_sequence(self):
        rule = Rule(text_file='gpl-2.0_49.RULE', license_expression=u'gpl-2.0')
        rule.rid = 2615
        m1 = LicenseMatch(rule=rule, matcher='chunk1', qspan=Span(0, 7), ispan=Span(0, 7))
        m2 = LicenseMatch(rule=rule, matcher='chunk2', qspan=Span(8, 15), ispan=Span(0, 7))
        m3 = LicenseMatch(rule=rule, matcher='chunk3', qspan=Span(16, 23), ispan=Span(0, 7))
        result = merge_matches([m1, m2, m3])
        assert result == [m1, m2, m3]

    def test_merge_merges_contained_and_overlapping_match(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0 OR gpl')
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 5), ispan=Span(0, 5))
        contained = LicenseMatch(rule=r1, qspan=Span(1, 4), ispan=Span(1, 4))
        overlapping = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))
        assert contained in overlapping
        assert contained in m1
        result = merge_matches([m1, contained, overlapping])
        expected = [LicenseMatch(rule=r1, qspan=Span(0, 6), ispan=Span(0, 6))]
        assert result == expected

    def test_merge_does_not_merge_multiple_contained_matches_across_rules(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0 OR gpl')
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 5), ispan=Span(0, 5))

        r2 = Rule(text_file='r2', license_expression='apache-2.0 OR gpl')
        contained1 = LicenseMatch(rule=r2, qspan=Span(1, 2), ispan=Span(1, 2))

        r3 = Rule(text_file='r3', license_expression='apache-2.0 OR gpl')
        contained2 = LicenseMatch(rule=r3, qspan=Span(3, 4), ispan=Span(3, 4))

        r5 = Rule(text_file='r5', license_expression='apache-2.0 OR gpl')
        m5 = LicenseMatch(rule=r5, qspan=Span(1, 6), ispan=Span(1, 6))

        result = merge_matches([m1, contained1, contained2, m5])
        assert sorted(result) == sorted([m1, contained1, contained2, m5])

    def test_filter_contained_matches_does_filter_across_rules(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0 OR gpl')
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 5), ispan=Span(0, 5))

        r2 = Rule(text_file='r2', license_expression='apache-2.0 OR gpl')
        contained1 = LicenseMatch(rule=r2, qspan=Span(1, 2), ispan=Span(1, 2))

        r3 = Rule(text_file='r3', license_expression='apache-2.0 OR gpl')
        contained2 = LicenseMatch(rule=r3, qspan=Span(3, 4), ispan=Span(3, 4))

        r5 = Rule(text_file='r5', license_expression='apache-2.0 OR gpl')
        m5 = LicenseMatch(rule=r5, qspan=Span(1, 6), ispan=Span(1, 6))

        result, _discarded = filter_contained_matches([m1, contained1, contained2, m5])
        assert result == [m1, m5]

    def test_filter_overlapping_matches_does_not_filter_multiple_contained_matches_across_rules(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0 OR gpl')
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 5), ispan=Span(0, 5))

        r2 = Rule(text_file='r2', license_expression='apache-2.0 OR gpl')
        contained1 = LicenseMatch(rule=r2, qspan=Span(1, 2), ispan=Span(1, 2))

        r3 = Rule(text_file='r3', license_expression='apache-2.0 OR gpl')
        contained2 = LicenseMatch(rule=r3, qspan=Span(3, 4), ispan=Span(3, 4))

        r5 = Rule(text_file='r5', license_expression='apache-2.0 OR gpl')
        m5 = LicenseMatch(rule=r5, qspan=Span(1, 6), ispan=Span(1, 6))

        result, _discarded = filter_overlapping_matches([m1, contained1, contained2, m5])
        assert result == [m1]

    def test_filter_contained_matches_filters_multiple_contained_matches(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0 OR gpl')
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 5), ispan=Span(0, 5))

        r2 = Rule(text_file='r2', license_expression='apache-2.0 OR gpl')
        contained1 = LicenseMatch(rule=r2, qspan=Span(1, 2), ispan=Span(1, 2))

        r3 = Rule(text_file='r3', license_expression='apache-2.0 OR gpl')
        contained2 = LicenseMatch(rule=r3, qspan=Span(3, 4), ispan=Span(3, 4))

        r5 = Rule(text_file='r5', license_expression='apache-2.0 OR gpl')
        m5 = LicenseMatch(rule=r5, qspan=Span(1, 6), ispan=Span(1, 6))

        matches, discarded = filter_contained_matches([m1, contained1, contained2, m5])
        assert matches == [m1, m5]
        assert sorted(discarded) == sorted([contained1, contained2, ])

    def test_filter_overlapping_matches_filters_multiple_contained_matches(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0 OR gpl')
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 5), ispan=Span(0, 5))

        r2 = Rule(text_file='r2', license_expression='apache-2.0 OR gpl')
        contained1 = LicenseMatch(rule=r2, qspan=Span(1, 2), ispan=Span(1, 2))

        r3 = Rule(text_file='r3', license_expression='apache-2.0 OR gpl')
        contained2 = LicenseMatch(rule=r3, qspan=Span(3, 4), ispan=Span(3, 4))

        r5 = Rule(text_file='r5', license_expression='apache-2.0 OR gpl')
        m5 = LicenseMatch(rule=r5, qspan=Span(1, 6), ispan=Span(1, 6))

        matches, discarded = filter_overlapping_matches([m1, contained1, contained2, m5])
        assert matches == [m1]
        assert sorted(discarded) == sorted([m5, contained1, contained2, ])

    def test_merge_does_not_merge_matches_with_same_spans_if_licenses_are_identical_but_rule_differ(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0')
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))
        m5 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))

        r2 = Rule(text_file='r2', license_expression='apache-2.0')
        m2 = LicenseMatch(rule=r2, qspan=Span(0, 2), ispan=Span(0, 2))

        matches = merge_matches([m1, m2, m5])
        assert sorted(matches) == sorted([LicenseMatch(rule=r1, qspan=Span(0, 6), ispan=Span(0, 6)), m2])

    def test_filter_contained_matches_filters_matches_with_same_spans_if_licenses_are_identical_but_rule_differ(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0')
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))
        m5 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))

        r2 = Rule(text_file='r2', license_expression='apache-2.0')
        m2 = LicenseMatch(rule=r2, qspan=Span(0, 2), ispan=Span(0, 2))

        matches, discarded = filter_contained_matches([m1, m2, m5])

        assert matches == [m1, m5]
        assert discarded

    def test_filter_overlapping_matches_filters_matches_with_same_spans_if_licenses_are_identical_but_rule_differ(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0')
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))
        m5 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))

        r2 = Rule(text_file='r2', license_expression='apache-2.0')
        m2 = LicenseMatch(rule=r2, qspan=Span(0, 2), ispan=Span(0, 2))

        matches, discarded = filter_overlapping_matches([m1, m2, m5])

        assert matches == [m5]
        assert discarded

    def test_merge_then_filter_matches_with_same_spans_if_licenses_are_identical_but_rule_differ(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0')
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))
        m5 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))

        r2 = Rule(text_file='r2', license_expression='apache-2.0')
        m2 = LicenseMatch(rule=r2, qspan=Span(0, 2), ispan=Span(0, 2))

        matches = merge_matches([m1, m2, m5])
        matches, discarded = filter_contained_matches(matches)

        assert matches == [LicenseMatch(rule=r1, qspan=Span(0, 6), ispan=Span(0, 6))]
        assert discarded

    def test_merge_overlapping_matches(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0')
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))
        m2 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))

        matches = merge_matches([m1, m2])
        assert matches == [LicenseMatch(rule=r1, qspan=Span(0, 6), ispan=Span(0, 6))]

    def test_merge_does_not_merges_matches_with_same_spans_if_licenses_are_the_same_but_have_different_licenses_ordering(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0 OR gpl')
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))
        m5 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))

        r2 = Rule(text_file='r2', license_expression='gpl OR apache-2.0')
        m2 = LicenseMatch(rule=r2, qspan=Span(0, 2), ispan=Span(0, 2))

        result = merge_matches([m1, m2, m5])
        assert sorted(result) == sorted([LicenseMatch(rule=r1, qspan=Span(0, 6), ispan=Span(0, 6)), m2])

    def test_merge_does_not_merges_matches_with_same_spans_if_rules_are_different(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0 OR gpl')
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))
        m5 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))

        r2 = Rule(text_file='r2', license_expression='apache-2.0 OR gpl')
        m2 = LicenseMatch(rule=r2, qspan=Span(0, 2), ispan=Span(0, 2))

        result = merge_matches([m1, m2, m5])
        assert sorted(result) == sorted([LicenseMatch(rule=r1, qspan=Span(0, 6), ispan=Span(0, 6)), m2])

    def test_merge_merges_duplicate_matches(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0')
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 8), ispan=Span(0, 8))
        m2 = LicenseMatch(rule=r1, qspan=Span(0, 8), ispan=Span(0, 8))

        matches = merge_matches([m1, m2])
        assert (matches == [m1]) or (matches == [m2])

    def test_merge_does_not_merge_overlapping_matches_in_sequence_with_assymetric_overlap(self):
        r1 = Rule(text_file='r1', license_expression=u'lgpl-2.0-plus')

        # ---> merge_matches: current: LicenseMatch<'3-seq', lines=(9, 28), 'lgpl-2.0-plus_9.RULE', u'lgpl-2.0-plus', choice=False, score=87.5, len=126, ilen=126, hilen=20, rlen=144, qreg=(50, 200), ireg=(5, 142), qspan=Span(50, 90)|Span(92, 142)|Span(151, 182)|Span(199, 200), ispan=Span(5, 21)|Span(23, 46)|Span(48, 77)|Span(79, 93)|Span(95, 100)|Span(108, 128)|Span(130, 142), hispan=Span(10)|Span(14)|Span(18)|Span(24)|Span(27)|Span(52)|Span(57)|Span(61)|Span(65, 66)|Span(68)|Span(70)|Span(80)|Span(88)|Span(96)|Span(111)|Span(113)|Span(115)|Span(131)|Span(141)>
        # ---> merge_matches: next:    LicenseMatch<'2-aho', lines=(28, 44), 'lgpl-2.0-plus_9.RULE', u'lgpl-2.0-plus', choice=False, score=100.0, len=144, ilen=144, hilen=21, rlen=144, qreg=(198, 341), ireg=(0, 143), qspan=Span(198, 341), ispan=Span(0, 143), hispan=Span(1)|Span(10)|Span(14)|Span(18)|Span(24)|Span(27)|Span(52)|Span(57)|Span(61)|Span(65, 66)|Span(68)|Span(70)|Span(80)|Span(88)|Span(96)|Span(111)|Span(113)|Span(115)|Span(131)|Span(141)>
        #     ---> ###merge_matches: next overlaps in sequence current, merged as new: LicenseMatch<'3-seq 2-aho', lines=(9, 44), 'lgpl-2.0-plus_9.RULE', u'lgpl-2.0-plus', choice=False, score=100.0, len=268, hilen=21, rlen=144, qreg=(50, 341), ireg=(0, 143), qspan=Span(50, 90)|Span(92, 142)|Span(151, 182)|Span(198, 341), ispan=Span(0, 143), his

        # ---> merge_matches: current: len=126, hilen=20, rlen=144, qreg=(50, 200), ireg=(5, 142)
        # ---> merge_matches: next:    len=144, hilen=21, rlen=144, qreg=(198, 341), ireg=(0, 143)

        m1 = LicenseMatch(
            rule=r1,
            qspan=Span(50, 90) | Span(92, 142) | Span(151, 182) | Span(199, 200),
            ispan=
                Span(5, 21) | Span(23, 46) | Span(48, 77) | Span(79, 93) |
                Span(95, 100) | Span(108, 128) | Span(130, 142),
            hispan=
                Span(10) | Span(14) | Span(18) | Span(24) | Span(27) | Span(52) |
                Span(57) | Span(61) | Span(65, 66) | Span(68) | Span(70) | Span(80) |
                Span(88) | Span(96) | Span(111) | Span(113) | Span(115) | Span(131) |
                Span(141),
        )
        m2 = LicenseMatch(
            rule=r1,
            qspan=Span(198, 341),
            ispan=Span(0, 143),
            hispan=
                Span(1) | Span(10) | Span(14) | Span(18) | Span(24) | Span(27) |
                Span(52) | Span(57) | Span(61) | Span(65, 66) | Span(68) | Span(70) |
                Span(80) | Span(88) | Span(96) | Span(111) | Span(113) | Span(115) |
                Span(131) | Span(141))

        matches = merge_matches([m1, m2])
        assert matches == [m1, m2]


class TestLicenseMatchFilter(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_filter_contained_matches_matches_filters_multiple_nested_contained_matches_and_large_overlapping(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0 OR gpl')

        m1 = LicenseMatch(rule=r1, qspan=Span(0, 5), ispan=Span(0, 5))
        large_overlap = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))
        contained = LicenseMatch(rule=r1, qspan=Span(1, 4), ispan=Span(1, 4))
        in_contained = LicenseMatch(rule=r1, qspan=Span(2, 3), ispan=Span(2, 3))

        result, discarded = filter_contained_matches([m1, contained, in_contained, large_overlap])
        assert result == [m1, large_overlap]
        assert discarded == [contained, in_contained]

    def test_filter_overlapping_matches_matches_filters_multiple_nested_contained_matches_and_large_overlapping(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0 OR gpl')
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 5), ispan=Span(0, 5))
        large_overlap = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))
        contained = LicenseMatch(rule=r1, qspan=Span(1, 4), ispan=Span(1, 4))
        in_contained = LicenseMatch(rule=r1, qspan=Span(2, 3), ispan=Span(2, 3))
        result, discarded = filter_overlapping_matches([m1, contained, in_contained, large_overlap])
        assert result == [m1]
        assert discarded

    def test_filter_matches_filters_non_contiguous_or_overlapping__but_contained_matches(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0 OR gpl')
        m1 = LicenseMatch(rule=r1, qspan=Span(1, 2), ispan=Span(1, 2))
        m2 = LicenseMatch(rule=r1, qspan=Span(3, 6), ispan=Span(3, 6))
        m3 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))
        m4 = LicenseMatch(rule=r1, qspan=Span(0, 7), ispan=Span(0, 7))
        m5 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))

        result, discarded = filter_contained_matches([m1, m2, m3, m4, m5])
        assert result == [m4]
        assert discarded

    def test_filter_matches_filters_non_contiguous_or_overlapping_contained_matches_with_touching_boundaries(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0 OR gpl')
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))

        r2 = Rule(text_file='r2', license_expression='apache-2.0 OR gpl')
        m2 = LicenseMatch(rule=r2, qspan=Span(3, 7), ispan=Span(3, 7))

        r3 = Rule(text_file='r3', license_expression='apache-2.0 OR gpl')
        m3 = LicenseMatch(rule=r3, qspan=Span(0, 6), ispan=Span(0, 6))

        r6 = Rule(text_file='r6', license_expression='apache-2.0 OR gpl')
        m6 = LicenseMatch(rule=r6, qspan=Span(1, 7), ispan=Span(1, 7))

        r5 = Rule(text_file='r5', license_expression='apache-2.0 OR gpl')
        m5 = LicenseMatch(rule=r5, qspan=Span(1, 6), ispan=Span(1, 6))

        r4 = Rule(text_file='r4', license_expression='apache-2.0 OR gpl')
        m4 = LicenseMatch(rule=r4, qspan=Span(0, 7), ispan=Span(0, 7))

        result, discarded = filter_contained_matches([m1, m2, m3, m4, m5, m6])
        assert result == [m4]
        assert discarded

    def test_filter_contained_matches_matches_does_filter_matches_with_contained_spans_if_licenses_are_different(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0')
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))

        r2 = Rule(text_file='r2', license_expression='apache-2.0')
        m2 = LicenseMatch(rule=r2, qspan=Span(1, 6), ispan=Span(1, 6))

        r3 = Rule(text_file='r3', license_expression='apache-1.1')
        m3 = LicenseMatch(rule=r3, qspan=Span(0, 2), ispan=Span(0, 2))

        matches, discarded = filter_contained_matches([m1, m2, m3])
        assert matches == [m1, m2]
        assert discarded

    def test_filter_overlapping_matches_matches_does_filter_matches_with_contained_spans_if_licenses_are_different(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0')
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))

        r2 = Rule(text_file='r2', license_expression='apache-2.0')
        m2 = LicenseMatch(rule=r2, qspan=Span(1, 6), ispan=Span(1, 6))

        r3 = Rule(text_file='r3', license_expression='apache-1.1')
        m3 = LicenseMatch(rule=r3, qspan=Span(0, 2), ispan=Span(0, 2))

        matches, discarded = filter_overlapping_matches([m1, m2, m3])
        assert matches == [m2]
        assert discarded

    def test_filter_overlapping_matches_matches_filters_matches_with_medium_overlap_only_if_license_are_the_same(self):
        r1 = Rule(text_file='r1', license_expression='apache-1.1')
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 10), ispan=Span(0, 10))
        m2 = LicenseMatch(rule=r1, qspan=Span(3, 11), ispan=Span(3, 11))

        r2 = Rule(text_file='r2', license_expression='gpl OR apache-2.0')
        m3 = LicenseMatch(rule=r2, qspan=Span(7, 15), ispan=Span(7, 15))

        result, discarded = filter_overlapping_matches([m1, m2, m3])
        assert sorted(result) == sorted([m1, m3])
        assert discarded

    def test_filter_matches_handles_interlaced_matches_with_overlap_and_same_license(self):
        rule_dir = self.get_test_loc('match_filter/rules')
        idx = index.LicenseIndex(load_rules(rule_dir))
        rules = {r.identifier: r for r in idx.rules_by_rid}
        query_loc = self.get_test_loc('match_filter/query')
        matches = idx.match(location=query_loc)
        expected = [
            # filtered: LicenseMatch(matcher='3-seq', rule=rules['rule1.RULE'], qspan=Span(4, 47) | Span(50, 59), ispan=Span(1, 53)),
            LicenseMatch(matcher='2-aho', rule=rules['rule2.RULE'], qspan=Span(24, 85), ispan=Span(0, 61)),
        ]

        assert matches == expected

    def test_filter_contained_matches_matches_filters_matches_does_not_discard_non_overlaping(self):
        r1 = Rule(text_file='r1', license_expression='apache-1.1')
        r2 = Rule(text_file='r2', license_expression='gpl OR apache-2.0')
        r3 = Rule(text_file='r3', license_expression='gpl')

        # we have these matches
        # 1. ABC
        # 2. ABCDEDFG
        # 3.    DEFCGJLJLJKLJJLKJLJJJLJLJLJJL
        # we do not want 1. to be discarded in the final

        m1 = LicenseMatch(rule=r1, qspan=Span(0, 5), ispan=Span(0, 5))
        m2 = LicenseMatch(rule=r2, qspan=Span(0, 40), ispan=Span(0, 40))
        m3 = LicenseMatch(rule=r3, qspan=Span(6, 120), ispan=Span(6, 120))

        result, discarded = filter_contained_matches([m2, m1, m3])
        assert result == [m2, m3]
        assert discarded == [m1]

    def test_filter_overlapping_matches_matches_filters_matches_does_not_discard_non_overlaping(self):
        r1 = Rule(text_file='r1', license_expression='apache-1.1')
        r2 = Rule(text_file='r2', license_expression='gpl OR apache-2.0')
        r3 = Rule(text_file='r3', license_expression='gpl')

        # we have these matches
        # 1. ABC
        # 2. ABCDEDFG
        # 3.    DEFCGJLJLJKLJJLKJLJJJLJLJLJJL
        # we do not want 1. to be discarded in the final

        m1 = LicenseMatch(rule=r1, qspan=Span(0, 5), ispan=Span(0, 5))
        m2 = LicenseMatch(rule=r2, qspan=Span(0, 40), ispan=Span(0, 40))
        m3 = LicenseMatch(rule=r3, qspan=Span(6, 120), ispan=Span(6, 120))

        result, discarded = filter_overlapping_matches([m2, m1, m3])
        assert result == [m3]
        assert discarded == [m1, m2]

        result, discarded = restore_non_overlapping(result, discarded)
        assert result == [m1]
        assert discarded == [m2]


class TestLicenseMatchScore(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_LicenseMatch_score_100(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0')
        r1.relevance = 100
        r1.length = 3

        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))
        assert m1.score() == 100

    def test_LicenseMatch_score_50(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0')
        r1.relevance = 50
        r1.length = 3

        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))
        assert m1.score() == 50

    def test_LicenseMatch_score_25_with_stored_relevance(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0')
        r1.relevance = 50
        r1.length = 6

        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))
        # NB we do not have a query here
        assert m1.score() == 25

    def test_LicenseMatch_score_0(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0')
        r1.relevance = 0
        r1.length = 6

        m1 = LicenseMatch(rule=r1, qspan=Span(), ispan=Span())
        assert m1.score() == 0

    def test_LicenseMatch_score_0_relevance(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0')
        r1.relevance = 0
        r1.length = 6

        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))
        assert m1.score() == 0

    def test_LicenseMatch_score_100_contiguous(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0')
        r1.relevance = 100
        r1.length = 42

        m1 = LicenseMatch(rule=r1, qspan=Span(0, 41), ispan=Span(0, 41))
        assert m1.score() == 100

    def test_LicenseMatch_score_100_non_contiguous(self):
        r1 = Rule(text_file='r1', license_expression='apache-2.0')
        r1.relevance = 100
        r1.length = 42

        m1 = LicenseMatch(rule=r1, qspan=Span(0, 19) | Span(30, 51), ispan=Span(0, 41))
        assert m1.score() == 80.77

    def test_LicenseMatch_stopwords_are_treated_as_unknown_2484(self):
        rules_dir = self.get_test_loc('stopwords/index/rules')
        lics_dir = self.get_test_loc('stopwords/index/licenses')
        rules = models.get_rules(licenses_data_dir=lics_dir, rules_data_dir=rules_dir)
        idx = LicenseIndex(rules)

        query_location = self.get_test_loc('stopwords/query.txt')
        matches = idx.match(location=query_location)
        assert matches == []


class TestCollectLicenseMatchTexts(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_get_full_matched_text_base(self):
        rule_text = u'''
            Copyright {{some copyright}}
            THIS IS FROM {{THE CODEHAUS}} AND CONTRIBUTORS
            IN NO EVENT SHALL {{THE CODEHAUS}} OR ITS CONTRIBUTORS BE LIABLE
            EVEN IF ADVISED OF THE {{POSSIBILITY OF SUCH}} DAMAGE
        '''

        rule = Rule(stored_text=rule_text, license_expression='test')
        idx = index.LicenseIndex([rule])

        querys = u'''
            foobar 45 . Copyright 2003 (C) James. All Rights Reserved.
            THIS IS FROM THE CODEHAUS AND CONTRIBUTORS
            IN NO EVENT SHALL THE best CODEHAUS OR ITS CONTRIBUTORS BE LIABLE
            EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. chabada DAMAGE 12 ABC dasdasda .
        '''
        result = idx.match(query_string=querys)
        assert len(result) == 1
        match = result[0]

        # Note that there is a trailing space in that string
        expected = u"""Copyright [2003] ([C]) [James]. [All] [Rights] [Reserved].
            THIS IS FROM THE CODEHAUS AND CONTRIBUTORS
            IN NO EVENT SHALL THE [best] CODEHAUS OR ITS CONTRIBUTORS BE LIABLE
            EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. """
        matched_text = u''.join(
            get_full_matched_text(match, query_string=querys, idx=idx, _usecache=False))
        assert matched_text == expected

        expected_nh = u"""Copyright 2003 (C) James. All Rights Reserved.
            THIS IS FROM THE CODEHAUS AND CONTRIBUTORS
            IN NO EVENT SHALL THE best CODEHAUS OR ITS CONTRIBUTORS BE LIABLE
            EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. """
        matched_text_nh = u''.join(
            get_full_matched_text(
                match, query_string=querys, idx=idx, _usecache=False, highlight=False))
        assert matched_text_nh == expected_nh

        expected_origin_text = u"""Copyright 2003 (C) James. All Rights Reserved.
            THIS IS FROM THE CODEHAUS AND CONTRIBUTORS
            IN NO EVENT SHALL THE best CODEHAUS OR ITS CONTRIBUTORS BE LIABLE
            EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. """
        origin_matched_text = u''.join(get_full_matched_text(
            match,
            query_string=querys,
            idx=idx,
            highlight_not_matched=u'%s',
        ))
        assert origin_matched_text == expected_origin_text

    def test_get_full_matched_text(self):
        rule_text = u'''
            Copyright {{some copyright}}
            THIS IS FROM {{THE CODEHAUS}} AND CONTRIBUTORS
            IN NO EVENT SHALL {{THE CODEHAUS}} OR ITS CONTRIBUTORS BE LIABLE
            EVEN IF ADVISED OF THE {{POSSIBILITY OF SUCH}} DAMAGE
        '''

        rule = Rule(stored_text=rule_text, license_expression='test')
        idx = index.LicenseIndex([rule])

        querys = u'''
            foobar 45 Copyright 2003 (C) James. All Rights Reserved.
            THIS IS FROM THE CODEHAUS AND CONTRIBUTORS
            IN NO EVENT SHALL THE best CODEHAUS OR ITS CONTRIBUTORS BE LIABLE
            EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. chabada DAMAGE 12 ABC
        '''
        result = idx.match(query_string=querys)
        assert len(result) == 1
        match = result[0]

        # Note that there is a trailing space in that string
        expected = u"""Copyright [2003] ([C]) [James]. [All] [Rights] [Reserved].
            THIS IS FROM THE CODEHAUS AND CONTRIBUTORS
            IN NO EVENT SHALL THE [best] CODEHAUS OR ITS CONTRIBUTORS BE LIABLE
            EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. """

        matched_text = u''.join(get_full_matched_text(match, query_string=querys, idx=idx, _usecache=False))
        assert matched_text == expected

        # the text is finally rstripped
        matched_text = match.matched_text(_usecache=False)
        assert matched_text == expected.rstrip()

        # test again using some HTML with tags
        # Note that there is a trailing space in that string
        expected = u"""Copyright <br>2003</br> (<br>C</br>) <br>James</br>. <br>All</br> <br>Rights</br> <br>Reserved</br>.
            THIS IS FROM THE CODEHAUS AND CONTRIBUTORS
            IN NO EVENT SHALL THE <br>best</br> CODEHAUS OR ITS CONTRIBUTORS BE LIABLE
            EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. """
        matched_text = u''.join(get_full_matched_text(
            match, query_string=querys, idx=idx, highlight_not_matched=u'<br>%s</br>', _usecache=False))
        assert matched_text == expected

        # test again using whole_lines
        expected = u"""            foobar 45 Copyright 2003 (C) James. All Rights Reserved.
            THIS IS FROM THE CODEHAUS AND CONTRIBUTORS
            IN NO EVENT SHALL THE best CODEHAUS OR ITS CONTRIBUTORS BE LIABLE
            EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. chabada DAMAGE 12 ABC\n"""
        matched_text = u''.join(get_full_matched_text(
            match, query_string=querys, idx=idx, highlight_not_matched=u'%s', whole_lines=True))
        assert matched_text == expected

    def test_get_full_matched_text_does_not_munge_underscore(self):
        rule_text = 'MODULE_LICENSE_GPL'

        rule = Rule(stored_text=rule_text, license_expression='test')
        idx = index.LicenseIndex([rule])

        querys = 'MODULE_LICENSE_GPL'
        result = idx.match(query_string=querys)
        assert len(result) == 1
        match = result[0]

        expected = 'MODULE_LICENSE_GPL'
        matched_text = u''.join(get_full_matched_text(match, query_string=querys, idx=idx, _usecache=False))
        assert matched_text == expected

    def test_get_full_matched_text_does_not_munge_plus(self):
        rule_text = 'MODULE_LICENSE_GPL+ +'

        rule = Rule(stored_text=rule_text, license_expression='test')
        idx = index.LicenseIndex([rule])

        querys = 'MODULE_LICENSE_GPL+ +'
        result = idx.match(query_string=querys)
        assert len(result) == 1
        match = result[0]

        expected = 'MODULE_LICENSE_GPL+ +\n'
        matched_text = u''.join(get_full_matched_text(match, query_string=querys, idx=idx, _usecache=False))
        assert matched_text == expected

    def test_tokenize_matched_text_does_cache_last_call_from_query_string_and_location(self):
        dictionary = {'module': 0, 'license': 1, 'gpl+': 2}
        location = None
        query_string = 'the MODULE_LICENSE_GPL+ foobar'
        result1 = tokenize_matched_text(location, query_string, dictionary)
        result2 = tokenize_matched_text(location, query_string, dictionary)
        assert result2 is result1

        location = self.get_test_loc('matched_text/tokenize_matched_text_query.txt')
        query_string = None
        result3 = tokenize_matched_text(location, query_string, dictionary)
        assert result3 is not result2
        assert result3 == result2

        result4 = tokenize_matched_text(location, query_string, dictionary)
        assert result4 is result3

    def test_tokenize_matched_text_does_return_correct_tokens(self):
        querys = u'''
            foobar 45 Copyright 2003 (C) James. All Rights Reserved.  THIS
            IS FROM THE CODEHAUS AND CONTRIBUTORS
        '''
        dictionary = dict(this=0, event=1, possibility=2, reserved=3, liable=5, copyright=6)
        result = tokenize_matched_text(location=None, query_string=querys, dictionary=dictionary)
        expected = [
            Token(value=u'\n', line_num=1, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'            ', line_num=2, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'foobar', line_num=2, pos=-1, is_text=True, is_matched=False, is_known=False),
            Token(value=u' ', line_num=2, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'45', line_num=2, pos=-1, is_text=True, is_matched=False, is_known=False),
            Token(value=u' ', line_num=2, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'Copyright', line_num=2, pos=0, is_text=True, is_matched=False, is_known=True),
            Token(value=u' ', line_num=2, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'2003', line_num=2, pos=-1, is_text=True, is_matched=False, is_known=False),
            Token(value=u' (', line_num=2, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'C', line_num=2, pos=-1, is_text=True, is_matched=False, is_known=False),
            Token(value=u') ', line_num=2, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'James', line_num=2, pos=-1, is_text=True, is_matched=False, is_known=False),
            Token(value=u'. ', line_num=2, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'All', line_num=2, pos=-1, is_text=True, is_matched=False, is_known=False),
            Token(value=u' ', line_num=2, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'Rights', line_num=2, pos=-1, is_text=True, is_matched=False, is_known=False),
            Token(value=u' ', line_num=2, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'Reserved', line_num=2, pos=1, is_text=True, is_matched=False, is_known=True),
            Token(value=u'.  ', line_num=2, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'THIS', line_num=2, pos=2, is_text=True, is_matched=False, is_known=True),
            Token(value=u'\n', line_num=2, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'            ', line_num=3, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'IS', line_num=3, pos=-1, is_text=True, is_matched=False, is_known=False),
            Token(value=u' ', line_num=3, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'FROM', line_num=3, pos=-1, is_text=True, is_matched=False, is_known=False),
            Token(value=u' ', line_num=3, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'THE', line_num=3, pos=-1, is_text=True, is_matched=False, is_known=False),
            Token(value=u' ', line_num=3, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'CODEHAUS', line_num=3, pos=-1, is_text=True, is_matched=False, is_known=False),
            Token(value=u' ', line_num=3, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'AND', line_num=3, pos=-1, is_text=True, is_matched=False, is_known=False),
            Token(value=u' ', line_num=3, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'CONTRIBUTORS', line_num=3, pos=-1, is_text=True, is_matched=False, is_known=False),
            Token(value=u'\n', line_num=3, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value='        \n', line_num=4, pos=-1, is_text=False, is_matched=False, is_known=False)
        ]

        assert result == expected

    def test_tokenize_matched_text_does_not_crash_on_turkish_unicode(self):
        querys = u'İrəli'
        result = tokenize_matched_text(location=None, query_string=querys, dictionary={})

        expected = [
            Token(value='i', line_num=1, pos=-1, is_text=True, is_matched=False, is_known=False),
            Token(value='rəli', line_num=1, pos=-1, is_text=True, is_matched=False, is_known=False),
            Token(value='\n', line_num=1, pos=-1, is_text=False, is_matched=False, is_known=False),
        ]
        assert result == expected

    def test_tokenize_matched_text_behaves_like_query_tokenizer_on_turkish_unicode(self):
        from licensedcode.tokenize import query_tokenizer
        querys = u'İrəli'
        matched_text_result = tokenize_matched_text(location=None, query_string=querys, dictionary={})
        matched_text_result = [t.value for t in matched_text_result]
        query_tokenizer_result = list(query_tokenizer(querys))

        if matched_text_result[-1] == '\n':
            matched_text_result = matched_text_result[:-1]

        assert matched_text_result == query_tokenizer_result

    def test_reportable_tokens_filter_tokens_does_not_strip_last_token_value(self):
        tokens = [
            Token(value=u'\n', line_num=1, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'            ', line_num=2, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'foobar', line_num=2, pos=-1, is_text=True, is_matched=False, is_known=False),
            Token(value=u' ', line_num=2, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'45', line_num=2, pos=-1, is_text=True, is_matched=False, is_known=False),
            Token(value=u' ', line_num=2, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'Copyright', line_num=2, pos=0, is_text=True, is_matched=False, is_known=True),
            Token(value=u' ', line_num=2, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'2003', line_num=2, pos=-1, is_text=True, is_matched=False, is_known=False),
            Token(value=u' (', line_num=2, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'C', line_num=2, pos=-1, is_text=True, is_matched=False, is_known=False),
            Token(value=u') ', line_num=2, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'James', line_num=2, pos=-1, is_text=True, is_matched=False, is_known=False),
            Token(value=u'. ', line_num=2, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'All', line_num=2, pos=-1, is_text=True, is_matched=False, is_known=False),
            Token(value=u' ', line_num=2, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'Rights', line_num=2, pos=-1, is_text=True, is_matched=False, is_known=False),
            Token(value=u' ', line_num=2, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'Reserved', line_num=2, pos=1, is_text=True, is_matched=False, is_known=True),
            Token(value=u'.  ', line_num=2, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'THIS', line_num=2, pos=2, is_text=True, is_matched=False, is_known=True),
            Token(value=u'\n', line_num=2, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'            ', line_num=3, pos=-1, is_text=False, is_matched=False, is_known=False),
        ]

        match_qspan = Span(0, 1)
        result = list(reportable_tokens(tokens, match_qspan, start_line=1, end_line=2, whole_lines=False))
        expected = [
            Token(value=u'Copyright', line_num=2, pos=0, is_text=True, is_matched=True, is_known=True),
            Token(value=u' ', line_num=2, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'2003', line_num=2, pos=-1, is_text=True, is_matched=False, is_known=False),
            Token(value=u' (', line_num=2, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'C', line_num=2, pos=-1, is_text=True, is_matched=False, is_known=False),
            Token(value=u') ', line_num=2, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'James', line_num=2, pos=-1, is_text=True, is_matched=False, is_known=False),
            Token(value=u'. ', line_num=2, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'All', line_num=2, pos=-1, is_text=True, is_matched=False, is_known=False),
            Token(value=u' ', line_num=2, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'Rights', line_num=2, pos=-1, is_text=True, is_matched=False, is_known=False),
            Token(value=u' ', line_num=2, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'Reserved', line_num=2, pos=1, is_text=True, is_matched=True, is_known=True),
            Token(value=u'.  ', line_num=2, pos=-1, is_text=False, is_matched=False, is_known=False)
        ]

        assert result == expected

        # est again with whole lines
        match_qspan = Span(0, 1)
        result = list(reportable_tokens(tokens, match_qspan, start_line=1, end_line=2, whole_lines=True))
        expected = [
            Token(value=u'\n', line_num=1, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'            ', line_num=2, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'foobar', line_num=2, pos=-1, is_text=True, is_matched=False, is_known=False),
            Token(value=u' ', line_num=2, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'45', line_num=2, pos=-1, is_text=True, is_matched=False, is_known=False),
            Token(value=u' ', line_num=2, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'Copyright', line_num=2, pos=0, is_text=True, is_matched=True, is_known=True),
            Token(value=u' ', line_num=2, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'2003', line_num=2, pos=-1, is_text=True, is_matched=False, is_known=False),
            Token(value=u' (', line_num=2, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'C', line_num=2, pos=-1, is_text=True, is_matched=False, is_known=False),
            Token(value=u') ', line_num=2, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'James', line_num=2, pos=-1, is_text=True, is_matched=False, is_known=False),
            Token(value=u'. ', line_num=2, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'All', line_num=2, pos=-1, is_text=True, is_matched=False, is_known=False),
            Token(value=u' ', line_num=2, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'Rights', line_num=2, pos=-1, is_text=True, is_matched=False, is_known=False),
            Token(value=u' ', line_num=2, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'Reserved', line_num=2, pos=1, is_text=True, is_matched=True, is_known=True),
            Token(value=u'.  ', line_num=2, pos=-1, is_text=False, is_matched=False, is_known=False),
            Token(value=u'THIS', line_num=2, pos=2, is_text=True, is_matched=False, is_known=True),
            Token(value=u'\n', line_num=2, pos=-1, is_text=False, is_matched=False, is_known=False)]

        assert result == expected

    def test_matched_text_is_collected_correctly_end2end(self):
        rules_data_dir = self.get_test_loc('matched_text/index/rules')
        query_location = self.get_test_loc('matched_text/query.txt')
        rules = models.load_rules(rules_data_dir)
        idx = LicenseIndex(rules)

        results = [match.matched_text(_usecache=False) for match in idx.match(location=query_location)]
        expected = [
            'This source code is licensed under both the Apache 2.0 license '
            '(found in the\n#  LICENSE',

            'This source code is licensed under [both] [the] [Apache] [2].[0] license '
            '(found in the\n#  LICENSE file in the root directory of this source tree)',

            'GPLv2 ('
        ]
        assert results == expected

    def check_matched_texts(self, test_loc, expected_texts, whole_lines=True):
        idx = cache.get_index()
        test_loc = self.get_test_loc(test_loc)
        matches = idx.match(location=test_loc)
        matched_texts = [
            m.matched_text(whole_lines=whole_lines, highlight=False, _usecache=False)
            for m in matches
        ]
        assert matched_texts == expected_texts

    def test_matched_text_is_collected_correctly_end2end_for_spdx_match_whole_lines(self):
        self.check_matched_texts(
            test_loc='matched_text/spdx/query.txt',
            expected_texts=['@REM # SPDX-License-Identifier: BSD-2-Clause-Patent'],
            whole_lines=True
        )

    def test_matched_text_is_collected_correctly_end2end_for_spdx_match(self):
        self.check_matched_texts(
            test_loc='matched_text/spdx/query.txt',
            expected_texts=['SPDX-License-Identifier: BSD-2-Clause-Patent'],
            whole_lines=False
        )

    def test_matched_text_is_not_truncated_with_unicode_diacritic_input_from_query(self):
        idx = cache.get_index()
        querys_with_diacritic_unicode = 'İ license MIT'
        result = idx.match(query_string=querys_with_diacritic_unicode)
        assert len(result) == 1
        match = result[0]
        expected = 'license MIT'
        matched_text = match.matched_text(_usecache=False,)
        assert matched_text == expected

    def test_matched_text_is_not_truncated_with_unicode_diacritic_input_from_file(self):
        idx = cache.get_index()
        file_with_diacritic_unicode_location = self.get_test_loc('matched_text/unicode_text/main3.js')
        result = idx.match(location=file_with_diacritic_unicode_location)
        assert len(result) == 1
        match = result[0]
        expected = 'license MIT'
        matched_text = match.matched_text(_usecache=False)
        assert matched_text == expected

    def test_matched_text_is_not_truncated_with_unicode_diacritic_input_from_query_whole_lines(self):
        idx = cache.get_index()
        querys_with_diacritic_unicode = 'İ license MIT'
        result = idx.match(query_string=querys_with_diacritic_unicode)
        assert len(result) == 1
        match = result[0]
        expected = '[İ] license MIT'
        matched_text = match.matched_text(_usecache=False, whole_lines=True)
        assert matched_text == expected

    def test_matched_text_is_not_truncated_with_unicode_diacritic_input_with_diacritic_in_rules(self):
        rule_dir = self.get_test_loc('matched_text/turkish_unicode/rules')
        idx = index.LicenseIndex(load_rules(rule_dir))
        query_loc = self.get_test_loc('matched_text/turkish_unicode/query')
        matches = idx.match(location=query_loc)
        matched_texts = [
            m.matched_text(whole_lines=False, highlight=False, _usecache=False)
            for m in matches
        ]

        expected = [
            'Licensed under the Apache License, Version 2.0\r\nnext_label=irəli',
            'İ license MIT',
            'İ license MIT',
            'Licensed under the Apache License, Version 2.0\r\nnext_label=irəli',
            'lİcense mit'
        ]

        assert matched_texts == expected

    def test_matched_text_is_not_truncated_with_unicode_diacritic_input_and_full_index(self):
        expected = [
            'Licensed under the Apache License, Version 2.0',
            'license MIT',
            'license MIT',
            'Licensed under the Apache License, Version 2.0'
        ]

        self.check_matched_texts(
            test_loc='matched_text/turkish_unicode/query',
            expected_texts=expected,
            whole_lines=False
        )

    def test_matched_text_does_not_ignores_whole_lines_in_binary_with_small_index(self):
        rule_dir = self.get_test_loc('matched_text/binary_text/rules')
        idx = index.LicenseIndex(load_rules(rule_dir))
        query_loc = self.get_test_loc('matched_text/binary_text/gosu')
        matches = idx.match(location=query_loc)
        matched_texts = [
            m.matched_text(whole_lines=True, highlight=False, _usecache=False)
            for m in matches
        ]

        expected = ['{{ .Self }} license: GPL-3 (full text at https://github.com/tianon/gosu)']

        assert matched_texts == expected

    def test_matched_text_does_not_ignores_whole_lines_in_binary_against_full_index(self):
        expected = ['{{ .Self }} license: GPL-3 (full text at https://github.com/tianon/gosu)']
        self.check_matched_texts(
            test_loc='matched_text/binary_text/gosu',
            expected_texts=expected,
            whole_lines=True,
        )

    def test_matched_text_is_collected_correctly_in_binary_ffmpeg_windows_whole_lines(self):
        expected_texts = [
            '--enable-gpl --enable-version3 --enable-dxva2 --enable-libmfx --enable-nvenc '
            '--enable-avisynth --enable-bzlib --enable-fontconfig --enable-frei0r '
            '--enable-gnutls --enable-iconv --enable-libass --enable-libbluray '
            '--enable-libbs2b --enable-libcaca --enable-libfreetype --enable-libgme '
            '--enable-libgsm --enable-libilbc --enable-libmodplug --enable-libmp3lame '
            '--enable-libopencore-amrnb --enable-libopencore-amrwb --enable-libopenh264 '
            '--enable-libopenjpeg --enable-libopus --enable-librtmp --enable-libsnappy '
            '--enable-libsoxr --enable-libspeex --enable-libtheora --enable-libtwolame '
            '--enable-libvidstab --enable-libvo-amrwbenc --enable-libvorbis '
            '--enable-libvpx --enable-libwavpack --enable-libwebp --enable-libx264 '
            '--enable-libx265 --enable-libxavs --enable-libxvid --enable-libzimg '
            '--enable-lzma --enable-decklink --enable-zlib',

            '%sconfiguration: --enable-gpl --enable-version3 --enable-dxva2 '
            '--enable-libmfx --enable-nvenc --enable-avisynth --enable-bzlib '
            '--enable-fontconfig --enable-frei0r --enable-gnutls --enable-iconv '
            '--enable-libass --enable-libbluray --enable-libbs2b --enable-libcaca '
            '--enable-libfreetype --enable-libgme --enable-libgsm --enable-libilbc '
            '--enable-libmodplug --enable-libmp3lame --enable-libopencore-amrnb '
            '--enable-libopencore-amrwb --enable-libopenh264 --enable-libopenjpeg '
            '--enable-libopus --enable-librtmp --enable-libsnappy --enable-libsoxr '
            '--enable-libspeex --enable-libtheora --enable-libtwolame --enable-libvidstab '
            '--enable-libvo-amrwbenc --enable-libvorbis --enable-libvpx '
            '--enable-libwavpack --enable-libwebp --enable-libx264 --enable-libx265 '
            '--enable-libxavs --enable-libxvid --enable-libzimg --enable-lzma '
            '--enable-decklink --enable-zlib',

            '%s is free software; you can redistribute it and/or modify\n'
            'it under the terms of the GNU General Public License as published by\n'
            'the Free Software Foundation; either version 3 of the License, or\n'
            '(at your option) any later version.\n'
            '%s is distributed in the hope that it will be useful,\n'
            'but WITHOUT ANY WARRANTY; without even the implied warranty of\n'
            'MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n'
            'GNU General Public License for more details.\n'
            'You should have received a copy of the GNU General Public License\n'
            'along with %s.  If not, see <http://www.gnu.org/licenses/>.',

            '--enable-gpl --enable-version3 --enable-dxva2 --enable-libmfx --enable-nvenc '
            '--enable-avisynth --enable-bzlib --enable-fontconfig --enable-frei0r '
            '--enable-gnutls --enable-iconv --enable-libass --enable-libbluray '
            '--enable-libbs2b --enable-libcaca --enable-libfreetype --enable-libgme '
            '--enable-libgsm --enable-libilbc --enable-libmodplug --enable-libmp3lame '
            '--enable-libopencore-amrnb --enable-libopencore-amrwb --enable-libopenh264 '
            '--enable-libopenjpeg --enable-libopus --enable-librtmp --enable-libsnappy '
            '--enable-libsoxr --enable-libspeex --enable-libtheora --enable-libtwolame '
            '--enable-libvidstab --enable-libvo-amrwbenc --enable-libvorbis '
            '--enable-libvpx --enable-libwavpack --enable-libwebp --enable-libx264 '
            '--enable-libx265 --enable-libxavs --enable-libxvid --enable-libzimg '
            '--enable-lzma --enable-decklink --enable-zlib',

            'libavfilter license: GPL version 3 or later',

            '--enable-gpl --enable-version3 --enable-dxva2 --enable-libmfx --enable-nvenc '
            '--enable-avisynth --enable-bzlib --enable-fontconfig --enable-frei0r '
            '--enable-gnutls --enable-iconv --enable-libass --enable-libbluray '
            '--enable-libbs2b --enable-libcaca --enable-libfreetype --enable-libgme '
            '--enable-libgsm --enable-libilbc --enable-libmodplug --enable-libmp3lame '
            '--enable-libopencore-amrnb --enable-libopencore-amrwb --enable-libopenh264 '
            '--enable-libopenjpeg --enable-libopus --enable-librtmp --enable-libsnappy '
            '--enable-libsoxr --enable-libspeex --enable-libtheora --enable-libtwolame '
            '--enable-libvidstab --enable-libvo-amrwbenc --enable-libvorbis '
            '--enable-libvpx --enable-libwavpack --enable-libwebp --enable-libx264 '
            '--enable-libx265 --enable-libxavs --enable-libxvid --enable-libzimg '
            '--enable-lzma --enable-decklink --enable-zlib',

            'libavformat license: GPL version 3 or later',

            '--enable-gpl --enable-version3 --enable-dxva2 --enable-libmfx --enable-nvenc '
            '--enable-avisynth --enable-bzlib --enable-fontconfig --enable-frei0r '
            '--enable-gnutls --enable-iconv --enable-libass --enable-libbluray '
            '--enable-libbs2b --enable-libcaca --enable-libfreetype --enable-libgme '
            '--enable-libgsm --enable-libilbc --enable-libmodplug --enable-libmp3lame '
            '--enable-libopencore-amrnb --enable-libopencore-amrwb --enable-libopenh264 '
            '--enable-libopenjpeg --enable-libopus --enable-librtmp --enable-libsnappy '
            '--enable-libsoxr --enable-libspeex --enable-libtheora --enable-libtwolame '
            '--enable-libvidstab --enable-libvo-amrwbenc --enable-libvorbis '
            '--enable-libvpx --enable-libwavpack --enable-libwebp --enable-libx264 '
            '--enable-libx265 --enable-libxavs --enable-libxvid --enable-libzimg '
            '--enable-lzma --enable-decklink --enable-zlib',

            'libavcodec license: GPL version 3 or later',

            '--enable-gpl --enable-version3 --enable-dxva2 --enable-libmfx --enable-nvenc '
            '--enable-avisynth --enable-bzlib --enable-fontconfig --enable-frei0r '
            '--enable-gnutls --enable-iconv --enable-libass --enable-libbluray '
            '--enable-libbs2b --enable-libcaca --enable-libfreetype --enable-libgme '
            '--enable-libgsm --enable-libilbc --enable-libmodplug --enable-libmp3lame '
            '--enable-libopencore-amrnb --enable-libopencore-amrwb --enable-libopenh264 '
            '--enable-libopenjpeg --enable-libopus --enable-librtmp --enable-libsnappy '
            '--enable-libsoxr --enable-libspeex --enable-libtheora --enable-libtwolame '
            '--enable-libvidstab --enable-libvo-amrwbenc --enable-libvorbis '
            '--enable-libvpx --enable-libwavpack --enable-libwebp --enable-libx264 '
            '--enable-libx265 --enable-libxavs --enable-libxvid --enable-libzimg '
            '--enable-lzma --enable-decklink --enable-zlib',

            'libpostproc license: GPL version 3 or later',

            '--enable-gpl --enable-version3 --enable-dxva2 --enable-libmfx --enable-nvenc '
            '--enable-avisynth --enable-bzlib --enable-fontconfig --enable-frei0r '
            '--enable-gnutls --enable-iconv --enable-libass --enable-libbluray '
            '--enable-libbs2b --enable-libcaca --enable-libfreetype --enable-libgme '
            '--enable-libgsm --enable-libilbc --enable-libmodplug --enable-libmp3lame '
            '--enable-libopencore-amrnb --enable-libopencore-amrwb --enable-libopenh264 '
            '--enable-libopenjpeg --enable-libopus --enable-librtmp --enable-libsnappy '
            '--enable-libsoxr --enable-libspeex --enable-libtheora --enable-libtwolame '
            '--enable-libvidstab --enable-libvo-amrwbenc --enable-libvorbis '
            '--enable-libvpx --enable-libwavpack --enable-libwebp --enable-libx264 '
            '--enable-libx265 --enable-libxavs --enable-libxvid --enable-libzimg '
            '--enable-lzma --enable-decklink --enable-zlib',

            'libswresample license: GPL version 3 or later',
            '--enable-gpl --enable-version3 --enable-dxva2 --enable-libmfx --enable-nvenc '
            '--enable-avisynth --enable-bzlib --enable-fontconfig --enable-frei0r '
            '--enable-gnutls --enable-iconv --enable-libass --enable-libbluray '
            '--enable-libbs2b --enable-libcaca --enable-libfreetype --enable-libgme '
            '--enable-libgsm --enable-libilbc --enable-libmodplug --enable-libmp3lame '
            '--enable-libopencore-amrnb --enable-libopencore-amrwb --enable-libopenh264 '
            '--enable-libopenjpeg --enable-libopus --enable-librtmp --enable-libsnappy '
            '--enable-libsoxr --enable-libspeex --enable-libtheora --enable-libtwolame '
            '--enable-libvidstab --enable-libvo-amrwbenc --enable-libvorbis '
            '--enable-libvpx --enable-libwavpack --enable-libwebp --enable-libx264 '
            '--enable-libx265 --enable-libxavs --enable-libxvid --enable-libzimg '
            '--enable-lzma --enable-decklink --enable-zlib',

            'libswscale license: GPL version 3 or later',
            '--enable-gpl --enable-version3 --enable-dxva2 --enable-libmfx --enable-nvenc '
            '--enable-avisynth --enable-bzlib --enable-fontconfig --enable-frei0r '
            '--enable-gnutls --enable-iconv --enable-libass --enable-libbluray '
            '--enable-libbs2b --enable-libcaca --enable-libfreetype --enable-libgme '
            '--enable-libgsm --enable-libilbc --enable-libmodplug --enable-libmp3lame '
            '--enable-libopencore-amrnb --enable-libopencore-amrwb --enable-libopenh264 '
            '--enable-libopenjpeg --enable-libopus --enable-librtmp --enable-libsnappy '
            '--enable-libsoxr --enable-libspeex --enable-libtheora --enable-libtwolame '
            '--enable-libvidstab --enable-libvo-amrwbenc --enable-libvorbis '
            '--enable-libvpx --enable-libwavpack --enable-libwebp --enable-libx264 '
            '--enable-libx265 --enable-libxavs --enable-libxvid --enable-libzimg '
            '--enable-lzma --enable-decklink --enable-zlib',

            'libavutil license: GPL version 3 or later',

            'This software is derived from the GNU GPL XviD codec (1.3.0).'
        ]

        self.check_matched_texts(
            test_loc='matched_text/ffmpeg/ffmpeg.exe',
            expected_texts=expected_texts,
            whole_lines=True
        )

    def test_matched_text_is_collected_correctly_in_binary_ffmpeg_windows_not_whole_lines(self):
        expected_texts = [
            'enable-gpl --enable-version3 --',
            'enable-gpl --enable-version3 --',
            'is free software; you can redistribute it and/or modify\n'
            'it under the terms of the GNU General Public License as published by\n'
            'the Free Software Foundation; either version 3 of the License, or\n'
            '(at your option) any later version.\n'
            '%s is distributed in the hope that it will be useful,\n'
            'but WITHOUT ANY WARRANTY; without even the implied warranty of\n'
            'MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n'
            'GNU General Public License for more details.\n'
            'You should have received a copy of the GNU General Public License\n'
            'along with %s.  If not, see <http://www.gnu.org/licenses/>.',
            'enable-gpl --enable-version3 --',
            'license: GPL version 3 or later',
            'enable-gpl --enable-version3 --',
            'license: GPL version 3 or later',
            'enable-gpl --enable-version3 --',
            'license: GPL version 3 or later',
            'enable-gpl --enable-version3 --',
            'license: GPL version 3 or later',
            'enable-gpl --enable-version3 --',
            'license: GPL version 3 or later',
            'enable-gpl --enable-version3 --',
            'license: GPL version 3 or later',
            'enable-gpl --enable-version3 --',
            'license: GPL version 3 or later',
            'This software is derived from the GNU GPL XviD codec ('
        ]

        self.check_matched_texts(
            test_loc='matched_text/ffmpeg/ffmpeg.exe',
            expected_texts=expected_texts,
            whole_lines=False,
        )

    def test_matched_text_is_collected_correctly_in_binary_ffmpeg_elf_whole_lines(self):
        expected_texts = [
            '--prefix=/usr --extra-version=0ubuntu0.1 --build-suffix=-ffmpeg '
            '--toolchain=hardened --libdir=/usr/lib/x86_64-linux-gnu '
            '--incdir=/usr/include/x86_64-linux-gnu --cc=cc --cxx=g++ --enable-gpl '
            '--enable-shared --disable-stripping --disable-decoder=libopenjpeg '
            '--disable-decoder=libschroedinger --enable-avresample --enable-avisynth '
            '--enable-gnutls --enable-ladspa --enable-libass --enable-libbluray '
            '--enable-libbs2b --enable-libcaca --enable-libcdio --enable-libflite '
            '--enable-libfontconfig --enable-libfreetype --enable-libfribidi '
            '--enable-libgme --enable-libgsm --enable-libmodplug --enable-libmp3lame '
            '--enable-libopenjpeg --enable-libopus --enable-libpulse --enable-librtmp '
            '--enable-libschroedinger --enable-libshine --enable-libsnappy '
            '--enable-libsoxr --enable-libspeex --enable-libssh --enable-libtheora '
            '--enable-libtwolame --enable-libvorbis --enable-libvpx --enable-libwavpack '
            '--enable-libwebp --enable-libx265 --enable-libxvid --enable-libzvbi '
            '--enable-openal --enable-opengl --enable-x11grab --enable-libdc1394 '
            '--enable-libiec61883 --enable-libzmq --enable-frei0r --enable-libx264 '
            '--enable-libopencv',
            '%sconfiguration: --prefix=/usr --extra-version=0ubuntu0.1 '
            '--build-suffix=-ffmpeg --toolchain=hardened '
            '--libdir=/usr/lib/x86_64-linux-gnu --incdir=/usr/include/x86_64-linux-gnu '
            '--cc=cc --cxx=g++ --enable-gpl --enable-shared --disable-stripping '
            '--disable-decoder=libopenjpeg --disable-decoder=libschroedinger '
            '--enable-avresample --enable-avisynth --enable-gnutls --enable-ladspa '
            '--enable-libass --enable-libbluray --enable-libbs2b --enable-libcaca '
            '--enable-libcdio --enable-libflite --enable-libfontconfig '
            '--enable-libfreetype --enable-libfribidi --enable-libgme --enable-libgsm '
            '--enable-libmodplug --enable-libmp3lame --enable-libopenjpeg '
            '--enable-libopus --enable-libpulse --enable-librtmp --enable-libschroedinger '
            '--enable-libshine --enable-libsnappy --enable-libsoxr --enable-libspeex '
            '--enable-libssh --enable-libtheora --enable-libtwolame --enable-libvorbis '
            '--enable-libvpx --enable-libwavpack --enable-libwebp --enable-libx265 '
            '--enable-libxvid --enable-libzvbi --enable-openal --enable-opengl '
            '--enable-x11grab --enable-libdc1394 --enable-libiec61883 --enable-libzmq '
            '--enable-frei0r --enable-libx264 --enable-libopencv',
            '%s is free software; you can redistribute it and/or modify\n'
            'it under the terms of the GNU General Public License as published by\n'
            'the Free Software Foundation; either version 2 of the License, or\n'
            '(at your option) any later version.\n'
            '%s is distributed in the hope that it will be useful,\n'
            'but WITHOUT ANY WARRANTY; without even the implied warranty of\n'
            'MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n'
            'GNU General Public License for more details.\n'
            'You should have received a copy of the GNU General Public License\n'
            'along with %s; if not, write to the Free Software\n'
            'Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA'
        ]

        self.check_matched_texts(
            test_loc='matched_text/ffmpeg/ffmpeg',
            expected_texts=expected_texts,
            whole_lines=True,
        )

    def test_matched_text_is_collected_correctly_in_binary_ffmpeg_static_whole_lines(self):
        expected_texts = ['libswresample license: LGPL version 2.1 or later']
        self.check_matched_texts(
            test_loc='matched_text/ffmpeg/libavsample.lib',
            expected_texts=expected_texts,
            whole_lines=True,
        )
