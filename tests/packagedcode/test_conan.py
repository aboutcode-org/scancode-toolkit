#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import ast
import os.path

from commoncode import testcase
from packages_test_utils import PackageTester
from packages_test_utils import check_result_equals_expected_json

from packagedcode import conan
from packagedcode import models
from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from scancode_config import REGEN_TEST_FIXTURES


class TestConanHandler(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), "data")

    def test_parse_for_boost_conanfile(self):
        test_file = self.get_test_loc("conan/recipes/boost/manifest/conanfile.py")
        expected_loc = self.get_test_loc(
            "conan/recipes/boost/conanfile.py-expected.json"
        )
        packages = conan.ConanFileHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_for_libgettext_conanfile(self):
        test_file = self.get_test_loc("conan/recipes/libgettext/manifest/conanfile.py")
        expected_loc = self.get_test_loc(
            "conan/recipes/libgettext/conanfile.py-expected.json"
        )
        packages = conan.ConanFileHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_for_libzip_conanfile(self):
        test_file = self.get_test_loc("conan/recipes/libzip/manifest/conanfile.py")
        expected_loc = self.get_test_loc(
            "conan/recipes/libzip/conanfile.py-expected.json"
        )
        packages = conan.ConanFileHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_for_boost_conandata(self):
        test_file = self.get_test_loc("conan/recipes/boost/manifest/conandata.yml")
        expected_loc = self.get_test_loc(
            "conan/recipes/boost/conandata.yml-expected.json"
        )
        packages = conan.ConanDataHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_for_libgettext_conandata(self):
        test_file = self.get_test_loc("conan/recipes/libgettext/manifest/conandata.yml")
        expected_loc = self.get_test_loc(
            "conan/recipes/libgettext/conandata.yml-expected.json"
        )
        packages = conan.ConanDataHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_for_libzip_conandata(self):
        test_file = self.get_test_loc("conan/recipes/libzip/manifest/conandata.yml")
        expected_loc = self.get_test_loc(
            "conan/recipes/libzip/conandata.yml-expected.json"
        )
        packages = conan.ConanDataHandler.parse(test_file)
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)


class TestConanEndtoEnd(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), "data")

    def test_package_scan_conan_end_to_end_full_boost(self):
        test_dir = self.get_test_loc("conan/recipes/boost/manifest")
        result_file = self.get_temp_file("json")
        expected_file = self.get_test_loc(
            "conan/recipes/boost/conan-boost-package-expected.json"
        )
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
        check_json_scan(
            expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES
        )

    def test_package_scan_conan_end_to_end_full_libgettext(self):
        test_dir = self.get_test_loc("conan/recipes/libgettext/manifest")
        result_file = self.get_temp_file("json")
        expected_file = self.get_test_loc(
            "conan/recipes/libgettext/conan-libgettext-package-expected.json"
        )
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
        check_json_scan(
            expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES
        )

    def test_package_scan_conan_end_to_end_full_libzip(self):
        test_dir = self.get_test_loc("conan/recipes/libzip/manifest")
        result_file = self.get_temp_file("json")
        expected_file = self.get_test_loc(
            "conan/recipes/libzip/conan-libzip-package-expected.json"
        )
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
        check_json_scan(
            expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES
        )


class TestConanFileParser(testcase.FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), "data")

    def test_ast_conanfileparser_boost(self):
        test_file = self.get_test_loc("conan/recipes/boost/manifest/conanfile.py")
        expected_loc = self.get_test_loc(
            "conan/recipes/boost/conanfile.py.ast-expected.json"
        )

        with open(test_file, encoding="utf-8") as loc:
            conan_recipe = loc.read()
        tree = ast.parse(conan_recipe)
        parser = conan.ConanFileParser()
        parser.visit(tree)

        results = parser.to_dict()
        check_result_equals_expected_json(
            result=results,
            expected_loc=expected_loc,
            regen=REGEN_TEST_FIXTURES,
        )


def test_is_constraint_resolved():
    constraint1 = "[>=1.2.11 <2]"
    expected1 = False

    constraint2 = "cci.20210118"
    expected2 = True

    assert conan.is_constraint_resolved(constraint1) == expected1
    assert conan.is_constraint_resolved(constraint2) == expected2


def test_get_dependencies():
    requires = ["zlib/[>=1.2.11 <2]", "bzip2/1.0.8", "xz_utils/5.4.4"]
    expected = [
        models.DependentPackage(
            purl="pkg:conan/zlib",
            scope="install",
            is_runtime=True,
            is_optional=False,
            is_resolved=False,
            extracted_requirement="[>=1.2.11 <2]",
        ),
        models.DependentPackage(
            purl="pkg:conan/bzip2@1.0.8",
            scope="install",
            is_runtime=True,
            is_optional=False,
            is_resolved=True,
            extracted_requirement="1.0.8",
        ),
        models.DependentPackage(
            purl="pkg:conan/xz_utils@5.4.4",
            scope="install",
            is_runtime=True,
            is_optional=False,
            is_resolved=True,
            extracted_requirement="5.4.4",
        ),
    ]

    assert conan.get_dependencies(requires) == expected
