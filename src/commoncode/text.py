# -*- coding: utf-8 -*-
# NOTE: the iso-8859-15 charset is not a mistake.
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

import re
import logging
import unicodedata

import chardet
from text_unidecode import unidecode

# Python 2 and 3 support
try:
    # Python 2
    unicode
except NameError:
    # Python 3
    unicode = str  # NOQA

"""
A text processing module providing functions to process and prepare text
before indexing or fingerprinting such as:
 - case folding
 - conversion of iso latin and unicode to ascii
 - punctuation stripping
 - line separator stripping and conversion
 """

LOG = logging.getLogger(__name__)


def lines(s):
    """
    Split a string in lines using the following conventions:
    - a line ending \r\n or \n is a separator and yields a new list element
    - empty lines or lines with only white spaces are not returned.
    - returned lines are stripped.

    Because of these constraints "".split() cannot be used directly. We first
    replace things where we want to split with line endings, then we
    splitlines.

    For example:
    >>> t='''This problem is.
    ... It is therefore
    ...
    ...
    ...  However,we
    ... without introducing ..
    ...  However, I have
    ...
    ...
    ... '''
    >>> len([p[1] for p in lines(t)])
    5
    >>> expected = ['This problem is.', 'It is therefore', 'However,we', 'without introducing ..', 'However, I have']
    >>> assert expected == [p for p in lines(t)]
    """
    return [l.strip() for l in s.splitlines() if l.strip()]


def foldcase(text):
    """
    Fold the cases of a text to lower case
    """
    return text.lower()


def nopunc():
    return re.compile(r'[\W_]', re.MULTILINE)


def nopunctuation(text):
    u"""
    Replaces any non alphanum symbol (i.e. punctuation) in text with space.
    Preserve the characters offsets by replacing punctuation with spaces.
    Warning: this also drops line endings.

    For example:
    >>> t = '''This problem is about sequence-bunching, %^$^%**^&*Â©Â©^(*&(*()()_+)_!@@#:><>>?/./,.,';][{}{]just'''
    >>> expected = ['This', 'problem', 'is', 'about', 'sequence', 'bunching', 'just']
    >>> assert expected == nopunctuation(t).split()
    >>> t = r'''This problem is about: sequence-bunching
    ...
    ... just
    ... '''
    >>> expected = 'This problem is about  sequence bunching  just '
    >>> assert expected == nopunctuation(t)
    """
    return re.sub(nopunc(), ' ', text)


CR = '\r'
LF = '\n'
CRLF = CR + LF
CRLF_NO_CR = ' ' + LF


def unixlinesep(text, preserve=False):
    """
    Normalize a string to Unix line separators. Preserve character offset by
    replacing with spaces if preserve is True.

    For example:
    >>> t= CR + LF + LF + CR + CR + LF
    >>> unixlinesep(t) == LF + LF + LF + LF
    True
    >>> unixlinesep(t, True) == ' ' + LF + LF + LF + ' ' + LF
    True
    """
    return text.replace(CRLF, CRLF_NO_CR if preserve else LF).replace(CR, LF)


def nolinesep(text):
    """
    Removes line separators, replacing them with spaces.
    For example:
    >>> t = CR + LF + CR + CR + CR + LF
    >>> nolinesep(t) == '      '
    True
    """
    return text.replace(CR, ' ').replace(LF, ' ')


def toascii(s, translit=False):
    u""" Convert a Unicode string to ASCII characters, including replacing accented
    characters with their non-accented equivalent.

    If `translit` is False use the Unicode NFKD equivalence.

    If `translit` is True, use a transliteration with the unidecode library.

    Non ISO-Latin and non ASCII characters are stripped from the
    output.
    When no transliteration is possible, the resulting character is replaced
    by an underscore "_".

    For Unicode NFKD equivalence, see http://en.wikipedia.org/wiki/Unicode_equivalence

    The convertion may NOT preserve the original string length and with NFKD some
    characters may be deleted.

    Inspired from: http://code.activestate.com/recipes/251871/#c10 by Aaron Bentley.

    For example:
    >>> acc =   u"ÀÁÂÃÄÅÇÈÉÊËÌÍÎÏÑÒÓÔÕÖØÙÚÛÜÝàáâãäåçèéêëìíîïñòóôõöøùúûüýÿẞß®©œŒØøÆæ₵₡￠¢Žž"
    >>> noacc = r'AAAAAACEEEEIIIINOOOOOUUUUYaaaaaaceeeeiiiinooooouuuuyyZz'
    >>> toascii(acc, translit=False) == noacc
    True
    >>> noacc = r'AAAAAACEEEEIIIINOOOOOOUUUUYaaaaaaceeeeiiiinoooooouuuuyySsss(r)(c)oeOEOoAEae_CL/CC/Zz'
    >>> toascii(acc, translit=True) == noacc
    True
    """
    try:
        if translit:
            converted = unidecode(s).encode('ascii', 'ignore')
            converted = converted.replace('[?]', '_')
        else:
            converted = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore')
    except:
        converted = str(s.decode('ascii', 'ignore'))
    return converted


def python_safe_name(s):
    """
    Return a name derived from string `s` safe to use as a Python identifier.

    For example:
    >>> s = "not `\\a /`good` -safe name ??"
    >>> assert python_safe_name(s) == 'not_good_safe_name'
    """
    s = toascii(s)
    s = foldcase(s)
    s = nopunctuation(s)
    s = s.strip()
    s = '_'.join(s.split())
    return s


def as_unicode(s):
    """
    Return unicode for a string be it bytes or unicode.
    Try to decode as Unicode. Try first some default encodings,
    then attempt Unicode trans-literation and finally
    fall-back to ASCII strings extraction.

    TODO: Add file/magic detection, unicodedmanit/BS3/4
    """
    if not s:
        return s

    if isinstance(s, unicode):
        return s

    try:
        return s.decode('utf-8')
    except UnicodeDecodeError:
        try:
            encoding = chardet.detect(s)
            if encoding:
                encoding = encoding.get('encoding')
                return s.decode(encoding)
        except UnicodeDecodeError:
                pass
        s = toascii(s, translit=True)
        if not isinstance(s, unicode):
            s = unicode(s)
        return s

