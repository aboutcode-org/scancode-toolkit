#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os.path

import pytest

from packagedcode import build_gradle
from packages_test_utils import PackageTester
from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from scancode_config import REGEN_TEST_FIXTURES


class TestBuildGradle(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_end2end_scan_can_detect_build_gradle(self):
        test_file = self.get_test_loc('build_gradle/build.gradle')
        expected_file = self.get_test_loc('build_gradle/end2end-expected.json')
        result_file = self.get_temp_file()
        run_scan_click(['--package', test_file, '--json-pp', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_BuildGradleHandler_parse_basic(self):
        test_file = self.get_test_loc('build_gradle/build.gradle')
        packages_data = build_gradle.BuildGradleHandler.parse(test_file)
        expected_file = self.get_test_loc('build_gradle/build.gradle-parse-expected.json', must_exist=False)
        self.check_packages_data(
            packages_data=packages_data,
            expected_loc=expected_file,
            must_exist=False,
            regen=REGEN_TEST_FIXTURES,
        )

    def test_BuildGradleHandler_parse_groovy1(self):
        test_file = self.get_test_loc('build_gradle/groovy1/build.gradle')
        packages_data = build_gradle.BuildGradleHandler.parse(test_file)
        expected_file = test_file + '-parse-expected.json'
        self.check_packages_data(
            packages_data=packages_data,
            expected_loc=expected_file,
            must_exist=False,
            regen=REGEN_TEST_FIXTURES,
        )

    def test_BuildGradleHandler_parse_groovy2(self):
        test_file = self.get_test_loc('build_gradle/groovy2/build.gradle')
        packages_data = build_gradle.BuildGradleHandler.parse(test_file)
        expected_file = test_file + '-parse-expected.json'
        self.check_packages_data(
            packages_data=packages_data,
            expected_loc=expected_file,
            must_exist=False,
            regen=REGEN_TEST_FIXTURES,
        )

    @pytest.mark.xfail(reason='Some gradle constructions are not yet handled correctly')
    def test_BuildGradleHandler_parse_groovy3(self):
        test_file = self.get_test_loc('build_gradle/groovy3/build.gradle')
        packages_data = build_gradle.BuildGradleHandler.parse(test_file)
        expected_file = test_file + '-parse-expected.json'
        self.check_packages_data(
            packages_data=packages_data,
            expected_loc=expected_file,
            must_exist=False,
            regen=REGEN_TEST_FIXTURES,
        )

    def test_BuildGradleHandler_parse_kotlin1(self):
        test_file = self.get_test_loc('build_gradle/kotlin1/build.gradle.kts')
        packages_data = build_gradle.BuildGradleHandler.parse(test_file)
        expected_file = test_file + '-parse-expected.json'
        self.check_packages_data(
            packages_data=packages_data,
            expected_loc=expected_file,
            must_exist=False,
            regen=REGEN_TEST_FIXTURES,
        )

    def test_BuildGradleHandler_parse_kotlin2(self):
        test_file = self.get_test_loc('build_gradle/kotlin2/build.gradle.kts')
        packages_data = build_gradle.BuildGradleHandler.parse(test_file)
        expected_file = test_file + '-parse-expected.json'
        self.check_packages_data(
            packages_data=packages_data,
            expected_loc=expected_file,
            must_exist=False,
            regen=REGEN_TEST_FIXTURES,
        )
