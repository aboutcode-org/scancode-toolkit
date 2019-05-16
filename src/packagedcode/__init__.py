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

from __future__ import absolute_import
from __future__ import unicode_literals

from packagedcode import chef
from packagedcode import models
from packagedcode import about
from packagedcode import bower
from packagedcode import cargo
from packagedcode import freebsd
from packagedcode import haxe
from packagedcode import maven
from packagedcode import npm
from packagedcode import nuget
from packagedcode import phpcomposer
from packagedcode import pypi
from packagedcode import rpm
from packagedcode import rubygems


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

    about.AboutPackage,
    npm.NpmPackage,
    phpcomposer.PHPComposerPackage,
    haxe.HaxePackage,
    cargo.RustCargoCrate,
    models.MeteorPackage,
    bower.BowerPackage,
    freebsd.FreeBSDPackage,
    models.CpanModule,
    rubygems.RubyGem,
    models.AndroidApp,
    models.AndroidLibrary,
    models.MozillaExtension,
    models.ChromeExtension,
    models.IOSApp,
    pypi.PythonPackage,
    models.CabPackage,
    models.MsiInstallerPackage,
    models.InstallShieldPackage,
    models.NSISInstallerPackage,
    nuget.NugetPackage,
    models.SharPackage,
    models.AppleDmgPackage,
    models.IsoImagePackage,
    models.SquashfsPackage,
    chef.ChefPackage,
]

PACKAGES_BY_TYPE = {cls.default_type: cls for cls in PACKAGE_TYPES}

# We cannot have two package classes with the same type
if len(PACKAGES_BY_TYPE) != len(PACKAGE_TYPES):
    seen_types = {}
    for pt in PACKAGE_TYPES:
        seen = seen_types.get(pt.default_type)
        if seen:
            msg = ('Invalid duplicated packagedcode.Package types: '
                   '"{}:{}" and "{}:{}" have the same type.'
                  .format(pt.default_type, pt.__name__, seen.default_type, seen.__name__,))
            raise Exception(msg)
        else:
            seen_types[pt.default_type] = pt


def get_package_class(scan_data, default=models.Package):
    """
    Return the Package subclass that corresponds to the package type in a
    mapping of package `scan_data`.

    For example:
    >>> data = {'type': 'cpan'}
    >>> assert models.CpanModule == get_package_class(data)
    >>> data = {'type': 'some stuff'}
    >>> assert models.Package == get_package_class(data)
    >>> data = {'type': None}
    >>> assert models.Package == get_package_class(data)
    >>> data = {}
    >>> assert models.Package == get_package_class(data)
    >>> data = []
    >>> assert models.Package == get_package_class(data)
    >>> data = None
    >>> assert models.Package == get_package_class(data)
    """
    ptype = scan_data and scan_data.get('type') or None
    if not ptype:
        # basic type for default package types
        return default
    ptype_class = PACKAGES_BY_TYPE.get(ptype)
    return ptype_class or default
