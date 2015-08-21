#
# Copyright (c) 2015 nexB Inc. and others. All rights reserved.
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

from __future__ import absolute_import, print_function

import codecs
from collections import OrderedDict
from functools import partial
import json
import logging
import re

from commoncode import filetype
from commoncode import fileutils

from packagedcode.models import AssertedLicense
from packagedcode.models import Dependency
from packagedcode.models import Package
from packagedcode.models import Party
from packagedcode.models import Repository

"""
Handle Node.js NPM packages
per https://www.npmjs.org/doc/files/package.json.html
"""

"""
To check
https://github.com/pombredanne/normalize-package-data
"""


logger = logging.getLogger(__name__)
# import sys
# logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
# logger.setLevel(logging.DEBUG)


def is_package_json(location):
    return (filetype.is_file(location)
            and fileutils.file_name(location).lower() == 'package.json')


def is_node_modules(location):
    return (filetype.is_dir(location)
            and fileutils.file_name(location).lower() == 'node_modules')


class NpmPackage(Package):
    type = 'npm'
    metafiles = ['package.json']
    primary_language = 'JavaScript'
    repo_types = [Repository.repo_type_npm]

    def get_info(self):
        """
        Return an Ordered dictionary of npm data.
        """
        package = OrderedDict()
        package['type'] = self.type
        package['packaging'] = self.packaging
        package['primary_language'] = self.primary_language
        package['metafile_location'] = self.metafile_locations and self.metafile_locations[0] or []
        package['id'] = self.name
        package['name'] = self.name
        package['qualified_name'] = self.qualified_name
        package['version'] = self.version
        package['summary'] = self.summary
        package['asserted_licenses'] = [l.as_dict() for l in self.asserted_licenses]

        # take the first of authors if any
        package['author'] = self.authors and self.authors[0].name
        package['author_email'] = self.authors and self.authors[0].email
        package['author_url'] = self.authors and self.authors[0].url
        package['homepage_url'] = self.homepage_url
        package['summary'] = self.summary
        # take the first of authors if any
        package['download_url'] = self.download_urls and self.download_urls[0]
        package['vcs_tool'] = self.vcs_tool
        package['vcs_repository'] = self.vcs_repository
        return package


def parse(location):
    """
    Return a Package object from a package.json
    """
    if not is_package_json(location):
        return

    # mapping of top level package.json items to the Package object field name
    plain_fields = OrderedDict([
        ('name', 'name'),
        ('version', 'version'),
        ('description', 'summary'),
        ('keywords', 'keywords'),
        ('homepage', 'homepage_url'),
    ])

    # mapping of top level package.json items to a function accepting as arguments:
    # - the package.json element value and a Package Object to update
    field_mappers = OrderedDict([
        ('author', author_mapper),
        ('bugs', bugs_mapper),
        ('contributors', contributors_mapper),
        ('maintainers', maintainers_mapper),
        ('license', licensing_mapper),
        ('licenses', licensing_mapper),
        ('dependencies', dependencies_mapper),
        ('devDependencies', dev_dependencies_mapper),
        ('peerDependencies', peer_dependencies_mapper),
        ('optionalDependencies', optional_dependencies_mapper),
        ('url', url_mapper),
        ('dist', dist_mapper),
        ('repository', repository_mapper),
    ])

    with codecs.open(location, encoding='utf-8') as loc:
        data = json.load(loc, object_pairs_hook=OrderedDict)

    if not data.get('name') or not data.get('version'):
        # a package.json without name and version is not a usable NPM package
        return

    # a package.json is at the root of an NPM package
    base_dir = fileutils.parent_directory(location)
    package = NpmPackage(location=base_dir)
    package.metafile_locations = [location]

    for source, target in plain_fields.items():
        value = data.get(source)
        if value:
            if isinstance(value, basestring):
                value = value.strip()
            if value:
                setattr(package, target, value)

    for source, func in field_mappers.items():
        logger.debug('parse: %(source)r, %(func)r' % locals())
        value = data.get(source)
        if value:
            if isinstance(value, basestring):
                value = value.strip()
            if value:
                func(value, package)

    package.download_urls.append(public_download_url(package.name, package.version))
    package.metafile_locations.append(location)
    return package


def licensing_mapper(licenses, package):
    """
    Update package licensing and return package.
    Licensing data structure has evolved over time and is a tad messy.
    https://docs.npmjs.com/files/package.json#license
    licenses is either:
    - a string with:
     - an SPDX id or expression { "license" : "(ISC OR GPL-3.0)" }
     - some license name or id
     - "SEE LICENSE IN <filename>"
    - (Deprecated) an array or a list of arrays of type, url.
    """
    if not licenses:
        return package

    if isinstance(licenses, basestring):
        package.asserted_licenses.append(AssertedLicense(license=licenses))

    elif isinstance(licenses, dict):
        """
         "license": {
            "type": "MIT",
            "url": "http://github.com/kriskowal/q/raw/master/LICENSE"
          }
        """
        package.asserted_licenses.append(AssertedLicense(license=licenses.get('type'),
                                                         url=licenses.get('url')))

    elif isinstance(licenses, list):
        """
        "licenses": ["type": "Apache License, Version 2.0",
                      "url": "http://www.apache.org/licenses/LICENSE-2.0" } ]
        or
        "licenses": ["MIT"],
        """
        # TODO: handle multiple values
        for lic in licenses:
            if isinstance(lic, basestring):
                package.asserted_licenses.append(AssertedLicense(license=lic))
            elif isinstance(lic, dict):
                package.asserted_licenses.append(AssertedLicense(license=lic.get('type'),
                                                                 url=lic.get('url')))
            else:
                # use the bare repr
                if lic:
                    package.asserted_licenses.append(AssertedLicense(license=repr(lic)))

    else:
        # use the bare repr
        package.asserted_licenses.append(AssertedLicense(license=repr(licenses)))

    return package


def author_mapper(author, package):
    """
    Update package author and return package.
    https://docs.npmjs.com/files/package.json#people-fields-author-contributors
    The "author" is one person.
    """
    name, email, url = parse_person(author)
    package.authors = [Party(type=Party.party_person,
                             name=name,
                             email=email,
                             url=url)]
    return package


def contributors_mapper(contributors, package):
    """
    Update package contributors and return package.
    https://docs.npmjs.com/files/package.json#people-fields-author-contributors
    "contributors" is an array of people.
    """
    contribs = []
    if isinstance(contributors, list):
        for contrib in contributors:
            name, email, url = parse_person(contrib)
            contribs.append(Party(type=Party.party_person,
                                  name=name,
                                  email=email,
                                  url=url))
    else:  # a string or dict
        name, email, url = parse_person(contributors)
        contribs.append(Party(type=Party.party_person,
                              name=name,
                              email=email,
                              url=url))
    package.contributors = contribs
    return package


def maintainers_mapper(maintainers, package):
    """
    Update package maintainers and return package.
    https://docs.npmjs.com/files/package.json#people-fields-author-contributors
    npm also sets a top-level "maintainers" field with your npm user info.
    """
    # note this is the same code as contributors_mappers... should be refactored
    maintains = []
    if isinstance(maintainers, list):
        for contrib in maintainers:
            name, email, url = parse_person(contrib)
            maintains.append(Party(type=Party.party_person,
                                   name=name,
                                   email=email,
                                   url=url))
    else:  # a string or dict
        name, email, url = parse_person(maintainers)
        maintains.append(Party(type=Party.party_person,
                               name=name,
                               email=email,
                               url=url))
    package.maintainers = maintains
    return package


def bugs_mapper(bugs, package):
    """
    Update package bug tracker and support email and return package.
    https://docs.npmjs.com/files/package.json#bugs
    The url to your project's issue tracker and / or the email address to
    which issues should be reported.
    { "url" : "https://github.com/owner/project/issues"
    , "email" : "project@hostname.com"
    }
    You can specify either one or both values. If you want to provide only a
    url, you can specify the value for "bugs" as a simple string instead of an
    object.
    """
    if isinstance(bugs, basestring):
        package.bug_tracking_url = bugs
    elif isinstance(bugs, dict):
        package.bug_tracking_url = bugs.get('url')
        support_contact = bugs.get('email')
        if support_contact:
            package.support_contacts = [support_contact]
    else:
        raise Exception('Invalid package.json bugs item')

    return package


def repository_mapper(repo, package):
    """
    https://docs.npmjs.com/files/package.json#repository
    "repository" :
      { "type" : "git"
      , "url" : "https://github.com/npm/npm.git"
      }
    "repository" :
      { "type" : "svn"
      , "url" : "https://v8.googlecode.com/svn/trunk/"
      }
    """
    if not repo:
        return package
    if isinstance(repo, basestring):
        package.vcs_repository = parse_repo_url(repo)
    elif isinstance(repo, dict):
        package.vcs_tool = repo.get('type') or 'git'
        package.vcs_repository = parse_repo_url(repo.get('url'))
    return package


VCS_URLS = (
    'https://',
    'http://',
    'git://',
    'git+git://',
    'hg+https://',
    'hg+http://',
    'git+https://',
    'git+http://',
    'svn+https://',
    'svn+http://',
    'svn://',
)


def parse_repo_url(repo_url):
    """
    https://docs.npmjs.com/files/package.json#repository
    Validate a repo_ulr and handle shortcuts for GitHub, GitHub gist,
    Bitbucket, or GitLab repositories (same syntax as npm install):
    This is done here: https://github.com/npm/npm/blob/d3c858ce4cfb3aee515bb299eb034fe1b5e44344/node_modules/hosted-git-info/git-host-info.js

    These should be resolved:
        npm/npm
        gist:11081aaa281
        bitbucket:example/repo
        gitlab:another/repo
        expressjs/serve-static
        git://github.com/angular/di.js.git
        git://github.com/hapijs/boom
        git@github.com:balderdashy/waterline-criteria.git
        http://github.com/ariya/esprima.git
        http://github.com/isaacs/nopt
        https://github.com/chaijs/chai
        https://github.com/christkv/kerberos.git
        https://gitlab.com/foo/private.git
        git@gitlab.com:foo/private.git
    """

    # TODO: Improve this and use outside of NPMs
    is_vcs_url = repo_url.startswith(VCS_URLS)
    if is_vcs_url:
        # TODO: ensure the .git suffix is present if needed
        return repo_url

    if repo_url.startswith('git@'):
        left, right = repo_url.split('@', 1)
        host, repo = right.split(':', 1)
        # may be we should
        if any(h in host for h in ['github', 'bitbucket', 'gitlab']):
            return 'https://%(host)s/%(repo)s' % locals()
        else:
            return repo_url

    if repo_url.startswith('gist:'):
        return repo_url

    elif repo_url.startswith(('bitbucket:', 'gitlab:', 'github:')):
        hoster_urls = {
            'bitbucket:': 'https://bitbucket.org/%(repo)s',
            'github:': 'https://github.com/%(repo)s',
            'gitlab:': 'https://gitlab.com/%(repo)s',
        }
        hoster, repo = repo_url.split(':', 1)
        return hoster_urls[hoster] % locals()
    elif len(repo_url.split('/')) == 2:
        # implicit github
        return 'https://github.com/%(repo_url)s' % locals()
    return repo_url


def url_mapper(url, package):
    """
    a "url" fieldis a redirection to your package that has been published
    somewhere else than the public npm registry
    """
    if url:
        package.download_urls.append(url)
    return package


def dist_mapper(dist, package):
    """
    only present in some package.json forms (as installed or from a registry?)
      "dist": {
        "shasum": "a124386bce4a90506f28ad4b1d1a804a17baaf32",
        "tarball": "http://registry.npmjs.org/npm/-/npm-2.13.5.tgz"
      },

    """
    package.download_sha1 = dist.get('shasum') or None
    tarball = dist.get('tarball')
    if tarball and tarball not in package.download_urls:
        package.download_urls.append(tarball)
    return package


def bundle_deps_mapper(bundle_deps, package):
    """
    https://docs.npmjs.com/files/package.json#bundleddependencies
    """
    package.dependencies[Package.dep_bundled] = bundle_deps
    return package


def _deps_mapper(deps, package, field_name):
    """
    Handle deps such as dependencies, devDependencies, peerDependencies, optionalDependencies
    return a tuple of (dep type, list of deps)
    https://docs.npmjs.com/files/package.json#dependencies
    https://docs.npmjs.com/files/package.json#peerdependencies
    https://docs.npmjs.com/files/package.json#devdependencies
    https://docs.npmjs.com/files/package.json#optionaldependencies
    """
    dep_types = {'dependencies': Package.dep_runtime,
                 'devDependencies': Package.dep_dev,
                 'peerDependencies': Package.dep_optional,
                 'optionalDependencies': Package.dep_optional,
                 }
    resolved_type = dep_types[field_name]
    dependencies = []
    for pid, version_constraint in deps.items():
        dep = Dependency(id=pid, version_constraint=version_constraint)
        dependencies.append(dep)
    if resolved_type in package.dependencies:
        package.dependencies[resolved_type].extend(dependencies)
    else:
        package.dependencies[resolved_type] = dependencies
    return package


dependencies_mapper = partial(_deps_mapper, field_name='dependencies')
dev_dependencies_mapper = partial(_deps_mapper, field_name='devDependencies')
peer_dependencies_mapper = partial(_deps_mapper, field_name='peerDependencies')
optional_dependencies_mapper = partial(_deps_mapper, field_name='optionalDependencies')


person_parser = re.compile(
    r'^(?P<name>[^\(<]+)'
    r'\s?'
    r'(?P<email><([^>]+)>)?'
    r'\s?'
    r'(?P<url>\([^\)]+\))?$'
).match


def parse_person(person):
    """
    https://docs.npmjs.com/files/package.json#people-fields-author-contributors
    A "person" is an object with a "name" field and optionally "url" and "email".

    Return a name, email, url tuple for a person object
    A person can be in the form:
      "author": {
        "name": "Isaac Z. Schlueter",
        "email": "i@izs.me",
        "url": "http://blog.izs.me"
      },
    or in the form:
      "author": "Isaac Z. Schlueter <i@izs.me> (http://blog.izs.me)",

    Both forms are equivalent.
    """
    # TODO: detect if this is a person name or a company name
    if isinstance(person, basestring):
        parsed = person_parser(person)
        if not parsed:
            return person, None, None
        else:
            name = parsed.group('name')
            email = parsed.group('email')
            url = parsed.group('url')

    elif isinstance(person, dict):
        # ensure we have our three values
        name = person.get('name')
        email = person.get('email')
        url = person.get('url')
    else:
        raise Exception('Incorrect NPM package.json person: %(person)r' % locals())

    return name and name.strip(), email and email.strip('<> '), url and url.strip('() ')


def public_download_url(name, version, registry='https://registry.npmjs.org'):
    """
    Return a package tarball download URL
    """
    return '%(registry)s/%(name)s/-/%(name)s-%(version)s.tgz' % locals()


def public_package_data_url(name, version, registry='https://registry.npmjs.org'):
    """
    Return a package metadata download URL
    """
    return '%(registry)s/%(name)s/%(version)s' % locals()
