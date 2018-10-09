#
# Copyright (c) 2018 nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/scancode-toolkit/
# The ScanCode software is licensed under the Apache License version 2.0.
# Data generated with ScanCode require an acknowledgment.
# ScanCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# When you publish or redistribute any data created with ScanCode or any ScanCode
# derivative work, you must accompany this data with the following acknowledgment:
#
#  Generated with ScanCode and provided on an "AS IS" BASIS, WITHOUT WARRANTIES
#  OR CONDITIONS OF ANY KIND, either express or implied. No content created from
#  ScanCode should be considered or used as legal advice. Consult an Attorney
#  for any legal advice.
#  ScanCode is a free software code scanning tool from nexB Inc. and others.
#  Visit https://github.com/nexB/scancode-toolkit/ for support and download.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import OrderedDict
from functools import partial

import attr

from plugincode.scan import ScanPlugin
from plugincode.scan import scan_impl
from scancode import CommandLineOption
from scancode import MISC_GROUP
from scancode import SCAN_OPTIONS_GROUP
from scancode import SCAN_GROUP
from scancode.api import DEJACODE_LICENSE_URL


def reindex_licenses(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return

    # TODO: check for temp file configuration and use that for the cache!!!
    from licensedcode.cache import get_cached_index
    import click
    click.echo('Checking and rebuilding the license index...')
    get_cached_index(check_consistency=True,)
    click.echo('Done.')
    ctx.exit(0)


@scan_impl
class LicenseScanner(ScanPlugin):
    """
    Scan a Resource for licenses.
    """

    resource_attributes = OrderedDict([
        ('licenses', attr.ib(default=attr.Factory(list))),
        ('license_expressions', attr.ib(default=attr.Factory(list))),
    ])

    sort_order = 2

    options = [
        CommandLineOption(('-l', '--license'),
            is_flag=True,
            help='Scan <input> for licenses.',
            help_group=SCAN_GROUP,
            sort_order=10),

        CommandLineOption(('--license-score',),
            type=int, default=0, show_default=True,
            requires=['license'],
            help='Do not return license matches with a score lower than this score. '
                 'A number between 0 and 100.',
            help_group=SCAN_OPTIONS_GROUP),

        CommandLineOption(('--license-text',),
            is_flag=True,
            requires=['license'],
            help='Include the detected licenses matched text.',
            help_group=SCAN_OPTIONS_GROUP),

        CommandLineOption(('--license-url-template',),
            default=DEJACODE_LICENSE_URL, show_default=True,
            requires=['license'],
            help='Set the template URL used for the license reference URLs. '
                 'Curly braces ({}) are replaced by the license key.',
            help_group=SCAN_OPTIONS_GROUP),

        CommandLineOption(('--license-diag',),
            is_flag=True,
            requires=['license'],
            help='Include diagnostic information in license scan results.',
            help_group=SCAN_OPTIONS_GROUP),

        CommandLineOption(
            ('--reindex-licenses',),
            is_flag=True, is_eager=True,
            callback=reindex_licenses,
            help='Check the license index cache and reindex if needed and exit.',
            help_group=MISC_GROUP)
    ]

    def is_enabled(self, license, **kwargs):  # NOQA
        return license

    def setup(self, cache_dir, **kwargs):
        """
        This is a cache warmup such that child process inherit from this.
        """
        from scancode_config import SCANCODE_DEV_MODE
        from licensedcode.cache import get_index
        get_index(cache_dir, check_consistency=SCANCODE_DEV_MODE,
                  return_value=False)

    def get_scanner(self, license_score=0, license_text=False,
                    license_url_template=DEJACODE_LICENSE_URL,
                    license_diag=False, cache_dir=None, **kwargs):

        from scancode.api import get_licenses
        return partial(get_licenses, min_score=license_score,
                       include_text=license_text, diag=license_diag,
                       license_url_template=license_url_template,
                       cache_dir=cache_dir)
