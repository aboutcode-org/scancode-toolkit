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

from licensedcode.models import Rule
from plugincode.post_scan import PostScanPlugin
from plugincode.post_scan import post_scan_impl
from commoncode.cliutils import PluggableCommandLineOption
from commoncode.cliutils import POST_SCAN_GROUP
import attr

TRACE = os.environ.get('SCANCODE_DEBUG_LICENSE_REFERENCE', False)


def logger_debug(*args):
    pass


logger = logging.getLogger(__name__)

if TRACE:
    import sys
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, str) and a or repr(a) for a in args))


@post_scan_impl
class LicenseReference(PostScanPlugin):
    """
    Add license and rule reference data to a scan.
    """

    codebase_attributes = dict(
        license_references=attr.ib(default=attr.Factory(list)),
        license_rule_references=attr.ib(default=attr.Factory(list))
    )

    # TODO: send to the tail of the scan, after files
    run_order = 1000
    sort_order = 1000

    options = [
        PluggableCommandLineOption(('--license-references',),
            is_flag=True,
            help='Return reference data for all licenses and license rules '
                 'present in detections.',
            help_group=POST_SCAN_GROUP,
            sort_order=100,
        )
    ]

    def is_enabled(self, license_references, **kwargs):
        return license_references

    def process_codebase(self, codebase, **kwargs):
        """
        Collect the ``license_references`` and ``rule_references``
        list of data mappings and add to the ``codebase``.
        """
        include_files = 'license' in kwargs
        include_packages = 'package' in kwargs

        license_references, rule_references = collect_license_and_rule_references(
            codebase=codebase,
            include_packages=include_packages,
            include_files=include_files,
        )
        codebase.attributes.license_references = license_references
        codebase.attributes.license_rule_references = rule_references


def collect_license_and_rule_references(codebase, include_packages=True, include_files=True):
    """
    Return a two-tuple of (``license_references``, ``license_rule_references``)
    sorted lists of unique mappings collected from a ``codebase``.
    """

    license_keys = set()
    rules_by_identifier = {}

    if include_packages:
        pks, prules = collect_references_from_packages(codebase)
        license_keys.update(pks)
        rules_by_identifier.update(prules)

    if include_files:
        pks, prules = collect_references_from_files(codebase)
        license_keys.update(pks)
        rules_by_identifier.update(prules)

    from licensedcode.cache import get_licenses_db
    db = get_licenses_db()
    license_keys = sorted(set(license_keys))
    license_references = [db[key].to_reference() for key in license_keys]

    rules = [rule for _id, rule in sorted(rules_by_identifier.items())]
    rule_references = [rule.to_reference() for rule in rules]
    return license_references, rule_references


def collect_references_from_packages(codebase):
    """
    Return a two-tuple of:
        (set of ``license_keys``, mapping of ``rules_by_identifier``)
    collected from the ``codebase`` top-level packages and file-level package_data.
    """
    licensing = Licensing()

    license_keys = set()
    rules_by_identifier = {}

    # top level
    packages = getattr(codebase.attributes, 'packages', []) or []
    for pkg in packages:
        expression = pkg['declared_license_expression']
        if expression:
            license_keys.update(licensing.license_keys(expression))

        detections = pkg['license_detections']
        rules_by_id = build_rules_from_detection_data(detections)
        rules_by_identifier.update(rules_by_id)

    # file level
    for resource in codebase.walk():
        package_datas = getattr(resource, 'package_data', []) or []
        for pkg in package_datas:
            expression = pkg['declared_license_expression']
            if expression:
                license_keys.update(licensing.license_keys(expression))

        detections = getattr(resource, 'license_detections', []) or []
        rules_by_id = build_rules_from_detection_data(detections)
        rules_by_identifier.update(rules_by_id)

    for rule in rules_by_identifier.values():
        # TODO: consider using the expresion object directly instead
        expo = rule.license_expression
        license_keys.update(licensing.license_keys(expo))

    return license_keys, rules_by_identifier


def collect_references_from_files(codebase):
    """
    Return a two-tuple of:
        (set of ``license_keys``, mapping of ``rules_by_identifier``)
    collected from the ``codebase`` files.
    """
    licensing = Licensing()

    license_keys = set()
    rules_by_identifier = {}

    for resource in codebase.walk():
        expression = getattr(resource, 'detected_license_expression', None)
        if expression:
            license_keys.update(licensing.license_keys(expression))

        detections = getattr(resource, 'license_detections', []) or []
        rules_by_id = build_rules_from_detection_data(detections)
        rules_by_identifier.update(rules_by_id)

        clues = getattr(resource, 'license_clues', []) or []
        rules_by_id = build_rules_from_match_data(clues)
        rules_by_identifier.update(rules_by_id)

    for rule in rules_by_identifier.values():
        # TODO: consider using the expresion object directly instead
        expo = rule.license_expression
        license_keys.update(licensing.license_keys(expo))

    return license_keys, rules_by_identifier


def build_rules_from_detection_data(license_detection_mappings):
    """
    Return a mapping of unique Rule as {identifier: Rule} from a
    ``license_detection_mappings`` list of LicenseDetection data mappings.
    """
    rules_by_identifier = {}
    if not license_detection_mappings:
        return rules_by_identifier

    for detection in license_detection_mappings:
        # FIXME: why this?
        if not detection:
            continue
        match_datas = detection['matches']
        match_rules_by_id = build_rules_from_match_data(match_datas)
        rules_by_identifier.update(match_rules_by_id)
    return rules_by_identifier


def build_rules_from_match_data(license_match_mappings):
    """
    Return a mapping of unique Rule as {identifier: Rule} from a
    ``license_match_mappings``  list of LicenseMatch data mappings .
    """
    rules_by_identifier = {}
    if not license_match_mappings:
        return rules_by_identifier

    for license_match_mapping in license_match_mappings:
        if TRACE:
            logger_debug('build_rules_from_match_data: license_match_mapping', license_match_mapping)

        try:
            rule_identifier = license_match_mapping['rule_identifier']
        except TypeError as e:
            raise Exception(license_match_mapping) from e

        if rule_identifier not in rules_by_identifier:
            rule = Rule.from_match_data(license_match_mapping)
            rules_by_identifier[rule_identifier] = rule
    return rules_by_identifier

