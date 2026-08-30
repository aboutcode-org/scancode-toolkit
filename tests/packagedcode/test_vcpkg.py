# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import json
import os.path

from packages_test_utils import PackageTester

from packagedcode import APPLICATION_PACKAGE_DATAFILE_HANDLERS
from packagedcode import HANDLER_BY_DATASOURCE_ID
from packagedcode import vcpkg
from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from scancode_config import REGEN_TEST_FIXTURES


class TestVcpkgHandler(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), "data")

    def test_vcpkg_handlers_are_registered(self):
        handlers = (
            vcpkg.VcpkgJsonHandler,
            vcpkg.VcpkgControlHandler,
            vcpkg.VcpkgPortfileHandler,
        )
        for handler in handlers:
            assert handler in APPLICATION_PACKAGE_DATAFILE_HANDLERS
            assert HANDLER_BY_DATASOURCE_ID[handler.datasource_id] is handler

    def test_parse_named_json_manifest(self):
        test_file = self.get_test_loc("vcpkg/json/named-port/vcpkg.json")
        package = list(vcpkg.VcpkgJsonHandler.parse(test_file))[0]

        assert package.purl == "pkg:vcpkg/sample-port@1.2.3?port_version=2"
        assert package.description == (
            "A sample vcpkg port.\nUsed to exercise manifest metadata."
        )
        assert package.extracted_license_statement == "MIT"
        assert [(party.name, party.email) for party in package.parties] == [
            ("Alice Example", "alice@example.com"),
            ("Bob Example", None),
        ]
        assert package.extra_data["version_scheme"] == "version-semver"
        assert package.extra_data["port_version"] == 2
        assert package.extra_data["overrides"] == [{"name": "zlib", "version": "1.3.1"}]
        assert package.extra_data["documentation"] == (
            "https://example.com/sample-port/docs"
        )
        assert package.extra_data["supports"] == "!uwp"
        assert package.extra_data["default-features"] == ["tls"]
        assert package.extra_data["builtin-baseline"] == "0123456789abcdef"
        assert package.extra_data["configuration"] == {"overlay-ports": ["ports"]}

        dependencies = {
            dependency.purl: dependency for dependency in package.dependencies
        }
        assert dependencies["pkg:vcpkg/zlib"].scope == "dependencies"
        assert dependencies["pkg:vcpkg/cmake"].scope == "host"
        assert not dependencies["pkg:vcpkg/cmake"].is_runtime
        assert dependencies["pkg:vcpkg/curl"].extracted_requirement == ">= 8.0.0#1"
        assert dependencies["pkg:vcpkg/curl"].extra_data == {
            "features": [
                "openssl",
                {"name": "schannel", "platform": "windows"},
            ],
            "default-features": False,
            "platform": "!uwp",
        }
        assert dependencies["pkg:vcpkg/python3"].scope == "feature:tools"
        assert dependencies["pkg:vcpkg/python3"].is_optional
        assert not dependencies["pkg:vcpkg/python3"].is_runtime

    def test_parse_application_json_manifest_without_identity(self):
        test_file = self.get_test_loc("vcpkg/json/application-manifest/vcpkg.json")
        package = list(vcpkg.VcpkgJsonHandler.parse(test_file))[0]

        assert package.name is None
        assert package.version is None
        assert package.purl is None
        assert package.is_private
        assert [dependency.purl for dependency in package.dependencies] == [
            "pkg:vcpkg/fmt",
            "pkg:vcpkg/ninja",
        ]

    def test_json_version_selection_is_deterministic(self):
        for version_field in vcpkg.VERSION_FIELDS:
            version, extra_data = vcpkg.get_version_data({version_field: "1.2.3"})
            assert version == "1.2.3"
            assert extra_data == {"version_scheme": version_field}

        manifest = {
            "version": "1",
            "version-semver": "2.0.0",
        }
        version, extra_data = vcpkg.get_version_data(manifest)

        assert version == "1"
        assert extra_data == {
            "version_scheme": "version",
            "version_fields": manifest,
        }

    def test_json_port_version_zero_is_not_a_qualifier(self):
        qualifiers, extra_data = vcpkg.get_port_version_data({"port-version": 0})

        assert qualifiers == {}
        assert extra_data == {"port_version": 0}

    def test_json_invalid_root_yields_no_package_data(self):
        test_file = self.get_test_loc("vcpkg/json/invalid-root/vcpkg.json")

        assert list(vcpkg.VcpkgJsonHandler.parse(test_file)) == []

    def test_json_malformed_syntax_is_not_silently_ignored(self):
        test_file = self.get_test_loc("vcpkg/json/malformed/vcpkg.json")

        with self.assertRaises(json.JSONDecodeError):
            list(vcpkg.VcpkgJsonHandler.parse(test_file))

    def test_control_recognition_requires_vcpkg_fields(self):
        vcpkg_control = self.get_test_loc("vcpkg/control/feature-stanzas/CONTROL")
        debian_control = self.get_test_loc("vcpkg/control/not-vcpkg/CONTROL")

        assert vcpkg.VcpkgControlHandler.is_datafile(vcpkg_control)
        assert not vcpkg.VcpkgControlHandler.is_datafile(debian_control)

    def test_parse_control_feature_stanzas_and_nested_dependencies(self):
        test_file = self.get_test_loc("vcpkg/control/feature-stanzas/CONTROL")
        package = list(vcpkg.VcpkgControlHandler.parse(test_file))[0]

        assert package.purl == "pkg:vcpkg/feature-port@3.4.5"
        assert package.qualifiers == {}
        assert package.extra_data["port_version"] == "0"
        assert package.extra_data["features"]["tools"] == {
            "description": "Build optional tools."
        }

        dependencies = package.dependencies
        assert [dependency.purl for dependency in dependencies] == [
            "pkg:vcpkg/curl",
            "pkg:vcpkg/zlib",
            "pkg:vcpkg/python3",
            "pkg:vcpkg/boost",
        ]
        assert dependencies[0].extra_data == {
            "features": ["core", "openssl"],
            "platform": "!windows",
        }
        assert dependencies[1].extra_data == {"platform": "windows & (!uwp | x64)"}
        assert dependencies[3].scope == "feature:tools"
        assert dependencies[3].is_optional
        assert dependencies[3].extra_data == {
            "features": ["filesystem", "program-options"],
            "platform": "!arm",
        }

    def test_split_control_dependencies_preserves_nested_commas(self):
        dependencies = (
            "curl[core,openssl] (!windows), "
            "zlib (windows & (!uwp | x64)), "
            "boost[filesystem,program-options]"
        )
        assert vcpkg.split_control_dependencies(dependencies) == [
            "curl[core,openssl] (!windows)",
            "zlib (windows & (!uwp | x64))",
            "boost[filesystem,program-options]",
        ]

    def test_parse_libgeotiff_control(self):
        test_file = self.get_test_loc("vcpkg/ports/libgeotiff/manifest/CONTROL")
        expected_loc = self.get_test_loc("vcpkg/ports/libgeotiff/CONTROL-expected.json")
        packages = vcpkg.VcpkgControlHandler.parse(test_file)

        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_curl_control_with_port_version(self):
        test_file = self.get_test_loc("vcpkg/ports/curl/manifest/CONTROL")
        package = list(vcpkg.VcpkgControlHandler.parse(test_file))[0]

        assert package.version == "7.73.0"
        assert package.qualifiers == {"port_version": "1"}
        assert package.purl == "pkg:vcpkg/curl@7.73.0?port_version=1"
        assert package.dependencies[0].purl == "pkg:vcpkg/zlib"
        assert len(package.dependencies) == 6

    def test_parse_control_license(self):
        test_file = self.get_test_loc("vcpkg/ports/licensed/manifest/CONTROL")
        package = list(vcpkg.VcpkgControlHandler.parse(test_file))[0]

        assert package.extracted_license_statement == "MIT"

    def test_parse_libgeotiff_portfile(self):
        test_file = self.get_test_loc("vcpkg/ports/libgeotiff/manifest/portfile.cmake")
        expected_loc = self.get_test_loc(
            "vcpkg/ports/libgeotiff/portfile.cmake-expected.json"
        )
        packages = list(vcpkg.VcpkgPortfileHandler.parse(test_file))

        assert packages[0].version is None
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_rapidjson_portfile_keeps_ref_as_source_data(self):
        test_file = self.get_test_loc("vcpkg/ports/rapidjson/manifest/portfile.cmake")
        expected_loc = self.get_test_loc(
            "vcpkg/ports/rapidjson/portfile.cmake-expected.json"
        )
        packages = list(vcpkg.VcpkgPortfileHandler.parse(test_file))
        package = packages[0]

        assert package.version is None
        assert package.extra_data["sources"][0]["reference"] == (
            "24b5e7a8b27f42fa16b96fc70aade9106cf7102f"
        )
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_portfile_parser_is_balanced_comment_aware_and_literal_only(self):
        test_file = self.get_test_loc("vcpkg/portfiles/adversarial/portfile.cmake")
        package = list(vcpkg.VcpkgPortfileHandler.parse(test_file))[0]
        sources = package.extra_data["sources"]

        assert [source["macro"] for source in sources] == [
            "vcpkg_download_distfile",
            "vcpkg_from_github",
            "vcpkg_from_bitbucket",
        ]
        assert sources[0]["urls"] == [
            "https://downloads.example.com/source.tar.gz",
            "https://mirror.example.com/source.tar.gz",
        ]
        assert "reference" not in sources[1]
        assert sources[1]["sha512"] == "github-sha512"
        assert sources[2]["sha512"] == "bitbucket-sha512"
        assert package.download_url == "https://downloads.example.com/source.tar.gz"
        assert package.sha512 == "distfile-sha512"

    def test_portfile_parser_supports_each_allowlisted_macro(self):
        content = """
            vcpkg_from_github(REPO a/github REF v1 SHA512 one)
            vcpkg_from_gitlab(REPO a/gitlab REF v2 SHA512 two)
            vcpkg_from_git(URL https://example.com/git REF abc)
            vcpkg_from_bitbucket(REPO a/bitbucket REF v3 SHA512 three)
            vcpkg_from_sourceforge(REPO project/path REF 1 FILENAME a.tgz SHA512 four)
            vcpkg_download_sourceforge(OUT REPO project/path REF 2 FILENAME b.tgz SHA512 five)
            vcpkg_download_distfile(OUT URLS https://example.com/a.tgz SHA512 six)
        """
        sources = vcpkg.get_source_data(content)["sources"]

        assert {source["macro"] for source in sources} == vcpkg.SOURCE_MACROS
        assert sources[2]["vcs_url"] == "https://example.com/git.git@abc"
        assert sources[4]["download_url"] == (
            "https://sourceforge.net/projects/project/files/path/1/a.tgz/download"
        )


class TestVcpkgEndToEnd(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), "data")

    def scan_packages(self, test_data_path):
        test_dir = self.get_test_loc(test_data_path)
        result_file = self.get_temp_file("json")
        run_scan_click(
            [
                "--package",
                "--strip-root",
                "--processes",
                "-1",
                test_dir,
                "--json",
                result_file,
            ]
        )
        with open(result_file, encoding="utf-8") as result:
            return result_file, json.load(result)

    def test_package_scan_assembles_one_vcpkg_package(self):
        result_file, scan = self.scan_packages("vcpkg/assembly/json-control-portfile")
        expected_file = self.get_test_loc(
            "vcpkg/assembly/json-control-portfile-expected.json"
        )
        assert [package["purl"] for package in scan["packages"]] == [
            "pkg:vcpkg/assembly-port@2.0"
        ]
        assert scan["dependencies"]
        assert any(file["package_data"] for file in scan["files"])

        check_json_scan(
            expected_file,
            result_file,
            remove_uuid=True,
            regen=REGEN_TEST_FIXTURES,
        )

    def test_package_scan_application_manifest_yields_only_dependencies(self):
        _result_file, scan = self.scan_packages("vcpkg/json/application-manifest")

        assert scan["packages"] == []
        assert [dependency["purl"] for dependency in scan["dependencies"]] == [
            "pkg:vcpkg/fmt",
            "pkg:vcpkg/ninja",
        ]
        assert scan["files"][0]["package_data"][0]["is_private"]

    def test_package_scan_control_and_portfile_assembles_one_package(self):
        _result_file, scan = self.scan_packages("vcpkg/ports/libgeotiff/manifest")
        packages = [
            package for package in scan["packages"] if package["type"] == "vcpkg"
        ]

        assert [package["purl"] for package in packages] == [
            "pkg:vcpkg/libgeotiff@1.4.2-10"
        ]
        package = packages[0]
        assert package["vcs_url"] == "https://github.com/OSGeo/libgeotiff.git"
        assert package["datasource_ids"] == ["vcpkg_control", "vcpkg_portfile"]

    def test_package_scan_lone_portfile_does_not_create_package(self):
        _result_file, scan = self.scan_packages("vcpkg/ports/rapidjson/manifest")

        assert not [
            package for package in scan["packages"] if package["type"] == "vcpkg"
        ]
        portfile = next(
            file for file in scan["files"] if file["path"] == "portfile.cmake"
        )
        assert portfile["package_data"][0]["datasource_id"] == ("vcpkg_portfile")
