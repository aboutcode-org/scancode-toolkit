#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os

from packagedcode.windows_helpers import msi_parse
from packagedcode.windows_helpers import reg_parse
from packagedcode.windows_helpers import report_installed_dotnet_versions
from packagedcode.windows_helpers import report_installed_programs

from packages_test_utils import PackageTester


class TestWindowsHelpers(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_msi_parse_7z(self):
        test_file = self.get_test_loc('windows_helpers/msi/7z1900-x64.msi')
        expected_loc = self.get_test_loc('windows_helpers/msi/7z1900-x64.msi.expected')
        package = msi_parse(test_file)
        self.check_package(package, expected_loc, regen=False)

    def test_report_installed_dotnet_versions(self):
        test_file = self.get_test_loc('windows_helpers/registry/Software_Delta')
        expected_loc = self.get_test_loc('windows_helpers/registry/Software_Delta-dotnet.expected')
        package = reg_parse(test_file)
        self.check_packages(package, expected_loc, regen=False)

    def test_report_installed_programs(self):
        test_file = self.get_test_loc('windows_helpers/registry/Software_Delta')
        expected_loc = self.get_test_loc('windows_helpers/registry/Software_Delta-installed.expected')
        package = reg_parse(test_file)
        self.check_packages(package, expected_loc, regen=False)

    def test_reg_parse_SOFTWARE(self):
        test_file = self.get_test_loc('windows_helpers/registry/Software_Delta')
        expected_loc = self.get_test_loc('windows_helpers/registry/Software_Delta.expected')
        package = reg_parse(test_file)
        self.check_packages(package, expected_loc, regen=False)
