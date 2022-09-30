#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#
import csv
import warnings

import saneyaml

from commoncode.cliutils import PluggableCommandLineOption
from commoncode.cliutils import OUTPUT_GROUP
from plugincode.output import output_impl
from plugincode.output import OutputPlugin

from formattedcode import FileOptionType

# Tracing flags
TRACE = False


def logger_debug(*args):
    pass


if TRACE:
    import sys
    import logging

    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, str)
                                     and a or repr(a) for a in args))


@output_impl
class LicenseCsvOutput(OutputPlugin):

    options = [
        PluggableCommandLineOption(('--license-csv',),
            type=FileOptionType(mode='w', encoding='utf-8', lazy=True),
            metavar='FILE',
            help='Write license scan debug output as CSV to FILE.',
            help_group=OUTPUT_GROUP,
            sort_order=30),
    ]

    def is_enabled(self, license_csv, **kwargs):
        return license_csv

    def process_codebase(self, codebase, license_csv, **kwargs):
        results = self.get_files(codebase, **kwargs)
        write_csv(results=results, output_file=license_csv)


def write_csv(results, output_file):
    results = list(results)

    headers = dict([
        ('license', []),
    ])

    rows = list(flatten_scan(results, headers))

    ordered_headers = []
    for key_group in headers.values():
        ordered_headers.extend(key_group)

    w = csv.DictWriter(output_file, fieldnames=ordered_headers)
    w.writeheader()

    for r in rows:
        w.writerow(r)


def flatten_scan(scan, headers):
    """
    Yield ordered dictionaries of key/values flattening the sequence
    data in a single line-separated value and keying always by path,
    given a ScanCode `scan` results list. Update the `headers` mapping
    sequences with seen keys as a side effect.
    """
    seen = set()

    def collect_keys(mapping, key_group):
        """Update the headers with new keys."""
        keys = mapping.keys()
        headers[key_group].extend(k for k in keys if k not in seen)
        seen.update(keys)

    seen = set()
    for scanned_file in scan:
        path = scanned_file.pop('path')

        # removing any slash at the begening of the path
        path = path.lstrip('/')

        # use a trailing slash for directories
        if scanned_file.get('type') == 'directory':
            continue

        for licensing in scanned_file.get('licenses', []):
            matched_rule = licensing['matched_rule']
            lic = dict(
                path=path,
                score = with_two_decimals(licensing['score']),
                start_line = licensing['start_line'],
                end_line = licensing['end_line'],
                identifier=matched_rule['identifier'],
                license_expression=matched_rule['license_expression'],
                matcher=matched_rule['matcher'],
                rule_length=matched_rule['rule_length'],
                matched_length=matched_rule['matched_length'],
                match_coverage=with_two_decimals(matched_rule['match_coverage']),
                rule_relevance=with_two_decimals(matched_rule['rule_relevance']),
            )
            values= tuple(lic.items())
            if values in seen:
                continue
            else:
                seen.add(values)
                collect_keys(lic, 'license')
                yield lic

def with_two_decimals(val):
    """
    Return a normalized score string with two decimal values
    """
    if isinstance(val, (float, int)):
        val = '{:.2f}'.format(val)
    if not isinstance(val, str):
        val = str(val)
    return val
