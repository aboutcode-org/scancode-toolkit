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
import os

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

        for resource in codebase.walk(topdown=False):
            match_reference_license(resource,codebase)


def match_reference_license(resource, codebase):
    """
    Find instances for any licenses in referenced filenames
    """
    licenses = resource.licenses
    license_expressions = resource.license_expressions
    if not licenses:
        return 

    location = resource.location
    
    from licensedcode import cache
    from scancode.api import get_licenses
    idx = cache.get_index()
    matches = idx.match(
        location=location, min_score=0)
    
    modified = False

    for match in matches:
        ref_files=match.rule.referenced_filenames
        if len(ref_files) != 0:
            for i in range(len(ref_files)):
                if not ref_files[i].startswith('usr/share/common-licenses'):
                 new_loc=find_reference_file(location,ref_files[i])
                 if new_loc != None:
                   new_lic=get_licenses(new_loc, min_score=0)
                   licenses.extend(new_lic['licenses'])
                   license_expressions.extend(new_lic['license_expressions'])
                   modified = True

    if modified:
        codebase.save_resource(resource)
    return resource

def find_reference_file(location,referenced_filename):
    file_name=referenced_filename
    par_dir=fileutils.parent_directory(location)

    for root, dirs, files in os.walk(par_dir):
      if file_name in files:
         path_file = os.path.join(root,file_name)
         return path_file
        
    return None