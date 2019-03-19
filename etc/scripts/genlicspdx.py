# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 nexB Inc. and others. All rights reserved.
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
from __future__ import unicode_literals
from __future__ import print_function

import os

import click
click.disable_unicode_literals_warning = True

from licensedcode.models import load_licenses
from scancode.cli import run_scan


"""
Generate an SPDX document for each license known in ScanCode that are not usted
at SPDX.
Run python genlicspdx.py -h for help.

NOTE: this is rather inefficient as it is starting a new command line process
for each license, taking a few seconds each time.
Upcomming code to call a scan function instead will be more efficient.
"""

FOSS_CATEGORIES = set([
    'Copyleft',
    'Copyleft Limited',
    'Patent License',
    'Permissive',
    'Public Domain',
])


NON_INTERESTING_KEYS=set([
    'other-copyleft',
    'other-permissive',
])


@click.command()
@click.argument('license_dir',
    type=click.Path(file_okay=False, exists=True, writable=True,
                    allow_dash=False, resolve_path=True),
    metavar='DIR')
@click.option('-v', '--verbose', is_flag=True, default=False, help='Print execution messages.')
@click.help_option('-h', '--help')
def cli(license_dir, verbose):
    """
    Create one SPDX tag-value document for each non-SPDX ScanCode licenses.
    Store these in the DIR directory
    """

    base_kwargs = dict(
        license=True, license_diag=True, license_text=True, info=True,
        strip_root=True, quiet=True, return_results=False)

    licenses_by_key = load_licenses(with_deprecated=False)


    for i, lic in enumerate(licenses_by_key.values()):
        ld = lic.to_dict()

        if lic.spdx_license_key:
            if verbose:
                click.echo(
                    'Skipping ScanCode: {key} that is an SPDX license: {spdx_license_key}'.format(**ld))
            continue

        if not lic.text_file or not os.path.exists(lic.text_file):
            if verbose:
                click.echo(
                    'Skipping license without text: {key}'.format(**ld))
            continue

        if lic.category not in FOSS_CATEGORIES:
            if verbose:
                click.echo(
                    'Skipping non FOSS license: {key}'.format(**ld))
            continue

        output = 'licenseref-scancode-{key}.spdx'.format(**ld)
        output = os.path.join(license_dir, output)

        if verbose:
            click.echo('Creating SPDX document for license: {key}'.format(**ld))
            click.echo('at: {output}'.format(**locals()))

        with open(output, 'wb') as ouput_file:
            kwargs = dict(input=lic.text_file, spdx_tv=ouput_file)
            kwargs.update(base_kwargs)
            run_scan(**kwargs)


if __name__ == '__main__':
    cli()
