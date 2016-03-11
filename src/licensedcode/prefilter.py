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

from bitarray import bitarray
from bitarray import bitdiff


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


def bit_candidates(qvector, high_bitvectors_by_rid, low_bitvectors_by_rid, len_junk, rules_subset=None, min_score=100):
    """
    Return rule candidates for further matching based on matching bitvectors on
    good token ranges.

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
    qbitvector = bitarray(qvector)
    qhigh_bitvector = qbitvector[len_junk:]

    # Is the query_vector entirely composed of junk tokens?
    if not qhigh_bitvector.any():
        return []

    if rules_subset is not None:
        matchable_vectors1 = ((rid, ihbv,) for rid, ihbv in enumerate(high_bitvectors_by_rid) if rid in rules_subset)
    else:
        matchable_vectors1 = enumerate(high_bitvectors_by_rid)

    candidates = _bit_candidates(qhigh_bitvector, matchable_vectors1, min_score)

    if candidates and min_score == 100:
        # further refine candidates using low tokens
        candidates_rules = set(rid for _, rid in candidates)
        matchable_vectors2 = [(rid, lhbv,) for rid, lhbv in enumerate(low_bitvectors_by_rid) if rid in candidates_rules]
        qlow_bitvector = qbitvector[:len_junk]
        candidates2 = set(rid for _, rid in _bit_candidates(qlow_bitvector, matchable_vectors2, min_score, ignore_empty=False))
        candidates = [(dist, rid,) for dist, rid in candidates if rid in candidates2]

    # order by lowest distance
    candidates.sort()
    return candidates


def _bit_candidates(qbitvector, bitvectors_by_rid, min_score=100, ignore_empty=True):
    """
    Return rule candidates for further matching based on matching bitvectors
    """
    if ignore_empty and not qbitvector.any():
        return []

    matchable_len = len(qbitvector)

    candidates = []
    candidates_append = candidates.append
    for rid, ibitvector in bitvectors_by_rid:
        # we compute the AND that tells us all tokenids that exist in both. then
        # the hamming distance of that bitarray to the rule array
        distance = bitdiff(qbitvector & ibitvector, ibitvector)
        # a difference means we have some common bits (i.e. tokenids)
        if distance != matchable_len:
            if min_score == 100:
                if distance == 0:
                    # only keep possible 100% matches
                    candidates_append((distance, rid,))
            else:
                candidates_append((distance, rid,))
    return candidates


def freq_candidates(qvector, frequencies_by_rid, lengths_by_rid, rules_subset=None, min_score=100):
    """
    Return rule candidates for further matching based on matching frequency
    vectors.
    """
    # transform the query vector in query frequencies
    query_freq = Counter({tid: len(postings) for tid, postings in enumerate(qvector) if postings})

    if rules_subset is not None:
        matchable_freqs = ((rid, rule_freq,) for rid, rule_freq in enumerate(frequencies_by_rid) if rid in rules_subset)
    else:
        matchable_freqs = enumerate(frequencies_by_rid)

    candidates = []
    candidates_append = candidates.append
    for rid, rule_freq in matchable_freqs:
        # We compute the intersection of frequency counters
        # The score is exactly the sum of intersection/ rule_length
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
            score = (score / float(rule_len)) * 100
            if score >= min_score:
                candidates_append((score, rid,))
    # order by highest score
    candidates.sort(reverse=True)
    return candidates
