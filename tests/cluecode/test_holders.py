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

import os.path
from unittest.case import expectedFailure

from commoncode.testcase import FileBasedTesting
from cluecode_assert_utils import check_detection


class TestHolders(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_holder_acme_c(self):
        test_file = self.get_test_loc('holders/holder_acme_c-c.c')
        expected = [
            'ACME, Inc.',
        ]
        check_detection(expected, test_file, what='holders')

    def test_holder_addr_c(self):
        test_file = self.get_test_loc('holders/holder_addr_c-addr_c.c')
        expected = [
            'Cornell University.',
            'Jon Doe.',
        ]
        check_detection(expected, test_file, what='holders')

    def test_holder_atheros_py(self):
        test_file = self.get_test_loc('holders/holder_atheros_py-py.py')
        expected = [
            'Atheros Communications, Inc.',
            'Atheros Communications, Inc.',
            'Intel Corporation.',
        ]
        check_detection(expected, test_file, what='holders')

    def test_holder_audio_c(self):
        test_file = self.get_test_loc('holders/holder_audio_c-c.c')
        expected = [
            'AudioCodes, DSP Group',
            'France Telecom, Universite de Sherbrooke.',
        ]
        check_detection(expected, test_file, what='holders')

    def test_holder_basic(self):
        test_file = self.get_test_loc('holders/holder_basic-copy_c.c')
        expected = [
            'Markus Franz Xaver Johannes Oberhumer',
            'Markus Franz Xaver Johannes Oberhumer',
            'Markus Franz Xaver Johannes Oberhumer',
            'Markus Franz Xaver Johannes Oberhumer',
            'Markus Franz Xaver Johannes Oberhumer',
            'Markus Franz Xaver Johannes Oberhumer',
            'Markus Franz Xaver Johannes Oberhumer',
            'Markus Franz Xaver Johannes Oberhumer',
            'Markus Franz Xaver Johannes Oberhumer',
            'Markus Franz Xaver Johannes Oberhumer',
            'Markus Franz Xaver Johannes Oberhumer',
            'Markus Franz Xaver Johannes Oberhumer',
            'Markus Franz Xaver Johannes Oberhumer',
            'Markus Franz Xaver Johannes Oberhumer',
            'http://www.oberhumer.com'
         ]
        check_detection(expected, test_file, what='holders')

    def test_holder_complex(self):
        test_file = self.get_test_loc('holders/holder_complex-strtol_c.c')
        expected = [
            'The Regents of the University of California.',
        ]
        check_detection(expected, test_file, what='holders')

    def test_holder_extjs_c(self):
        test_file = self.get_test_loc('holders/holder_extjs_c-c.c')
        expected = [
            'Ext JS, LLC.',
        ]
        check_detection(expected, test_file, what='holders')

    def test_holder_hans_jurgen_html(self):
        test_file = self.get_test_loc('holders/holder_hans_jurgen_html-9_html.html')
        expected = [
            'Hans-Jurgen Koch.',
        ]
        check_detection(expected, test_file, what='holders')

    def test_holder_hostpad(self):
        test_file = self.get_test_loc('holders/holder_hostpad-hostapd_cli_c.c')
        expected = [
            'Jouni Malinen',
            'Jouni Malinen',
        ]
        check_detection(expected, test_file, what='holders')

    def test_holder_ibm_c(self):
        test_file = self.get_test_loc('holders/holder_ibm_c-ibm_c.c')
        expected = [
            'ibm technologies',
            'IBM Corporation',
            'Ibm Corp.',
            'ibm.com',
            'IBM technology',
            'IBM company',
        ]
        check_detection(expected, test_file, what='holders')

    def test_holder_ifrename(self):
        test_file = self.get_test_loc('holders/holder_ifrename-ifrename_c.c')
        expected = [
            'Jean Tourrilhes',
        ]
        check_detection(expected, test_file, what='holders')

    def test_holder_in_c(self):
        test_file = self.get_test_loc('holders/holder_in_c-c.c')
        expected = [
            'Markus Franz Xaver Johannes Oberhumer',
            'Markus Franz Xaver Johannes Oberhumer',
            'Markus Franz Xaver Johannes Oberhumer',
            'Markus Franz Xaver Johannes Oberhumer',
            'Markus Franz Xaver Johannes Oberhumer',
            'Markus Franz Xaver Johannes Oberhumer',
            'Markus Franz Xaver Johannes Oberhumer',
            'Markus Franz Xaver Johannes Oberhumer',
            'Markus Franz Xaver Johannes Oberhumer',
            'Markus Franz Xaver Johannes Oberhumer',
        ]
        check_detection(expected, test_file, what='holders')

    def test_holder_in_copyright(self):
        test_file = self.get_test_loc('holders/holder_in_copyright-COPYRIGHT_madwifi.madwifi')
        expected = [
            'Sam Leffler, Errno Consulting, Atheros Communications, Inc.',
        ]
        check_detection(expected, test_file, what='holders')

    def test_holder_in_h(self):
        test_file = self.get_test_loc('holders/holder_in_h-ah_h.h')
        expected = [
            'Sam Leffler, Errno Consulting, Atheros Communications, Inc.',
        ]
        check_detection(expected, test_file, what='holders')

    def test_holder_in_license(self):
        test_file = self.get_test_loc('holders/holder_in_license-COPYING_gpl.gpl')
        expected = [
            'Free Software Foundation, Inc.',
            'the Free Software Foundation',
        ]
        check_detection(expected, test_file, what='holders')

    def test_holder_in_readme(self):
        test_file = self.get_test_loc('holders/holder_in_readme-README')
        expected = [
            'Jouni Malinen',
        ]
        check_detection(expected, test_file, what='holders')

    def test_holder_in_text_(self):
        test_file = self.get_test_loc('holders/holder_in_text_.txt')
        expected = [
            'Markus Franz Xaver Johannes Oberhumer',
            'Markus Franz Xaver Johannes Oberhumer',
            'Markus Franz Xaver Johannes Oberhumer',
            'Markus Franz Xaver Johannes Oberhumer',
            'Markus Franz Xaver Johannes Oberhumer',
            'Markus Franz Xaver Johannes Oberhumer',
            'Markus Franz Xaver Johannes Oberhumer',
            'Markus Franz Xaver Johannes Oberhumer',
            'Markus Franz Xaver Johannes Oberhumer',
            'Markus Franz Xaver Johannes Oberhumer',
        ]
        check_detection(expected, test_file, what='holders')

    def test_holder_in_uuencode_binary(self):
        test_file = self.get_test_loc('holders/holder_in_uuencode_binary-mips_be_elf_hal_o_uu.uu')
        expected = [
            'Sam Leffler, Errno Consulting, Atheros Communications, Inc.',
        ]
        check_detection(expected, test_file, what='holders')

    def test_holder_javascript(self):
        test_file = self.get_test_loc('holders/holder_javascript-utilities_js.js')
        expected = [
            'Yahoo! Inc.',
            'Robert Penner',
        ]
        check_detection(expected, test_file, what='holders')

    def test_holder_javascript_large(self):
        test_file = self.get_test_loc('holders/holder_javascript_large-ext_all_js.js')
        expected = [
            'Ext JS, LLC',
         ]
        check_detection(expected, test_file, what='holders')

    def test_holder_mergesort_java(self):
        test_file = self.get_test_loc('holders/holder_mergesort_java-MergeSort_java.java')
        expected = [
            'Sun Microsystems, Inc.',
        ]
        check_detection(expected, test_file, what='holders')

    @expectedFailure
    def test_holder_multiline(self):
        test_file = self.get_test_loc('holders/holder_multiline-Historical.txt')
        expected = [
            'GEORGE J. CARRETTE, CONCORD, MASSACHUSETTS.',
        ]
        check_detection(expected, test_file, what='holders')

    def test_holder_nokia_cpp(self):
        test_file = self.get_test_loc('holders/holder_nokia_cpp-cpp.cpp')
        expected = [
            'Nokia Mobile Phones.',
        ]
        check_detection(expected, test_file, what='holders')

    def test_holder_sample_java(self):
        test_file = self.get_test_loc('holders/holder_sample_java-java.java')
        expected = [
            'Sample ABC Inc.',
        ]
        check_detection(expected, test_file, what='holders')

    def test_holder_simple(self):
        test_file = self.get_test_loc('holders/holder_simple-copy_c.c')
        expected = [
            'Markus Franz Xaver Johannes Oberhumer',
        ]
        check_detection(expected, test_file, what='holders')

    def test_holder_snmptrapd_c(self):
        test_file = self.get_test_loc('holders/holder_snmptrapd_c-snmptrapd_c.c')
        expected = [
            'Carnegie Mellon University',
        ]
        check_detection(expected, test_file, what='holders')

    def test_holder_somefile_cpp(self):
        test_file = self.get_test_loc('holders/holder_somefile_cpp-somefile_cpp.cpp')
        expected = [
            'Private Company (PC) Property of Private Company',
            'Private Company'        ]
        check_detection(expected, test_file, what='holders')

    def test_holder_stacktrace_cpp(self):
        test_file = self.get_test_loc('holders/holder_stacktrace_cpp-stacktrace_cpp.cpp')
        expected = [
            'Rickard E. Faith',
        ]
        check_detection(expected, test_file, what='holders')

    def test_holder_super_c(self):
        test_file = self.get_test_loc('holders/holder_super_c-c.c')
        expected = [
            'Super Technologies Corporation, Cedar Rapids, Iowa, U.S.A.',
            'Benjamin Herrenschmuidt',
            'IBM Corp.',
        ]
        check_detection(expected, test_file, what='holders')

    def test_holder_treetablemodeladapter_java(self):
        test_file = self.get_test_loc('holders/holder_treetablemodeladapter_java-TreeTableModelAdapter_java.java')
        expected = [
            'Sun Microsystems, Inc.',
        ]
        check_detection(expected, test_file, what='holders')

    def test_holder_tunnel_h(self):
        test_file = self.get_test_loc('holders/holder_tunnel_h-tunnel_h.h')
        expected = [
            'Frank Strauss',
        ]
        check_detection(expected, test_file, what='holders')

    def test_holder_var_route_c(self):
        test_file = self.get_test_loc('holders/holder_var_route_c-var_route_c.c')
        expected = [
            'Carnegie Mellon University',
            'TGV, Incorporated',
            'Erik Schoenfelder',
            'Simon Leinen'
        ]
        check_detection(expected, test_file, what='holders')

    def test_holder_xcon_sh(self):
        test_file = self.get_test_loc('holders/holder_xcon_sh-9_sh.sh')
        expected = [
            'X Consortium',
        ]
        check_detection(expected, test_file, what='holders')

    def test_holder_young_c(self):
        test_file = self.get_test_loc('holders/holder_young_c-c.c')
        expected = [
            'Eric Young',
        ]
        check_detection(expected, test_file, what='holders')

    def test_holder_oracle(self):
        test_file = self.get_test_loc('holders/oracle.txt')
        expected = ['Oracle and/or its affiliates.']
        check_detection(expected, test_file, what='holders')
