#
# Copyright (c) nexB Inc. and others. All rights reserved.
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

from bitarray import bitarray
from commoncode.testcase import FileBasedTesting
from scancode.fingerprint import *


class TestFingerprint(FileBasedTesting):

    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_get_weighted_hash1(self):
        simhash = Simhash()
        test_file = self.get_test_loc('fingerprint/get_weighted_hash-test1.txt')

        with open(test_file, 'r') as f:
            hashable = f.read()

        simhash.update(hashable)
        result = simhash.get_weighted_hash()
        expected = [0, -2, 2, 0, 0, -2, 2, 2, -2, 0, -2, 0, 0, 0, -2, 0, 2, 0, -2, -2, 0, 0, 2, 0, 2, 2, 0, 2, 0, 0, 0, -2, 2, 0, 0, 0, -2, 2, 0, 0, 0, 0, 0, 2, -2, 0, 0, -2, 2, 0, -2, 2, 2, -2, 0, -2, 2, 0, -2, 2, 0, 2, 2, 0, 0, 0, 2, 0, 0, -2, 0, 0, 0, 2, -2, 0, 0, 0, -2, 0, 0, 2, 0, 2, 0, 0, 0, 0, -2, -2, 2, 2, 0, 0, -2, -2, -2, -2, -2, 0, 0, 2, 0, 2, 2, -2, 0, 2, 2, -2, 0, -2, -2, 2, 0, 2, 0, 0, 0, 0, 2, -2, 0, 2, -2, -2, 0, -2]
        assert result == expected


    def test_get_weighted_hash2(self):
        simhash = Simhash()
        test_file = self.get_test_loc('fingerprint/get_weighted_hash-test2.txt')

        with open(test_file, 'r') as f:
            hashable = f.read()

        simhash.update(hashable)
        result = simhash.get_weighted_hash()
        expected = [-1, -1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, -1, -1, -1, 1, -1, 1, 1, 1, -1, 1, -1, 1, 1, -1, 1, 1, 1, -1, -1, 1, 1, 1, -1, -1, -1, -1, -1, -1, 1, 1, 1, 1, -1, -1, -1, 1, 1, -1, 1, 1, -1, 1, 1, -1, 1, -1, 1, -1, 1, -1, -1, -1, -1, -1, 1, 1, -1, -1, -1, 1, 1, 1, -1, -1, -1, -1, 1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, 1, 1, -1, -1, -1, 1, -1, -1, 1, 1, -1, 1, -1, -1, 1, -1, 1, 1, 1, -1, 1, 1, 1, -1, -1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1, -1, -1, 1]
        assert result == expected


    def test_process_weighted_hash1(self):
        simhash = Simhash()
        result = simhash.process_weighted_hash([1, 2, 3, 4])
        expected = bitarray('1111')
        assert result == expected


    def test_process_weighted_hash2(self):
        simhash = Simhash()
        result = simhash.process_weighted_hash([0, 0, 0, 0])
        expected = bitarray('0000')
        assert result == expected


    def test_process_weighted_hash3(self):
        simhash = Simhash()
        result = simhash.process_weighted_hash([1, -2, -3, 4, 5, -6, 7, 0, 0])
        expected = bitarray('100110100')
        assert result == expected


    def test_process_shingles1(self):
        simhash = Simhash()
        weighted_hash = [1] * HASH_LENGTH
        expected = [0, 0, 2, 2, 0, 0, 0, 2, 2, 2, 2, 2, 0, 2, 0, 0, 0, 2, 2, 2, 0, 0, 2, 2, 0, 2, 2, 2, 2, 0, 2, 2, 2, 2, 2, 0, 2, 2, 0, 0, 0, 0, 2, 2, 0, 0, 2, 0, 2, 0, 0, 0, 2, 2, 2, 0, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0, 2, 0, 0, 2, 2, 2, 2, 2, 0, 2, 2, 0, 2, 2, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0, 0, 2, 0, 2, 2, 2, 2, 0, 2, 0, 0, 0, 0, 2, 0, 0, 0, 2, 2, 2, 0, 2, 0, 0, 0, 0, 2, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0, 0]
        result = simhash.process_shingles('Thisisfortesting', weighted_hash)
        assert result == expected


    def test_process_shingles2(self):
        simhash = Simhash()
        weighted_hash = [0, 0, 2, 2, 0, 0, 0, 2, 2, 2, 2, 2, 0, 2, 0, 0, 0, 2, 2, 2, 0, 0, 2, 2, 0, 2, 2, 2, 2, 0, 2, 2, 2, 2, 2, 0, 2, 2, 0, 0, 0, 0, 2, 2, 0, 0, 2, 0, 2, 0, 0, 0, 2, 2, 2, 0, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0, 2, 0, 0, 2, 2, 2, 2, 2, 0, 2, 2, 0, 2, 2, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0, 0, 2, 0, 2, 2, 2, 2, 0, 2, 0, 0, 0, 0, 2, 0, 0, 0, 2, 2, 2, 0, 2, 0, 0, 0, 0, 2, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0, 0]
        expected = [1, 1, 3, 1, -1, 1, 1, 3, 1, 1, 1, 3, 1, 1, 1, -1, -1, 1, 3, 3, 1, 1, 3, 1, 1, 3, 3, 3, 1, 1, 3, 1, 1, 3, 3, -1, 1, 1, -1, -1, 1, -1, 3, 1, 1, -1, 3, 1, 3, 1, 1, -1, 3, 3, 1, 1, 1, 1, 3, 1, -1, 1, -1, 1, 1, -1, 3, 1, 1, 3, 1, 1, 1, 3, 1, 1, 3, -1, 3, 1, 1, 1, 3, -1, 1, -1, 1, 1, 1, -1, 1, 3, 1, 1, 1, 1, 3, 1, 1, -1, 1, 1, -1, 1, -1, 1, -1, 1, 3, 3, -1, 1, -1, 1, -1, -1, 3, -1, 1, 3, 1, 1, -1, 1, 1, 3, 1, -1]
        result = simhash.process_shingles('tryforanotherone', weighted_hash)
        assert result == expected


    def test_process_shingles3(self):
        simhash = Simhash()
        weighted_hash = [0, 0, 2, 2, 0, 0, 0, 2, 2, 2, 2, 2, 0, 2, 0, 0, 0, 2, 2, 2, 0, 0, 2, 2, 0, 2, 2, 2, 2, 0, 2, 2, 2, 2, 2, 0, 2, 2, 0, 0, 0, 0, 2, 2, 0, 0, 2, 0, 2, 0, 0, 0, 2, 2, 2, 0, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0, 2, 0, 0, 2, 2, 2, 2, 2, 0, 2, 2, 0, 2, 2, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0, 0, 2, 0, 2, 2, 2, 2, 0, 2, 0, 0, 0, 0, 2, 0, 0, 0, 2, 2, 2, 0, 2, 0, 0, 0, 0, 2, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0, 0]
        expected = [1, -1, 1, 1, -1, -1, 1, 3, 1, 1, 1, 1, -1, 1, -1, -1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3, 1, 1, 1, 3, 1, 3, 3, 1, 1, 3, -1, 1, 1, 1, 1, 3, 1, 1, 3, 1, 1, -1, 1, -1, 3, 1, 1, -1, 1, 1, 1, -1, -1, 1, 1, -1, 1, 1, 1, 1, -1, 1, 3, 1, 1, 1, 1, 1, 3, 1, 1, 3, -1, 1, 3, -1, -1, -1, -1, 1, 1, 1, 1, 1, -1, 3, 3, 3, 3, 1, 1, -1, 1, 1, -1, 3, 1, -1, -1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, -1, 3, 1, -1, 1, -1, 1, 1, -1, 1]
        result = simhash.process_shingles('for(inti=0;i<n;i++)', weighted_hash)
        assert result == expected


    def test_hex_digest1(self):
        simhash = Simhash()
        test_file = self.get_test_loc('fingerprint/fingerprint-test1.java')

        with open(test_file, 'r') as f:
            hashable = f.read()

        simhash.update(hashable)
        result = simhash.hex_digest()
        assert result == '4e42d8c0ed6693654866425451210417'


    def test_hex_digest2(self):
        simhash = Simhash()
        test_file = self.get_test_loc('fingerprint/fingerprint-test2.c')

        with open(test_file, 'r') as f:
            hashable = f.read()

        simhash.update(hashable)
        result = simhash.hex_digest()
        assert result == 'baa2d1d169be06a306c1873afe6db4da'


    def test_hex_digest3(self):
        simhash = Simhash()
        test_file = self.get_test_loc('fingerprint/fingerprint-test3.py')

        with open(test_file, 'r') as f:
            hashable = f.read()

        simhash.update(hashable)
        result = simhash.hex_digest()
        assert result == '7f43e1b18f9c0e705fcf28007bc41754'


    def test_hex_digest3(self):
        simhash = Simhash()
        assert simhash.hex_digest() == None


    def test_update(self):
        simhash = Simhash()
        assert simhash.tokens == []

        simhash.update('This is for testing purpose \n It should work fine')
        expected = ['This', 'is', 'for', 'testing', 'purpose', 'It', 'should', 'work', 'fine']
        assert simhash.tokens == expected


    def test_generate_fingerprint(self):
        simhash = Simhash()
        simhash.update('This should work')
        expected = bitarray('11100010001110100111100010101000101110111111110000010011000110000110001110000000100000111011101110111100110001011011110001011100')
        assert simhash.generate_fingerprint() == expected

        simhash.update('this will get added too!')
        expected = bitarray('00000010000000000011110010100000101000001111100000000001010110000110101110111000100000110101000000010100100000000010110011010010')
        assert simhash.generate_fingerprint() == expected

    def test_similarity_matching1(self):
        simhash1 = Simhash()
        simhash2 = Simhash()

        test_file1 = self.get_test_loc('fingerprint/similarity_matching1.py')
        test_file2 = self.get_test_loc('fingerprint/similarity_matching2.py')

        with open(test_file1, 'r') as f:
            hashable1 = f.read()

        with open(test_file2, 'r') as f:
            hashable2 = f.read()

        simhash1.update(hashable1)
        simhash2.update(hashable2)
        distance = simhash1.hamming_distance(simhash1.generate_fingerprint(), simhash2.generate_fingerprint())

        assert distance == 14


    def test_similarity_matching2(self):
        simhash1 = Simhash()
        simhash2 = Simhash()

        test_file1 = self.get_test_loc('fingerprint/similarity_matching3.py')
        test_file2 = self.get_test_loc('fingerprint/similarity_matching4.py')

        with open(test_file1, 'r') as f:
            hashable1 = f.read()

        with open(test_file2, 'r') as f:
            hashable2 = f.read()

        simhash1.update(hashable1)
        simhash2.update(hashable2)
        distance = simhash1.hamming_distance(simhash1.generate_fingerprint(), simhash2.generate_fingerprint())

        assert distance == 66


    def test_similarity_matching3(self):
        simhash1 = Simhash()
        simhash2 = Simhash()

        test_file1 = self.get_test_loc('fingerprint/similarity_matching5.py')
        test_file2 = self.get_test_loc('fingerprint/similarity_matching6.py')

        with open(test_file1, 'r') as f:
            hashable1 = f.read()

        with open(test_file2, 'r') as f:
            hashable2 = f.read()

        simhash1.update(hashable1)
        simhash2.update(hashable2)
        distance = simhash1.hamming_distance(simhash1.generate_fingerprint(), simhash2.generate_fingerprint())

        assert distance == 13
