#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from licensedcode import tokenize
"""
Matching strategy for unknown matching using ngrams.
"""

# Set to False to enable debug tracing
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


def add_ngrams(automaton, tids, rule_length, unknown_ngram_length=7):
    """
    Add the `tids` sequence of token ids to an unknown ngram automaton.
    """
    if rule_length < unknown_ngram_length:
        return

    rule_ngrams = tokenize.ngrams(tids, ngram_length=unknown_ngram_length)

    for ngram in rule_ngrams:
        ngram = tuple(ngram)
        automaton.add_word(ngram, ngram)


def unknown_match(idx, query_run, automaton, unknown_ngram_length=7, **kwargs):
    """
    Return a list of unknown LicenseMatch by matching the `query_run` against
    the `automaton` and `idx` index.
    """
    matches = list(get_matches(
        qtokens=query_run.tokens,
        qbegin=query_run.start,
        automaton=automaton,
        unknown_ngram_length=unknown_ngram_length,
    ))
    return matches


def get_matches(qtokens, qbegin, automaton, unknown_ngram_length=7):
    """
    Yield tuples of automaton matches positions as (match start, match end, match value) from
    matching `qtokens` sequence of query token ids starting at the `qbegin` absolute
    query start position position using the `automaton`.
    """
    # iterate over matched strings: the matched value is matching ngram
    qtokens = tuple(qtokens)
    for qend, matched_ngram in automaton.iter(qtokens):
        qend = qbegin + qend + 1
        qstart = qend - unknown_ngram_length
        yield qstart, qend, matched_ngram 
