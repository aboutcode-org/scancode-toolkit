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

from licensedcode.whoosh_spans.spans import Span


TRACE = False
TRACE_REPR = False
TRACE_REFINE = False
TRACE_FILTER = False
TRACE_MERGE = False


def logger_debug(*args): pass

if TRACE:
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

    __slots__ = 'rule', 'qspan', 'ispan', 'hispan', 'line_by_pos' , 'query_run_start', '_type'

    def __init__(self, rule, qspan, ispan, hispan=None, line_by_pos=None, query_run_start=0, _type=''):
        """
        Create a new match from:
         - rule: matched Rule object
         - qspan: query text matched Span, start at zero which is the absolute query start (not the query_run start).
         - ispan: rule text matched Span, start at zero which is the rule start.
         - hispan: rule text matched Span for high tokens, start at zero which is the rule start. Always a subset of ispan.
         - line_by_pos: mapping of (query positions -> line numbers). Line numbers start at one.
           Optional: if not provided, the `lines` start and end tuple will be (0, 0) and no line information will be available.
         - _type: a string indicating which matching procedure this match was created with. Used for debugging and testing only.
         
         Note the relationship between is the qspan and ispan is such that:
         - they always have the exact same number of items but when sorted each value at an index may be different
         - the nth position when sorted is such that the token value is equal
        """
        self.rule = rule
        self.qspan = qspan
        self.ispan = ispan
        if hispan is None:
            hispan = Span()
        self.hispan = hispan
        self.line_by_pos = line_by_pos or {}
        self.query_run_start = query_run_start
        self._type = _type

    def __repr__(self):

        spans = ''
        if TRACE_REPR:
            qspan = self.qspan
            ispan = self.ispan
            spans = 'qspan=%(qspan)r, ispan=%(ispan)r, ' % locals()

        rep = dict(
            rule_id=self.rule.identifier(),
            rule_licenses=', '.join(sorted(self.rule.licenses)),
            score=self.score(),

            qlen=self.qlen(),
            qreg=(self.qstart, self.qend),
            spans=spans,
            ilen=self.ilen(),
            rlen=self.rule.length,
            ireg=(self.istart, self.iend),

            lines=self.lines,
            _type=self._type,
        )
        return ('LicenseMatch<%(rule_id)r, %(rule_licenses)r, '
               'score=%(score)r, qlen=%(qlen)r, ilen=%(ilen)r, rlen=%(rlen)r, '
               'qreg=%(qreg)r, ireg=%(ireg)r, '
               '%(spans)s'
               'lines=%(lines)r, %(_type)r>') % rep

    def __eq__(self, other):
        """
        Strict equality.
        """
        return (isinstance(other, LicenseMatch)
            and self.same_licensing(other)
            and self.qspan == other.qspan
            and self.ispan == other.ispan
        )

#     def __hash__(self):
#         """
#         Matches are hashable.
#         """
#         # FIXME: is this really True???
#         return hash((self.rule, tuple(self.qspan), tuple(self.ispan), self.lines))

    def same(self, other):
        """
        Return True if other has the same licensing, score and spans.
        """
        return (isinstance(other, LicenseMatch)
            and self.same_licensing(other)
            and self.qspan == other.qspan 
            and self.ispan == other.ispan)

    def same_licensing(self, other):
        """
        Return True if other has the same detected license keys.
        """
        return self.rule.same_licensing(other.rule)

    def __lt__(self, other):
        return self.qstart < other.qstart

    @property
    def qstart(self):
        return self.qspan.start

    @property
    def qend(self):
        return self.qspan.end

    def qlen(self):
        """
        Return the length of the match as the number of matched query tokens.
        """
        return len(self.qspan)

    def qmagnitude(self):
        return self.qspan.magnitude()

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

    def imagnitude(self):
        return self.ispan.magnitude()

    @property
    def histart(self):
        return self.hispan.start

    @property
    def hiend(self):
        return self.hispan.end

    def hilen(self):
        """
        Return the length of the match as the number of matched query tokens.
        """
        return len(self.hispan)

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
        Return True if this match spans both surround other match spans.
        """
        return self.qsurround(other) and self.isurround(other)

    def is_qafter(self, other):
        return self.qspan.is_after(other.qspan)

    def is_iafter(self, other):
        return self.ispan.is_after(other.ispan)

    def is_after(self, other):
        """
        Return True if this match spans are strictly after other match spans.
        """
        return self.is_qafter(other) and self.is_iafter(other)

    def subtract(self, other):
        """
        Subtract an other match from this match by removing overlapping span
        items present in both matches from this match.
        """
        self.qspan.difference_update(other.qspan)
        self.ispan.difference_update(other.ispan)
        return self

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

        matches = sorted(matches, key=lambda m: (m.rule.rid, m.qspan.start, -m.qlen(), -m.ilen()))
        merged = []
        # only merge for now matches with the same rule
        # iterate on matches grouped by rule, one rule at a time.
        for _rid, rule_matches in groupby(matches, key=lambda m: m.rule.rid):
            rule_matches = list(rule_matches)
            i = 0
            if TRACE_MERGE:
                logger_debug('merge_match: processing rule:', rule_matches[0].rule.identifier())

            # compare two matches in the sorted sequence: current_match and the next one
            while i < len(rule_matches) - 1:
                current_match = rule_matches[i]
                j = i + 1
                if TRACE_MERGE:
                    logger_debug('merge_match: current_match:', current_match)

                while j < len(rule_matches):
                    next_match = rule_matches[j]
                    if TRACE_MERGE:
                        logger_debug(' merge_match: next_match:', next_match)

                    if next_match.same(current_match):
                        if TRACE_MERGE: logger_debug('    ==> NEW MERGED 2: identical:', current_match)
                        del rule_matches[j]
                        continue

                    if next_match.qdistance_to(current_match) >= max_dist or next_match.idistance_to(current_match) >= max_dist:
                        break

                    # surrounding
                    if current_match.surround(next_match):
                        current_match.update(next_match)
                        if TRACE_MERGE: logger_debug('    ==> NEW MERGED 1:', current_match)
#                         rule_matches[i] = current_match
                        del rule_matches[j]

#                     # next_match is in increasing sequence and touch
#                     elif (
#                           current_match.qstart <= next_match.qstart
#                     and   current_match.istart <= next_match.istart
#
#                     and next_match.qdistance_to(current_match) < max_dist
#                     and next_match.idistance_to(current_match) < max_dist):
#                         current_match.update(next_match)
#                         if TRACE_MERGE: logger_debug('    ==> NEW MERGED:', current_match)
# #                         rule_matches[i] = current_match
#                         del rule_matches[j]

                    # next_match is in increasing sequence and within a distance
                    elif (current_match.qstart < next_match.qstart
                    and current_match.qend < next_match.qend
                    and current_match.istart < next_match.istart
                    and current_match.iend < next_match.iend
                    and next_match.qdistance_to(current_match) < max_dist
                    and next_match.idistance_to(current_match) < max_dist
                    # and minimal overlap
#                     and current_match.qoverlap(next_match) > 5  # (current_match.ilen() / 10)
#                     and current_match.ioverlap(next_match) > 5  # (current_match.ilen() / 10)
                    ):
                        current_match.update(next_match)
                        if TRACE_MERGE: logger_debug('    ==> NEW MERGED 2:', current_match)
#                         rule_matches[i] = current_match
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
        # FIXME: we may be combining apples and oranges by considering same licensing too!
        same_licensing = self.same_licensing(other)
        if not (same_rule or same_licensing):

            raise TypeError('Cannot combine matches with different rules or licensing: from: %(self)r, to: %(other)r' % locals())

        if other._type not in self._type:
            new_type = ' '.join([self._type, other._type])
        else:
            new_type = self._type

        line_by_pos = dict(self.line_by_pos)
        line_by_pos.update(other.line_by_pos)

        combined = LicenseMatch(rule=self.rule,
                                qspan=Span(self.qspan | other.qspan),
                                ispan=Span(self.ispan | other.ispan),
                                hispan=Span(self.hispan | other.hispan),
                                line_by_pos=line_by_pos,
                                query_run_start=min(self.query_run_start, other.query_run_start),
                                _type=new_type)

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
        self._type = combined._type
        self.query_run_start = min(self.query_run_start, other.query_run_start)

        return self

    def rebase(self, new_query_start, line_by_pos, _type):
        """
        Return a copy of this match rebasing the qspan on the new query or query
        run start, using the new line_by_pos and updating the _type of match.
        """
        return LicenseMatch(
            rule=self.rule,
            qspan=Span(self.qspan.rebase(new_query_start - self.query_run_start)),
            ispan=Span(self.ispan),
            hispan=Span(self.hispan),
            line_by_pos=line_by_pos,
            query_run_start=new_query_start,
            _type=' '.join([self._type, _type]),
        )

    def score(self):
        """
        Return the score for this match as a float between 0 and 100.
        This is a ratio of matched tokens to the rule length.
        """
        # TODO: compute a better score based tf/idf, BM25, applying ratio to low tokens, etc
        if not self.rule.length:
            return 0
        score = self.ilen() / self.rule.length
        return round(score * 100, 2)

    def density(self):
        """
        Return the computed density of this match as a float between 0 and 1. A
        dense match has ispan contiguous and has a maximum density of one.
        A sparse match has some non-contiguous ispan.

        Density is not related to the score: a low scoring match can be dense
        and a high scoring match can be sparse.

        The density is computed as the ratio of ilen (effective number of
        matched itokens) to the magnitude of the qspan (actual maximal range of
        positions for this match).
        """
        dens = self.ilen() / self.qmagnitude()
        if TRACE and dens > 1:
            logger_debug('density cannot be bigger than 1', dens)
        return dens

    def min_idensity(self):
        """
        Return the minimum density as a float between 0 and 1 that this match
        should have to be considered as a good match.

        This is a function of the match length and the matched rule density.
        """
        return self.rule.min_density()

    def small(self):
        """
        Return True if this match is "small" based on its rule thresholds.
        """
        thresholds = self.rule.thresholds()
        min_ihigh = thresholds.min_high
        min_ilen = thresholds.min_len
        if self.hilen() < min_ihigh or self.ilen() < min_ilen:
            return True

    def sparse(self):
        """
        Return True if this match is "sparse" based on its rule thresholds.
        """
        thresholds = self.rule.thresholds()
        min_ihigh = thresholds.min_high
        min_ilen = thresholds.min_len
        max_igaps = thresholds.max_gaps

        # do not consider significant matches as sparse unless they are very sparse
        if self.hilen() > min_ihigh or self.ilen() > min_ilen:
            if (self.density() > self.min_idensity() or self.ispan.density() > self.min_idensity()):
                return False

        m_qmag = self.qmagnitude()

        m_rule_len = self.rule.length
        # long match that exceeds maximum gaps
        if m_qmag > m_rule_len + max_igaps:
            if TRACE_REFINE: logger_debug('     LicenseMatch.sparse: discarding1: m_qmag=%(m_qmag)r > m_rule_len=%(m_rule_len)r + max_igaps=%(max_igaps)r' % locals())
            return True

        # match that does not meet minimum density
        m_density = self.density()
        m_min_dens = self.min_idensity()
        if m_density < m_min_dens:
            if TRACE_REFINE: logger_debug('     LicenseMatch.sparse: discarding2: m_density=%(m_density)r < m_min_dens=%(m_min_dens)r' % locals())
            return True

        # small match that does not meet minimum density
        m_density = self.density()
        m_min_dens = self.min_idensity()
        if m_density < m_min_dens:
            if TRACE_REFINE: logger_debug('     LicenseMatch.sparse: discarding3: m_density=%(m_density)r < m_min_dens=%(m_min_dens)r' % locals())
            return True

        m_ilen = self.ilen()
        if TRACE_REFINE: logger_debug('     LicenseMatch.sparse: m_rule_len=%(m_rule_len)r m_ilen=%(m_ilen)r' % locals())
        if m_rule_len < 15 and m_ilen != m_rule_len:
            if TRACE_REFINE: logger_debug('     LicenseMatch.sparse: discarding4: m_rule_len=%(m_rule_len)r < 10 and m_ilen=%(m_ilen)r != m_rule_len' % locals())
            return True


        # finally consider actual gaps vs rule gaps
        # m_gaps_sum = m_qmag - self.qlen()
        # m_gaps = self.qspan.gaps()
        # m_density = self.density()
        # if m_density < self.min_idensity():
        #    return True


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
    matches = sorted(matches, key=lambda m: (m.qstart, -m.qlen(), -m.ilen()))


    if TRACE_FILTER: print('filter_matches: number of matches to process:', len(matches))

    discarded = []
    # compare two matches in the sorted sequence: current_match and the next one
    i = 0
    while i < len(matches) - 1:
        current_match = matches[i]
        if TRACE_FILTER: print('filter_match: current_match:', current_match)

        j = i + 1

        while j < len(matches):
            next_match = matches[j]
            if TRACE_FILTER: print(' filter_match: next_match:', next_match)

            # Skip qcontained, irrespective of licensing
            if current_match.contains_qspan(next_match):
                if TRACE_FILTER: print('   filter_matches: next_match in current_match')
#                 discarded.append(matches[j])
                del matches[j]
                continue

            # Skip same range contained, same of licensing
            if current_match.qsurround(next_match) and current_match.same_licensing(next_match):
                if TRACE_FILTER: print('   filter_matches: next_match in current_match region and same licensing')
#                 discarded.append(matches[j])
                del matches[j]
                continue


#             # if the next_match overlaps, merge it in current_match and delete it
#             if (current_match.rule== next_match.rule and current_match.qoverlap(next_match)):
#                 if TRACE_FILTER: print('   filter_matches: mergeable same rule')
#                 current_match = current_match.update(next_match)
#                 matches[i] = current_match
#                 del matches[j]
#                 continue

            # Skip fully qcontained in this match and next next match, irrespective of licensing
            if j + 1 < len(matches):
                next_next_match = matches[j + 1]
                this_and_next_next_qspan = current_match.qspan | next_next_match.qspan
                if next_match.qspan.issubset(this_and_next_next_qspan):
                    if TRACE_FILTER: print('   filter_matches: next_match qspan in (current_match+next_next_match)')
#                     discarded.append(matches[j])
                    del matches[j]
                    continue

#             # if the next_match is surrounded, and has some overlap, delete it
            if (current_match.surround(next_match) and (current_match.qlen() / next_match.qlen()) > 2):
                if TRACE_FILTER: print('   filter_matches: remove surrounded with much bigger match')
                matches[i] = current_match
                discarded.append(matches[j])
                del matches[j]
                continue

            if (current_match.qoverlap(next_match) > (current_match.ilen() / 5)
            and current_match.ioverlap(next_match) > (current_match.ilen() / 5)
            and current_match.same_licensing(next_match)
            ):
                current_match.update(next_match)
                if TRACE_FILTER: print('   filter_matches: combined overlapping')
                del matches[j]


            # otherwise check the next after next_match
            j += 1
        # otherwise use the next as the new reference match
        i += 1

    # FIXME: returned discarded too
    return matches, discarded


def filter_low_score(matches, min_score=100):
    """
    Return a new matches iterable filtering matches that are sparse with a low
    density of matched positions. Also return the matches that were filtered out.
    """
    kept = []
    discarded = []

    for match in matches:
        if match.score() >= min_score:
            kept.append(match)
        else:
            discarded.append(match)

    return kept, discarded


def filter_short_matches(matches):
    """
    Return a new matches iterable filtering matches shorter a minimal length
    using ipos. Never filter matches with a rule length shorter than the minimal
    length. Also return the matches that were filtered out.
    """
    kept = []
    discarded = []

    for match in matches:
        if match.small():
            if TRACE_REFINE: logger_debug('DISCARDING SHORT:', match)
            discarded.append(match)
        else:
            kept.append(match)
    return kept, discarded


def filter_sparse_matches(matches):
    """
    Return a new matches iterable filtering matches that are sparse with a low
    density of matched positions. Also return the matches that were filtered out.
    """
    kept = []
    discarded = []

    for match in matches:
        if match.sparse():
            if TRACE_REFINE: logger_debug('DISCARDING Sparse:', match)
            discarded.append(match)
        else:
            kept.append(match)
    return kept, discarded


def refine_matches(matches, min_score=0):
    """
    Return two sequences of matches: one contains refined good matches, and the
    other contains matches that were filtered out.
    """
    if TRACE: logger_debug('#####refine_matches: START matches#', len(matches))
    if TRACE_REFINE: map(logger_debug, matches)

    all_discarded = []

    logger_debug('   ##### refine_matches: MERGED_matches#:', len(matches))
    if TRACE_REFINE: map(logger_debug, matches)

    matches, discarded = filter_short_matches(matches)
    all_discarded.extend(discarded)
    if TRACE: logger_debug('   #####refine_matches: SHORT #', len(matches))
    if TRACE_REFINE: map(logger_debug, matches)
    if TRACE: logger_debug('   #####refine_matches: SHORT discarded#', len(discarded))
    if TRACE_REFINE: map(logger_debug, discarded)

    matches, discarded = filter_sparse_matches(matches)
    all_discarded.extend(discarded)
    if TRACE: logger_debug('   #####refine_matches: SPARSE filter#', len(matches))
    if TRACE_REFINE: map(logger_debug, matches)
    if TRACE: logger_debug('   #####refine_matches: SPARSE discarded#', len(discarded))
    if TRACE_REFINE: map(logger_debug, discarded)


    matches, discarded = filter_matches(matches)
    all_discarded.extend(discarded)
    logger_debug('   ##### refine_matches: FILTERED_matches#:', len(matches))
    if TRACE_REFINE: map(logger_debug, matches)
    if TRACE: logger_debug('   #####refine_matches: FILTERED discarded#', len(discarded))
    if TRACE_REFINE: map(logger_debug, discarded)

    if min_score:
        matches, discarded = filter_low_score(matches, min_score=min_score)
        all_discarded.extend(discarded)

        if TRACE: logger_debug('   #####refine_matches: LOW SCORE #', len(matches))
        if TRACE_REFINE: map(logger_debug, matches)
        if TRACE: logger_debug('   ###refine_matches: LOW SCORE discarded #:', len(discarded))
        if TRACE_REFINE: map(logger_debug, discarded)

    return matches, all_discarded
