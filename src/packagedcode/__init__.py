#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from packagedcode import about
from packagedcode import bower
from packagedcode import build
from packagedcode import cargo
from packagedcode import chef
from packagedcode import debian
from packagedcode import conda
from packagedcode import cocoapods
from packagedcode import freebsd
from packagedcode import golang
from packagedcode import haxe
from packagedcode import maven
from packagedcode import models
from packagedcode import npm
from packagedcode import nuget
from packagedcode import opam
from packagedcode import phpcomposer
from packagedcode import pypi
from packagedcode import rpm
from packagedcode import rubygems
from packagedcode import win_pe


# Note: the order matters: from the most to the least specific
# Package classes MUST be added to this list to be active
PACKAGE_TYPES = [
    rpm.RpmPackage,
    debian.DebianPackage,

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
    cocoapods.CocoapodsPackage,
    opam.OpamPackage,
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
    golang.GolangPackage,
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
    build.BazelPackage,
    build.BuckPackage,
    build.AutotoolsPackage,
    conda.CondaPackage,
    win_pe.WindowsExecutable,
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


_props = frozenset([
    'api_data_url',
    'repository_download_url',
    'purl',
    'repository_homepage_url']
)


def get_package_instance(scan_data, properties=_props):
    """
    Given a `scan_data` native Python mapping representing a Package, return a
    Package object instance.
    """
    # remove computed properties from attributes
    scan_data = {k: v for k, v in scan_data.items() if k not in properties}
    klas = get_package_class(scan_data)
    return klas(**scan_data)
