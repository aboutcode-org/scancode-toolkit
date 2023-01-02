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
from license_expression import Licensing

from licensedcode.models import get_rule_object_from_match


TRACE_REFERENCE = os.environ.get('SCANCODE_DEBUG_LICENSE_REFERENCE', False)
TRACE_EXTRACT = os.environ.get('SCANCODE_DEBUG_LICENSE_REFERENCE_EXTRACT', False)

def logger_debug(*args):
    pass


logger = logging.getLogger(__name__)

if TRACE_REFERENCE or TRACE_EXTRACT:
    import sys
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, str) and a or repr(a) for a in args))


def populate_license_references(codebase):
    """
    Get unique License and Rule data from all license detections in a codebase-level
    list and only refer to them in the resource level detections. This does two things:

    1. populates the `license_references` and `license_rule_references` attributes
       for the `codebase`
    2. it also removes the reference data from all the resource and package
       license detections as a side effect.
    """
    licexps = []
    rules_data = []

    if not hasattr(codebase.attributes, 'license_detections'):
        return

    has_packages = False
    if hasattr(codebase.attributes, 'packages'):
        has_packages = True

    if has_packages:
        codebase_packages = codebase.attributes.packages
        for pkg in codebase_packages:
            if TRACE_REFERENCE:
                logger_debug(
                    f'populate_license_references: codebase.packages',
                    f'extract_license_rules_reference_data from: {pkg["purl"]}\n',
                )

            license_rules_reference_data = extract_license_rules_reference_data(
                license_detections=pkg['license_detections']
            )
            if license_rules_reference_data:
                rules_data.extend(license_rules_reference_data)
            licexps.append(pkg['declared_license_expression'])

    # This license rules reference data is duplicate as `licenses` is a
    # top level summary of all unique license detections but this function
    # is called as the side effect is removing the reference attributes
    # from license matches

    if TRACE_REFERENCE:
        identifiers = [
            detection["identifier"]
            for detection in codebase.attributes.license_detections
        ]
        logger_debug(
            f'populate_license_references: codebase.license_detections',
            f'extract_license_rules_reference_data from: {identifiers}\n',
        )
    _discard = extract_license_rules_reference_data(codebase.attributes.license_detections)

    for resource in codebase.walk():

        # Get license_expressions from both package and license detections
        license_licexp = getattr(resource, 'detected_license_expression')
        if license_licexp:
            licexps.append(license_licexp)

        if has_packages:
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

            license_rules_reference_data = extract_license_rules_reference_data(
                license_detections=package_license_detections
            )
            if license_rules_reference_data:
                rules_data.extend(license_rules_reference_data)

        license_detections = getattr(resource, 'license_detections', []) or []
        license_clues = getattr(resource, 'license_clues', []) or []

        license_rules_reference_data = extract_license_rules_reference_data(
            license_detections=license_detections,
            license_matches=license_clues,
        )
        if license_rules_reference_data:
            rules_data.extend(license_rules_reference_data)

        codebase.save_resource(resource)

    license_references = get_license_references(license_expressions=licexps)
    codebase.attributes.license_references.extend(license_references)

    rule_references = get_unique_rule_references(rules_data=rules_data)
    codebase.attributes.license_rule_references.extend(rule_references)

    if TRACE_REFERENCE:
        logger_debug(
            f'populate_license_references: codebase.license_references',
            f'license_expressions: {licexps}\n',
            f'license_references: {license_references}\n',
            f'rules_data: {rules_data}\n',
            f'rule_references: {rule_references}\n',
        )
        raise Exception()


def add_detection_to_license_references(codebase, license_detection_mappings):
    """
    Add references data from `license_detection_mappings` to codebase level
    license refernces attributes.
    """

    license_expressions = [
        detection["license_expression"]
        for detection in license_detection_mappings
    ]
    license_references = get_license_references(license_expressions=license_expressions)
    license_rules_reference_data = extract_license_rules_reference_data(
        license_detections=license_detection_mappings,
    )
    rule_references = get_unique_rule_references(rules_data=license_rules_reference_data)
    add_license_references_to_codebase(codebase, license_references, rule_references)


def add_license_references_to_codebase(codebase, license_references, rule_references):
    """
    Given the `license_references` and `rule_references` data, add it to the respective
    `codebase` attributes if they aren't already present.
    """
    license_references_new = []
    rule_references_new = []

    license_keys = set()
    rule_identifiers = set()

    for license_reference in codebase.attributes.license_references:
        license_keys.add(license_reference["key"])

    for rule_reference in codebase.attributes.license_rule_references:
        rule_identifiers.add(rule_reference["rule_identifier"])

    for license_reference in license_references:
        if not license_reference["key"] in license_keys:
            license_references_new.append(license_reference)

    for rule_reference in rule_references:
        if not rule_reference["rule_identifier"] in rule_identifiers:
            rule_references_new.append(rule_reference)

    codebase.attributes.license_references.extend(license_references_new)
    codebase.attributes.license_rule_references.extend(rule_references_new)


def get_license_references(license_expressions, licensing=Licensing()):
    """
    Get a list of unique License data from a list of `license_expression` strings.
    These are added to the codebase attribute `license_references`.
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
    rules_references_by_identifier = {}

    for rule_data in rules_data:
        rule_identifier = rule_data['rule_identifier']
        rules_references_by_identifier[rule_identifier] = rule_data

    return rules_references_by_identifier.values()


def extract_license_rules_reference_data(license_detections=None, license_matches=None):
    """
    Get Rule data for references from a list of LicenseDetection mappings `license_detections`
    and LicenseMatch mappings `license_matches`.

    Also removes this data from the list of LicenseMatch in detections,
    apart from the `rule_identifier` as this data is referenced at codebase-level
    attribute `license_rule_references`.
    """
    rule_identifiers = set()
    rules_reference_data = []

    if license_detections:

        for detection in license_detections:
            if not detection:
                continue

            for match in detection['matches']:

                rule_identifier = match['rule_identifier']
                if 'referenced_filenames' in match:
                    ref_data = get_reference_data(match)

                    if rule_identifier not in rule_identifiers:
                        rule_identifiers.update(rule_identifier)
                        rules_reference_data.append(ref_data)

                    if TRACE_EXTRACT:
                        logger_debug(
                            f'extract_license_rules_reference_data:',
                            f'rule_identifier: {rule_identifier}\n',
                            f'ref_data: {ref_data}\n',
                            f'match: {match}\n',
                            f'rules_reference_data: {rules_reference_data}\n',
                        )

    if license_matches:

        for match in license_matches:

            rule_identifier = match['rule_identifier']
            ref_data = get_reference_data(match)

            if rule_identifier not in rule_identifiers:
                rule_identifiers.update(rule_identifier)
                rules_reference_data.append(ref_data)

    return rules_reference_data


def get_reference_data(match):
    """
    Get reference data from a LicenseMatch mapping `match` after rehydrating.
    """

    rule = get_rule_object_from_match(license_match=match)

    ref_data = {}
    ref_data['rule_identifier'] = match['rule_identifier']
    ref_data['license_expression'] = match['license_expression']
    ref_data['rule_url'] = rule.rule_url
    ref_data['rule_relevance'] = match.pop('rule_relevance')
    ref_data['rule_length'] = match.pop('rule_length')
    ref_data['is_license_text'] = match.pop('is_license_text')
    ref_data['is_license_notice'] = match.pop('is_license_notice')
    ref_data['is_license_reference'] = match.pop('is_license_reference')
    ref_data['is_license_tag'] = match.pop('is_license_tag')
    ref_data['is_license_intro'] = match.pop('is_license_intro')
    ref_data['referenced_filenames'] = match.pop('referenced_filenames')
    ref_data['rule_text'] = rule.text

    _ = match.pop('licenses')

    return ref_data
