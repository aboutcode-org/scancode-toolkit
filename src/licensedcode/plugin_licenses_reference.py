#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import attr
from collections import Counter

from commoncode.cliutils import PluggableCommandLineOption
from commoncode.cliutils import POST_SCAN_GROUP
from license_expression import Licensing
from plugincode.post_scan import PostScanPlugin
from plugincode.post_scan import post_scan_impl

from licensedcode.detection import LicenseDetection

# Set to True to enable debug tracing
TRACE = False

if TRACE:
    import logging
    import sys

    logger = logging.getLogger(__name__)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, str) and a or repr(a) for a in args))

    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)
else:

    def logger_debug(*args):
        pass


@post_scan_impl
class LicensesReference(PostScanPlugin):
    """
    Add a reference list of all licenses data and text.
    """
    codebase_attributes = dict(
        license_references=attr.ib(default=attr.Factory(list)),
        licensedb_references=attr.ib(default=attr.Factory(list))
    )

    sort_order = 500

    options = [
        PluggableCommandLineOption(('--licenses-reference',),
            is_flag=True, default=False,
            help='Include a reference of all the licenses referenced in this '
                 'scan with the data details and full texts.',
            help_group=POST_SCAN_GROUP)
    ]

    def is_enabled(self, licenses_reference, **kwargs):
        return licenses_reference

    def process_codebase(self, codebase, licenses_reference, **kwargs):
        """
        Get Licenses and LicenseDB data from all license detections in a codebase level list
        and only refer to them in the resource level detections. 
        """
        licexps = []
        license_db_data = []

        if hasattr(codebase.attributes, 'packages'):
            codebase_packages = codebase.attributes.packages
            for pkg in codebase_packages:
                license_db_data.extend(
                    get_license_db_reference_data(
                        license_detections=pkg['license_detections']
                    )
                )
                licexps.append(pkg['declared_license_expression'])

        for resource in codebase.walk():

            # Get license_expressions from both package and license detections
            license_licexp = getattr(resource, 'detected_license_expression')
            if license_licexp:
                licexps.append(license_licexp)
            package_data = getattr(resource, 'package_data', []) or []
            # TODO: license_expression attribute name is changing soon
            package_licexps = [pkg['declared_license_expression'] for pkg in package_data]
            licexps.extend(package_licexps)

            # Get license matches from both package and license detections
            license_detections = getattr(resource, 'license_detections', []) or []
            #TODO: report license detections (with license matches) for packages
            license_db_data.extend(
                get_license_db_reference_data(license_detections=license_detections)
            )

            codebase.save_resource(resource)

        license_references = get_license_references(license_expressions=licexps)
        codebase.attributes.license_references.extend(license_references)

        licensedb_references = get_licensedb_references(license_db_data=license_db_data)
        codebase.attributes.licensedb_references.extend(licensedb_references)


def get_license_references(license_expressions, licensing=Licensing()):
    """
    Get a list of License data from a list of `license_expression` strings.
    """
    from licensedcode.cache import get_licenses_db

    license_keys = set()
    license_references = []

    for expression in license_expressions:
        if expression:
            license_keys.update(licensing.license_keys(expression))

    db = get_licenses_db()
    for key in sorted(license_keys):
        license_references.append(
            db[key].to_dict(include_ignorables=False, include_text=True)
        )

    return license_references


def get_licensedb_references(license_db_data):
    """
    """
    license_db_ids = set()
    licensedb_references = []

    for licdb_ref in license_db_data:

        licdb_id = licdb_ref['licensedb_identifier']
        if licdb_id not in license_db_ids:
            license_db_ids.update(licdb_id)
            licensedb_references.append(licdb_ref)

    return licensedb_references


def get_license_db_reference_data(license_detections):
    """
    """
    license_db_ids = set()
    license_db_reference_data = []

    for detection in license_detections:
        matches = detection['matches']

        for match in matches:

            licdb_id = match['licensedb_identifier']

            ref_data = {}
            ref_data['license_expression'] = match['license_expression']
            ref_data['licensedb_identifier'] = licdb_id
            ref_data['referenced_filenames'] = match.pop('referenced_filenames')
            ref_data['is_license_text'] = match.pop('is_license_text')
            ref_data['is_license_notice'] = match.pop('is_license_notice')
            ref_data['is_license_reference'] = match.pop('is_license_reference')
            ref_data['is_license_tag'] = match.pop('is_license_tag')
            ref_data['is_license_intro'] = match.pop('is_license_intro')
            ref_data['rule_length'] = match.pop('rule_length')
            ref_data['rule_relevance'] = match.pop('rule_relevance')

            if 'matched_text' in match:
                ref_data['matched_text'] = match.pop('matched_text')

            _ = match.pop('licenses')

            if licdb_id not in license_db_ids:
                license_db_ids.update(licdb_id)
                license_db_reference_data.append(ref_data)

    return license_db_reference_data


def get_license_detection_references(license_detections_by_path):
    """
    """
    detection_objects = []

    for path, detections in license_detections_by_path.items():

        for detection in detections:
            detection_obj = LicenseDetection.from_mapping(detection=detection)
            _matches = detection.pop('matches')
            _reasons = detection.pop('detection_rules')
            detection_obj.file_region = detection_obj.get_file_region(path=path)
            detection["id"] = detection_obj.identifier

            detection_objects.append(detection_obj)

    detection_references = UniqueDetection.get_unique_detections(detection_objects)
    return detection_references


@attr.s
class UniqueDetection:
    """
    An unique License Detection.
    """
    unique_identifier = attr.ib(type=int)
    license_detection = attr.ib()
    files = attr.ib(factory=list)

    @classmethod
    def get_unique_detections(cls, license_detections):
        """
        Get all unique license detections from a list of
        LicenseDetections.
        """
        identifiers = get_identifiers(license_detections)
        unique_detection_counts = dict(Counter(identifiers))

        unique_license_detections = []
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
            unique_license_detections.append(
                cls(
                    files=list(file_regions),
                    license_detection=attr.asdict(detection),
                    unique_identifier=detection.identifier,
                )
            )

        return unique_license_detections


def get_identifiers(license_detections):
    """
    Get identifiers for all license detections.
    """
    identifiers = (
        detection.identifier
        for detection in license_detections
    )
    return identifiers
