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
import typing
import uuid
from enum import Enum
from hashlib import sha1

import attr
from collections import defaultdict
from license_expression import combine_expressions
from license_expression import Licensing

from commoncode.resource import clean_path
from commoncode.text import python_safe_name
from licensedcode.cache import get_index
from licensedcode.cache import get_cache
from licensedcode.match import LicenseMatch
from licensedcode.match import set_matched_lines
from licensedcode.models import UnDetectedRule
from licensedcode.models import compute_relevance
from licensedcode.models import Rule
from licensedcode.query import Query
from licensedcode.query import LINES_THRESHOLD
from licensedcode.spans import Span
from licensedcode.tokenize import query_tokenizer

"""
LicenseDetection data structure and processing.

A LicenseDetection combines one or more matches together using various rules and
heuristics.
"""

TRACE = os.environ.get('SCANCODE_DEBUG_LICENSE_DETECTION', False)

TRACE_ANALYSIS = False
TRACE_IS_FUNCTIONS = False


def logger_debug(*args):
    pass


logger = logging.getLogger(__name__)

if TRACE:

    if (
        TRACE
        or TRACE_ANALYSIS
        or TRACE_IS_FUNCTIONS
    ):

        logging.basicConfig(stream=sys.stdout)
        logger.setLevel(logging.DEBUG)

        def logger_debug(*args):
            return logger.debug(' '.join(isinstance(a, str) and a or repr(a) for a in args))

MATCHER_UNDETECTED = '5-undetected'

# All values of match_coverage less than this value then they are not considered
# as perfect detections
IMPERFECT_MATCH_COVERAGE_THR = 100

# Values of match_coverage less than this are reported as `license_clues` matches
CLUES_MATCH_COVERAGE_THR = 60

# Low Relevance threshold
LOW_RELEVANCE_THRESHOLD = 70

# False positives to spurious and gibberish texts are found usually later in the file
# and matched to relatively short rules
# Threshold Value of start line after which a match to likely be a false positive
FALSE_POSITIVE_START_LINE_THRESHOLD = 1000

# Threshold Value of rule length below which a match to likely be a false positive
FALSE_POSITIVE_RULE_LENGTH_THRESHOLD = 3


class DetectionCategory(Enum):
    """
    These are the primary types of Detections which a group of license
    matches are classified into.
    """
    PERFECT_DETECTION = 'perfect-detection'
    UNKNOWN_INTRO_BEFORE_DETECTION = 'unknown-intro-before-detection'
    UNKNOWN_FILE_REFERENCE_LOCAL = 'unknown-file-reference-local'
    UNKNOWN_REFERENCE_IN_FILE_TO_PACKAGE = 'unknown-reference-in-file-to-package'
    UNKNOWN_REFERENCE_IN_FILE_TO_NONEXISTENT_PACKAGE = 'unknown-reference-in-file-to-nonexistent-package'
    PACKAGE_UNKNOWN_FILE_REFERENCE_LOCAL = 'package-unknown-file-reference-local'
    PACKAGE_ADD_FROM_SIBLING_FILE = 'from-package-sibling-file'
    PACKAGE_ADD_FROM_FILE = 'from-package-file'
    EXTRA_WORDS = 'extra-words'
    UNKNOWN_MATCH = 'unknown-match'
    LICENSE_CLUES = 'license-clues'
    IMPERFECT_COVERAGE = 'imperfect-match-coverage'
    FALSE_POSITVE = 'possible-false-positive'
    UNDETECTED_LICENSE = 'undetected-license'
    MATCH_FRAGMENTS = 'match-fragments'
    LOW_RELEVANCE = 'low-relevance'


class DetectionRule(Enum):
    """
    These are secondary types of Detections/Heuristics which are applied to the
    group of LicenseMatch objects to create a LicenseDetection object and it's
    effective `license_expression`.

    These are logged in LicenseDetection.detection_log for verbosity.
    """
    UNKNOWN_MATCH = 'unknown-match'
    LICENSE_CLUES = 'license-clues'
    FALSE_POSITIVE = 'possible-false-positive'
    NOT_LICENSE_CLUES = 'not-license-clues-as-more-detections-present'
    UNKNOWN_REFERENCE_TO_LOCAL_FILE = 'unknown-reference-to-local-file'
    UNKNOWN_INTRO_FOLLOWED_BY_MATCH = 'unknown-intro-followed-by-match'
    UNKNOWN_REFERENCE_IN_FILE_TO_PACKAGE = 'unknown-reference-in-file-to-package'
    UNKNOWN_REFERENCE_IN_FILE_TO_NONEXISTENT_PACKAGE = 'unknown-reference-in-file-to-nonexistent-package'
    CONTAINED_SAME_LICENSE = 'contained-with-same-license'
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

    def to_dict(self):
        return attr.asdict(self, dict_factory=dict)


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

    matches = attr.ib(
        default=attr.Factory(list),
        metadata=dict(
            help='List of license matches combined in this detection.'
        )
    )

    detection_log = attr.ib(
        repr=False,
        default=attr.Factory(list),
        metadata=dict(
            help='A list of detection DetectionRule explaining how '
            'this detection was created.'
        )
    )

    identifier = attr.ib(
        default=None,
        metadata=dict(
            help='An identifier unique for a license detection, containing the license '
            'expression and a UUID crafted from the match contents.')
    )

    # Only used in unique detection calculation and referencing
    file_region = attr.ib(
        default=attr.Factory(dict),
        metadata=dict(
            help='File path and start end lines to locate the detection.'
        )
    )

    @classmethod
    def from_matches(
        cls,
        matches,
        analysis=None,
        post_scan=False,
        package_license=False,
    ):
        """
        Return a LicenseDetection created out of `matches` list of
        LicenseMatch objects.

        If `analysis` is , `matches` are not analyzed again for
        license_expression creation.

        If `post_scan` is True, this function is called outside
        the main license detection step.
        """
        if not matches:
            return

        if analysis is None:
            analysis = analyze_detection(
                license_matches=matches,
                package_license=package_license
            )

        detection_log, license_expression = get_detected_license_expression(
            analysis=analysis,
            license_matches=matches,
            post_scan=post_scan,
        )

        if license_expression == None:
            return cls(
                matches=matches,
                detection_log=detection_log,
            )

        detection = cls(
            matches=matches,
            license_expression=str(license_expression),
            detection_log=detection_log,
        )
        detection.identifier = detection.identifier_with_expression
        return detection

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
    def _identifier(self):
        """
        Return an unique identifier for a license detection, based on it's
        underlying license matches with the tokenized matched_text.
        """
        data = []
        for match in self.matches:

            matched_text = match.matched_text
            if isinstance(matched_text, typing.Callable):
                matched_text = matched_text()
                if matched_text is None:
                    matched_text = ''
            if not isinstance(matched_text, str):
                matched_text = repr(matched_text)

            tokenized_matched_text = tuple(query_tokenizer(matched_text))

            identifier = (
                match.rule.identifier,
                match.score(),
                tokenized_matched_text,
            )
            data.append(identifier)

        # Return a uuid generated from the contents of the matches
        return get_uuid_on_content(content=data)

    @property
    def identifier_with_expression(self):
        """
        Return an identifer for a license detection with the license expression
        and an UUID created from the detection contents.
        """
        id_safe_expression = python_safe_name(s=str(self.license_expression))
        return "{}-{}".format(id_safe_expression, self._identifier)

    def get_start_end_line(self):
        """
        Return start and end line for a license detection issue, from the
        license match(es).
        """
        if isinstance(self.matches[0], dict):
            start_line = min([match['start_line'] for match in self.matches])
            end_line = max([match['end_line'] for match in self.matches])
        else:
            start_line = min([match.start_line for match in self.matches])
            end_line = max([match.end_line for match in self.matches])
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
        accordingly. Append the ``reason`` to the detection_log.

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
            self.detection_log.append(reason)

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
        """
        Return the percentage of license text in the file where the
        license was detected, from a list of `qspans`.

        Here qspans is a list of all individual qspans corresponding
        to the LicenseDetections for the file.
        """

        matched_tokens_length = len(Span().union(*qspans))
        query_tokens_length = self.query.tokens_length(with_unknown=True)
        return round((matched_tokens_length / query_tokens_length) * 100, 2)

    def to_dict(
        self,
        include_text=False,
        license_text_diagnostics=False,
        license_diagnostics=False,
        whole_lines=True,
    ):
        """
        Return a mapping for LicenseDetection objects.
        """

        def dict_fields(attr, value):
            if attr.name == 'file_region':
                return False

            if attr.name == 'detection_log' and not license_diagnostics:
                return False

            return True

        data_matches = []

        for match in self.matches:
            data_matches.append(
                match.to_dict(
                    include_text=include_text,
                    license_text_diagnostics=license_text_diagnostics,
                    whole_lines=whole_lines,
                )
            )

        detection = attr.asdict(self, filter=dict_fields, dict_factory=dict)
        detection["matches"] = data_matches

        return detection


def get_uuid_on_content(content):
    """
    Return an UUID based on the contents of a list, which should be
    a list of hashable elements.
    """
    identifier_string = repr(tuple(content))
    md_hash = sha1(identifier_string.encode('utf-8'))
    return str(uuid.UUID(hex=md_hash.hexdigest()[:32]))


@attr.s
class LicenseDetectionFromResult(LicenseDetection):
    """
    A LicenseDetection object that is created and rehydrated from a
    LicenseDetection mapping. The LicenseMatch objects in the
    `matches` will be LicenseMatchFromResult objects too, as these are
    created from data mappings and don't have the input text/spans
    available.
    """

    @classmethod
    def from_license_detection_mapping(
        cls,
        license_detection_mapping,
        file_path,
    ):
        """
        Return a LicenseDetectionFromResult objects created from a LicenseDetection
        mapping `license_detection_mapping`.
        """
        matches = LicenseMatchFromResult.from_dicts(
            license_match_mappings=license_detection_mapping["matches"]
        )

        detection = cls(
            license_expression=license_detection_mapping["license_expression"],
            detection_log=license_detection_mapping.get("detection_log", []) or None,
            identifier=license_detection_mapping["identifier"],
            matches=matches,
            file_region=None,
        )
        detection.file_region = detection.get_file_region(path=file_path)
        return detection


def detections_from_license_detection_mappings(
    license_detection_mappings,
    file_path,
):
    """
    Return a list of LicenseDetectionFromResult objects created from a
    list of LicenseDetection mappings: `license_detection_mappings`.
    """
    license_detections = []

    for license_detection_mapping in license_detection_mappings:
        license_detections.append(
            LicenseDetectionFromResult.from_license_detection_mapping(
                license_detection_mapping=license_detection_mapping,
                file_path=file_path,
            )
        )

    return license_detections


def get_new_identifier_from_detections(initial_detection, detections_added, license_expression):
    """
    Return a new UUID based on two sets of detections: `initial_detection` is
    the detection being modified with a list of detections (from another file region)
    `detections_added`.
    """
    identifiers = [
        detection_mapping["identifier"]
        for detection_mapping in detections_added
    ]
    identifiers.append(initial_detection["identifier"])
    uuid = get_uuid_on_content(content=sorted(identifiers))
    return f"{license_expression}-{uuid}"


@attr.s
class LicenseMatchFromResult(LicenseMatch):
    """
    A LicenseMatch object recreated from a LicenseMatch data mapping.
    """
    match_score = attr.ib(
        default=None,
        metadata=dict(
            help='License Detection Score')
    )

    matched_length = attr.ib(
        default=None,
        metadata=dict(
            help='License match length')
    )

    match_coverage = attr.ib(
        default=None,
        metadata=dict(
            help='License match coverage')
    )

    text = attr.ib(
        default=None,
        metadata=dict(
            help='Text which was matched')
    )

    def score(self):
        return self.match_score

    def len(self):
        return self.matched_length

    def coverage(self):
        return self.match_coverage

    @property
    def matched_text(self, whole_lines=False, highlight=True):
        return self.text

    @property
    def identifier(self):
        return self.rule.identifier

    @classmethod
    def from_dict(cls, license_match_mapping):
        """
        Return a LicenseMatchFromResult object from a ``license_match_mapping``
        LicenseMatch data mappping.
        """
        rule = Rule.from_match_data(license_match_mapping)
        matched_text = license_match_mapping.get("matched_text") or None

        return cls(
            start_line=license_match_mapping["start_line"],
            end_line=license_match_mapping["end_line"],
            match_score=license_match_mapping["score"],
            matched_length=license_match_mapping["matched_length"],
            match_coverage=license_match_mapping["match_coverage"],
            matcher=license_match_mapping["matcher"],
            text=matched_text,
            rule=rule,
            qspan=None,
            ispan=None,
        )

    @classmethod
    def from_dicts(cls, license_match_mappings):
        """
        Return a LicenseMatchFromResult object from a ``license_match_mapping`s`
        list of LicenseMatch data mapppings.
        """
        return [LicenseMatchFromResult.from_dict(lmm) for lmm in license_match_mappings]

    def to_dict(
        self,
        include_text=False,
        license_text_diagnostics=False,
        whole_lines=True,
    ):
        """
        Return a "result" scan data built from a LicenseMatch object.
        """
        matched_text = None
        if include_text:
            matched_text = self.matched_text

        result = {}

        # Detection Level Information
        result['score'] = self.score()
        result['start_line'] = self.start_line
        result['end_line'] = self.end_line
        result['matched_length'] = self.len()
        result['match_coverage'] = self.coverage()
        result['matcher'] = self.matcher

        # LicenseDB Level Information (Rule that was matched)
        result['license_expression'] = self.rule.license_expression
        result['rule_identifier'] = self.rule.identifier
        result['rule_relevance'] = self.rule.relevance
        result['rule_url'] = self.rule.rule_url

        if include_text:
            result['matched_text'] = matched_text
        return result


def collect_license_detections(codebase, include_license_clues=True):
    """
    Return a list of LicenseDetectionFromResult object rehydrated from
    LicenseDetection mappings, from resources and packages in a ``codebase``.

    As a side effect, this also corrects `declared_license_expression` in packages
    according to their license detections. This is required because package fields
    are populated in package plugin, which runs before the license plugin, and thus
    the license plugin step where unknown references to other files are dereferenced
    does not show up automatically in package attributes. 
    """
    has_packages = hasattr(codebase.root, 'package_data')
    has_licenses = hasattr(codebase.root, 'license_detections')

    all_license_detections = []

    for resource in codebase.walk():

        resource_license_detections = []
        if has_licenses:
            license_detections = getattr(resource, 'license_detections', []) or []
            license_clues = getattr(resource, 'license_clues', []) or []

            if license_detections:
                license_detection_objects = detections_from_license_detection_mappings(
                    license_detection_mappings=license_detections,
                    file_path=resource.path,
                )
                resource_license_detections.extend(license_detection_objects)

            if include_license_clues and license_clues:
                license_matches = LicenseMatchFromResult.from_dicts(
                    license_match_mappings=license_clues,
                )

                for group_of_matches in group_matches(license_matches=license_matches):
                    detection = LicenseDetection.from_matches(matches=group_of_matches)
                    detection.file_region = detection.get_file_region(path=resource.path)
                    resource_license_detections.append(detection)

            all_license_detections.extend(resource_license_detections)

        if TRACE:
            logger_debug(
                f'license detections collected at path {resource.path}:',
                f'resource_license_detections: {resource_license_detections}\n',
                f'all_license_detections: {all_license_detections}',
            )

        if has_packages:
            package_data = getattr(resource, 'package_data', []) or []

            package_license_detection_mappings = []
            modified = False
            for package in package_data:

                package_license_detections = package["license_detections"]
                if package_license_detections:
                    package_license_detection_mappings.extend(package_license_detections)
                    detection_is_same, license_expression = verify_package_license_expression(
                        license_detection_mappings=package_license_detections,
                        license_expression=package["declared_license_expression"]
                    )
                    if not detection_is_same:
                        package["declared_license_expression"] = license_expression
                        modified = True

                other_license_detections = package["other_license_detections"]
                if other_license_detections:
                    package_license_detection_mappings.extend(other_license_detections)
                    detection_is_same, license_expression = verify_package_license_expression(
                        license_detection_mappings=other_license_detections,
                        license_expression=package["other_license_expression"]
                    )
                    if not detection_is_same:
                        package["other_license_expression"] = license_expression
                        modified = True

            if modified:
                codebase.save_resource(resource)

            if package_license_detection_mappings:
                package_license_detection_objects = detections_from_license_detection_mappings(
                    license_detection_mappings=package_license_detection_mappings,
                    file_path=resource.path,
                )
                all_license_detections.extend(package_license_detection_objects)

    return all_license_detections



def verify_package_license_expression(license_detection_mappings, license_expression):
    """
    Returns a tuple of two files: `detection_is_same` and `license_expression` depending
    on whether the `license_expression` is same as the license_expression computed from
    `license_detection_mappings`:
    1. If they are the same, we return True and None for the `license_expression`
    2. If they are not the same, we return False, and the computed `license_expression`
    """
    license_expressions_from_detections = [
            detection["license_expression"]
            for detection in license_detection_mappings
        ]

    license_expression_from_detections = str(combine_expressions(
        expressions=license_expressions_from_detections,
        relation='AND',
        unique=True,
    ))

    if not license_expression_from_detections == license_expression:
        return False, license_expression_from_detections
    else:
        return True, None



@attr.s
class UniqueDetection:
    """
    An unique License Detection.
    """
    identifier = attr.ib(default=None)
    license_expression = attr.ib(default=None)
    detection_count = attr.ib(default=None)
    matches = attr.ib(default=attr.Factory(list))
    detection_log = attr.ib(default=attr.Factory(list))
    file_regions = attr.ib(factory=list)

    @classmethod
    def get_unique_detections(cls, license_detections):
        """
        Return all unique UniqueDetection from a ``license_detections`` list of
        LicenseDetection.
        """
        detections_by_id = get_detections_by_id(license_detections)
        unique_license_detections = []

        for all_detections in detections_by_id.values():
            file_regions = [
                detection.file_region
                for detection in all_detections
            ]
            detection = next(iter(all_detections))
            detection_log = []
            if hasattr(detection, "detection_log"):
                if detection.detection_log:
                    detection_log.extend(detection.detection_log)

            if not detection.license_expression:
                detection.license_expression = str(combine_expressions(
                    expressions=[
                        match.rule.license_expression
                        for match in detection.matches
                    ]
                ))
                detection.identifier = detection.identifier_with_expression

            unique_license_detections.append(
                cls(
                    identifier=detection.identifier,
                    license_expression=detection.license_expression,
                    detection_log=detection_log or [],
                    matches=detection.matches,
                    detection_count=len(file_regions),
                    file_regions=file_regions,
                )
            )

        return unique_license_detections

    def to_dict(self, license_diagnostics):

        def dict_fields(attr, value):

            if attr.name == 'file_regions':
                return False

            if attr.name == 'matches':
                return False

            if attr.name == 'detection_log' and not license_diagnostics:
                return False

            return True

        return attr.asdict(self, filter=dict_fields)

    def get_license_detection_object(self):
        return LicenseDetection(
            license_expression=self.license_expression,
            detection_log=self.detection_log,
            matches=self.matches,
            identifier=self.identifier,
            file_region=None,
        )


def sort_unique_detections(license_detections):
    """
    Return a sorted list of UniqueDetection mappings from a unsorted list of the same.
    These are sorted in alphabetical order of the license_expression (and same license
    expressions are sorted by their detection_count in descending order, and then by their
    UUID).
    """

    def by_expression_count(detection):
        return detection["license_expression"], -detection["detection_count"], detection["identifier"]

    return sorted(license_detections, key=by_expression_count)


def get_detections_by_id(license_detections):
    """
    Get a dict(hashmap) where each item is: {detection.identifier: all_detections} where
    `all_detections` is all detections in `license_detections` whose detection.identifier
    is the same.
    """
    detections_by_id = defaultdict(list)
    for detection in license_detections:
        detections_by_id[detection.identifier].append(detection)

    return detections_by_id


def get_identifiers(license_detections):
    """
    Return identifiers for all ``license detections``.
    """
    identifiers = (
        detection.identifier
        for detection in license_detections
    )
    return identifiers


def get_detections_from_mappings(detection_mappings):
    """
    Return a list of LicenseDetection objects from a list of
    ``detection_mappings``.
    """
    license_detections = []

    for mapping in detection_mappings:
        license_detections.append(LicenseDetection(**mapping))

    return license_detections


def is_undetected_license_matches(license_matches):
    """
    Return True if there is only one LicenseMatch in ``license_matches``
    and it is of the `undetected` type.
    """
    if len(license_matches) != 1:
        return False

    if license_matches[0].matcher == MATCHER_UNDETECTED:
        return True


def is_correct_detection(license_matches):
    """
    Return True if all the matches in ``license_matches`` List of LicenseMatch
    are correct license detections.
    """
    matchers = (license_match.matcher for license_match in license_matches)
    is_match_coverage_perfect = [
        license_match.coverage() == 100
        for license_match in license_matches
    ]

    return (
        all(matcher in ("1-hash", "1-spdx-id", "2-aho") for matcher in matchers)
        and all(is_match_coverage_perfect) and not has_unknown_matches(license_matches)
    )


def is_match_coverage_less_than_threshold(license_matches, threshold, any_matches=True):
    """
    Return True if any of the matches in ``license_matches`` List of LicenseMatch
    has a `match_coverage` value below the threshold (a value between 0-100).

    If `any_matches` is False, return True if none of the matches in `license_matches`

    """
    if not any_matches:
        return not any(
            license_match.coverage() > threshold
            for license_match in license_matches
        )

    return any(
        license_match.coverage() < threshold
        for license_match in license_matches
    )


def calculate_query_coverage_coefficient(license_match):
    """
    Calculates and returns an integer `query_coverage_coefficient` value
    for a LicenseMatch, which is an indicator of extra words being present
    as follows:

    1. If this value is 0, i.e. `score`==`match_coverage`*`rule_relevance`, then
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
    Return True if any of the matches in ``license_matches`` List of LicenseMatch
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


def has_low_rule_relevance(license_matches):
    """
    Return True if any on the matches in ``license_matches`` List of LicenseMatch
    objects has a match with low score because of low rule relevance.
    """
    return any(
        license_match.rule.relevance < LOW_RELEVANCE_THRESHOLD
        for license_match in license_matches
    )


def is_false_positive(license_matches, package_license=False):
    """
    Return True if all of the matches in ``license_matches`` List of LicenseMatch
    are false positives.

    False Positive occurs when other text/code is falsely matched to a license rule,
    """
    if package_license:
        return False

    start_line_region = min(
        license_match.start_line for license_match in license_matches
    )
    match_rule_length_values = [
        license_match.rule.length for license_match in license_matches
    ]

    all_match_rule_length_one = all(
        match_rule_length == 1
        for match_rule_length in match_rule_length_values
    )
    bare_rules = ['gpl_bare', 'freeware_bare', 'public-domain_bare']
    is_bare_rule = all(
        any([
            bare_rule in license_match.rule.identifier
            for bare_rule in bare_rules
        ])
        for license_match in license_matches
    )

    is_gpl = all(
        'gpl' in license_match.rule.identifier
        for license_match in license_matches
    )

    matches_is_license_tag_flags = all(
        license_match.rule.is_license_tag for license_match in license_matches
    )

    is_single_match = len(license_matches) == 1

    if is_single_match and is_bare_rule:
        return True

    if is_gpl and all_match_rule_length_one:
        return True

    if start_line_region > FALSE_POSITIVE_START_LINE_THRESHOLD and any(
        match_rule_length_value <= FALSE_POSITIVE_RULE_LENGTH_THRESHOLD
        for match_rule_length_value in match_rule_length_values
    ):
        return True

    if matches_is_license_tag_flags and all_match_rule_length_one:
        return True

    return False


def has_unknown_matches(license_matches):
    """
    Return True if any of the matches in ``license_matches`` List of LicenseMatch
    has an `unknown` rule identifier.
    """
    return any(match.rule.has_unknown for match in license_matches)


def is_unknown_intro(license_match):
    """
    Return True if the LicenseMatch is an unknown license intro.
    """
    return (
        license_match.rule.has_unknown and
        license_match.rule.is_license_intro
    )


def is_license_clues(license_matches):
    """
    Return True if the license_matches are not part of a correct
    license detection and are mere license clues.
    """
    return not is_correct_detection(license_matches) and (
        is_match_coverage_less_than_threshold(
            license_matches=license_matches,
            threshold=CLUES_MATCH_COVERAGE_THR,
            any_matches=False,
        )
    )


def has_unknown_intro_before_detection(license_matches):
    """
    Given a list of LicenseMatch objects, return True if there
    exists a license intro and it is followed by license matches
    which are proper license detections.

    A common source of false positive license detections in unstructured files
    are license introduction statements that are immediately followed by a
    license notice. In these cases, the license introduction can be discarded as
    this is for the license match that follows it.
    """
    if len(license_matches) == 1:
        return False

    if all([
        is_unknown_intro(match) for match in license_matches
    ]):
        return False

    has_unknown_intro = False
    has_unknown_intro_before_detection = False

    for match in license_matches:
        if is_unknown_intro(match):
            has_unknown_intro = True
            continue

        if has_unknown_intro:
            if not is_match_coverage_less_than_threshold(
                [match], IMPERFECT_MATCH_COVERAGE_THR
            ) and not has_unknown_matches([match]):
                has_unknown_intro_before_detection = True
                return has_unknown_intro_before_detection

    if has_unknown_intro:
        filtered_matches = filter_license_intros(license_matches)
        if license_matches != filtered_matches:
            if is_match_coverage_less_than_threshold(
                license_matches=filtered_matches,
                threshold=IMPERFECT_MATCH_COVERAGE_THR,
                any_matches=False,
            ):
                has_unknown_intro_before_detection = True

    return has_unknown_intro_before_detection


def filter_license_intros(license_match_objects):
    """
    Return a filtered ``license_matches`` list of LicenseMatch objects removing
    spurious matches to license introduction statements (e.g.
    `is_license_intro` Rules.)
    """
    filtered_matches = [match for match in license_match_objects if not is_license_intro(match)]
    if not filtered_matches:
        return license_match_objects
    else:
        return filtered_matches


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
    Return True if `license_match` LicenseMatch mapping has a non-empty
    `referenced_filename`, i.e. contains a license reference to a local file,
    otherwise return False.
    """
    return bool(license_match.rule.referenced_filenames)


def filter_license_references(license_match_objects):
    """
    Return a filtered ``license_matches`` list of LicenseMatch objects removing
    matches which had references to local files with licenses.
    """
    filtered_matches = [match for match in license_match_objects if not is_license_reference_local_file(match)]
    if TRACE:
        logger_debug(f"detection: filter_license_references: license_matches: {license_match_objects}: filtered_matches: {filtered_matches}")

    if not filtered_matches:
        return license_match_objects
    else:
        return filtered_matches


def has_references_to_local_files(license_matches):
    """
    Return True if any of the matched Rule for the ``license_matches`` has a
    non empty `referenced_filenames`, otherwise return False.
    """
    return any(
        bool(match.rule.referenced_filenames)
        for match in license_matches
    )


def get_detected_license_expression(
    analysis,
    license_matches=None,
    license_match_mappings=None,
    post_scan=False,
):
    """
    Return a tuple of (detection_log, combined_expression) by combining a `matches` list of
    LicenseMatch objects according to the `analysis` string.

    If `post_scan` is True, this function is being called from outside the main
    license detection.
    """
    if not license_match_mappings and not license_matches:
        raise Exception(f"Either license_match_mappings or license_matches must be provided")

    if license_match_mappings:
        license_matches = LicenseMatchFromResult.from_dicts(license_match_mappings)

    if TRACE or TRACE_ANALYSIS:
        logger_debug(
            f'license_matches {license_matches}',
            f'package_license {analysis}',
            f'post_scan: {post_scan}',
        )

    matches_for_expression = None
    combined_expression = None
    detection_log = []

    if analysis == DetectionCategory.FALSE_POSITVE.value:
        if TRACE_ANALYSIS:
            logger_debug(f'analysis {DetectionRule.FALSE_POSITIVE.value}')
        detection_log.append(DetectionRule.FALSE_POSITIVE.value)
        return detection_log, combined_expression

    elif analysis == DetectionCategory.UNDETECTED_LICENSE.value:
        if TRACE_ANALYSIS:
            logger_debug(f'analysis {DetectionCategory.UNDETECTED_LICENSE.value}')
        matches_for_expression = license_matches
        detection_log.append(DetectionRule.UNDETECTED_LICENSE.value)

    elif analysis == DetectionCategory.UNKNOWN_INTRO_BEFORE_DETECTION.value:
        if TRACE_ANALYSIS:
            logger_debug(f'analysis {DetectionCategory.UNKNOWN_INTRO_BEFORE_DETECTION.value}')
        matches_for_expression = filter_license_intros(license_matches)
        detection_log.append(DetectionRule.UNKNOWN_INTRO_FOLLOWED_BY_MATCH.value)

    elif post_scan:
        if analysis == DetectionCategory.UNKNOWN_REFERENCE_IN_FILE_TO_PACKAGE.value:
            if TRACE_ANALYSIS:
                logger_debug(f'analysis {DetectionCategory.UNKNOWN_REFERENCE_IN_FILE_TO_PACKAGE.value}')
            matches_for_expression = filter_license_references(license_matches)
            detection_log.append(DetectionRule.UNKNOWN_REFERENCE_IN_FILE_TO_PACKAGE.value)

        elif analysis == DetectionCategory.UNKNOWN_REFERENCE_IN_FILE_TO_NONEXISTENT_PACKAGE.value:
            if TRACE_ANALYSIS:
                logger_debug(f'analysis {DetectionCategory.UNKNOWN_REFERENCE_IN_FILE_TO_NONEXISTENT_PACKAGE.value}')
            matches_for_expression = filter_license_references(license_matches)
            detection_log.append(DetectionRule.UNKNOWN_REFERENCE_IN_FILE_TO_NONEXISTENT_PACKAGE.value)

        elif analysis == DetectionCategory.UNKNOWN_FILE_REFERENCE_LOCAL.value:
            if TRACE_ANALYSIS:
                logger_debug(f'analysis {DetectionCategory.UNKNOWN_FILE_REFERENCE_LOCAL.value}')
            matches_for_expression = filter_license_references(license_matches)
            detection_log.append(DetectionRule.UNKNOWN_REFERENCE_TO_LOCAL_FILE.value)

        elif analysis == DetectionCategory.PACKAGE_UNKNOWN_FILE_REFERENCE_LOCAL.value:
            if TRACE_ANALYSIS:
                logger_debug(f'analysis {DetectionCategory.PACKAGE_UNKNOWN_FILE_REFERENCE_LOCAL.value}')
            matches_for_expression = filter_license_references(license_matches)
            detection_log.append(DetectionRule.PACKAGE_UNKNOWN_REFERENCE_TO_LOCAL_FILE.value)

        elif analysis == DetectionCategory.PACKAGE_ADD_FROM_SIBLING_FILE.value:
            if TRACE_ANALYSIS:
                logger_debug(f'analysis {DetectionCategory.PACKAGE_ADD_FROM_SIBLING_FILE.value}')
            matches_for_expression = filter_license_references(license_matches)
            detection_log.append(DetectionRule.PACKAGE_ADD_FROM_SIBLING_FILE.value)

        elif analysis == DetectionCategory.PACKAGE_ADD_FROM_FILE.value:
            if TRACE_ANALYSIS:
                logger_debug(f'analysis {DetectionCategory.PACKAGE_ADD_FROM_FILE.value}')
            matches_for_expression = filter_license_references(license_matches)
            detection_log.append(DetectionRule.PACKAGE_ADD_FROM_FILE.value)

    elif analysis == DetectionCategory.UNKNOWN_MATCH.value:
        if TRACE_ANALYSIS:
            logger_debug(f'analysis {DetectionCategory.UNKNOWN_MATCH.value}')
        matches_for_expression = license_matches
        detection_log.append(DetectionRule.UNKNOWN_MATCH.value)

    elif analysis == DetectionCategory.LICENSE_CLUES.value:
        if TRACE_ANALYSIS:
            logger_debug(f'analysis {DetectionCategory.LICENSE_CLUES.value}')
        detection_log.append(DetectionRule.LICENSE_CLUES.value)
        return detection_log, combined_expression

    else:
        if TRACE_ANALYSIS:
            logger_debug(f'analysis not-combined')
        matches_for_expression = license_matches

    if TRACE:
        logger_debug(f'matches_for_expression: {matches_for_expression}', f'detection_log: {detection_log}')

    combined_expression = combine_expressions(
        expressions=[match.rule.license_expression for match in matches_for_expression]
    )

    if TRACE or TRACE_ANALYSIS:
        logger_debug(f'combined_expression {combined_expression}')

    return detection_log, combined_expression


def get_unknown_license_detection(query_string):
    """
    Given a `query_string`, create a LicenseDetection object with
    undetected matches from it.
    """
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

def get_matches_from_detection_mappings(license_detections):
    """
    Return a ``license_matches`` list of LicenseMatch mappings from a
    `license_detections` list of LicenseDetection mappings.
    """
    license_matches = []
    if not license_detections:
        return license_matches

    for detection in license_detections:
        license_matches.extend(detection["matches"])

    return license_matches


def get_license_keys_from_detections(license_detections, licensing=Licensing()):
    """
    Return a list of unique license key strings from a ``license_detections``
    list of LicenseDetection mappings.
    """
    license_keys = set()

    matches = get_matches_from_detection_mappings(license_detections)
    for match in matches:
        license_keys.update(
            licensing.license_keys(
                expression=match.get('license_expression'),
                unique=True
            )
        )
    return list(license_keys)


def get_ambiguous_license_detections_by_type(unique_license_detections):
    """
    Return a list of ambiguous unique license detections which needs review
    and would be todo items for the reviewer from a list of
    `unique_license_detections`.
    """

    ambi_license_detections = {}

    for detection in unique_license_detections:
        if not detection.license_expression:
            ambi_license_detections[DetectionCategory.MATCH_FRAGMENTS.value] = detection

        elif is_undetected_license_matches(license_matches=detection.matches):
            ambi_license_detections[DetectionCategory.UNDETECTED_LICENSE.value] = detection

        elif "unknown" in detection.license_expression:
            if has_unknown_matches(license_matches=detection.matches):
                ambi_license_detections[DetectionCategory.UNKNOWN_MATCH.value] = detection

        elif is_match_coverage_less_than_threshold(
            license_matches=detection.matches,
            threshold=IMPERFECT_MATCH_COVERAGE_THR,
        ):
            ambi_license_detections[DetectionCategory.IMPERFECT_COVERAGE.value] = detection

        elif has_extra_words(license_matches=detection.matches):
            ambi_license_detections[DetectionCategory.EXTRA_WORDS.value] = detection

        elif has_low_rule_relevance(license_matches=detection.matches):
            ambi_license_detections[DetectionCategory.LOW_RELEVANCE.value] = detection

    return ambi_license_detections


def analyze_detection(license_matches, package_license=False):
    """
    Analyse a list of LicenseMatch objects, and determine if the license detection
    is correct or it is wrong/partially-correct/false-positive/has extra words or
    some other detection case.
    """
    if TRACE:
        logger_debug(f'license_matches {license_matches}', f'package_license {package_license}')

    if is_undetected_license_matches(license_matches=license_matches):
        return DetectionCategory.UNDETECTED_LICENSE.value

    elif has_unknown_intro_before_detection(license_matches=license_matches):
        return DetectionCategory.UNKNOWN_INTRO_BEFORE_DETECTION.value

    elif has_references_to_local_files(license_matches=license_matches):
        return DetectionCategory.UNKNOWN_FILE_REFERENCE_LOCAL.value

    # Case where the match is a false positive
    # In package license detection this is turned off
    elif not package_license and is_false_positive(
        license_matches=license_matches,
        package_license=package_license,
    ):
        return DetectionCategory.FALSE_POSITVE.value

    # Case where all matches have `matcher` as `1-hash` or `4-spdx-id`
    elif is_correct_detection(license_matches=license_matches):
        return DetectionCategory.PERFECT_DETECTION.value

    # Case where even though the matches have perfect coverage, they have
    # matches with `unknown` rule identifiers
    elif has_unknown_matches(license_matches=license_matches):
        return DetectionCategory.UNKNOWN_MATCH.value

    elif is_license_clues(license_matches=license_matches):
        return DetectionCategory.LICENSE_CLUES.value

    # Case where at least one of the matches have `match_coverage`
    # below IMPERFECT_MATCH_COVERAGE_THR
    elif is_match_coverage_less_than_threshold(
        license_matches=license_matches,
        threshold=IMPERFECT_MATCH_COVERAGE_THR,
    ):
        return DetectionCategory.IMPERFECT_COVERAGE.value

    # Case where at least one of the match have extra words
    elif has_extra_words(license_matches=license_matches):
        return DetectionCategory.EXTRA_WORDS.value

    # Cases where Match Coverage is a perfect 100 for all matches
    else:
        return DetectionCategory.PERFECT_DETECTION.value


def group_matches(license_matches, lines_threshold=LINES_THRESHOLD):
    """
    Given a list of ``license_matches`` LicenseMatch objects, yield lists of
    grouped matches together where each group is less than `lines_threshold`
    apart, while also considering presence of license intros.
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


def get_referenced_filenames(license_matches):
    """
    Return a list of unique referenced filenames found in the rules of a list of
    ``license_matches``
    """
    unique_filenames = []
    for license_match in license_matches:
        for filename in license_match.rule.referenced_filenames:
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


def process_detections(detections, licensing=Licensing()):
    """
    Yield LicenseDetection objects given a list of LicenseDetection objects
    after postprocessing for the following:

    1. Include license clues as detections if there are other proper detections
       with the same license keys.
    """
    if len(detections) == 1:
        yield detections[0]
    else:
        detected_license_keys = set()

        for detection in detections:
            if detection.license_expression != None:
                detected_license_keys.update(
                    licensing.license_keys(expression=detection.license_expression)
                )

        for detection in detections:
            if detection.license_expression == None:
                license_keys = licensing.license_keys(expression=detection.license_expression)
                if all(
                    key in detected_license_keys
                    for key in license_keys
                ):
                    detection.license_expression = str(combine_expressions(
                        expressions=[
                            match.rule.license_expression
                            for match in detection.matches
                        ],
                        unique=True,
                        licensing=licensing,
                    ))
                    detection.detection_log.append(DetectionRule.NOT_LICENSE_CLUES.value)
                    detection.identifier = detection.identifier_with_expression

            yield detection


def detect_licenses(
    index=None,
    location=None,
    query_string=None,
    analysis=None,
    post_scan=False,
    package_license=False,
    unknown_licenses=False,
    min_score=0,
    deadline=sys.maxsize,
    as_expression=False,
    **kwargs
):
    """
    Yield LicenseDetection objects for licenses detected in the file at
    `location` or from the `query_string`.

    The `analysis` string, if not None, is one of the DetectionCategory values,
    which effects how the license matches are merged into a LicenseDetection.

    If this function is called outside the main license detection, `post_scan`
    is `True`, otherwise `False`.

    If this function is called within the package license detection,
    `package_license` is `True`, to enable package license specific heuristics.
    """
    if location and query_string:
        raise Exception("Only one of location or query_string should be provided")

    if not location and not query_string:
        return

    if not index:
        from licensedcode import cache
        index = cache.get_index()

    license_matches = index.match(
        location=location,
        query_string=query_string,
        min_score=min_score,
        deadline=deadline,
        as_expression=as_expression,
        unknown_licenses=unknown_licenses,
        **kwargs,
    )

    if not license_matches:
        return

    if TRACE:
        logger_debug(f"detection: detect_licenses: location: {location}: query_string: {query_string}")

    detections = []
    for group_of_matches in group_matches(license_matches=license_matches):
        detections.append(
            LicenseDetection.from_matches(
                matches=group_of_matches,
                analysis=analysis,
                post_scan=post_scan,
                package_license=package_license,
            )
        )

    yield from process_detections(detections=detections)
