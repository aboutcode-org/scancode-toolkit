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

from array import array
from collections import Counter
from math import log

from intbitset import intbitset

from commoncode.dict_utils import sparsify


"""
Approximate matching strategies using token sets and multisets.

This is used as a pre-filter to find candidates rules that have the highest
likeliness of matching a query.

The purpose is to quickly and aggressively filter rules that could not possibly
yield a valid match. The candidates rules are ranked and used later for pair-
wise matching with the query. This way either less or no matching is needed.

We collect a subset of rules that could be matched by ranking them and keep the
top candidates. We also filter out rules based on minimum thresholds such as
matched token occurrences or an approximation of the length of a match.

The primary technique is token ids sets and multisets intersections. We use the
a tf-idf and intersection length to compute scores/ranking elements including
ressemblance and containment. This is essentially a traditional IR inverted
index approach.

But we also want to return every matches and not just probabilistic top-ranked
matches based on frequencies as is typically done in a search engine. There2fore
we compute the intersection of the query against every rules. This proves more
efficient than a traditional inverted intersection in part because the queries
are much larger (1000's of tokens) than a traditional search engine query.

Since we use integers to represent tokens, we reduce the problem to integer set
or multisets/bags/counters intersections. Furthermore, we have a finite and
limited number of tokens.

Two techniques are used in sequence: tokens sets and multisets.

Tokens occurrence sets
======================

A tokens occurrence set is represented as an array of bits (aka. a bitmap) where
each bit position corresponds to a token id. The length of each bit array is
therefore equal to the number of unique tokens across all rules. This forms a
term occurrence matrix stored compactly as bitmaps. With about 15K unique tokens
and about 6k rules, we store about 90 millions bits (15K x 6K) for about 10MB
of total storage for this matrix. Computing intersections of bitmaps is fast
even if it needs to be done thousand times for each query and query run.

The length of the intersection of a query and rule bitmap tells us the count of
shared tokens. We can skip rules based on thresholds and we then rank and keep
the top rules.


Tokens ids occurrences multisets aka. frequency counters
========================================================

A tokens frequency counter maps a token id to the number of times it shows up in
a text. This is also called a multiset or a bag or Counter.

Given the subset of ranked candidate rules from the token sets intersection
step, we intersect the query and rule token multisets. For each shared token we
collect the minimum count of a token present in both. We sum these to obtain an
approximation to the number of matchable tokens between the query and rule. This
is an approximation because it does not consider the relative positions of the
tokens so it may be bigger than what will eventually be matched using a sequence
alignment.

This sum is then used for the same filtering and ranking used for the token sets
step: skip if some threshold is not met and rank the candidates.

Finally we return the sorted top candidates
"""

# Set to True for tracing
TRACE = False
TRACE_DEEP = False
TRACE_CANDIDATES = False


def logger_debug(*args): pass


if TRACE or TRACE_CANDIDATES:
    import logging
    import sys

    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, basestring) and a or repr(a) for a in args))

# TODO: add bigrams sets and multisets
# TODO: see also https://github.com/bolo1729/python-memopt/blob/master/memopt/memopt.py for multisets


def index_token_sets(token_ids, len_tokens):
    """
    Return a tuple of (tids set, tids multiset) given a `token_ids` tids
    sequence and the known `len_tokens` total number of known tokens.
    """
    tids_mset = Counter(tid for tid in token_ids
        # this skips unknown token ids that are -1 as well as possible None
        if tid >= 0)

    tids_set = intbitset(tids_mset.keys())
    # OPTMIZED: sparsifyfor speed
    sparsify(tids_mset)
    return tids_set, tids_mset


def compute_idfs(len_rules, tokens_doc_freq_by_tid):
    """
    Return a mapping of {token id -> inverse document frequency} given mapping
    of `tokens_doc_freq_by_tid` counting the number of rules in which a token if
    occurs and the `len_rules` number of rules.
    """
    # note: we perform some smoothing as in sklearn:
    # See https://github.com/scikit-learn/scikit-learn/blob/645d3224182d1dd3723ffbf983172aad07cfeba8/sklearn/feature_extraction/text.py#L1131
    # note: we use a more compact array of floats where the index is a token id.
    return array('f', (log(len_rules / tdf) if tdf else 0.
                       for tdf in tokens_doc_freq_by_tid))


# FIXME: we should consider existing aho matches when considering candidate
# and not rematch these at all

# FIXME: we should consider more aggressively the thresholds and what a match filters
# would discard when we compute candaites to eventually discard many or all candidates
# we compute too many candidates that may waste time in seq matching for no reason

# FIXME: Also we should remove any weak and or small rules from the top candidates
# and anything that cannot be seq matched at all. (e.g. no high match)
def compute_candidates(query_run, idx, rules_subset, top=30):
    """
    Return a ranked list of rule candidates for further matching give a
    `query_run`.
    Use approximate matching based on token sets ignoring positions. Only
    consider rules that have an rid in a `rules_subset` rid set if provided.

    The ranking is based on a combo of a td-idf score , the resemblance and the containment.
    """
    rid_rules = enumerate(idx.rules_by_rid)
    if rules_subset:
        rid_rules = ((rid, rule) for rid, rule in rid_rules if rid in rules_subset)

    # perform two steps of ranking:
    # step one with tid sets and step two with tid multisets for refinement
    qset, qmset = index_token_sets(query_run.matchable_tokens(), idx.len_tokens)
    tokens_idf_by_tid = idx.tokens_idf_by_tid
    ###########################################################################
    # step 1 is on token id sets:
    ###########################################################################
    if TRACE_DEEP: logger_debug('compute_candidates: STEP: SETS')

    sortable_candidates1 = []
    sortable_candidates1_append = sortable_candidates1.append
    isets_by_rid = idx.tids_all_sets_by_rid
    qset_len = len(qset)

    for rid, rule in rid_rules:
        iset = isets_by_rid[rid]
        compared = compare_token_sets(qset, qset_len, iset, rule, tokens_idf_by_tid)
        if compared:
            sortable_candidates1_append((compared, rid, rule))

    if not sortable_candidates1:
        return []

    sortable_candidates1.sort(reverse=True)

    if TRACE_CANDIDATES and sortable_candidates1:
        logger_debug('compute_candidates: step1 sortable_candidates1:', len(sortable_candidates1))
        for scores, _rid, rule in sortable_candidates1[:20]:
            logger_debug(rule)
            logger_debug(scores)
            logger_debug()

    ###########################################################################
    # step 2 is on tid multisets
    ###########################################################################
    if TRACE_DEEP: logger_debug('compute_candidates: STEP: MULTISETS')

    sortable_candidates2 = []
    sortable_candidates2_append = sortable_candidates2.append
    imsets_by_rid = idx.tids_all_msets_by_rid
    # the len of a multiset is the sum of its values in our case
    qmset_len = sum(qmset.values())

    # rerank only the top candidates
    # TODO: should we rerank more than the top, like top *2 ?
    for _set_scores , rid, rule in sortable_candidates1[:top * 2]:
        imset = imsets_by_rid[rid]
        compared = compare_token_multisets(qmset, qmset_len, imset, rule, tokens_idf_by_tid)
        if compared:
            sortable_candidates2_append((compared, rule))

    if not sortable_candidates2:
        return []

    sortable_candidates2.sort(reverse=True)

    if TRACE_CANDIDATES and sortable_candidates2:
        logger_debug('compute_candidates: FINAL sortable_candidates2:', len(sortable_candidates2))
        for scores, rule in sortable_candidates2[:20]:
            logger_debug(rule)
            logger_debug(scores)
            logger_debug()

    ###########################################################################
    # keep top
    # (and remove sort_order from Schwartzian transform)
    candidates = [cand for _so, cand in sortable_candidates2[:top]]
    return candidates


def compare_token_sets(qset, qset_len, iset, rule, tokens_idf_by_tid):
    """
    Compare a `qset` query token ids set with a `iset` index rule token ids set.
    Return a score tuple to use a rank sorting key or None.
    """
    intersection = qset & iset
    intersection_len = len(intersection)

    if intersection_len == 0:
        return

    thresholds = rule.thresholds_unique()
    iset_len = rule.length_unique
# 
#     # for "small" rules, all tokens must be matched
#     small = thresholds.small
#     if small and intersection_len < iset_len:
#         return
# 
#     # need match len above min length
#     if intersection_len < thresholds.min_len:
#         return

    # resemblance and containment
    union_len = qset_len + iset_len - intersection_len
    resemblance = intersection_len / union_len
    containment = intersection_len / iset_len

    tdidf_score = compute_tfidf_set_score(
        intersection, qset_len, tokens_idf_by_tid)
#     tdidf_score = tdidf_score / intersection_len

    score = (2 * tdidf_score + 2 * containment + resemblance) / 5
    return (
        'score', score,
        'tdidf_score', round(tdidf_score, 7),
        'containment', round(containment, 3),
        'resemblance', round(resemblance, 4),
        'iset_len', iset_len,
        'qset_len', qset_len,
    )


def compare_token_multisets(qset, qset_len, iset, rule, tokens_idf_by_tid):
    """
    Compare a `qset` query multiset with a `iset` index rule multiset.
    Return a score tuple to use a rank sorting key or None.
    Use the rule and `tokens_idf_by_tid` to compute the score.
    """

    thresholds = rule.thresholds()
    iset_len = rule.length

    # Compute the intersection of two token ids multisets. For a
    # token id present in both multisets, the intersection value is the minimum of
    # the occurence count in the query and rule for this token.

    intersection = {}

    # iterate the smallest of the two sets
    if qset_len < iset_len:
        set1, set2 = qset, iset
    else:
        set1, set2 = iset, qset

    for elem, e1count in set1.items():
        e2count = set2[elem]
        count = min(e1count, e2count)
        if count:
            intersection[elem] = count

    intersection_len = sum(intersection.values())

    if intersection_len == 0:
        return

    # need match len above min length
    if intersection_len < thresholds.min_len:
        return

    # resemblance and containment
    union_len = sum(qset.values()) + sum(iset.values()) - intersection_len
    resemblance = intersection_len / union_len

    if intersection_len >= iset_len:
        containment = 1
    else:
        containment = intersection_len / iset_len

    # honor minimum coverage
    minimum_coverage = rule.minimum_coverage
    if minimum_coverage and containment < (minimum_coverage / iset_len):
        return

    tdidf_score = compute_tfidf_mset_score(
        intersection, qset_len, tokens_idf_by_tid)
#     tdidf_score = tdidf_score / intersection_len

    score = (2 * tdidf_score + 2 * containment + resemblance) / 5
    return (
        'score', score,
        'tdidf_score', round(tdidf_score, 7),
        'containment', round(containment, 3),
        'resemblance', round(resemblance, 4),
        'iset_len', iset_len,
        'qset_len', qset_len,
    )


def compute_tfidf_set_score(intersection, qlen, tokens_idf_by_tid):
    """
    Return a score as a float for a `intersection` set of matched token ids from
    a query of length `qlen` and `tokens_idf_by_tid` mapping of
    {token id -> idf}

    """
    tfidf = 0.
    tf = 1 / qlen
    for tid in intersection:
        idf = tokens_idf_by_tid[tid]
        tfidf += (tf * idf)
    return tfidf


def compute_tfidf_mset_score(intersection, qlen, tokens_idf_by_tid):
    """
    Return a score as a float for a `intersection` multiset of matched token
    ids from a query of length `qlen` and `tokens_idf_by_tid` a mapping of
    {token id -> idf}

    """
    tfidf = 0.
    for tid, tid_count in intersection.items():
        tf = tid_count / qlen
        idf = tokens_idf_by_tid[tid]
        tfidf += (tf * idf) 
    return tfidf
