#
# Copyright (c) 2016 nexB Inc. and others. All rights reserved.
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
from functools import partial
from functools import total_ordering
from hashlib import md5
from itertools import chain
from itertools import groupby
import textwrap

from licensedcode import query
from licensedcode.spans import Span
from licensedcode import cache
from licensedcode import MAX_DIST

"""
LicenseMatch data structure and matches merging and filtering routines.
"""

TRACE = True
TRACE_SPAN_DETAILS = True
TRACE_FILTER = True
TRACE_MERGE = True
TRACE_MERGE_TEXTS = True
TRACE_REFINE = True
TRACE_REFINE_SMALL = True
TRACE_REFINE_SOLID = True


def logger_debug(*args): pass

if TRACE:
    import logging
    import sys

    logger = logging.getLogger(__name__)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, basestring) and a or repr(a) for a in args))

    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)


# When soring matches for merging or refining, we divide starts and length by
# ROUNDING with an intergerb division to round values in coarse bands
ROUNDING = 10


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

    __slots__ = 'rule', 'qspan', 'ispan', 'hispan', 'line_by_pos' , 'query_run_start', 'matcher'

    # containment relationships and thresholds between two matches
    CONTAINMENT_SMALL = 0.1
    CONTAINMENT_MEDIUM = 0.5
    CONTAINMENT_LARGE = 0.8

    def __init__(self, rule, qspan, ispan, hispan=None, line_by_pos=None, query_run_start=0, matcher=''):
        """
        Create a new match from:
         - rule: matched Rule object
         - qspan: query text matched Span, start at zero which is the absolute query start (not the query_run start).
         - ispan: rule text matched Span, start at zero which is the rule start.
         - hispan: rule text matched Span for high tokens, start at zero which is the rule start. Always a subset of ispan.
         - line_by_pos: mapping of (query positions -> line numbers). Line numbers start at one.
           Optional: if not provided, the `lines` start and end tuple will be (0, 0) and no line information will be available.
         - matcher: a string indicating which matching procedure this match was created with. Used for debugging and testing only.

         Note that the relationship between is the qspan and ispan is such that:
         - they always have the exact same number of items but when sorted each value at an index may be different
         - the nth position when sorted by position is such that their token value is equal for this position
        """
        self.rule = rule
        self.qspan = qspan
        self.ispan = ispan
        if hispan is None:
            hispan = Span()
        self.hispan = hispan
        self.line_by_pos = line_by_pos or {}
        self.query_run_start = query_run_start
        self.matcher = matcher

    def __repr__(self, trace=TRACE_SPAN_DETAILS):

        spans = ''
        if trace:
            hispan = self.hispan
            qspan = self.qspan
            ispan = self.ispan
            spans = ', qspan=%(qspan)r, ispan=%(ispan)r, hispan=%(hispan)r' % locals()

        rep = dict(
            matcher=self.matcher,
            spans=spans,
            rule_id=self.rule.identifier,
            licenses=', '.join(self.rule.licenses),
            choice=self.rule.license_choice,
            score=self.score(),
            qlen=self.qlen(),
            ilen=self.ilen(),
            hilen=self.hilen(),
            qreg=(self.qstart, self.qend),
            rlen=self.rule.length,
            ireg=(self.istart, self.iend),
            lines=self.lines(),
        )
        return ('LicenseMatch<%(matcher)r, lines=%(lines)r, '
                '%(rule_id)r, %(licenses)r, choice=%(choice)r, '
                'score=%(score)r, qlen=%(qlen)r, ilen=%(ilen)r, hilen=%(hilen)r, rlen=%(rlen)r, '
                'qreg=%(qreg)r, ireg=%(ireg)r'
                '%(spans)s>') % rep

    def __eq__(self, other):
        """
        Strict equality is based on licensing not matched rule.
        """
        return (isinstance(other, LicenseMatch)
            and self.same_licensing(other)
            and self.qspan == other.qspan
            and self.ispan == other.ispan
        )

    def same_licensing(self, other):
        """
        Return True if other has the same licensing.
        """
        return self.rule.same_licensing(other.rule)

    def licensing_contains(self, other):
        """
        Return True if other licensing is contained is this match licensing.
        """
        return self.rule.licensing_contains(other.rule)

    @property
    def qstart(self):
        return self.qspan.start

    def __lt__(self, other):
        return self.qstart < other.qstart

    @property
    def qend(self):
        return self.qspan.end

    def qlen(self):
        """
        Return the length of the match as the number of matched query tokens.
        """
        return len(self.qspan)

    @property
    def istart(self):
        return self.ispan.start

    @property
    def iend(self):
        return self.ispan.end

    def ilen(self):
        """
        Return the length of the match as the number of matched index tokens.
        """
        return len(self.ispan)

    @property
    def histart(self):
        return self.hispan.start

    def hilen(self):
        """
        Return the length of the match as the number of matched query tokens.
        """
        return len(self.hispan)

    def lines(self):
        """
        Return a tuple of start and end line for this match.
        """
        return self.line_by_pos.get(self.qstart, 0), self.line_by_pos.get(self.qend, 0)

    def __contains__(self, other):
        """
        Return True if qspan contains other.qspan and ispan contains other.ispan.
        """
        return other.qspan in self.qspan and other.ispan in self.ispan

    def qcontains(self, other):
        """
        Return True if qspan contains other.qspan.
        """
        return other.qspan in self.qspan

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

    def overlap(self, other):
        """
        Return the number of overlaping positions with other.
        """
        return self.qspan.overlap(other.qspan)

    def overlap_ratio(self, other):
        """
        Return a float ratio representing the proportion of overlaping query
        positions with other compared with self number of query positions. This is an
        indication of containment.
        """
        return self.overlap(other) / self.qlen()

    def coverage(self):
        """
        Return the coverage of this match to the matched rule as a float between 0 and 1.
        """
        if not self.rule.length:
            return 0
        return self.ilen() / self.rule.length

    def score(self):
        """
        Return the score for this match as a float between 0 and 100.

        This is a ratio of matched tokens to the rule length and an indication of
        coverage of match with respect to the matched rule.
        """
        # TODO: compute a better score based tf/idf, BM25, applying ratio to low tokens, etc
        return round(self.coverage() * 100, 2)

    def surround(self, other):
        """
        Return True if this match query span surrounds other other match query span.

        This is different from containment. A matched query region can surround
        another matched query region and have no positions in common with the
        surrounded match.
        """
        return self.qstart <= other.qstart and self.qend >= other.qend

    def is_after(self, other):
        """
        Return True if this match spans are strictly after other match spans.
        """
        return self.qspan.is_after(other.qspan) and self.ispan.is_after(other.ispan)

    def subtract(self, other):
        """
        Subtract an other match from this match by removing overlapping span
        items present in both matches from this match.
        """
        self.qspan.difference_update(other.qspan)
        self.ispan.difference_update(other.ispan)
        return self

    def combine(self, other):
        """
        Return a new match combining self and an other match.
        """
        if self.rule != other.rule:
            raise TypeError('Cannot combine matches with different rules: from: %(self)r, to: %(other)r' % locals())

        if other.matcher not in self.matcher:
            newmatcher = ' '.join([self.matcher, other.matcher])
        else:
            newmatcher = self.matcher

        line_by_pos = dict(self.line_by_pos)
        line_by_pos.update(other.line_by_pos)

        combined = LicenseMatch(rule=self.rule,
                                qspan=Span(self.qspan | other.qspan),
                                ispan=Span(self.ispan | other.ispan),
                                hispan=Span(self.hispan | other.hispan),
                                line_by_pos=line_by_pos,
                                query_run_start=min(self.query_run_start, other.query_run_start),
                                matcher=newmatcher)
        return combined

    def update(self, other):
        """
        Update self with other match and return self.
        """
        combined = self.combine(other)
        self.qspan = combined.qspan
        self.ispan = combined.ispan
        self.hispan = combined.hispan
        self.line_by_pos = combined.line_by_pos
        self.matcher = combined.matcher
        self.query_run_start = min(self.query_run_start, other.query_run_start)
        return self

    def rebase(self, new_query_start, new_query_end, line_by_pos, matcher):
        """
        Return a copy of this match with a new qspan and new line_by_pos and
        updating the matcher of match as needed.
        """
        offset = new_query_start - self.query_run_start
        return LicenseMatch(
            rule=self.rule,
            qspan=self.qspan.rebase(offset),
            ispan=Span(self.ispan),
            hispan=Span(self.hispan),
            line_by_pos=line_by_pos,
            query_run_start=new_query_start,
            matcher=' '.join([self.matcher.replace(cache.MATCH_CACHE, '').strip(), matcher]),
        )

    def small(self):
        """
        Return True if this match is "small" based on its rule thresholds.
        """
        thresholds = self.rule.thresholds()
        min_ihigh = thresholds.min_high
        min_ilen = thresholds.min_len
        hilen = self.hilen()
        ilen = self.ilen()
        if TRACE_REFINE_SMALL:
            logger_debug('LicenseMatch.small(): hilen=%(hilen)r < min_ihigh=%(min_ihigh)r or ilen=%(ilen)r < min_ilen=%(min_ilen)r : thresholds=%(thresholds)r' % locals(),)
        if thresholds.small and self.score() < 50 and (hilen < min_ihigh or ilen < min_ilen):
            return True
        if hilen < min_ihigh or ilen < min_ilen:
            return True

    def false_positive(self, idx):
        """
        Return a false positive rule id if the LicenseMatch match is a false
        positive or None otherwise (nb: not False).
        Lookup the matched tokens sequence against the idx index.
        """
        ilen = self.ilen()
        if ilen > idx.largest_false_positive_length:
            return
        rule_tokens = idx.tids_by_rid[self.rule.rid]
        ispan = self.ispan
        matched_itokens = array('h', (tid for ipos, tid in enumerate(rule_tokens) if ipos in ispan))
        # note: hash computation is inlined here but MUST be the same code as in match_hash
        matched_hash = md5(matched_itokens.tostring()).digest()
        return idx.false_positive_rid_by_hash.get(matched_hash)


def merge_matches(matches, max_dist=MAX_DIST):
    """
    Merge matches to the same rule in a sequence of matches. Return a new list
    of merged matches if they can be merged. Matches that cannot be merged are
    returned as-is.
    For being merged two matches must also be in increasing query and index positions.
    """

    if len(matches) < 2:
        return matches

    # only merge matches with the same rule: sort then group by rule
    # for the same rule, sort on start, longer high, longer match, matcher type
    sorter = lambda m: (m.rule.identifier, m.qspan.start, -m.hilen(), -m.qlen(), m.matcher)
    all_matches = sorted(matches, key=sorter)


    matches_by_rule = [(rid, list(rule_matches)) for rid, rule_matches
                        in groupby(all_matches, key=lambda m: m.rule.identifier)]

    if TRACE_MERGE: print('merge_matches: number of matches to process:', len(matches))

    merged = []
    for rid, matches in matches_by_rule:
        if TRACE_MERGE: logger_debug('merge_matches: processing rule:', rid)

        # compare two matches in the sorted sequence: current and next
        i = 0
        while i < len(matches) - 1:
            current_match = matches[i]
            if TRACE_MERGE: logger_debug('---> merge_matches: current:', current_match)

            j = i + 1
            while j < len(matches):
                next_match = matches[j]
                if TRACE_MERGE: logger_debug('   ---> merge_matches: next:', next_match)

                # remove contained matches
                if current_match.qcontains(next_match):
                    if TRACE_MERGE: logger_debug('    ---> ###merge_matches: next contained in current')
                    del matches[j]
                    j += 1
                    continue

                # remove contained matches
                if next_match.qcontains(current_match):
                    if TRACE_MERGE: logger_debug('    ---> ###merge_matches: current contained in next ')
                    del matches[i]
                    break

                # merge surrounded
                if current_match.surround(next_match):
                    current_match.update(next_match)
                    if TRACE_MERGE: logger_debug('    ---> ###merge_matches: current surrounds next, merged as new:')
                    del matches[j]
#                     j += 1
                    continue

                # merge surrounded the other way too, updating current
                if next_match.surround(current_match):
                    current_match.update(next_match)
                    if TRACE_MERGE: logger_debug('    ---> ###merge_matches: next surrounds current, merged as new:', current_match)
                    del matches[i]
                    break

                # next_match is strictly in increasing sequence
                if next_match.is_after(current_match):
                    current_match.update(next_match)
                    if TRACE_MERGE: logger_debug('    ---> ###merge_matches: next follows current, merged as new:', current_match)
                    del matches[j]
#                     j += 1
                    continue

                # next_match overlaps in some increasing sequence with overlap
                if (current_match.qstart <= next_match.qstart
                and current_match.qend <= next_match.qend
                and current_match.overlap(next_match)):
                    current_match.update(next_match)
                    if TRACE_MERGE: logger_debug('    ---> ###merge_matches: next overlaps in sequence current, merged as new:', current_match)
                    del matches[j]
#                     j += 1
                    continue

                j += 1
            i += 1
        merged.extend(matches)
    return merged


def filter_contained_matches(matches):
    """
    Return a filtered list of LicenseMatch given a `matches` list of LicenseMatch by
    removing duplicated or superfluous matches using containment relationships.
    Works across all matches.

    For instance a match entirely contained in another bigger match is removed. When
    more than one matched position matches the same license(s), only one match of
    this set is kept.
    """
    discarded = []

    if len(matches) < 2:
        return matches, discarded

    # sort on start, longer high, longer match, matcher type
    sorter = lambda m: (m.qspan.start, -m.hilen(), -m.qlen(), m.matcher)
    matches = sorted(matches, key=sorter)

    if TRACE_FILTER: print('filter_contained_matches: number of matches to process:', len(matches))


    # compare two matches in the sorted sequence: current and next match
    i = 0
    while i < len(matches) - 1:
        current_match = matches[i]
        if TRACE_FILTER: logger_debug('---> filter_contained_matches: current:', current_match)
        j = i + 1
        while j < len(matches):
            next_match = matches[j]
            if TRACE_FILTER: logger_debug('   ---> filter_contained_matches: next:', next_match)

            # remove contained matches
            if current_match.qcontains(next_match):
                if TRACE_FILTER: logger_debug('    ---> ###filter_contained_matches: next contained in current, removed next')
                discarded.append(next_match)
                del matches[j]
                continue

            # remove contained matches the other way
            if next_match.qcontains(current_match):
                if TRACE_FILTER: logger_debug('    ---> ###filter_contained_matches: current contained in next, removed current')
                discarded.append(current_match)
                del matches[i]
                continue

            # handle overlapping matches: determine overlap and containment relationship
            overlap = current_match.overlap(next_match)
            # overlap_ratio_to_current = overlap / current_match.qlen()
            overlap_ratio_to_next = overlap / next_match.qlen()

            # next match overlap to current
            large_next = overlap_ratio_to_next >= LicenseMatch.CONTAINMENT_LARGE
            medium_next = overlap_ratio_to_next >= LicenseMatch.CONTAINMENT_MEDIUM
            small_next = overlap_ratio_to_next >= LicenseMatch.CONTAINMENT_SMALL

            if TRACE_FILTER: logger_debug('  ---> ###filter_contained_matches: containment is:', (large_next and 'LARGE') or (medium_next and 'MEDIUM') or (small_next and 'SMALL') or 'NOT CONTAINED')

            if large_next:
                if TRACE_FILTER: logger_debug('    ---> ###filter_contained_matches: LARGE NEXT')
                if current_match.qlen() >= next_match.qlen():
                    if TRACE_FILTER: logger_debug('      ---> ###filter_contained_matches: LARGE next included, removed next')
                    discarded.append(next_match)
                    del matches[j]
                    continue
                else:
                    if TRACE_FILTER: logger_debug('      ---> ###filter_contained_matches: LARGE current included, removed current')
                    discarded.  append(current_match)
                    del matches[i]
                    continue

            elif medium_next:
                if TRACE_FILTER: logger_debug('    ---> ###filter_contained_matches: MEDIUM NEXT')
                contains_license = current_match.licensing_contains(next_match)
                if TRACE_FILTER: logger_debug('      ---> ###filter_contained_matches: next licensing is contained:', contains_license)
                if contains_license:
                    if current_match.qlen() >= next_match.qlen():
                        if TRACE_FILTER: logger_debug('      ---> ###filter_contained_matches: MEDIUM next included, removed next')
                        discarded.append(next_match)
                        del matches[j]
                        continue
                    else:
                        if TRACE_FILTER: logger_debug('      ---> ###filter_contained_matches: MEDIUM current included, removed current')
                        discarded.  append(current_match)
                        del matches[i]
                        continue

            elif (small_next and current_match.surround(next_match) and current_match.licensing_contains(next_match)):
                if TRACE_FILTER: logger_debug('    ---> ###filter_contained_matches: SMALL NEXT')
                if current_match.qlen() >= next_match.qlen():
                    if TRACE_FILTER: logger_debug('      ---> ###filter_contained_matches: SMALL next surrounded, removed next')
                    discarded.append(next_match)
                    del matches[j]
                    continue
            j += 1
        i += 1

    # FIXME: returned discarded too
    return matches, discarded


def filter_low_score(matches, min_score=100):
    """
    Return a list of matches scoring above `min_score` and a list of matches scoring below.
    """
    if not min_score:
        return matches, []

    kept = []
    discarded = []
    for match in matches:
        if match.score() < min_score:
            if TRACE_REFINE: logger_debug('    ==> DISCARDING small score:', match)
            discarded.append(match)
        else:
            kept.append(match)

    return kept, discarded


def filter_not_solid(matches):
    """
    Return a list of matches to solid rules that are not solid and a list of small matches.
    """
    kept = []
    discarded = []
    for match in matches:
        if match.rule.solid  and match.score() != 100:
            if TRACE_REFINE_SOLID: logger_debug('    ==> DISCARDING NOT SOLID:', 'solid:', match.rule.solid, 'score:', match.score(), match)
            discarded.append(match)
        else:
            if TRACE_REFINE_SOLID: logger_debug('  ===> NOT DISCARDING NOT SOLID:', 'solid:', match.rule.solid, 'score:', match.score(), match)
            kept.append(match)
    return kept, discarded


def filter_short_matches(matches):
    """
    Return a list of matches that are not small and a list of small matches.
    """
    kept = []
    discarded = []
    for match in matches:
        if (match.small()):  # and match.score() < SMALL_MATCH_MIN_SCORE):
            if TRACE_REFINE_SMALL: logger_debug('    ==> DISCARDING SHORT:', match)
            discarded.append(match)
        else:
            if TRACE_REFINE_SMALL: logger_debug('  ===> NOT DISCARDING SHORT:', match)
            kept.append(match)
    return kept, discarded


def filter_spurious_matches(matches):
    """
    Return a list of matches that are not spurious and a list of spurrious
    matches.
    """
    kept = []
    discarded = []

    for match in matches:
        qdens = match.qspan.density()
        idens = match.ispan.density()
        ilen = match.ilen()
        hilen = match.hilen()
        if (
           (ilen < 20 and hilen < 5 and (qdens < 0.3 or idens < 0.3))
        # or (ilen < 20 and qdens < 0.2 and idens < 0.2)
        # or (qdens < 0.1 and idens < 0.1)
           ):
            if TRACE_REFINE: logger_debug('    ==> DISCARDING Spurious:', match)
            discarded.append(match)
        else:
            kept.append(match)
    return kept, discarded


def filter_false_positive_matches(idx, matches):
    """
    Return a list of matches that are not false positives and a list of false
    positive matches given an index `idx`.
    """
    kept = []
    discarded = []
    for match in matches:
        fp = match.false_positive(idx)
        if fp is None:
#             if TRACE_REFINE: logger_debug('    ==> NOT DISCARDING FALSE POSITIVE:', match)
            kept.append(match)
        else:
            if TRACE_REFINE: logger_debug('    ==> DISCARDING FALSE POSITIVE:', match, 'fp rule:', idx.rules_by_rid[fp].identifier)
            discarded.append(match)
    return kept, discarded


def refine_matches(matches, idx, min_score=0, max_dist=MAX_DIST):
    """
    Return two sequences of matches: one contains refined good matches, and the
    other contains matches that were filtered out.
    """
    if TRACE: logger_debug()
    if TRACE: logger_debug(' #####refine_matches: STARTING matches#', len(matches))
    if TRACE_REFINE: map(logger_debug, matches)

    matches = merge_matches(matches, max_dist=max_dist)
    if TRACE: logger_debug('     ##### refine_matches: STARTING MERGED_matches#:', len(matches))

    all_discarded = []

    matches, discarded = filter_not_solid(matches)
    all_discarded.extend(discarded)

    matches, discarded = filter_short_matches(matches)
    all_discarded.extend(discarded)

    if TRACE: logger_debug('   #####refine_matches: NOT SHORT #', len(matches))
    if TRACE_REFINE: map(logger_debug, matches)
    if TRACE: logger_debug('   #####refine_matches: SHORT discarded#', len(discarded))
    if TRACE_REFINE: map(logger_debug, discarded)

    matches, discarded = filter_false_positive_matches(idx, matches)
    all_discarded.extend(discarded)
    if TRACE: logger_debug('   #####refine_matches: NOT FALSE POS #', len(matches))
    if TRACE_REFINE: map(logger_debug, matches)
    if TRACE: logger_debug('   #####refine_matches: FALSE POS discarded#', len(discarded))
    if TRACE_REFINE: map(logger_debug, discarded)

    matches, discarded = filter_spurious_matches(matches)
    all_discarded.extend(discarded)
    if TRACE: logger_debug('   #####refine_matches: NOT SPURIOUS#', len(matches))
    if TRACE_REFINE: map(logger_debug, matches)
    if TRACE: logger_debug('   #####refine_matches: SPURIOUS discarded#', len(discarded))
    if TRACE_REFINE: map(logger_debug, discarded)

    matches = merge_matches(matches, max_dist=max_dist)
    if TRACE: logger_debug(' #####refine_matches: before FILTER matches#', len(matches))
    if TRACE_REFINE: map(logger_debug, matches)

    matches, discarded = filter_contained_matches(matches)
    all_discarded.extend(discarded)
    logger_debug('   ##### refine_matches: NOT FILTERED matches#:', len(matches))
    if TRACE_REFINE: map(logger_debug, matches)
    if TRACE: logger_debug('   #####refine_matches: FILTERED discarded#', len(discarded))
    if TRACE_REFINE: map(logger_debug, discarded)

    if min_score:
        matches, discarded = filter_low_score(matches, min_score=min_score)
        all_discarded.extend(discarded)
        if TRACE: logger_debug('   #####refine_matches: NOT LOW SCORE #', len(matches))
        if TRACE_REFINE: map(logger_debug, matches)
        if TRACE: logger_debug('   ###refine_matches: LOW SCORE discarded #:', len(discarded))
        if TRACE_REFINE: map(logger_debug, discarded)

    matches = merge_matches(matches, max_dist=max_dist)

    logger_debug('   ##### refine_matches: FINAL MERGED_matches#:', len(matches))
    if TRACE_REFINE: map(logger_debug, matches)

    return matches, all_discarded


def get_texts(match, location=None, query_string=None, idx=None, width=120):
    """
    Given a match and a query location of query string return a tuple of wrapped
    texts at `width` for:

    - the matched query text as a string.
    - the matched rule text as a string.

    Used primarily to recover the matched texts for testing or reporting.

    Unmatched positions are represented as <no-match>. Punctuation is removed ,
    spaces are normalized (new line is replaced by a space), case is preserved.

    If `width` is a number superior to zero, the texts are wrapped to width.
    """
    return (get_matched_qtext(match, location, query_string, idx, width),
            get_match_itext(match, width))


def get_matched_qtext(match, location=None, query_string=None, idx=None, width=120, margin=0):
    """
    Return the matched query text as a wrapped string of `width` given a match,
    a query location or string and an index.

    Used primarily to recover the matched texts for testing or reporting.

    Unmatched positions are represented as <no-match>.
    Punctuation is removed , spaces are normalized (new line is replaced by a
    space), case is preserved.

    If `width` is a number superior to zero, the texts are wrapped to width.
    """
    return format_text(matched_query_tokens_str(match, location, query_string, idx), width=width, margin=margin)


def get_match_itext(match, width=120, margin=0):
    """
    Return the matched rule text as a wrapped string of `width` given a match.
    Used primarily to recover the matched texts for testing or reporting.
    Unmatched positions inside are represented as <no-match>.
    Punctuation is removed , spaces are normalized (new line is replaced by a space),
    case is preserved.

    If `width` is a number superior to zero, the texts are wrapped to width.
    """
    return format_text(matched_rule_tokens_str(match), width=width, margin=margin)


def format_text(tokens, width=120, no_match='<no-match>', margin=4):
    """
    Return a formatted text wrapped at `width` given an iterable of tokens.
    None tokens for unmatched positions are replaced with `no_match`.
    """
    nomatch = lambda s: s or no_match
    tokens = map(nomatch, tokens)
    noop = lambda x: [x]
    initial_indent = subsequent_indent = u' ' * margin
    wrapper = partial(textwrap.wrap, width=width, break_on_hyphens=False,
                      initial_indent=initial_indent,
                      subsequent_indent=subsequent_indent)
    wrap = width and wrapper or noop
    return u'\n'.join(wrap(u' '.join(tokens)))


def matched_query_tokens_str(match, location=None, query_string=None, idx=None):
    """
    Return an iterable of matched query token strings given a query file at
    `location` or a `query_string`, a match and an index.
    Yield None for unmatched positions.
    Punctuation is removed , spaces are normalized (new line is replaced by a space),
    case is preserved.
    Used primarily to recover the matched texts for testing or reporting.
    """
    assert idx
    dictionary_get = idx.dictionary.get

    tokens = (query.query_tokenizer(line, lower=False)
              for line in query.query_lines(location, query_string))
    tokens = chain.from_iterable(tokens)
    match_qspan = match.qspan
    match_qspan_start = match_qspan.start
    match_qspan_end = match_qspan.end
    known_pos = -1
    started = False
    finished = False
    for token in tokens:
        token_id = dictionary_get(token.lower())
        if token_id is None:
            if not started:
                continue
            if finished:
                break
        else:
            known_pos += 1

        if match_qspan_start <= known_pos <= match_qspan_end:
            started = True
            if known_pos == match_qspan_end:
                finished = True

            if known_pos in match_qspan and token_id is not None:
                yield token
            elif token_id is not None:
                yield '<%s>' % token
            else:
                yield '[%s]' % token


def matched_rule_tokens_str(match):
    """
    Return an iterable of matched rule token strings given a match.
    Yield None for unmatched positions.
    Punctuation is removed, spaces are normalized (new line is replaced by a space),
    case is preserved.
    Used primarily to recover the matched texts for testing or reporting.
    """
    ispan = match.ispan
    ispan_start = ispan.start
    ispan_end = ispan.end
    for pos, token in enumerate(match.rule.tokens(lower=False)):
        if ispan_start <= pos <= ispan_end:
            if pos in ispan:
                yield token
            else:
                yield '<%s>' % token


def merge_matches_old(matches, max_dist=MAX_DIST):
    """
    Merge overlapping, touching or close-by matches in the given iterable of
    matches. Return a new list of merged matches if they can be merged.
    Matches that cannot be merged are returned as-is.

    Only matches for the same licensing can be merged.

    The overlap and touch is considered using both the qspan and ispan.

    The maximal merge is always returned and eventually a single match per
    rule is returned if all matches for that rule can be merged.

    For being merged two matches must also be in increasing query and index positions.
    """
    # FIXME: longer and denser matches starting at the same qspan should
    # be sorted first

    # only merge matches with the same licensing_identifier
    # iterate on matches grouped by licensing_identifier, one licensing_identifier at a time.
    # FIXME: we should divide by ROUNDING with an interger division to round values in coarse start bands
    sorter = lambda m: (m.rule.licensing_identifier, m.qspan.start , -m.qlen(), -m.ilen())
    matches = sorted(matches, key=sorter)
    merged = []

    for _rid, rule_matches in groupby(matches, key=lambda m: m.rule.licensing_identifier):
        rule_matches = list(rule_matches)
        i = 0
        if TRACE_MERGE:
            logger_debug('merge_match: processing rule:', rule_matches[0].rule.identifier)

        # compare two matches in the sorted sequence: current_match and the next one
        while i < len(rule_matches) - 1:
            current_match = rule_matches[i]
            j = i + 1
            if TRACE_MERGE: logger_debug('---> merge_match: current_match:', current_match)

            while j < len(rule_matches):
                next_match = rule_matches[j]
                if TRACE_MERGE: logger_debug(' --> merge_match: next_match:', next_match)

                if (next_match.qdistance_to(current_match) >= max_dist
                 or next_match.idistance_to(current_match) >= max_dist):
                    break

                # remove surrounded matches
                if (current_match.surround(next_match)
                and
                    (
                        current_match.hilen() > next_match.hilen()
                     or
                        (current_match.hilen() == next_match.hilen() and current_match.ilen() >= next_match.ilen())
                    )
                    ):
                    # current_match.update(next_match)
                    if TRACE_MERGE: logger_debug('    ==> NEW MERGED 1:', current_match)
                    if TRACE_MERGE: logger_debug('      ==> DISCARDED1:', rule_matches[j])
                    if TRACE_MERGE_TEXTS: print('       MERGE1    ==> surround:\n',
                                           current_match, '\n', get_match_itext(current_match),
                                           '\nnext:\n', get_match_itext(next_match))

                    del rule_matches[j]

                # next_match is strictly in increasing sequence and within distance
                # and same rule
                elif (next_match.is_after(current_match)
                and current_match.rule == next_match.rule
                and next_match.qdistance_to(current_match) < max_dist
                and next_match.idistance_to(current_match) < max_dist):
                    current_match.update(next_match)
                    if TRACE_MERGE: logger_debug('    ==> NEW MERGED 2:', current_match)
                    if TRACE_MERGE: logger_debug('      ==> DISCARDED2:', rule_matches[j])
                    if TRACE_MERGE_TEXTS: print('       MERGE2    ==> increasing within dist\n',
                                           current_match, '\n', get_match_itext(current_match),
                                           '\nnext:\n', get_match_itext(next_match))
                    del rule_matches[j]

                else:
                    j += 1
            i += 1
        merged.extend(rule_matches)
    return merged
