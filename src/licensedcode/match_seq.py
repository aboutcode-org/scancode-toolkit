#
# Copyright (c) 2016 nexB Inc. and others. All rights reserved.
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

from __future__ import absolute_import, division, print_function

from licensedcode.seq import SequenceMatcher

from licensedcode.match import LicenseMatch
from licensedcode.match import get_texts
from licensedcode.whoosh_spans.spans import Span
from licensedcode import MAX_DIST


TRACE = False
TRACE2 = False

def logger_debug(*args): pass

if TRACE:
    import logging
    import sys

    logger = logging.getLogger(__name__)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, basestring) and a or repr(a) for a in args))

    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

"""
Matching strategy using pair-wise sequences matching with difflib.SequenceMatcher.
"""


# FIXME: MATCH_SEQ_TYPE = 'seq'
MATCH_SEQ_TYPE = 'lcsseq'


def index_smatchers(tids_by_rid, len_junk):
    """
    Return a list of sequence matcher, one for each rule. 
    """
    return [SequenceMatcher(tokens, len_junk) for tokens in tids_by_rid]


def match_sequence(idx, candidate, query_run, max_dist=MAX_DIST):
    """
    Return a list of LicenseMatch by matching the `query_run` tokens sequence
    against the `idx` index for the `candidate` rule tuple (rid, rule, intersection).
    """
    if not candidate:
        return []

    rid, rule, intersection = candidate
    smatcher = idx.smatchers_by_rid[rid]
    itokens = idx.tids_by_rid[rid]

    len_junk = idx.len_junk
    line_by_pos = query_run.line_by_pos

    qbegin = query_run.start
    qfinish = query_run.end
    qtokens = query_run.query.tokens
    high_matchables = query_run.high_matchables

    get_matching_blocks = smatcher.get_matching_blocks
    matches = []
    # match this rule as long as long we find alignments and are matchable
    qstart = qbegin
    while qstart <= qfinish:
        if not high_matchables:
            break
        smatches = get_matching_blocks(qtokens, starta=qstart, matchables=query_run.matchables)
        if not smatches:
            break
        if TRACE2:
            logger_debug('smatches:')
            for m in smatches:
                i, j, k = m
                print(m)
                print('qtokens:', ' '.join(idx.tokens_by_tid[t] for t in qtokens[i:i + k]))
                print('itokens:', ' '.join(idx.tokens_by_tid[t] for t in itokens[j:j + k]))

        # create one match for each smatch
        for qpos, ipos, mlen in smatches:
            qspan = Span(range(qpos, qpos + mlen))
            iposses = range(ipos, ipos + mlen)
            hispan = Span(p for p in iposses if itokens[p] >= len_junk)
            ispan = Span(iposses)
            match = LicenseMatch(rule, qspan, ispan, hispan, line_by_pos, qbegin, MATCH_SEQ_TYPE)
            if TRACE2:
                qt, it = get_texts(match, location=query_run.query.location, query_string=query_run.query.query_string, idx=idx)
                print('###########################')
                print(match)
                print('###########################')
                print(qt)
                print('###########################')
                print(it)
                print('###########################')
            matches.append(match)
            query_run.subtract(qspan)
            qstart = max([qstart, qspan.end +1])

    matches = LicenseMatch.merge(matches, max_dist=max_dist)
    if TRACE: map(logger_debug, matches)
    return matches
