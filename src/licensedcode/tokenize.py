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

from array import array
from collections import deque
from itertools import islice
from itertools import izip
import re
from zlib import crc32

from textcode.analysis import text_lines

from licensedcode import NGRAM_LENGTH


"""
Utilities to break texts in lines and tokens (aka. words) and ngrams with
specialized version for queries and rules texts.
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
        lines = text_lines(location, demarkup=True)
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
        return
    text = lower and text.lower() or text
    for token in word_splitter(text):
        if token:
            yield token


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
    Return an iterable of tokens from a unicode rule text returning templated
    parts as a None token. Leading and trailing templated parts are skipped.

    For example:
    >>> list(rule_tokenizer(''))
    []
    >>> list(rule_tokenizer('some Text with   spAces! + _ -'))
    [u'some', u'text', u'with', u'spaces']

    Unbalanced templates are handled correctly:
    >>> list(rule_tokenizer('{{}some }}Text with   spAces! + _ -'))
    [u'some', u'text', u'with', u'spaces']

    Templates are handled correctly and yielding None for templates:
    >>> list(rule_tokenizer('{{Hi}}some {{}}Text with{{noth+-_!@ing}}   {{junk}}spAces! + _ -{{}}'))
    [u'some', None, u'text', u'with', None, u'spaces']
    """
    if not text:
        return

    text = lower and text.lower() or text
    tokens = template_splitter(text)
    # replace templates with None
    tokens = [None if token.startswith('{{') else token for token in tokens]

    # remove leading and trailing templates
    while tokens and tokens[0] is None:
        del tokens[0]
    while tokens and tokens[-1] is None:
        del tokens[-1]

    tokens = iter(tokens)
    previous = next(tokens)
    yield previous

    for token in tokens:
        if token:
            yield token
        else:
            # Here token is None and a gap.
            # yield only if the previous was not a gap:
            # only return one gap for contiguous gaps
            if previous:
                yield token
        previous = token

def ngrams_longuest(tokens, ngram_length=NGRAM_LENGTH, offset=0, len_junk=0):
    """
    Return an iterable of (start, len, ngram) where ngram is a tuple of
    `ngram_length` or less tokens from a given a sequence of tokens. 

    If tokens contains less than `ngram_length` elements, the ngram will be
    shorter than ngram_length.
    Add `offset` to the start.

    For example:
    >>> list(ngrams_longuest([1,2,3,4,5], 2))
    [(0, 2, '\\x01\\x00\\x02\\x00'), (1, 2, '\\x02\\x00\\x03\\x00'), (2, 2, '\\x03\\x00\\x04\\x00'), (3, 2, '\\x04\\x00\\x05\\x00')]

    >>> list(ngrams_longuest([1,2,3,4,5], 6))
    [(0, 5, '\\x01\\x00\\x02\\x00\\x03\\x00\\x04\\x00\\x05\\x00')]

    >>> list(ngrams_longuest([1,2,3,4,5], 5))
    [(0, 5, '\\x01\\x00\\x02\\x00\\x03\\x00\\x04\\x00\\x05\\x00')]

    >>> list(ngrams_longuest([1,2,3,4], 2))
    [(0, 2, '\\x01\\x00\\x02\\x00'), (1, 2, '\\x02\\x00\\x03\\x00'), (2, 2, '\\x03\\x00\\x04\\x00')]

    >>> list(ngrams_longuest([1,2,3], 2))
    [(0, 2, '\\x01\\x00\\x02\\x00'), (1, 2, '\\x02\\x00\\x03\\x00')]

    >>> list(ngrams_longuest([1,2], 3))
    [(0, 2, '\\x01\\x00\\x02\\x00')]

    >>> list(ngrams_longuest([1], 2))
    [(0, 1, '\\x01\\x00')]
    """
    if not tokens:
        return

    lt = len(tokens)
    if lt <= ngram_length:
        if tokens[0] >= len_junk and tokens[-1] >= len_junk:
            yield offset, lt, array(b'h', tokens).tostring()
    else:
        ngram = deque()
        tokens = iter(tokens)

        for _ in range(ngram_length - 1):
            ngram.append(next(tokens))

        for start, tok in enumerate(tokens):
            ngram.append(tok)
            ln = len(ngram)
            # only yield ngrams starting or ending with a high token
            if ngram[0] >= len_junk and ngram[-1] >= len_junk:
                yield start + offset, ln, array(b'h', ngram).tostring()
            ngram.popleft()


def multigrams(tokens, ngram_length=NGRAM_LENGTH, offset=0, len_junk=0):
    """
    Return an iterable of (start, len, ngram) for every ngram length from one
    (e.g. unigrams) to ngram_length given a sequence of tokens. Add `offset` to
    start. Only return multigrams whose start or end is a high token id.

    For example, with these tokens [1, 2, 3, 4, 5] and ngram_length 3, these
    ngrams are returned::

    >>> unigrams = [1, 2, 3, 4, 5]
    >>> from pprint import pprint
    >>> pprint(list(multigrams(unigrams, 3)))
    [(0, 3, '\\x01\\x00\\x02\\x00\\x03\\x00'),
     (1, 3, '\\x02\\x00\\x03\\x00\\x04\\x00'),
     (2, 3, '\\x03\\x00\\x04\\x00\\x05\\x00'),
     (0, 2, '\\x01\\x00\\x02\\x00'),
     (1, 2, '\\x02\\x00\\x03\\x00'),
     (2, 2, '\\x03\\x00\\x04\\x00'),
     (3, 2, '\\x04\\x00\\x05\\x00'),
     (0, 1, '\\x01\\x00'),
     (1, 1, '\\x02\\x00'),
     (2, 1, '\\x03\\x00'),
     (3, 1, '\\x04\\x00'),
     (4, 1, '\\x05\\x00')]


    And with ngram_length 4, these tokens are returned::

    >>> pprint(list(multigrams(unigrams, 4)))
    [(0, 4, '\\x01\\x00\\x02\\x00\\x03\\x00\\x04\\x00'),
     (1, 4, '\\x02\\x00\\x03\\x00\\x04\\x00\\x05\\x00'),
     (0, 3, '\\x01\\x00\\x02\\x00\\x03\\x00'),
     (1, 3, '\\x02\\x00\\x03\\x00\\x04\\x00'),
     (2, 3, '\\x03\\x00\\x04\\x00\\x05\\x00'),
     (0, 2, '\\x01\\x00\\x02\\x00'),
     (1, 2, '\\x02\\x00\\x03\\x00'),
     (2, 2, '\\x03\\x00\\x04\\x00'),
     (3, 2, '\\x04\\x00\\x05\\x00'),
     (0, 1, '\\x01\\x00'),
     (1, 1, '\\x02\\x00'),
     (2, 1, '\\x03\\x00'),
     (3, 1, '\\x04\\x00'),
     (4, 1, '\\x05\\x00')]

    >>> pprint(list(multigrams(unigrams, 6)))
    [(0, 5, '\\x01\\x00\\x02\\x00\\x03\\x00\\x04\\x00\\x05\\x00'),
     (0, 4, '\\x01\\x00\\x02\\x00\\x03\\x00\\x04\\x00'),
     (1, 4, '\\x02\\x00\\x03\\x00\\x04\\x00\\x05\\x00'),
     (0, 3, '\\x01\\x00\\x02\\x00\\x03\\x00'),
     (1, 3, '\\x02\\x00\\x03\\x00\\x04\\x00'),
     (2, 3, '\\x03\\x00\\x04\\x00\\x05\\x00'),
     (0, 2, '\\x01\\x00\\x02\\x00'),
     (1, 2, '\\x02\\x00\\x03\\x00'),
     (2, 2, '\\x03\\x00\\x04\\x00'),
     (3, 2, '\\x04\\x00\\x05\\x00'),
     (0, 1, '\\x01\\x00'),
     (1, 1, '\\x02\\x00'),
     (2, 1, '\\x03\\x00'),
     (3, 1, '\\x04\\x00'),
     (4, 1, '\\x05\\x00')]
    """
    if len(tokens) < ngram_length:
        ngram_length = len(tokens)
    # iterate backwards the ngram length i.e. 4,3,2,1
    for n in range(ngram_length, 0, -1):
        for ng in ngrams_longuest(tokens, n, offset, len_junk):
            yield ng


def rule_multigrams(tokens, ngram_length=NGRAM_LENGTH, gaps=None, len_junk=0):
    """
    Return an iterable of tuple(start, len, ngram) given a `tokens` sequence.
    Each ngram is a tuple of ngram_length tokens or less.

    Skip ngrams that spans over a `gaps` positions where `gaps` is a set of gap
    start positions.

    Skip some ngrams that contain junk tokens.

    For example:

    >>> tokens = [1, 2, 3, 4, 5]
    >>> from pprint import pprint
    >>> pprint(list(rule_multigrams(tokens, 3)))
    [(0, 3, '\\x01\\x00\\x02\\x00\\x03\\x00'),
     (1, 3, '\\x02\\x00\\x03\\x00\\x04\\x00'),
     (2, 3, '\\x03\\x00\\x04\\x00\\x05\\x00'),
     (0, 2, '\\x01\\x00\\x02\\x00'),
     (1, 2, '\\x02\\x00\\x03\\x00'),
     (2, 2, '\\x03\\x00\\x04\\x00'),
     (3, 2, '\\x04\\x00\\x05\\x00'),
     (0, 1, '\\x01\\x00'),
     (1, 1, '\\x02\\x00'),
     (2, 1, '\\x03\\x00'),
     (3, 1, '\\x04\\x00'),
     (4, 1, '\\x05\\x00')]

    With gaps
    >>> tokens = [1, 2, 3, 4, 5]
    >>> gaps = set([2])
    >>> from pprint import pprint
    >>> pprint(list(rule_multigrams(tokens, 2, gaps)))
    [(0, 2, '\\x01\\x00\\x02\\x00'),
     (1, 2, '\\x02\\x00\\x03\\x00'),
     (0, 1, '\\x01\\x00'),
     (1, 1, '\\x02\\x00'),
     (2, 1, '\\x03\\x00'),
     (3, 2, '\\x04\\x00\\x05\\x00'),
     (3, 1, '\\x04\\x00'),
     (4, 1, '\\x05\\x00')]

    With gaps and junk:
    >>> tokens = [1, 2, 3, 4, 5]
    >>> gaps = set([2])
    >>> from pprint import pprint
    >>> pprint(list(rule_multigrams(tokens, 2, gaps, len_junk=2)))
    [(1, 2, '\\x02\\x00\\x03\\x00'),
     (1, 1, '\\x02\\x00'),
     (2, 1, '\\x03\\x00'),
     (3, 2, '\\x04\\x00\\x05\\x00'),
     (3, 1, '\\x04\\x00'),
     (4, 1, '\\x05\\x00')]

    """
    for start, chunk in rule_tokens_slices(tokens, gaps):
        for start, nglen, ngram in multigrams(chunk, ngram_length, start, len_junk):
            yield start, nglen, ngram


def rule_tokens_slices(tokens, gaps=None):
    """
    Return an iterable of tuple(start, tokens sub-sequence) given a `tokens`
    sequence by breaking the tokens sequence in sub-sequences at each gap if
    any.
    Also breaks the sequence on tokens with a None or -1 value.
    None or -1 are not returned as values.

    For example:
    >>> tokens = [1, 2, 3, 4, 5]
    >>> list(rule_tokens_slices(tokens))
    [(0, array('h', [1, 2, 3, 4, 5]))]

    >>> tokens = []
    >>> list(rule_tokens_slices(tokens))
    []

    With gaps
    >>> tokens = [5, 6, 7, 8, 8, 9, 11]
    >>> list(rule_tokens_slices(tokens, gaps=set([1,3])))
    [(0, array('h', [5, 6])), (2, array('h', [7, 8])), (4, array('h', [8, 9, 11]))]
    """
    if not tokens:
        return
    if not gaps:
        yield 0, array(b'h', tokens)
    else:
        prevgap = 0
        for gap in sorted(gaps):
            # first slice from start to first gap
            if not prevgap:
                yield prevgap, array(b'h', tokens[:gap + 1])
                prevgap = gap
                continue
            # middle slices: from prevgap to next gap
            yield prevgap + 1, array(b'h', tokens[prevgap + 1 : gap + 1])
            prevgap = gap

        # last slice from last gap to the end
        yield prevgap + 1, array(b'h', tokens[prevgap + 1:])

def query_multigrams(tokens, ngram_length=NGRAM_LENGTH, len_junk=0, offset=0):
    """
    Return an iterable of tuple(start, len, ngram) given a `tokens` sequence.
    Each ngram is a tuple of ngram_length tokens or less.

    Add offset to start.
    Skip ngrams that contain None or -1 for unknown tokens.
    Skip some ngrams that contain junk tokens.

    For example:

    >>> tokens = [1, 2, 3, 4, 5]
    >>> from pprint import pprint
    >>> pprint(list(query_multigrams(tokens, 3)))
    [(0, 3, '\\x01\\x00\\x02\\x00\\x03\\x00'),
     (1, 3, '\\x02\\x00\\x03\\x00\\x04\\x00'),
     (2, 3, '\\x03\\x00\\x04\\x00\\x05\\x00'),
     (0, 2, '\\x01\\x00\\x02\\x00'),
     (1, 2, '\\x02\\x00\\x03\\x00'),
     (2, 2, '\\x03\\x00\\x04\\x00'),
     (3, 2, '\\x04\\x00\\x05\\x00'),
     (0, 1, '\\x01\\x00'),
     (1, 1, '\\x02\\x00'),
     (2, 1, '\\x03\\x00'),
     (3, 1, '\\x04\\x00'),
     (4, 1, '\\x05\\x00')]

    With unknown tokens:
    >>> tokens = [1, 2, 3, -1, 4, 5]
    >>> from pprint import pprint
    >>> pprint(list(query_multigrams(tokens, 2)))
    [(0, 2, '\\x01\\x00\\x02\\x00'),
     (1, 2, '\\x02\\x00\\x03\\x00'),
     (0, 1, '\\x01\\x00'),
     (1, 1, '\\x02\\x00'),
     (2, 1, '\\x03\\x00'),
     (4, 2, '\\x04\\x00\\x05\\x00'),
     (4, 1, '\\x04\\x00'),
     (5, 1, '\\x05\\x00')]

    With unknown tokens and junk:
    >>> tokens = [1, 2, 3, -1, 4, 5]
    >>> from pprint import pprint
    >>> pprint(list(query_multigrams(tokens, 2, len_junk=2)))
    [(0, 2, '\\x01\\x00\\x02\\x00'),
     (1, 2, '\\x02\\x00\\x03\\x00'),
     (0, 1, '\\x01\\x00'),
     (1, 1, '\\x02\\x00'),
     (2, 1, '\\x03\\x00'),
     (4, 2, '\\x04\\x00\\x05\\x00'),
     (4, 1, '\\x04\\x00'),
     (5, 1, '\\x05\\x00')]

    With unknown tokens and junk and offset:
    >>> tokens = [1, 2, 3, -1, 4, 5]
    >>> from pprint import pprint
    >>> pprint(list(query_multigrams(tokens, 2, len_junk=2, offset=3)))
    [(3, 2, '\\x01\\x00\\x02\\x00'),
     (4, 2, '\\x02\\x00\\x03\\x00'),
     (3, 1, '\\x01\\x00'),
     (4, 1, '\\x02\\x00'),
     (5, 1, '\\x03\\x00'),
     (7, 2, '\\x04\\x00\\x05\\x00'),
     (7, 1, '\\x04\\x00'),
     (8, 1, '\\x05\\x00')]
    """
    for start, chunk in query_tokens_slices(tokens):
        for start, nglen, ngram in multigrams(chunk, ngram_length, offset=start):
            yield start + offset, nglen, ngram



def query_multigramsold(tokens, ngram_length=NGRAM_LENGTH, len_junk=0, offset=0):
    """
    Return an iterable of tuple(start, len, ngram) given a `tokens` sequence.
    Each ngram is a tuple of ngram_length tokens or less.

    Add offset to start.
    Skip ngrams that contain None or -1 for unknown tokens.
    Skip some ngrams that contain junk tokens.

    For example:

    >>> tokens = [1, 2, 3, 4, 5]
    >>> from pprint import pprint
    >>> pprint(list(query_multigrams(tokens, 3)))
    [(0, 3, '\\x01\\x00\\x02\\x00\\x03\\x00'),
     (1, 3, '\\x02\\x00\\x03\\x00\\x04\\x00'),
     (2, 3, '\\x03\\x00\\x04\\x00\\x05\\x00'),
     (0, 2, '\\x01\\x00\\x02\\x00'),
     (1, 2, '\\x02\\x00\\x03\\x00'),
     (2, 2, '\\x03\\x00\\x04\\x00'),
     (3, 2, '\\x04\\x00\\x05\\x00'),
     (0, 1, '\\x01\\x00'),
     (1, 1, '\\x02\\x00'),
     (2, 1, '\\x03\\x00'),
     (3, 1, '\\x04\\x00'),
     (4, 1, '\\x05\\x00')]

    With unknown tokens:
    >>> tokens = [1, 2, 3, -1, 4, 5]
    >>> from pprint import pprint
    >>> pprint(list(query_multigrams(tokens, 2)))
    [(0, 2, '\\x01\\x00\\x02\\x00'),
     (1, 2, '\\x02\\x00\\x03\\x00'),
     (0, 1, '\\x01\\x00'),
     (1, 1, '\\x02\\x00'),
     (2, 1, '\\x03\\x00'),
     (4, 2, '\\x04\\x00\\x05\\x00'),
     (4, 1, '\\x04\\x00'),
     (5, 1, '\\x05\\x00')]

    With unknown tokens and junk:
    >>> tokens = [1, 2, 3, -1, 4, 5]
    >>> from pprint import pprint
    >>> pprint(list(query_multigrams(tokens, 2, len_junk=2)))
    [(0, 2, '\\x01\\x00\\x02\\x00'),
     (1, 2, '\\x02\\x00\\x03\\x00'),
     (0, 1, '\\x01\\x00'),
     (1, 1, '\\x02\\x00'),
     (2, 1, '\\x03\\x00'),
     (4, 2, '\\x04\\x00\\x05\\x00'),
     (4, 1, '\\x04\\x00'),
     (5, 1, '\\x05\\x00')]

    With unknown tokens and junk and offset:
    >>> tokens = [1, 2, 3, -1, 4, 5]
    >>> from pprint import pprint
    >>> pprint(list(query_multigrams(tokens, 2, len_junk=2, offset=3)))
    [(3, 2, '\\x01\\x00\\x02\\x00'),
     (4, 2, '\\x02\\x00\\x03\\x00'),
     (3, 1, '\\x01\\x00'),
     (4, 1, '\\x02\\x00'),
     (5, 1, '\\x03\\x00'),
     (7, 2, '\\x04\\x00\\x05\\x00'),
     (7, 1, '\\x04\\x00'),
     (8, 1, '\\x05\\x00')]
    """
    for start, chunk in query_tokens_slices(tokens):
        for start, nglen, ngram in multigrams(chunk, ngram_length, offset=start):
            yield start + offset, nglen, ngram


def query_tokens_slices(tokens):
    """
    Return an iterable of tuple(start, tokens sub-sequence) given a `tokens`
    sequence by breaking the tokens sequence in sub-sequences at tokens with a
    None or -1 value. None or -1 are not returned in the sub-sequences but they
    increment start positions.

    For example:
    >>> tokens = [1, 2, 3, 4, 5]
    >>> list(query_tokens_slices(tokens))
    [(0, [1, 2, 3, 4, 5])]

    >>> tokens = []
    >>> list(query_tokens_slices(tokens))
    []

    With gaps
    >>> tokens = [None, -1, 5, 6, 7, 8, 8, 9, 11, -1, None]
    >>> list(query_tokens_slices(tokens))
    [(2, [5, 6, 7, 8, 8, 9, 11])]

    >>> tokens = [None, -1, 5, 6, 7, 8, -1, None, 8, 9, 11, -1, None]
    >>> list(query_tokens_slices(tokens))
    [(2, [5, 6, 7, 8]), (8, [8, 9, 11])]

    >>> tokens = [None, -1, 5, 6, 7, 8, -1, None, 8, 9, -1, 11, -1, None]
    >>> list(query_tokens_slices(tokens))
    [(2, [5, 6, 7, 8]), (8, [8, 9]), (11, [11])]
    """
    if not tokens:
        return

    pos_tokens = list(enumerate(tokens))

    # remove leading and trailing None and -1 tokens
    # FIXME: why -1?
    while pos_tokens and (pos_tokens[0][1] is None or pos_tokens[0][1] < 0):
        del pos_tokens[0]
    while pos_tokens and (pos_tokens[-1][1] is None or pos_tokens[-1][1] < 0):
        del pos_tokens[-1]

    if not pos_tokens:
        return

    pos_tokens = iter(pos_tokens)

    toks = deque()
    # first tok is never a gap by construction
    toks.append(next(pos_tokens))

    for start, token in pos_tokens:
        if token is not None and token > -1:
            toks.append((start, token,))
        else:
            # Here token is unknown.
            # yield accumulated and reset
            if toks:
                start, _ = toks[0]
                yield start, [t for _, t in toks]
                toks.clear()

    # last sub seq
    if toks:
        start, _ = toks[0]
        yield start, [t for _, t in toks]


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
    """
    return izip(*(islice(iterable, i, None) for i in range(ngram_length)))


def ngrams2(iterable, ngram_length):
    """
    Return an iterable of ngrams of length `ngram_length` given an iterable.
    Each ngram is a tuple of ngram_length items.
    The returned iterable is empty if the input iterable contains less than
    `ngram_length` items.

    For example:
    >>> list(ngrams2([1,2,3,4,5], 2))
    [(1, 2), (2, 3), (3, 4), (4, 5)]

    >>> list(ngrams2([1,2,3,4,5], 4))
    [(1, 2, 3, 4), (2, 3, 4, 5)]

    >>> list(ngrams2([1,2,3,4], 2))
    [(1, 2), (2, 3), (3, 4)]
    
    >>> list(ngrams2([1,2,3], 2))
    [(1, 2), (2, 3)]
    >>> list(ngrams2([1,2], 2))
    [(1, 2)]
    >>> list(ngrams2([1], 2))
    []
    """
    iterable = iter(iterable)
    ngram = deque()
    for _ in range(ngram_length - 1):
        ngram.append(next(iterable))

    for token in iterable:
        ngram.append(token)
        yield tuple(ngram)
        ngram.popleft()


def select_ngrams(ngrams):
    """
    Return an iterable subset of a sequence of ngrams.
    
    Using the hailstorm algorithm.
    DEFINITION: from the paper: Hailstorm (Hs)
    http://www2009.eprints.org/7/1/p61.pdf

    The algorithm first fingerprints every token and then selects a shingle s if
    the minimum fingerprint value of all k tokens in s occurs at the first or
    the last position of s (and potentially also in between). Due to the
    probabilistic properties of Rabin fingerprints the probability that a
    shingle is chosen is 2/k if all tokens in the shingle are different."

    For example:
    >>> list(select_ngrams([(2, 1, 3), (1, 1, 3), (5, 1, 3), (2, 6, 1), (7, 3, 4)]))
    [(2, 1, 3), (1, 1, 3), (2, 6, 1), (7, 3, 4)]
    """
    last = len(ngrams) - 1
    for i, ngram in enumerate(ngrams):
        # FIXME: use a proper hash
        nghs = [crc32(str(ng)) for ng in ngram]
        min_hash = min(nghs)
        if nghs[0] == min_hash or nghs[-1] == min_hash:
            yield ngram
        else:
            # always yield the first or last ngram too.
            if i == 0 or i == last:
                yield ngram
