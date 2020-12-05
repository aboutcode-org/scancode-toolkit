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

import os

from commoncode.testcase import FileBasedTesting
from licensedcode import legal

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


class TestSpecialFiles(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_is_special_legal_file_COPYING(self):
        test_loc = self.get_test_loc('legal/COPYING')
        expected = 'yes'
        assert expected == legal.is_special_legal_file(test_loc)

    def test_is_special_legal_file_Copyrights(self):
        test_loc = self.get_test_loc('legal/Copyrights')
        expected = 'yes'
        assert expected == legal.is_special_legal_file(test_loc)

    def test_is_special_legal_file_LICENSE(self):
        test_loc = self.get_test_loc('legal/LICENSE')
        expected = 'yes'
        assert expected == legal.is_special_legal_file(test_loc)

    def test_is_special_legal_file_Notice(self):
        test_loc = self.get_test_loc('legal/Notice')
        expected = 'yes'
        assert expected == legal.is_special_legal_file(test_loc)

    def test_is_special_legal_file_no_license_in_here_java(self):
        test_loc = self.get_test_loc('legal/no_license_in_here.java')
        expected = 'maybe'
        assert expected == legal.is_special_legal_file(test_loc)

    def test_is_special_legal_file_noticE_html(self):
        test_loc = self.get_test_loc('legal/noticE.html')
        expected = 'yes'
        assert expected == legal.is_special_legal_file(test_loc)

    def test_is_special_legal_file_useless_notice_txt(self):
        test_loc = self.get_test_loc('legal/useless_notice.txt')
        expected = 'maybe'
        assert expected == legal.is_special_legal_file(test_loc)
