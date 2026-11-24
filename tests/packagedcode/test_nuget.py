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
    
    def test_package_lock_json_is_package_data_file(self):
        test_file = self.get_test_loc('nuget/packages.lock.json')
        assert nuget.NugetPackagesLockHandler.is_datafile(test_file)

    def test_parse_nuspec_with_fallback_group_without_target_framework(self):
        test_file = self.get_temp_file('test.nuspec')
        with open(test_file, 'w') as f:
            f.write('''<?xml version="1.0"?>
<package xmlns="http://schemas.microsoft.com/packaging/2010/07/nuspec.xsd">
  <metadata>
    <id>SamplePackage</id>
    <version>1.0.0</version>
    <dependencies>
      <group>
        <dependency id="FallbackDep" version="1.0.0" />
      </group>
      <group targetFramework="net6.0">
        <dependency id="Net6Dep" version="2.0.0" />
      </group>
    </dependencies>
  </metadata>
</package>''')
        packages = list(nuget.NugetNuspecHandler.parse(test_file))
        assert len(packages) == 1
        package = packages[0]
        assert package.name == 'SamplePackage'
        assert len(package.dependencies) == 2
        dep_fallback = [d for d in package.dependencies if d.purl == 'pkg:nuget/FallbackDep'][0]
        assert dep_fallback.extracted_requirement == '1.0.0'
        assert not dep_fallback.extra_data.get('framework')

        dep_net6 = [d for d in package.dependencies if d.purl == 'pkg:nuget/Net6Dep'][0]
        assert dep_net6.extracted_requirement == '2.0.0'
        assert dep_net6.extra_data.get('framework') == 'net6.0'

    def test_parse_nuspec_with_expression_license(self):
        test_file = self.get_temp_file('test_license.nuspec')
        with open(test_file, 'w') as f:
            f.write('''<?xml version="1.0"?>
<package xmlns="http://schemas.microsoft.com/packaging/2010/07/nuspec.xsd">
  <metadata>
    <id>SampleLicensePackage</id>
    <version>1.0.0</version>
    <license type="expression">Apache-2.0</license>
  </metadata>
</package>''')
        packages = list(nuget.NugetNuspecHandler.parse(test_file))
        assert len(packages) == 1
        package = packages[0]
        assert package.extracted_license_statement == 'Apache-2.0'
        assert package.declared_license_expression == 'apache-2.0'

    def test_parse_packages_lock_with_project_dependency(self):
        test_file = self.get_temp_file('packages.lock.json')
        with open(test_file, 'w') as f:
            f.write('''{
  "version": 1,
  "dependencies": {
    "net6.0": {
      "MyClassLib": {
        "type": "Project",
        "dependencies": {}
      },
      "Newtonsoft.Json": {
        "type": "Direct",
        "resolved": "13.0.1",
        "contentHash": "abc"
      }
    }
  }
}''')
        packages = list(nuget.NugetPackagesLockHandler.parse(test_file))
        assert len(packages) == 1
        package = packages[0]
        assert len(package.dependencies) == 2
        proj_dep = [d for d in package.dependencies if d['purl'] == 'pkg:nuget/MyClassLib'][0]
        assert proj_dep['is_direct'] is True
