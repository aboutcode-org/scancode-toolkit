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

from collections import OrderedDict
from packagedcode.models import AndroidAppPackage
from packagedcode.models import AndroidLibPackage
from packagedcode.models import AppleDmgPackage
from packagedcode.models import AssertedLicense
from packagedcode.models import CabPackage
from packagedcode.models import InstallShieldPackage
from packagedcode.models import IsoImagePackage
from packagedcode.models import JarPackage
from packagedcode.models import JarAppPackage
from packagedcode.models import MozillaExtPackage
from packagedcode.models import MsiInstallerPackage
from packagedcode.models import NugetPackage
from packagedcode.models import NSISInstallerPackage
from packagedcode.models import PythonPackage
from packagedcode.models import Package
from packagedcode.models import Party
from packagedcode import models
from packagedcode.models import RarPackage
from packagedcode.models import RpmPackage
from packagedcode.models import RubyGemPackage
from packagedcode.models import SharPackage
from packagedcode.models import TarPackage
from packagedcode.models import ZipPackage
from unittest.case import expectedFailure


class TestModels(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_model_creation_and_dump(self):
        aap = models.AndroidAppPackage()
        result = aap.as_dict()
        expected = OrderedDict([('type', 'Android app'),
                                ('packaging', 'archive'),
                                ('primary_language', 'Java')])
        assert expected == result

    def test_validate_package(self):
        package = Package(dict(
            name='Sample',
            summary='Some package',
            payload_type='source',
            authors=[Party(
                dict(
                    name='Some Author',
                    email='some@email.com'
                    )
                )
            ],
            keywords=['some', 'keyword'],
            vcs_tool='git',
            asserted_licenses=[
                AssertedLicense(dict(
                    license='apache-2.0'
                    )
                )
            ],
            )
        )
        assert 'Sample' == package.name
        assert 'Some package' == package.summary
        assert 'source' == package.payload_type
        assert 'Some Author' == package.authors[0].name
        assert ['some', 'keyword'] == package.keywords
        assert 'apache-2.0' == package.asserted_licenses[0].license

    def test_rpm_recognize_package(self):
        input = self.get_test_loc('package_models/rpm/elfinfo-1.0-1.fc9.src.rpm')
        output = RpmPackage.recognize_package(input)
        assert output is not None

    def test_jar_recognize_package(self):
        input = self.get_test_loc('package_models/jar/org.apache.felix.ipojo.handler.extender.pattern-0.8.0.jar')
        output = JarPackage.recognize_package(input)
        assert output is not None

    @expectedFailure
    def test_jarapp_recognize_package(self):
        input = self.get_test_loc('package_models/jarapp/ear-example-0.12.ear')
        output = JarAppPackage.recognize_package(input)
        assert output is not None

    def test_rubygem_recognize_package(self):
        input = self.get_test_loc('package_models/rubygem/actionmailer-4.0.3.gem')
        output = RubyGemPackage.recognize_package(input)
        assert output is not None

    @expectedFailure
    def test_androidapp_recognize_package(self):
        input = self.get_test_loc('package_models/androidapp/net.tecnotopia.SimpleCalculator.apk')
        output = AndroidAppPackage.recognize_package(input)
        assert output is not None

    def test_androidlib_recognize_package(self):
        input = self.get_test_loc('package_models/androidlib/pixlhash-0.1.0.aar')
        output = AndroidLibPackage.recognize_package(input)
        assert output is not None

    def test_mozillaext_recognize_package(self):
        input = self.get_test_loc('package_models/mozillaext/-0.1.3.1-fx.xpi')
        output = MozillaExtPackage.recognize_package(input)
        assert output is not None

    def test_python_recognize_package(self):
        input = self.get_test_loc('package_models/python/url-0.1.4.3-py2.py3-none-any.whl')
        output = PythonPackage.recognize_package(input)
        assert output is not None

    def test_cab_recognize_package(self):
        input = self.get_test_loc('package_models/cab/BTToggler_v1.0.CAB')
        output = CabPackage.recognize_package(input)
        assert output is not None

    def test_msiinstaller_recognize_package(self):
        input = self.get_test_loc('package_models/msiinstaller/Tycho-0.1.msi')
        output = MsiInstallerPackage.recognize_package(input)
        assert output is not None

    def test_installshield_recognize_package(self):
        input = self.get_test_loc('package_models/installshield/BalloonRSS_1.0_setup.exe')
        output = InstallShieldPackage.recognize_package(input)
        assert output is not None

    def test_nuget_recognize_package(self):
        input = self.get_test_loc('package_models/nuget/elmah.xml.1.2.nupkg')
        output = NugetPackage.recognize_package(input)
        assert output is not None

    def test_nsisinstaller_recognize_package(self):
        input = self.get_test_loc('package_models/nsisinstaller/BalloonRSS_1.0_setup.exe')
        output = NSISInstallerPackage.recognize_package(input)
        assert output is not None

    @expectedFailure
    def test_shar_recognize_package(self):
        input = self.get_test_loc('package_models/shar/WinMusik-3.0.6-FreeBSD-Port.shar')
        output = SharPackage.recognize_package(input)
        assert output is not None

    def test_appledmg_recognize_package(self):
        input = self.get_test_loc('package_models/appledmg/Darwine-x86-0.9.6.dmg')
        output = AppleDmgPackage.recognize_package(input)
        assert output is not None

    def test_isoimage_recognize_package(self):
        input = self.get_test_loc('package_models/isoimage/Luxur-alpha.iso')
        output = IsoImagePackage.recognize_package(input)
        assert output is not None

    def test_rar_recognize_package(self):
        input = self.get_test_loc('package_models/rar/fuverse0.001.rar')
        output = RarPackage.recognize_package(input)
        assert output is not None

    def test_tar_recognize_package(self):
        input = self.get_test_loc('package_models/tar/termometr-1.0.tar.gz')
        output = TarPackage.recognize_package(input)
        assert output is not None

    def test_zip_recognize_package(self):
        input = self.get_test_loc('package_models/zip/slaaf2-0.2-win32.zip')
        output = ZipPackage.recognize_package(input)
        assert output is not None
