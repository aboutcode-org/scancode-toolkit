#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import logging
import os
from functools import partial

import attr
import click
from commoncode.cliutils import PluggableCommandLineOption
from commoncode.cliutils import SCAN_GROUP
from commoncode.cliutils import SCAN_OPTIONS_GROUP
from commoncode.cliutils import MISC_GROUP
from plugincode.scan import ScanPlugin
from plugincode.scan import scan_impl
from license_expression import Licensing
from licensedcode.cache import build_spdx_license_expression, get_cache
from licensedcode.detection import DetectionCategory
from licensedcode.detection import find_referenced_resource
from licensedcode.detection import get_detected_license_expression
from licensedcode.detection import get_matches_from_detection_mappings
from licensedcode.detection import get_referenced_filenames
from licensedcode.detection import LicenseDetection
from licensedcode.detection import group_matches
from licensedcode.detection import process_detections
from licensedcode.detection import DetectionCategory
from licensedcode.detection import detections_from_license_detection_mappings
from licensedcode.detection import matches_from_license_match_mappings
from licensedcode.detection import UniqueDetection
from licensedcode.detection import LicenseDetectionFromResult
from licensedcode.licenses_reference import populate_license_references
from licensedcode.license_db import dump_license_data
from packagedcode.utils import combine_expressions
from scancode.api import SCANCODE_LICENSEDB_URL

TRACE = os.environ.get('SCANCODE_DEBUG_PLUGIN_LICENSE', False)


def logger_debug(*args):
    pass


logger = logging.getLogger(__name__)

if TRACE:
    import sys
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, str) and a or repr(a) for a in args))

@scan_impl
class LicenseScanner(ScanPlugin):
    """
    Scan a Resource for licenses.
    """

    resource_attributes = dict([
        ('detected_license_expression', attr.ib(default=None)),
        ('detected_license_expression_spdx', attr.ib(default=None)),
        ('license_detections', attr.ib(default=attr.Factory(list))),
        ('license_clues', attr.ib(default=attr.Factory(list))),
        ('percentage_of_license_text', attr.ib(default=0)),
        ('for_license_detections', attr.ib(default=attr.Factory(list))),
    ])

    codebase_attributes = dict(
        license_detections=attr.ib(default=attr.Factory(list)),
        license_references=attr.ib(default=attr.Factory(list)),
        license_rule_references=attr.ib(default=attr.Factory(list))
    )

    sort_order = 4

    options = [
        PluggableCommandLineOption(('-l', '--license'),
            is_flag=True,
            help='Scan <input> for licenses.',
            help_group=SCAN_GROUP,
            sort_order=10,
        ),

        PluggableCommandLineOption(('--license-score',),
            type=int, default=0, show_default=True,
            required_options=['license'],
            help='Do not return license matches with a score lower than this score. '
                 'A number between 0 and 100.',
            help_group=SCAN_OPTIONS_GROUP,
        ),

        PluggableCommandLineOption(('--license-text',),
            is_flag=True,
            required_options=['license'],
            help='Include the detected licenses matched text.',
            help_group=SCAN_OPTIONS_GROUP,
        ),

        PluggableCommandLineOption(('--license-text-diagnostics',),
            is_flag=True,
            required_options=['license_text'],
            help='In the matched license text, include diagnostic highlights '
                 'surrounding with square brackets [] words that are not matched.',
            help_group=SCAN_OPTIONS_GROUP,
        ),

        PluggableCommandLineOption(('--license-url-template',),
            default=SCANCODE_LICENSEDB_URL, show_default=True,
            required_options=['license'],
            help='Set the template URL used for the license reference URLs. '
                 'Curly braces ({}) are replaced by the license key.',
            help_group=SCAN_OPTIONS_GROUP,
        ),
        PluggableCommandLineOption(
            ('--unknown-licenses',),
            is_flag=True,
            required_options=['license'],
            help='[EXPERIMENTAL] Detect unknown licenses. ',
            help_group=SCAN_OPTIONS_GROUP,
        ),
        PluggableCommandLineOption(
            ('--get-license-data',),
            type=click.Path(exists=False, readable=True, file_okay=False, resolve_path=True, path_type=str),
            metavar='DIR',
            callback=dump_license_data,
            help='Include this directory with additional custom licenses and license rules '
                 'in the license detection index. Creates the directory if it does not exist. ',
            help_group=MISC_GROUP,
            is_eager=True,
        ),
    ]

    def is_enabled(self, license, **kwargs):  # NOQA
        return license

    def setup(self, **kwargs):
        """
        This is a cache warmup such that child process inherit from the
        loaded index.
        """
        from licensedcode.cache import populate_cache
        populate_cache()

    def get_scanner(
        self,
        license_score=0,
        license_text=False,
        license_text_diagnostics=False,
        license_url_template=SCANCODE_LICENSEDB_URL,
        unknown_licenses=False,
        **kwargs
    ):

        from scancode.api import get_licenses
        return partial(get_licenses,
            min_score=license_score,
            include_text=license_text,
            license_text_diagnostics=license_text_diagnostics,
            license_url_template=license_url_template,
            unknown_licenses=unknown_licenses,
        )

    def process_codebase(self, codebase, **kwargs):
        """
        Post-processing to follow license references to other files and add
        `is_builtin` flags to licenses, if applicable.

        Also add codebase level unique `license_detections` and license reference
        attributes.
        """
        from licensedcode import cache
        cche = cache.get_cache()
        cle = codebase.get_or_create_current_header()
        licenses = cache.get_licenses_db()
        has_additional_licenses = False

        if cche.additional_license_directory:
            cle.extra_data['additional_license_directory'] = cche.additional_license_directory
            has_additional_licenses = True
        if cche.additional_license_plugins:
            cle.extra_data['additional_license_plugins'] = cche.additional_license_plugins
            has_additional_licenses = True

        if TRACE and has_additional_licenses:
            logger_debug(
                f'add_referenced_filenames_license_matches: additional_licenses',
                f'has_additional_licenses: {has_additional_licenses}\n',
                f'additional_license_directory: {cche.additional_license_directory}\n',
                f'additional_license_plugins : {cche.additional_license_plugins}'
            )

        if codebase.has_single_resource and not codebase.root.is_file:
            return

        license_detections = collect_license_detections(codebase)
        unique_license_detections = UniqueDetection.get_unique_detections(license_detections)

        if TRACE:
            logger_debug(
                f'process_codebase: codebase license_detections',
                f'license_detections: {license_detections}\n',
                f'unique_license_detections: {unique_license_detections}',
            )

        modified = False
        for resource in codebase.walk(topdown=False):
            # follow license references to other files
            if TRACE:
                license_expressions_before = resource.detected_license_expression

            modified = add_referenced_license_matches_for_detections(resource, codebase)

            if has_additional_licenses and resource.is_file and resource.license_detections:
                add_builtin_license_flag(resource, licenses)

            if TRACE and modified:
                license_expressions_after = resource.detected_license_expression
                logger_debug(
                    f'add_referenced_filenames_license_matches: Modfied:',
                    f'{resource.path} with license_expressions:\n'
                    f'before: {license_expressions_before}\n'
                    f'after : {license_expressions_after}'
                )

        populate_for_license_detections_in_resources(
            codebase=codebase,
            detections=unique_license_detections,
        )
        codebase.attributes.license_detections.extend([
            unique_detection.to_dict()
            for unique_detection in unique_license_detections
        ])

        populate_license_references(codebase)


def populate_for_license_detections_in_resources(codebase, detections):
    """
    Given a `codebase` and a list of `UniqueDetection` objects `detections`,
    populate all the resource level `for_license_detections` attributes for
    these unique detections.
    """
    for detection in detections:
        if TRACE:
            logger_debug(
                f'populate_for_license_detections_in_resources:',
                f'for detection: {detection.license_expression}\n',
                f'file paths: {detection.files}',
            )
        for file_region in detection.files:
            resource = codebase.get_resource(path=file_region.path)
            resource.for_license_detections.append(detection.identifier)


def collect_license_detections(codebase):
    """
    Given a `codebase` collect all LicenseDetection mappings and LicenseMatch mappings
    and then return rehydrated LicenseDetectionFromResult objects created out of them.
    """
    has_packages = False
    has_licenses = False

    if hasattr(codebase.root, 'package_data'):
        has_packages = True

    if hasattr(codebase.root, 'license_detections'):
        has_licenses = True

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

    if TRACE:
        logger_debug(
            f'before process_detections licenses:',
            f'resource_license_detections: {resource_license_detections}\n',
            f'all_license_detections: {all_license_detections}',
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

                all_license_detections.extend(package_license_detection_objects)

    return all_license_detections


def add_builtin_license_flag(resource, licenses):
    """
    Add a `is_builtin` flag to each license rule data mapping if there are
    additional licenses present in the cache, either through an additional
    license directory or additional license plugins.
    """
    for detection in resource.license_detections:
        for match in detection["matches"]:
            add_builtin_value(license_match=match, licenses=licenses)


def add_builtin_value(license_match, licenses):
    """
    Add `is_builtin` flags and the corresponding values for each
    license rule data mapping.
    """
    license_expression = license_match['license_expression']
    license_keys = Licensing().license_keys(
        license_expression,
        unique=True,
        simple=True,
    )

    if all([
        licenses.get(license_key).is_builtin
        for license_key in license_keys
    ]):
        license_match['is_builtin'] = True
    else:
        license_match['is_builtin'] = False


def add_referenced_license_matches_for_detections(resource, codebase):
    """
    Return an updated ``resource`` saving it in place, after adding new license
    matches (licenses and license_expressions) following their Rule
    ``referenced_filenames`` if any. Return None if ``resource`` is not a file
    Resource or was not updated.
    """
    if not resource.is_file:
        return

    license_detection_mappings = resource.license_detections
    if not license_detection_mappings:
        return

    modified = False

    for license_detection_mapping in license_detection_mappings:

        license_detection_object = LicenseDetectionFromResult.from_license_detection_mapping(
            license_detection_mapping=license_detection_mapping,
            file_path=resource.path,
        )
        detection_modified = False
        license_match_mappings = license_detection_mapping["matches"]
        referenced_filenames = get_referenced_filenames(license_detection_object.matches)

        if not referenced_filenames:
            continue 
        
        for referenced_filename in referenced_filenames:
            referenced_resource = find_referenced_resource(
                referenced_filename=referenced_filename,
                resource=resource,
                codebase=codebase,
            )

            if referenced_resource and referenced_resource.license_detections:
                modified = True
                detection_modified = True
                license_match_mappings.extend(
                    get_matches_from_detection_mappings(
                        license_detections=referenced_resource.license_detections
                    )
                )

        if not detection_modified:
            continue

        detection_log, license_expression = get_detected_license_expression(
            license_match_mappings=license_match_mappings,
            analysis=DetectionCategory.UNKNOWN_FILE_REFERENCE_LOCAL.value,
            post_scan=True,
        )
        license_detection_mapping["license_expression"] = str(license_expression)
        license_detection_mapping["detection_log"] = detection_log

    if modified:
        license_expressions = [
            detection["license_expression"]
            for detection in resource.license_detections
        ]
        resource.detected_license_expression = combine_expressions(
            expressions=license_expressions,
            relation='AND',
            unique=True,
        )

        resource.detected_license_expression_spdx = str(build_spdx_license_expression(
            license_expression=resource.detected_license_expression,
            licensing=get_cache().licensing,
        ))

        codebase.save_resource(resource)
        return resource
