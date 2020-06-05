#
# Copyright (c) nexB Inc. and others. All rights reserved.
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

import os.path

import pytest

from packagedcode import debian
from packages_test_utils import PackageTester


class TestDebian(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_status_file_not_a_status_file(self):
        test_file = self.get_test_loc('debian/not-a-status-file')
        test_packages = list(debian.parse_status_file(test_file))
        assert [] == test_packages

    def test_parse_status_file_basic(self):
        test_file = self.get_test_loc('debian/basic/status')
        expected_loc = self.get_test_loc('debian/basic/status.expected')
        # specify ubuntu distro as this was the source of the test `status` file
        packages = list(debian.parse_status_file(test_file, distro='ubuntu'))
        self.check_packages(packages, expected_loc, regen=False)


class TestDebianGetListOfInstalledFiles(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')
    
    def test_multi_arch_is_same(self):
        test_info_dir = self.get_test_loc('debian/same-multi-arch')

        test_pkg = debian.DebianPackage(
            name='libatk-adaptor',
            multi_arch='same',
            qualifiers={'arch':'amd64'}
        )

        expected = [
             ('usr/lib/gnome-settings-daemon-3.0/gtk-modules/at-spi2-atk.desktop', '34900bd11562f427776ed2c05ba6002d'),
             ('usr/lib/unity-settings-daemon-1.0/gtk-modules/at-spi2-atk.desktop', '34900bd11562f427776ed2c05ba6002d'),
             ('usr/lib/x86_64-linux-gnu/gtk-2.0/modules/libatk-bridge.so', '6ddbc10b64afe708945c3b1497714aaa'),
             ('usr/share/doc/libatk-adaptor/NEWS.gz', '3a24add33624132b6b3b4c2ed08a4394'),
             ('usr/share/doc/libatk-adaptor/README', '452c2e9db46c9ac92a10e700d116b120'),
             ('usr/share/doc/libatk-adaptor/copyright', '971e4b2093741db8c51d263cd5c3ee48'),
        ]

        results = list(test_pkg.get_list_of_installed_files(test_info_dir))

        assert 6 == len(results)
        assert expected == results
        
    def test_multi_arch_is_foreign(self):
        test_info_dir = self.get_test_loc('debian/foreign-multi-arch')

        test_pkg = debian.DebianPackage(
            name='fonts-sil-abyssinica',
            multi_arch='foreign',
            qualifiers={'arch':'amd64'}
        )

        expected = [
          ('usr/share/bug/fonts-sil-abyssinica/presubj', '7faf213b3c06e818b9976cc2ae5af51a'),
          ('usr/share/bug/fonts-sil-abyssinica/script',  '672370efca8bffa183e2828907e0365d'),
          ('usr/share/doc/fonts-sil-abyssinica/OFL-FAQ.txt.gz', 'ea72ae1d2ba5471ef54b132c79b1a03b'),
          ('usr/share/doc/fonts-sil-abyssinica/README.Debian', 'f497d6bfc7ca4d423d703fabb7ff2e4c'),
          ('usr/share/doc/fonts-sil-abyssinica/changelog.Debian.gz', '7f81bc6ed7506b95af01b5eef76662bb'),
          ('usr/share/doc/fonts-sil-abyssinica/copyright', '13d9a840b6db71f7060670be0aafa953'),
          ('usr/share/doc/fonts-sil-abyssinica/documentation/AbyssinicaSILGraphiteFontFeatures.odt', '0e4a5ad6839067740e81a3e1244b0b16'),
          ('usr/share/doc/fonts-sil-abyssinica/documentation/AbyssinicaSILGraphiteFontFeatures.pdf.gz', '8fee9c92ecd425c71217418b8370c5ae'),
          ('usr/share/doc/fonts-sil-abyssinica/documentation/AbyssinicaSILOpenTypeFontFeatures.pdf.gz', '2cc8cbe21730258dd03a465e045066cc'),
          ('usr/share/doc/fonts-sil-abyssinica/documentation/AbyssinicaSILTypeSample.pdf.gz', '40948ce7d8e4b1ba1c7043ec8926edf9'),
          ('usr/share/doc/fonts-sil-abyssinica/documentation/AbyssinicaSILTypeTunerGuide.pdf.gz', '36ca1d62ca7365216e8bda952d2461e6'),
          ('usr/share/doc/fonts-sil-abyssinica/documentation/DOCUMENTATION.txt', '491295c116dbcb74bcad2d78a56aedbe'),
          ('usr/share/doc/fonts-sil-abyssinica/documentation/SILEthiopicPrivateUseAreaBlock.pdf.gz', 'bea5aeeb76a15c2c1b8189d1b2437b31'),
          ('usr/share/fonts/truetype/abyssinica/AbyssinicaSIL-R.ttf', '9e3d4310af3892a739ba7b1189c44dca'),
        ]
        
        results = list(test_pkg.get_list_of_installed_files(test_info_dir))

        assert 14 == len(results)
        assert expected == results

    def test_multi_arch_is_missing(self):
        test_info_dir = self.get_test_loc('debian/missing-multi-arch')

        test_pkg = debian.DebianPackage(
            name='mokutil',
            qualifiers={'arch':'amd64'}
        )

        expected = [
            ('usr/bin/mokutil', '7a1a2629613d260e43dabc793bebdf19'),
            ('usr/share/bash-completion/completions/mokutil', '9086049384eaf0360dca4371ca50acbf'),
            ('usr/share/doc/mokutil/changelog.Debian.gz', 'b3f4bb874bd61e4609823993857b9c17'),
            ('usr/share/doc/mokutil/copyright', '24dd593b630976a785b4c5ed097bbd96'),
            ('usr/share/man/man1/mokutil.1.gz', 'b608675058a943d834129b6972b8509a'),
        ]
        results = list(test_pkg.get_list_of_installed_files(test_info_dir))

        assert 5 == len(results)
        assert expected == results
