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

from packagedcode.models import PackageFile
from packagedcode.win_reg import create_absolute_installed_file_path
from packagedcode.win_reg import get_installed_packages
from packagedcode.win_reg import _report_installed_dotnet_versions
from packagedcode.win_reg import _report_installed_programs
from packagedcode.win_reg import remove_drive_letter

from packages_test_utils import PackageTester


class TestWinReg(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_win_reg__report_installed_dotnet_versions(self):
        test_file = self.get_test_loc('win_reg/SOFTWARE-registry-entries.json')
        expected_loc = self.get_test_loc('win_reg/SOFTWARE-dotnet-installation.expected')
        with open(test_file) as f:
            software_registry_entries = json.load(f)
        packages = _report_installed_dotnet_versions(software_registry_entries)
        self.check_packages(packages, expected_loc, regen=False)

    def test_win_reg__report_installed_programs(self):
        test_file = self.get_test_loc('win_reg/SOFTWARE-registry-entries.json')
        expected_loc = self.get_test_loc('win_reg/SOFTWARE-installed-programs.expected')
        with open(test_file) as f:
            software_registry_entries = json.load(f)
        packages = _report_installed_programs(software_registry_entries)
        self.check_packages(packages, expected_loc, regen=False)

    def test_win_reg_remove_drive_letter(self):
        test_path = 'C:\\Users\\Test\\Desktop'
        expected_path = 'Users/Test/Desktop'
        result = remove_drive_letter(test_path)
        self.assertEqual(result, expected_path)

    def test_win_reg_create_absolute_installed_file_path(self):
        root_dir = '/home/test/c/'
        test_path = 'C:\\Program Files\\Test Program\\'
        result = create_absolute_installed_file_path(root_dir, test_path)
        expected_path = '/home/test/c/Program Files/Test Program'
        self.assertEqual(result, expected_path)

    def test_win_reg_get_installed_packages(self):
        test_root_dir = self.get_test_loc('win_reg/get_installed_packages_docker/layer')
        expected_loc = self.get_test_loc('win_reg/get_installed_packages_docker/expected-results')
        results = list(get_installed_packages(test_root_dir))
        # Ensure only one program is detected
        self.assertEqual(len(results), 1)
        result = results[0]
        # Check to see if the resulting InstalledProgramFile was created properly
        self.check_package(result, expected_loc, regen=False)
        expected_installed_files = [
            PackageFile(path=os.path.join(test_root_dir, 'Files/Program Files/Test/Test.exe')),
            PackageFile(path=os.path.join(test_root_dir, 'Files/Program Files/Test/Uninstall.exe')),
            PackageFile(path=os.path.join(test_root_dir, 'Files/Program Files/Test/Test.dat')),
        ]
        self.assertEqual(sorted(result.installed_files), sorted(expected_installed_files))
