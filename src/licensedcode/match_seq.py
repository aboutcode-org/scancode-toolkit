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


from licensedcode.match import get_texts
from licensedcode.match import LicenseMatch
from licensedcode.seq import match_blocks
from licensedcode.spans import Span

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
Matching strategy using pair-wise multiple local sequences alignment and diff-
like approaches.
"""

MATCH_SEQ = '3-seq'

def match_sequence(idx, candidate, query_run, start_offset=0):
    """
    Return a list of LicenseMatch by matching the `query_run` tokens sequence
    against the `idx` index for the `candidate` rule tuple (rid, rule,
    intersection).
    """
    if not candidate:
        return []

    rid, rule, _intersection = candidate
    high_postings = idx.high_postings_by_rid[rid]
    itokens = idx.tids_by_rid[rid]

    len_junk = idx.len_junk

    qbegin = query_run.start + start_offset
    qfinish = query_run.end
    qtokens = query_run.query.tokens

    matches = []
    qstart = qbegin
    qlen = len(query_run)

    # match as long as long we find alignments and have high matchable tokens
    # this allows to find repeated instances of the same rule in the query run

    query_run_matchables = query_run.matchables
    while qstart <= qfinish:
        if not query_run_matchables:
            break
        block_matches = match_blocks(qtokens, itokens, qstart, qlen, high_postings, len_junk, query_run_matchables)
        if not block_matches:
            break
        if TRACE2:
            logger_debug('block_matches:')
            for m in block_matches:
                i, j, k = m
                print(m)
                print('qtokens:', ' '.join(idx.tokens_by_tid[t] for t in qtokens[i:i + k]))
                print('itokens:', ' '.join(idx.tokens_by_tid[t] for t in itokens[j:j + k]))

        # create one match for each matching block: this not entirely correct
        # but this will be sorted out at LicenseMatch merging and filtering time
        for qpos, ipos, mlen in block_matches:
            qspan = Span(range(qpos, qpos + mlen))
            iposses = range(ipos, ipos + mlen)
            hispan = Span(p for p in iposses if itokens[p] >= len_junk)
            ispan = Span(iposses)
            match = LicenseMatch(rule, qspan, ispan, hispan, qbegin, MATCH_SEQ)
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
            qstart = max([qstart, qspan.end + 1])

    if TRACE: map(logger_debug, matches)
    return matches
