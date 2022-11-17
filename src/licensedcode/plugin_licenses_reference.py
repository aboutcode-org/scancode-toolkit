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
        rule_references=attr.ib(default=attr.Factory(list))
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

    def process_codebase(self, codebase, **kwargs):
        """
        Get unique License and Rule data from all license detections in a codebase-level
        list and only refer to them in the resource level detections. 
        """
        licexps = []
        rules_data = []

        if hasattr(codebase.attributes, 'packages'):
            codebase_packages = codebase.attributes.packages
            for pkg in codebase_packages:
                rules_data.extend(
                    get_license_rules_reference_data(
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
            package_licexps = [
                pkg['declared_license_expression']
                for pkg in package_data
            ]
            licexps.extend(package_licexps)

            # Get license matches from both package and license detections
            package_license_detections = []
            for pkg in package_data:
                if not pkg['license_detections']:
                    continue

                package_license_detections.extend(pkg['license_detections'])

            rules_data.extend(
                get_license_rules_reference_data(license_detections=package_license_detections)
            )

            license_detections = getattr(resource, 'license_detections', []) or []
            license_clues = getattr(resource, 'license_clues', []) or []
            rules_data.extend(
                get_license_rules_reference_data(
                    license_detections=license_detections,
                    license_clues=license_clues,
                )
            )

            codebase.save_resource(resource)

        license_references = get_license_references(license_expressions=licexps)
        codebase.attributes.license_references.extend(license_references)

        rule_references = get_unique_rule_references(rules_data=rules_data)
        codebase.attributes.rule_references.extend(rule_references)


def get_license_references(license_expressions, licensing=Licensing()):
    """
    Get a list of unique License data from a list of `license_expression` strings.
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


def get_unique_rule_references(rules_data):
    """
    Get a list of unique Rule data from a list of Rule data.
    """
    rule_identifiers = set()
    rules_references = []

    for rule_data in rules_data:

        rule_identifier = rule_data['rule_identifier']
        if rule_identifier not in rule_identifiers:
            rule_identifiers.update(rule_identifier)
            rules_references.append(rule_data)

    return rules_references


def get_license_rules_reference_data(license_detections, license_clues=None):
    """
    Get Rule data for references from a list of LicenseDetections.

    Also removes this data from the list of LicenseMatch in detections,
    apart from the `rule_identifier` as this data is referenced at top-level
    by this attribute.
    """
    rule_identifiers = set()
    rules_reference_data = []

    if license_detections:

        for detection in license_detections:
            if not detection:
                continue

            for match in detection['matches']:

                rule_identifier = match['rule_identifier']
                ref_data = get_reference_data(match)

                if rule_identifier not in rule_identifiers:
                    rule_identifiers.update(rule_identifier)
                    rules_reference_data.append(ref_data)
    
    if license_clues:

        for match in license_clues:

            rule_identifier = match['rule_identifier']
            ref_data = get_reference_data(match)

            if rule_identifier not in rule_identifiers:
                rule_identifiers.update(rule_identifier)
                rules_reference_data.append(ref_data)

    return rules_reference_data


def get_reference_data(match):

    ref_data = {}
    ref_data['license_expression'] = match['license_expression']
    ref_data['rule_identifier'] = match['rule_identifier']
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

    return ref_data
