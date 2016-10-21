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
        scan_results = scan_results['results']

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
    rows = []

    # unique keys, but ordered
    keys = OrderedSet(['Resource'])

    for entry in scan:
        location = entry['location']
        if strip:
            # do not keep leading slash but add it back afterwards. keep trailing slashes
            location = location.lstrip('/')
            splits = [s for s in location.split('/')]
            location = '/'.join(splits[strip:])

        location = location.startswith('/')  and location or '/' + location

        # collect rows for each section if present and each corresponding keys

        """
        {
          "type": "file",
          "name": "test_patch.py",
          "extension": ".py",
          "date": "2015-12-08",
          "size": 72347,
          "sha1": "bc1dc65b7d6b88709ce170291f93cd255bda8ffa",
          "md5": "25edeca9fbedd5b53e7e70af0ab0140a",
          "files_count": null,
          "mime_type": "text/x-python",
          "file_type": "Python script, ASCII text executable",
          "programming_language": "Python",
          "is_binary": null,
          "is_text": true,
          "is_archive": null,
          "is_media": null,
          "is_source": true,
          "is_script": true
        }
        """

        for info in entry.get('infos', []):
            if info['type'] == 'directory':
                if not location.endswith('/'):
                    location = location + '/'
            inf = OrderedDict(Resource=location)
            for k, val in info.items():
                key = 'info_' + k
                inf[key] = val
                keys.add(key)
            rows.append(inf)

        """
      "licenses": [
        {
          "key": "apache-2.0",
          "score": 100.0,
          "short_name": "Apache 2.0",
          "category": "Attribution",
          "owner": "Apache Software Foundation",
          "homepage_url": "http://www.apache.org/licenses/",
          "text_url": "http://www.apache.org/licenses/LICENSE-2.0",
          "dejacode_url": "https://enterprise.dejacode.com/license_library/Demo/apache-2.0/",
          "spdx_license_key": "Apache-2.0",
          "spdx_url": "http://spdx.org/licenses/Apache-2.0",
          "start_line": 4,
          "end_line": 23
        },
        {
          "key": "scancode-acknowledgment",
          "score": 100.0,
          "short_name": "ScanCode acknowledgment",
          "category": "Attribution",
          "owner": "nexB Inc.",
          "homepage_url": "https://github.com/nexB/scancode-toolkit/",
          "text_url": "",
          "dejacode_url": "https://enterprise.dejacode.com/license_library/Demo/scancode-acknowledgment/",
          "spdx_license_key": "",
          "spdx_url": "",
          "start_line": 4,
          "end_line": 23
        }
      ],
        """
        for licensing in entry.get('licenses', []):
            lic = OrderedDict(Resource=location)
            for k, val in licensing.items():
                if k not in ('start_line', 'end_line',):
                    k = 'license_' + k
                lic[k] = val
                keys.add(k)
            rows.append(lic)

        """
      "copyrights": [
        {
          "statements": [
            "Copyright (c) 2015 nexB Inc."
          ],
          "holders": [
            "nexB Inc."
          ],
          "authors": [],
          "start_line": 2,
          "end_line": 2
        }
      ],
        """
        for copy_info in entry.get('copyrights', []):
            start_line = copy_info['start_line']
            end_line = copy_info['end_line']
            for cop in copy_info.get('statements', []):
                inf = OrderedDict(Resource=location)
                inf['copyright'] = cop
                inf['start_line'] = start_line
                inf['end_line'] = end_line
                rows.append(inf)
                keys.update(inf.keys())

            for hold in copy_info.get('holders', []):
                inf = OrderedDict(Resource=location)
                inf['copyright_holder'] = hold
                inf['start_line'] = start_line
                inf['end_line'] = end_line
                rows.append(inf)
                keys.update(inf.keys())

            for auth in copy_info.get('authors', []):
                inf = OrderedDict(Resource=location)
                inf['author'] = auth
                inf['start_line'] = start_line
                inf['end_line'] = end_line
                rows.append(inf)
                keys.update(inf.keys())

        """
        {
          "type": "Nuget",
          "packaging": "archive",
          "primary_language": null
        }
        """
        for info in entry.get('packages', []):
            inf = OrderedDict(Resource=location)
            inf.update(('package_' + k, v or '') for k, v in info.items())
            keys.update(inf.keys())
            rows.append(inf)

        for info in [promote_inner_keys(y) for x in entry.get('package_details', []) for y in flatten(x)]:
            inf = OrderedDict(Resource=location)
            inf.update(('package_details_' + k, v or '') for k, v in info.items())
            keys.update(inf.keys())
            rows.append(inf)

        """
        {
          "url": "http://nexb.com/",
          "start_line": 3,
          "end_line": 3
        },
        """
        for url in entry.get('urls', []):
            url = OrderedDict(Resource=location)
            for k, val in url.items():
                url[k] = val
                keys.add(key)
            rows.append(url)

        """
        {
          "email": "info@winimage.com",
          "start_line": 1124,
          "end_line": 1124
        }
        """
        for email in entry.get('emails', []):
            email = OrderedDict(Resource=location)
            for k, val in email.items():
                email[k] = val
                keys.add(key)
            rows.append(email)


    # keys = ['Resource'] + [x for x in keys if x != 'Resource']
    all_rows = []
    for row in rows:
        d = OrderedDict()
        for k in keys.keys():
            d[k] = row.get(k, '')
        all_rows.append(d)

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
