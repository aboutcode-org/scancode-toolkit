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


def check_csvs(
        result_file, expected_file,
        ignore_keys=('date', 'file_type', 'mime_type',),
        regen=True):
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


def check_json(result, expected_file, regen=True):
    if regen:
        with codecs.open(expected_file, 'wb', encoding='utf-8') as reg:
            reg.write(json.dumps(result, indent=4, separators=(',', ': ')))
    expected = json.load(
        codecs.open(expected_file, encoding='utf-8'), object_pairs_hook=OrderedDict)
    assert expected == result


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
        expected_file = self.get_test_loc('json2csv/minimal.json-expected')
        check_json(result, expected_file)

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
        expected_file = self.get_test_loc('json2csv/full.json-expected')
        check_json(result, expected_file)

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
        check_csvs(result_file, expected_file, regen=True)

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
        expected_file = self.get_test_loc('json2csv/key_order.expected.json')
        check_json(result, expected_file)

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
        expected_file = self.get_test_loc('json2csv/package_license_value_null.json-expected')
        check_json(result, expected_file)

    def test_prefix_path(self):
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
        result = list(json2csv.flatten_scan(scan, headers, True))
        expected_file = self.get_test_loc('json2csv/minimal.json-prefix-path-expected')
        check_json(result, expected_file)


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
        check_csvs(result_file, expected_file, regen=True)
