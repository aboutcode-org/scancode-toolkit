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

from unittest import TestCase

from commoncode.codec import bin_to_num
from commoncode.codec import num_to_bin
from commoncode.codec import urlsafe_b64encode_int


class TestCodec(TestCase):

    def test_bin_to_num_basic(self):
        expected = 123
        result = bin_to_num(b'{')
        assert expected == result

    def test_bin_to_num_zero(self):
        expected = 0
        result = bin_to_num(b'\x00')
        assert expected == result

    def test_bin_to_num_large_number(self):
        expected = 432346237462348763
        result = bin_to_num(b'\x06\x00\x00\x9c\xbf\xeb\x83\xdb')
        assert expected == result

    def test_bin_to_num_and_num_to_bin_is_idempotent(self):
        expected = 432346237462348763
        result = bin_to_num(num_to_bin(432346237462348763))
        assert expected == result

    def test_num_to_bin_basic(self):
        expected = b'{'
        result = num_to_bin(123)
        assert expected == result

    def test_num_to_bin_zero(self):
        expected = b'\x00'
        result = num_to_bin(0)
        assert expected == result

    def test_num_to_bin_large_number(self):
        expected = b'\x06\x00\x00\x9c\xbf\xeb\x83\xdb'
        result = num_to_bin(432346237462348763)
        assert expected == result

    def test_num_to_bin_bin_to_num_is_idempotent(self):
        expected = b'\x06\x00\x00\x9c\xbf\xeb\x83\xdb'
        result = num_to_bin(bin_to_num(b'\x06\x00\x00\x9c\xbf\xeb\x83\xdb'))
        assert expected == result

    def test_urlsafe_b64encode_int_zero(self):
        assert  b'AA==' == urlsafe_b64encode_int(0)

    def test_urlsafe_b64encode_int_basic(self):
        assert b'HKq1w7M=' == urlsafe_b64encode_int(123123123123)

    def test_urlsafe_b64encode_int_limit_8bits_255(self):
        assert b'_w==' == urlsafe_b64encode_int(255)

    def test_urlsafe_b64encode_int_limit_8bits_256(self):
        assert b'AQA=' == urlsafe_b64encode_int(256)

    def test_urlsafe_b64encode_int_adds_no_padding_for_number_that_are_multiple_of_6_bits(self):
        assert b'____________' == urlsafe_b64encode_int(0xFFFFFFFFFFFFFFFFFF)
        assert 8 == len(urlsafe_b64encode_int(0xFFFFFFFFFFFF))

    def test_urlsafe_b64encode_int_very_large_number(self):
        b64 = (b'QAAAAAAgAAAAAQAACAAAAAAAAAAAAAAkAAIAAAAAAAAAAAAAAACAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAiAAAAAAAIAAAAAAAAAAAAAAEAACAAAAAAAA=')
        expected = b64
        num = 2678771517966886466622496485850735537232223496190189203248435106535830319026141316924949516664780383591425235756710588949364368366679435700855700642969357960349427980681242720502045830438444033569999428606714388704082526548154984676817460705606960919023941301616034362869262429593297635158449513824256
        result = urlsafe_b64encode_int(num)
        assert expected == result
