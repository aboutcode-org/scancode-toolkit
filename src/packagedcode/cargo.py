
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import logging
import re

import attr
import saneyaml
import toml
from packageurl import PackageURL

from packagedcode import models

"""
Handle Rust cargo crates
"""

TRACE = False

logger = logging.getLogger(__name__)

if TRACE:
    import sys
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

# TODO:  add dependencies


class CargoTomlHandler(models.DatafileHandler):
    datasource_id = 'cargo_toml'
    path_patterns = ('*/Cargo.toml',)
    default_package_type = 'cargo'
    default_primary_language = 'Rust'
    description = 'Rust Cargo.toml package manifest'

    @classmethod
    def parse(cls, location):
        package_data = toml.load(location, _dict=dict)

        core_package_data = package_data.get('package', {})

        name = core_package_data.get('name')
        version = core_package_data.get('version')
        description = core_package_data.get('description') or ''
        description = description.strip()

        authors = core_package_data.get('authors')
        parties = list(party_mapper(authors, party_role='author'))

        declared_license = core_package_data.get('license')
        license_expression = cls.compute_normalized_license(declared_license)
        # TODO: load as a notice_text
        license_file = core_package_data.get('license-file')
        keywords = core_package_data.get('keywords') or []
        categories = core_package_data.get('categories') or []
        keywords.extend(categories)

        # cargo dependencies are complex and can be overriden at multiple levels
        dependencies = []
        for key, value in core_package_data.items():
            if key.endswith('dependencies'):
                dependencies.extend(dependency_mapper(dependencies=value, scope=key))

        package = models.PackageData(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            name=name,
            version=version,
            primary_language=cls.default_primary_language,
            description=description,
            parties=parties,
            declared_license=declared_license,
            license_expression=license_expression,
            repository_homepage_url=name and f'https://crates.io/crates/{name}',
            repository_download_url=name and version and f'https://crates.io/api/v1/crates/{name}/{version}/download',
            api_data_url=name and  f'https://crates.io/api/v1/crates/{name}',
            dependencies=dependencies,
        )

        yield package

    @classmethod
    def assemble(cls, package_data, resource, codebase):
        """
        Assemble Cargo.toml and possible Cargo.lock datafiles
        """
        yield from cls.assemble_from_many_datafiles(
            datafile_name_patterns=('Cargo.toml', 'Cargo.lock',),
            directory=resource.parent(codebase),
            codebase=codebase,
        )


@attr.s()
class CargoLockHandler(models.DatafileHandler):
    datasource_id = 'cargo_lock'
    path_patterns = ('*/Cargo.lock',)
    default_package_type = 'cargo'
    default_primary_language = 'Rust'
    description = 'Rust Cargo.lock dependencies lockfile'

    # TODO: also add extra package data found such as version control and commits
    # [[package]]
    # name = "ansi_term"
    # version = "0.11.0"
    # source = "registry+https://github.com/rust-lang/crates.io-index"
    # checksum = "ee49baf6cb617b853aa8d93bf420db2383fab46d314482ca2803b40d5fde979b"
    # dependencies = [
    #  "winapi",
    # ]

    @classmethod
    def parse(cls, location):
        cargo_lock = toml.load(location, _dict=dict)
        dependencies = []
        package = cargo_lock.get('package', [])
        for dep in package:
            dependencies.append(
                models.DependentPackage(
                    purl=PackageURL(
                        type='cargo',
                        name=dep.get('name'),
                        version=dep.get('version')
                    ).to_string(),
                    extracted_requirement=dep.get('version'),
                    scope='dependencies',
                    is_runtime=True,
                    is_optional=False,
                    is_resolved=True,

                )
            )

        yield models.PackageData(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            primary_language=cls.default_primary_language,
            dependencies=dependencies,
        )

    @classmethod
    def assemble(cls, package_data, resource, codebase):
        """
        Assemble Cargo.toml and possible Cargo.lock datafiles
        """
        yield from cls.assemble_from_many_datafiles(
            datafile_name_patterns=('Cargo.toml', 'Cargo.lock',),
            directory=resource.parent(codebase),
            codebase=codebase,
        )


def dependency_mapper(dependencies, scope='dependencies'):
    """
    Yield DependentPackage collected from a list of cargo dependencies
    """
    is_runtime = not scope.endswith(('dev-dependencies', 'build-dependencies'))
    for name, requirement in dependencies.items():
        if isinstance(requirement, str):
            # plain version requirement
            is_optional = False
        elif isinstance(requirement, dict):
            # complex requirement, with more than version are harder to handle
            # so we just dump
            is_optional = requirement.pop('optional', False)
            requirement = saneyaml.dump(requirement)

        yield models.DependentPackage(
            purl=PackageURL(
                type='cargo',
                name=name,
            ).to_string(),
            extracted_requirement=requirement,
            scope=scope,
            is_runtime=is_runtime,
            is_optional=is_optional,
            is_resolved=False,
        )


def party_mapper(party, party_role):
    """
    Yields a Party object with party of `party_role`.
    https://doc.rust-lang.org/cargo/reference/manifest.html#the-authors-field-optional
    """
    for person in party:
        name, email = parse_person(person)
        yield models.Party(
            type=models.party_person,
            name=name,
            role=party_role,
            email=email)


person_parser = re.compile(
    r'^(?P<name>[^\(<]+)'
    r'\s?'
    r'(?P<email><([^>]+)>)?'
).match

person_parser_no_name = re.compile(
    r'(?P<email><([^>]+)>)?'
).match


def parse_person(person):
    """
    https://doc.rust-lang.org/cargo/reference/manifest.html#the-authors-field-optional
    A "person" is an object with an optional "name" or "email" field.

    A person can be in the form:
      "author": "Isaac Z. Schlueter <i@izs.me>"

    For example:
    >>> p = parse_person('Barney Rubble <b@rubble.com>')
    >>> assert p == ('Barney Rubble', 'b@rubble.com')
    >>> p = parse_person('Barney Rubble')
    >>> assert p == ('Barney Rubble', None)
    >>> p = parse_person('<b@rubble.com>')
    >>> assert p == (None, 'b@rubble.com')
    """

    parsed = person_parser(person)
    if not parsed:
        name = None
        parsed = person_parser_no_name(person)
    else:
        name = parsed.group('name')

    email = parsed.group('email')

    if name:
        name = name.strip()
    if email:
        email = email.strip('<> ')

    return name, email
