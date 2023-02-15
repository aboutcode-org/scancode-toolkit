# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import re
from collections import defaultdict
from binascii import crc32
from itertools import islice

from licensedcode.spans import Span
from licensedcode.stopwords import STOPWORDS
from textcode.analysis import numbered_text_lines

"""
Utilities to break texts in lines and tokens (aka. words),
and handle required phrases in texts through these tokens,
with specialized version for queries and rules texts.
"""


def query_lines(
    location=None,
    query_string=None,
    strip=True,
    start_line=1,
    plain_text=False,
):
    """
    Return an iterable of tuples (line number, text line) given a file at
    `location` or a `query string`. Include empty lines.
    Line numbers start at ``start_line`` which is 1-based by default.

    If `plain_text` is True treat the file as a plain text file and do not
    attempt to detect its type and extract its content with special procedures.
    This is used mostly when loading license texts and rules.
    """
    # TODO: OPTIMIZE: tokenizing line by line may be rather slow
    # we could instead get lines and tokens at once in a batch?
    numbered_lines = []
    if location:
        numbered_lines = numbered_text_lines(
            location,
            demarkup=False,
            start_line=start_line,
            plain_text=plain_text,
        )

    elif query_string:
        if strip:
            keepends = False
        else:
            keepends = True

        numbered_lines = enumerate(
            query_string.splitlines(keepends),
            start_line,
        )

    for line_number, line in numbered_lines:
        if strip:
            yield line_number, line.strip()
        else:
            yield line_number, line.rstrip('\n') + '\n'

# Split on whitespace and punctuations: keep only characters and numbers and +
# when in the middle or end of a word. Keeping the trailing + is important for
# licenses name such as GPL2+. The use a double negation "not non word" meaning
# "words" to define the character ranges


query_pattern = '[^_\\W]+\\+?[^_\\W]*'
word_splitter = re.compile(query_pattern, re.UNICODE).findall

key_phrase_pattern = '(?:' + query_pattern + '|\\{\\{|\\}\\})'
key_phrase_splitter = re.compile(key_phrase_pattern, re.UNICODE).findall

KEY_PHRASE_OPEN = '{{'
KEY_PHRASE_CLOSE = '}}'

# FIXME: this should be folded in a single pass tokenization with the index_tokenizer


def key_phrase_tokenizer(text, stopwords=STOPWORDS):
    """
    Yield tokens from a rule ``text`` including key phrases {{brace}} markers.
    This tokenizer behaves the same as as the ``index_tokenizer`` returning also
    KEY_PHRASE_OPEN and KEY_PHRASE_CLOSE as separate tokens so that they can be
    used to parse key phrases.

    >>> x = list(key_phrase_splitter('{{AGPL-3.0  GNU Affero License v3.0}}'))
    >>> assert x == ['{{', 'AGPL', '3', '0', 'GNU', 'Affero', 'License', 'v3', '0', '}}'], x

    >>> x = list(key_phrase_splitter('{{{AGPL{{{{Affero }}License}}0}}'))
    >>> assert x == ['{{', 'AGPL', '{{', '{{', 'Affero', '}}', 'License', '}}', '0', '}}'], x

    >>> list(index_tokenizer('')) == []
    True

    >>> x = list(index_tokenizer('{{AGPL-3.0  GNU Affero License v3.0}}'))
    >>> assert x == ['agpl', '3', '0', 'gnu', 'affero', 'license', 'v3', '0']

    >>> x = list(key_phrase_tokenizer('{{AGPL-3.0  GNU Affero License v3.0}}'))
    >>> assert x == ['{{', 'agpl', '3', '0', 'gnu', 'affero', 'license', 'v3', '0', '}}']
    """
    if not text:
        return
    for token in key_phrase_splitter(text.lower()):
        if token and token not in stopwords:
            yield token


def return_spans_for_key_phrase_in_text(text, key_phrase):
    """
    Returns a list of Spans where in `text`, the `key_phrase` exists,
    and if it doesn't exist anywhere, returns an empty list.
    """
    spans_with_key_phrase = []
    
    text_tokens = list(index_tokenizer(text))
    key_phrase_tokens = list(index_tokenizer(key_phrase))
    key_phrase_first_token = key_phrase_tokens[0]

    if all([
        key_phrase_token in text_tokens
        for key_phrase_token in key_phrase_tokens
    ]):
        start_positions = [
            i
            for i, x in enumerate(text_tokens)
            if x == key_phrase_first_token
        ]

        for start_pos in start_positions:
            end_pos = start_pos + len(key_phrase_tokens)

            if end_pos <= len(text_tokens) and text_tokens[start_pos:end_pos] == key_phrase_tokens:
                spans_with_key_phrase.append(
                    Span(start_pos, end_pos-1)
                )
    
    return spans_with_key_phrase


def get_ignorable_spans(rule):
    """
    Return a list of Spans which are the positions in the rule text there
    are ignorable URLs or referenced filenames.
    """
    ignorable_spans = []
    ignorables = rule.referenced_filenames + rule.ignorable_urls
    for ignorable in ignorables:
        ignorable_spans.extend(
            return_spans_for_key_phrase_in_text(text=rule.text, key_phrase=ignorable)
        )
    
    return ignorable_spans


def get_non_overlapping_spans(old_key_phrase_spans, new_key_phrase_spans):
    """
    Given two list of spans `old_key_phrase_spans` and `new_key_phrase_spans`,
    return all the spans in `new_key_phrase_spans` that do not overlap with any
    of the spans in `old_key_phrase_spans`.

    The list of spans `old_key_phrase_spans` contains all the spans of required
    phrases or ignorables already present in a rule text, and the other list of spans
    `new_key_phrase_spans` contains the proposed new required phrases.
    """
    if not old_key_phrase_spans:
        return new_key_phrase_spans
    
    for new_span in new_key_phrase_spans:
        if not any(
            old_span.overlap(new_span) != 0
            for old_span in old_key_phrase_spans
        ):
            yield new_span


def combine_tokens(token_tuples):
    """
    Returns a string `combined_text` combining token tuples from the list `token_tuples`,
    which are token tuples created by the tokenizer functions.
    """
    combined_text = ''
    
    for token_tuple in token_tuples:
        _value, token = token_tuple
        combined_text += token
        
    return combined_text


def add_key_phrase_markers(text, key_phrase_span):
    """
    Given a string `text` and a Span object `key_phrase_span`, add key phrase
    markers to the `text` around the tokens which the span represents, while
    being mindful of whitespace and stopwords.
    """
    tokens_tuples_without_markers = list(matched_query_text_tokenizer(text))
    tokens_tuples_with_markers = []
    token_index = 0

    for token_tuple in tokens_tuples_without_markers:
        
        is_word, token = token_tuple

        if is_word and token not in STOPWORDS:
            if token_index == key_phrase_span.start:
                tokens_tuples_with_markers.append((False, KEY_PHRASE_OPEN))

            token_index += 1

        tokens_tuples_with_markers.append(token_tuple)
        
        if is_word and token not in STOPWORDS: 
            if token_index == key_phrase_span.end + 1:
                tokens_tuples_with_markers.append((False, KEY_PHRASE_CLOSE))
            
    return combine_tokens(tokens_tuples_with_markers)


def index_tokenizer(text, stopwords=STOPWORDS):
    """
    Return an iterable of tokens from a rule or query ``text`` using index
    tokenizing rules. Ignore words that exist as lowercase in the ``stopwords``
    set.

    For example::
    >>> list(index_tokenizer(''))
    []
    >>> x = list(index_tokenizer('some Text with   spAces! + _ -'))
    >>> assert x == ['some', 'text', 'with', 'spaces']

    >>> x = list(index_tokenizer('{{}some }}Text with   spAces! + _ -'))
    >>> assert x == ['some', 'text', 'with', 'spaces']

    >>> x = list(index_tokenizer('{{Hi}}some {{}}Text with{{noth+-_!@ing}}   {{junk}}spAces! + _ -{{}}'))
    >>> assert x == ['hi', 'some', 'text', 'with', 'noth+', 'ing', 'junk', 'spaces']

    >>> stops = set(['quot', 'lt', 'gt'])
    >>> x = list(index_tokenizer('some &quot&lt markup &gt&quot', stopwords=stops))
    >>> assert x == ['some', 'markup']
    """
    if not text:
        return []
    words = word_splitter(text.lower())
    return (token for token in words if token and token not in stopwords)


def index_tokenizer_with_stopwords(text, stopwords=STOPWORDS):
    """
    Return a tuple of (tokens, stopwords_by_pos) for a rule
    ``text`` using index tokenizing rules where tokens is a list of tokens and
    stopwords_by_pos is a mapping of {pos: stops count} where "pos" is a token
    position and "stops count" is the number of stopword tokens after this
    position if any. For stopwords at the start, the position is using the magic
    -1 key. Use the lowercase ``stopwords`` set.

    For example::

    >>> toks, stops = index_tokenizer_with_stopwords('')
    >>> assert toks == [], (toks, stops)
    >>> assert stops == {}

    >>> toks, stops = index_tokenizer_with_stopwords('some Text with   spAces! + _ -')
    >>> assert toks == ['some', 'text', 'with', 'spaces'], (toks, stops)
    >>> assert stops == {}

    >>> toks, stops = index_tokenizer_with_stopwords('{{}some }}Text with   spAces! + _ -')
    >>> assert toks == ['some', 'text', 'with', 'spaces'], (toks, stops)
    >>> assert stops == {}

    >>> toks, stops = index_tokenizer_with_stopwords('{{Hi}}some {{}}Text with{{noth+-_!@ing}}   {{junk}}spAces! + _ -{{}}')
    >>> assert toks == ['hi', 'some', 'text', 'with', 'noth+', 'ing', 'junk', 'spaces'], (toks, stops)
    >>> assert stops == {}

    >>> stops = set(['quot', 'lt', 'gt'])
    >>> toks, stops = index_tokenizer_with_stopwords('some &quot&lt markup &gt&quot', stopwords=stops)
    >>> assert toks == ['some', 'markup'], (toks, stops)
    >>> assert stops == {0: 2, 1: 2}

    >>> toks, stops = index_tokenizer_with_stopwords('{{g', stopwords=stops)
    >>> assert toks == ['g'], (toks, stops)
    >>> assert stops == {}
    """
    if not text:
        return [], {}

    tokens = []
    tokens_append = tokens.append

    # we use a defaultdict as a convenience at construction time
    # TODO: use the actual words and not just a count
    stopwords_by_pos = defaultdict(int)

    pos = -1

    for token in word_splitter(text.lower()):
        if token:
            if token in stopwords:
                # If we have not yet started, then all tokens seen so far
                # are stopwords and we keep a count of them in the magic
                # "-1" position.
                stopwords_by_pos[pos] += 1
            else:
                pos += 1
                tokens_append(token)

    return tokens, dict(stopwords_by_pos)


def query_tokenizer(text):
    """
    Return an iterable of tokens from a unicode query text. Do not ignore stop
    words. They are handled at a later stage in a query.

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
    if not text:
        return []
    words = word_splitter(text.lower())
    return (token for token in words if token)


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
            if isinstance(ng, str):
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
