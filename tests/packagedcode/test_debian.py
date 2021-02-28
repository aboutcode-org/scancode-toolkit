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
from packagedcode import models
from packages_test_utils import PackageTester
from packages_test_utils import check_result_equals_expected_json


@skipIf(on_windows, 'These tests contain files that are not legit on Windows.')
class TestDebianPackageGetInstalledPackages(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_basic_rootfs(self):
        test_rootfs = self.extract_test_tar('debian/basic-rootfs.tar.gz')
        result = [package.to_dict(_detailed=True)
            for package in debian.get_installed_packages(test_rootfs)]
        expected = self.get_test_loc('debian/basic-rootfs-expected.json')
        check_result_equals_expected_json(result, expected, regen=False)

    def test_basic_rootfs_with_licenses_and_copyrights(self):
        test_rootfs = self.extract_test_tar('debian/basic-rootfs.tar.gz')
        result = [package.to_dict(_detailed=True)
            for package in debian.get_installed_packages(test_rootfs, detect_licenses=True)]
        expected = self.get_test_loc('debian/basic-rootfs-with-licenses-expected.json')
        check_result_equals_expected_json(result, expected, regen=False)

    def test_get_installed_packages_should_not_fail_on_rootfs_without_installed_debian_packages(self):
        test_rootfs = self.get_temp_dir()
        result = list(debian.get_installed_packages(test_rootfs))
        assert result == []


class TestDebian(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_status_file_not_a_status_file(self):
        test_file = self.get_test_loc('debian/not-a-status-file')
        test_packages = list(debian.parse_status_file(test_file))
        assert test_packages == []

    def test_parse_status_file_non_existing_file(self):
        test_file = os.path.join(self.get_test_loc('debian'), 'foobarbaz')
        try:
            list(debian.parse_status_file(test_file))
            self.fail('FileNotFoundError not raised')
        except FileNotFoundError:
            pass

    def test_parse_status_file_basic(self):
        test_file = self.get_test_loc('debian/basic/status')
        expected_loc = self.get_test_loc('debian/basic/status.expected')
        # specify ubuntu distro as this was the source of the test `status` file
        packages = list(debian.parse_status_file(test_file, distro='ubuntu'))
        self.check_packages(packages, expected_loc, regen=False)

    def test_parse_status_file_perl_error(self):
        test_file = self.get_test_loc('debian/mini-status/status')
        expected_loc = self.get_test_loc('debian/mini-status/status.expected')
        packages = list(debian.parse_status_file(test_file, distro='debian'))
        self.check_packages(packages, expected_loc, regen=False)

    @skipIf(on_windows, 'File names cannot contain colons on Windows')
    def test_parse_end_to_end(self):
        test_dir = self.extract_test_tar('debian/end-to-end.tgz')
        test_info_dir = os.path.join(test_dir, 'end-to-end')
        test_file = os.path.join(test_info_dir, 'status')

        packages = list(debian.parse_status_file(test_file, distro='ubuntu'))
        assert len(packages) == 1

        test_package = packages[0]

        expected = [
            models.PackageFile('/lib/x86_64-linux-gnu/libncurses.so.5.9', md5='23c8a935fa4fc7290d55cc5df3ef56b1'),
            models.PackageFile('/usr/lib/x86_64-linux-gnu/libform.so.5.9', md5='98b70f283324e89db5787a018a54adf4'),
            models.PackageFile('/usr/lib/x86_64-linux-gnu/libmenu.so.5.9', md5='e3a0f5154928da2da234920343ac14b2'),
            models.PackageFile('/usr/lib/x86_64-linux-gnu/libpanel.so.5.9', md5='a927e7d76753bb85f5a784b653d337d2')
        ]

        resources = test_package.get_list_of_installed_files(test_info_dir)

        assert len(resources) == 4
        assert resources == expected

    def test_get_installed_packages_ubuntu_with_missing_md5sums(self):
        test_root_dir = self.get_test_loc('debian/ubuntu-var-lib-dpkg/')

        packages = debian.get_installed_packages(root_dir=test_root_dir, distro='ubuntu', detect_licenses=False)
        result = [p.to_dict(_detailed=True) for p in packages]
        expected = self.get_test_loc('debian/ubuntu-var-lib-dpkg/expected.json')
        check_result_equals_expected_json(result, expected, regen=False)


class TestDebianGetListOfInstalledFiles(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_missing_md5sum_file(self):
        test_info_dir = self.get_test_loc('debian/missing-md5sum-file')

        test_pkg = debian.DebianPackage(
            name='libatk-adaptor',
            multi_arch='same',
            qualifiers={'arch':'amd64'}
        )

        assert test_pkg.get_list_of_installed_files(test_info_dir) == []

    @skipIf(on_windows, 'File names cannot contain colons on Windows')
    def test_multi_arch_is_same(self):
        test_dir = self.extract_test_tar('debian/same-multi-arch.tgz')
        test_info_dir = os.path.join(test_dir, 'same-multi-arch')

        test_pkg = debian.DebianPackage(
            name='libatk-adaptor',
            multi_arch='same',
            qualifiers={'arch':'amd64'}
        )

        expected = [
             models.PackageFile('/usr/lib/gnome-settings-daemon-3.0/gtk-modules/at-spi2-atk.desktop', md5='34900bd11562f427776ed2c05ba6002d'),
             models.PackageFile('/usr/lib/unity-settings-daemon-1.0/gtk-modules/at-spi2-atk.desktop', md5='34900bd11562f427776ed2c05ba6002d'),
             models.PackageFile('/usr/lib/x86_64-linux-gnu/gtk-2.0/modules/libatk-bridge.so', md5='6ddbc10b64afe708945c3b1497714aaa'),
             models.PackageFile('/usr/share/doc/libatk-adaptor/NEWS.gz', md5='3a24add33624132b6b3b4c2ed08a4394'),
             models.PackageFile('/usr/share/doc/libatk-adaptor/README', md5='452c2e9db46c9ac92a10e700d116b120'),
             models.PackageFile('/usr/share/doc/libatk-adaptor/copyright', md5='971e4b2093741db8c51d263cd5c3ee48'),
        ]

        results = test_pkg.get_list_of_installed_files(test_info_dir)

        assert len(results) == 6
        assert results == expected

    def test_multi_arch_is_foreign(self):
        test_info_dir = self.get_test_loc('debian/foreign-multi-arch')

        test_pkg = debian.DebianPackage(
            name='fonts-sil-abyssinica',
            multi_arch='foreign',
            qualifiers={'arch':'amd64'}
        )

        expected = [
            models.PackageFile('/usr/share/bug/fonts-sil-abyssinica/presubj', md5='7faf213b3c06e818b9976cc2ae5af51a'),
            models.PackageFile('/usr/share/bug/fonts-sil-abyssinica/script', md5='672370efca8bffa183e2828907e0365d'),
            models.PackageFile('/usr/share/doc/fonts-sil-abyssinica/OFL-FAQ.txt.gz', md5='ea72ae1d2ba5471ef54b132c79b1a03b'),
            models.PackageFile('/usr/share/doc/fonts-sil-abyssinica/README.Debian', md5='f497d6bfc7ca4d423d703fabb7ff2e4c'),
            models.PackageFile('/usr/share/doc/fonts-sil-abyssinica/changelog.Debian.gz', md5='7f81bc6ed7506b95af01b5eef76662bb'),
            models.PackageFile('/usr/share/doc/fonts-sil-abyssinica/copyright', md5='13d9a840b6db71f7060670be0aafa953'),
            models.PackageFile('/usr/share/doc/fonts-sil-abyssinica/documentation/AbyssinicaSILGraphiteFontFeatures.odt', md5='0e4a5ad6839067740e81a3e1244b0b16'),
            models.PackageFile('/usr/share/doc/fonts-sil-abyssinica/documentation/AbyssinicaSILGraphiteFontFeatures.pdf.gz', md5='8fee9c92ecd425c71217418b8370c5ae'),
            models.PackageFile('/usr/share/doc/fonts-sil-abyssinica/documentation/AbyssinicaSILOpenTypeFontFeatures.pdf.gz', md5='2cc8cbe21730258dd03a465e045066cc'),
            models.PackageFile('/usr/share/doc/fonts-sil-abyssinica/documentation/AbyssinicaSILTypeSample.pdf.gz', md5='40948ce7d8e4b1ba1c7043ec8926edf9'),
            models.PackageFile('/usr/share/doc/fonts-sil-abyssinica/documentation/AbyssinicaSILTypeTunerGuide.pdf.gz', md5='36ca1d62ca7365216e8bda952d2461e6'),
            models.PackageFile('/usr/share/doc/fonts-sil-abyssinica/documentation/DOCUMENTATION.txt', md5='491295c116dbcb74bcad2d78a56aedbe'),
            models.PackageFile('/usr/share/doc/fonts-sil-abyssinica/documentation/SILEthiopicPrivateUseAreaBlock.pdf.gz', md5='bea5aeeb76a15c2c1b8189d1b2437b31'),
            models.PackageFile('/usr/share/fonts/truetype/abyssinica/AbyssinicaSIL-R.ttf', md5='9e3d4310af3892a739ba7b1189c44dca'),
        ]

        results = test_pkg.get_list_of_installed_files(test_info_dir)

        assert len(results) == 14
        assert results == expected

    def test_multi_arch_is_missing(self):
        test_info_dir = self.get_test_loc('debian/missing-multi-arch')

        test_pkg = debian.DebianPackage(
            name='mokutil',
            qualifiers={'arch':'amd64'}
        )

        expected = [
            models.PackageFile('/usr/bin/mokutil', md5='7a1a2629613d260e43dabc793bebdf19'),
            models.PackageFile('/usr/share/bash-completion/completions/mokutil', md5='9086049384eaf0360dca4371ca50acbf'),
            models.PackageFile('/usr/share/doc/mokutil/changelog.Debian.gz', md5='b3f4bb874bd61e4609823993857b9c17'),
            models.PackageFile('/usr/share/doc/mokutil/copyright', md5='24dd593b630976a785b4c5ed097bbd96'),
            models.PackageFile('/usr/share/man/man1/mokutil.1.gz', md5='b608675058a943d834129b6972b8509a'),
        ]
        results = test_pkg.get_list_of_installed_files(test_info_dir)

        assert len(results) == 5
        assert results == expected
