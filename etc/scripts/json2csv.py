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
    def __init__(self, arg):
        self.seq = arg[:]

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


def parse_scan(scan):
    header = []
    rows = []

    # We get the headers of the CSV from the first component.
    for key in scan[0].keys():
        header.append(key)

    for component in scan:
        row = []
        for field in header:
            row.append(component[field])
        rows.append(row)

    return header, rows


def json_scan_to_csv(json_input, csv_output, strip=0):
    """
    Convert a scancode JSON output file to a nexb-toolkit-like CSV.
    Optionally strip up to `strip` path segments from the location paths.
    """
    scan_results = load_scan(json_input)
    headers, rows = parse_scan(scan_results)
    with open(csv_output, 'wb') as output:
        w = unicodecsv.writer(output)
        w.writerow(headers)
        for r in rows:
            w.writerow(r)


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
