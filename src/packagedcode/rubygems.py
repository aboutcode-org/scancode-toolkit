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
class RubyGem(models.Package):
    metafiles = ('metadata.gz-extract', '*.gemspec', 'Gemfile', 'Gemfile.lock',)
    filetypes = ('.tar', 'tar archive',)
    mimetypes = ('application/x-tar',)
    extensions = ('.gem',)
    default_type = 'gem'
    default_primary_language = 'Ruby'
    default_web_baseurl = 'https://rubygems.org/gems/'
    default_download_baseurl = 'https://rubygems.org/downloads'
    default_api_baseurl = 'https://rubygems.org/api'

    @classmethod
    def get_package_root(cls, manifest_resource, codebase):
        # FIXME: this can vary if we have a plain checkout or install vs. a .gem
        # archive where we have "multiple" roots
        if manifest_resource.name.endswith('.gem'):
            return manifest_resource

        if manifest_resource.name == 'metadata.gz-extract':
            # first level is metadata.gz-extract/
            parent = manifest_resource.parent(codebase)
            # second level is actual .gem-extract/ directory
            return parent.parent(codebase)

        if manifest_resource.name.endswith(('.gemspec', 'Gemfile', 'Gemfile.lock',)):
            return manifest_resource.parent(codebase)

        # unknown?
        return manifest_resource

    def compute_normalized_license(self):
        return compute_normalized_license(self.declared_license)

    @classmethod
    def recognize(cls, location):

        # an unextracted .gen archive
        if location.endswith('.gem'):
            yield get_gem_package(location)

        # an extractcode-extracted .gen archive
        if location.endswith('metadata.gz-extract'):
            with open(location, 'rb') as met:
                metadata = met.read()
            metadata = saneyaml.load(metadata)
            yield build_rubygem_package(metadata)

        if location.endswith('.gemspec'):
            # TODO: implement me
            pass

        if location.endswith('Gemfile'):
            # TODO: implement me
            pass

        if location.endswith('Gemfile.lock'):
            # TODO: implement me
            pass

    def repository_homepage_url(self, baseurl=default_web_baseurl):
        return rubygems_homepage_url(self.name, self.version, repo=baseurl)

    def repository_download_url(self, baseurl=default_download_baseurl):
        quals = self.qualifiers or {}
        platform = quals.get('platform') or None
        return rubygems_download_url(self.name, self.version, platform, repo=baseurl)

    def api_data_url(self, baseurl=default_api_baseurl):
        return rubygems_api_url(self.name, self.version, repo=baseurl)

    @classmethod
    def extra_key_files(cls):
        return ['metadata.gz-extract', 'metadata.gz-extract/metadata.gz-extract']

    @classmethod
    def extra_root_dirs(cls):
        return ['data.tar.gz-extract', 'metadata.gz-extract']


def compute_normalized_license(declared_license):
    """
    Return a normalized license expression string detected from a list of
    declared license items.
    """
    if not declared_license:
        return

    detected_licenses = []

    for declared in declared_license:
        detected_license = models.compute_normalized_license(declared)
        if detected_license:
            detected_licenses.append(detected_license)

    if detected_licenses:
        return combine_expressions(detected_licenses)


def rubygems_homepage_url(name, version, repo='https://rubygems.org/gems'):
    """
    Return a Rubygems.org homepage URL given a name, optional version and a base
    rubygems `repo` web interface URL.

    For instance: https://rubygems.org/gems/mocha/versions/1.7.0 or
    https://rubygems.org/gems/mocha
    """
    repo = repo.rstrip('/')
    if version:
        version = version.strip().strip('/')
        home_url = '{repo}/{name}/versions/{version}'
    else:
        home_url = '{repo}/{name}'
    return home_url.format(**locals())


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


def get_gem_package(location, download_url=None, purl=None):
    """
    Return a RubyGem Package built from the .gem file at `location` or None.
    """
    if not location.endswith('.gem'):
        return

    metadata = get_gem_metadata(location)
    metadata = saneyaml.load(metadata)
    return build_rubygem_package(metadata, download_url, purl)


def get_gem_metadata(location):
    """
    Return the string content of the metadata of a .gem archive file at
    `location` or None
    """
    extract_loc = None
    try:
        # Extract first level of tar archive
        extract_loc = fileutils.get_temp_dir(prefix='scancode-extract-')
        abs_location = abspath(expanduser(location))
        warnings = archive.extract_tar(abs_location, extract_loc) or []
        if warnings:
            raise Exception('Failed to extract RubyGem .gem file.\n' + '\n'.join(warnings))


        # The gzipped metadata is the second level of archive.
        metadata = os.path.join(extract_loc, 'metadata')
        # or it can be a plain, non-gzipped file
        metadata_gz = metadata + '.gz'

        if os.path.exists(metadata):
            with open(metadata, 'rb') as met:
                content = met.read()

        elif os.path.exists(metadata_gz):
            content, warnings = get_gz_compressed_file_content(metadata_gz)
            if warnings:
                raise Exception('Failed to extract RubyGem .gem/metadata.gz file.\n' + '\n'.join(warnings))

        else:
            raise Exception('No gem metadata found in RubyGem .gem file.')

        return content

    finally:
        if extract_loc:
            fileutils.delete(extract_loc)


def build_rubygem_package(gem_data, download_url=None, package_url=None):
    """
    Return a Package built from a Gem `gem_data` mapping or None.
    The `gem_data can come from a .gemspec or .gem/gem_data.
    Optionally use the provided `download_url` and `purl` strings.
    """
    if not gem_data:
        return

    name = gem_data.get('name')

    short_desc = gem_data.get('summary') or ''
    long_desc = gem_data.get('description') or ''
    if long_desc == short_desc:
        long_desc = None
    descriptions = [d for d in (short_desc, long_desc) if d and d.strip()]
    description = '\n'.join(descriptions)

    # Since the gem spec doc is not clear https://guides.rubygems.org
    # /specification-reference/#licenseo, we will treat a list of licenses and a
    # conjunction for now (e.g. AND)
    license = gem_data.get('license')
    licenses = gem_data.get('licenses')
    declared_license = licenses_mapper(license, licenses)

    package = RubyGem(
        name=name,
        description=description,
        homepage_url=gem_data.get('homepage'),
        download_url=download_url,
        declared_license=declared_license
    )

    # we can have one singular or a plural list of authors
    authors = gem_data.get('authors') or []
    # or a string of coma-sperated authors (in the Rubygems API)
    if isinstance(authors, str):
        authors = [a.strip() for a in authors.split(',') if a.strip()]
    authors.append(gem_data.get('author') or '')
    for author in authors:
        if author and author.strip():
            party = models.Party(name=author, role='author')
            package.parties.append(party)

    # TODO: we have a email that is either a string or a list of string

    # date: 2019-01-09 00:00:00.000000000 Z
    date = gem_data.get('date')
    if date and len(date) >= 10:
        date = date[:10]
        package.release_date = date[:10]


    # there are two levels of nesting
    version1 = gem_data.get('version') or {}
    version = version1.get('version') or None
    package.version = version
    package.set_purl(package_url)

    metadata = gem_data.get('metadata') or {}
    if metadata:
        homepage_url = metadata.get('homepage_uri')
        if homepage_url:
            if not package.homepage_url:
                package.homepage_url = homepage_url
            elif package.homepage_url == homepage_url:
                pass
            else:
                # we have both and one is wrong.
                # we prefer the existing one from the metadata
                pass

        package.bug_tracking_url = metadata.get('bug_tracking_uri')

        source_code_url = metadata.get('source_code_uri')
        if source_code_url:
            package.code_view_url = source_code_url
            # TODO: infer purl and add purl to package.source_packages

        # not used for now
        #   "changelog_uri"     => "https://example.com/user/bestgemever/CHANGELOG.md",
        #   "wiki_uri"          => "https://example.com/user/bestgemever/wiki"
        #   "mailing_list_uri"  => "https://groups.example.com/bestgemever",
        #   "documentation_uri" => "https://www.example.info/gems/bestgemever/0.0.1",

    platform = gem_data.get('platform')
    if platform != 'ruby':
        qualifiers = dict(platform=platform)
        if not package.qualifiers:
            package.qualifiers = {}

        package.qualifiers.update(qualifiers)

    package.dependencies = get_dependencies(gem_data.get('dependencies'))

    if not package.download_url:
        package.download_url = package.repository_download_url()

    if not package.homepage_url:
        package.homepage_url = package.repository_homepage_url()

    return package


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


def get_dependencies(dependencies):
    """
    Return a list of DependentPackage from the dependencies data found in a
    .gem/metadata. Here is an example of the raw YAML:

        dependencies:
        - !ruby/object:Gem::Dependency
          requirement: !ruby/object:Gem::Requirement
            requirements:
            - - '='
              - !ruby/object:Gem::Version
                version: '10.0'
          name: rake
          prerelease: false
          type: :development
          version_requirements: !ruby/object:Gem::Requirement
            requirements:
            - - '='
              - !ruby/object:Gem::Version
                version: '10.0'
        - !ruby/object:Gem::Dependency
          requirement: !ruby/object:Gem::Requirement
            requirements:
            - - "~>"
              - !ruby/object:Gem::Version
                version: 0.7.1
          name: rake-compiler
          prerelease: false
          type: :development
          version_requirements: !ruby/object:Gem::Requirement
            requirements:
            - - "~>"
              - !ruby/object:Gem::Version
                version: 0.7.1

    And once loaded with saneyaml it looks like this with several intermediate
    nestings:
        {
          "dependencies": [
            {
              "requirement": {
                "requirements": [
                  ["=", {"version": "10.0"}]
                ]
              },
              "name": "rake",
              "prerelease": false,
              "type": ":development",
              "version_requirements": {
                "requirements": [
                  ["=", {"version": "10.0"}]
                ]
              }
            },
            {
              "requirement": {
                "requirements": [
                  ["~>", {"version": "0.7.1"}]
                ]
              },
              "name": "rake-compiler",
              "prerelease": false,
              "type": ":development",
              "version_requirements": {
                "requirements": [
                  ["~>", {"version": "0.7.1"}]
                ]
              }
            }
          ]
        }

    """
    if not dependencies:
        return []

    deps = []
    for dependency in dependencies:
        name = dependency.get('name')
        if not name:
            continue

        scope = dependency.get('type', '').strip(':') or 'runtime'
        # the other value is runtime
        is_optional = scope == 'development'
        is_runtime = scope == 'runtime'

        requirements = dependency.get('requirement', {}).get('requirements', [])
        constraints = []
        for constraint, version in requirements:
            version = version.get('version') or None

            # >= 0 allows for any version: we ignore these type of contrainsts
            # as this is the same as no constraint. We also ignore lack of
            # constraints and versions
            if ((constraint == '>=' and version == '0') or not (constraint and version)):
                continue
            version_constraint = '{} {}'.format(constraint, version)
            constraints.append(version_constraint)

        # if we have only one version constraint and this is "=" then we are resolved
        is_resolved = False
        if constraints and len(constraints) == 1:
            is_resolved = constraint == '='

        version_constraint = ', '.join(constraints)

        dep = models.DependentPackage(
            purl=RubyGem.create(name=name).purl,
            requirement=version_constraint or None,
            scope=scope,
            is_runtime=is_runtime,
            is_optional=is_optional,
            is_resolved=is_resolved,
        )
        deps.append(dep)

    return deps


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


################################################################################
def parse_gemspec(location):
    raise NotImplementedError


def get_gemspec_data(location):
    """
    Return a mapping of Gem data from parsing a .gemspec  file.
    """
    if not location.endswith('.gemspec'):
        return

    spec = spec_defaults()
    raw_spec = parse_gemspec(location)
    if TRACE:
        keys = raw_spec.keys()
        logger.debug('\nRubygems spec keys for %(gemfile)r:\n%(keys)r' % locals())
    spec.update(raw_spec)
    spec = normalize(spec)
    return spec


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


def parse_spec(location):
    pass


class GemSpec(object):
    """
    Represent a Gem specification.
    """

    # TODO: Check if we should use 'summary' instead of description
    def __init__(self, location):
        """
        Initialize from the gem spec or gem file at location.
        """
        spec = parse_spec(location)
        self.location = location
        self.description = spec.get('description')
        self.summary = spec.get('summary')
        self.author = spec.get('author')
        self.authors = spec.get('authors')
        # can be a list
        self.email = spec.get('email')


        self.spec['licenses'] = self.map_licenses()
        self.make_unique()

    def __str__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.location)

    def make_unique(self):
        """
        Ensure that lists in the spec only contain unique values.
        """
        new_spec = {}
        for key, value in self.spec.items:
            if isinstance(value, list):
                newlist = []
                for item in value:
                    if item not in newlist:
                        newlist.append(item)
                new_spec[key] = newlist
            else:
                new_spec[key] = value
        return new_spec

    def get_description(self):
        """
        Using 'description' over 'summary' unless summary contains
        more data.
        See http://guides.rubygems.org/specification-reference/
        Note that it is common to see this is spec files: s.description = s.summary
        """
        description = self.spec.get('description', '')
        summary = self.spec.get('summary', '')

        content = description
        # FIXME: we should join these.
        if len(summary) > len(description):
            content = summary

        content = ' '.join(content.split())
        return content.strip()

    def get_email(self):
        """
        Join the list of emails as a comma-separated string.
        """
        email = self.spec.get('email', u'')
        if isinstance(email, list):
            email = u', '.join(email)
        return email

    def map_licenses(self):
        licenses = self.spec.get('licenses', [])
        if not isinstance(licenses, list):
            licenses = [licenses]

        mapped_licenses = []
        for lic in licenses:
            mapped_license = LICENSES_MAPPING.get(lic, None)
            if mapped_license:
                mapped_licenses.append(mapped_license)
            else:
                if TRACE:
                    logger.warning('WARNING: {}: no license mapping for: "{}"'.format(self.filename, lic))
        return mapped_licenses
