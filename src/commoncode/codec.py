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

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

from base64 import standard_b64decode as stddecode
from base64 import urlsafe_b64encode as b64encode

from commoncode.system import py2


"""
Numbers to bytes or strings and URLs coder/decoders.
"""


if py2:
    c2i = ord
    i2c = chr
else:
    # noop
    c2i = lambda c: c
    i2c = lambda i: bytes([i])


if py2:
    def num_to_bin(num):
        """
        Convert a `num` integer or long to a binary string byte-ordered such
        that the least significant bytes are at the beginning of the string
        (aka. big endian).
        """
        # Zero is not encoded but returned as an empty value
        if num == 0:
            return b'\x00'

        binstr = []
        while num > 0:
            # add the least significant byte value
            binstr.append(i2c(num & 0xFF))
            # shift the next byte to least significant and repeat
            num = num >> 8

        # reverse the list now such that the most significant
        # byte is at the start of this string to speed decoding
        return b''.join(reversed(binstr))


    def bin_to_num(binstr):
        """
        Convert a big endian byte-ordered binary string to an integer or long.
        """
        num = 0
        for charac in binstr:
            # the most significant byte is a the start of the string so we multiply
            # that value by 256 (e.g. <<8) and add the value of the current byte,
            # then move to next byte in the string and repeat
            num = (num << 8) + c2i(charac)
        return num
else:
    def num_to_bin(num):
        """
        Convert a `num` integer or long to a binary string byte-ordered such that
        the least significant bytes are at the beginning of the string (aka. big
        endian).
        """
        # Zero is not encoded but returned as an empty value
        if num == 0:
            return b'\x00'

        return num.to_bytes((num.bit_length() + 7) // 8, 'big')

    def bin_to_num(binstr):
        """
        Convert a big endian byte-ordered binary string to an integer or long.
        """
        return int.from_bytes(binstr, byteorder='big', signed=False)


def urlsafe_b64encode(s):
    """
    Encode a binary string to a url safe base64 encoding.
    """
    return b64encode(s)


def urlsafe_b64decode(b64):
    """
    Decode a url safe base64-encoded string.
    Note that we use stddecode to work around a bug in the standard library.
    """
    b = b64.replace(b'-', b'+').replace(b'_', b'/')
    return stddecode(b)


def urlsafe_b64encode_int(num):
    """
    Encode a number (int or long) in url safe base64.
    """
    return b64encode(num_to_bin(num))
