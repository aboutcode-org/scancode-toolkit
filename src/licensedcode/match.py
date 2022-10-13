#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from enum import IntEnum
from itertools import groupby
from typing import NamedTuple

import attr
from attr import validators

from licensedcode import MAX_DIST
from licensedcode import SMALL_RULE
from licensedcode import query
from licensedcode.spans import Span
from licensedcode.stopwords import STOPWORDS
from licensedcode.tokenize import index_tokenizer
from licensedcode.tokenize import matched_query_text_tokenizer

"""
LicenseMatch data structure and processing.
A key feature is merging and filtering of matches.

Merging combines match fragments made to the same license rule and that in the
correct sequence.

Filtering discards matches based on various heuristics and rules such as:

- containment: a small match is contained in a larger match
- overlap: based on a level of overlap between matches
- various spurious matches rules based on length, required content, etc.
- false positives

The filter functions are executed in a specific sequence over the list of matches.
"""

TRACE = False
TRACE_MERGE = False
TRACE_REFINE = False
TRACE_FILTER_FALSE_POSITIVE = False
TRACE_FILTER_CONTAINED = False
TRACE_FILTER_OVERLAPPING = False
TRACE_FILTER_SPURIOUS_SINGLE_TOKEN = False
TRACE_FILTER_SPURIOUS = False
TRACE_FILTER_SHORT = False
TRACE_FILTER_RULE_MIN_COVERAGE = False
TRACE_FILTER_BELOW_MIN_SCORE = False
TRACE_FILTER_SINGLE_WORD_GIBBERISH = False
TRACE_SET_LINES = False
TRACE_KEY_PHRASES = False
TRACE_REGIONS = False
TRACE_FILTER_LICENSE_LIST = False
TRACE_FILTER_LICENSE_LIST_DETAILED = False
TRACE_FILTER_INVALID_UNKNOWN = False

TRACE_MATCHED_TEXT = False
TRACE_MATCHED_TEXT_DETAILS = False
TRACE_HIGHLIGHTED_TEXT = False

# these control the details in a LicenseMatch representation
TRACE_REPR_MATCHED_RULE = False
TRACE_REPR_SPAN_DETAILS = False
TRACE_REPR_THRESHOLDS = False
TRACE_REPR_ALL_MATCHED_TEXTS = False


def logger_debug(*args): pass


if (TRACE
    or TRACE_MERGE
    or TRACE_REFINE
    or TRACE_FILTER_CONTAINED
    or TRACE_FILTER_OVERLAPPING
    or TRACE_FILTER_RULE_MIN_COVERAGE
    or TRACE_FILTER_SPURIOUS_SINGLE_TOKEN
    or TRACE_FILTER_SPURIOUS
    or TRACE_FILTER_SHORT
    or TRACE_FILTER_RULE_MIN_COVERAGE
    or TRACE_FILTER_BELOW_MIN_SCORE
    or TRACE_SET_LINES
    or TRACE_MATCHED_TEXT
    or TRACE_MATCHED_TEXT_DETAILS
    or TRACE_HIGHLIGHTED_TEXT
    or TRACE_FILTER_SINGLE_WORD_GIBBERISH
    or TRACE_KEY_PHRASES
    or TRACE_REGIONS
    or TRACE_FILTER_LICENSE_LIST
    or TRACE_FILTER_LICENSE_LIST_DETAILED
    or TRACE_FILTER_INVALID_UNKNOWN
):

    use_print = True
    if use_print:
        prn = print
    else:
        import logging
        import sys
        logger = logging.getLogger(__name__)
        # logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
        logging.basicConfig(stream=sys.stdout)
        logger.setLevel(logging.DEBUG)
        prn = logger.debug

    def logger_debug(*args):
        return prn(' '.join(isinstance(a, str) and a or repr(a) for a in args))

    def _debug_print_matched_query_text(match, extras=5):
        """
        Print a matched query text including `extras` tokens before and after
        the match. Used for debugging license matches.
        """
        # Create a fake new match with extra tokens before and after
        new_match = match.combine(match)
        new_qstart = max([0, match.qstart - extras])
        new_qend = min([match.qend + extras, len(match.query.tokens)])
        new_qspan = Span(new_qstart, new_qend)
        new_match.qspan = new_qspan

        logger_debug(new_match)
        logger_debug(' MATCHED QUERY TEXT with extras')
        qt = new_match.matched_text(whole_lines=False)
        logger_debug(qt)


class DiscardReason(IntEnum):
    NOT_DISCARDED = 0
    MISSING_KEY_PHRASES = 1
    BELOW_MIN_COVERAGE = 2
    SPURIOUS_SINGLE_TOKEN = 3
    TOO_SHORT = 4
    SCATTERED_ON_TOO_MANY_LINES = 5
    INVALID_SINGLE_WORD_GIBBERISH = 6
    SPURIOUS = 7
    CONTAINED = 8
    OVERLAPPING = 9
    NON_CONTINUOUS = 10
    FALSE_POSITIVE = 11
    BELOW_MIN_SCORE = 12
    LICENSE_LIST = 13


@attr.s(slots=True, eq=False, order=False, repr=False)
class LicenseMatch(object):
    """
    License detection match to a rule with matched query positions and lines and
    matched index positions. Also computes a score for a match. At a high level,
    a match behaves a little like a Span and has several similar methods taking
    into account both the query and index-side Spans.

    Note that the relationship between the query-side qspan Span and the index-
    side ispan Span is such that:

    - they always have the exact same number of items but when sorted each
      value at a given index may be different
    - the nth position when sorted by position is such that their token
      value is equal for this position.

    These properties mean that the qspan and ispan can be safely zipped with
    zip(). Also and as a convention throughout, we always use qspan first then
    ispan: in general we put query-related variables on the left hand side and
    index-related variables on the right hand side.
    """

    rule = attr.ib(
        metadata=dict(
            help='matched Rule object'
        )
    )

    qspan = attr.ib(
        metadata=dict(
            help='query text matched Span, start at zero which is the absolute '
                 'query start (not the query_run start)'
        )
    )

    ispan = attr.ib(
        metadata=dict(
            help='rule text matched Span, start at zero which is the rule start.'
        )
    )

    hispan = attr.ib(
        default=attr.Factory(Span),
        metadata=dict(
            help='rule text matched Span for high tokens, start at zero which '
                 'is the rule start. Always a subset of ispan.'
        )
    )

    query_run_start = attr.ib(
        default=0,
        metadata=dict(
            help='Starting position of the QueryRun where this match '
                 'was found.'
            )
    )

    matcher = attr.ib(
        default='',
        metadata=dict(
            help='A string indicating which matching procedure this match was '
                 'created with. Used for diagnostics, debugging and testing.'
        )
    )

    start_line = attr.ib(
        default=0,
        metadata=dict(help='match start line, 1-based')
    )

    end_line = attr.ib(
        default=0,
        metadata=dict(help='match end line, 1-based')
    )

    query = attr.ib(
        default=None,
        metadata=dict(help='Query object for this match')
    )

    discard_reason = attr.ib(
        default=DiscardReason.NOT_DISCARDED,
        validator=validators.in_(DiscardReason),
        metadata=dict(
            help='An internal reason code to track why a match was discarded '
            'e.g., filtered out.'
        )
    )

    def __repr__(
        self,
        trace_spans=TRACE_REPR_SPAN_DETAILS,
        trace_thresholds=TRACE_REPR_THRESHOLDS,
        trace_rule=TRACE_REPR_MATCHED_RULE,
        trace_text=TRACE_REPR_ALL_MATCHED_TEXTS,
    ):
        spans = ''
        if trace_spans:
            spans = (
                f'\n    qspan={self.qspan!r}, '
                f'\n    ispan={self.ispan!r}, '
                f'\n    hispan={self.hispan!r}'
             )

        thresh = ''
        if trace_thresholds:
            qdens = round(self.qdensity() * 100, 2)
            idens = round(self.idensity() * 100, 2)
            thresh = f'\n    qdens={qdens!r}, idens={idens!r}'

        rule_id = self.rule.identifier
        if trace_rule:
            rule_id = '\n    ' + repr(self.rule)

        qreg = (self.qstart, self.qend)
        ireg = (self.istart, self.iend)
        spans = spans
        thresh = thresh

        if trace_text:
            text = f'    matched_text:        {self.matched_text()!r}\n'
        else:
            text = ''
        return (
            f'LicenseMatch: '
            f'{self.rule.license_expression!r}, '
            f'lines={self.lines()!r}, '
            f'matcher={self.matcher!r}, '
            f'rid={rule_id}, '
            f'sc={self.score()!r}, '
            f'cov={self.coverage()!r}, '
            f'len={self.len()}, '
            f'hilen={self.hilen()}, '
            f'rlen={self.rule.length}, '
            f'qreg={qreg!r}, '
            f'ireg={ireg!r}'
            f'{thresh}{spans}'
            f'{text}'
        )

    def __eq__(self, other):
        """
        Strict equality is based on licensing, matched positions and not based
        on matched rule.
        """
        return (isinstance(other, LicenseMatch)
            and self.qspan == other.qspan
            and self.ispan == other.ispan
            and self.rule.same_licensing(other.rule)
        )

    def __ne__(self, other):
        """
        Strict inequality is based on licensing, matched positions and not based
        on matched rule.
        """
        return (not isinstance(other, LicenseMatch)
            or self.qspan != other.qspan
            or self.ispan != other.ispan
            or not self.rule.same_licensing(other.rule)
        )

    # NOTE: we implement all rich comparison operators with some inlining for
    # performance reasons

    def __lt__(self, other):
        if not isinstance(other, LicenseMatch):
            return NotImplemented

        return self.qstart < other.qstart

    def __lte__(self, other):
        if not isinstance(other, LicenseMatch):
            return NotImplemented

        return self.qstart < other.qstart or (
            self.qspan == other.qspan
            and self.ispan == other.ispan
            and self.rule.same_licensing(other.rule)
        )

    def __gt__(self, other):
        if not isinstance(other, LicenseMatch):
            return NotImplemented

        return self.qstart > other.qstart

    def __gte__(self, other):
        if not isinstance(other, LicenseMatch):
            return NotImplemented

        return self.qstart > other.qstart or (
            self.qspan == other.qspan
            and self.ispan == other.ispan
            and self.rule.same_licensing(other.rule)
        )

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

    def lines(self, line_by_pos=None):
        if line_by_pos:
            self.set_lines(line_by_pos)
        return self.start_line, self.end_line

    def set_lines(self, line_by_pos):
        """
        Set this match start and end lines using a mapping of ``line_by_pos``
        {pos: line}.
        """
        self.start_line = line_by_pos[self.qstart]
        self.end_line = line_by_pos[self.qend]
        if TRACE_SET_LINES:
            logger_debug('LicenseMatch.set_lines: match.start_line :', self.start_line)
            logger_debug('LicenseMatch.set_lines: match.end_line :', self.end_line)

    @property
    def qstart(self):
        return self.qspan.start

    @property
    def qend(self):
        return self.qspan.end

    def len(self):
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

    def hilen(self):
        """
        Return the length of the match as the number of matched high tokens.
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
        Overlapping matches have a zero distance.
        Non-overlapping touching matches have a distance of one.
        """
        return self.qspan.distance_to(other.qspan)

    def idistance_to(self, other):
        """
        Return the absolute ispan distance from self to other match.
        Overlapping matches have a zero distance.
        Non-overlapping touching matches have a distance of one.
        """
        return self.ispan.distance_to(other.ispan)

    def overlap(self, other):
        """
        Return the number of overlapping positions with other.
        """
        return self.qspan.overlap(other.qspan)

    def _icoverage(self):
        """
        Return the coverage of this match to the matched rule as a float between
        0 and 1.
        """
        if not self.rule.length:
            return 0
        return self.len() / self.rule.length

    def coverage(self):
        """
        Return the coverage of this match to the matched rule as a rounded float
        between 0 and 100.
        """
        return round(self._icoverage() * 100, 2)

    def qmagnitude(self):
        """
        Return the maximal query length represented by this match start and end
        in the query. This number represents the full extent of the matched
        query region including matched, unmatched AND unknown tokens, but
        excluding STOPWORDS.

        The magnitude is the same as the length if the match is a contiguous
        match without any unknown token in its range. It will be greater than
        the matched length for a non-contiguous match with gaps between its
        matched tokens. It can also be greater than the query length when there
        are unknown tokens in the matched range.
        """
        # The query side of the match may not be contiguous and may contain
        # unmatched known tokens or unknown tokens. Therefore we need to compute
        # the real portion query length including unknown tokens that is
        # included in this match, for both matches and unmatched tokens

        query = self.query
        qspan = self.qspan
        qmagnitude = self.qregion_len()

        # note: to avoid breaking many tests we check query presence
        if query:
            # Compute a count of unknown tokens that are inside the matched
            # range, ignoring end position of the query span: unknowns here do
            # not matter as they are never in the match but they influence the
            # score.
            unknowns_pos = qspan & query.unknowns_span
            qspe = qspan.end
            unknowns_pos = (pos for pos in unknowns_pos if pos != qspe)
            qry_unkxpos = query.unknowns_by_pos
            unknowns_in_match = sum(qry_unkxpos[pos] for pos in unknowns_pos)

            # update the magnitude by adding the count of unknowns in the match.
            # This number represents the full extent of the matched query region
            # including matched, unmatched and unknown tokens.
            qmagnitude += unknowns_in_match

        return qmagnitude

    def is_continuous(self):
        """
        Return True if the all the matched tokens of this match are continuous
        without any extra unmatched known or unkwown words, or stopwords.
        """
        return (
            self.len() == self.qregion_len() == self.qmagnitude()
        )

    def qregion(self):
        """
        Return the maximal positions Span representing this match from
        start to end as query positions, including matched and unmatched tokens.
        """
        return Span(self.qstart, self.qend)

    def qregion_len(self):
        """
        Return the maximal number of positions represented by this match start
        and end region of query positions including matched and unmatched
        tokens.
        """
        return self.qspan.magnitude()

    def qregion_lines(self):
        """
        Return the maximal lines Span that this match query regions covers.
        """
        return Span(self.start_line, self.end_line)

    def qregion_lines_len(self):
        """
        Return the maximal number of lines that this match query regions covers.
        """
        return self.end_line - self.start_line + 1

    def qdensity(self):
        """
        Return the query density of this match as a ratio of its length to its
        qmagnitude, a float between 0 and 1. A dense match has all its matched
        query tokens contiguous and a maximum qdensity of one. A sparse low
        qdensity match has some non-contiguous matched query tokens interspersed
        between matched query tokens. An empty match has a zero qdensity.
        """
        mlen = self.len()
        if not mlen:
            return 0
        qmagnitude = self.qmagnitude()
        if not qmagnitude:
            return 0
        return mlen / qmagnitude

    def idensity(self):
        """
        Return the ispan density of this match as a ratio of its rule-side
        matched length to its rule side magnitude. This is a float between 0 and
        1. A dense match has all its matched rule tokens contiguous and a
        maximum idensity of one. A sparse low idensity match has some non-
        contiguous matched rule tokens interspersed between matched rule tokens.
        An empty match has a zero qdensity.
        """
        return self.ispan.density()

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

        qmagnitude = self.qmagnitude()

        # Compute the score as the ration of the matched query length to the
        # qmagnitude, e.g. the length of the matched region
        if not qmagnitude:
            return 0

        # FIXME: this should exposed as an q/icoverage() method instead
        query_coverage = self.len() / qmagnitude
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
                f'from: {self!r}, to: {other!r}'
            )

        if other.matcher not in self.matcher:
            newmatcher = ' '.join([self.matcher, other.matcher])
        else:
            newmatcher = self.matcher

        if (
            self.discard_reason == DiscardReason.NOT_DISCARDED
            or other.discard_reason == DiscardReason.NOT_DISCARDED
        ):
            discard_reason = DiscardReason.NOT_DISCARDED

        elif (
            self.discard_reason == DiscardReason.MISSING_KEY_PHRASES
            and other.discard_reason == DiscardReason.MISSING_KEY_PHRASES
        ):
            discard_reason = DiscardReason.MISSING_KEY_PHRASES

        elif self.discard_reason == DiscardReason.MISSING_KEY_PHRASES:
            discard_reason = other.discard_reason

        elif other.discard_reason == DiscardReason.MISSING_KEY_PHRASES:
            discard_reason = self.discard_reason

        else:
            discard_reason = self.discard_reason

        combined = LicenseMatch(
            rule=self.rule,
            qspan=Span(self.qspan | other.qspan),
            ispan=Span(self.ispan | other.ispan),
            hispan=Span(self.hispan | other.hispan),
            query_run_start=min(self.query_run_start, other.query_run_start),
            matcher=newmatcher,
            query=self.query,
            discard_reason=discard_reason,
        )
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
        self.matcher = combined.matcher
        self.discard_reason = combined.discard_reason
        return self

    def is_small(self):
        """
        Return True if this match is "small" based on its rule lengths and
        thresholds. Small matches are spurious matches that are discarded.
        """
        matched_len = self.len()
        min_matched_len = self.rule.min_matched_length

        high_matched_len = self.hilen()
        min_high_matched_len = self.rule.min_high_matched_length

        if TRACE_FILTER_SHORT:
            logger_debug(
                f'LicenseMatch.is_small(): {self!r}: coverage: {self.coverage()}'
            )

        if matched_len < min_matched_len or high_matched_len < min_high_matched_len:
            if TRACE_FILTER_SHORT:
                logger_debug('  LicenseMatch.is_small(): CASE 1')
            return True

        if self.rule.is_small and self.coverage() < 80:
            if TRACE_FILTER_SHORT:
                logger_debug('  LicenseMatch.is_small(): CASE 2')
            return True

        if TRACE_FILTER_SHORT:
            logger_debug('  LicenseMatch.is_small(): not small')

        return False

    def itokens(self, idx):
        """
        Return the sequence of matched itoken ids.
        """
        ispan = self.ispan
        rid = self.rule.rid
        if rid is not None:
            for pos, token in enumerate(idx.tids_by_rid[rid]):
                if pos in ispan:
                    yield token

    def itokens_hash(self, idx):
        """
        Return a hash from the matched itoken ids.
        """
        from licensedcode.match_hash import index_hash
        itokens = list(self.itokens(idx))
        if itokens:
            return index_hash(itokens)

    # FIXME: this should be done for all the matches found in a given scanned
    # location at once to avoid reprocessing many times the original text
    def matched_text(
        self,
        whole_lines=False,
        highlight=True,
        highlight_matched='{}',
        highlight_not_matched='[{}]',
        _usecache=True
    ):
        """
        Return the matched text for this match or an empty string if no query
        exists for this match.

        `_usecache` can be set to False in testing to avoid any unwanted caching
        side effects as the caching depends on which index instance is being
        used and this index can change during testing.
        """
        if TRACE_MATCHED_TEXT:
            logger_debug(f'LicenseMatch.matched_text: self.query: {self.query}')

        query = self.query
        if not query:
            # TODO: should we raise an exception instead???
            # this case should never exist except for tests!
            return u''

        if whole_lines and query.has_long_lines:
            whole_lines = False

        return ''.join(get_full_matched_text(
            match=self,
            location=query.location,
            query_string=query.query_string,
            idx=query.idx,
            whole_lines=whole_lines,
            highlight=highlight,
            highlight_matched=highlight_matched,
            highlight_not_matched=highlight_not_matched,
            _usecache=_usecache
        )).rstrip()

    def get_highlighted_text(self, trace=TRACE_HIGHLIGHTED_TEXT):
        """
        Return HTML representing the full text of the original scanned file
        where the matched text portions and the non-matched text portions are
        highlighted using HTML tags.
        """
        if trace:
            logger_debug(f'LicenseMatch.get_highlighted_text: self.query: {self.query}')

        query = self.query
        if not query:
            return u''

        return ''.join(get_highlighted_lines(match=self, query=query, trace=trace))


def set_matched_lines(matches, line_by_pos):
    """
    Update a ``matches`` LicenseMatch sequence with start and end line given a
    `line_by_pos` {pos: line} mapping.
    """
    # if there is no line_by_pos, do not bother: the lines will stay to zero.
    if line_by_pos:
        for match in matches:
            match.set_lines(line_by_pos)


def merge_matches(matches, max_dist=None, trace=TRACE_MERGE):
    """
    Return a list of merged LicenseMatch matches given a `matches` list of
    LicenseMatch. Merging is a "lossless" operation that combines two or more
    matches to the same rule and that are in sequence of increasing query and
    index positions in a single new match.
    """
    # shortcut for single matches
    if len(matches) < 2:
        return matches

    # only merge matches with the same rule: sort then group by rule for the
    # same rule, sort on start, longer high, longer match, matcher type
    sorter = lambda m: (m.rule.identifier, m.qspan.start, -m.hilen(), -m.len(), m.matcher)
    matches.sort(key=sorter)
    matches_by_rule = [
        (rid, list(rule_matches))
        for rid, rule_matches
        in groupby(matches, key=lambda m: m.rule.identifier)
    ]

    if trace:
        print('merge_matches: number of matches to process:', len(matches))

    if max_dist is None:
        max_dist = MAX_DIST

    merged = []
    merged_extend = merged.extend

    for rid, rule_matches in matches_by_rule:
        if trace:
            logger_debug('merge_matches: processing rule:', rid)

        rule_length = rule_matches[0].rule.length

        # FIXME this is likely too much as we are getting gaps that are often too big
        max_rule_side_dist = min((rule_length // 2) or 1, max_dist)

        # compare two matches in the sorted sequence: current and next
        i = 0
        while i < len(rule_matches) - 1:
            j = i + 1
            while j < len(rule_matches):
                current_match = rule_matches[i]
                next_match = rule_matches[j]

                if trace:
                    logger_debug('---> merge_matches: current:', current_match)
                    logger_debug('---> merge_matches: next:   ', next_match)

                # FIXME: also considers the match length!
                # stop if we exceed max dist
                # or distance over 1/2 of rule length
                if (current_match.qdistance_to(next_match) > max_rule_side_dist
                or current_match.idistance_to(next_match) > max_rule_side_dist):

                    if trace:
                        logger_debug(
                            f'    ---> ###merge_matches: '
                            f'MAX_DIST/max_rule_side_dist: {max_rule_side_dist} reached, '
                            'breaking')

                    break

                # keep one of equal matches
                # with same qspan: FIXME: is this ever possible?
                if current_match.qspan == next_match.qspan and current_match.ispan == next_match.ispan:

                    if trace:
                        logger_debug(
                            '    ---> ###merge_matches: next EQUALS current, '
                            'del next')

                    del rule_matches[j]
                    continue

                # if we have two equal ispans and some overlap
                # keep the shortest/densest match in qspan e.g. the smallest magnitude of the two
                if current_match.ispan == next_match.ispan and current_match.overlap(next_match):
                    cqmag = current_match.qspan.magnitude()
                    nqmag = next_match.qspan.magnitude()
                    if cqmag <= nqmag:

                        if trace:
                            logger_debug(
                                '    ---> ###merge_matches: '
                                'current ispan EQUALS next ispan, current qmagnitude smaller, '
                                'del next')

                        del rule_matches[j]
                        continue
                    else:
                        if trace:
                            logger_debug(
                                '    ---> ###merge_matches: '
                                'current ispan EQUALS next ispan, next qmagnitude smaller, '
                                'del current')

                        del rule_matches[i]
                        i -= 1
                        break

                # remove contained matches
                if current_match.qcontains(next_match):

                    if trace:
                        logger_debug(
                            '    ---> ###merge_matches: '
                            'next CONTAINED in current, '
                            'del next')

                    del rule_matches[j]
                    continue

                # remove contained matches the other way
                if next_match.qcontains(current_match):
                    if trace:
                        logger_debug(
                            '    ---> ###merge_matches: '
                            'current CONTAINED in next, '
                            'del current')

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
                        if trace:
                            logger_debug(
                                '    ---> ###merge_matches: '
                                'current SURROUNDS next, '
                                'merged as new:', current_match)

                        del rule_matches[j]
                        continue

                # FIXME: qsurround is too weak. We want to check also isurround
                # merge surrounded the other way too: merge in current
                if next_match.surround(current_match):
                    new_match = current_match.combine(next_match)
                    if len(new_match.qspan) == len(new_match.ispan):
                        # the merged matched is likely aligned
                        next_match.update(current_match)
                        if trace:
                            logger_debug(
                                '    ---> ###merge_matches: '
                                'next SURROUNDS current, '
                                'merged as new:', current_match)

                        del rule_matches[i]
                        i -= 1
                        break

                # FIXME: what about the distance??

                # next_match is strictly in increasing sequence: merge in current
                if next_match.is_after(current_match):
                    current_match.update(next_match)
                    if trace:
                        logger_debug(
                            '    ---> ###merge_matches: '
                            'next follows current, '
                            'merged as new:', current_match)

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

                            if trace:
                                logger_debug(
                                    '    ---> ###merge_matches: '
                                    'next overlaps in sequence current, '
                                    'merged as new:', current_match)

                            del rule_matches[j]
                            continue

                j += 1
            i += 1
        merged_extend(rule_matches)
    return merged

# FIXME we should consider the length and distance between matches to break
# early from the loops: trying to check containment on wildly separated matches
# does not make sense


def filter_contained_matches(
    matches,
    trace=TRACE_FILTER_CONTAINED,
    reason=DiscardReason.CONTAINED,
):
    """
    Return a filtered list of kept LicenseMatch matches and a list of
    discardable matches given a `matches` list of LicenseMatch by removing
    matches that are contained in larger matches.

    For instance a match entirely contained in another bigger match is removed.
    When more than one matched position matches the same license(s), only one
    match of this set is kept.
    """

    # do not bother if there is only one match
    if len(matches) < 2:
        return matches, []

    discarded = []
    discarded_append = discarded.append

    # NOTE: we do not filter matches in place: sorted creates a copy
    # sort on start, longer high, longer match, matcher type
    sorter = lambda m: (m.qspan.start, -m.hilen(), -m.len(), m.matcher)
    matches = sorted(matches, key=sorter)
    matches_pop = matches.pop

    if trace:
        print('filter_contained_matches: number of matches to process:', len(matches))
        print('filter_contained_matches: initial matches')
        for m in matches:
            print(m)

    # compare two matches in the sorted sequence: current and next match we
    # progressively compare a pair and remove next or current
    i = 0
    while i < len(matches) - 1:
        j = i + 1
        while j < len(matches):
            current_match = matches[i]
            next_match = matches[j]
            if trace:
                logger_debug('---> filter_contained_matches: current: i=', i, current_match)
                logger_debug('---> filter_contained_matches: next:    j=', j, next_match)

            # BREAK/shortcircuit rather than continue since continuing looking
            # next matches will yield no new findings. e.g. stop when no overlap
            # is possible. Based on sorting order if no overlap is possible,
            # then no future overlap will be possible with the current match.
            # Note that touching and overlapping matches have a zero distance.
            if next_match.qend > current_match.qend:
                if trace:
                    logger_debug(
                        '    ---> ###filter_contained_matches: matches have a distance: '
                        'NO OVERLAP POSSIBLE -->',
                        'qdist:', current_match.qdistance_to(next_match))

                j += 1
                break

            # equals matched spans
            if current_match.qspan == next_match.qspan:
                if current_match.coverage() >= next_match.coverage():
                    if trace:
                        logger_debug(
                            '    ---> ###filter_contained_matches: '
                            'next EQUALS current, '
                            'removed next with lower or equal coverage', matches[j])

                    discarded_append(matches_pop(j))
                    continue
                else:
                    if trace:
                        logger_debug(
                            '    ---> ###filter_contained_matches: '
                            'next EQUALS current, '
                            'removed current with lower coverage', matches[i])
                    discarded_append(matches_pop(i))
                    i -= 1
                    break

            # remove contained matched spans
            if current_match.qcontains(next_match):
                if trace:
                    logger_debug(
                        '    ---> ###filter_contained_matches: '
                        'next CONTAINED in current, '
                        'removed next', matches[j])
                discarded_append(matches_pop(j))
                continue

            # remove contained matches the other way
            if next_match.qcontains(current_match):
                if trace:
                    logger_debug(
                        '    ---> ###filter_contained_matches: '
                        'current CONTAINED in next, '
                        'removed current', matches[i])
                discarded_append(matches_pop(i))
                i -= 1
                break

            j += 1
        i += 1

    for disc in discarded:
        disc.discard_reason = reason

    return matches, discarded


def filter_overlapping_matches(
    matches,
    skip_contiguous_false_positive=True,
    trace=TRACE_FILTER_OVERLAPPING,
    reason=DiscardReason.OVERLAPPING,
):
    """
    Return a filtered list of kept LicenseMatch matches and a list of
    discardable matches given a `matches` list of LicenseMatch by removing
    some overlapping matches using the importance of this overlap.

    For instance a shorter match mostly overlapping and contained considerably
    in another neighboring and larger match may be filtered.
    The overlap are qualified as small, media, large and extra large.
    """

    # do not bother if there is only one match
    if len(matches) < 2:
        return matches, []

    discarded = []
    discarded_append = discarded.append

    # overlap relationships and thresholds between two matches: based on
    # this containment we may prefer one match over the other and discard a
    # match
    OVERLAP_SMALL = 0.10
    OVERLAP_MEDIUM = 0.40
    OVERLAP_LARGE = 0.70
    OVERLAP_EXTRA_LARGE = 0.90

    # NOTE: we do not filter matches in place: sorted creates a copy
    # sort on start, longer high, longer match, matcher type
    sorter = lambda m: (m.qspan.start, -m.hilen(), -m.len(), m.matcher)
    matches = sorted(matches, key=sorter)
    matches_pop = matches.pop

    if trace:
        logger_debug(
            'filter_overlapping_matches: '
            'number of matches to process:', len(matches))
        logger_debug('filter_overlapping_matches: initial matches')
        for m in matches:
            logger_debug('  ', m,)
            print('========================')
            print(m.matched_text())
            print('========================')

    # compare two matches in the sorted sequence: current and next match we
    # progressively compare a pair and remove next or current
    i = 0
    while i < len(matches) - 1:
        j = i + 1
        while j < len(matches):
            current_match = matches[i]
            next_match = matches[j]

            if trace:
                logger_debug(
                    '  ---> filter_overlapping_matches: '
                    'current: i=', i, current_match)
                logger_debug(
                    '  ---> filter_overlapping_matches: '
                    'next:    j=', j, next_match)

            # BREAK/shortcircuit rather than continue since continuing looking
            # next matches will yield no new findings. e.g. stop when no overlap
            # is possible.
            if next_match.qstart > current_match.qend:
                if trace:
                    logger_debug(
                        '    ---> ###filter_overlapping_matches: matches disjoint: '
                        'NO OVERLAP POSSIBLE -->',
                        'qdist:', current_match.qdistance_to(next_match))

                j += 1
                break

            overlap = current_match.overlap(next_match)
            if not overlap:
                if trace:
                    logger_debug(
                        '    ---> ###filter_overlapping_matches: matches do not overlap: '
                        'NO OVERLAP POSSIBLE -->',
                        'qdist:', current_match.qdistance_to(next_match))

                j += 1
                continue

            if (skip_contiguous_false_positive
                and current_match.rule.is_false_positive
                and next_match.rule.is_false_positive
            ):
                if trace:
                    logger_debug(
                        '    ---> ###filter_overlapping_matches: '
                        'overlapping FALSE POSITIVES are not treated as overlapping.')

                j += 1
                continue

            # next match overlaps with current, so we handle overlapping
            # matches: determine overlap and containment relationships
            overlap_ratio_to_next = overlap / next_match.len()

            extra_large_next = overlap_ratio_to_next >= OVERLAP_EXTRA_LARGE
            large_next = overlap_ratio_to_next >= OVERLAP_LARGE
            medium_next = overlap_ratio_to_next >= OVERLAP_MEDIUM
            small_next = overlap_ratio_to_next >= OVERLAP_SMALL

            # current match overlap to next
            overlap_ratio_to_current = overlap / current_match.len()

            extra_large_current = overlap_ratio_to_current >= OVERLAP_EXTRA_LARGE
            large_current = overlap_ratio_to_current >= OVERLAP_LARGE
            medium_current = overlap_ratio_to_current >= OVERLAP_MEDIUM
            small_current = overlap_ratio_to_current >= OVERLAP_SMALL

            if trace:
                logger_debug(
                    '  ---> ###filter_overlapping_matches:',
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

            if extra_large_next and current_match.len() >= next_match.len():
                if trace:
                    logger_debug(
                        '      ---> ###filter_overlapping_matches: '
                        'EXTRA_LARGE next included, '
                        'removed shorter next', matches[j])

                discarded_append(matches_pop(j))
                continue

            if extra_large_current and current_match.len() <= next_match.len():
                if trace:
                    logger_debug(
                        '      ---> ###filter_overlapping_matches: '
                        'EXTRA_LARGE next includes current, '
                        'removed shorter current', matches[i])

                discarded_append(matches_pop(i))
                i -= 1
                break

            if large_next and current_match.len() >= next_match.len() and current_match.hilen() >= next_match.hilen():
                if trace:
                    logger_debug(
                        '      ---> ###filter_overlapping_matches: '
                        'LARGE next included, '
                        'removed shorter next', matches[j])

                discarded_append(matches_pop(j))
                continue

            if large_current and current_match.len() <= next_match.len() and current_match.hilen() <= next_match.hilen():
                if trace:
                    logger_debug(
                        '      ---> ###filter_overlapping_matches: '
                        'LARGE next includes '
                        'current, removed shorter current', matches[i])

                discarded_append(matches_pop(i))
                i -= 1
                break

            if medium_next:
                if trace:
                    logger_debug(
                        '    ---> ###filter_overlapping_matches: '
                        'MEDIUM NEXT')

                if (current_match.licensing_contains(next_match)
                    and current_match.len() >= next_match.len()
                    and current_match.hilen() >= next_match.hilen()
                ):
                    if trace:
                        logger_debug(
                            '      ---> ###filter_overlapping_matches: '
                            'MEDIUM next included with next licensing contained, '
                            'removed next', matches[j],)

                    discarded_append(matches_pop(j))
                    continue

                # case of a single trailing "license foo" nex match overlapping on "license" only
                if (next_match.len() == 2
                    and current_match.len() >= next_match.len() + 2
                    and current_match.hilen() >= next_match.hilen()
                    and current_match.rule.ends_with_license
                    and next_match.rule.starts_with_license
                ):
                    if trace:
                        logger_debug(
                            '      ---> ###filter_overlapping_matches: '
                            'MEDIUM next starts_with_license '
                            'and current ends_with_license, '
                            'removed next', matches[j],)

                    discarded_append(matches_pop(j))
                    continue

                if (next_match.licensing_contains(current_match)
                    and current_match.len() <= next_match.len()
                    and current_match.hilen() <= next_match.hilen()
                ):
                    if trace:
                        logger_debug(
                            '      ---> ###filter_overlapping_matches: '
                            'MEDIUM next includes current with current licensing contained, '
                            'removed current', matches[i])

                    discarded_append(matches_pop(i))
                    i -= 1
                    break

            if medium_current:
                if trace:
                    logger_debug(
                        '    ---> ###filter_overlapping_matches: '
                        'MEDIUM CURRENT')

                if (current_match.licensing_contains(next_match)
                    and current_match.len() >= next_match.len()
                    and current_match.hilen() >= next_match.hilen()
                ):
                    if trace:
                        logger_debug(
                            '      ---> ###filter_overlapping_matches: '
                            'MEDIUM current, bigger current with next licensing contained, '
                            'removed next', matches[j])

                    discarded_append(matches_pop(j))
                    continue

                if (next_match.licensing_contains(current_match)
                    and current_match.len() <= next_match.len()
                    and current_match.hilen() <= next_match.hilen()
                ):
                    if trace:
                        logger_debug(
                            '      ---> ###filter_overlapping_matches: '
                            'MEDIUM current, bigger next current with current licensing contained, '
                            'removed current', matches[i])

                    discarded_append(matches_pop(i))
                    i -= 1
                    break

            if (small_next
                and current_match.surround(next_match)
                and current_match.licensing_contains(next_match)
                and current_match.len() >= next_match.len()
                and current_match.hilen() >= next_match.hilen()
            ):
                if trace:
                    logger_debug(
                        '      ---> ###filter_overlapping_matches: '
                        'SMALL next surrounded, '
                        'removed next', matches[j])

                discarded_append(matches_pop(j))
                continue

            if (small_current
                and next_match.surround(current_match)
                and next_match.licensing_contains(current_match)
                and current_match.len() <= next_match.len()
                and current_match.hilen() <= next_match.hilen()
            ):
                if trace:
                    logger_debug(
                        '      ---> ###filter_overlapping_matches: '
                        'SMALL current surrounded, '
                        'removed current', matches[i])

                discarded_append(matches_pop(i))
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
                        clen = current_match.len()
                        # we want at least 90% of the current that is in the overlap
                        if overlap_len >= (clen * 0.9):
                            if trace:
                                logger_debug(
                                    '      ---> ###filter_overlapping_matches: '
                                    'current mostly contained in previous and next, '
                                    'removed current', matches[i])

                            discarded_append(matches_pop(i))
                            i -= 1
                            break

            j += 1
        i += 1

    if trace:
        print('filter_overlapping_matches: final  matches')
        for m in matches:
            print('  ', m)
        print('filter_overlapping_matches: final  discarded')
        for m in discarded:
            print('  ', m)

    for disc in discarded:
        disc.discard_reason = reason

    return matches, discarded


def restore_non_overlapping(matches, discarded):
    """
    Return a tuple of (matches, discarded) sequences of LicenseMatch given
    `matches` and `discarded` sequences of LicenseMatch. Reintegrate as matches
    these that may have been filtered too agressively.
    """
    all_matched_qspans = Span().union(*(m.qspan for m in matches))

    to_keep = []
    to_keep_append = to_keep.append

    to_discard = []
    to_discard_append = to_discard.append

    for disc in merge_matches(discarded):
        if not disc.qspan & all_matched_qspans:
            # keep previously discarded matches that do not intersect at all
            to_keep_append(disc)
            disc.discard_reason = DiscardReason.NOT_DISCARDED
        else:
            to_discard_append(disc)

    return to_keep, to_discard


def filter_below_rule_minimum_coverage(
    matches,
    trace=TRACE_FILTER_RULE_MIN_COVERAGE,
    reason=DiscardReason.BELOW_MIN_COVERAGE,
):
    """
    Return a filtered list of kept LicenseMatch matches and a list of
    discardable matches given a `matches` list of LicenseMatch by removing
    matches that have a coverage below a rule-defined minimum coverage.
    """
    from licensedcode.match_seq import MATCH_SEQ

    kept = []
    kept_append = kept.append
    discarded = []
    discarded_append = discarded.append

    for match in matches:
        # always keep exact matches
        if match.matcher != MATCH_SEQ:
            kept_append(match)
            continue

        if match.coverage() < match.rule.minimum_coverage:
            if trace:
                logger_debug(
                    '    ==> DISCARDING rule.minimum_coverage:',
                    type(match.rule.minimum_coverage), ':',
                    repr(match.rule.minimum_coverage),
                    'match:', match)

            match.discard_reason = reason
            discarded_append(match)
        else:
            kept_append(match)

    return kept, discarded


def filter_matches_below_minimum_score(
    matches,
    min_score=100,
    trace=TRACE_FILTER_BELOW_MIN_SCORE,
    reason=DiscardReason.BELOW_MIN_SCORE,
):
    """
    Return a filtered list of kept LicenseMatch matches and a list of
    discardable matches given a ``matches`` list of LicenseMatch by removing
    matches scoring below the provided ``min_score``.
    """
    if not min_score:
        return matches, []

    kept = []
    kept_append = kept.append
    discarded = []
    discarded_append = discarded.append

    for match in matches:
        if match.score() < min_score:
            if trace:
                logger_debug('    ==> DISCARDING low score:', match)

            match.discard_reason = reason
            discarded_append(match)
        else:
            kept_append(match)

    return kept, discarded


def filter_matches_to_spurious_single_token(
    matches,
    query=None,
    unknown_count=5,
    trace=TRACE_FILTER_SPURIOUS_SINGLE_TOKEN,
    reason=DiscardReason.SPURIOUS_SINGLE_TOKEN,
):
    """
    Return a filtered list of kept LicenseMatch matches and a list of
    discardable matches given a ``matches`` list of LicenseMatch by removing
    matches to a single token considered as "spurious" matches.

    A "spurious" single token match is a match to a single token that is
    surrounded on both sides by at least `unknown_count` tokens that are either
    unknown tokens, short tokens composed of a single character, tokens
    composed only of digits or several punctuations and stopwords.
    """
    from licensedcode.match_seq import MATCH_SEQ
    if not query:
        return matches, []

    kept = []
    kept_append = kept.append
    discarded = []
    discarded_append = discarded.append

    unknowns_by_pos = query.unknowns_by_pos
    shorts_and_digits = query.shorts_and_digits_pos

    for match in matches:
        if match.len() != 1:
            kept_append(match)
            continue

        # always keep extact matches
        if match.matcher != MATCH_SEQ:
            kept_append(match)
            continue

        qstart = match.qstart
        qend = match.qend

        # compute the number of unknown tokens before and after this single
        # matched position note:
        # - unknowns_by_pos is a dict,
        # - shorts_and_digits is a set of ints
        before = unknowns_by_pos.get(qstart - 1, 0)
        for p in range(qstart - 1 - unknown_count, qstart):
            if p in shorts_and_digits:
                before += 1
        if before < unknown_count:
            if trace:
                logger_debug(
                    '    ==> !!! NOT DISCARDING spurious_single_token, '
                    'not enough before:', match, before)
                _debug_print_matched_query_text(match, extras=unknown_count)

            kept_append(match)
            continue

        after = unknowns_by_pos.get(qstart, 0)
        for p in range(qend, qend + 1 + unknown_count):
            if p in shorts_and_digits:
                after += 1

        if after >= unknown_count:
            if trace:
                logger_debug('    ==> DISCARDING spurious_single_token:', match)
                _debug_print_matched_query_text(match, extras=unknown_count)

            match.discard_reason = reason
            discarded_append(match)
        else:
            if trace:
                logger_debug(
                    '    ==> !!! NOT DISCARDING spurious_single_token, '
                    'not enough after:', match, before, after)
                _debug_print_matched_query_text(match, extras=unknown_count)

            kept_append(match)

    return kept, discarded


def filter_too_short_matches(
    matches,
    trace=TRACE_FILTER_SHORT,
    reason=DiscardReason.TOO_SHORT,
):
    """
    Return a filtered list of kept LicenseMatch matches and a list of
    discardable matches given a `matches` list of LicenseMatch by removing
    matches considered as too small to be relevant.
    """
    from licensedcode.match_seq import MATCH_SEQ

    kept = []
    kept_append = kept.append
    discarded = []
    discarded_append = discarded.append

    for match in matches:
        if match.matcher == MATCH_SEQ and match.is_small():
            if trace:
                logger_debug('    ==> DISCARDING SHORT:', match)

            match.discard_reason = reason
            discarded_append(match)

        else:
            if trace:
                logger_debug('  ===> NOT DISCARDING SHORT:', match)

            kept_append(match)

    return kept, discarded


def split_weak_matches(matches):
    """
    Return a filtered list of kept LicenseMatch matches and a list of weak
    matches given a `matches` list of LicenseMatch by considering shorter
    sequence matches with a low coverage or match to unknown licenses. These are
    set aside before "unknown license" matching.
    """
    from licensedcode.match_seq import MATCH_SEQ

    kept = []
    kept_append = kept.append
    discarded = []
    discarded_append = discarded.append

    for match in matches:
        # always keep exact matches
        if (match.matcher == MATCH_SEQ
            and match.len() <= SMALL_RULE
            and match.coverage() <= 25
        ) or match.rule.has_unknown:

            discarded_append(match)
        else:
            kept_append(match)

    return kept, discarded


def filter_spurious_matches(
    matches,
    trace=TRACE_FILTER_SPURIOUS,
    reason=DiscardReason.SPURIOUS,
):
    """
    Return a filtered list of kept LicenseMatch matches and a list of
    discardable matches given a `matches` list of LicenseMatch by removing
    matches considered as irrelevant or spurious.

    Spurious matches are matches with a low density (e.g. where the matched
    tokens are separated by many unmatched tokens.)
    """
    from licensedcode.match_seq import MATCH_SEQ
    from licensedcode.match_unknown import MATCH_UNKNOWN

    kept = []
    kept_append = kept.append
    discarded = []
    discarded_append = discarded.append

    for match in matches:
        # always keep exact matches
        if match.matcher not in (MATCH_SEQ, MATCH_UNKNOWN):
            kept_append(match)
            continue

        qdens = match.qdensity()
        idens = match.idensity()
        mlen = match.len()
        hilen = match.hilen()

        if (mlen < 10 and (qdens < 0.1 or idens < 0.1)):
            if trace:
                logger_debug('    ==> DISCARDING Spurious1:', match)

            discarded_append(match)

        elif (mlen < 15 and (qdens < 0.2 or idens < 0.2)):
            if trace:
                logger_debug('    ==> DISCARDING Spurious2:', match)

            discarded_append(match)

        elif (mlen < 20 and hilen < 5 and (qdens < 0.3 or idens < 0.3)):
            if trace:
                logger_debug('    ==> DISCARDING Spurious3:', match)

            discarded_append(match)

        elif (mlen < 30 and hilen < 8 and (qdens < 0.4 or idens < 0.4)):
            if trace:
                logger_debug('    ==> DISCARDING Spurious4:', match)

            discarded_append(match)

        elif (qdens < 0.4 or idens < 0.4):
            if trace:
                logger_debug('    ==> DISCARDING Spurious5:', match)

            discarded_append(match)

        else:
            kept_append(match)

    for disc in discarded:
        disc.discard_reason = reason

    return kept, discarded


def filter_invalid_matches_to_single_word_gibberish(
    matches,
    trace=TRACE_FILTER_SINGLE_WORD_GIBBERISH,
    reason=DiscardReason.INVALID_SINGLE_WORD_GIBBERISH,
):
    """
    Return a filtered list of kept LicenseMatch matches and a list of
    discardable matches given a `matches` list of LicenseMatch by removing
    gibberish matches considered as invalid under these conditions:

    - the scanned file is a binary file (we could relax this in the future
    - the matched rule has a single word (length 1)
    - the matched rule "is_license_reference: yes"
    - the matched rule has a low relevance, e.g., under 75
    - the matched text has either:
      - one or more leading or trailing punctuations (except for +)
        unless this has a high relevance and the rule is contained as-is
        in the matched text (considering case)
      - mixed upper and lower case characters (but not a Title case) unless
        exactly the same mixed case as the rule text
    """
    kept = []
    kept_append = kept.append
    discarded = []
    discarded_append = discarded.append

    for match in matches:
        rule = match.rule
        if rule.length == 1 and rule.is_license_reference and match.query.is_binary:
            matched_text = match.matched_text(
                whole_lines=False,
                highlight=False,
            ).strip()

            rule_text = rule.text

            if trace:
                logger_debug(
                    '    ==> POTENTIAL INVALID GIBBERISH:', match,
                    'matched_text:', repr(matched_text),
                    'rule_text:', repr(rule_text)
                )

            if rule.relevance >= 80:
                max_diff = 1
            else:
                max_diff = 0

            if not is_valid_short_match(
                matched_text=matched_text,
                rule_text=rule_text,
                max_diff=max_diff,
            ):
                if trace:
                    logger_debug('    ==> DISCARDING INVALID GIBBERISH:', match)
                discarded_append(match)
                match.discard_reason = reason
                continue

        kept_append(match)

    return kept, discarded


def filter_invalid_contained_unknown_matches(
    unknown_matches,
    good_matches,
    trace=TRACE_FILTER_INVALID_UNKNOWN,
):
    """
    Return a filtered list of good_unknowns LicenseMatch unknown matches given
    an ``unknown_matches`` list of LicenseMatch resulting from unknown license
    detection by considering their containment in any "qregion" of the
    ``good_matches`` list of LicenseMatch.
    """
    good_unknowns = []
    good_unknowns_append = good_unknowns.append

    good_matches_qregions = [m.qregion() for m in good_matches]

    for match in unknown_matches:
        qspan = match.qspan
        if any(qspan in good_qregion for good_qregion in good_matches_qregions):
            if trace:
                logger_debug('    ==> DISCARDING INVALID UNKNOWN:', match)
        else:
            good_unknowns_append(match)

    return good_unknowns


def filter_short_matches_scattered_on_too_many_lines(
    matches,
    trace=TRACE_FILTER_SHORT,
    reason=DiscardReason.SCATTERED_ON_TOO_MANY_LINES,
):
    """
    Return a filtered list of kept LicenseMatch matches and a list of
    discardable matches given a ``matches`` list of LicenseMatch by removing
    short matches that are scattered on too many lines (including empty lines)
    to be considered as a proper, valid match.
    """
    # keep solo matches
    if len(matches) == 1:
        return matches, []

    kept = []
    kept_append = kept.append
    discarded = []
    discarded_append = discarded.append

    for match in matches:
        rule = match.rule
        if rule.is_small:
            matched_len = match.len()
            qregion_lines_len = match.qregion_lines_len()

            # Matches to license tag are special and can be scattered on a few
            # extra lines.
            if rule.is_license_tag:
                matched_len += 2

            # a match is scattered if it uses more lines than its token length
            if qregion_lines_len > matched_len:
                if trace: logger_debug('    ==> DISCARDING SCATTERED:', match)
                match.discard_reason = reason
                discarded_append(match)
                continue

        if trace: logger_debug('  ===> NOT DISCARDING SCATTERED:', match)
        kept_append(match)

    return kept, discarded


def is_valid_short_match(
    matched_text,
    rule_text,
    max_diff=0,
    trace=TRACE_FILTER_SINGLE_WORD_GIBBERISH,
):
    """
    Return True if the match with ``matched_text`` is a valid short match given
    a ``rule_text``.
    ``max_diff`` is the maximum number of character differences between these
    two texts that is considered as acceptable.

    For example:
    >>> is_valid_short_match("gpl", "GPL")
    True
    >>> is_valid_short_match("Gpl", "GPL")
    True
    >>> is_valid_short_match("gPl", "GPL")
    False
    >>> is_valid_short_match("GPL[", "GPL")
    False
    >>> is_valid_short_match("~gpl", "GPL")
    False
    >>> is_valid_short_match("GPL", "gpl")
    True
    >>> is_valid_short_match("Gpl+", "gpl+")
    True
    >>> is_valid_short_match("~gpl", "GPL", max_diff=0)
    False
    >>> is_valid_short_match("~gpl", "GPL", max_diff=1)
    True
    >>> is_valid_short_match("ALv2@", "ALv2", max_diff=1)
    True
    >>> is_valid_short_match("aLv2@", "ALv2", max_diff=1)
    False
    >>> is_valid_short_match("alv2@", "ALv2", max_diff=1)
    True
    >>> is_valid_short_match("GPLv2@", "GPLv2")
    True
    >>> is_valid_short_match("LGPL2@", "LGPL2")
    True
    >>> is_valid_short_match("gpl) &", "GPL")
    False
    >>> is_valid_short_match("GPLv2(", "GPLv2")
    True
    >>> is_valid_short_match("GPLv2", "GPLv2")
    True
    >>> is_valid_short_match("GPLV2+", "GPLv2+")
    True
    >>> is_valid_short_match("gplv2+", "GPLv2+")
    True
    >>> is_valid_short_match("LGPLV2+", "LGPLv2+")
    True
    >>> is_valid_short_match("LgplV2+", "LGPLv2+")
    True
    >>> is_valid_short_match("Cc0(", "CC0")
    False
    >>> is_valid_short_match("CC0", "CC0")
    True
    >>> is_valid_short_match("Cc0", "CC0")
    True
    >>> is_valid_short_match("COPYINGv3", "COPYINGV3")
    True
    >>> is_valid_short_match("MpL2", "MPL2")
    False
    >>> is_valid_short_match('WJa2!n"n#n$n;F#Cc0(n', "CC0")
    False

    """
    if trace:
        logger_debug(
            '==> is_valid_short_match:',
            'matched_text:', repr(matched_text),
            'rule_text:', repr(rule_text),
            'max_diff:', max_diff,
        )

    if matched_text == rule_text:
        return True

    # For long enough rules (length in characters), we consider all matches to
    # be correct
    len_rule_text = len(rule_text)
    if len_rule_text >= 5:
        return True

    # Length differences help decide that this is invalid as the extra chars
    # will be punctuation by construction
    diff = len(matched_text) - len_rule_text

    if diff and diff != max_diff:
        if trace:
            logger_debug(
                '    ==> is_valid_short_match:', 'diff:', diff,
                'max_diff:', max_diff)

        return False

    if rule_text.endswith('+'):
        matched_text = matched_text.rstrip('+')
        rule_text = rule_text.rstrip('+')

    # Same length, do we have mixed case? or title case?
    # All of same case and title case are OK, mixed case not OK.
    is_title_case = matched_text.istitle()

    if is_title_case:
        if trace:
            logger_debug(
                '    ==> is_valid_short_match:',
                'is_title_case:', 'matched_text:', matched_text)

        return True

    is_same_case_for_all_chars = (
        matched_text.lower() == matched_text
        or matched_text.upper() == matched_text
    )

    if is_same_case_for_all_chars:
        if trace:
            logger_debug(
                '    ==> is_valid_short_match:',
                'is_same_case_for_all_chars:',
                'matched_text:', matched_text, 'rule_text:', rule_text)

        return True

    matched_text_contains_full_rule_text = rule_text in matched_text
    if matched_text_contains_full_rule_text:
        if trace:
            logger_debug(
                '    ==> is_valid_short_match:',
                'matched_text_contains_full_rule_text:',
                'matched_text:', matched_text, 'rule_text:', rule_text)

        return True

    if trace:
        logger_debug('    ==> is_valid_short_match:', 'INVALID', matched_text)

    return False


def filter_false_positive_matches(
    matches,
    trace=TRACE_REFINE or TRACE_FILTER_FALSE_POSITIVE,
    reason=DiscardReason.FALSE_POSITIVE,
):
    """
    Return a filtered list of kept LicenseMatch matches and a list of
    discardable matches given a ``matches`` list of LicenseMatch by removing
    matches to false positive rules.
    """
    kept = []
    kept_append = kept.append
    discarded = []
    discarded_append = discarded.append

    for match in matches:
        if match.rule.is_false_positive:
            if trace:
                logger_debug('    ==> DISCARDING FALSE POSITIVE:', match)

            match.discard_reason = reason
            discarded_append(match)
        else:
            kept_append(match)

    return kept, discarded


def filter_matches_missing_key_phrases(
    matches,
    trace=TRACE_KEY_PHRASES,
    reason=DiscardReason.MISSING_KEY_PHRASES,
):
    """
    Return a filtered list of kept LicenseMatch matches and a list of
    discardable matches  given a ``matches`` list of LicenseMatch by removing
    all ``matches`` that do not contain all key phrases defined in their matched
    rule.
    A key phrase must be matched exactly without gaps or unknown words.

    A rule with "is_continuous" set to True is the same as if its whole text
    was defined as a keyphrase and is processed here too.
    """
    # never discard a solo match, unless matched to "is_continuous" rule
    if len(matches) == 1:
        rule = matches[0]
        if not rule.is_continuous:
            return matches, []

    kept = []
    kept_append = kept.append
    discarded = []
    discarded_append = discarded.append

    if trace:
        logger_debug('filter_matches_missing_key_phrases')

    for match in matches:
        if trace:
            logger_debug('  CHECKING KEY PHRASES for:', match)

        is_continuous = match.rule.is_continuous
        ikey_spans = match.rule.key_phrase_spans

        if not (ikey_spans or is_continuous):
            kept_append(match)
            if trace:
                logger_debug('    ==> KEEPING, NO KEY PHRASES OR IS_CONTINUOUS DEFINED')
            continue

        if is_continuous and not match.is_continuous():
            discarded_append(match)
            if trace:
                logger_debug('    ==> DISCARDING, IS_CONTINUOUS BUT NOT IS_CONTINUOUS')
            continue

        ispan = match.ispan
        if not is_continuous:
            if any(ikey_span not in ispan for ikey_span in ikey_spans):
                if trace:
                    logger_debug(
                        '    ==> DISCARDING, KEY PHRASES MISSING',
                        'ikey_spans:', ikey_spans,
                        'ispan:', ispan,
                    )
                match.discard_reason = reason
                discarded_append(match)
                continue
        else:
            # use whole ispan in this case
            ikey_spans = [match.ispan]

        # keep matches as candidate if they contain all key phrase positions in the ispan
        if trace:
            print('    CANDIDATE TO KEEP: all ikey_span in match.ispan:', ikey_spans, ispan)

        # discard matches that contain key phrases, but interrupted by
        # unknown or stop words.

        unknown_by_pos = match.query.unknowns_by_pos

        qstopwords_by_pos = match.query.stopwords_by_pos
        qstopwords_by_pos_get = qstopwords_by_pos.get

        istopwords_by_pos = match.rule.stopwords_by_pos
        istopwords_by_pos_get = istopwords_by_pos.get

        # iterate on each key phrase span to ensure that they are continuous
        # and contain no unknown words on the query side

        is_valid = True

        qspan = match.qspan

        for ikey_span in ikey_spans:

            # check that are no gaps in the key phrase span on the query side
            # BUT, do not redo the check for is_continuous already checked above
            if is_continuous:
                qkey_span = qspan
            else:
                qkey_poss = (
                    qpos for qpos, ipos in zip(qspan, ispan)
                    if ipos in ikey_span
                )

                qkey_span = Span(qkey_poss)
                if len(qkey_span) != qkey_span.magnitude():

                    logger_debug(
                        '    ==> DISCARDING, KEY PHRASES PRESENT, BUT NOT CONTINUOUS:',
                        'qkey_span:', qkey_span, 'qpan:', qspan
                    )

                    is_valid = False
                    break

            # check that key phrase spans does not contain stop words and does
            # not contain unknown words

            # NOTE: we do not check the last qkey_span position of a key phrase
            # since unknown is a number of words after a given span position:
            # these are pinned to the last position and we would not care for
            # what unknown or stop words show up after a key phrase ends.

            qkey_span_end = qkey_span.end
            contains_unknown = any(
                qpos in unknown_by_pos for qpos in qkey_span
                if qpos != qkey_span_end
            )

            if contains_unknown:
                logger_debug(
                    '    ==> DISCARDING, KEY PHRASES PRESENT, BUT UNKNOWNS:',
                    'qkey_span:', qkey_span, 'qpan:', qspan,
                    'unknown_by_pos:', unknown_by_pos
                )

                is_valid = False
                break

            has_same_stopwords_pos = True
            for qpos, ipos in zip(qspan, ispan):
                if qpos not in qkey_span or qpos == qkey_span_end:
                    continue

                if istopwords_by_pos_get(ipos) != qstopwords_by_pos_get(qpos):
                    has_same_stopwords_pos = False
                    break

            if not has_same_stopwords_pos:
                logger_debug(
                    '    ==> DISCARDING, KEY PHRASES PRESENT, BUT STOPWORDS NOT SAME:',
                    'qkey_span:', qkey_span, 'qpan:', qspan,
                    'istopwords_by_pos:', istopwords_by_pos,
                    'qstopwords_by_pos:', qstopwords_by_pos
                )

                is_valid = False
                break

        if is_valid:
            logger_debug('    ==> KEEPING, KEY PHRASES PRESENT, CONTINUOUS AND NO UNKNOWNS')
            kept_append(match)
        else:
            match.discard_reason = reason
            discarded_append(match)

        if trace:
            print()

    return kept, discarded


def get_matching_regions(
    matches,
    min_tokens_gap=10,
    min_lines_gap=3,
    trace=TRACE_REGIONS,
):
    """
    Return a list of token query position Spans, where each Span represents a
    region of related LicenseMatch contained that Span given a ``matches`` list
    of LicenseMatch.

    Matching regions are such that:

    - all matches in the regions are entirely contained in the region Span

    Two consecutive region Spans are such that:

    - there are no overlaping matches between them
    - there are at least ``min_tokens_gap`` unmatched tokens between them
    - OR there are at least ``min_lines_gap`` unmatched lines between them
    """
    regions = []

    prev_region = None
    prev_region_lines = None
    cur_region = None
    cur_region_lines = None

    for match in matches:
        if trace:
            logger_debug('Match:', match)
        if not prev_region:
            prev_region = match.qregion()
            prev_region_lines = match.qregion_lines()
        else:
            cur_region = match.qregion()
            cur_region_lines = match.qregion_lines()

            if trace:
                logger_debug(
                    '  prev_region:', prev_region,
                    'cur_region:', cur_region,
                    'prev_region.distance_to(cur_region):',
                    prev_region.distance_to(cur_region),
                )
                logger_debug(
                    '  prev_region_lines:', prev_region_lines,
                    'cur_region_lines:', cur_region_lines,
                    'prev_region_lines.distance_to(cur_region_lines):',
                    prev_region_lines.distance_to(cur_region_lines)
                )

            if (prev_region.distance_to(cur_region) > min_tokens_gap
                or prev_region_lines.distance_to(cur_region_lines) > min_lines_gap
            ):

                regions.append(prev_region)

                prev_region = cur_region
                prev_region_lines = cur_region_lines
            else:
                prev_region = Span(prev_region.start, cur_region.end)
                prev_region_lines = Span(prev_region_lines.start, cur_region_lines.end)

    if prev_region and prev_region not in regions:
        regions.append(prev_region)

    if trace:
        logger_debug('Final regions:', regions,)

    return regions


# min length for a short sequence of false positives
MIN_SHORT_FP_LIST_LENGTH = 15

# min proportion of the matches with unique license expression
MIN_UNIQUE_LICENSES_PROPORTION = 1 / 3

# min length for a long sequence of false positives
MIN_LONG_FP_LIST_LENGTH = 150


def filter_false_positive_license_lists_matches(
    matches,
    min_matches=MIN_SHORT_FP_LIST_LENGTH,
    min_matches_long=MIN_LONG_FP_LIST_LENGTH,
    min_unique_licenses_proportion=MIN_UNIQUE_LICENSES_PROPORTION,
    reason=DiscardReason.LICENSE_LIST,
    trace=TRACE_FILTER_LICENSE_LIST,
):
    """
    Return a filtered list of kept LicenseMatch matches and a list of
    discardable matches given a `matches` list of LicenseMatch by checking false
    positive status for matches to lists of licenses ids such as lists of SPDX
    license ids found in license-related tools code or data files.
    """

    # do not bother if there are not enough matches
    len_matches = len(matches)
    if len_matches < min_matches:
        return matches, []

    # TODO: adjust arguments based on well-known filenames from SPDX tools
    # for instance hackage needs 1/6 licenses as
    # use simplified procedure if there are many matches
    if len_matches > min_matches_long:
        if is_list_of_false_positives(
            matches=matches,
            min_matches=min_matches_long,
            min_candidate_proportion=0.95,
            min_unique_licenses=min_matches_long,
            min_unique_licenses_proportion=min_unique_licenses_proportion,
            trace=trace,
        ):

            if trace:
                print('filter_false_positive_license_lists_matches: ALL FP!')

            # discard all matches
            return [], matches

    # other, use detailed procedure where we try to identify sub-sequences
    # of false positives matches

    if trace:
        print('filter_false_positive_license_lists_matches: '
              'number of matches to process:', len_matches)
        print('initial matches')
        for m in matches:
            print('  ', m)

    kept = []
    kept_append = kept.append
    kept_extend = kept.extend
    discarded = []
    discarded_extend = discarded.extend

    # a list of discardable candidates contiguous matches
    discardable_candidates = []

    # max distance between two matches
    max_distance = 10

    for match in matches:
        if trace:
            print('  -----------------------------------------------------------')
            print('  PROCESSING MATCH:', match)

        is_candidate = is_candidate_false_positive(match)

        if is_candidate:
            if trace: print('  IS CANDIDATE')
            if not discardable_candidates:
                if trace: print('    FIRST DISCARDABLE APPEND')
                discardable_candidates.append(match)
                continue

            previous = discardable_candidates[-1]
            is_within_distance = previous.qdistance_to(match) <= max_distance
            if is_within_distance:
                if trace: print('    CLOSE ENOUGH:', previous.qdistance_to(match))
                discardable_candidates.append(match)

            else:
                if trace: print('    NOT CLOSE ENOUGH:', previous.qdistance_to(match))

                # is_candidate but not close enough
                if is_list_of_false_positives(discardable_candidates):
                    if trace: print('      IS FP: EXTEND DISCARD')
                    discarded_extend(discardable_candidates)
                else:
                    if trace: print('      IS NOT FP: EXTEND KEEP')
                    kept_extend(discardable_candidates)

                if trace: print('    IS NOT FP: NEW FIRST')
                discardable_candidates.clear()
                discardable_candidates.append(match)

        else:
            if trace: print('  NOT CANDIDATE')
            # not is_candidate:
            if is_list_of_false_positives(discardable_candidates):
                if trace: print('      IS FP: EXTEND DISCARD')
                discarded_extend(discardable_candidates)
            else:
                if trace: print('      IS NOT FP: EXTEND KEEP')
                kept_extend(discardable_candidates)

            if trace: print('    IS NOT CAN: KEEP CURRENT')
            discardable_candidates.clear()
            kept_append(match)

    # if we have some left, process them
    if discardable_candidates:

        if is_list_of_false_positives(discardable_candidates):
            if trace: print(' left overdiscardable_candidates: is_list_of_false_positives, discarded')
            discarded_extend(discardable_candidates)
        else:
            if trace: print(' left overdiscardable_candidates: NOT is_list_of_false_positives, kept')
            kept_extend(discardable_candidates)

    for disc in discarded:
        disc.discard_reason = reason

    if trace:
        print('filter_false_positive_license_lists_matches: final KEPT matches')
        for m in kept:
            print('  ', m)
        print('filter_false_positive_license_lists_matches: final DISCARDED matches')
        for m in discarded:
            print('  ', m)

    return kept, discarded


def count_unique_licenses(matches):
    """
    Return a count of unique license expression
    """
    return len(set(m.rule.license_expression for m in matches))


# min number of unique license expression across matches
MIN_UNIQUE_LICENSES = MIN_SHORT_FP_LIST_LENGTH * MIN_UNIQUE_LICENSES_PROPORTION

# Most matches are on a single line, only a few are not
# e.g. qregion_lines_len is 1


def is_list_of_false_positives(
    matches,
    min_matches=MIN_SHORT_FP_LIST_LENGTH,
    min_unique_licenses=MIN_UNIQUE_LICENSES,
    min_unique_licenses_proportion=MIN_UNIQUE_LICENSES_PROPORTION,
    min_candidate_proportion=0,
    trace=TRACE_FILTER_LICENSE_LIST,
):
    """
    Return True if all LicenseMatch in the ``matches`` list form a proper false
    positive license list sequence.

    Check that:
    - there are at least ``min_matches`` matches

    - there is at least ``min_unique_licenses_proportion`` proportion of the
      matches with unique license expression. If all matches have a unique
      license expression, then this proportion is "1". If each license
      expression is repeated three times in the ``matches``, then the proportion
      is 1/3.

    - if there is not at least ``min_unique_licenses_proportion`` there are at
      least ``min_unique_licenses`` unique license expressions.

    - there is at least ``min_candidate_proportion`` proportion of matches with
      "is_candidate_false_positive()" returning True . This is a float between 0
      and 1. The check is skipped if the value is '0'.
    """
    if not matches:
        return [], []

    len_matches = len(matches)

    is_long_enough_sequence = len_matches >= min_matches

    if trace:
        print('      ========================================================')
        print('      is_long_enough_sequence:', is_long_enough_sequence)

    len_unique_licenses = count_unique_licenses(matches)
    has_enough_licenses = (
        len_unique_licenses / len_matches > min_unique_licenses_proportion
    )
    if trace:
        print(
            '      has_enough_licenses:', has_enough_licenses,
            'min_unique_licenses_proportion:', min_unique_licenses_proportion,
            'len_unique_licenses', len_unique_licenses,
            'len_matches:', len_matches,
            'len(unique_expressions)/len_matches:', len_unique_licenses / len_matches
        )

    if not has_enough_licenses:
        if trace:
            print(
                '      NOT has_enough_licenses:', has_enough_licenses,
                'but len_unique_licenses >= min_unique_licenses:',
                len_unique_licenses, '>=', min_unique_licenses,
            )
        has_enough_licenses = len_unique_licenses >= min_unique_licenses

    has_enough_candidates = True
    if min_candidate_proportion:
        candidates_count = len([
            m for m in matches
            if is_candidate_false_positive(m)
        ])
        has_enough_candidates = (
            (candidates_count / len_matches)
            > min_candidate_proportion
        )
        if trace:
            print(
                '      has_enough_candidates:', has_enough_candidates,
                'min_candidate_proportion:', min_candidate_proportion,
                'candidates_count:', candidates_count,
                'len_matches:', len_matches,
                'candidates_count / len_matches:', candidates_count / len_matches,
            )
    else:
        if trace:
            print('      has_enough_licenses    :', has_enough_licenses)

    is_fp = (
        is_long_enough_sequence
        and has_enough_licenses
        and has_enough_candidates
    )
    if trace:
        print('      is_list_of_false_positives    :', is_fp)
        print('      ========================================================')

    return is_fp


def is_candidate_false_positive(
    match,
    max_length=20,
    trace=TRACE_FILTER_LICENSE_LIST_DETAILED,
):
    """
    Return True if the ``match`` LicenseMatch is a candidate false positive
    license list match.
    """
    is_candidate = (
        # only tags or refs,
        (match.rule.is_license_reference or match.rule.is_license_tag)
        # but not tags that are SPDX license identifiers
        and not match.matcher == '1-spdx-id'
        # exact matches only
        and match.coverage() == 100

        # not too long
        and match.len() <= max_length
    )

    if trace:
        print('  MATCH:', match)
        print('  is_candidate_false_positive:', is_candidate,
              'is_license_reference:', match.rule.is_license_reference,
              'is_license_tag:', match.rule.is_license_tag,
              'coverage:', match.coverage(),
              'match.len():', match.len(), '<=', 'max_length:', max_length,
              ':', match.len() <= max_length
          )
    return is_candidate


def refine_matches(
    matches,
    query=None,
    min_score=0,
    filter_false_positive=True,
    merge=True,
    trace_basic=TRACE,
    trace=TRACE_REFINE,
):
    """
    Return a filtered list of kept LicenseMatch matches and a list of
    discardable matches given a `matches` list of LicenseMatch by removing
    matches that do not mee certain criteria as defined in multiple filters.
    """

    if trace_basic:
        logger_debug()
        logger_debug(' #####refine_matches: STARTING matches#', len(matches))
    if trace:
        for m in matches:
            logger_debug(m)
    if not matches:
        return [], []

    all_discarded = []
    all_discarded_extend = all_discarded.extend

    if merge:
        matches = merge_matches(matches)

        if trace_basic:
            logger_debug('     ##### refine_matches: STARTING MERGED_matches#:', len(matches))

    def _log(_matches, _discarded, msg):
        if trace_basic:
            logger_debug('   #####refine_matches: KEPT', msg, '#', len(matches))

        if trace:
            for m in matches:
                logger_debug(m)

        if trace_basic:
            logger_debug('   #####refine_matches: DISCARDED NOT', msg, '#', len(_discarded))

        if trace:
            for m in matches:
                logger_debug(m)

    set_matched_lines(matches, query.line_by_pos)

    # FIXME: we should have only a single loop on all the matches at once!!
    # and not 10's of loops!!!

    matches, discarded = filter_matches_missing_key_phrases(matches)
    all_discarded_extend(discarded)
    _log(matches, discarded, 'HAS KEY PHRASES')

    matches, discarded = filter_spurious_matches(matches)
    all_discarded_extend(discarded)
    _log(matches, discarded, 'GOOD')

    matches, discarded = filter_below_rule_minimum_coverage(matches)
    all_discarded_extend(discarded)
    _log(matches, discarded, 'ABOVE MIN COVERAGE')

    matches, discarded = filter_matches_to_spurious_single_token(matches, query)
    all_discarded_extend(discarded)
    _log(matches, discarded, 'MORE THAN ONE NON SPURIOUS TOKEN')

    matches, discarded = filter_too_short_matches(matches)
    all_discarded_extend(discarded)
    _log(matches, discarded, 'LONG ENOUGH')

    matches, discarded = filter_short_matches_scattered_on_too_many_lines(matches)
    all_discarded_extend(discarded)
    _log(matches, discarded, 'ACCEPTABLE IF NOT SHORT SCATTERED')

    matches, discarded = filter_invalid_matches_to_single_word_gibberish(matches)
    all_discarded_extend(discarded)
    _log(matches, discarded, 'MORE THAN ONE NON INVALID GIBBERISH TOKEN')

    # TODO: we seem to be always merging?
    matches = merge_matches(matches)

    if trace_basic:
        logger_debug(' #####refine_matches: before FILTER matches#', len(matches))
    if trace:
        for m in matches:
            logger_debug(m)

    matches, discarded_contained = filter_contained_matches(matches)
    _log(matches, discarded_contained, 'NON CONTAINED')

    matches, discarded_overlapping = filter_overlapping_matches(matches)
    _log(matches, discarded_overlapping, 'NON OVERLAPPING')

    if discarded_contained:
        to_keep, discarded_contained = restore_non_overlapping(matches, discarded_contained)
        matches.extend(to_keep)
        all_discarded_extend(discarded_contained)
        _log(to_keep, discarded_contained, 'NON CONTAINED REFINED')

    if discarded_overlapping:
        to_keep, discarded_overlapping = restore_non_overlapping(matches, discarded_overlapping)
        matches.extend(to_keep)
        all_discarded_extend(discarded_overlapping)
        _log(to_keep, discarded_overlapping, 'NON OVERLAPPING REFINED')

    matches, discarded_contained = filter_contained_matches(matches)
    all_discarded_extend(discarded_contained)
    _log(matches, discarded_contained, 'NON CONTAINED')

    if filter_false_positive:
        matches, discarded = filter_false_positive_matches(matches)
        all_discarded_extend(discarded)
        _log(matches, discarded, 'TRUE POSITIVE')

        # license listings are false positive-like
        matches, discarded = filter_false_positive_license_lists_matches(matches)
        all_discarded_extend(discarded)
        _log(matches, discarded, 'NOT A LICENSE LIST')

    if min_score:
        matches, discarded = filter_matches_below_minimum_score(matches, min_score=min_score)
        all_discarded_extend(discarded)
        _log(matches, discarded, 'HIGH ENOUGH SCORE')

    if merge:
        matches = merge_matches(matches)

    if trace:
        logger_debug('   ##### refine_matches: FINAL MERGED_matches#:', len(matches))
        for m in matches:
            logger_debug(m)

    return matches, all_discarded


@attr.s(slots=True, frozen=True)
class Token1:
    """
    Used to represent a token in collected query-side matched texts and SPDX
    identifiers.
    """
    # original text value for this token.
    value = attr.ib()
    # line number, one-based
    line_num = attr.ib()
    # absolute position for known tokens, zero-based. -1 for unknown tokens
    pos = attr.ib(default=-1)
    # True if text/alpha False if this is punctuation or spaces
    is_text = attr.ib(default=False)
    # True if part of a match
    is_matched = attr.ib(default=False)
    # True if this is a known token
    is_known = attr.ib(default=False)


class Token2:
    """
    Used to represent a token in collected query-side matched texts and SPDX
    identifiers.
    """
    __slots__ = (
        'value',
        'line_num',
        'pos',
        'is_text',
        'is_matched',
        'is_known',
    )

    def __init__(
        self,
        value,
        line_num,
        pos=-1,
        is_text=False,
        is_matched=False,
        is_known=False
    ):
        # original text value for this token.
        self.value = value
        # line number, one-based
        self.line_num = line_num
        # absolute position for known tokens, zero-based. -1 for unknown tokens
        self.pos = pos
        # True if text/alpha False if this is punctuation or spaces
        self.is_text = is_text
        # True if part of a match
        self.is_matched = is_matched
        # True if this is a known token
        self.is_known = is_known


class Token3(NamedTuple):
    """
    Used to represent a token in collected query-side matched texts and SPDX
    identifiers.
    """
    # original text value for this token.
    value: str
    # line number, one-based
    line_num: int
    # absolute position for known tokens, zero-based. -1 for unknown tokens
    pos: int = -1
    # True if text/alpha False if this is punctuation or spaces
    is_text: bool = False
    # True if part of a match
    is_matched: bool = False
    # True if this is a known token
    is_known: bool = False


# we try different variants of tokens to find the fastest one
Token = Token1


def tokenize_matched_text(
    location,
    query_string,
    dictionary,
    start_line=1,
    _cache={},
):
    """
    Return a list of Token objects with pos and line number collected from the
    file at `location` or the `query_string` string. `dictionary` is the index
    mapping a token string to a token id.

    NOTE: the _cache={} arg IS A GLOBAL mutable by design.
    """
    key = location, query_string, start_line
    cached = _cache.get(key)
    if cached:
        return cached
    # we only cache the last call
    _cache.clear()
    _cache[key] = result = list(
        _tokenize_matched_text(
            location=location,
            query_string=query_string,
            dictionary=dictionary,
            start_line=start_line,
        )
    )
    return result


def _tokenize_matched_text(
    location,
    query_string,
    dictionary,
    start_line=1,
    trace=TRACE_MATCHED_TEXT_DETAILS,
):
    """
    Yield Token objects with pos and line number collected from the file at
    `location` or the `query_string` string. `dictionary` is the index mapping
    of tokens to token ids.
    """
    pos = 0
    qls = query.query_lines(
        location=location,
        query_string=query_string,
        strip=False,
        start_line=start_line,
    )
    for line_num, line in qls:
        if trace:
            logger_debug('  _tokenize_matched_text:',
                'line_num:', line_num,
                'line:', line)

        for is_text, token_str in matched_query_text_tokenizer(line):
            if trace:
                logger_debug('     is_text:', is_text, 'token_str:', repr(token_str))

            # Determine if a token is is_known in the license index or not. This
            # is essential as we need to realign the query-time tokenization
            # with the full text to report proper matches.
            if is_text and token_str and token_str.strip():

                # we retokenize using the query tokenizer:
                # 1. to lookup for is_known tokens in the index dictionary

                # 2. to ensure the number of tokens is the same in both
                # tokenizers (though, of course, the case will differ as the
                # regular query tokenizer ignores case and punctuations).

                # NOTE: we have a rare Unicode bug/issue because of some Unicode
                # codepoint such as some Turkish characters that decompose to
                # char + punct when casefolded. This should be fixed in Unicode
                # release 14 and up and likely implemented in Python 3.10 and up
                # See https://github.com/nexB/scancode-toolkit/issues/1872
                # See also: https://bugs.python.org/issue34723#msg359514
                qtokenized = list(index_tokenizer(token_str))
                if not qtokenized:

                    yield Token(
                        value=token_str,
                        line_num=line_num,
                        is_text=is_text,
                        is_known=False,
                        pos=-1,
                    )

                elif len(qtokenized) == 1:
                    is_known = qtokenized[0] in dictionary
                    if is_known:
                        p = pos
                        pos += 1
                    else:
                        p = -1

                    yield Token(
                        value=token_str,
                        line_num=line_num,
                        is_text=is_text,
                        is_known=is_known,
                        pos=p,
                    )
                else:
                    # we have two or more tokens from the original query mapped
                    # to a single matched text tokenizer token.
                    for qtoken in qtokenized:
                        is_known = qtoken in dictionary
                        if is_known:
                            p = pos
                            pos += 1
                        else:
                            p = -1

                        yield Token(
                            value=qtoken,
                            line_num=line_num,
                            is_text=is_text,
                            is_known=is_known,
                            pos=p,
                        )
            else:

                yield Token(
                    value=token_str,
                    line_num=line_num,
                    is_text=False,
                    is_known=False,
                    pos=-1,
                )


def reportable_tokens(
    tokens,
    match_qspan,
    start_line,
    end_line,
    whole_lines=False,
    trace=TRACE_MATCHED_TEXT_DETAILS,
):
    """
    Yield Tokens from a ``tokens`` iterable of Token objects (built from a query-
    side scanned file or string) that are inside a ``match_qspan`` matched Span
    starting at `start_line` and ending at ``end_line``. If whole_lines is True,
    also yield unmatched Tokens that are before and after the match and on the
    first and last line of a match (unless the lines are very long text lines or
    the match is from binary content.)

    As a side effect, known matched tokens are tagged as "is_matched=True" if
    they are matched.

    If ``whole_lines`` is True, any token within matched lines range is
    included. Otherwise, a token is included if its position is within the
    matched ``match_qspan`` or it is a punctuation token immediately after the
    matched ``match_qspan`` even though not matched.
    """
    start = match_qspan.start
    end = match_qspan.end

    started = False
    finished = False

    end_pos = 0
    last_pos = 0
    for real_pos, tok in enumerate(tokens):
        if trace:
            logger_debug('reportable_tokens: processing', real_pos, tok)

        # ignore tokens outside the matched lines range
        if tok.line_num < start_line:
            if trace:
                logger_debug('  tok.line_num < start_line:', tok.line_num, '<', start_line)

            continue

        if tok.line_num > end_line:
            if trace:
                logger_debug('  tok.line_num > end_line', tok.line_num, '>', end_line)

            break

        if trace:
            logger_debug('reportable_tokens:', real_pos, tok)

        is_included = False

        # tagged known matched tokens (useful for highlighting)
        if tok.pos != -1 and tok.is_known and tok.pos in match_qspan:
            tok = attr.evolve(tok, is_matched=True)
            is_included = True
            if trace:
                logger_debug('  tok.is_matched = True', 'match_qspan:', match_qspan)
        else:
            if trace:
                logger_debug(
                    '  unmatched token: tok.is_matched = False',
                    'match_qspan:', match_qspan,
                    'tok.pos in match_qspan:', tok.pos in match_qspan,
                )

        if whole_lines:
            # we only work on matched lines so no need to test further
            # if start_line <= tok.line_num <= end_line.
            if trace:
                logger_debug('  whole_lines')

            is_included = True

        else:
            # Are we in the match_qspan range or a punctuation right before or after
            # that range?

            # start
            if not started and tok.pos == start:
                started = True
                if trace:
                    logger_debug('  start')

                is_included = True

            # middle
            if started and not finished:
                if trace:
                    logger_debug('    middle')

                is_included = True

            if tok.pos == end:
                if trace:
                    logger_debug('  at end')

                finished = True
                started = False
                end_pos = real_pos

            # one punctuation token after a match
            if finished and not started and end_pos and last_pos == end_pos:
                end_pos = 0
                if not tok.is_text:
                    # strip the trailing spaces of the last token
                    if tok.value.strip():
                        if trace:
                            logger_debug('  end yield')

                        is_included = True

        last_pos = real_pos
        if is_included:
            yield tok


def get_full_matched_text(
    match,
    location=None,
    query_string=None,
    idx=None,
    whole_lines=False,
    highlight=True,
    highlight_matched='{}',
    highlight_not_matched='[{}]',
    only_matched=False,
    stopwords=STOPWORDS,
    _usecache=True,
    trace=TRACE_MATCHED_TEXT,
):
    """
    Yield strings corresponding to the full matched query text given a ``match``
    LicenseMatch detected with an `idx` LicenseIndex in a query file at
    ``location`` or a ``query_string``.

    See get_full_qspan_matched_text() for other arguments documentation
    """
    if trace:
        logger_debug('get_full_matched_text:  match:', match)

    return get_full_qspan_matched_text(
        match_qspan=match.qspan,
        match_query_start_line=match.query.start_line,
        match_start_line=match.start_line,
        match_end_line=match.end_line,
        location=location,
        query_string=query_string,
        idx=idx,
        whole_lines=whole_lines,
        highlight=highlight,
        highlight_matched=highlight_matched,
        highlight_not_matched=highlight_not_matched,
        only_matched=only_matched,
        stopwords=stopwords,
        _usecache=_usecache,
        trace=trace,
    )


def get_full_qspan_matched_text(
    match_qspan,
    match_query_start_line,
    match_start_line,
    match_end_line,
    location=None,
    query_string=None,
    idx=None,
    whole_lines=False,
    highlight=True,
    highlight_matched='{}',
    highlight_not_matched='[{}]',
    only_matched=False,
    stopwords=STOPWORDS,
    _usecache=True,
    trace=TRACE_MATCHED_TEXT,
):
    """
    Yield strings corresponding to words of the matched query text given a
    ``match_qspan`` LicenseMatch qspan Span detected with an `idx` LicenseIndex
    in a query file at ``location`` or a ``query_string``.

    - ``match_query_start_line`` is the match query.start_line
    - ``match_start_line`` is the match start_line
    - ``match_end_line`` is the match= end_line

    The returned strings contains the full text including punctuations and
    spaces that are not participating in the match proper including punctuations.

    If ``whole_lines`` is True, the unmatched part at the start of the first
    matched line and the unmatched part at the end of the last matched lines are
    also included in the returned text (unless the line is very long).

    If ``highlight`` is True, each token is formatted for "highlighting" and
    emphasis with the ``highlight_matched`` format string for matched tokens or to
    the ``highlight_not_matched`` for tokens not matched. The default is to
    enclose an unmatched token sequence in [] square brackets. Punctuation is
    not highlighted.

    if ``only_matched`` is True, only matched tokens are returned and
    ``whole_lines`` and ``highlight`` are ignored. Unmatched words are replaced
    by a "dot".

    If ``_usecache`` is True, the tokenized text is cached for efficiency.
    """
    if trace:
        logger_debug('get_full_qspan_matched_text:  match_qspan:', match_qspan)
        logger_debug('get_full_qspan_matched_text:  location:', location)
        logger_debug('get_full_qspan_matched_text:  query_string :', query_string)

    assert location or query_string
    assert idx

    if only_matched:
        # use highlighting to skip the reporting of unmatched entirely
        whole_lines = False
        highlight = True
        highlight_matched = '{}'
        highlight_not_matched = '.'
        highlight = True

    # Create and process a stream of Tokens
    if not _usecache:
        # for testing only, reset cache on each call
        tokens = tokenize_matched_text(
            location=location,
            query_string=query_string,
            dictionary=idx.dictionary,
            start_line=match_query_start_line,
            _cache={},
        )
    else:
        tokens = tokenize_matched_text(
            location=location,
            query_string=query_string,
            dictionary=idx.dictionary,
            start_line=match_query_start_line,
        )

    if trace:
        tokens = list(tokens)
        print()
        logger_debug('get_full_qspan_matched_text:  tokens:')
        for t in tokens:
            print('    ', t)
        print()

    tokens = reportable_tokens(
        tokens=tokens,
        match_qspan=match_qspan,
        start_line=match_start_line,
        end_line=match_end_line,
        whole_lines=whole_lines,
    )

    if trace:
        tokens = list(tokens)
        logger_debug('get_full_qspan_matched_text:  reportable_tokens:')
        for t in tokens:
            print(t)
        print()

    # Finally yield strings with eventual highlightings
    for token in tokens:
        val = token.value
        if not highlight:
            yield val
        else:
            if token.is_text and val.lower() not in stopwords:
                if token.is_matched:
                    yield highlight_matched.format(val)
                else:
                    yield highlight_not_matched.format(val)
            else:
                # we do not highlight punctuation and stopwords.
                yield val


def get_highlighted_lines(
    match,
    query,
    stopwords=STOPWORDS,
    trace=TRACE_HIGHLIGHTED_TEXT,
):
    """
    Yield highlighted text lines (with line returns) for the whole of the matched and unmatched text of a ``query``.
    """
    tokens = tokenize_matched_text(
        location=query.location,
        query_string=query.query_string,
        dictionary=query.idx.dictionary,
        start_line=match.query.start_line,
        _cache={},
    )
    tokens = tag_matched_tokens(tokens=tokens, match_qspan=match.qspan)

    if trace:
        tokens = list(tokens)
        print()
        logger_debug('get_highlighted_lines:  tokens:')
        for t in tokens:
            print('    ', t)
        print()
    header = '''<style>
      pre.log {color: #f1f1f1; background-color: #222; font-family: monospace;}
      pre.wrap {white-space: pre-wrap;}
      span.not-matched {color:#f5bf3c;}
      span.matched {color:#000000;}
</style>

<div class="license-match"><pre>'''
    footer = '''</pre></div>'''

    yield header
    highlight_matched = '<span class="matched">{}</span>'
    highlight_not_matched = '<span class="not-matched">{}</span>'
    for token in tokens:
        val = token.value
        if token.is_text and val.lower() not in stopwords:
            if token.is_matched:
                yield highlight_matched.format(val)
            else:
                yield highlight_not_matched.format(val)
        else:
            # we do not highlight punctuation and stopwords.
            yield highlight_not_matched.format(val)

    yield footer


def tag_matched_tokens(tokens, match_qspan):
    """
    Yield Tokens from a ``tokens`` iterable of Token objects.
    Known matched tokens are tagged as "is_matched=True" if they are matched.
    """
    for tok in tokens:
        # tagged known matched tokens (useful for highlighting)
        if tok.pos != -1 and tok.is_known and tok.pos in match_qspan:
            tok = attr.evolve(tok, is_matched=True)
        yield tok
