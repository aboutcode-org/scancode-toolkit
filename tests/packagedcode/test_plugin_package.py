#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
from unittest.case import skipIf

from commoncode.system import on_windows

from packagedcode.plugin_package import get_installed_packages
from packages_test_utils import PackageTester
from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from scancode_config import REGEN_TEST_FIXTURES


class TestPlugins(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_package_command_scan_about(self):
        test_dir = self.get_test_loc('about/aboutfiles/')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin/about-package-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_package_command_scan_bower(self):
        test_dir = self.get_test_loc('bower/package')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin/bower-package-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_package_command_scan_cargo(self):
        test_dir = self.get_test_loc('cargo/package')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin/cargo-package-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_package_command_scan_chef(self):
        test_dir = self.get_test_loc('chef/package')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin/chef-package-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_package_command_scan_conda(self):
        test_dir = self.get_test_loc('conda/package')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin/conda-package-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_package_command_scan_cran_r_package(self):
        test_dir = self.get_test_loc('cran/package')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin/cran-package-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_package_command_scan_freebsd(self):
        test_dir = self.get_test_loc('freebsd/package')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin/freebsd-package-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_package_command_scan_haxe(self):
        test_dir = self.get_test_loc('haxe/package')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin/haxe-package-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_package_command_scan_maven(self):
        test_dir = self.get_test_loc('maven2')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin/maven-package-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_package_command_scan_npm(self):
        test_dir = self.get_test_loc('npm/package')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin/npm-package-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_package_command_scan_maven_with_license(self):
        test_dir = self.get_test_loc('maven2')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin/maven-package-with-license-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_package_command_scan_npm_with_license(self):
        test_dir = self.get_test_loc('npm/package')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin/npm-package-with-license-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_package_command_scan_nuget(self):
        test_dir = self.get_test_loc('nuget/package')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin/nuget-package-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_package_command_scan_opam(self):
        test_dir = self.get_test_loc('opam/package')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin/opam-package-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_package_command_scan_phpcomposer(self):
        test_dir = self.get_test_loc('phpcomposer/package')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin/phpcomposer-package-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    @skipIf(on_windows, 'somehow this fails on Windows')
    def test_package_command_scan_python(self):
        test_dir = self.get_test_loc('recon/pypi')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin/python-package-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_package_command_scan_rubygems(self):
        test_dir = self.get_test_loc('rubygems/package')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin/rubygems-package-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_package_command_scan_rpm(self):
        test_dir = self.get_test_loc('rpm/package')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin/rpm-package-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_package_command_scan_win_pe(self):
        test_dir = self.get_test_loc('win_pe/file.exe')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin/win_pe-package-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_package_command_scan_mum(self):
        test_dir = self.get_test_loc('windows/mum/test.mum')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin/mum-package-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_package_command_scan_pubspec_package(self):
        test_dir = self.get_test_loc('pubspec/specs/authors-pubspec.yaml')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin/pubspec-expected.json', must_exist=False)
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_package_command_scan_pubspec_lock_package(self):
        test_dir = self.get_test_loc('pubspec/locks/dart-pubspec.lock')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin/pubspec-lock-expected.json', must_exist=False)
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_package_command_scan_mui(self):
        test_dir = self.get_test_loc('win_pe/clfs.sys.mui')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin/mui-package-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_package_command_scan_mun(self):
        test_dir = self.get_test_loc('win_pe/crypt32.dll.mun')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin/mun-package-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_package_command_scan_com(self):
        test_dir = self.get_test_loc('win_pe/chcp.com')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin/com-package-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_package_command_scan_tlb(self):
        test_dir = self.get_test_loc('win_pe/stdole2.tlb')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin/tlb-package-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_package_command_scan_sys(self):
        test_dir = self.get_test_loc('win_pe/tbs.sys')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin/sys-package-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_package_command_scan_winmd(self):
        test_dir = self.get_test_loc('win_pe/Windows.AI.winmd')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('plugin/winmd-package-expected.json')
        run_scan_click(['--package', '--strip-root', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_package_list_command(self, regen=REGEN_TEST_FIXTURES):
        expected_file = self.get_test_loc('plugin/help.txt')
        result = run_scan_click(['--list-packages'])
        if regen:
            with open(expected_file, 'w') as ef:
                ef.write(result.output)
        assert result.output == open(expected_file).read()

    def test_system_package_get_installed_packages(self):
        test_dir = self.extract_test_tar('debian/basic-rootfs.tar.gz')
        expected_file = self.get_test_loc('plugin/get_installed_packages-expected.json')
        results = list(get_installed_packages(test_dir))
        self.check_packages_data(results, expected_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)
