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
from packages_test_utils  import build_tests
from packages_test_utils import PackageTester
from scancode_config import REGEN_TEST_FIXTURES

test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


class TestPubspecDatadriven(PackageTester):
    test_data_dir = test_data_dir

    def test_pubspec_lock_is_package_data_file(self):
        test_file = self.get_test_loc('pubspec/locks/dart-pubspec.lock')
        assert pubspec.DartPubspecLockHandler.is_datafile(test_file)

    def test_pubspec_yaml_is_package_data_file(self):
        test_file = self.get_test_loc('pubspec/specs/authors-pubspec.yaml')
        assert pubspec.DartPubspecYamlHandler.is_datafile(test_file)

    def test_parse_lock(self):
        test_loc = self.get_test_loc('pubspec/mini-pubspec.lock')
        expected_loc = self.get_test_loc('pubspec/mini-pubspec.lock-expected.json')
        package_data = pubspec.DartPubspecLockHandler.parse(test_loc)
        self.check_packages_data(package_data, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_build_dep_path_dependency(self):
        dep = pubspec.build_dep(
            name='my_local_package',
            version={'path': '../my_local_package'},
            scope='dependencies',
        )
        assert dep.purl == 'pkg:pubspec/my_local_package'
        assert dep.extracted_requirement is None
        assert not dep.is_pinned
        assert dep.extra_data == {'path': '../my_local_package'}

    def test_build_dep_git_dependency(self):
        dep = pubspec.build_dep(
            name='kittens',
            version={'git': {'url': 'git://github.com/munificent/kittens.git', 'ref': 'some-branch'}},
            scope='dependencies',
        )
        assert dep.purl == 'pkg:pubspec/kittens'
        assert dep.extracted_requirement is None
        assert not dep.is_pinned
        assert dep.extra_data == {'git': {'url': 'git://github.com/munificent/kittens.git', 'ref': 'some-branch'}}

    def test_build_dep_unversioned_dependency(self):
        dep = pubspec.build_dep(
            name='collection',
            version=None,
            scope='dependencies',
        )
        assert dep.purl == 'pkg:pubspec/collection'
        assert dep.extracted_requirement is None
        assert not dep.is_pinned
        assert dep.extra_data == {}

    def test_build_dep_hosted_with_version(self):
        dep = pubspec.build_dep(
            name='transmogrify',
            version={'hosted': 'https://some-package-repo.com', 'version': '^1.4.0'},
            scope='dependencies',
        )
        assert dep.purl == 'pkg:pubspec/transmogrify'
        assert dep.extracted_requirement == '^1.4.0'
        assert not dep.is_pinned
        assert dep.extra_data == {'hosted': 'https://some-package-repo.com', 'version': '^1.4.0'}


def pub_tester(location,):
    manifests = []
    for package_data in pubspec.DartPubspecYamlHandler.parse(location):
        manifests.append(package_data.to_dict())
    return manifests


def lock_tester(location,):
    manifests = []
    for package_data in pubspec.DartPubspecLockHandler.parse(location):
        manifests.append(package_data.to_dict())
    return manifests


build_tests(
    test_dir=os.path.join(test_data_dir, 'pubspec/specs'),
    clazz=TestPubspecDatadriven,
    test_method_prefix='test_pubspec_yaml',
    tested_function=pub_tester,
    test_file_suffix='pubspec.yaml',
    regen=REGEN_TEST_FIXTURES,
)

build_tests(
    test_dir=os.path.join(test_data_dir, 'pubspec/locks'),
    clazz=TestPubspecDatadriven,
    test_method_prefix='test_pubspec_lock',
    tested_function=lock_tester,
    test_file_suffix='pubspec.lock',
    regen=REGEN_TEST_FIXTURES,
)
