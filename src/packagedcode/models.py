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
from __future__ import print_function

from collections import OrderedDict
from schematics.models import Model
from schematics.types import StringType
from schematics.types import IntType
from schematics.types.base import BooleanType
from schematics.types.base import URLType
from schematics.types.compound import DictType
from schematics.types.compound import ListType
from schematics.types.compound import ModelType


"""
Common data model for package information and dependencies, abstracting the
many small differences existing between package management formats and tools.

At a high level a package is some piece of code that can be consumed as a unit
and provisioned by some package manager or can be installed as such.

In the simplest case, it can be a single file such as script; more commonly a
package is a complex set of archives, directories structures, file systems
images or self-executable installers.

A package typically contains:
 - some metadata,
 - some payload of code, doc, data.

Package metadata are found in multiple places:
- inside code text  (JavaDoc tags or Python __copyright__ magic)
- inside binaries (such as a Linux Elf or LKM or a Windows PE or an RPM header).
- in dedicated metafiles (such as a Maven POM, NPM package.json and many others)

These metadata provide details on:
 - information on the format version of the current metadata file or header.
 - the package id or name and version.
 - a package namespace such as a central registry ensuing uniqueness of names.
 - some pre-requisite such as a specific OS (Linux), runtime (Java) or
   processor or architecture, some API level (such as an ABI or else),
 - info on the programming language used or needed or technical domain, either
   implicitly or explicitly.
 - documentation such as descriptions, notes, categories, tags,
   classifications or groups of sorts. This can include urls to external
   documentation, either explicitly or implicitly.
 - origin information: author, provider, distributor, vendor, owner, home
   urls, etc.
 - some contact or support information such as emails, mailing lists, forums,
 - some checksum or crypto signature of sorts to verify the integrity of the
   package, often stored outside the package itself,
 - version control info such as a Git or SVN repo where the source came from.
 - license and copyright info, either structured or not, eventually per-file
   or directory.
 - dependent packages, possibly grouped by purpose (dev, build, test, prod)
   The dependencies are either a complete tree or only the first level direct
   dependencies as a flat list. They can point to a name or some remote of local
   files. Dependencies are expressed usually as a package name and a version
   constraint or in some cases as lower level programming language-specific
   dependencies (such as OSGi Java package imports).
 - build and packaging instructions. Several package metadata formats mix
   build/packaging directives or instructions with the package metadata (such
   as RPM spec files).
 - installation directives and installation scripts to actually install the
   payload. These can be implicit such as with RPM directory structures.
 - where to fetch corresponding sources when compiled, either explicitly or
   implicitly, such as a VCS or some other package.
 - modification or patches applied and the patches themselves, with possibly
   changelog docs.
 - pointers to package registries where to fetch this or dependent packages,
   either explicitly or implicitly, including local files, VCS pointers or
   some central registry/repository URL.
 - description of the specific things provided by the payload, such as a
   binary, some API/ABI level, some library, some language namespace or some
   capability of sorts.

The payload of files and directories possibly contains:
  -- documentation,
  -- data files,
  -- code in source or compiled form or both.
"""


class EnhancedModel(Model):
    def __init__(self, deserialize_mapping=None, strict=True, **kwargs):
        Model.__init__(self, raw_data=kwargs, deserialize_mapping=deserialize_mapping, strict=strict)


class Version(EnhancedModel):
    version = StringType()


class AssertedLicense(EnhancedModel):
    """
    As asserted in a package
    """
    license = StringType(default=None)
    text = StringType(default=None)
    notice = StringType(default=None)
    url = StringType(default=None)


class Party(EnhancedModel):
    """
    A party is a person, project or organization
    """
    name = StringType()
    url = StringType()
    email = StringType()
    party_person = 'person'
    # often loosely defined
    party_project = 'project'
    # more formally defined
    party_org = 'organization'

    PARTY_TYPES = (party_person, party_project, party_org,)

    type = StringType(choices=PARTY_TYPES)


class Dependency(EnhancedModel):
    """
    A dependency points to a Package via a package id and version, and jhas a version
    constraint  (such as ">= 3.4"). The version is the effective version that
    has been picked and resolved.
    """
    id = StringType()
    # the effective or concrete resolved and used version
    version = StringType()

    # the potential constraints for this dep.
    # this is package format specific
    version_constraint = StringType()

    # a normalized list of version constraints for this dep.
    # this is package indepdenent
    normalized_version_constraints = ListType(StringType(), default=[])

    # is the dep up to date and the latest available?
    is_latest = BooleanType(default=False)

    def resolve_and_normalize(self):
        """
        Compute the concrete version and normalized_version_constraints
        """
        pass


class Package(EnhancedModel):
    """
    A package base class.
    """
    # descriptive name of the type of package:
    # RubyGem, Python Wheel, Maven Jar, etc.
    # see PACKAGE_TYPES
    type = StringType()

    # types information
    filetypes = tuple()
    mimetypes = tuple()
    extensions = tuple()

    # list of metafiles for a package type
    metafiles = []

    # primary programming language for a package type
    # i.e. RubyGems are primarily ruby, etc
    primary_language = None

    repo_types = []

    as_archive = 'archive'
    as_dir = 'directory'
    as_file = 'file'
    PACKAGINGS = [as_archive, as_dir, as_file]

    # one of PACKAGINGS
    packaging = StringType(choices=PACKAGINGS)

    dep_runtime = 'runtime'
    dep_dev = 'development'
    dep_test = 'test'
    dep_build = 'build'
    dep_optional = 'optional'
    dep_bundled = 'optional'
    dep_ci = 'continuous integration'
    DEPENDENCY_GROUPS = (dep_runtime, dep_dev, dep_optional, dep_test,
                         dep_build, dep_ci, dep_bundled)

    # path to a file or directory
    location = None

    # the id of the package
    id = StringType()
    versioning = ModelType(Version)
    name = StringType(required=True)
    # this is a "short" description.
    summary = StringType()
    # this is a "long" description, often several pages of text.
    description = StringType()

    payload_src = 'source'
    # binaries include minified JavaScripts and similar text but obfuscated formats
    payload_bin = 'binary'
    payload_doc = 'doc'
    PAYLOADS = [payload_src, payload_bin, payload_doc]
    # the type of payload in this package. one of PAYLOADS or none
    payload_type = StringType(choices=PAYLOADS)

    # list of Parties: authors, packager, maintainers, contributors, distributor, vendor, etc
    authors = ListType(ModelType(Party), default=[])
    maintainers = ListType(ModelType(Party), default=[])
    contributors = ListType(ModelType(Party), default=[])
    owners = ListType(ModelType(Party), default=[])
    packagers = ListType(ModelType(Party), default=[])
    distributors = ListType(ModelType(Party), default=[])
    vendors = ListType(ModelType(Party), default=[])

    # keywords or tags
    keywords = ListType(StringType(), default=[])
    # url to a reference documentation for keywords or tags (such as a Pypi or SF.net Trove map)
    keywords_doc_url = URLType()

    # paths to metadata files for this package, if any
    # can be the same as the package location (e.g. RPMs)
    metafile_locations = ListType(StringType(), default=[])

    # URLs to metadata files for this package.
    metafile_urls = ListType(URLType(), default=[])

    homepage_url = URLType()
    notes = StringType()

    # one or more direct download urls, possibly in SPDX vcs url form
    # the first one is considered to be the primary
    download_urls = ListType(URLType(), default=[])

    # checksums for the download
    download_sha1 = StringType()
    download_sha256 = StringType()
    download_md5 = StringType()

    # issue or bug tracker
    bug_tracking_url = URLType()

    # strings (such as email, urls, etc)
    support_contacts = ListType(StringType(), default=[])

    # a URL where the code can be browsed online
    code_view_url = URLType()

    # one of git, svn, hg, etc
    vcs_tool = StringType(choices=['git', 'svn', 'hg'])
    # a URL in the SPDX form of:
    # git+https://github.com/nexb/scancode-toolkit.git
    vcs_repository = StringType()
    # a revision, branch, tag reference, etc (can also be included in the URL
    vcs_revision = StringType()

    # a top level copyright often asserted in metadata
    copyright_top_level = StringType()
    # effective copyrights as detected and eventually summarized
    copyrights = ListType(StringType(), default=[])

    # as asserted licensing information
    # a list of AssertLicense objects
    asserted_licenses = ListType(ModelType(AssertedLicense), default=[])

    # list of legal files locations (such as COPYING, NOTICE, LICENSE, README, etc.)
    legal_file_locations = ListType(StringType(), default=[])

    # resolved or detected license expressions
    license_expression = StringType()
    # a list of license texts
    license_texts = ListType(StringType(), default=[])

    # a list of notices texts
    notice_texts = ListType(StringType(), default=[])

    # map of dependency group to a list of dependencies for each DEPENDENCY_GROUPS
    dependencies = DictType(ListType(ModelType(Dependency)), default={})

    def as_dict(self):
        return OrderedDict(self.to_primitive().items())

    @staticmethod
    def get_package(location):
        """
        takes 'location' of a metafile for a given package and returns the
        corresponding package object.
        """
        return

    # map to a list of related packages keyed by PAYLOAD
    # for instance the SRPM of an RPM
    related_packages = ListType(ModelType(EnhancedModel), default=[])

    @property
    def component_version(self):
        """
        Return the component-level version representation for this package.
        Subclasses can override.
        """
        return self.versioning.version

    def compare_version(self, package, package_version=True):
        """
        Compare self version with another package version using the same
        semantics as the builtin cmp function: return an integer that is
        negative if self.version<package.version, zero if
        self.version==package.version, positive if self.version>package.version.

        Use the component version instead of thepackage version if
        `package_version` is False.

        Subclasses can override for package-type specific comparisons.

        For example:

        >>> q=Package(dict(versioning=Version(dict(version='2'))))
        >>> p=Package(dict(versioning=Version(dict(version='1'))))
        >>> p.compare_version(q)
        -1
        >>> p.compare_version(p)
        0
        >>> r=Package(dict(versioning=Version(dict(version='0'))))
        >>> p.compare_version(r)
        1
        >>> s=Package(dict(versioning=Version(dict(version='1'))))
        >>> p.compare_version(s)
        0
        """
        x = package_version and self.versioning.version or self.component_version
        y = package_version and package.versioning.version or package.component_version
        return cmp(x, y)

    @property
    def qualified_name(self):
        """
        Name prefixed with the package type (creating a namespace for unicity.)
        or None
        """
        return self.name and self.type + ' ' + self.name or None


class Repository(EnhancedModel):
    """
    A package repository.
    """
    repo_type_yum = 'YUM'
    repo_type_debian = 'Debian'
    repo_type_maven = 'Maven'
    repo_type_ivy = 'IVY'
    repo_type_python = 'Pypi'
    repo_type_gems = 'Rubygems'
    repo_type_npm = 'NPM'
    repo_type_cpan = 'CPAN'
    repo_type_nuget = 'Nuget'

    REPO_TYPES = (
        repo_type_yum,
        repo_type_debian,
        repo_type_maven,
        repo_type_ivy,
        repo_type_python,
        repo_type_gems,
        repo_type_npm,
        repo_type_cpan,
        repo_type_nuget,
    )

    # one of REPO_TYPES
    type = StringType(choices=REPO_TYPES)
    url = URLType(default=None)
    public = BooleanType(default=False)
    mirror_urls = ListType(URLType, default=[])
    # optional: used for well known "named" public repos such as:
    # Maven Central, Pypi, RubyGems, npmjs.org
    name = StringType(default=None)

#
# Package Types
#

# NOTE: this is somewhat redundant with extractcode archive handlers
# yet the purpose and semantics are rather different here


class RpmVersion(Version):
    version = StringType()
    release = StringType()
    epoch = IntType()


class RpmPackage(Package):
    versioning = ModelType(RpmVersion)
    type = StringType(default='RPM')
    metafiles = ('*.spec',)
    extensions = ('.rpm', '.srpm', '.mvl', '.vip',)
    filetypes = ('rpm ',)
    mimetypes = ('application/x-rpm',)
    packaging = StringType(default=Package.as_archive)
    repo_types = (Repository.repo_type_yum,)


class DebianVersion(Version):
    version = StringType()


class DebianPackage(Package):
    versioning = ModelType(DebianVersion)
    type = StringType(default='Debian package')
    metafiles = ('*.control',)
    extensions = ('.deb',)
    filetypes = ('debian binary package',)
    mimetypes = ('application/x-archive',
                 'application/vnd.debian.binary-package',)
    packaging = StringType(default=Package.as_archive)
    repo_types = (Repository.repo_type_debian,)


class JarVersion(Version):
    version = StringType()


class JarPackage(Package):
    versioning = ModelType(JarVersion)
    type = StringType(default='Java Jar')
    metafiles = ('META-INF/MANIFEST.MF',)
    extensions = ('.jar',)
    filetypes = ('java archive ', 'zip archive',)
    mimetypes = ('application/java-archive', 'application/zip',)
    primary_language = StringType(default='Java')
    packaging = StringType(default=Package.as_archive)
    repo_types = (Repository.repo_type_maven, Repository.repo_type_ivy,)


class JarAppVersion(Version):
    versioning = StringType()


class JarAppPackage(Package):
    versioning = ModelType(JarAppVersion)
    type = StringType(default='Java application')
    metafiles = ('WEB-INF/',)
    extensions = ('.war', '.sar', '.ear',)
    filetypes = ('java archive ', 'zip archive',)
    mimetypes = ('application/java-archive', 'application/zip')
    primary_language = StringType(default='Java')
    packaging = StringType(default=Package.as_archive)
    repo_types = (Repository.repo_type_maven, Repository.repo_type_ivy,)


class MavenVersion(Version):
    versioning = StringType()


class MavenPackage(JarPackage, JarAppPackage):
    versioning = ModelType(MavenVersion)
    type = StringType(default='Maven')
    metafiles = ('META-INF/**/*.pom', 'pom.xml',)
    repo_types = (Repository.repo_type_maven,)


class BowerVersion(Version):
    version = StringType()


class BowerPackage(Package):
    versioning = ModelType(BowerVersion)
    type = StringType(default='Bower')
    metafiles = ('bower.json',)
    primary_language = 'JavaScript'
    repo_types = ()


class MeteorVersion(Version):
    version = StringType()


class MeteorPackage(Package):
    versioning = ModelType(MeteorVersion)
    type = StringType(default='Meteor')
    metafiles = ('package.js',)
    primary_language = 'JavaScript'
    repo_types = ()


class CpanVersion(Version):
    version = StringType()


class CpanModule(Package):
    versioning = ModelType(CpanVersion)
    type = StringType(default='CPAN')
    metafiles = ('*.pod',
                 'MANIFEST',
                 'META.yml',)
    primary_language = 'Perl'
    repo_types = (Repository.repo_type_cpan,)


class RubyGemVersion(Version):
    version = StringType()


class RubyGemPackage(Package):
    versioning = ModelType(RubyGemVersion)
    type = StringType(default='RubyGem')
    metafiles = ('*.control',
                 '*.gemspec',
                 'Gemfile',
                 'Gemfile.lock',
                 )
    filetypes = ('.tar', 'tar archive',)
    mimetypes = ('application/x-tar',)
    extensions = ('.gem',)
    primary_language = 'Ruby'
    packaging = StringType(default=Package.as_archive)
    repo_types = (Repository.repo_type_gems,)


class AndroidAppVersion(Version):
    version = StringType()


class AndroidAppPackage(Package):
    versioning = ModelType(AndroidAppVersion)
    type = StringType(default='Android app')
    filetypes = ('zip archive',)
    mimetypes = ('application/zip',)
    extensions = ('.apk',)
    primary_language = StringType(default='Java')
    packaging = StringType(default=Package.as_archive)
    repo_types = ()


class AndroidLibVersion(Version):
    version = StringType()


# see http://tools.android.com/tech-docs/new-build-system/aar-formats
class AndroidLibPackage(Package):
    versioning = ModelType(AndroidLibVersion)
    type = StringType(default='Android library')
    filetypes = ('zip archive',)
    mimetypes = ('application/zip',)
    # note: Apache Axis also uses AAR extensions for plain Jars.
    # this can be decided based on internal structure
    extensions = ('.aar',)
    primary_language = StringType(default='Java')
    packaging = StringType(default=Package.as_archive)
    repo_types = ()


class MozillaExtVersion(Version):
    version = StringType()


class MozillaExtPackage(Package):
    versioning = ModelType(MozillaExtVersion)
    type = StringType(default='Mozilla extension')
    filetypes = ('zip archive',)
    mimetypes = ('application/zip',)
    extensions = ('.xpi',)
    primary_language = StringType(default='JavaScript')
    packaging = StringType(default=Package.as_archive)
    repo_types = ()


class ChromeExtVersion(Version):
    Version = StringType()


class ChromeExtPackage(Package):
    versioning = ModelType(ChromeExtVersion)
    type = StringType(default='Chrome extension')
    filetypes = ('data',)
    mimetypes = ('application/octet-stream',)
    extensions = ('.crx',)
    primary_language = StringType(default='JavaScript')
    packaging = StringType(default=Package.as_archive)
    repo_types = ()


class IosAppVersion(Version):
    version = StringType()


class IosAppPackage(Package):
    versioning = ModelType(IosAppVersion)
    type = StringType(default='iOS app')
    filetypes = ('zip archive',)
    mimetypes = ('application/zip',)
    extensions = ('.ipa',)
    primary_language = StringType(default='Objective-C')
    packaging = StringType(default=Package.as_archive)
    repo_types = ()


class PythonVersion(Version):
    version = StringType()


class PythonPackage(Package):
    versioning = ModelType(PythonVersion)
    type = StringType(default='Python package')
    filetypes = ('zip archive',)
    mimetypes = ('application/zip',)
    extensions = ('.egg', '.whl', '.pyz', '.pex',)
    primary_language = StringType(default='Python')
    packaging = StringType(default=Package.as_archive)
    repo_types = (Repository.repo_type_python,)


class CabVersion(Version):
    version = StringType()


class CabPackage(Package):
    versioning = ModelType(CabVersion)
    type = StringType(default='Microsoft cab')
    filetypes = ('microsoft cabinet',)
    mimetypes = ('application/vnd.ms-cab-compressed',)
    extensions = ('.cab',)
    packaging = StringType(default=Package.as_archive)
    repo_types = ()


class MsiInstallerVersion(Version):
    version = StringType()


class MsiInstallerPackage(Package):
    versioning = ModelType(MsiInstallerVersion)
    type = StringType(default='Microsoft MSI Installer')
    filetypes = ('msi installer',)
    mimetypes = ('application/x-msi',)
    extensions = ('.msi',)
    packaging = StringType(default=Package.as_archive)
    repo_types = ()


class InstallShieldVersion(Version):
    version = StringType()


# notes: this catches all  exe and fails often
class InstallShieldPackage(Package):
    versioning = ModelType(InstallShieldVersion)
    type = StringType(default='InstallShield Installer')
    filetypes = ('installshield',)
    mimetypes = ('application/x-dosexec',)
    extensions = ('.exe',)
    packaging = StringType(default=Package.as_archive)
    repo_types = ()


class NugetVersion(Version):
    version = StringType()


class NugetPackage(Package):
    versioning = ModelType(NugetVersion)
    type = StringType(default='Nuget')
    metafiles = ('[Content_Types].xml', '*.nuspec',)
    filetypes = ('zip archive', 'microsoft ooxml',)
    mimetypes = ('application/zip', 'application/octet-stream',)
    extensions = ('.nupkg',)
    packaging = StringType(default=Package.as_archive)
    repo_types = (Repository.repo_type_nuget)


class NSISInstallerVersion(Version):
    version = StringType()


class NSISInstallerPackage(Package):
    versioning = ModelType(NSISInstallerVersion)
    type = StringType(default='Nullsoft Installer')
    filetypes = ('nullsoft installer',)
    mimetypes = ('application/x-dosexec',)
    extensions = ('.exe',)
    packaging = StringType(default=Package.as_archive)
    repo_types = ()


class SharVersion(Version):
    version = StringType()


class SharPackage(Package):
    versioning = ModelType(SharVersion)
    type = StringType(default='shar shell archive')
    filetypes = ('posix shell script',)
    mimetypes = ('text/x-shellscript',)
    extensions = ('.sha', '.shar', '.bin',)
    packaging = StringType(default=Package.as_archive)
    repo_types = ()


class AppleDmgVersion(Version):
    version = StringType()


class AppleDmgPackage(Package):
    versioning = ModelType(AppleDmgVersion)
    type = StringType(default='Apple dmg')
    filetypes = ('zlib compressed',)
    mimetypes = ('application/zlib',)
    extensions = ('.dmg', '.sparseimage',)
    packaging = StringType(default=Package.as_archive)
    repo_types = ()


class IsoImageVersion(Version):
    version = StringType()


class IsoImagePackage(Package):
    versioning = ModelType(IsoImageVersion)
    type = StringType(default='ISO CD image')
    filetypes = ('iso 9660 cd-rom', 'high sierra cd-rom',)
    mimetypes = ('application/x-iso9660-image',)
    extensions = ('.iso', '.udf', '.img',)
    packaging = StringType(default=Package.as_archive)
    repo_types = ()


class SquashfsVersion(Version):
    version = StringType()


class SquashfsPackage(Package):
    versioning = ModelType(SquashfsVersion)
    type = StringType(default='squashfs FS')
    filetypes = ('squashfs',)
    mimetypes = tuple()
    packaging = StringType(default=Package.as_archive)
    repo_types = ()


#
# these very generic archives must come last
#


class RarVersion(Version):
    version = StringType()


class RarPackage(Package):
    versioning = ModelType(RarVersion)
    type = StringType(default='RAR archive')
    filetypes = ('rar archive',)
    mimetypes = ('application/x-rar',)
    extensions = ('.rar',)
    packaging = StringType(default=Package.as_archive)
    repo_types = ()


class TarVersion(Version):
    version = StringType()


class TarPackage(Package):
    versioning = ModelType(TarVersion)
    type = StringType(default='plain tarball')
    filetypes = (
        '.tar', 'tar archive',
        'xz compressed', 'lzma compressed',
        'gzip compressed',
        'bzip2 compressed',
        '7-zip archive',
        "compress'd data",
    )
    mimetypes = (
        'application/x-xz',
        'application/x-tar',
        'application/x-lzma',
        'application/x-gzip',
        'application/x-bzip2',
        'application/x-7z-compressed',
        'application/x-compress',
    )
    extensions = (
        '.tar', '.tar.xz', '.txz', '.tarxz',
        'tar.lzma', '.tlz', '.tarlz', '.tarlzma',
        '.tgz', '.tar.gz', '.tar.gzip', '.targz', '.targzip', '.tgzip',
        '.tar.bz2', '.tar.bz', '.tar.bzip', '.tar.bzip2', '.tbz',
        '.tbz2', '.tb2', '.tarbz2',
        '.tar.7z', '.tar.7zip', '.t7z',
        '.tz', '.tar.z', '.tarz',
    )
    packaging = StringType(default=Package.as_archive)


class ZipVersion(Version):
    version = StringType()


class ZipPackage(Package):
    versioning = ModelType(ZipVersion)
    type = StringType(default='plain zip')
    filetypes = ('zip archive', '7-zip archive',)
    mimetypes = ('application/zip', 'application/x-7z-compressed',)
    extensions = ('.zip', '.zipx', '.7z',)
    packaging = StringType(default=Package.as_archive)


# TODO: Add VM images formats(VMDK, OVA, OVF, VDI, etc) and Docker/other containers
