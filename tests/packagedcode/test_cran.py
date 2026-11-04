#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os

from packagedcode import cran
from packages_test_utils import PackageTester
from scancode_config import REGEN_TEST_FIXTURES


class TestCran(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_as_package(self):
        test_file = self.get_test_loc('cran/codetools/DESCRIPTION')
        packages = cran.CranDescriptionFileHandler.parse(test_file)
        expected_loc = self.get_test_loc(
            'cran/codetools/package.json.expected')
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_as_package2(self):
        test_file = self.get_test_loc('cran/geometry/DESCRIPTION')
        packages = cran.CranDescriptionFileHandler.parse(test_file)
        expected_loc = self.get_test_loc(
            'cran/geometry/package.json.expected')
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_single_line_depends_without_author_or_maintainer(self):
        test_file = self.get_test_loc('cran/single-line-depends/DESCRIPTION')
        packages = cran.CranDescriptionFileHandler.parse(test_file)
        expected_loc = self.get_test_loc(
            'cran/single-line-depends/package.json.expected')
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_without_depends(self):
        test_file = self.get_test_loc('cran/no-depends/DESCRIPTION')
        packages = cran.CranDescriptionFileHandler.parse(test_file)
        expected_loc = self.get_test_loc(
            'cran/no-depends/package.json.expected')
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_get_dependencies(self):
        results = list(cran.get_dependencies('R (>= 3.4.0),\nmethods, utils (>= 3.0), '))
        expected = [('R', '>= 3.4.0'), ('methods', None), ('utils', '>= 3.0')]
        assert results == expected
