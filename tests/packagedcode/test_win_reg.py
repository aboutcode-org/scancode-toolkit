#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os

from packagedcode.win_reg import reg_parse
from packagedcode.win_reg import report_installed_dotnet_versions
from packagedcode.win_reg import report_installed_programs

from packages_test_utils import PackageTester


class TestWindowsHelpers(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_report_installed_dotnet_versions(self):
        test_file = self.get_test_loc('win_reg/Software_Delta')
        expected_loc = self.get_test_loc('win_reg/Software_Delta-dotnet.expected')
        package = report_installed_dotnet_versions(test_file)
        self.check_packages(package, expected_loc, regen=False)

    def test_report_installed_programs(self):
        test_file = self.get_test_loc('win_reg/Software_Delta')
        expected_loc = self.get_test_loc('win_reg/Software_Delta-installed.expected')
        package = report_installed_programs(test_file)
        self.check_packages(package, expected_loc, regen=False)

    def test_reg_parse_SOFTWARE(self):
        test_file = self.get_test_loc('win_reg/Software_Delta')
        expected_loc = self.get_test_loc('win_reg/Software_Delta.expected')
        package = reg_parse(test_file)
        self.check_packages(package, expected_loc, regen=False)
