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
from schematics.types import EmailType
from schematics.types import HashType
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

    def as_dict(self, **kwargs):
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
    repo_nuget,
    repo_python,
    repo_yum,
)


class Repository(BaseModel):
    """
    A package repository.
    """
    type = StringType(choices=REPO_TYPES)
    url = URIType()
    # True if this is a public repository
    public = BooleanType(default=False)
    mirror_urls = ListType(URIType)
    # optional: nickname used for well known "named" public repos such as:
    # Maven Central, Pypi, RubyGems, npmjs.org or their mirrors
    nickname = StringType()
    
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
    """
    License as asserted in a package metadata.
    """
    license = StringType()
    url = URIType()
    text = StringType()
    notice = StringType()

    class Options:
        fields_order = 'license', 'url', 'text', 'notice'


# Party types
#################################
party_person = 'person' 
party_project = 'project'  # often loosely defined
party_org = 'organization'  # more formally defined
PARTY_TYPES = (party_person, party_project, party_org,)


class Party(BaseModel):
    """
    A party is a person, project or organization.
    """
    type = StringType(choices=PARTY_TYPES)
    name = StringType()
    url = URLType()
    email = EmailType()

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


# FIXME: this is broken ... Debs and RPMs use file deps as an indirection and not directly package deps.
class Dependency(BaseModel):
    """
    A dependency points to a Package via a package name and a version constraint
    (such as ">= 3.4"). The version is the effective version that has been
    picked and resolved.
    """
    # package name for this dependency
    name = StringType(required=True)
    
    # The effective or concrete resolved and used version
    version = VersionType()

    # The version constraints (aka. possible versions) for this dep. 
    # The meaning is package type-specific
    version_constraint = StringType()

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
    """
    A generic related package.
    """
    # Descriptive name of the type of package:
    # RubyGem, Python Wheel, Maven Jar, etc.
    type = StringType(choices=PARTY_TYPES)

    name = StringType(required=True)
    version = VersionType()

    # the type of payload in this package. one of PAYLOADS or none
    payload_type = StringType(choices=PAYLOADS)

    class Options:
        fields_order = 'type', 'name', 'version', 'payload_type'


class Package(BaseModel):
    """
    A package base class. Override for specific pacakge behaviour. The way a
    package is created and serialized should be uniform across all Package
    types.
    """
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

    # Descriptive name of the type of package:
    # RubyGem, Python Wheel, Maven Jar, etc.
    type = StringType(required=True)

    name = StringType(required=True)
    version = VersionType()

    # primary programming language for a package type
    # i.e. RubyGems are primarily ruby, etc
    primary_language = StringType()

    # type of packaging of this Package
    packaging = StringType(choices=PACKAGINGS)

    # TODO: add os and arches!!
    
    # this is a "short" description.
    summary = StringType()
    # this is a "long" description, often several pages of text.
    description = StringType()
    # the type of payload in this package. one of PAYLOADS or none
    payload_type = StringType(choices=PAYLOADS)

    # list of Parties: authors, packager, maintainers, contributors, distributor, vendor, etc
    # FIXME: this would be simpler as a list where each Party has also a type
    authors = ListType(ModelType(Party))
    maintainers = ListType(ModelType(Party))
    contributors = ListType(ModelType(Party))
    owners = ListType(ModelType(Party))
    packagers = ListType(ModelType(Party))
    distributors = ListType(ModelType(Party))
    vendors = ListType(ModelType(Party))

    # keywords or tags
    keywords = ListType(StringType())

    # url to a reference documentation for keywords or tags (such as a Pypi or SF.net Trove map)
    # FIXME: this is a Package-class attribute
    keywords_doc_url = URLType()

    # Paths to actual metadata files for this package, if any.
    # Relative to the package root directory or archive root.
    metafile_locations = ListType(StringType())

    # URLs to remote metadata files for this package if available
    metafile_urls = ListType(URIType())

    homepage_url = URIType()
    notes = StringType()

    # one or more direct download urls, possibly in SPDX vcs url form
    # the first one is considered to be the primary
    download_urls = ListType(URIType())

    # checksums for the download
    download_sha1 = SHA1Type()
    download_sha256 = SHA256Type()
    download_md5 = MD5Type()

    # issue or bug tracker
    bug_tracking_url = URLType()

    # strings (such as email, urls, etc)
    support_contacts = ListType(StringType())

    # a URL where the code can be browsed online
    code_view_url = URIType()

    # one of git, svn, hg, etc
    vcs_tool = StringType(choices=['git', 'svn', 'hg', 'bzr', 'cvs'])
    # a URL in the SPDX form of:
    # git+https://github.com/nexb/scancode-toolkit.git
    vcs_repository = URIType()
    # a revision, branch, tag reference, etc (can also be included in the URL
    vcs_revision = StringType()

    # a top level copyright often asserted in metadata
    copyright_top_level = StringType()
    # effective copyrights as detected and eventually summarized
    copyrights = ListType(StringType())

    # as asserted licensing information
    # a list of AssertLicense objects
    asserted_licenses = ListType(ModelType(AssertedLicense))

    # List of paths legal files  (such as COPYING, NOTICE, LICENSE, README, etc.)
    # Paths are relative to the root of the package
    legal_file_locations = ListType(StringType())

    # Resolved or detected license expressions
    license_expression = StringType()
    # list of license texts
    license_texts = ListType(StringType())

    # list of notices texts
    notice_texts = ListType(StringType())

    # Map a DEPENDENCY_GROUPS group name to a list of Dependency
    # FIXME: we should instead just have a plain list where each dep contain a groups list.
    dependencies = DictType(ListType(ModelType(Dependency)), default={})

    # List of related packages and the corresponding payload.
    # For instance the SRPM of an RPM
    related_packages = ListType(ModelType(RelatedPackage))

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

    @staticmethod
    def recognize(location):
        """
        Return a Package object or None given a location to a file or directory
        pointing to a package archive, metafile or similar.
        
        Sub-classes must override to implement recognition.
        """
        raise NotImplementedError()

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


class MavenJar(JavaJar):
    metafiles = ('META-INF/**/*.pom', 'pom.xml',)
    repo_types = (repo_maven,)

    type = StringType(default='Apache Maven')


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


class NugetPackage(Package):
    metafiles = ('[Content_Types].xml', '*.nuspec',)
    filetypes = ('zip archive', 'microsoft ooxml',)
    mimetypes = ('application/zip', 'application/octet-stream',)
    extensions = ('.nupkg',)
    repo_types = (repo_nuget,)

    type = StringType(default='Nuget')
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
