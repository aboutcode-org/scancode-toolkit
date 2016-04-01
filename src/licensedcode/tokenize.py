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
from itertools import islice
from itertools import izip

from licensedcode import NGRAM_LENGTH


"""
Utilities to tokenize rules and query texts.
"""

# Split on whitespace and punctuation: keep only characters using a (trick)
# double negation regex on characters (e.g. [^\W]), underscore, dash and +
word_splitter = re.compile(r'[^\W_\-\+]+', re.UNICODE).finditer


def query_tokenizer(text, lower=True):
    """
    Return an iterable of tokens from a unicode query text.
    """
    # FIXME we are processing the whole text at once in memory
    if text:
        text = lower and text.lower() or text
        for match in word_splitter(text):
            token = match.group()
            if token:
                yield token


# Template-aware splitter, keeping a templated part {{anything}} as a token.
# Use non capturing groups for alternation.
template_splitter = re.compile(r'''
    # same split on white space and punctuation as in the base splitter
    (?:[^\W_\-\+])+
    |
    # a template part is anything enclosed in double braces
    (?:{{[^{}]*}})
''' , re.UNICODE | re.VERBOSE).findall


def rule_tokenizer(text, lower=True):
    """
    Return a sequence of tokens from a unicode rule text returning templated
    parts as a None token. Leading and trailing templated parts are skipped.
    """
    if  text:
        text = lower and text.lower() or text
        tokens = template_splitter(text)
        # replace templates with None
        tokens = [None if token.startswith(u'{') else token for token in tokens]

        # remove leading and trailing template templates
        while tokens and tokens[0] is None:
            del tokens[0]
        while tokens and tokens[-1] is None:
            del tokens[-1]

        # remove contiguous templates
        prev = -1
        for token in tokens:
            if prev == -1:
                prev = token
                if token:
                    yield token
                    prev = token
                continue

            if token:
                yield token
                prev = token

            else:
                if prev is None and token is None:
                    continue
                else:
                    yield token
                    prev = token


def ngrams(iterable, ngram_length):
    """
    Return an iterator of tuples of ngrams of length `ngram_len` given an
    iterable. The returned iterable is empty if the input iterable contains less
    than `ngram_length` elements.

    Note: this is a fairly arcane but optimized way to compute ngrams.

    For example:
    >>> list(ngrams([1,2,3,4,5], 2))
    [(1, 2), (2, 3), (3, 4), (4, 5)]
    >>> list(ngrams([1,2,3,4], 2))
    [(1, 2), (2, 3), (3, 4)]
    >>> list(ngrams([1,2,3], 2))
    [(1, 2), (2, 3)]
    >>> list(ngrams([1,2], 2))
    [(1, 2)]
    >>> list(ngrams([1], 2))
    []
    """
    return izip(*(islice(iterable, i, None) for i in range(ngram_length)))


def ngrams_with_positions(tokens, len_junk, start_pos=0, ngram_length=NGRAM_LENGTH):
    """
    Return an iterator of (start, end, ngram tuple) for ngrams of length
    `ngram_len` given an iterable of tokens. The returned iterable is empty if
    the input iterable contains less than `ngram_length` tokens. Only high, non-
    junk tokens are considered: Tokens with a "junk" id and None tokens are
    ignored and not part of the returned ngrams.  For each ngram, the start and
    end position is the absolute position in the token stream. Ngrams may
    therefore have an end position extending beyond start + ngram_length.
    """
    tokens_with_pos = ((pos, token) for pos, token in enumerate(tokens, start_pos)
                                    if token is not None and token > len_junk)

    for pos_ngram in ngrams(tokens_with_pos):
        ngr, poss = zip(*pos_ngram)
        start = poss[0]
        end = poss[-1]
        yield start, end, tuple(ngr)
