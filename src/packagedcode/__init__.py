#
# Copyright (c) 2016 nexB Inc. and others. All rights reserved.
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

from packagedcode import models
from packagedcode import maven
from packagedcode import npm
from packagedcode import nuget
from packagedcode import phpcomposer
from packagedcode import rpm


# Note: the order matters: from the most to the least specific
# Package classes MUST be added to this list to be active
PACKAGE_TYPES = [
    rpm.RpmPackage,
    models.DebianPackage,

    models.JavaJar,
    models.JavaEar,
    models.JavaWar,
    maven.MavenPomPackage,
    models.IvyJar,
    models.JBossSar,
    models.Axis2Mar,

    npm.NpmPackage,
    phpcomposer.PHPComposerPackage,
    models.MeteorPackage,
    models.BowerPackage,
    models.CpanModule,
    models.RubyGem,
    models.AndroidApp,
    models.AndroidLibrary,
    models.MozillaExtension,
    models.ChromeExtension,
    models.IOSApp,
    models.PythonPackage,
    models.CabPackage,
    models.MsiInstallerPackage,
    models.InstallShieldPackage,
    models.NSISInstallerPackage,
    nuget.NugetPackage,
    models.SharPackage,
    models.AppleDmgPackage,
    models.IsoImagePackage,
    models.SquashfsPackage,
    # these should always come last
    models.RarPackage,
    models.TarPackage,
    models.PlainZipPackage,
]

