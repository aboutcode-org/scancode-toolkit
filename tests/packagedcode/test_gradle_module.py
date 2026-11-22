#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os.path

from packagedcode import gradle_module
from packagedcode.cache import get_cache
from packagedcode.recognize import recognize_package_data
from packages_test_utils import PackageTester
from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from scancode_config import REGEN_TEST_FIXTURES

# The two real-world fixtures below were downloaded from Maven Central for
# https://github.com/aboutcode-org/scancode-toolkit/issues/3522:
# - https://repo1.maven.org/maven2/com/squareup/retrofit2/converter-moshi/2.11.0/converter-moshi-2.11.0.module
# - https://repo1.maven.org/maven2/com/github/ben-manes/caffeine/caffeine/3.2.0/caffeine-3.2.0.module
# The remaining fixtures are synthetic edge cases hand-written for this
# handler, following the field shapes of the Gradle Module Metadata format
# (GradleModuleMetadataParser in the Gradle source tree).


class TestGradleModule(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_is_datafile_module(self):
        test_file = self.get_test_loc('gradle_module/converter-moshi-2.11.0/converter-moshi-2.11.0.module')
        assert gradle_module.GradleModuleMetadataHandler.is_datafile(test_file)

    def test_is_datafile_caffeine_module(self):
        test_file = self.get_test_loc('gradle_module/caffeine-3.2.0/caffeine-3.2.0.module')
        assert gradle_module.GradleModuleMetadataHandler.is_datafile(test_file)

    def test_is_not_datafile_not_a_module(self):
        # A JSON file without formatVersion/component is not Gradle Module
        # Metadata, even though it has a .module extension.
        test_file = self.get_test_loc('gradle_module/not-a-module/not-a-module.module')
        assert not gradle_module.GradleModuleMetadataHandler.is_datafile(test_file)

    def test_is_not_datafile_malformed(self):
        test_file = self.get_test_loc('gradle_module/malformed/malformed.module')
        assert not gradle_module.GradleModuleMetadataHandler.is_datafile(test_file)

    def test_is_not_datafile_pom(self):
        test_file = self.get_test_loc('maven2/pom-generic/pom.xml')
        assert not gradle_module.GradleModuleMetadataHandler.is_datafile(test_file)

    def test_parse_converter_moshi(self):
        test_file = self.get_test_loc('gradle_module/converter-moshi-2.11.0/converter-moshi-2.11.0.module')
        expected_loc = self.get_test_loc(
            'gradle_module/converter-moshi-2.11.0/converter-moshi-2.11.0.module.package.json'
        )
        packages = gradle_module.GradleModuleMetadataHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_caffeine(self):
        test_file = self.get_test_loc('gradle_module/caffeine-3.2.0/caffeine-3.2.0.module')
        expected_loc = self.get_test_loc(
            'gradle_module/caffeine-3.2.0/caffeine-3.2.0.module.package.json'
        )
        packages = gradle_module.GradleModuleMetadataHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_rich_versions(self):
        test_file = self.get_test_loc('gradle_module/rich-versions/rich-versions.module')
        expected_loc = self.get_test_loc(
            'gradle_module/rich-versions/rich-versions.module.package.json'
        )
        packages = gradle_module.GradleModuleMetadataHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_capabilities_and_available_at(self):
        test_file = self.get_test_loc(
            'gradle_module/capabilities-and-available-at/capabilities-and-available-at.module'
        )
        expected_loc = self.get_test_loc(
            'gradle_module/capabilities-and-available-at/capabilities-and-available-at.module.package.json'
        )
        packages = gradle_module.GradleModuleMetadataHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_multiplatform(self):
        test_file = self.get_test_loc('gradle_module/multiplatform/multiplatform.module')
        expected_loc = self.get_test_loc(
            'gradle_module/multiplatform/multiplatform.module.package.json'
        )
        packages = gradle_module.GradleModuleMetadataHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_no_variants(self):
        test_file = self.get_test_loc('gradle_module/no-variants/no-variants.module')
        expected_loc = self.get_test_loc(
            'gradle_module/no-variants/no-variants.module.package.json'
        )
        packages = gradle_module.GradleModuleMetadataHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_minimal(self):
        test_file = self.get_test_loc('gradle_module/minimal/minimal.module')
        expected_loc = self.get_test_loc(
            'gradle_module/minimal/minimal.module.package.json'
        )
        packages = gradle_module.GradleModuleMetadataHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_format_1_0(self):
        test_file = self.get_test_loc('gradle_module/format-1.0/format-1.0.module')
        expected_loc = self.get_test_loc(
            'gradle_module/format-1.0/format-1.0.module.package.json'
        )
        packages = gradle_module.GradleModuleMetadataHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_not_a_module_yields_nothing(self):
        test_file = self.get_test_loc('gradle_module/not-a-module/not-a-module.module')
        packages = list(gradle_module.GradleModuleMetadataHandler.parse(test_file))
        assert packages == []

    def test_parse_malformed_yields_nothing(self):
        test_file = self.get_test_loc('gradle_module/malformed/malformed.module')
        packages = list(gradle_module.GradleModuleMetadataHandler.parse(test_file))
        assert packages == []

    def test_parse_converter_moshi_assertions(self):
        test_file = self.get_test_loc('gradle_module/converter-moshi-2.11.0/converter-moshi-2.11.0.module')
        package = next(gradle_module.GradleModuleMetadataHandler.parse(test_file))
        data = package.to_dict()
        assert data['type'] == 'maven'
        assert data['namespace'] == 'com.squareup.retrofit2'
        assert data['name'] == 'converter-moshi'
        assert data['version'] == '2.11.0'
        assert data['purl'] == 'pkg:maven/com.squareup.retrofit2/converter-moshi@2.11.0'
        assert data['datasource_id'] == 'gradle_module_metadata'
        assert data['primary_language'] == 'Java'
        # .module files carry no description, homepage or license.
        assert data['description'] is None
        assert data['homepage_url'] is None
        assert data['declared_license_expression'] is None
        # Main jar: apiElements and runtimeElements carry the same file.
        assert data['download_url'] == (
            'https://repo1.maven.org/maven2/com/squareup/retrofit2/converter-moshi/'
            '2.11.0/converter-moshi-2.11.0.jar'
        )
        assert data['size'] == 5292
        assert data['sha256'] == 'dbfae9dbde0b61e5c5671648c8d9fd486efae9ad07d573ed01bd0de4688d9b2c'
        assert data['sha512'] == (
            '0889ca2b7b016684601f1d183d0c241531d219e5011a04a6f386f8510c018e380c68cdc08a9a80787305cb69509a5b9c9036140d8f10281881677104bac6d6ae'
        )
        assert data['source_packages'] == [
            'pkg:maven/com.squareup.retrofit2/converter-moshi@2.11.0?classifier=sources'
        ]
        assert data['extra_data']['format_version'] == '1.1'
        assert data['extra_data']['gradle_version'] == '8.7'
        assert data['extra_data']['component_attributes'] == {'org.gradle.status': 'release'}
        # Dependencies are deduplicated across apiElements/runtimeElements:
        # exactly two entries, runtime wins for scope.
        dependencies = data['dependencies']
        assert len(dependencies) == 2
        assert dependencies[0]['purl'] == 'pkg:maven/com.squareup.retrofit2/retrofit@2.11.0'
        assert dependencies[0]['extracted_requirement'] == '2.11.0'
        assert dependencies[0]['is_pinned'] is True
        assert dependencies[0]['scope'] == 'runtimeElements'
        assert dependencies[0]['is_runtime'] is True
        assert dependencies[0]['extra_data']['variants'] == ['apiElements', 'runtimeElements']
        assert dependencies[1]['purl'] == 'pkg:maven/com.squareup.moshi/moshi@1.15.1'
        assert dependencies[1]['extracted_requirement'] == '1.15.1'
        assert dependencies[1]['is_pinned'] is True

    def test_parse_caffeine_assertions(self):
        test_file = self.get_test_loc('gradle_module/caffeine-3.2.0/caffeine-3.2.0.module')
        package = next(gradle_module.GradleModuleMetadataHandler.parse(test_file))
        data = package.to_dict()
        assert data['purl'] == 'pkg:maven/com.github.ben-manes.caffeine/caffeine@3.2.0'
        assert data['size'] == 906581
        assert data['sha256'] == 'ec411dfdf0c03f25218648ce89861630b71680e5858a9a7278ebac8e55cab3d7'
        assert data['extra_data']['gradle_version'] == '8.12'
        assert len(data['extra_data']['variants']) == 4
        assert data['extra_data']['variants']['apiElements']['attributes'][
            'org.gradle.jvm.version'
        ] == 11
        dependencies = data['dependencies']
        assert len(dependencies) == 2
        assert dependencies[0]['purl'] == 'pkg:maven/org.jspecify/jspecify@1.0.0'
        assert dependencies[1]['purl'] == 'pkg:maven/com.google.errorprone/error_prone_annotations@2.36.0'

    def test_parse_rich_versions_assertions(self):
        test_file = self.get_test_loc('gradle_module/rich-versions/rich-versions.module')
        package = next(gradle_module.GradleModuleMetadataHandler.parse(test_file))
        data = package.to_dict()
        dependencies = {dep['purl']: dep for dep in data['dependencies']}
        assert len(dependencies) == 6

        prefers = dependencies['pkg:maven/com.example/prefers-lib']
        assert prefers['extracted_requirement'] == '2.0.0'
        assert prefers['is_pinned'] is False
        assert prefers['scope'] == 'runtimeElements'
        assert prefers['is_runtime'] is True
        assert prefers['extra_data']['version'] == {'prefers': '2.0.0'}
        assert prefers['extra_data']['variants'] == ['apiElements', 'runtimeElements']

        strictly = dependencies['pkg:maven/com.example/strictly-lib@3.0.0']
        assert strictly['extracted_requirement'] == '3.0.0'
        assert strictly['is_pinned'] is True
        assert strictly['scope'] == 'apiElements'
        assert strictly['is_runtime'] is False

        plain = dependencies['pkg:maven/com.example/plain-lib@4.0.0']
        assert plain['extracted_requirement'] == '4.0.0'
        assert plain['is_pinned'] is True

        no_version = dependencies['pkg:maven/com.example/no-version-lib']
        assert no_version['extracted_requirement'] is None
        assert no_version['is_pinned'] is False

        rejects = dependencies['pkg:maven/com.example/rejects-lib@5.0.0']
        assert rejects['extracted_requirement'] == '5.0.0'
        assert rejects['is_pinned'] is True
        assert rejects['extra_data']['rejects'] == ['5.0.1', '5.0.2']
        assert rejects['extra_data']['reason'] == 'needed for tests'
        assert rejects['extra_data']['excludes'] == [
            {'group': 'com.example', 'module': 'excluded-lib'}
        ]

        runtime_only = dependencies['pkg:maven/com.example/runtime-only-lib@6.0.0']
        assert runtime_only['scope'] == 'runtimeElements'
        assert runtime_only['is_runtime'] is True

    def test_parse_capabilities_and_available_at_assertions(self):
        test_file = self.get_test_loc(
            'gradle_module/capabilities-and-available-at/capabilities-and-available-at.module'
        )
        package = next(gradle_module.GradleModuleMetadataHandler.parse(test_file))
        data = package.to_dict()
        assert data['purl'] == 'pkg:maven/com.example/capabilities-demo@1.0.0'
        assert data['dependencies'] == []
        variants = data['extra_data']['variants']
        assert variants['apiElements']['capabilities'] == [
            {'group': 'com.example', 'name': 'capabilities-demo', 'version': '1.0.0'}
        ]
        assert variants['otherPlatform']['available-at'] == {
            'url': 'https://example.com/other',
            'group': 'com.example',
            'name': 'capabilities-demo-other',
            'version': '1.0.0',
        }

    def test_parse_multiplatform_assertions(self):
        test_file = self.get_test_loc('gradle_module/multiplatform/multiplatform.module')
        package = next(gradle_module.GradleModuleMetadataHandler.parse(test_file))
        data = package.to_dict()
        assert data['purl'] == 'pkg:maven/org.example/multiplatform-lib@2.0.0'
        dependencies = data['dependencies']
        assert len(dependencies) == 3
        shared = [d for d in dependencies if d['purl'] == 'pkg:maven/com.example/shared-lib@1.0.0']
        assert len(shared) == 1
        assert shared[0]['extra_data']['variants'] == [
            'jvmApiElements',
            'jsApiElements',
            'metadataElements',
        ]
        # The main artifact falls back to the first variant shipping a jar.
        assert data['download_url'] == (
            'https://repo1.maven.org/maven2/org/example/multiplatform-lib/2.0.0/'
            'multiplatform-lib-jvm-2.0.0.jar'
        )
        assert data['size'] == 5000

    def test_parse_no_variants_assertions(self):
        test_file = self.get_test_loc('gradle_module/no-variants/no-variants.module')
        package = next(gradle_module.GradleModuleMetadataHandler.parse(test_file))
        data = package.to_dict()
        assert data['purl'] == 'pkg:maven/com.example/no-variants@1.0.0'
        assert data['dependencies'] == []
        assert data['download_url'] is None
        assert data['size'] is None

    def test_parse_format_1_0_assertions(self):
        test_file = self.get_test_loc('gradle_module/format-1.0/format-1.0.module')
        package = next(gradle_module.GradleModuleMetadataHandler.parse(test_file))
        data = package.to_dict()
        assert data['purl'] == 'pkg:maven/com.example/format-one@1.0.0'
        assert data['extra_data']['format_version'] == '1.0'
        # 1.0 files carry sha1/md5 only: no sha256/sha512.
        assert data['sha1'] == 'aabbccddeeff00112233445566778899aabbccdd'
        assert data['sha256'] is None
        assert data['sha512'] is None
        assert len(data['dependencies']) == 1

    def test_parse_rejects_unknown_format_version(self):
        module_data = {
            'formatVersion': '2.0',
            'component': {'group': 'com.example', 'module': 'x', 'version': '1.0.0'},
        }
        assert gradle_module.GradleModuleMetadataHandler._parse(module_data) is None

    def test_parse_rejects_missing_component_coordinates(self):
        assert gradle_module.GradleModuleMetadataHandler._parse({}) is None
        assert gradle_module.GradleModuleMetadataHandler._parse(
            {'formatVersion': '1.1', 'component': {'module': 'x'}}
        ) is None
        assert gradle_module.GradleModuleMetadataHandler._parse(None) is None

    def test_recognize_gradle_module(self):
        # Force a rebuild of the on-disk pattern index so the newly
        # registered handler is visible to recognition.
        get_cache(force=True)
        test_file = self.get_test_loc('gradle_module/converter-moshi-2.11.0/converter-moshi-2.11.0.module')
        packages = recognize_package_data(test_file)
        assert packages
        assert packages[0].datasource_id == 'gradle_module_metadata'
        assert packages[0].type == 'maven'

    def test_end2end_scan_gradle_module(self):
        test_file = self.get_test_loc('gradle_module/converter-moshi-2.11.0/converter-moshi-2.11.0.module')
        expected_file = self.get_test_loc(
            'gradle_module/converter-moshi-2.11.0/converter-moshi-2.11.0.module-expected.json'
        )
        result_file = self.get_temp_file()
        run_scan_click(['--package', test_file, '--json-pp', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_end2end_scan_gradle_module_package_only(self):
        test_file = self.get_test_loc('gradle_module/converter-moshi-2.11.0/converter-moshi-2.11.0.module')
        expected_file = self.get_test_loc(
            'gradle_module/converter-moshi-2.11.0/converter-moshi-2.11.0.module-package-only-expected.json'
        )
        result_file = self.get_temp_file('results.json')
        run_scan_click(['--package-only', test_file, '--json-pp', result_file])
        check_json_scan(expected_file, result_file, regen=REGEN_TEST_FIXTURES)
