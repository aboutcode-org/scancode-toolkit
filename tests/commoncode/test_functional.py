#
# Copyright (c) nexB Inc. and others.
# SPDX-License-Identifier: Apache-2.0
#
# Visit https://aboutcode.org and https://github.com/nexB/ for support and download.
# ScanCode is a trademark of nexB Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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
        assert expected == test

    def test_flatten_generator(self):

        def gen():
            for _ in range(2):
                yield range(5)

        expected = [0, 1, 2, 3, 4, 0, 1, 2, 3, 4]
        test = flatten(gen())
        assert expected == test

    def test_flatten_empties(self):
        expected = ['a']
        test = flatten([[], (), ['a']])
        assert expected == test

    def test_partial(self):

        def test_func(a, b):
            pass

        wrapped = partial(test_func, a=2)
        assert 'test_func' == wrapped.__name__

    def test_memoized(self):
        call_count = Counter()

        @memoize
        def test_func(a):
            call_count[a] += 1

        test_func(1)
        assert call_count[1] == 1
        test_func(1)
        assert call_count[1] == 1
        test_func(2)
        assert call_count[2] == 1
        test_func(2)
        assert call_count[2] == 1
        test_func(2)
        assert call_count[1] == 1
