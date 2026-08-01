# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os.path

from packages_test_utils import PackageTester
from packagedcode import vcpkg
from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from scancode_config import REGEN_TEST_FIXTURES


class TestVcpkg(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), "data")

    def test_parse_vcpkg_json(self):
        test_file = self.get_test_loc("vcpkg/vcpkg.json")
        expected_loc = self.get_test_loc(
            "vcpkg/vcpkg.json-expected.json", must_exist=not REGEN_TEST_FIXTURES
        )
        packages = vcpkg.VcpkgJsonHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_vcpkg_control(self):
        test_file = self.get_test_loc("vcpkg/CONTROL")
        expected_loc = self.get_test_loc(
            "vcpkg/CONTROL-expected.json", must_exist=not REGEN_TEST_FIXTURES
        )
        packages = vcpkg.VcpkgControlHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_package_scan_vcpkg_end_to_end(self):
        test_dir = self.get_test_loc("vcpkg")
        result_file = self.get_temp_file("json")
        expected_file = self.get_test_loc(
            "vcpkg/vcpkg-end-to-end-expected.json", must_exist=not REGEN_TEST_FIXTURES
        )
        run_scan_click(
            [
                "--package",
                "--strip-root",
                "--processes",
                "-1",
                test_dir,
                "--json",
                result_file,
            ]
        )
        check_json_scan(
            expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES
        )

