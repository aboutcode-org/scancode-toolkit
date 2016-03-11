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

from licensedcode.match import LicenseMatch
from licensedcode.models import Rule
from licensedcode.whoosh_spans.spans import Span
from licensedcode.match import filter_matches
from licensedcode import models
from licensedcode.match import build_match


TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


class TestLicenseMatch(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_LicenseMatch_equality(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, qspans=(Span(0, 2),), ispans=(Span(0, 2),))
        m2 = LicenseMatch(rule=r1, qspans=(Span(0, 2),), ispans=(Span(0, 2),))
        assert m1 == m2

        r2 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        m3 = LicenseMatch(rule=r2, qspans=(Span(0, 2),), ispans=(Span(0, 2),))
        assert m1 != m3

    def test_build_match(self):
        rule = models.Rule()
        match = build_match([(5, 0)], rule, {})
        assert Span(5) == match.qregion
        assert Span(0) == match.iregion

    def test_filter_matches_filters_single_contained_match(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, qspans=(Span(0, 5),), ispans=(Span(0, 5),))
        contained = LicenseMatch(rule=r1, qspans=(Span(1, 4),), ispans=(Span(1, 4),))
        m5 = LicenseMatch(rule=r1, qspans=(Span(1, 6),), ispans=(Span(1, 6),))

        assert contained in m5
        assert contained in m1
        result = filter_matches([m1, contained, m5], merge_spans=True)
        assert [LicenseMatch(rule=r1, qspans=(Span(0, 6),), ispans=(Span(0, 6),))] == result

    def test_filter_matches_filters_multiple_contained_matches(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, qspans=(Span(0, 5),), ispans=(Span(0, 5),))

        r2 = Rule(text_file='r2', licenses=['apache-2.0', 'gpl'])
        contained1 = LicenseMatch(rule=r2, qspans=(Span(1, 2),), ispans=(Span(1, 2),))

        r3 = Rule(text_file='r3', licenses=['apache-2.0', 'gpl'])
        contained2 = LicenseMatch(rule=r3, qspans=(Span(3, 4),), ispans=(Span(3, 4),))

        r5 = Rule(text_file='r5', licenses=['apache-2.0', 'gpl'])
        m5 = LicenseMatch(rule=r5, qspans=(Span(1, 6),), ispans=(Span(1, 6),))

        result = filter_matches([m1, contained1, contained2, m5], merge_spans=True)
        assert [LicenseMatch(rule=r1, qspans=(Span(0, 6),), ispans=(Span(0, 6),))] == result

    def test_filter_matches_filters_multiple_nested_contained_matches(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, qspans=(Span(0, 5),), ispans=(Span(0, 5),))
        contained = LicenseMatch(rule=r1, qspans=(Span(1, 4),), ispans=(Span(1, 4),))
        in_contained = LicenseMatch(rule=r1, qspans=(Span(2, 3),), ispans=(Span(2, 3),))
        m5 = LicenseMatch(rule=r1, qspans=(Span(1, 6),), ispans=(Span(1, 6),))

        result = filter_matches([m1, contained, in_contained, m5], merge_spans=False)
        match = result[0]
        assert (Span(0, 5), Span(1, 6),) == match.qspans
        assert (Span(0, 5), Span(1, 6),) == match.ispans
        expected = LicenseMatch(rule=r1, qspans=(Span(0, 6),), ispans=(Span(0, 6),))
        match.simplify()
        assert (Span(0, 6),) == match.qspans
        assert (Span(0, 6),) == match.ispans
        assert [expected] == result

    def test_filter_matches_merges_contained_and_overlaping_matches(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        r2 = Rule(text_file='r2', licenses=['apache-2.0', 'gpl2'])

        overlap = LicenseMatch(rule=r1, qspans=(Span(0, 5),), ispans=(Span(0, 5),))
        same_span1 = LicenseMatch(rule=r1, qspans=(Span(1, 6),), ispans=(Span(1, 6),))
        same_span2 = LicenseMatch(rule=r2, qspans=(Span(1, 6),), ispans=(Span(1, 6),))

        result = filter_matches([overlap, same_span1, same_span2], merge_spans=True)
        expected = [
            LicenseMatch(rule=r1, qspans=(Span(0, 6),), ispans=(Span(0, 6),)),
        ]
        assert expected == result

    def test_filter_matches_does_filter_contiguous_non_overlapping_matches_in_sequence(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, qspans=(Span(0, 2),), ispans=(Span(0, 2),))
        m2 = LicenseMatch(rule=r1, qspans=(Span(3, 6),), ispans=(Span(3, 6),))
        m5 = LicenseMatch(rule=r1, qspans=(Span(1, 6),), ispans=(Span(1, 6),))

        result = filter_matches([m1, m2, m5])
        match = result[0]
        match.simplify()
        assert LicenseMatch(rule=r1, qspans=(Span(0, 6),), ispans=(Span(0, 6),)) == match

    def test_filter_matches_doesfilter_non_contiguous_matches_in_sequence(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, qspans=(Span(0, 2),), ispans=(Span(0, 2),))
        m2 = LicenseMatch(rule=r1, qspans=(Span(4, 6),), ispans=(Span(4, 6),))
        m5 = LicenseMatch(rule=r1, qspans=(Span(1, 6),), ispans=(Span(1, 6),))

        result = filter_matches([m1, m2, m5], merge_spans=True)
        assert [LicenseMatch(rule=r1, qspans=(Span(0, 6),), ispans=(Span(0, 6),))] == result

    def test_filter_matches_filters_non_contiguous_or_overlapping__but_contained_matches(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, qspans=(Span(1, 2),), ispans=(Span(1, 2),))
        m2 = LicenseMatch(rule=r1, qspans=(Span(3, 6),), ispans=(Span(3, 6),))
        m3 = LicenseMatch(rule=r1, qspans=(Span(1, 6),), ispans=(Span(1, 6),))
        m4 = LicenseMatch(rule=r1, qspans=(Span(0, 7),), ispans=(Span(0, 7),))
        m5 = LicenseMatch(rule=r1, qspans=(Span(1, 6),), ispans=(Span(1, 6),))

        result = filter_matches([m1, m2, m3, m4, m5], merge_spans=True)
        assert [m4] == result

    def test_filter_matches_filters_non_contiguous_or_overlapping_contained_matches_with_touching_boundaries(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, qspans=(Span(0, 2),), ispans=(Span(0, 2),))

        r2 = Rule(text_file='r2', licenses=['apache-2.0', 'gpl'])
        m2 = LicenseMatch(rule=r2, qspans=(Span(3, 7),), ispans=(Span(3, 7),))

        r3 = Rule(text_file='r3', licenses=['apache-2.0', 'gpl'])
        m3 = LicenseMatch(rule=r3, qspans=(Span(0, 6),), ispans=(Span(0, 6),))

        r6 = Rule(text_file='r6', licenses=['apache-2.0', 'gpl'])
        m6 = LicenseMatch(rule=r6, qspans=(Span(1, 7),), ispans=(Span(1, 7),))

        r5 = Rule(text_file='r5', licenses=['apache-2.0', 'gpl'])
        m5 = LicenseMatch(rule=r5, qspans=(Span(1, 6),), ispans=(Span(1, 6),))

        r4 = Rule(text_file='r4', licenses=['apache-2.0', 'gpl'])
        m4 = LicenseMatch(rule=r4, qspans=(Span(0, 7),), ispans=(Span(0, 7),))

        result = filter_matches([m1, m2, m3, m4, m5, m6], merge_spans=True)
        assert [m4] == result

    def test_filter_matches_does_filter_matches_with_contained_spans_if_licenses_are_different(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0'])
        m1 = LicenseMatch(rule=r1, qspans=(Span(0, 2),), ispans=(Span(0, 2),))

        r2 = Rule(text_file='r2', licenses=['apache-2.0'])
        m2 = LicenseMatch(rule=r2, qspans=(Span(1, 6),), ispans=(Span(1, 6),))

        r3 = Rule(text_file='r3', licenses=['apache-1.1'])
        m3 = LicenseMatch(rule=r3, qspans=(Span(0, 2),), ispans=(Span(0, 2),))

        result = filter_matches([m1, m2, m3], merge_spans=True)
        assert [LicenseMatch(rule=r1, qspans=(Span(0, 6),), ispans=(Span(0, 6),))] == result

    def test_filter_matches_filters_matches_with_same_spans_if_licenses_are_identical(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0'])
        m1 = LicenseMatch(rule=r1, qspans=(Span(0, 2),), ispans=(Span(0, 2),))
        m5 = LicenseMatch(rule=r1, qspans=(Span(1, 6),), ispans=(Span(1, 6),))

        r2 = Rule(text_file='r2', licenses=['apache-2.0'])
        m2 = LicenseMatch(rule=r2, qspans=(Span(0, 2),), ispans=(Span(0, 2),))

        result = filter_matches([m1, m2, m5], merge_spans=True)
        assert [LicenseMatch(rule=r1, qspans=(Span(0, 6),), ispans=(Span(0, 6),))] == result

    def test_filter_matches_filters_matches_with_same_spans_if_licenses_are_the_same_but_have_different_licenses_ordering(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, qspans=(Span(0, 2),), ispans=(Span(0, 2),))
        m5 = LicenseMatch(rule=r1, qspans=(Span(1, 6),), ispans=(Span(1, 6),))

        r2 = Rule(text_file='r2', licenses=['gpl', 'apache-2.0'])
        m2 = LicenseMatch(rule=r2, qspans=(Span(0, 2),), ispans=(Span(0, 2),))

        result = filter_matches([m1, m2, m5], merge_spans=True)
        assert [LicenseMatch(rule=r1, qspans=(Span(0, 6),), ispans=(Span(0, 6),))] == result

    def test_filter_matches_filters_matches_with_partially_overlapping_spans_if_license_are_the_same(self):
        r1 = Rule(text_file='r1', licenses=['apache-1.1'])
        m1 = LicenseMatch(rule=r1, qspans=(Span(0, 10),), ispans=(Span(0, 10),))
        m2 = LicenseMatch(rule=r1, qspans=(Span(1, 6),), ispans=(Span(1, 6),))
        r2 = Rule(text_file='r2', licenses=['gpl', 'apache-2.0'])
        m3 = LicenseMatch(rule=r2, qspans=(Span(5, 15),), ispans=(Span(5, 15),))

        result = filter_matches([m1, m2, m3], merge_spans=True)
        assert [m1, m3] == result

    def test_LicenseMatch_same(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, qspans=(Span(0, 2),), ispans=(Span(0, 2),))
        r2 = Rule(text_file='r2', licenses=['gpl', 'apache-2.0'])
        m2 = LicenseMatch(rule=r2, qspans=(Span(0, 2),), ispans=(Span(0, 2),))

        assert m1.same(m2)
        assert m2.same(m1)

    def test_LicenseMatch_not_same(self):
        r1 = Rule(text_file='r1', licenses=['apache-1.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, qspans=(Span(0, 2),), ispans=(Span(0, 2),))
        r2 = Rule(text_file='r2', licenses=['gpl', 'apache-2.0'])
        m2 = LicenseMatch(rule=r2, qspans=(Span(0, 2),), ispans=(Span(0, 2),))

        assert not m1.same(m2)
        assert not m2.same(m1)

        r3 = Rule(text_file='r3', licenses=['apache-1.0', 'gpl'])
        m3 = LicenseMatch(rule=r3, qspans=(Span(0, 2),), ispans=(Span(0, 2),))

        assert m1.same(m3)
        assert m3.same(m1)

        r4 = Rule(text_file='r4', licenses=['apache-1.0', 'gpl'])
        m4 = LicenseMatch(rule=r4, qspans=(Span(1, 2),), ispans=(Span(1, 2),))

        assert not m1.same(m4)
        assert not m4.same(m1)

    def test_LicenseMatch_comparisons(self):
        r1 = Rule(text_file='r1', licenses=['apache-2.0', 'gpl'])
        contained1 = LicenseMatch(rule=r1, qspans=(Span(0, 5),), ispans=(Span(0, 5),))
        contained2 = LicenseMatch(rule=r1, qspans=(Span(1, 4),), ispans=(Span(1, 4),))
        same_span1 = LicenseMatch(rule=r1, qspans=(Span(1, 6),), ispans=(Span(1, 6),))
        same_span2 = LicenseMatch(rule=r1, qspans=(Span(1, 6),), ispans=(Span(1, 6),))
        before_after = LicenseMatch(rule=r1, qspans=(Span(8, 9),), ispans=(Span(8, 9),))
        touching = LicenseMatch(rule=r1, qspans=(Span(7, 7),), ispans=(Span(7, 7),))
        overlap = LicenseMatch(rule=r1, qspans=(Span(4, 7),), ispans=(Span(4, 7),))

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
        assert same_span1.is_before(before_after)

        assert before_after.touch(touching)
        assert before_after.is_after(touching)
        assert touching.is_before(before_after)

        assert touching.touch(before_after)
        assert not before_after.touch(same_span1)
        assert before_after.is_after(contained1)

    def test_LicenseMatch_merge_should_not_merge_repeated_matches(self):
        rule = Rule(text_file='gpl-2.0_49.RULE', licenses=[u'gpl-2.0'])
        rule.rid = 2615
        m1 = LicenseMatch(rule=rule, _type='chunk1', qspans=[Span(0, 7)], ispans=[Span(0, 7)])
        m2 = LicenseMatch(rule=rule, _type='chunk2', qspans=[Span(8, 15)], ispans=[Span(0, 7)])
        m3 = LicenseMatch(rule=rule, _type='chunk3', qspans=[Span(16, 23)], ispans=[Span(0, 7)])
        result = LicenseMatch.merge([m1, m2, m3])
        assert [m1, m2, m3] == result
