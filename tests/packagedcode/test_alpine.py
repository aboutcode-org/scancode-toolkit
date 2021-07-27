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

test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


class TestAlpineInstalledPackage(PackageTester):
    test_data_dir = test_data_dir

    def test_parse_alpine_installed_db_small(self):
        test_installed = self.get_test_loc('alpine/small-installed/installed')
        result = [package.to_dict(_detailed=True)
            for package in alpine.parse_alpine_installed_db(test_installed)]
        expected = test_installed + '-expected.json'
        check_result_equals_expected_json(result, expected, regen=False)

    def test_parse_alpine_installed_db_single(self):
        test_installed = self.get_test_loc('alpine/single-installed/installed')
        result = [package.to_dict(_detailed=True)
            for package in alpine.parse_alpine_installed_db(test_installed)]
        expected = test_installed + '-expected.json'
        check_result_equals_expected_json(result, expected, regen=False)

    def test_parse_alpine_installed_db_full(self):
        test_installed = self.get_test_loc('alpine/full-installed/installed')
        result = [package.to_dict(_detailed=True)
            for package in alpine.parse_alpine_installed_db(test_installed)]
        expected = test_installed + '-expected.json'
        check_result_equals_expected_json(result, expected, regen=False)


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
    regen=False,
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
    regen=False,
)
