# -*- coding: utf-8 -*-
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
from __future__ import unicode_literals

from commoncode import compat
from commoncode import text
from commoncode.text import CR, LF
from commoncode.system import py2

import pytest
pytestmark = pytest.mark.scanpy3  # NOQA


def test_lines():
    t = '''This problem is.
It is therefore


 However,we
without introducing ..
 However, I have


'''
    assert 5 == len([p[1] for p in text.lines(t)])
    expected = ['This problem is.', 'It is therefore', 'However,we', 'without introducing ..', 'However, I have']
    assert expected == [p for p in text.lines(t)]


def test_foldcase():
    test = ' Fold THE cases of a text to lower casM'
    assert test.lower() == text.foldcase(test)


def test_nopunctuation():
    test = '''This problem is about sequence-bunching, %^$^%**^&*Â©Â©^(*&(*()()_+)_!@@#:><>>?/./,.,';][{}{]just'''
    if py2:
        expected = ['This', 'problem', 'is', 'about', 'sequence', 'bunching', '\xc2', '\xc2', 'just']
    else:
        expected = ['This', 'problem', 'is', 'about', 'sequence', 'bunching', 'Â', 'Â', 'just']
    assert expected == text.nopunctuation(test).split()

    test = 'This problem is about: sequence-bunching\n\n just \n'
    expected = 'This problem is about  sequence bunching   just  '
    assert expected == text.nopunctuation(test)


def test_unixlinesep():
    t = CR + LF + LF + CR + CR + LF
    assert LF + LF + LF + LF == text.unixlinesep(t)
    assert ' ' + LF + LF + LF + ' ' + LF == text.unixlinesep(t, True)


def test_nolinesep():
    t = CR + LF + CR + CR + CR + LF
    assert '      ' == text.nolinesep(t)


def test_toascii():
    acc = u"ÀÁÂÃÄÅÇÈÉÊËÌÍÎÏÑÒÓÔÕÖØÙÚÛÜÝàáâãäåçèéêëìíîïñòóôõöøùúûüýÿẞß®©œŒØøÆæ₵₡￠¢Žž"
    expected = r'AAAAAACEEEEIIIINOOOOOUUUUYaaaaaaceeeeiiiinooooouuuuyyZz'
    assert expected == text.toascii(acc, translit=False)
    expected = r'AAAAAACEEEEIIIINOOOOOOUUUUYaaaaaaceeeeiiiinoooooouuuuyySsss(r)(c)oeOEOoAEae_CL/CC/Zz'
    assert expected == text.toascii(acc, translit=True)


def test_toascii_works_with_empty_unicode_or_bytes():
    assert u'' == text.toascii(b'', translit=False)
    assert u'' == text.toascii(u'', translit=True)
    assert u'' == text.toascii(b'', translit=False)
    assert u'' == text.toascii(u'', translit=True)


def test_python_safe_name():
    s = "not `\\a /`good` -safe name ??"
    assert 'not___a___good___safe_name' == text.python_safe_name(s)
    s1 = "string1++or+"
    s2 = "string1 +or "
    assert text.python_safe_name(s1) == text.python_safe_name(s2)


def test_as_unicode():
    assert '' == text.as_unicode('')
    try:
        text.as_unicode(None)
        raise Exception('Exception should have been raised')
    except AssertionError:
        pass
    assert isinstance(text.as_unicode(b'some bytes'), compat.unicode)
