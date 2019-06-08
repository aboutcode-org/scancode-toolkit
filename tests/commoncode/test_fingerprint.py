#
# Copyright (c) 2018 nexB Inc. and others. All rights reserved.
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
from commoncode.fingerprint import get_tokenlist
from commoncode.fingerprint import process_weightedlist
from commoncode.fingerprint import process_shingles
from commoncode.fingerprint import hash_length
from commoncode.fingerprint import get_weightedlist
from commoncode.fingerprint import generate_fingerprint

class TestFingerprint(FileBasedTesting):

    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_get_tokenlist(self):
        test_file = self.get_test_loc('fingerprint/token-test.txt')
        result = get_tokenlist(test_file)
        expected = ['This', 'is', 'for', 'testing', 'purpose', 'It', 'should', 'work', 'fine', '.']
        assert result == expected

    def test_get_weightedlist1(self):
        test_file = self.get_test_loc('fingerprint/get_weightedlist-test1.txt')
        tokenlist = get_tokenlist(test_file)
        result = get_weightedlist(tokenlist)
        expected = [0, -2, 2, 0, 0, -2, 2, 2, -2, 0, -2, 0, 0, 0, -2, 0, 2, 0, -2, -2, 0, 0, 2, 0, 2, 2, 0, 2, 0, 0, 0, -2, 2, 0, 0, 0, -2, 2, 0, 0, 0, 0, 0, 2, -2, 0, 0, -2, 2, 0, -2, 2, 2, -2, 0, -2, 2, 0, -2, 2, 0, 2, 2, 0, 0, 0, 2, 0, 0, -2, 0, 0, 0, 2, -2, 0, 0, 0, -2, 0, 0, 2, 0, 2, 0, 0, 0, 0, -2, -2, 2, 2, 0, 0, -2, -2, -2, -2, -2, 0, 0, 2, 0, 2, 2, -2, 0, 2, 2, -2, 0, -2, -2, 2, 0, 2, 0, 0, 0, 0, 2, -2, 0, 2, -2, -2, 0, -2]
        assert result == expected

    def test_get_weightedlist2(self):
        test_file = self.get_test_loc('fingerprint/get_weightedlist-test2.txt')
        tokenlist = get_tokenlist(test_file)
        result = get_weightedlist(tokenlist)
        expected = [-1, -1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, -1, -1, -1, 1, -1, 1, 1, 1, -1, 1, -1, 1, 1, -1, 1, 1, 1, -1, -1, 1, 1, 1, -1, -1, -1, -1, -1, -1, 1, 1, 1, 1, -1, -1, -1, 1, 1, -1, 1, 1, -1, 1, 1, -1, 1, -1, 1, -1, 1, -1, -1, -1, -1, -1, 1, 1, -1, -1, -1, 1, 1, 1, -1, -1, -1, -1, 1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, 1, 1, -1, -1, -1, 1, -1, -1, 1, 1, -1, 1, -1, -1, 1, -1, 1, 1, 1, -1, 1, 1, 1, -1, -1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, -1, -1, 1]
        assert result == expected

    def test_get_weightedlist3(self):
        test_file = self.get_test_loc('fingerprint/get_weightedlist-test3.txt')
        tokenlist = get_tokenlist(test_file)
        result = get_weightedlist(tokenlist)
        expected = [1, 1, -1, 1, -1, 1, -1, -1, -1, -1, -1, 1, 1, 1, -1, 1, 1, -1, -1, -1, 1, 1, -1, -1, 1, 1, -1, 1, 1, -1, -1, 1, 1, -1, -1, -1, 1, 1, 1, 1, -1, -1, -1, -1, -1, -1, -1, -1, 1, -1, 1, 1, -1, -1, 1, -1, -1, -1, -1, -1, -1, 1, -1, -1, 1, 1, 1, -1, 1, -1, -1, 1, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, -1, 1, 1, 1, -1, 1, 1, -1, -1, 1, 1, 1, 1, 1, -1, -1, -1, -1, 1, -1, -1, -1, -1, 1, -1, -1, 1, 1, 1, 1, 1, 1, -1]
        assert result == expected

    def test_process_weightedlist1(self):
        result = process_weightedlist([1, 2, 3, 4])
        expected = [1, 1, 1, 1]
        assert result == expected

    def test_process_weightedlist2(self):
        result = process_weightedlist([0, 0, 0, 0])
        expected = [0, 0, 0, 0]
        assert result == expected

    def test_process_weightedlist3(self):
        result = process_weightedlist([1, -2, -3, 4, 5, -6, 7, 0, 0])
        expected = [1, 0, 0, 1, 1, 0, 1, 0,0]
        assert result == expected

    def test_process_shingles1(self):
        weightedList = [1] * hash_length
        expected = [0, 0, 2, 2, 0, 0, 0, 2, 2, 2, 2, 2, 0, 2, 0, 0, 0, 2, 2, 2, 0, 0, 2, 2, 0, 2, 2, 2, 2, 0, 2, 2, 2, 2, 2, 0, 2, 2, 0, 0, 0, 0, 2, 2, 0, 0, 2, 0, 2, 0, 0, 0, 2, 2, 2, 0, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0, 2, 0, 0, 2, 2, 2, 2, 2, 0, 2, 2, 0, 2, 2, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0, 0, 2, 0, 2, 2, 2, 2, 0, 2, 0, 0, 0, 0, 2, 0, 0, 0, 2, 2, 2, 0, 2, 0, 0, 0, 0, 2, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0, 0]
        result = process_shingles('Thisisfortesting', weightedList)
        assert result == expected

    def test_process_shingles2(self):
        weightedList = [0, 0, 2, 2, 0, 0, 0, 2, 2, 2, 2, 2, 0, 2, 0, 0, 0, 2, 2, 2, 0, 0, 2, 2, 0, 2, 2, 2, 2, 0, 2, 2, 2, 2, 2, 0, 2, 2, 0, 0, 0, 0, 2, 2, 0, 0, 2, 0, 2, 0, 0, 0, 2, 2, 2, 0, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0, 2, 0, 0, 2, 2, 2, 2, 2, 0, 2, 2, 0, 2, 2, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0, 0, 2, 0, 2, 2, 2, 2, 0, 2, 0, 0, 0, 0, 2, 0, 0, 0, 2, 2, 2, 0, 2, 0, 0, 0, 0, 2, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0, 0]
        expected = [1, 1, 3, 1, -1, 1, 1, 3, 1, 1, 1, 3, 1, 1, 1, -1, -1, 1, 3, 3, 1, 1, 3, 1, 1, 3, 3, 3, 1, 1, 3, 1, 1, 3, 3, -1, 1, 1, -1, -1, 1, -1, 3, 1, 1, -1, 3, 1, 3, 1, 1, -1, 3, 3, 1, 1, 1, 1, 3, 1, -1, 1, -1, 1, 1, -1, 3, 1, 1, 3, 1, 1, 1, 3, 1, 1, 3, -1, 3, 1, 1, 1, 3, -1, 1, -1, 1, 1, 1, -1, 1, 3, 1, 1, 1, 1, 3, 1, 1, -1, 1, 1, -1, 1, -1, 1, -1, 1, 3, 3, -1, 1, -1, 1, -1, -1, 3, -1, 1, 3, 1, 1, -1, 1, 1, 3, 1, -1]
        result = process_shingles('tryforanotherone', weightedList)
        assert result == expected

    def test_process_shingles3(self):
        weightedList = [0, 0, 2, 2, 0, 0, 0, 2, 2, 2, 2, 2, 0, 2, 0, 0, 0, 2, 2, 2, 0, 0, 2, 2, 0, 2, 2, 2, 2, 0, 2, 2, 2, 2, 2, 0, 2, 2, 0, 0, 0, 0, 2, 2, 0, 0, 2, 0, 2, 0, 0, 0, 2, 2, 2, 0, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0, 2, 0, 0, 2, 2, 2, 2, 2, 0, 2, 2, 0, 2, 2, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0, 0, 2, 0, 2, 2, 2, 2, 0, 2, 0, 0, 0, 0, 2, 0, 0, 0, 2, 2, 2, 0, 2, 0, 0, 0, 0, 2, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0, 0]
        expected = [1, -1, 1, 1, -1, -1, 1, 3, 1, 1, 1, 1, -1, 1, -1, -1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3, 1, 1, 1, 3, 1, 3, 3, 1, 1, 3, -1, 1, 1, 1, 1, 3, 1, 1, 3, 1, 1, -1, 1, -1, 3, 1, 1, -1, 1, 1, 1, -1, -1, 1, 1, -1, 1, 1, 1, 1, -1, 1, 3, 1, 1, 1, 1, 1, 3, 1, 1, 3, -1, 1, 3, -1, -1, -1, -1, 1, 1, 1, 1, 1, -1, 3, 3, 3, 3, 1, 1, -1, 1, 1, -1, 3, 1, -1, -1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, -1, 3, 1, -1, 1, -1, 1, 1, -1, 1]
        result = process_shingles('for(inti=0;i<n;i++)', weightedList)
        assert result == expected

    def test_generate_fingerprint1(self):
        test_file = self.get_test_loc('fingerprint/fingerprint-test1.java')
        result = generate_fingerprint(test_file)
        assert result == '01001110010000101101100011000000111011010110011010010011011001010100100001100110010000100101010001010001001000010000010000010111'

    def test_generate_fingerprint2(self):
        test_file = self.get_test_loc('fingerprint/fingerprint-test2.c')
        result = generate_fingerprint(test_file)
        assert result == '10111010101000101101000111010001011010011011111000000110101000110000011011000001100001110011101011111110011011011011010011011010'

    def test_generate_fingerprint3(self):
        test_file = self.get_test_loc('fingerprint/fingerprint-test3.py')
        result = generate_fingerprint(test_file)
        assert result == '01111111010000111110000110110001100011111001110000001110011100000101111111001111001010000000000001111011110001000001011101010100'