#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 AND CC-BY-4.0
#
# Visit https://aboutcode.org and https://github.com/nexB/scancode-toolkit for
# support and download. ScanCode is a trademark of nexB Inc.
#
# The ScanCode software is licensed under the Apache License version 2.0.
# The ScanCode open data is licensed under CC-BY-4.0.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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
