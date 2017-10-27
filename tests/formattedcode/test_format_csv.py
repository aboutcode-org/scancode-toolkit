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

import codecs
from collections import OrderedDict
import json
import os

import unicodecsv

from commoncode.testcase import FileDrivenTesting
from scancode.cli_test_utils import run_scan_click
from scancode.cli_test_utils import run_scan_plain

from formattedcode.format_csv import flatten_scan


test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


def load_scan(json_input):
    """
    Return a list of scan results loaded from a json_input, either in
    ScanCode standard JSON format or the data.json html-app format.
    """
    with codecs.open(json_input, 'rb', encoding='utf-8') as jsonf:
        scan = jsonf.read()

    scan_results = json.loads(scan, object_pairs_hook=OrderedDict)
    scan_results = scan_results['files']
    return scan_results


def check_json(result, expected_file, regen=False):
    if regen:
        with codecs.open(expected_file, 'wb', encoding='utf-8') as reg:
            reg.write(json.dumps(result, indent=4, separators=(',', ': ')))
    expected = json.load(
        codecs.open(expected_file, encoding='utf-8'), object_pairs_hook=OrderedDict)
    assert expected == result


def check_csvs(result_file, expected_file,
               ignore_keys=('date', 'file_type', 'mime_type',),
               regen=False):
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


def test_flatten_scan_minimal():
    test_json = test_env.get_test_loc('csv/flatten_scan/minimal.json')
    scan = load_scan(test_json)
    headers = OrderedDict([
        ('info', []),
        ('license', []),
        ('copyright', []),
        ('email', []),
        ('url', []),
        ('package', []),
        ])
    result = list(flatten_scan(scan, headers))
    expected_file = test_env.get_test_loc('csv/flatten_scan/minimal.json-expected')
    check_json(result, expected_file)


def test_flatten_scan_full():
    test_json = test_env.get_test_loc('csv/flatten_scan/full.json')
    scan = load_scan(test_json)
    headers = OrderedDict([
        ('info', []),
        ('license', []),
        ('copyright', []),
        ('email', []),
        ('url', []),
        ('package', []),
        ])
    result = list(flatten_scan(scan, headers))
    expected_file = test_env.get_test_loc('csv/flatten_scan/full.json-expected')
    check_json(result, expected_file)


def test_flatten_scan_key_ordering():
    test_json = test_env.get_test_loc('csv/flatten_scan/key_order.json')
    scan = load_scan(test_json)
    headers = OrderedDict([
        ('info', []),
        ('license', []),
        ('copyright', []),
        ('email', []),
        ('url', []),
        ('package', []),
        ])
    result = list(flatten_scan(scan, headers))
    expected_file = test_env.get_test_loc('csv/flatten_scan/key_order.expected.json')
    check_json(result, expected_file)


def test_flatten_scan_with_no_keys_does_not_error_out():
    # this scan has no results at all
    test_json = test_env.get_test_loc('csv/flatten_scan/no_keys.json')
    scan = load_scan(test_json)
    headers = OrderedDict([
        ('info', []),
        ('license', []),
        ('copyright', []),
        ('email', []),
        ('url', []),
        ('package', []),
        ])
    result = list(flatten_scan(scan, headers))
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


def test_flatten_scan_can_process_package_license_when_license_value_is_null():
    test_json = test_env.get_test_loc('csv/flatten_scan/package_license_value_null.json')
    scan = load_scan(test_json)
    headers = OrderedDict([
        ('info', []),
        ('license', []),
        ('copyright', []),
        ('email', []),
        ('url', []),
        ('package', []),
        ])
    result = list(flatten_scan(scan, headers))
    expected_file = test_env.get_test_loc('csv/flatten_scan/package_license_value_null.json-expected')
    check_json(result, expected_file)


def test_csv_minimal():
    test_dir = test_env.get_test_loc('csv/srp')
    result_file = test_env.get_temp_file('csv')
    expected_file = test_env.get_test_loc('csv/srp.csv')
    result = run_scan_click(['--copyright', '--format', 'csv', test_dir, result_file])
    assert result.exit_code == 0
    assert 'Scanning done' in result.output
    check_csvs(result_file, expected_file)


def test_csv_tree():
    test_dir = test_env.get_test_loc('csv/tree/scan')
    result_file = test_env.get_temp_file('csv')
    expected_file = test_env.get_test_loc('csv/tree/expected.csv')
    result = run_scan_click(['--copyright', '--format', 'csv', test_dir, result_file])
    assert result.exit_code == 0
    check_csvs(result_file, expected_file)


def test_can_process_live_scan_with_all_options():
    test_dir = test_env.get_test_loc('csv/livescan/scan')
    result_file = test_env.get_temp_file('csv')
    rc, stdout, stderr = run_scan_plain(
        ['-clip', '--email', '--url', '--strip-root', '--format', 'csv',
         test_dir, result_file])
    try:
        assert rc == 0
    except:
        print(stdout, stderr)
        print(stdout, stderr)
        raise

    expected_file = test_env.get_test_loc('csv/livescan/expected.csv')
    check_csvs(result_file, expected_file, regen=False)
