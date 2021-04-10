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

from licensedcode.tokenize import ngrams

import synclic

"""
A script to generate false-positive license detection rules from lists of SPDX
licenses.

Common license detection tools use list of SPDX licenses ids to support their operations.
As a result, we get a lot of matched licenses and in these cases, these are false positives.

Here we fetch all released SPDX licenses lists and generate false positives
using these approaches to have a reasonable set of combinations of license ids
as found in the wild:

1. For each SPDX license list release, we consider these lists:
 - all IDs
 - all non-deprecated IDs
 - all licenses
 - all non-deprecated licenses
 - all exceptions
 - all non-deprecated exceptions

We generate lists of ids only and list of ids and name

2. For each of these lists we sort them:
 - respective case
 - ignoring case

3. for each of these sorted list we collect sub-sequences of 6 license, one
  per line and generate a false positive RULE from that.

If a RULE already exists, it will be skipped.
"""

TRACE = False

template = '''----------------------------------------
is_false_positive: yes
notes: a sequence of SPDX license ids and names is not a license
---
{}
'''


@click.command()
@click.argument(
    'license_dir', type=click.Path(), metavar='DIR')

@click.argument(
    # 'A buildrules-formatted file used to generate new licenses rules.')
    'output', type=click.Path(), metavar='FILE')

@click.option(
    '--commitish', type=str, default=None,
    help='An optional commitish to use for SPDX license data instead of the latest release.')

@click.option(
    # 'A buildrules-formatted file used to generate new licenses rules.')
    '--from-list', default=None, type=click.Path(), metavar='LIST_FILE',
    help='Use file with a list of entries to ignore instead')

@click.option(
    '-t', '--trace', is_flag=True, default=False,
    help='Print execution trace.')

@click.help_option('-h', '--help')
def cli(license_dir, output, commitish=None, from_list=None, trace=False):
    """
    Generate ScanCode false-positive license detection rules from lists of SPDX
    license. Save these in FILE for use with buildrules.

    the `spdx` directory is used as a temp store for fetched SPDX licenses.
    """
    global TRACE
    TRACE = trace

    if not from_list:
        spdx_source = synclic.SpdxSource(external_base_dir=license_dir)

        spdx_by_key = spdx_source.get_licenses(
            commitish=commitish,
            skip_oddities=False,
        )

        all_licenses_and_exceptions = []
        all_licenses_and_exceptions_non_deprecated = []
        licenses = []
        exceptions = []
        licenses_non_deprecated = []
        exceptions_non_deprecated = []

        lists_of_licenses = [
            all_licenses_and_exceptions,
            all_licenses_and_exceptions_non_deprecated,
            licenses,
            exceptions,
            licenses_non_deprecated,
            exceptions_non_deprecated,
        ]

        for lspdx in spdx_by_key.values():
            all_licenses_and_exceptions.append(lspdx)
            is_deprecated = lspdx.is_deprecated
            if not is_deprecated:
                all_licenses_and_exceptions_non_deprecated.append(lspdx)
            if lspdx.is_exception:
                exceptions.append(lspdx)
                if not is_deprecated:
                    exceptions_non_deprecated.append(lspdx)
            else:
                licenses.append(lspdx)
                if not is_deprecated:
                    licenses_non_deprecated.append(lspdx)

        lists_of_sorted_licenses = []
        for lic_list in lists_of_licenses:
            sorted_case_sensitive = sorted(lic_list, key=lambda x: x.spdx_license_key)

            as_ids = [l.spdx_license_key for l in sorted_case_sensitive]
            lists_of_sorted_licenses.append(as_ids)

            as_id_names = [f'{l.spdx_license_key}  {l.name}' for l in sorted_case_sensitive]
            lists_of_sorted_licenses.append(as_id_names)

            sorted_case_insensitive = sorted(lic_list, key=lambda x: x.spdx_license_key.lower())
            as_ids = [l.spdx_license_key for l in sorted_case_insensitive]
            lists_of_sorted_licenses.append(as_ids)

            as_id_names = [f'{l.spdx_license_key}  {l.name}' for l in sorted_case_insensitive]
            lists_of_sorted_licenses.append(as_id_names)

    else:
        with open(from_list) as inp:
            lists_of_sorted_licenses = [inp.read().splitlines(False)]

    with open(output, 'w') as o:
        for lic_list in lists_of_sorted_licenses:
            write_ngrams(texts=lic_list, output=o)

        o.write('----------------------------------------\n')


def write_ngrams(texts, output, _seen=set(), ngram_length=6):
    """
    Write the texts list as ngrams to the output file-like object.
    """
    for text in ['\n'.join(ngs) for ngs in ngrams(texts, ngram_length=ngram_length)]:
        if text in _seen:
            continue
        _seen.add(text)
        output.write(template.format(text))


if __name__ == '__main__':
    cli()
