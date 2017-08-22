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
import string
import re

from schematics.exceptions import StopValidation
from schematics.exceptions import ValidationError

from schematics.models import Model

from schematics.types import fill_template
from schematics.types import random_string

from schematics.types import BaseType
from schematics.types import BooleanType
from schematics.types import DateTimeType
from schematics.types import EmailType
from schematics.types import HashType
from schematics.types import LongType
from schematics.types import MD5Type
from schematics.types import SHA1Type
from schematics.types import StringType
from schematics.types import URLType

from schematics.types.compound import DictType
from schematics.types.compound import ListType
from schematics.types.compound import ModelType
from schematics.transforms import blacklist


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

These metadata provide details for:
 - information on the version of the file format of the current metadata file or header.
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


class ListType(ListType):
    """
    ListType with a default of an empty list.
    """
    def __init__(self, field, **kwargs):
        super(ListType, self).__init__(field=field, default=[], **kwargs)


PackageId = namedtuple('PackageId', 'type name version')


class PackageIndentifierType(BaseType):
    """
    Global identifier for a package
    """
    def __init__(self, **kwargs):
        super(PackageIndentifierType, self).__init__(**kwargs)

    def to_primitive(self, value, context=None):
        """
        Return a package id string, joining segments with a pipe separator.
        """
        if not value:
            return value

        if isinstance(value, PackageId):
            return u'|'.join(v or u'' for v in value)
        else:
            raise TypeError('Invalid package identifier')

    def to_native(self, value):
        return value

    def validate_id(self, value):
        if not isinstance(value, PackageId):
            raise StopValidation(self.messages['Invalid Package ID: must be PackageId named tuple'])


class SHA256Type(HashType):
    LENGTH = 64


class SHA512Type(HashType):
    LENGTH = 128


class URIType(StringType):
    """
    A field that validates input as a URI with several supported schemes beyond
    HTTP.
    """
    # Regex is derived from the code of schematics.URLType. BSD-licensed, see corresponding ABOUT file
    URI_REGEX = re.compile(
        r'^'
        r'(?:'
            r'(?:https?'
            r'|ftp|sftp|ftps'
            r'|rsync'
            r'|ssh'
            r'|git|git\+https?|git\+ssh|git\+git|git\+file'
            r'|hg|hg\+https?|hg\+ssh|hg\+static-https?'

            r'|bzr|bzr\+https?|bzr\+ssh|bzr\+sftp|bzr\+ftp|bzr+lp'
            r'|svn|svn\+http?|svn\+ssh|svn\+svn'
            r')'
            r'://'

        r'|'
            r'git\@'
        r')'

        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,2000}[A-Z0-9])?\.)+[A-Z]{2,63}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )

    def __init__(self, **kwargs):
        super(URIType, self).__init__(**kwargs)

    def _mock(self, context=None):
        return fill_template('https://a%s.ZZ', self.min_length, self.max_length)

    def validate_url(self, value):
        if not self.__class__.URI_REGEX.match(value):
            raise StopValidation(self.messages['Invalid URI'])

    def canonical(self):
        """
        Return a canonical representation of this URI.
        """
        raise NotImplementedError()


class VersionType(BaseType):
    """
    A Package version is a string or a sequence of strings (list or tuple).

    'separator' is the separator string used to join a version sequence made of
    parts such as major, minor and patch.

    Packages with alternative versioning can subclass to define their own
    versioning scheme with add extra methods, a refined compare method for
    instance when storing a tuple, namedtuple or list for each each version
    parts or parsing the version in parts or exposiing parts.
    """
    metadata = dict(
        label='version',
        description='The version of the package as a string. '
        'Package types may implement specialized handling for versions, but this seralizes as a string')

    def __init__(self, separator=None, **kwargs):
        if not separator:
            separator = ''
        self.separator = separator
        super(VersionType, self).__init__(**kwargs)

    def validate_version(self, value):
        """
        Accept strings and empty strings or None as values in a value list
        """
        if value is None or isinstance(value, basestring):
            return

        if isinstance(value, (list, tuple,)) and all(isinstance(v, basestring) or v in (None, '') for v in value):
            return

        msg = 'Version must be a string or sequence of strings, not %r'
        raise ValidationError(msg % value)

    def to_primitive(self, value, context=None):
        """
        Return a version string. If the version is a sequence, join segments with separators.
        Subclasses can override.
        """
        if not value:
            return value
        if isinstance(value, (list, tuple,)):
            return unicode(self.separator).join(v for v in value if v)
        return unicode(value)

    def to_native(self, value):
        return value

    def sortable(self, value):
        """
        Return an opaque tuple to sort or compare versions. When not defined, a
        version sorts first.

        Each segment of a version is split on spaces, underscore, period and
        dash and returned separately in a sequence. Number are converted to int. This allows
        for a more natural sort.
        """
        if not value:
            return (-1,)
        srt = []
        if isinstance(value, (list, tuple,)):
            return tuple(value)

        # isinstance(value, basestring):
        for v in re.split('[\.\s\-_]', value):
            srt.append(v.isdigit() and int(v) or v)
        return tuple(srt)

    def _mock(self, context=None):
        a = random_string(1, string.digits)
        b = random_string(1, string.digits)
        return self.separator.join([a, b])


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


# Package repo types
###############################
repo_bower = 'Bower'
repo_cpan = 'CPAN'
repo_debian = 'Debian'
repo_gems = 'Rubygems'
repo_godoc = 'Godoc'
repo_ivy = 'IVY'
repo_maven = 'Maven'
repo_npm = 'NPM'
repo_phpcomposer = 'Packagist'
repo_nuget = 'Nuget'
repo_python = 'Pypi'
repo_yum = 'YUM'

REPO_TYPES = (
    repo_bower,
    repo_cpan,
    repo_debian,
    repo_gems,
    repo_godoc,
    repo_ivy,
    repo_maven,
    repo_npm,
    repo_phpcomposer,
    repo_nuget,
    repo_python,
    repo_yum,
)


class Repository(BaseModel):
    metadata = dict(
        label='package repository',
        description='Represents a package repository.')

    type = StringType(choices=REPO_TYPES)
    type.metadata = dict(
        label='package repository type',
        description='The type of package repository for this repository. '
        'One of: ' + ', '.join(REPO_TYPES))

    url = URIType()
    url.metadata = dict(
        label='url',
        description='URL to this repository.')

    public = BooleanType(default=False)
    public.metadata = dict(
        label='public repository',
        description='A flag set to true if this is a public repository.')

    mirror_urls = ListType(URIType)
    mirror_urls.metadata = dict(
        label='repository mirror urls',
        description='A list of URLs for mirrors of this repository.')

    nickname = StringType()
    nickname.metadata = dict(
        label='repository nickname',
        description='nickname used for well known "named" public repos such as: '
        'Maven Central, Pypi, RubyGems, npmjs.org or their mirrors')

    class Options:
        fields_order = 'type', 'url', 'public', 'mirror_urls', 'name'

    def download_url(self, package):
        """
        Return a download URL for this package in this repository.
        """
        return NotImplementedError()

    def packages(self):
        """
        Return an iterable of Package objects available in this repository.
        """
        return NotImplementedError()


class AssertedLicense(BaseModel):
    metadata = dict(
        label='asserted license',
        description='Represents the licensing as asserted in a package metadata.')

    license = StringType()
    license.metadata = dict(
        label='license',
        description='license as asserted. This can be a text, a name or anything.')

    url = URIType()
    url.metadata = dict(
        label='url',
        description='URL to a web page for this license.')

    text = StringType()
    text.metadata = dict(
        label='license text',
        description='license text as asserted.')

    notice = StringType()
    notice.metadata = dict(
        label='notice',
        description='a license notice for this package')

    class Options:
        fields_order = 'license', 'url', 'text', 'notice'


# Party types
#################################
party_person = 'person'
party_project = 'project'  # often loosely defined
party_org = 'organization'  # more formally defined
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

    url = URLType()
    name.metadata = dict(
        label='url',
        description='URL to a primary web page for this party.')

    email = EmailType()
    email.metadata = dict(
        label='email',
        description='Email for this party.')

    class Options:
        fields_order = 'type', 'name', 'email', 'url'


# Groupings of package dependencies
###################################
dep_runtime = 'runtime'
dep_dev = 'development'
dep_test = 'test'
dep_build = 'build'
dep_optional = 'optional'
dep_bundled = 'bundled'
dep_ci = 'continuous integration'
DEPENDENCY_GROUPS = (dep_runtime, dep_dev, dep_optional, dep_test, dep_build, dep_ci, dep_bundled,)


# FIXME: this is broken ... OSGi uses "Java packages" deps as an indirection and not directly package deps.
class Dependency(BaseModel):
    metadata = dict(
        label='dependency',
        description='A dependency points to a Package via a package name and a version constraint '
        '(such as ">= 3.4"). The version is the effective version that has been '
        'picked and resolved.')

    name = StringType(required=True)
    name.metadata = dict(
        label='name',
        description='Name of the package for this dependency.')

    version = VersionType()
    version.metadata = dict(
        label='version',
        description='Version of this dependent package: '
        'The effective or concrete resolved and used version.')

    version_constraint = StringType()
    version_constraint.metadata = dict(
        label='version',
        description='The version constraints (aka. possible versions) '
        'for this dependent package: The meaning of this constraings is '
        'package type-specific. ')

    class Options:
        fields_order = 'type', 'name', 'version', 'version_constraint'

    def resolve(self):
        """
        Compute a concrete version.
        """
        # A normalized list of version constraints for this dep. This is package-
        # independent and should be a normalized data structure describing all the
        # different version range constraints
        # normalized_version_constraints = ListType(StringType())
        raise NotImplementedError()


# Types of the payload of a Package
###################################
payload_src = 'source'
# binaries include minified JavaScripts and similar obfuscated texts formats
payload_bin = 'binary'
payload_doc = 'doc'
PAYLOADS = (payload_src, payload_bin, payload_doc)


# Packaging types
#################################
as_archive = 'archive'
as_dir = 'directory'
as_file = 'file'
PACKAGINGS = (as_archive, as_dir, as_file)

# TODO: define relations. See SPDX specs


class RelatedPackage(BaseModel):
    metadata = dict(
        label='related package',
        description='A generic related package.')

    type = StringType(required=True)
    type.metadata = dict(
        label='type',
        description='Descriptive name of the type of package: '
        'RubyGem, Python Wheel, Java Jar, Debian package, etc.')

    name = StringType(required=True)
    name.metadata = dict(
        label='name',
        description='Name of the package.')

    version = VersionType()
    version.metadata = dict(
        label='version',
        description='Version of the package')

    payload_type = StringType(choices=PAYLOADS)
    payload_type.metadata = dict(
        label='Payload type',
        description='The type of payload for this package. One of: ' + ', '.join(PAYLOADS))

    class Options:
        fields_order = 'type', 'name', 'version', 'payload_type'


class Package(BaseModel):
    """
    A package object.
    Override for specific package behaviour. The way a
    package is created and serialized should be uniform across all Package
    types.
    """
    metadata = dict(
        label='package',
        description='A package object.')

    ###############################
    # real class-level attributes
    ###############################
    # content types data to recognize a package
    filetypes = tuple()
    mimetypes = tuple()
    extensions = tuple()
    # list of known metafiles for a package type, to recognize a package
    metafiles = []

    # list of supported repository types a package type, for reference
    repo_types = []

    ###############################
    # Field descriptors
    ###############################
    # from here on, these are actual instance attributes, using descriptors

    type = StringType(required=True)
    type.metadata = dict(
        label='package type',
        description='Descriptive name of the type of package: '
        'RubyGem, Python Wheel, Java Jar, Debian package, etc.')

    name = StringType(required=True)
    name.metadata = dict(
        label='package name',
        description='Name of the package.')

    version = VersionType()
    version.metadata = dict(
        label='package version',
        description='Version of the package. '
        'Package types may implement specific handling for versions but this is always serialized as a string.')

    primary_language = StringType()
    primary_language.metadata = dict(
        label='Primary programming language',
        description='Primary programming language of the package, such as Java, C, C++. '
        'Derived from the package type: i.e. RubyGems are primarily ruby, etc.')

    packaging = StringType(choices=PACKAGINGS)
    packaging.metadata = dict(
        label='Packaging',
        description='How a package is packaged. One of: ' + ', '.join(PACKAGINGS))

    # TODO: add os and arches!!

    summary = StringType()
    summary.metadata = dict(
        label='Summary',
        description='Summary for this package i.e. a short description')

    description = StringType()
    description.metadata = dict(
        label='Description',
        description='Description for this package '
        'i.e. a long description, often several pages of text')

    payload_type = StringType(choices=PAYLOADS)
    payload_type.metadata = dict(
        label='Payload type',
        description='The type of payload for this package. One of: ' + ', '.join(PAYLOADS))

    # we useLongType instead of IntType is because
    # IntType 2147483647 is the max size which means we cannot store
    # more than 2GB files
    size = LongType()
    size.metadata = dict(
        label='size',
        description='size of the package download in bytes')

    release_date = DateTimeType()
    release_date.metadata = dict(
        label='release date',
        description='Release date of the package')

    # FIXME: this would be simpler as a list where each Party has also a type
    authors = ListType(ModelType(Party))
    authors.metadata = dict(
        label='authors',
        description='A list of party objects. Note: this model schema will change soon.')

    maintainers = ListType(ModelType(Party))
    maintainers.metadata = dict(
        label='maintainers',
        description='A list of party objects. Note: this model schema will change soon.')

    contributors = ListType(ModelType(Party))
    contributors.metadata = dict(
        label='contributors',
        description='A list of party objects. Note: this model schema will change soon.')

    owners = ListType(ModelType(Party))
    owners.metadata = dict(
        label='owners',
        description='A list of party objects. Note: this model schema will change soon.')

    packagers = ListType(ModelType(Party))
    packagers.metadata = dict(
        label='owners',
        description='A list of party objects. Note: this model schema will change soon.')

    distributors = ListType(ModelType(Party))
    distributors.metadata = dict(
        label='distributors',
        description='A list of party objects. Note: this model schema will change soon.')

    vendors = ListType(ModelType(Party))
    vendors.metadata = dict(
        label='vendors',
        description='A list of party objects. Note: this model schema will change soon.')

    keywords = ListType(StringType())
    keywords.metadata = dict(
        label='keywords',
        description='A list of keywords or tags.')

    # FIXME: this is a Package-class attribute
    keywords_doc_url = URLType()
    keywords_doc_url.metadata = dict(
        label='keywords documentation URL',
        description='URL to a reference documentation for keywords or '
        'tags (such as a Pypi or SF.net Trove map)')

    metafile_locations = ListType(StringType())
    metafile_locations.metadata = dict(
        label='metafile locations',
        description='A list of metafile locations for this package '
        '(such as a package.json, a setup.py). '
        'Relative to the package root directory or archive root')

    metafile_urls = ListType(URIType())
    metafile_urls.metadata = dict(
        label='metafile URLs',
        description='A list of metafile remote URLs for this package '
        '(such as a package.json, a setup.py)')

    homepage_url = URIType()
    homepage_url.metadata = dict(
        label='homepage URL',
        description='URL to the homepage for this package')

    notes = StringType()
    notes.metadata = dict(
        label='Notes',
        description='Notes, free text about this package')

    download_urls = ListType(URIType())
    download_urls.metadata = dict(
        label='Download URLs',
        description='A list of direct download URLs, possibly in SPDX VCS url form. '
        'The first item is considered to be the primary download URL')

    download_sha1 = SHA1Type()
    download_sha1.metadata = dict(label='Download SHA1', description='Shecksum for the download')
    download_sha256 = SHA256Type()
    download_sha256.metadata = dict(label='Download SHA256', description='Shecksum for the download')
    download_md5 = MD5Type()
    download_md5.metadata = dict(label='Download MD5', description='Shecksum for the download')

    bug_tracking_url = URLType()
    bug_tracking_url.metadata = dict(
        label='bug tracking URL',
        description='URL to the issue or bug tracker for this package')

    support_contacts = ListType(StringType())
    support_contacts.metadata = dict(
        label='Support contacts',
        description='A list of strings (such as email, urls, etc) for support contacts')

    code_view_url = URIType()
    code_view_url.metadata = dict(
        label='code view URL',
        description='a URL where the code can be browsed online')

    VCS_CHOICES = ['git', 'svn', 'hg', 'bzr', 'cvs']
    vcs_tool = StringType(choices=VCS_CHOICES)
    vcs_tool.metadata = dict(
        label='Version control system tool',
        description='The type of VCS tool for this package. One of: ' + ', '.join(VCS_CHOICES))

    vcs_repository = URIType()
    vcs_repository.metadata = dict(
        label='VCS Repository URL',
        description='a URL to the VCS repository in the SPDX form of:'
        'git+https://github.com/nexb/scancode-toolkit.git')

    vcs_revision = StringType()
    vcs_revision.metadata = dict(
        label='VCS revision',
        description='a revision, commit, branch or tag reference, etc. '
        '(can also be included in the URL)')

    copyright_top_level = StringType()
    copyright_top_level.metadata = dict(
        label='Top level Copyright',
        description='a top level copyright often asserted in package metadata')

    copyrights = ListType(StringType())
    copyrights.metadata = dict(
        label='Copyrights',
        description='A list of effective copyrights as detected and eventually summarized')

    asserted_licenses = ListType(ModelType(AssertedLicense))
    asserted_licenses.metadata = dict(
        label='asserted licenses',
        description='A list of asserted license objects representing '
        'the asserted licensing information for this package')

    legal_file_locations = ListType(StringType())
    legal_file_locations.metadata = dict(
        label='legal file locations',
        description='A list of paths to legal files '
        '(such as COPYING, NOTICE, LICENSE, README, etc.). '
        'Paths are relative to the root of the package')

    license_expression = StringType()
    license_expression.metadata = dict(
        label='license expression',
        description='license expression: either resolved or detected license expression')

    license_texts = ListType(StringType())
    license_texts.metadata = dict(
        label='license texts',
        description='A list of license texts for this package.')

    notice_texts = ListType(StringType())
    license_texts.metadata = dict(
        label='notice texts',
        description='A list of notice texts for this package.')

    # Map a DEPENDENCY_GROUPS group name to a list of Dependency
    # FIXME: we should instead just have a plain list where each dep contain a group.
    dependencies = DictType(ListType(ModelType(Dependency)), default={})
    dependencies.metadata = dict(
        label='dependencies',
        description='An object mapping a dependency group to a '
        'list of dependency objects for this package. '
        'Note: the schema for this will change soon.'
        'The possible values for dependency grousp are:' + ', '.join(DEPENDENCY_GROUPS)
        )

    related_packages = ListType(ModelType(RelatedPackage))
    related_packages.metadata = dict(
        label='related packages',
        description='A list of related_package objects for this package. '
        'For instance the SRPM source of a binary RPM.')

    class Options:
        # this defines the important serialization order
        fields_order = [
            'type',
            'name',
            'version',
            'primary_language',
            'packaging',
            'summary',
            'description',
            'payload_type',
            'size',
            'release_date',

            'authors',
            'maintainers',
            'contributors',
            'owners',
            'packagers',
            'distributors',
            'vendors',

            'keywords',
            'keywords_doc_url',

            'metafile_locations',
            'metafile_urls',

            'homepage_url',
            'notes',
            'download_urls',
            'download_sha1',
            'download_sha256',
            'download_md5',

            'bug_tracking_url',
            'support_contacts',
            'code_view_url',

            'vcs_tool',
            'vcs_repository',
            'vcs_revision',

            'copyright_top_level',
            'copyrights',

            'asserted_licenses',
            'legal_file_locations',
            'license_expression',
            'license_texts',
            'notice_texts',

            'dependencies',
            'related_packages'
        ]

        # we use for now a "role" that excludes deps and relationships from the
        # serailization
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
        return

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

    @property
    def identifier(self):
        """
        Return a PackageId object for this package.
        """
        return PackageId(self.type, self.name, self.version)


#
# Package sub types
# NOTE: this is somewhat redundant with extractcode archive handlers
# yet the purpose and semantics are rather different here


class DebianPackage(Package):
    metafiles = ('*.control',)
    extensions = ('.deb',)
    filetypes = ('debian binary package',)
    mimetypes = ('application/x-archive', 'application/vnd.debian.binary-package',)
    repo_types = (repo_debian,)

    type = StringType(default='Debian package')
    packaging = StringType(default=as_archive)


class JavaJar(Package):
    metafiles = ('META-INF/MANIFEST.MF',)
    extensions = ('.jar',)
    filetypes = ('java archive ', 'zip archive',)
    mimetypes = ('application/java-archive', 'application/zip',)
    repo_types = (repo_maven, repo_ivy,)

    type = StringType(default='Java Jar')
    packaging = StringType(default=as_archive)
    primary_language = StringType(default='Java')


class JavaWar(Package):
    metafiles = ('WEB-INF/web.xml',)
    extensions = ('.war',)
    filetypes = ('java archive ', 'zip archive',)
    mimetypes = ('application/java-archive', 'application/zip')
    repo_types = (repo_maven, repo_ivy,)

    type = StringType(default='Java Web application')
    packaging = StringType(default=as_archive)
    primary_language = StringType(default='Java')


class JavaEar(Package):
    metafiles = ('META-INF/application.xml', 'META-INF/ejb-jar.xml')
    extensions = ('.ear',)
    filetypes = ('java archive ', 'zip archive',)
    mimetypes = ('application/java-archive', 'application/zip')
    repo_types = (repo_maven, repo_ivy,)

    type = StringType(default='Enterprise Java application')
    packaging = StringType(default=as_archive)
    primary_language = StringType(default='Java')


class Axis2Mar(Package):
    metafiles = ('META-INF/module.xml',)
    extensions = ('.mar',)
    filetypes = ('java archive ', 'zip archive',)
    mimetypes = ('application/java-archive', 'application/zip')
    repo_types = (repo_maven, repo_ivy,)

    type = StringType(default='Apache Axis2 module')
    packaging = StringType(default=as_archive)
    primary_language = StringType(default='Java')


class JBossSar(Package):
    metafiles = ('META-INF/jboss-service.xml',)
    extensions = ('.sar',)
    filetypes = ('java archive ', 'zip archive',)
    mimetypes = ('application/java-archive', 'application/zip')
    repo_types = (repo_maven, repo_ivy,)

    type = StringType(default='JBoss service archive')
    packaging = StringType(default=as_archive)
    primary_language = StringType(default='Java')


class IvyJar(JavaJar):
    metafiles = ('ivy.xml',)
    repo_types = (repo_ivy,)

    type = StringType(default='Apache IVY package')


class BowerPackage(Package):
    metafiles = ('bower.json',)
    repo_types = (repo_bower, repo_npm,)

    type = StringType(default='Bower package')
    primary_language = StringType(default='JavaScript')


class MeteorPackage(Package):
    metafiles = ('package.js',)

    type = StringType(default='Meteor package')
    primary_language = 'JavaScript'


class CpanModule(Package):
    metafiles = ('*.pod', '*.pm', 'MANIFEST', 'Makefile.PL', 'META.yml', 'META.json', '*.meta', 'dist.ini')
    # TODO: refine me
    extensions = (
        '.tar.gz',
    )
    repo_types = (repo_cpan,)

    type = StringType(default='CPAN Perl module')
    primary_language = 'Perl'


# TODO: refine me
class Godep(Package):
    metafiles = ('Godeps',)
    repo_types = (repo_godoc,)

    type = StringType(default='Go package')
    primary_language = 'Go'


class RubyGem(Package):
    metafiles = ('*.control', '*.gemspec', 'Gemfile', 'Gemfile.lock',)
    filetypes = ('.tar', 'tar archive',)
    mimetypes = ('application/x-tar',)
    extensions = ('.gem',)
    repo_types = (repo_gems,)

    type = StringType(default='RubyGem')
    primary_language = 'Ruby'
    packaging = StringType(default=as_archive)


class AndroidApp(Package):
    filetypes = ('zip archive',)
    mimetypes = ('application/zip',)
    extensions = ('.apk',)

    type = StringType(default='Android app')
    primary_language = StringType(default='Java')
    packaging = StringType(default=as_archive)


# see http://tools.android.com/tech-docs/new-build-system/aar-formats
class AndroidLibrary(Package):
    filetypes = ('zip archive',)
    mimetypes = ('application/zip',)
    # note: Apache Axis also uses AAR extensions for plain Jars.
    # this could be decided based on internal structure
    extensions = ('.aar',)

    type = StringType(default='Android library')
    primary_language = StringType(default='Java')
    packaging = StringType(default=as_archive)


class MozillaExtension(Package):
    filetypes = ('zip archive',)
    mimetypes = ('application/zip',)
    extensions = ('.xpi',)

    type = StringType(default='Mozilla extension')
    primary_language = StringType(default='JavaScript')
    packaging = StringType(default=as_archive)


class ChromeExtension(Package):
    filetypes = ('data',)
    mimetypes = ('application/octet-stream',)
    extensions = ('.crx',)

    type = StringType(default='Chrome extension')
    primary_language = StringType(default='JavaScript')
    packaging = StringType(default=as_archive)


class IOSApp(Package):
    filetypes = ('zip archive',)
    mimetypes = ('application/zip',)
    extensions = ('.ipa',)

    type = StringType(default='iOS app')
    primary_language = StringType(default='Objective-C')
    packaging = StringType(default=as_archive)


class PythonPackage(Package):
    filetypes = ('zip archive',)
    mimetypes = ('application/zip',)
    extensions = ('.egg', '.whl', '.pyz', '.pex',)
    repo_types = (repo_python,)

    type = StringType(default='Python package')
    primary_language = StringType(default='Python')
    packaging = StringType(default=as_archive)


class CabPackage(Package):
    filetypes = ('microsoft cabinet',)
    mimetypes = ('application/vnd.ms-cab-compressed',)
    extensions = ('.cab',)

    type = StringType(default='Microsoft cab')
    packaging = StringType(default=as_archive)


class MsiInstallerPackage(Package):
    filetypes = ('msi installer',)
    mimetypes = ('application/x-msi',)
    extensions = ('.msi',)

    type = StringType(default='Microsoft MSI Installer')
    packaging = StringType(default=as_archive)


class InstallShieldPackage(Package):
    filetypes = ('installshield',)
    mimetypes = ('application/x-dosexec',)
    extensions = ('.exe',)

    type = StringType(default='InstallShield Installer')
    packaging = StringType(default=as_archive)


class NSISInstallerPackage(Package):
    filetypes = ('nullsoft installer',)
    mimetypes = ('application/x-dosexec',)
    extensions = ('.exe',)

    type = StringType(default='Nullsoft Installer')
    packaging = StringType(default=as_archive)


class SharPackage(Package):
    filetypes = ('posix shell script',)
    mimetypes = ('text/x-shellscript',)
    extensions = ('.sha', '.shar', '.bin',)

    type = StringType(default='shar shell archive')
    packaging = StringType(default=as_archive)


class AppleDmgPackage(Package):
    filetypes = ('zlib compressed',)
    mimetypes = ('application/zlib',)
    extensions = ('.dmg', '.sparseimage',)

    type = StringType(default='Apple dmg')
    packaging = StringType(default=as_archive)


class IsoImagePackage(Package):
    filetypes = ('iso 9660 cd-rom', 'high sierra cd-rom',)
    mimetypes = ('application/x-iso9660-image',)
    extensions = ('.iso', '.udf', '.img',)

    type = StringType(default='ISO CD image')
    packaging = StringType(default=as_archive)


class SquashfsPackage(Package):
    filetypes = ('squashfs',)

    type = StringType(default='squashfs image')
    packaging = StringType(default=as_archive)


#
# these very generic archive packages must come last in recogniztion order
#


class RarPackage(Package):
    filetypes = ('rar archive',)
    mimetypes = ('application/x-rar',)
    extensions = ('.rar',)

    type = StringType(default='RAR archive')
    packaging = StringType(default=as_archive)


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

    type = StringType(default='plain tarball')
    packaging = StringType(default=as_archive)


class PlainZipPackage(Package):
    filetypes = ('zip archive', '7-zip archive',)
    mimetypes = ('application/zip', 'application/x-7z-compressed',)
    extensions = ('.zip', '.zipx', '.7z',)

    packaging = StringType(default=as_archive)
    type = StringType(default='plain zip')

# TODO: Add VM images formats(VMDK, OVA, OVF, VDI, etc) and Docker/other containers
