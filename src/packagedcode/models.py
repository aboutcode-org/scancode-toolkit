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

from collections import OrderedDict


"""
Common data model for packages information and dependencies, abstracting the
many small differences existing between package management formats and tools.

At a high level a package is some piece of code that can be consumed as a unit
and provisioned by some package manager or can be installed as such.

In the simplest case, it can be a single file such as script; more commonly a
package is a complex set of archives, directories structures, file systems
images or self-executable installers.

A package typically contains:
 - some metadata,
 - some payload of code, doc, data.

Packages metadata are found in multiple places:
- inside code text  (JavaDoc tags or Python __copyright__ magic)
- inside binaries (such as a Linux Elf or LKM or a Windows PE or an RPM header).
- in dedicated metafiles (such as a Maven POMs, NPM package.json and many others)

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


class Package(object):
    """
    A package base class.
    """
    # descriptive name of the type of package:
    # RubyGem, Python Wheel, Maven Jar, etc.
    # see PACKAGE_TYPES
    type = None

    # types information
    filetypes = tuple()
    mimetypes = tuple()
    extensions = tuple()

    # list of metafiles for a package type
    metafiles = []

    # primary programming language for a package type
    # i.e. RubyGems are primarily ruby, etc
    primary_language = None

    # one of PACKAGINGS
    packaging = None

    as_archive = 'archive'
    as_dir = 'directory'
    as_file = 'file'
    PACKAGINGS = (as_archive, as_dir, as_file)

    dep_runtime = 'runtime'
    dep_dev = 'development'
    dep_test = 'test'
    dep_build = 'build'
    dep_optional = 'optional'
    dep_ci = 'continuous integration'

    DEPENDENCY_GROUPS = (dep_runtime, dep_dev, dep_optional, dep_test, dep_build, dep_ci)

    def __init__(self, location=None):
        # path to a file or directory
        self.location = location

        # path to where a package archive has been extracted
        self.extracted_to = None

        # the id of the package
        self.id = ''
        self.version = ''
        self.name = ''
        self.summary = ''
        self.description = ''

        # paths to metadata files for this package.
        # can be the same as the package location (e.g. RPMs)
        self.metafile_locations = []

        self.homepage_url = ''
        self.notes = ''

        # list of Party: authors, packager, distributor, vendor, etc
        self.parties = []

        self.copyright = ''

        # as asserted licensing information
        self.asserted_licensing = ''

        # list of legal files locations (such as COPYING, etc)
        self.legal_file_locations = []

        # resolved or detected license expressions
        self.license_expression = ''
        self.license_text = ''
        self.notice_text = ''

        # map of dependency group to a list of dependencies for each
        # DEPENDENCY_GROUPS
        self.dependencies = OrderedDict()

    def as_dict(self, simple=True):
        """
        Return an Ordered dictionary of package data, composed only of simple
        types: OrderedDict, lists and unicode strings.
        """
        if simple:
            package = OrderedDict()
            package['type'] = self.type
            package['packaging'] = self.packaging
            package['primary_language'] = self.primary_language
            # package['extracted_to'] = self.extracted_to
            return package
        else:
            raise NotImplementedError()


class Party(object):
    """
    A party is a person, project or organization
    """
    party_person = 'person'
    # often loosely defined
    party_project = 'project'
    # more formally defined
    party_org = 'organization'

    PARTY_TYPES = (party_person, party_project, party_org,)

    def __init__(self, name, type=None, emails=None, urls=None,  # @ReservedAssignment
                 city=None, country=None, notes=None):
        self.name = name
        # one of PARTY_TYPES
        self.type = type
        self.emails = emails or []
        self.urls = urls or []
        self.city = city
        self.country = country
        self.notes = notes

    def as_dict(self):
        party = OrderedDict()
        party['name'] = self.name
        party['type'] = self.type
        party['email'] = self.email
        party['urls'] = self.urls
        party['country'] = self.country
        party['notes'] = self.notes
        return party


class Dependency(object):
    """
    A dependency points to a Package via a package id and a list of version
    constraints (such as ">= 3.4"). The version is the effective  version that
    has been picked and resolved.
    """
    def __init__(self, id, version_constraints=None, version=None):  # @ReservedAssignment
        self.id = id
        # the effective or concrete version
        self.version = version
        self.version_constraints = version_constraints or []

    def as_dict(self):
        dep = OrderedDict()
        dep['id'] = self.package_id
        dep['version'] = self.urls
        dep['version_constraints'] = self.version_constraints
        return dep

    def resolve(self):
        pass


class Repository(object):
    """
    A package repository.
    """
    repo_type_yum = 'YUM'
    repo_type_debian = 'Debian'
    repo_type_maven = 'Maven'
    repo_type_ivy = 'IVY'
    repo_type_artifactory = 'Artifactory'
    repo_type_python = 'Pypi'
    repo_type_gems = 'Rubygems'
    repo_type_npm = 'NPM'

    REPO_TYPES = (
        repo_type_yum,
        repo_type_debian,
        repo_type_maven,
        repo_type_ivy,
        repo_type_artifactory,
        repo_type_python,
        repo_type_gems,
        repo_type_npm,
    )

    def __init__(self, type, url, public=False, mirror_urls=None, name=None):  # @ReservedAssignment
        # one of REPO_TYPES
        self.type = type
        self.url = url
        self.public = public
        self.mirror_urls = mirror_urls or []
        # optional: used for well known "named" public repos such as:
        # Maven Central, Pypi, RubyGems, npm.org
        self.name = name


#
# Package Types
#

# NOTE: this is somewhat redundant with extractcode archive handlers
# yet the purpose and semantics are rather different here

class RpmPackage(Package):
    type = 'RPM'
    metafiles = ('*.spec',)
    extensions = ('.rpm', '.srpm', '.mvl', '.vip',)
    filetypes = ('rpm ',)
    mimetypes = ('application/x-rpm',)
    packaging = Package.as_archive


class DebianPackage(Package):
    type = 'Debian package'
    metafiles = ('*.control',)
    extensions = ('.deb',)
    filetypes = ('debian binary package',)
    mimetypes = ('application/x-archive',
                 'application/vnd.debian.binary-package',)
    packaging = Package.as_archive


class JarPackage(Package):
    type = 'Java Jar'
    metafiles = ['META-INF/MANIFEST.MF']
    extensions = ('.jar',)
    filetypes = ('java archive ', 'zip archive',)
    mimetypes = ('application/java-archive', 'application/zip',)
    primary_language = 'Java'
    packaging = Package.as_archive


class JarAppPackage(Package):
    type = 'Java application'
    metafiles = ['WEB-INF/']
    extensions = ('.war', '.sar', '.ear',)
    filetypes = ('java archive ', 'zip archive',)
    mimetypes = ('application/java-archive', 'application/zip')
    primary_language = 'Java'
    packaging = Package.as_archive


class MavenPackage(JarPackage, JarAppPackage):
    type = 'Maven'
    metafiles = ['META-INF/**/*.pom', 'pom.xml']


class NpmPackage(Package):
    type = 'NPM'
    metafiles = ['package.json']
    primary_language = 'JavaScript'


class BowerPackage(Package):
    type = 'Bower'
    metafiles = ['bower.json']
    primary_language = 'JavaScript'


class MeteorPackage(Package):
    type = 'Meteor'
    metafiles = ['package.js']
    primary_language = 'JavaScript'


class CpanModule(Package):
    type = 'CPAN'
    metafiles = ['*.pod',
                 'MANIFEST',
                 'META.yml']
    primary_language = 'Perl'


class RubyGemPackage(Package):
    type = 'RubyGem'
    filetypes = ('.tar', 'tar archive',)
    mimetypes = ('application/x-tar',)
    extensions = ('.gem',)
    primary_language = 'Ruby'
    packaging = Package.as_archive


class AndroidAppPackage(Package):
    type = 'Android app'
    filetypes = ('zip archive',)
    mimetypes = ('application/zip',)
    extensions = ('.apk',)
    primary_language = 'Java'
    packaging = Package.as_archive


    # see http://tools.android.com/tech-docs/new-build-system/aar-formats
class AndroidLibPackage(Package):
    type = 'Android library'
    filetypes = ('zip archive',)
    mimetypes = ('application/zip',)
    # note: Apache Axis also uses AAR extensions for plain Jars.
    # this can be decided based on internal structure
    extensions = ('.aar',)
    primary_language = 'Java'
    packaging = Package.as_archive


class MozillaExtPackage(Package):
    type = 'Mozilla extension'
    filetypes = ('zip archive',)
    mimetypes = ('application/zip',)
    extensions = ('.xpi',)
    primary_language = 'JavaScript'
    packaging = Package.as_archive


class ChromeExtPackage(Package):
    type = 'Chrome extension'
    filetypes = ('data',)
    mimetypes = ('application/octet-stream',)
    extensions = ('.crx',)
    primary_language = 'JavaScript'
    packaging = Package.as_archive


class IosAppPackage(Package):
    type = 'iOS app'
    filetypes = ('zip archive',)
    mimetypes = ('application/zip',)
    extensions = ('.ipa',)
    primary_language = 'Objective-C'
    packaging = Package.as_archive


class PythonPackage(Package):
    type = 'Python package'
    filetypes = ('zip archive',)
    mimetypes = ('application/zip',)
    extensions = ('.egg', '.whl', '.pyz', '.pex',)
    primary_language = 'Python'
    packaging = Package.as_archive


class CabPackage(Package):
    type = 'Microsoft cab'
    filetypes = ('microsoft cabinet',)
    mimetypes = ('application/vnd.ms-cab-compressed',)
    extensions = ('.cab',)
    packaging = Package.as_archive


class MsiInstallerPackage(Package):
    type = 'Microsoft MSI Installer'
    filetypes = ('msi installer',)
    mimetypes = ('application/x-msi',)
    extensions = ('.msi',)
    packaging = Package.as_archive


# notes: this catches all  exe and fails often
class InstallShieldPackage(Package):
    type = 'InstallShield Installer'
    filetypes = ('installshield',)
    mimetypes = ('application/x-dosexec',)
    extensions = ('.exe',)
    packaging = Package.as_archive


class NugetPackage(Package):
    type = 'Nuget'
    metafiles = ['[Content_Types].xml', '*.nuspec']
    filetypes = ('zip archive', 'microsoft ooxml')
    mimetypes = ('application/zip', 'application/octet-stream')
    extensions = ('.nupkg',)
    packaging = Package.as_archive


class NSISInstallerPackage(Package):
    type = 'Nullsoft Installer'
    filetypes = ('nullsoft installer',)
    mimetypes = ('application/x-dosexec',)
    extensions = ('.exe',)
    packaging = Package.as_archive


class SharPackage(Package):
    type = 'shar shell archive'
    filetypes = ('posix shell script',)
    mimetypes = ('text/x-shellscript',)
    extensions = ('.sha', '.shar', '.bin')
    packaging = Package.as_archive


class AppleDmgPackage(Package):
    type = 'Apple dmg'
    filetypes = ('zlib compressed',)
    mimetypes = ('application/zlib',)
    extensions = ('.dmg', '.sparseimage',)
    packaging = Package.as_archive


class IsoImagePackage(Package):
    type = 'ISO CD image'
    filetypes = ('iso 9660 cd-rom', 'high sierra cd-rom')
    mimetypes = ('application/x-iso9660-image',)
    extensions = ('.iso', '.udf', '.img')
    packaging = Package.as_archive


class SquashfsPackage(Package):
    type = 'squashfs FS'
    filetypes = ('squashfs',)
    packaging = Package.as_archive

#
# these very generic archives must come last
#

class RarPackage(Package):
    type = 'RAR archive'
    filetypes = ('rar archive',)
    mimetypes = ('application/x-rar',)
    extensions = ('.rar',)
    packaging = Package.as_archive


class TarPackage(Package):
    type = 'plain tarball'
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
    packaging = Package.as_archive


class ZipPackage(Package):
    type = 'plain zip'
    filetypes = ('zip archive', '7-zip archive',)
    mimetypes = ('application/zip', 'application/x-7z-compressed',)
    extensions = ('.zip', '.zipx', '.7z',)
    packaging = Package.as_archive


# TODO: Add VM images formats(VMDK, OVA, OVF, VDI, etc) and Docker/other containers


# Note: the order matters: from the most to the least specific
PACKAGE_TYPES = [
    RpmPackage,
    DebianPackage,
    JarPackage,
    JarAppPackage,
    # TODO: add support for these
    # MavenPackage
    NpmPackage,
    BowerPackage,
    MeteorPackage,
    CpanModule,
    RubyGemPackage,
    AndroidAppPackage,
    AndroidLibPackage,
    MozillaExtPackage,
    ChromeExtPackage,
    IosAppPackage,
    PythonPackage,
    RarPackage,
    CabPackage,
    MsiInstallerPackage,
    InstallShieldPackage,
    NSISInstallerPackage,
    NugetPackage,
    SharPackage,
    AppleDmgPackage,
    IsoImagePackage,
    SquashfsPackage,
    # these should always come last
    TarPackage,
    ZipPackage,
    ]
