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

from collections import OrderedDict
import json
import logging
import os
import subprocess

from commoncode import fileutils

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
        return logger.debug(' '.join(isinstance(a, basestring) and a or repr(a) for a in args))

here = os.path.dirname(os.path.abspath(__file__))
DUMPSPEC_SCRIPT_LOCATION = os.path.join(here, 'rubygems_dumpspec.rb')
INDEX_SCRIPT_LOCATION = os.path.join(here, 'rubygems_index.rb')


def is_gem_file(location):
    """
    Return True if a file is a .gem archive or a .gemspec file.
    """
    return location.endswith(('.gem', '.gemspec'))


def get_spec(gemfile, script_file=DUMPSPEC_SCRIPT_LOCATION):
    """
    Return a gemspecs mapping by calling a Ruby script invoking the
    Rubygems native API or None.
    This requieres Ruby and Rubygems to be installed and in the path.
    """
    if not is_gem_file(gemfile):
        return

    # FIXME: use the safer commoncode.command instead
    cmd = 'ruby {script_file} {gemfile}'.format(**locals())
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    out, err = p.communicate()

    if err:
        raise Exception(err)

    spec = spec_defaults()
    raw_spec = json.loads(out)
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
        'metadata': {},
        'full_name': None,
        'homepage': '',
        'licenses': [],
        'loaded_from': None,
    }


def get_specs(locations):
    """
    Return a list of gemsspec mappings extracted from a list of
    gems or gemspecs file locations. FIXME: this should not exist
    """
    specs = []

    for gem_file in locations:
        if not is_gem_file(gem_file):
            continue
        spec = json.loads(get_spec(gem_file))
        specs.append(spec)
    return specs


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
    Return a gem mapping filtering out any field that is not a known
    field in a gem mapping. Ensure that all known fields are present
    even if empty.
    """
    return OrderedDict(
        [(k, gem_data.get(k) or None) for k in known_fields]
    )


LICENSE_KEYS_MAPPING = {
    'None': None,
    'Apache 2.0': 'apache-2.0',
    'Apache License 2.0': 'apache-2.0',
    'Apache-2.0': 'apache-2.0',
    'Apache': 'apache-2.0',
    'GPL': 'gpl-2.0',
    'GPL-2': 'gpl-2.0',
    'GNU GPL v2': 'gpl-2.0',
    'GPLv2+': 'gpl-2.0-plus',
    'GPLv2': 'gpl-2.0',
    'GPLv3': 'gpl-3.0',
    'MIT': 'mit',
    'Ruby': 'ruby',
    "same as ruby": 'ruby',
    "same as ruby's": 'ruby',
    'Ruby 1.8': 'ruby',
    'Artistic 2.0': 'artistic-2.0',
    'Perl Artistic v2': 'artistic-2.0',
    '2-clause BSDL': 'bsd-simplified',
    'BSD': 'bsd-new',
    'BSD-3': 'bsd-new',
    'ISC': 'isc',
    'SIL Open Font License': 'ofl-1.0',
    'New Relic': 'new-relic',
    'GPL2': 'gpl-2.0',
    'BSD-2-Clause': 'bsd-simplified',
    'BSD 2-Clause': 'bsd-simplified',
    'LGPL-3': 'lgpl-3.0',
    'LGPL-2.1+': 'lgpl-2.1-plus',
    'LGPLv2.1+': 'lgpl-2.1-plus',
    'LGPL': 'lgpl',
    'Unlicense': 'unlicense',
}


def get_download_url(gem_filename):
    """
    Return a public download URL given a Gem archive filename.
    """
    return 'https://rubygems.org/downloads/%(gem_filename)s' % locals()


class GemSpec(object):
    """
    Represent a Gem specification.
    """

    # TODO: Check if we should use 'summary' instead of description
    def __init__(self, location):
        """
        Initialize from the gem spec or gem file at location.
        """
        self.spec = get_spec(location)
        self.location = location
        self.filename = fileutils.file_name(location)
        self.primary_language = 'Ruby'
        self.spec['description'] = self.get_description()
        self.spec['authors'] = self.spec.get('authors', [])
        self.spec['email'] = self.get_email()
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

        #FIXME: we should use both and check if one is in the other.
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
            mapped_license = LICENSE_KEYS_MAPPING.get(lic, None)
            if mapped_license:
                mapped_licenses.append(mapped_license)
            else:
                if TRACE:
                    logger.warning('WARNING: {}: no license mapping for: "{}"'.format(self.filename, lic))
        return mapped_licenses

    def to_dict(self):
        d = OrderedDict()
        d.update(sorted(self.spec.items()))
        return d


def get_index(index_file, script_file=INDEX_SCRIPT_LOCATION):
    """
    Return a list of list of [name, version, platform] for each Gem in
    a Rubygems index by calling a Ruby script to unmarshal a Rubygems
    index.

    See:
        https://bundler.rubygems.org/
        https://github.com/bundler/bundler/blob/1bc75e0b6748bd37dd92189e1f347abebcf78971/lib/bundler/fetcher.rb
        https://github.com/rubygems/rubygems/blob/d3db595be39639fdc6b020e24fab4d0cf052b448/lib/rubygems/indexer.rb#L68
        https://github.com/rubygems/rubygems/blob/d3db595be39639fdc6b020e24fab4d0cf052b448/lib/rubygems/server.rb#L12
        https://github.com/rubygems/rubygems/blob/d3db595be39639fdc6b020e24fab4d0cf052b448/lib/rubygems/source.rb
        https://blog.engineyard.com/2014/new-rubygems-index-format
        https://rubygems.org/specs.4.8.gz
        https://rubygems.org/latest_specs.4.8.gz
        https://rubygems.org/prerelease_specs.4.8.gz
    """
    # FIXME: use the safer commoncode.command instead
    cmd = 'ruby {script_file} {index_file}'.format(**locals())
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    out, err = p.communicate()

    if err:
        raise Exception(err)
    return json.loads(out)
