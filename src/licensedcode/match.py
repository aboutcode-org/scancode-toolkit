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
from __future__ import division
from __future__ import print_function

from itertools import groupby
from functools import total_ordering

import attr

from licensedcode import MAX_DIST
from licensedcode import query
from licensedcode.spans import Span
from licensedcode.tokenize import matched_query_text_tokenizer

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


if (TRACE or TRACE_FILTER_CONTAINS or TRACE_MERGE
    or TRACE_REFINE_RULE_MIN_COVERAGE or TRACE_REFINE_SINGLE
    or TRACE_REFINE_SMALL):

    import logging
    import sys

    from licensedcode.tracing import _debug_print_matched_query_text

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
    matched index positions. Also computes a score for a match. At a high level,
    a match behaves a bit like a Span and has several similar methods taking
    into account both the query and index Span.
    """

    __slots__ = (
        'rule', 'qspan', 'ispan', 'hispan', 'query_run_start',
        'matcher', 'start_line', 'end_line', 'query',
    )

    def __init__(self, rule, qspan, ispan, hispan=None, query_run_start=0,
                 matcher='', start_line=0, end_line=0, query=None):
        """
        Create a new match from:
         - rule: matched Rule object
         - qspan: query text matched Span, start at zero which is the absolute
           query start (not the query_run start).
         - ispan: rule text matched Span, start at zero which is the rule start.
         - hispan: rule text matched Span for high tokens, start at zero which
           is the rule start. Always a subset of ispan.
         - matcher: a string indicating which matching procedure this match was
           created with. Used for diagnostics, debugging and testing.

         Note that the relationship between is the qspan and ispan is such that:
         - they always have the exact same number of items but when sorted each
           value at an index may be different
         - the nth position when sorted by position is such that their token
           value is equal for this position.
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
        self.query = query

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
            license_expression=self.rule.license_expression,
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
        return (
            'LicenseMatch<%(matcher)r, lines=%(lines)r, %(rule_id)r, '
            '%(license_expression)r, sc=%(score)r, cov=%(coverage)r, '
            'qlen=%(qlen)r, ilen=%(ilen)r, hilen=%(hilen)r, rlen=%(rlen)r, '
            'qreg=%(qreg)r, ireg=%(ireg)r %(spans)s>') % rep

    def __eq__(self, other):
        """
        Strict equality is based on licensing not matched rule.
        """
        return (isinstance(other, LicenseMatch)
            and self.same_licensing(other)
            and self.qspan == other.qspan
            and self.ispan == other.ispan
        )

    def __ne__(self, other):
        """
        Strict inequality is based on licensing not matched rule.
        """
        if not isinstance(other, LicenseMatch):
            return True

        return not all([
                self.same_licensing(other),
                self.qspan == other.qspan,
                self.ispan == other.ispan,
        ])

    def same_licensing(self, other):
        """
        Return True if other has the same licensing.
        """
        return self.rule.same_licensing(other.rule)

    def licensing_contains(self, other):
        """
        Return True if this match licensing contains the other match licensing.
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

    def _icoverage(self):
        """
        Return the coverage of this match to the matched rule as a float between
        0 and 1.
        """
        if not self.rule.length:
            return 0
        return self.ilen() / self.rule.length

    def coverage(self):
        """
        Return the coverage of this match to the matched rule as a rounded float
        between 0 and 100.
        """
        return round(self._icoverage() * 100, 2)

    def score(self):
        """
        Return the score for this match as a rounded float between 0 and 100.

        The score is an indication of the confidence that a match is good. It is
        computed from the number of matched tokens, the number of query tokens
        in the matched range (including unknowns and unmatched) and the matched
        rule relevance.
        """
        # relevance is a number between 0 and 100. Divide by 100
        relevance = self.rule.relevance / 100
        if not relevance:
            return 0

        # The query side of the match may not be contiguous and may contains
        # unmatched known tokens or unknown tokens. Therefore we need to compute
        # the real portion query length including unknown tokens that is
        # included in this match, for both matches and unmatched tokens

        qspan = self.qspan
        magnitude = qspan.magnitude()
        query = self.query
        # note: to avoid breaking many tests we check query presence
        if query:
            # Compute a count of unknowns tokens that are inside the matched
            # range, ignoring end position of the query span: unknowns here do
            # not matter as they are never in the match
            unknowns_pos = qspan & query.unknowns_span
            qspe = qspan.end
            unknowns_pos = (pos for pos in unknowns_pos if pos != qspe)
            qry_unkxpos = query.unknowns_by_pos
            unknowns_in_match = sum(qry_unkxpos[pos] for pos in unknowns_pos)

            # Fixup the magnitude by adding the count of unknowns in the match.
            # This number represents the full extent of the matched query region
            # including matched, unmatched and unknown tokens.
            magnitude += unknowns_in_match

        # Compute the score as the ration of the matched query length to the
        # magnitude, e.g. the length of the matched region
        if not magnitude:
            return 0

        # FIXME: this should exposed as an q/icoverage() method instead
        query_coverage = self.qlen() / magnitude
        rule_coverage = self._icoverage()
        if query_coverage < 1 and rule_coverage < 1:
            # use rule coverage in this case
            return  round(rule_coverage * relevance * 100, 2)
        return  round(query_coverage * rule_coverage * relevance * 100, 2)

    def surround(self, other):
        """
        Return True if this match query span surrounds other other match query
        span.

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
            raise TypeError(
                'Cannot combine matches with different rules: '
                'from: %(self)r, to: %(other)r' % locals())

        if other.matcher not in self.matcher:
            newmatcher = ' '.join([self.matcher, other.matcher])
        else:
            newmatcher = self.matcher

        combined = LicenseMatch(
            rule=self.rule,
            qspan=Span(self.qspan | other.qspan),
            ispan=Span(self.ispan | other.ispan),
            hispan=Span(self.hispan | other.hispan),
            query_run_start=min(self.query_run_start, other.query_run_start),
            matcher=newmatcher,
            query=self.query)
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
            coverage = self.coverage()
            logger_debug(
                'LicenseMatch.small(): hilen=%(hilen)r, ilen=%(ilen)r, '
                'thresholds=%(thresholds)r coverage=%(coverage)r' % locals(),)

        if thresholds.small and (hilen < min_ihigh or ilen < min_ilen) and self.coverage() < 50:
            if TRACE_REFINE_SMALL:
                logger_debug(
                    'LicenseMatch.small(): CASE 1 thresholds.small and '
                    'self.coverage() < 50 and (hilen < min_ihigh or ilen < min_ilen)')
            return True

        if hilen < min_ihigh or ilen < min_ilen:
            if TRACE_REFINE_SMALL:
                logger_debug('LicenseMatch.small(): CASE 2 hilen < min_ihigh or ilen < min_ilen')
            return True

        if TRACE_REFINE_SMALL:
            logger_debug('LicenseMatch.small(): not small')

        return False

    def matched_text(self, whole_lines=False,
                     highlight_matched=u'%s', highlight_not_matched=u'[%s]'):
        """
        Return the matched text for this match or an empty string if no
        query exists for this match.
        """
        query = self.query
        if not query:
            # TODO: should we raise an exception instead???
            # this cvase should never exist except for tests!
            return u''
        return u''.join(get_full_matched_text(
            self,
            location=query.location,
            query_string=query.query_string,
            idx=query.idx,
            whole_lines=whole_lines,
            highlight_matched=highlight_matched,
            highlight_not_matched=highlight_not_matched)
        )


def set_lines(matches, line_by_pos):
    """
    Update a matches sequence with start and end line given a line_by_pos
    pos->line mapping.
    """
    # if there is no line_by_pos, do not bother: the lines will stay to zero.
    if line_by_pos:
        for match in matches:
            match.start_line = line_by_pos[match.qstart]
            match.end_line = line_by_pos[match.qend]
            if TRACE:
                logger_debug('set_lines: match.start_line :', match.start_line)
                logger_debug('set_lines: match.end_line :', match.end_line)


def merge_matches(matches, max_dist=MAX_DIST):
    """
    Merge matches to the same rule in a sequence of matches. Return a new list
    of merged matches if they can be merged. Matches that cannot be merged are
    returned as-is.
    For being merged two matches must also be in increasing query and index
    positions.
    """

    # shortcut for single matches
    if len(matches) < 2:
        return matches

    # only merge matches with the same rule: sort then group by rule for the
    # same rule, sort on start, longer high, longer match, matcher type
    sorter = lambda m: (m.rule.identifier, m.qspan.start, -m.hilen(), -m.qlen(), m.matcher)
    matches.sort(key=sorter)
    matches_by_rule = [(rid, list(rule_matches)) for rid, rule_matches
                        in groupby(matches, key=lambda m: m.rule.identifier)]
    if TRACE_MERGE: print('merge_matches: number of matches to process:', len(matches))

    merged = []
    for rid, rule_matches in matches_by_rule:
        if TRACE_MERGE: logger_debug('merge_matches: processing rule:', rid)
        rlen = rule_matches[0].rule.length
        max_rlen_dist = min((rlen // 2) or 1, MAX_DIST)

        # compare two matches in the sorted sequence: current and next
        i = 0
        while i < len(rule_matches) - 1:
            j = i + 1
            while j < len(rule_matches):
                current_match = rule_matches[i]
                next_match = rule_matches[j]
                if TRACE_MERGE: logger_debug('---> merge_matches: current:', current_match)
                if TRACE_MERGE: logger_debug('---> merge_matches: next:   ', next_match)

                # two exact matches can never be merged as they will not be overlapping
                # only sequence matches for the same rule can be merged
                # if current_match.matcher != MATCH_SEQ and next_match.matcher != MATCH_SEQ:
                #    if TRACE_MERGE: logger_debug('    ---> ###merge_matches: both matches are EXACT_MATCHES, skipping')
                #    break

                # FIXME: also considers the match length!
                # stop if we exceed max dist
                # or distance over 1/2 of rule length
                if (current_match.qdistance_to(next_match) > max_rlen_dist
                or current_match.idistance_to(next_match) > max_rlen_dist):
                    if TRACE_MERGE: logger_debug('    ---> ###merge_matches: MAX_DIST/max_rlen_dist: %(max_rlen_dist)d reached, breaking' % locals())
                    break

                # keep one of equal matches
                # with same qspan: FIXME: is this ever possible?
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

                # FIXME: what about the distance??

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

# FIXME we should consider the length and distance between matches to break
# early from the loops: trying to check containment on wildly separated matches
# does not make sense


def filter_contained_matches(matches):
    """
    Return a filtered list of LicenseMatch given a `matches` list of
    LicenseMatch by removing duplicated or superfluous matches using containment
    relationships. Works across all matches.

    For instance a match entirely contained in another bigger match is removed.
    When more than one matched position matches the same license(s), only one
    match of this set is kept.
    """

    discarded = []

    # do not bother if there is only one match
    if len(matches) < 2:
        return matches, discarded

    # containment relationships and thresholds between two matches: based on
    # this containment we may prefer one match over the other and discard a
    # match
    CONTAINMENT_SMALL = 0.10
    CONTAINMENT_MEDIUM = 0.40
    CONTAINMENT_LARGE = 0.60
    CONTAINMENT_EXTRA_LARGE = 0.80

    # sort on start, longer high, longer match, matcher type
    sorter = lambda m: (m.qspan.start, -m.hilen(), -m.qlen(), m.matcher)
    matches = sorted(matches, key=sorter)

    if TRACE_FILTER_CONTAINS: print('filter_contained_matches: number of matches to process:', len(matches))
    if TRACE_FILTER_CONTAINS:
        print('filter_contained_matches: initial matches')
        map(print, matches)

    # compare two matches in the sorted sequence: current and next match we
    # progressively compare a pair and remove next or current
    i = 0
    while i < len(matches) - 1:
        j = i + 1
        while j < len(matches):
            current_match = matches[i]
            next_match = matches[j]
            if TRACE_FILTER_CONTAINS: logger_debug('---> filter_contained_matches: current: i=', i, current_match)
            if TRACE_FILTER_CONTAINS: logger_debug('---> filter_contained_matches: next:    j=', j, next_match)

            # TODO: is this really correct?: we could break/shortcircuit rather
            # than continue since continuing looking next matches will yield no
            # new findings stop when no overlap: Touching and overlapping
            # matches have a zero distance.
            if current_match.qdistance_to(next_match):
                if TRACE_FILTER_CONTAINS: logger_debug('    ---> ###filter_contained_matches: matches have a distance: NO OVERLAP POSSIBLE -->', 'qdist:', current_match.qdistance_to(next_match))
                j += 1
                continue

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

            # check the previous current and next match: discard current if it
            # is entirely contained in a combined previous and next and previous
            # and next do not overlap

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
    Return a list of matches scoring at or above a rule-defined minimum coverage
    and a list of matches with a coverage below a rule-defined minimum coverage.
    """
    from licensedcode.match_seq import MATCH_SEQ

    kept = []
    discarded = []
    for match in matches:
        # always keep exact matches
        if match.matcher != MATCH_SEQ:
            kept.append(match)
            continue
        if match.coverage() < match.rule.minimum_coverage:
            if TRACE_REFINE_RULE_MIN_COVERAGE: logger_debug('    ==> DISCARDING rule.minimum_coverage:', type(match.rule.minimum_coverage), ':', repr(match.rule.minimum_coverage), 'match:', match)
            discarded.append(match)
        else:
            kept.append(match)
    return kept, discarded


def filter_low_score(matches, min_score=100):
    """
    Return a list of matches scoring above `min_score` and a list of matches
    scoring below.
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


def filter_spurious_single_token(matches, query=None, unknown_count=5):
    """
    Return a list of matches without "spurious" single token matches and a list
    of "spurious" single token matches.

    A "spurious" single token match is a match to a single token that is
    surrounded on both sides by at least `unknown_count` tokens of either
    unknown tokens, short tokens composed of a single character or tokens
    composed only of digits.
    """
    from licensedcode.match_seq import MATCH_SEQ
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
        # always keep extact matches
        if match.matcher != MATCH_SEQ:
            kept.append(match)
            continue

        qstart = match.qstart
        qend = match.qend

        # compute the number of unknown tokens before and after this single
        # matched position note: unknowns_by_pos is a defaultdict(int),
        # shorts_and_digits is a set of integers
        before = unknowns_by_pos[qstart - 1]
        for p in range(qstart - 1 - unknown_count, qstart):
            if p in shorts_and_digits:
                before += 1
        if before < unknown_count:
            if TRACE_REFINE_SINGLE: logger_debug('    ==> !!! NOT DISCARDING spurrious_single_token, not enough before:', match, before)
            if TRACE_REFINE_SINGLE: _debug_print_matched_query_text(match, query, extras=unknown_count, logger_debug=logger_debug)
            kept.append(match)
            continue

        after = unknowns_by_pos[qstart]
        for p in range(qend, qend + 1 + unknown_count):
            if p in shorts_and_digits:
                after += 1

        if after >= unknown_count:
            if TRACE_REFINE_SINGLE: logger_debug('    ==> DISCARDING spurrious_single_token:', match)
            if TRACE_REFINE_SINGLE: _debug_print_matched_query_text(match, query, extras=unknown_count, logger_debug=logger_debug)
            discarded.append(match)
        else:
            if TRACE_REFINE_SINGLE: logger_debug('    ==> !!! NOT DISCARDING spurrious_single_token, not enough after:', match, before, after)
            if TRACE_REFINE_SINGLE: _debug_print_matched_query_text(match, query, extras=unknown_count, logger_debug=logger_debug)
            kept.append(match)
    return kept, discarded


def filter_short_matches(matches):
    """
    Return a list of matches that are not short and a list of short spurious
    matches.
    """
    from licensedcode.match_seq import MATCH_SEQ
    kept = []
    discarded = []
    for match in matches:
        # always keep exact matches
        if match.matcher != MATCH_SEQ:
            kept.append(match)
            continue

        if match.small():
            if TRACE_REFINE_SMALL: logger_debug('    ==> DISCARDING SHORT:', match)
            discarded.append(match)
        else:
            if TRACE_REFINE_SMALL: logger_debug('  ===> NOT DISCARDING SHORT:', match)
            kept.append(match)
    return kept, discarded


def filter_spurious_matches(matches):
    """
    Return a list of matches that are not spurious and a list of spurious
    matches.

    Spurious matches are small matches with a low density (e.g. where the
    matched tokens are separated by many unmatched tokens.)
    """
    from licensedcode.match_seq import MATCH_SEQ
    kept = []
    discarded = []

    for match in matches:
        # always keep exact matches
        if match.matcher != MATCH_SEQ:
            kept.append(match)
            continue

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


def filter_false_positive_matches(matches):
    """
    Return a list of matches that are not false positives and a list of false
    positive matches.
    """
    kept = []
    discarded = []
    for match in matches:
        if match.rule.is_false_positive:
            if TRACE_REFINE: logger_debug('    ==> DISCARDING FALSE POSITIVE:', match)
            discarded.append(match)
        else:
            # if TRACE_REFINE: logger_debug('    ==> NOT DISCARDING FALSE POSITIVE:', match)
            kept.append(match)
    return kept, discarded


def refine_matches(matches, idx, query=None, min_score=0, max_dist=MAX_DIST, filter_false_positive=True, merge=True):
    """
    Return two sequences of matches: one contains refined good matches, and the
    other contains matches that were filtered out.
    """
    if TRACE: logger_debug()
    if TRACE: logger_debug(' #####refine_matches: STARTING matches#', len(matches))
    if TRACE_REFINE: map(logger_debug, matches)

    if merge:
        matches = merge_matches(matches, max_dist=max_dist)
        if TRACE: logger_debug('     ##### refine_matches: STARTING MERGED_matches#:', len(matches))

    all_discarded = []

    # FIXME: we should have only a single loop on all the matches at once!!
    # and not 10's of loops!!!

    matches, discarded = filter_rule_min_coverage(matches)
    all_discarded.extend(discarded)
    if TRACE: logger_debug('   #####refine_matches: NOT UNDER MIN COVERAGE #', len(matches))
    if TRACE_REFINE: map(logger_debug, matches)
    if TRACE: logger_debug('   #####refine_matches: UNDER MIN COVERAGE discarded#', len(discarded))
    if TRACE_REFINE: map(logger_debug, discarded)

    matches, discarded = filter_spurious_single_token(matches, query)
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

    if filter_false_positive:
        matches, discarded = filter_false_positive_matches(matches)
        all_discarded.extend(discarded)
        if TRACE: logger_debug('   #####refine_matches: NOT FALSE POS #', len(matches))
        if TRACE_REFINE: map(logger_debug, matches)
        if TRACE: logger_debug('   #####refine_matches: FALSE POS discarded#', len(discarded))
        if TRACE_REFINE: map(logger_debug, discarded)

    if min_score:
        matches, discarded = filter_low_score(matches, min_score=min_score)
        all_discarded.extend(discarded)
        if TRACE: logger_debug('   #####refine_matches: NOT LOW SCORE #', len(matches))
        if TRACE_REFINE: map(logger_debug, matches)
        if TRACE: logger_debug('   ###refine_matches: LOW SCORE discarded #:', len(discarded))
        if TRACE_REFINE: map(logger_debug, discarded)

    if merge:
        matches = merge_matches(matches, max_dist=max_dist)

    logger_debug('   ##### refine_matches: FINAL MERGED_matches#:', len(matches))
    if TRACE_REFINE: map(logger_debug, matches)

    return matches, all_discarded


@attr.s(slots=True)
class Token(object):
    """
    Used to represent a token in collected matched texts and SPDX identifiers.
    """
    # original text value for this token.
    value = attr.ib()
    # line number, one-based
    line_num = attr.ib()
    # absolute position for known tokens, zero-based. -1 for unknown tokens
    pos = attr.ib(default=-1)
    # False if this is punctuation
    is_text = attr.ib(default=False)
    # True if included in the returned matched text
    is_included = attr.ib(default=False, repr=False)
    # True if part of a match
    is_matched = attr.ib(default=False, repr=False)
    # True if this is a known token
    is_known = attr.ib(default=False)


def get_full_matched_text(
        match, location=None, query_string=None, idx=None,
        whole_lines=False, highlight_matched=u'%s', highlight_not_matched=u'[%s]'):
    """
    Yield unicode strings corresponding to the full matched matched query text
    given a query file at `location` or a `query_string`, a `match` LicenseMatch
    and an `idx` LicenseIndex.

    This contains the full text including punctuations and spaces that are not
    participating in the match proper.

    If `whole_lines` is True, the unmatched part at the start of the first
    matched line and the end of the last matched lines are also included in the
    returned text.

    Each token is interpolated for "highlighting" and emphasis with the
    `highlight_matched` format string for matched tokens or to the
    `highlight_not_matched` for tokens not matched. The default is to enclose an
    unmatched token sequence in [] square brackets. Punctuation is not
    highlighted.
    """
    assert location or query_string
    assert idx
    dictionary_get = idx.dictionary.get

    def _tokenize(location, query_string):
        """Yield Tokens with pos and line number."""
        _pos = -1
        for _line_num, _line in query.query_lines(location, query_string, strip=False):
            for _is_text, _token in matched_query_text_tokenizer(_line):
                _known = _is_text and dictionary_get(_token.lower()) is not None
                _tok = Token(value=_token, line_num=_line_num, is_text=_is_text, is_known=_known)
                if _known:
                    _pos += 1
                    _tok.pos = _pos
                yield _tok

    def _in_matched_lines(tokens, _start_line, _end_line):
        """Yield tokens that are within matched start and end lines."""
        for _tok in tokens:
            if _tok.line_num < _start_line:
                continue
            if _tok.line_num > _end_line:
                break
            yield _tok

    def _tag_tokens_as_matched(tokens, qspan):
        """Tag tokens within qspan as matched."""
        for _tok in tokens:
            if _tok.pos != -1 and _tok.is_known and _tok.pos in qspan:
                _tok.is_matched = True
            yield _tok

    def _tag_tokens_as_included_in_whole_lines(tokens, _start_line, _end_line):
        """Tag tokens within start and end lines as included."""
        for _tok in tokens:
            if _start_line <= _tok.line_num <= _end_line:
                _tok.is_included = True
            yield _tok

    def _tag_tokens_as_included_in_matched_range(tokens, _start, _end):
        """Tag tokens within start and end positions as included."""
        started = False
        finished = False
        for _tok in tokens:
            if not started and _tok.pos == _start:
                started = True

            if started and not finished:
                _tok.is_included = True

            yield _tok

            if _tok.pos == _end:
                finished = True

    # Create and process a stream of Tokens
    tokenized = _tokenize(location, query_string)
    in_matched_lines = _in_matched_lines(tokenized, match.start_line, match.end_line)
    matched = _tag_tokens_as_matched(in_matched_lines, match.qspan)
    if whole_lines:
        as_included = _tag_tokens_as_included_in_whole_lines(matched, match.start_line, match.end_line)
    else:
        as_included = _tag_tokens_as_included_in_matched_range(matched, match.qspan.start, match.qspan.end)
    tokens = (t for t in as_included if t.is_included)

    # Finally yield strings with eventual highlightings
    for token in tokens:
        if token.is_text:
            if token.is_matched:
                yield highlight_matched % token.value
            else:
                yield highlight_not_matched % token.value
        else:
            # punctuation
            yield token.value
