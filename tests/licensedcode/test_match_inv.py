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
from licensedcode.whoosh_spans.spans import Span

from licensedcode import models
from licensedcode import match_inv


TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


class IndexTesting(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def get_test_rules(self, base, subset=None):
        base = self.get_test_loc(base)
        test_files = sorted(os.listdir(base))
        if subset:
            test_files = [t for t in test_files if t in subset]
        return [models.Rule(text_file=os.path.join(base, license_key), licenses=[license_key]) for license_key in test_files]


def hstrings(hts, query):
    "Replace token ids in hit tuples with strings to make sense of test results"
    qtoks = query.split()
    return [(qtoks[q] , q, i)  for q, i in hts]


def gstrings(ghts, query):
    "Replace token ids in hit groups with strings to make sense of test results"
    return [hstrings(hts, query) for hts in ghts]


class TestHits(IndexTesting):
    test_data_dir = TEST_DATA_DIR

    def test_group_hits_with_simple_numerical_hits(self):
        hits_by_rid = {
            0: [
                (0, 5),
                (1, 3),
                (2, 0),
                (3, 1),
                (4, 5),
                (5, 6),
                (6, 7),
                (7, 8),
                (8, 9)
            ],
            1: [
                (0, 10),
                (1, 1),
                (3, 3),
                (4, 10),
                (5, 11),
                (6, 6),
                (6, 12),
                (8, 14),
                (9, 16),
                (10, 17)
            ]
        }

        expected = {
         0: [[(2, 0), (3, 1), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9)],
             [(1, 3)],
             [(0, 5)]],
         1: [[(1, 1), (3, 3), (6, 6)],
             [(0, 10)],
             [(4, 10), (5, 11), (6, 12), (8, 14), (9, 16), (10, 17)]]}


        assert expected[0] == match_inv.group_hits(hits_by_rid[0], max_dist=5)
        assert expected[1] == match_inv.group_hits(hits_by_rid[1], max_dist=5)

    def test_build_match(self):
        rule = models.Rule(_text='abc')
        line_by_pos = {}
        hits = [(5, 0,)]
        match = match_inv.build_match(hits, rule, line_by_pos)
        assert Span([5]) == match.qspan
        assert Span([0]) == match.ispan

    def test_build_matches1(self):
        hit_groups = [
            [(5, 0,)],
            [(3, 1,)],
            [(0, 2), (1, 3), (5, 4), (6, 5), (7, 6), (8, 7), (9, 8)],
        ]

        expected = [
            (Span([5]), Span([0])),
            (Span([3]), Span([1])),
            (Span([0, 1, 5, 6, 7, 8, 9]), Span([2, 3, 4, 5, 6, 7, 8])),
        ]

        rule = models.Rule(_text='ab')
        rule.rid = 0
        matches = match_inv.build_matches(hit_groups, rule, {})
        result = [(match.qspan, match.ispan) for match in matches]
        assert expected == result

    def test_build_matches2(self):
        hit_groups = [
            [(10, 0,)],
            [(1, 1), (3, 3), (10, 4), (11, 5)],
            [(6, 6,)],
            [(12, 6), (14, 8), (16, 9), (17, 10)],
        ]

        expected = [
            (Span([10]), Span([0])),
            (Span([1, 3, 10, 11]), Span([1, 3, 4, 5])),
            (Span([6]), Span([6])),
            (Span([12, 14, 16, 17]), Span([6, 8, 9, 10]))
        ]

        rule = models.Rule(_text='ab')
        rule.rid = 0
        matches = match_inv.build_matches(hit_groups, rule, {})
        result = [(match.qspan, match.ispan) for match in matches]
        assert expected == result
