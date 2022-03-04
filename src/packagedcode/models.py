#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import fnmatch
import logging
import os
import sys

import attr
from packageurl import normalize_qualifiers
from packageurl import PackageURL

from commoncode.datautils import choices
from commoncode.datautils import Boolean
from commoncode.datautils import Date
from commoncode.datautils import Integer
from commoncode.datautils import List
from commoncode.datautils import Mapping
from commoncode.datautils import String
from commoncode.datautils import TriBoolean

from commoncode import filetype
from commoncode.fileutils import file_name
from commoncode.fileutils import splitext_name
from typecode import contenttype


"""
Data models for package information and dependencies, and also data models
for package data for abstracting the differences existing between
package formats and tools.

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

1. package data information collected in a "manifest" or similar at a file level
2. packages at the codebase level, where a package contains
   one or more package data, and files for that package.

The second requires the first to be computed.

These are case classes to extend:

- PackageData:
    Base class with shared package attributes and methods.
- PackageDataFile:
    Mixin class that represents a specific package manifest file.
- Package:
    Mixin class that represents a package that's constructed from one or more
    package data. It also tracks package files. Basically a package instance.

Here is an example of the classes that would need to exist to support a new fictitious
package type or ecosystem `dummy`.

- DummyPackageData(PackageData):
    This class provides type wide defaults and basic implementation for type specific methods.
- DummyManifest(DummyPackageData, PackageDataFile) or DummyLockFile(DummyPackageData, PackageDataFile):
    This class provides methods to recognize and parse a package manifest file format.
- DummyPackage(DummyPackageData, Package):
    This class provides methods to create package instances for one or more manifests and to
    collect package file paths.
"""

SCANCODE_DEBUG_PACKAGE_API = os.environ.get('SCANCODE_DEBUG_PACKAGE_API', False)

TRACE = False or SCANCODE_DEBUG_PACKAGE_API
TRACE_MERGING = True or SCANCODE_DEBUG_PACKAGE_API

def logger_debug(*args):
    pass

logger = logging.getLogger(__name__)

if TRACE:
    import logging

    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, str) and a or repr(a) for a in args))

    logger_debug = print


class BaseModel(object):
    """
    Base class for all package models.
    """

    def to_dict(self, **kwargs):
        """
        Return an dict of primitive Python types.
        """
        return attr.asdict(self)

    @classmethod
    def create(cls, **kwargs):
        """
        Return an object built from ``kwargs``. Always ignore unknown attributes
        provided in ``kwargs`` that do not exist as declared attr fields in
        ``cls``.
        """
        known_attr = cls.fields()
        kwargs = {k: v for k, v in kwargs.items() if k in known_attr}
        return cls(**kwargs)


    @classmethod
    def fields(cls):
        """
        Return a list of field names defined on this model.
        """
        return list(attr.fields_dict(cls))


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
        repr=True,
        validator=choices(PARTY_TYPES),
        label='party type',
        help='the type of this party: One of: '
            +', '.join(p for p in PARTY_TYPES if p))

    role = String(
        repr=True,
        label='party role',
        help='A role for this party. Something such as author, '
             'maintainer, contributor, owner, packager, distributor, '
             'vendor, developer, owner, etc.')

    name = String(
        repr=True,
        label='name',
        help='Name of this party.')

    email = String(
        repr=True,
        label='email',
        help='Email for this party.')

    url = String(
        repr=True,
        label='url',
        help='URL to a primary web page for this party.')


@attr.s()
class BasePackageData(BaseModel):
    """
    A base identifiable package object using discrete identifying attributes as
    specified here https://github.com/package-url/purl-spec.
    """

    # class-level attributes used to recognize a package
    filetypes = tuple()
    mimetypes = tuple()
    extensions = tuple()

    # list of known metafiles for a package type
    file_patterns = tuple()

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

    # TODO: add description of the Package type for info
    # type_description = None

    type = String(
        repr=True,
        label='package type',
        help='Optional. A short code to identify what is the type of this '
             'package. For instance gem for a Rubygem, docker for container, '
             'pypi for Python Wheel or Egg, maven for a Maven Jar, '
             'deb for a Debian package, etc.')

    namespace = String(
        repr=True,
        label='package namespace',
        help='Optional namespace for this package.')

    name = String(
        repr=True,
        label='package name',
        help='Name of the package.')

    version = String(
        repr=True,
        label='package version',
        help='Optional version of the package as a string.')

    qualifiers = Mapping(
        default=None,
        value_type=str,
        converter=lambda v: normalize_qualifiers(v, encode=False),
        label='package qualifiers',
        help='Optional mapping of key=value pairs qualifiers for this package')

    subpath = String(
        label='extra package subpath',
        help='Optional extra subpath inside a package and relative to the root '
             'of this package')

    def __attrs_post_init__(self, *args, **kwargs):
        if not self.type and hasattr(self, 'default_type'):
            self.type = self.default_type

    @property
    def purl(self):
        """
        Return a compact purl package URL string.
        """
        if not self.name:
            return
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

    def set_purl(self, package_url):
        """
        Update this Package object with the `package_url` purl string or
        PackageURL attributes.
        """
        if not package_url:
            return

        if not isinstance(package_url, PackageURL):
            package_url = PackageURL.from_string(package_url)

        attribs = ['type', 'namespace', 'name', 'version', 'qualifiers', 'subpath']
        for att in attribs:
            self_val = getattr(self, att)
            purl_val = getattr(package_url, att)
            if not self_val and purl_val:
                setattr(self, att, purl_val)

    def to_dict(self, **kwargs):
        """
        Return an dict of primitive Python types.
        """
        mapping = attr.asdict(self)
        if self.name:
            mapping['purl'] = self.purl
            mapping['repository_homepage_url'] = self.repository_homepage_url()
            mapping['repository_download_url'] = self.repository_download_url()
            mapping['api_data_url'] = self.api_data_url()
        else:
            mapping['purl'] = None
            mapping['repository_homepage_url'] = None
            mapping['repository_download_url'] = None
            mapping['api_data_url'] = None

        if self.qualifiers:
            mapping['qualifiers'] = normalize_qualifiers(
                qualifiers=self.qualifiers,
                encode=False,
            )
        return mapping

    @classmethod
    def create(cls, **kwargs):
        """
        Return a Package built from ``kwargs``. Always ignore unknown attributes
        provided in ``kwargs`` that do not exist as declared attr fields in
        ``cls``.
        """
        from packagedcode import get_package_class
        type_cls = get_package_class(kwargs, default=cls)
        return super(BasePackageData, type_cls).create(**kwargs)


@attr.s()
class DependentPackage(BaseModel):
    """
    An identifiable dependent package package object.
    """

    purl = String(
        repr=True,
        label='Dependent package URL',
        help='A compact purl package URL. Typically when there is an '
             'unresolved requirement, there is no version. '
             'If the dependency is resolved, the version should be added to '
             'the purl')

    # ToDo: rename to `extracted_requirement`  * as found in the package manifest *
    requirement = String(
        repr=True,
        label='dependent package version requirement',
        help='A string defining version(s)requirements. Package-type specific.')

    # ToDo: add `vers` See https://github.com/nexB/univers/blob/main/src/univers/version_range.py

    scope = String(
        repr=True,
        label='dependency scope',
        help='The scope of this dependency, such as runtime, install, etc. '
        'This is package-type specific and is the original scope string.')

    is_runtime = Boolean(
        default=True,
        label='is runtime flag',
        help='True if this dependency is a runtime dependency.')

    is_optional = Boolean(
        default=False,
        label='is optional flag',
        help='True if this dependency is an optional dependency')

    is_resolved = Boolean(
        default=False,
        label='is resolved flag',
        help='True if this dependency version requirement has '
             'been resolved and this dependency url points to an '
             'exact version.')

    #ToDo: add `resolved_package` -> (PackageData)


@attr.s
class Dependency(DependentPackage):

    dependency_uuid = String(
        label='Dependency instance UUID',
        help='A unique ID for dependency instances in a codebase scan.'
             'Consists of a pURL and an UUID field as a pURL qualifier.'
    )

    for_package = String(
        label='A Package UUID',
        help='The UUID of the package instance to which this dependency file belongs'
    )

    lockfile = String(
        label='path to a lockfile',
        help='A path string from where this dependency instance was created'
             'Consists of a pURL and an UUID field as a pURL qualifier.'
    )


@attr.s()
class PackageFile(BaseModel):
    """
    A file that belongs to a package.
    """

    path = String(
        label='Path of this installed file',
        help='The path of this installed file either relative to a rootfs '
             '(typical for system packages) or a path in this scan (typical '
             'for application packages).',
        repr=True,
    )

    size = Integer(
        label='file size',
        help='size of the file in bytes')

    sha1 = String(
        label='SHA1 checksum',
        help='SHA1 checksum for this file in hexadecimal')

    md5 = String(
        label='MD5 checksum',
        help='MD5 checksum for this file in hexadecimal')

    sha256 = String(
        label='SHA256 checksum',
        help='SHA256 checksum for this file in hexadecimal')

    sha512 = String(
        label='SHA512 checksum',
        help='SHA512 checksum for this file in hexadecimal')


@attr.s()
class PackageData(BasePackageData):
    """
    A package object as represented by either data from one of its different types of
    package data or that of a package instance created from one or more of these
    package data, and files for that package.
    """

    # Optional. Public default type for a package class.
    default_primary_language = None

    primary_language = String(
        label='Primary programming language',
        help='Primary programming language',)

    description = String(
        label='Description',
        help='Description for this package. '
             'By convention the first should be a summary when available.')

    release_date = Date(
        label='release date',
        help='Release date of the package')

    parties = List(
        item_type=Party,
        label='parties',
        help='A list of parties such as a person, project or organization.')

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

    size = Integer(
        default=None,
        label='download size',
        help='size of the package download in bytes')

    sha1 = String(
        label='SHA1 checksum',
        help='SHA1 checksum for this download in hexadecimal')

    md5 = String(
        label='MD5 checksum',
        help='MD5 checksum for this download in hexadecimal')

    sha256 = String(
        label='SHA256 checksum',
        help='SHA256 checksum for this download in hexadecimal')

    sha512 = String(
        label='SHA512 checksum',
        help='SHA512 checksum for this download in hexadecimal')

    bug_tracking_url = String(
        label='bug tracking URL',
        help='URL to the issue or bug tracker for this package')

    code_view_url = String(
        label='code view URL',
        help='a URL where the code can be browsed online')

    vcs_url = String(
        help='a URL to the VCS repository in the SPDX form of: '
             'https://github.com/nexb/scancode-toolkit.git@405aaa4b3 '
              'See SPDX specification "Package Download Location" '
              'at https://spdx.org/spdx-specification-21-web-version#h.49x2ik5 ')

    copyright = String(
        label='Copyright',
        help='Copyright statements for this package. Typically one per line.')

    license_expression = String(
        label='license expression',
        help='The license expression for this package typically derived '
             'from its declared license or from some other type-specific '
             'routine or convention.')

    declared_license = String(
        label='declared license',
        help='The declared license mention, tag or text as found in a '
             'package manifest. This can be a string, a list or dict of '
             'strings possibly nested, as found originally in the manifest.')

    notice_text = String(
        label='notice text',
        help='A notice text for this package.')

    root_path = String(
        label='package root path',
        help='The path to the root of the package documented in this manifest '
             'if any, such as a Maven .pom or a npm package.json parent directory.')

    contains_source_code = TriBoolean(
        label='contains source code',
        help='Flag set to True if this package contains its own source code, None '
             'if this is unknown, False if not.')

    source_packages = List(
        item_type=String,
        label='List of related source code packages',
        help='A list of related  source code Package URLs (aka. "purl") for '
             'this package. For instance an SRPM is the "source package" for a '
             'binary RPM.')

    installed_files = List(
        item_type=PackageFile,
        label='installed files',
        help='List of files installed by this package.')

    extra_data = Mapping(
        label='extra data',
        help='A mapping of arbitrary extra Package data.')

    def __attrs_post_init__(self, *args, **kwargs):
        if not self.type and hasattr(self, 'default_type'):
            self.type = self.default_type

        if not self.primary_language and hasattr(self, 'default_primary_language'):
            self.primary_language = self.default_primary_language

    @classmethod
    def get_package_resources(cls, package_root, codebase):
        """
        Yield the Resources of a Package starting from `package_root`
        """
        if not cls.is_ignored_package_resource(package_root, codebase):
            yield package_root
        for resource in package_root.walk(codebase, topdown=True, ignored=cls.is_ignored_package_resource):
            yield resource

    @classmethod
    def ignore_resource(cls, resource, codebase):
        """
        Return True if `resource` should be ignored.
        """
        return False

    @staticmethod
    def is_ignored_package_resource(resource, codebase):
        from packagedcode import PACKAGE_DATA_CLASSES
        return any(pt.ignore_resource(resource, codebase) for pt in PACKAGE_DATA_CLASSES)

    def compute_normalized_license(self):
        """
        Return a normalized license_expression string using the declared_license
        field. Return 'unknown' if there is a declared license but it cannot be
        detected and return None if there is no declared license

        Subclasses can override to handle specifics such as supporting specific
        license ids and conventions.
        """
        return compute_normalized_license(self.declared_license)

    @classmethod
    def extra_key_files(cls):
        """
        Return a list of extra key file paths (or path glob patterns) beyond
        standard, well known key files for this Package. List items are strings
        that are either paths or glob patterns and are relative to the package
        root.

        Knowing if a file is a "key-file" file is important for classification
        and summarization. For instance, a JAR can have key files that are not
        top level under the META-INF directory. Or a .gem archive contains a
        metadata.gz file.

        Sub-classes can implement as needed.
        """
        return []

    @classmethod
    def extra_root_dirs(cls):
        """
        Return a list of extra package root-like directory paths (or path glob
        patterns) that should be considered to determine if a files is a top
        level file or not. List items are strings that are either paths or glob
        patterns and are relative to the package root.

        Knowing if a file is a "top-level" file is important for classification
        and summarization.

        Sub-classes can implement as needed.
        """
        return []

    def to_dict(self, _detailed=False, **kwargs):
        data = super().to_dict(**kwargs)
        if _detailed:
            data['installed_files'] = [
                istf.to_dict() for istf in (self.installed_files or [])
            ]
        else:
            data.pop('installed_files', None)
        return data


def compute_normalized_license(declared_license, expression_symbols=None):
    """
    Return a normalized license_expression string from the ``declared_license``.
    Return 'unknown' if there is a declared license but it cannot be detected
    (including on errors) and return None if there is no declared license.

    Use the ``expression_symbols`` mapping of {lowered key: LicenseSymbol}
    if provided. Otherwise use the standard SPDX license symbols.
    """

    if not declared_license:
        return

    from packagedcode import licensing
    try:
        return licensing.get_normalized_expression(
            query_string=declared_license,
            expression_symbols=expression_symbols
        )
    except Exception:
        # FIXME: add logging
        # we never fail just for this
        return 'unknown'


@attr.s
class PackageDataFile:
    """
    A mixin for package manifests, lockfiles and other package data files
    that can be recognized.

    When creating a new package data, a class should be created that extends
    both PackageDataFile and PackageData.
    """

    dependencies = List(
        item_type=DependentPackage,
        label='dependencies',
        help='A list of DependentPackage for this package. ')


    # class-level attributes used to recognize a package
    filetypes = tuple()
    mimetypes = tuple()
    extensions = tuple()

    # list of known file_patterns for a package manifest type
    file_patterns = tuple()

    @property
    def package_data_type(self):
        """
        A tuple unique across package data, created from the default package type
        and the manifest type.
        """
        return self.default_type, self.manifest_type()

    @classmethod
    def manifest_type(cls):
        return f"{cls.__module__}.{cls.__qualname__}"

    @classmethod
    def is_package_data_file(cls, location):
        """
        Return True if the file at ``location`` is likely a manifest/lockfile/other
        package data file of this type.

        Sub-classes should override to implement their own package data file recognition.
        """
        if not filetype.is_file(location):
            return

        filename = file_name(location)

        file_patterns = cls.file_patterns
        if any(fnmatch.fnmatchcase(filename, metaf) for metaf in file_patterns):
            return True

        T = contenttype.get_type(location)
        ftype = T.filetype_file.lower()
        mtype = T.mimetype_file

        _base_name, extension = splitext_name(location, is_file=True)
        extension = extension.lower()

        if TRACE:
            logger_debug(
                'is_manifest: ftype:', ftype, 'mtype:', mtype,
                'pygtype:', T.filetype_pygment,
                'fname:', filename, 'ext:', extension,
            )

        type_matched = False
        if cls.filetypes:
            type_matched = any(t in ftype for t in cls.filetypes)

        mime_matched = False
        if cls.mimetypes:
            mime_matched = any(m in mtype for m in cls.mimetypes)

        extension_matched = False
        extensions = cls.extensions
        if extensions:
            extensions = (e.lower() for e in extensions)
            extension_matched = any(
                fnmatch.fnmatchcase(extension, ext_pat)
                for ext_pat in extensions
            )

        if type_matched and mime_matched and extension_matched:
            return True

    @classmethod
    def recognize(cls, location):
        """
        Yield one or more PackageData objects given a file at `location`
        pointing to a package archive, manifest, lockfile or other package data.

        Sub-classes should override to implement their own package recognition and creation.
 
        This should be called on the file at `location` only if `is_manifest` function
        of the same class returns True.
        """
        raise NotImplementedError


@attr.s()
class Package:
    """
    A package mixin as represented by its package data, files and data
    from its package data. Here package obviously represents a package
    instance.

    Subclasses must extend a Package subclass for a given ecosystem.
    """

    package_uuid = String(
        label='Package instance UUID',
        help='A unique ID for package instances in a codebase scan.'
             'Consists of a pURL and an UUID field as a pURL qualifier.'
    )

    package_data_files = List(
        item_type=String,
        label='Package data paths',
        help='List of package data file paths for this package'
    )

    files = List(
        item_type=PackageFile,
        label='Provided files',
        help='List of files provided by this package.'
    )

    @property
    def ignore_paths(self):
        """
        Paths to ignore when looking for other package_data files.

        Override the default empty list by defining for each package ecosystems specifically.
        """
        return []

    def get_package_data(self):
        """
        Returns a mapping of package data attributes and corresponding values.
        """
        mapping = self.to_dict()

        # Removes Package specific attributes
        for attribute in ('package_uuid', 'package_data_files', 'files'):
            mapping.pop(attribute, None)

        # Remove attributes which are BasePackageData functions
        for attribute in ('repository_homepage_url', 'repository_download_url', 'api_data_url'):
            mapping.pop(attribute, None)

        return mapping

    def populate_package_data(self, package_data_by_path, uuid):
        """
        Create a package instance object from one or multiple package data.
        """
        for path, package_data in package_data_by_path.items():
            if TRACE:
                logger.debug('Merging package manifest data for: {}'.format(path))
                logger.debug('package manifest data: {}'.format(repr(package_data)))
            self.package_data_files.append(path)
            self.update(package_data.copy())

        self.package_data_files = tuple(self.package_data_files)

        # Set `package_uuid` as pURL for the package + it's uuid as a qualifier
        # in the pURL string
        try:
            purl_with_uuid = PackageURL.from_string(self.purl)
        except ValueError:
            if TRACE:
                logger.debug("Couldn't create purl for: {}".format(path))
            return

        purl_with_uuid.qualifiers["uuid"] = str(uuid)
        self.package_uuid = purl_with_uuid.to_string()

    def get_package_files(self, resource, codebase):
        """
        Return a list of all the file paths for a package instance.
 
        Sub-classes should override to implement their own package files finding methods.
        """
        files = []

        if codebase.has_single_resource:
            files.append(resource.path)
            return files

        parent = resource.parent(codebase)

        for resource in parent.walk(codebase):
            if resource.is_dir:
                continue

            files.append(resource.path)
        
        return files

    def get_other_package_data(self, resource, codebase):
        """
        Return a dictionary of other package data by their paths for a given package instance.

        Sub-classes can override to implement their own package manifest finding methods.
        """
        package_data_by_path = {}

        if codebase.has_single_resource:
            return package_data_by_path

        parent = resource.parent(codebase)

        paths_to_ignore = self.ignore_paths

        for resource in parent.walk(codebase):
            if resource.is_dir:
                continue

            if paths_to_ignore:
                if any(
                    path in resource.path
                    for path in paths_to_ignore
                ):
                    continue

            filename = file_name(resource.location)
            file_patterns = self.get_file_patterns(manifests=self.manifests)
            if any(fnmatch.fnmatchcase(filename, pattern) for pattern in file_patterns):
                if not resource.package_data:
                    continue # Raise Exception(?)

                #ToDo: Implement for multiple package data per path
                package_data_by_path[resource.path] = resource.package_data[0]

        return package_data_by_path
    
    def get_file_patterns(self, manifests):
        """
        Return a list of all `file_patterns` for all the PackageData classes
        in `manifests`.
        """
        manifest_file_patterns = []
        for manifest in manifests:
            manifest_file_patterns.extend(manifest.file_patterns)
        
        return manifest_file_patterns

    def update(self, package_data, replace=False):
        """
        Update the Package object with data from the `package_data`
        object.
        When an `package_instance` field has no value one side and and the
        `package_data` field has a value, the `package_instance` field is always
        set to this value.
        If `replace` is True and a field has a value on both sides, then
        package_instance field value will be replaced by the package_data
        field value. Otherwise if `replace` is False, the package_instance
        field value is left unchanged in this case.
        """
        existing_mapping = self.get_package_data()

        # Remove PackageData specific attributes
        for attribute in ['root_path']:
            package_data.pop(attribute, None)
            existing_mapping.pop(attribute, None)

        for existing_field, existing_value in existing_mapping.items():
            new_value = package_data[existing_field]
            if TRACE_MERGING:
                logger.debug(
                    '\n'.join([
                        'existing_field:', repr(existing_field),
                        '    existing_value:', repr(existing_value),
                        '    new_value:', repr(new_value)])
                )

            # FIXME: handle Booleans???

            # These fields has to be same across the package_data
            if existing_field in ('name', 'version', 'type', 'primary_language'):
                if existing_value and new_value and existing_value != new_value:
                    raise Exception(
                        '\n'.join([
                            'Mismatched {}:'.format(existing_field),
                            '    existing_value: {}'.format(existing_value),
                            '    new_value: {}'.format(new_value)
                        ])
                    )

            if not new_value:
                if TRACE_MERGING:
                    logger.debug('  No new value for {}: skipping'.format(existing_field))
                continue

            if not existing_value or replace:
                if TRACE_MERGING and not existing_value:
                    logger.debug(
                        '  No existing value: set to new: {}'.format(new_value))

                if TRACE_MERGING and replace:
                    logger.debug(
                        '  Existing value and replace: set to new: {}'.format(new_value))

                if existing_field == 'parties':
                    # If `existing_field` is `parties`, then we update the `Party` table
                    parties = new_value
                    parties_new = []

                    for party in parties:
                        party_new = Party(
                            type=party['type'],
                            role=party['role'],
                            name=party['name'],
                            email=party['email'],
                            url=party['url'],
                        )
                        parties_new.append(party_new)

                    if replace:
                        setattr(self, existing_field, parties_new)
                    else:
                        existing_value.extend(parties_new)
                        setattr(self, existing_field, existing_value)

                elif existing_field == 'dependencies':
                    # If `existing_field` is `dependencies`, then we update the `DependentPackage` table
                    dependencies = new_value
                    deps_new = []

                    for dependency in dependencies:
                        dep_new = DependentPackage(
                            purl=dependency['purl'],
                            requirement=dependency['requirement'],
                            scope=dependency['scope'],
                            is_runtime=dependency['is_runtime'],
                            is_optional=dependency['is_optional'],
                            is_resolved=dependency['is_resolved'],
                        )
                        deps_new.append(dep_new)

                    if replace:
                        setattr(self, existing_field, deps_new)
                    else:
                        existing_value.extend(deps_new)
                        setattr(self, existing_field, existing_value)

                    if TRACE_MERGING:
                        logger.debug("Set value to self: {} at {}".format(new_value, existing_field))
                        logger.debug("Set value to self: types: {} at {}".format(type(new_value), type(existing_field)))

                elif existing_field == 'purl':
                    self.set_purl(package_url=new_value)

                else:
                    # If `existing_field` is not `parties` or `dependencies`, then the
                    # `existing_field` is a regular field on the Package model and can
                    # be updated normally.
                    if TRACE_MERGING:
                        logger.debug("Set value to self: {} at {}".format(new_value, existing_field))
                        logger.debug("Set value to self: types: {} at {}".format(type(new_value), type(existing_field)))  
                    setattr(self, existing_field, new_value)

            if existing_value and new_value and existing_value != new_value:
                # ToDo: What to do when conflicting values are present
                # license_expression: do AND?
                if TRACE_MERGING:
                    logger.debug("Value mismatch between new and existing: ")  
                    logger.debug(
                        '\n'.join([
                            'existing_field:', repr(existing_field),
                            '    existing_value:', repr(existing_value),
                            '    new_value:', repr(new_value)])
                    )              

            if TRACE_MERGING:
                logger.debug('  Nothing done')


# Package types
# NOTE: this is somewhat redundant with extractcode archive handlers
# yet the purpose and semantics are rather different here


@attr.s()
class JavaJar(PackageData, PackageDataFile):
    file_patterns = ('META-INF/MANIFEST.MF',)
    extensions = ('.jar',)
    filetypes = ('java archive ', 'zip archive',)
    mimetypes = ('application/java-archive', 'application/zip',)
    default_type = 'jar'
    default_primary_language = 'Java'


@attr.s()
class JavaWar(PackageData, PackageDataFile):
    file_patterns = ('WEB-INF/web.xml',)
    extensions = ('.war',)
    filetypes = ('java archive ', 'zip archive',)
    mimetypes = ('application/java-archive', 'application/zip')
    default_type = 'war'
    default_primary_language = 'Java'


@attr.s()
class JavaEar(PackageData, PackageDataFile):
    file_patterns = ('META-INF/application.xml', 'META-INF/ejb-jar.xml')
    extensions = ('.ear',)
    filetypes = ('java archive ', 'zip archive',)
    mimetypes = ('application/java-archive', 'application/zip')
    default_type = 'ear'
    default_primary_language = 'Java'


@attr.s()
class Axis2Mar(PackageData, PackageDataFile):
    """Apache Axis2 module"""
    file_patterns = ('META-INF/module.xml',)
    extensions = ('.mar',)
    filetypes = ('java archive ', 'zip archive',)
    mimetypes = ('application/java-archive', 'application/zip')
    default_type = 'axis2'
    default_primary_language = 'Java'


@attr.s()
class JBossSar(PackageData, PackageDataFile):
    file_patterns = ('META-INF/jboss-service.xml',)
    extensions = ('.sar',)
    filetypes = ('java archive ', 'zip archive',)
    mimetypes = ('application/java-archive', 'application/zip')
    default_type = 'jboss'
    default_primary_language = 'Java'


@attr.s()
class MeteorPackage(PackageData, PackageDataFile):
    file_patterns = ('package.js',)
    default_type = 'meteor'
    default_primary_language = 'JavaScript'


@attr.s()
class CpanModule(PackageData, PackageDataFile):
    file_patterns = (
        '*.pod',
        # TODO: .pm is not a package manifest
        '*.pm',
        'MANIFEST',
        'Makefile.PL',
        'META.yml',
        'META.json',
        '*.meta',
        'dist.ini',)
    # TODO: refine me
    extensions = ('.tar.gz',)
    default_type = 'cpan'
    default_primary_language = 'Perl'


# TODO: refine me: Go packages are a mess but something is emerging
# TODO: move to and use godeps.py
@attr.s()
class Godep(PackageData, PackageDataFile):
    file_patterns = ('Godeps',)
    default_type = 'golang'
    default_primary_language = 'Go'


@attr.s()
class AndroidApp(PackageData, PackageDataFile):
    filetypes = ('zip archive',)
    mimetypes = ('application/zip',)
    extensions = ('.apk',)
    default_type = 'android'
    default_primary_language = 'Java'


# see http://tools.android.com/tech-docs/new-build-system/aar-formats
@attr.s()
class AndroidLibrary(PackageData, PackageDataFile):
    filetypes = ('zip archive',)
    mimetypes = ('application/zip',)
    # note: Apache Axis also uses AAR extensions for plain Jars.
    # this could be decided based on internal structure
    extensions = ('.aar',)
    default_type = 'android-lib'
    default_primary_language = 'Java'


@attr.s()
class MozillaExtension(PackageData, PackageDataFile):
    filetypes = ('zip archive',)
    mimetypes = ('application/zip',)
    extensions = ('.xpi',)
    default_type = 'mozilla'
    default_primary_language = 'JavaScript'


@attr.s()
class ChromeExtension(PackageData, PackageDataFile):
    filetypes = ('data',)
    mimetypes = ('application/octet-stream',)
    extensions = ('.crx',)
    default_type = 'chrome'
    default_primary_language = 'JavaScript'


@attr.s()
class IOSApp(PackageData, PackageDataFile):
    filetypes = ('zip archive',)
    mimetypes = ('application/zip',)
    extensions = ('.ipa',)
    default_type = 'ios'
    default_primary_language = 'Objective-C'


@attr.s()
class CabPackage(PackageData, PackageDataFile):
    filetypes = ('microsoft cabinet',)
    mimetypes = ('application/vnd.ms-cab-compressed',)
    extensions = ('.cab',)
    default_type = 'cab'


@attr.s()
class InstallShieldPackage(PackageData, PackageDataFile):
    filetypes = ('installshield',)
    mimetypes = ('application/x-dosexec',)
    extensions = ('.exe',)
    default_type = 'installshield'


@attr.s()
class NSISInstallerPackage(PackageData, PackageDataFile):
    filetypes = ('nullsoft installer',)
    mimetypes = ('application/x-dosexec',)
    extensions = ('.exe',)
    default_type = 'nsis'


@attr.s()
class SharPackage(PackageData, PackageDataFile):
    filetypes = ('posix shell script',)
    mimetypes = ('text/x-shellscript',)
    extensions = ('.sha', '.shar', '.bin',)
    default_type = 'shar'


@attr.s()
class AppleDmgPackage(PackageData, PackageDataFile):
    filetypes = ('zlib compressed',)
    mimetypes = ('application/zlib',)
    extensions = ('.dmg', '.sparseimage',)
    default_type = 'dmg'


@attr.s()
class IsoImagePackage(PackageData, PackageDataFile):
    filetypes = ('iso 9660 cd-rom', 'high sierra cd-rom',)
    mimetypes = ('application/x-iso9660-image',)
    extensions = ('.iso', '.udf', '.img',)
    default_type = 'iso'


@attr.s()
class SquashfsPackage(PackageData, PackageDataFile):
    filetypes = ('squashfs',)
    default_type = 'squashfs'

# TODO: Add VM images formats(VMDK, OVA, OVF, VDI, etc) and Docker/other containers
