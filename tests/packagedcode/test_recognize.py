#
# Copyright (c) 2015 nexB Inc. and others. All rights reserved.
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

from __future__ import absolute_import, print_function

import os.path

from commoncode.testcase import FileBasedTesting

from packagedcode import models
from packagedcode.recognize import packaged_archive
from packagedcode.recognize import ArchiveRecognizer


class TestRecognize(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_packaged_archive_deb(self):
        test_file = self.get_test_loc('archives/adduser_3.112ubuntu1_all.deb')
        package = packaged_archive(test_file)
        assert isinstance(package, models.DebianPackage)

    def test_packaged_archive_rpm(self):
        test_file = self.get_test_loc('archives/alfandega-2.2-2.rh80.src.rpm')
        package = packaged_archive(test_file)
        assert isinstance(package, models.RpmPackage)

    def test_packaged_archive_cab(self):
        test_file = self.get_test_loc('archives/basic.cab')
        package = packaged_archive(test_file)
        assert isinstance(package, models.CabPackage)

    def test_packaged_archive_rar(self):
        test_file = self.get_test_loc('archives/basic.rar')
        package = packaged_archive(test_file)
        assert isinstance(package, models.RarPackage)

    def test_packaged_archive_zip(self):
        test_file = self.get_test_loc('archives/myarch-2.3.0.7z')
        package = packaged_archive(test_file)
        assert isinstance(package, models.ZipPackage)

    def test_packaged_archive_gem(self):
        test_file = self.get_test_loc('archives/mysmallidea-address_standardization-0.4.1.gem')
        package = packaged_archive(test_file)
        assert isinstance(package, models.RubyGemPackage)

    def test_packaged_archive_jar(self):
        test_file = self.get_test_loc('archives/simple.jar')
        package = packaged_archive(test_file)
        assert isinstance(package, models.JarPackage)

    def test_packaged_archive_iso(self):
        test_file = self.get_test_loc('archives/small.iso')
        package = packaged_archive(test_file)
        assert isinstance(package, models.IsoImagePackage)

    def test_packaged_archive_tarball(self):
        test_file = self.get_test_loc('archives/tarred_bzipped.tar.bz2')
        package = packaged_archive(test_file)
        assert isinstance(package, models.TarPackage)

    def test_recognize_archive(self):
        test_dir = self.get_test_loc('archives')
        packages = list(ArchiveRecognizer().recon(test_dir))
        assert 9 == len(packages)
        assert all(isinstance(p, models.Package) for p in packages)
