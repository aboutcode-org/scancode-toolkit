#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os.path

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
        expected_file = self.get_test_loc('alpine/rootfs/alpine-rootfs.tar.xz-expected.json', must_exist=False)
        result_file = self.get_temp_file('results.json')
        run_scan_click(['--system-package', test_dir, '--json-pp', result_file])
        check_json_scan(expected_file, result_file, regen=REGEN_TEST_FIXTURES)

    def test_can_scan_installed_system_package_in_alpine_container_layer(self):
        test_dir = self.extract_test_tar('alpine/alpine-container-layer.tar.xz')
        expected_file = self.get_test_loc('alpine/alpine-container-layer.tar.xz-scan-expected.json', must_exist=False)
        result_file = self.get_temp_file('results.json')
        run_scan_click(['--system-package', test_dir, '--json-pp', result_file])
        check_json_scan(expected_file, result_file, regen=REGEN_TEST_FIXTURES)

    def test_can_get_installed_system_packages_with_license_from_alpine_container_layer(self):
        from packagedcode.plugin_package import get_installed_packages
        test_dir = self.extract_test_tar('alpine/alpine-container-layer.tar.xz')
        expected_file = self.get_test_loc('alpine/alpine-container-layer.tar.xz-get-installed-expected.json', must_exist=False)
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
