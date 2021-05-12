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
    assert len([p[1] for p in text.lines(t)]) == 5
    expected = ['This problem is.', 'It is therefore', 'However,we', 'without introducing ..', 'However, I have']
    assert [p for p in text.lines(t)] == expected


def test_foldcase():
    test = ' Fold THE cases of a text to lower casM'
    assert text.foldcase(test) == test.lower()


def test_nopunctuation():
    test = '''This problem is about sequence-bunching, %^$^%**^&*Â©Â©^(*&(*()()_+)_!@@#:><>>?/./,.,';][{}{]just'''
    expected = ['This', 'problem', 'is', 'about', 'sequence', 'bunching', 'Â', 'Â', 'just']
    assert text.nopunctuation(test).split() == expected

    test = 'This problem is about: sequence-bunching\n\n just \n'
    expected = 'This problem is about  sequence bunching   just  '
    assert text.nopunctuation(test) == expected


def test_unixlinesep():
    t = CR + LF + LF + CR + CR + LF
    assert text.unixlinesep(t) == LF + LF + LF + LF
    assert text.unixlinesep(t, True) == ' ' + LF + LF + LF + ' ' + LF


def test_nolinesep():
    t = CR + LF + CR + CR + CR + LF
    assert text.nolinesep(t) == '      '


def test_toascii():
    acc = u"ÀÁÂÃÄÅÇÈÉÊËÌÍÎÏÑÒÓÔÕÖØÙÚÛÜÝàáâãäåçèéêëìíîïñòóôõöøùúûüýÿẞß®©œŒØøÆæ₵₡￠¢Žž"
    expected = r'AAAAAACEEEEIIIINOOOOOUUUUYaaaaaaceeeeiiiinooooouuuuyyZz'
    assert text.toascii(acc, translit=False) == expected
    expected = r'AAAAAACEEEEIIIINOOOOOOUUUUYaaaaaaceeeeiiiinoooooouuuuyySsss(r)(c)oeOEOoAEae_CL/CC/Zz'
    assert text.toascii(acc, translit=True) == expected


def test_toascii_works_with_empty_unicode_or_bytes():
    assert text.toascii(b'', translit=False) == u''
    assert text.toascii(u'', translit=True) == u''
    assert text.toascii(b'', translit=False) == u''
    assert text.toascii(u'', translit=True) == u''


def test_python_safe_name():
    s = "not `\\a /`good` -safe name ??"
    assert text.python_safe_name(s) == 'not___a___good___safe_name'
    s1 = "string1++or+"
    s2 = "string1 +or "
    assert text.python_safe_name(s2) == text.python_safe_name(s1)


def test_as_unicode():
    assert text.as_unicode('') == ''
    assert isinstance(text.as_unicode(b'some bytes'), str)
    assert text.as_unicode(None) == None
    try:
        text.as_unicode(['foo'])
        raise Exception('Exception should have been raised')
    except AssertionError:
        pass
