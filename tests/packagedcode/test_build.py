#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os.path

from packagedcode import build
from packagedcode import models
from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from commoncode.resource import Codebase
from packages_test_utils import PackageTester


class TestBuild(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data/build')

    def test_end2end_scan_can_detect_bazel(self):
        test_file = self.get_test_loc('bazel/end2end')
        expected_file = self.get_test_loc('bazel/end2end-expected.json')
        result_file = self.get_temp_file('results.json')
        run_scan_click(['--package', test_file, '--json-pp', result_file])
        check_json_scan(expected_file, result_file, regen=False)

    def test_end2end_scan_can_detect_buck(self):
        test_file = self.get_test_loc('buck/end2end')
        expected_file = self.get_test_loc('buck/end2end-expected.json')
        result_file = self.get_temp_file('results.json')
        run_scan_click(['--package', test_file, '--json-pp', result_file])
        check_json_scan(expected_file, result_file, regen=False)

    def test_build_get_package_resources(self):
        test_loc = self.get_test_loc('get_package_resources')
        codebase = Codebase(test_loc)
        root = codebase.root
        expected = [
            'get_package_resources',
            'get_package_resources/BUCK',
            'get_package_resources/file1',
        ]
        results = [r.path for r in build.BaseBuildManifestPackage.get_package_resources(root, codebase)]
        assert results == expected

    def test_BazelPackage_recognize(self):
        test_file = self.get_test_loc('bazel/parse/BUILD')
        result_packages = build.BazelPackage.recognize(test_file)
        expected_packages = [
            build.BazelPackage(name='hello-greet'),
            build.BazelPackage(name='hello-world'),
        ]
        compare_package_results(expected_packages, result_packages)

    def test_BuckPackage_recognize(self):
        test_file = self.get_test_loc('buck/parse/BUCK')
        result_packages = build.BuckPackage.recognize(test_file)
        expected_packages = [
            build.BuckPackage(name='app'),
            build.BuckPackage(name='app2'),
        ]
        compare_package_results(expected_packages, result_packages)

    def test_BuckPackage_recognize_with_license(self):
        test_file = self.get_test_loc('buck/parse/license/BUCK')
        result_packages = build.BuckPackage.recognize(test_file)
        expected_packages = [
            build.BuckPackage(
                name='app',
                declared_license=['LICENSE'],
            )
        ]
        compare_package_results(expected_packages, result_packages)

    def test_MetadataBzl_recognize(self):
        test_file = self.get_test_loc('metadatabzl/METADATA.bzl')
        result_packages = build.MetadataBzl.recognize(test_file)
        expected_packages = [
            build.MetadataBzl(
                type='github',
                name='example',
                version='0.0.1',
                declared_license=['BSD-3-Clause'],
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


def compare_package_results(expected, result):
    # We don't want to compare `root_path`, since the result will always
    # have a different `root_path` than the expected result
    result_packages = []
    for result_package in result:
        r = result_package.to_dict()
        r.pop('root_path')
        result_packages.append(r)
    expected_packages = []
    for expected_package in expected:
        e = expected_package.to_dict()
        e.pop('root_path')
        expected_packages.append(e)
    assert result_packages == expected_packages
