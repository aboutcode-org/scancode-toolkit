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

from collections import Counter
from unittest.case import TestCase

from bitarray import bitarray

from licensedcode import prefilter


class FilterTesting(TestCase):

    def test_bit_candidates(self):
        qbvector = bitarray('011')

        high_bitvectors_by_rid = [
            bitarray('11')
        ]
        low_bitvectors_by_rid = [
            bitarray('0')
        ]
        len_junk = 1
        candidates = prefilter.bit_candidates(qbvector, high_bitvectors_by_rid, low_bitvectors_by_rid, len_junk, min_score=100)
        assert [(0, 0)] == candidates

    def test_bit_candidates2(self):
        qbvector = bitarray('100')
        high_bitvectors_by_rid = [
            bitarray('11')
        ]
        low_bitvectors_by_rid = [
            bitarray('1')
        ]
        len_junk = 1
        candidates = prefilter.bit_candidates(qbvector, high_bitvectors_by_rid, low_bitvectors_by_rid, len_junk, min_score=100)
        assert [] == candidates

        qbvector = bitarray('111')
        candidates = prefilter.bit_candidates(qbvector, high_bitvectors_by_rid, low_bitvectors_by_rid, len_junk, min_score=100)
        assert [(0, 0)] == candidates

        qbvector = bitarray('011')
        candidates = prefilter.bit_candidates(qbvector, high_bitvectors_by_rid, low_bitvectors_by_rid, len_junk, min_score=100)
        assert [] == candidates

    def test_freq_candidates(self):
        qvector = [[0], [1, 2, 3], [0]]
        frequencies_by_rid = [
            Counter({0: 1, 1: 3, 2: 0}),
            Counter({0: 2, 1: 2, 2: 1})
        ]

        lengths_by_rid = [4,5]

        candidates = prefilter.freq_candidates(qvector, frequencies_by_rid, lengths_by_rid, min_score=100)
        assert [(100, 0)] == candidates
