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


def flatten_on_key(k, d):
    if k in d and isinstance(d[k], list) and len(d[k]) > 0:
        flatlist = []
        for x in d[k]:
            flat_d = OrderedDict(d)
            flat_d[k] = x
            flatlist.append(flat_d)
        return flatlist
    else:
        return [d]


def flatten(d):
    temp = [d]
    for k in d.keys():
        flatlist = []
        for v in temp:
            flatlist += flatten_on_key(k, v)
        temp = flatlist
    return flatlist


def promote_inner_keys(d):
    for k1, v1 in d.items():
        if isinstance(v1, dict):
            d.pop(k1)
            for k2, v2 in v1.items():
                d[k1 + "_" + k2] = v2
    return d


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


def json_scan_to_csv(json_input, csv_output, strip=0):
    """
    Convert a scancode JSON output file to a nexb-toolkit-like CSV.
    Optionally strip up to `strip` path segments from the location paths.
    """
    scan_results = load_scan(json_input)
    rows = scan_as_list(scan_results, strip)
    headers = rows[0].keys()
    with open(csv_output, 'wb') as output:
        w = unicodecsv.writer(output)
        w.writerow(headers)
        for r in rows:
            w.writerow(r.values())


def scan_as_list(scan, strip=0):
    """
    Return a list of ordered dictionaries of key/values flattening the data and
    keying always by location, given a ScanCode scan results list.
    Optionally strip up to `strip` path segments from the location paths.
    """
    resources = OrderedDict()

    # unique keys, but ordered
    keys = OrderedSet(['Resource'])

    for entry in scan:
        location = entry['path']
        if strip:
            # do not keep leading slash but add it back afterwards. keep trailing slashes
            location = location.lstrip('/')
            splits = [s for s in location.split('/')]
            location = '/'.join(splits[strip:])

        location = location.startswith('/') and location or '/' + location

        if entry['type'] == 'directory':
            if not location.endswith('/'):
                location = location + '/'

        # element 0 = file info in an OrderedDict
        # element 1 = license info, each license and its info is in its own OrderedDict, which is then stored in a list
        # element 2 = copyright info, each copyright and its info is in its own OrderedDict, which is then stored in a list
        # There will need to be a fourth element for package info
        resources[location] = [OrderedDict(Resource=location), [], []]

        file_info = resources[location][0]
        licenses = resources[location][1]
        copyrights = resources[location][2]

        keys.add('type')
        file_info['type'] = entry['type']

        for field in entry.keys():
            # We handled these fields above
            if field == 'path' or field == 'type':
                continue

            elif field == 'licenses':
                for licensing in entry.get('licenses', []):
                    lic = OrderedDict(Resource=location)
                    for k, val in licensing.items():
                        if k == 'matched_rule':
                            # We deal with this after processing the rest of the license fields
                            continue
                        if k not in ('start_line', 'end_line',):
                            k = 'license_' + k
                        lic[k] = val
                        keys.add(k)
                    licenses.append(lic)

                    matched_rule = licensing.get('matched_rule')
                    # We create a new row of matched rule info for each license associated with a rule
                    for matched_rule_license in matched_rule.get('licenses', []):
                        matched_rule_info = OrderedDict(Resource=location)
                        for k, val in matched_rule.items():
                            k = 'license_matched_rule_' + k
                            if k == 'license_matched_rule_licenses':
                                matched_rule_info[k] = matched_rule_license
                            else:
                                matched_rule_info[k] = val
                            keys.add(k)
                        licenses.append(matched_rule_info)

            elif field == 'copyrights':
                for copy_info in entry.get('copyrights', []):
                    start_line = copy_info['start_line']
                    end_line = copy_info['end_line']
                    for cop in copy_info.get('statements', []):
                        inf = OrderedDict(Resource=location)
                        inf['copyright'] = cop
                        inf['start_line'] = start_line
                        inf['end_line'] = end_line
                        copyrights.append(inf)
                        keys.update(inf.keys())

                    for hold in copy_info.get('holders', []):
                        inf = OrderedDict(Resource=location)
                        inf['copyright_holder'] = hold
                        inf['start_line'] = start_line
                        inf['end_line'] = end_line
                        copyrights.append(inf)
                        keys.update(inf.keys())

                    for auth in copy_info.get('authors', []):
                        inf = OrderedDict(Resource=location)
                        inf['author'] = auth
                        inf['start_line'] = start_line
                        inf['end_line'] = end_line
                        copyrights.append(inf)
                        keys.update(inf.keys())

            elif field == 'packages':
                # TODO: Add package option support
                continue

            elif field == 'scan_errors':
                # TODO: Add scan error support
                continue

            else:
                keys.add(field)
                file_info[field] = entry[field]

    all_rows = []
    for resource in resources:
        file_info = resources[resource][0]
        licenses = resources[resource][1]
        copyrights = resources[resource][2]

        # Flatten file info
        row = OrderedDict()
        for k in keys.keys():
            row[k] = file_info.get(k, '')
        all_rows.append(row)

        # Flatten license info
        for licensing in licenses:
            row = OrderedDict()
            for k in keys.keys():
                row[k] = licensing.get(k, '')
            all_rows.append(row)

        # Flatten copyright info
        for copy_info in copyrights:
            row = OrderedDict()
            for k in keys.keys():
                row[k] = copy_info.get(k, '')
            all_rows.append(row)

    return all_rows


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
