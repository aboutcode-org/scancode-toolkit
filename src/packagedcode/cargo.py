
# Copyright (c) 2019 nexB Inc. and others. All rights reserved.
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
from functools import partial
import io
import toml
import logging
import re

import attr

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
    metafiles = ('Cargo.toml',)
    default_type = 'cargo'
    default_primary_language = 'Rust'
    default_web_baseurl = "https://crates.io"
    default_download_baseurl = "https://crates.io/api/v1"
    default_api_baseurl = "https://crates.io/api/v1"

    @classmethod
    def recognize(cls, location):
        return parse(location)

    @classmethod
    def get_package_root(cls, manifest_resource, codebase):
        return manifest_resource.parent(codebase)

    def repository_homepage_url(self, baseurl=default_web_baseurl):
        return '{}/crates/{}'.format(baseurl, self.name)

    def repository_download_url(self, baseurl=default_download_baseurl):
        return '{}/crates/{}/{}/download'.format(baseurl, self.name, self.version)

    def api_data_url(self, baseurl=default_api_baseurl):
        return '{}/crates/{}'.format(baseurl, self.name)

    def compute_normalized_license(self):
        return models.compute_normalized_license(self.declared_license)


def is_cargo_toml(location):
    return (filetype.is_file(location) and fileutils.file_name(location).lower() == 'cargo.toml')


def parse(location):
    """
    Return a Package object from a Cargo.toml file or None.
    """
    if not is_cargo_toml(location):
        return

    with io.open(location, encoding='utf-8') as loc:
        package_data = toml.load(location, _dict=OrderedDict)

    return build_package(package_data)


def build_package(package_data):
    """
    Return a Pacakge object from a package data mapping or None.
    """

    name = package_data.get('package').get('name')
    version = package_data.get('package').get('version')
    description = package_data.get('package').get('description')

    # TODO: Remove this ordered_dict_map once cargo.py is able to handle
    # the appropriate data (source_packages, dependencies, etc..)
    # At the moment, this is only useful for making tests pass
    ordered_dict_map = {}
    for key in ("source_packages", "dependencies", "keywords"):
        ordered_dict_map[key] = OrderedDict()

    package = RustCargoCrate(
        name=name,
        version=version,
        description=description,
        **ordered_dict_map
    )

    field_mappers = [
        ('authors', partial(party_mapper, party_type="author")),
    ]
    for source, func in field_mappers:
        value = package_data.get('package').get(source)
        func(value, package)

    return package


def party_mapper(party, package, party_type):
    for auth in party:
        name, email = parse_person(auth)
        package.parties.append(models.Party(
            type=models.party_person,
            name=name,
            role=party_type,
            email=email))
    return package


def parse_person(person):
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
