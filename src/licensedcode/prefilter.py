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

from collections import Counter
from operator import attrgetter

from bitarray import bitdiff

from licensedcode import query


"""
Pre-matching filters using bitvectors and other approximate matching techniques:
the purpose is to collect subset of rules that could be matched given a minimum
score threshold. This way less matching needs to be done and in some cases no
matching is necessary.

Filtering strategies return a subset of candidate rules using:
- bitvectors where each bit position correspond to a token id to quickly check for token occurrence
- token_id->frequency counters to quickly check for rule that could be matched with a minimum score
"""


"""
bitvectors:
==========
This filter uses a term occurrence matrix stored compactly as bit arrays.

The idea is to create a bit vector for each rule using only high id non-junk
tokens. Then this is used at matching time as a filter such that we can identify
quickly which rules are likely to get matches and we then do actual matching
only against this subset of rules.

frequency counters:
==================
We build and store a token counter of the frequency for each rule, then build a
similar counter for the query. Then we compute the intersection and union of
these counters pair-wise to compute the distance between a rule and the query.
Generally this is similar to bitvectors but bigger and involving not only token
occurrence but also it frequency. We can derive an approximate score from the
counter distance that is used to further ignore Rules that could not be matched.
"""

# debug flags
DEBUG = False

def logger_debug(*args): pass


if DEBUG:
    import logging
    import sys

    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, basestring) and a or repr(a) for a in args))


def get_query_candidates(tokens, idx):
    """
    Return a list of candidate rule ids for matching given a whole query, an
    index, an optional subset of rule_ids to consider and a minimum score.
    """
    qhigh_bitvector = query.build_bv((t for t in tokens if t >= idx.len_junk), idx.bv_template)
    qhigh_bitvector = qhigh_bitvector[idx.len_junk:]
    candidates = set()
    candidates_add = candidates.add
    for rid, ibitvector in enumerate(idx.high_bitvectors_by_rid):
        # we compute the AND that tells us all tokenids that exist in both. then
        # the hamming distance of that bitarray to the rule array
        intersection = qhigh_bitvector & ibitvector
        if intersection.any():
            candidates_add(rid)
#     print()
#     print ('CANDIDATES', candidates)

#     print ('CANDIDATES', len(candidates))
    return candidates


"""
Approach to collect candidates:

# chunk matching 1
#################
- using bitvectors, collect candidates with 100% high matches. complement with 100% low matches.
Filter using high and low token lens and special check for small rules.

- using frequencies, refine these candidates with 80% high matches. complement with low matches to refine to 80%. 
Filter using high and low token lens and special check for small rules. to ensure we can get some chunk matches
Sort on longer matches first rather than high scoring first.

- perform CHUNK matching on a rule, reinject junk, substract from query run
Repeat


# chunk matching 2
#################
- using bitvectors, collect candidates with at least a distance TBD.
Filter using high token lens and special check for small rules based on unique high tokens.

- using frequencies, refine these candidates with 50% high matches. complement with low matches to refine to 50%. 
Filter using high and low token lens and special check for small rules to ensure we can get some chunk matches

- perform CHUNK matching on a rule, reinject junk, substract from query run
Repeat

# inv matching 2
#################
- using bitvectors, collect candidates with at least one shared token.
Filter using high token lens and special check for small rules based on unique high tokens.

- using whole frequencies, compute score to sort these candidates from high to low score
Filter using high and low token lens and special check for small rules to ensure we can get some chunk matches

- perform INV matching on a rule, reinject junk, substract from query run
Repeat
"""

def compute_candidates(query_run, idx, rules_subset=None):
    """
    Return a list of rule id candidates for further matching based on
    matching bitvectors sorted by decreasing importance.
    
    Only rules that share at least a certain number of tokens with the query are returned.
    This minimum number is rule-specific and based on:
    - the count of occurring unique tokens in the query,
    - the distance between this count and the total count of occurring unique tokens in a rule.
    - the actual length of a rule in high, low and combined tokens,
    - a minimal length of a match
    """
    qbitvector = query_run.bv()
    qhigh_bitvector = qbitvector[idx.len_junk:]
    qhigh_count = qhigh_bitvector.count()
    qlow_bitvector = qbitvector[:idx.len_junk]
    qlow_count = qlow_bitvector.count()
    q_count = qlow_count + qhigh_count

    high_bitvectors_by_rid = idx.high_bitvectors_by_rid

    # subset the rules
    if rules_subset:
        interesting_rules = [r for r in idx.rules_by_rid if r.rid in rules_subset]

    candidates = []
    for rule in interesting_rules:
        ihigh_bitvector = high_bitvectors_by_rid[rule.rid]
        # the intersection that tells us which token ids exist in both
        high_intersection = qhigh_bitvector & ihigh_bitvector
        high_intersection_len = high_intersection.count()

        if rule.high_length <= 4 and high_intersection_len != rule.high_length:
            continue

        if rule.high_length - high_intersection_len < 4:
            continue

        candidate = high_intersection_len, rule.rid
        candidates.append(candidate)

    if not candidates:
        return [], []
    candidates.sort(reverse=True)
    top_ten = candidates[:10]
    all_candidates = set(rid for _, rid in candidates)

    # further refine the top 10 candidates to get the really highest scoring first
    top_candidates = []
    query_freq = query_run.frequencies()
    for _inter_len, rid in top_ten:
        rule_len = idx.rules_by_rid[rid].length
        rule_freq = idx.frequencies_by_rid[rid]
        intersection = rule_freq & query_freq
        score = sum(intersection.values())
        score = (score / rule_len) * 100
        top_candidates.append((score, rid,))

    top_candidates.sort(reverse=True)
    top_candidates= [rid for _, rid in top_candidates]
    return top_candidates, all_candidates


def get_candidates(query_run, idx, rules_subset=None, min_score=100):
    """
    Return a list of candidate rule ids for matching given a query_run, an
    index, an optional subset of rule_ids to consider and a minimum score.
    """
    b_candidates = bit_candidates(query_run.bv(), idx.high_bitvectors_by_rid, idx.low_bitvectors_by_rid, idx.len_junk, rules_subset=rules_subset, min_score=min_score)
    if not b_candidates:
        logger_debug('get_candidates: bit candidates: all junk from bitvector. No match')
        return []
    logger_debug('get_candidates: bit candidates:', len(b_candidates))

    f_candidates = freq_candidates_from_query_run(query_run, idx, rules_subset=set(rid for (_, rid) in b_candidates), min_score=min_score)

    if not f_candidates:
        logger_debug('get_candidates: f_candidates: No match')
        return []
    logger_debug('get_candidates: f_candidates:', len(f_candidates))
    return f_candidates


def bit_candidates(qbitvector, high_bitvectors_by_rid, low_bitvectors_by_rid, len_junk, rules_subset=None, min_score=100):
    """
    Return rule candidates for further matching based on matching bitvectors on
    good token ranges.
    """
    qhigh_bitvector = qbitvector[len_junk:]

    # Is the query_vector entirely composed of junk tokens?
    if not qhigh_bitvector.any():
        return []

    if rules_subset is not None:
        matchable_vectors1 = [(rid, ihbv,) for rid, ihbv in enumerate(high_bitvectors_by_rid) if rid in rules_subset]
    else:
        matchable_vectors1 = enumerate(high_bitvectors_by_rid)

    candidates = _bit_candidates(qhigh_bitvector, matchable_vectors1, min_score, ignore_empty=True)

    if candidates and min_score == 100:
        # further refine candidates using low tokens
        candidates_rules = set(rid for _, rid in candidates)
        matchable_vectors2 = [(rid, lhbv,) for rid, lhbv in enumerate(low_bitvectors_by_rid) if rid in candidates_rules]
        qlow_bitvector = qbitvector[:len_junk]
        candidates2 = set(rid for _, rid in _bit_candidates(qlow_bitvector, matchable_vectors2, min_score, ignore_empty=False))
        candidates = [(dist, rid,) for dist, rid in candidates if rid in candidates2]

    # order by lowest distance:
    # TODO: is this really needed?
    candidates.sort()
    return candidates


def _bit_candidates(qbitvector, bitvectors_by_rid, min_score=100, ignore_empty=True):
    """
    Return rule candidates for further matching based on matching bitvectors.

    Note: the bit count of an XOR between to vectors is the hamming distance
    between these two bits vectors. bitdiff is a shortcut for XOR and count:
    - a 0 distance means that the vectors are identical.
    - a maximum distance of len_good (the length of the bitvectors) means that
    all bits are different
    
    We first use an AND between a query and rule vector to get a new vector that
    has 1 for common 1 bits. We then compute the hamming distance between that
    vector and the rule vector which is the exact number of token id presents in
    both the query and rule.
    """
    if ignore_empty and not qbitvector.any():
        return []

    # FIXME: this length should be cached and never changes for high and low
    matchable_len = len(qbitvector)
    candidates = []
    candidates_append = candidates.append
    for rid, ibitvector in bitvectors_by_rid:
        # we compute the intersection that tells us which token ids exist in
        # both, then the hamming distance of that bitarray to the rule array
        intersection = qbitvector & ibitvector
        distance = bitdiff(intersection, ibitvector)
        # a difference means we have some common bits (i.e. token ids)
        if distance != matchable_len:
            if min_score == 100:
                if distance == 0:
                    # only keep possible 100% matches
                    candidates_append((distance, rid,))
            else:
                candidates_append((distance, rid,))
    return candidates


def freq_candidates_from_query_run(query_run, idx, rules_subset=None, min_score=100):
    lengths_by_rid = [rule.length for rule in idx.rules_by_rid]
    return freq_candidates(query_run.vector(),
                           idx.frequencies_by_rid,
                           lengths_by_rid,
                           rules_subset, min_score)


def freq_candidates(qvector, frequencies_by_rid, lengths_by_rid, rules_subset=None, min_score=100):
    """
    Return rule candidates for further matching based on matching frequency
    vectors.
    """
    # transform the query vector in query frequencies
    # FIXME: use QueryRun method instead
    # FIXME: would iterating tokens be faster?
    query_freq = Counter({tid: len(postings) for tid, postings in enumerate(qvector) if postings})

    if rules_subset is not None:
        matchable_freqs = ((rid, rule_freq,) for rid, rule_freq in enumerate(frequencies_by_rid) if rid in rules_subset)
    else:
        matchable_freqs = enumerate(frequencies_by_rid)

    candidates = []
    candidates_append = candidates.append
    for rid, rule_freq in matchable_freqs:
        # We compute the intersection of frequency counters
        # The score is exactly the sum of intersection/ length
        rule_len = lengths_by_rid[rid]
        intersection = rule_freq & query_freq

        if min_score == 100:
            # for 100% score we need to check each token freq individually and
            # not the the whole score. each value must be bigger than or equal
            # to the rule freq for a given token id. Or the difference must not
            # be superior to zero
            difference = rule_freq - intersection
            if any(v > 0 for v in difference.values()):
                continue
            candidates_append((100, rid,))
        else:
            score = sum(intersection.values())
            score = (score / rule_len) * 100
            if score >= min_score:
                candidates_append((score, rid,))
    # order by highest score
    candidates.sort(reverse=True)
    return candidates
