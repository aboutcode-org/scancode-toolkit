#
# Copyright (c) 2018 nexB Inc. and others. All rights reserved.
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

from plugincode.output import output_impl
from plugincode.output import OutputPlugin
from scancode import CommandLineOption
from scancode import FileOptionType
from scancode import OUTPUT_GROUP


@output_impl
class CsvOutput(OutputPlugin):

    options = [
        CommandLineOption(('--csv',),
            type=FileOptionType(mode='wb', lazy=False),
            metavar='FILE',
            help='Write scan output as CSV to FILE.',
            help_group=OUTPUT_GROUP,
            sort_order=30),
    ]

    def is_enabled(self, csv, **kwargs):
        return csv

    def process_codebase(self, codebase, csv, **kwargs):
        results = self.get_results(codebase, **kwargs)
        write_csv(results, csv)


def write_csv(results, output_file):
    # FIXMe: this is reading all in memory
    results = list(results)

    headers = OrderedDict([
        ('info', []),
        ('license', []),
        ('copyright', []),
        ('email', []),
        ('url', []),
        ('package', []),
    ])

    # note: FIXME: headers are collected as a side effect and this is not great
    rows = list(flatten_scan(results, headers))

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
                          if not isinstance(v, (list, dict))))
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
                        if mrk in ('match_coverage', 'rule_relevance'):
                            # normalize the string representation of this number
                            mrv = '{:.2f}'.format(mrv)
                        mrk = 'matched_rule__' + mrk
                        lic[mrk] = mrv
                    continue

                if k == 'score':
                    # normalize score with two decimal values
                    val = '{:.2f}'.format(val)

                # lines are present in multiple scans: keep their column name as
                # not scan-specific. Prefix othe columns with license__
                if k not in ('start_line', 'end_line',):
                    k = 'license__' + k
                lic[k] = val
            collect_keys(lic, 'license')
            yield lic

        for copyr in scanned_file.get('copyrights', []):
            inf = OrderedDict(Resource=path)
            inf['copyright'] = copyr['value']
            inf['start_line'] = copyr['start_line']
            inf['end_line'] = copyr['start_line']
            collect_keys(inf, 'copyright')
            yield inf

        for copyr in scanned_file.get('holders', []):
            inf = OrderedDict(Resource=path)
            inf['copyright_holder'] = copyr['value']
            inf['start_line'] = copyr['start_line']
            inf['end_line'] = copyr['start_line']
            collect_keys(inf, 'copyright')
            yield inf

        for copyr in scanned_file.get('authors', []):
            inf = OrderedDict(Resource=path)
            inf['author'] = copyr['value']
            inf['start_line'] = copyr['start_line']
            inf['end_line'] = copyr['start_line']
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

        for package in scanned_file.get('packages', []):
            flat = flatten_package(package, path)
            collect_keys(flat, 'package')
            yield flat


def flatten_package(_package, path, prefix='package__'):

    # exclude some columns for now that contain list of items
    excluded_package_columns = {
        # list of strings
        'download_checksums',
        'keywords',
        # list of dicts
        'parties',
        'dependencies',

        # comming from a match

        # we have license_expression we do not need more
        'licenses_summary',
        'licenses',
        'license_choices_expression',
        'license_choices',

        'api_url',
        'uuid',
        'sha1',
        'md5',
        'owner',

        'reference_notes',
        'project',
        'codescan_identifier',
        'is_license_notice',
        'is_copyright_notice',
        'is_notice_in_codebase',
        # 'notice_filename',
        # 'notice_url',
        'website_terms_of_use',
        'is_active',
        'curation_level',
        'completion_level',
        'guidance',
        'admin_notes',
        'ip_sensitivity_approved',
        'affiliate_obligations',
        'affiliate_obligation_triggers',
        'concluded_license',
        'legal_comments',
        'legal_reviewed',
        'approval_reference',
        'distribution_formats_allowed',
        'acceptable_linkage',
        'export_restrictions',
        'approved_download_location',
        'approved_community_interaction',
        'urn',
        'created_date',
        'last_modified_date',
        'dataspace',
        'external_references',
        'display_name',
        'notes',
        'origin_date',
        'sublicense_allowed',
    }

    pack = OrderedDict(Resource=path)
    for k, val in _package.items():
        # FIXME: we only keep for now some of the value collections
        if k in excluded_package_columns:
            continue
        # prefix columns with "package__"
        nk = prefix + k

        if k == 'version':
            if val:
                # prefix versions with a v to avoid spreadsheet tools to mistake
                # a version for a number or date.
                val = 'v ' + val
                pack[nk] = val
            else:
                pack[nk] = ''
            continue

        # these may come from a match

        if k == 'components' and val and isinstance(val, list):
            for compo in val:
                for compo_key, compo_val in compo.items():
                    if compo_key in excluded_package_columns:
                        continue

                    compo_nk = nk + '__' + compo_key

                    if compo_val is None:
                        pack[compo_nk] = ''
                        continue

                    if not isinstance(compo_val, basestring):
                        compo_val = repr(compo_val)
                    existing = pack.get(compo_nk) or []
                    pack[compo_nk] = ' \n'.join(existing + [compo_val])
            continue

        if k == 'match':
            for mk, mval in val.items():
                match_nk = nk + '__' + mk
                pack[match_nk] = mval
            continue

        # everything else
        # collect all the keys

        pack[nk] = ''

        if isinstance(val, basestring):
            pack[nk] = val
        else:
            # Use repr if not a string
            if val:
                pack[nk] = repr(val)

    return pack
