#
# Copyright (c) 2017 nexB Inc. and others. All rights reserved.
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
from licensedcode import MAX_DIST
from licensedcode import tokenize

"""
LicenseMatch data structure and matches merging and filtering routines.
"""

TRACE = False
TRACE_FILTER_CONTAINS = False
TRACE_REFINE = False
TRACE_MERGE = False
TRACE_REFINE_SMALL = False
TRACE_REFINE_SINGLE = False
TRACE_REFINE_RULE_MIN_COVERAGE = False
TRACE_SPAN_DETAILS = False


def logger_debug(*args): pass

if TRACE or TRACE_FILTER_CONTAINS or TRACE_MERGE or TRACE_REFINE_RULE_MIN_COVERAGE or TRACE_REFINE_SINGLE:
    import logging
    import sys

    logger = logging.getLogger(__name__)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, basestring) and a or repr(a) for a in args))

    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)


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

    __slots__ = 'rule', 'qspan', 'ispan', 'hispan', 'query_run_start', 'matcher', 'start_line', 'end_line'

    def __init__(self, rule, qspan, ispan, hispan=None, query_run_start=0, matcher='', start_line=0, end_line=0):
        """
        Create a new match from:
         - rule: matched Rule object
         - qspan: query text matched Span, start at zero which is the absolute query start (not the query_run start).
         - ispan: rule text matched Span, start at zero which is the rule start.
         - hispan: rule text matched Span for high tokens, start at zero which is the rule start. Always a subset of ispan.
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
        self.query_run_start = query_run_start
        self.matcher = matcher
        self.start_line = start_line
        self.end_line = end_line

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
            coverage=self.coverage(),
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
                'sc=%(score)r, cov=%(coverage)r, qlen=%(qlen)r, ilen=%(ilen)r, hilen=%(hilen)r, rlen=%(rlen)r, '
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

    def lines(self):
        return self.start_line, self.end_line

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

    def coverage(self):
        """
        Return the coverage of this match to the matched rule as a rounded float between 0 and 100.
        """
        return round(self._coverage() * 100, 2)

    def _coverage(self):
        """
        Return the coverage of this match to the matched rule as a float between 0 and 1.
        """
        if not self.rule.length:
            return 0
        return self.ilen() / self.rule.length

    def score(self):
        """
        Return the score for this match as a rounded float between 0 and 100.

        The score is an indication of the confidence that a match is good. It is
        computed from the number of matched tokens, the number of rule tokens and the
        matched rule relevance.
        """
        # _coverage is a value between 0 and 1
        coverage = self._coverage()
        if not coverage:
            return 0

        # relevance is a number between 0 and 100. Divide by 100
        relevance = self.rule.relevance / 100
        if not relevance:
            return 0

        if not coverage or not relevance:
            return 0

        score = coverage * relevance
        if score == 1:
            # Is the match a contiguous match or not? If not, recompute the score
            # with an alternative approach to avoid the case where a 100% match that
            # is not covering ALL of the query side region (e.g. a non-contiguous
            # match) can contain extra misleading words.
            # see https://github.com/nexB/scancode-toolkit/issues/534
            matched_and_unmatched = self.qspan.magnitude()
            matched = self.qlen()
            if matched != matched_and_unmatched:
                score = matched / matched_and_unmatched

        return  round(score * 100, 2)

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

    def combine(self, other):
        """
        Return a new match object combining self and an other match.
        """
        if self.rule != other.rule:
            raise TypeError('Cannot combine matches with different rules: from: %(self)r, to: %(other)r' % locals())

        if other.matcher not in self.matcher:
            newmatcher = ' '.join([self.matcher, other.matcher])
        else:
            newmatcher = self.matcher

        combined = LicenseMatch(rule=self.rule,
                                qspan=Span(self.qspan | other.qspan),
                                ispan=Span(self.ispan | other.ispan),
                                hispan=Span(self.hispan | other.hispan),
                                query_run_start=min(self.query_run_start, other.query_run_start),
                                matcher=newmatcher)
        return combined

    def update(self, other):
        """
        Update self with other match and return the updated self in place.
        """
        combined = self.combine(other)
        self.qspan = combined.qspan
        self.ispan = combined.ispan
        self.hispan = combined.hispan
        self.matcher = combined.matcher
        self.query_run_start = min(self.query_run_start, other.query_run_start)
        return self

    def small(self):
        """
        Return True if this match is "small" based on its rule thresholds.
        Small matches are spurrious matches that are discarded.
        """
        thresholds = self.rule.thresholds()
        min_ihigh = thresholds.min_high
        min_ilen = thresholds.min_len
        hilen = self.hilen()
        ilen = self.ilen()
        if TRACE_REFINE_SMALL:
            logger_debug('LicenseMatch.small(): hilen=%(hilen)r, ilen=%(ilen)r, thresholds=%(thresholds)r' % locals(),)
        if thresholds.small and self.coverage() < 50 and (hilen < min_ihigh or ilen < min_ilen):
            if TRACE_REFINE_SMALL:
                logger_debug('LicenseMatch.small(): CASE 1 thresholds.small and self.coverage() < 50 and (hilen < min_ihigh or ilen < min_ilen)')
            return True
        if hilen < min_ihigh or ilen < min_ilen:
            if TRACE_REFINE_SMALL:
                logger_debug('LicenseMatch.small(): CASE 2 hilen < min_ihigh or ilen < min_ilen')
            return True

    def false_positive(self, idx):
        """
        Return a True-ish (e.g. a false positive rule id) if the LicenseMatch match
        is a false positive or None otherwise (nb: not False). This is done by a
        lookup of the matched tokens sequence against the `idx` index false positive
        rules.
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


def set_lines(matches, line_by_pos):
    """
    Update a matches sequence with start and end line given a line_by_pos pos->line mapping.
    """
    # if there is no line_by_pos, do not bother: the lines will stay to zero.
    if line_by_pos:
        for match in matches:
            match.start_line = line_by_pos[match.qstart]
            match.end_line = line_by_pos[match.qend]


def merge_matches(matches, max_dist=MAX_DIST):
    """
    Merge matches to the same rule in a sequence of matches. Return a new list
    of merged matches if they can be merged. Matches that cannot be merged are
    returned as-is.
    For being merged two matches must also be in increasing query and index positions.
    """
    # shortcut for single matches
    if len(matches) < 2:
        return matches

    # only merge matches with the same rule: sort then group by rule
    # for the same rule, sort on start, longer high, longer match, matcher type
    sorter = lambda m: (m.rule.identifier, m.qspan.start, -m.hilen(), -m.qlen(), m.matcher)
    matches.sort(key=sorter)
    matches_by_rule = [(rid, list(rule_matches)) for rid, rule_matches
                        in groupby(matches, key=lambda m: m.rule.identifier)]
    if TRACE_MERGE: print('merge_matches: number of matches to process:', len(matches))

    merged = []
    for rid, rule_matches in matches_by_rule:
        if TRACE_MERGE: logger_debug('merge_matches: processing rule:', rid)

        # compare two matches in the sorted sequence: current and next
        i = 0
        while i < len(rule_matches) - 1:
            j = i + 1
            while j < len(rule_matches):
                current_match = rule_matches[i]
                next_match = rule_matches[j]
                if TRACE_MERGE: logger_debug('---> merge_matches: current:', current_match)
                if TRACE_MERGE: logger_debug('---> merge_matches: next:   ', next_match)

                # stop if we exceed max dist
                if (current_match.qdistance_to(next_match) > MAX_DIST
                or current_match.idistance_to(next_match) > MAX_DIST):
                    break

                # keep one of equal matches
                if current_match.qspan == next_match.qspan and current_match.ispan == next_match.ispan:
                    if TRACE_MERGE: logger_debug('    ---> ###merge_matches: next EQUALS current, del next')
                    del rule_matches[j]
                    continue

                # if we have two equal ispans and some overlap
                # keep the shortest/densest match in qspan e.g. the smallest magnitude of the two
                if current_match.ispan == next_match.ispan and current_match.overlap(next_match):
                    cqmag = current_match.qspan.magnitude()
                    nqmag = next_match.qspan.magnitude()
                    if cqmag <= nqmag:
                        if TRACE_MERGE: logger_debug('    ---> ###merge_matches: current ispan EQUALS next ispan, current qmagnitude smaller, del next')
                        del rule_matches[j]
                        continue
                    else:
                        if TRACE_MERGE: logger_debug('    ---> ###merge_matches: current ispan EQUALS next ispan, next qmagnitude smaller, del current')
                        del rule_matches[i]
                        i -= 1
                        break

                # remove contained matches
                if current_match.qcontains(next_match):
                    if TRACE_MERGE: logger_debug('    ---> ###merge_matches: next CONTAINED in current, del next')
                    del rule_matches[j]
                    continue

                # remove contained matches the other way
                if next_match.qcontains(current_match):
                    if TRACE_MERGE: logger_debug('    ---> ###merge_matches: current CONTAINED in next, del current')
                    del rule_matches[i]
                    i -= 1
                    break

                # FIXME: qsurround is too weak. We want to check also isurround
                # merge surrounded
                if current_match.surround(next_match):
                    new_match = current_match.combine(next_match)
                    if len(new_match.qspan) == len(new_match.ispan):
                        # the merged matched is likely aligned
                        current_match.update(next_match)
                        if TRACE_MERGE: logger_debug('    ---> ###merge_matches: current SURROUNDS next, merged as new:', current_match)
                        del rule_matches[j]
                        continue

                # FIXME: qsurround is too weak. We want to check also isurround
                # merge surrounded the other way too: merge in current
                if next_match.surround(current_match):
                    new_match = current_match.combine(next_match)
                    if len(new_match.qspan) == len(new_match.ispan):
                        # the merged matched is likely aligned
                        next_match.update(current_match)
                        if TRACE_MERGE: logger_debug('    ---> ###merge_matches: next SURROUNDS current, merged as new:', current_match)
                        del rule_matches[i]
                        i -= 1
                        break

                # next_match is strictly in increasing sequence: merge in current
                if next_match.is_after(current_match):
                    current_match.update(next_match)
                    if TRACE_MERGE: logger_debug('    ---> ###merge_matches: next follows current, merged as new:', current_match)
                    del rule_matches[j]
                    continue

                # next_match overlaps
                # Check increasing sequence and overlap importance to decide merge
                if (current_match.qstart <= next_match.qstart
                and current_match.qend <= next_match.qend
                and current_match.istart <= next_match.istart
                and current_match.iend <= next_match.iend):
                    qoverlap = current_match.qspan.overlap(next_match.qspan)
                    if qoverlap:
                        ioverlap = current_match.ispan.overlap(next_match.ispan)
                        # only merge if overlaps are equals (otherwise they are not aligned)
                        if qoverlap == ioverlap:
                            current_match.update(next_match)
                            if TRACE_MERGE: logger_debug('    ---> ###merge_matches: next overlaps in sequence current, merged as new:', current_match)
                            del rule_matches[j]
                            continue

                j += 1
            i += 1
        merged.extend(rule_matches)
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

    # do not bother if there is only one match
    if len(matches) < 2:
        return matches, discarded

    # containment relationships and thresholds between two matches
    # based on this containment we may prefer one match over the other and discard a match
    CONTAINMENT_SMALL = 0.10
    CONTAINMENT_MEDIUM = 0.40
    CONTAINMENT_LARGE = 0.60
    CONTAINMENT_EXTRA_LARGE = 0.80

    # sort on start, longer high, longer match, matcher type
    sorter = lambda m: (m.qspan.start, -m.hilen(), -m.qlen(), m.matcher)
    matches = sorted(matches, key=sorter)

    if TRACE_FILTER_CONTAINS: print('filter_contained_matches: number of matches to process:', len(matches))
    if TRACE_FILTER_CONTAINS:
        print('filter_contained_matches: matches')
        map(print, matches)

    # compare two matches in the sorted sequence: current and next match
    # we progressively compare a pair and remove next or current
    i = 0
    while i < len(matches) - 1:
        j = i + 1
        while j < len(matches):
            current_match = matches[i]
            next_match = matches[j]

            # stop when no overlap: Touching and overlapping matches have a zero distance.
#             if current_match.qdistance_to(next_match):
#                 break

            if TRACE_FILTER_CONTAINS: logger_debug('---> filter_contained_matches: current: i=', i, current_match)
            if TRACE_FILTER_CONTAINS: logger_debug('---> filter_contained_matches: next:    j=', j, next_match)

            # equals matches
            if current_match.qspan == next_match.qspan:
                if current_match.coverage() >= next_match.coverage():
                    if TRACE_FILTER_CONTAINS: logger_debug('    ---> ###filter_contained_matches: next EQUALS current, removed next with lower or equal coverage', matches[j], '\n')
                    discarded.append(next_match)
                    del matches[j]
                    continue
                else:
                    if TRACE_FILTER_CONTAINS: logger_debug('    ---> ###filter_contained_matches: next EQUALS current, removed current with lower coverage', matches[i], '\n')
                    discarded.append(current_match)
                    del matches[i]
                    i -= 1
                    break

            # remove contained matches
            if current_match.qcontains(next_match):
                if TRACE_FILTER_CONTAINS: logger_debug('    ---> ###filter_contained_matches: next CONTAINED in current, removed next', matches[j], '\n')
                discarded.append(next_match)
                del matches[j]
                continue

            # remove contained matches the other way
            if next_match.qcontains(current_match):
                if TRACE_FILTER_CONTAINS: logger_debug('    ---> ###filter_contained_matches: current CONTAINED in next, removed current', matches[i], '\n')
                discarded.append(current_match)
                del matches[i]
                i -= 1
                break

            # handle overlapping matches: determine overlap and containment relationships
            overlap = current_match.overlap(next_match)

            # next match overlap to current
            overlap_ratio_to_next = overlap / next_match.qlen()

            extra_large_next = overlap_ratio_to_next >= CONTAINMENT_EXTRA_LARGE
            large_next = overlap_ratio_to_next >= CONTAINMENT_LARGE
            medium_next = overlap_ratio_to_next >= CONTAINMENT_MEDIUM
            small_next = overlap_ratio_to_next >= CONTAINMENT_SMALL

            # current match overlap to next
            overlap_ratio_to_current = overlap / current_match.qlen()

            extra_large_current = overlap_ratio_to_current >= CONTAINMENT_EXTRA_LARGE
            large_current = overlap_ratio_to_current >= CONTAINMENT_LARGE
            medium_current = overlap_ratio_to_current >= CONTAINMENT_MEDIUM
            small_current = overlap_ratio_to_current >= CONTAINMENT_SMALL

            if TRACE_FILTER_CONTAINS: logger_debug(
                '  ---> ###filter_contained_matches:',
                'overlap:', overlap,
                'containment of next to current is:',
                'overlap_ratio_to_next:', overlap_ratio_to_next,
                (extra_large_next and 'EXTRA_LARGE')
                or (large_next and 'LARGE')
                or (medium_next and 'MEDIUM')
                or (small_next and 'SMALL')
                or 'NOT CONTAINED',
                'containment of current to next is:',
                'overlap_ratio_to_current:', overlap_ratio_to_current,
                (extra_large_current and 'EXTRA_LARGE')
                or (large_current and 'LARGE')
                or (medium_current and 'MEDIUM')
                or (small_current and 'SMALL')
                or 'NOT CONTAINED',
            )

            if extra_large_next and current_match.qlen() >= next_match.qlen():
                if TRACE_FILTER_CONTAINS: logger_debug('      ---> ###filter_contained_matches: EXTRA_LARGE next included, removed shorter next', matches[j], '\n')
                discarded.append(next_match)
                del matches[j]
                continue

            if extra_large_current and current_match.qlen() <= next_match.qlen():
                if TRACE_FILTER_CONTAINS: logger_debug('      ---> ###filter_contained_matches: EXTRA_LARGE next includes current, removed shorter current', matches[i], '\n')
                discarded.append(current_match)
                del matches[i]
                i -= 1
                break

            if large_next and current_match.qlen() >= next_match.qlen() and current_match.hilen() >= next_match.hilen():
                if TRACE_FILTER_CONTAINS: logger_debug('      ---> ###filter_contained_matches: LARGE next included, removed shorter next', matches[j], '\n')
                discarded.append(next_match)
                del matches[j]
                continue

            if large_current and current_match.qlen() <= next_match.qlen() and current_match.hilen() <= next_match.hilen():
                if TRACE_FILTER_CONTAINS: logger_debug('      ---> ###filter_contained_matches: LARGE next includes current, removed shorter current', matches[i], '\n')
                discarded.append(current_match)
                del matches[i]
                i -= 1
                break

            if medium_next:
                if TRACE_FILTER_CONTAINS: logger_debug('    ---> ###filter_contained_matches: MEDIUM NEXT')
                if current_match.licensing_contains(next_match) and current_match.qlen() >= next_match.qlen() and current_match.hilen() >= next_match.hilen():
                    if TRACE_FILTER_CONTAINS: logger_debug(
                        '      ---> ###filter_contained_matches: MEDIUM next included with next licensing contained, removed next', matches[j], '\n',)
                    discarded.append(next_match)
                    del matches[j]
                    continue

                if next_match.licensing_contains(current_match) and current_match.qlen() <= next_match.qlen() and current_match.hilen() <= next_match.hilen():
                    if TRACE_FILTER_CONTAINS: logger_debug(
                        '      ---> ###filter_contained_matches: MEDIUM next includes current with current licensing contained, removed current', matches[i], '\n')
                    discarded.append(current_match)
                    del matches[i]
                    i -= 1
                    break

            if medium_current:
                if TRACE_FILTER_CONTAINS: logger_debug('    ---> ###filter_contained_matches: MEDIUM CURRENT')
                if current_match.licensing_contains(next_match) and current_match.qlen() >= next_match.qlen() and current_match.hilen() >= next_match.hilen():
                    if TRACE_FILTER_CONTAINS: logger_debug(
                        '      ---> ###filter_contained_matches: MEDIUM current, bigger current with next licensing contained, removed next', matches[j], '\n')
                    discarded.append(next_match)
                    del matches[j]
                    continue

                if next_match.licensing_contains(current_match) and current_match.qlen() <= next_match.qlen() and current_match.hilen() <= next_match.hilen():
                    if TRACE_FILTER_CONTAINS: logger_debug(
                        '      ---> ###filter_contained_matches: MEDIUM current, bigger next current with current licensing contained, removed current', matches[i], '\n')
                    discarded.append(current_match)
                    del matches[i]
                    i -= 1
                    break

            if small_next and current_match.surround(next_match) and current_match.licensing_contains(next_match) and current_match.qlen() >= next_match.qlen() and current_match.hilen() >= next_match.hilen():
                if TRACE_FILTER_CONTAINS: logger_debug('      ---> ###filter_contained_matches: SMALL next surrounded, removed next', matches[j], '\n')
                discarded.append(next_match)
                del matches[j]
                continue

            if small_current and next_match.surround(current_match) and next_match.licensing_contains(current_match) and current_match.qlen() <= next_match.qlen() and current_match.hilen() <= next_match.hilen():
                if TRACE_FILTER_CONTAINS: logger_debug('      ---> ###filter_contained_matches: SMALL current surrounded, removed current', matches[i], '\n')
                discarded.append(next_match)
                del matches[i]
                i -= 1
                break

            # check the previous current and next match
            # discard current if it is entirely contained in a combined previous and next
            # and previous and next do not overlap

            # ensure that we have a previous
            if i:
                previous_match = matches[i - 1]
                # ensure previous and next do not overlap
                if not previous_match.overlap(next_match):
                    # ensure most of current is contained in the previous and next overlap
                    cpo = current_match.overlap(previous_match)
                    cno = current_match.overlap(next_match)
                    if cpo and cno:
                        overlap_len = cno + cpo
                        cqlen = current_match.qlen()
                        # we want at least 90% of the current that is in the overlap
                        if overlap_len >= (cqlen * 0.9):
                            if TRACE_FILTER_CONTAINS: logger_debug('      ---> ###filter_contained_matches: current mostly contained in previsou and next, removed current', matches[i], '\n')
                            discarded.append(next_match)
                            del matches[i]
                            i -= 1
                            break

            j += 1
        i += 1

    # FIXME: returned discarded too
    return matches, discarded


def filter_rule_min_coverage(matches):
    """
    Return a list of matches scoring at or above a rule-defined minimum coverage and
    a list of matches with a coverage below a rule-defined minimum coverage.
    """
    kept = []
    discarded = []
    for match in matches:
        if match.coverage() < match.rule.minimum_coverage:
            if TRACE_REFINE_RULE_MIN_COVERAGE: logger_debug('    ==> DISCARDING rule.minimum_coverage:', type(match.rule.minimum_coverage), ':', repr(match.rule.minimum_coverage), 'match:', match)
            discarded.append(match)
        else:
            kept.append(match)
    return kept, discarded


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


def filter_spurious_single_token(matches, query=None, idx=None, unknown_count=5):
    """
    Return a list of matches without "spurious" single token matches and a list of
    "spurious" single token matches.

    A "spurious" single token match is a match to a single token that is surrounded
    on both sides by at least `unknown_count` tokens of either unknown tokens, short
    tokens composed of a single character or tokens composed only of digits.
    """
    kept = []
    discarded = []
    if not query:
        return matches, discarded

    unknowns_by_pos = query.unknowns_by_pos
    shorts_and_digits = query.shorts_and_digits_pos
    for match in matches:
        if not match.qlen() == 1:
            kept.append(match)
            continue

        qstart = match.qstart
        qend = match.qend

        # compute the number of unknown tokens before and after this single matched position
        # note: unknowns_by_pos is a defaultdict(int), shorts_and_digits is a set of integers
        before = unknowns_by_pos[qstart - 1]
        for p in range(qstart - 1 - unknown_count, qstart):
            if p in shorts_and_digits:
                before += 1
        if before < unknown_count:
            if TRACE_REFINE_SINGLE: logger_debug('    ==> !!! NOT DISCARDING spurrious_single_token, not enough before:', match, before)
            if TRACE_REFINE_SINGLE: _debug_print_matched_query_text(match, query, extras=unknown_count)
            kept.append(match)
            continue

        after = unknowns_by_pos[qstart]
        for p in range(qend, qend + 1 + unknown_count):
            if p in shorts_and_digits:
                after += 1

        if after >= unknown_count:
            if TRACE_REFINE_SINGLE: logger_debug('    ==> DISCARDING spurrious_single_token:', match)
            if TRACE_REFINE_SINGLE: _debug_print_matched_query_text(match, query, extras=unknown_count)
            discarded.append(match)
        else:
            if TRACE_REFINE_SINGLE: logger_debug('    ==> !!! NOT DISCARDING spurrious_single_token, not enough after:', match, before, after)
            if TRACE_REFINE_SINGLE: _debug_print_matched_query_text(match, query, extras=unknown_count)
            kept.append(match)
    return kept, discarded


def filter_short_matches(matches):
    """
    Return a list of matches that are not short and a list of short spurious matches.
    """
    kept = []
    discarded = []
    for match in matches:
        if match.small():
            if TRACE_REFINE_SMALL: logger_debug('    ==> DISCARDING SHORT:', match)
            discarded.append(match)
        else:
            if TRACE_REFINE_SMALL: logger_debug('  ===> NOT DISCARDING SHORT:', match)
            kept.append(match)
    return kept, discarded


def filter_spurious_matches(matches):
    """
    Return a list of matches that are not spurious and a list of spurious matches.

    Spurious matches are small matches with a low density (e.g. where the matched
    tokens are separated by many unmatched tokens.)
    """
    kept = []
    discarded = []

    for match in matches:
        qdens = match.qspan.density()
        idens = match.ispan.density()
        ilen = match.ilen()
        hilen = match.hilen()
        if (
           (ilen < 30 and hilen < 8 and (qdens < 0.4 or idens < 0.4))
        or (ilen < 20 and hilen < 5 and (qdens < 0.3 or idens < 0.3))
        or (ilen < 15 and (qdens < 0.2 or idens < 0.2))
        or (ilen < 10 and (qdens < 0.1 or idens < 0.1))
           ):
            if TRACE_REFINE: logger_debug('    ==> DISCARDING Spurious:', match)
            discarded.append(match)
        else:
            kept.append(match)
    return kept, discarded


def filter_false_positive_matches(matches, idx):
    """
    Return a list of matches that are not false positives and a list of false
    positive matches given an index `idx`.
    """
    kept = []
    discarded = []
    for match in matches:
        fp = match.false_positive(idx)
        if fp is None:
            # if TRACE_REFINE: logger_debug('    ==> NOT DISCARDING FALSE POSITIVE:', match)
            kept.append(match)
        else:
            if TRACE_REFINE: logger_debug('    ==> DISCARDING FALSE POSITIVE:', match, 'fp rule:', idx.rules_by_rid[fp].identifier)
            discarded.append(match)
    return kept, discarded


def refine_matches(matches, idx, query=None, min_score=0, max_dist=MAX_DIST):
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

    matches, discarded = filter_rule_min_coverage(matches)
    all_discarded.extend(discarded)
    if TRACE: logger_debug('   #####refine_matches: NOT UNDER MIN COVERAGE #', len(matches))
    if TRACE_REFINE: map(logger_debug, matches)
    if TRACE: logger_debug('   #####refine_matches: UNDER MIN COVERAGE discarded#', len(discarded))
    if TRACE_REFINE: map(logger_debug, discarded)

    matches, discarded = filter_spurious_single_token(matches, query, idx)
    all_discarded.extend(discarded)
    if TRACE: logger_debug('   #####refine_matches: NOT SINGLE TOKEN #', len(matches))
    if TRACE_REFINE: map(logger_debug, matches)
    if TRACE: logger_debug('   #####refine_matches: SINGLE TOKEN discarded#', len(discarded))
    if TRACE_REFINE: map(logger_debug, discarded)

    matches, discarded = filter_short_matches(matches)
    all_discarded.extend(discarded)
    if TRACE: logger_debug('   #####refine_matches: NOT SHORT #', len(matches))
    if TRACE_REFINE: map(logger_debug, matches)
    if TRACE: logger_debug('   #####refine_matches: SHORT discarded#', len(discarded))
    if TRACE_REFINE: map(logger_debug, discarded)

    matches, discarded = filter_false_positive_matches(matches, idx)
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

    Unmatched positions to known tokens are represented between angular backets <>
    and between square brackets [] for unknown tokens not part of the index.
    Punctuation is removed , spaces are normalized (new line is replaced by a space),
    case is preserved.

    If `width` is a number superior to zero, the texts are wrapped to width.
    """
    return (get_matched_qtext(match, location, query_string, idx, width),
            get_match_itext(match, width))


def get_matched_qtext(match, location=None, query_string=None, idx=None, width=120, margin=0):
    """
    Return the matched query text as a wrapped string of `width` given a match, a
    query location or string and an index.

    Unmatched positions are represented between angular backets <> or square brackets
    [] for unknown tokens not part of the index. Punctuation is removed , spaces are
    normalized (new line is replaced by a space), case is preserved.

    If `width` is a number superior to zero, the texts are wrapped to width with an
    optional `margin`.
    """
    return format_text(matched_query_tokens_str(match, location, query_string, idx), width=width, margin=margin)


def get_match_itext(match, width=120, margin=0):
    """
    Return the matched rule text as a wrapped string of `width` given a match.

    Unmatched positions are represented between angular backets <>.
    Punctuation is removed , spaces are normalized (new line is replaced by a space),
    case is preserved.

    If `width` is a number superior to zero, the texts are wrapped to width with an
    optional `margin`.
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

    Yield None for unmatched positions. Punctuation is removed, spaces are normalized
    (new line is replaced by a space), case is preserved.
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
            else:
                if token_id is not None:
                    yield '<%s>' % token
                else:
                    yield '[%s]' % token


def matched_rule_tokens_str(match):
    """
    Return an iterable of matched rule token strings given a match.
    Yield None for unmatched positions.
    Punctuation is removed, spaces are normalized (new line is replaced by a space),
    case is preserved.
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


def _debug_print_matched_query_text(match, query, extras=5):
    """
    Print a matched query text including `extras` tokens before and after the match.
    Used for debugging license matches.
    """
    # create a fake new match with extra unknown left and right
    new_match = match.combine(match)
    new_qstart = max([0, match.qstart - extras])
    new_qend = min([match.qend + extras, len(query.tokens)])
    new_qspan = Span(new_qstart, new_qend)
    new_match.qspan = new_qspan

    logger_debug(new_match)
    logger_debug(' MATCHED QUERY TEXT with extras')
    qt, _it = get_texts(new_match, location=query.location, query_string=None, idx=query.idx)
    print(qt)


def get_full_matched_text(match, location=None, query_string=None, idx=None,
                          whole_lines=False,
                          highlight_matched=u'%s', highlight_not_matched=u'[%s]'):
    """
    Yield a stream of unicode strings corresponding to the full matched matched query
    text given a query file at `location` or a `query_string`, a `match` and an
    `index`. This contains the full text including punctuations and spaces that are
    not participating in the matche proper.

    Each text token string is interpolated for optional highlighting with the
    `highlight_matched` format string is matched or to the to the
    `highlight_not_matched` is not matched.
    Punctuation is not "highlighted".

    Optionally if `whole_lines` is True, the unmatched part at the start of the first
    matched line and the end of the last matched lines are included in the text.
    """
    assert idx
    dictionary_get = idx.dictionary.get


    import attr
    @attr.s(slots=True)
    class Token(object):
        value = attr.ib()
        line_num = attr.ib()
        pos = attr.ib(default=-1)
        is_text = attr.ib(default=False)
        is_included = attr.ib(default=False)
        is_matched = attr.ib(default=False)
        is_known = attr.ib(default=False)


    def _tokenize(location, query_string):
        """Yield Tokens with pos and line number."""
        _pos = -1
        for _line_num, _line in enumerate(query.query_lines(location, query_string, strip=False), 1):
            for _is_text, _token in tokenize.matched_query_text_tokenizer(_line):
                _known = _is_text and dictionary_get(_token.lower()) is not None
                _tok = Token(value=_token, line_num=_line_num, is_text=_is_text, is_known=_known)
                if _known:
                    _pos += 1
                    _tok.pos = _pos
                yield _tok


    def _filter_unmatched_lines(tokens, _start_line, _end_line):
        """Skip lines that are not matched."""
        for token in tokens:
            if token.line_num < _start_line:
                continue
            if token.line_num > _end_line:
                break
            yield token


    def _tag_tokens_as_matched(tokens, qspan):
        """Tag tokens that are matched with is_matched."""
        for token in tokens:
            if token.pos != -1 and token.is_known and token.pos in qspan:
                token.is_matched = True
            yield token


    def _tag_tokens_as_included_in_whole_lines(tokens, _start_line, _end_line):
        """Tag all tokens in lines as included."""
        for token in tokens:
            if _start_line <= token.line_num <= _end_line:
                token.is_included = True
            yield token


    def _tag_tokens_as_included_in_matched_range(tokens, _start, _end):
        """Tag tokens with start and end as included."""
        started = False
        finished = False
        for token in tokens:
            if not started and token.pos == _start:
                started = True

            if started and not finished:
                token.is_included = True

            yield token

            if token.pos == _end:
                finished = True


    def _filter_non_included_tokens(tokens):
        """Skip non included tokens."""
        for token in tokens:
            if token.is_included:
                yield token

    # Create and process a stream of Tokens
    tokenized = _tokenize(location, query_string)
    in_line_range = _filter_unmatched_lines(tokenized, match.start_line, match.end_line)
    matched = _tag_tokens_as_matched(in_line_range, match.qspan)
    if whole_lines:
        included = _tag_tokens_as_included_in_whole_lines(matched, match.start_line, match.end_line)
    else:
        included = _tag_tokens_as_included_in_matched_range(matched, match.qspan.start, match.qspan.end)
    tokens = _filter_non_included_tokens(included)

    # Finally yiled strings with eventual highlightings
    for token in tokens:
        if token.is_text:
            if token.is_matched:
                yield highlight_matched % token.value
            else:
                yield highlight_not_matched % token.value
        else:
            # punctuation
            yield token.value
