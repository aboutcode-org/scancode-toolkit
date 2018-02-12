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

from __future__ import print_function, absolute_import, division

from array import array

import ahocorasick

from licensedcode.match import LicenseMatch
from licensedcode.spans import Span

"""
Matching strategy for exact matching using Aho-Corasick automatons.
"""

# Set to False to enable debug tracing
TRACE = False
TRACE_DEEP = False

if TRACE:
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


def add_sequence(automaton, tids, rid, start=0):
    """
    Add the `tids` sequence of token ids for the `rid` Rule id starting at `start`
    position to the an Aho-Corasick `automaton`.
    """
    end = len(tids) - 1
    tokens = array('h', tids).tostring()
    existing = automaton.get(tokens, None)
    # the value for a trie key is a set of tuples (rule id, start position, end position)
    value = rid, start, start + end
    if existing:
        # ensure that for identical strings added several times, all rid/pos are
        # added to the value set
        existing.add(value)
    else:
        automaton.add_word(tokens, set([value]))


MATCH_AHO_EXACT = '2-aho'
MATCH_AHO_FRAG = '5-aho-frag'


def exact_match(idx, query_run, automaton):
    """
    Return a list of exact LicenseMatch by matching the `query_run` against
    the `automaton` and `idx` index.
    """
    if TRACE: logger_debug(' #exact_AHO: start ... ')
    if TRACE_DEEP: logger_debug(' #exact_AHO: query_run:', query_run)

    len_junk = idx.len_junk
    rules_by_rid = idx.rules_by_rid

    qtokens = query_run.tokens
    qbegin = query_run.start
    query_run_matchables = query_run.matchables
    query = query_run.query

    qtokens_as_str = array('h', qtokens).tostring()
    matches = []

    # iterate over matched strings: the matched value is (rule id, index start pos, index end pos)
    for qend, matched_rule_segments in automaton.iter(qtokens_as_str):

        for rid, istart, iend in matched_rule_segments:
            rule = rules_by_rid[rid]
            if TRACE_DEEP: logger_debug('   #exact_AHO: found match to rule:', rule.identifier)

            ################################
            # FIXME: use a trie of ints or a trie or Unicode characters to avoid this shenaningan
            ################################
            # Since the Tries stores bytes and we have two bytes per tokenid, the
            # real end must be adjusted
            real_qend = (qend - 1) / 2
            # ... and there is now a real possibility of a false match.
            # For instance say we have these tokens :
            #   gpl encoded as 0012 and lgpl encoded as 1200 and mit as 2600
            # And if we scan this "mit lgpl" we get this encoding 2600 1200.
            # The automaton will find a matched string  of 0012 to gpl in the middle
            # matching falsely so we check that the corrected end qposition
            # must be always an integer.
            real_qend_int = int(real_qend)
            if real_qend != real_qend_int:
                if TRACE: logger_debug('   #exact_AHO: real_qend != int(real_qend), discarding rule match:', rule.identifier)
                continue

            match_len = iend + 1 - istart
            matcher = match_len == rule.length and MATCH_AHO_EXACT or MATCH_AHO_FRAG

            real_qend = real_qend_int
            qposses = range(qbegin + real_qend - match_len + 1, qbegin + real_qend + 1)

            if any(p not in query_run_matchables for p in qposses):
                if TRACE: logger_debug(
                    '   #exact_AHO: not matchable match: '
                    'any(p not in query_run_matchables for p in qposses), discarding rule:',
                    rule.identifier)
                continue

            qspan = Span(qposses)
            ispan = Span(range(istart, iend + 1))

            itokens = idx.tids_by_rid[rid]
            hispan = Span(p for p in ispan if itokens[p] >= len_junk)

            match = LicenseMatch(rule, qspan, ispan, hispan, qbegin, matcher=matcher, query=query)
            matches.append(match)

    if TRACE and matches:
        logger_debug(' ##exact_AHO: matches found#', matches)
        map(print, matches)

    return matches
