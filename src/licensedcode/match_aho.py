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

from licensedcode.match import LicenseMatch
from licensedcode.spans import Span

"""
Matching strategy for exact matching using Aho-Corasick automatons.
"""

# Set to False to enable debug tracing
TRACE = False

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


def index_aho(tids_by_rid):
    """
    Return an Aho-Corasick automaton for a list of `tids_by_rid` tid arrays.
    """
    import ahocorasick
    auto = ahocorasick.Automaton(ahocorasick.STORE_INTS)
    for rid, tokens in enumerate(tids_by_rid):
        auto.add_word(tokens.tostring(), rid)
    auto.make_automaton()
    return auto


def exact_match(idx, query_run, automaton, rules_subset=None):
    """
    Return a list of exact LicenseMatch by matching the `query_run` against
    the `automaton` and `idx` index.
    Only return matches for a rule id present in rules_subset if provided.
    """
    MATCH_TYPE = 'aho'

    if TRACE: logger_debug(' #exact: start ... ')

    len_junk = idx.len_junk
    rules_by_rid = idx.rules_by_rid

    qtokens = query_run.tokens
    qbegin = query_run.start
    query_run_matchables = query_run.matchables
    line_by_pos = query_run.line_by_pos

    qtokens_as_str = array('h', qtokens).tostring()
    matches = []
    for qend, rid in automaton.iter(qtokens_as_str):
        if rules_subset and rid not in rules_subset:
            continue

        rule = rules_by_rid[rid]
        len_rule = rule.length

        # FIXME: use a trie of ints or a trie or Unicode characters to avoid this shenaningan
        
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
        if real_qend != int(real_qend):
            continue

        real_qend = int(real_qend)
        qposses = range(qbegin + real_qend - len_rule + 1, qbegin + real_qend + 1)

        if any(p not in query_run_matchables for p in qposses):
            if TRACE: logger_debug('   #exact: not matchable match')
            continue

        qspan = Span(qposses)
        ispan = Span(range(len_rule))

        itokens = idx.tids_by_rid[rid]
        hispan = Span(p for p in ispan if itokens[p] >= len_junk)

        match = LicenseMatch(rule, qspan, ispan, hispan, line_by_pos, query_run.start, MATCH_TYPE)
        matches.append(match)

    if TRACE and matches: logger_debug(' ##small exact: matches found#', matches)

    return matches
