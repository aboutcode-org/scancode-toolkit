# -*- coding: iso-8859-15 -*-
# NOTE: the iso-8859-15 charset is not a mistake.
#
# Copyright (c) 2015 nexB Inc. and others. All rights reserved.
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

from __future__ import absolute_import, print_function

import re
import logging
import unicodedata

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
    >>> [p for p in lines(t)]
    ['This problem is.', 'It is therefore', 'However,we', 'without introducing ..', 'However, I have']
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
    >>> nopunctuation(t).split()
    ['This', 'problem', 'is', 'about', 'sequence', 'bunching', 'just']
    >>> t = r'''This problem is about: sequence-bunching
    ... 
    ... just
    ... '''
    >>> nopunctuation(t)
    'This problem is about  sequence bunching  just '
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


# additional non standard normalizations but quite common sense
unicode_translation_table = {u'Ø': u'O', u'ø': u'o', u'ž': u'z', u'Ž': u'Z'}

# Other candidates
{
    u'¢': u'c',
    # not space preserving
    u'æ': u'a',
    u'Æ': u'A',

    u'œ': u'o',
    u'Œ': u'O',

    u'©': u'(c)',
    u'®': u'(r)',

    # see http://en.wikipedia.org/wiki/Ã
    u'ß': u'ss',
    u'\u1e9e': u'SS'
}


def toascii(s):
    u"""
    Convert a Unicode string to ASCII characters, including replacing accented
    characters with their non-accented NFKD equivalent. Non ISO-Latin and non
    ASCII characters are stripped from the output. For Unicode NFKD
    equivalence, see http://en.wikipedia.org/wiki/Unicode_equivalence

    Does not preserve the original length and character offsets.

    Inspired from:
    http://code.activestate.com/recipes/251871/#c10 by Aaron Bentley.

    For example:
    >>> acc =   u"ÀÁÂÃÄÅÇÈÉÊËÌÍÎÏÑÒÓÔÕÖØÙÚÛÜÝàáâãäåçèéêëìíîïñòóôõöøùúûüýÿ"
    >>> noacc = r"AAAAAACEEEEIIIINOOOOOUUUUYaaaaaaceeeeiiiinooooouuuuyy"
    >>> toascii(acc) == noacc
    True
    """
    try:
        return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore')
    except:
        return str(s.decode('ascii', 'ignore'))


def python_safe_name(s):
    """
    Return a name derived from string `s` safe to use as a Python identifier.

    For example:

    >>> s = "not `\\a /`good` -safe name ??"
    >>> python_safe_name(s)
    'not_good_safe_name'

    """
    s = toascii(s)
    s = foldcase(s)
    s = nopunctuation(s)
    s = s.strip()
    s = '_'.join(s.split())
    return s
