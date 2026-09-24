#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
#

import os

from packagedcode import publiccode
from packages_test_utils import PackageTester
from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from scancode_config import REGEN_TEST_FIXTURES


class TestPubliccode(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_publiccode_yml_is_datafile(self):
        test_file = self.get_test_loc('publiccode/publiccode.yml')
        assert publiccode.PubliccodeYmlHandler.is_datafile(test_file)

    def test_parse_publiccode_yml(self):
        test_file = self.get_test_loc('publiccode/publiccode.yml')
        packages = publiccode.PubliccodeYmlHandler.parse(test_file)
        expected_loc = self.get_test_loc(
            'publiccode/publiccode.yml-expected.json',
            must_exist=False,
        )
        self.check_packages_data(
            packages_data=packages,
            expected_loc=expected_loc,
            must_exist=False,
            regen=REGEN_TEST_FIXTURES,
        )

    def test_scan_cli_works(self):
        test_file = self.get_test_loc('publiccode/publiccode.yml')
        expected_file = self.get_test_loc(
            'publiccode/publiccode.yml-scancode.json',
            must_exist=False,
        )
        result_file = self.get_temp_file('results.json')
        run_scan_click(['--package', test_file, '--json', result_file])
        check_json_scan(
            expected_file=expected_file,
            result_file=result_file,
            remove_uuid=True,
            regen=REGEN_TEST_FIXTURES,
        )

    def test_publiccode_yml_no_version_key_returns_nothing(self):
        test_file = self.get_temp_file(extension='yml', file_name='publiccode')
        with open(test_file, 'w') as temp_file:
            temp_file.write('name: something\nversion: 1.0\n')

        packages = list(publiccode.PubliccodeYmlHandler.parse(test_file))
        assert packages == []

    def test_publiccode_yml_path_patterns(self):
        assert publiccode.PubliccodeYmlHandler.path_patterns == (
            '*publiccode.yml',
            '*publiccode.yaml',
        )
