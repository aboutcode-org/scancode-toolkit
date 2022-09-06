#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import posixpath
import sys
import os
import logging
from enum import Enum

import attr
from license_expression import combine_expressions

from commoncode.resource import clean_path
from licensedcode.cache import get_index
from licensedcode.cache import get_cache
from licensedcode.match import LicenseMatch
from licensedcode.match import set_matched_lines
from licensedcode.models import Rule
from licensedcode.models import compute_relevance
from licensedcode.spans import Span
from licensedcode.tokenize import query_tokenizer
from licensedcode.query import Query
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


MATCHER_UNDETECTED = '5-undetected'
 
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
    PACKAGE_UNKNOWN_FILE_REFERENCE_LOCAL = 'package-unknown-file-reference-local'
    PACKAGE_ADD_FROM_SIBLING_FILE = 'from-package-sibling-file'
    PACKAGE_ADD_FROM_FILE = 'from-package-file'
    EXTRA_WORDS = 'extra-words'
    UNKNOWN_MATCH = 'unknown-match'
    LICENSE_CLUES = 'license-clues'
    IMPERFECT_COVERAGE = 'imperfect-match-coverage'
    FALSE_POSITVE = 'false-positive'
    UNDETECTED_LICENSE = 'undetected-license'


class DetectionRule(Enum):
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
    UNDETECTED_LICENSE = 'undetected-license'
    PACKAGE_UNKNOWN_REFERENCE_TO_LOCAL_FILE = 'package-unknown-reference-to-local-file'
    PACKAGE_ADD_FROM_SIBLING_FILE = 'from-package-sibling-file'
    PACKAGE_ADD_FROM_FILE = 'from-package-file'


@attr.s
class FileRegion:
    """
    A file has one or more file-regions, which are separate regions of the file
    containing some license information (separated by code/text/others in between),
    and identified by a start line and an end line.
    """
    path = attr.ib(type=str)
    start_line = attr.ib(type=int)
    end_line = attr.ib(type=int)


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

    detection_rules = attr.ib(
        repr=False,
        default=attr.Factory(list),
        metadata=dict(
            help='A list of detection DetectionRule explaining how '
            'this detection was created.'
        )
    )

    matches = attr.ib(
        default=attr.Factory(list),
        metadata=dict(
            help='List of license matches combined in this detection.'
        )
    )

    # Only used in unique detection calculation and referencing
    file_region = attr.ib(
        default=attr.Factory(dict),
        metadata=dict(
            help='File path and start end lines to locate the detection.'
        )
    )

    @classmethod
    def from_matches(cls, matches, analysis=None, post_scan=False):
        """
        Return a LicenseDetection created out of `matches` list of LicenseMatch.
        """
        if not matches:
            return
        
        if analysis is None:
            analysis=analyze_detection(matches)

        reasons, license_expression = get_detected_license_expression(
            matches=matches,
            analysis=analysis,
            post_scan=post_scan,
        )

        if license_expression == None:
            return cls(matches=matches)

        return cls(
            matches=matches,
            license_expression=str(license_expression),
            detection_rules=reasons,
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

    def get_file_region(self, path):
        """
        This is an identifier for a license detection, based on it's underlying
        license matches.
        """
        start_line, end_line = self.get_start_end_line()
        return FileRegion(
            path=path,
            start_line=start_line,
            end_line=end_line,
        )

    @property
    def identifier(self):
        """
        This is an identifier for a license detection, based on it's underlying
        license matches.

        This is not guaranteed to be unique for a detection, as certain small and
        unknown matches could have the same value for this identifier, but will
        be unique for most other cases.
        """
        data = []
        for match in self.matches:
            identifier = (match['rule_identifier'], match['match_coverage'],)
            data.append(identifier)

        # Return a positive hash value for the tuple
        return tuple(data).__hash__() % ((sys.maxsize + 1) * 2)
    
    @property
    def identifier_with_text(self):
        """
        This is an identifier for a license detection, based on it's underlying
        license matches with the tokenized matched_text.

        This is guaranteed to be unique for a detection.
        """
        data = []
        for match in self.matches:
            tokenized_matched_text = tuple(query_tokenizer(match['matched_text']))
            identifier = (
                match['rule_identifier'],
                match['match_coverage'],
                tokenized_matched_text,
            )
            data.append(identifier)

        # Return a positive hash value for the tuple
        return tuple(data).__hash__() % ((sys.maxsize + 1) * 2)
    
    def get_start_end_line(self):
        """
        Returns start and end line for a license detection issue, from the
        license match(es).
        """
        start_line = min([match['start_line'] for match in self.matches])
        end_line = max([match['end_line'] for match in self.matches])
        return start_line, end_line

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
        Append the ``reason`` to the detection_rules.

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
            self.detection_rules.append(reason)

        licensing = get_cache().licensing
        if combine_license:
            license_expression = combine_expressions(
                [self.license_expression, match.license_expression],
                unique=True,
                licensing=licensing,
            )
            self.license_expression = str(license_expression)

        elif override_license:
            # Use the match expression
            license_expression = licensing.parse(match.license_expression)
            self.license_expression = str(license_expression)

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
        spdx_license_url=SPDX_LICENSE_URL,
    ):
        def dict_fields(attr, value):
            if attr.name == 'file_region':
                return False

            return True

        data_matches = []

        for match in self.matches:
            data_matches.append(
                match.get_mapping(
                    include_text=include_text,
                    license_text_diagnostics=license_text_diagnostics,
                    license_url_template=license_url_template,
                    spdx_license_url=spdx_license_url,
                )
            )

        detection = attr.asdict(self, filter=dict_fields, dict_factory=dict)
        detection["matches"] = data_matches

        return detection


def get_detections_from_mappings(detection_mappings):

    license_detections = []

    for mapping in detection_mappings:
        license_detections.append(LicenseDetection(**mapping))

    return license_detections


def is_undetected_license_matches(license_matches):
    
    if len(license_matches) != 1:
        return False
    
    if license_matches[0].matcher == MATCHER_UNDETECTED:
        return True


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

    if analysis == DetectionCategory.UNDETECTED_LICENSE.value:
        matches_for_expression = matches
        reasons.append(DetectionRule.UNDETECTED_LICENSE.value)

    elif analysis == DetectionCategory.UNKNOWN_INTRO_BEFORE_DETECTION.value:
        matches_for_expression = filter_license_intros(matches)
        reasons.append(DetectionRule.UNKNOWN_INTRO_FOLLOWED_BY_MATCH.value)

    elif analysis == DetectionCategory.UNKNOWN_FILE_REFERENCE_LOCAL.value and post_scan:
        matches_for_expression = filter_license_references(matches)
        reasons.append(DetectionRule.UNKNOWN_REFERENCE_TO_LOCAL_FILE.value)

    elif analysis == DetectionCategory.PACKAGE_UNKNOWN_FILE_REFERENCE_LOCAL.value and post_scan:
        matches_for_expression = filter_license_references(matches)
        reasons.append(DetectionRule.PACKAGE_UNKNOWN_REFERENCE_TO_LOCAL_FILE.value)

    elif analysis == DetectionCategory.PACKAGE_ADD_FROM_SIBLING_FILE and post_scan:
        matches_for_expression = filter_license_references(matches)
        reasons.append(DetectionRule.PACKAGE_ADD_FROM_SIBLING_FILE.value)

    elif analysis == DetectionCategory.PACKAGE_ADD_FROM_FILE.value and post_scan:
        matches_for_expression = filter_license_references(matches)
        reasons.append(DetectionRule.PACKAGE_ADD_FROM_FILE.value)

    elif (
        analysis == DetectionCategory.UNKNOWN_MATCH.value or
        analysis == DetectionCategory.LICENSE_CLUES.value
    ):
        return reasons, combined_expression

    else:
        matches_for_expression = matches
        reasons.append(DetectionRule.NOT_COMBINED.value)

    if isinstance(matches[0], dict):
        combined_expression = combine_expressions(
            expressions=[match['license_expression'] for match in matches_for_expression]
        )
    else:
        combined_expression = combine_expressions(
            expressions=[match.rule.license_expression for match in matches_for_expression]
        )

    return reasons, combined_expression


def get_unknown_license_detection(query_string):

    undetected_matches = get_undetected_matches(query_string)
    return LicenseDetection.from_matches(undetected_matches)


def get_undetected_matches(query_string):
    """
    Return a list of LicenseMatch (with a single match) created for an unknown
    license match with the ``query_string``.

    Return an empty list if both name and text are empty.
    """
    if not query_string:
        return []

    query_string = f'license {query_string}'
    # FIXME: track lines
    expression_str = 'unknown'

    idx = get_index()
    query = Query(query_string=query_string, idx=idx)

    query_run = query.whole_query_run()

    match_len = len(query_run)
    match_start = query_run.start
    matched_tokens = query_run.tokens

    qspan = Span(range(match_start, query_run.end + 1))
    ispan = Span(range(0, match_len))
    len_legalese = idx.len_legalese
    hispan = Span(p for p, t in enumerate(matched_tokens) if t < len_legalese)

    undetected_rule = UnDetectedRule(
        license_expression=expression_str,
        text=query_string,
        length=match_len,
    )

    match = LicenseMatch(
        rule=undetected_rule,
        qspan=qspan,
        ispan=ispan,
        hispan=hispan,
        query_run_start=match_start,
        matcher=MATCHER_UNDETECTED,
        query=query_run.query,
    )

    matches = [match]
    set_matched_lines(matches, query.line_by_pos)
    return matches


@attr.s(slots=True, repr=False)
class UnDetectedRule(Rule):
    """
    A specialized rule object that is used for the special case of extracted
    license statements without any valid license detection.

    Since there is a license where there is a non empty extracted license
    statement (typically found in a package manifest), if there is no license
    detected by scancode, it would be incorrect to not point out that there
    is a license (though undetected).
    """

    def __attrs_post_init__(self, *args, **kwargs):
        self.identifier = 'package-manifest-' + self.license_expression
        expression = self.licensing.parse(self.license_expression)
        self.license_expression = expression.render()
        self.license_expression_object = expression
        self.is_license_tag = True
        self.is_small = False
        self.relevance = 100
        self.has_stored_relevance = True

    def load(self):
        raise NotImplementedError

    def dump(self):
        raise NotImplementedError


def get_matches_from_detections(license_detections):
    """
    Return a `license_matches` list of LicenseMatch objects from a
    `license_detections` list of LicenseDetection objects.
    """
    license_matches = []
    if not license_detections:
        return license_matches

    for detection in license_detections:
        license_matches.extend(detection.matches)
    
    return license_matches


def get_matches_from_detection_mappings(license_detections):
    """
    Return a `license_matches` list of LicenseMatch dicts from a
    `license_detections` list of LicenseDetection dicts.
    """
    license_matches = []
    if not license_detections:
        return license_matches

    for detection in license_detections:
        license_matches.extend(detection["matches"])
    
    return license_matches


def get_license_keys_from_detections(license_detections):
    """
    Return a list of unique license key strings from a list of LicenseDetections.
    """
    license_keys = set()

    matches = get_matches_from_detection_mappings(license_detections)
    for match in matches:
        licenses = match.get('licenses')
        license_keys.update([entry.get('key') for entry in licenses])
    return list(license_keys)


def analyze_detection(license_matches):
    """
    Analyse a list of LicenseMatch objects, and determine if the license detection
    is correct or it is wrong/partially-correct/false-positive/has extra words or
    some other detection case.
    """
    if is_undetected_license_matches(license_matches):
        return DetectionCategory.UNDETECTED_LICENSE.value

    elif has_unknown_intro_before_detection(license_matches):
        return DetectionCategory.UNKNOWN_INTRO_BEFORE_DETECTION.value

    elif has_unknown_references_to_local_files(license_matches):
        return DetectionCategory.UNKNOWN_FILE_REFERENCE_LOCAL.value

    # Case where all matches have `matcher` as `1-hash` or `4-spdx-id`
    elif is_correct_detection(license_matches):
        return DetectionCategory.PERFECT_DETECTION.value

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
    This creates a new group if there is a license intro, and doesn't create a new
    group if the last match was a license intro.
    """
    group_of_license_matches = []

    for license_match in license_matches:
        # If this is the first match or the start of another group after yielding
        # the contents of the previous group
        if not group_of_license_matches:
            group_of_license_matches.append(license_match)
            continue

        previous_match = group_of_license_matches[-1]
        is_in_group_by_threshold = license_match.start_line <= previous_match.end_line + lines_threshold

        # If the previous match is an intro, we should keep this match in the group
        # This is regardless of line number difference being more than threshold
        if previous_match.rule.is_license_intro:
            group_of_license_matches.append(license_match)
            continue

        # If the current match is an intro, we should create a new group
        # This is regardless of line number difference being less than threshold
        elif license_match.rule.is_license_intro:
            yield group_of_license_matches
            group_of_license_matches = [license_match]

        # If none of previous or current match has license intro then we look at line numbers
        # If line number difference is within threshold, we keep the current match in the group
        elif is_in_group_by_threshold:
            group_of_license_matches.append(license_match)
            continue

        # If line number difference is outside threshold, we make a new group
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
        ld.append(matches[0], DetectionRule.NOT_COMBINED)
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
                    reason=DetectionRule.UNKNOWN_INTRO_FOLLOWED_BY_MATCH,
                    override_license=True,
                )

            # CONTAINED_SAME_LICENSE: combine current and next
            elif (
                current_match.same_licensing(next_match) and
                current_match.qcontains(next_match)
            ):
                current_detection.append(
                    match=next_match,
                    reason=DetectionRule.CONTAINED_SAME_LICENSE,
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


def get_referenced_filenames(license_matches):
    """
    Return a list of unique referenced filenames found in the rules of a list of
    ``license_matches``
    """
    unique_filenames = []
    for license_match in license_matches:
        for filename in license_match['referenced_filenames']:
            if filename not in unique_filenames:
                unique_filenames.append(filename)

    return unique_filenames


def find_referenced_resource(referenced_filename, resource, codebase, **kwargs):
    """
    Return a Resource matching the ``referenced_filename`` path or filename
    given a ``resource`` in ``codebase``.
    
    Return None if the ``referenced_filename`` cannot be found in the same
    directory as the base ``resource``, or at the codebase ``root``.
    
    ``referenced_filename`` is the path or filename referenced in a
    LicenseMatch detected at ``resource``,
    """
    if not resource:
        return

    parent_path = resource.parent_path()
    if not parent_path:
        return

    # this can be a path or a plain name
    referenced_filename = clean_path(referenced_filename)
    path = posixpath.join(parent_path, referenced_filename)
    resource = codebase.get_resource(path=path)
    if resource:
        return resource

    # Also look at codebase root for referenced file
    # TODO: look at project root identified by key-files
    # instead of codebase scan root
    root_path = codebase.root.path
    path = posixpath.join(root_path, referenced_filename)
    resource = codebase.get_resource(path=path)
    if resource:
        return resource


def detect_licenses(
    index=None,
    location=None,
    query_string=None,
    analysis=None,
    post_scan=False,
    min_score=0,
    deadline=sys.maxsize,
    as_expression=False,
    **kwargs
):
    """
    Yield LicenseDetection objects for licenses detected in the file at
    `location`.
    """
    if location and query_string:
        raise Exception("Either location or query_string should be provided")

    if not index:
        from licensedcode import cache
        index = cache.get_index()

    if location:
        matches = index.match(
            location=location,
            min_score=min_score,
            deadline=deadline,
            as_expression=as_expression,
            **kwargs,
        )
    elif query_string:
        matches = index.match(
            query_string=query_string,
            min_score=min_score,
            deadline=deadline,
            as_expression=as_expression,
            **kwargs,
        )
    else:
        return

    if not matches:
        return

    if TRACE:
        logger_debug(f"detection: detect_licenses: location: {location}: query_string: {query_string}")

    for group_of_matches in group_matches(matches):
        yield LicenseDetection.from_matches(
            matches=group_of_matches,
            analysis=analysis,
            post_scan=post_scan
        )
