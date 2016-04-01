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

from __future__ import absolute_import, division, print_function

from collections import defaultdict
from itertools import groupby
from operator import itemgetter

from licensedcode.difflib2 import SequenceMatcher
from licensedcode.whoosh_spans.spans import Span

from licensedcode.match import EXACT_MATCH_SCORE
from licensedcode.match import LicenseMatch
from licensedcode.query import Query

"""
Matching strategy using pair-wise sequences matching with difflib.SequenceMatcher
"""

# debug flags: set to True for temp debug tracing
DEBUG1 = False
DEBUG_FILTER = False
DEBUG_PERF = False


def build_seq_matchers(rules_tokens):
    """
    Return a list od sequence matcher, one for each rule. 
    """
    return [SequenceMatcher(b=rule_toks) for rule_toks in rules_tokens]


def match_rules_seq(idx, query_run):
    """
    Match the query_run QueryRun against every rule matcher.
    Return tuples of hits as (rid, matched ispan, matched qspan).
    These tuples are guaranteed to be returned:
    - in increasing rule id
    - in increasing query position for a given rule id
    """
    if not idx.rule_seq_matchers:
        # build and cache sequence matchers
        rule_seq_matchers = build_seq_matchers(idx.rules_tokens)
        idx.rule_seq_matchers = rule_seq_matchers

    # TODO: OPTIMIZE consider sorted rules based on length or else

    # OPTIMIZED : bound to local scope because used frequently
    from licensedcode.whoosh_spans.spans import Span  # @Reimport

    # OPTIMIZED : bound to local scope because used frequently
    start_qpos = query_run.start

    for rid, matcher in enumerate(idx.rule_seq_matchers):
        """
        FIXME: THIS CANNOT WORK to match repeated texts more than once. We might
        need to split the text in areas first based on some index matching.

        Each triple is of the form (i, j, n), and means that a[i:i+n] ==
        b[j:j+n]. where a is the query and b the rule. The triples are
        monotonically increasing in i and in j which means that we may not
        match cases where the same rule text appears more than once in the
        query. The last triple is a dummy, (len(a), len(b), 0), and is the
        only triple with n==0.
        """
        #TODO: add run start offset
        matcher.set_seq1(query_run.tokens)
        for qpos, ipos, matched_len in matcher.get_matching_blocks():
            if matched_len == 0:
                continue
            # TODO: OPTIMIZE: arrays of in may be smaller and faster than Spans
            # restore the correct absolution position
            abs_qpos = start_qpos + qpos
            yield rid, Span(ipos, ipos + matched_len - 1), Span(abs_qpos, abs_qpos + matched_len - 1)

        # OPTIMIZED: finally, reset seq1 to avoid stuffing memory with query tokens
        matcher.set_seq1([])


def match_sequences(idx, location=None, query_string=None, min_score=100):
    """
    Return a sequence of LicenseMatch by matching the file at `location` or the
    `query` text string against the `idx` LicenseIndex. Only include matches
    with scores greater or equal to `min_score`.
    Use sequence alignment as a match strategy.
    """
    if DEBUG_FILTER or DEBUG1 or DEBUG_PERF:
        print()

    junk_runs = []
    exact_matches = []
    approx_hits = defaultdict(list)
    qry = Query(location, query_string, idx)
    for run in qry.query_runs():
        if DEBUG1:
            print('new run')
        if not run.matchable():
            junk_runs.append(run)
            continue
        for rid, spans in groupby(match_rules_seq(idx, run), key=itemgetter(0)):
            hits = ((ispan, qspan) for _, ispan, qspan in spans)
            for ispan, qspan in merge_hit_spans(hits):
                if DEBUG1:
                    print(' merged:', ispan, qspan)
                rule_last_pos = idx.rules_by_rid[rid].length - 1
                # is this an exact match with no gaps: i.e. a hit starting at 0 and ending at rule length?
                # FIXME : this cannot work now that we are broken in query runs
                if ispan.start == 0 and ispan.end == rule_last_pos:
                    rule = idx.rules[rid]
                    exact_matches.append(LicenseMatch(rule, qspan, ispan, EXACT_MATCH_SCORE, run.line_by_pos))
                else:
                    # TODO: is this an exact match with gaps? we cannot resolve this yet
                    # TODO:  else: this is an approximate match of sorts
                    approx_hits[rid].append((ispan, qspan, run.line_by_pos))

    if DEBUG1:
        print()
        print('  exact_matches:', exact_matches)
        print('  junk_runs:', junk_runs)
        print('  approx_hits:', approx_hits)

    ######################3
    # TODO: re-inject junk in Matches
    ######################3

    approx_matches = []
    if min_score < 100:
        # Approximate hits and matches

        # get remaining hits not part of exact hits
        # approx_hits = idx.approximate_hits(remaining_hits_by_rid)

        for rid, items in approx_hits.items():
            #current_rid_matches = []
            rule = idx.rulesd[rid]
            for ispan, qspan, line_by_pos in items:
                # process accumulated partial matches for the current rid
                # 1. compute some indication of how far apart these matches are gap-wise

                # 2. compute how much of an index doc qtokens these matches consume
                match_coverage = len(ispan) / rule.max_len()
                score = round(match_coverage * 100, 2)

                # 3. assemble a maximal span? (or later if we have no interspersed matches in between
                if min_score <= score:
                    approx_matches.append(LicenseMatch(rule, qspan, ispan, score, line_by_pos))

        # TODO: process last matches if any
        # same process as in if current_rid != rid, should be in a function

        # TODO: remove approx matches that could be inside gaps from exact matches

    # combine and filter all matches, sorted by query positions
    matches = sorted(exact_matches + approx_matches, key=lambda x: x.qspan)
    return matches


def merge_hit_spans(hit_spans):
    """
    Return an iterable of tuple of (index_span, query_span) Spans by merging
    when possible the contiguous Spans in an iterable of `hits`. Spans are
    merged if sequence of ispan and qspan can both be merged the same way.
    """
    prev_ispan = prev_qspan = None
    for ispan, qspan in hit_spans:
        # start of iteration
        if not prev_ispan:
            prev_ispan, prev_qspan = ispan, qspan
            continue

        # test contiguity between previous and current end of the previous hit and start of the current hit
        imerged, qmerged = Span.merge([prev_ispan, ispan]), Span.merge([prev_qspan, qspan])
        if imerged and qmerged:
            # we can keep the merges and keep merging more
            prev_ispan, prev_qspan = imerged, qmerged
        else:
            yield prev_ispan, prev_qspan
            prev_ispan, prev_qspan = ispan, qspan

    # process last group if any
    if prev_ispan and prev_qspan:
        yield prev_ispan, prev_qspan
