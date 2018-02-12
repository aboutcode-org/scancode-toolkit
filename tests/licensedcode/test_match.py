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

import os

from commoncode.testcase import FileBasedTesting

from licensedcode import index
from licensedcode.match import filter_contained_matches
from licensedcode.match import LicenseMatch
from licensedcode.models import Rule
from licensedcode.models import load_rules
from licensedcode.spans import Span
from licensedcode.match import merge_matches
from licensedcode.match import get_full_matched_text

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


class TestLicenseMatchBasic(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_LicenseMatch_equality(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))
        m2 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))

        assert m1 == m2

        r2 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        m3 = LicenseMatch(rule=r2, qspan=Span(0, 2), ispan=Span(0, 2))

        assert m1 != m3

        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))
        r2 = Rule(text_file='r2', licenses=['gpl', 'apache-2.0'])
        m2 = LicenseMatch(rule=r2, qspan=Span(0, 2), ispan=Span(0, 2))

        assert m1 != m2
        assert m2 != m1

        r3 = Rule(text_file='r3', licenses=['gpl', 'apache-2.0'])
        m3 = LicenseMatch(rule=r3, qspan=Span(0, 2), ispan=Span(0, 2))

        assert m2 != m3

    def test_LicenseMatch_not_equal(self):
        r1 = Rule(text_file='r1', licenses=['apache-1.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))
        r2 = Rule(text_file='r2', licenses=['gpl', 'apache-2.0'])
        m2 = LicenseMatch(rule=r2, qspan=Span(0, 2), ispan=Span(0, 2))

        assert m1 != m2

        r3 = Rule(text_file='r3', licenses=['apache-1.0', 'gpl'])
        m3 = LicenseMatch(rule=r3, qspan=Span(0, 2), ispan=Span(0, 2))

        assert m1 == m3

        r4 = Rule(text_file='r4', licenses=['apache-1.0', 'gpl'])
        m4 = LicenseMatch(rule=r4, qspan=Span(1, 2), ispan=Span(1, 2))

        assert not m1 == m4

    def test_LicenseMatch_equals(self):
        rule = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        m1 = LicenseMatch(rule=rule, matcher='chunk1', qspan=Span(0, 7), ispan=Span(0, 7), start_line=1, end_line=1)
        m2 = LicenseMatch(rule=rule, matcher='chunk2', qspan=Span(0, 7), ispan=Span(0, 7), start_line=1, end_line=1)
        assert m1 == m2

        m3 = LicenseMatch(rule=rule, matcher='chunk3', qspan=Span(16, 23), ispan=Span(0, 7), start_line=3, end_line=3)
        assert m1 != m3

    def test_LicenseMatch_comparisons(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
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
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        r2 = Rule(text_file='r2', licenses=['apache-2.0', 'gpl2'])

        m1 = LicenseMatch(rule=r1, qspan=Span(0, 5), ispan=Span(0, 5))
        m2 = LicenseMatch(rule=r2, qspan=Span(1, 6), ispan=Span(1, 6))

        try:
            m1.combine(m2)
        except TypeError:
            pass

    def test_combine_matches_with_same_rules(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])

        m1 = LicenseMatch(rule=r1, qspan=Span(0, 5), ispan=Span(0, 5))
        m2 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))

        match = m1.combine(m2)
        assert Span(0, 6) == match.qspan
        assert Span(0, 6) == match.ispan

    def test_combine_matches_cannot_combine_matches_with_same_licensing_and_different_rules(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        r2 = Rule(text_file='r2', licenses=['apache-2.0', 'gpl'])

        m1 = LicenseMatch(rule=r1, qspan=Span(0, 5), ispan=Span(0, 5))
        m2 = LicenseMatch(rule=r2, qspan=Span(1, 6), ispan=Span(1, 6))

        try:
            m1.combine(m2)
            self.fail('Should fail')
        except TypeError:
            pass

    def test_LicenseMatch_small(self):
        r1_text = u'licensed under the GPL, licensed under the GPL distribute extent of law'
        small_rule = Rule(text_file='small_rule', licenses=['apache-1.1'], _text=r1_text)

        r2_text = u'licensed under the GPL, licensed under the GPL re distribute extent of law' * 10
        long_rule = Rule(text_file='long_rule', licenses=['apache-1.1'], _text=r2_text)

        _idx = index.LicenseIndex([small_rule, long_rule])

        test = LicenseMatch(rule=small_rule, qspan=Span(0, 10), ispan=Span(0, 10), hispan=Span(12))
        assert test.small()
        test = LicenseMatch(rule=small_rule, qspan=Span(0, 10), ispan=Span(0, 10), hispan=Span(11, 12))
        assert test.small()

        test = LicenseMatch(rule=small_rule, qspan=Span(10, 11, 12), ispan=Span(10, 11, 12), hispan=Span(11, 12))
        assert test.small()

        test = LicenseMatch(rule=small_rule, qspan=Span(1, 6), ispan=Span(1, 6))
        assert test.small()

        test = LicenseMatch(rule=long_rule, qspan=Span(0, 10), ispan=Span(0, 10), hispan=Span(12))
        assert test.small()

        test = LicenseMatch(rule=long_rule, qspan=Span(5, 10), ispan=Span(5, 10), hispan=Span(5, 6))
        assert test.small()

        test = LicenseMatch(rule=small_rule, qspan=Span(1, 10), ispan=Span(1, 10), hispan=Span(3, 6))
        assert not test.small()

    def test_LicenseMatch_score_is_not_100_with_aho_match_and_extra_unknown_token_hash_match(self):
        text = (
            'this file is licensed under the GPL license version2 only '
            'or any other version. You can redistribute this file under '
            'this or any other license.')
        r1 = Rule(text_file='r1', licenses=['apache-1.1'], _text=text)
        idx = index.LicenseIndex([r1])

        querys = (
            'this file is licensed under the GPL license version2 only '
            + ' big ' +
            'or any other version. You can redistribute this file under '
            'this or any other license.')

        match = idx.match(query_string=querys)[0]
        assert match.score() < 100

    def test_LicenseMatch_score_is_not_100_with_aho_match_and_extra_unknown_token_seq_match(self):
        text = (
            'this file is licensed under the GPL license version2 only '
            'or any other version. You can redistribute this file under '
            'this or any other license.')
        r1 = Rule(text_file='r1', licenses=['apache-1.1'], _text=text)
        idx = index.LicenseIndex([r1])

        querys = (
            'this file is licensed under the GPL license version2 only '
            + ' is ' +
            'or any other version. You can redistribute this file under '
            'this or any other license.')

        match = idx.match(query_string=querys)[0]
        assert match.score() < 100

    def test_LicenseMatch_score_is_not_100_with_aho_match_and_extra_unknown_token_aho_match(self):
        text = (
            'this file is licensed under the GPL license version2 only '
            'or any other version. You can redistribute this file under '
            'this or any other license.')
        r1 = Rule(text_file='r1', licenses=['apache-1.1'], _text=text)
        idx = index.LicenseIndex([r1])

        querys = (
            'this this file is licensed under the GPL license version2 only '
            + ' big ' +
            'or any other version. You can redistribute this file under '
            'this or any other license. that')

        match = idx.match(query_string=querys)[0]
        assert match.score() < 100


class TestMergeMatches(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_merge_does_merge_non_contiguous_matches_in_sequence(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))
        m2 = LicenseMatch(rule=r1, qspan=Span(4, 6), ispan=Span(4, 6))
        m5 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))

        results = merge_matches([m1, m2, m5])
        assert [LicenseMatch(rule=r1, qspan=Span(0, 6), ispan=Span(0, 6))] == results

    def test_merge_does_not_merge_overlapping_matches_of_different_rules_with_different_licensing(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        r2 = Rule(text_file='r2', licenses=['apache-2.0', 'gpl2'])

        m1 = LicenseMatch(rule=r1, qspan=Span(0, 5), ispan=Span(0, 5))
        m2 = LicenseMatch(rule=r2, qspan=Span(1, 6), ispan=Span(1, 6))

        assert [m1, m2] == merge_matches([m1, m2])

    def test_merge_does_merge_overlapping_matches_of_same_rules_if_in_sequence(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])

        m1 = LicenseMatch(rule=r1, qspan=Span(0, 5), ispan=Span(0, 5))
        m2 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))

        assert [LicenseMatch(rule=r1, qspan=Span(0, 6), ispan=Span(0, 6))] == merge_matches([m1, m2])

    def test_merge_does_not_merge_overlapping_matches_of_same_rules_if_in_sequence_with_gaps(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        r1.length = 50

        m1 = LicenseMatch(rule=r1, qspan=Span(1, 3), ispan=Span(1, 3))
        m2 = LicenseMatch(rule=r1, qspan=Span(14, 20), ispan=Span(4, 10))

        expected = [LicenseMatch(rule=r1, qspan=Span(1, 3) | Span(14, 20), ispan=Span(1, 10))]
        results = merge_matches([m1, m2])
        assert expected == results

    def test_merge_does_not_merge_overlapping_matches_of_same_rules_if_in_sequence_with_gaps_for_long_match(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        r1.length = 20
        m1 = LicenseMatch(rule=r1, qspan=Span(1, 10), ispan=Span(1, 10))
        m2 = LicenseMatch(rule=r1, qspan=Span(14, 20), ispan=Span(14, 20))

        expected = [LicenseMatch(rule=r1, qspan=Span(1, 10) | Span(14, 20), ispan=Span(1, 10) | Span(14, 20))]
        results = merge_matches([m1, m2])
        assert expected == results

    def test_merge_does_not_merge_overlapping_matches_of_same_rules_if_in_not_sequence(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])

        m1 = LicenseMatch(rule=r1, qspan=Span(1, 3), ispan=Span(1, 3))
        m2 = LicenseMatch(rule=r1, qspan=Span(14, 20), ispan=Span(1, 3))

        matches = merge_matches([m1, m2])
        assert sorted([m1, m2]) == sorted(matches)

    def test_merge_does_not_merge_contained_matches_of_different_rules_with_same_licensing(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        r2 = Rule(text_file='r2', licenses=['apache-2.0', 'gpl'])

        m1 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))
        m2 = LicenseMatch(rule=r2, qspan=Span(1, 6), ispan=Span(1, 6))

        matches = merge_matches([m1, m2])
        assert sorted([m1, m2]) == sorted(matches)

    def test_files_does_filter_contained_matches_of_different_rules_with_same_licensing(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        r2 = Rule(text_file='r2', licenses=['apache-2.0', 'gpl'])

        m1 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))
        m2 = LicenseMatch(rule=r2, qspan=Span(1, 6), ispan=Span(1, 6))

        matches, discarded = filter_contained_matches([m1, m2])
        assert [m2] == matches
        assert [m1] == discarded

    def test_merge_does_not_merge_overlaping_matches_with_same_licensings(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        r2 = Rule(text_file='r2', licenses=['apache-2.0', 'gpl'])

        overlap = LicenseMatch(rule=r1, qspan=Span(0, 5), ispan=Span(0, 5))
        same_span1 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))
        same_span2 = LicenseMatch(rule=r2, qspan=Span(1, 6), ispan=Span(1, 6))

        result = merge_matches([overlap, same_span1, same_span2])
        expected = [
            LicenseMatch(rule=r1, qspan=Span(0, 6), ispan=Span(0, 6)),
            LicenseMatch(rule=r2, qspan=Span(1, 6), ispan=Span(1, 6)),
        ]
        assert sorted(expected) == sorted(result)

    def test_filter_does_filter_overlaping_matches_with_same_licensings(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        r2 = Rule(text_file='r2', licenses=['apache-2.0', 'gpl'])

        overlap = LicenseMatch(rule=r1, qspan=Span(0, 5), ispan=Span(0, 5))
        same_span1 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))
        same_span2 = LicenseMatch(rule=r2, qspan=Span(1, 6), ispan=Span(1, 6))

        matches, discarded = filter_contained_matches([overlap, same_span1, same_span2])
        assert [overlap] == matches
        assert discarded

    def test_filter_prefers_longer_overlaping_matches(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        r2 = Rule(text_file='r2', licenses=['apache-2.0', 'gpl'])

        overlap = LicenseMatch(rule=r1, qspan=Span(0, 5), ispan=Span(0, 5))
        same_span1 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))
        same_span2 = LicenseMatch(rule=r2, qspan=Span(1, 8), ispan=Span(1, 8))

        matches, discarded = filter_contained_matches([overlap, same_span1, same_span2])
        assert [same_span2] == matches
        assert discarded

    def test_merge_contiguous_touching_matches_in_sequence(self):
        r1 = Rule(_text='r1', licenses=['apache-2.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))
        m2 = LicenseMatch(rule=r1, qspan=Span(3, 6), ispan=Span(3, 6))

        result = merge_matches([m1, m2])
        match = result[0]
        assert LicenseMatch(rule=r1, qspan=Span(0, 6), ispan=Span(0, 6)) == match

    def test_merge_contiguous_contained_matches(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))
        m2 = LicenseMatch(rule=r1, qspan=Span(3, 6), ispan=Span(3, 6))
        m5 = LicenseMatch(rule=r1, qspan=Span(7, 8), ispan=Span(7, 8))

        result = merge_matches([m1, m2, m5])
        assert [LicenseMatch(rule=r1, qspan=Span(0, 8), ispan=Span(0, 8))] == result

    def test_merge_should_not_merge_repeated_matches_out_of_sequence(self):
        rule = Rule(text_file='gpl-2.0_49.RULE', licenses=[u'gpl-2.0'])
        rule.rid = 2615
        m1 = LicenseMatch(rule=rule, matcher='chunk1', qspan=Span(0, 7), ispan=Span(0, 7))
        m2 = LicenseMatch(rule=rule, matcher='chunk2', qspan=Span(8, 15), ispan=Span(0, 7))
        m3 = LicenseMatch(rule=rule, matcher='chunk3', qspan=Span(16, 23), ispan=Span(0, 7))
        result = merge_matches([m1, m2, m3])
        assert [m1, m2, m3] == result

    def test_merge_merges_contained_and_overlapping_match(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 5), ispan=Span(0, 5))
        contained = LicenseMatch(rule=r1, qspan=Span(1, 4), ispan=Span(1, 4))
        overlapping = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))
        assert contained in overlapping
        assert contained in m1
        result = merge_matches([m1, contained, overlapping])
        expected = [LicenseMatch(rule=r1, qspan=Span(0, 6), ispan=Span(0, 6))]
        assert expected == result

    def test_merge_does_not_merge_multiple_contained_matches_across_rules(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 5), ispan=Span(0, 5))

        r2 = Rule(text_file='r2', licenses=['apache-2.0', 'gpl'])
        contained1 = LicenseMatch(rule=r2, qspan=Span(1, 2), ispan=Span(1, 2))

        r3 = Rule(text_file='r3', licenses=['apache-2.0', 'gpl'])
        contained2 = LicenseMatch(rule=r3, qspan=Span(3, 4), ispan=Span(3, 4))

        r5 = Rule(text_file='r5', licenses=['apache-2.0', 'gpl'])
        m5 = LicenseMatch(rule=r5, qspan=Span(1, 6), ispan=Span(1, 6))

        result = merge_matches([m1, contained1, contained2, m5])
        assert sorted([m1, contained1, contained2, m5]) == sorted(result)

    def test_filter_does_not_filter_multiple_contained_matches_across_rules(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 5), ispan=Span(0, 5))

        r2 = Rule(text_file='r2', licenses=['apache-2.0', 'gpl'])
        contained1 = LicenseMatch(rule=r2, qspan=Span(1, 2), ispan=Span(1, 2))

        r3 = Rule(text_file='r3', licenses=['apache-2.0', 'gpl'])
        contained2 = LicenseMatch(rule=r3, qspan=Span(3, 4), ispan=Span(3, 4))

        r5 = Rule(text_file='r5', licenses=['apache-2.0', 'gpl'])
        m5 = LicenseMatch(rule=r5, qspan=Span(1, 6), ispan=Span(1, 6))

        result, _discarded = filter_contained_matches([m1, contained1, contained2, m5])
        assert [m1] == result

    def test_filter_multiple_contained_matches(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 5), ispan=Span(0, 5))

        r2 = Rule(text_file='r2', licenses=['apache-2.0', 'gpl'])
        contained1 = LicenseMatch(rule=r2, qspan=Span(1, 2), ispan=Span(1, 2))

        r3 = Rule(text_file='r3', licenses=['apache-2.0', 'gpl'])
        contained2 = LicenseMatch(rule=r3, qspan=Span(3, 4), ispan=Span(3, 4))

        r5 = Rule(text_file='r5', licenses=['apache-2.0', 'gpl'])
        m5 = LicenseMatch(rule=r5, qspan=Span(1, 6), ispan=Span(1, 6))

        matches, discarded = filter_contained_matches([m1, contained1, contained2, m5])
        assert [m1] == matches
        assert sorted([m5, contained1, contained2, ]) == sorted(discarded)

    def test_merge_does_not_merge_matches_with_same_spans_if_licenses_are_identical_but_rule_differ(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0'])
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))
        m5 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))

        r2 = Rule(text_file='r2', licenses=['apache-2.0'])
        m2 = LicenseMatch(rule=r2, qspan=Span(0, 2), ispan=Span(0, 2))

        matches = merge_matches([m1, m2, m5])
        assert sorted([LicenseMatch(rule=r1, qspan=Span(0, 6), ispan=Span(0, 6)), m2]) == sorted(matches)

    def test_filter_filters_matches_with_same_spans_if_licenses_are_identical_but_rule_differ(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0'])
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))
        m5 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))

        r2 = Rule(text_file='r2', licenses=['apache-2.0'])
        m2 = LicenseMatch(rule=r2, qspan=Span(0, 2), ispan=Span(0, 2))

        matches, discarded = filter_contained_matches([m1, m2, m5])

        assert [m5] == matches
        assert discarded

    def test_merge_then_filter_matches_with_same_spans_if_licenses_are_identical_but_rule_differ(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0'])
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))
        m5 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))

        r2 = Rule(text_file='r2', licenses=['apache-2.0'])
        m2 = LicenseMatch(rule=r2, qspan=Span(0, 2), ispan=Span(0, 2))

        matches = merge_matches([m1, m2, m5])
        matches, discarded = filter_contained_matches(matches)

        assert [LicenseMatch(rule=r1, qspan=Span(0, 6), ispan=Span(0, 6))] == matches
        assert discarded

    def test_merge_overlapping_matches(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0'])
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))
        m2 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))

        matches = merge_matches([m1, m2])
        assert [LicenseMatch(rule=r1, qspan=Span(0, 6), ispan=Span(0, 6))] == matches

    def test_merge_does_not_merges_matches_with_same_spans_if_licenses_are_the_same_but_have_different_licenses_ordering(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))
        m5 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))

        r2 = Rule(text_file='r2', licenses=['gpl', 'apache-2.0'])
        m2 = LicenseMatch(rule=r2, qspan=Span(0, 2), ispan=Span(0, 2))

        result = merge_matches([m1, m2, m5])
        assert sorted([LicenseMatch(rule=r1, qspan=Span(0, 6), ispan=Span(0, 6)), m2]) == sorted(result)

    def test_merge_does_not_merges_matches_with_same_spans_if_rules_are_different(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))
        m5 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))

        r2 = Rule(text_file='r2', licenses=['apache-2.0', 'gpl'])
        m2 = LicenseMatch(rule=r2, qspan=Span(0, 2), ispan=Span(0, 2))

        result = merge_matches([m1, m2, m5])
        assert sorted([LicenseMatch(rule=r1, qspan=Span(0, 6), ispan=Span(0, 6)), m2]) == sorted(result)

    def test_merge_merges_duplicate_matches(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0'])
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 8), ispan=Span(0, 8))
        m2 = LicenseMatch(rule=r1, qspan=Span(0, 8), ispan=Span(0, 8))

        matches = merge_matches([m1, m2])
        assert ([m1] == matches) or ([m2] == matches)

    def test_merge_does_not_merge_overlapping_matches_in_sequence_with_assymetric_overlap(self):
        r1 = Rule(text_file='r1', licenses=[u'lgpl-2.0-plus'])

        # ---> merge_matches: current: LicenseMatch<'3-seq', lines=(9, 28), 'lgpl-2.0-plus_9.RULE', u'lgpl-2.0-plus', choice=False, score=87.5, qlen=126, ilen=126, hilen=20, rlen=144, qreg=(50, 200), ireg=(5, 142), qspan=Span(50, 90)|Span(92, 142)|Span(151, 182)|Span(199, 200), ispan=Span(5, 21)|Span(23, 46)|Span(48, 77)|Span(79, 93)|Span(95, 100)|Span(108, 128)|Span(130, 142), hispan=Span(10)|Span(14)|Span(18)|Span(24)|Span(27)|Span(52)|Span(57)|Span(61)|Span(65, 66)|Span(68)|Span(70)|Span(80)|Span(88)|Span(96)|Span(111)|Span(113)|Span(115)|Span(131)|Span(141)>
        # ---> merge_matches: next:    LicenseMatch<'2-aho', lines=(28, 44), 'lgpl-2.0-plus_9.RULE', u'lgpl-2.0-plus', choice=False, score=100.0, qlen=144, ilen=144, hilen=21, rlen=144, qreg=(198, 341), ireg=(0, 143), qspan=Span(198, 341), ispan=Span(0, 143), hispan=Span(1)|Span(10)|Span(14)|Span(18)|Span(24)|Span(27)|Span(52)|Span(57)|Span(61)|Span(65, 66)|Span(68)|Span(70)|Span(80)|Span(88)|Span(96)|Span(111)|Span(113)|Span(115)|Span(131)|Span(141)>
        #     ---> ###merge_matches: next overlaps in sequence current, merged as new: LicenseMatch<'3-seq 2-aho', lines=(9, 44), 'lgpl-2.0-plus_9.RULE', u'lgpl-2.0-plus', choice=False, score=100.0, qlen=268, ilen=144, hilen=21, rlen=144, qreg=(50, 341), ireg=(0, 143), qspan=Span(50, 90)|Span(92, 142)|Span(151, 182)|Span(198, 341), ispan=Span(0, 143), his

        # ---> merge_matches: current: qlen=126, ilen=126, hilen=20, rlen=144, qreg=(50, 200), ireg=(5, 142)
        # ---> merge_matches: next:    qlen=144, ilen=144, hilen=21, rlen=144, qreg=(198, 341), ireg=(0, 143)

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
        assert [m1, m2] == matches


class TestLicenseMatchFilter(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_filter_matches_filters_multiple_nested_contained_matches_and_large_overlapping(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 5), ispan=Span(0, 5))
        large_overlap = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))
        contained = LicenseMatch(rule=r1, qspan=Span(1, 4), ispan=Span(1, 4))
        in_contained = LicenseMatch(rule=r1, qspan=Span(2, 3), ispan=Span(2, 3))
        result, discarded = filter_contained_matches([m1, contained, in_contained, large_overlap])
        assert [m1] == result
        assert discarded

    def test_filter_matches_filters_non_contiguous_or_overlapping__but_contained_matches(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, qspan=Span(1, 2), ispan=Span(1, 2))
        m2 = LicenseMatch(rule=r1, qspan=Span(3, 6), ispan=Span(3, 6))
        m3 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))
        m4 = LicenseMatch(rule=r1, qspan=Span(0, 7), ispan=Span(0, 7))
        m5 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))

        result, discarded = filter_contained_matches([m1, m2, m3, m4, m5])
        assert [m4] == result
        assert discarded

    def test_filter_matches_filters_non_contiguous_or_overlapping_contained_matches_with_touching_boundaries(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))

        r2 = Rule(text_file='r2', licenses=['apache-2.0', 'gpl'])
        m2 = LicenseMatch(rule=r2, qspan=Span(3, 7), ispan=Span(3, 7))

        r3 = Rule(text_file='r3', licenses=['apache-2.0', 'gpl'])
        m3 = LicenseMatch(rule=r3, qspan=Span(0, 6), ispan=Span(0, 6))

        r6 = Rule(text_file='r6', licenses=['apache-2.0', 'gpl'])
        m6 = LicenseMatch(rule=r6, qspan=Span(1, 7), ispan=Span(1, 7))

        r5 = Rule(text_file='r5', licenses=['apache-2.0', 'gpl'])
        m5 = LicenseMatch(rule=r5, qspan=Span(1, 6), ispan=Span(1, 6))

        r4 = Rule(text_file='r4', licenses=['apache-2.0', 'gpl'])
        m4 = LicenseMatch(rule=r4, qspan=Span(0, 7), ispan=Span(0, 7))

        result, discarded = filter_contained_matches([m1, m2, m3, m4, m5, m6])
        assert [m4] == result
        assert discarded

    def test_filter_matches_does_filter_matches_with_contained_spans_if_licenses_are_different(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0'])
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))

        r2 = Rule(text_file='r2', licenses=['apache-2.0'])
        m2 = LicenseMatch(rule=r2, qspan=Span(1, 6), ispan=Span(1, 6))

        r3 = Rule(text_file='r3', licenses=['apache-1.1'])
        m3 = LicenseMatch(rule=r3, qspan=Span(0, 2), ispan=Span(0, 2))

        matches, discarded = filter_contained_matches([m1, m2, m3])
        assert [m2] == matches
        assert discarded

    def test_filter_matches_filters_matches_with_medium_overlap_only_if_license_are_the_same(self):
        r1 = Rule(text_file='r1', licenses=['apache-1.1'])
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 10), ispan=Span(0, 10))
        m2 = LicenseMatch(rule=r1, qspan=Span(3, 11), ispan=Span(3, 11))

        r2 = Rule(text_file='r2', licenses=['gpl', 'apache-2.0'])
        m3 = LicenseMatch(rule=r2, qspan=Span(7, 15), ispan=Span(7, 15))

        result, discarded = filter_contained_matches([m1, m2, m3])
        assert sorted([m1, m3]) == sorted(result)
        assert discarded

    def test_filter_matches_handles_interlaced_matches_with_overlap_and_same_license(self):
        rule_dir = self.get_test_loc('match_filter/rules')
        idx = index.LicenseIndex(load_rules(rule_dir))
        rules = {r.identifier: r for r in idx.rules_by_rid}
        query_loc = self.get_test_loc('match_filter/query')
        matches = idx.match(location=query_loc)
        expected = [
            # filtered: LicenseMatch(matcher='3-seq', rule=rules['rule1.RULE'], qspan=Span(4, 47) | Span(50, 59), ispan=Span(1, 53)),
            LicenseMatch(matcher='2-aho', rule=rules['rule2.RULE'], qspan=Span(24, 86), ispan=Span(0, 62)),
        ]

        assert expected == matches


class TestLicenseMatchScore(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_LicenseMatch_score_100(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0'])
        r1.relevance = 100
        r1.length = 3

        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))
        assert m1.score() == 100

    def test_LicenseMatch_score_50(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0'])
        r1.relevance = 50
        r1.length = 3

        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))
        assert m1.score() == 50

    def test_LicenseMatch_score_25_with_stored_relevance(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0'])
        r1.relevance = 50
        r1.length = 6

        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))
        # NB we do not have a query here
        assert m1.score() == 25

    def test_LicenseMatch_score_0(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0'])
        r1.relevance = 0
        r1.length = 6

        m1 = LicenseMatch(rule=r1, qspan=Span(), ispan=Span())
        assert m1.score() == 0

    def test_LicenseMatch_score_0_relevance(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0'])
        r1.relevance = 0
        r1.length = 6

        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))
        assert m1.score() == 0

    def test_LicenseMatch_score_100_contiguous(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0'])
        r1.relevance = 100
        r1.length = 42

        m1 = LicenseMatch(rule=r1, qspan=Span(0, 41), ispan=Span(0, 41))
        assert m1.score() == 100

    def test_LicenseMatch_score_100_non_contiguous(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0'])
        r1.relevance = 100
        r1.length = 42

        m1 = LicenseMatch(rule=r1, qspan=Span(0, 19) | Span(30, 51), ispan=Span(0, 41))
        assert m1.score() == 80.77


class TestCollectLicenseMatchTexts(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_get_full_matched_text(self):
        rule_text = u'''
            Copyright {{some copyright}}
            THIS IS FROM {{THE CODEHAUS}} AND CONTRIBUTORS
            IN NO EVENT SHALL {{THE CODEHAUS}} OR ITS CONTRIBUTORS BE LIABLE
            EVEN IF ADVISED OF THE {{POSSIBILITY OF SUCH}} DAMAGE
        '''

        rule = Rule(_text=rule_text, licenses=['test'],)
        idx = index.LicenseIndex([rule])

        querys = u'''
            foobar 45 Copyright 2003 (C) James. All Rights Reserved.
            THIS IS FROM THE CODEHAUS AND CONTRIBUTORS
            IN NO EVENT SHALL THE best CODEHAUS OR ITS CONTRIBUTORS BE LIABLE
            EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. chabada DAMAGE 12 ABC
        '''
        result = idx.match(query_string=querys)
        assert 1 == len(result)
        match = result[0]

        expected = u"""Copyright [2003] ([C]) [James]. [All] [Rights] [Reserved].
            THIS IS FROM [THE] [CODEHAUS] AND CONTRIBUTORS
            IN NO EVENT SHALL [THE] [best] [CODEHAUS] OR ITS CONTRIBUTORS BE LIABLE
            EVEN IF ADVISED OF THE [POSSIBILITY] [OF] [SUCH] DAMAGE"""
        matched_text = u''.join(get_full_matched_text(match, query_string=querys, idx=idx))
        assert expected == matched_text

        # test again using a template
        expected = u"""Copyright <br>2003</br> (<br>C</br>) <br>James</br>. <br>All</br> <br>Rights</br> <br>Reserved</br>.
            THIS IS FROM <br>THE</br> <br>CODEHAUS</br> AND CONTRIBUTORS
            IN NO EVENT SHALL <br>THE</br> <br>best</br> <br>CODEHAUS</br> OR ITS CONTRIBUTORS BE LIABLE
            EVEN IF ADVISED OF THE <br>POSSIBILITY</br> <br>OF</br> <br>SUCH</br> DAMAGE"""
        matched_text = u''.join(get_full_matched_text(match, query_string=querys, idx=idx, highlight_not_matched=u'<br>%s</br>'))
        assert expected == matched_text

        # test again using whole_lines
        expected = u"""            foobar 45 Copyright 2003 (C) James. All Rights Reserved.
            THIS IS FROM THE CODEHAUS AND CONTRIBUTORS
            IN NO EVENT SHALL THE best CODEHAUS OR ITS CONTRIBUTORS BE LIABLE
            EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. chabada DAMAGE 12 ABC\n"""
        matched_text = u''.join(get_full_matched_text(match, query_string=querys, idx=idx, highlight_not_matched=u'%s', whole_lines=True))
        assert expected == matched_text
