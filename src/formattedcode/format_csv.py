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

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

from collections import OrderedDict

import unicodecsv

from plugincode.output import scan_output_writer


"""
Output plugin to write scan results as CSV.
"""


@scan_output_writer
def write_csv(scanned_files, output_file, *args, **kwargs):
    """
    Write scan output formatted as CSV.
    """
    scan_results = list(scanned_files)

    headers = OrderedDict([
        ('info', []),
        ('license', []),
        ('copyright', []),
        ('email', []),
        ('url', []),
        ('package', []),
    ])

    # note: FIXME: headers are collected as a side effect and this is not great
    rows = list(flatten_scan(scan_results, headers))

    ordered_headers = []
    for key_group in headers.values():
        ordered_headers.extend(key_group)

    w = unicodecsv.DictWriter(output_file, ordered_headers)
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

    for scanned_file in scan:
        path = scanned_file.pop('path')

        # alway use a root slash
        if not path.startswith('/'):
            path = '/' + path

        # use a trailing slash for directories
        if scanned_file.get('type') == 'directory' and not path.endswith('/'):
            path += '/'

        errors = scanned_file.pop('scan_errors', [])

        file_info = OrderedDict(Resource=path)
        file_info.update(((k, v) for k, v in scanned_file.items()
        # FIXME: info are NOT lists: lists are the actual scans
                          if not isinstance(v, list)))
        # Scan errors are joined in a single multi-line value
        file_info['scan_errors'] = '\n'.join(errors)
        collect_keys(file_info, 'info')
        yield file_info

        for licensing in scanned_file.get('licenses', []):
            lic = OrderedDict(Resource=path)
            for k, val in licensing.items():
                # do not include matched text for now.
                if k == 'matched_text':
                    continue
                if k == 'matched_rule':
                    for mrk, mrv in val.items():
                        mrk = 'matched_rule__' + mrk
                        if mrk == 'license_choice':
                            mrv = 'y' if mrv else ''
                        if mrk == 'licenses':
                            mrv = ' '.join(mrv)
                        if mrk in ('match_coverage', 'rule_relevance'):
                            # normalize the string representation of this number
                            mrv = '{:.2f}'.format(mrv)
                        lic[mrk] = mrv
                    continue

                if k == 'score':
                    # normalize the string representation of this number
                    val = '{:.2f}'.format(val)

                # lines are present in multiple scans: keep their column name as not scan-specific
                # Prefix othe columns with license__
                if k not in ('start_line', 'end_line',):
                    k = 'license__' + k
                lic[k] = val
            collect_keys(lic, 'license')
            yield lic

        copyright_key_to_column_name = [
            ('statements', 'copyright'),
            ('holders', 'copyright_holder'),
            ('authors', 'author')
        ]
        for copy_info in scanned_file.get('copyrights', []):
            start_line = copy_info['start_line']
            end_line = copy_info['end_line']
            # rename some keys to a different column header
            for key, header in copyright_key_to_column_name:
                for cop in copy_info.get(key, []):
                    inf = OrderedDict(Resource=path)
                    inf[header] = cop
                    inf['start_line'] = start_line
                    inf['end_line'] = end_line
                    collect_keys(inf, 'copyright')
                    yield inf

        for email in scanned_file.get('emails', []):
            email_info = OrderedDict(Resource=path)
            email_info.update(email)
            collect_keys(email_info, 'email')
            yield email_info

        for url in scanned_file.get('urls', []):
            url_info = OrderedDict(Resource=path)
            url_info.update(url)
            collect_keys(url_info, 'url')
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
            pack = OrderedDict(Resource=path)
            for k, val in package.items():
                # prefix columns with "package__"
                nk = 'package__' + k

                if k in excluded_package_columns:
                    continue

                # process plain string values
                if not isinstance(val, (list, dict, OrderedDict)):
                    # prefix versions with a v to avoid spreadsheet tools to mistake
                    # a version for a number or date.
                    if k == 'version' and val:
                        val = 'v ' + val
                    pack[nk] = val

                # FIXME: we only keep for now some of the value collections
                elif not val or k not in ('authors', 'download_urls'):
                    continue

                pack[nk] = ''
                if k == 'authors':
                    # FIXME: we only keep the first author name for now
                    pack[nk] = val[0]['name']

                elif k == 'download_urls':
                    # FIXME: we only keep the first URL for now
                    pack[nk] = val[0]

            collect_keys(pack, 'package')
            yield pack
