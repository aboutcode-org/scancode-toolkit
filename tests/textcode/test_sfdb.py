#
# Copyright (c) 2018 nexB Inc. and others. All rights reserved.
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

import os

from commoncode.testcase import FileBasedTesting
from textcode import sfdb


class TestSfdb(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def check_get_text_lines(self, test_file, expected_file):
        test_file = self.get_test_loc(test_file )
        expected_file = self.get_test_loc(expected_file)
        expected = open(expected_file, 'rb').read().splitlines(True)
        assert expected == list(sfdb.get_text_lines(test_file))

    def test_get_text_lines_ambro(self):
        test_file = 'splinefonts/Ambrosia.sfd'
        expected_file = 'splinefonts/Ambrosia.sfd.expected'
        self.check_get_text_lines(test_file, expected_file)

    def test_get_text_lines_deja(self):
        test_file = 'splinefonts/DejaVuSerif.sfd'
        expected_file = 'splinefonts/DejaVuSerif.sfd.expected'
        self.check_get_text_lines(test_file, expected_file)

    def test_get_text_lines_liber(self):
        test_file = 'splinefonts/LiberationMono-Italic.sfd'
        expected_file = 'splinefonts/LiberationMono-Italic.sfd.expected'
        self.check_get_text_lines(test_file, expected_file)
