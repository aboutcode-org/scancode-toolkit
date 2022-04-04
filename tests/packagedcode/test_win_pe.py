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
from scancode_config import REGEN_TEST_FIXTURES


class TestWinPePeInfo(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    expected_file_suffix = '.expected.json'

    def get_results(self, test_file):
        return win_pe.pe_info(test_file)

    def check_win_pe(self, test_file, regen=REGEN_TEST_FIXTURES):
        expected_file = test_file + self.expected_file_suffix
        result = self.get_results(test_file)
        if regen:
            with open(expected_file, 'w') as out:
                json.dump(result, out, indent=2)

        with io.open(expected_file, encoding='utf-8') as expect:
            expected = json.load(expect)

        assert result == expected

    def test_gosum_is_package_data_file(self):
        test_file = self.get_test_loc('win_pe/_ctypes_test.pyd')
        assert win_pe.WindowsExecutableHandler.is_datafile(test_file)

    def test_win_pe_ctypes_test_pyd(self):
        test_file = self.get_test_loc('win_pe/_ctypes_test.pyd')
        self.check_win_pe(test_file, regen=REGEN_TEST_FIXTURES)

    def test_win_pe_euc_jp_so(self):
        test_file = self.get_test_loc('win_pe/euc-jp.so')
        self.check_win_pe(test_file, regen=REGEN_TEST_FIXTURES)

    def test_win_pe_file_exe(self):
        test_file = self.get_test_loc('win_pe/file.exe')
        self.check_win_pe(test_file, regen=REGEN_TEST_FIXTURES)

    def test_win_pe_libiconv2_dll(self):
        test_file = self.get_test_loc('win_pe/libiconv2.dll')
        self.check_win_pe(test_file, regen=REGEN_TEST_FIXTURES)

    def test_win_pe_libintl3_dll(self):
        test_file = self.get_test_loc('win_pe/libintl3.dll')
        self.check_win_pe(test_file, regen=REGEN_TEST_FIXTURES)

    def test_win_pe_microsoft_practices_enterpriselibrary_caching_dll(self):
        test_file = self.get_test_loc('win_pe/Microsoft.Practices.EnterpriseLibrary.Caching.dll')
        self.check_win_pe(test_file, regen=REGEN_TEST_FIXTURES)

    def test_win_pe_tre4_dll(self):
        test_file = self.get_test_loc('win_pe/tre4.dll')
        self.check_win_pe(test_file, regen=REGEN_TEST_FIXTURES)

    def test_win_pe_zlib1_dll(self):
        test_file = self.get_test_loc('win_pe/zlib1.dll')
        self.check_win_pe(test_file, regen=REGEN_TEST_FIXTURES)

    def test_win_pe_Moq_Silverlight_dll(self):
        test_file = self.get_test_loc('win_pe/Moq.Silverlight.dll')
        self.check_win_pe(test_file, regen=REGEN_TEST_FIXTURES)

    def test_win_pe_clfs_sys_mui(self):
        test_file = self.get_test_loc('win_pe/clfs.sys.mui')
        self.check_win_pe(test_file, regen=REGEN_TEST_FIXTURES)

    def test_win_pe_crypt32_dll_mun(self):
        test_file = self.get_test_loc('win_pe/crypt32.dll.mun')
        self.check_win_pe(test_file, regen=REGEN_TEST_FIXTURES)

    def test_win_pe_stdole2_tlb(self):
        test_file = self.get_test_loc('win_pe/stdole2.tlb')
        self.check_win_pe(test_file, regen=REGEN_TEST_FIXTURES)

    def test_win_pe_tbs_sys(self):
        test_file = self.get_test_loc('win_pe/tbs.sys')
        self.check_win_pe(test_file, regen=REGEN_TEST_FIXTURES)

    def test_win_pe_Windows_AI_winmd(self):
        test_file = self.get_test_loc('win_pe/Windows.AI.winmd')
        self.check_win_pe(test_file, regen=REGEN_TEST_FIXTURES)

    def test_win_pe_chcp_com(self):
        test_file = self.get_test_loc('win_pe/chcp.com')
        self.check_win_pe(test_file, regen=REGEN_TEST_FIXTURES)


class TestWinPeParseToPackage(TestWinPePeInfo):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    expected_file_suffix = '.package-expected.json'

    def get_results(self, test_file):
        package_data = []
        for manifest in win_pe.WindowsExecutableHandler.parse(test_file):
            package_data.append(manifest.to_dict())
        return package_data
