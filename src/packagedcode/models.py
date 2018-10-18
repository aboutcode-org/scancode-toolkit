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

from collections import OrderedDict
import logging
import sys

import attr
from attr.validators import in_ as choices
from packageurl import PackageURL

from commoncode.datautils import Boolean
from commoncode.datautils import Date
from commoncode.datautils import Integer
from commoncode.datautils import List
from commoncode.datautils import Mapping
from commoncode.datautils import String


# Python 2 and 3 support
try:
    # Python 2
    unicode
    str_orig = str
    bytes = str  # NOQA
    str = unicode  # NOQA
except NameError:
    # Python 3
    unicode = str  # NOQA


"""
Data models for package information and dependencies, abstracting the
differences existing between package formats and tools.

A package has a somewhat fuzzy definition and is code that can be consumed and
provisioned by a package manager or can be installed.

It can be a single file such as script; more commonly a package is stored in an
archive or directory.

A package contains:
 - information typically in a "manifest" file,
 - a payload of code, doc, data.

Structured package information are found in multiple places:
- in manifest file proper (such as a Maven POM, NPM package.json and many others)
- in binaries (such as an Elf or LKM, Windows PE or RPM header).
- in code (JavaDoc tags or Python __copyright__ magic)
There are collectively named "manifests" in ScanCode.

We handle package information at two levels:
1.- package information collected in a "manifest" at a file level
2.- aggregated package information based on "manifest" at a directory or archive
level (or in some rarer cases file level)

The second requires the first to be computed.
The schema for these two is the same.
"""

TRACE = False


def logger_debug(*args):
    pass


logger = logging.getLogger(__name__)

if TRACE:
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, (bytes, str)) and a or repr(a) for a in args))



class BaseModel(object):
    """
    Base class for all package models.
    """

    def to_dict(self, **kwargs):
        """
        Return an OrderedDict of primitive Python types.
        """
        return attr.asdict(self, dict_factory=OrderedDict)


party_person = 'person'
# often loosely defined
party_project = 'project'
# more formally defined
party_org = 'organization'
PARTY_TYPES = (
    None,
    party_person,
    party_project,
    party_org,
)


@attr.s()
class Party(BaseModel):
    """
    A party is a person, project or organization related to a package.
    """

    type = String(
        validator=choices(PARTY_TYPES),
        label='party type',
        help='the type of this party: One of: '
            +', '.join(p for p in PARTY_TYPES if p)
    )

    role = String(
        label='party role',
        help='A role for this party. Something such as author, '
             'maintainer, contributor, owner, packager, distributor, '
             'vendor, developer, owner, etc.'
    )

    name = String(
        label='name',
        help='Name of this party.'
    )

    email = String(
        label='email',
        help='Email for this party.'
    )

    url = String(
        label='url',
        help='URL to a primary web page for this party.'
    )


@attr.s()
class BasePackage(BaseModel):
    """
    A base identifiable package object using discrete identifying attributes as
    specified here https://github.com/package-url/purl-spec.
    """

    # class-level attributes used to recognize a package
    filetypes = tuple()
    mimetypes = tuple()
    extensions = tuple()
    # list of known metafiles for a package type
    metafiles = []

    # Optional. Public default web base URL for package homepages of this
    # package type on the default repository.
    default_web_baseurl = None

    # Optional. Public default download base URL for direct downloads of this
    # package type the default repository.
    default_download_baseurl = None

    # Optional. Public default API repository base URL for package API calls of
    # this package type on the default repository.
    default_api_baseurl = None

    # Optional. Public default type for a package class.
    default_type = None

    type = String(
#         default=attr.NOTHING,
        repr=True,
        label='package type',
        help='Optional. A short code to identify what is the type of this '
             'package. For instance gem for a Rubygem, docker for container, '
             'pypi for Python Wheel or Egg, maven for a Maven Jar, '
             'deb for a Debian package, etc.'
    )

    namespace = String(
        repr=True,
        label='package namespace',
        help='Optional namespace for this package.'
    )

    name = String(
#         default=attr.NOTHING,
        repr=True,
        label='package name',
        help='Name of the package.'
    )

    version = String(
        repr=True,
        label='package version',
        help='Optional version of the package as a string.'
    )

    qualifiers = Mapping(
        default=None,
        value_type=str,
        label='package qualifiers',
        help='Optional mapping of key=value pairs qualifiers for this package'
    )

    subpath = String(
        label='extra package subpath',
        help='Optional extra subpath inside a package and relative to the root '
             'of this package'
    )

    def __attrs_post_init__(self, *args, **kwargs):
        if not self.type and hasattr(self, 'default_type'):
            self.type = self.default_type

    @property
    def purl(self):
        """
        Return a compact purl package URL string.
        """
        return PackageURL(
            self.type, self.namespace, self.name, self.version,
            self.qualifiers, self.subpath).to_string()

    def repository_homepage_url(self, baseurl=default_web_baseurl):
        """
        Return the package repository homepage URL for this package, e.g. the
        URL to the page for this package in its package repository. This is
        typically different from the package homepage URL proper.
        Subclasses should override to provide a proper value.
        """
        return

    def repository_download_url(self, baseurl=default_download_baseurl):
        """
        Return the package repository download URL to download the actual
        archive of code of this package. This may be different than the actual
        download URL and is computed from the default public respoitory baseurl.
        Subclasses should override to provide a proper value.
        """
        return

    def api_data_url(self, baseurl=default_api_baseurl):
        """
        Return the package repository API URL to obtain structured data for this
        package such as the URL to a JSON or XML api.
        Subclasses should override to provide a proper value.
        """
        return

    def to_dict(self, **kwargs):
        """
        Return an OrderedDict of primitive Python types.
        """
        mapping = attr.asdict(self, dict_factory=OrderedDict)
        if not kwargs.get('exclude_properties'):
            mapping['purl'] = self.purl
            mapping['repository_homepage_url'] = self.repository_homepage_url()
            mapping['repository_download_url'] = self.repository_download_url()
            mapping['api_data_url'] = self.api_data_url()
        return mapping


@attr.s()
class DependentPackage(BaseModel):
    """
    An identifiable dependent package package object.
    """

    purl = String(
        repr=True,
        label='Dependent package URL',
        help='A compact purl package URL'
    )

    requirement = String(
        repr=True,
        label='dependent package version requirement',
        help='A string defining version(s)requirements. Package-type specific.'
    )

    scope = String(
        repr=True,
        label='dependency scope',
        help='The scope of this dependency, such as runtime, install, etc. '
        'This is package-type specific and is the original scope string.'
    )

    is_runtime = Boolean(
        default=True,
        label='is runtime flag',
        help='True if this dependency is a runtime dependency.'
    )

    is_optional = Boolean(
        default=False,
        label='is optional flag',
        help='True if this dependency is an optional dependency'
    )

    is_resolved = Boolean(
        default=False,
        label='is resolved flag',
        help='True if this dependency version requirement has '
             'been resolved and this dependency url points to an '
             'exact version.'
    )


code_type_src = 'source'
code_type_bin = 'binary'
code_type_doc = 'documentation'
code_type_data = 'data'
CODE_TYPES = (
    None,
    code_type_src,
    code_type_bin,
    code_type_doc,
    code_type_data,
)


@attr.s()
class Package(BasePackage):
    """
    A package object as represented by its manifest data.
    """

    # Optional. Public default type for a package class.
    default_primary_language = None

    primary_language = String(
        label='Primary programming language',
        help='Primary programming language',
    )

    code_type = String(
        validator=choices(CODE_TYPES),
        label='code type',
        help='Primary type of code in this Package such as source, binary, '
             'data, documentation.'
    )

    description = String(
        label='Description',
        help='Description for this package. '
        'By convention the first should be a summary when available.')

    size = Integer(
        default=None,
        label='download size',
        help='size of the package download in bytes')

    release_date = Date(
        label='release date',
        help='Release date of the package')

    parties = List(
        item_type=Party,
        label='parties',
        help='A list of parties such as a person, project or organization.'
    )

    # FIXME: consider using tags rather than keywords
    keywords = List(
        item_type=str,
        label='keywords',
        help='A list of keywords.')

    homepage_url = String(
        label='homepage URL',
        help='URL to the homepage for this package.')

    download_url = String(
        label='Download URL',
        help='A direct download URL.')

    download_sha1 = String(
        label='SHA1 checksum',
        help='SHA1 checksum for this download in hexadecimal')

    download_md5 = String(
        label='MD5 checksum',
        help='MD5 checksum for this download in hexadecimal')

    download_sha256 = String(
        label='SHA256 checksum',
        help='SHA256 checksum for this download in hexadecimal')

    download_sha512 = String(
        label='SHA512 checksum',
        help='SHA512 checksum for this download in hexadecimal')

    # FIXME: use a simpler, compact VCS URL instead???
#     vcs_url = StringType()
#     vcs_url.metadata = dict(
#         label='Version control URL',
#         help='Version control URL for this package using the SPDX VCS URL conventions.')

    bug_tracking_url = String(
        label='bug tracking URL',
        help='URL to the issue or bug tracker for this package')

    code_view_url = String(
        label='code view URL',
        help='a URL where the code can be browsed online')

    VCS_CHOICES = [
        None,
        'git', 'svn', 'hg', 'bzr', 'cvs'
    ]
    vcs_tool = String(
        validator=choices(VCS_CHOICES),
        label='Version control system tool',
        help='The type of VCS tool for this package. One of: '
             +', '.join(c for c in VCS_CHOICES if c))

    vcs_repository = String(
        label='VCS Repository URL',
        help='a URL to the VCS repository in the SPDX form of:'
        'git+https://github.com/nexb/scancode-toolkit.git')

    vcs_revision = String(
        label='VCS revision',
        help='a revision, commit, branch or tag reference, etc. '
        '(can also be included in the URL)')

    copyright = String(
        label='Copyright',
        help='Copyright statements for this package. Typically one per line.')

    license_expression = String(
        label='license expression',
        help='The license expression for this package.')

    declared_licensing = String(
        label='declared licensing',
        help='The licensing text as declared in a package manifest.')

    notice_text = String(
        label='notice text',
        help='A notice text for this package.')

    manifest_path = String(
        label='manifest path',
        help='A relative path to the manifest file if any, such as a '
             'Maven .pom or a npm package.json.')

    dependencies = List(
        item_type=DependentPackage,
        label='dependencies',
        help='A list of DependentPackage for this package. ')

    source_packages = List(
        item_type=String,
        label='Source packages for this package',
        help='A list of source package URLs (aka. "purl") for this package. '
        'For instance an SRPM is the "source package" for a binary RPM.')

    def __attrs_post_init__(self, *args, **kwargs):
        if not self.type and hasattr(self, 'default_type'):
            self.type = self.default_type

        if not self.primary_language and hasattr(self, 'default_primary_language'):
            self.primary_language = self.default_primary_language

    @classmethod
    def recognize(cls, location):
        """
        Return a Package object or None given a file location pointing to a
        package archive, manifest or similar.

        Sub-classes should override to implement their own package recognition.
        """
        raise NotImplementedError

    @classmethod
    def get_package_root(cls, manifest_resource, codebase):
        """
        Return the Resource for the package root given a `manifest_resource`
        Resource object that represents a manifest in the `codebase` Codebase.

        Each package type and instance have different conventions on how a
        package manifest relates to the root of a package.

        For instance, given a "package.json" file, the root of an npm is the
        parent directory. The same applies with a Maven "pom.xml". In the case
        of a "xyz.pom" file found inside a JAR META-INF/ directory, the root is
        the JAR itself which may not be the direct parent

        Each package type should subclass as needed. This deafult to return the
        same path.
        """
        return manifest_resource
#

# Package types
# NOTE: this is somewhat redundant with extractcode archive handlers
# yet the purpose and semantics are rather different here


@attr.s()
class DebianPackage(Package):
    metafiles = ('*.control',)
    extensions = ('.deb',)
    filetypes = ('debian binary package',)
    mimetypes = ('application/x-archive', 'application/vnd.debian.binary-package',)
    default_type = 'deb'


@attr.s()
class JavaJar(Package):
    metafiles = ('META-INF/MANIFEST.MF',)
    extensions = ('.jar',)
    filetypes = ('java archive ', 'zip archive',)
    mimetypes = ('application/java-archive', 'application/zip',)
    default_type = 'jar'
    default_primary_language = 'Java'


@attr.s()
class JavaWar(Package):
    metafiles = ('WEB-INF/web.xml',)
    extensions = ('.war',)
    filetypes = ('java archive ', 'zip archive',)
    mimetypes = ('application/java-archive', 'application/zip')
    default_type = 'war'
    default_primary_language = 'Java'


@attr.s()
class JavaEar(Package):
    metafiles = ('META-INF/application.xml', 'META-INF/ejb-jar.xml')
    extensions = ('.ear',)
    filetypes = ('java archive ', 'zip archive',)
    mimetypes = ('application/java-archive', 'application/zip')
    default_type = 'ear'
    default_primary_language = 'Java'


@attr.s()
class Axis2Mar(Package):
    """Apache Axis2 module"""
    metafiles = ('META-INF/module.xml',)
    extensions = ('.mar',)
    filetypes = ('java archive ', 'zip archive',)
    mimetypes = ('application/java-archive', 'application/zip')
    default_type = 'axis2'
    default_primary_language = 'Java'


@attr.s()
class JBossSar(Package):
    metafiles = ('META-INF/jboss-service.xml',)
    extensions = ('.sar',)
    filetypes = ('java archive ', 'zip archive',)
    mimetypes = ('application/java-archive', 'application/zip')
    default_type = 'jboss'
    default_primary_language = 'Java'


@attr.s()
class IvyJar(JavaJar):
    metafiles = ('ivy.xml',)
    default_type = 'ivy'
    default_primary_language = 'Java'


@attr.s()
class BowerPackage(Package):
    metafiles = ('bower.json',)
    default_type = 'bower'
    default_primary_language = 'JavaScript'

    @classmethod
    def get_package_root(cls, manifest_resource, codebase):
        return manifest_resource.parent(codebase)


@attr.s()
class MeteorPackage(Package):
    metafiles = ('package.js',)
    default_type = 'meteor'
    default_primary_language = 'JavaScript'

    @classmethod
    def get_package_root(cls, manifest_resource, codebase):
        return manifest_resource.parent(codebase)


@attr.s()
class CpanModule(Package):
    metafiles = (
        '*.pod',
        '*.pm',
        'MANIFEST',
        'Makefile.PL',
        'META.yml',
        'META.json',
        '*.meta',
        'dist.ini',
    )
    # TODO: refine me
    extensions = ('.tar.gz',)
    default_type = 'cpan'
    default_primary_language = 'Perl'


# TODO: refine me: Go packages are a mess but something is emerging
# TODO: move to and use godeps.py
@attr.s()
class Godep(Package):
    metafiles = ('Godeps',)
    default_type = 'golang'
    default_primary_language = 'Go'

    @classmethod
    def get_package_root(cls, manifest_resource, codebase):
        return manifest_resource.parent(codebase)


@attr.s()
class RubyGem(Package):
    metafiles = ('*.control', '*.gemspec', 'Gemfile', 'Gemfile.lock',)
    filetypes = ('.tar', 'tar archive',)
    mimetypes = ('application/x-tar',)
    extensions = ('.gem',)
    default_type = 'gem'
    default_primary_language = 'Ruby'

    @classmethod
    def get_package_root(cls, manifest_resource, codebase):
        return manifest_resource.parent(codebase)


# @attr.s()
# class AlpinePackage(Package):
#     metafiles = ('*.control',)
#     extensions = ('.apk',)
#     filetypes = ('debian binary package',)
#     mimetypes = ('application/x-archive', 'application/vnd.debian.binary-package',)
#     default_type = 'alpine'


@attr.s()
class AndroidApp(Package):
    filetypes = ('zip archive',)
    mimetypes = ('application/zip',)
    extensions = ('.apk',)
    default_type = 'android'
    default_primary_language = 'Java'


# see http://tools.android.com/tech-docs/new-build-system/aar-formats
@attr.s()
class AndroidLibrary(Package):
    filetypes = ('zip archive',)
    mimetypes = ('application/zip',)
    # note: Apache Axis also uses AAR extensions for plain Jars.
    # this could be decided based on internal structure
    extensions = ('.aar',)
    default_type = 'android-lib'
    default_primary_language = 'Java'


@attr.s()
class MozillaExtension(Package):
    filetypes = ('zip archive',)
    mimetypes = ('application/zip',)
    extensions = ('.xpi',)
    default_type = 'mozilla'
    default_primary_language = 'JavaScript'


@attr.s()
class ChromeExtension(Package):
    filetypes = ('data',)
    mimetypes = ('application/octet-stream',)
    extensions = ('.crx',)
    default_type = 'chrome'
    default_primary_language = 'JavaScript'


@attr.s()
class IOSApp(Package):
    filetypes = ('zip archive',)
    mimetypes = ('application/zip',)
    extensions = ('.ipa',)
    default_type = 'ios'
    default_primary_language = 'Objective-C'


@attr.s()
class CabPackage(Package):
    filetypes = ('microsoft cabinet',)
    mimetypes = ('application/vnd.ms-cab-compressed',)
    extensions = ('.cab',)
    default_type = 'cab'


@attr.s()
class MsiInstallerPackage(Package):
    filetypes = ('msi installer',)
    mimetypes = ('application/x-msi',)
    extensions = ('.msi',)
    default_type = 'msi'


@attr.s()
class InstallShieldPackage(Package):
    filetypes = ('installshield',)
    mimetypes = ('application/x-dosexec',)
    extensions = ('.exe',)
    default_type = 'installshield'


@attr.s()
class NSISInstallerPackage(Package):
    filetypes = ('nullsoft installer',)
    mimetypes = ('application/x-dosexec',)
    extensions = ('.exe',)
    default_type = 'nsis'


@attr.s()
class SharPackage(Package):
    filetypes = ('posix shell script',)
    mimetypes = ('text/x-shellscript',)
    extensions = ('.sha', '.shar', '.bin',)
    default_type = 'shar'


@attr.s()
class AppleDmgPackage(Package):
    filetypes = ('zlib compressed',)
    mimetypes = ('application/zlib',)
    extensions = ('.dmg', '.sparseimage',)
    default_type = 'dmg'


@attr.s()
class IsoImagePackage(Package):
    filetypes = ('iso 9660 cd-rom', 'high sierra cd-rom',)
    mimetypes = ('application/x-iso9660-image',)
    extensions = ('.iso', '.udf', '.img',)
    default_type = 'iso'


@attr.s()
class SquashfsPackage(Package):
    filetypes = ('squashfs',)
    default_type = 'squashfs'


# TODO: Add VM images formats(VMDK, OVA, OVF, VDI, etc) and Docker/other containers
