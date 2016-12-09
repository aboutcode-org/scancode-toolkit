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
        result = list(json2csv.flatten_scan(scan))
        expected = self.get_test_loc('json2csv/minimal.json-expected')
        expected = json.load(open(expected), object_pairs_hook=OrderedDict)
        assert expected == result

    def test_scanc_as_list_full(self):
        test_json = self.get_test_loc('json2csv/full.json')
        scan = json2csv.load_scan(test_json)
        result = list(json2csv.flatten_scan(scan))
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

    def test_json2csv_full(self):
        test_json = self.get_test_loc('json2csv/full.json')
        result_file = self.get_temp_file('.csv')
        json2csv.json_scan_to_csv(test_json, result_file)
        expected_file = self.get_test_loc('json2csv/full.csv')
        expected = codecs.open(expected_file, 'rb', encoding='utf-8').read()
        result = codecs.open(result_file, 'rb', encoding='utf-8').read()
        assert expected == result

    def test_key_ordering(self):
        test_json = self.get_test_loc('json2csv/key_order.json')
        scan = json2csv.load_scan(test_json)
        result = list(json2csv.flatten_scan(scan))

        expected = [
            OrderedDict([
                ('Resource', u'/code/srp_vfy.c'),
                (u'type', u'file'),
                (u'name', u'srp_vfy.c'),
                (u'extension', u'.c'),
                (u'date', u'2016-11-10'),
                (u'size', 17428),
                (u'sha1', u'fa622c0499367a7e551d935c4c7394d5dfc31b26'),
                (u'md5', u'4e02508d6433c8893e72fd521f36b37a'),
                (u'files_count', None),
                (u'mime_type', u'text/plain'),
                (u'file_type', u'ASCIItext'),
                (u'programming_language', u'C'),
                (u'is_binary', None),
                (u'is_text', True),
                (u'is_archive', None),
                (u'is_media', None),
                (u'is_source', True),
                (u'is_script', None)
            ]),
            OrderedDict([
                ('Resource', u'/code/srp_vfy.c'),
                ('scan_errors', '')
            ]),
            OrderedDict([
                ('Resource', u'/code/srp_lib.c'),
                (u'type', u'file'),
                (u'name', u'srp_lib.c'),
                (u'extension', u'.c'),
                (u'date', u'2016-11-10'),
                (u'size', 7302),
                (u'sha1', u'624360fb75baf8f3498f6d70f7b3c66ed03bfa6c'),
                (u'md5', u'b5c2f56afc2477d5a1768f97b314fe0f'),
                (u'files_count', None),
                (u'mime_type', u'text/x-c'),
                (u'file_type', u'Csource, ASCIItext'),
                (u'programming_language', u'C'),
                (u'is_binary', None),
                (u'is_text', True),
                (u'is_archive', None),
                (u'is_media', None),
                (u'is_source', True),
                (u'is_script', None)
            ]),
            OrderedDict([
                ('Resource', u'/code/srp_lib.c'),
                ('scan_errors', '')
            ]),
            OrderedDict([
                ('Resource', u'/code/build.info'),
                (u'type', u'file'),
                (u'name', u'build.info'),
                (u'extension', u'.info'),
                (u'date', u'2016-11-10'),
                (u'size', 65),
                (u'sha1', u'994b9ec16ec11f96a1dfade472ecec8c5c837ab4'),
                (u'md5', u'eaacdd82c253a8967707c431cca6227e'),
                (u'files_count', None),
                (u'mime_type', u'text/plain'),
                (u'file_type', u'ASCIItext'),
                (u'programming_language', None),
                (u'is_binary', None),
                (u'is_text', True),
                (u'is_archive', None),
                (u'is_media', None),
                (u'is_source', None),
                (u'is_script', None)
            ]),
            OrderedDict([
                ('Resource', u'/code/build.info'),
                ('scan_errors', '')
            ])
        ]

        assert expected == result

    def test_json_with_no_keys_does_not_error_out(self):
        # this scan has no results at all
        test_json = self.get_test_loc('json2csv/no_keys.json')
        scan = json2csv.load_scan(test_json)
        result = list(json2csv.flatten_scan(scan))
        assert [] == result

    def test_can_process_html_app_and_regular_json_the_same_way(self):
        test_html = self.get_test_loc('json2csv/minimal_html_app_data.json')
        test_json = self.get_test_loc('json2csv/minimal.json')
        assert json2csv.load_scan(test_html) == json2csv.load_scan(test_json)
