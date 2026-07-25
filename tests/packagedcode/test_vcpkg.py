#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os.path

from packages_test_utils import PackageTester

from packagedcode import vcpkg
from scancode_config import REGEN_TEST_FIXTURES


class TestVcpkgHandler(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), "data")

    def test_parse_libgeotiff_control(self):
        test_file = self.get_test_loc("vcpkg/ports/libgeotiff/manifest/CONTROL")
        expected_loc = self.get_test_loc(
            "vcpkg/ports/libgeotiff/CONTROL-expected.json",
            must_exist=False,
        )
        packages = vcpkg.VcpkgControlHandler.parse(test_file)
        self.check_packages_data(
            packages,
            expected_loc,
            must_exist=False,
            regen=REGEN_TEST_FIXTURES,
        )

    def test_parse_curl_control_with_port_version(self):
        test_file = self.get_test_loc("vcpkg/ports/curl/manifest/CONTROL")
        expected_loc = self.get_test_loc(
            "vcpkg/ports/curl/CONTROL-expected.json",
            must_exist=False,
        )
        packages = list(vcpkg.VcpkgControlHandler.parse(test_file))

        assert packages[0].version == "7.73.0"
        assert packages[0].qualifiers == {"port_version": "1"}
        assert packages[0].purl == "pkg:vcpkg/curl@7.73.0?port_version=1"
        assert [dependency.purl for dependency in packages[0].dependencies] == [
            "pkg:vcpkg/zlib"
        ]
        self.check_packages_data(
            packages,
            expected_loc,
            must_exist=False,
            regen=REGEN_TEST_FIXTURES,
        )

    def test_parse_control_license(self):
        test_file = self.get_test_loc("vcpkg/ports/licensed/manifest/CONTROL")
        package = list(vcpkg.VcpkgControlHandler.parse(test_file))[0]

        assert package.extracted_license_statement == "MIT"

    def test_parse_libgeotiff_portfile(self):
        test_file = self.get_test_loc("vcpkg/ports/libgeotiff/manifest/portfile.cmake")
        expected_loc = self.get_test_loc(
            "vcpkg/ports/libgeotiff/portfile.cmake-expected.json",
            must_exist=False,
        )
        packages = list(vcpkg.VcpkgPortfileHandler.parse(test_file))

        assert packages[0].version is None
        self.check_packages_data(
            packages,
            expected_loc,
            must_exist=False,
            regen=REGEN_TEST_FIXTURES,
        )

    def test_parse_rapidjson_portfile(self):
        test_file = self.get_test_loc("vcpkg/ports/rapidjson/manifest/portfile.cmake")
        expected_loc = self.get_test_loc(
            "vcpkg/ports/rapidjson/portfile.cmake-expected.json",
            must_exist=False,
        )
        packages = list(vcpkg.VcpkgPortfileHandler.parse(test_file))

        assert packages[0].version == "24b5e7a8b27f42fa16b96fc70aade9106cf7102f"
        self.check_packages_data(
            packages,
            expected_loc,
            must_exist=False,
            regen=REGEN_TEST_FIXTURES,
        )

    def test_parse_gitlab_portfile(self):
        test_file = self.get_test_loc("vcpkg/ports/gitlab/manifest/portfile.cmake")
        package = list(vcpkg.VcpkgPortfileHandler.parse(test_file))[0]

        assert package.vcs_url == "https://gitlab.example.com/group/project"
        assert package.version == "v1.2.3"
        assert package.sha512 == "gitlab-checksum"

    def test_parse_git_portfile(self):
        test_file = self.get_test_loc("vcpkg/ports/git/manifest/portfile.cmake")
        package = list(vcpkg.VcpkgPortfileHandler.parse(test_file))[0]

        assert package.vcs_url == "https://example.com/project.git"
        assert package.version == "abc123"
        assert package.sha512 == "git-checksum"

    def test_parse_distfile_uses_first_literal_url(self):
        test_file = self.get_test_loc("vcpkg/ports/distfile/manifest/portfile.cmake")
        package = list(vcpkg.VcpkgPortfileHandler.parse(test_file))[0]

        assert package.download_url == "https://example.com/project-1.0.tar.gz"
        assert package.sha512 == "distfile-checksum"
