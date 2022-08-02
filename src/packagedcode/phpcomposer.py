#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import io
import json
from functools import partial

from packagedcode import models
from packagedcode.utils import combine_expressions

"""
Parse PHP composer package manifests, see https://getcomposer.org/ and
https://packagist.org/

TODO: add support for composer.lock and packagist formats: both are fairly
similar.
"""


class BasePhpComposerHandler(models.DatafileHandler):

    @classmethod
    def assemble(cls, package_data, resource, codebase, package_adder):
        datafile_name_patterns = (
            'composer.json',
            'composer.lock',
        )

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
    def assign_package_to_resources(cls, package, resource, codebase, package_adder):
        return models.DatafileHandler.assign_package_to_parent_tree(package, resource, codebase, package_adder)

    @classmethod
    def compute_normalized_license(cls, package):
        """
        Per https://getcomposer.org/doc/04-schema.md#license this is an expression
        """
        return compute_normalized_license(package.declared_license)


class PhpComposerJsonHandler(BasePhpComposerHandler):
    datasource_id = 'php_composer_json'
    path_patterns = ('*composer.json',)
    default_package_type = 'composer'
    default_primary_language = 'PHP'
    description = 'PHP composer manifest'
    documentation_url = 'https://getcomposer.org/doc/04-schema.md'

    @classmethod
    def parse(cls, location):
        """
        Yield one or more Package manifest objects given a file ``location``
        pointing to a package archive, manifest or similar.

        Note that this is NOT exactly the packagist.json format (all are closely
        related of course but have important (even if minor) differences.
        """
        with io.open(location, encoding='utf-8') as loc:
            package_json = json.load(loc)

        yield build_package_data(package_json)


def get_repository_homepage_url(namespace, name):
    if namespace and name:
        return f'https://packagist.org/packages/{namespace}/{name}'
    elif name:
        return f'https://packagist.org/packages/{name}'


def get_api_data_url(namespace, name):
    if namespace and name:
        return f'https://packagist.org/p/packages/{namespace}/{name}.json'
    elif name:
        return f'https://packagist.org/p/packages/{name}.json'


def build_package_data(package_data):

    # Note: A composer.json without name and description is not a usable PHP
    # composer package. Name and description fields are required but only for
    # published packages: https://getcomposer.org/doc/04-schema.md#name We want
    # to catch both published and non-published packages here. Therefore, we use
    # None as a package name if there is no name.

    ns_name = package_data.get('name')
    is_private = False
    if not ns_name:
        ns = None
        name = None
        is_private = True
    else:
        ns, _, name = ns_name.rpartition('/')

    package = models.PackageData(
        datasource_id=PhpComposerJsonHandler.datasource_id,
        type=PhpComposerJsonHandler.default_package_type,
        namespace=ns,
        name=name,
        repository_homepage_url=get_repository_homepage_url(ns, name),
        api_data_url=get_api_data_url(ns, name),
        primary_language=PhpComposerJsonHandler.default_primary_language,
    )

    # mapping of top level composer.json items to the Package object field name
    plain_fields = [
        ('version', 'version'),
        ('description', 'summary'),
        ('keywords', 'keywords'),
        ('homepage', 'homepage_url'),
    ]

    for source, target in plain_fields:
        value = package_data.get(source)
        if isinstance(value, str):
            value = value.strip()
            if value:
                setattr(package, target, value)

    # mapping of top level composer.json items to a function accepting as
    # arguments the composer.json element value and returning an iterable of
    # key, values Package Object to update
    field_mappers = [
        ('authors', author_mapper),
        ('license', partial(licensing_mapper, is_private=is_private)),
        ('support', support_mapper),
        ('require', partial(_deps_mapper, scope='require', is_runtime=True)),
        ('require-dev', partial(_deps_mapper, scope='require-dev', is_optional=True)),
        ('provide', partial(_deps_mapper, scope='provide', is_runtime=True)),
        ('conflict', partial(_deps_mapper, scope='conflict', is_runtime=True, is_optional=True)),
        ('replace', partial(_deps_mapper, scope='replace', is_runtime=True, is_optional=True)),
        ('suggest', partial(_deps_mapper, scope='suggest', is_runtime=True, is_optional=True)),
        ('source', source_mapper),
        ('dist', dist_mapper)
    ]

    for source, func in field_mappers:
        value = package_data.get(source)
        if value:
            if isinstance(value, str):
                value = value.strip()
            if value:
                func(value, package)

    # Parse vendor from name value
    vendor_mapper(package)

    if not package.license_expression and package.declared_license:
        package.license_expression = models.compute_normalized_license(package.declared_license)

    return package


class PhpComposerLockHandler(BasePhpComposerHandler):
    datasource_id = 'php_composer_lock'
    path_patterns = ('*composer.lock',)
    default_package_type = 'composer'
    default_primary_language = 'PHP'
    description = 'PHP composer lockfile'
    documentation_url = 'https://getcomposer.org/doc/01-basic-usage.md#commit-your-composer-lock-file-to-version-control'

    @classmethod
    def parse(cls, location):
        with io.open(location, encoding='utf-8') as loc:
            package_data = json.load(loc)

        packages = [
            build_package_data(p)
            for p in package_data.get('packages', [])
        ]
        packages_dev = [
            build_package_data(p)
            for p in package_data.get('packages-dev', [])
        ]

        required_deps = [
            build_dep_package(p, scope='require', is_runtime=True, is_optional=False)
            for p in packages
        ]
        required_dev_deps = [
            build_dep_package(p, scope='require-dev', is_runtime=False, is_optional=True)
            for p in packages_dev
        ]

        yield models.PackageData(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            primary_language=cls.default_primary_language,
            dependencies=required_deps + required_dev_deps
        )

        for package in packages + packages_dev:
            yield package


def compute_normalized_license(declared_license):
    """
    Return a normalized license expression string detected from a list of
    declared license items or string type.
    """
    if not declared_license:
        return

    detected_licenses = []

    if isinstance(declared_license, str):
        if declared_license == 'proprietary':
            return declared_license
        if '(' in declared_license and ')' in declared_license and ' or ' in declared_license:
            declared_license = declared_license.strip().rstrip(')').lstrip('(')
            declared_license = declared_license.split(' or ')
        else:
            return models.compute_normalized_license(declared_license)

    if isinstance(declared_license, list):
        for declared in declared_license:
            detected_license = models.compute_normalized_license(declared)
            detected_licenses.append(detected_license)
    else:
        declared_license = repr(declared_license)
        detected_license = models.compute_normalized_license(declared_license)

    if detected_licenses:
        # build a proper license expression: the defaultfor composer is OR
        return combine_expressions(detected_licenses, 'OR')


def licensing_mapper(licenses, package, is_private=False):
    """
    Update package licensing and return package.
    Licensing data structure has evolved over time and is a tad messy.
    https://getcomposer.org/doc/04-schema.md#license
    The value of license is either:
    - an SPDX expression string:  {  "license": "(LGPL-2.1 or GPL-3.0+)" }
    - a list of SPDX license ids choices: "license": ["LGPL-2.1","GPL-3.0+"]

    Some older licenses are plain strings and not SPDX ids. Also if there is no
    license and the `is_private` Fkag is True, we return a "proprietary-license"
    license.
    """
    if not licenses and is_private:
        package.declared_license = 'proprietary-license'
        return package

    package.declared_license = licenses
    return package


def author_mapper(authors_content, package):
    """
    Update package parties with authors and return package.
    https://getcomposer.org/doc/04-schema.md#authors
    """
    for name, role, email, url in parse_person(authors_content):
        role = role or 'author'
        package.parties.append(
            models.Party(type=models.party_person, name=name,
                         role=role, email=email, url=url))
    return package


def support_mapper(support, package):
    """
    Update support and bug tracking url.
    https://getcomposer.org/doc/04-schema.md#support
    """
    # TODO: there are many other information we ignore for now
    package.bug_tracking_url = support.get('issues') or None
    package.code_view_url = support.get('source') or None
    return package


def source_mapper(source, package):
    """
    Add vcs_url from source tag, if present. Typically only present in
    composer.lock
    """
    tool = source.get('type')
    if not tool:
        return package
    url = source.get('url')
    if not url:
        return package
    version = source.get('reference')
    package.vcs_url = '{tool}+{url}@{version}'.format(**locals())
    return package


def dist_mapper(dist, package):
    """
    Add download_url from source tag, if present. Typically only present in
    composer.lock
    """
    url = dist.get('url')
    if not url:
        return package
    package.download_url = url
    return package


def vendor_mapper(package):
    """
    Vendor is the first part of the name element.
    https://getcomposer.org/doc/04-schema.md#name
    """
    if package.namespace:
        package.parties.append(
            models.Party(type=models.party_person,
                         name=package.namespace, role='vendor'))
    return package


def _deps_mapper(deps, package, scope, is_runtime=False, is_optional=False):
    """
    Handle deps such as dependencies, devDependencies
    return a tuple of (dep type, list of deps)
    https://getcomposer.org/doc/04-schema.md#package-links
    """
    for ns_name, requirement in deps.items():
        ns, _, name = ns_name.rpartition('/')
        purl = models.PackageURL(type='composer', namespace=ns, name=name).to_string()
        dep = models.DependentPackage(
            purl=purl,
            extracted_requirement=requirement,
            scope=scope,
            is_runtime=is_runtime,
            is_optional=is_optional)
        package.dependencies.append(dep)
    return package


def parse_person(persons):
    """
    https://getcomposer.org/doc/04-schema.md#authors
    A "person" is an object with a "name" field and optionally "url" and "email".

    Yield  a name, email, url tuple for a person object
    A person can be in the form:
        "authors": [
            {
                "name": "Nils Adermann",
                "email": "naderman@naderman.de",
                "homepage": "http://www.naderman.de",
                "role": "Developer"
            },
            {
                "name": "Jordi Boggiano",
                "email": "j.boggiano@seld.be",
                "homepage": "http://seld.be",
                "role": "Developer"
            }
        ]

    Both forms are equivalent.
    """
    if isinstance(persons, list):
        for person in persons:
            # ensure we have our three values
            name = person.get('name')
            role = person.get('role')
            email = person.get('email')
            url = person.get('homepage')
            # FIXME: this got cargoculted from npm package.json parsing
            yield (
                name and name.strip(),
                role and role.strip(),
                email and email.strip('<> '),
                url and url.strip('() '))
    else:
        raise ValueError('Incorrect PHP composer persons: %(persons)r' % locals())


def build_dep_package(package, scope, is_runtime, is_optional):
    return models.DependentPackage(
        purl=package.purl,
        scope=scope,
        is_runtime=is_runtime,
        is_optional=is_optional,
        is_resolved=True,
    )
