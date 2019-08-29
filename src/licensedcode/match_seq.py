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

from time import time
import sys

from six import string_types

from licensedcode.match import LicenseMatch
from licensedcode.spans import Span


TRACE = False
TRACE2 = False
TRACE3 = False


def logger_debug(*args): pass


if TRACE or TRACE2 or TRACE3:
    import logging

    logger = logging.getLogger(__name__)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, string_types) and a or repr(a) for a in args))

    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

"""
Matching strategy using pair-wise multiple local sequences alignment and diff-
like approaches.
"""

MATCH_SEQ = '3-seq'


def match_sequence(idx, rule, query_run, high_postings, start_offset=0,
                   match_blocks=None, deadline=sys.maxsize):
    """
    Return a list of LicenseMatch by matching the `query_run` tokens sequence
    starting at `start_offset` against the `idx` index for the candidate `rule`.
    Stop processing when reachin the deadline time.
    """
    if not rule:
        return []

    if not match_blocks:
        from licensedcode.seq import match_blocks

    rid = rule.rid
    itokens = idx.tids_by_rid[rid]

    len_legalese = idx.len_legalese

    qbegin = query_run.start + start_offset
    qfinish = query_run.end
    qtokens = query_run.query.tokens
    query = query_run.query

    matches = []
    qstart = qbegin

    # match as long as long we find alignments and have high matchable tokens
    # this allows to find repeated instances of the same rule in the query run

    while qstart <= qfinish:

        if TRACE2:
            logger_debug('\n\nmatch_seq:==========================LOOP=============================')

        if not query_run.is_matchable(include_low=False):
            break

        if TRACE2:
            logger_debug('match_seq:running block_matches:', 'a_start:', qstart, 'a_end', qfinish + 1)


        block_matches = match_blocks(
            a=qtokens, b=itokens, a_start=qstart, a_end=qfinish + 1,
            b2j=high_postings, len_good=len_legalese,
            matchables=query_run.matchables)

        if not block_matches:
            break

        # create one match for each matching block: they will be further merged
        # at LicenseMatch merging and filtering time

        for qpos, ipos, mlen in block_matches:

            qspan_end = qpos + mlen
            # skip single non-high word matched as as sequence
            if mlen > 1 or (mlen == 1 and qtokens[qpos] < len_legalese):
                qspan = Span(range(qpos, qspan_end))
                ispan = Span(range(ipos, ipos + mlen))
                hispan = Span(p for p in ispan if itokens[p] < len_legalese)
                match = LicenseMatch(
                    rule, qspan, ispan, hispan, qbegin,
                    matcher=MATCH_SEQ, query=query)
                matches.append(match)

                if TRACE2:
                    from licensedcode.tracing import get_texts
                    qt, it = get_texts(match)
                    logger_debug('###########################')
                    logger_debug(match)
                    logger_debug('###########################')
                    logger_debug(qt)
                    logger_debug('###########################')
                    logger_debug(it)
                    logger_debug('###########################')

            qstart = max([qstart, qspan_end])

            if time() > deadline:
                break

        if time() > deadline:
            break

    if TRACE:
        logger_debug('match_seq: FINAL LicenseMatch(es)')
        for m in matches:
            logger_debug(m)
        logger_debug('\n\n')

    return matches
