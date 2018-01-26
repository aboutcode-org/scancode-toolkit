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

from __future__ import absolute_import
from __future__ import print_function

from unittest.case import TestCase

from commoncode.functional import flatten


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
