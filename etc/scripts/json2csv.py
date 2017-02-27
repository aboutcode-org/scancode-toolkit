#!/usr/bin/python2
#
# Copyright (c) 2017 nexB Inc. and others. All rights reserved.
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

from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import codecs
from collections import OrderedDict
import json
import os

import click
import unicodecsv

"""
Convert a ScanCode JSON scan file to a nexb-toolkit-like CSV.
Ensure you are in the scancode virtualenv and call: etc/scripts/json2csv -h
"""


def load_scan(json_input):
    """
    Return a list of scan results loaded from a json_input, either in ScanCode
    standard JSON format or the data.json html-app format.
    """
    with codecs.open(json_input, 'rb', encoding='utf-8') as jsonf:
        scan = jsonf.read()

    # strip the leading data padding if any (used in the html-app JSON)
    html_app_lead = 'data='
    is_html_app_json = scan.startswith(html_app_lead)
    if is_html_app_json:
        scan = scan[len(html_app_lead):]

    scan_results = json.loads(scan, object_pairs_hook=OrderedDict)

    if not is_html_app_json:
        scan_results = scan_results['files']

    return scan_results


def json_scan_to_csv(json_input, csv_output):
    """
    Convert a scancode JSON output file to a nexb-toolkit-like CSV.
    csv_output is an open file descriptor.
    """
    scan_results = load_scan(json_input)
    rows = list(flatten_scan(scan_results))
    headers = collect_header_keys(rows)
    w = unicodecsv.DictWriter(csv_output, headers)
    w.writeheader()
    for r in rows:
        w.writerow(r)


def flatten_scan(scan):
    """
    Yield ordered dictionaries of key/values flattening the data and
    keying always by path, given a ScanCode scan results list.
    """
    for scanned_file in scan:
        path = scanned_file['path']

        # alway use a root slash
        path = path if path.startswith('/') else '/' + path

        # alway use a trailing slash for directories
        if scanned_file.get('type', '') == 'directory':
            if not path.endswith('/'):
                path = path + '/'

        # alway create a root directory
        path = '/code' + path

        file_info = OrderedDict()
        file_info['Resource'] = path
        # info are NOT lists
        info_details = ((k, v) for k, v in scanned_file.items() if k != 'path' and not isinstance(v, list))
        file_info.update(info_details)
        # Scan errors are joined in a single multi-line value
        file_info['scan_errors'] = '\n'.join(scanned_file.get('scan_errors', []))
        yield file_info

        for licensing in scanned_file.get('licenses', []):
            lic = OrderedDict()
            lic['Resource'] = path
            for k, val in licensing.items():
                # do not include matched rule details for now.
                if k == 'matched_rule':
                    continue

                if k == 'score':
                    # normalize the string representation of this number
                    val = '{:.2f}'.format(val)

                # lines are present in multiple scans: keep their column name as not scan-specific
                # Prefix othe columns with license__
                if k not in ('start_line', 'end_line',):
                    k = 'license__' + k
                lic[k] = val
            yield lic

        key_to_header_mapping = [
            ('statements', 'copyright'),
            ('holders', 'copyright_holder'),
            ('authors', 'author')
        ]
        for copy_info in scanned_file.get('copyrights', []):
            start_line = copy_info['start_line']
            end_line = copy_info['end_line']
            # rename some keys to a different column header
            for key, header in key_to_header_mapping:
                for cop in copy_info.get(key, []):
                    inf = OrderedDict()
                    inf['Resource'] = path
                    inf[header] = cop
                    inf['start_line'] = start_line
                    inf['end_line'] = end_line
                    yield inf

        for email in scanned_file.get('emails', []):
            email_info = OrderedDict()
            email_info['Resource'] = path
            email_info.update(email)
            yield email_info

        for url in scanned_file.get('urls', []):
            url_info = OrderedDict()
            url_info['Resource'] = path
            url_info.update(url)
            yield url_info

        # exclude some columns from the packages for now
        excluded_package_columns = {
            'packaging',
            'payload_type',
            'keywords_doc_url',
            'download_sha1',
            'download_sha256',
            'download_md5',
            'code_view_url',
            'vcs_tool',
            'vcs_revision',
            'license_expression'
        }

        for package in scanned_file.get('packages', []):
            pack = OrderedDict()
            pack['Resource'] = path
            for k, val in package.items():
                # prefix columns with "package__"
                nk = 'package__' + k

                # keep all non-excluded plain string values
                if k not in excluded_package_columns and not isinstance(val, (list, dict, OrderedDict)):
                    # prefix versions with a v to avoid spreadsheet tools to mistake
                    # a version for a number or date.
                    if k == 'version' and val:
                        val = 'v ' + val
                    pack[nk] = val

                # FIXME: we only keep for now some of the value lists
                elif k in ('authors', 'download_urls', 'copyrights', 'asserted_licenses'):
                    pack[nk] = ''
                    if val and len(val):
                        if k == 'authors':
                            # FIXME: we only keep the first author name for now
                            pack[nk] = val[0]['name']

                        if k == 'download_urls':
                            # FIXME: we only keep the first URL for now
                            pack[nk] = val[0]

                        if k == 'copyrights':
                            # All copyright statements are joined in a single multiline value
                            pack[nk] = '\n'.join(val)

                        if k == 'asserted_licenses':
                            # All licenses are joined in a single multi-line value
                            licenses = [license_info.get('license') for license_info in val]
                            licenses = [lic for lic in licenses if lic]
                            pack[nk] = '\n'.join(licenses)

            yield pack


def collect_header_keys(scan_data):
    """
    Return a list of keys collected from a list of scanned data dictionaries.
    """
    keys = []
    for scan in scan_data:
        for key in scan.keys():
            if key not in keys:
                keys.append(key)
    return keys


@click.command()
@click.argument('json_input', type=click.Path(exists=True, readable=True))
@click.argument('csv_output', type=click.File('wb', lazy=False))
@click.help_option('-h', '--help')
def cli(json_input, csv_output):
    """
    Convert a ScanCode JSON scan file to a nexb-toolkit-like CSV.

    JSON_INPUT is either a ScanCode json format scan or the data.json file from a ScanCode html-app format scan.

    Paths will be prefixed with '/code/' to provide a common base directory for scanned resources.
    """
    json_input = os.path.abspath(os.path.expanduser(json_input))
    json_scan_to_csv(json_input, csv_output)


if __name__ == '__main__':
    cli()
