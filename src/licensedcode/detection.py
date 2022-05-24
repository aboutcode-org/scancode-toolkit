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
from licensedcode.query import LINES_THRESHOLD

from scancode.api import SPDX_LICENSE_URL
from scancode.api import SCANCODE_LICENSEDB_URL


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


# All values of match_coverage less than this value and more than
# `IMPERFECT_MATCH_COVERAGE_THR` are taken as `near-perfect-match-coverage` cases
IMPERFECT_MATCH_COVERAGE_THR = 100

# Values of match_coverage less than this are reported as `license_clues` matches
CLUES_MATCH_COVERAGE_THR = 60

# False positives to spurious and gibberish texts are found usually later in the file
# and matched to relatively short rules 
# Threshold Value of start line after which a match to likely be a false positive
FALSE_POSITIVE_START_LINE_THRESHOLD = 1000

# Threshold Value of rule length below which a match to likely be a false positive
FALSE_POSITIVE_RULE_LENGTH_THRESHOLD = 3


class DetectionCategory(Enum):
    PERFECT_DETECTION = 'perfect-detection'
    UNKNOWN_INTRO_BEFORE_DETECTION = 'unknown-intro-before-detection'
    UNKNOWN_FILE_REFERENCE_LOCAL = 'unknown-file-reference-local'
    EXTRA_WORDS = 'extra-words'
    UNKNOWN_MATCH = 'unknown-match'
    LICENSE_CLUES = 'license-clues'
    IMPERFECT_COVERAGE = 'imperfect-match-coverage'
    FALSE_POSITVE = 'false-positive'


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
        default=attr.Factory(list),
        metadata=dict(
            help='List of license matches combined in this detection.'
        )
    )

    @classmethod
    def from_matches(cls, matches):
        """
        Return a LicenseDetection created out of `matches` list of LicenseMatch.
        """
        if not matches:
            return

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
        assert self.matches
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
        return compute_relevance(self.rules_length())

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
            data_matches.append(
                licenses_data_from_match(
                    match=match,
                    include_text=include_text,
                    license_text_diagnostics=license_text_diagnostics,
                    license_url_template=license_url_template,
                )
            )

        detection = attr.asdict(self)
        detection["matches"] = data_matches

        return detection


def licenses_data_from_match(
    match,
    include_text=False,
    license_text_diagnostics=False,
    license_url_template=SCANCODE_LICENSEDB_URL,
):
    """
    Return a list of "licenses" scan data built from a license match.
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

    result = {}

    # Detection Level Information
    result['score'] = match.score()
    result['start_line'] = match.start_line
    result['end_line'] = match.end_line
    result['matched_length'] = match.len()
    result['match_coverage'] = match.coverage()
    result['matcher'] = match.matcher

    # LicenseDB Level Information (Rule that was matched)
    result['license_expression'] = match.rule.license_expression
    result['licensedb_identifier'] = match.rule.identifier
    result['referenced_filenames'] = match.rule.referenced_filenames
    result['is_license_text'] = match.rule.is_license_text
    result['is_license_notice'] = match.rule.is_license_notice
    result['is_license_reference'] = match.rule.is_license_reference
    result['is_license_tag'] = match.rule.is_license_tag
    result['is_license_intro'] = match.rule.is_license_intro
    result['rule_length'] = match.rule.length
    result['rule_relevance'] = match.rule.relevance
    if include_text:
        result['matched_text'] = matched_text

    # License Level Information (Individual licenses that this rule refers to)
    result['licenses'] = detected_licenses = []
    for license_key in match.rule.license_keys():
        detected_license = {}
        detected_licenses.append(detected_license)

        lic = licenses.get(license_key)

        detected_license['key'] = lic.key
        detected_license['name'] = lic.name
        detected_license['short_name'] = lic.short_name
        detected_license['category'] = lic.category
        detected_license['is_exception'] = lic.is_exception
        detected_license['is_unknown'] = lic.is_unknown
        detected_license['owner'] = lic.owner
        detected_license['homepage_url'] = lic.homepage_url
        detected_license['text_url'] = lic.text_urls[0] if lic.text_urls else ''
        detected_license['reference_url'] = license_url_template.format(lic.key)
        detected_license['scancode_text_url'] = SCANCODE_LICENSE_TEXT_URL.format(lic.key)
        detected_license['scancode_data_url'] = SCANCODE_LICENSE_DATA_URL.format(lic.key)

        spdx_key = lic.spdx_license_key
        detected_license['spdx_license_key'] = spdx_key

        if spdx_key:
            is_license_ref = spdx_key.lower().startswith('licenseref-')
            if is_license_ref:
                spdx_url = SCANCODE_LICENSE_TEXT_URL.format(lic.key)
            else:
                # TODO: Is this replacing spdx_key???
                spdx_key = lic.spdx_license_key.rstrip('+')
                spdx_url = SPDX_LICENSE_URL.format(spdx_key)
        else:
            spdx_url = ''
        detected_license['spdx_url'] = spdx_url

    return result


def is_correct_detection(license_matches):
    """
    Return True if all the matches in `license_matches` List of LicenseMatch
    are correct license detections.
    """
    matchers = (license_match.matcher for license_match in license_matches)
    return (
        all(matcher in ("1-hash", "1-spdx-id") for matcher in matchers)
        and not has_unknown_matches(license_matches)
    )


def is_match_coverage_less_than_threshold(license_matches, threshold):
    """
    Return True if any of the matches in `license_matches` List of LicenseMatch
    has a `match_coverage` value below the threshold (a value between 0-100).
    """
    return any(
        license_match.coverage() < threshold
        for license_match in license_matches
    )

def calculate_query_coverage_coefficient(license_match):
    """
    Calculates a `query_coverage_coefficient` value for a LicenseMatch:
    1. If this value is 0, i.e. `score`==`match_coverage`*`rule_Relevance`, then
       there are no extra words in that license match.
    2. If this value is a positive number, i.e. `score`!=`match_coverage`*`rule_Relevance`,
       then there are extra words in that match.
    """
    score_coverage_relevance = (
        license_match.coverage() * license_match.rule.relevance
    ) / 100

    return score_coverage_relevance - license_match.score()


def has_extra_words(license_matches):
    """
    Return True if any of the matches in `license_matches` List of LicenseMatch
    has extra words.
    Having extra words means contains a perfect match with a license/rule, but there
    are some extra words in addition to the matched text.
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
    Return True if all of the matches in `license_matches` List of LicenseMatch
    are false positives.
    
    False Positive occurs when other text/code is falsely matched to a license rule,
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
    Return True if any of the matches in `license_matches` List of LicenseMatch
    has an `unknown` rule identifier.
    """
    return any(match.rule.has_unknown for match in license_matches)


def is_unknown_intro(license_match):
    """
    Return True if the LicenseMatch is an unknown intro.
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


def filter_license_intros(license_matches):
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
    Return True if `license_match` LicenseMatch dict has a non-empty `referenced_filename`,
    i.e. contains a license reference to a local file.
    """
    return bool(license_match['referenced_filenames'])


def filter_license_references(license_matches):
    """
    Return a filtered ``license_matches`` list of LicenseMatch objects removing
    references to local files with licenses.
    """
    return [match for match in license_matches if not is_license_reference_local_file(match)]


def has_unknown_references_to_local_files(license_matches):
    return any(
        bool(match.rule.referenced_filenames)
        for match in license_matches
    )


def get_detected_license_expression(matches, analysis, post_scan=False):
    """
    Return a tuple of (reasons, combined_expression) by combining a `matches` list of
    LicenseMatch objects using an `analysis` code string.
    """
    matches_for_expression = None
    combined_expression = None
    reasons = []

    if analysis == DetectionCategory.UNKNOWN_INTRO_BEFORE_DETECTION.value:
        matches_for_expression = filter_license_intros(matches)
        reasons.append(CombinationReason.UNKNOWN_INTRO_FOLLOWED_BY_MATCH.value)
    elif analysis == DetectionCategory.UNKNOWN_FILE_REFERENCE_LOCAL.value and post_scan:
        matches_for_expression = filter_license_references(matches)
        reasons.append(CombinationReason.UNKNOWN_REFERENCE_TO_LOCAL_FILE.value)
    elif (
        analysis == DetectionCategory.UNKNOWN_MATCH.value or
        analysis == DetectionCategory.LICENSE_CLUES.value
    ):
        return reasons, combined_expression
    else:
        matches_for_expression = matches
        reasons.append(CombinationReason.NOT_COMBINED.value)

    if isinstance(matches[0], dict):
        combined_expression = combine_expressions(
            expressions=[match['license_expression'] for match in matches_for_expression]
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
    Analyse a list of LicenseMatch objects, and determine if the license detection
    is correct or it is wrong/partially-correct/false-positive/has extra words or
    some other detection case.
    """
    if has_unknown_references_to_local_files(license_matches):
        return DetectionCategory.UNKNOWN_FILE_REFERENCE_LOCAL.value

    # Case where all matches have `matcher` as `1-hash` or `4-spdx-id`
    elif is_correct_detection(license_matches):
        return DetectionCategory.PERFECT_DETECTION.value

    elif has_unknown_intro_before_detection(license_matches):
        return DetectionCategory.UNKNOWN_INTRO_BEFORE_DETECTION.value

    elif is_match_coverage_less_than_threshold(
        license_matches, CLUES_MATCH_COVERAGE_THR
    ):
        return DetectionCategory.LICENSE_CLUES.value

    # Case where at least one of the matches have `match_coverage`
    # below IMPERFECT_MATCH_COVERAGE_THR
    elif is_match_coverage_less_than_threshold(
        license_matches, IMPERFECT_MATCH_COVERAGE_THR
    ):
        return DetectionCategory.IMPERFECT_COVERAGE.value

    # Case where at least one of the match have extra words
    elif has_extra_words(license_matches):
        return DetectionCategory.EXTRA_WORDS.value

    # Case where even though the matches have perfect coverage, they have
    # matches with `unknown` rule identifiers
    elif has_unknown_matches(license_matches):
        return DetectionCategory.UNKNOWN_MATCH.value

    # Case where the match is a false positive
    elif is_false_positive(license_matches):
        return DetectionCategory.FALSE_POSITVE.value

    # Cases where Match Coverage is a perfect 100 for all matches
    else:
        return DetectionCategory.PERFECT_DETECTION.value


def group_matches(license_matches, lines_threshold=LINES_THRESHOLD):
    """
    Given a list of `matches` LicenseMatch objects, yield lists of grouped matches
    together where each group is less than `lines_threshold` apart.
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
