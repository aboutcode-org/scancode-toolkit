#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os.path
from unittest.case import skipIf

from commoncode.system import on_windows

from packagedcode import debian
from packages_test_utils import PackageTester
from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from scancode_config import REGEN_TEST_FIXTURES
from packagedcode.debian import build_package_data_from_package_filename
from packagedcode.debian import DebianDebPackageHandler


@skipIf(on_windows, 'These tests contain files that are not legit on Windows.')
class TestDebianPackageGetInstalledPackages(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_scan_system_package_end_to_end_installed_debian_basic_rootfs(self):
        test_dir = self.extract_test_tar('debian/basic-rootfs.tar.gz')
        expected_file = self.get_test_loc('debian/basic-rootfs-expected.json')
        result_file = self.get_temp_file('results.json')
        run_scan_click(['--system-package', test_dir, '--json-pp', result_file])
        check_json_scan(expected_file, result_file, regen=REGEN_TEST_FIXTURES)

    def test_can_scan_system_package_installed_debian_with_license_from_container_layer(self):
        test_dir = self.extract_test_tar('debian/debian-container-layer.tar.xz')
        expected_file = self.get_test_loc('debian/debian-container-layer.tar.xz.scan-expected.json', must_exist=False)
        result_file = self.get_temp_file('results.json')
        run_scan_click(['--system-package', test_dir, '--json-pp', result_file])
        check_json_scan(expected_file, result_file, regen=REGEN_TEST_FIXTURES)

    def test_can_get_installed_system_packages_with_license_from_debian_container_layer(self):
        from packagedcode.plugin_package import get_installed_packages
        test_dir = self.extract_test_tar('debian/debian-container-layer.tar.xz')
        expected_file = self.get_test_loc('debian/debian-container-layer.tar.xz.get-installed-expected.json', must_exist=False)
        results = list(get_installed_packages(test_dir))
        self.check_packages_data(results, expected_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)


class TestDebian(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_status_file_not_a_status_file(self):
        test_file = self.get_test_loc('debian/not-a-status-file')
        test_packages = list(debian.DebianInstalledStatusDatabaseHandler.parse(test_file))
        assert test_packages == []

    def test_parse_status_file_non_existing_file(self):
        test_file = os.path.join(self.get_test_loc('debian'), 'foobarbaz')
        try:
            list(debian.DebianInstalledStatusDatabaseHandler.parse(test_file))
            self.fail('FileNotFoundError not raised')
        except FileNotFoundError:
            pass

    def test_parse_status_file_basic(self):
        test_file = self.get_test_loc('debian/basic/status')
        expected_loc = self.get_test_loc('debian/basic/status.expected')
        # specify ubuntu distro as this was the source of the test `status` file
        packages = list(debian.DebianInstalledStatusDatabaseHandler.parse(test_file))
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_parse_status_file_perl_error(self):
        test_file = self.get_test_loc('debian/mini-status/status')
        expected_loc = self.get_test_loc('debian/mini-status/status.expected')
        packages = list(debian.DebianInstalledStatusDatabaseHandler.parse(test_file))
        self.check_packages_data(packages, expected_loc, regen=REGEN_TEST_FIXTURES)

    @skipIf(on_windows, 'File names cannot contain colons on Windows')
    def test_scan_system_package_end_to_end_installed_debian(self):
        test_dir = self.extract_test_tar('debian/end-to-end.tgz')
        expected_file = self.get_test_loc('debian/end-to-end.tgz.expected.json', must_exist=False)
        result_file = self.get_temp_file('results.json')
        run_scan_click(['--system-package', test_dir, '--json-pp', result_file])
        check_json_scan(expected_file, result_file, regen=REGEN_TEST_FIXTURES)

    def test_scan_system_package_end_to_end_installed_ubuntu_with_missing_md5sums(self):
        test_dir = self.get_test_loc('debian/ubuntu-var-lib-dpkg/')
        expected_file = self.get_test_loc('debian/ubuntu-var-lib-dpkg/expected.json')
        result_file = self.get_temp_file('results.json')
        run_scan_click(['--system-package', test_dir, '--json-pp', result_file])
        check_json_scan(expected_file, result_file, regen=REGEN_TEST_FIXTURES)


class TestDebianGetListOfInstalledFiles(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_missing_md5sum_file(self):
        test_file = self.get_test_loc('debian/missing-md5sum-file/foobar.md5sums')
        results = debian.parse_debian_files_list(
            location=test_file,
            datasource_id=debian.DebianInstalledMd5sumFilelistHandler.datasource_id,
            package_type=debian.DebianInstalledMd5sumFilelistHandler.default_package_type,
        )

        assert list(results) == []

    @skipIf(on_windows, 'File names cannot contain colons on Windows')
    def test_multi_arch_is_same(self):
        test_dir = self.extract_test_tar('debian/same-multi-arch.tgz')
        test_file = os.path.join(test_dir, 'same-multi-arch/libatk-adaptor:amd64.md5sums')

        results = debian.parse_debian_files_list(
            location=test_file,
            datasource_id=debian.DebianInstalledMd5sumFilelistHandler.datasource_id,
            package_type=debian.DebianInstalledMd5sumFilelistHandler.default_package_type,
        )

        expected_loc = self.get_test_loc('debian/libatk-adaptor-amd64.md5sums.expected.json', must_exist=False)
        self.check_packages_data(results, expected_loc, must_exist=False, regen=REGEN_TEST_FIXTURES)

    def test_parse_debian_files_list_no_arch(self):
        test_file = self.get_test_loc('debian/files-md5sums/mokutil.md5sums')
        results = debian.parse_debian_files_list(
            location=test_file,
            datasource_id=debian.DebianInstalledMd5sumFilelistHandler.datasource_id,
            package_type=debian.DebianInstalledMd5sumFilelistHandler.default_package_type,
        )

        expected_loc = self.get_test_loc('debian/files-md5sums/mokutil.md5sums.expected.json', must_exist=False)
        self.check_packages_data(results, expected_loc, must_exist=False, regen=REGEN_TEST_FIXTURES)

    @skipIf(on_windows, 'File names cannot contain colons on Windows')
    def test_parse_debian_files_list_with_arch(self):
        test_file = self.get_test_loc('debian/files-md5sums/mokutil.md5sums', copy=True)
        from commoncode import fileutils
        from pathlib import Path
        src = Path(test_file)
        test_dir = src.parent
        test_file = str(test_dir / "mockutil:amd64.md5sum")
        fileutils.copyfile(str(src), test_file)

        results = debian.parse_debian_files_list(
            location=test_file,
            datasource_id=debian.DebianInstalledMd5sumFilelistHandler.datasource_id,
            package_type=debian.DebianInstalledMd5sumFilelistHandler.default_package_type,
        )

        expected_loc = self.get_test_loc('debian/files-md5sums/mokutil-amd64.md5sums.expected.json', must_exist=False)
        self.check_packages_data(results, expected_loc, must_exist=False, regen=REGEN_TEST_FIXTURES)

    def test_build_package_data_from_package_filename_deb_does_not_crash_on_version(self):
        filename = 'libapache2-mod-md_2.4.38-3+deb10u10_amd64.deb'
        result = build_package_data_from_package_filename(
            filename=filename,
            datasource_id='debian_deb',
            package_type='deb',
        )
        assert str(result.purl) == 'pkg:deb/libapache2-mod-md@2.4.38-3%2Bdeb10u10?architecture=amd64'

    def test_build_package_data_from_package_filename_orig_sdoes_not_crash_on_version(self):
        filename = 'abseil_0~20200923.3.orig.tar.gz'
        result = build_package_data_from_package_filename(
            filename=filename,
            datasource_id='debian_deb',
            package_type='deb',
        )
        assert str(result.purl) == 'pkg:deb/abseil@0~20200923.3'

    def test_build_package_data_from_package_filename_debian_tar_sdoes_not_crash_on_version(self):
        filename = 'abseil_20220623.1-1.debian.tar.xz'
        result = build_package_data_from_package_filename(
            filename=filename,
            datasource_id='debian_deb',
            package_type='deb',
        )
        assert str(result.purl) == 'pkg:deb/abseil@20220623.1-1'

    def test_DebianDebPackageHandler_parse_does_not_crash_on_version(self):
        location = 'foo/bar/libapache2-mod-md_2.4.38-3+deb10u10_amd64.deb'
        result = list(DebianDebPackageHandler.parse(location))[0]
        assert str(result.purl) == 'pkg:deb/libapache2-mod-md@2.4.38-3%2Bdeb10u10?architecture=amd64'
