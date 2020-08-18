#
# Copyright (c) 2019 nexB Inc. and others. All rights reserved.
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
from unittest.case import skipIf

from commoncode.system import on_windows
from packages_test_utils import PackageTester
from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click


class TestPlugins(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_package_list_command(self, regen=False):
        expected_file = self.get_test_loc('plugin/help.txt')
        result = run_scan_click(['--list-packages'])
        if regen:
            wmode = 'w'
            with open(expected_file, wmode) as ef:
                ef.write(result.output)
        assert open(expected_file).read() == result.output

    @skipIf(on_windows, 'somehow this fails on Windows')
    def test_package_command_scan_python(self):
        test_dir = self.get_test_loc('pypi/package')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin/python-package-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, regen=False)

    def test_package_command_scan_maven(self):
        test_dir = self.get_test_loc('maven2')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin/maven-package-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, regen=False)

    def test_package_command_scan_about(self):
        test_dir = self.get_test_loc('about')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin/about-package-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, regen=False)

    def test_package_command_scan_bower(self):
        test_dir = self.get_test_loc('bower/package')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin/bower-package-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, regen=False)

    def test_package_command_scan_cargo(self):
        test_dir = self.get_test_loc('cargo/package')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin/cargo-package-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, regen=False)

    def test_package_command_scan_chef(self):
        test_dir = self.get_test_loc('chef/package')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin/chef-package-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, regen=False)

    def test_package_command_scan_conda(self):
        test_dir = self.get_test_loc('conda/package')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin/conda-package-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, regen=False)

    def test_package_command_scan_freebsd(self):
        test_dir = self.get_test_loc('freebsd/package')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin/freebsd-package-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, regen=False)

    def test_package_command_scan_haxe(self):
        test_dir = self.get_test_loc('haxe/package')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin/haxe-package-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, regen=False)

    def test_package_command_scan_npm(self):
        test_dir = self.get_test_loc('npm/package')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin/npm-package-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, regen=False)

    def test_package_command_scan_nuget(self):
        test_dir = self.get_test_loc('nuget/package')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin/nuget-package-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, regen=False)

    def test_package_command_scan_phpcomposer(self):
        test_dir = self.get_test_loc('phpcomposer/package')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin/phpcomposer-package-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, regen=False)

    def test_package_command_scan_rubygems(self):
        test_dir = self.get_test_loc('rubygems/package')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin/rubygems-package-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, regen=False)

    def test_package_command_scan_rpm(self):
        test_dir = self.get_test_loc('rpm/package')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin/rpm-package-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, regen=False)

    def test_package_command_scan_cran_r_package(self):
        test_dir = self.get_test_loc('cran/package')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin/cran-package-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, regen=False)
