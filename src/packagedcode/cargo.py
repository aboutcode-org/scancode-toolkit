
# Copyright (c) nexB Inc. and others. All rights reserved.
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

from collections import OrderedDict
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
class RustCargoCrate(models.Package):
    metafiles = ('Cargo.toml', 'Cargo.lock')
    default_type = 'cargo'
    default_primary_language = 'Rust'
    default_web_baseurl = 'https://crates.io'
    default_download_baseurl = 'https://crates.io/api/v1'
    default_api_baseurl = 'https://crates.io/api/v1'

    @classmethod
    def recognize(cls, location):
        yield parse(location)

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


def parse(location):
    """
    Return a Package object from a Cargo.toml/Cargo.lock file.
    """
    handlers = {'cargo.toml': build_cargo_toml_package, 'cargo.lock': build_cargo_lock_package}
    filename = filetype.is_file(location) and fileutils.file_name(location).lower()
    handler = handlers.get(filename)
    if handler:
        return handler and handler(toml.load(location, _dict=OrderedDict))


def build_cargo_toml_package(package_data):
    """
    Return a Package object from a Cargo.toml package data mapping or None.
    """

    core_package_data = package_data.get('package', {})
    name = core_package_data.get('name')
    version = core_package_data.get('version')
    description = core_package_data.get('description')
    if description:
        description = description.strip()

    authors = core_package_data.get('authors')
    parties = list(party_mapper(authors, party_role='author'))

    declared_license = core_package_data.get('license')

    package = RustCargoCrate(
        name=name,
        version=version,
        description=description,
        parties=parties,
        declared_license=declared_license
    )

    return package


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


def build_cargo_lock_package(package_data):
    """
    Return a Package object from a Cargo.lock package data mapping or None.
    """

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
                requirement=dep.get('version'),
                scope='dependency',
                is_runtime=True,
                is_optional=False,
                is_resolved=True,
            )
        )
    
    return RustCargoCrate(dependencies=package_dependencies)
