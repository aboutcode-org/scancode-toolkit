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
    test_data_dir = os.path.join(os.path.dirname(__file__), "data/build")

    def test_end2end_scan_can_detect_bazel(self):
        test_file = self.get_test_loc("bazel/end2end")
        expected_file = self.get_test_loc("bazel/end2end-expected.json")
        result_file = self.get_temp_file("results.json")
        run_scan_click(["--package", test_file, "--json-pp", result_file])
        check_json_scan(expected_file, result_file, regen=REGEN_TEST_FIXTURES)

    def test_end2end_scan_can_detect_buck(self):
        test_file = self.get_test_loc("buck/end2end")
        expected_file = self.get_test_loc("buck/end2end-expected.json")
        result_file = self.get_temp_file("results.json")
        run_scan_click(["--package", test_file, "--json-pp", result_file])
        check_json_scan(expected_file, result_file, regen=REGEN_TEST_FIXTURES)

    def test_BazelPackage_parse(self):
        test_file = self.get_test_loc("bazel/parse/BUILD")
        result_packages = build.BazelBuildHandler.parse(test_file)
        expected_packages = [
            models.PackageData(
                name="hello-greet",
                type=build.BazelBuildHandler.default_package_type,
                datasource_id=build.BazelBuildHandler.datasource_id,
            ),
            models.PackageData(
                name="hello-world",
                type=build.BazelBuildHandler.default_package_type,
                datasource_id=build.BazelBuildHandler.datasource_id,
            ),
        ]
        compare_package_results(expected_packages, result_packages)

    def test_BuckPackage_parse(self):
        test_file = self.get_test_loc("buck/parse/BUCK")
        result_packages = build.BuckPackageHandler.parse(test_file)
        expected_packages = [
            models.PackageData(
                name="app",
                type=build.BuckPackageHandler.default_package_type,
                datasource_id=build.BuckPackageHandler.datasource_id,
            ),
            models.PackageData(
                name="app2",
                type=build.BuckPackageHandler.default_package_type,
                datasource_id=build.BuckPackageHandler.datasource_id,
            ),
        ]
        compare_package_results(expected_packages, result_packages)

    def test_BuckPackage_recognize_with_license(self):
        test_file = self.get_test_loc("buck/parse/license/BUCK")
        test_loc = self.get_test_loc("buck/parse/license/")
        result_package = list(build.BuckPackageHandler.parse(test_file))[0]
        codebase = Codebase(test_loc)
        resource = codebase.get_resource("license/BUCK")
        _detections, license_expression = build.get_license_detections_and_expression(
            result_package, resource, codebase
        )
        assert license_expression == "apache-2.0"

    def test_MetadataBzl_parse(self):
        test_file = self.get_test_loc("metadatabzl/METADATA.bzl")
        result_packages = build.BuckMetadataBzlHandler.parse(test_file, package_only=True)
        package_data = dict(
            datasource_id=build.BuckMetadataBzlHandler.datasource_id,
            type="github",
            name="example",
            version="0.0.1",
            extracted_license_statement=["BSD-3-Clause"],
            parties=[models.Party(type=models.party_org, name="oss_foundation", role="maintainer")],
            extra_data=dict(upstream_hash="deadbeef"),
            homepage_url="https://github.com/example/example",
        )
        expected_packages = [
            models.PackageData.from_data(package_data=package_data, package_only=True)
        ]
        compare_package_results(expected_packages, result_packages)

    def test_MetadataBzl_parse_with_package_url(self):
        test_file = self.get_test_loc("metadatabzl/with-package-url/METADATA.bzl")
        result_packages = build.BuckMetadataBzlHandler.parse(test_file, package_only=True)
        package_data = dict(
            datasource_id=build.BuckMetadataBzlHandler.datasource_id,
            name="animation",
            namespace="androidx.compose.animation",
            type="maven",
            version="0.0.1",
            extracted_license_statement=["BSD-3-Clause"],
            parties=[models.Party(type=models.party_org, name="oss_foundation", role="maintainer")],
            homepage_url="https://developer.android.com/jetpack/androidx/releases/compose-animation#0.0.1",
        )
        expected_packages = [
            models.PackageData.from_data(package_data=package_data, package_only=True)
        ]
        compare_package_results(expected_packages, result_packages)

    def test_MetadataBzl_recognize_new_format(self):
        test_file = self.get_test_loc("metadatabzl/new-format/METADATA.bzl")
        result_packages = build.BuckMetadataBzlHandler.parse(test_file, package_only=True)
        package_data = dict(
            datasource_id=build.BuckMetadataBzlHandler.datasource_id,
            type="github",
            name="example/example",
            version="0.0.1",
            extracted_license_statement="BSD-3-Clause",
            parties=[models.Party(type=models.party_org, name="example_org", role="maintainer")],
            download_url="",
            sha1="",
            homepage_url="https://github.com/example/example",
            vcs_url="https://github.com/example/example.git",
            extra_data=dict(vcs_commit_hash="deadbeef"),
        )
        expected_packages = [
            models.PackageData.from_data(package_data=package_data, package_only=True)
        ]
        compare_package_results(expected_packages, result_packages)


class TestBazelModuleHandler(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), "data")

    def test_parse_basic_module(self):
        location = self.get_test_loc("bazel_module/MODULE.bazel")
        results = list(build.BazelModuleHandler.parse(location))

        assert len(results) == 1
        pkg = results[0]

        # Package identity
        assert pkg.name == "my_sample_project"
        assert pkg.version == "0.5.0"
        assert pkg.type == "bazel"
        assert pkg.datasource_id == "bazel_module"

        # Total deps: 3 runtime + 1 dev = 4
        assert len(pkg.dependencies) == 4

    def test_parse_runtime_dependencies(self):
        location = self.get_test_loc("bazel_module/MODULE.bazel")
        results = list(build.BazelModuleHandler.parse(location))
        pkg = results[0]

        runtime_deps = [d for d in pkg.dependencies if d.scope == "dependencies"]
        assert len(runtime_deps) == 3

        dep_names = [d.purl for d in runtime_deps]
        assert "pkg:bazel/rules_python@0.24.0" in dep_names
        assert "pkg:bazel/rules_go@0.41.0" in dep_names

    def test_parse_dev_dependency(self):
        location = self.get_test_loc("bazel_module/MODULE.bazel")
        results = list(build.BazelModuleHandler.parse(location))
        pkg = results[0]

        dev_deps = [d for d in pkg.dependencies if d.scope == "dev"]
        assert len(dev_deps) == 1
        assert dev_deps[0].purl == "pkg:bazel/googletest@1.14.0"
        assert dev_deps[0].is_optional is True
        assert dev_deps[0].is_runtime is False

    def test_parse_module_without_version(self):
        location = self.get_test_loc("bazel_module/MODULE_no_version.bazel")
        results = list(build.BazelModuleHandler.parse(location))

        assert len(results) == 1
        pkg = results[0]
        assert pkg.name == "minimal_module"
        assert pkg.version is None

    def test_path_pattern_matches(self):
        handler = build.BazelModuleHandler
        assert handler.is_datafile("some/path/MODULE.bazel", _bare_filename=True)
        assert not handler.is_datafile("some/path/notMODULE.bazel", _bare_filename=True)
        assert not handler.is_datafile("some/path/WORKSPACE", _bare_filename=True)
        assert not handler.is_datafile("some/path/BUILD", _bare_filename=True)
