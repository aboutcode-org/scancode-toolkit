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

from __future__ import absolute_import, print_function

import codecs
from collections import OrderedDict
import json
import os

from commoncode.testcase import FileBasedTesting

import json2csv


class TestJson2CSV(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'testdata')

    def test_scanc_as_list_minimal(self):
        test_json = self.get_test_loc('json2csv/minimal.json')
        scan = json2csv.load_scan(test_json)
        result = json2csv.scan_as_list(scan)
        expected = self.get_test_loc('json2csv/minimal.json-expected')
        expected = json.load(open(expected), object_pairs_hook=OrderedDict)
        assert expected == result

    def test_scanc_as_list_minimal_with_strip(self):
        test_json = self.get_test_loc('json2csv/minimal.json')
        scan = json2csv.load_scan(test_json)
        result = json2csv.scan_as_list(scan, strip=2)
        expected = self.get_test_loc('json2csv/minimal.json-strip-expected')
        expected = json.load(open(expected), object_pairs_hook=OrderedDict)
        assert expected == result

    def test_scanc_as_list_full(self):
        test_json = self.get_test_loc('json2csv/full.json')
        scan = json2csv.load_scan(test_json)
        result = json2csv.scan_as_list(scan)
        expected = self.get_test_loc('json2csv/full.json-expected')
        expected = json.load(open(expected), object_pairs_hook=OrderedDict)
        assert expected == result

    def test_json2csv_minimal(self):
        test_json = self.get_test_loc('json2csv/minimal.json')
        result_file = self.get_temp_file('.csv')
        json2csv.json_scan_to_csv(test_json, result_file)
        expected_file = self.get_test_loc('json2csv/minimal.csv')
        expected = codecs.open(expected_file, 'rb', encoding='utf-8').read()
        result = codecs.open(result_file, 'rb', encoding='utf-8').read()
        assert expected == result

    def test_key_ordering(self):
        test_json = self.get_test_loc('json2csv/key_order.json')
        scan = json2csv.load_scan(test_json)
        result = json2csv.scan_as_list(scan)

        expected = [
         OrderedDict([
            (u'Resource', u'/tests/extractcode/test_patch.py'),
            (u'info_type', u'file'),
            (u'info_name', u'test_patch.py'),
            (u'info_extension', u'.py'),
            (u'info_date', u'2015-12-08'),
            (u'info_size', 72347),
            (u'info_sha1', u'bc1dc65b7d6b88709ce170291f93cd255bda8ffa'),
            (u'info_md5', u'25edeca9fbedd5b53e7e70af0ab0140a'),
            (u'info_files_count', None),
            (u'info_mime_type', u'text/x-python'),
            (u'info_file_type', u'Python script, ASCII text executable'),
            (u'info_programming_language', u'Python'),
            (u'info_is_binary', None),
            (u'info_is_text', True),
            (u'info_is_archive', None),
            (u'info_is_media', None),
            (u'info_is_source', True),
            (u'info_is_script', True),
        ]),

         OrderedDict([
            (u'Resource', u'/tests/extractcode/test_sevenzip.py'),
            (u'info_type', u'file'),
            (u'info_name', u'test_sevenzip.py'),
            (u'info_extension', u'.py'),
            (u'info_date', u'2015-12-08'),
            (u'info_size', 8773),
            (u'info_sha1', u'e6ece461dc3af299ff4684081b9010a87fcd82f0'),
            (u'info_md5', u'166bde096f06b5fa4ea962f94f217e0b'),
            (u'info_files_count', None),
            (u'info_mime_type', u'text/x-python'),
            (u'info_file_type', u'Python script, ASCII text executable, with very long lines'),
            (u'info_programming_language', u'Python'),
            (u'info_is_binary', None),
            (u'info_is_text', True),
            (u'info_is_archive', None),
            (u'info_is_media', None),
            (u'info_is_source', True),
            (u'info_is_script', True),
        ])
        ]
        assert expected == result

    def test_json_with_no_keys_does_not_error_out(self):
        # this scan has no results at all
        test_json = self.get_test_loc('json2csv/no_keys.json')
        scan = json2csv.load_scan(test_json)
        result = json2csv.scan_as_list(scan)
        assert [] == result

    def test_can_process_html_app_and_regular_json_the_same_way(self):
        test_html = self.get_test_loc('json2csv/format_html_app_data.json')
        test_json = self.get_test_loc('json2csv/format_json_scan.json')
        assert json2csv.load_scan(test_html) == json2csv.load_scan(test_json)
