# -*- coding: utf-8 -*-
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

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from itertools import islice
from itertools import izip
import re
from zlib import crc32

from textcode.analysis import text_lines


"""
Utilities to break texts in lines and tokens (aka. words) with specialized version
for queries and rules texts.
"""


def query_lines(location=None, query_string=None):
    """
    Return an iterable of text lines given a file at `location` or a
    `query string`. Include empty lines. 
    """
    # TODO: OPTIMIZE: tokenizing line by line may be rather slow
    # we could instead get lines and tokens at once in a batch?
    lines = []
    if location:
        lines = text_lines(location, demarkup=False)
    elif query_string:
        lines = query_string.splitlines(False)

    for line in lines:
        yield line.strip()


# Split on whitespace and punctuations: keep only characters using a (trick)
# double negation regex on characters (e.g. [^\W]), underscore, dash and +.
# Keeping the + is important for licenses name such as GPL2+.
query_pattern = r'[^\W_\-\+©]+'
word_splitter = re.compile(query_pattern, re.UNICODE).findall


def query_tokenizer(text, lower=True):
    """
    Return an iterable of tokens from a unicode query text.
    """
    if not text:
        return []
    text = lower and text.lower() or text
    return (token for token in word_splitter(text) if token)


# Template-aware splitter, keeping a templated part {{anything}} as a token.
# This splitter yields plain token strings or double braces-enclosed strings
# {{something}} for templates.
# Use non capturing groups for alternation.
rule_pattern = r'''
    # Same split on white space and punctuation as in word_splitter
    (?:[^\W_\-\+©])+
    |
    # a template part is anything enclosed in double braces
    (?:{{[^{}]*}})
'''
template_splitter = re.compile(rule_pattern , re.UNICODE | re.VERBOSE).findall


def rule_tokenizer(text, lower=True):
    """
    Return an iterable of tokens from a unicode rule text, skipping templated
    parts, including leading and trailing templated parts.

    For example:
    >>> list(rule_tokenizer(''))
    []
    >>> list(rule_tokenizer('some Text with   spAces! + _ -'))
    [u'some', u'text', u'with', u'spaces']

    Unbalanced templates are handled correctly:
    >>> list(rule_tokenizer('{{}some }}Text with   spAces! + _ -'))
    [u'some', u'text', u'with', u'spaces']

    Templates are handled and skipped for templated sequences:
    >>> list(rule_tokenizer('{{Hi}}some {{}}Text with{{noth+-_!@ing}}   {{junk}}spAces! + _ -{{}}'))
    [u'some', u'text', u'with', u'spaces']
    """
    if not text:
        return []
    text = lower and text.lower() or text
    tokens = template_splitter(text)
    # skip templates
    return (token for token in tokens if token and not token.startswith('{{'))


def ngrams(iterable, ngram_length):
    """
    Return an iterable of ngrams of length `ngram_length` given an iterable.
    Each ngram is a tuple of ngram_length items.
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
    >>> list(ngrams(array(b'h', [1,2,3,4,5]), 2))
    [(1, 2), (2, 3), (3, 4), (4, 5)]

    >>> list(ngrams(tuple([1,2,3,4,5]), 2))
    [(1, 2), (2, 3), (3, 4), (4, 5)]
    """
    return izip(*(islice(iterable, i, None) for i in range(ngram_length)))


def select_ngrams(ngrams, with_pos=False):
    """
    Return an iterable as a subset of a sequence of ngrams using the hailstorm
    algorithm. If `with_pos` is True also include the starting position for the ngram
    in the original sequence.
    
    Definition from the paper: http://www2009.eprints.org/7/1/p61.pdf
      The algorithm first fingerprints every token and then selects a shingle s if
      the minimum fingerprint value of all k tokens in s occurs at the first or the
      last position of s (and potentially also in between). Due to the
      probabilistic properties of Rabin fingerprints the probability that a shingle
      is chosen is 2/k if all tokens in the shingle are different.

    For example:
    >>> list(select_ngrams([(2, 1, 3), (1, 1, 3), (5, 1, 3), (2, 6, 1), (7, 3, 4)]))
    [(2, 1, 3), (1, 1, 3), (2, 6, 1), (7, 3, 4)]

    Positions can also be included. In this case, tuple of (pos, ngram) are returned:
    >>> list(select_ngrams([(2, 1, 3), (1, 1, 3), (5, 1, 3), (2, 6, 1), (7, 3, 4)], with_pos=True))
    [(0, (2, 1, 3)), (1, (1, 1, 3)), (3, (2, 6, 1)), (4, (7, 3, 4))]

    This works also from a generator:
    >>> list(select_ngrams(x for x in [(2, 1, 3), (1, 1, 3), (5, 1, 3), (2, 6, 1), (7, 3, 4)]))
    [(2, 1, 3), (1, 1, 3), (2, 6, 1), (7, 3, 4)]
    """
    last = None
    for i, ngram in enumerate(ngrams):
        # FIXME: use a proper hash
        nghs = [crc32(str(ng)) for ng in ngram]
        min_hash = min(nghs)
        if with_pos:
            ngram = (i, ngram,)
        if nghs[0] == min_hash or nghs[-1] == min_hash:
            yield ngram
            last = ngram
        else:
            # always yield the first or last ngram too.
            if i == 0:
                yield ngram
                last = ngram
    if last != ngram:
        yield ngram
