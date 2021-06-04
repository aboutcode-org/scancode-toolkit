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


class TestCran(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_as_package(self):
        test_file = self.get_test_loc('cran/codetools/DESCRIPTION')
        package = cran.parse(test_file)
        expected_loc = self.get_test_loc(
            'cran/codetools/package.json.expected')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_as_package2(self):
        test_file = self.get_test_loc('cran/geometry/DESCRIPTION')
        package = cran.parse(test_file)
        expected_loc = self.get_test_loc(
            'cran/geometry/package.json.expected')
        self.check_package(package, expected_loc, regen=False)
