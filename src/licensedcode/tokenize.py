# -*- coding: utf-8 -*-
#
# Copyright (c) 2017-2018 nexB Inc. and others. All rights reserved.
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

from itertools import islice

# Python 2 and 3 support
try:
    # Python 2
    import itertools.izip as zip  # NOQA
except ImportError:
    # Python 3
    pass

from binascii import crc32
import re

from commoncode.system import py2
from commoncode.system import py3
from licensedcode.stopwords import STOPWORDS
from textcode.analysis import numbered_text_lines


"""
Utilities to break texts in lines and tokens (aka. words) with specialized version
for queries and rules texts.
"""


def query_lines(location=None, query_string=None, strip=True):
    """
    Return an iterable of tuples (line number, text line) given a file at
    `location` or a `query string`. Include empty lines.
    """
    # TODO: OPTIMIZE: tokenizing line by line may be rather slow
    # we could instead get lines and tokens at once in a batch?
    numbered_lines = []
    if location:
        numbered_lines = numbered_text_lines(location, demarkup=False)
    elif query_string:
        if strip:
            keepends = False
        else:
            keepends = True
        numbered_lines = enumerate(query_string.splitlines(keepends), 1)

    for line_number, line in numbered_lines:
        if strip:
            yield line_number, line.strip()
        else:
            yield line_number, line


# Split on whitespace and punctuations: keep only characters and numbers and +
# when in the middle or end of a word. Keeping the trailing + is important for
# licenses name such as GPL2+
query_pattern = '[^_\\W]+\\+?[^_\\W]*'
word_splitter = re.compile(query_pattern, re.UNICODE).findall


def query_tokenizer(text, stopwords=STOPWORDS):
    """
    Return an iterable of tokens from a unicode query text. Ignore words that
    exist as lowercase in the `stopwords` set.

    For example::
    >>> list(query_tokenizer(''))
    []
    >>> x = list(query_tokenizer('some Text with   spAces! + _ -'))
    >>> assert x == ['some', 'text', 'with', 'spaces']

    >>> x = list(query_tokenizer('{{}some }}Text with   spAces! + _ -'))
    >>> assert x == ['some', 'text', 'with', 'spaces']

    >>> x = list(query_tokenizer('{{Hi}}some {{}}Text with{{noth+-_!@ing}}   {{junk}}spAces! + _ -{{}}'))
    >>> assert x == ['hi', 'some', 'text', 'with', 'noth+', 'ing', 'junk', 'spaces']

    """
    return _query_tokenizer(text.lower(), stopwords)


def _query_tokenizer(text, stopwords=STOPWORDS):
    """
    Return an iterable of tokens from a unicode query text. Ignore words that
    exist as lowercase in the `stopwords` set.
    """
    if not text:
        return []
    return (token for token in word_splitter(text) if token and token not in stopwords)


# Alternate pattern which is the opposite of query_pattern used for
# matched text collection
not_query_pattern = '[_\\W\\s\\+]+[_\\W\\s]?'

# collect tokens and non-token texts in two different groups
_text_capture_pattern = (
    '(?P<token>' +
        query_pattern +
    ')' +
    '|' +
    '(?P<punct>' +
        not_query_pattern +
    ')'
)
tokens_and_non_tokens = re.compile(_text_capture_pattern, re.UNICODE).finditer


def matched_query_text_tokenizer(text):
    """
    Return an iterable of tokens and non-tokens punctuation from a unicode query
    text keeping everything (including punctuations, line endings, etc.)
    The returned iterable contains 2-tuples of:
    - True if the string is a text token or False if this is not
      (such as punctuation, spaces, etc).
    - the corresponding string.
    This is used to reconstruct the matched query text for reporting.
    """
    if not text:
        return
    for match in tokens_and_non_tokens(text):
        if match:
            mgd = match.groupdict()
            token = mgd.get('token')
            punct = mgd.get('punct')
            if token:
                yield True, token
            elif punct:
                yield False, punct
            else:
                # this should never happen
                raise Exception('Internal error in matched_query_text_tokenizer')


def ngrams(iterable, ngram_length):
    """
    Return an iterable of ngrams of length `ngram_length` given an `iterable`.
    Each ngram is a tuple of `ngram_length` items.

    The returned iterable is empty if the input iterable contains less than
    `ngram_length` items.

    Note: this is a fairly arcane but optimized way to compute ngrams.

    For example:
    >>> list(ngrams([1,2,3,4,5], 2))
    [(1, 2), (2, 3), (3, 4), (4, 5)]

    >>> list(ngrams([1,2,3,4,5], 4))
    [(1, 2, 3, 4), (2, 3, 4, 5)]

    >>> list(ngrams([1,2,3,4], 2))
    [(1, 2), (2, 3), (3, 4)]

    >>> list(ngrams([1,2,3], 2))
    [(1, 2), (2, 3)]

    >>> list(ngrams([1,2], 2))
    [(1, 2)]

    >>> list(ngrams([1], 2))
    []

    This also works with arrays or tuples:

    >>> from array import array
    >>> list(ngrams(array('h', [1,2,3,4,5]), 2))
    [(1, 2), (2, 3), (3, 4), (4, 5)]

    >>> list(ngrams(tuple([1,2,3,4,5]), 2))
    [(1, 2), (2, 3), (3, 4), (4, 5)]
    """
    return zip(*(islice(iterable, i, None) for i in range(ngram_length)))


def select_ngrams(ngrams, with_pos=False):
    """
    Return an iterable as a subset of a sequence of ngrams using the hailstorm
    algorithm. If `with_pos` is True also include the starting position for the
    ngram in the original sequence.

    Definition from the paper: http://www2009.eprints.org/7/1/p61.pdf

      The algorithm first fingerprints every token and then selects a shingle s
      if the minimum fingerprint value of all k tokens in s occurs at the first
      or the last position of s (and potentially also in between). Due to the
      probabilistic properties of Rabin fingerprints the probability that a
      shingle is chosen is 2/k if all tokens in the shingle are different.

    For example:
    >>> list(select_ngrams([(2, 1, 3), (1, 1, 3), (5, 1, 3), (2, 6, 1), (7, 3, 4)]))
    [(2, 1, 3), (1, 1, 3), (5, 1, 3), (2, 6, 1), (7, 3, 4)]

    Positions can also be included. In this case, tuple of (pos, ngram) are returned:
    >>> list(select_ngrams([(2, 1, 3), (1, 1, 3), (5, 1, 3), (2, 6, 1), (7, 3, 4)], with_pos=True))
    [(0, (2, 1, 3)), (1, (1, 1, 3)), (2, (5, 1, 3)), (3, (2, 6, 1)), (4, (7, 3, 4))]

    This works also from a generator:
    >>> list(select_ngrams(x for x in [(2, 1, 3), (1, 1, 3), (5, 1, 3), (2, 6, 1), (7, 3, 4)]))
    [(2, 1, 3), (1, 1, 3), (5, 1, 3), (2, 6, 1), (7, 3, 4)]
    """
    last = None
    for pos, ngram in enumerate(ngrams):
        # FIXME: use a proper hash
        nghs = []
        for ng in ngram:
            if ((py2 and isinstance(ng, basestring))
                    or (py3 and isinstance(ng, str))):
                ng = bytearray(ng, encoding='utf-8')
            else:
                ng = bytearray(str(ng).encode('utf-8'))
            nghs.append(crc32(ng) & 0xffffffff)
        min_hash = min(nghs)
        if with_pos:
            ngram = (pos, ngram,)
        if min_hash in (nghs[0], nghs[-1]):
            yield ngram
            last = ngram
        else:
            # always yield the first or last ngram too.
            if pos == 0:
                yield ngram
                last = ngram
    if last != ngram:
        yield ngram
