#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os.path

from commoncode.resource import Codebase

from packagedcode import build
from packagedcode import models
from packages_test_utils import PackageTester
from packages_test_utils import compare_package_results
from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from scancode_config import REGEN_TEST_FIXTURES



class TestBuild(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data/build')

    def test_end2end_scan_can_detect_bazel(self):
        test_file = self.get_test_loc('bazel/end2end')
        expected_file = self.get_test_loc('bazel/end2end-expected.json')
        result_file = self.get_temp_file('results.json')
        run_scan_click(['--package', test_file, '--json-pp', result_file])
        check_json_scan(expected_file, result_file, regen=REGEN_TEST_FIXTURES)

    def test_end2end_scan_can_detect_buck(self):
        test_file = self.get_test_loc('buck/end2end')
        expected_file = self.get_test_loc('buck/end2end-expected.json')
        result_file = self.get_temp_file('results.json')
        run_scan_click(['--package', test_file, '--json-pp', result_file])
        check_json_scan(expected_file, result_file, regen=REGEN_TEST_FIXTURES)

    def test_BazelPackage_parse(self):
        test_file = self.get_test_loc('bazel/parse/BUILD')
        result_packages = build.BazelBuildHandler.parse(test_file)
        expected_packages = [
            models.PackageData(
                name='hello-greet',
                type=build.BazelBuildHandler.default_package_type,
                datasource_id=build.BazelBuildHandler.datasource_id,
            ),
            models.PackageData(
                name='hello-world',
                type=build.BazelBuildHandler.default_package_type,
                datasource_id=build.BazelBuildHandler.datasource_id,
            )
        ]
        compare_package_results(expected_packages, result_packages)

    def test_BuckPackage_parse(self):
        test_file = self.get_test_loc('buck/parse/BUCK')
        result_packages = build.BuckPackageHandler.parse(test_file)
        expected_packages = [
            models.PackageData(
                name='app',
                type=build.BuckPackageHandler.default_package_type,
                datasource_id=build.BuckPackageHandler.datasource_id,
            ),
            models.PackageData(
                name='app2',
                type=build.BuckPackageHandler.default_package_type,
                datasource_id=build.BuckPackageHandler.datasource_id,
            ),
        ]
        compare_package_results(expected_packages, result_packages)

    def test_BuckPackage_recognize_with_license(self):
        test_file = self.get_test_loc('buck/parse/license/BUCK')
        test_loc = self.get_test_loc('buck/parse/license/')
        result_package = list(build.BuckPackageHandler.parse(test_file))[0]
        codebase = Codebase(test_loc)
        resource = codebase.get_resource('license/BUCK')
        _detections, license_expression = build.get_license_detections_and_expression(
            result_package, resource, codebase
        )
        assert license_expression == 'apache-2.0'

    def test_MetadataBzl_parse(self):
        test_file = self.get_test_loc('metadatabzl/METADATA.bzl')
        result_packages = build.BuckMetadataBzlHandler.parse(test_file)
        expected_packages = [
            models.PackageData(
                datasource_id=build.BuckMetadataBzlHandler.datasource_id,
                type='github',
                name='example',
                version='0.0.1',
                extracted_license_statement=['BSD-3-Clause'],
                parties=[
                    models.Party(
                        type=models.party_org,
                        name='oss_foundation',
                        role='maintainer'
                    )
                ],
                homepage_url='https://github.com/example/example',
            ),
        ]
        compare_package_results(expected_packages, result_packages)

    def test_MetadataBzl_recognize_new_format(self):
        test_file = self.get_test_loc('metadatabzl/new-format/METADATA.bzl')
        result_packages = build.BuckMetadataBzlHandler.parse(test_file)
        expected_packages = [
            models.PackageData(
                datasource_id=build.BuckMetadataBzlHandler.datasource_id,
                type='github',
                name='example/example',
                version='0.0.1',
                extracted_license_statement='BSD-3-Clause',
                parties=[
                    models.Party(
                        type=models.party_org,
                        name='example_org',
                        role='maintainer'
                    )
                ],
                download_url='',
                sha1='',
                homepage_url='https://github.com/example/example',
                vcs_url='https://github.com/example/example.git',
                extra_data=dict(vcs_commit_hash="deadbeef")
            )
        ]
        compare_package_results(expected_packages, result_packages)
