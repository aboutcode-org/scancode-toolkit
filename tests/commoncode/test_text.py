# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/commoncode for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from commoncode import text
from commoncode.text import CR
from commoncode.text import LF


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
    assert isinstance(text.as_unicode(b'some bytes'), str)
    assert None == text.as_unicode(None)
    try:
        text.as_unicode(['foo'])
        raise Exception('Exception should have been raised')
    except AssertionError:
        pass
