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

from collections import namedtuple
from collections import OrderedDict
import logging
import sys
from urllib import quote
from urlparse import unquote

from schematics.exceptions import ValidationError
from schematics.models import Model
from schematics.transforms import blacklist
from schematics.types import BooleanType
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


class OrderedDictType(DictType):
    """
    An ordered dictionary type.
    If a value is an ordered dict, it is sorted or
    """
    def __init__(self, field, coerce_key=None, **kwargs):
        kwargs['default'] = OrderedDict()
        super(OrderedDictType, self).__init__(field, coerce_key=None, **kwargs)

    def to_native(self, value, safe=False, context=None):
        if not value:
            value = OrderedDict()

        if not isinstance(value, (dict, OrderedDict)):
            raise ValidationError(u'Only dictionaries may be used in an OrderedDictType')

        items = value.iteritems()
        if not isinstance(value, OrderedDict):
            items = sorted(value.iteritems())

        return OrderedDict((self.coerce_key(k), self.field.to_native(v, context))
                    for k, v in items)

    def export_loop(self, dict_instance, field_converter,
                    role=None, print_none=False):
        """Loops over each item in the model and applies either the field
        transform or the multitype transform.  Essentially functions the same
        as `transforms.export_loop`.
        """
        data = OrderedDict()

        items = dict_instance.iteritems()
        if not isinstance(dict_instance, OrderedDict):
            items = sorted(dict_instance.iteritems())

        for key, value in items:
            if hasattr(self.field, 'export_loop'):
                shaped = self.field.export_loop(value, field_converter,
                                                role=role)
                feels_empty = shaped and len(shaped) == 0
            else:
                shaped = field_converter(self.field, value)
                feels_empty = shaped is None

            if feels_empty and self.field.allow_none():
                data[key] = shaped
            elif shaped is not None:
                data[key] = shaped
            elif print_none:
                data[key] = shaped

        if len(data) > 0:
            return data
        elif len(data) == 0 and self.allow_none():
            return data
        elif print_none:
            return data


class BaseListType(ListType):
    """
    ListType with a default of an empty list.
    """
    def __init__(self, field, **kwargs):
        kwargs['default'] = []
        super(BaseListType, self).__init__(field=field, **kwargs)


class PackageIdentifier(
        namedtuple('PackageIdentifier',
            'type namespace name version qualifiers path')):
    """
    A "mostly universal" Package identifier tuple.
    This is either
     - a URL string as in:
        `type://namespace/name@version?qualifiers#path`
     - a set of string fields:
      - type: optional. The type of package as maven, npm, rpm.
      - namespace: optional. Some namespace prefix, slash-separated
        such as an NPM scope, a Gigthub user or org, a Debian distro
        codename, a Maven groupid.
      - name: mandatory.
      - version: optional.
      - qualifiers: optional. A dictionary of name/value pairs
        (when serialized in an deintifier string, this is using a URL
        query string formatting as: foo=bar&alice=bob)
      - path: optional. A path relative to the root of a package
        pointing to a directory or file inside a package, such as the
        Golang sub-path inside a Git repo.
    """
    def __new__(self, type=None, namespace=None, name=None,
                version=None, qualifiers=None, path=None):

        for key, value in (
            ('type', type),
            ('namespace', namespace),
            ('name', name),
            ('version', version),
            ('qualifiers', qualifiers),
            ('path', path)):

            if key == 'qualifiers':
                if qualifiers and not isinstance(qualifiers, dict):
                    raise ValueError(
                        "Invalid PackageIdentifier: 'qualifiers' "
                        "must be a mapping: {}".format(repr(qualifiers)))
                continue

            if value and not isinstance(value, basestring):
                raise ValueError(
                    'Invalid PackageIdentifier: '
                    '{} must be a string: {}'.format(repr(name), repr(value)))

            if key == 'name' and not name:
                raise ValueError("Invalid PackageIdentifier: a 'name' is required.")

        return super(PackageIdentifier, self).__new__(PackageIdentifier,
            type or None, namespace or None,
            name,
            version or None, qualifiers or None, path or None)

    def __str__(self, *args, **kwargs):
        return self.to_string()

    def to_string(self):
        """
        Return a compact ABC Package identifier URL in the form of
        `type://namespace/name@version?qualifiers#path`
        """
        identifier = []
        if self.type:
            identifier.append(self.type.strip())
            identifier.append(':')

        if self.namespace:
            identifier.append(quote(self.namespace.strip().strip('/')))
            identifier.append('/')

        identifier.append(quote(self.name.strip().strip('/')))

        if self.version:
            identifier.append('@')
            identifier.append(quote(self.version.strip()))

        # note: qualifiers are sorted, and each part quoted
        if self.qualifiers:
            quals = sorted(self.qualifiers.items())
            quals = [(quote(k.strip()), quote(v.strip())) for k, v in quals]
            quals = ['{}={}'.format(k, v) for k, v in quals]
            quals = '&'.join(quals)
            identifier.append('?')
            identifier.append(self.quals)

        if self.path:
            identifier.append('#')
            identifier.append(quote(self.path.strip().strip('/')))
        return ''.join(identifier)

    @classmethod
    def from_string(cls, package_id):
        """
        Return a PackageIdentifier parsed from a string.
        """
        if not package_id:
            raise ValueError('package_id is required.')
        package_id = package_id.strip()

        head, _sep, path = package_id.rpartition('#')
        if path:
            path = unquote(path).strip()

        head, _sep, qualifiers = head.rpartition('?')
        if qualifiers:
            quals = qualifiers.split('&')
            quals = [kv.split('=') for kv in quals]
            quals = [(unquote(k).strip(), unquote(v).strip()) for k, v in quals]
            qualifiers = dict(quals)

        head, _sep, version = head.rpartition('@')
        if version:
            version = unquote(version).strip()

        type, _sep, ns_name = head.rpartition(':')
        if type:
            type = type.strip().lower()

        ns_name = ns_name.strip('/')
        ns_name = ns_name.split('/')
        ns_name = [unquote(part).strip() for part in ns_name if part]
        namespace = ''

        if len(ns_name) > 1:
            name = ns_name[-1].strip()
            ns = ns_name[0:-1]
            ns = [p.strip() for p in ns]
            namespace = '/'.join(ns)
        elif len(ns_name) == 1:
            name = ns_name[0].strip()

        if not name:
            raise ValueError('A package name is required: '.format(repr(package_id)))

        return PackageIdentifier(type, namespace, name, version, qualifiers, path)


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


class PackageRelationship(BaseModel):
    metadata = dict(
        label='relationship between two packages',
        description='A directed relationship between two packages. '
            'This consiste of three attributes:'
            'The "from" (or subject) package identifier in the relationship, '
            'the "to" (or object) package identifier in the relationship, '
            'and the "relationship" (or predicate) string that specifies the relationship.'
            )

    from_pid= StringType()
    from_pid.metadata = dict(
        label='"From" package identifier in the relationship',
        description='A compact ABC Package identifier URL in the form of '
            'type://namespace/name@version?qualifiers#path')

    to_pid= StringType()
    to_pid.metadata = dict(
        label='"To" package identifier in the relationship',
        description='A compact ABC Package identifier URL in the form of '
            'type://namespace/name@version?qualifiers#path')

    relationship= StringType()
    relationship.metadata = dict(
        label='Relationship between two packages.',
        description='Relationship between the from and to package '
            'identifiers such as "source_of" when a package is the source '
            'code package for another package')


class BasePackage(BaseModel):
    metadata = dict(
        label='base package',
        description='A base identifiable package object using discrete '
            'identifiers attributes.')

    # class-level attributes used to recognize a package
    filetypes = tuple()
    mimetypes = tuple()
    extensions = tuple()
    # list of known metafiles for a package type
    metafiles = []

    type = StringType()
    type.metadata = dict(
        label='package type',
        description='Optional. A short code to identify what is the type of this '
            'package. For instance gem for a Rubygem, docker for container, '
            'pypi for Python Wheel or Egg, maven for a Maven Jar, '
            'deb for a Debian package, etc.')

    namespace = StringType()
    namespace.metadata = dict(
        label='package namespace',
        description='Optional namespace for this package.')

    name = StringType(required=True)
    name.metadata = dict(
        label='package name',
        description='Name of the package.')

    version = StringType()
    version.metadata = dict(
        label='package version',
        description='Optional version of the package as a string.')

    qualifiers = DictType(StringType)
    qualifiers.metadata = dict(
        label='package qualifiers',
        description='Optional mapping of key=value pairs qualifiers for this package')

    path = StringType()
    path.metadata = dict(
        label='extra package path',
        description='Optional extra path inside and relative to the root of this package')

    @property
    def identifier(self):
        """
        Return a compact ABC Package identifier URL in the form of
        `type://namespace/name@version?qualifiers#path`
        """
        pid = PackageIdentifier(
            self.type, self.namespace, self.name, self.version,
            self.qualifiers, self.path)
        return str(pid)

    class Options:
        # this defines the important serialization order
        fields_order = [
            'type',
            'namespace',
            'name',
            'version',
            'qualifiers',
            'path',
        ]


class DependentPackage(BaseModel):
    metadata = dict(
        label='minimally identifiable dependency',
        description='A base identifiable package object.')

    identifier = StringType()
    identifier.metadata = dict(
        label='package identifier',
        description='A compact ABC Package identifier URL in the form of '
        'type://namespace/name@version?qualifiers#path')

    requirement = StringType()
    requirement.metadata = dict(
        label='dependency version requirement',
        description='A string defining version(s)requirements. Package-type specific.')

    scope = StringType()
    scope.metadata = dict(
        label='dependency scope',
        description='The scope of a dependency, such as runtime, install, etc. '
        'This is package-type specific and is the original scope string.')

    is_runtime = BooleanType()
    is_runtime.metadata = dict(
        label='is runtime flag',
        description='True if this dependency is a runtime dependency.')

    is_optional = BooleanType()
    is_runtime.metadata = dict(
        label='is optional flag',
        description='True if this dependency is an optional dependency')

    is_resolved = BooleanType()
    is_resolved.metadata = dict(
        label='is resolved flag',
        description='True if this dependency version requirement has '
        'been resolved and this dependency identifier points to an '
        'exact version.')

    class Options:
        # this defines the important serialization order
        fields_order = [
            'identifier',
            'requirement',
            'scope',
            'is_runtime',
            'is_optional',
            'is_resolved',
        ]


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

    parties = BaseListType(ModelType(Party))
    parties.metadata = dict(
        label='parties',
        description='A list of parties such as a person, project or organization.'
    )

    # FIXME: consider using tags rather than keywords
    keywords = BaseListType(StringType())
    keywords.metadata = dict(
        label='keywords',
        description='A list of tags.')

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

    homepage_url = StringType()
    homepage_url.metadata = dict(
        label='homepage URL',
        description='URL to the homepage for this package')

#    repository_page_url = StringType()
#    repository_page_url.metadata = dict(
#        label='Package repository page URL',
#        description='URL to the page for this package in its package repository')

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

    license_expression = StringType()
    license_expression.metadata = dict(
        label='license expression',
        description='The license expression for this package.')

    asserted_license = StringType()
    asserted_license.metadata = dict(
        label='asserted license',
        description='The license as asserted by this package as a text.')

    notice_text = StringType()
    notice_text.metadata = dict(
        label='notice text',
        description='A notice text for this package.')

    dependencies = BaseListType(ModelType(DependentPackage))
    dependencies.metadata = dict(
        label='dependencies',
        description='A list of DependentPackage for this package. ')

    related_packages = BaseListType(ModelType(PackageRelationship))
    related_packages.metadata = dict(
        label='related packages',
        description='A list of package relationships for this package. '
        'For instance an SRPM is the "source of" a binary RPM.')

    class Options:
        # this defines the important serialization order
        fields_order = [
            'type',
            'namespace',
            'name',
            'version',
            'qualifiers',
            'path',
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
            'license_expression',
            'asserted_license',
            'license_url',
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
        return cls(location)

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
