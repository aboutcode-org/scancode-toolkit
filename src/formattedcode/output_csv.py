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

import saneyaml
from six import string_types
import unicodecsv

from commoncode import compat
from plugincode.output import output_impl
from plugincode.output import OutputPlugin
from scancode import CommandLineOption
from scancode import FileOptionType
from scancode import OUTPUT_GROUP


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
        return logger.debug(' '.join(isinstance(a, string_types)
                                     and a or repr(a) for a in args))


@output_impl
class CsvOutput(OutputPlugin):

    options = [
        CommandLineOption(('--csv',),
            type=FileOptionType(mode='wb', lazy=True),
            metavar='FILE',
            help='Write scan output as CSV to FILE.',
            help_group=OUTPUT_GROUP,
            sort_order=30),
    ]

    def is_enabled(self, csv, **kwargs):
        return csv

    def process_codebase(self, codebase, csv, **kwargs):
        results = self.get_files(codebase, **kwargs)
        write_csv(results, csv)


def write_csv(results, output_file):
    # FIXMe: this is reading all in memory
    results = list(results)

    headers = OrderedDict([
        ('info', []),
        ('license_expression', []),
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

        # removing any slash at the begening of the path
        path = path.lstrip('/')

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

        for lic_exp in scanned_file.get('license_expressions', []):
            inf = OrderedDict(Resource=path, license_expression=lic_exp)
            collect_keys(inf, 'license_expression')
            yield inf

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
                        else:
                            mrv = pretty(mrv)
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


def pretty(data):
    """
    Return a unicode text pretty representation of data (as YAML or else) if
    data is a sequence or mapping or the data as-is otherwise
    """
    if not data:
        return None
    seqtypes = list, tuple
    maptypes = OrderedDict, dict
    coltypes = seqtypes + maptypes
    if isinstance(data, seqtypes):
        if len(data) == 1 and isinstance(data[0], string_types):
            return data[0].strip()
    if isinstance(data, coltypes):
        return saneyaml.dump(
            data, indent=2, encoding='utf-8').decode('utf-8').strip()
    return data


def get_package_columns(_columns=set()):
    """
    Return (and cache in_columns) a set of package column names included in the
    CSV output.
    Some columsn are excluded for now such as lists of mappings: these do not
    serialize well to CSV
    """
    if _columns:
        return _columns

    from packagedcode.models import Package

    # exclude some columns for now that contain list of items
    excluded_columns = {
        # list of strings
        'keywords',
        # list of dicts
        'parties',
        'dependencies',
        'source_packages',
    }

    # some extra columns for components
    extra_columns = [
        'components',
        'owner_name',
        'reference_notes',
        'description',
        'notice_filename',
        'notice_url',
    ]

    fields = Package.fields() + extra_columns
    _columns = set(f for f in fields if f not in excluded_columns)
    return _columns


def flatten_package(_package, path, prefix='package__'):

    # known package columns

    package_columns = get_package_columns()

    pack = OrderedDict(Resource=path)
    for k, val in _package.items():
        if k not in package_columns:
            continue

        # prefix columns with "package__"
        nk = prefix + k

        if k == 'version':
            val = val or ''
            if val and not val.lower().startswith('v'):
                # prefix versions with a v to avoid spreadsheet tools to mistake
                # a version for a number or date when reading CSVs (common with
                # Excel and LibreOffice).
                val = 'v ' + val
            pack[nk] = val
            continue

        # these may come from a component matched
        if k == 'components' and val and isinstance(val, list):
            for component in val:
                for component_key, component_val in component.items():
                    if component_key not in package_columns:
                        continue

                    component_new_key = nk + '__' + component_key

                    if component_val is None:
                        pack[component_new_key] = ''
                        continue

                    if isinstance(component_val, list):
                        component_val = '\n'.join(component_val)

                    if not isinstance(component_val, compat.unicode):
                        component_val = repr(component_val)

                    existing = pack.get(component_new_key) or []
                    if not isinstance(existing, list):
                        existing = [existing]

                    if TRACE:
                        logger_debug('component_new_key:', component_new_key, 'existing:', type(existing), repr(existing))
                        logger_debug('component_key:', component_key, 'component_val:', type(component_val), repr(component_val))

                    pack[component_new_key] = ' \n'.join(existing + [component_val])
            continue

        # everything else

        pack[nk] = ''

        if isinstance(val, compat.unicode):
            pack[nk] = val
        else:
            # Use repr if not a string
            if val:
                pack[nk] = pretty(val)

    return pack
