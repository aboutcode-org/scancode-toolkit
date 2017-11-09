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
from __future__ import unicode_literals

from collections import OrderedDict
import codecs
import json
import os

from commoncode.testcase import FileBasedTesting
from packagedcode import win_pe


class TestWinPe(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def check_win_pe(self, test_file, expected_file, regen=False):
        result = win_pe.pe_info(test_file, include_extra_data=True)
        if regen:
            with codecs.open(expected_file, 'wb', encoding='UTF-8') as out:
                json.dump(result, out, indent=2)

        with codecs.open(expected_file, encoding='utf-8') as expect:
            expected = json.load(expect, object_pairs_hook=OrderedDict)
        assert expected == dict(result)

    def test_win_pe_ctypes_test_pyd(self):
        test_file = self.get_test_loc('win_pe/_ctypes_test.pyd')
        expected_file = self.get_test_loc('win_pe/_ctypes_test.pyd.expected.json')
        self.check_win_pe(test_file, expected_file)

    def test_win_pe_euc_jp_so(self):
        test_file = self.get_test_loc('win_pe/euc-jp.so')
        expected_file = self.get_test_loc('win_pe/euc-jp.so.expected.json')
        self.check_win_pe(test_file, expected_file)

    def test_win_pe_file_exe(self):
        test_file = self.get_test_loc('win_pe/file.exe')
        expected_file = self.get_test_loc('win_pe/file.exe.expected.json')
        self.check_win_pe(test_file, expected_file)

    def test_win_pe_libiconv2_dll(self):
        test_file = self.get_test_loc('win_pe/libiconv2.dll')
        expected_file = self.get_test_loc('win_pe/libiconv2.dll.expected.json')
        self.check_win_pe(test_file, expected_file)

    def test_win_pe_libintl3_dll(self):
        test_file = self.get_test_loc('win_pe/libintl3.dll')
        expected_file = self.get_test_loc('win_pe/libintl3.dll.expected.json')
        self.check_win_pe(test_file, expected_file)

    def test_win_pe_microsoft_practices_enterpriselibrary_caching_dll(self):
        test_file = self.get_test_loc('win_pe/Microsoft.Practices.EnterpriseLibrary.Caching.dll')
        expected_file = self.get_test_loc('win_pe/Microsoft.Practices.EnterpriseLibrary.Caching.dll.expected.json')
        self.check_win_pe(test_file, expected_file)

    def test_win_pe_tre4_dll(self):
        test_file = self.get_test_loc('win_pe/tre4.dll')
        expected_file = self.get_test_loc('win_pe/tre4.dll.expected.json')
        self.check_win_pe(test_file, expected_file)

    def test_win_pe_zlib1_dll(self):
        test_file = self.get_test_loc('win_pe/zlib1.dll')
        expected_file = self.get_test_loc('win_pe/zlib1.dll.expected.json')
        self.check_win_pe(test_file, expected_file)

    def test_win_pe_Moq_Silverlight_dll(self):
        test_file = self.get_test_loc('win_pe/Moq.Silverlight.dll')
        expected_file = self.get_test_loc('win_pe/Moq.Silverlight.dll.expected.json')
        self.check_win_pe(test_file, expected_file)
