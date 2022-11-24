#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os

import pytest

from packagedcode import rubyparse
from packages_test_utils import get_test_file_paths
from packages_test_utils import PackageTesterBase
from scancode_config import REGEN_TEST_FIXTURES

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


class TestRubyparseParse(PackageTesterBase):
    test_data_dir = TEST_DATA_DIR

    def check_parse_tree(self, test_path, regen):
        test_file = self.get_test_loc(test_path)
        with open(test_file) as tf:
            text = tf.read()
        parse_tree = rubyparse.parse_spec(text)
        parse_tree = parse_tree.pformat(margin=120, indent=2)
        expected_loc = f'{test_file}-rubyparse-expected.tree'
        expected_loc = self.get_test_loc(expected_loc, must_exist=False)
        if regen:
            with open(expected_loc, 'w') as ex:
                ex.write(parse_tree)
        else:
            with open(expected_loc) as ex:
                expected = ex.read()
            assert parse_tree == expected

    gemspecs = get_test_file_paths(base_dir=TEST_DATA_DIR, pattern="rubygems/**/*.gemspec")

    @pytest.mark.parametrize("test_path", gemspecs)
    def test_rubyparse_parse_gemspecs(self, test_path, regen=REGEN_TEST_FIXTURES):
        self.check_parse_tree(test_path, regen)

    gemfiles = get_test_file_paths(base_dir=TEST_DATA_DIR, pattern="rubygems/**/Gemfile")

    @pytest.mark.parametrize("test_path", gemfiles)
    def test_rubyparse_parse_gemfiles(self, test_path, regen=REGEN_TEST_FIXTURES):
        self.check_parse_tree(test_path, regen)

    podspecs = get_test_file_paths(base_dir=TEST_DATA_DIR, pattern="cocoapods/**/*.podspec")

    @pytest.mark.parametrize("test_path", podspecs)
    def test_rubyparse_parse_podspecs(self, test_path, regen=REGEN_TEST_FIXTURES):
        self.check_parse_tree(test_path, regen)

    podfiles = get_test_file_paths(base_dir=TEST_DATA_DIR, pattern="cocoapods/**/Podfile")

    @pytest.mark.parametrize("test_path", podfiles)
    def test_rubyparse_parse_podfiles(self, test_path, regen=REGEN_TEST_FIXTURES):
        self.check_parse_tree(test_path, regen)

