#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os.path
import unittest

from packagedcode import alpine
from packages_test_utils  import build_tests
from packages_test_utils import check_result_equals_expected_json
from packages_test_utils import PackageTester
from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from scancode_config import REGEN_TEST_FIXTURES

test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


class TestAlpineInstalledPackage(PackageTester):
    test_data_dir = test_data_dir

    def test_parse_alpine_installed_db_small(self):
        test_installed = self.get_test_loc('alpine/small-installed/installed')
        result = [package.to_dict(_detailed=True)
            for package in alpine.parse_alpine_installed_db(
                location=test_installed, datasource_id='alpine_installed_db', package_type='alpine',
            )]
        expected = test_installed + '-expected.json'
        check_result_equals_expected_json(result, expected, regen=REGEN_TEST_FIXTURES)

    def test_parse_alpine_installed_db_single(self):
        test_installed = self.get_test_loc('alpine/single-installed/installed')
        result = [package.to_dict(_detailed=True)
            for package in alpine.parse_alpine_installed_db(
                location=test_installed, datasource_id='alpine_installed_db', package_type='alpine',
            )]
        expected = test_installed + '-expected.json'
        check_result_equals_expected_json(result, expected, regen=REGEN_TEST_FIXTURES)

    def test_parse_alpine_installed_db_full(self):
        test_installed = self.get_test_loc('alpine/full-installed/installed')
        result = [package.to_dict(_detailed=True)
            for package in alpine.parse_alpine_installed_db(
                location=test_installed, datasource_id='alpine_installed_db', package_type='alpine',
            )]
        expected = test_installed + '-expected.json'
        check_result_equals_expected_json(result, expected, regen=REGEN_TEST_FIXTURES)

    def test_scan_system_package_end_to_end_installed_alpine(self):
        test_dir = self.extract_test_tar('alpine/rootfs/alpine-rootfs.tar.xz')
        test_dir = os.path.join(test_dir, 'alpine-rootfs')
        expected_file = self.get_test_loc('alpine/rootfs/alpine-rootfs.tar.xz-expected.json')
        result_file = self.get_temp_file('results.json')
        run_scan_click(['--system-package', test_dir, '--json-pp', result_file])
        check_json_scan(expected_file, result_file, regen=REGEN_TEST_FIXTURES)

    def test_can_scan_installed_system_package_in_alpine_container_layer(self):
        test_dir = self.extract_test_tar('alpine/alpine-container-layer.tar.xz', filter='fully_trusted')
        expected_file = self.get_test_loc('alpine/alpine-container-layer.tar.xz-scan-expected.json')
        result_file = self.get_temp_file('results.json')
        run_scan_click(['--system-package', test_dir, '--json-pp', result_file])
        check_json_scan(expected_file, result_file, regen=REGEN_TEST_FIXTURES)

    def test_can_get_installed_system_packages_with_license_from_alpine_container_layer(self):
        from packagedcode.plugin_package import get_installed_packages
        test_dir = self.extract_test_tar('alpine/alpine-container-layer.tar.xz', filter='fully_trusted')
        expected_file = self.get_test_loc('alpine/alpine-container-layer.tar.xz-get-installed-expected.json')
        results = list(get_installed_packages(test_dir))
        self.check_packages_data(results, expected_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)


def apkbuild_tester(location):
    return alpine.parse_apkbuild(location, strict=True).to_dict()


class TestAlpineApkbuildDatadriven(PackageTester):
    test_data_dir = test_data_dir


build_tests(
    test_dir=os.path.join(test_data_dir, 'alpine/apkbuild'),
    clazz=TestAlpineApkbuildDatadriven,
    test_method_prefix='test_',
    tested_function=apkbuild_tester,
    test_file_suffix='APKBUILD',
    regen=REGEN_TEST_FIXTURES,
)


def apkbuild_problems_tester(location):
    return alpine.parse_apkbuild(location, strict=True).to_dict()


class TestAlpineApkbuildProblemsDatadriven(PackageTester):
    test_data_dir = test_data_dir


build_tests(
    test_dir=os.path.join(test_data_dir, 'alpine/apkbuild-problems'),
    clazz=TestAlpineApkbuildProblemsDatadriven,
    test_method_prefix='test_',
    tested_function=apkbuild_problems_tester,
    test_file_suffix='APKBUILD',
    regen=REGEN_TEST_FIXTURES,
)


class TestAlpineMatchedLicenseText(unittest.TestCase):
    def test_alpine_license_detection_matched_text_custom_multiple(self):
        # Regression test for https://github.com/aboutcode-org/scancode-toolkit/issues/4307
        detection = alpine.get_alpine_license_detection("custom:multiple")
        self.assertEqual(detection.declared_license, "custom:multiple")
        self.assertEqual(detection.license_expression, "unknown-license-reference")
        self.assertEqual(len(detection.license_detections), 1)
        matches = detection.license_detections[0]["matches"]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["matched_text"], "custom:multiple")
        self.assertNotIn("licenseref-scancode-", matches[0]["matched_text"])

    def test_alpine_license_detection_matched_text_custom_isc(self):
        detection = alpine.get_alpine_license_detection("custom ISC")
        self.assertEqual(detection.license_expression, "unknown-license-reference AND isc")
        matches = detection.license_detections[0]["matches"]
        self.assertNotIn("licenseref-scancode-", matches[0]["matched_text"])

    def test_alpine_license_detection_matched_text_public_domain(self):
        detection = alpine.get_alpine_license_detection("Public-Domain")
        self.assertEqual(detection.license_expression, "public-domain")
        matches = detection.license_detections[0]["matches"]
        self.assertEqual(matches[0]["matched_text"], "Public-Domain")
        self.assertNotIn("licenseref-scancode-", matches[0]["matched_text"])
