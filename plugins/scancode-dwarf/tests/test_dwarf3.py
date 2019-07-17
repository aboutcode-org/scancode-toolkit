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

from __future__ import absolute_import, print_function

from collections import OrderedDict
import json
import os
from unittest.case import skipIf

# FIXME: this is a temp hack
import private_test_utils as FIXED_testcase
 
from commoncode.testcase import FileBasedTesting
from commoncode.system import on_mac
from commoncode.system import on_windows

from compiledcode import dwarf3


@skipIf(on_mac, 'Mac is not yet supported: nm needs to be built first')
class TestDwarf3(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def check_dwarf3(self, test_file, expected_file, regen=False):
        test_loc = FIXED_testcase.get_test_loc(test_file, self.test_data_dir, exists=False)
        result = list(dwarf3.get_source_file_path_references(test_loc))
        expected_loc = FIXED_testcase.get_test_loc(expected_file, self.test_data_dir, exists=False)

        if regen:
            with open(expected_loc, 'wb') as exc:
                json.dump(result, exc, indent=2, encoding='utf-8')

        with open(expected_loc, 'rb') as exc:
            expected = json.load(exc, encoding='utf-8', object_pairs_hook=OrderedDict)

        assert sorted(expected) == sorted(result)

    def test_dwarf3_corrupted_malformed_stringtable(self):
        test_file = 'elf-corrupted/malformed_stringtable'
        expected_file = 'elf-corrupted/malformed_stringtable.dwarf3.expected.json'
        if on_windows:
            # nm gets less on Windows from this elf
            expected_file = 'elf-corrupted/malformed_stringtable.win.dwarf3.expected.json'
        self.check_dwarf3(test_file, expected_file)

    def test_dwarf3_with_error_misc_elfs_cpp_test_o(self):
        self.check_dwarf3('misc_elfs/cpp-test.o', 'misc_elfs/cpp-test.o.dwarf3.expected.json')

    def test_dwarf3_with_error_ssdeep_x86_64(self):
        self.check_dwarf3('dwarf/ssdeep.x86_64', 'dwarf/ssdeep.x86_64.dwarf3.expected.json')

    def test_dwarf3_with_error_amd64_exec(self):
        self.check_dwarf3('dwarf/amd64_exec', 'dwarf/amd64_exec.dwarf3.expected.json')

    def test_dwarf3_with_error_shash_x86_64(self):
        self.check_dwarf3('dwarf/shash.x86_64', 'dwarf/shash.x86_64.dwarf3.expected.json')

    def test_dwarf3_empty_on_non_existing_file(self):
        self.check_dwarf3('dwarf/32.fsize.chgg_DOES_NOT_EXIST', 'dwarf/32.fsize.chgg_DOES_NOT_EXIST.dwarf3.expected.json')

    def test_dwarf3_misc_elfs_null_elf(self):
        self.check_dwarf3('misc_elfs/null_elf', 'misc_elfs/null_elf.dwarf3.expected.json')

    def test_dwarf3_file_linux_i686(self):
        self.check_dwarf3('dwarf/file.linux.i686', 'dwarf/file.linux.i686.dwarf3.expected.json')

    def test_dwarf3_file_darwin_i386(self):
        self.check_dwarf3('dwarf/file.darwin.i386', 'dwarf/file.darwin.i386.dwarf3.expected.json')

    def test_dwarf3_file_linux_x86_64(self):
        self.check_dwarf3('dwarf/file.linux.x86_64', 'dwarf/file.linux.x86_64.dwarf3.expected.json')

    def test_dwarf3_arm_exec_nosect(self):
        self.check_dwarf3('dwarf/arm_exec_nosect', 'dwarf/arm_exec_nosect.dwarf3.expected.json')

    def test_dwarf3_file_stripped(self):
        self.check_dwarf3('dwarf/file_stripped', 'dwarf/file_stripped.dwarf3.expected.json')

    def test_dwarf3_ia64_exec(self):
        self.check_dwarf3('dwarf/ia64_exec', 'dwarf/file_stripped.dwarf3.expected.json')

    def test_dwarf3_corrupted_corrupt_o(self):
        self.check_dwarf3('elf-corrupted/corrupt.o', 'elf-corrupted/corrupt.o.dwarf3.expected.json')

    def test_dwarf3_analyze_so_debug(self):
        self.check_dwarf3('dwarf2/analyze.so.debug', 'dwarf2/analyze.so.debug.dwarf3.expected.json')

    def test_dwarf3_autotalent_so_debug(self):
        self.check_dwarf3('dwarf2/autotalent.so.debug', 'dwarf2/autotalent.so.debug.dwarf3.expected.json')

    def test_dwarf3_labrea_debug(self):
        self.check_dwarf3('dwarf2/labrea.debug', 'dwarf2/labrea.debug.dwarf3.expected.json')

    def test_dwarf3_latex2emf_debug(self):
        self.check_dwarf3('dwarf2/latex2emf.debug', 'dwarf2/latex2emf.debug.dwarf3.expected.json')

    def test_dwarf3_libgnutls_so_26_22_4(self):
        self.check_dwarf3('dwarf2/libgnutls.so.26.22.4', 'dwarf2/libgnutls.so.26.22.4.dwarf3.expected.json')

    def test_dwarf3_libgnutls_extra_so_26_22_4(self):
        self.check_dwarf3('dwarf2/libgnutls-extra.so.26.22.4', 'dwarf2/libgnutls-extra.so.26.22.4.dwarf3.expected.json')

    def test_dwarf3_libgnutls_openssl_so_27_0_0(self):
        self.check_dwarf3('dwarf2/libgnutls-openssl.so.27.0.0', 'dwarf2/libgnutls-openssl.so.27.0.0.dwarf3.expected.json')

    def test_dwarf3_libgnutlsxx_so_27_0_0(self):
        self.check_dwarf3('dwarf2/libgnutlsxx.so.27.0.0', 'dwarf2/libgnutlsxx.so.27.0.0.dwarf3.expected.json')

    def test_dwarf3_pam_vbox_so_debug(self):
        self.check_dwarf3('dwarf2/pam_vbox.so.debug', 'dwarf2/pam_vbox.so.debug.dwarf3.expected.json')

    def test_dwarf3_misc_elfs_mips32_exec(self):
        self.check_dwarf3('misc_elfs/mips32_exec', 'misc_elfs/mips32_exec.dwarf3.expected.json')

    def test_dwarf3_misc_elfs_mips64_exec(self):
        self.check_dwarf3('misc_elfs/mips64_exec', 'misc_elfs/mips64_exec.dwarf3.expected.json')

    def test_dwarf3_arm_exec(self):
        self.check_dwarf3('dwarf/arm_exec', 'dwarf/arm_exec.dwarf3.expected.json')

    def test_dwarf3_arm_gentoo_elf(self):
        self.check_dwarf3('dwarf/arm_gentoo_elf', 'dwarf/arm_gentoo_elf.dwarf3.expected.json')

    def test_dwarf3_arm_object(self):
        self.check_dwarf3('dwarf/arm_object', 'dwarf/arm_object.dwarf3.expected.json')

    def test_dwarf3_arm_scatter_load(self):
        self.check_dwarf3('dwarf/arm_scatter_load', 'dwarf/arm_scatter_load.dwarf3.expected.json')

    def test_dwarf3_ia32_exec(self):
        self.check_dwarf3('dwarf/ia32_exec', 'dwarf/ia32_exec.dwarf3.expected.json')

    def test_dwarf3_libelf_begin_o(self):
        self.check_dwarf3('dwarf/libelf-begin.o', 'dwarf/libelf-begin.o.dwarf3.expected.json')

    def test_dwarf3_shash_i686(self):
        self.check_dwarf3('dwarf/shash.i686', 'dwarf/shash.i686.dwarf3.expected.json')

    def test_dwarf3_ssdeep_i686(self):
        self.check_dwarf3('dwarf/ssdeep.i686', 'dwarf/ssdeep.i686.dwarf3.expected.json')

    def test_dwarf3_amd64_exec(self):
        self.check_dwarf3('dwarf/amd64_exec', 'dwarf/amd64_exec.dwarf3.expected.json')
