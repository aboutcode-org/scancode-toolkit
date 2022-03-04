#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os.path

from packagedcode import build_gradle
from packagedcode import models
from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from packages_test_utils import PackageTester


class TestBuildGradle(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data/build_gradle')

    def test_end2end_scan_can_detect_build_gradle(self):
        test_file = self.get_test_loc('build.gradle')
        expected_file = self.get_test_loc('end2end-expected.json')
        result_file = self.get_temp_file()
        run_scan_click(['--package', test_file, '--json-pp', result_file])
        check_json_scan(expected_file, result_file, remove_instance_uuid=True, regen=False)

    def test_build_gradle_recognize(self):
        test_file = self.get_test_loc('build.gradle')
        result_packages = build_gradle.BuildGradle.recognize(test_file)

        expected_packages = [
            build_gradle.BuildGradle(
                type='build.gradle',
                dependencies = [
                    models.DependentPackage(
                        purl='pkg:build.gradle/com.google/guava@1.0',
                        requirement='1.0',
                        scope='api',
                        is_runtime=True,
                        is_optional=False,
                        is_resolved=False
                    ),
                    models.DependentPackage(
                        purl='pkg:build.gradle/org.apache/commons@1.0',
                        requirement='1.0',
                        scope='usageDependencies',
                        is_runtime=True,
                        is_optional=False,
                        is_resolved=False
                    ),
                    models.DependentPackage(
                        purl='pkg:build.gradle/org.jacoco.ant@0.7.4.201502262128',
                        requirement='0.7.4.201502262128',
                        scope='',
                        is_runtime=True,
                        is_optional=False,
                        is_resolved=False
                    ),
                    models.DependentPackage(
                        purl='pkg:build.gradle/org.jacoco.agent@0.7.4.201502262128',
                        requirement='0.7.4.201502262128',
                        scope='',
                        is_runtime=True,
                        is_optional=False,
                        is_resolved=False
                    ),
                ]
            ),
        ]
        compare_package_results(expected_packages, result_packages)


def compare_package_results(expected, result):
    # We don't want to compare `root_path`, since the result will always
    # have a different `root_path` than the expected result
    result_packages = []
    for result_package in result:
        r = result_package.to_dict()
        result_packages.append(r)
    expected_packages = []
    for expected_package in expected:
        e = expected_package.to_dict()
        expected_packages.append(e)
    assert result_packages == expected_packages
