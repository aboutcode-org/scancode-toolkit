#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from os.path import dirname
from os.path import join

from commoncode.testcase import FileDrivenTesting

from cluecode.plugin_ignore_copyrights import is_ignored
from scancode.cli_test_utils import run_scan_click
from scancode.cli_test_utils import check_json_scan
from scancode_config import REGEN_TEST_FIXTURES




class TestIgnoreCopyrights(FileDrivenTesting):

    test_data_dir = join(dirname(__file__), 'data')

    def test_is_ignored(self):
        import re
        patterns = [re.compile('Berkeley'), re.compile('1993.*Californi')]
        test1 = 'The Regents of the University of California.'
        test2 = 'Copyright (c) 1993 The Regents of the University of California.'
        test3 = 'the University of California, Berkeley and its contributors.'

        assert not is_ignored(patterns, [test1])
        assert is_ignored(patterns, [test1, test2, test3])
        assert is_ignored(patterns, [test3])
        assert is_ignored(patterns, [test2])

    def test_ignore_holders(self):
        test_dir = self.extract_test_tar('plugin_ignore_copyrights/basic.tgz')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin_ignore_copyrights/holders.expected.json')
        run_scan_click(['-c', '--ignore-copyright-holder', 'Regents', '--json-pp', result_file, test_dir])
        check_json_scan(expected_file, result_file, remove_file_date=True, regen=REGEN_TEST_FIXTURES)

    def test_ignore_authors(self):
        test_dir = self.extract_test_tar('plugin_ignore_copyrights/basic.tgz')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin_ignore_copyrights/authors.expected.json')
        run_scan_click(['-c', '--ignore-author', 'Berkeley', '--json-pp', result_file, test_dir])
        check_json_scan(expected_file, result_file, remove_file_date=True, regen=REGEN_TEST_FIXTURES)
