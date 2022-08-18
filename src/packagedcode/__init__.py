#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import attr

from commoncode.system import on_linux
from packagedcode import about
from packagedcode import alpine
from packagedcode import bower
from packagedcode import build
from packagedcode import build_gradle
from packagedcode import cargo
from packagedcode import chef
from packagedcode import debian
from packagedcode import debian_copyright
from packagedcode import distro
from packagedcode import conda
from packagedcode import cocoapods
from packagedcode import cran
from packagedcode import freebsd
from packagedcode import godeps
from packagedcode import golang
from packagedcode import haxe
from packagedcode import jar_manifest
from packagedcode import maven
from packagedcode import misc
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

if on_linux:
    from packagedcode import msi
    from packagedcode import win_reg

# Note: the order matters: from the most to the least specific parser.
# a handler classes MUST be added to this list to be active
APPLICATION_PACKAGE_DATAFILE_HANDLERS = [
    about.AboutFileHandler,

    alpine.AlpineApkArchiveHandler,
    alpine.AlpineApkbuildHandler,

    bower.BowerJsonHandler,

    build_gradle.BuildGradleHandler,

    build.AutotoolsConfigureHandler,
    build.BazelBuildHandler,
    build.BuckMetadataBzlHandler,
    build.BuckPackageHandler,

    cargo.CargoLockHandler,
    cargo.CargoTomlHandler,

    chef.ChefMetadataJsonHandler,
    chef.ChefMetadataRbHandler,

    cocoapods.PodspecHandler,
    cocoapods.PodspecJsonHandler,
    cocoapods.PodfileLockHandler,
    cocoapods.PodfileHandler,

    conda.CondaYamlHandler,
    conda.CondaMetaYamlHandler,

    cran.CranDescriptionFileHandler,

    debian_copyright.DebianCopyrightFileInPackageHandler,
    debian.DebianDscFileHandler,

    debian.DebianControlFileInExtractedDebHandler,
    debian.DebianControlFileInSourceHandler,

    debian.DebianDebPackageHandler,
    debian.DebianMd5sumFilelistInPackageHandler,

    debian.DebianSourcePackageMetadataTarballHandler,
    debian.DebianSourcePackageTarballHandler,

    distro.EtcOsReleaseHandler,

    freebsd.CompactManifestHandler,

    godeps.GodepsHandler,
    golang.GoModHandler,
    golang.GoSumHandler,

    haxe.HaxelibJsonHandler,

    jar_manifest.JavaJarManifestHandler,

    maven.MavenPomXmlHandler,
    maven.MavenPomPropertiesHandler,

    misc.AndroidAppArchiveHandler,
    misc.AndroidLibraryHandler,
    misc.AppleDmgHandler,
    misc.Axis2MarArchiveHandler ,
    misc.Axis2MarModuleXmlHandler ,
    misc.CabArchiveHandler,
    misc.ChromeExtensionHandler,
    misc.CpanDistIniHandler ,
    misc.CpanMakefilePlHandler,
    misc.CpanManifestHandler,
    misc.CpanMetaJsonHandler,
    misc.CpanMetaYmlHandler,
    misc.InstallShieldPackageHandler,
    misc.IosAppIpaHandler,
    misc.IsoImageHandler,
    misc.IvyXmlHandler,

    misc.JavaEarAppXmlHandler ,
    misc.JavaEarHandler ,

    # is this redundant with Jar manifest?
    misc.JavaJarHandler,

    misc.JavaWarHandler,
    misc.JavaWarWebXmlHandler,

    misc.JBossSarHandler ,
    misc.JBossServiceXmlHandler ,

    misc.MeteorPackageHandler,
    misc.MozillaExtensionHandler,
    misc.NsisInstallerHandler,
    misc.SharArchiveHandler,
    misc.SquashfsImageHandler,
    npm.NpmPackageJsonHandler,
    npm.NpmPackageLockJsonHandler,
    npm.NpmShrinkwrapJsonHandler,
    npm.YarnLockV1Handler,
    npm.YarnLockV2Handler,

    nuget.NugetNupkgHandler,
    nuget.NugetNuspecHandler,

    opam.OpamFileHandler,

    phpcomposer.PhpComposerJsonHandler,
    phpcomposer.PhpComposerLockHandler,

    pubspec.DartPubspecYamlHandler,
    pubspec.DartPubspecLockHandler,

    pypi.PipfileHandler,
    pypi.PipfileLockHandler,
    pypi.PipRequirementsFileHandler,
    pypi.PypiEggHandler,
    # pypi.PypiSdistArchiveHandler,
    pypi.PypiWheelHandler,
    pypi.PyprojectTomlHandler,
    pypi.PythonEditableInstallationPkgInfoFile,
    pypi.PythonEggPkgInfoFile,
    pypi.PythonInstalledWheelMetadataFile,
    pypi.PythonSdistPkgInfoFile,
    pypi.PythonSetupPyHandler,
    pypi.SetupCfgHandler,

    readme.ReadmeHandler,

    rpm.RpmArchiveHandler,
    rpm.RpmSpecfileHandler,

    rubygems.GemMetadataArchiveExtractedHandler,
    rubygems.GemArchiveHandler,

    # the order of these handlers matter
    rubygems.GemfileInExtractedGemHandler,
    rubygems.GemfileHandler,

    # the order of these handlers matter
    rubygems.GemfileLockInExtractedGemHandler,
    rubygems.GemfileLockHandler,

    # the order of these handlers matter
    rubygems.GemspecInInstalledVendorBundleSpecificationsHandler,
    rubygems.GemspecInExtractedGemHandler,
    rubygems.GemspecHandler,

    windows.MicrosoftUpdateManifestHandler,

    win_pe.WindowsExecutableHandler,
]

if on_linux:
    APPLICATION_PACKAGE_DATAFILE_HANDLERS += [
        msi.MsiInstallerHandler,
    ]

SYSTEM_PACKAGE_DATAFILE_HANDLERS = [
    alpine.AlpineInstalledDatabaseHandler,

    debian_copyright.DebianCopyrightFileInPackageHandler,
    debian_copyright.DebianCopyrightFileInSourceHandler,

    # TODO: consider activating? debian_copyright.StandaloneDebianCopyrightFileHandler,

    debian.DebianDistrolessInstalledDatabaseHandler,

    debian.DebianInstalledFilelistHandler,
    debian.DebianInstalledMd5sumFilelistHandler,
    debian.DebianInstalledStatusDatabaseHandler,
]

if on_linux:
    SYSTEM_PACKAGE_DATAFILE_HANDLERS += [
        rpm.RpmInstalledBdbDatabaseHandler,
        rpm.RpmInstalledSqliteDatabaseHandler,
        rpm.RpmInstalledNdbDatabaseHandler,

        win_reg.InstalledProgramFromDockerSoftwareDeltaHandler,
        win_reg.InstalledProgramFromDockerFilesSoftwareHandler,
        win_reg.InstalledProgramFromDockerUtilityvmSoftwareHandler,
    ]

ALL_DATAFILE_HANDLERS= (
    APPLICATION_PACKAGE_DATAFILE_HANDLERS + [
        p for p in SYSTEM_PACKAGE_DATAFILE_HANDLERS 
        if p not in APPLICATION_PACKAGE_DATAFILE_HANDLERS
    ]
)

HANDLER_BY_DATASOURCE_ID = {handler.datasource_id: handler for handler in ALL_DATAFILE_HANDLERS}


class UnknownPackageDatasource(Exception):
    pass


def get_package_handler(package_data):
    """
    Return the DatafileHandler class that corresponds to a ``package_data``
    PackageData object. Raise a UnknownPackageDatasource error if the
    DatafileHandler is not found.
    """
    ppc = HANDLER_BY_DATASOURCE_ID.get(package_data.datasource_id)
    if not ppc:
        raise UnknownPackageDatasource(package_data)
    return ppc

