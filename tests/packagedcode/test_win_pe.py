#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import io
import json
import os

from commoncode.testcase import FileBasedTesting
from packagedcode import win_pe


class TestWinPePeInfo(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    expected_file_suffix = '.expected.json'

    def get_results(self, test_file):
        return win_pe.pe_info(test_file)

    def check_win_pe(self, test_file, regen=False):
        expected_file = test_file + self.expected_file_suffix
        result = self.get_results(test_file)
        if regen:
            with open(expected_file, 'w') as out:
                json.dump(result, out, indent=2)

        with io.open(expected_file, encoding='utf-8') as expect:
            expected = json.load(expect)

        assert result == expected

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


class TestWinPeParseToPackage(TestWinPePeInfo):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    expected_file_suffix = '.package-expected.json'

    def get_results(self, test_file):
        return win_pe.parse(test_file).to_dict()
