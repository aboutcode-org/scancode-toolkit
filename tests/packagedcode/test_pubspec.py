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

    def test_build_dep_non_string_versions(self):
        dep_none = pubspec.build_dep('pkg_none', None, 'dependencies')
        assert dep_none.purl == 'pkg:pubspec/pkg_none'
        assert dep_none.extracted_requirement is None
        assert dep_none.is_pinned is False
        assert dep_none.extra_data == {}

        dep_path = pubspec.build_dep('pkg_path', {'path': '../local_pkg'}, 'dependencies')
        assert dep_path.purl == 'pkg:pubspec/pkg_path'
        assert dep_path.extracted_requirement is None
        assert dep_path.is_pinned is False
        assert dep_path.extra_data == {'path': '../local_pkg'}

        dep_git = pubspec.build_dep('pkg_git', {'git': {'url': 'git://github.com/foo/bar.git'}}, 'dependencies')
        assert dep_git.purl == 'pkg:pubspec/pkg_git'
        assert dep_git.extracted_requirement is None
        assert dep_git.is_pinned is False
        assert dep_git.extra_data == {'git': {'url': 'git://github.com/foo/bar.git'}}

        dep_hosted = pubspec.build_dep('pkg_hosted', {'hosted': 'http://pub.example.com', 'version': '^1.0.0'}, 'dependencies')
        assert dep_hosted.purl == 'pkg:pubspec/pkg_hosted'
        assert dep_hosted.extracted_requirement == '^1.0.0'
        assert dep_hosted.is_pinned is False
        assert dep_hosted.extra_data == {'hosted': 'http://pub.example.com', 'version': '^1.0.0'}

    def test_parse_pubspec_yaml_path_git_unversioned_dependencies(self):
        test_file = self.get_temp_file('pubspec.yaml')
        with open(test_file, 'w') as f:
            f.write(
                'name: test_app\n'
                'version: 1.0.0\n'
                'dependencies:\n'
                '  flutter:\n'
                '    sdk: flutter\n'
                '  my_local:\n'
                '    path: ../my_local\n'
                '  collection:\n'
            )
        packages = list(pubspec.DartPubspecYamlHandler.parse(test_file))
        assert len(packages) == 1
        pkg = packages[0]
        assert pkg.name == 'test_app'
        deps = {d.purl: d for d in pkg.dependencies}
        assert 'pkg:pubspec/flutter' in deps
        assert 'pkg:pubspec/my_local' in deps
        assert 'pkg:pubspec/collection' in deps
        assert deps['pkg:pubspec/my_local'].extra_data == {'path': '../my_local'}
        assert deps['pkg:pubspec/collection'].extracted_requirement is None


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
