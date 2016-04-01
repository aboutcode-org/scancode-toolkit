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

from __future__ import print_function, absolute_import

from copy import copy
from itertools import islice
from itertools import izip

from licensedcode.whoosh_spans.spans import Span
from licensedcode import NGRAM_LENGTH
from licensedcode.match import LicenseMatch
from licensedcode.tokenize import ngrams


"""
Matching strategy using mapping of token sequences to rules positions

The idea is to match long sequences of tokens at once. For instance. matching
a whole license text in one lookup without needing any further alignment.

For that we index for each rule the starter ngrams mapped to a rule start
position and matchable length as a matchable rule span. A rule has one starter
ngram if this is not a template, or several if this a template.

At matching time:
 - compute ngrams from the query.
 - lookup ngrams in the index for starter ngrams.
 -- If there is a match check if we can match this at once again the corresponding rule span
 --- if yes, yield a LicenseMatch 
 --- if this is an exact match, skip the matched query chunk 
"""

# Set to True to enable debug tracing
DEBUG = False

if DEBUG :
    import logging
    import sys

    logger = logging.getLogger(__name__)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, basestring) and a or repr(a) for a in args))

    # logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)
else:
    def logger_debug(*args):
        pass


MATCH_TYPE = 'chunk'


def index_starters(rule_tokens, gaps, _ngram_length=NGRAM_LENGTH):
    """
    Given an sequence of rule tokens and a set of gaps for that rule, return a
    sequence of tuples of (starter ngram, start,) computed from the tokens,
    gaps and ngram len. start is the starting position of the ngram.
    """
    rule_tokens = list(rule_tokens)
    len_tokens = len(rule_tokens)
    if not gaps:
        # no gaps: consider only the first ngram and the whole rule.
        if len_tokens >= _ngram_length:
            yield tuple(rule_tokens[:_ngram_length]), 0
    else:
        # T' starts at -1
        # pos:
        # 0 1 2 T 3 4 5 6 7 T 8 9 L
        # gaps + len:
        #       2           7     10
        # slices:
        #  [0:3]      [3:8]     [8:11]
        # span:
        #  [0:2]      [3:7]     [8:10]
        # recipe:
        #  [T'+1:T+1] [T'+1:T+1] [T'+1:T+1]

        for start, ngram in enumerate(ngrams(rule_tokens, ngram_length=_ngram_length)):
            if start == 0:
                if not any(g in gaps for g in range(0, _ngram_length - 2)):
                    yield ngram, start

            elif start - 1 in gaps and not any(p in range(start, start + _ngram_length - 1) for p in gaps):
                yield ngram, start


def match_chunks(idx, candidates, query_run, _ngram_length=NGRAM_LENGTH):
    """
    Return a LicenseMatch by matching the query sequence against the idx index
    only for the `candidates` rule ids. `candidates` is a list of candidate rule
    ids sorted by decreasing likeliness of being matched. Match uses
    `idx.start_ngrams_by_rid` ngrams of `ngram_length`.
    """
    logger_debug('match_chunks: start....')

    # FIXME: likely not needed
    query_run = copy(query_run)

    candidates = set(candidates)
    chunk_matches = []
    # loop for as long as we have matches returned
    while True:
        if not candidates:
            break
        matches = _match_chunk(idx, candidates, query_run, _ngram_length)
        if matches:
            chunk_matches.extend(matches)
            query_run.substract(matches)
            # refine the candidates
        else:
            break

    logger_debug('match_chunks: matched_chunks:', len(chunk_matches))
    if DEBUG:
        if chunk_matches:
            logger_debug('match_chunks: matched_chunks:')
            map(logger_debug, chunk_matches)
        else:
            logger_debug('  match_chunks: ..NO matched_chunks:')

    return chunk_matches


def _match_chunk(idx, candidates, query_run, _ngram_length=NGRAM_LENGTH):
    """
    Return a sequence of LicenseMatch by matching the longest possible
    `query_tokens` sequence against the idx index only for the sequence of
    `candidates` rule ids.
    """
    logger_debug('_match_chunk: start....')

    starters = idx.start_ngrams_by_rid
    tokens_by_rid = idx.tokens_by_rid

    query_run_start = query_run.start

    matches = []
    matches_append = matches.append
    for qngram, qstart in query_run.ngrams(_ngram_length):
        for rid in candidates:
            rid_starters = starters[rid]
            if not rid_starters:
#                 logger_debug(' no rid_starters')
                continue

            istarts = rid_starters.get(qngram)
            if DEBUG:
                if istarts is not None:
                    logger_debug(' _match_chunks: found rid_starters')
                    logger_debug('  _match_chunks: qngram, qstart:', u' '.join(idx.tokens_by_tid[t] for t in qngram), qstart)
                    logger_debug('  _match_chunks: rid_starters:', [(u' '.join(idx.tokens_by_tid[t] for t in key), values) for key, values in rid_starters.items()])

            if istarts is None:
                continue

            if DEBUG: logger_debug(' _match_chunks: FOUND rid_starters istarts, qstart', istarts, qstart)

            rule = idx.rules_by_rid[rid]
            rule_tokens = tokens_by_rid[rid]
            # find the longest matching sequence starting at this starter
            for istart in istarts:
                if DEBUG: logger_debug(' _match_chunks: for istart in istarts')

                # handle query_run start offset
                qtks = islice(query_run.tokens, qstart - query_run_start, None)
                itks = islice(rule_tokens, istart, None)
                # note that we do not izip_longest here
                pos = -1
                broke = False
                for pos, (qtok, itok) in enumerate(izip(qtks, itks)):

                    if DEBUG: logger_debug('   _match_chunks: considering --> matched pos:', pos, 'token:', idx.tokens_by_tid[qtok])

                    if qtok != itok:
                        if DEBUG: logger_debug('    _match_chunks: BREAK: qtok != itok --> matched pos:', pos, 'qtoken:', idx.tokens_by_tid[qtok], 'itoken:', idx.tokens_by_tid[itok])
                        broke = True
                        break
                if pos != -1:
                    # at worst we will have a match that is ngram_length long
                    if DEBUG:
                        logger_debug('      _match_chunks: ==>pos != -1')

                    if broke:
                        offset_fix = 1
                    else:
                        offset_fix = 0

                    if DEBUG:
                        logger_debug('        _match_chunks: ==>pos qstart', qstart)

                    # handle query_run start offset
                    # qspan = [Span(qstart + query_run_start, qstart + pos - offset_fix + query_run_start)]
                    qspan = Span(qstart, qstart + pos - offset_fix)
                    ispan = Span(istart, istart + pos - offset_fix)
#                     print()
#                     print('qspan', qspan)
#                     print()
#                     print('ispan', qspan)
#                     print()
#                     print('query_run.start', query_run.start)
#                     print()
#                     map(print, [(pos, idx.tokens_by_tid[tid]) for pos, tid in query_run.tokens_pos()])
#                     print()

                    match = LicenseMatch(rule, qspan, ispan, query_run.line_by_pos, _type=MATCH_TYPE)

                    if DEBUG:
                        logger_debug('        _match_chunks: appending match:', match)
                        logger_debug('          _match_chunks: appending matched spans:', qspan, ispan)

                    matches_append(match)

            if DEBUG:
                logger_debug(' _match_chunks: ==>END for istart in istarts')

            # TODO: advance to next match and skip matched parts???

    if DEBUG:
        logger_debug('_match_chunk: matches found')
        matches = list(matches)
        map(logger_debug, matches)

    return matches
