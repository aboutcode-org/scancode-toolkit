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

from collections import deque
from itertools import combinations
from itertools import groupby

from licensedcode.whoosh_spans.spans import Span

from licensedcode import MAX_GAP
from licensedcode import MIN_LENGTH

from licensedcode.match import LicenseMatch


"""
Matching strategy using the inverted index.

The concepts used here are:
 - inverted index: a mapping of token_id-> postings.

 - postings: positional postings list in the inverted index for a token_id as a
   mapping of rule_id-> list of absolute positions in a rule for a token.

 - vector: query vector is a sparse list where the list index is token id and
   each item is a list of absolute positions where a token is found in a query.

 - hit: tuple of matched index and query positions for a given rule as (1,2,)
 - hit group: group of closely related hits in a list as [(1,2,), (2,3,) ...]
 - span group: like a hit group but using Span objects with a start and end.

 - match: object associating together the matched span groups for index and
   query positions, the matched rule, scores, etc..

 - bridging: when two hits (or spans) are separated by up to a certain number of
   unmatched tokens, bridging consist in merging these in a single hit or span.

By convention tuples of query and index positions are always stored in this
order: (query, index) with variable names prefixed with q and i. This applies to
hits and spans.
"""


# debug flags
DEBUG = False
DEBUG_DEEP = False

def logger_debug(*args): pass

def logger_debug_deep(*args): pass

if DEBUG or DEBUG_DEEP:
    import logging
    import sys

    logger = logging.getLogger(__name__)
    # logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, basestring) and a or repr(a) for a in args))

    if DEBUG_DEEP:
        def logger_debug_deep(*args):
            return logger.debug(' '.join(isinstance(a, basestring) and a or repr(a) for a in args))


MATCH_TYPE = 'inverted'


def match_inverted(idx, candidates, query_run, max_dist=MAX_GAP, dilate=5):
    """
    Return a sequence of LicenseMatch by matching the file at `location` or the
    `query` text string against the `idx` LicenseIndex. Only include matches
    with scores greater or equal to `min_score`. 
    
    The matching is done in two steps: first a match is done using only the high
    token ids (aka. good tokens). Second, based on the matched rules, the low
    token ids (aka. junk tokens are re-injected in the matches only for matched
    rules.

    Use a larger max_dist for the first step to allow larger discontinuities in
    matches. When we re-inject the junk tokens from the posting lists only for
    the matched rules we also only consider for closely positioned junk wrt. to
    actual matches: either junk contained in matched spans or just before and
    after, ignoring other junk that is further away or out sequence.

    The rationale is that some very frequent junk tokens have postings lists
    that are 100K long. By only considering junk in the second matching step, we
    avoid processing these large lists that do not contribute to the matching
    accuracy.
    """
    len_junk = idx.len_junk
    query_run_vector=query_run.vector()
    matches = []
    # We proceed in order of higher scored rule in the filtering steps one rule
    # at a time
    # TODO: stop early if we have consumed all the query.
    logger_debug('match_inverted: start')
    for rid in candidates:
        if DEBUG: logger_debug('  match_inverted: processing candidate rid:', rid, idx.rules_by_rid[rid].identifier())

        rule = idx.rules_by_rid[rid]
        rule_postings = idx.postings_by_rid[rid]

        # collect hits for ALL tokens
        good_hits = list(get_rule_hits(query_run_vector, rule_postings, len_junk=len_junk, high_tokens=True))
        logger_debug('  match_inverted: good_hits:', good_hits)
        if not good_hits:
            continue

        hits_groups = group_hits(good_hits, max_dist=max_dist)
        rule_matches = list(build_matches(hits_groups, rule, query_run.line_by_pos, _type=MATCH_TYPE))

        if DEBUG: logger_debug('  match_inverted: rule_matches from good hits #', len(rule_matches))
        if DEBUG_DEEP: [logger_debug('   ', m) for m in rule_matches]

#         # discard spurious matches
#
#         rule_matches, discarded = filter_short_matches(rule_matches, min_length=min_length)
#         print('%%%%%%%%%%%%%%%%%%%%%%%%% INV1', discarded)
#         discarded_matches.extend(discarded)
#
#         logger_debug('  match_inverted: rule_matches after filter_short_matches#', len(rule_matches))
#         if DEBUG: [logger_debug('   ', m) for m in rule_matches]
#
#         # discard very sparse matches
#         rule_matches, discarded = filter_sparse_matches(rule_matches, min_density=min_density)
#         print('%%%%%%%%%%%%%%%%%%%%%%%%% INV2', discarded)
#         discarded_matches.extend(discarded)
#
#         logger_debug('  match_inverted: rule_matches after filter_sparse_matches:', min_density, '#', len(rule_matches))
#         if DEBUG: [logger_debug('   ', m) for m in rule_matches]

        # collect hits for junk tokens
        rule_matches = reinject_hits_for_rule(rule_matches, query_run, rule, rule_postings, len_junk, dilate=dilate, high_tokens=False)

#         logger_debug('  match_inverted: matches with junk reinjected #', len(rule_matches))
#         if DEBUG: [logger_debug('   ', m) for m in rule_matches]
#
#         logger_debug('  match_inverted: rule_matches after discarding low score #', len(rule_matches))
#         if DEBUG: [logger_debug('   ', m) for m in rule_matches]
#
#         logger_debug_deep('  match_inverted: updated rule_matches for rid:', rid, ' at step2:', len(rule_matches))
#         if DEBUG: [logger_debug('   ', m) for m in rule_matches]
        matches.extend(rule_matches)

    logger_debug('  match_inverted: accumulated matches #', len(matches))
    if DEBUG: [logger_debug('   ', m) for m in matches]
    return matches


def reinject_hits_for_rule(rule_matches, query_run, rule, rule_postings, len_junk, dilate, high_tokens=False):
    """
    Iterate matches for a single rule and re-inject relevant high or low (junk)
    tokens in these matches updating matches in-place.
    """
    logger_debug('    reinject_hits_for_rule: adding junk back')
    junk_hits = list(get_rule_hits(query_run.vector(), rule_postings, len_junk, high_tokens))

    coeff = rule.length if rule.length <= MIN_LENGTH else 10
    actual_dilate = min([dilate, int(rule.length / coeff)])
    logger_debug('    reinject_hits_for_rule: dilate:', dilate, 'actual_dilate:', actual_dilate)

    for match in rule_matches:
        # TODO: optimize if we have a 100% match we could just append and continue
        # logger_debug_deep('   reinject_hits: processing match for junk q/ispans  :', match.qspans, '##', match.ispans)
        # logger_debug_deep('   reinject_hits: processing match for junk:', match)

        relevant_junk_hits = list(collect_reinjectable_hits(junk_hits, match, dilate=actual_dilate))

        if not relevant_junk_hits:
            logger_debug_deep('    reinject_hits: no relevant_junk_hits')
            continue

        # build a 'fake' match from junk
        junk_match = build_match(relevant_junk_hits, rule, query_run.line_by_pos, _type=MATCH_TYPE)

        # logger_debug_deep('    reinject_hits: about to inject relevant_junk_hits:', junk_match)
        # logger_debug_deep('    reinject_hits: about to inject relevant_junk_hits:', junk_match.qspans, '##', junk_match.ispans)

        # update in place the match with junk tokens
        match = match.update(junk_match)

        # logger_debug_deep('     reinject_hits: created combined match q/ispans  :', match.qspans, '##', match.ispans)
        # logger_debug_deep('     reinject_hits: created combined match  :', match)
    return rule_matches


def reinject_hits(matches, query_run, rules_by_rid, postings_by_rid, len_junk, dilate, high_tokens):
    """
    Iterate arbitrary matches and re-inject relevant tokens (only high_tokens if high_tokens
    is True) in these matches, updating matches in-place.
    """
    if not matches:
        return matches
    matches = sorted(matches, key=lambda m: m.rule.rid)
    # only merge for now matches with the same rule
    # iterate on matches grouped by rule, one rule at a time.
    for rid, rule_matches in groupby(matches, key=lambda m: m.rule.rid):
        rule_matches = list(rule_matches)
        rule = rules_by_rid[rid]
        rule_postings = postings_by_rid[rid]
        reinject_hits_for_rule(rule_matches, query_run, rule, rule_postings, len_junk, dilate, high_tokens)
    return matches


def get_rule_hits(qvector, rule_postings, len_junk, high_tokens=True):
    """
    Return an iterable of matched [ (qpos, ipos, ), ...] collected for a query
    vector from an inverted index rule postings for a single rule.
    Collect hits only for good high token ids if high_tokens is True.
    if high_tokens is False, collect hits only for low (junk) token ids.
    """

    if high_tokens:
        qvector = qvector[len_junk:]
    else:
        qvector = qvector[:len_junk]

    rule_postings_get = rule_postings.get

    # offset fir token ids if not considering junk
    tid_offset = len_junk if high_tokens else 0

    # collect matching aligned positions
    for tid, qpostings in enumerate(qvector, tid_offset):
        if not qpostings:
            continue

        ipostings = rule_postings_get(tid)
        if not ipostings:
            continue

        for qpos in qpostings:
            for ipos in ipostings:
                yield qpos, ipos


def get_hits_spans(hits):
    """
    Return qspan and ispan for an iterable of hits [(qpos, ipos, ), ...].
    """
    qposs, iposs = zip(*hits)
    return Span(qposs), Span(iposs)


def get_rule_hits_in_spans(hits, qspan, ispan):
    """
    Return a filtered iterable of hits [(qpos, ipos, ), ...] keeping only hits
    whose positions are in the provided qspan and ispan.
    """
    qrs = qspan.start
    qre = qspan.end
    irs = ispan.start
    ire = ispan.end
    for qpos, ipos in hits:
        if qrs <= qpos <= qre and irs <= ipos <= ire:
            yield qpos, ipos


def collect_reinjectable_hits(hits, match, dilate=11):
    """
    Return an iterable of hits [ (qpos, ipos, ), ...] collected for the junk
    portion of a query collecting only these that are inside dilated matched
    spans.
    """
    qspan = match.qspan
    dqrs = qspan.start - dilate
    dqre = qspan.end + dilate

    ispan = match.ispan
    dirs = ispan.start - dilate
    dire = ispan.end + dilate

    for qpos, ipos in hits:
        if dqrs < qpos < dqre  and dirs < ipos < dire:
            yield qpos, ipos


def group_hits(hits, max_dist):
    """
    Return a list of list as [[(qpos, ipos), ..], [....]]
    where the hits have been grouped based on their increasing sequence and a
    separation by up to a max_dist distance.
    """
    logger_debug('group_hits: start....')

    # list of groups. Each group is a list of (qpos, ipos) tuple
    hits_groups = []
    hits_groups_append = hits_groups.append

    hits_not_grouped = sorted(hits, key=lambda x: (x[1], x[0]))

    while hits_not_grouped:
        hits_group, hits_not_grouped = progressive_group_hits(hits_not_grouped, max_dist)
        logger_debug('group_hits: hits_groups, hits_not_grouped:', hits_groups, hits_not_grouped)
        hits_groups_append(hits_group)

    logger_debug('group_hits: collected hits_groups:', hits_groups)
    filtered_hits_groups = filter_contained_groups(hits_groups)
    logger_debug('group_hits:filtered groups:', filtered_hits_groups)
    return filtered_hits_groups


def progressive_group_hits(hits, max_dist):
    """
    Return a hits_group and the remaining hits list that could not be grouped
    with that group. Grouping in based on increasing sequence and a separation
    by up to a max_dist distance.
    """
    if not hits:
        return [], []

    # first hit is initial group
    first_hit = hits[0]
    tail_qpos, tail_ipos = first_hit

    hits_grouped = [first_hit]
    hits_grouped_append = hits_grouped.append

    hits_not_grouped = []
    hits_not_grouped_append = hits_not_grouped.append

    for qpos, ipos in hits[1:]:
        # Check tail for query position being in sequence
        # TODO: also check for large gaps
        if tail_qpos < qpos and tail_ipos < ipos and qpos - tail_qpos < max_dist and ipos - tail_ipos < max_dist:
            hits_grouped_append((qpos, ipos,))
            tail_qpos, tail_ipos = qpos, ipos
        else:
            hits_not_grouped_append((qpos, ipos,))

    return hits_grouped, hits_not_grouped


def filter_contained_groups(hits_groups):
    """
    Given a hits_groups list of list of (qpos, ipos) tuples, return a new list
    where groups whose qpos are contained in another group have been discarded.
    """
    # TODO: OPTIMIZE: these multiple loops are likely very inefficient
    # TODO: OPTIMIZE: we should use Spans earlier and here instead

    logger_debug('filter_contained_groups: start....')

    # decorate each hit group query positions with a group id as a tuple of (gid, set(all qpos))
    qset_hit_groups = [(gid, set([q for q, _i in group])) for gid, group in enumerate(hits_groups)]

    contained = set()
    contained_add = contained.add
    # first pass: group entirely contained in a single group
    # pairwise exploration:
    # FIXME: we are or should be sorted use current and next approach similar to Spam.merge
    for qs_group1, qs_group2 in combinations(qset_hit_groups, 2):
        gid1, qset1 = qs_group1
        gid2, qset2 = qs_group2
        if gid1 in contained or gid2 in contained:
            # logger_debug(' filter_contained_groups: gid1 in contained or gid2 in contained:', gid1, gid1 in contained, gid1, gid2 in contained)
            # do not examine a pair where one side has been found as being contained
            continue
        if qset2.issubset(qset1):
            # all g2 positions are in g1
            contained_add(gid2)
        elif qset1.issubset(qset2):
            # all g1 positions are in g2
            contained_add(gid1)

    # second pass: groups with all their qpos contained in the rest of all other groups qpos
    # one against all-minus-self exploration
    remainder = [(gid, qset) for gid, qset in qset_hit_groups if gid not in contained]
    for gid1, qset1 in remainder:
        if gid1 in contained:
            continue

        all_others = ((gid, qset) for gid, qset in remainder if gid != gid1 and gid not in contained)
        all_other_qset = set()
        for gid2, qset2 in all_others:
            all_other_qset.update(qset2)
        if qset1.issubset(all_other_qset):
            contained_add(gid1)

    # third pass: groups with overlapping leading positions contained another groups are truncated
    remaning_groups = list(enumerate(group for gid, group in enumerate(hits_groups) if gid not in contained))
    contained = set()
    # pairwise exploration
    for gid_group1, gid_group2 in combinations(remaning_groups, 2):
        gid1, group1 = gid_group1
        gid2, group2 = gid_group2
        if gid1 in contained or gid2 in contained:
            continue

        # compare the smallest of the two groups to the largest
        lg1, lg2 = len(group1), len(group2)
        if lg1 >= lg2:
            longest = group1
            shortest = group2
        else:
            longest = group2
            shortest = group1

        # compare shortest to longest and build a truncated new group removing overlaps
        qset1 = set(q for q, _i in longest)
        leading_overlap = 0
        new_group = deque(shortest)
        while new_group:
            head2qpos, _head2ipos = new_group[0]
            if head2qpos in qset1:
                _discarded = new_group.popleft()
                leading_overlap += 1
            else:
                break

        if not new_group:
            contained_add(gid2)
        else:
            for _i in range(leading_overlap):
                shortest.pop(0)

    return [group for gid, group in remaning_groups if gid not in contained]


def build_match(hits, rule, line_by_pos, _type=None):
    """
    Return a match from a hits list, a rule and a mapping of qpos -> line
    numbers.
    """
    qhits, ihits = zip(*hits)
    return LicenseMatch(rule, Span(qhits), Span(ihits), line_by_pos, _type=_type)


def build_matches(hit_groups, rule, line_by_pos, _type=MATCH_TYPE):
    """
    Return an iterable of (rid, list of matches) built from hit groups for a rule
    and line_by_pos mapping of qpos -> line numbers. One match is created for each hit group.
    """
    for hit_group in hit_groups:
        yield build_match(hit_group, rule, line_by_pos, _type)
