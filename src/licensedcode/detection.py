#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
import logging
from enum import Enum

import attr
from license_expression import combine_expressions

from licensedcode.cache import build_spdx_license_expression
from licensedcode.cache import get_cache
from licensedcode.match import LicenseMatch
from licensedcode.models import compute_relevance
from licensedcode.tokenize import query_tokenizer

"""
LicenseDetection data structure and processing.

A LicenseDetection combines one or more matches together using various rules and
heuristics.
"""

TRACE = os.environ.get('SCANCODE_DEBUG_LICENSE_DETECTION', False)


def logger_debug(*args):
    pass


logger = logging.getLogger(__name__)


if TRACE:
    import sys

    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, str) and a or repr(a) for a in args))


SPDX_LICENSE_URL = 'https://spdx.org/licenses/{}'
DEJACODE_LICENSE_URL = 'https://enterprise.dejacode.com/urn/urn:dje:license:{}'
SCANCODE_LICENSEDB_URL = 'https://scancode-licensedb.aboutcode.org/{}'

# All values of match_coverage less than this value are taken as
# `near-perfect-match-coverage` cases
NEAR_PERFECT_MATCH_COVERAGE_THR = 100

# Values of match_coverage less than this are taken as `imperfect-match-coverage` cases
IMPERFECT_MATCH_COVERAGE_THR = 95

# Values of match_coverage less than this are reported as `license_clues` matches
CLUES_MATCH_COVERAGE_THR = 60

# How many Lines in between has to be present for two matches being of a different group
# (i.e. and therefore, different rule)
LINES_THRESHOLD = 4

# Threshold Values of start line and rule length for a match to likely be a false positive
# (more than the start_line threshold and less than the rule_length threshold)
FALSE_POSITIVE_START_LINE_THRESHOLD = 1000
FALSE_POSITIVE_RULE_LENGTH_THRESHOLD = 3

# Whether to Use the NLP BERT Models
USE_LICENSE_CASE_BERT_MODEL = False
USE_FALSE_POSITIVE_BERT_MODEL = False

ISSUE_CASES_VERSION = 0.1



DETECTION_CATEGORIES = {
    "perfect-detection": "The license detection is accurate.",
    "imperfect-match-coverage": (
        "The license detection is inconclusive with high confidence, because only "
        "a small part of the rule text is matched."
    ),
    "near-perfect-match-coverage": (
        "The license detection is conclusive with a medium confidence because "
        "because most, but not all of the rule text is matched."
    ),
    "extra-words": (
        "The license detection is conclusive with high confidence because all the "
        "rule text is matched, but some unknown extra words have been inserted in "
        "the text."
    ),
    "false-positive": (
        "The license detection is inconclusive, and is unlikely to be about a "
        "license as a piece of code/text is detected.",
    ),
    "unknown-match": (
        "The license detection is inconclusive, as the license matches have "
        "been matched to rules having unknown as their license key"
    ),
}


class CombinationReason(Enum):
    NOT_COMBINED = 'not-combined'
    UNKNOWN_REFERENCE_TO_LOCAL_FILE = 'unknown-reference-to-local-file' 
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


@attr.s(slots=True, eq=False, order=False)
class LicenseDetection:
    """
    A LicenseDetection combines one or more LicenseMatch using multiple rules
    and heuristics. For instance, a "license intro" match followed by a proper
    match may be combined in a single detection for the matched license
    expression.
    """

    license_expression = attr.ib(
        default=None,
        metadata=dict(
            help='Full license expression string '
            'using the SPDX license expression syntax and ScanCode license keys.')
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

    matches = attr.ib(
        #repr=matches_compact_repr,
        default=attr.Factory(list),
        metadata=dict(
            help='List of license matches combined in this detection.'
        )
    )

    @classmethod
    def from_matches(cls, matches):
        """
        Return a LicenseDetection created out of `matches` list of LicenseMatch
        objects after computing the license_expression by analyzing and combining
        matches for the different cases.
        """
        reasons, license_expression = get_detected_license_expression(
            matches=matches,
            analysis=analyze_detection(matches),
        )

        if license_expression == None:
            return cls(matches=matches)

        spdx_license_expression = build_spdx_license_expression(
            str(license_expression),
            licensing=get_cache().licensing
        )

        return cls(
            matches=matches,
            license_expression=str(license_expression),
            spdx_license_expression=str(spdx_license_expression),
            combination_reasons=reasons,
        )

    def __eq__(self, other):
        return (
            isinstance(other, LicenseDetection)
            and self.matches == other.matches
        )

    @property
    def query(self):
        # A LicenseDetection will always be created with matches
        if self.matches:
            # All the matches in a file or in a LicenseDetection point to the
            # same query
            return self.matches[0].query
    
    @property
    def qspans(self):
        return [match.qspan for match in self.matches]

    @property
    def identifier(self):
        """
        This is an identifier for a license detection, based on it's underlying
        license matches.
        """
        data = []
        for license_match in self.original_licenses:
            identifier = (license_match.rule_identifier, license_match.coverage(),)
            data.append(identifier)

        return tuple(data)
    
    @property
    def identifier_with_text(self):
        """
        This is an identifier for a issue, which is an unknown license intro,
        based on it's underlying license matches.
        """
        data = []
        for license_match in self.original_licenses:
            tokenized_matched_text = tuple(query_tokenizer(license_match.matched_text))
            identifier = (
                license_match.rule_identifier,
                license_match.coverage(),
                tokenized_matched_text,
            )
            data.append(identifier)

        return tuple(data)

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
        return compute_relevance(self.rules_length)

    def score(self):
        """
        Return the score for this detection as a rounded float between 0 and 100.

        The score is an indication of the confidence of the detection.

        This is computed as the sum of the underlying matches score weighted
        by the length of a match to the overall detection length.
        """
        length = self.length
        weighted_scores = (m.score() * (m.len() / length) for m in self.matches)
        return min([round(sum(weighted_scores), 2), 100])

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

            self.license_expression = str(license_expression)

        elif override_license:
            # Use the match expression
            license_expression = licensing.parse(match.license_expression)

            self.spdx_license_expression = build_spdx_license_expression(
                license_expression,
                licensing=licensing,
            )

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

    def percentage_license_text_of_file(self, qspans):
        from licensedcode.spans import Span

        matched_tokens_length = len(Span().union(*qspans))
        query_tokens_length = self.query.tokens_length(with_unknown=True)
        return round((matched_tokens_length / query_tokens_length) * 100, 2)
    
    def to_dict(
        self, 
        include_text=False,
        license_text_diagnostics=False,
        license_url_template=SCANCODE_LICENSEDB_URL,
    ):
        matches = self.matches
        data_matches = []

        for match in matches:
            data_matches.extend(
                _licenses_data_from_match(
                    match=match,
                    include_text=include_text,
                    license_text_diagnostics=license_text_diagnostics,
                    license_url_template=license_url_template,
                )
            )

        detection = attr.asdict(self)
        detection["matches"] = data_matches

        return detection


def _licenses_data_from_match(
    match,
    include_text=False,
    license_text_diagnostics=False,
    license_url_template=SCANCODE_LICENSEDB_URL,
):
    """
    Return a list of "licenses" scan data built from a license match.
    Used directly only internally for testing.
    """
    from licensedcode import cache
    licenses = cache.get_licenses_db()

    matched_text = None
    if include_text:
        if license_text_diagnostics:
            matched_text = match.matched_text(whole_lines=False, highlight=True)
        else:
            matched_text = match.matched_text(whole_lines=True, highlight=False)

    SCANCODE_BASE_URL = 'https://github.com/nexB/scancode-toolkit/tree/develop/src/licensedcode/data/licenses'
    SCANCODE_LICENSE_TEXT_URL = SCANCODE_BASE_URL + '/{}.LICENSE'
    SCANCODE_LICENSE_DATA_URL = SCANCODE_BASE_URL + '/{}.yml'

    detected_licenses = []
    for license_key in match.rule.license_keys():
        lic = licenses.get(license_key)
        result = {}
        detected_licenses.append(result)
        result['key'] = lic.key
        result['score'] = match.score()
        result['name'] = lic.name
        result['short_name'] = lic.short_name
        result['category'] = lic.category
        result['is_exception'] = lic.is_exception
        result['is_unknown'] = lic.is_unknown
        result['owner'] = lic.owner
        result['homepage_url'] = lic.homepage_url
        result['text_url'] = lic.text_urls[0] if lic.text_urls else ''
        result['reference_url'] = license_url_template.format(lic.key)
        result['scancode_text_url'] = SCANCODE_LICENSE_TEXT_URL.format(lic.key)
        result['scancode_data_url'] = SCANCODE_LICENSE_DATA_URL.format(lic.key)

        spdx_key = lic.spdx_license_key
        result['spdx_license_key'] = spdx_key

        if spdx_key:
            is_license_ref = spdx_key.lower().startswith('licenseref-')
            if is_license_ref:
                spdx_url = SCANCODE_LICENSE_TEXT_URL.format(lic.key)
            else:
                spdx_key = lic.spdx_license_key.rstrip('+')
                spdx_url = SPDX_LICENSE_URL.format(spdx_key)
        else:
            spdx_url = ''
        result['spdx_url'] = spdx_url
        result['start_line'] = match.start_line
        result['end_line'] = match.end_line
        matched_rule = result['matched_rule'] = {}
        matched_rule['identifier'] = match.rule.identifier
        matched_rule['license_expression'] = match.rule.license_expression
        matched_rule['licenses'] = match.rule.license_keys()
        matched_rule['referenced_filenames'] = match.rule.referenced_filenames
        matched_rule['is_license_text'] = match.rule.is_license_text
        matched_rule['is_license_notice'] = match.rule.is_license_notice
        matched_rule['is_license_reference'] = match.rule.is_license_reference
        matched_rule['is_license_tag'] = match.rule.is_license_tag
        matched_rule['is_license_intro'] = match.rule.is_license_intro
        matched_rule['has_unknown'] = match.rule.has_unknown
        matched_rule['matcher'] = match.matcher
        matched_rule['rule_length'] = match.rule.length
        matched_rule['matched_length'] = match.len()
        matched_rule['match_coverage'] = match.coverage()
        matched_rule['rule_relevance'] = match.rule.relevance
        # FIXME: for sanity this should always be included?????
        if include_text:
            result['matched_text'] = matched_text
    return detected_licenses


def matches_compact_repr(matches):
    """
    Return a string representing a list of license matches in a compact way.
    """
    return ', '.join(m.rule.identifier for m in matches)


def is_correct_detection(license_matches):
    """
    Return True if all the license matches in a file-region are correct
    license detections, as they are either SPDX license tags, or the file content has
    a exact match with a license hash.

    :param license_matches: list
        List of LicenseMatch.
    """
    matchers = (license_match.matcher for license_match in license_matches)
    return (
        all(matcher in ("1-hash", "1-spdx-id") for matcher in matchers)
        and not has_unknown_matches(license_matches)
    )


def is_match_coverage_less_than_threshold(license_matches, threshold):
    """
    Returns True if any of the license matches in a file-region has a `match_coverage`
    value below the threshold.

    :param license_matches: list
        List of LicenseMatch.
    :param threshold: int
        A `match_coverage` threshold value in between 0-100
    """
    coverage_values = (
        license_match.coverage() for license_match in license_matches
    )
    return any(coverage_value < threshold for coverage_value in coverage_values)


def calculate_query_coverage_coefficient(license_match):
    """
    Calculates a `query_coverage_coefficient` value for that match. For a match:
    1. If this value is 0, i.e. `score`==`match_coverage`*`rule_Relevance`, then
       there are no extra words in that license match.
    2. If this value is a +ve number, i.e. `score`!=`match_coverage`*`rule_Relevance`,
       then there are extra words in that match.

    :param matched_license: LicenseMatch.
    """
    score_coverage_relevance = (
        license_match.coverage() * license_match.rule.relevance
    ) / 100

    return score_coverage_relevance - license_match.score()


def is_extra_words(license_matches):
    """
    Return True if any of the license matches in a file-region has extra words. Having
    extra words means contains a perfect match with a license/rule, but there are some
    extra words in addition to the matched text.

    :param license_matches: list
        List of LicenseMatch.
    """
    match_query_coverage_diff_values = (
        calculate_query_coverage_coefficient(license_match)
        for license_match in license_matches
    )
    return any(
        match_query_coverage_diff_value > 0
        for match_query_coverage_diff_value in match_query_coverage_diff_values
    )


def is_false_positive(license_matches):
    """
    Return True if all of the license matches in a file-region are false positives.
    False Positive occurs when other text/code is falsely matched to a license rule,
    because it matches with a one-word license rule with it's `is_license_tag` value as
    True. Note: Usually if it's a false positive, there's only one match in that region.

    :param license_matches: list
        List of LicenseMatch.
    """
    start_line_region = min(
        license_match.start_line for license_match in license_matches
    )
    match_rule_length_values = [
        license_match.rule.length for license_match in license_matches
    ]

    if start_line_region > FALSE_POSITIVE_START_LINE_THRESHOLD and any(
        match_rule_length_value <= FALSE_POSITIVE_RULE_LENGTH_THRESHOLD
        for match_rule_length_value in match_rule_length_values
    ):
        return True

    match_is_license_tag_flags = (
        license_match.rule.is_license_tag for license_match in license_matches
    )
    return all(
        (is_license_tag_flag and match_rule_length == 1)
        for is_license_tag_flag, match_rule_length in zip(
            match_is_license_tag_flags, match_rule_length_values
        )
    )


def has_unknown_matches(license_matches):
    """
    Return True if any on the license matches has a license match with an
    `unknown` rule identifier.

    :param license_matches: list
        List of LicenseMatch.
    """
    return any(match.rule.has_unknown for match in license_matches)


def is_unknown_intro(license_match):
    """
    Return True if all the license matches is an unknown intro LicenseMatch.

    :param license_matches: list
        List of LicenseMatch.
    """
    return (
        license_match.rule.has_unknown and
        license_match.rule.is_license_intro
    )


def is_license_clues(license_matches):
    """
    """
    return not is_correct_detection(license_matches) and (
        has_unknown_matches(license_matches) or
        is_match_coverage_less_than_threshold(
            license_matches=license_matches,
            threshold=CLUES_MATCH_COVERAGE_THR,
        )
    )


def has_unknown_intro_before_detection(license_matches):

    has_unknown_intro = False
    has_unknown_intro_before_detection = False

    for match in license_matches:
        if is_unknown_intro(match):
            has_unknown_intro = True
            continue

        if has_unknown_intro:
            has_unknown_intro_before_detection = True

    return has_unknown_intro_before_detection


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


def is_license_reference_local_file(license_match):
    """
    Return True if `license_match` LicenseMatch dict has a
    non-empty `referenced_filename`, i.e. contains a license
    reference to a local file.
    """
    if license_match['matched_rule']['referenced_filenames']:
        return True

    return False


def combine_license_references(license_matches):
    """
    Return a filtered ``license_matches`` list of LicenseMatch objects removing
    references to local files with licenses.

    A common source of unknown license detections in license references to
    a local file like "see license in LICENSE.md". In these cases we can
    remove the unknown reference with the license detection in the file.
    """
    return [match for match in license_matches if not is_license_reference_local_file(match)]


def get_detected_license_expression(matches, analysis):
    """
    Get `reasons` and `combined_license_expression` after combining
    `matches` list of LicenseMatch objects.
    """
    matches_for_expression = None
    reasons = []

    if analysis == "unknown-intro-before-detection":
        matches_for_expression = combine_license_intros(matches)
        reasons.append(CombinationReason.UNKNOWN_INTRO_FOLLOWED_BY_MATCH.value)
    elif analysis == "unknown-file-reference-local":
        matches_for_expression = combine_license_references(matches)
        reasons.append(CombinationReason.UNKNOWN_REFERENCE_TO_LOCAL_FILE.value)
    else:
        matches_for_expression = matches

    if isinstance(matches[0], dict):
        combined_expression = combine_expressions(
            expressions=[match['matched_rule']['license_expression'] for match in matches_for_expression]
        )
    else:
        combined_expression = combine_expressions(
            expressions=[match.rule.license_expression for match in matches_for_expression]
        )

    return reasons, combined_expression


def get_matches_from_detections(license_detections):
    """
    Return a `license_matches` list of LicenseMatch dicts from a
    `license_detections` list of LicenseDetection dicts.
    """
    license_matches = []
    for detection in license_detections:
        license_matches.extend(detection["matches"])
    
    return license_matches


def analyze_detection(license_matches):
    """
    Analyse license matches from a file-region, and determine if the license detection
    in that file region is correct or it is wrong/partially-correct/false-positive or
    has extra words.

    :param license_matches: list
        List of LicenseMatch.
    """
    # Case where all matches have `matcher` as `1-hash` or `4-spdx-id`
    if is_correct_detection(license_matches):
        return "correct-license-detection"

    elif has_unknown_intro_before_detection(license_matches):
        return "unknown-intro-before-detection"

    elif is_match_coverage_less_than_threshold(
        license_matches, CLUES_MATCH_COVERAGE_THR
    ):
        return "clues-imperfect-match-coverage"

    # Case where at least one of the matches have `match_coverage`
    # below IMPERFECT_MATCH_COVERAGE_THR
    elif is_match_coverage_less_than_threshold(
        license_matches, IMPERFECT_MATCH_COVERAGE_THR
    ):
        return "imperfect-match-coverage"

    # Case where at least one of the matches have `match_coverage`
    # below NEAR_PERFECT_MATCH_COVERAGE_THR
    elif is_match_coverage_less_than_threshold(
        license_matches, NEAR_PERFECT_MATCH_COVERAGE_THR
    ):
        return "near-perfect-match-coverage"

    # Case where at least one of the match have extra words
    elif is_extra_words(license_matches):
        return "extra-words"

    # Case where even though the matches have perfect coverage, they have
    # matches with `unknown` rule identifiers
    elif has_unknown_matches(license_matches):
        return "unknown-match"

    # Case where the match is a false positive
    elif is_false_positive(license_matches):
        return "false-positive"

    # Cases where Match Coverage is a perfect 100 for all matches
    else:
        return "correct-license-detection"


def group_matches(license_matches, lines_threshold=LINES_THRESHOLD):
    """
    Given a list of `matches` yield lists of grouped matches together where each
    group is less than `lines_threshold` apart.
    Each item in `matches` is a ScanCode matched license using the structure
    that is found in the JSON scan results.

    :param license_matches: list
        List of LicenseMatch.
    :param lines_threshold: int
        The maximum space that can exist between two matches for them to be
        considered in the same file-region.
    :returns: list generator
        A list of groups, where each group is a list of matches in the same file-region.
    """
    group_of_license_matches = []
    for license_match in license_matches:
        if not group_of_license_matches:
            group_of_license_matches.append(license_match)
            continue
        previous_match = group_of_license_matches[-1]
        is_in_group = license_match.start_line <= previous_match.end_line + lines_threshold
        if is_in_group:
            group_of_license_matches.append(license_match)
            continue
        else:
            yield group_of_license_matches
            group_of_license_matches = [license_match]

    yield group_of_license_matches


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
                current_match.rule.has_unknown and (
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


def detect_licenses(location, min_score, deadline, **kwargs):
    """
    Yield LicenseDetection objects for licenses detected in the file at
    `location`.
    """
    from licensedcode import cache
    idx = cache.get_index()

    matches = idx.match(
        location=location,
        min_score=min_score,
        deadline=deadline,
        **kwargs,
    )

    for group_of_matches in group_matches(matches):
        yield LicenseDetection.from_matches(matches=group_of_matches)
