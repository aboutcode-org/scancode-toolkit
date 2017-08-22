# -*- coding: utf-8 -*-
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

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os

from commoncode.testcase import FileBasedTesting
from commoncode.testcase import file_cmp
from commoncode import fileutils
from commoncode import text

from textcode import markup


class TestMarkup(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def atest_gen(self):
        """
        Rename to test xxx to regen tests.
        """
        test_dir = self.get_test_loc(u'markup', True)
        expected_dir = self.get_test_loc(u'markup_expected')
        template = u"""
    def test_%(tn)s(self):
        test_file = self.get_test_loc(u'markup/%(test_file)s')
        expected = self.get_test_loc(u'markup_expected/%(test_file)s')
        result = markup.convert_to_text(test_file)
        file_cmp(expected, result, ignore_line_endings=True)"""

        for test_file in os.listdir(test_dir):
            tn = text.python_safe_name(test_file)
            location = os.path.join(test_dir, test_file)
            result = markup.convert_to_text(location)
            expected_file = os.path.join(expected_dir, test_file)
            fileutils.copyfile(result, expected_file)
            print(template % locals())

    def test_404_htm(self):
        test_file = self.get_test_loc(u'markup/404.htm')
        expected = self.get_test_loc(u'markup_expected/404.htm')
        result = markup.convert_to_text(test_file)
        file_cmp(expected, result, ignore_line_endings=True)

    def test_a_htm(self):
        test_file = self.get_test_loc(u'markup/a.htm')
        expected = self.get_test_loc(u'markup_expected/a.htm')
        result = markup.convert_to_text(test_file)
        file_cmp(expected, result, ignore_line_endings=True)

    def test_allclasses_frame_html(self):
        test_file = self.get_test_loc(u'markup/allclasses-frame.html')
        expected = self.get_test_loc(u'markup_expected/allclasses-frame.html')
        result = markup.convert_to_text(test_file)
        file_cmp(expected, result, ignore_line_endings=True)

    def test_chinese_htm(self):
        test_file = self.get_test_loc(u'markup/chinese.htm')
        expected = self.get_test_loc(u'markup_expected/chinese.htm')
        result = markup.convert_to_text(test_file)
        file_cmp(expected, result, ignore_line_endings=True)

    def test_contenttype_html(self):
        test_file = self.get_test_loc(u'markup/contenttype.html')
        expected = self.get_test_loc(u'markup_expected/contenttype.html')
        result = markup.convert_to_text(test_file)
        file_cmp(expected, result, ignore_line_endings=True)

    def test_double_pygment_in_html_html(self):
        # FIXME: the output is still markup. we need a second pass
        test_file = self.get_test_loc(u'markup/double_pygment_in_html.html')
        expected = self.get_test_loc(u'markup_expected/double_pygment_in_html.html')
        result = markup.convert_to_text(test_file)
        file_cmp(expected, result, ignore_line_endings=True)

    def test_json_phps(self):
        test_file = self.get_test_loc(u'markup/JSON.phps')
        expected = self.get_test_loc(u'markup_expected/JSON.phps')
        result = markup.convert_to_text(test_file)
        file_cmp(expected, result, ignore_line_endings=True)

    def test_json_phps_html(self):
        test_file = self.get_test_loc(u'markup/JSON.phps.html')
        expected = self.get_test_loc(u'markup_expected/JSON.phps.html')
        result = markup.convert_to_text(test_file)
        file_cmp(expected, result, ignore_line_endings=True)

    def test_label_html(self):
        test_file = self.get_test_loc(u'markup/Label.html')
        expected = self.get_test_loc(u'markup_expected/Label.html')
        result = markup.convert_to_text(test_file)
        file_cmp(expected, result, ignore_line_endings=True)

    def test_lgpl_license_html(self):
        test_file = self.get_test_loc(u'markup/lgpl_license.html')
        expected = self.get_test_loc(u'markup_expected/lgpl_license.html')
        result = markup.convert_to_text(test_file)
        file_cmp(expected, result, ignore_line_endings=True)

    def test_pdl_html(self):
        test_file = self.get_test_loc(u'markup/PDL.html')
        expected = self.get_test_loc(u'markup_expected/PDL.html')
        result = markup.convert_to_text(test_file)
        file_cmp(expected, result, ignore_line_endings=True)

    def test_php_php(self):
        test_file = self.get_test_loc(u'markup/php.php')
        expected = self.get_test_loc(u'markup_expected/php.php')
        result = markup.convert_to_text(test_file)
        file_cmp(expected, result, ignore_line_endings=True)

    def test_php_highlighted_in_html_html(self):
        # FIXME: the output is still markup. we need a second pass
        test_file = self.get_test_loc(u'markup/php_highlighted_in_html.html')
        expected = self.get_test_loc(u'markup_expected/php_highlighted_in_html.html')
        result = markup.convert_to_text(test_file)
        file_cmp(expected, result, ignore_line_endings=True)

    def test_rst_highlighted_html(self):
        test_file = self.get_test_loc(u'markup/rst_highlighted.html')
        expected = self.get_test_loc(u'markup_expected/rst_highlighted.html')
        result = markup.convert_to_text(test_file)
        file_cmp(expected, result, ignore_line_endings=True)

    def test_services_htm(self):
        test_file = self.get_test_loc(u'markup/services.htm')
        expected = self.get_test_loc(u'markup_expected/services.htm')
        result = markup.convert_to_text(test_file)
        file_cmp(expected, result, ignore_line_endings=True)

    def test_sissl_license_html(self):
        test_file = self.get_test_loc(u'markup/sissl_license.html')
        expected = self.get_test_loc(u'markup_expected/sissl_license.html')
        result = markup.convert_to_text(test_file)
        file_cmp(expected, result, ignore_line_endings=True)

    def test_text_phps(self):
        test_file = self.get_test_loc(u'markup/text.phps')
        expected = self.get_test_loc(u'markup_expected/text.phps')
        result = markup.convert_to_text(test_file)
        file_cmp(expected, result, ignore_line_endings=True)

    def test_us_htm(self):
        test_file = self.get_test_loc(u'markup/us.htm')
        expected = self.get_test_loc(u'markup_expected/us.htm')
        result = markup.convert_to_text(test_file)
        file_cmp(expected, result, ignore_line_endings=True)
