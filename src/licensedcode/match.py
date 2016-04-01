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

from functools import total_ordering
from itertools import groupby
from operator import or_

from licensedcode.whoosh_spans.spans import Span
from licensedcode import NGRAM_LENGTH
from licensedcode import MAX_GAP


DEBUG = False
DEBUG_REPR = False
DEBUG_REFINE = False
DEBUG_FILTER = False
DEBUG_MERGE = False

def logger_debug(*args): pass

if DEBUG:
    import logging
    import sys

    logger = logging.getLogger(__name__)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, basestring) and a or repr(a) for a in args))

    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)


EXACT_MATCH_SCORE = 1.

# FIXME: Implement each ordering functions. From the Python docs: Note: While
# this decorator makes it easy to create well behaved totally ordered types, it
# does come at the cost of slower execution and more complex stack traces for
# the derived comparison methods. If performance benchmarking indicates this is
# a bottleneck for a given application, implementing all six rich comparison
# methods instead is likely to provide an easy speed boost.

@total_ordering
class LicenseMatch(object):
    """
    License detection match to a rule with matched query positions and lines and
    matched index positions. Also computes a score for match. At a high level, a
    match behaves a bit like a Span and has several similar methods taking into
    account both the query and index Span.
    """

    __slots__ = 'rule', 'qspan', 'ispan', 'line_by_pos' , '_type', '_merged'

    def __init__(self, rule, qspan, ispan, line_by_pos=None, _type=''):
        """
        Create a new match from:
         - rule: matched Rule object
         - qspan: query text matched Span.
         - ispan: rule text matched Span start at zero.
         - line_by_pos: mapping of (query positions -> line numbers). Line numbers start at one.
           Optional: if not provided, the `lines` start and end tuple will be (0, 0) and no line information will be available.
         - _type: a string indicating which matching procedure this match was created with. Used for debugging and testing only.
        """
        self.rule = rule
        self.qspan = qspan
        self.ispan = ispan
        self.line_by_pos= line_by_pos or {}
        self._type = _type

        # a list of original matches that were merged in this match
        self._merged = []


    def __repr__(self):
        data = dict(
            rid=self.rule.rid,
            rule_id=self.rule.identifier(),
            rule_licenses=', '.join(sorted(self.rule.licenses)),
            nscore=round(self.normalized_score(), 2),
            ilen=self.ilen(),
            qse=(self.qstart, self.qend),
            ise=(self.istart, self.iend),
            qspan=self.qspan,
            ispan=self.ispan,
            lines=self.lines,
            _type=self._type,
            density=round(self.density(), 2),
        )
        msg = 'LicenseMatch<%(rule_id)r, %(rule_licenses)r, s=%(nscore)r, l=%(ilen)r, d=%(density)r, qse=%(qse)r, ise=%(ise)r, ln=%(lines)r, %(_type)r>'
        if DEBUG_REPR:
            msg += '''
            qspan=%(qspan)r
            ispan=%(ispan)r'''

        return msg % data

    def __eq__(self, other):
        """
        Strict equality.
        """
        return (isinstance(other, LicenseMatch)
            and self.rule == other.rule
            and self.qspan == other.qspan
            and self.ispan == other.ispan
            and self.lines == other.lines)

    def __copy__(self):
        """
        Return a shallow copy of self.
        """
        return LicenseMatch(self.rule, Span(self.qspan), Span(self.ispan), dict(self.line_by_pos), _type=self._type)

    def __lt__(self, other):
        """
        Only consider qspan for ordering
        """
        return self.qstart < other.qstart

    def __hash__(self):
        """
        Matches are hashable.
        """
        return hash((self.rule, tuple(self.qspan), tuple(self.ispan), self.lines))

    @property
    def qstart(self):
        return self.qspan.start

    @property
    def qend(self):
        return self.qspan.end

    @property
    def istart(self):
        return self.ispan.start

    @property
    def iend(self):
        return self.ispan.end

    @property
    def lines(self):
        return self.line_by_pos.get(self.qstart, 0), self.line_by_pos.get(self.qend, 0)

    def __contains__(self, other):
        """
        Return True if every other qspan and ispan are contained in any self qspan.
        """
        return self.contains_qspan(other) and self.contains_ispan(other)

    def contains_qspan(self, other):
        return other.qspan.issubset(self.qspan)

    def contains_ispan(self, other):
        return other.ispan.issubset(self.ispan)
    
    def qdistance_to(self, other):
        """
        Return the absolute qspan distance to other match.
        Touching and overlapping matches have a zero distance.
        """
        return self.qspan.distance_to(other.qspan)

    def idistance_to(self, other):
        """
        Return the absolute ispan distance from self to other match.
        Touching and overlapping matches have a zero distance.
        """
        return self.ispan.distance_to(other.ispan)

    def qoverlap(self, other):
        return self.qspan.overlap(other.qspan)

    def ioverlap(self, other):
        return self.ispan.overlap(other.ispan)

    def overlap(self, other):
        """
        Return True if this match spans both overlap with other match spans.
        """
        return self.qoverlap(other) and self.ioverlap(other)

    def qtouch(self, other):
        return self.qspan.touch(other.qspan)

    def itouch(self, other):
        return self.ispan.touch(other.ispan)

    def touch(self, other):
        """
        Return True if this match spans both touch other match spans.
        """
        return self.qtouch(other) and self.itouch(other)

    def qsurround(self, other):
        return self.qspan.surround(other.qspan)

    def isurround(self, other):
        return self.ispan.surround(other.ispan)

    def surround(self, other):
        """
        Return True if this match spans both surround (without touching) other match spans.
        """
        return self.qsurround(other) and self.isurround(other)

    def is_qbefore(self, other):
        return self.qspan.is_before(other.qspan)

    def is_qbefore_or_touch(self, other):
        return self.qspan.is_before_or_touch(other.qspan)

    def is_ibefore(self, other):
        return self.ispan.is_before(other.ispan)

    def is_ibefore_or_touch(self, other):
        return self.ispan.is_before_or_touch(other.ispan)

    def is_before(self, other):
        """
        Return True if this match spans are strictly before other match spans.
        """
        return self.is_qbefore(other) and self.is_ibefore(other)

    def is_qafter(self, other):
        return self.qspan.is_after(other.qspan)

    def is_qafter_or_touch(self, other):
        return self.qspan.is_after_or_touch(other.qspan)

    def is_iafter(self, other):
        return self.ispan.is_after(other.ispan)

    def is_iafter_or_touch(self, other):
        return self.ispan.is_after_or_touch(other.ispan)

    def is_after(self, other):
        """
        Return True if this match spans are strictly after other match spans.
        """
        return self.is_qafter(other) and self.is_iafter(other)

    def is_after_or_touch(self, other):
        return self.is_qafter_or_touch(other) and self.is_iafter_or_touch(other)

    @staticmethod
    def merge(matches, max_dist=15):
        """
        Merge overlapping, touching or close-by matches in the given iterable of
        matches. Return a new list of merged matches if they can be merged.
        Matches that cannot be merged are returned as-is. 
        
        Only matches for the same rules can be merged.
        
        The overlap and touch is considered using both the qspan and ispan.
        
        The maximal merge is always returned and eventually a single match per
        rule is returned if all matches for that rule can be merged.
        
        For being merged two matches must also be in increasing query and index positions.
        """
        # FIXME: longer and denser matches starting at the same qspan should
        # be sorted first

        matches = sorted(matches, key=lambda m: (m.rule.rid, m.qspan))
        merged = []
        # only merge for now matches with the same rule
        # iterate on matches grouped by rule, one rule at a time.
        for _rid, rule_matches in groupby(matches, key=lambda m: m.rule.rid):
            rule_matches = list(rule_matches)
            i = 0
            if DEBUG_MERGE:
                print('merge_match: processing rule:', rule_matches[0].rule.identifier())

            # compare two matches in the sorted sequence: this_match and the next one
            while i < len(rule_matches) - 1:
                this_match = rule_matches[i]
                j = i + 1
                if DEBUG_MERGE:
                    print('merge_match: this_match:', this_match)

                while j < len(rule_matches):
                    next_match = rule_matches[j]
                    if DEBUG_MERGE:
                        print('merge_match: next_match:', next_match)
                        print()
                        print(' next_match.is_qafter_or_touch(this_match):', next_match.is_qafter_or_touch(this_match))
                        print(' next_match.is_iafter_or_touch(this_match):', next_match.is_iafter_or_touch(this_match))
                        print()
                        print(' this_match.qoverlap(next_match)          :', this_match.qoverlap(next_match))
                        print(' this_match.ioverlap(next_match)          :', this_match.ioverlap(next_match))
                        print()

                    if next_match.qdistance_to(this_match) >= max_dist or next_match.idistance_to(this_match) >= max_dist:
                        break

                    # if next_match is in sequence or overlaps, merge it in
                    # this_match and delete next_match
                    if (
                        this_match.overlap(next_match)
                    or (
                        (
                         this_match.qoverlap(next_match)
                         or (
                             next_match.is_qafter_or_touch(this_match)
                             and next_match.qdistance_to(this_match) < max_dist
                             and next_match.idistance_to(this_match) < max_dist
                            )
                        )
                        and
                        (
                            (
                             next_match.is_iafter_or_touch(this_match)
                             and next_match.qdistance_to(this_match) < max_dist
                             and next_match.idistance_to(this_match) < max_dist
                            )
                         or (
                             next_match.ioverlap(this_match)
                             and next_match.istart > this_match.istart
                             and next_match.iend > this_match.iend
                            )
                        )
                       )
                    or (
                        this_match.surround(next_match)
                       )
                    ):
                        if DEBUG_MERGE:
                            print('====>MERGING')
                            print()
                        this_match = this_match.update(next_match)
                        rule_matches[i] = this_match
                        del rule_matches[j]

                    # otherwise check the next after next_match
                    else:
                        j += 1
                # otherwise use the next as the new reference match
                i += 1
            merged.extend(rule_matches)
        return merged

    def combine(self, other):
        """
        Return a new match combining self and an other match.
        """
        same_rule = self.rule == other.rule
        same_licensing = self.same_licensing(other)
        assert same_rule or same_licensing, 'Cannot combine matches with different rules or licensing: from: %(self)r, to: %(other)r' % locals()
        combined = LicenseMatch(self.rule, self.qspan | other.qspan, self.ispan | other.ispan)

        # combine and set lines Region (we cannot pass line by pos to the initializer as we do not have it stored in a match)
        combined.line_by_pos.update(self.line_by_pos)
        combined.line_by_pos.update(other.line_by_pos) 

        if other._type not in self._type:
            combined._type = ' '.join([self._type, other._type])
        else:
            combined._type = self._type

        # keep track of merged
        # combined._merged = self._merged + other._merged + [copy(self), copy(other)]
        return combined

    def update(self, other):
        """
        Update self with other match and return self.
        """
        combined = self.combine(other)
        self.qspan = combined.qspan
        self.ispan = combined.ispan
        self.line_by_pos = combined.line_by_pos
        self._type = combined._type
        return self

    def ilen(self):
        """
        Return the length of the match as the number of matched index tokens.
        """
        return len(self.ispan)

    def negative(self):
        """
        Return True if this match is for a "negative" rule.
        """
        return self.rule.negative()

    def score(self):
        """
        Return the computed score for this match as a float between 0 and 1.
        """
        if not self.rule.length:
            return 0.
        # simple ratio of matched tokens to total rule tokens
        return self.ilen() / self.rule.length

    def normalized_score(self):
        """
        Return the computed score for this match as a float between 0 and 100.
        """
        score = self.score()
        if score:
            score = score * 100
        return round(score, 2)

    def density(self):
        """
        Return the computed density of this match as a float between 0 and 1. A
        dense match has ispan contiguous and has a maximum density of one.
        A sparse match has some non-contiguous ispan.

        Density is not related to the score: a low scoring match can be dense
        and a high scoring match can be sparse.

        The density is computed as the ratio of ilen (effective number of
        matched itokens) to the length of the qspan (actual maximal range of
        positions for this match).
        """
        dens = self.ilen() / self.qspan.magnitude()
        # assert dens <= 1, 'density cannot be bigger than 1' + str(dens)
        if DEBUG and dens > 1:
            logger_debug('density cannot be bigger than 1', dens)
        return dens

    def minimum_density(self):
        """
        Return the minimum density as a float between 0 and 1 that this match
        should have to be considered as a good match.
        
        The rationale is that for some small rules with very few tokens, it does
        not make sense to consider sparse matches at all unless their density is
        high.
        
        For example, a rule with this text: 
            Apache-1.1
        should not be matched to this query:    
            This Apache component was released as v1.1 in 2015.
        """

        rule_len = self.rule.length

        # set as the biggest of 1/10th the length or the ngram length
        smallest_gap = max([round(rule_len / 10), NGRAM_LENGTH])

        # not more than max_gap
        gap_length = min([smallest_gap, MAX_GAP])

        # for a rule with no gaps and a length of 4 or less, the minimum density is 1.
        return rule_len / (rule_len + (self.rule.gaps_count * gap_length))

    def same(self, other):
        """
        Return True if other has the same licensing, score and spans.
        """
        return self.same_licensing(other) and self.same_score(other) and self.same_spans(other)

    def same_rule(self, other):
        """
        Return True if other has the same license rule.
        """
        return self.rule == other.rule

    def same_licensing(self, other):
        """
        Return True if other has the same detected license keys.
        """
        return self.rule.same_licensing(other.rule)

    def same_score(self, other):
        """
        Return True if other has the same score.
        """
        return self.score() == other.score()

    def same_spans(self, other):
        """
        Return True if other has the same qspan and ispan.
        """
        return self.qspan == other.qspan and self.ispan == other.ispan

    def small(self, min_length=NGRAM_LENGTH):
        """
        Return True if this match is "small" meaning that it has an ilen smaller
        than min_length unless the rule length is smaller than min_length in
        which case it is never considered small.
        """
        if self.rule.length <= min_length:
            return False
        return self.ilen() < min_length

    def query_positions(self, offset=0):
        """
        Return a set of unique matched query positions.
        Subtract offset from positions if provided.
        """
        return set([i + offset for i in self.qspan])


def query_positions(matches, offset=0):
    """
    Return a set of unique matched query positions for a list of matches.
    Subtract offset from positions if provided.
    """
    return matches and reduce(or_, (match.query_positions(offset) for match in matches)) or set()


def filter_matches(matches):
    """
    Return a filtered list of LicenseMatch given a `matches` list of
    LicenseMatch by removing duplicated or superfluous matches based on matched
    positions relation such as sequence, containment, touch, overlap, same
    licensing.

    Matches that are entirely contained in another bigger match are removed.
    When more than one matched position matches the same license(s), only one
    match of this set is kept.
    """
    matches = sorted(matches, key=lambda m: (m.qstart, -m.ilen()))

    if DEBUG_FILTER: print('filter_matches: number of matches to process:', len(matches))

    # compare two matches in the sorted sequence: this_match and the next one
    i = 0
    while i < len(matches) - 1:
        this_match = matches[i]
        if DEBUG_FILTER: print('filter_match: this_match:', this_match)

        j = i + 1

        while j < len(matches):
            next_match = matches[j]
            if DEBUG_FILTER: print(' filter_match: next_match:', next_match)

            # Skip strict duplicates
            if next_match.same(this_match):
                if DEBUG_FILTER: print('   filter_matches: next_match.same')
                del matches[j]
                continue

            # Skip qcontained, irrespective of licensing
            if this_match.contains_qspan(next_match):
                if DEBUG_FILTER: print('   filter_matches: next_match in this_match')
                del matches[j]
                continue

            # if the next_match overlaps, merge it in this_match and delete it
            if (this_match.same_rule(next_match) and this_match.qoverlap(next_match)):
                if DEBUG_FILTER: print('   filter_matches: mergeable same rule')
                this_match = this_match.update(next_match)
                matches[i] = this_match
                del matches[j]
                continue

            # Skip fully qcontained in this match and next next match, irrespective of licensing
            if j + 1 < len(matches):
                next_next_match = matches[j + 1]
                this_and_next_next_qspan = this_match.qspan | next_next_match.qspan
                if next_match.qspan.issubset(this_and_next_next_qspan):
                    if DEBUG_FILTER: print('   filter_matches: next_match qspan in (this_match+next_next_match)')
                    del matches[j]
                    continue

            # if the next_match overlaps, merge it in this_match and delete it
            if (this_match.same_licensing(next_match) and this_match.qoverlap(next_match)):
                if DEBUG_FILTER: print('   filter_matches: mergeable same licensing')
                this_match = this_match.update(next_match)
                matches[i] = this_match
                del matches[j]
                continue

            # otherwise check the next after next_match
            else:
                j += 1
        # otherwise use the next as the new reference match
        i += 1

    return matches


def filter_low_scoring_matches(matches, min_score=100):
    """
    Return a new matches iterable filtering matches that are sparse with a low
    density of matched positions. Also return the matches that were filtered out.
    """
    kept = []
    discarded = []

    for match in matches:
        if match.normalized_score() >= min_score:
            kept.append(match)
        else:
            discarded.append(match)

    return kept, discarded


def filter_short_matches(matches, min_length=0):
    """
    Return a new matches iterable filtering matches shorter a minimal length
    using ipos. Never filter matches with a rule length shorter than the minimal
    length. Also return the matches that were filtered out.
    """
    kept = []
    discarded = []

    if not min_length:
        return list(matches), discarded

    for match in matches:
        if not match.small(min_length=min_length):
            kept.append(match)
        else:
            discarded.append(match)

    return kept, discarded


def filter_sparse_matches(matches, min_density=0.33):
    """
    Return a new matches iterable filtering matches that are sparse with a low
    density of matched positions. Also return the matches that were filtered out.
    """
    kept = []
    discarded = []

    for match in matches:
        density = match.density()
        if density >= match.minimum_density() and density >= min_density:
            kept.append(match)
        else:
            discarded.append(match)

    return kept, discarded


def filter_spurious_matches(matches, idx):
    """
    Return a new matches sequence filtering spurious matches. Also return the
    matches that were filtered out.
    Spurious matches are sparse and short matches that are false positive. 
    """
    kept = []
    discarded = []

    minimum_density = 0.33
    for match in matches:
        rule = match.rule
        rule_high_len = rule.high_length
        rule_low_len = rule.low_length
        rule_len = rule.tid_length
        rule_gaps = rule.gaps

        rule_min_density = rule_minimum_density()
        match_density = match.density()

        # Is the match too sparse to be relevant?
        #   Do we have gaps at expected gaps positions?
        # Is the rule so short that it should be a high density match?
        # Does the rule have enough good tokens matched to be relevant?

        if match_density >= rule_minimum_density and match_density >= minimum_density:
            kept.append(match)
        else:
            discarded.append(match)

    return kept, discarded


def rule_minimum_density(rule):
    """
    Return the minimum density as a float between 0 and 1 that this match
    should have to be considered as a good match.
    
    The rationale is that for some small rules with very few tokens, it does
    not make sense to consider sparse matches at all unless their density is
    high.
    
    For example, a rule with this text: 
        Apache-1.1
    should not be matched to this query:    
        This Apache component was released as v1.1 in 2015.
    """

    rule_len = rule.length

    # set as the biggest of 1/10th the length or the ngram length
    smallest_gap = max([round(rule_len / 10), NGRAM_LENGTH])

    # not more than max_gap
    gap_length = min([smallest_gap, MAX_GAP])

    # for a rule with no gaps and a length of 4 or less, the minimum density is 1.
    return rule_len / (rule_len + (rule.gaps_count * gap_length))



def refine_matches(matches, max_dist, min_length, min_density, min_score):
    """
    Return two sequences of matches: one contains refined good matches, and the
    other contains matches that were filtered out.
    """
    if DEBUG_REFINE: map(logger_debug, matches)

    if DEBUG: logger_debug('   #####_match: matches: ALL matches simplified#', len(matches))
    if DEBUG_REFINE: map(logger_debug, matches)

    matches = LicenseMatch.merge(matches, max_dist=max_dist)

    matches = filter_matches(matches)

    logger_debug('   ##### _match: filtered_matches#:', len(matches))
    if DEBUG_REFINE: map(logger_debug, matches)

    all_discarded = []

    logger_debug('   #####_match: MERGED #:', len(matches))
    if DEBUG_REFINE: map(logger_debug, matches)

    matches, discarded = filter_sparse_matches(matches, min_density=min_density)
    all_discarded.extend(discarded)

    if DEBUG: logger_debug('   #####_match: after sparse filter#', len(matches))
    if DEBUG_REFINE: map(logger_debug, matches)

    matches, discarded = filter_short_matches(matches, min_length=min_length)
    all_discarded.extend(discarded)

    if DEBUG: logger_debug('   #####: after filter_short_matches#', len(matches))
    if DEBUG_REFINE: map(logger_debug, matches)

    matches, discarded = filter_low_scoring_matches(matches, min_score=min_score)
    all_discarded.extend(discarded)

    if DEBUG: logger_debug('   #####_match: after filter_low_scoring_matches#', len(matches))
    if DEBUG_REFINE: map(logger_debug, matches)

    if DEBUG: logger_debug('   ###_match: FINAL matches#:', len(matches))
    if DEBUG_REFINE: map(logger_debug, matches)

    return matches, all_discarded
