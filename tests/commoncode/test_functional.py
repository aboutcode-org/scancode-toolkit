#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/commoncode for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from collections import Counter
from unittest.case import TestCase

from commoncode.functional import flatten
from commoncode.functional import memoize
from commoncode.functional import partial


class TestFunctional(TestCase):

    def test_flatten(self):
        expected = [7, 6, 5, 4, 'a', 3, 3, 2, 1]
        test = flatten([7, (6, [5, [4, ["a"], 3]], 3), 2, 1])
        assert test == expected

    def test_flatten_generator(self):

        def gen():
            for _ in range(2):
                yield range(5)

        expected = [0, 1, 2, 3, 4, 0, 1, 2, 3, 4]
        test = flatten(gen())
        assert test == expected

    def test_flatten_empties(self):
        expected = ['a']
        test = flatten([[], (), ['a']])
        assert test == expected

    def test_partial(self):

        def test_func(a, b):
            pass

        wrapped = partial(test_func, a=2)
        assert wrapped.__name__ == 'test_func'

    def test_memoized(self):
        call_count = Counter()

        @memoize
        def test_func(a):
            call_count[a] += 1

        test_func(1)
        assert 1 == call_count[1]
        test_func(1)
        assert 1 == call_count[1]
        test_func(2)
        assert 1 == call_count[2]
        test_func(2)
        assert 1 == call_count[2]
        test_func(2)
        assert 1 == call_count[1]
