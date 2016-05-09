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

from licensedcode import index
from licensedcode.match import filter_matches
from licensedcode.match import LicenseMatch
from licensedcode import models
from licensedcode.models import Rule
from licensedcode.whoosh_spans.spans import Span
from licensedcode import query


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

    def test_LicenseMatch_lines(self):
        rule = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        line_by_pos = {x: 1 for x in range(0, 8)}
        line_by_pos.update({x: 2 for x in range(8, 16)})
        line_by_pos.update({x: 3 for x in range(16, 24)})

        m1 = LicenseMatch(rule=rule, _type='chunk1', qspan=Span(0, 7), ispan=Span(0, 7), line_by_pos=line_by_pos)
        assert (1, 1) == m1.lines
        m2 = LicenseMatch(rule=rule, _type='chunk2', qspan=Span(0, 7), ispan=Span(0, 7), line_by_pos=line_by_pos)
        assert (1, 1) == m2.lines
        assert m1 == m2

        m3 = LicenseMatch(rule=rule, _type='chunk3', qspan=Span(16, 23), ispan=Span(0, 7), line_by_pos=line_by_pos)
        assert (3, 3) == m3.lines
        assert m1 != m3

    def test_LicenseMatch_same(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))
        r2 = Rule(text_file='r2', licenses=['gpl', 'apache-2.0'])
        m2 = LicenseMatch(rule=r2, qspan=Span(0, 2), ispan=Span(0, 2))

        assert m1.same(m2)
        assert m2.same(m1)

    def test_LicenseMatch_not_same(self):
        r1 = Rule(text_file='r1', licenses=['apache-1.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))
        r2 = Rule(text_file='r2', licenses=['gpl', 'apache-2.0'])
        m2 = LicenseMatch(rule=r2, qspan=Span(0, 2), ispan=Span(0, 2))

        assert not m1.same(m2)
        assert not m2.same(m1)

        r3 = Rule(text_file='r3', licenses=['apache-1.0', 'gpl'])
        m3 = LicenseMatch(rule=r3, qspan=Span(0, 2), ispan=Span(0, 2))

        assert m1.same(m3)
        assert m3.same(m1)

        r4 = Rule(text_file='r4', licenses=['apache-1.0', 'gpl'])
        m4 = LicenseMatch(rule=r4, qspan=Span(1, 2), ispan=Span(1, 2))

        assert not m1.same(m4)
        assert not m4.same(m1)

    def test_LicenseMatch_comparisons(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        contained1 = LicenseMatch(rule=r1, qspan=Span(0, 5), ispan=Span(0, 5))
        contained2 = LicenseMatch(rule=r1, qspan=Span(1, 4), ispan=Span(1, 4))
        same_span1 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))
        same_span2 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))
        before_after = LicenseMatch(rule=r1, qspan=Span(8, 9), ispan=Span(8, 9))
        touching = LicenseMatch(rule=r1, qspan=Span(7, 7), ispan=Span(7, 7))
        overlap = LicenseMatch(rule=r1, qspan=Span(4, 7), ispan=Span(4, 7))

        assert same_span1.same(same_span2)
        assert same_span1 in same_span2

        assert not same_span1.touch(same_span2)
        assert not same_span2.touch(same_span1)

        assert same_span1.overlap(same_span2)
        assert same_span2.overlap(same_span1)

        assert contained1 not in same_span1
        assert same_span1 not in contained1

        assert contained1.overlap(same_span2)
        assert not contained1.touch(same_span2)
        assert not same_span2.touch(contained1)

        assert contained1.surround(contained2)

        assert contained2 in same_span2
        assert contained2 in contained1

        assert contained2.overlap(overlap)
        assert overlap.overlap(contained2)
        assert overlap.overlap(same_span1)
        assert not overlap.overlap(before_after)

        assert before_after.is_after(same_span1)

        assert before_after.touch(touching)
        assert before_after.is_after(touching)

        assert touching.touch(before_after)
        assert not before_after.touch(same_span1)
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

    def test_combine_matches_with_same_licensing(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        r2 = Rule(text_file='r2', licenses=['apache-2.0', 'gpl'])

        m1 = LicenseMatch(rule=r1, qspan=Span(0, 5), ispan=Span(0, 5))
        m2 = LicenseMatch(rule=r2, qspan=Span(1, 6), ispan=Span(1, 6))

        match = m1.combine(m2)
        assert Span(0, 6) == match.qspan
        assert Span(0, 6) == match.ispan


class TestLicenseMatchMerge(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_merge_does_merge_non_contiguous_matches_in_sequence(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))
        m2 = LicenseMatch(rule=r1, qspan=Span(4, 6), ispan=Span(4, 6))
        m5 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))

        matches = LicenseMatch.merge([m1, m2, m5])
        expected = LicenseMatch(rule=r1, qspan=Span(0, 6), ispan=Span(0, 6))
        assert [expected] == matches

    def test_merge_cannot_merge_contained_matches_of_different_rules(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        r2 = Rule(text_file='r2', licenses=['apache-2.0', 'gpl2'])

        overlap = LicenseMatch(rule=r1, qspan=Span(0, 5), ispan=Span(0, 5))
        same_span1 = LicenseMatch(rule=r2, qspan=Span(1, 6), ispan=Span(1, 6))

        try:
            LicenseMatch.merge([overlap, same_span1])
        except TypeError:
            pass

    def test_merge_can_merge_contained_matches_of_same_licensing(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        r2 = Rule(text_file='r2', licenses=['apache-2.0', 'gpl'])

        overlap = LicenseMatch(rule=r1, qspan=Span(0, 5), ispan=Span(0, 5))
        same_span1 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))
        same_span2 = LicenseMatch(rule=r2, qspan=Span(1, 6), ispan=Span(1, 6))

        result = LicenseMatch.merge([overlap, same_span1, same_span2])
        expected = [
            LicenseMatch(rule=r1, qspan=Span(0, 6), ispan=Span(0, 6)),
        ]
        assert expected == result

    def test_merge_contiguous_touching_matches_in_sequence(self):
        r1 = Rule(_text='r1', licenses=['apache-2.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))
        m2 = LicenseMatch(rule=r1, qspan=Span(3, 6), ispan=Span(3, 6))

        result = LicenseMatch.merge([m1, m2])
        match = result[0]
        assert LicenseMatch(rule=r1, qspan=Span(0, 6), ispan=Span(0, 6)) == match

    def test_merge_contiguous_contained_matches(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))
        m2 = LicenseMatch(rule=r1, qspan=Span(3, 6), ispan=Span(3, 6))
        m5 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))

        result = LicenseMatch.merge([m1, m2, m5])
        match = result[0]
        assert LicenseMatch(rule=r1, qspan=Span(0, 6), ispan=Span(0, 6)) == match

    def test_merge_should_not_merge_repeated_matches_out_of_sequence(self):
        rule = Rule(text_file='gpl-2.0_49.RULE', licenses=[u'gpl-2.0'])
        rule.rid = 2615
        m1 = LicenseMatch(rule=rule, _type='chunk1', qspan=Span(0, 7), ispan=Span(0, 7))
        m2 = LicenseMatch(rule=rule, _type='chunk2', qspan=Span(8, 15), ispan=Span(0, 7))
        m3 = LicenseMatch(rule=rule, _type='chunk3', qspan=Span(16, 23), ispan=Span(0, 7))
        result = LicenseMatch.merge([m1, m2, m3])
        assert [m1, m2, m3] == result

    def test_merge_merges_single_contained_match(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 5), ispan=Span(0, 5))
        contained = LicenseMatch(rule=r1, qspan=Span(1, 4), ispan=Span(1, 4))
        m5 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))
        assert contained in m5
        assert contained in m1
        result = LicenseMatch.merge([m1, contained, m5])
        assert [LicenseMatch(rule=r1, qspan=Span(0, 6), ispan=Span(0, 6))] == result

    def test_merge_merge_multiple_contained_matches(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 5), ispan=Span(0, 5))

        r2 = Rule(text_file='r2', licenses=['apache-2.0', 'gpl'])
        contained1 = LicenseMatch(rule=r2, qspan=Span(1, 2), ispan=Span(1, 2))

        r3 = Rule(text_file='r3', licenses=['apache-2.0', 'gpl'])
        contained2 = LicenseMatch(rule=r3, qspan=Span(3, 4), ispan=Span(3, 4))

        r5 = Rule(text_file='r5', licenses=['apache-2.0', 'gpl'])
        m5 = LicenseMatch(rule=r5, qspan=Span(1, 6), ispan=Span(1, 6))

        result = LicenseMatch.merge([m1, contained1, contained2, m5])
        assert [LicenseMatch(rule=r1, qspan=Span(0, 6), ispan=Span(0, 6))] == result

    def test_merge_merge_matches_with_same_spans_if_licenses_are_identical(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0'])
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))
        m5 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))

        r2 = Rule(text_file='r2', licenses=['apache-2.0'])
        m2 = LicenseMatch(rule=r2, qspan=Span(0, 2), ispan=Span(0, 2))

        matches = LicenseMatch.merge([m1, m2, m5])

        assert [LicenseMatch(rule=r1, qspan=Span(0, 6), ispan=Span(0, 6))] == matches

    def test_merge_merges_matches_with_same_spans_if_licenses_are_the_same_but_have_different_licenses_ordering(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))
        m5 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))

        r2 = Rule(text_file='r2', licenses=['gpl', 'apache-2.0'])
        m2 = LicenseMatch(rule=r2, qspan=Span(0, 2), ispan=Span(0, 2))

        result = LicenseMatch.merge([m1, m2, m5])
        assert [LicenseMatch(rule=r1, qspan=Span(0, 6), ispan=Span(0, 6))] == result

    def test_merge_merges_duplicate_matches(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0'])
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 8), ispan=Span(0, 8))
        m2 = LicenseMatch(rule=r1, qspan=Span(0, 8), ispan=Span(0, 8))

        matches = LicenseMatch.merge([m1, m2])
        assert [m1] == matches or [m2] == matches 


class TestLicenseMatchFilter(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_filter_matches_filters_multiple_nested_contained_matches(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        m1 =           LicenseMatch(rule=r1, qspan=Span(0, 5), ispan=Span(0, 5))
        overlap =      LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))
        contained =    LicenseMatch(rule=r1, qspan=Span(1, 4), ispan=Span(1, 4))
        in_contained = LicenseMatch(rule=r1, qspan=Span(2, 3), ispan=Span(2, 3))

        
        result, discarded = filter_matches([m1, contained, in_contained, overlap])
        assert [m1, overlap] == result
        assert [] == discarded

    def test_filter_matches_filters_non_contiguous_or_overlapping__but_contained_matches(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, qspan=Span(1, 2), ispan=Span(1, 2))
        m2 = LicenseMatch(rule=r1, qspan=Span(3, 6), ispan=Span(3, 6))
        m3 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))
        m4 = LicenseMatch(rule=r1, qspan=Span(0, 7), ispan=Span(0, 7))
        m5 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))

        result, discarded = filter_matches([m1, m2, m3, m4, m5])
        assert [m4] == result
        assert [] == discarded

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

        result, discarded = filter_matches([m1, m2, m3, m4, m5, m6])
        assert [m4] == result
        assert [] == discarded

    def test_filter_matches_does_filter_matches_with_contained_spans_if_licenses_are_different(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0'])
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 2), ispan=Span(0, 2))

        r2 = Rule(text_file='r2', licenses=['apache-2.0'])
        m2 = LicenseMatch(rule=r2, qspan=Span(1, 6), ispan=Span(1, 6))

        r3 = Rule(text_file='r3', licenses=['apache-1.1'])
        m3 = LicenseMatch(rule=r3, qspan=Span(0, 2), ispan=Span(0, 2))

        matches, discarded = filter_matches([m1, m2, m3])
        assert [m1, m2] == matches
        assert[] == discarded

    def test_filter_matches_filters_matches_with_partially_overlapping_spans_if_license_are_the_same(self):
        r1 = Rule(text_file='r1', licenses=['apache-1.1'])
        m1 = LicenseMatch(rule=r1, qspan=Span(0, 10), ispan=Span(0, 10))
        m2 = LicenseMatch(rule=r1, qspan=Span(1, 6), ispan=Span(1, 6))
        r2 = Rule(text_file='r2', licenses=['gpl', 'apache-2.0'])
        m3 = LicenseMatch(rule=r2, qspan=Span(5, 15), ispan=Span(5, 15))

        result, discarded = filter_matches([m1, m2, m3])
        assert [m1, m3] == result
        assert[] == discarded

    def test_filter_matches_filters_partially_contained_matches_with_significant_overlap(self):
        rule_dir = self.get_test_loc('match_filter/rules')
        rules = models.rules(rule_dir)
        idx = index.LicenseIndex(rules)

        query_loc = self.get_test_loc('match_filter/query')
        matches = idx.match(location=query_loc, min_score=0)
        assert 1 == len(matches)
        match = matches[0]
        assert [] == match


def print_matched_texts(match, location=None, query_string=None, idx=None):
    """
    Convenience function to print matched texts for tracing and debugging tests.
    """
    qtext, itext = query.get_texts(match, location=location, 
                                   query_string=query_string, 
                                   dictionary=idx.dictionary)
    print()
    print('Matched qtext:')
    print(qtext)
    print()
    print('Matched itext:')
    print(itext)

