#
# Copyright (c) 2017 nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/scancode-toolkit/
# The ScanCode software is licensed under the Apache License version 2.0.
# Data generated with ScanCode require an acknowledgment.
# ScanCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# When you publish or redistribute any data created with ScanCode or any ScanCode
# derivative work, you must accompany this data with the following acknowledgment:
#
#  Generated with ScanCode and provided on an "AS IS" BASIS, WITHOUT WARRANTIES
#  OR CONDITIONS OF ANY KIND, either express or implied. No content created from
#  ScanCode should be considered or used as legal advice. Consult an Attorney
#  for any legal advice.
#  ScanCode is a free software code scanning tool from nexB Inc. and others.
#  Visit https://github.com/nexB/scancode-toolkit/ for support and download.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os

from packagedcode import nuget

from packages_test_utils import PackageTester


class TestNuget(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_creates_package_from_nuspec_bootstrap(self):
        test_file = self.get_test_loc('nuget/bootstrap.nuspec')
        package = nuget.parse(test_file)
        expected_loc = self.get_test_loc('nuget/bootstrap.nuspec.json.expected')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_creates_package_from_nuspec_entity_framework(self):
        test_file = self.get_test_loc('nuget/EntityFramework.nuspec')
        package = nuget.parse(test_file)
        expected_loc = self.get_test_loc('nuget/EntityFramework.nuspec.json.expected')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_creates_package_from_nuspec_jquery_ui(self):
        test_file = self.get_test_loc('nuget/jQuery.UI.Combined.nuspec')
        package = nuget.parse(test_file)
        expected_loc = self.get_test_loc('nuget/jQuery.UI.Combined.nuspec.json.expected')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_creates_package_from_nuspec_microsoft_asp_mvc(self):
        test_file = self.get_test_loc('nuget/Microsoft.AspNet.Mvc.nuspec')
        package = nuget.parse(test_file)
        expected_loc = self.get_test_loc('nuget/Microsoft.AspNet.Mvc.nuspec.json.expected')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_creates_package_from_nuspec(self):
        test_file = self.get_test_loc('nuget/Microsoft.Net.Http.nuspec')
        package = nuget.parse(test_file)
        expected_loc = self.get_test_loc('nuget/Microsoft.Net.Http.nuspec.json.expected')
        self.check_package(package, expected_loc, regen=False)

    def test_parse_as_package(self):
        test_file = self.get_test_loc('nuget/Castle.Core.nuspec')
        package = nuget.parse(test_file)
        expected_loc = self.get_test_loc('nuget/Castle.Core.nuspec.json.expected')
        self.check_package(package, expected_loc, regen=False)
