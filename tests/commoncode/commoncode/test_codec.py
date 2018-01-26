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

from unittest import TestCase

from commoncode.codec import bin_to_num, num_to_bin
from commoncode.codec import _encode, to_base_n
from commoncode.codec import to_base10, to_base85


class TestCodec(TestCase):

    def test_bin_to_num_basic(self):
        expected = 123
        result = bin_to_num('{')
        assert expected == result

    def test_bin_to_num_zero(self):
        expected = 0
        result = bin_to_num('\x00')
        assert expected == result

    def test_bin_to_num_large_number(self):
        expected = 432346237462348763
        result = bin_to_num('\x06\x00\x00\x9c\xbf\xeb\x83\xdb')
        assert expected == result

    def test_bin_to_num_and_num_to_bin_is_idempotent(self):
        expected = 432346237462348763
        result = bin_to_num(num_to_bin(432346237462348763))
        assert expected == result

    def test_num_to_bin_basic(self):
        expected = '{'
        result = num_to_bin(123)
        assert expected == result

    def test_num_to_bin_zero(self):
        expected = '\x00'
        result = num_to_bin(0)
        assert expected == result

    def test_num_to_bin_large_number(self):
        expected = '\x06\x00\x00\x9c\xbf\xeb\x83\xdb'
        result = num_to_bin(432346237462348763)
        assert expected == result

    def test_num_to_bin_bin_to_num_is_idempotent(self):
        expected = '\x06\x00\x00\x9c\xbf\xeb\x83\xdb'
        result = num_to_bin(bin_to_num('\x06\x00\x00\x9c\xbf\xeb\x83\xdb'))
        assert expected == result

    def test_encode_zero(self):
        assert  'AA==' == _encode(0)

    def test_encode_basic(self):
        assert 'HKq1w7M=' == _encode(123123123123)

    def test_encode_limit_8bits_255(self):
        assert '_w==' == _encode(255)

    def test_encode_limit_8bits_256(self):
        assert 'AQA=' == _encode(256)

    def test_encode_adds_no_padding_for_number_that_are_multiple_of_6_bits(self):
        assert '____________' == _encode(0xFFFFFFFFFFFFFFFFFF)
        assert 8 == len(_encode(0xFFFFFFFFFFFF))

    def test_encode_very_large_number(self):
        b64 = ('QAAAAAAgAAAAAQAACAAAAAAAAAAAAAAkAAIAAAAAAAAAAAAAAACAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAiAAAAAAAIAAAAAAAAAAAAAAEAACAAAAAAAA=')
        expected = b64
        num = 2678771517966886466622496485850735537232223496190189203248435106535830319026141316924949516664780383591425235756710588949364368366679435700855700642969357960349427980681242720502045830438444033569999428606714388704082526548154984676817460705606960919023941301616034362869262429593297635158449513824256L
        result = _encode(num)
        assert expected == result

    def test_base64_is_idempotent(self):
        for i in [0, 63, 782963129, 99999999, 2147483647]:
            assert i == to_base10(to_base_n(i, 64), 64)

    def test_base36_is_idempotent(self):
        for i in [0, 63, 782963129, 99999999, 2147483647]:
            assert i == to_base10(to_base_n(i, 36), 36)

    def test_base85_is_idempotent(self):
        # we use this for 12-bit hashes
        for i in [0, 63, 100, 1000, 4095, 4294967295]:
            assert i == to_base10(to_base85(i), 85)

    def test_to_base_n_with_unknown_base_raise_exception(self):
        try:
            to_base_n(892103712, 86)
        except AssertionError:
            pass

        try:
            to_base_n(892103712, 16522)
        except AssertionError:
            pass

        try:
            to_base_n(892103712, 1)
        except AssertionError:
            pass
