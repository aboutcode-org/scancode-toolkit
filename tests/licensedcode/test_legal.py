#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#
import os

from commoncode.testcase import FileBasedTesting
from licensedcode import legal

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


class TestSpecialFiles(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_is_special_legal_file_COPYING(self):
        test_loc = self.get_test_loc('legal/COPYING')
        expected = 'yes'
        assert legal.is_special_legal_file(test_loc) == expected

    def test_is_special_legal_file_Copyrights(self):
        test_loc = self.get_test_loc('legal/Copyrights')
        expected = 'yes'
        assert legal.is_special_legal_file(test_loc) == expected

    def test_is_special_legal_file_LICENSE(self):
        test_loc = self.get_test_loc('legal/LICENSE')
        expected = 'yes'
        assert legal.is_special_legal_file(test_loc) == expected

    def test_is_special_legal_file_Notice(self):
        test_loc = self.get_test_loc('legal/Notice')
        expected = 'yes'
        assert legal.is_special_legal_file(test_loc) == expected

    def test_is_special_legal_file_no_license_in_here_java(self):
        test_loc = self.get_test_loc('legal/no_license_in_here.java')
        expected = 'maybe'
        assert legal.is_special_legal_file(test_loc) == expected

    def test_is_special_legal_file_noticE_html(self):
        test_loc = self.get_test_loc('legal/noticE.html')
        expected = 'yes'
        assert legal.is_special_legal_file(test_loc) == expected

    def test_is_special_legal_file_useless_notice_txt(self):
        test_loc = self.get_test_loc('legal/useless_notice.txt')
        expected = 'maybe'
        assert legal.is_special_legal_file(test_loc) == expected
