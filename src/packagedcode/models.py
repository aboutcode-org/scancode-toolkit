#
# Copyright (c) 2017 nexB Inc. and others. All rights reserved.
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
from __future__ import unicode_literals

import logging
import sys

from schematics.models import Model
from schematics.transforms import blacklist
from schematics.types import DateTimeType
from schematics.types import LongType
from schematics.types import StringType
from schematics.types.compound import DictType
from schematics.types.compound import ListType
from schematics.types.compound import ModelType


"""
Data models for package information and dependencies, abstracting the
differences existing between package formats and tools.

A package is  code that can be consumed and provisioned by a package
manager or can be installed.

It can be a single file such as script; more commonly a package is
stored in an archive or directory.

A package contains:
 - information/metadata,
 - a payload of code, doc, data.

Package metadata are found in multiple places:
- in manifest (such as a Maven POM, NPM package.json and many others)
- in binaries (such as an Elf or LKM, Windows PE or RPM header).
- in code (JavaDoc tags or Python __copyright__ magic)

These metadata provide details such as:
 - package identifier (e.g. name and version).
 - package registry
 - download URLs or information
 - pre-requisite such as OS, runtime, architecture, API/ABI, etc.
 - informative description, keywords, URLs, etc.
 - author, provider, distributor, vendor, etc. collectively ass "parties"
 - contact and support information (emails, mailing lists, ...)
 - checksum or signature to verify integrity
 - version control references (Git, SVN repo)
 - license and copyright
 - dependencies on other packages
 - build/packaging instructions
 - installation directives/scripts
 - corresponding sources download pointers
 - modification or patches applied,changelog docs.
"""


TRACE = False

def logger_debug(*args):
    pass

logger = logging.getLogger(__name__)

if TRACE:
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, basestring) and a or repr(a) for a in args))


class BaseListType(ListType):
    """
    ListType with a default of an empty list.
    """
    def __init__(self, field, **kwargs):
        super(BaseListType, self).__init__(field=field, default=[], **kwargs)


class BaseModel(Model):
    """
    Base class for all schematics models.
    """
    def __init__(self, **kwargs):
        super(BaseModel, self).__init__(raw_data=kwargs)

    def to_dict(self, **kwargs):
        """
        Return a dict of primitive Python types for this model instance.
        This is an OrderedDict because each model has a 'field_order' option.
        """
        return self.to_primitive(**kwargs)

party_person = 'person'
# often loosely defined
party_project = 'project'
# more formally defined
party_org = 'organization'
PARTY_TYPES = (party_person, party_project, party_org,)

class Party(BaseModel):
    metadata = dict(
        label='party',
        description='A party is a person, project or organization related to a package.')

    type = StringType(choices=PARTY_TYPES)
    type.metadata = dict(
        label='party type',
        description='the type of this party: One of: ' + ', '.join(PARTY_TYPES))

    name = StringType()
    name.metadata = dict(
        label='name',
        description='Name of this party.')

    role = StringType()
    role.metadata = dict(
        label='party role',
        description='A role for this party. Something such as author, '
        'maintainer, contributor, owner, packager, distributor, '
        'vendor, developer, owner, etc.')

    url = StringType()
    url.metadata = dict(
        label='url',
        description='URL to a primary web page for this party.')

    email = StringType()
    email.metadata = dict(
        label='email',
        description='Email for this party.')

    class Options:
        fields_order = 'type', 'role', 'name', 'email', 'url'


class BasePackage(BaseModel):
    metadata = dict(
        label='base package',
        description='A base identifiable package object.')

    # class-level attributes used to recognize a package
    filetypes = tuple()
    mimetypes = tuple()
    extensions = tuple()
    # list of known metafiles for a package type
    metafiles = []

    type = StringType()
    type.metadata = dict(
        label='package type',
        description='A short code to identify what is the type of this package.'
        'For instance gem for a Rubygem, docker for container, '
        'pypi for Python Wheel or Egg, '
        'maven for a Maven Jar, '
        'deb for a Debian package, etc.')

    name = StringType(required=True)
    name.metadata = dict(
        label='package name',
        description='Name of the package.')

    version = StringType()
    version.metadata = dict(
        label='package version',
        description='Version of the package as a string.')

    class Options:
        # this defines the important serialization order
        fields_order = [
            'type',
            'name',
            'version',
        ]


# Groupings/pupose/scope for package dependencies
dep_runtime = 'runtime'
dep_dev = 'development'
dep_test = 'test'
dep_build = 'build'
dep_optional = 'optional'
dep_bundled = 'bundled'
dep_ci = 'continuous integration'
DEPENDENCY_GROUPS = (
    dep_runtime,
    dep_dev,
    dep_optional,
    dep_test,
    dep_build,
    dep_ci,
    dep_bundled,
)


code_type_src = 'source'
code_type_bin = 'binary'
code_type_doc = 'documentation'
code_type_data = 'data'
CODE_TYPES = (
    code_type_src,
    code_type_bin,
    code_type_doc,
    code_type_data,
)


class Package(BasePackage):
    metadata = dict(
        label='package',
        description='A package object.')

    description = StringType()
    description.metadata = dict(
        label='Description',
        description='Description for this package. '
        'By convention the first should be a summary when available.')

    release_date = DateTimeType()
    release_date.metadata = dict(
        label='release date',
        description='Release date of the package')

    primary_language = StringType()
    primary_language.metadata = dict(label='Primary programming language')

    code_type = StringType(choices=CODE_TYPES)
    code_type.metadata = dict(
        label='code type',
        description='Primary type of code in this Package such as source, binary, data, documentation.'
    )

    # FIXME: this would be simpler as a list where each Party has also a type
    parties = BaseListType(ModelType(Party))
    parties.metadata = dict(
        label='parties',
        description='A list of parties such as a person, project or organization.'
    )


    keywords = BaseListType(StringType())
    keywords.metadata = dict(
        label='keywords',
        description='A list of keywords or tags.')

    size = LongType()
    size.metadata = dict(
        label='download size',
        description='size of the package download in bytes')

    download_url = StringType()
    download_url.metadata = dict(
        label='Download URL',
        description='A direct download URLs, possibly in SPDX VCS url form.')

    download_checksums = BaseListType(StringType())
    download_checksums.metadata = dict(
        label='download checksums',
        description='A list of checksums for this download in '
        'hexadecimal and prefixed with the checksum algorithm and a colon '
        '(e.g. sha1:asahgsags')

    # TODO: add package_homepage_url such as a Pypi page or an npmjs page
    homepage_url = StringType()
    homepage_url.metadata = dict(
        label='homepage URL',
        description='URL to the homepage for this package')

    # FIXME: use a simpler, compact VCS URL instead???
    VCS_CHOICES = ['git', 'svn', 'hg', 'bzr', 'cvs']
    vcs_tool = StringType(choices=VCS_CHOICES)
    vcs_tool.metadata = dict(
        label='Version control system tool',
        description='The type of VCS tool for this package. One of: ' + ', '.join(VCS_CHOICES))

    vcs_repository = StringType()
    vcs_repository.metadata = dict(
        label='VCS Repository URL',
        description='a URL to the VCS repository in the SPDX form of:'
        'git+https://github.com/nexb/scancode-toolkit.git')

    vcs_revision = StringType()
    vcs_revision.metadata = dict(
        label='VCS revision',
        description='a revision, commit, branch or tag reference, etc. '
        '(can also be included in the URL)')

    code_view_url = StringType()
    code_view_url.metadata = dict(
        label='code view URL',
        description='a URL where the code can be browsed online')

    bug_tracking_url = StringType()
    bug_tracking_url.metadata = dict(
        label='bug tracking URL',
        description='URL to the issue or bug tracker for this package')

    copyright = StringType()
    copyright.metadata = dict(
        label='Copyright',
        description='Copyright statements for this package. Typically one per line.')

    asserted_license = StringType()
    asserted_license.metadata = dict(
        label='asserted license',
        description='The license as asserted by this package as a text.')

    license_expression = StringType()
    license_expression.metadata = dict(
        label='license expression',
        description='license expression: either resolved or detected license expression')

    notice_text = StringType()
    notice_text.metadata = dict(
        label='notice text',
        description='A notice text for this package.')

    # Map a DEPENDENCY_GROUPS group name to a list of Dependency
    # FIXME: we should instead just have a plain list where each dep contain a group.
    dependencies = DictType(ListType(ModelType(BasePackage)), default={})
    dependencies.metadata = dict(
        label='dependencies',
        description='A mapping of a dependency group to a '
        'list of dependent packages for this package. '
        'One of:' + ', '.join(DEPENDENCY_GROUPS)
        )

    related_packages = BaseListType(ModelType(BasePackage))
    related_packages.metadata = dict(
        label='related packages',
        description='A list of related Packages objects for this package. '
        'For instance the SRPM source of a binary RPM.')

    class Options:
        # this defines the important serialization order
        fields_order = [
            'type',
            'name',
            'version',
            'primary_language',
            'code_type',
            'description',
            'size',
            'release_date',
            'parties',
            'keywords',
            'homepage_url',
            'download_url',
            'download_checksums',
            'bug_tracking_url',
            'code_view_url',
            'vcs_tool',
            'vcs_repository',
            'vcs_revision',
            'copyright',
            'asserted_license',
            'license_expression',
            'notice_text',
            'dependencies',
            'related_packages'
        ]

        # we use for now a "role" that excludes deps and relationships from the
        # serialization
        roles = {'no_deps': blacklist('dependencies', 'related_packages')}

    def __init__(self, location=None, **kwargs):
        """
        Initialize a new Package.
        Subclass can override but should override the recognize method to populate a package accordingly.
        """
        # path to a file or directory where this Package is found in a scan
        self.location = location
        super(Package, self).__init__(**kwargs)

    @classmethod
    def recognize(cls, location):
        """
        Return a Package object or None given a location to a file or directory
        pointing to a package archive, metafile or similar.

        Sub-classes should override to implement their own package recognition.
        """
        return cls()

    @property
    def component_version(self):
        """
        Return the component-level version representation for this package.
        Subclasses can override.
        """
        return self.version

    def compare_version(self, other, component_level=False):
        """
        Compare the version of this package with another package version.

        Use the same semantics as the builtin cmp function. It returns:
        - a negaitive integer if this version < other version,
        - zero if this version== other.version
        - a positive interger if this version > other version.

        Use the component-level version if `component_level` is True.

        Subclasses can override for package-type specific comparisons.

        For example:
        # >>> q=Package(version='2')
        # >>> p=Package(version='1')
        # >>> p.compare_version(q)
        # -1
        # >>> p.compare_version(p)
        # 0
        # >>> r=Package(version='0')
        # >>> p.compare_version(r)
        # 1
        # >>> s=Package(version='1')
        # >>> p.compare_version(s)
        # 0
        """
        x = component_level and self.component_version() or self.version
        y = component_level and other.component_version() or self.version
        return cmp(x, y)

    def sort_key(self):
        """
        Return some data suiatble to use as a key function when sorting.
        """
        return (self.type, self.name, self.version.sortable(self.version),)

#
# Package types
# NOTE: this is somewhat redundant with extractcode archive handlers
# yet the purpose and semantics are rather different here


class DebianPackage(Package):
    metafiles = ('*.control',)
    extensions = ('.deb',)
    filetypes = ('debian binary package',)
    mimetypes = ('application/x-archive', 'application/vnd.debian.binary-package',)
    type = StringType(default='deb')


# class AlpinePackage(Package):
#     metafiles = ('*.control',)
#     extensions = ('.apk',)
#     filetypes = ('debian binary package',)
#     mimetypes = ('application/x-archive', 'application/vnd.debian.binary-package',)
#     type = StringType(default='apk')


class JavaJar(Package):
    metafiles = ('META-INF/MANIFEST.MF',)
    extensions = ('.jar',)
    filetypes = ('java archive ', 'zip archive',)
    mimetypes = ('application/java-archive', 'application/zip',)
    type = StringType(default='jar')
    primary_language = StringType(default='Java')


class JavaWar(Package):
    metafiles = ('WEB-INF/web.xml',)
    extensions = ('.war',)
    filetypes = ('java archive ', 'zip archive',)
    mimetypes = ('application/java-archive', 'application/zip')
    type = StringType(default='war')
    primary_language = StringType(default='Java')


class JavaEar(Package):
    metafiles = ('META-INF/application.xml', 'META-INF/ejb-jar.xml')
    extensions = ('.ear',)
    filetypes = ('java archive ', 'zip archive',)
    mimetypes = ('application/java-archive', 'application/zip')
    type = StringType(default='ear')
    primary_language = StringType(default='Java')


class Axis2Mar(Package):
    """Apache Axis2 module"""
    metafiles = ('META-INF/module.xml',)
    extensions = ('.mar',)
    filetypes = ('java archive ', 'zip archive',)
    mimetypes = ('application/java-archive', 'application/zip')
    type = StringType(default='axis2')
    primary_language = StringType(default='Java')


class JBossSar(Package):
    metafiles = ('META-INF/jboss-service.xml',)
    extensions = ('.sar',)
    filetypes = ('java archive ', 'zip archive',)
    mimetypes = ('application/java-archive', 'application/zip')
    type = StringType(default='jboss')
    primary_language = StringType(default='Java')


class IvyJar(JavaJar):
    metafiles = ('ivy.xml',)
    type = StringType(default='ivy')
    primary_language = StringType(default='Java')


class BowerPackage(Package):
    metafiles = ('bower.json',)
    type = StringType(default='bower')
    primary_language = StringType(default='JavaScript')


class MeteorPackage(Package):
    metafiles = ('package.js',)
    type = StringType(default='meteor')
    primary_language = StringType(default='JavaScript')


class CpanModule(Package):
    metafiles = ('*.pod', '*.pm', 'MANIFEST', 'Makefile.PL', 'META.yml', 'META.json', '*.meta', 'dist.ini')
    # TODO: refine me
    extensions = ('.tar.gz',)
    type = StringType(default='cpan')
    primary_language = StringType(default='Perl')


# TODO: refine me: Go packages are a mess but something is emerging
class Godep(Package):
    metafiles = ('Godeps',)
    type = StringType(default='go')
    primary_language = StringType(default='Go')


class RubyGem(Package):
    metafiles = ('*.control', '*.gemspec', 'Gemfile', 'Gemfile.lock',)
    filetypes = ('.tar', 'tar archive',)
    mimetypes = ('application/x-tar',)
    extensions = ('.gem',)
    type = StringType(default='gem')
    primary_language = StringType(default='gem')


class AndroidApp(Package):
    filetypes = ('zip archive',)
    mimetypes = ('application/zip',)
    extensions = ('.apk',)
    type = StringType(default='android')
    primary_language = StringType(default='Java')


# see http://tools.android.com/tech-docs/new-build-system/aar-formats
class AndroidLibrary(Package):
    filetypes = ('zip archive',)
    mimetypes = ('application/zip',)
    # note: Apache Axis also uses AAR extensions for plain Jars.
    # this could be decided based on internal structure
    extensions = ('.aar',)
    type = StringType(default='android-lib')
    primary_language = StringType(default='Java')


class MozillaExtension(Package):
    filetypes = ('zip archive',)
    mimetypes = ('application/zip',)
    extensions = ('.xpi',)
    type = StringType(default='mozilla')
    primary_language = StringType(default='JavaScript')


class ChromeExtension(Package):
    filetypes = ('data',)
    mimetypes = ('application/octet-stream',)
    extensions = ('.crx',)
    type = StringType(default='chrome')
    primary_language = StringType(default='JavaScript')


class IOSApp(Package):
    filetypes = ('zip archive',)
    mimetypes = ('application/zip',)
    extensions = ('.ipa',)
    type = StringType(default='ios')
    primary_language = StringType(default='Objective-C')


class PythonPackage(Package):
    filetypes = ('zip archive',)
    mimetypes = ('application/zip',)
    extensions = ('.egg', '.whl', '.pyz', '.pex',)
    type = StringType(default='pypi')
    primary_language = StringType(default='Python')


class CabPackage(Package):
    filetypes = ('microsoft cabinet',)
    mimetypes = ('application/vnd.ms-cab-compressed',)
    extensions = ('.cab',)
    type = StringType(default='cab')


class MsiInstallerPackage(Package):
    filetypes = ('msi installer',)
    mimetypes = ('application/x-msi',)
    extensions = ('.msi',)
    type = StringType(default='msi')


class InstallShieldPackage(Package):
    filetypes = ('installshield',)
    mimetypes = ('application/x-dosexec',)
    extensions = ('.exe',)
    type = StringType(default='installshield')


class NSISInstallerPackage(Package):
    filetypes = ('nullsoft installer',)
    mimetypes = ('application/x-dosexec',)
    extensions = ('.exe',)
    type = StringType(default='nsis')


class SharPackage(Package):
    filetypes = ('posix shell script',)
    mimetypes = ('text/x-shellscript',)
    extensions = ('.sha', '.shar', '.bin',)
    type = StringType(default='shar')


class AppleDmgPackage(Package):
    filetypes = ('zlib compressed',)
    mimetypes = ('application/zlib',)
    extensions = ('.dmg', '.sparseimage',)
    type = StringType(default='dmg')


class IsoImagePackage(Package):
    filetypes = ('iso 9660 cd-rom', 'high sierra cd-rom',)
    mimetypes = ('application/x-iso9660-image',)
    extensions = ('.iso', '.udf', '.img',)
    type = StringType(default='iso')


class SquashfsPackage(Package):
    filetypes = ('squashfs',)
    type = StringType(default='squashfs')

#
# these very generic archive packages must come last in recogniztion order
#


class RarPackage(Package):
    filetypes = ('rar archive',)
    mimetypes = ('application/x-rar',)
    extensions = ('.rar',)
    type = StringType(default='rar')


class TarPackage(Package):
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
    type = StringType(default='tarball')


class PlainZipPackage(Package):
    filetypes = ('zip archive', '7-zip archive',)
    mimetypes = ('application/zip', 'application/x-7z-compressed',)
    extensions = ('.zip', '.zipx', '.7z',)
    type = StringType(default='zip')

# TODO: Add VM images formats(VMDK, OVA, OVF, VDI, etc) and Docker/other containers
