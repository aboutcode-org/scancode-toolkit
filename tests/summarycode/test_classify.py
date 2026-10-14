#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from os.path import dirname
from os.path import join

from commoncode.testcase import FileDrivenTesting
from commoncode.resource import Codebase

from scancode.cli_test_utils import run_scan_click
from scancode.cli_test_utils import check_json_scan
from scancode_config import REGEN_TEST_FIXTURES
from summarycode.classify import set_classification_flags
from summarycode.classify_plugin import FileClassifier


class TestClassify(FileDrivenTesting):

    test_data_dir = join(dirname(__file__), 'data')

    def test_set_classification_flags_is_readme(self):
        test_dir = self.get_test_loc('classify/readme')
        codebase = Codebase(
            test_dir, resource_attributes=FileClassifier.resource_attributes)
        for res in codebase.walk():
            if not res.is_file:
                continue
            set_classification_flags(res)
            assert res.is_readme

    def test_set_classification_flags_is_legal(self):
        test_dir = self.get_test_loc('classify/legal')
        codebase = Codebase(
            test_dir, resource_attributes=FileClassifier.resource_attributes)
        for res in codebase.walk():
            if not res.is_file:
                continue
            set_classification_flags(res)
            assert res.is_legal

    def test_set_classification_flags_not_is_legal(self):
        test_dir = self.get_test_loc('classify/not-legal')
        codebase = Codebase(
            test_dir, resource_attributes=FileClassifier.resource_attributes)
        for res in codebase.walk():
            if not res.is_file:
                continue
            set_classification_flags(res)
            assert not res.is_legal

    def test_set_classification_flags_is_package_data_file(self):
        test_dir = self.get_test_loc('classify/manifest')
        codebase = Codebase(
            test_dir, resource_attributes=FileClassifier.resource_attributes)
        for res in codebase.walk():
            if not res.is_file:
                continue
            set_classification_flags(res)
            assert res.is_manifest

    def test_set_classification_flags_modern_manifests(self):
        import posixpath

        class MockResource:
            def __init__(self, path, is_top_level=True):
                self.path = path
                self.name = posixpath.basename(path)
                self.base_name = posixpath.splitext(self.name)[0]
                self.is_top_level = is_top_level
                self.package_data = []
                self.is_legal = False
                self.is_readme = False
                self.is_community = False
                self.is_manifest = False
                self.is_key_file = False

        modern_manifests = [
            'Cargo.toml',
            'Cargo.lock',
            'poetry.lock',
            'Pipfile.lock',
            'package-lock.json',
            'pnpm-lock.yaml',
            'yarn.lock',
            'go.mod',
            'go.sum',
            'pubspec.yaml',
            'pubspec.lock',
            'composer.lock',
            'build.gradle.kts',
            'Package.resolved',
            'conanfile.py',
            'uv.lock',
        ]

        for m in modern_manifests:
            res = MockResource('project/' + m)
            set_classification_flags(res)
            assert res.is_manifest, f'Failed manifest classification for: {m}'

    def test_archives_not_classified_as_manifest(self):
        import posixpath

        class MockResource:
            def __init__(self, path, is_top_level=True):
                self.path = path
                self.name = posixpath.basename(path)
                self.base_name = posixpath.splitext(self.name)[0]
                self.is_top_level = is_top_level
                self.package_data = []
                self.is_legal = False
                self.is_readme = False
                self.is_community = False
                self.is_manifest = False
                self.is_key_file = False

        archives = [
            'pkg.whl',
            'lib.jar',
            'app.gem',
            'binary.rpm',
            'bundle.deb',
            'archive.tar.gz',
            'dist.zip',
        ]

        for a in archives:
            res = MockResource('project/' + a)
            set_classification_flags(res)
            assert not res.is_manifest, f'Unexpected manifest classification for archive: {a}'

    def test_classify_cli_option(self):
        test_dir = self.get_test_loc('classify/cli')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('classify/cli.expected.json')
        run_scan_click(['--info', '--classify', '--json-pp', result_file, test_dir])
        check_json_scan(expected_file, result_file, remove_file_date=True, regen=REGEN_TEST_FIXTURES)

    def test_classify_with_package_data(self):
        test_dir = self.get_test_loc('score/jar')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('classify/with_package_data.expected.json')
        run_scan_click(['--info', '--classify', '--package', '--json-pp', result_file, test_dir])
        check_json_scan(expected_file, result_file, remove_file_date=True, regen=REGEN_TEST_FIXTURES)
