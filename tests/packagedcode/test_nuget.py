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

    def test_parse_as_package_only(self):
        test_file = self.get_test_loc('nuget/Castle.Core.nuspec')
        package = nuget.NugetNuspecHandler.parse(location=test_file, package_only=True)
        expected_loc = self.get_test_loc('nuget/Castle.Core.nuspec-package-only.json.expected')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES, package_only=True)

    def test_parse_nuget_package_lock_json(self):
        test_file = self.get_test_loc('nuget/packages.lock.json')
        package = nuget.NugetPackagesLockHandler.parse(location=test_file)
        expected_loc = self.get_test_loc('nuget/packages.lock.json.expected')
        self.check_packages_data(package, expected_loc, regen=REGEN_TEST_FIXTURES, package_only=True)

    def test_parse_nuget_package_lock_json_with_project_and_central_transitive_types(self):
        test_file = self.get_test_loc(
            'nuget/packages-with-project-and-central-transitive.lock.json'
        )

        packages = list(
            nuget.NugetPackagesLockHandler.parse(
                location=test_file,
                package_only=True,
            )
        )

        assert len(packages) == 1

        package = packages[0].to_dict()
        dependencies = package['dependencies']
        dependencies_by_purl = {
            dependency['purl']: dependency
            for dependency in dependencies
        }

        assert 'pkg:nuget/Local.Project@1.0.0' not in dependencies_by_purl

        assert dependencies_by_purl['pkg:nuget/Direct.Package@1.0.0']['is_direct'] is True
        assert dependencies_by_purl['pkg:nuget/Direct.Package@1.0.0']['extracted_requirement'] == '[1.0.0, )'

        assert dependencies_by_purl['pkg:nuget/Transitive.Package@2.0.0']['is_direct'] is False
        assert dependencies_by_purl['pkg:nuget/Transitive.Package@2.0.0']['extracted_requirement'] == '2.0.0'

        assert dependencies_by_purl['pkg:nuget/CentralTransitive.Package@3.0.0']['is_direct'] is False
        assert dependencies_by_purl['pkg:nuget/CentralTransitive.Package@3.0.0']['extracted_requirement'] == '[3.0.0, )'

    def test_package_lock_json_is_package_data_file(self):
        test_file = self.get_test_loc('nuget/packages.lock.json')
        assert nuget.NugetPackagesLockHandler.is_datafile(test_file)
