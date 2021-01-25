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
from textcode import sfdb


class TestSfdb(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def check_get_text_lines(self, test_file, expected_file):
        test_file = self.get_test_loc(test_file)
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
