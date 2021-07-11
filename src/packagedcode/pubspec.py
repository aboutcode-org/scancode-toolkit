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

- Deps need to be fleshed out

API is limited and only returns all versions of a package
    See https://pub.dev/feed.atom
    See https://github.com/dart-lang/pub/blob/master/doc/repository-spec-v2.md
    See https://dart.dev/tools/pub/publishing#important-files
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
        yield parse(location)

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
        return f'{baseurl}/{self.name}'

    def compute_normalized_license(self):
        return compute_normalized_license(self.declared_license)


def compute_normalized_license(declared_license, location):
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


def parse(location):
    """
    Return a PubspecPackage constructed from the pubspec.yaml file at ``location``
    or None.
    """
    if not is_pubspec(location):
        return
    with open(location) as inp:
        package_data = saneyaml.load(inp.read())
    return build_package(package_data)


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
        purl = PackageURL(type='pubspec', name=name)
        if version.replace('.', '').isdigit():
            # version is pinned exactly
            purl.version = version

        yield models.DependentPackage(
            purl=purl.to_string(),
            requirement=version,
            scope=dependency_field_name,
            is_runtime=is_runtime,
            is_optional=is_runtime,
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

    # TODO: use these in extra data?
    # issue_tracker_url = pubspec_data.get('issue_tracker')
    # documentation_url = pubspec_data.get('documentation')

    # Author and authors are deprecated
    # author = pubspec_data.get('author')
    # authors = pubspec_data.get('authors') or []

    # TODO: this is some kind of SDK dep
    # environment = pubspec_data.get('environment')

    # FIXME: what to do with these?
    # dependencies_overrides = pubspec_get('dependencies_overrides')

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

    package = PubspecPackage(
        name=name,
        version=version,
        vcs_url=vcs_url,
        description=description,
        declared_license=declared_license,
        homepage_url=homepage_url,
        dependencies=package_dependencies,
    )
    return package

