#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os.path

from packagedcode import git_submodules
from packages_test_utils import PackageTester
from scancode_config import REGEN_TEST_FIXTURES
from scancode.cli_test_utils import run_scan_click
from scancode.cli_test_utils import check_json_scan


class TestGitSubmodules(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_can_detect_gitmodules(self):
        test_dir = self.extract_test_zip('gitmodules/gitmodules.zip')
        test_file = os.path.join(test_dir, '.gitmodules')
        assert git_submodules.GitSubmodulesHandler.is_datafile(test_file)

    def test_parse_gitmodules(self):
        test_dir = self.extract_test_zip('gitmodules/gitmodules.zip')
        test_file = os.path.join(test_dir, '.gitmodules')
        packages = git_submodules.GitSubmodulesHandler.parse(test_file)
        expected_loc = self.get_test_loc('gitmodules/repo.parse.expected.json')
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_scan_cli_works(self):
        test_dir = self.extract_test_zip('gitmodules/gitmodules.zip')
        expected_file = self.get_test_loc('gitmodules/repo.scan.expected.json')
        result_file = self.get_temp_file('results.json')
        run_scan_click(['--package', test_dir, '--json', result_file])
        check_json_scan(
            expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES,
        )