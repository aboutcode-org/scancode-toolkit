#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from copy import copy
from os import path

import pytest

from commoncode.testcase import FileDrivenTesting

from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from scancode_config import REGEN_TEST_FIXTURES


class TestScanReview(FileDrivenTesting):

    test_data_dir = path.join(path.dirname(__file__), 'data/todo/')

    def test_end2end_todo_works_on_codebase_without_ambiguous_detections(self):
        test_dir = self.get_test_loc('no_todo/base64-arraybuffer-0.1.4/')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('no_todo/base64-arraybuffer.expected.json')
        run_scan_click([
            '-clip',
            '--todo',
            '--json-pp', result_file, test_dir
        ])
        check_json_scan(expected_file, result_file, remove_uuid=True, remove_file_date=True, regen=REGEN_TEST_FIXTURES)

    def test_end2end_todo_works_on_unknown_licenses_plain(self):
        test_dir = self.get_test_loc('todo_present/unknown-license.txt')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('todo_present/unknown-license-expected.json')
        run_scan_click([
            '--license',
            '--license-text',
            '--unknown-licenses',
            '--todo',
            '--json-pp', result_file, test_dir
        ])
        check_json_scan(expected_file, result_file, remove_uuid=True, remove_file_date=True, regen=REGEN_TEST_FIXTURES)

    def test_end2end_todo_works_on_unknown_licenses_diagnostics(self):
        test_dir = self.get_test_loc('todo_present/unknown-license.txt')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('todo_present/unknown-license-expected-diag.json')
        run_scan_click([
            '--license',
            '--license-text',
            '--license-diagnostics',
            '--license-text-diagnostics',
            '--unknown-licenses',
            '--todo',
            '--json-pp', result_file, test_dir
        ])
        check_json_scan(expected_file, result_file, remove_uuid=True, remove_file_date=True, regen=REGEN_TEST_FIXTURES)

    def test_end2end_todo_works_on_package_manifest_without_version(self):
        test_dir = self.get_test_loc('todo_present/incomplete-setup.cfg')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('todo_present/incomplete-setup-cfg-expected.json')
        run_scan_click([
            '--package',
            '--todo',
            '--json-pp', result_file, test_dir
        ])
        check_json_scan(expected_file, result_file, remove_uuid=True, remove_file_date=True, regen=REGEN_TEST_FIXTURES)

    def test_end2end_todo_works_on_from_json(self):
        test_dir = self.get_test_loc('todo_present/unknown-license.txt')
        intermediate_result_file = self.get_temp_file('json')
        final_result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('todo_present/unknown-license-expected-diag.json')
        run_scan_click([
            '--license',
            '--license-text',
            '--license-diagnostics',
            '--license-text-diagnostics',
            '--unknown-licenses',
            '--json-pp', intermediate_result_file, test_dir
        ])
        run_scan_click([
            '--todo',
            '--from-json', intermediate_result_file,
            '--json-pp', final_result_file
        ])
        check_json_scan(expected_file, final_result_file, remove_uuid=True, remove_file_date=True, regen=REGEN_TEST_FIXTURES)

    def test_end2end_todo_works_on_license_clues_diagnostics(self):
        test_dir = self.get_test_loc('todo_present/README.multi-orig-tarball-package')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('todo_present/README.multi-orig-tarball-package-expected-diag.json')
        run_scan_click([
            '--license',
            '--license-text',
            '--license-diagnostics',
            '--license-text-diagnostics',
            '--todo',
            '--json-pp', result_file, test_dir
        ])
        check_json_scan(expected_file, result_file, remove_uuid=True, remove_file_date=True, regen=REGEN_TEST_FIXTURES)
