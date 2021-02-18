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
from textcode import sfdb


class TestSfdb(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def check_get_text_lines(self, test_file, expected_file):
        test_file = self.get_test_loc(test_file)
        expected_file = self.get_test_loc(expected_file)
        expected = open(expected_file, 'rb').read().splitlines(True)
        assert list(sfdb.get_text_lines(test_file)) == expected

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
