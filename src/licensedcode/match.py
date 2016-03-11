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

from functools import total_ordering
from itertools import groupby
from itertools import izip

from licensedcode.whoosh_spans import spans
from licensedcode.whoosh_spans.spans import Span
from licensedcode import NGRAM_LENGTH
from licensedcode import MAX_GAP


DEBUG = False
DEBUG_REPR = False
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


@total_ordering
class LicenseMatch(object):
    """
    License detection match to a rule with matched query positions and lines and
    matched index positions. Also computes a score for match. At a high level, a
    match behaves a bit like a Span and has several similar methods taking into
    account not a single span but the aligned query and index spans and regions.
    """

    __slots__ = 'rule', 'qspans', 'qregion', 'ispans', 'iregion', 'lines' , '_type', '_merged', '_ilen'

    def __init__(self, rule, qspans, ispans, line_by_pos=None, merge_spans=False, _type=''):
        """
        Create a new match from:
         - rule: matched Rule object
         - qspans: query text matched Spans list, start at zero.
         - qregion: query text maximal matched region as a single span.
         - ispans: rule text matched Spans list, start at zero.
         - iregion: rule text maximal matched region as a single span.
         - line_by_pos: mapping of (query positions -> line numbers). Line numbers start at one.
           Optional: if not provided, the `lines` spans will be Span(0) and no line information will be available.
         - merge_spans: if True, the ispans and qspans are also merged.
         - _type: a string indicating which matching procedure this match was created with. Used for debugging and testing only.
        """
        self.rule = rule

        # note: spans are not merged nor sorted by default
        if merge_spans:
            self.qspans = tuple(Span.merge(qspans))
            self.ispans = tuple(Span.merge(ispans))
        else:
            self.qspans = tuple(qspans)
            self.ispans = tuple(ispans)

        def _region(spans):
            # FIXME: we are iterating a tuple of TWO values: end and start
            starts, ends = izip(*spans)
            return Span(min(starts), max(ends))

        self.qregion = _region(self.qspans)
        self.iregion = _region(self.ispans)

        # cached index side match length
        self._ilen = None

        # span of lines for the query region
        if line_by_pos:
            self.lines = Span(line_by_pos[self.qregion.start], line_by_pos[self.qregion.end])
        else:
            self.lines = Span(0)

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
            qregion=self.qregion,
            iregion=self.iregion,
            qspans=self.qspans,
            ispans=self.ispans,
            lines=self.lines,
            _type=self._type,
            density=round(self.density(), 2),
        )
        if DEBUG_REPR:
            return ('''LicenseMatch<%(rule_id)r, %(rule_licenses)r, s=%(nscore)r, l=%(ilen)r, d=%(density)r, qs=%(qregion)r, ir=%(iregion)r, ln=%(lines)r, %(_type)r
            qspans=%(qspans)r
            ispans=%(ispans)r''' % data)
        else:
            return ('LicenseMatch<%(rule_id)r, %(rule_licenses)r, s=%(nscore)r, l=%(ilen)r, d=%(density)r, qr=%(qregion)r, ir=%(iregion)r, ln=%(lines)r, %(_type)r>' % data)

    def __eq__(self, other):
        """
        Strict equality.
        """
        return (isinstance(other, LicenseMatch)
            and self.rule == other.rule
            and self.qspans == other.qspans
            and self.ispans == other.ispans
            and self.lines == other.lines)

    def __copy__(self):
        """
        Return a shallow copy of self.
        """
        copied = LicenseMatch(self.rule, self.qspans[:], self.ispans[:], merge_spans=False, _type=self._type)
        copied.lines = Span(self.lines.start, self.lines.end)
        return copied

    def __lt__(self, match):
        """
        Only consider qregion for ordering
        """
        return self.qregion < match.qregion

    def __hash__(self):
        """
        Matches are hashable.
        """
        return hash((self.rule, tuple(self.qspans), tuple(self.ispans), self.lines))

    def __contains__(self, match):
        """
        Return True if every other qspans are contained in any self qspans.
        """
        return self.contains_qspans(match) and self.contains_ispans(match)

    def contains_qregion(self, match):
        return match.qregion in self.qregion

    def contains_iregion(self, match):
        return match.iregion in self.iregion

    def contains_qspans(self, match):
        return spans.contained(self.qspans, match.qspans)

    def contains_ispans(self, match):
        return spans.contained(self.ispans, match.ispans)

    def contains_spans(self, match):
        """
        Return True if all other match qspans and ispans are contained in this match qspans and ispans.
        """
        return self.contains_qspans(match) and self.contains_ispans(match)

    def qdistance_to(self, match):
        """
        Return the absolute qregion distance to other match.
        Touching and overlapping matches have a zero distance.
        """
        return self.qregion.distance_to(match.qregion)

    def idistance_to(self, match):
        """
        Return the absolute iregion distance from self to other match.
        Touching and overlapping matches have a zero distance.
        """
        return self.iregion.distance_to(match.iregion)

    def qoverlap(self, match):
        return self.qregion.overlap(match.qregion)

    def ioverlap(self, match):
        return self.iregion.overlap(match.iregion)

    def overlap(self, match):
        """
        Return True if this match regions both overlap with other match regions.
        """
        return self.qoverlap(match) and self.ioverlap(match)

    def qtouch(self, match):
        return self.qregion.touch(match.qregion)

    def itouch(self, match):
        return self.iregion.touch(match.iregion)

    def touch(self, match):
        """
        Return True if this match regions both touch other match regions.
        """
        return self.qtouch(match) and self.itouch(match)

    def qsurround(self, match):
        return self.qregion.surround(match.qregion)

    def isurround(self, match):
        return self.iregion.surround(match.iregion)

    def surround(self, match):
        """
        Return True if this match regions both surround (without touching) other match regions.
        """
        return self.qsurround(match) and self.isurround(match)

    def is_qbefore(self, match):
        return self.qregion.is_before(match.qregion)

    def is_qbefore_or_touch(self, match):
        return self.qregion.is_before_or_touch(match.qregion)

    def is_ibefore(self, match):
        return self.iregion.is_before(match.iregion)

    def is_ibefore_or_touch(self, match):
        return self.iregion.is_before_or_touch(match.iregion)

    def is_before(self, match):
        """
        Return True if this match regions are strictly before other match regions.
        """
        return self.is_qbefore(match) and self.is_ibefore(match)

    def is_qafter(self, match):
        return self.qregion.is_after(match.qregion)

    def is_qafter_or_touch(self, match):
        return self.qregion.is_after_or_touch(match.qregion)

    def is_iafter(self, match):
        return self.iregion.is_after(match.iregion)

    def is_iafter_or_touch(self, match):
        return self.iregion.is_after_or_touch(match.iregion)

    def is_after(self, match):
        """
        Return True if this match regions are strictly after other match regions.
        """
        return self.is_qafter(match) and self.is_iafter(match)

    def is_after_or_touch(self, match):
        return self.is_qafter_or_touch(match) and self.is_iafter_or_touch(match)

    def simplify(self):
        """
        Simplify match by merging mergeable qspans and ispans.
        """
        self.qspans = tuple(Span.merge(self.qspans))
        self.ispans = tuple(Span.merge(self.ispans))

    @staticmethod
    def merge(matches, merge_spans=False, max_dist=15):
        """
        Merge overlapping, touching or close-by matches in the given iterable of
        matches. Return a new list of merged matches if they can be merged.
        Matches that cannot be merged are returned as-is. 
        
        Only matches for the same rules can be merged.
        
        The overlap and touch is considered using both the qregion and iregion.
        
        The maximal merge is always returned and eventually a single match per
        rule is returned if all matches for that rule can be merged.
        
        For being merged two matches must also be in increasing query and index positions.

        `merge_spans` is a flag to also merge ispans and qspans in all returned
        matches.
        """
        # FIXME: longer and denser matches starting at the same qregion should
        # be sorted first

        matches = sorted(matches, key=lambda m: (m.rule.rid, m.qregion))
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
                             and next_match.iregion.start > this_match.iregion.start
                             and next_match.iregion.end > this_match.iregion.end
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
                        this_match = this_match.update(next_match, merge_spans=merge_spans)
                        rule_matches[i] = this_match
                        del rule_matches[j]

                    # otherwise check the next after next_match
                    else:
                        j += 1
                # otherwise use the next as the new reference match
                i += 1
            merged.extend(rule_matches)
        return merged

    def combine(self, match, merge_spans=False):
        """
        Return a new match combining self and an other match.
        """
        same_rule = self.rule == match.rule
        same_licensing = self.same_licensing(match)
        assert same_rule or same_licensing, 'Cannot combine matches with different rules or licensing: from: %(self)r, to: %(match)r' % locals()
        combined = LicenseMatch(self.rule, self.qspans + match.qspans, self.ispans + match.ispans, merge_spans=merge_spans)

        # combine and set lines spans (we cannot pass it to the initializer as we do not have it stored in a match)
        combined.lines = self.lines.to(match.lines)
        if match._type not in self._type:
            combined._type = ' '.join([self._type, match._type])
        else:
            combined._type = self._type

        # keep track of merged
        # combined._merged = self._merged + match._merged + [copy(self), copy(match)]
        return combined

    def update(self, match, merge_spans=False):
        """
        Update self with other match and return self.
        """
        combined = self.combine(match, merge_spans=merge_spans)
        self.qspans = combined.qspans
        self.ispans = combined.ispans
        self.qregion = combined.qregion
        self.iregion = combined.iregion
        self.lines = combined.lines
        self._type = combined._type
        self._ilen = None
        return self

    def ilen(self):
        """
        Return the length of the match as the number of matched index tokens.
        """
        if self._ilen is None:
            # self.ispans = tuple(Span.merge(self.ispans))
            self._ilen = sum(len(span) for span in self.ispans)
        return self._ilen

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
        return self.ilen() / float(self.rule.length)

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
        dense match has all ispans contiguous and has a maximum density of one.
        A sparse match has some non-contiguous ispans.

        Density is not related to the score: a low scoring match can be dense
        and a high scoring match can be sparse.

        The density is computed as the ratio of ilen (effective number of
        matched itokens) to the length of the qregion (actual maximal range of
        positions for this match).
        """
        dens = self.ilen() / float(len(self.qregion))
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

        rule_len = float(self.rule.length)

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

    def almost_same(self, other):
        """
        Return True if other has the same licensing, a close score and the same regions (not spans).
        """
        return self.same_licensing(other) and self.close_score(other) and self.same_regions(other)

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

    def close_score(self, other, threshold=0.1):
        """
        Return True if other has a score close to self where close is defined as
        having an absolute difference less than a threshold.
        """
        return abs(self.score() - other.score()) <= threshold

    def same_qspans(self, other):
        return self.qspans == other.qspans

    def same_ispans(self, other):
        return self.ispans == other.ispans

    def same_spans(self, other):
        """
        Return True if other has the same qspans and ispans.
        """
        return self.same_qspans(other) and self.same_ispans(other)

    def same_regions(self, other):
        """
        Return True if other has the same regions.
        """
        return self.qregion == other.qregion and self.iregion == other.iregion

    def more_relevant_spans(self, other):
        """
        Return True if self is more relevant than other score-wise with same spans.
        """
        return self.same_spans(other) and self.score() > other.score()

    def more_relevant_regions(self, other):
        """
        Return True if self is more relevant than other score-wise with same regions.
        """
        return self.same_regions(other) and self.score() > other.score()

    def small(self, min_length=NGRAM_LENGTH):
        """
        Return True if this match is "small" meaning that it has an ilen smaller
        than min_length unless the rule length is smaller than min_length in
        which case it is never considered small.
        """
        if self.rule.length <= min_length:
            return False
        return self.ilen() < min_length


def build_match(hits, rule, line_by_pos, merge_spans=False, _type=None):
    """
    Return a match from a hits list, a rule and a mapping of qpos -> line
    numbers.
    """
    qhits, ihits = izip(*hits)
    qspans, ispans = Span.from_ints(qhits), Span.from_ints(ihits)
    return LicenseMatch(rule, qspans, ispans, line_by_pos, merge_spans=merge_spans, _type=_type)


def filter_matches(matches, merge_spans=False):
    """
    Return a filtered list of LicenseMatch given a `matches` list of
    LicenseMatch by removing duplicated or superfluous matches based on matched
    positions relation such as sequence, containment, touch, overlap, same
    licensing.

    Matches that are entirely contained in another bigger match are removed.
    When more than one matched position matches the same license(s), only one
    match of this set is kept.
    """

    matches = sorted(matches, key=lambda m: (m.qregion.start, -m.ilen()))

    if DEBUG_FILTER:
        print('filter_matches: number of matches to process:', len(matches))

    i = 0

    # compare two matches in the sorted sequence: this_match and the next one
    while i < len(matches) - 1:
        this_match = matches[i]
        # this_match.simplify()
        if DEBUG_FILTER:
            print('filter_match: this_match:', this_match)

        j = i + 1

        while j < len(matches):
            next_match = matches[j]
            # note: this is essential to compare spans
            # next_match.simplify()
            if DEBUG_FILTER:
                print(' filter_match: next_match:', next_match)

            # Skip strict duplicates
            if next_match.same(this_match):
                if DEBUG_FILTER:
                    print('   filter_matches: next_match.same')
                del matches[j]
                continue

            # Skip qcontained, irrespective of licensing
            if this_match.contains_qspans(next_match):
                if DEBUG_FILTER:
                    print('   filter_matches: next_match in this_match')
                del matches[j]
                continue

            # if the next_match overlaps, merge it in this_match and delete it
            if (this_match.same_rule(next_match) and this_match.qoverlap(next_match)):
                if DEBUG_FILTER:
                    print('   filter_matches: mergeable same rule')
                this_match = this_match.update(next_match, merge_spans=merge_spans)
                matches[i] = this_match
                del matches[j]
                continue

            # Skip fully qcontained in this match and next next match, irrespective of licensing
            if j + 1 < len(matches):
                next_next_match = matches[j + 1]
                this_and_next_next_qspans = this_match.qspans + next_next_match.qspans
                if spans.contained(this_and_next_next_qspans, next_match.qspans):
                    if DEBUG_FILTER:
                        print('   filter_matches: next_match qspans in (this_match+next_next_match)')
                    del matches[j]
                    continue

            # if the next_match overlaps, merge it in this_match and delete it
            if (this_match.same_licensing(next_match) and this_match.qoverlap(next_match)):
                if DEBUG_FILTER:
                    print('   filter_matches: mergeable same licensing')
                this_match = this_match.update(next_match, merge_spans=merge_spans)
                matches[i] = this_match
                del matches[j]
                continue

            # otherwise check the next after next_match
            else:
                j += 1
        # otherwise use the next as the new reference match
        i += 1

    return matches


def filter_spurious_matches(matches, min_score=100, min_length=0, min_density=0.33):
    """
    Return a matches sequence filtered from spurious matches and a sequence of
    filtered matches.
    """


def filter_low_scoring_matches(matches, min_score=100):
    """
    Return a new matches iterable filtering matches that are sparse with a low
    density of matched positions.
    """
    return [match for match in matches if match.normalized_score() >= min_score]


def filter_short_matches(matches, min_length=0):
    """
    Return a new matches iterable filtering matches shorter a minimal length
    using ipos. Never filter matches with a rule length shorter than the minimal
    length.
    """
    if not min_length:
        return list(matches)
    return [match for match in matches if not match.small(min_length=min_length)]


def filter_sparse_matches(matches, min_density=0.33):
    """
    Return a new matches iterable filtering matches that are sparse with a low
    density of matched positions.
    """
    filtered = []
    for match in matches:
        density = match.density()
        if density >= match.minimum_density() and density >= min_density:
            filtered.append(match)
    return filtered
