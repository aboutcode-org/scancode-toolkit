#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os.path

from packagedcode import pubspec

from packages_test_utils  import check_result_equals_expected_json
from packages_test_utils  import build_tests
from packages_test_utils import PackageTester

test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


class TestPubspecDatadriven(PackageTester):
    test_data_dir = test_data_dir

    def test_pubspec_lock_is_manifest(self):
        test_file = self.get_test_loc('pubspec/locks/dart-pubspec.lock')
        assert pubspec.PubspecLock.is_manifest(test_file)

    def test_pubspec_yaml_is_manifest(self):
        test_file = self.get_test_loc('pubspec/specs/authors-pubspec.yaml')
        assert pubspec.PubspecYAML.is_manifest(test_file)

    def test_parse_lock(self):
        test_loc = self.get_test_loc('pubspec/mini-pubspec.lock')
        expected_loc = self.get_test_loc('pubspec/mini-pubspec.lock-expected.json', must_exist=False)
        package_manifests = pubspec.PubspecLock.recognize(test_loc)
        self.check_packages(package_manifests, expected_loc, regen=False)


def pub_tester(location,):
    manifests = []
    for package_manifest in pubspec.PubspecYAML.recognize(location):
        manifests.append(package_manifest.to_dict())
    return manifests


def lock_tester(location,):
    manifests = []
    for package_manifest in pubspec.PubspecLock.recognize(location):
        manifests.append(package_manifest.to_dict())
    return manifests


build_tests(
    test_dir=os.path.join(test_data_dir, 'pubspec/specs'),
    clazz=TestPubspecDatadriven,
    test_method_prefix='test_pubspec_yaml',
    tested_function=pub_tester,
    test_file_suffix='pubspec.yaml',
    regen=False,
)

build_tests(
    test_dir=os.path.join(test_data_dir, 'pubspec/locks'),
    clazz=TestPubspecDatadriven,
    test_method_prefix='test_pubspec_lock',
    tested_function=lock_tester,
    test_file_suffix='pubspec.lock',
    regen=False,
)
