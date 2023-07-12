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
from commoncode.cliutils import POST_SCAN_GROUP, PluggableCommandLineOption
from licensedcode.detection import collect_license_detections
from licensedcode.detection import DetectionCategory as LicenseDetectionCategory
from licensedcode.detection import FileRegion
from licensedcode.detection import get_ambiguous_license_detections_by_type
from licensedcode.detection import get_uuid_on_content
from licensedcode.detection import UniqueDetection
from plugincode.post_scan import PostScanPlugin, post_scan_impl
from packageurl import PackageURL

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

    - detection_identifier:
      review_comments:
      detection_data:
    
    - detection_identifier:
      review_comments:
      detection_data:

detection_identifier: This is PURL + UUID (similar to top-level packages)
    or license_expression + UUID (similar to top-level license detections)

detection_data: This is PackageData objects in case of package detections
    and LicenseDetection objects in case of license detections.

"""

@post_scan_impl
class AmbiguousDetectionsToDoPlugin(PostScanPlugin):
    """
    Summarize a scan by compiling review items of ambiguous detections.
    """
    sort_order = 10

    resource_attributes = dict(for_todo=attr.ib(default=attr.Factory(list)))
    codebase_attributes = dict(todo=attr.ib(default=attr.Factory(list)))

    options = [
        PluggableCommandLineOption(
            ('--todo',),
            is_flag=True,
            default=False,
            help='Summarize scans by providing all ambiguous '
            'detections which are todo items and needs manual review.',
            help_group=POST_SCAN_GROUP,
        )
    ]

    def is_enabled(self, todo, **kwargs):
        return todo

    def process_codebase(self, codebase, **kwargs):

        has_packages = False
        has_licenses = False

        if hasattr(codebase.root, 'package_data'):
            has_packages = True

        if hasattr(codebase.root, 'license_detections'):
            has_licenses = True

        if not has_packages and not has_licenses:
            usage_suggestion_message = (
                "The --review option should be used with atleast one of the license [`--license`], "
                "or package [`--package`] options."
            )
            warnings.simplefilter('always', ToDoPluginUsageWarning)
            warnings.warn(
                usage_suggestion_message,
                ToDoPluginUsageWarning,
                stacklevel=2,
            )
            return

        ambi_license_detections = []
        if has_licenses:
            all_license_detections = collect_license_detections(codebase=codebase, include_license_clues=True)
            unique_license_detections = UniqueDetection.get_unique_detections(all_license_detections)
            ambi_license_detections_by_type = get_ambiguous_license_detections_by_type(unique_license_detections)
            ambi_license_detections = get_ambiguous_license_detections(ambi_license_detections_by_type)

        ambi_package_detections = []
        if has_packages:
            ambi_package_detections = get_ambiguous_package_detections(codebase=codebase)

        ambiguous_detections = ambi_license_detections + ambi_package_detections
        populate_resources_for_reviews(
            codebase=codebase,
            ambiguous_detections=ambiguous_detections,
        )
        todo_items = [
            detection.to_dict()
            for detection in ambiguous_detections
        ]

        codebase.attributes.todo = todo_items


def get_ambiguous_license_detections(ambi_license_detections_by_type):

    ambi_license_detections = []
    for detection_type, detection in ambi_license_detections_by_type.items():
        ambi_license_detections.append(
            AmbiguousDetection.from_license(
                detection=detection,
                detection_log=[detection_type],
                file_regions=detection.file_regions,
            )
        )

    return ambi_license_detections


def get_ambiguous_package_detections(codebase):
    codebase_packages = codebase.attributes.packages
    codebase_dependencies = codebase.attributes.dependencies
    
    codebase_packages_purls = [
        package["purl"]
        for package in codebase_packages
    ]
    deps_datafile_paths = set()
    deps_datafile_paths.update([
        dep["datafile_path"]
        for dep in codebase_dependencies
    ])

    ambi_package_detections = []

    for resource in codebase.walk():
        package_data = getattr(resource, 'package_data', []) or []
        for package in package_data:
            detection_type = None
            if not package["purl"]:
                if resource.path not in deps_datafile_paths and not resource.for_packages:
                    detection_type=PackageDetectionCategory.CANNOT_CREATE_PURL.value
            else:
                if package["purl"] not in codebase_packages_purls:
                    detection_type=PackageDetectionCategory.CANNOT_CREATE_TOP_LEVEL_PACKAGE.value
            
            if detection_type:
                ambi_package_detections.append(
                    AmbiguousDetection.from_package(
                        package_data=package,
                        detection_log=[detection_type],
                        file_path=resource.path,
                    )
                )

    return ambi_package_detections


def populate_resources_for_reviews(codebase, ambiguous_detections):

    for detection in ambiguous_detections:
        for file_region in detection.file_regions:
            resource = codebase.get_resource(path=file_region.path)
            resource.for_todo.append(detection.detection_id)


class ToDoPluginUsageWarning(RuntimeWarning):
    pass


def get_package_identifier(package_data, file_path):

    identifier_elements = (
        package_data["purl"],
        package_data["declared_license_expression"],
        file_path,
    )
    return get_uuid_on_content(content=[identifier_elements])


def get_unknown_purl(package_type):
    purl = PackageURL(type=package_type, name="unknown")
    return purl.to_string()


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

    review_comments = attr.ib(
        default=attr.Factory(list),
        metadata=dict(
            help='List of file regions where this ambiguous detection is present. '
        )
    )


    detection = attr.ib(
        repr=False,
        default=attr.Factory(dict),
        metadata=dict(
            help='The ambiguous detection with all its attributes and data. '
        )
    )

    file_regions = attr.ib(
        default=attr.Factory(dict),
        metadata=dict(
            help='List of file regions where this ambiguous detection is present. '
        )
    )

    @classmethod
    def from_package(cls, package_data, detection_log, file_path):
        purl = package_data["purl"]
        if not purl:
            purl = get_unknown_purl(package_data["type"])
        identifier = get_package_identifier(package_data, file_path)
        detection_id = f"{purl}-{identifier}"
        file_region = FileRegion(
            path=file_path,
            start_line=None,
            end_line=None,
        )
        review_comments = get_review_comments(detection_log)
        return cls(
            detection_id=detection_id,
            detection=package_data,
            review_comments=review_comments,
            file_regions=[file_region],
        )

    @classmethod
    def from_license(cls, detection, detection_log, file_regions):
        review_comments = get_review_comments(detection_log)
        detection_object = detection.get_license_detection_object()
        license_diagnostics = False
        if detection_object.detection_log != None:
            license_diagnostics = True
        detection_mapping = detection_object.to_dict(
            include_text=True,
            license_diagnostics=license_diagnostics,
        )
        return cls(
            detection_id=detection.identifier,
            detection=detection_mapping,
            review_comments=review_comments,
            file_regions=file_regions,
        )


    def to_dict(self):
        def dict_fields(attr, value):
            if attr.name == 'file_regions':
                return False

            return True

        return attr.asdict(self, filter=dict_fields, dict_factory=dict)


class PackageDetectionCategory(Enum):
    """
    These are the primary types of Detections which a ambigously detected
    package data is classified into.

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
    MATCH_FRAGMENTS = (
        "Fragments of license text were detected which are not proper license detections "
        "and likely has misleading license expression, but this has some clues about licenses, "
        "which needs review."
    )
    IMPERFECT_COVERAGE = (
        "The license detection likely is not conclusive as there was "
        "license matches with low score or coverage, and so this needs "
        "review. scancode would likely benifit from a license rule addition "
        "from this case, so please report this to scancode-toolkit github issues."
    )
    LOW_RELEVANCE = (
        "The license detection needs more review as they have low score due to "
        "the relevance of the matched rules as low, even though the match coverage "
        "is perfect, i.e. there is an exact match."
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

    review_comments = {}

    if LicenseDetectionCategory.EXTRA_WORDS.value in detection_log:
        review_comments[LicenseDetectionCategory.EXTRA_WORDS.value] = ReviewComments.EXTRA_WORDS.value

    if LicenseDetectionCategory.UNKNOWN_MATCH.value in detection_log:
        review_comments[LicenseDetectionCategory.UNKNOWN_MATCH.value] = ReviewComments.UNKNOWN_MATCH.value

    if LicenseDetectionCategory.MATCH_FRAGMENTS.value in detection_log:
        review_comments[LicenseDetectionCategory.MATCH_FRAGMENTS.value] = ReviewComments.MATCH_FRAGMENTS.value
    
    if LicenseDetectionCategory.LOW_RELEVANCE.value in detection_log:
        review_comments[LicenseDetectionCategory.LOW_RELEVANCE.value] = ReviewComments.LOW_RELEVANCE.value

    if LicenseDetectionCategory.LICENSE_CLUES.value in detection_log:
        review_comments[LicenseDetectionCategory.LICENSE_CLUES.value] = ReviewComments.LICENSE_CLUES.value

    if LicenseDetectionCategory.IMPERFECT_COVERAGE.value in detection_log:
        review_comments[LicenseDetectionCategory.IMPERFECT_COVERAGE.value] = ReviewComments.IMPERFECT_COVERAGE.value

    if LicenseDetectionCategory.FALSE_POSITVE.value in detection_log:
        review_comments[LicenseDetectionCategory.FALSE_POSITVE.value] = ReviewComments.FALSE_POSITVE.value

    if LicenseDetectionCategory.UNDETECTED_LICENSE.value in detection_log:
        review_comments[LicenseDetectionCategory.UNDETECTED_LICENSE.value] = ReviewComments.UNDETECTED_LICENSE.value

    if PackageDetectionCategory.CANNOT_CREATE_PURL.value in detection_log:
        review_comments[PackageDetectionCategory.CANNOT_CREATE_PURL.value] = ReviewComments.CANNOT_CREATE_PURL.value

    if PackageDetectionCategory.CANNOT_CREATE_TOP_LEVEL_PACKAGE.value in detection_log:
        review_comments[PackageDetectionCategory.CANNOT_CREATE_TOP_LEVEL_PACKAGE.value] = ReviewComments.CANNOT_CREATE_TOP_LEVEL_PACKAGE.value

    return review_comments


AMBIGUOUS_LICENSE_DETECTION_TYPES = [
    LicenseDetectionCategory.EXTRA_WORDS.value,
    LicenseDetectionCategory.FALSE_POSITVE.value,
    LicenseDetectionCategory.IMPERFECT_COVERAGE.value,
    LicenseDetectionCategory.LICENSE_CLUES.value,
    LicenseDetectionCategory.UNDETECTED_LICENSE.value,
    LicenseDetectionCategory.UNKNOWN_MATCH.value,
]
