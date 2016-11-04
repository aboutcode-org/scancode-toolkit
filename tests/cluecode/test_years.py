#
# Copyright (c) 2015 nexB Inc. and others. All rights reserved.
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

import os.path

from commoncode.testcase import FileBasedTesting
from cluecode_assert_utils import check_detection


class TestYears(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_years_hostpad(self):
        test_file = self.get_test_loc('years/years_hostpad-hostapd_cli_c.c')
        expected = [
            u'2004-2005',
            u'2004-2005',
        ]
        check_detection(expected, test_file, what='years')

    def test_years_ifrename(self):
        test_file = self.get_test_loc('years/years_ifrename-ifrename_c.c')
        expected = [
            u'2004',
        ]
        check_detection(expected, test_file, what='years')

    def test_years_in_c(self):
        test_file = self.get_test_loc('years/years_in_c-c.c')
        expected = [
            u'2005',
            u'2004',
            u'2003',
            u'2002',
            u'2001',
            u'2000',
            u'1999',
            u'1998',
            u'1997',
            u'1996',
        ]
        check_detection(expected, test_file, what='years')

    def test_years_in_copyright(self):
        test_file = self.get_test_loc('years/years_in_copyright-COPYRIGHT_madwifi.madwifi')
        expected = [
            u'2002-2006',
        ]
        check_detection(expected, test_file, what='years')

    def test_years_in_h(self):
        test_file = self.get_test_loc('years/years_in_h-ah_h.h')
        expected = [
            u'2002-2006',
        ]
        check_detection(expected, test_file, what='years')

    def test_years_in_license(self):
        test_file = self.get_test_loc('years/years_in_license-COPYING_gpl.gpl')
        expected = [
            u'1989, 1991',
        ]
        check_detection(expected, test_file, what='years')

    def test_years_in_readme(self):
        test_file = self.get_test_loc('years/years_in_readme-README')
        expected = [
            u'2002-2006',
        ]
        check_detection(expected, test_file, what='years')

    def test_years_in_txt(self):
        test_file = self.get_test_loc('years/years_in_txt.txt')
        expected = [
            u'2005',
            u'2004',
            u'2003',
            u'2002',
            u'2001',
            u'2000',
            u'1999',
            u'1998',
            u'1997',
            u'1996',
        ]
        check_detection(expected, test_file, what='years')

    def test_years_in_uuencode_binary(self):
        test_file = self.get_test_loc('years/years_in_uuencode_binary-mips_be_elf_hal_o_uu.uu')
        expected = [
            u'2002-2006',
        ]
        check_detection(expected, test_file, what='years')
