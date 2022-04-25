#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os

from packagedcode import nuget
from packages_test_utils import PackageTester
from scancode_config import REGEN_TEST_FIXTURES


class TestNuget(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_nuspec_is_package_data_file(self):
        test_file = self.get_test_loc('nuget/bootstrap.nuspec')
        assert nuget.NugetNuspecHandler.is_datafile(test_file)

    def test_parse_creates_package_from_nuspec_bootstrap(self):
        test_file = self.get_test_loc('nuget/bootstrap.nuspec')
        package = nuget.NugetNuspecHandler.parse(test_file)
        expected_loc = self.get_test_loc('nuget/bootstrap.nuspec.json.expected')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_creates_package_from_nuspec_entity_framework(self):
        test_file = self.get_test_loc('nuget/EntityFramework.nuspec')
        package = nuget.NugetNuspecHandler.parse(test_file)
        expected_loc = self.get_test_loc('nuget/EntityFramework.nuspec.json.expected')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_creates_package_from_nuspec_jquery_ui(self):
        test_file = self.get_test_loc('nuget/jQuery.UI.Combined.nuspec')
        package = nuget.NugetNuspecHandler.parse(test_file)
        expected_loc = self.get_test_loc('nuget/jQuery.UI.Combined.nuspec.json.expected')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_creates_package_from_nuspec_microsoft_asp_mvc(self):
        test_file = self.get_test_loc('nuget/Microsoft.AspNet.Mvc.nuspec')
        package = nuget.NugetNuspecHandler.parse(test_file)
        expected_loc = self.get_test_loc('nuget/Microsoft.AspNet.Mvc.nuspec.json.expected')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_creates_package_from_nuspec(self):
        test_file = self.get_test_loc('nuget/Microsoft.Net.Http.nuspec')
        package = nuget.NugetNuspecHandler.parse(test_file)
        expected_loc = self.get_test_loc('nuget/Microsoft.Net.Http.nuspec.json.expected')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_as_package(self):
        test_file = self.get_test_loc('nuget/Castle.Core.nuspec')
        package = nuget.NugetNuspecHandler.parse(test_file)
        expected_loc = self.get_test_loc('nuget/Castle.Core.nuspec.json.expected')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)
