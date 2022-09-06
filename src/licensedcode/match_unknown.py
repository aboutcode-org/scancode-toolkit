#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import ahocorasick

from licensedcode import tokenize
from licensedcode.models import UnknownRule
from licensedcode.match import get_full_qspan_matched_text
from licensedcode.match import LicenseMatch
from licensedcode.spans import Span

"""
Matching strategy for unknown license detection using ngrams.
"""

# Set to True to enable debug tracing
TRACE = False

if TRACE:
    import logging
    import sys

    logger = logging.getLogger(__name__)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, str) and a or repr(a) for a in args))

    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

else:

    def logger_debug(*args):
        pass

MATCH_UNKNOWN = '6-unknown'

UNKNOWN_NGRAM_LENGTH = 6


def get_automaton():
    """
    Return a new empty automaton.
    """
    return ahocorasick.Automaton(ahocorasick.STORE_INTS, ahocorasick.KEY_SEQUENCE)  # NOQA


def add_ngrams(
    automaton,
    tids,
    tokens,
    rule_length,
    len_legalese,
    unknown_ngram_length=UNKNOWN_NGRAM_LENGTH,
):
    """
    Add the `tids` sequence of token ids to an unknown ngram automaton.
    """
    if rule_length >= unknown_ngram_length:
        tids_ngrams = tokenize.ngrams(tids, ngram_length=unknown_ngram_length)
        toks_ngrams = tokenize.ngrams(tokens, ngram_length=unknown_ngram_length)
        for tids_ngram, toks_ngram in zip(tids_ngrams, toks_ngrams):
            if is_good_tokens_ngram(toks_ngram, tids_ngram, len_legalese):
                # note that we do not store positions as values, only the ngram
                # since we do not keep the rule origin of an ngram
                automaton.add_word(tids_ngram)


markers = frozenset([
    'copyright', 'c', 'copyrights',
    'rights',
    'reserved',
    'trademark',
    'foundation', 'government', 'institute', 'university',
    'inc', 'corp', 'co',
    'author',
    'com', 'org', 'net', 'uk', 'fr', 'be', 'de',
    'http', 'https', 'www',
])


def is_good_tokens_ngram(
    tokens_ngram,
    tids_ngram,
    len_legalese,
    markers=markers,
):
    """
    Return True if the ``tokens_ngram`` ngram of token strings or ``tids_ngram``
    ngram of token ids is a "good" ngram.
    """
    min_good = 3

    # too many digits
    if sum(t.isdigit() for t in tokens_ngram) >= min_good:
        return False

    # a year is a sign of copyright
    if any(t.isdigit() and len(t) == 4 for t in tokens_ngram):
        return False

    # too many single chars
    if sum(len(t) == 1 for t in tokens_ngram) >= min_good:
        return False

    # too little token diversity, e.g. this is a repeat
    if len(set(tids_ngram)) <= 2:
        return False

    # we want at least one high token
    if not any(tid < len_legalese for tid in tids_ngram):
        return False

    # copyright and similar markers
    if any(t in markers for t in tokens_ngram):
        return False

    return True


def match_unknowns(
    idx,
    query_run,
    automaton,
    unknown_ngram_length=UNKNOWN_NGRAM_LENGTH,
    **kwargs,
):
    """
    Return a LicenseMatch (or None) by matching the ``query_run`` against the
    ``automaton`` and ``idx`` index.
    """
    matched_ngrams = get_matched_ngrams(
        tokens=query_run.tokens,
        qbegin=query_run.start,
        automaton=automaton,
        unknown_ngram_length=unknown_ngram_length,
    )

    if TRACE:
        tokens_by_tid = idx.tokens_by_tid

        def get_tokens(_toks):
            return (' '.join(tokens_by_tid[t] for t in _toks))

        print('match_unknowns: matched_ngrams')
        for qstart, qend, matched_toks in matched_ngrams:
            print(
                '   ', 'qstart', qstart,
                'qend', qend,
                'matched_toks', get_tokens(matched_toks))

    # build match from merged matched ngrams
    qspans = (Span(qstart, qend) for qstart, qend in matched_ngrams)
    qspan = Span().union(*qspans)

    if not qspan:
        return

    query = query_run.query
    query_tokens = query.tokens

    matched_tokens = [query_tokens[qpos] for qpos in qspan]
    match_len = len(qspan)

    if TRACE:
        print('match_unknowns: matched_span:', get_tokens(matched_tokens))

    # we use the query side to build the ispans
    ispan = Span(0, match_len)

    # build synthetic rule text for "only_matched" text
    line_by_pos = query.line_by_pos

    try:
        match_start_line = line_by_pos[qspan.start]
        match_end_line = line_by_pos[qspan.end]
    except:
        print('empty span:', qspan)
        raise

    text = ''.join(get_full_qspan_matched_text(
        match_qspan=qspan,
        match_query_start_line=query.start_line,
        match_start_line=match_start_line,
        match_end_line=match_end_line,
        location=query.location,
        query_string=query.query_string,
        idx=idx,
        only_matched=True,
    ))

    if TRACE:
        print('match_unknowns: text', text)

    # ... and use this in a synthetic UnknownRule
    rule = UnknownRule(text=text, length=match_len)

    # finally craft a LicenseMatch and return
    len_legalese = idx.len_legalese
    hispan = Span(
        ipos for ipos, tok in zip(ispan, matched_tokens)
        if tok < len_legalese
    )

    if len(qspan) < unknown_ngram_length * 4 or len(hispan) < 5:
        if TRACE:
            print('match_unknowns: Skipping weak unkown match', text)
        return

    match = LicenseMatch(
        rule=rule,
        qspan=qspan,
        ispan=ispan,
        hispan=hispan,
        query_run_start=query_run.start,
        matcher=MATCH_UNKNOWN,
        query=query,
    )

    if TRACE:
        print('match_unknowns: match:', match)

    return match


def get_matched_ngrams(
    tokens,
    qbegin,
    automaton,
    unknown_ngram_length=UNKNOWN_NGRAM_LENGTH,
):
    """
    Yield tuples of automaton matching positions as (qstart, qend)
    from matching the ``tokens`` sequence of query token ids starting at the
    `qbegin` absolute query start position position using the `automaton`.
    """
    # iterate over matched strings: the matched value is the matching ngram
    # which is an n-tuple of token ids
    qtokens = tuple(tokens)
    offset = unknown_ngram_length - 1
    for qend, _ in automaton.iter(qtokens):
        qend = qbegin + qend
        qstart = qend - offset
        yield qstart, qend
