#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import json
import os

from packagedcode.win_reg import _report_installed_dotnet_versions
from packagedcode.win_reg import _report_installed_programs

from packages_test_utils import PackageTester


class TestWindowsHelpers(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test__report_installed_dotnet_versions(self):
        test_file = self.get_test_loc('win_reg/SOFTWARE-registry-entries.json')
        expected_loc = self.get_test_loc('win_reg/SOFTWARE-dotnet-installation.expected')
        with open(test_file) as f:
            software_registry_entries = json.load(f)
        packages = _report_installed_dotnet_versions(software_registry_entries)
        self.check_packages(packages, expected_loc, regen=False)

    def test__report_installed_programs(self):
        test_file = self.get_test_loc('win_reg/SOFTWARE-registry-entries.json')
        expected_loc = self.get_test_loc('win_reg/SOFTWARE-installed-programs.expected')
        with open(test_file) as f:
            software_registry_entries = json.load(f)
        packages = _report_installed_programs(software_registry_entries)
        self.check_packages(packages, expected_loc, regen=False)
