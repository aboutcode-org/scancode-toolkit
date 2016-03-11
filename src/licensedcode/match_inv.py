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

from collections import defaultdict
from collections import deque
from itertools import combinations
from itertools import groupby

from licensedcode.whoosh_spans.spans import Span

from licensedcode import MAX_GAP
from licensedcode import MIN_LENGTH

from licensedcode.match import build_match
from licensedcode.match import filter_sparse_matches
from licensedcode.match import filter_short_matches
from licensedcode.match import filter_low_scoring_matches


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


def match_inverted(idx, candidates, qvector, line_by_pos, min_score=100, max_dist=MAX_GAP, min_density=0.2, dilate=5, min_length=MIN_LENGTH):
    """
    Return a sequence of LicenseMatch by matching the file at `location` or the
    `query` text string against the `idx` LicenseIndex. Only include matches
    with scores greater or equal to `min_score`. 
    
    The matching is done in two steps: first a match is done using only the high
    token ids (aka. good tokens). Second, based on the matched rules, the low
    token ids (aka. junk tokens are reinjected in the matches only for matched
    rules.

    Use a larger max_dist for the first step to allow larger discontinuities in
    matches. When we reinject the junk tokens from the posting lists only for
    the matched rules we also only consider for closely positioned junk wrt. to
    actual matches: either junk contained in matched regions or just before and
    after, ignoring other junk that is further away or out sequence.

    The rationale is that some very frequent junk tokens have postings lists
    that are 100K long. By only considering junk in the second matching step, we
    avoid processing these large lists that do not contribute to the matching
    accuracy.
    """
    len_junk = idx.len_junk

    matches = []
    # We proceed in order of higher scored rule in the filtering steps one rule
    # at a time
    # TODO: stop early if we have consumed all the query.
    logger_debug('match_inverted: start')
    for distance, rid in candidates:
        logger_debug('  match_inverted: processing candidate rid:', rid, idx.rules_by_rid[rid].identifier(), 'with distance:', distance)

        rule = idx.rules_by_rid[rid]
        rule_postings = idx.postings_by_rid[rid]

        # collect hits for good tokens
        good_hits = list(get_rule_hits(qvector, rule_postings, len_junk=0, junk=False, _tokens_by_tid=idx.tokens_by_tid))
        if DEBUG: logger_debug('  match_inverted: rule_hits:', good_hits)

        if not good_hits:
            continue

        all_hits = sorted(good_hits, key=lambda x: (x[1], x[0]))
        if DEBUG: logger_debug('  match_inverted: all_hits:', all_hits)

        hits_by_rid = {rid: all_hits}

        hit_groups_by_rid = group_hits_by_rid(hits_by_rid, max_dist=max_dist, rules={rid: rule})

        # create matches for this rule
        rule_matches = list(build_matches(hit_groups_by_rid, {rid: rule}, line_by_pos, _type=MATCH_TYPE))

        logger_debug('  match_inverted: rule_matches from good hits #', len(rule_matches))
        if DEBUG: [logger_debug('   ', m) for m in rule_matches]

        # discard small matches
        rule_matches = filter_short_matches(rule_matches, min_length=min_length)
        logger_debug('  match_inverted: rule_matches after filter_short_matches#', len(rule_matches))
        if DEBUG: [logger_debug('   ', m) for m in rule_matches]

        # discard very sparse matches
        rule_matches = filter_sparse_matches(rule_matches, min_density=min_density)
        logger_debug('  match_inverted: rule_matches after filter_sparse_matches:', min_density, '#', len(rule_matches))
        if DEBUG: [logger_debug('   ', m) for m in rule_matches]

        # collect hits for junk tokens
        rule_matches = reinject_hits_for_rule(rule_matches, qvector, rule, rule_postings, len_junk, line_by_pos, dilate=dilate, junk=True)
        logger_debug('  match_inverted: matches with junk reinjected #', len(rule_matches))
        if DEBUG: [logger_debug('   ', m) for m in rule_matches]

        # discard low score matches
        rule_matches = filter_low_scoring_matches(rule_matches, min_score)
        logger_debug('  match_inverted: rule_matches after discarding low score #', len(rule_matches))
        if DEBUG: [logger_debug('   ', m) for m in rule_matches]

        logger_debug_deep('  match_inverted: updated rule_matches for rid:', rid, ' at step2:', len(rule_matches))
        if DEBUG: [logger_debug('   ', m) for m in rule_matches]
        matches.extend(m for m in rule_matches)

    logger_debug('  match_inverted: accumulated matches #', len(matches))
    if DEBUG: [logger_debug('   ', m) for m in matches]
    return matches


def reinject_hits_for_rule(rule_matches, qvector, rule, rule_postings, len_junk, line_by_pos, dilate, junk=True):
    """
    Iterate matches for a single rule and re-inject relevant junk tokens in
    these matches updating matches in-place.
    """
    logger_debug('    reinject_hits_for_rule: adding junk back')
    junk_hits = list(get_rule_hits(qvector, rule_postings, len_junk, junk))

    coeff = float(rule.length) if rule.length <= MIN_LENGTH else 10.0
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
        junk_match = build_match(relevant_junk_hits, rule, line_by_pos, _type=MATCH_TYPE)

        # logger_debug_deep('    reinject_hits: about to inject relevant_junk_hits:', junk_match)
        # logger_debug_deep('    reinject_hits: about to inject relevant_junk_hits:', junk_match.qspans, '##', junk_match.ispans)

        # update in place the match with junk tokens
        match = match.update(junk_match, merge_spans=True)

        # logger_debug_deep('     reinject_hits: created combined match q/ispans  :', match.qspans, '##', match.ispans)
        # logger_debug_deep('     reinject_hits: created combined match  :', match)
    return rule_matches


def reinject_hits(matches, qvector, rules_by_rid, postings_by_rid, len_junk, line_by_pos, dilate, junk):
    """
    Iterate arbitrary matches and re-inject relevant tokens (only junk if junk
    is True) in these matches, updating matches in-place.
    """
    matches = sorted(matches, key=lambda m: m.rule.rid)
    # only merge for now matches with the same rule
    # iterate on matches grouped by rule, one rule at a time.
    for rid, rule_matches in groupby(matches, key=lambda m: m.rule.rid):
        rule_matches = list(rule_matches)
        rule = rules_by_rid[rid]
        rule_postings = postings_by_rid[rid]
        reinject_hits_for_rule(rule_matches, qvector, rule, rule_postings, len_junk, line_by_pos, dilate, junk)
    return matches


def get_rule_hits(qvector, rule_postings, len_junk, junk=False, _tokens_by_tid=None):
    """
    Return an iterable of matched [ (qpos, ipos, ), ...] collected for a query
    vector from an inverted index rule postings for a single rule.
    Collect hits only for good high token ids if junk is False.
    if junk is True, collect hits only for junk low token ids.
    """
    if DEBUG_DEEP:
        if  _tokens_by_tid:
            logger_debug('    get_rule_hits: rule_postings:', {_tokens_by_tid[tid]: list(post) for tid, post in rule_postings.items()})
            logger_debug('    get_rule_hits: junk, qvector:', junk, [(_tokens_by_tid[tid], postings) for tid, postings in enumerate(qvector) if postings])
        else:
            logger_debug('    get_rule_hits: rule_postings:', rule_postings)
            logger_debug('    get_rule_hits: junk, qvector:', junk, [(tid, postings) for tid, postings in enumerate(qvector) if postings])

    if junk:
        qvector = qvector[:len_junk]
    else:
        qvector = qvector[len_junk:]

    rule_postings_get = rule_postings.get
    tid_offset = 0 if junk else len_junk
    # align positions
    for tid, qpostings in enumerate(qvector, tid_offset):
        if qpostings:
            ipostings = rule_postings_get(tid)
            if ipostings:
                for qpos in qpostings:
                    for ipos in ipostings:
                        # if  _tokens_by_tid:
                            # logger_debug('        get_rule_hits: found hit:', _tokens_by_tid[tid], qpos, ipos)
                        yield qpos, ipos


def get_hits_regions(hits):
    """
    Return qregion and iregion spans for an iterable of hits [(qpos, ipos, ), ...].
    """
    qposs, iposs = zip(*hits)
    return Span(min(qposs), max(qposs)), Span(min(iposs), max(iposs))


def get_rule_hits_in_regions(hits, qregion, iregion):
    """
    Return a filtered iterable of hits [(qpos, ipos, ), ...] keeping only hits
    whose positions are in the provided qregion and iregion spans.
    """
    qrs = qregion.start
    qre = qregion.end
    irs = iregion.start
    ire = iregion.end
    for qpos, ipos in hits:
        if qrs <= qpos <= qre and irs <= ipos <= ire:
            yield qpos, ipos


def collect_reinjectable_hits(hits, match, dilate=11):
    """
    Return an iterable of hits [ (qpos, ipos, ), ...] collected for the junk
    portion of a query collecting only these that are inside dilated matched
    regions.
    """
    qregion = match.qregion
    dqrs = qregion.start - dilate
    dqre = qregion.end + dilate
    # qspans_range = Span.ranges(match.qspans)

    iregion = match.iregion
    dirs = iregion.start - dilate
    dire = iregion.end + dilate
    # ispans_range = Span.ranges(match.ispans)

    for qpos, ipos in hits:
        if dqrs < qpos < dqre  and dirs < ipos < dire:  # and qpos not in qspans_range and ipos not in ispans_range:
            yield qpos, ipos


def group_hits_by_rid(hits_by_rid, max_dist, rules=None):
    """
    Return a mapping of rule_id -> list of list as [[(qpos, ipos), ..], [....]]
    where the hits have been grouped based on their increasing sequence and a
    separation by up to a max_dist distance.
    """
    # map of rid -> list of groups. Each group is a list of (qpos, ipos) tuple
    hit_groups_by_rid = defaultdict(list)

    logger_debug('group_hits_by_rid: start....')
    for rid, hits in hits_by_rid.items():
        hits_not_grouped = list(hits)
        rid_hit_groups = hit_groups_by_rid[rid]
        rid_hit_groups_append = rid_hit_groups.append
        # hits_group = []
        # perform progressive grouping 10 times
        # FIXME: why 10 times? why not doing progressive all the way until all
        # hits have been processed (with hits_not_grouped)?
        while hits_not_grouped:
            hits_group, hits_not_grouped = progressive_group_hits(hits_not_grouped, max_dist)
            # logger_debug('          group_hits_by_rid: hits_group, hits_not_grouped:', hits_group, hits_not_grouped)
            rid_hit_groups_append(hits_group)

        # logger_debug('          group_hits_by_rid: rid, rid_hit_groups         :', rid, rid_hit_groups)
        rid_hit_groups = filter_contained_groups(rid_hit_groups)
        hit_groups_by_rid[rid] = rid_hit_groups
        # logger_debug('          group_hits_by_rid: rid, filter_contained_groups:', rid, hit_groups_by_rid[rid])
    return dict(hit_groups_by_rid)


# @profile
def progressive_group_hits(hits, max_dist):
    """
    Return a hits_group and the remaining hits list that could not be grouped
    with that group. Grouping in based on increasing sequence and a separation
    by up to a max_dist distance.
    """

    # logger_debug('###################')
    # logger_debug('progressive_group_hits: start....')
    # logger_debug('progressive_group_hits: hits, max_dist....', hits, max_dist)

    if not hits:
        return [], []

    # first hit is initial group
    first_hit = hits[0]
    tail_qpos, tail_ipos = first_hit

    hits_group = [first_hit]
    hits_group_append = hits_group.append

    hits_not_grouped = []
    hits_not_grouped_append = hits_not_grouped.append

    # logger_debug(' progressive_group_hits1: tail_qpos, tail_ipos', tail_qpos, tail_ipos)
    # logger_debug(' progressive_group_hits1: hits_group', hits_group)
    # logger_debug(' progressive_group_hits1: hits_not_grouped', hits_not_grouped)
    # logger_debug()
    for qpos, ipos in hits[1:]:
        # Check tail for query position being in sequence
        # also check for large gaps
        if tail_qpos < qpos and tail_ipos < ipos and qpos - tail_qpos < max_dist and ipos - tail_ipos < max_dist:
            hits_group_append((qpos, ipos,))
            tail_qpos, tail_ipos = qpos, ipos
            # logger_debug('    progressive_group_hits2: tail_qpos, tail_ipos', tail_qpos, tail_ipos)
            # logger_debug('    progressive_group_hits2: hits_group', hits_group)
            # logger_debug('    progressive_group_hits2: hits_not_grouped', hits_not_grouped)
            # logger_debug()

            continue

        hits_not_grouped_append((qpos, ipos,))
        # logger_debug('    progressive_group_hits3: tail_qpos, tail_ipos', tail_qpos, tail_ipos)
        # logger_debug('    progressive_group_hits3: hits_group', hits_group)
        # logger_debug('    progressive_group_hits3: hits_not_grouped', hits_not_grouped)
        # logger_debug()

    # logger_debug('###################')

    return hits_group, hits_not_grouped


def filter_contained_groups(hit_groups):
    """
    Given a hit_groups as a list of list of (qpos, ipos) tuple, return a new
    list where groups whose qpos are contained in another group have been
    discarded.
    """
    # TODO: OPTIMIZE: these multiple loops are likely very inefficient
    # TODO: OPTIMIZE: we should use Spans earlier and here instead

    logger_debug('filter_contained_groups: start....')

    # decorate each hit group query positions with a group id as a tuple of (gid, set(all qpos))
    qset_hit_groups = [(gid, set([q for q, _i in group])) for gid, group in enumerate(hit_groups)]
    # logger_debug('filter_contained_groups: qset_hit_groups:', qset_hit_groups)

    contained = set()
    contained_add = contained.add
    # first pass: group entirely contained in a single group
    # pairwise exploration:
    # FIXME: we are or should be sorted use current and next approach similar to Spam.merge
    for qs_group1, qs_group2 in combinations(qset_hit_groups, 2):
        gid1, qset1 = qs_group1
        gid2, qset2 = qs_group2
        # logger_debug('filter_contained_groups: gid1, qset1:', gid1, qset1)
        # logger_debug('filter_contained_groups: gid2, qset2:', gid2, qset2)
        if gid1 in contained or gid2 in contained:
            # logger_debug(' filter_contained_groups: gid1 in contained or gid2 in contained:', gid1, gid1 in contained, gid1, gid2 in contained)
            # do not examine a pair where one side has been found as being contained
            continue
        if qset2.issubset(qset1):
            # all g2 positions are in g1
            # logger_debug(' filter_contained_groups: qset2.issubset(qset1):', gid2, qset2.issubset(qset1))
            contained_add(gid2)
        elif qset1.issubset(qset2):
            # all g1 positions are in g2
            # logger_debug(' filter_contained_groups: qset1.issubset(qset2):', gid1, qset1.issubset(qset2))
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
    remaning_groups = list(enumerate(group for gid, group in enumerate(hit_groups) if gid not in contained))
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


def build_matches(hit_groups_by_rid, rules, line_by_pos, _type=MATCH_TYPE):
    """
    Return an iterable of (rid, list of matches) built from hit groups, rules
    and qpos -> line numbers. One match is created for each hit group.
    """
    # Each list value is itself a list. This later list contains spans
    for rid, hit_group in hit_groups_by_rid.items():
        rule = rules[rid]
        for hits in hit_group:
            yield build_match(hits, rule, line_by_pos, _type=_type)
