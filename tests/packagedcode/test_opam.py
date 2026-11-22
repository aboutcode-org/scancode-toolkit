
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os

import pytest

from packagedcode import opam
from packages_test_utils import PackageTester
from scancode_config import REGEN_TEST_FIXTURES


class TestOcaml(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_is_manifest_cargo_toml(self):
        test_file = self.get_test_loc('opam/sample1/sample1.opam')
        assert opam.OpamFileHandler.is_datafile(test_file)

    def test_parse_sample1(self):
        test_file = self.get_test_loc('opam/sample1/sample1.opam')
        expected_loc = self.get_test_loc('opam/sample1/output.opam.expected')
        packages = opam.OpamFileHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_sample2(self):
        test_file = self.get_test_loc('opam/sample2/sample2.opam')
        expected_loc = self.get_test_loc('opam/sample2/output.opam.expected')
        packages = opam.OpamFileHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_sample3(self):
        test_file = self.get_test_loc('opam/sample3/sample3.opam')
        expected_loc = self.get_test_loc('opam/sample3/output.opam.expected')
        packages = opam.OpamFileHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_sample4(self):
        test_file = self.get_test_loc('opam/sample4/opam')
        expected_loc = self.get_test_loc('opam/sample4/output.opam.expected')
        packages = opam.OpamFileHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_sample5(self):
        test_file = self.get_test_loc('opam/sample5/opam')
        expected_loc = self.get_test_loc('opam/sample5/output.opam.expected')
        packages = opam.OpamFileHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_sample6(self):
        test_file = self.get_test_loc('opam/sample6/sample6.opam')
        expected_loc = self.get_test_loc('opam/sample6/output.opam.expected')
        packages = opam.OpamFileHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_sample7(self):
        test_file = self.get_test_loc('opam/sample7/sample7.opam')
        expected_loc = self.get_test_loc('opam/sample7/output.opam.expected')
        packages = opam.OpamFileHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_sample8(self):
        test_file = self.get_test_loc('opam/sample8/opam')
        expected_loc = self.get_test_loc('opam/sample8/output.opam.expected')
        packages = opam.OpamFileHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_get_repository_homepage_url(self):
        assert opam.get_repository_homepage_url('dune') == 'https://opam.ocaml.org/packages/dune'
        assert opam.get_repository_homepage_url(None) is None

    def test_parse_opam_single_line_depends_and_authors(self):
        test_file = self.get_temp_file('test.opam')
        with open(test_file, 'w') as f:
            f.write('''opam-version: "2.0"
name: "single-line-pkg"
version: "1.2.3"
authors: ["Jane Doe <jane@example.com>"]
maintainer: ["Maintainer Team <maintainer@example.com>"]
homepage: "https://example.com"
license: "MIT"
depends: [ "dune" {>= "2.0.0"} ]
''')
        packages = list(opam.OpamFileHandler.parse(test_file))
        assert len(packages) == 1
        package = packages[0]
        assert package.name == "single-line-pkg"
        assert package.version == "1.2.3"
        assert package.repository_homepage_url == "https://opam.ocaml.org/packages/single-line-pkg"
        assert len(package.parties) == 2
        author = [p for p in package.parties if p.role == 'author'][0]
        assert author.name == "Jane Doe <jane@example.com>"
        assert len(package.dependencies) == 1
        dep = package.dependencies[0]
        assert dep.purl == "pkg:opam/dune"
        assert dep.extracted_requirement == ">= 2.0.0"

    def test_parse_opam_checksum_with_comments_and_blank_lines(self):
        test_file = self.get_temp_file('checksum.opam')
        with open(test_file, 'w') as f:
            f.write('''opam-version: "2.0"
name: "checksum-pkg"
version: "1.0.0"
checksum: [
  # Comment inside checksum block
  "md5=b7a7b7cce64eabf224d05ed9f2b9d471"

  "sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
]
''')
        packages = list(opam.OpamFileHandler.parse(test_file))
        assert len(packages) == 1
        package = packages[0]
        assert package.md5 == "b7a7b7cce64eabf224d05ed9f2b9d471"
        assert package.sha256 == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


FILE_LINE = [
    ('authors: "BAP Team"', ('authors', '"BAP Team"')),
    ('homepage: "https://github.com/BinaryAnalysisPlatform/bap/"', ('homepage', '"https://github.com/BinaryAnalysisPlatform/bap/"'))
]

CHECKSUM_LINE = [
    ('md5=b7a7b7cce64eabf224d05ed9f2b9d471', ('md5', 'b7a7b7cce64eabf224d05ed9f2b9d471')),
    ('md5=86d48dc11dd66adac6daadbecb5f6888', ('md5', '86d48dc11dd66adac6daadbecb5f6888'))
]

DEP_LINE = [
    ('"ocaml"', ('ocaml', '')),
    ('"bap-std" {= "1.0.0"}', ('bap-std', '{= "1.0.0"}')),
    ('"camlp4"', ('camlp4', '')),
    ('"bitstring" {< "3.0.0"}', ('bitstring', '{< "3.0.0"}'))
]


class TestRegex(object):
    @pytest.mark.parametrize('line, expected_data', FILE_LINE)
    def test_parse_file_line(self, line, expected_data):
        parsed_line = opam.parse_file_line(line)
        line_information = parsed_line.groupdict()
        key, value = line_information.get('key'), line_information.get('value')
        assert (key, value) == expected_data

    @pytest.mark.parametrize('checksum, expected_data', CHECKSUM_LINE)
    def test_parse_checksum(self, checksum, expected_data):
        parsed_checksum = opam.parse_checksum(checksum)
        checksum_information = parsed_checksum.groupdict()
        key, value = checksum_information.get('key'), checksum_information.get('value')
        assert (key, value) == expected_data

    @pytest.mark.parametrize('dep, expected_data', DEP_LINE)
    def test_parse_dep(self, dep, expected_data):
        parsed_dep = opam.parse_dep(dep)
        dep_information = parsed_dep.groupdict()
        name, version = dep_information.get('name'), dep_information.get('version')
        assert (name, version) == expected_data


LINE = [
    ('"caml-list@inria.fr"', 'caml-list@inria.fr'),
    ('[make "install"]', 'make install')
]


class TestFunction(object):
    @pytest.mark.parametrize('line, expected_data', LINE)
    def test_parse_file_line(self, line, expected_data):
        stripped_line = opam.clean_data(line)
        assert stripped_line == expected_data
