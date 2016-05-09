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

from collections import deque
from itertools import islice
from itertools import izip
import re

from licensedcode import NGRAM_LENGTH
from textcode.analysis import text_lines


"""
Utilities to break texts in lines, tokens (aka. words) and ngrams with
specialized version for queries and rules texts.
"""


def query_lines(location=None, query_string=None):
    """
    Return an iterable of line text given a file at location or a
    query string. Include empty lines. 
    """
    # TODO: OPTIMIZE: tokenizing line by line may be rather slow
    # we could instead get lines and tokens at once in a batch?
    lines = []
    if location:
        lines = text_lines(location)
    elif query_string:
        lines = query_string.splitlines(False)

    for line in lines:
        yield line.strip()


# Split on whitespace and punctuation: keep only characters using a (trick)
# double negation regex on characters (e.g. [^\W]), underscore, dash and +
word_splitter = re.compile(r'[^\W_\-\+]+', re.UNICODE).findall


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


def query_tokenid_tokenizer(text, dictionary):
    """
    Return an iterable of token ids from a unicode query text and a dictionary.
    Return -1 for unknown tokens.
    """
    if not text:
        return
    for token in word_splitter(text.lower()):
        if token:
            yield dictionary.get(token, -1)



# Template-aware splitter, keeping a templated part {{anything}} as a token.
# This splitter yields plain token strings or double braces-enclosed strings
# {{something}} for templates.
template_splitter = re.compile(r'''
    # Use non capturing groups for alternation.
    # same split on white space and punctuation as in word_splitter
    (?:[^\W_\-\+])+
    |
    # a template part is anything enclosed in double braces
    (?:{{[^{}]*}})
''' , re.UNICODE | re.VERBOSE).findall


def rule_tokenizer(text, lower=True):
    """
    Return an iterable of tokens from a unicode rule text returning templated
    parts as a -1 token. Leading and trailing templated parts are skipped.

    For example:
    >>> list(rule_tokenizer(''))
    []
    >>> list(rule_tokenizer('some Text with   spAces! + _ -'))
    ['some', 'text', 'with', 'spaces']

    Unbalanced templates are handled correctly:
    >>> list(rule_tokenizer('{{}some }}Text with   spAces! + _ -'))
    ['some', 'text', 'with', 'spaces']

    Templates are handled correctly and yielding None for templates:
    >>> list(rule_tokenizer('{{Hi}}some {{}}Text with{{noth+-_!@ing}}   {{junk}}spAces! + _ -{{}}'))
    ['some', None, 'text', 'with', None, 'spaces']
    """
    if not text:
        return

    text = lower and text.lower() or text
    tokens = template_splitter(text)
    # replace templates with None
    tokens = [None if token.startswith(u'{{') else token for token in tokens]

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


def query_ngrams(tokens, ngram_length=NGRAM_LENGTH, start=0):
    """
    Return an iterable of tuple(start position, ngram) given a `tokens` iterable. 
    Each ngram is a tuple of ngram_length tokens.
    Start positions start at `start`.
    Skip ngrams that contain a None token.

    For example:
    >>> list(query_ngrams([1,2,3,4,5], 2))
    [(0, (1, 2)), (1, (2, 3)), (2, (3, 4)), (3, (4, 5))]
    >>> list(query_ngrams([1,2,3,4], 3))
    [(0, (1, 2, 3)), (1, (2, 3, 4))]
    >>> list(query_ngrams([1,2,3,4], 5))
    []
    >>> list(query_ngrams([1,2], 2))
    [(0, (1, 2))]
    >>> list(query_ngrams([1], 2))
    []

    With Nones:
    >>> list(query_ngrams([1,2,3,None], 3))
    [(0, (1, 2, 3))]

    With start:
    >>> list(query_ngrams([1,2,3,4,5], 2, 5))
    [(5, (1, 2)), (6, (2, 3)), (7, (3, 4)), (8, (4, 5))]
    >>> list(query_ngrams([1,None,3,4,5], 2, 5))
    [(7, (3, 4)), (8, (4, 5))]
    """
    qngrams = enumerate(ngrams(tokens, ngram_length), start)
    return ((start, ngram) for start, ngram in qngrams if None not in ngram)


def rule_ngrams(tokens, ngram_length=NGRAM_LENGTH, gaps=None):
    """
    Return an iterable of tuple(start position, ngram) given a `tokens` iterable.
    Each ngram is a tuple of ngram_length tokens.

    Skip ngrams that spans over a `gaps` positions where `gaps` is a set of gap
    start positions.
    
    For example:
    >>> list(rule_ngrams([1,2,3,4,5], 2))
    [(0, (1, 2)), (1, (2, 3)), (2, (3, 4)), (3, (4, 5))]
    >>> list(rule_ngrams([1,2,3,4], 3))
    [(0, (1, 2, 3)), (1, (2, 3, 4))]
    >>> list(rule_ngrams([1,2,3,4], 5))
    []
    >>> list(rule_ngrams([1,2], 2))
    [(0, (1, 2))]
    >>> list(rule_ngrams([1], 2))
    []
    >>> list(rule_ngrams([5,6,7,8,8,9], ngram_length=3))
    [(0, (5, 6, 7)), (1, (6, 7, 8)), (2, (7, 8, 8)), (3, (8, 8, 9))]

    With gaps at 1 (item 6) and 3 (item 8):
    >>> list(rule_ngrams([5,6,7,8,12,9], ngram_length=2, gaps=set([1,3])))
    [(0, (5, 6)), (2, (7, 8)), (4, (12, 9))]
    >>> list(rule_ngrams([5,6,7,8,12,9], ngram_length=3, gaps=set([1,3])))
    []
    """
    for start, ngram in enumerate(ngrams(tokens, ngram_length)):
        if gaps:
            # Note: by design it is perfectly ok for the last token of an ngram
            # to be at a gap position. The gap position is the same as the token
            # just before a gap.
            if not any(p in gaps for p in xrange(start, start + ngram_length - 1)):
                yield start, ngram
        else:
            yield start, ngram


def ngrams_longuest(tokens, ngram_length=NGRAM_LENGTH, offset=0):
    """
    Return an iterable of (start, len, ngram) where ngram is a tuple of
    `ngram_length` or less tokens from a given a sequence of tokens. 

    If tokens contains less than `ngram_length` elements, the ngram will be
    shorter than ngram_length.
    Add `offset` to the start.

    For example:
    >>> list(ngrams_longuest([1,2,3,4,5], 2))
    [(0, 2, (1, 2)), (1, 2, (2, 3)), (2, 2, (3, 4)), (3, 2, (4, 5))]

    >>> list(ngrams_longuest([1,2,3,4,5], 6))
    [(0, 5, (1, 2, 3, 4, 5))]

    >>> list(ngrams_longuest([1,2,3,4,5], 5))
    [(0, 5, (1, 2, 3, 4, 5))]

    >>> list(ngrams_longuest([1,2,3,4], 2))
    [(0, 2, (1, 2)), (1, 2, (2, 3)), (2, 2, (3, 4))]
 
    >>> list(ngrams_longuest([1,2,3], 2))
    [(0, 2, (1, 2)), (1, 2, (2, 3))]
    >>> list(ngrams_longuest([1,2], 3))
    [(0, 2, (1, 2))]
    >>> list(ngrams_longuest([1], 2))
    [(0, 1, (1,))]
    """
    if not tokens:
        return

    if len(tokens) <= ngram_length:
        yield offset, len(tokens), tuple(tokens)
    else:
        ngram = deque()
        tokens = iter(tokens)

        for _ in range(ngram_length - 1):
            ngram.append(next(tokens))

        for start, tok in enumerate(tokens):
            ngram.append(tok)
            yield start + offset, len(ngram), tuple(ngram)
            ngram.popleft()


def multigrams(tokens, ngram_length=NGRAM_LENGTH, offset=0):
    """
    Return an iterable of (start, len, ngram) for every ngram length from one
    (e.g. unigrams) to ngram_length given a sequence of tokens.
    Add `offset` to start.

    For example, with these tokens [1, 2, 3, 4, 5] and ngram_length 3, these ngrams
    are returned::

    >>> unigrams = [1, 2, 3, 4, 5]
    >>> from pprint import pprint
    >>> pprint(list(multigrams(unigrams, 3)))
    [(0, 3, (1, 2, 3)),
     (1, 3, (2, 3, 4)),
     (2, 3, (3, 4, 5)),
     (0, 2, (1, 2)),
     (1, 2, (2, 3)),
     (2, 2, (3, 4)),
     (3, 2, (4, 5)),
     (0, 1, (1,)),
     (1, 1, (2,)),
     (2, 1, (3,)),
     (3, 1, (4,)),
     (4, 1, (5,))]

    And with ngram_length 4, these tokens are returned::

    >>> pprint(list(multigrams(unigrams, 4)))
    [(0, 4, (1, 2, 3, 4)),
     (1, 4, (2, 3, 4, 5)),
     (0, 3, (1, 2, 3)),
     (1, 3, (2, 3, 4)),
     (2, 3, (3, 4, 5)),
     (0, 2, (1, 2)),
     (1, 2, (2, 3)),
     (2, 2, (3, 4)),
     (3, 2, (4, 5)),
     (0, 1, (1,)),
     (1, 1, (2,)),
     (2, 1, (3,)),
     (3, 1, (4,)),
     (4, 1, (5,))]

    >>> pprint(list(multigrams(unigrams, 6)))
    [(0, 5, (1, 2, 3, 4, 5)),
     (0, 4, (1, 2, 3, 4)),
     (1, 4, (2, 3, 4, 5)),
     (0, 3, (1, 2, 3)),
     (1, 3, (2, 3, 4)),
     (2, 3, (3, 4, 5)),
     (0, 2, (1, 2)),
     (1, 2, (2, 3)),
     (2, 2, (3, 4)),
     (3, 2, (4, 5)),
     (0, 1, (1,)),
     (1, 1, (2,)),
     (2, 1, (3,)),
     (3, 1, (4,)),
     (4, 1, (5,))]
    """
    if len(tokens) < ngram_length:
        ngram_length = len(tokens)
    # iterate backwards the ngram length i.e. 4,3,2,1
    for n in range(ngram_length, 0, -1):
        for ng in ngrams_longuest(tokens, n, offset):
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
    [(0, 3, (1, 2, 3)),
     (1, 3, (2, 3, 4)),
     (2, 3, (3, 4, 5)),
     (0, 2, (1, 2)),
     (1, 2, (2, 3)),
     (2, 2, (3, 4)),
     (3, 2, (4, 5)),
     (0, 1, (1,)),
     (1, 1, (2,)),
     (2, 1, (3,)),
     (3, 1, (4,)),
     (4, 1, (5,))]

    With gaps
    >>> tokens = [1, 2, 3, 4, 5]
    >>> gaps = set([2])
    >>> from pprint import pprint
    >>> pprint(list(rule_multigrams(tokens, 2, gaps)))
    [(0, 2, (1, 2)),
     (1, 2, (2, 3)),
     (0, 1, (1,)),
     (1, 1, (2,)),
     (2, 1, (3,)),
     (3, 2, (4, 5)),
     (3, 1, (4,)),
     (4, 1, (5,))]

    With gaps and junk:
    >>> tokens = [1, 2, 3, 4, 5]
    >>> gaps = set([2])
    >>> from pprint import pprint
    >>> pprint(list(rule_multigrams(tokens, 2, gaps, len_junk=2)))
    [(0, 2, (1, 2)),
     (1, 2, (2, 3)),
     (1, 1, (2,)),
     (2, 1, (3,)),
     (3, 2, (4, 5)),
     (3, 1, (4,)),
     (4, 1, (5,))]
    """
    for start, chunk in rule_tokens_slices(tokens, gaps):
        for start, nglen, ngram in multigrams(chunk, ngram_length, offset=start):
            if nglen in (1, 2, 3) and all(tid < len_junk for tid in ngram):
                continue
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
    [(0, [1, 2, 3, 4, 5])]

    >>> tokens = []
    >>> list(rule_tokens_slices(tokens))
    []

    With gaps
    >>> tokens = [5, 6, 7, 8, 8, 9, 11]
    >>> list(rule_tokens_slices(tokens,gaps=set([1,3])))
    [(0, [5, 6]), (2, [7, 8]), (4, [8, 9, 11])]
    """
    if not tokens:
        return
    if not gaps:
        yield 0, tokens
    else:
        prevgap = 0
        for gap in sorted(gaps):
            # first slice from start to first gap
            if not prevgap:
                yield prevgap, tokens[:gap + 1]
                prevgap = gap
                continue
            # middle slices: from prevgap to next gap
            yield prevgap + 1, tokens[prevgap + 1 : gap + 1]
            prevgap = gap

        # last slice from last gap to the end
        yield prevgap + 1, tokens[prevgap + 1:]


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
    [(0, 3, (1, 2, 3)),
     (1, 3, (2, 3, 4)),
     (2, 3, (3, 4, 5)),
     (0, 2, (1, 2)),
     (1, 2, (2, 3)),
     (2, 2, (3, 4)),
     (3, 2, (4, 5)),
     (0, 1, (1,)),
     (1, 1, (2,)),
     (2, 1, (3,)),
     (3, 1, (4,)),
     (4, 1, (5,))]

    With unknown tokens:
    >>> tokens = [1, 2, 3, -1, 4, 5]
    >>> from pprint import pprint
    >>> pprint(list(query_multigrams(tokens, 2)))
    [(0, 2, (1, 2)),
     (1, 2, (2, 3)),
     (0, 1, (1,)),
     (1, 1, (2,)),
     (2, 1, (3,)),
     (4, 2, (4, 5)),
     (4, 1, (4,)),
     (5, 1, (5,))]

    With unknown tokens and junk:
    >>> tokens = [1, 2, 3, -1, 4, 5]
    >>> from pprint import pprint
    >>> pprint(list(query_multigrams(tokens, 2, len_junk=2)))
    [(0, 2, (1, 2)),
     (1, 2, (2, 3)),
     (1, 1, (2,)),
     (2, 1, (3,)),
     (4, 2, (4, 5)),
     (4, 1, (4,)),
     (5, 1, (5,))]

    With unknown tokens and junk and offset:
    >>> tokens = [1, 2, 3, -1, 4, 5]
    >>> from pprint import pprint
    >>> pprint(list(query_multigrams(tokens, 2, len_junk=2, offset=3)))
    [(3, 2, (1, 2)),
     (4, 2, (2, 3)),
     (4, 1, (2,)),
     (5, 1, (3,)),
     (7, 2, (4, 5)),
     (7, 1, (4,)),
     (8, 1, (5,))]
    """
    for start, chunk in query_tokens_slices(tokens):
        for start, nglen, ngram in multigrams(chunk, ngram_length, offset=start):
            if nglen in (1, 2, 3) and all(tid < len_junk for tid in ngram):
                continue
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
