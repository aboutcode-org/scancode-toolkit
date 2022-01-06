# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import click

from licensedcode.cache import get_licenses_by_spdx_key

import synclic

"""
A script to generate license detection rules from lists of SPDX
licenses for their name or id/name combos.

It is common to see SPDX license names and ids used for licensing documentation.

Here we fetch the latest SPDX licenses list and generate rules for each
license id/name, name and a few other related combinations.
"""

TRACE = False

template = '''----------------------------------------
license_expression: {key}
relevance: 100
{is_license}: yes
minimum_coverage: 100
is_continuous: yes
notes: Rule based on an SPDX license identifier and name
---
{text}
'''


@click.command()
@click.argument(
    # 'A buildrules-formatted file used to generate new licenses rules.')
    'output', type=click.Path(), metavar='FILE')

@click.help_option('-h', '--help')
def cli(output):
    """
    Generate ScanCode license detection rules from a list of SPDX
    license. Save these in FILE for use with buildrules.

    The `spdx` directory is used as a temp store for fetched SPDX licenses.
    """

    licenses_by_spdx_key = get_licenses_by_spdx_key(
        licenses=None,
        include_deprecated=False,
        lowercase_keys=False,
        include_other_spdx_license_keys=True,
    )

    spdx_source = synclic.SpdxSource(external_base_dir=None)
    spdx_data = list(spdx_source.fetch_spdx_licenses())

    messages = []
    with open(output, 'w') as o:
        for spdx in spdx_data:
            is_exception = 'licenseExceptionId' in spdx
            spdx_key = spdx.get('licenseId') or spdx.get('licenseExceptionId')
            name = spdx['name']
            lic = licenses_by_spdx_key.get(spdx_key)
            if not lic:
                print('--> Skipping SPDX license unknown in ScanCode:', spdx_key,)
                continue
            for rule in build_rules(lic.key, spdx_key, name, is_exception):
                o.write(rule)

        o.write('----------------------------------------\n')

    for msg in messages:
        print(*msg)


def build_rules(key, spdx_key, name, is_exception=False):
    yield template.format(
        key=key,
        is_license='is_license_reference',
        text=name,
    )

    yield template.format(
        key=key,
        is_license='is_license_reference',
        text=f'name: {name}',
    )

    yield template.format(
        key=key,
        is_license='is_license_reference',
        text=f'{spdx_key} {name}',
    )

    yield template.format(
        key=key,
        is_license='is_license_reference',
        text=f'{name} {spdx_key}',
    )

    yield template.format(
        key=key,
        is_license='is_license_tag',
        text=f'{spdx_key} {name}',
    )

    yield template.format(
        key=key,
        is_license='is_license_tag',
        text=f'license: {spdx_key}',
    )

    yield template.format(
        key=key,
        is_license='is_license_tag',
        text=f'license: {name}',
    )

    if is_exception:
        yield template.format(
            key=key,
            is_license='is_license_tag',
            text=f'licenseExceptionId: {spdx_key}',
        )
    else:
        yield template.format(
            key=key,
            is_license='is_license_tag',
            text=f'licenseId: {spdx_key}',
        )


if __name__ == '__main__':
    cli()
