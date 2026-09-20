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
import tempfile

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

    def test_deps_json_is_datafile(self):
        test_file = self.get_test_loc('nuget/deps_json/simple.deps.json')
        assert nuget.DotNetDepsJsonHandler.is_datafile(test_file)

    def test_parse_simple_deps_json(self):
        test_file = self.get_test_loc('nuget/deps_json/simple.deps.json')
        packages = nuget.DotNetDepsJsonHandler.parse(test_file)
        expected_loc = self.get_test_loc('nuget/deps_json/simple.deps.json.expected')
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_snoop_deps_json(self):
        test_file = self.get_test_loc('nuget/deps_json/Snoop.Core.deps.json')
        packages = nuget.DotNetDepsJsonHandler.parse(test_file)
        expected_loc = self.get_test_loc('nuget/deps_json/Snoop.Core.deps.json.expected')
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_small_app_deps_json(self):
        test_file = self.get_test_loc('nuget/deps_json/small_app.deps.json')
        packages = nuget.DotNetDepsJsonHandler.parse(test_file)
        expected_loc = self.get_test_loc('nuget/deps_json/small_app.deps.json.expected')
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_empty_libraries_deps_json(self):
        fd, temp_path = tempfile.mkstemp(suffix='.deps.json')
        with os.fdopen(fd, 'w') as f:
            json.dump({
                "runtimeTarget": {"name": ".NETCoreApp,Version=v6.0"},
                "libraries": {}
            }, f)

        try:
            packages = list(nuget.DotNetDepsJsonHandler.parse(temp_path))
            assert len(packages) == 0
        finally:
            os.remove(temp_path)

    def test_parse_without_runtime_target_uses_targets(self):
        fd, temp_path = tempfile.mkstemp(suffix='.deps.json')
        with os.fdopen(fd, 'w') as f:
            json.dump({
                "targets": {
                    ".NETCoreApp,Version=v8.0": {
                        "App/1.0.0": {
                            "dependencies": {
                                "Newtonsoft.Json": "13.0.3"
                            }
                        },
                        "Newtonsoft.Json/13.0.3": {}
                    }
                },
                "libraries": {
                    "App/1.0.0": {"type": "project"},
                    "Newtonsoft.Json/13.0.3": {"type": "package"}
                }
            }, f)

        try:
            packages = list(nuget.DotNetDepsJsonHandler.parse(temp_path))
            assert len(packages) == 2

            app = [p for p in packages if p.name == 'App'][0]
            assert app.extra_data.get('target_framework') == '.NETCoreApp,Version=v8.0'
            assert len(app.dependencies) == 1
            dependency = app.dependencies[0]
            assert dependency.get('purl') == 'pkg:nuget/Newtonsoft.Json@13.0.3'
            assert dependency.get('scope') == '.NETCoreApp,Version=v8.0'
            assert dependency.get('resolved_package', {}).get('purl') == 'pkg:nuget/Newtonsoft.Json@13.0.3'
        finally:
            os.remove(temp_path)

    def test_parse_runtime_target_mismatch_falls_back_to_targets(self):
        fd, temp_path = tempfile.mkstemp(suffix='.deps.json')
        with os.fdopen(fd, 'w') as f:
            json.dump({
                "runtimeTarget": {"name": ".NETCoreApp,Version=v8.0/win-x64"},
                "targets": {
                    ".NETCoreApp,Version=v8.0": {
                        "App/1.0.0": {
                            "dependencies": {
                                "Serilog": "3.1.0"
                            }
                        },
                        "Serilog/3.1.0": {}
                    }
                },
                "libraries": {
                    "App/1.0.0": {"type": "project"},
                    "Serilog/3.1.0": {"type": "package"}
                }
            }, f)

        try:
            packages = list(nuget.DotNetDepsJsonHandler.parse(temp_path))
            assert len(packages) == 2

            app = [p for p in packages if p.name == 'App'][0]
            assert app.extra_data.get('target_framework') == '.NETCoreApp,Version=v8.0'
            assert len(app.dependencies) == 1
            dependency = app.dependencies[0]
            assert dependency.get('purl') == 'pkg:nuget/Serilog@3.1.0'
            assert dependency.get('scope') == '.NETCoreApp,Version=v8.0'
            assert dependency.get('resolved_package', {}).get('purl') == 'pkg:nuget/Serilog@3.1.0'
        finally:
            os.remove(temp_path)

    def test_parse_without_runtime_target_merges_multiple_targets(self):
        fd, temp_path = tempfile.mkstemp(suffix='.deps.json')
        with os.fdopen(fd, 'w') as f:
            json.dump({
                "targets": {
                    ".NETCoreApp,Version=v8.0": {
                        "App/1.0.0": {
                            "dependencies": {
                                "Newtonsoft.Json": "13.0.3"
                            }
                        },
                        "Newtonsoft.Json/13.0.3": {}
                    },
                    ".NETFramework,Version=v4.7.2": {
                        "App/1.0.0": {
                            "dependencies": {
                                "Serilog": "3.1.0"
                            }
                        },
                        "Serilog/3.1.0": {}
                    }
                },
                "libraries": {
                    "App/1.0.0": {"type": "project"},
                    "Newtonsoft.Json/13.0.3": {"type": "package"},
                    "Serilog/3.1.0": {"type": "package"}
                }
            }, f)

        try:
            packages = list(nuget.DotNetDepsJsonHandler.parse(temp_path))
            assert len(packages) == 3

            app = [p for p in packages if p.name == 'App'][0]
            assert app.extra_data.get('target_frameworks') == [
                '.NETCoreApp,Version=v8.0',
                '.NETFramework,Version=v4.7.2',
            ]

            dependencies = sorted(app.dependencies, key=lambda dep: dep.get('purl'))
            assert [dep.get('purl') for dep in dependencies] == [
                'pkg:nuget/Newtonsoft.Json@13.0.3',
                'pkg:nuget/Serilog@3.1.0',
            ]
            assert [dep.get('scope') for dep in dependencies] == [
                '.NETCoreApp,Version=v8.0',
                '.NETFramework,Version=v4.7.2',
            ]
            assert [dep.get('resolved_package', {}).get('purl') for dep in dependencies] == [
                'pkg:nuget/Newtonsoft.Json@13.0.3',
                'pkg:nuget/Serilog@3.1.0',
            ]
        finally:
            os.remove(temp_path)
