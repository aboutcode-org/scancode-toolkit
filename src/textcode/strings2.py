#
# Copyright (c) 2016 Fireeye, Inc. All rights reserved.
#
# Modifications Copyright (c) 2016 nexB, Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/scancode-toolkit/
# The ScanCode software is licensed under the Apache License version 2.0.
# ScanCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# This file contains code derived and modified from Fireeye's flare FLOSS:
# https://www.github.com/fireeye/flare-floss
# The original code was taken on 2016-10-28 from:
# https://raw.githubusercontent.com/fireeye/flare-floss/0db13aff88d0487f818f19a36de879dc27c94e13/floss/strings.py
# modifications:
# - do not return offsets
# - do not check for buffers filled with a single byte
# - removed main()
# - do not cache compiled patterns. re does cache patterns alright.


from __future__ import absolute_import, print_function

import re


ASCII_BYTE = (
    " !\"#\$%&\'\(\)\*\+,-\./0123456789:;<=>\?@ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "\[\]\^_`abcdefghijklmnopqrstuvwxyz\{\|\}\\\~\t"
)


def extract_ascii_strings(buf, n=3):
    """
    Yield Unicode strings (ASCII) from a buf string of binary data.

    :param buf: A bytestring.
    :type buf: str
    :param n: The minimum length of strings to extract.
    :type n: int
    :rtype: Sequence[string]
    """
    if not buf:
        return

    reg = '([%s]{%d,})' % (ASCII_BYTE, n)
    r = re.compile(reg)
    for match in r.finditer(buf):
        yield match.group().decode('ascii')


def extract_unicode_strings(buf, n=3):
    """
    Yield Unicode strings (UTF-16-LE encoded ASCII) from a buf string of binary data.

    :param buf: A bytestring.
    :type buf: str
    :param n: The minimum length of strings to extract.
    :type n: int
    :rtype: Sequence[string]
    """
    if not buf:
        return

    reg = b'((?:[%s]\x00){%d,})' % (ASCII_BYTE, n)
    r = re.compile(reg)
    for match in r.finditer(buf):
        try:
            yield match.group().decode('utf-16')
        except UnicodeDecodeError:
            pass


def extract_strings(buf, n=3):
    """
    Yield unicode strings (ASCII and UTF-16-LE encoded ASCII) from a buf string of binary data.

    :param buf: A bytestring.
    :type buf: str
    :param n: The minimum length of strings to extract.
    :type n: int
    :rtype: Sequence[string]
    """
    for s in extract_ascii_strings(buf):
        yield s

    for s in extract_unicode_strings(buf):
        yield s
