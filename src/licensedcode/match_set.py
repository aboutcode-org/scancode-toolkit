#
# Copyright (c) 2018 nexB Inc. and others. All rights reserved.
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
from __future__ import print_function
from __future__ import division

from collections import defaultdict
from collections import namedtuple

from intbitset import intbitset

from commoncode.dict_utils import sparsify

from licensedcode.models import Rule

"""
Approximate matching strategies using token sets and multisets.

This is used as a pre-filter to find candidates rules that have the highest
likeliness of matching a query.

The purpose is to quickly and aggressively filter rules that could not possibly
yield a valid match. The candidates are ranked and used later for a pair-wise
matching with the query. This way either less or no matching is needing.

We collect a subset of rules that could be matched given a minimum threshold of
matched token occurrences or an approximation of the length of a match.

The primary technique is to compute token ids sets then multisets intersections
and use the intersection length for ranking. This is basically the same approach
as a traditional IR inverted index postings and query intersection, but we want
to return every matches and not just probabilistic top-ranked matches based on
frequencies as is typically done in a search engine. Therefore we compute the
intersection of the query against every rules. This proves more efficient than a
traditional inverted intersection in part because the queries are much larger
(1000's of tokens) than a traditional search engine query.

Since we use integer to represent tokens, we reduce the problem to integer set
or multisets intersections. Furthermore, we have a finite and limited number of
tokens and we distinguish high and low (junk or common, similar to stop words or
frequencies in IR) token ids based on a threshold. We use these properties to
consider first sets of high tokens and refine candidates based on the sets of
low tokens.

Two techniques are used in sequence: tokens sets and multisets.

Tokens occurrence sets
======================

A tokens occurrence set is represented as an array of bits (aka. a bitmap) where each
bit position corresponds to a token id. The length of each bit array is therefore
equal to the number of unique tokens across all rules. This forms a term occurrence
matrix stored compactly as bitmaps. With about 14K unique tokens and about 3500
rules, we store about 50 millions bits (14K x 3500) for about 6MB of total storage
for this matrix. Computing intersections of bitmaps is fast even if it needs to be
done 3500 times for each query and query run.

The length of the intersection of a query and rule bitmap tells us the count of
shared tokens. We first intersect high tokens sets. If the intersection is empty or
below a minimum rule-specific length, we can skip this rule. If we want an exact
match and we have fewer tokens present in the intersection than in the rule then we
can skip this rule too such as for a small rule that must be matched entirely. If we
have some shared high tokens above the minimum, we then intersect the low token sets.
We use the lengths of these two intersections to rank the candidates.


Tokens ids occurrences multisets aka. frequency counters
========================================================

A tokens frequency counter maps a token id to the number of times it shows up in a
text. This is also called a multiset.

Given the subset of ranked candidates from the token sets intersection step, we
intersect the query and rule frequency counters. For each shared token we collect the
minimum of the two token counts. We sum these to obtain an approximation to the
number of matchable tokens between the query and rule. This is an approximation
because it does not consider the relative positions of the tokens so it may be bigger
than what will eventually be matched.

This sum is then used for the same filtering and ranking used for the token sets
step: First intersect high tokens, skip if some threshold is not met. Then intersect
the low tokens and sum the min-sum of these two intersections to rank the candidates.

Token frequencies allow extra filtering when looking only for exact matches or for
small rules where we want all shared tokens quantities to be matched.

Note about candidates ranking and scoring: we use only the matched lengths for now
for ranking. (aka. the set intersections cardinality). This could be refined by
computing tf/idf, BM25 or other various similarity measures or their approximations
such as Levenshtein distance, Jaccard coefficient, etc.
"""

# Set to True for tracing
TRACE = False
TRACE2 = False
TRACE_DEEP = False
TRACE_ULTRA_DEEP = False
TRACE_COMPARE_SET = False


def logger_debug(*args): pass


if TRACE:
    import logging
    import sys

    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, basestring) and a or repr(a) for a in args))

# TODO: add bigrams sets and multisets
# TODO: see also https://github.com/bolo1729/python-memopt/blob/master/memopt/memopt.py for multisets


def tids_sets_intersector(qset, iset):
    """
    Return the intersection of a query and index token ids sets.
    """
    return qset & iset


def tids_set_counter(tset):
    """
    Return the number of elements present in a token ids set, aka. the set
    cardinality.
    """
    return len(tset)


def tids_multisets_intersector(qmset, imset):
    """
    Return the intersection of a query and index token ids multisets. For a
    token id present in both multisets, the intersection value is the minimum of
    the occurence count in the query and rule for this token.
    Optimized for defaultdicts.
    """
    result = defaultdict(int)
    # iterate the smallest of the two sets
    if len(qmset) < len(imset):
        set1, set2 = qmset, imset
    else:
        set1, set2 = imset, qmset

    for elem, count in set1.items():
        c2count = set2[elem]
        res = count if count < c2count else c2count
        if res:
            result[elem] = res
    return result


def tids_multiset_counter(tmset):
    """
    Return the sum of occurences of elements present in a token ids multiset,
    aka. the multiset cardinality.
    """
    return sum(tmset.values())


def index_token_sets(token_ids, len_junk, len_good):
    """
    Return a 4-tuple of low & high tids sets, low & high tids multisets given a
    token_ids sequence.
    """
    # For multisets, we use a defaultdict, rather than a Counter. This is midly
    # faster than a Counter for sparse sets.

    # this variant uses intbitset to evaluate its performance wrt to bitarray

    low_tids_set = intbitset(len_junk)
    low_tids_set_add = low_tids_set.add
    high_tids_set = intbitset(len_good)
    high_tids_set_add = high_tids_set.add
    low_tids_mset = defaultdict(int)
    high_tids_mset = defaultdict(int)
    for tid in token_ids:
        # this skips unknown token ids that are -1 as well as possible None
        if tid < 0:
            continue
        if tid < len_junk:
            low_tids_mset[tid] += 1
            low_tids_set_add(tid)
        else:
            high_tids_mset[tid] += 1
            high_tids_set_add(tid)

    # sparify for speed
    sparsify(low_tids_mset)
    sparsify(high_tids_mset)
    return low_tids_set, high_tids_set, low_tids_mset, high_tids_mset


CandidateData = namedtuple('CandidateData', 'intersection distance matched_length high_inter_len low_inter_len')

# FIXME: we should consider existing aho matches when considering candidate
# and not rematch these at all

# FIXME: we should consider more aggressively the thresholds and what a match filters
# would discard when we compute candaites to eventually discard many or all candidates
# we compute too many candidates that may waste time in seq matching for no reason


# FIXME: Also we should remove any weak and or small rules from the top candidates
# and anything that cannot be seq matched at all. (e.g. no high match)
def compute_candidates(query_run, idx, rules_subset, top=30):
    """
    Return a ranked list of rule candidates for further matching as a tuple of:
    (rid, rule, multiset of intersected token ids).
    Use approximate matching based on token sets ignoring their positions.
    Only consider rules that have an rid in a `rules_subset` rid set.

    Only return rules sharing some minimum number of tokens with the query based on
    per rule thresholds: the minimum number of tokens that needs to matched and
    ranking is rule-specific and based on matching high then low tokens for the query
    and rule using:

    - counts of common tokens occurrence and their minimum
    - lengths of match and minimal match length
    - the difference and distance of from query to rule
    """

    # high and low query-side token ids sets and multisets
    qlows, qhighs, qlowms, qhighms = index_token_sets(query_run.matchable_tokens(), idx.len_junk, idx.len_good)

    # initial rules
    candidates = [(rid, rule, None) for rid, rule in enumerate(idx.rules_by_rid) if rid in rules_subset]

    # step 1 is on token id sets:
    qlow, qhigh = qlows, qhighs
    sets_by_rid = idx.tids_sets_by_rid
    intersector, counter = tids_sets_intersector, tids_set_counter
    thresholds_getter = Rule.thresholds_unique

    # perform two steps of matching:
    # step one with sets and step two multisets for refinements
    for step in 'sets', 'multisets':
        if TRACE_ULTRA_DEEP: logger_debug('compute_candidates: STEP:', step)
        sortable_candidates = []

        for rid, rule, _intersection in candidates:
            ilow, ihigh = sets_by_rid[rid]
            if TRACE_ULTRA_DEEP:
                logger_debug('candidate: qlow:', [(idx.tokens_by_tid[tid], val) for tid, val in enumerate(qlow)])
                logger_debug('candidate: ilow:', [(idx.tokens_by_tid[tid], val) for tid, val in enumerate(ilow)])
                logger_debug('candidate: qhigh:', [(idx.tokens_by_tid[tid], val) for tid, val in enumerate(qhigh, idx.len_junk)])
                logger_debug('candidate: ihigh:', [(idx.tokens_by_tid[tid], val) for tid, val in enumerate(ihigh, idx.len_junk)])

            thresholds = thresholds_getter(rule)
            if TRACE_DEEP:
                compared = compare_sets(qhigh, qlow, ihigh, ilow, thresholds, intersector, counter, rule, idx)
            else:
                compared = compare_sets(qhigh, qlow, ihigh, ilow, thresholds, intersector, counter)
            if compared:
                sort_order, intersection = compared
                sortable_candidates.append((sort_order, rid, rule, intersection))

        ranked = sorted(sortable_candidates)

        if TRACE2 and ranked:
            logger_debug(' compute_candidates: RANKED at step:', step, ':', len(ranked))
            if TRACE_DEEP:
                for sort_order, rid, rule, _intersection in ranked[:10]:
                    logger_debug(' compute_candidates: rule:', rule.identifier,
                                 'sort_order:', sort_order)

        # remove _sort_order
        candidates = [cand[1:] for cand in ranked]
        # keep only the top candidates
        candidates = candidates[:top]
        if not candidates:
            break

        # step 2 is on tids multisets: update the parameters after step1 if needed
        qlow, qhigh = qlowms, qhighms
        sets_by_rid = idx.tids_msets_by_rid
        intersector, counter = tids_multisets_intersector, tids_multiset_counter
        thresholds_getter = Rule.thresholds

    if TRACE and candidates:
        logger_debug('compute_candidates: FINAL top candidates:', len(candidates))
        tops = [rule.identifier for _rid, rule, _inter in candidates[:10]]
        logger_debug(tops)

    # discard false positive rules from candidates: we never want to run
    # a sequence match on these
    # TODO: discard also rules that can only be matched exactly with the automaton
    candidates = [(rid, rule, inter) for (rid, rule, inter) in candidates if not rule.is_false_positive]

    return candidates


def compare_sets(qhigh, qlow, ihigh, ilow, thresholds, intersector, counter, _rule=None, _idx=None):
    """
    Compare a query qhigh and qlow sets with an index rule ihigh and ilow sets.
    Return a tuple suitable for sorting and the computed sets intersection or None if
    this combination is not match worthy.

    Use the rule Thresholds `thresholds` to determine match worthiness and ranking.

    `intersector` and `counter` are callables that compute the intersection and count
    for sets or multisets.
    """
    # intersect on high tokens
    #########################################
    high_inter = intersector(qhigh, ihigh)
    high_inter_len = counter(high_inter)

    if high_inter_len == 0:
        return

    # for "small" rules, all high must be matched
    small = thresholds.small
    if small and high_inter_len < thresholds.high_len:
        return

    # need some high match above min high
    if high_inter_len < thresholds.min_high:
        return

    # intersect again but on low tokens
    ###################################
    low_inter = intersector(qlow, ilow)
    low_inter_len = counter(low_inter)

    # for small, all low must be matched
    if small and low_inter_len < thresholds.low_len:
        return

    # need match len above min length
    if high_inter_len + low_inter_len < thresholds.min_len:
        return

    # distance
    matched_length = high_inter_len + low_inter_len
    distance = thresholds.length - matched_length
    high_distance = thresholds.high_len - high_inter_len

    # ressemblance and containment
    high_union_len = counter(qhigh) + counter(ihigh) - high_inter_len
    low_union_len = counter(qlow) + counter(ilow) - low_inter_len
    high_resemblance = high_inter_len / high_union_len
    # low_resemblance = low_inter_len / low_union_len
    resemblance = (high_inter_len + low_inter_len) / (high_union_len + low_union_len)
    high_jaccard_distance = 1. - high_resemblance
    jaccard_distance = 1. - resemblance

    high_containment = high_inter_len / thresholds.high_len

    # we give a bigger weight to high containment
    containment = high_containment
    if thresholds.low_len and low_inter_len:
        low_containment = low_inter_len / thresholds.low_len
        low_importance = 0.9
        containment = (high_containment + (low_containment * low_importance)) / (1 + low_importance)

    # Sort order is based on resemblance and containment with additional
    # distances and length to differentiate ties
    # FIXME: this is rather complex and likely can be vastly simplified
    sort_order = -containment, -high_containment, jaccard_distance, high_jaccard_distance, high_distance, distance, -high_inter_len, -matched_length, thresholds.length

    # We also return the intersection for the whole token ids range
    # FIXME: but this is NOT used anywhere for now
    inter = low_inter
    low_inter.update(high_inter)

    if TRACE_DEEP:
        logger_debug('compare_sets: intersected rule:', _rule.identifier)
        logger_debug('  compare_sets: thresholds:', thresholds)
        logger_debug('  compare_sets: high_inter:', ' '.join(_idx.tokens_by_tid[tid] for tid in high_inter))

    return sort_order, inter
