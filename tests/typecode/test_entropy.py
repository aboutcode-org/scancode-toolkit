#
# Copyright (c) 201 nexB Inc. and others. All rights reserved.
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
from __future__ import division

from functools import partial
import unittest

from commoncode.system import py2
from typecode.entropy import gzip_entropy
from typecode.entropy import shannon_entropy

import pytest
pytestmark = pytest.mark.scanpy3  # NOQA


def check_entropy(data, expected, func=shannon_entropy):
    entro = round(func(data), 2)
    expected = round(expected, 2)
    assert expected == entro


class TestEntropy(unittest.TestCase):

    def test_shannon_entropy(self):
        # some tests values collected from various places for sanity
        # https://www.reddit.com/r/dailyprogrammer/comments/4fc896/20160418_challenge_263_easy_calculating_shannon/
        # https://github.com/natano/python-entropy/blob/76f14557cd2f80adbc7e8dc821ba33864dd0afdc/test_entropy.py
        # https://github.com/UniquePassive/randcam/blob/9ebf7678f58427910b1a2b99704169dd467d47e1/tests/tests.py#L20
        # http://rosettacode.org/wiki/Entropy#Python
        check = partial(check_entropy, func=shannon_entropy)

        if py2:
            check(b''.join(map(chr, range(256))), 8.0)
        else:
            check(bytes(list(range(256))), 8.0)

        check('', 0.0)
        check('0', 0.0)
        check(b'\x00' * 1024, 0.0)
        check(b'\xff' * 1024, 0.0)
        check(b'\x00\xff' * 512, 1.0)
        check(b'\xff\x00' * 512, 1.0)
        check(b'\x00\xcc\xff' * 512, 1.58)
        check('122333444455555666666777777788888888', 2.79)
        check('563881467447538846567288767728553786', 2.79)
        check(sorted('563881467447538846567288767728553786'), 2.79)
        check('https://www.reddit.com/r/dailyprogrammer', 4.06)
        check('int main(int argc, char *argv[])', 3.87)
        check(('0' * 1000) + ('1' * 1000), 1.0)
        check('1223334444', 1.846439)
        check('1227774444', 1.846439)
        check('Rosetta Code is the best site in the world!', 3.646513)
        check('Rosetta Code', 3.08496)
        check('1223334444555555555', 1.96981)
        check('122333', 1.45914)
        check('aaBBcccDDDD', 1.936260)
        check('1234567890abcdefghijklmnopqrstuvwxyz', 5.1699250)
        check('01010101010101010102020202020202', 1.49)
        data = ('Lorem ipsum dolor sit amet, consectetur adipisicing ''elit, '
                'sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.')
        check(data, 4.02)
        check('hnpshnhahphshnp', 2.11)

    def test_gz_entropy(self):
        check = partial(check_entropy, func=gzip_entropy)
        if py2:
            check(b''.join(map(chr, range(256))), 1.04)
        else:
            check(bytes(list(range(256))), 1.04)

        check('', 0.0)
        check('0', 9.0)
        check(b'\x00' * 1024, 0.02)
        check(b'\xff' * 1024, 0.02)
        check(b'\x00\xff' * 512, 0.02)
        check(b'\xff\x00' * 512, 0.02)
        check(b'\x00\xcc\xff' * 512, 0.01)
        check('122333444455555666666777777788888888', 0.72)
        check('563881467447538846567288767728553786', 1.03)
        check(''.join(sorted('563881467447538846567288767728553786')), 0.72)
        check('https://www.reddit.com/r/dailyprogrammer', 1.2)
        check('int main(int argc, char *argv[])', 1.16)
        check(('0' * 1000) + ('1' * 1000), 0.01)
        check('1223334444', 1.6)
        check('1227774444', 1.6)
        check('Rosetta Code is the best site in the world!', 1.07)
        check('Rosetta Code', 1.67)
        check('1223334444555555555', 1.0)
        check('122333', 2.33)
        check('aaBBcccDDDD', 1.55)
        check('1234567890abcdefghijklmnopqrstuvwxyz', 1.22)
        check('01010101010101010102020202020202', 0.47)
        data = ('Lorem ipsum dolor sit amet, consectetur adipisicing ''elit, '
                'sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.')
        check(data, 0.8)
        check('hnpshnhahphshnp', 1.4)
