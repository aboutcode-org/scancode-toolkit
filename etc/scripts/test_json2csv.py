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

import unicodecsv

from commoncode.testcase import FileBasedTesting

import json2csv


def load_csv(location):
    """
    Load a CSV file at location and return a tuple of (field names, list of rows as
    mappings field->value).
    """
    with codecs.open(location, 'rb', encoding='utf-8') as csvin:
        reader = unicodecsv.DictReader(csvin)
        fields = reader.fieldnames
        values = sorted(reader)
        return fields, values


def check_csvs(result_file, expected_file, ignore_keys=('date', 'file_type', 'mime_type',), regen=False):
    """
    Load and compare two CSVs.
    `ignore_keys` is a tuple of keys that will be ignored in the comparisons.
    """
    result_fields, results = load_csv(result_file)
    if regen:
        import shutil
        shutil.copy2(result_file, expected_file)
    expected_fields, expected = load_csv(expected_file)
    assert expected_fields == result_fields
    # then check results line by line for more compact results
    for exp, res in zip(sorted(expected), sorted(results)):
        for ign in ignore_keys:
            exp.pop(ign, None)
            res.pop(ign, None)
        assert exp == res


class TestJson2CSV(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'testdata')

    def test_flatten_scan_minimal(self):
        test_json = self.get_test_loc('json2csv/minimal.json')
        scan = json2csv.load_scan(test_json)
        headers = OrderedDict([
            ('info', []),
            ('license', []),
            ('copyright', []),
            ('email', []),
            ('url', []),
            ('package', []),
            ])
        result = list(json2csv.flatten_scan(scan, headers))
        expected_headers = OrderedDict([
            ('info', ['Resource', 'scan_errors']),
            ('license', ['license__key', 'license__score', 'license__short_name',
                          'license__category', 'license__owner', 'license__homepage_url',
                          'license__text_url', 'license__dejacode_url',
                          'license__spdx_license_key', 'license__spdx_url',
                          'start_line', 'end_line']),
            ('copyright', ['copyright', 'copyright_holder']),
            ('email', []), ('url', []),
            ('package', [])
        ])
        assert expected_headers == headers

        expected = self.get_test_loc('json2csv/minimal.json-expected')
        expected = json.load(codecs.open(expected, encoding='utf-8'), object_pairs_hook=OrderedDict)
        assert expected == result

    def test_flatten_scan_full(self):
        test_json = self.get_test_loc('json2csv/full.json')
        scan = json2csv.load_scan(test_json)
        headers = OrderedDict([
            ('info', []),
            ('license', []),
            ('copyright', []),
            ('email', []),
            ('url', []),
            ('package', []),
            ])
        result = list(json2csv.flatten_scan(scan, headers))
        expected_headers = OrderedDict([
            ('info', ['Resource', 'type', 'name', 'extension', 'date', 'size',
                       'sha1', 'md5', 'files_count', 'mime_type', 'file_type',
                       'programming_language', 'is_binary', 'is_text',
                       'is_archive', 'is_media', 'is_source', 'is_script',
                       'scan_errors']),
            ('license', ['license__key', 'license__score', 'license__short_name',
                          'license__category', 'license__owner', 'license__homepage_url',
                          'license__text_url', 'license__dejacode_url',
                          'license__spdx_license_key', 'license__spdx_url',
                          'start_line', 'end_line']),
            ('copyright', ['copyright', 'copyright_holder', 'author']),
            ('email', ['email']),
            ('url', ['url']),
            ('package', ['package__type', 'package__name', 'package__version',
                          'package__primary_language', 'package__summary',
                          'package__description', 'package__authors',
                          'package__homepage_url', 'package__notes',
                          'package__download_urls', 'package__bug_tracking_url',
                          'package__vcs_repository', 'package__copyright_top_level',
                          'package__copyrights', 'package__asserted_licenses'])])
        assert expected_headers == headers
        expected = self.get_test_loc('json2csv/full.json-expected')
        expected = json.load(codecs.open(expected, encoding='utf-8'), object_pairs_hook=OrderedDict)
        assert expected == result

    def test_json2csv_minimal(self):
        test_json = self.get_test_loc('json2csv/minimal.json')
        result_file = self.get_temp_file('.csv')
        with open(result_file, 'wb') as rf:
            json2csv.json_scan_to_csv(test_json, rf)
        expected_file = self.get_test_loc('json2csv/minimal.csv')
        check_csvs(result_file, expected_file)

    def test_json2csv_full(self):
        test_json = self.get_test_loc('json2csv/full.json')
        result_file = self.get_temp_file('.csv')
        with open(result_file, 'wb') as rf:
            json2csv.json_scan_to_csv(test_json, rf)
        expected_file = self.get_test_loc('json2csv/full.csv')
        check_csvs(result_file, expected_file)

    def test_key_ordering(self):
        test_json = self.get_test_loc('json2csv/key_order.json')
        scan = json2csv.load_scan(test_json)
        headers = OrderedDict([
            ('info', []),
            ('license', []),
            ('copyright', []),
            ('email', []),
            ('url', []),
            ('package', []),
            ])
        result = list(json2csv.flatten_scan(scan, headers))
        expected_headers = OrderedDict([
            ('info', ['Resource', 'type', 'name', 'extension', 'date',
                       'size', 'sha1', 'md5', 'files_count', 'mime_type',
                       'file_type', 'programming_language', 'is_binary',
                       'is_text', 'is_archive', 'is_media', 'is_source',
                       'is_script', 'scan_errors']),
            ('license', []),
            ('copyright', []),
            ('email', []),
            ('url', []),
            ('package', [])
        ])
        assert expected_headers == headers

        expected = [
            OrderedDict([
                ('Resource', '/srp_vfy.c'),
                ('type', 'file'),
                ('name', 'srp_vfy.c'),
                ('extension', '.c'),
                ('date', '2016-11-10'),
                ('size', 17428),
                ('sha1', 'fa622c0499367a7e551d935c4c7394d5dfc31b26'),
                ('md5', '4e02508d6433c8893e72fd521f36b37a'),
                ('files_count', None),
                ('mime_type', 'text/plain'),
                ('file_type', 'ASCIItext'),
                ('programming_language', 'C'),
                ('is_binary', None),
                ('is_text', True),
                ('is_archive', None),
                ('is_media', None),
                ('is_source', True),
                ('is_script', None),
                ('scan_errors', '')
            ]),
            OrderedDict([
                ('Resource', '/srp_lib.c'),
                ('type', 'file'),
                ('name', 'srp_lib.c'),
                ('extension', '.c'),
                ('date', '2016-11-10'),
                ('size', 7302),
                ('sha1', '624360fb75baf8f3498f6d70f7b3c66ed03bfa6c'),
                ('md5', 'b5c2f56afc2477d5a1768f97b314fe0f'),
                ('files_count', None),
                ('mime_type', 'text/x-c'),
                ('file_type', 'Csource, ASCIItext'),
                ('programming_language', 'C'),
                ('is_binary', None),
                ('is_text', True),
                ('is_archive', None),
                ('is_media', None),
                ('is_source', True),
                ('is_script', None),
                ('scan_errors', '')
            ]),
            OrderedDict([
                ('Resource', '/build.info'),
                ('type', 'file'),
                ('name', 'build.info'),
                ('extension', '.info'),
                ('date', '2016-11-10'),
                ('size', 65),
                ('sha1', '994b9ec16ec11f96a1dfade472ecec8c5c837ab4'),
                ('md5', 'eaacdd82c253a8967707c431cca6227e'),
                ('files_count', None),
                ('mime_type', 'text/plain'),
                ('file_type', 'ASCIItext'),
                ('programming_language', None),
                ('is_binary', None),
                ('is_text', True),
                ('is_archive', None),
                ('is_media', None),
                ('is_source', None),
                ('is_script', None),
                ('scan_errors', '')
            ])
        ]

        assert expected == result

    def test_json_with_no_keys_does_not_error_out(self):
        # this scan has no results at all
        test_json = self.get_test_loc('json2csv/no_keys.json')
        scan = json2csv.load_scan(test_json)
        headers = OrderedDict([
            ('info', []),
            ('license', []),
            ('copyright', []),
            ('email', []),
            ('url', []),
            ('package', []),
            ])
        result = list(json2csv.flatten_scan(scan, headers))
        expected_headers = OrderedDict([
            ('info', []),
            ('license', []),
            ('copyright', []),
            ('email', []),
            ('url', []),
            ('package', []),
            ])
        assert expected_headers == headers
        assert [] == result

    def test_can_process_html_app_and_regular_json_the_same_way(self):
        test_html = self.get_test_loc('json2csv/minimal_html_app_data.json')
        test_json = self.get_test_loc('json2csv/minimal.json')
        assert json2csv.load_scan(test_html) == json2csv.load_scan(test_json)

    def test_can_process_package_license_when_license_value_is_null(self):
        test_json = self.get_test_loc('json2csv/package_license_value_null.json')
        scan = json2csv.load_scan(test_json)
        headers = OrderedDict([
            ('info', []),
            ('license', []),
            ('copyright', []),
            ('email', []),
            ('url', []),
            ('package', []),
            ])
        result = list(json2csv.flatten_scan(scan, headers))
        expected_headers = OrderedDict([
            ('info', ['Resource', 'scan_errors']),
            ('license', ['license__key', 'license__score', 'license__short_name', 'license__category', 'license__owner', 'license__homepage_url', 'license__text_url', 'license__dejacode_url', 'license__spdx_license_key', 'license__spdx_url', 'start_line', 'end_line']), ('copyright', ['copyright', 'copyright_holder']),
            ('email', []),
            ('url', []),
            ('package', ['package__asserted_licenses'])])
        assert expected_headers == headers
        expected = self.get_test_loc('json2csv/package_license_value_null.json-expected')
        expected = json.load(codecs.open(expected, encoding='utf-8'), object_pairs_hook=OrderedDict)
        assert expected == result

class TestJson2CSVWithLiveScans(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'testdata')

    def test_can_process_scan_from_json_scan(self):
        import scancode
        from commoncode.command import execute
        test_dir = self.get_test_loc('livescan/scan')
        json_file = self.get_temp_file('json')
        scan_cmd = os.path.join(scancode.root_dir, 'scancode')
        rc, _stdout, _stderr = execute(scan_cmd,
            ['-clip', '--email', '--url', '--strip-root', '--format', 'json', test_dir, json_file])
        assert rc == 0
        result_file = self.get_temp_file('.csv')
        with open(result_file, 'wb') as rf:
            json2csv.json_scan_to_csv(json_file, rf)
        expected_file = self.get_test_loc('livescan/expected.csv')
        check_csvs(result_file, expected_file)
