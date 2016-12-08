#!/usr/bin/python2
#
# Copyright (c) 2016 nexB Inc. and others. All rights reserved.
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

from __future__ import print_function, absolute_import

from collections import OrderedDict
import json
import os

import click
import unicodecsv

"""
Convert a ScanCode JSON scan file to a nexb-toolkit-like CSV.
Ensure you are in the scancode virtualenv and call:
etc/scripts/json2csv -h
"""


class OrderedSet(object):
    """
    Ordered set based on list.
    """
    def __init__(self):
        self.seq = []

    def add(self, value):
        if value not in self.seq:
            self.seq.append(value)

    def keys(self):
        return self.seq[:]

    def update(self, iterable):
        for value in iterable:
            self.add(value)


def load_scan(json_input):
    """
    Return a list of scan results loaded from a json_input, either in ScanCode
    standard JSON format or the data.json html-app format.
    """
    with open(json_input) as jsonf:
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


def json_scan_to_csv(json_input, csv_output, strip=0):
    """
    Convert a scancode JSON output file to a nexb-toolkit-like CSV.
    Optionally strip up to `strip` path segments from the location paths.
    """
    scan_results = load_scan(json_input)
    rows = list(flatten_scan(scan_results, strip))
    headers = collect_header_keys(rows)
    with open(csv_output, 'wb') as output:
        w = unicodecsv.DictWriter(output, headers)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def flatten_scan(scan, strip=0):
    """
    Yield ordered dictionaries of key/values flattening the data and
    keying always by path, given a ScanCode scan results list.
    Optionally strip up to `strip` path segments from the location paths.
    """

    for scanned_file in scan:
        path = scanned_file['path']
        if strip:
            # do not keep leading slash but add it back afterwards. keep trailing slashes
            path = path.lstrip('/')
            splits = [s for s in path.split('/')]
            path = '/'.join(splits[strip:])

        path = path if path.startswith('/') else '/' + path

        if scanned_file.get('type', '') == 'directory':
            if not path.endswith('/'):
                path = path + '/'

        path = '/code' + path

        file_info = OrderedDict(Resource=path)
        info_details = OrderedDict(((k, v) for k, v in scanned_file.items() if k != 'path' and not isinstance(v, list)))
        file_info.update(info_details)
        yield file_info

        error_info = OrderedDict(Resource=path)
        errors = [error for error in scanned_file.get('scan_errors', [])]
        error_info['scan_errors'] = '\n'.join(errors)
        yield error_info

        for licensing in scanned_file.get('licenses', []):
            lic = OrderedDict(Resource=path)
            for k, val in licensing.items():
                if k == 'matched_rule':
                    continue
                if k not in ('start_line', 'end_line',):
                    k = 'license__' + k
                lic[k] = val
            yield lic

        for copy_info in scanned_file.get('copyrights', []):
            start_line = copy_info['start_line']
            end_line = copy_info['end_line']
            for key, header in (('statements', 'copyright'), ('holders', 'copyright_holder'), ('authors', 'author')):
                for cop in copy_info.get(key, []):
                    inf = OrderedDict(Resource=path)
                    inf[header] = cop
                    inf['start_line'] = start_line
                    inf['end_line'] = end_line
                    yield inf

        for email in scanned_file.get('emails', []):
            email_info = OrderedDict(Resource=path)
            for k, val in email.items():
                email_info[k] = val
            yield email_info

        for url in scanned_file.get('urls', []):
            url_info = OrderedDict(Resource=path)
            for k, val in url.items():
                url_info[k] = val
            yield url_info

        excluded_columns = ('packaging',
                            'payload_type',
                            'keywords_doc_url',
                            'download_sha1',
                            'download_sha256',
                            'download_md5',
                            'code_view_url',
                            'vcs_tool',
                            'vcs_revision',
                            'license_expression')

        for package in scanned_file.get('packages', []):
            pack = OrderedDict(Resource=path)
            for k, val in package.items():
                nk = 'package__' + k
                if not isinstance(val, (list, dict, OrderedDict)):
                    if k not in excluded_columns:
                        pack[nk] = val
                elif k in ('authors', 'download_urls', 'copyrights', 'asserted_licenses'):
                    if len(val) > 0:
                        if k == 'authors':
                            # We only want the first author
                            pack[nk] = val[0]['name']
                        if k == 'download_urls':
                            # We only want the first URL
                            pack[nk] = val[0]
                        if k == 'copyrights':
                            pack[nk] = '\n'.join(val)
                        if k == 'asserted_licenses':
                            licenses = [license_info['license'] for license_info in val]
                            pack[nk] = '\n'.join(licenses)
                    else:
                        pack[nk] = ''
            yield pack


def collect_header_keys(scan_data):
    """
    Return a list of keys collected from a list of scanned data dictionaries.
    """
    keys = OrderedSet()
    for scan in scan_data:
        keys.update(scan.keys())
    return keys.keys()


@click.command()
@click.argument('json_input', type=click.Path(exists=True, readable=True))
@click.argument('csv_output', type=click.Path(exists=False, readable=True))
@click.option('-s', '--strip', help='Number of leading path segments to strip from location paths', type=click.INT, default=0)
@click.help_option('-h', '--help')
def cli(json_input, csv_output, strip=0):
    """
    Convert a ScanCode JSON scan file to a nexb-toolkit-like CSV.
    Optionally strip up to `strip` leading path segments from the location paths.

    JSON_INPUT is either a ScanCode json format scan or the data.json file from a ScanCode html-app format scan.
    """
    json_input = os.path.abspath(os.path.expanduser(json_input))
    csv_output = os.path.abspath(os.path.expanduser(csv_output))
    json_scan_to_csv(json_input, csv_output, strip=strip)


if __name__ == '__main__':
    cli()
