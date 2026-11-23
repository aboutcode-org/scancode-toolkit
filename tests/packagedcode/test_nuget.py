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
import xmltodict

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
    
    def test_package_lock_json_is_package_data_file(self):
        test_file = self.get_test_loc('nuget/packages.lock.json')
        assert nuget.NugetPackagesLockHandler.is_datafile(test_file)

    def test_get_dependencies_default_group_without_target_framework(self):
        nuspec_xml = """<package>
          <metadata>
            <dependencies>
              <group>
                <dependency id="RouteMagic" version="1.10" />
              </group>
            </dependencies>
          </metadata>
        </package>"""
        parsed = xmltodict.parse(nuspec_xml)
        nuspec = parsed['package']['metadata']
        deps = list(nuget.get_dependencies(nuspec))
        assert len(deps) == 1
        assert deps[0].purl == 'pkg:nuget/RouteMagic'
        assert deps[0].extracted_requirement == '1.10'
        assert deps[0].extra_data == {}

    def test_get_dependencies_mixed_groups(self):
        nuspec_xml = """<package>
          <metadata>
            <dependencies>
              <group>
                <dependency id="RouteMagic" version="1.10" />
              </group>
              <group targetFramework="net40">
                <dependency id="jQuery" version="1.9.1" />
              </group>
            </dependencies>
          </metadata>
        </package>"""
        parsed = xmltodict.parse(nuspec_xml)
        nuspec = parsed['package']['metadata']
        deps = list(nuget.get_dependencies(nuspec))
        assert len(deps) == 2
        assert deps[0].purl == 'pkg:nuget/RouteMagic'
        assert deps[0].extracted_requirement == '1.10'
        assert deps[0].extra_data == {}
        assert deps[1].purl == 'pkg:nuget/jQuery'
        assert deps[1].extracted_requirement == '1.9.1'
        assert deps[1].extra_data == {'framework': 'net40'}

    def test_get_dependencies_empty_group(self):
        nuspec_xml = """<package>
          <metadata>
            <dependencies>
              <group targetFramework="netstandard2.0" />
            </dependencies>
          </metadata>
        </package>"""
        parsed = xmltodict.parse(nuspec_xml)
        nuspec = parsed['package']['metadata']
        deps = list(nuget.get_dependencies(nuspec))
        assert deps == []

    def test_parse_nuget_package_lock_json_empty_dependencies(self):
        temp_file = self.get_temp_file('packages.lock.json')
        with open(temp_file, 'w') as f:
            json.dump({'version': 1, 'dependencies': {}}, f)
        packages = list(nuget.NugetPackagesLockHandler.parse(location=temp_file))
        assert len(packages) == 1
        assert packages[0].dependencies == []
        assert packages[0].extra_data == {}
