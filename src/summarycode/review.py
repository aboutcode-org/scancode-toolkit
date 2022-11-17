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
import warnings
from enum import Enum

import attr
from collections import Counter
from commoncode.cliutils import POST_SCAN_GROUP, PluggableCommandLineOption
from licensedcode.detection import LicenseDetection
from licensedcode.detection import group_matches
from licensedcode.detection import analyze_detection
from licensedcode.detection import process_detections
from licensedcode.detection import DetectionCategory
from licensedcode.detection import DetectionRule
from licensedcode.detection import FileRegion
from licensedcode.detection import detections_from_license_detection_mappings
from licensedcode.detection import matches_from_license_match_mappings
from plugincode.post_scan import PostScanPlugin, post_scan_impl

TRACE = os.environ.get('SCANCODE_DEBUG_REVIEW', False)


def logger_debug(*args):
    pass


logger = logging.getLogger(__name__)


if TRACE:
    import sys

    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, str) and a or repr(a) for a in args))


"""
Create summarized ambiguous detections for review.

review:

    packages:

        - detection_id: package#1
          detection:
            purl:
            detection_log:
            package_data:
        
        - detection_id: package#2
          detection:
            purl:
            detection_log:
            declared_license_expression:
    
    licenses:

        - detection_id: license#1
          detection:
            license_expression:
            detection_log:
            matches:
        
        - detection_id: package#2
          detection:
            license_expression:
            detection_log:
            matches:

"""

@post_scan_impl
class AmbiguousDetectionsReviewPlugin(PostScanPlugin):
    """
    Summarize a scan by compiling review items of ambiguous detections.
    """
    sort_order = 10

    resource_attributes = dict(for_reviews=attr.ib(default=attr.Factory(list)))
    codebase_attributes = dict(review=attr.ib(default=attr.Factory(list)))

    options = [
        PluggableCommandLineOption(
            ('--review',),
            is_flag=True,
            default=False,
            help='Summarize scans by providing all ambiguous '
            'detections which needs manual review.',
            help_group=POST_SCAN_GROUP,
        )
    ]

    def is_enabled(self, review, **kwargs):
        return review

    def process_codebase(self, codebase, **kwargs):

        has_packages = False
        has_licenses = False

        if hasattr(codebase.root, 'package_data'):
            has_packages = True

        if hasattr(codebase.root, 'license_detections'):
            has_licenses = True

        if not has_packages and not has_licenses:
            deprecation_message = (
                "The --review option should be used with atleast one of the license [`-l`], "
                "or package [`-p`] options."
            )
            warnings.simplefilter('always', ReviewPluginUsageWarning)
            warnings.warn(
                deprecation_message,
                ReviewPluginUsageWarning,
                stacklevel=2,
            )
            return

        codebase_packages = None
        codebase_dependencies = None

        deps_datafile_paths = set()
        if has_packages:
            codebase_packages = codebase.attributes.packages
            codebase_dependencies = codebase.attributes.dependencies
            codebase_packages_purls = [
                package["purl"]
                for package in codebase_packages
            ]
            deps_datafile_paths.update([
                dep["datafile_path"]
                for dep in codebase_dependencies
            ])

        all_license_detections = []
        ambi_package_detections = []
        ambi_package_detection_count = 0

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

                if license_clues:
                    license_match_objects = matches_from_license_match_mappings(
                        license_match_mappings=license_clues,
                    )

                    for group_of_matches in group_matches(license_matches=license_match_objects):
                        detection = LicenseDetection.from_matches(matches=group_of_matches)
                        detection.file_region = detection.get_file_region(path=resource.path)
                        resource_license_detections.append(detection)

            all_license_detections.extend(
                list(process_detections(detections=resource_license_detections))
            )

            if has_packages:
                package_data = getattr(resource, 'package_data', []) or []

                package_license_detection_mappings = []
                for package in package_data:

                    if package["license_detections"]:
                        package_license_detection_mappings.extend(package["license_detections"])

                    if package["other_license_detections"]:
                        package_license_detection_mappings.extend(package["other_license_detections"])

                    if package_license_detection_mappings:
                        package_license_detection_objects = detections_from_license_detection_mappings(
                            license_detection_mappings=package_license_detection_mappings,
                            file_path=resource.path,
                        )

                        for package_license_detection_object in package_license_detection_objects:
                            package_license_detection_object.detection_log.append(
                                DetectionRule.PACKAGE_LICENSE.value
                            )

                        all_license_detections.extend(package_license_detection_objects)

                    if not package["purl"]:
                        if resource.path not in deps_datafile_paths:
                            ambi_package_detection_count += 1
                            ambi_package_detections.append(
                                AmbiguousPackageDetection.from_package(
                                    num=ambi_package_detection_count,
                                    package_data=package,
                                    file_path=resource.path,
                                    detection_type=PackageDetectionCategory.CANNOT_CREATE_PURL.value,
                                )
                            )
                    else:
                        if package["purl"] not in codebase_packages_purls:
                            ambi_package_detection_count += 1
                            ambi_package_detections.append(
                                AmbiguousPackageDetection.from_package(
                                    num=ambi_package_detection_count,
                                    package_data=package,
                                    file_path=resource.path,
                                    detection_type=PackageDetectionCategory.CANNOT_CREATE_TOP_LEVEL_PACKAGE.value,
                                )
                            )

        ambi_license_detections = UniqueDetection.get_unique_detections(all_license_detections)

        populate_resources_for_reviews(
            codebase,
            ambi_license_detections + ambi_package_detections,
        )

        codebase.attributes.review.append(
            AmbiguousDetectionsRevieiw.from_detections(
                license_detections=ambi_license_detections,
                package_detections=ambi_package_detections,
            ).to_dict()
        )


def populate_resources_for_reviews(codebase, detections):

    for detection in detections:
        for file_region in detection.files:
            resource = codebase.get_resource(path=file_region.path)
            resource.for_reviews.append(detection.detection_id)


class ReviewPluginUsageWarning(RuntimeWarning):
    pass


@attr.s
class AmbiguousDetectionsRevieiw:
    """
    Detections which needs review.
    """
    licenses = attr.ib(
        repr=False,
        default=attr.Factory(list),
        metadata=dict(
            help='Ambiguous license detections with all its attributes and data, '
            'This is a list of AmbiguousDetections. '
        )
    )

    packages = attr.ib(
        repr=False,
        default=attr.Factory(list),
        metadata=dict(
            help='Ambiguous package detections with all its attributes and data, '
            'This is a list of AmbiguousDetections. '
        )
    )

    @classmethod
    def from_detections(
        cls,
        license_detections,
        package_detections,
    ):
        return cls(
            licenses=get_detection_mappings(license_detections),
            packages=get_detection_mappings(package_detections),
        )

    def to_dict(self):
        return attr.asdict(self)


def get_detection_mappings(review_detections):
            detection_mappings = []
            for review_detection in review_detections:
                review_detection.review_comments = get_review_comments(
                    detection_log=review_detection.detection["detection_log"],
                )
                detection_mappings.append(
                    review_detection.to_dict()
                )

            return detection_mappings


@attr.s
class AmbiguousDetection:
    """
    Detections which needs review.
    """
    detection_id = attr.ib(
        default=None,
        metadata=dict(
            help='A detection ID identifying an unique detection. '
            'This has two parts one with the type of detection in string, '
            'like `package`/`license` and a positive integer '
            'denoting the detection number.'
        )
    )

    detection = attr.ib(
        repr=False,
        default=attr.Factory(dict),
        metadata=dict(
            help='The ambiguous detection with all its attributes and data. '
        )
    )

    review_comments = attr.ib(
        default=attr.Factory(list),
        metadata=dict(
            help='List of file regions where this ambiguous detection is present. '
        )
    )

    files = attr.ib(
        default=attr.Factory(dict),
        metadata=dict(
            help='List of file regions where this ambiguous detection is present. '
        )
    )

    @classmethod
    def from_package(cls, num, package_data, file_path):
        detection_id_template = "package#{}"
        file_region = FileRegion(
            path=file_path,
            start_line=None,
            end_line=None,
        )
        return cls(
            detection_id=detection_id_template.format(num),
            detection=package_data,
            files=[file_region],
        )

    def to_dict(self):
        def dict_fields(attr, value):
            if attr.name == 'files':
                return False

            return True

        return attr.asdict(self, filter=dict_fields, dict_factory=dict)


class PackageDetectionCategory(Enum):
    """
    These are the primary types of Detections which a detected package data
    is classified into.

    These are logged in PackageDetection.detection_log for verbosity.
    """
    CANNOT_CREATE_PURL = 'cannot-create-purl'
    CANNOT_CREATE_TOP_LEVEL_PACKAGE = 'cannot-create-top-level-package'


class ReviewComments(Enum):
    """
    These are explanatory comments for the cases of ambiguous package
    or license detections which are reported to be reviewed.
    """
    EXTRA_WORDS = (
        "The license detection is conclusive with high confidence because all the "
        "rule text is matched, but some unknown extra words have been inserted in "
        "the text, which needs to be reviewed. "
    )
    UNKNOWN_MATCH = (
        "The license detection is inconclusive, as the license matches have "
        "been matched to rules having unknown as their license key, and these "
        "needs to be reviewed."
    )
    LICENSE_CLUES = (
        "License clues were detected which are not proper license detections "
        "but likely has some clues about licenses, which needs review."
    )
    IMPERFECT_COVERAGE = (
        "The license detection likely is not conslusive as there was "
        "license matches with low score or coverage, and so this needs "
        "review. scancode would likely benifit from a license rule addition "
        "from this case, so please report this to scancode-toolkit github issues."
    )
    FALSE_POSITVE = (
        "The license detection is inconclusive, and is unlikely to be about a "
        "license as a piece of code/text is detected, and this needs to be reviewed. ",
    )
    UNDETECTED_LICENSE = (
        "This was a non-empty extracted license statement from a package "
        "data file, and no license could be detected here. So this needs "
        "to be reviewed."
    )
    CANNOT_CREATE_PURL = (
        "The package data detected doesn't have enough fields to create "
        "a packageURL (required fields are type, name and version), and "
        "it is also not a lockfile or similar which has dependencies. "
        "This is likely due to a package manifest with insufficient data, "
        "but a package manifest which has to be reviewed anyway."
    )
    CANNOT_CREATE_TOP_LEVEL_PACKAGE = (
        "The package data detected couldn't be processed/merged into a "
        "scan-level package that is returned, and this is likely because "
        "the package assembly method for this specific type of package "
        "data is not implemented or there is a bug in the same. Please "
        "report this to scancode-toolkit github issues."
    )


def get_review_comments(detection_log):

    review_comments = []

    if DetectionCategory.EXTRA_WORDS.value in detection_log:
        review_comments.append(ReviewComments.EXTRA_WORDS.value)

    if DetectionCategory.UNKNOWN_MATCH.value in detection_log:
        review_comments.append(ReviewComments.UNKNOWN_MATCH.value)

    if DetectionCategory.LICENSE_CLUES.value in detection_log:
        review_comments.append(ReviewComments.LICENSE_CLUES.value)

    if DetectionCategory.IMPERFECT_COVERAGE.value in detection_log:
        review_comments.append(ReviewComments.IMPERFECT_COVERAGE.value)

    if DetectionCategory.FALSE_POSITVE.value in detection_log:
        review_comments.append(ReviewComments.FALSE_POSITVE.value)

    if DetectionCategory.UNDETECTED_LICENSE.value in detection_log:
        review_comments.append(ReviewComments.UNDETECTED_LICENSE.value)

    if PackageDetectionCategory.CANNOT_CREATE_PURL.value in detection_log:
        review_comments.append(ReviewComments.CANNOT_CREATE_PURL.value)

    if PackageDetectionCategory.CANNOT_CREATE_TOP_LEVEL_PACKAGE.value in detection_log:
        review_comments.append(ReviewComments.CANNOT_CREATE_TOP_LEVEL_PACKAGE.value)

    return review_comments

@attr.s
class AmbiguousPackageDetection(AmbiguousDetection):
    """
    License detections which needs review.
    """
    @classmethod
    def from_package(cls, num, package_data, file_path, detection_type):
        detection_id_template = "package#{}"
        detection_log = [detection_type]
        detection = PackageDetection(
            purl=package_data["purl"],
            detection_log=detection_log,
            package_data=package_data,
        )
        file_region = FileRegion(
            path=file_path,
            start_line=None,
            end_line=None,
        )

        return cls(
            detection_id=detection_id_template.format(num),
            detection=detection,
            files=[file_region],
        )


@attr.s
class PackageDetection:

    purl = attr.ib(
        default=None,
        metadata=dict(
            help='The package URL for the ambiguous package detection. '
        )
    )

    detection_log = attr.ib(
        default=None,
        metadata=dict(
            help='The detection log for the ambiguous package detection. '
        )
    )

    package_data = attr.ib(
        repr=False,
        default=attr.Factory(dict),
        metadata=dict(
            help='The ambiguous package detection with all its attributes and data. '
        )
    )


AMBIGUOUS_LICENSE_DETECTION_TYPES = [
    DetectionCategory.EXTRA_WORDS.value,
    DetectionCategory.FALSE_POSITVE.value,
    DetectionCategory.IMPERFECT_COVERAGE.value,
    DetectionCategory.LICENSE_CLUES.value,
    DetectionCategory.UNDETECTED_LICENSE.value,
    DetectionCategory.UNKNOWN_MATCH.value,
]


@attr.s
class UniqueDetection(AmbiguousDetection):
    """
    An unique License Detection.
    """
    detection_id = attr.ib(type=int)
    detection = attr.ib()
    review_comments = attr.ib(factory=list)
    files = attr.ib(factory=list)

    @classmethod
    def get_unique_detections(cls, license_detections):
        """
        Get all unique license detections from a list of
        LicenseDetections.
        """
        unique_ambigious_license_detections = []
        if not license_detections:
            return unique_ambigious_license_detections

        identifiers = get_identifiers(license_detections)
        unique_detection_counts = dict(Counter(identifiers))
        detection_id_template = "license#{}"

        unique_license_count = 0
        for detection_identifier in unique_detection_counts.keys():
            file_regions = (
                detection.file_region
                for detection in license_detections
                if detection_identifier == detection.identifier
            )
            all_detections = (
                detection
                for detection in license_detections
                if detection_identifier == detection.identifier
            )

            detection = next(all_detections)

            if DetectionRule.PACKAGE_LICENSE.value in detection.detection_log:
                package_license = True
            else:
                package_license = False

            analysis = analyze_detection(
                license_matches=detection.matches,
                package_license=package_license,
            )

            if TRACE:
                logger_debug("analysis: {analysis}")
                logger_debug("detection: {detection}")

            if analysis in AMBIGUOUS_LICENSE_DETECTION_TYPES:
                unique_license_count += 1
                unique_ambigious_license_detections.append(
                    cls(
                        files=list(file_regions),
                        detection=detection.to_dict(),
                        detection_id=detection_id_template.format(unique_license_count),
                    )
                )

        return unique_ambigious_license_detections


def get_identifiers(license_detections):
    """
    Get identifiers for all license detections.
    """
    identifiers = (
        detection.identifier
        for detection in license_detections
    )
    return identifiers
