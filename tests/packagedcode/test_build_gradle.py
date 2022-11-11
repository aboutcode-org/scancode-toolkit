#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os

from packagedcode import build_gradle
from packages_test_utils import build_tests
from packages_test_utils import PackageTester
from packages_test_utils import populate_license_fields
from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from scancode_config import REGEN_TEST_FIXTURES

test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


class TestBuildGradle(PackageTester):
    test_data_dir = test_data_dir

    def test_end2end_scan_can_detect_build_gradle(self):
        test_file = self.get_test_loc('build_gradle/end2end/build.gradle')
        expected_file = self.get_test_loc('build_gradle/end2end/build.gradle-expected.json')
        result_file = self.get_temp_file()
        run_scan_click(['--package', test_file, '--json-pp', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)


def check_gradle_parse(location):
    packages_data = build_gradle.BuildGradleHandler.parse(location)
    results = []
    for package_data in packages_data:
        populate_license_fields(package_data)
        results.append(package_data.to_dict())
    return results


class TestBuildGradleGroovy(PackageTester):
    test_data_dir = test_data_dir


build_tests(
    test_dir=os.path.join(test_data_dir, 'build_gradle/groovy'),
    clazz=TestBuildGradleGroovy,
    test_method_prefix='test_',
    tested_function=check_gradle_parse,
    test_file_suffix='.gradle',
    regen=REGEN_TEST_FIXTURES,
)


class TestBuildGradleKotlin(PackageTester):
    test_data_dir = test_data_dir


build_tests(
    test_dir=os.path.join(test_data_dir, 'build_gradle/kotlin'),
    clazz=TestBuildGradleGroovy,
    test_method_prefix='test_',
    tested_function=check_gradle_parse,
    test_file_suffix='.gradle.kts',
    regen=REGEN_TEST_FIXTURES,
)
