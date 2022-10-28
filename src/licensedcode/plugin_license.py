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
import posixpath
from functools import partial

import attr
from commoncode.cliutils import PluggableCommandLineOption
from commoncode.cliutils import SCAN_OPTIONS_GROUP
from commoncode.cliutils import SCAN_GROUP
from commoncode.resource import clean_path
from plugincode.scan import ScanPlugin
from plugincode.scan import scan_impl

from scancode.api import SCANCODE_LICENSEDB_URL

TRACE = os.environ.get('SCANCODE_DEBUG_LICENSE_PLUGIN', False)


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
        ('licenses', attr.ib(default=attr.Factory(list))),
        ('license_expressions', attr.ib(default=attr.Factory(list))),
        ('percentage_of_license_text', attr.ib(default=0)),
    ])

    sort_order = 2

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
            help='[EXPERIMENTAL] Detect unknown licenses and follow license '
                 'references such as "See license in file COPYING".',
            help_group=SCAN_OPTIONS_GROUP,
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

    def process_codebase(self, codebase, unknown_licenses, **kwargs):
        """
        Post process the codebase to further detect unknown licenses and follow
        license references to other files.

        This is an EXPERIMENTAL feature for now.
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

        modified = False
        for resource in codebase.walk(topdown=False):
            # follow license references to other files
            if TRACE:
                license_expressions_before = list(resource.license_expressions)

            if unknown_licenses:
                modified = add_referenced_filenames_license_matches(resource, codebase)

            if has_additional_licenses and resource.is_file and resource.licenses:
                add_builtin_license_flag(resource, licenses)

            if TRACE and modified:
                license_expressions_after = list(resource.license_expressions)
                logger_debug(
                    f'add_referenced_filenames_license_matches: Modfied:',
                    f'{resource.path} with license_expressions:\n'
                    f'before: {license_expressions_before}\n'
                    f'after : {license_expressions_after}'
                )


def add_builtin_license_flag(resource, licenses):
    """
    Add a `is_builtin` flag to each license rule data mapping if there are
    additional licenses present in the cache, either through an additional
    license directory or additional license plugins.
    """
    for match in resource.licenses:
        add_builtin_value(license_match=match, licenses=licenses)


def add_builtin_value(license_match, licenses):
    license_key = license_match['key']
    lic = licenses.get(license_key)
    if lic.is_builtin:
        license_match['matched_rule']['is_builtin'] = True
    else:
        license_match['matched_rule']['is_builtin'] = False


def add_referenced_filenames_license_matches(resource, codebase):
    """
    Return an updated ``resource`` saving it in place, after adding new license
    matches (licenses and license_expressions) following their Rule
    ``referenced_filenames`` if any. Return None if ``resource`` is not a file
    Resource or was not updated.
    """
    if not resource.is_file:
        return

    license_matches = resource.licenses
    if not license_matches:
        return

    license_expressions = resource.license_expressions

    modified = False

    for referenced_filename in get_referenced_filenames(license_matches):
        referenced_resource = find_referenced_resource(
            referenced_filename=referenced_filename,
            resource=resource,
            codebase=codebase,
        )

        if referenced_resource and referenced_resource.licenses:
            modified = True
            # TODO: we should hint that these matches were defererenced from
            # following a referenced filename
            license_matches.extend(referenced_resource.licenses)
            license_expressions.extend(referenced_resource.license_expressions)

    if modified:
        codebase.save_resource(resource)
        return resource


def get_referenced_filenames(license_matches):
    """
    Return a list of unique referenced filenames found in the rules of a list of
    ``license_matches``
    """
    unique_filenames = []
    for license_match in license_matches:
        for filename in license_match['matched_rule']['referenced_filenames']:
            if filename not in unique_filenames:
                unique_filenames.append(filename)

    return unique_filenames


def find_referenced_resource(referenced_filename, resource, codebase, **kwargs):
    """
    Return a Resource matching the ``referenced_filename`` path or filename
    given a ``resource`` in ``codebase``. Return None if the
    ``referenced_filename`` cannot be found in the same directory as the base
    ``resource``. ``referenced_filename`` is the path or filename referenced in
    a LicenseMatch of ``resource``,
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
