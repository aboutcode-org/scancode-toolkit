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

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from operator import itemgetter

from licensedcode.models import Rule


"""
Pre-matching filters to find candidates rules that have the highest likeliness
of matching a query using approximate and probabilistic matching techniques.

The purpose is to quickly and aggressively filter rules that could not possibly
yield a valid match. The candidates are ranked and used later for a pair-wise
matching with the query. This way either less or no matching is needing.

We collect a subset of rules that could be matched given a minimum threshold of
matched token occurrences or an approximation of the length of a match.

The primary technique is to compute sets or multisets intersections and use the
intersection length for ranking.

Since we use integer to represent tokens, this reduces the problem to integer
set or multisets intersections. Furthermore, we have a finite and limited number
of tokens and we distinguish high and low (junk or common) token ids based on a
threshold. We use these properties to consider first sets of high tokens and
refine candidates based on the sets of low tokens.

Two techniques are used here: tokens sets and multisets.

Tokens occurrence sets
======================

A tokens occurrence set is represented as an array of bits (aka. a bit map)
where each bit position corresponds to a token id. The length of each bit array
is therefore equal to the number of unique tokens across all rules. This forms a
term occurrence matrix stored compactly as bit arrays. With about 14K unique
tokens and about 3500 rules, we store about 50 millions bits (14K x 3500) for
about 6MB of total storage for this matrix. Computing intersections of bit
arrays is very fast even if it needs to be done 3500 times for each query and
query run.

The length of the intersection of a query and rule bit array tells us the
occurrence count of common tokens. We first intersect high tokens arrays. If the
intersection is empty or below a minimum rule-specific length, we can skip that
rule for further matching. If we want an exact match and we have less tokens
present than in the rule, we skip this rule. If we have some common high tokens,
we then intersect the low token arrays. We sum the lengths of these two
intersections to rank the candidates.


Tokens occurrence multisets aka. frequency counters
===================================================

A tokens frequency counter maps a token id to the number of times it shows up in
a text. This is also called a multiset.

We intersect the query and rule frequency counters. For each shared token we
collect the minimum of the two token counts. We sum these to obtain an
approximation to the number of matched tokens. This is an approximation because
it does not consider the relative positions of the tokens.

This sum is then used for the same filtering and ranking used for the token sets
filter: First intersect high tokens first, skip if some threshold is not met.
Then intersect the low token and sum the min-sum of these two intersections to
rank the candidates. 

Token frequencies also allow extra filtering when looking only for exact matches
or for small rules where we want all tokens to be matched.


About candidates ranking and scoring: we use only the matched lengths for now for
ranking. This could be refined by computing tf/idf, BM25 or approximating
various similarity measures or their approximations such as Levenshtein
distance, Jaccard coefficient, etc.
"""

# debug flags
TRACE = False
TRACE_DEEP = False

def logger_debug(*args): pass


if TRACE:
    import logging
    import sys

    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, basestring) and a or repr(a) for a in args))


def compute_candidates(query_run, idx, rules_subset, top=0, exact=False, refine=True):
    """
    Return a ranked list of rule id candidates for further matching using
    approximate ranked matching, ignoring positions.

    Only consider rules that have an rid in `rules_subset`.
    Return at most `top` candidates. If `exact` is True, only return rules that
    may be matched exactly.

    If `refine` is False, filter and rank using tokens occurrence sets only in a single step
    If `refine` is True, refine candidates using tokens occurrence multisets in a second step.
    
    Only return rules sharing at least a minimum number of tokens with the query.
    Minimums and ranking is rule-specific and based on:
    - occurrences in high and low tokens for the query and the rule
    - minimal match occurrences for a rule in high and low tokens
    - lengths and minimal match length for a rule in high and low tokens
    - the difference and distance of these between the query and the rule 
    """

    # initial rules
    candidates = [(rid, rule) for (rid, rule) in enumerate(idx.rules_by_rid) if rid in rules_subset]

    # perform one step with set or two steps with sets and then multisets for refinements
    steps = (1, 2,) if refine else (1,)

    # step 1 is on bit sets:
    _qbitvector = query_run.bv()
    qhigh = _qbitvector[idx.len_junk:]
    qlow = _qbitvector[:idx.len_junk]
    high_by_rid = idx.high_bitvectors_by_rid
    low_by_rid = idx.low_bitvectors_by_rid
    thresholds_getter = Rule.thresholds_unique
    intersector = int_set_intersector

    for step in steps:
        if TRACE_DEEP: logger_debug('compute_candidates: STEP:', step)
        sortable_candidates = []

        for rid, rule in candidates:
            if TRACE_DEEP: logger_debug(' compute_candidates: evaluating rule:', rule.identifier())

            ihigh = high_by_rid[rid]
            ilow = low_by_rid[rid]
            thresholds = thresholds_getter(rule)
            sort_order = compare_sets(qhigh, qlow, ihigh, ilow, thresholds, intersector, exact=exact)
            if sort_order:
                sortable_candidates.append((sort_order, rid, rule))

        ranked = sorted(sortable_candidates)
        if top:
            ranked = ranked[:top]

        if TRACE_DEEP and sortable_candidates:
            logger_debug(' compute_candidates: RANKED at step:', step, ':', len(sortable_candidates))
            if TRACE_DEEP:
                for sort_order, rid, rule in ranked:
                    logger_debug(' compute_candidates: rule:', rule.identifier(), 'sort_order:', sort_order)

        candidates = [(rid, rule) for _sort_order, rid, rule in ranked]

        if len(steps) == 2:
            # step 2 is on frequencies multisets: update the parameters after step1 if needed
            qhigh, qlow = query_run.frequencies(start=idx.len_junk)
            high_by_rid = idx.high_frequencies_by_rid
            low_by_rid = idx.low_frequencies_by_rid
            thresholds_getter = Rule.thresholds
            intersector = int_multiset_intersector

    if TRACE:
        logger_debug('compute_candidates: FINAL candidates:', len(sortable_candidates))
        tops = [r.identifier() for _i, r in candidates[:10]]
        map(logger_debug, tops)

    # FIXME: we should return the matched vectors or counters intersections:
    # they contain valuable information for matching e.g. the actual token ids
    # matched and could therefore speed up a lot matching since non-matched
    # tokens could be skipped entirely from the matching phase.

    # return only rid from (rid, rule)
    good_candidates = map(itemgetter(0), candidates)
    return good_candidates


def int_set_intersector(qbv, ibv):
    """
    Return the number of bits set to 1 in the intersection of a query and an
    index integer set.
    """
    # using bitarrays at the moment
    return (qbv & ibv).count()


def int_multiset_intersector(qfreq, ifreq):
    """
    Return the sum of the minimum values of the intersection of a query and an
    index integer multiset.
    """
    # With collection.Counter, the intersection of two Counter a and b is
    # min(a[x], b[x]).

    # TODO: we could re-implement this using a faster intersection for our
    # smaller use-case using arrays instead of counters
    return sum((ifreq & qfreq).itervalues())


def compare_sets(qhigh, qlow, ihigh, ilow, thresholds, intersector, exact=True):
    """
    Compare a query qhigh and qlow sets with an index rule ihigh and ilow sets.
    Return a tuple suitable for ranked sorting or None if this combination is
    not match worthy.
    
    Use the models.Thresholds `thresholds` to determine match worthiness and
    ranking.
    
    Use the `intersector` callable to compute the number of matching tokens
    between sets allowing to use this function for sets or multisets or set-like
    objects.
    
    If `exact` is True, return None if the query could not be matched exactly
    against this index rule.
    """
    # the intersection that tells us which token ids exist in both
    high_inter_len = intersector(qhigh, ihigh)

    # for exact, all high must be matched

    if exact and high_inter_len < thresholds.high_len:
        if TRACE_DEEP:
            ihigh_len = thresholds.high_len
            logger_debug('  compare_sets: SKIP 1: exact=%(exact)r and high_inter_len=%(high_inter_len)r != ihigh_len=%(ihigh_len)r' % locals())
        return

    # need some high match above min high
    if high_inter_len < thresholds.min_high:
        if TRACE_DEEP:
            min_ihigh = thresholds.min_high
            logger_debug('  compare_sets: SKIP 2: high_inter_len=%(high_inter_len)r < min_ihigh=%(min_ihigh)r' % locals())
        return

    # intersect again this time on low tokens
    low_inter_len = intersector(qlow, ilow)

    # for exact, all low must be matched
    if exact and low_inter_len < thresholds.low_len:
        if TRACE_DEEP:
            ilow_len = thresholds.low_len
            logger_debug('  compare_sets: SKIP 3: exact=%(exact)r and low_inter_len=%(low_inter_len)r < ilow_len=%(ilow_len)r' % locals())
        return

    # need match len above min length
    if high_inter_len + low_inter_len < thresholds.min_len:
        if TRACE_DEEP:
            min_ilen = thresholds.min_len
            logger_debug('  compare_sets: SKIP 4: high_inter_len=%(high_inter_len)r + low_inter_len=%(low_inter_len)r < min_ilen=%(min_ilen)r' % locals())
        return

    # for small rules, we want all tokens matched
    if thresholds.small and (high_inter_len + low_inter_len != thresholds.length):
        if TRACE_DEEP:
            small = thresholds.small
            ilen = thresholds.length
            logger_debug('  compare_sets: SKIP 5: small=%(small)r and high_inter_len=%(high_inter_len)r + low_inter_len=%(low_inter_len)r != ilen=%(ilen)r' % locals())
        return

    # FIXME: this does not make sense, for bitvectors: we cannot evaluate gaps at this stage!!!!
    # therefore this will always be True
    # need match len within gap bounds
    if high_inter_len + low_inter_len > thresholds.length + thresholds.max_gaps:
        if TRACE_DEEP:
            max_igaps = thresholds.max_gaps
            ilen = thresholds.length
            logger_debug('  compare_sets: SKIP 6: high_inter_len=%(high_inter_len)r + low_inter_len=%(low_inter_len)r > ilen=%(ilen)r + max_igaps=%(max_igaps)r' % locals())
        return

    length = high_inter_len + low_inter_len
    distance = thresholds.length - length

    # set sort order by closest distance,  longest lengths
    candidate = distance, -high_inter_len, -length, thresholds.length
    return candidate
