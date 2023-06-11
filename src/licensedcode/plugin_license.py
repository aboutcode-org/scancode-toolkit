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
from commoncode.cliutils import PluggableCommandLineOption
from commoncode.cliutils import SCAN_GROUP
from commoncode.cliutils import SCAN_OPTIONS_GROUP
from plugincode.scan import ScanPlugin
from plugincode.scan import scan_impl

from licensedcode.cache import build_spdx_license_expression, get_cache
from licensedcode.detection import collect_license_detections
from licensedcode.detection import find_referenced_resource
from licensedcode.detection import get_detected_license_expression
from licensedcode.detection import get_matches_from_detection_mappings
from licensedcode.detection import get_new_identifier_from_detections
from licensedcode.detection import get_referenced_filenames
from licensedcode.detection import DetectionCategory
from licensedcode.detection import LicenseDetectionFromResult
from licensedcode.detection import UniqueDetection
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
        # The license expression summarizing the license info for this
        # resource, combined from all the license detections
        ('detected_license_expression', attr.ib(default=None)),
        # The detected license expression for this file, with
        # SPDX license keys
        ('detected_license_expression_spdx', attr.ib(default=None)),
        # A list of all proper license detections in the resource
        # with the license expression and license detection details
        ('license_detections', attr.ib(default=attr.Factory(list))),
        # license matches that are not proper detections and potentially
        # just clues to licenses or likely false positives, and are not
        # inlcuded in computing the detected license expression for the resource
        ('license_clues', attr.ib(default=attr.Factory(list))),
        # Percentage of file words detected as license text or notice.
        ('percentage_of_license_text', attr.ib(default=0)),
    ])

    codebase_attributes = dict(
        license_detections=attr.ib(default=attr.Factory(list)),
    )

    run_order = 4
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

        PluggableCommandLineOption(('--license-diagnostics',),
            is_flag=True,
            required_options=['license'],
            help='In license detections, include diagnostic details to figure '
                 'out the license detection post processing steps applied.',
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
        )
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
        license_diagnostics=False,
        license_url_template=SCANCODE_LICENSEDB_URL,
        unknown_licenses=False,
        **kwargs
    ):

        from scancode.api import get_licenses
        return partial(get_licenses,
            min_score=license_score,
            include_text=license_text,
            license_text_diagnostics=license_text_diagnostics,
            license_diagnostics=license_diagnostics,
            license_url_template=license_url_template,
            unknown_licenses=unknown_licenses,
        )

    def process_codebase(self, codebase, license_diagnostics, **kwargs):
        """
        Post-process ``codebase`` to follow referenced filenames to license
        matches in other files.
        Also add top-level unique ``license_detections``.
        """
        from licensedcode import cache
        cche = cache.get_cache()

        cle = codebase.get_or_create_current_header()

        if cche.additional_license_directory:
            cle.extra_data['additional_license_directory'] = cche.additional_license_directory

        if cche.additional_license_plugins:
            cle.extra_data['additional_license_plugins'] = cche.additional_license_plugins

        if TRACE and cche.has_additional_licenses:
            logger_debug(
                f'add_referenced_filenames_license_matches: additional_licenses',
                f'has_additional_licenses: {cche.has_additional_licenses}\n',
                f'additional_license_directory: {cche.additional_license_directory}\n',
                f'additional_license_plugins : {cche.additional_license_plugins}'
            )

        if codebase.has_single_resource and not codebase.root.is_file:
            return

        modified = False
        for resource in codebase.walk(topdown=False):
            # follow license references to other files
            if TRACE:
                license_expressions_before = resource.detected_license_expression

            modified = add_referenced_filenames_license_matches_for_detections(resource, codebase)

            if TRACE and modified:
                license_expressions_after = resource.detected_license_expression
                logger_debug(
                    f'add_referenced_filenames_license_matches: Modified:',
                    f'{resource.path} with license_expressions:\n'
                    f'before: {license_expressions_before}\n'
                    f'after : {license_expressions_after}'
                )

        license_detections = collect_license_detections(
            codebase=codebase,
            include_license_clues=False
        )
        unique_license_detections = UniqueDetection.get_unique_detections(
            license_detections=license_detections,
        )

        if TRACE:
            logger_debug(
                f'process_codebase: codebase license_detections',
                f'license_detections: {license_detections}\n',
                f'unique_license_detections: {unique_license_detections}',
            )

        codebase.attributes.license_detections.extend([
            unique_detection.to_dict(license_diagnostics=license_diagnostics)
            for unique_detection in unique_license_detections
        ])



def add_referenced_filenames_license_matches_for_detections(resource, codebase):
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

        license_detection = LicenseDetectionFromResult.from_license_detection_mapping(
            license_detection_mapping=license_detection_mapping,
            file_path=resource.path,
        )
        detection_modified = False
        detections_added = []
        license_match_mappings = license_detection_mapping["matches"]
        referenced_filenames = get_referenced_filenames(license_detection.matches)

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
                detections_added.extend(referenced_resource.license_detections)
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
        license_detection_mapping["identifier"] = get_new_identifier_from_detections(
            initial_detection=license_detection_mapping,
            detections_added=detections_added,
            license_expression=license_expression,
        )

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
