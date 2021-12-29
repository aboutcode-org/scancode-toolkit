#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import logging
import sys
import warnings

import attr
import saneyaml
from commoncode import filetype
from packageurl import PackageURL

from packagedcode import models
from packagedcode.utils import combine_expressions

TRACE = False


def logger_debug(*args):
    pass


logger = logging.getLogger(__name__)

if TRACE:
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(''.join(isinstance(a, str) and a or repr(a) for a in args))

"""
Collect data from Dart pub packages.
See https://dart.dev/tools/pub/pubspec
"""

"""
TODO:
- license is only in a LICENSE file
  https://dart.dev/tools/pub/publishing#preparing-to-publish
See https://dart.dev/tools/pub/publishing#important-files

API has theses URLs:
is limited and only returns all versions of a package
- feeds https://pub.dev/feed.atom
- all packages, paginated: https://pub.dev/api/packages
- one package, all version: https://pub.dev/api/packages/painter
- one version: https://pub.dev/api/packages/painter/versions/0.3.1

See https://github.com/dart-lang/pub/blob/master/doc/repository-spec-v2.md
"""


@attr.s()
class PubspecPackage(models.Package):
    metafiles = ('pubspec.yaml', 'pubspec.lock',)
    extensions = ('.yaml', '.lock',)
    default_type = 'pubspec'
    default_primary_language = 'dart'
    default_web_baseurl = 'https://pub.dev/packages'
    default_download_baseurl = 'https://pub.dartlang.org/packages'
    default_api_baseurl = 'https://pub.dev/api/packages'

    @classmethod
    def recognize(cls, location):
        if is_pubspec_yaml(location):
            yield parse_pub(location)
        elif is_pubspec_lock(location):
            yield parse_lock(location)

    def repository_homepage_url(self, baseurl=default_web_baseurl):
        return f'{baseurl}/{self.name}/versions/{self.version}'

    def repository_download_url(self, baseurl=default_download_baseurl):
        # A URL should be in the form of:
        # https://pub.dartlang.org/packages/url_launcher/versions/6.0.9.tar.gz
        # And it may resolve to:
        # https://storage.googleapis.com/pub-packages/packages/http-0.13.2.tar.gz
        # as seen in the pub.dev web pages
        return f'{baseurl}/{self.name}/versions/{self.version}.tar.gz'

    def api_data_url(self, baseurl=default_api_baseurl):
        return f'{baseurl}/{self.name}/versions/{self.version}'

    def compute_normalized_license(self):
        return compute_normalized_license(self.declared_license)


def compute_normalized_license(declared_license, location=None):
    """
    Return a normalized license expression string detected from a list of
    declared license items.

    The specification for pub demands to have a LICENSE file side-by-side and
    nothing else. See https://dart.dev/tools/pub/publishing#preparing-to-publish
    """
    # FIXME: we need a location to find the FILE file
    # Approach:
    # Find the LICENSE file
    # detect on the text
    # combine all expressions

    if not declared_license:
        return

    detected_licenses = []

    if detected_licenses:
        return combine_expressions(detected_licenses)


def parse_pub(location, compute_normalized_license=False):
    """
    Return a PubspecPackage constructed from the pubspec.yaml file at ``location``
    or None.
    """
    if not is_pubspec_yaml(location):
        return
    with open(location) as inp:
        package_data = saneyaml.load(inp.read())

    package = build_package(package_data)
    if package and compute_normalized_license:
        package.compute_normalized_license()
    return package


def file_endswith(location, endswith):
    """
    Check if the file at ``location`` ends with ``endswith`` string or tuple.
    """
    return filetype.is_file(location) and location.endswith(endswith)


def is_pubspec_yaml(location):
    return file_endswith(location, 'pubspec.yaml')


def is_pubspec_lock(location):
    return file_endswith(location, 'pubspec.lock')


def parse_lock(location):
    """
    Yield PubspecPackages dependencies constructed from the pubspec.lock file at
    ``location``.
    """
    if not is_pubspec_lock(location):
        return

    with open(location) as inp:
        locks_data = saneyaml.load(inp.read())

    return PubspecPackage(dependencies=list(collect_locks(locks_data)))


def collect_locks(locks_data):
    """
    Yield DependentPackage from locks data

    The general form is
        packages:
          _fe_analyzer_shared:
            dependency: transitive
            description:
              name: _fe_analyzer_shared
              url: "https://pub.dartlang.org"
            source: hosted
            version: "22.0.0"
        sdks:
          dart: ">=2.12.0 <3.0.0"
    """
    # FIXME: we treat all as nno optioanl for now
    sdks = locks_data.get('sdks') or {}
    for name, version in sdks.items():
        dep = build_dep(
            name,
            version,
            scope='sdk',
            is_runtime=True,
            is_optional=False,
        )
        yield dep

    packages = locks_data.get('packages') or {}
    for name, details in packages.items():
        version = details.get('version')

        # FIXME: see  https://github.com/dart-lang/pub/blob/2a08832e0b997ff92de65571b6d79a9b9099faa0/lib/src/lock_file.dart#L344
        #     transitive, direct main, direct dev, direct overridden.
        # they do not map exactly to the pubspec scopes since transitive can be
        # either main or dev
        scope = details.get('dependency')
        if scope == 'direct dev':
            is_runtime = False
        else:
            is_runtime = True

        desc = details.get('description') or {}
        known_desc = isinstance(desc, dict)

        # issue a warning for unknown data structure
        warn = False
        if not known_desc:
            if not (isinstance(desc, str) and desc == 'flutter'):
                warn = True
        else:
            dname = desc.get('name')
            durl = desc.get('url')
            dsource = details.get('source')

            if (
                (dname and dname != name)
                or (durl and durl != 'https://pub.dartlang.org')
                or (dsource and dsource not in ['hosted', 'sdk', ])
            ):
                warn = True

        if warn:
            warnings.warn(
                f'Dart pubspec.locks with unsupported external repo '
                f'description or source: {details}',
                stacklevel=1,
            )

        dep = build_dep(
            name,
            version,
            scope=scope,
            is_runtime=is_runtime,
            is_optional=False,
        )
        yield dep


def collect_deps(data, dependency_field_name, is_runtime=True, is_optional=False):
    """
    Yield DependentPackage found in the ``dependency_field_name`` of ``data``.
    Use is_runtime and is_optional in created DependentPackage.

    The shape of the data is:
        dependencies:
          path: 1.7.0
          meta: ^1.2.4
          yaml: ^3.1.0

        environment:
          sdk: '>=2.12.0 <3.0.0'
    """
    # TODO: these can be more complex for SDKs
    # https://dart.dev/tools/pub/dependencies#dependency-sources
    dependencies = data.get(dependency_field_name) or {}
    for name, version in dependencies.items():
        dep = build_dep(
            name,
            version,
            scope=dependency_field_name,
            is_runtime=is_runtime,
            is_optional=is_optional,
        )
        yield dep


def build_dep(name, version, scope, is_runtime=True, is_optional=False):
    """
    Return DependentPackage from the provided data.
    """

    # TODO: these can be more complex for SDKs
    # https://dart.dev/tools/pub/dependencies#dependency-sources

    if isinstance(version, dict) and 'sdk' in version:
        # {'sdk': 'flutter'} type of deps....
        # which is a wart that we keep as a requiremnet
        version = ', '.join(': '.join([k, str(v)]) for k, v in version.items())

    if version.replace('.', '').isdigit():
        # version is pinned exactly if it is only made of dots and digits
        purl = PackageURL(type='pubspec', name=name, version=version)
        is_resolved = True
    else:
        purl = PackageURL(type='pubspec', name=name)
        is_resolved = False

    dep = models.DependentPackage(
        purl=purl.to_string(),
        requirement=version,
        scope=scope,
        is_runtime=is_runtime,
        is_optional=is_optional,
        is_resolved=is_resolved,
    )
    return dep


def build_package(pubspec_data):
    """
    Return a package object from a package data mapping or None
    """
    name = pubspec_data.get('name')
    version = pubspec_data.get('version')
    description = pubspec_data.get('description')
    homepage_url = pubspec_data.get('homepage')
    declared_license = pubspec_data.get('license')
    vcs_url = pubspec_data.get('repository')
    download_url = pubspec_data.get('archive_url')

    # Author and authors are deprecated
    authors = []
    author = pubspec_data.get('author')
    if author:
        authors.append(author)
    authors.extend(pubspec_data.get('authors') or [])

    parties = []
    for auth  in authors:
        parties.append(models.Party(
            type=models.party_person,
            role='author',
            name=auth
        ))

    package_dependencies = []
    dependencies = collect_deps(
        pubspec_data,
        'dependencies',
        is_runtime=True,
        is_optional=False,
    )
    package_dependencies.extend(dependencies)

    dev_dependencies = collect_deps(
        pubspec_data,
        'dev_dependencies',
        is_runtime=False,
        is_optional=True,
    )
    package_dependencies.extend(dev_dependencies)

    env_dependencies = collect_deps(
        pubspec_data,
        'environment',
        is_runtime=True,
        is_optional=False,
    )
    package_dependencies.extend(env_dependencies)

    extra_data = {}

    def add_to_extra_if_present(_key):
        _value = pubspec_data.get(_key)
        if _value:
            extra_data[_key] = _value

    add_to_extra_if_present('issue_tracker')
    add_to_extra_if_present('documentation')
    add_to_extra_if_present('dependencies_overrides')
    add_to_extra_if_present('executables')
    add_to_extra_if_present('publish_to')

    package = PubspecPackage(
        name=name,
        version=version,
        vcs_url=vcs_url,
        description=description,
        declared_license=declared_license,
        parties=parties,
        homepage_url=homepage_url,
        dependencies=package_dependencies,
        extra_data=extra_data,
    )

    if not download_url:
        package.download_url = package.repository_download_url()

    return package

