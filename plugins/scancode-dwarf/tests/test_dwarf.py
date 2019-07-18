#
# Copyright (c) 2019 nexB Inc. and others. All rights reserved.
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

from collections import OrderedDict
import json
import os

from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click

from scandwarf.dwarf import Dwarf
from commoncode.testcase import FileBasedTesting


class TestDwarf(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_dwarf_error_on_non_existing_file(self):
        test_file = 'dwarf/32.fsize.cdasdasdasd'
        expected_msg = "dwarfdump2 ERROR:  can't open "
        try:
            Dwarf(test_file)
        except Exception, e:
            assert expected_msg in str(e)

    def test_dwarf_error_on_malformed_stringtable(self):
        test_loc = self.get_test_loc('elf-corrupted/malformed_stringtable')
        expected_msg = 'dwarfdump2 ERROR:  dwarf_elf_init:  DW_DLE_ELF_STRPTR_ERROR'
        try:
            Dwarf(test_loc)
        except Exception, e:
            assert expected_msg in str(e)

    def test_dwarf_error_on_corrupted_object(self):
        test_loc = self.get_test_loc('elf-corrupted/corrupt.o')
        expected_msg = "dwarfdump2 ERROR:  dwarf_elf_init:  DW_DLE_ELF_STRPTR_ERROR"
        try:
            Dwarf(test_loc)
        except Exception, e:
            assert expected_msg in str(e)

    def check_dwarf(self, test_file, expected_file, regen=False):
        dwarf = Dwarf(self.get_test_loc(test_file))
        result = dwarf.asdict()

        expected_file = self.get_test_loc(expected_file)
        if regen:
            with open(expected_file, 'wb') as exc:
                json.dump(result, exc, indent=2, encoding='utf-8')

        with open(expected_file, 'rb') as exc:
            expected = json.load(exc, encoding='utf-8', object_pairs_hook=OrderedDict)

        assert sorted(expected['original_source_files']) == sorted(result['original_source_files'])
        assert sorted(expected['included_source_files']) == sorted(result['included_source_files'])

    def test_dwarf_amd64_exec(self):
        self.check_dwarf('dwarf/amd64_exec', 'dwarf/amd64_exec.dwarf.expected.json')

    def test_dwarf_arm_exec(self):
        self.check_dwarf('dwarf/arm_exec', 'dwarf/arm_exec.dwarf.expected.json')

    def test_dwarf_arm_exec_nosect(self):
        self.check_dwarf('dwarf/arm_exec_nosect', 'dwarf/arm_exec_nosect.dwarf.expected.json')

    def test_dwarf_arm_gentoo_elf(self):
        self.check_dwarf('dwarf/arm_gentoo_elf', 'dwarf/arm_gentoo_elf.dwarf.expected.json')

    def test_dwarf_arm_object(self):
        self.check_dwarf('dwarf/arm_object', 'dwarf/arm_object.dwarf.expected.json')

    def test_dwarf_arm_scatter_load(self):
        self.check_dwarf('dwarf/arm_scatter_load', 'dwarf/arm_scatter_load.dwarf.expected.json')

    def test_dwarf_file_darwin_i386(self):
        self.check_dwarf('dwarf/file.darwin.i386', 'dwarf/file.darwin.i386.dwarf.expected.json')

    def test_dwarf_file_linux_i686(self):
        self.check_dwarf('dwarf/file.linux.i686', 'dwarf/file.linux.i686.dwarf.expected.json')

    def test_dwarf_file_linux_x86_64(self):
        self.check_dwarf('dwarf/file.linux.x86_64', 'dwarf/file.linux.x86_64.dwarf.expected.json')

    def test_dwarf_file_stripped(self):
        self.check_dwarf('dwarf/file_stripped', 'dwarf/file_stripped.dwarf.expected.json')

    def test_dwarf_ia32_exec(self):
        self.check_dwarf('dwarf/ia32_exec', 'dwarf/ia32_exec.dwarf.expected.json')

    def test_dwarf_ia64_exec(self):
        self.check_dwarf('dwarf/ia64_exec', 'dwarf/ia64_exec.dwarf.expected.json')

    def test_dwarf_libelf_begin_o(self):
        self.check_dwarf('dwarf/libelf-begin.o', 'dwarf/libelf-begin.o.dwarf.expected.json')

    def test_dwarf_shash_i686(self):
        self.check_dwarf('dwarf/shash.i686', 'dwarf/shash.i686.dwarf.expected.json')

    def test_dwarf_ssdeep_i686(self):
        self.check_dwarf('dwarf/ssdeep.i686', 'dwarf/ssdeep.i686.dwarf.expected.json')

    def test_dwarf_ssdeep_x86_64(self):
        self.check_dwarf('dwarf/ssdeep.x86_64', 'dwarf/ssdeep.x86_64.dwarf.expected.json')


class TestScanPluginDwarfScan(FileBasedTesting):

    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_scancode_with_dwarf(self):
        test_dir = self.get_test_loc('dwarf/ssdeep.x86_64')
        result_file = self.get_temp_file('json')
        args = ['--dwarf', test_dir, '--json', result_file]
        run_scan_click(args)
        test_loc = self.get_test_loc('dwarf/ssdeep.x86_64_scan.expected.json')
        check_json_scan(test_loc, result_file, regen=False)
        
