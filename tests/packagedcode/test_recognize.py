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
from packagedcode.recognize import recognize_packaged_archives


class TestRecognize(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_recognize_packaged_archives_deb(self):
        test_file = self.get_test_loc('archives/adduser_3.112ubuntu1_all.deb')
        package = recognize_packaged_archives(test_file)
        assert isinstance(package, models.DebianPackage)

    def test_recognize_packaged_archives_rpm(self):
        test_file = self.get_test_loc('archives/alfandega-2.2-2.rh80.src.rpm')
        package = recognize_packaged_archives(test_file)
        assert isinstance(package, models.RpmPackage)

    def test_recognize_packaged_archives_cab(self):
        test_file = self.get_test_loc('archives/basic.cab')
        package = recognize_packaged_archives(test_file)
        assert isinstance(package, models.CabPackage)

    def test_recognize_packaged_archives_rar(self):
        test_file = self.get_test_loc('archives/basic.rar')
        package = recognize_packaged_archives(test_file)
        assert isinstance(package, models.RarPackage)

    def test_recognize_packaged_archives_zip(self):
        test_file = self.get_test_loc('archives/myarch-2.3.0.7z')
        package = recognize_packaged_archives(test_file)
        assert isinstance(package, models.ZipPackage)

    def test_recognize_packaged_archives_gem(self):
        test_file = self.get_test_loc('archives/mysmallidea-address_standardization-0.4.1.gem')
        package = recognize_packaged_archives(test_file)
        assert isinstance(package, models.RubyGemPackage)

    def test_recognize_packaged_archives_jar(self):
        test_file = self.get_test_loc('archives/simple.jar')
        package = recognize_packaged_archives(test_file)
        assert isinstance(package, models.JarPackage)

    def test_recognize_packaged_archives_iso(self):
        test_file = self.get_test_loc('archives/small.iso')
        package = recognize_packaged_archives(test_file)
        assert isinstance(package, models.IsoImagePackage)

    def test_recognize_packaged_archives_tarball(self):
        test_file = self.get_test_loc('archives/tarred_bzipped.tar.bz2')
        package = recognize_packaged_archives(test_file)
        assert isinstance(package, models.TarPackage)
