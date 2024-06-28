#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os.path

from packagedcode import swift
from packages_test_utils import PackageTester
from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from scancode_config import REGEN_TEST_FIXTURES


class TestSwiftHandler(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), "data/swift")

    def test_parse_for_mapboxmaps_manifest(self):
        test_file = self.get_test_loc(
            "packages/mapboxmaps_manifest_and_resolved/Package.swift.json"
        )
        expected_loc = self.get_test_loc("swift-maboxmaps-manifest-parse-expected.json")
        packages = swift.SwiftManifestJsonHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_for_mapboxmaps_resolved(self):
        test_file = self.get_test_loc(
            "packages/mapboxmaps_manifest_and_resolved/Package.resolved"
        )
        expected_loc = self.get_test_loc("swift-maboxmaps-resolved-parse-expected.json")
        packages = swift.SwiftPackageResolvedHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)


class TestSwiftEndtoEnd(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), "data/swift")

    def test_package_scan_swift_end_to_end_full_mapboxmaps_manifest_only(self):
        test_dir = self.get_test_loc("packages/mapboxmaps_manifest")
        result_file = self.get_temp_file("json")
        expected_file = self.get_test_loc(
            "swift-mapboxmaps-manifest-package-expected.json"
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

    def test_package_scan_swift_end_to_end_full_mapboxmaps_manifest_and_resolved(self):
        test_dir = self.get_test_loc("packages/mapboxmaps_manifest_and_resolved")
        result_file = self.get_temp_file("json")
        expected_file = self.get_test_loc(
            "swift-mapboxmaps-manifest-and-resolved-package-expected.json"
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

    def test_package_scan_swift_end_to_end_full_mapboxmaps_resolved_only(self):
        test_dir = self.get_test_loc("packages/fastlane_resolved_v1")
        result_file = self.get_temp_file("json")
        expected_file = self.get_test_loc(
            "swift-fastlane-resolved-v1-package-expected.json"
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

    def test_package_scan_swift_end_to_end_full_vercelui_resolved_only(self):
        test_dir = self.get_test_loc("packages/vercelui")
        result_file = self.get_temp_file("json")
        expected_file = self.get_test_loc(
            "swift-vercelui-expected.json"
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
