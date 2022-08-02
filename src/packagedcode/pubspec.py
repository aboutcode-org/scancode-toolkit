#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import warnings

import saneyaml
from packageurl import PackageURL

from packagedcode import models
from packagedcode.utils import combine_expressions
"""
Collect data from Dart pub packages.
See https://dart.dev/tools/pub/pubspec

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

# FIXME: warnings reported here DO NOT work. We should have a better way


class BaseDartPubspecHandler(models.DatafileHandler):

    @classmethod
    def assemble(cls, package_data, resource, codebase, package_adder):
        datafile_name_patterns = \
            DartPubspecYamlHandler.path_patterns + DartPubspecLockHandler.path_patterns

        if resource.has_parent():
            dir_resource=resource.parent(codebase)
        else:
            dir_resource=resource

        yield from cls.assemble_from_many_datafiles(
            datafile_name_patterns=datafile_name_patterns,
            directory=dir_resource,
            codebase=codebase,
            package_adder=package_adder,
        )

    @classmethod
    def compute_normalized_license(cls, package):
        return compute_normalized_license(package.declared_license)


class DartPubspecYamlHandler(BaseDartPubspecHandler):
    datasource_id = 'pubspec_yaml'
    path_patterns = ('*pubspec.yaml',)
    default_package_type = 'pubspec'
    default_primary_language = 'dart'
    description = 'Dart pubspec manifest'
    documentation_url = 'https://dart.dev/tools/pub/pubspec'

    @classmethod
    def parse(cls, location):
        with open(location) as inp:
            pubspec_data = saneyaml.load(inp.read())

        package_data = build_package(pubspec_data)
        if package_data:
            yield package_data


def compute_normalized_license(declared_license):
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


class DartPubspecLockHandler(BaseDartPubspecHandler):
    datasource_id = 'pubspec_lock'
    path_patterns = ('*pubspec.lock',)
    default_package_type = 'pubspec'
    default_primary_language = 'dart'
    description = 'Dart pubspec lockfile'
    documentation_url = 'https://web.archive.org/web/20220330081004/https://gpalma.pt/blog/what-is-the-pubspec-lock/'

    @classmethod
    def parse(cls, location):
        with open(location) as inp:
            locks_data = saneyaml.load(inp.read())

        dependencies = list(collect_locks(locks_data))

        yield models.PackageData(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            primary_language=cls.default_primary_language,
            dependencies=dependencies
        )


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
        purl = PackageURL(
            type='pubspec',
            name=name,
            version=version,
        )
        is_resolved = True
    else:
        purl = PackageURL(
            type='pubspec',
            name=name,
        )
        is_resolved = False

    dep = models.DependentPackage(
        purl=purl.to_string(),
        extracted_requirement=version,
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

    api_data_url = name and version and f'https://pub.dev/api/packages/{name}/versions/{version}'
    repository_homepage_url = name and version and f'https://pub.dev/packages/{name}/versions/{version}'

    # A URL should be in the form of:
    # https://pub.dartlang.org/packages/url_launcher/versions/6.0.9.tar.gz
    # And it may resolve to:
    # https://storage.googleapis.com/pub-packages/packages/http-0.13.2.tar.gz
    # as seen in the pub.dev web pages
    repository_download_url = name and version and f'https://pub.dartlang.org/packages/{name}/versions/{version}.tar.gz'

    download_url = download_url or repository_download_url

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

    package = models.PackageData(
        datasource_id=DartPubspecYamlHandler.datasource_id,
        type=DartPubspecYamlHandler.default_primary_language,
        primary_language=DartPubspecYamlHandler.default_primary_language,
        name=name,
        version=version,
        download_url=download_url,
        vcs_url=vcs_url,
        description=description,
        declared_license=declared_license,
        parties=parties,
        homepage_url=homepage_url,
        dependencies=package_dependencies,
        extra_data=extra_data,
        repository_homepage_url=repository_homepage_url,
        api_data_url=api_data_url,
        repository_download_url=repository_download_url,
    )

    if not package.license_expression and package.declared_license:
        package.license_expression = models.compute_normalized_license(package.declared_license)

    return package
