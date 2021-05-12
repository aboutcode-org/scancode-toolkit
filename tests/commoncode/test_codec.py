#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/commoncode for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from unittest import TestCase

from commoncode.codec import bin_to_num
from commoncode.codec import num_to_bin
from commoncode.codec import urlsafe_b64encode_int


class TestCodec(TestCase):

    def test_bin_to_num_basic(self):
        expected = 123
        result = bin_to_num(b'{')
        assert result == expected

    def test_bin_to_num_zero(self):
        expected = 0
        result = bin_to_num(b'\x00')
        assert result == expected

    def test_bin_to_num_large_number(self):
        expected = 432346237462348763
        result = bin_to_num(b'\x06\x00\x00\x9c\xbf\xeb\x83\xdb')
        assert result == expected

    def test_bin_to_num_and_num_to_bin_is_idempotent(self):
        expected = 432346237462348763
        result = bin_to_num(num_to_bin(432346237462348763))
        assert result == expected

    def test_num_to_bin_basic(self):
        expected = b'{'
        result = num_to_bin(123)
        assert result == expected

    def test_num_to_bin_zero(self):
        expected = b'\x00'
        result = num_to_bin(0)
        assert result == expected

    def test_num_to_bin_large_number(self):
        expected = b'\x06\x00\x00\x9c\xbf\xeb\x83\xdb'
        result = num_to_bin(432346237462348763)
        assert result == expected

    def test_num_to_bin_bin_to_num_is_idempotent(self):
        expected = b'\x06\x00\x00\x9c\xbf\xeb\x83\xdb'
        result = num_to_bin(bin_to_num(b'\x06\x00\x00\x9c\xbf\xeb\x83\xdb'))
        assert result == expected

    def test_urlsafe_b64encode_int_zero(self):
        assert urlsafe_b64encode_int(0) ==  b'AA=='

    def test_urlsafe_b64encode_int_basic(self):
        assert urlsafe_b64encode_int(123123123123) == b'HKq1w7M='

    def test_urlsafe_b64encode_int_limit_8bits_255(self):
        assert urlsafe_b64encode_int(255) == b'_w=='

    def test_urlsafe_b64encode_int_limit_8bits_256(self):
        assert urlsafe_b64encode_int(256) == b'AQA='

    def test_urlsafe_b64encode_int_adds_no_padding_for_number_that_are_multiple_of_6_bits(self):
        assert urlsafe_b64encode_int(0xFFFFFFFFFFFFFFFFFF) == b'____________'
        assert len(urlsafe_b64encode_int(0xFFFFFFFFFFFF)) == 8

    def test_urlsafe_b64encode_int_very_large_number(self):
        b64 = (b'QAAAAAAgAAAAAQAACAAAAAAAAAAAAAAkAAIAAAAAAAAAAAAAAACAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAiAAAAAAAIAAAAAAAAAAAAAAEAACAAAAAAAA=')
        expected = b64
        num = 2678771517966886466622496485850735537232223496190189203248435106535830319026141316924949516664780383591425235756710588949364368366679435700855700642969357960349427980681242720502045830438444033569999428606714388704082526548154984676817460705606960919023941301616034362869262429593297635158449513824256
        result = urlsafe_b64encode_int(num)
        assert result == expected
