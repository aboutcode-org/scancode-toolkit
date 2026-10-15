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
from types import SimpleNamespace

from commoncode.testcase import FileDrivenTesting
from commoncode.resource import Codebase

from scancode.cli_test_utils import run_scan_click
from scancode.cli_test_utils import check_json_scan
from scancode_config import REGEN_TEST_FIXTURES
from summarycode.classify import set_classification_flags
from summarycode.classify import get_manifest_patterns
from summarycode.classify import is_manifest_path
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

    def test_manifest_patterns_include_active_handlers(self):
        suffixes, globs = get_manifest_patterns()

        assert '/cargo.lock' in suffixes
        assert '/go.mod' in suffixes
        assert '*conda*.yaml' in globs

    def test_manifest_paths_include_root_nested_and_globbed_formats(self):
        paths = (
            'Cargo.lock',
            'project/uv.lock',
            'project/go.mod',
            'project/conda-environment.yaml',
            'project/conda-meta/metadata.json',
        )
        for path in paths:
            assert is_manifest_path(path), path

        resource = SimpleNamespace(
            path='Cargo.lock',
            name='Cargo.lock',
            base_name='Cargo',
            is_top_level=True,
            package_data=[],
        )
        set_classification_flags(resource)
        assert resource.is_manifest
        assert resource.is_key_file

    def test_package_archives_are_not_classified_as_manifests(self):
        paths = (
            'project/package.whl',
            'project/library.jar',
            'project/archive.tar.gz',
            'project/unknown-file.txt',
        )
        for path in paths:
            assert not is_manifest_path(path), path

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
