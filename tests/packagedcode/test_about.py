#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os.path

from packagedcode import about

from packages_test_utils import PackageTester


class TestAbout(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_about_file_home_url(self):
        test_file = self.get_test_loc('about/apipkg.ABOUT')
        package = about.parse(test_file)
        expected_loc = self.get_test_loc('about/apipkg.ABOUT-expected')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_about_file_homepage_url(self):
        test_file = self.get_test_loc('about/appdirs.ABOUT')
        package = about.parse(test_file)
        expected_loc = self.get_test_loc('about/appdirs.ABOUT-expected')
        self.check_package(package, expected_loc, regen=False)
