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
    metafiles = ('pubspec.yaml',)
    extensions = ('.yaml',)
    default_type = 'pubspec'
    default_primary_language = 'dart'
    default_web_baseurl = 'https://pub.dev/packages'
    default_download_baseurl = 'https://pub.dartlang.org/packages'
    default_api_baseurl = 'https://pub.dev/api/packages'

    @classmethod
    def recognize(cls, location):
        yield parse_pub(location)

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
    if not is_pubspec(location):
        return
    with open(location) as inp:
        package_data = saneyaml.load(inp.read())

    package = build_package(package_data)
    if package and compute_normalized_license:
        package.compute_normalized_license()
    return package


def is_pubspec(location):
    """
    Check if the file is a yaml file or not
    """
    return filetype.is_file(location) and location.endswith('pubspec.yaml')


def collect_deps(data, dependency_field_name, is_runtime=True, is_optional=False):
    """
    Yield DependentPackage found in the ``dependency_field_name`` of ``data``
    """

    # TODO: these can be more complex for SDKs
    # https://dart.dev/tools/pub/dependencies#dependency-sources

    dependencies = data.get(dependency_field_name) or {}
    for name, version in dependencies.items():
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

        yield models.DependentPackage(
            purl=purl.to_string(),
            requirement=version,
            scope=dependency_field_name,
            is_runtime=is_runtime,
            is_optional=is_optional,
            is_resolved=is_resolved,
        )


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

