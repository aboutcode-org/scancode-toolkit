#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import attr

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
from packagedcode import jar_manifest
from packagedcode import maven
from packagedcode import models
from packagedcode import msi
from packagedcode import npm
from packagedcode import nuget
from packagedcode import opam
from packagedcode import phpcomposer
from packagedcode import pubspec
from packagedcode import pypi
from packagedcode import readme
from packagedcode import rpm
from packagedcode import rubygems
from packagedcode import win_pe
from packagedcode import windows


# Note: the order matters: from the most to the least specific
# Package classes MUST be added to this list to be active
PACKAGE_MANIFEST_TYPES = [
    rpm.RpmManifest,
    debian.DebianPackage,

    models.JavaJar,
    jar_manifest.JavaManifest,
    models.JavaEar,
    models.JavaWar,
    maven.MavenPomPackage,
    jar_manifest.IvyJar,
    models.JBossSar,
    models.Axis2Mar,

    about.Aboutfile,
    npm.PackageJson,
    npm.PackageLockJson,
    npm.YarnLockJson,
    phpcomposer.ComposerJson,
    phpcomposer.ComposerLock,
    haxe.HaxelibJson,
    cargo.CargoToml,
    cargo.CargoLock,
    cocoapods.Podspec,
    cocoapods.PodfileLock,
    cocoapods.PodspecJson,
    opam.OpamFile,
    models.MeteorPackage,
    bower.BowerJson,
    freebsd.CompactManifest,
    models.CpanModule,
    rubygems.GemArchive,
    rubygems.GemArchiveExtracted,
    rubygems.GemSpec,
    rubygems.GemfileLock,
    models.AndroidApp,
    models.AndroidLibrary,
    models.MozillaExtension,
    models.ChromeExtension,
    models.IOSApp,
    pypi.MetadataFile,
    pypi.BinaryDistArchive,
    pypi.SourceDistArchive,
    pypi.SetupPy,
    pypi.DependencyFile,
    pypi.PipfileLock,
    pypi.RequirementsFile,
    golang.GoMod,
    golang.GoSum,
    models.CabPackage,
    models.InstallShieldPackage,
    models.NSISInstallerPackage,
    nuget.Nuspec,
    models.SharPackage,
    models.AppleDmgPackage,
    models.IsoImagePackage,
    models.SquashfsPackage,
    chef.MetadataJson,
    chef.Metadatarb,
    build.BazelPackage,
    build.BuckPackage,
    build.AutotoolsPackage,
    conda.Condayml,
    win_pe.WindowsExecutableManifest,
    readme.ReadmeManifest,
    build.MetadataBzl,
    msi.MsiInstallerPackage,
    windows.MicrosoftUpdateManifest,
    pubspec.PubspecYaml,
    pubspec.PubspecLock
]

PACKAGE_INSTANCE_TYPES = [
    pypi.PythonPackageInstance
]

PACKAGE_MANIFESTS_BY_TYPE = {
    cls.default_type: cls
    for cls in PACKAGE_MANIFEST_TYPES
}

PACKAGE_INSTANCES_BY_TYPE = {
    cls.default_type: cls
    for cls in PACKAGE_INSTANCE_TYPES
}

def check_package_manifest_classes():

    # We cannot have two package classes with the same type
    if len(PACKAGE_MANIFESTS_BY_TYPE) != len(PACKAGE_MANIFEST_TYPES):
        seen_types = {}
        for pmt in PACKAGE_MANIFEST_TYPES:
            manifest = pmt()
            assert manifest.package_manifest_type
            seen = seen_types.get(manifest.package_manifest_type)
            if seen:
                msg = ('Invalid duplicated packagedcode.Package types: '
                    '"{}:{}" and "{}:{}" have the same type.'
                    .format(manifest.package_manifest_type, manifest.__name__, seen.package_manifest_type, seen.__name__,))
                raise Exception(msg)
            else:
                seen_types[manifest.package_manifest_type] = manifest


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
    ptype_class = PACKAGE_MANIFESTS_BY_TYPE.get(ptype)
    return ptype_class or default


def get_package_instance(scan_data):
    """
    Return a Package instance re-built from a mapping of ``scan_data`` native
    Python data that has the structure of a scan. Known attributes that store a
    list of objects are also "rehydrated" (such as models.Party).

    The Package instance will use the Package subclass that supports the
    provided package "type" when possible or the base Package class otherwise.

    Unknown attributes provided in ``scan_data`` that do not exist as fields in
    the Package class are kept as items in the Package.extra_data mapping.
    An Exception is raised if an "unknown attribute" name already exists as
    a Package.extra_data key.
    """
    # TODO: consider using a proper library for this such as cattrs,
    # marshmallow, etc. or use the field type that we declare.

    # Each of these are lists of class instances tracked here, which are stored
    # as a list of mappings in scanc_data
    list_field_types_by_name = {
        'parties': models.Party,
        'dependencies': models.DependentPackage,
        'installed_files': models.PackageFile,
    }

    # these are computed attributes serialized on a package
    # that should not be recreated when serializing
    computed_attributes = set([
        'purl',
        'repository_homepage_url',
        'repository_download_url',
        'api_data_url'
    ])

    # re-hydrate lists of typed objects
    klas = get_package_class(scan_data)
    existing_fields = attr.fields_dict(klas)

    extra_data = scan_data.get('extra_data', {}) or {}
    package_data = {}

    for key, value in scan_data.items():
        if not value or key in computed_attributes:
            continue

        field = existing_fields.get(key)

        if not field:
            if key not in extra_data:
                # keep unknown field as extra data
                extra_data[key] = value
                continue
            else:
                raise Exception(
                    f'Invalid scan_data with duplicated key: {key}={value!r} '
                    f'present both as attribute AND as extra_data: '
                    f'{key}={extra_data[key]!r}'
                )

        list_field_type = list_field_types_by_name.get(key)
        if not list_field_type:
            # this is a plain known field
            package_data[key] = value
            continue

        # Since we have a list_field_type, value must be a list of mappings:
        # we transform it in a list of objects.

        if not isinstance(value, list):
            raise Exception(
                f'Invalid scan_data with unknown data structure. '
                f'Expected the value to be a list of dicts and not a '
                f'{type(value)!r} for {key}={value!r}'
            )

        objects = list(_build_objects_list(values=value, klass=list_field_type))
        package_data[key] = objects

    return klas(**package_data)


def _build_objects_list(values, klass):
    """
    Yield ``klass`` objects built from a ``values`` list of mappings.
    """
    # Since we have a list_field_type, value must be a list of mappings:
    # we transform it in a list of objects.

    if not isinstance(values, list):
        raise Exception(
            f'Invalid scan_data with unknown data structure. '
            f'Expected the value to be a list of dicts and not a '
            f'{type(values)!r} for {values!r}'
        )

    for val in values:
        if not val:
            continue

        if not isinstance(val, dict):
            raise Exception(
                f'Invalid scan_data with unknown data structure. '
                f'Expected the value to be a mapping for and not a '
                f'{type(val)!r} for {values!r}'
            )

        yield klass.create(**val)

