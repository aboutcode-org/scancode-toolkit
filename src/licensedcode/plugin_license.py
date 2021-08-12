#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from functools import partial

import attr

from commoncode import fileutils
from commoncode.cliutils import PluggableCommandLineOption
from plugincode.scan import ScanPlugin
from plugincode.scan import scan_impl
from commoncode.cliutils import MISC_GROUP
from commoncode.cliutils import SCAN_OPTIONS_GROUP
from commoncode.cliutils import SCAN_GROUP
from scancode.api import SCANCODE_LICENSEDB_URL


def reindex_licenses(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return

    # TODO: check for temp file configuration and use that for the cache!!!
    from licensedcode.cache import get_index
    import click
    click.echo('Checking and rebuilding the license index...')
    get_index(check_consistency=True)
    click.echo('Done.')
    ctx.exit(0)


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
            sort_order=10),

        PluggableCommandLineOption(('--license-score',),
            type=int, default=0, show_default=True,
            required_options=['license'],
            help='Do not return license matches with a score lower than this score. '
                 'A number between 0 and 100.',
            help_group=SCAN_OPTIONS_GROUP),

        PluggableCommandLineOption(('--license-text',),
            is_flag=True,
            required_options=['license'],
            help='Include the detected licenses matched text.',
            help_group=SCAN_OPTIONS_GROUP),

        PluggableCommandLineOption(('--license-text-diagnostics',),
            is_flag=True,
            required_options=['license_text'],
            help='In the matched license text, include diagnostic highlights '
                 'surrounding with square brackets [] words that are not matched.',
            help_group=SCAN_OPTIONS_GROUP),

        PluggableCommandLineOption(('--license-url-template',),
            default=SCANCODE_LICENSEDB_URL, show_default=True,
            required_options=['license'],
            help='Set the template URL used for the license reference URLs. '
                 'Curly braces ({}) are replaced by the license key.',
            help_group=SCAN_OPTIONS_GROUP),

        PluggableCommandLineOption(
            ('--reindex-licenses',),
            hidden=True,
            is_flag=True, is_eager=True,
            callback=reindex_licenses,
            help='Check the license index cache and reindex if needed and exit.',
            help_group=MISC_GROUP)
    ]

    def is_enabled(self, license, **kwargs):  # NOQA
        return license

    def setup(self, **kwargs):
        """
        This is a cache warmup such that child process inherit from this.
        """
        from licensedcode.cache import populate_cache
        populate_cache()

    def get_scanner(
        self,
        license_score=0,
        license_text=False,
        license_text_diagnostics=False,
        license_url_template=SCANCODE_LICENSEDB_URL,
        **kwargs
    ):

        from scancode.api import get_licenses
        return partial(get_licenses,
            min_score=license_score,
            include_text=license_text,
            license_text_diagnostics=license_text_diagnostics,
            license_url_template=license_url_template
        )

    def process_codebase(self, codebase, **kwargs):
        
        if codebase.has_single_resource:
            return

        for resource in codebase.walk(topdown=False):
            match_reference_license(resource,codebase)


def match_reference_license(resource, codebase):
    """
    Return the updated license matches having reference to another files
    """
    if not resource.is_file:
        return

    licenses = resource.licenses
    license_expressions = resource.license_expressions
    if not licenses:
        return 

    referenced_licenses = []
    referenced_license_expressions = []
    referenced_filenames = []
    
    for license in licenses:
        referenced_files = license['matched_rule']['referenced_filenames']
        for referenced_filename in referenced_files:
            if not referenced_filename in referenced_filenames:
                referenced_filenames.append(referenced_filename)
                
    for referenced_filename in referenced_filenames:
        new_resource = find_reference_licenses(referenced_filename=referenced_filename, resource=resource, codebase=codebase)
        if new_resource:
            referenced_licenses.extend(new_resource.licenses)
            referenced_license_expressions.extend(new_resource.license_expressions)

    licenses.extend(referenced_licenses)
    license_expressions.extend(referenced_license_expressions)
    codebase.save_resource(resource)
    return resource


def find_reference_licenses(referenced_filename, resource, codebase, **kwargs):
    """
    Return the resource object for matching referenced-filename given a resource in codebase
    """
    parent = resource.parent(codebase)
    
    for child in parent.children(codebase):
        path = child.path
        if path.endswith(referenced_filename) or fileutils.file_base_name(child.path) == referenced_filename:
            return child
