#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

import os

from packagedcode import srcinfo
from packages_test_utils import PackageTester


class TestSrcinfo(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), "data")

    def test_parse_basic_metadata(self):
        location = self.get_test_loc("srcinfo/rust-basic/.SRCINFO")
        packages = list(srcinfo.SrcinfoHandler.parse(location))

        assert len(packages) == 1
        package = packages[0]
        assert package.type == "arch"
        assert package.name == "rust-basic"
        assert package.version == "1.0.0-1"
        assert package.homepage_url == "https://github.com/example/rust-basic"
        assert package.extracted_license_statement == "MIT"

    def test_parse_dependencies_and_architecture(self):
        location = self.get_test_loc("srcinfo/with-deps/.SRCINFO")
        package = next(srcinfo.SrcinfoHandler.parse(location))

        dependencies = {
            dependency.extracted_requirement: dependency for dependency in package.dependencies
        }
        assert dependencies["gcc-libs"].scope == "depends"
        assert dependencies["rust"].scope == "makedepends"
        assert dependencies["python: for scripts"].is_optional

    def test_parse_split_packages(self):
        location = self.get_test_loc("srcinfo/split-package/.SRCINFO")
        packages = list(srcinfo.SrcinfoHandler.parse(location))

        assert [package.name for package in packages] == ["rust-split-bin", "rust-split-lib"]
        assert all(package.version == "1.0.0-1" for package in packages)

    def test_parse_sources_and_checksums(self):
        location = self.get_test_loc("srcinfo/with-checksums/.SRCINFO")
        package = next(srcinfo.SrcinfoHandler.parse(location))

        assert package.extra_data["source"] == ["file1.tar.gz", "file2.tar.gz"]
        assert package.extra_data["sha256sums"] == ["abc123def456", "789ghi012jkl"]

    def test_parse_architecture_specific_dependencies(self):
        location = self.get_test_loc("srcinfo/arch-specific/.SRCINFO")
        package = next(srcinfo.SrcinfoHandler.parse(location))

        dependencies = {
            dependency.extracted_requirement: dependency for dependency in package.dependencies
        }
        assert dependencies["lib32-glibc"].scope == "depends_x86_64"
        assert dependencies["aarch64-specific-lib"].scope == "depends_aarch64"

    def test_parse_custom_license(self):
        location = self.get_test_loc("srcinfo/custom-license/.SRCINFO")
        package = next(srcinfo.SrcinfoHandler.parse(location))

        assert package.extracted_license_statement == "custom:vendor-license"
        assert package.declared_license_expression == "unknown-license-reference"
