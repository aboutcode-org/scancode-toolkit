#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import json
import os.path

from commoncode import testcase
from packagedcode.maven import GradleModuleMetadataHandler


class TestGradleModuleMetadataHandler(testcase.FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), "data")

    def test_parse_opentest4j_1_3_0_module_basic_fields(self):
        test_file = self.get_test_loc(
            "gradle_module_metadata/opentest4j-1.3.0/opentest4j-1.3.0.module"
        )

        packages = list(GradleModuleMetadataHandler.parse(test_file))
        assert len(packages) == 1
        pkg = packages[0]

        assert pkg.datasource_id == "gradle_module_metadata"
        assert pkg.type == "maven"
        assert pkg.primary_language == "Java"

        assert pkg.namespace == "org.opentest4j"
        assert pkg.name == "opentest4j"
        assert pkg.version == "1.3.0"

        assert pkg.repository_homepage_url == (
            "https://repo1.maven.org/maven2/org/opentest4j/opentest4j/1.3.0/"
        )
        assert pkg.repository_download_url == (
            "https://repo1.maven.org/maven2/org/opentest4j/opentest4j/1.3.0/opentest4j-1.3.0.jar"
        )
        assert pkg.api_data_url == (
            "https://repo1.maven.org/maven2/org/opentest4j/opentest4j/1.3.0/opentest4j-1.3.0.module"
        )

        # From apiElements/runtimeElements file checksums
        assert pkg.size == 14304
        assert pkg.sha1 == "152ea56b3a72f655d4fd677fc0ef2596c3dd5e6e"
        assert pkg.sha256 == "48e2df636cab6563ced64dcdff8abb2355627cb236ef0bf37598682ddf742f1b"
        assert pkg.sha512 == (
            "78fc698a7871bb50305e3657893c10500595f043348d875f57bc39ca4a6a51eda3967b7c8c8a7ec3e8f85f2171bca4aa98823e912e416e87e81c6ba5b70a37c3"
        )
        assert pkg.md5 == "03c404f727531f3fd3b4c73997899327"

        # Extra data should include gradle metadata
        assert pkg.extra_data.get("format_version") == "1.1"
        assert pkg.extra_data.get("gradle_version") == "8.2"
        assert pkg.extra_data.get("gradle_status") == "release"

        component_attributes = pkg.extra_data.get("component_attributes") or {}
        assert component_attributes.get("org.gradle.status") == "release"

    def test_parse_opentest4j_1_3_0_module_variants_metadata(self):
        test_file = self.get_test_loc(
            "gradle_module_metadata/opentest4j-1.3.0/opentest4j-1.3.0.module"
        )

        packages = list(GradleModuleMetadataHandler.parse(test_file))
        assert len(packages) == 1
        pkg = packages[0]

        variants = pkg.extra_data.get("variants") or []
        assert variants, "Expected variants in extra_data"

        variant_names = {v.get("name") for v in variants}
        assert "apiElements" in variant_names
        assert "runtimeElements" in variant_names
        assert "javadocElements" in variant_names
        assert "sourcesElements" in variant_names

        # Ensure at least the apiElements variant contains expected file details
        api_variants = [v for v in variants if v.get("name") == "apiElements"]
        assert len(api_variants) == 1
        api_variant = api_variants[0]

        api_files = api_variant.get("files") or []
        assert api_files, "Expected files list for apiElements variant"
        assert api_files[0].get("name") == "opentest4j-1.3.0.jar"
        assert api_files[0].get("url") == "opentest4j-1.3.0.jar"
        assert api_files[0].get("size") == 14304

    def test_parse_returns_nothing_when_component_is_missing_required_fields(self):
        # Minimal invalid Gradle module metadata: missing group/module/version
        invalid_module = {
            "formatVersion": "1.1",
            "component": {
                # 'group': 'org.example',  # missing
                "module": "demo",
                "version": "1.0.0",
            },
            "variants": [],
        }

        test_dir = self.get_temp_dir()
        test_file = os.path.join(test_dir, "invalid.module")
        with open(test_file, "w", encoding="utf-8") as f:
            json.dump(invalid_module, f)

        packages = list(GradleModuleMetadataHandler.parse(test_file))
        assert packages == []

    def test_description_contains_status_when_present(self):
        test_file = self.get_test_loc(
            "gradle_module_metadata/opentest4j-1.3.0/opentest4j-1.3.0.module"
        )
        packages = list(GradleModuleMetadataHandler.parse(test_file))
        assert len(packages) == 1
        pkg = packages[0]

        # Format is defined by _build_description()
        assert pkg.description == "opentest4j version 1.3.0 (status: release)"
