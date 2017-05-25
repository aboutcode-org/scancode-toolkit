#
# Copyright (c) 2017 nexB Inc. and others. All rights reserved.
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
from __future__ import unicode_literals

"""
Numbers to bytes or strings and URLs coder/decoders.
"""

padding = b'/'

b85_symbols = b'0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{|}~'
len_b85_symbols = len(b85_symbols)


def to_base_n(num, base):
    """
    Convert `num` number to a string representing this number in base `base`
    where base <= 85.

    Use recursion for progressive encoding.
    """
    # ensure that base is within bounds
    assert base >= 2 and base <= len_b85_symbols
    if num == 0:
        return b'0'
    # recurse with a floor division to encode from left to right
    based = to_base_n(num // base, base)
    # remove leading zeroes resulting from floor-based encoding
    stripped = based.lstrip(b'0')
    # pick the symbol in the symbol table using a modulo
    encoded = b85_symbols[num % base]
    return stripped + encoded


MAXLEN = len(to_base_n(pow(2, 32) - 1, 85))


def to_base85(num):
    """
    Convert `num` number to a string representing this number in base 85,
    padded as needed.

    The character set to encode 85 base85 digits is defined to be:
         '0'..'9', 'A'..'Z', 'a'..'z', '!', '#', '$', '%', '&', '(',
         ')', '*', '+', '-', ';', '<', '=', '>', '?', '@', '^', '_',
         '`', '{', '|', '}', and '~'.

    From http://www.faqs.org/rfcs/rfc1924.html

    See also http://en.wikipedia.org/wiki/Base_85 for the rationale for Base
    85. Git also uses https://github.com/git/git/blob/master/base85.c
    """
    encoded = to_base_n(num, 85)
    # add padding
    elen = len(encoded)
    if elen < MAXLEN:
        encoded = encoded + (padding * (MAXLEN - (elen)))
    return encoded


def to_base10(s, b=36):
    """
    Convert a string s representing a number in base b back to an integer where base <= 85.
    """

    assert b <= len(b85_symbols) and b >= 2, 'Base must be in range(2, %d)' % (len(b85_symbols))
    # strip padding
    s = s.replace(padding, b'')

    base10_num = 0
    i = len(s) - 1
    for digit in s:
        base10_num += b85_symbols.index(digit) * pow(b, i)
        i -= 1
    return base10_num


def num_to_bin(num):
    """
    Convert a `num` integer or long to a binary string byte-ordered such that
    the least significant bytes are at the beginning of the string (aka. little
    endian).

    NOTE: The code below does not use struct for conversions to handle
    arbitrary long binary strings (such as a SHA512 digest) and convert that
    safely to a long: using structs does not work easily for this.
    """
    binstr = []

    # Zero is not encoded but returned as an empty value
    if num == 0:
        return b'\x00'

    while num > 0:
        # add the least significant byte value
        binstr.append(chr(num & 0xFF))
        # shift the next byte to least significant and repeat
        num = num >> 8

    # reverse the list now such that the most significant
    # byte is at the start of this string to speed decoding
    return b''.join(reversed(binstr))


def bin_to_num(binstr):
    """
    Convert a little endian byte-ordered binary string to an integer or long.
    """
    # this will cast to long as needed
    num = 0
    for charac in binstr:
        # the most significant byte is a the start of the string so we multiply
        # that value by 256 (e.g. <<8) and add the value of the current byte,
        # then move to next byte in the string and repeat
        num = (num << 8) + ord(charac)
    return num


from base64 import standard_b64decode as stddecode
from base64 import urlsafe_b64encode as b64encode


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


def _encode(num):
    """
    Encode a number (int or long) in url safe base64.
    """
    return b64encode(num_to_bin(num))
