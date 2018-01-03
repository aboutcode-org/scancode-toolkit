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

from commoncode.testcase import FileDrivenTesting
from scancode.cli_test_utils import run_scan_click


test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


def remove_variable_data(scan_result):
    """
    Remove variable fields from scan, such as date, version to ensure that the
    test data is stable.
    """
    for line in scan_result:
        header = line.get('header')
        if header:
            header.pop('scancode_version', None)
        for scanned_file in line.get('files', []):
            scanned_file.pop('date', None)


def check_jsonlines_scan(expected_file, result_file, regen=False):
    """
    Check the scan result_file JSON Lines results against the expected_file
    expected JSON results, which is a list of mappings, one per line. If regen
    is True the expected_file WILL BE overwritten with the results. This is
    convenient for updating tests expectations. But use with caution.
    """
    result = _load_jsonlines_result(result_file)
    remove_variable_data(result)

    if regen:
        with open(expected_file, 'wb') as reg:
            json.dump(result, reg, indent=2, separators=(',', ': '))
    expected = _load_json_result(expected_file)
    remove_variable_data(expected)

    assert expected == result


def _load_jsonlines_result(result_file):
    """
    Load the result file as utf-8 JSON Lines
    """
    with codecs.open(result_file, encoding='utf-8') as res:
        return [json.loads(line, object_pairs_hook=OrderedDict) for line in res]


def _load_json_result(result_file):
    """
    Load the result file as utf-8 JSON
    """
    with codecs.open(result_file, encoding='utf-8') as res:
        return json.load(res, object_pairs_hook=OrderedDict)


def test_jsonlines():
    test_dir = test_env.get_test_loc('json/simple')
    result_file = test_env.get_temp_file('jsonline')

    result = run_scan_click(['-i', '--format', 'jsonlines', test_dir, result_file])
    assert result.exit_code == 0
    assert 'Scanning done' in result.output

    expected = test_env.get_test_loc('json/simple-expected.jsonlines')
    check_jsonlines_scan(test_env.get_test_loc(expected), result_file, regen=False)
