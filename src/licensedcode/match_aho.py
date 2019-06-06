#
# Copyright (c) nexB Inc. and others. All rights reserved.
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
from __future__ import division
from __future__ import print_function

from array import array
from itertools import groupby

import ahocorasick

from licensedcode import SMALL_RULE
from licensedcode.match import LicenseMatch
from licensedcode.spans import Span

"""
Matching strategy for exact matching using Aho-Corasick automatons.
"""

# Set to False to enable debug tracing
TRACE = False
TRACE_FRAG = False
TRACE_DEEP = False

if TRACE or TRACE_FRAG:
    import logging
    import sys

    logger = logging.getLogger(__name__)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, basestring) and a or repr(a) for a in args))

    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

else:

    def logger_debug(*args):
        pass


def get_automaton():
    """
    Return a new empty automaton.
    """
    return ahocorasick.Automaton(ahocorasick.STORE_ANY)


def add_sequence(automaton, tids, rid, start=0, with_duplicates=False):
    """
    Add the `tids` sequence of token ids for the `rid` Rule id starting at `start`
    position to the an Aho-Corasick `automaton`.

    If `with_duplicates` is True and if `tids` exists in the automaton, append a
    rule pointers to a list of "values" for these `tids`. Otherwise if `tids`
    exists in the automaton, adding a new sequence will overwrite the previous
    entry.
    """
    end = len(tids) - 1
    # the value for a trie key is a list of tuples (rule id, start position, end position)
    value = rid, start, start + end
    tokens = array('h', tids).tostring()
    if with_duplicates:
        existing = automaton.get(tokens, None)
        if existing:
            # ensure that for identical strings added several times, all rid/pos are
            # added to the value set
            existing.append(value)
        else:
            automaton.add_word(tokens, [value])
    else:
        automaton.add_word(tokens, [value])


MATCH_AHO_EXACT = '2-aho'
MATCH_AHO_FRAG = '5-aho-frag'


def exact_match(idx, query_run, automaton, matcher=MATCH_AHO_EXACT, **kwargs):
    """
    Return a list of exact LicenseMatch by matching the `query_run` against
    the `automaton` and `idx` index.
    """
    if TRACE: logger_debug(' #exact_AHO: start ... ')
    if TRACE_DEEP: logger_debug(' #exact_AHO: query_run:', query_run)

    matches = []
    matches_append = matches.append

    qbegin = query_run.start

    matched_positions = get_matched_positions(query_run.tokens, qbegin, automaton)
    matched_spans = get_matched_spans(matched_positions, query_run.matchables)

    len_legalese = idx.len_legalese
    rules_by_rid = idx.rules_by_rid
    tids_by_rid = idx.tids_by_rid
    query = query_run.query
    for rid, qspan, ispan in matched_spans:
        itokens = tids_by_rid[rid]
        hispan = Span(p for p in ispan if itokens[p] < len_legalese)

        rule = rules_by_rid[rid]
        match = LicenseMatch(
            rule, qspan, ispan, hispan, qbegin, matcher=matcher, query=query)
        matches_append(match)
    if TRACE and matches:
        logger_debug(' ##exact_AHO: matches found#')
        map(print, matches)

    return matches


def get_matched_spans(positions, matchables):
    """
    Yield tuples of matched spans as (rid, qspan, ispan) from an iterable of
    (rid, qstart, qend, istart, iend). Skip position that is not entirely
    within the `matchables` set of matchable positions.
    """
    for rid, match_qstart, match_qend, istart, iend in positions:
        # if not all( x >= 0 for x in (match_qstart, match_qend, istart, iend)):
        #    raise Exception(rid, match_qstart, match_qend, istart, iend)

        qspan = Span(list(range(match_qstart, match_qend)))
        # TODO: is this about negatives? this should be optimized?
        # if any(p not in query_run_matchables for p in qspan):
        if any(p not in matchables for p in qspan):  # not qspan.set.issubset(matchables):
            if TRACE: logger_debug(
                '   #exact_AHO:get_matched_spans not matchable match: any(p not in '
                'query_run_matchables for p in qspan), discarding rule:', rid)
            continue
        ispan = Span(list(range(istart, iend)))
        yield rid, qspan, ispan


def get_matched_positions(tokens, qbegin, automaton):
    """
    Yield tuples of matched positions as (rid, qstart, qend, istart, iend) such
    that these start and end positions are suitable as range() arguments. Match
    `tokens` sequence of token ids starting at the `qbegin` absolute query start
    position position using the `automaton`.
    """
    for qend, matched_rule_segments in get_matches(tokens, qbegin, automaton):
        for rid, istart, iend in matched_rule_segments:
            if TRACE_DEEP:
                logger_debug('   #EXACT get_matches: found match to rule:', rid)
            iend = iend + 1
            match_len = iend - istart
            qstart = qend - match_len
            yield rid, qstart, qend, istart, iend


def get_matches(tokens, qbegin, automaton):
    """
    Yield tuples of automaton matches positions as (match end, match value) from
    matching `tokens` sequence of token ids starting at the `qbegin` absolute
    query start position position using the `automaton`.
    """
    # iterate over matched strings: the matched value is (rule id, index start
    # pos, index end pos)
    qtokens_as_str = array('h', tokens).tostring()
    for qend, matched_value in automaton.iter(qtokens_as_str):

        ################################
        # FIXME: use a trie of ints or a trie of Unicode characters to avoid
        # this shenaningan. NB: this will be possible when using Python 3
        ################################
        # Since the Tries stores bytes and we have two bytes per tokenid,
        # the real end must be adjusted
        real_qend = (qend - 1) / 2
        # ... and there is now a real possibility of a false match. For
        # instance say we have these tokens : gpl encoded as 0012 and lgpl
        # encoded as 1200 and mit as 2600 And if we scan this "mit lgpl" we
        # get this encoding 2600 1200. The automaton will find a matched
        # string of 0012 to gpl in the middle matching falsely so we check
        # that the corrected end qposition must be always an integer.
        real_qend_int = int(real_qend)
        if real_qend != real_qend_int:
            if TRACE_DEEP: logger_debug(
                '   #EXACT get_matches: real_qend != int(real_qend), '
                'discarding match to value:', matched_value)
            continue
        qend = qbegin + real_qend_int + 1
        yield qend, matched_value


def match_fragments(idx, query_run):
    """
    Return a list of Span by matching the `query_run` against the `automaton`
    and `idx` index.

    This is using a BLAST-like matching approach: we match ngram fragments of
    rules (e.g. a seed) and then we extend left and right.
    """
    if TRACE_FRAG:
        logger_debug('-------------->match_fragments')

    # Get matches using the AHO Fragments automaton
    matches = exact_match(
        idx, query_run, automaton=idx.fragments_automaton, matcher=MATCH_AHO_FRAG)
    if TRACE_FRAG:
        logger_debug('match_fragments')
        map(print, matches)

    # Discard fragments that have any already matched positions in previous matches
    from licensedcode.match import filter_already_matched_matches
    matches, _discarded = filter_already_matched_matches(matches, query_run.query)


    # Merge matches with a zero max distance, e.g. contiguous or overlapping
    # with matches to the same rule
    from licensedcode.match import merge_matches
    matches = merge_matches(matches, max_dist=0)

    # extend matched fragments left and right. We group by rule
    from licensedcode.seq import extend_match

    rules_by_rid = idx.rules_by_rid
    tids_by_rid = idx.tids_by_rid
    len_legalese = idx.len_legalese

    alo = qbegin = query_run.start
    ahi = query_run.end
    query = query_run.query
    qtokens = query.tokens
    matchables = query_run.matchables

    frag_matches = []

    keyf = lambda m: m.rule.rid
    matches.sort(key=keyf)
    matches_by_rule = groupby(matches, key=keyf)

    for rid, rule_matches in matches_by_rule:
        itokens = tids_by_rid[rid]
        blo, bhi = 0, len(itokens)
        rule = rules_by_rid[rid]

        for match in rule_matches:
            i, j , k = match.qstart, match.istart, match.len()
            # extend alignment left and right as long as we have matchables
            qpos, ipos, mlen = extend_match(
                i, j, k, qtokens, itokens,
                alo, ahi, blo, bhi, matchables)

            qspan = Span(range(qpos, qpos + mlen))
            ispan = Span(range(ipos, ipos + mlen))
            hispan = Span(p for p in ispan if itokens[p] < len_legalese)
            match = LicenseMatch(rule, qspan, ispan, hispan, qbegin,
                matcher=MATCH_AHO_FRAG, query=query)
            frag_matches.append(match)

    # Merge matches as usual
    matches = merge_matches(matches)

    return frag_matches


def add_start(automaton, tids, rule_identifier, rule_length):
    """
    Add the `tids` sequence of starting token ids for the `rule_identifier` Rule
    or `rule_length` to the an Aho-Corasick `automaton`.
    """
    # the value for a trie key is list of (rule identifier, rule_length)
    tokens = array('h', tids).tostring()
    existing = automaton.get(tokens, None)
    value = rule_length, rule_identifier
    if existing:
        existing.append(value)
    else:
        automaton.add_word(tokens, [value])


def finalize_starts(automaton):
    for values in automaton.values():
        values.sort(reverse=True)
    automaton.make_automaton()


def get_matched_starts(tokens, qbegin, automaton, len_start=SMALL_RULE):
    """
    Yield tuples of matched positions as (qstart, [(rule_length, rule_id), ...).
    Match `tokens` sequence of token ids starting at the `qbegin` absolute query
    start position position using the `automaton`.
    """
    for qend, values in get_matches(tokens, qbegin, automaton):
        qstart = qend - len_start
        yield qstart, values
