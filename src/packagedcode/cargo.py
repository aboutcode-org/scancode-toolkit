
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
from packageurl import PackageURL
import toml

from commoncode import filetype
from commoncode import fileutils
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


@attr.s()
class RustCargoCrate(models.PackageData):
    default_type = 'cargo'
    default_primary_language = 'Rust'
    default_web_baseurl = 'https://crates.io'
    default_download_baseurl = 'https://crates.io/api/v1'
    default_api_baseurl = 'https://crates.io/api/v1'

    @classmethod
    def get_package_root(cls, manifest_resource, codebase):
        return manifest_resource.parent(codebase)

    def repository_homepage_url(self, baseurl=default_web_baseurl):
        if self.name:
            return '{}/crates/{}'.format(baseurl, self.name)

    def repository_download_url(self, baseurl=default_download_baseurl):
        if self.name and self.version:
            return '{}/crates/{}/{}/download'.format(baseurl, self.name, self.version)

    def api_data_url(self, baseurl=default_api_baseurl):
        if self.name:
            return '{}/crates/{}'.format(baseurl, self.name)


@attr.s()
class CargoToml(RustCargoCrate, models.PackageDataFile):

    file_patterns = ('Cargo.toml',)
    extensions = ('.toml',)

    @classmethod
    def is_package_data_file(cls, location):
        """
        Return True if the file at ``location`` is likely a manifest of this type.
        """
        return filetype.is_file(location) and fileutils.file_name(location).lower() == 'cargo.toml'

    @classmethod
    def recognize(cls, location):
        """
        Yield one or more Package manifest objects given a file ``location`` pointing to a
        package archive, manifest or similar.
        """
        package_data = toml.load(location, _dict=dict)

        core_package_data = package_data.get('package', {})
        name = core_package_data.get('name')
        version = core_package_data.get('version')
        description = core_package_data.get('description')
        if description:
            description = description.strip()

        authors = core_package_data.get('authors')
        parties = list(party_mapper(authors, party_role='author'))

        declared_license = core_package_data.get('license')

        package = cls(
            name=name,
            version=version,
            description=description,
            parties=parties,
            declared_license=declared_license
        )

        yield package


@attr.s()
class CargoLock(RustCargoCrate, models.PackageDataFile):

    file_patterns = ('Cargo.lock',)
    extensions = ('.lock',)

    @classmethod
    def is_package_data_file(cls, location):
        """
        Return True if the file at ``location`` is likely a manifest of this type.
        """
        return (filetype.is_file(location)
            and fileutils.file_name(location).lower() == 'cargo.lock')

    @classmethod
    def recognize(cls, location):
        """
        Yield one or more Package manifest objects given a file ``location`` pointing to a
        package archive, manifest or similar.
        """
        package_data = toml.load(location, _dict=dict)

        package_dependencies = []
        core_package_data = package_data.get('package', [])
        for dep in core_package_data:
            package_dependencies.append(
                models.DependentPackage(
                    purl=PackageURL(
                        type='crates',
                        name=dep.get('name'),
                        version=dep.get('version')
                    ).to_string(),
                    extracted_requirement=dep.get('version'),
                    scope='dependency',
                    is_runtime=True,
                    is_optional=False,
                    is_resolved=True,
                )
            )
        
        yield cls(dependencies=package_dependencies)


@attr.s()
class RustPackage(RustCargoCrate, models.Package):
    """
    A Rust Package that is created out of one/multiple rust package
    manifests and package-like data, with it's files.
    """

    @property
    def manifests(self):
        return [
            CargoToml,
            CargoLock
        ]


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


person_parser = re.compile(
    r'^(?P<name>[^\(<]+)'
    r'\s?'
    r'(?P<email><([^>]+)>)?'
).match

person_parser_no_name = re.compile(
    r'(?P<email><([^>]+)>)?'
).match
