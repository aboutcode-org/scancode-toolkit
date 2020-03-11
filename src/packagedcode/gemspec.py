#
# Copyright (c) 2017 nexB Inc. and others. All rights reserved.
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
import os
from os.path import abspath
from os.path import expanduser

import attr
import saneyaml
from six import string_types

from commoncode import fileutils
from extractcode import archive
from extractcode.uncompress import get_gz_compressed_file_content
from packagedcode import models
from packagedcode.utils import combine_expressions

import io
import re

from commoncode import filetype
from packagedcode import models

# TODO: check:
# https://github.com/hugomaiavieira/pygments-rspec
# https://github.com/tushortz/pygeminfo
# https://github.com/mfwarren/gemparser/blob/master/src/gemparser/__init__.py
# https://gitlab.com/balasankarc/gemfileparser

TRACE = False


def logger_debug(*args):
    pass


logger = logging.getLogger(__name__)

if TRACE:
    import sys
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(
            isinstance(a, string_types) and a or repr(a) for a in args))


@attr.s()
class GemSpec(models.Package):
    """
    Represent a GemSpec specification.
    """

    metafiles = ('*.gemspec',)
    extensions = ('.gemspec',)
    default_type = 'gemspec'
    default_primary_language = 'Ruby'
    default_web_baseurl = 'https://rubygems.org/gems/'
    default_download_baseurl = 'https://rubygems.org/downloads'
    default_api_baseurl = 'https://rubygems.org/api'

    @classmethod
    def recognize(cls, location):
        return parse(location)

    @classmethod
    def get_package_root(cls, manifest_resource, codebase):
        # FIXME: this can vary if we have a plain checkout or install vs. a .gem
        # archive where we have "multiple" roots

        if manifest_resource.name.endswith(('.gemspec', 'Gemfile', 'Gemfile.lock',)):
            return manifest_resource.parent(codebase)

        # unknown?
        return manifest_resource

    def compute_normalized_license(self):
        return compute_normalized_license(self.declared_license)

    def repository_homepage_url(self, baseurl=default_web_baseurl):
        return rubygems_homepage_url(self.name, self.version, repo=baseurl)

    def repository_download_url(self, baseurl=default_download_baseurl):
        quals = self.qualifiers or {}
        platform = quals.get('platform') or None
        return rubygems_download_url(self.name, self.version, platform, repo=baseurl)

    def api_data_url(self, baseurl=default_api_baseurl):
        return rubygems_api_url(self.name, self.version, repo=baseurl)


def parse(location):
    """
    Return a Package object from a gemspec file or None.
    """
    if not location.endswith('.gemspec'):
        return

    with io.open(location) as loc:
        package_data = saneyaml.load(location, _dict=OrderedDict)

    return build_package(package_data)

def build_package(package_data):
    """
    Return a Pacakge object from a package data mapping or None.
    """

    if not package_data:
        return

    #name = package_data.get('name') or None
    #version = package_data.get('version') or None

    core_package_data = package_data.get('package', {})
    name = core_package_data.get('name')
    version = core_package_data.get('version')
    description = core_package_data.get('description')
    if description:
        description = description.strip()

    authors = core_package_data.get('authors')
    parties = list(party_mapper(authors, party_role='author'))

    # TODO: Remove this ordered_dict_map once cargo.py is able to handle
    # the appropriate data (source_packages, dependencies, etc..)
    # At the moment, this is only useful for making tests pass
    #ordered_dict_map = {}
    #for key in ("source_packages", "dependencies", "keywords", "parties"):
    #    ordered_dict_map[key] = OrderedDict()

    package = GemSpec(
        name=name,
        version=version,
        description=description,
        parties=parties
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


def rubygems_download_url(name, version, platform=None, repo='https://rubygems.org/downloads'):
    """
    Return a .gem download URL given a name, version, and optional platform (e.g. java)
    and a base repo URL.

    For example: https://rubygems.org/downloads/mocha-1.7.0.gem
    """
    repo = repo.rstrip('/')
    name = name.strip().strip('/')
    version = version.strip().strip('/')
    version_plat = version
    if platform  and platform != 'ruby':
        version_plat = '{version}-{platform}'.format(**locals())
    return '{repo}/{name}-{version_plat}.gem'.format(**locals())


def rubygems_api_url(name, version=None, repo='https://rubygems.org/api'):
    """
    Return a package API data URL given a name, an optional version and a base
    repo API URL.

    For instance:
    https://rubygems.org/api/v2/rubygems/action_tracker/versions/1.0.2.json

    If no version, we return:
    https://rubygems.org/api/v1/versions/turbolinks.json

    Unused:
    https://rubygems.org/api/v1/gems/mqlight.json
    """
    repo = repo.rstrip('/')
    if version:
        api_url = '{repo}/v2/rubygems/{name}/versions/{version}.json'
    else:
        api_url = '{repo}/v1/versions/{name}.json'
    return api_url.format(**locals())


def licenses_mapper(license, licenses):
    """
    Return declared_licenses list based on the `license` and
    `licenses` values found in a package.
    """
    declared_licenses = []
    if license:
        declared_licenses.append(str(license).strip())
    if licenses:
        for lic in licenses:
            if lic and lic.strip():
                declared_licenses.append(lic.strip())
    return declared_licenses


# mapping of {Gem license: scancode license key}
LICENSES_MAPPING = {
    'Apache 2.0': 'apache-2.0',
    'Apache-2.0': 'apache-2.0',
    'Apache': 'apache-2.0',
    'Apache License 2.0': 'apache-2.0',
    'Artistic 2.0': 'artistic-2.0',
    '2-clause BSDL': 'bsd-simplified',
    'BSD 2-Clause': 'bsd-simplified',
    'BSD-2-Clause': 'bsd-simplified',
    'BSD-3': 'bsd-new',
    'BSD': 'bsd-new',
    'GNU GPL v2': 'gpl-2.0',
    'GPL-2': 'gpl-2.0',
    'GPL2': 'gpl-2.0',
    'GPL': 'gpl-2.0',
    'GPLv2': 'gpl-2.0',
    'GPLv2+': 'gpl-2.0-plus',
    'GPLv3': 'gpl-3.0',
    'ISC': 'isc',
    'LGPL-2.1+': 'lgpl-2.1-plus',
    'LGPL-3': 'lgpl-3.0',
    'LGPL': 'lgpl',
    'LGPL': 'lgpl-2.0-plus',
    'LGPLv2.1+': 'lgpl-2.1-plus',
    'MIT': 'mit',
    'New Relic': 'new-relic',
    'None': 'unknown',
    'Perl Artistic v2': 'artistic-2.0',
    'Ruby 1.8': 'ruby',
    'Ruby': 'ruby',
    'same as ruby': 'ruby',
    'same as ruby\'s': 'ruby',
    'SIL Open Font License': 'ofl-1.0',
    'Unlicense': 'unlicense',
}

def spec_defaults():
    """
    Return a mapping with spec attribute defaults to ensure that the
    returned results are the same on RubyGems 1.8 and RubyGems 2.0
    """
    return {
        'base_dir': None,
        'bin_dir': None,
        'cache_dir': None,
        'doc_dir': None,
        'gem_dir': None,
        'gems_dir': None,
        'ri_dir': None,
        'spec_dir': None,
        'spec_file': None,
        'cache_file': None,
        'full_gem_path': None,
        'full_name': None,
        'gem_data': {},
        'full_name': None,
        'homepage': '',
        'licenses': [],
        'loaded_from': None,
    }


# known gem fields. other are ignored
known_fields = [
    'platform',
    'name',
    'version',
    'homepage',
    'summary',
    'description',
    'licenses',
    'email',
    'authors',
    'date',
    'requirements',
    'dependencies',

    # extra fields
    'files',
    'test_files',
    'extra_rdoc_files',

    'rubygems_version',
    'required_ruby_version',

    'rubyforge_project',
    'loaded_from',
    'original_platform',
    'new_platform',
    'specification_version',
]


def normalize(gem_data, known_fields=known_fields):
    """
    Return a mapping of gem data filtering out any field that is not a known
    field in a gem mapping. Ensure that all known fields are present
    even if empty.
    """
    return OrderedDict(
        [(k, gem_data.get(k) or None) for k in known_fields]
    )


