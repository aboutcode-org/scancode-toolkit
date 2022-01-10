#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from enum import Enum

import attr
from license_expression import combine_expressions

from licensedcode.cache import build_spdx_license_expression
from licensedcode.cache import get_cache
from licensedcode.match import LicenseMatch
from licensedcode.models import compute_relevance

"""
LicenseDetection data structure and processing.

A LicenseDetection combines one or more matches together using various rules and
heuristics.
"""

TRACE = False


def logger_debug(*args): pass


if TRACE:
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


def matches_compact_repr(matches):
    """
    Return a string representing a list of license matches in a compact way.
    """
    return ', '.join(m.rule.identifier for m in matches)


@attr.s(slots=True, eq=False, order=False)
class LicenseDetection:
    """
    A LicenseDetection combines one or more LicenseMatch using multiple rules
    and heuristics. For instance, a "license intro" match followed by a proper
    match may be combined in a single detection for the matched license
    expression.
    """

    matches = attr.ib(
        repr=matches_compact_repr,
        default=attr.Factory(list),
        metadata=dict(
            help='List of license matches combined in this detection.'
        )
    )

    length = attr.ib(
        default=0,
        metadata=dict(help=
            'Detection length as the number of known tokens across all matches. '
            'Because of the possible overlap this may be inaccurate.'
        )
    )

    primary_license_expression = attr.ib(
        default=None,
        metadata=dict(
            help='Primary license expression string '
            'using the SPDX license expression syntax and ScanCode license keys.')
    )

    license_expression = attr.ib(
        default=None,
        metadata=dict(
            help='Full license expression string '
            'using the SPDX license expression syntax and ScanCode license keys.')
    )

    primary_spdx_license_expression = attr.ib(
        repr=False,
        default=None,
        metadata=dict(
            help='License expression string for this license detection'
            'using the SPDX license expression syntax and SPDX license ids.')
    )

    spdx_license_expression = attr.ib(
        repr=False,
        default=None,
        metadata=dict(
            help='Full license expression string for this license detection'
            'using the SPDX license expression syntax and SPDX license ids.')
    )

    combination_reasons = attr.ib(
        repr=False,
        default=attr.Factory(list),
        metadata=dict(
            help='A list of detection CombinationReason explaining how '
            'this detection was created.'
        )
    )

    def __eq__(self, other):
        return (
            isinstance(other, LicenseDetection)
            and self.matches == other.matches
        )

    def rules_length(self):
        """
        Return the length of the combined matched rules as the number
        of all rule tokens.
        Because of the possible overlap this may be inaccurate.
        """
        return sum(m.self.rule.length for m in self.matches)

    def coverage(self):
        """
        Return the score for this detection as a rounded float between 0 and 100.

        This is an indication of the how much this detection covers the rules of
        the underlying match.

        This is computed as the sum of the underlying matches coverage weighted
        by the length of a match to the overall detection length.
        """
        length = self.length
        weighted_coverages = (m.coverage() * (m.len() / length) for m in self.matches)
        return  min([round(sum(weighted_coverages), 2), 100])

    def relevance(self):
        """
        Return the ``relevance`` of this detection. The relevance
        is a float between 0 and 100 where 100 means highly relevant and 0 means
        not relevant at all.

        This is computed as the relevance of the sum of the underlying matches
        rule length.
        """
        return compute_relevance(self.rules_len)

    def score(self):
        """
        Return the score for this detection as a rounded float between 0 and 100.

        The score is an indication of the confidence of the detection.

        This is computed as the sum of the underlying matches score weighted
        by the length of a match to the overall detection length.
        """
        length = self.length
        weighted_scores = (m.score() * (m.len() / length) for m in self.matches)
        return  min([round(sum(weighted_scores), 2), 100])

    def append(
        self,
        match,
        reason=None,
        combine_license=False,
        override_license=False,
    ):
        """
        Append the ``match`` LicenseMatch to this detection and update it
        accordingly.
        Append the ``reason`` to the combination_reasons.

        If ``combine_license`` is True the license_expression of the ``match``
        is combined with the detection license_expression. Do not combine
        otherwise.

        If ``override_license`` is True, the license_expression of the ``match``
        replaces the the detection license_expression. Do not override license
        otherwise.

        ``combine_license`` and ``override_license`` are ignored for the first
        match appended to this detection: license is taken as is in this case.
        """
        if not isinstance(match, LicenseMatch):
            raise TypeError(f'Not a LicenseMatch: {match!r}')
        assert not (combine_license and override_license), (
            'combine_license and override_license are mutually exclusive'
        )

        if not self.matches:
            # first match is always an ovveride
            combine_license = False
            override_license = True

        self.matches.append(match)
        self.length += match.length
        if reason:
            self.combination_reasons.append(reason)

        licensing = get_cache().licensing
        if combine_license:
            license_expression = combine_expressions(
                [self.license_expression, match.license_expression],
                unique=True,
                licensing=licensing,
            )

            self.spdx_license_expression = build_spdx_license_expression(
                license_expression,
                licensing=licensing,
            )
            # FIXME: we are not yet doing anything wrt. primary licenses
            self.primary_license_expression = str(license_expression)
            self.primary_spdx_license_expression = self.spdx_license_expression

            self.license_expression = str(license_expression)

        elif override_license:
            # Use the match expression
            license_expression = licensing.parse(match.license_expression)

            self.spdx_license_expression = build_spdx_license_expression(
                license_expression,
                licensing=licensing,
            )
            # FIXME: we are not yet doing anything wrt. primary licenses
            self.primary_license_expression = str(license_expression)
            self.primary_spdx_license_expression = self.spdx_license_expression

            self.license_expression = str(license_expression)

    def matched_text(
        self,
        whole_lines=False,
        highlight=True,
        highlight_matched='{}',
        highlight_not_matched='[{}]',
    ):
        """
        Return the matched text for this detection, combining texts from all
        matches (that can possibly for different files.)
        """
        return '\n'.join(
            m.matched_text(
                whole_lines=whole_lines,
                highlight=highlight,
                highlight_matched=highlight_matched,
                highlight_not_matched=highlight_not_matched,
                _usecache=True
            )
            for m in self.matches
        )


def combine_license_intros(license_matches):
    """
    Return a filtered ``license_matches`` list of LicenseMatch objects removing
    spurious matches to license introduction statements (e.g.
    `is_license_intro` Rules.)

    A common source of false positive license detections in unstructured files
    are license introduction statements that are immediately followed by a
    license notice. In these cases, the license introduction can be discarded as
    this is for the license match that follows it.
    """

    return [match for match in license_matches if not is_license_intro(match)]


def is_license_intro(license_match):
    """
    Return True if `license_match` LicenseMatch object is matched completely to
    a unknown license intro present as a Rule.
    """
    from licensedcode.match_aho import MATCH_AHO_EXACT

    return (
        license_match.rule.is_license_intro
        and (
            license_match.matcher == MATCH_AHO_EXACT
            or license_match.coverage() == 100
        )
    )


class CombinationReason(Enum):
    NOT_COMBINED = 'not-combined'
    UNKNOWN_INTRO_FOLLOWED_BY_MATCH = 'unknown-intro-followed-by-match'
    CONTAINED_SAME_LICENSE = 'contained-with-same-license'
    NOTICE_FOLLOWED_BY_TEXT = 'notice-followed-by-text'
    CONTIGUOUS_SAME_LICENSE = 'contiguous-with-same-license'
    REF_FOLLOWED_BY_NOTICE = 'ref-followed-by-notice'
    REF_FOLLOWED_BY_TEXT = 'ref-followed-by-text'
    TAG_FOLLOWED_BY_NOTICE = 'tag-followed-by-notice'
    TAG_FOLLOWED_BY_TEXT = 'tag-followed-by-text'
    TAG_FOLLOWED_BY_REF = 'tag-followed-by-ref'
    UNKNOWN_FOLLOWED_BY_MATCH = 'unknown-ref-followed-by-match'
    UNVERSIONED_FOLLOWED_BY_VERSIONED = 'un-versioned-followed-by-versioned'


def combine_matches_in_detections(matches):
    """
    Return a list of LicenseDetection given a ``matches`` list of LicenseMatch.
    """
    # do not bother if there is only one match
    if len(matches) < 2:
        ld = LicenseDetection()
        ld.append(matches[0], CombinationReason.NOT_COMBINED)
        return [ld]

    matches = sorted(matches)

    detections = []
    current_detection = None

    # Compare current and next matches in the sorted sequence
    # Compare a pair and combine in LicenseDetection when relevant

    i = 0
    while i < len(matches) - 1:
        j = i + 1
        while j < len(matches):
            current_match = matches[i]
            next_match = matches[j]

            if not current_detection:
                current_detection = LicenseDetection()
                current_detection.append(current_match)

            # BREAK/shortcircuit rather than continue since continuing looking
            # next matches will yield no new possible addition to this
            # detection. e.g. stop when the distance between matches is too
            # large
            if current_match.distance_to(next_match) > 10:
                detections.append(current_detection)
                current_detection = None
                break

            # UNKNOWN_INTRO_FOLLOWED_BY_MATCH: combine current and next
            if (
                current_match.rule.is_license_intro and
                current_match.rule.is_unknown and (
                    next_match.rule.is_license_reference
                    or next_match.rule.is_license_text
                    or next_match.rule.is_license_notice
                )
            ):
                current_detection.append(
                    match=next_match,
                    reason=CombinationReason.UNKNOWN_INTRO_FOLLOWED_BY_MATCH,
                    override_license=True,
                )

            # CONTAINED_SAME_LICENSE: combine current and next
            elif (
                current_match.same_licensing(next_match) and
                current_match.qcontains(next_match)
            ):
                current_detection.append(
                    match=next_match,
                    reason=CombinationReason.CONTAINED_SAME_LICENSE,
                    # no license changes
                    override_license=False,
                    combine_license=False,
                )

            else:
                # do not combine, start a new detection
                detections.append(current_detection)
                current_detection = None

            j += 1
        i += 1

    return detections
