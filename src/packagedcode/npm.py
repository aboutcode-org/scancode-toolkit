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

import codecs
from collections import OrderedDict
from functools import partial
import json
import logging
import re

from commoncode import filetype
from commoncode import fileutils

from packagedcode import models
from packagedcode.utils import parse_repo_url


"""
Handle Node.js NPM packages
per https://www.npmjs.org/doc/files/package.json.html
"""

"""
To check
https://github.com/pombredanne/normalize-package-data
"""

# TODO: add os and engines from package.json??

logger = logging.getLogger(__name__)
# import sys
# logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
# logger.setLevel(logging.DEBUG)


class NpmPackage(models.Package):
    metafiles = ('package.json', 'npm-shrinkwrap.json')
    filetypes = ('.tgz',)
    mimetypes = ('application/x-tar',)

    type = models.StringType(default='npm')
    primary_language = models.StringType(default='JavaScript')

    @classmethod
    def recognize(cls, location):
        return parse(location)


def is_package_json(location):
    return (filetype.is_file(location)
            and fileutils.file_name(location).lower() == 'package.json')


def is_node_modules(location):
    return (filetype.is_dir(location)
            and fileutils.file_name(location).lower() == 'node_modules')


def parse(location):
    """
    Return a Package object from a package.json file or None.
    """
    if not is_package_json(location):
        return

    with codecs.open(location, encoding='utf-8') as loc:
        package_data = json.load(loc, object_pairs_hook=OrderedDict)

    # a package.json is at the root of an NPM package
    base_dir = fileutils.parent_directory(location)
    return build_package(package_data, base_dir)


def build_package(package_data, base_dir=None):
    """
    Return a Package object from a package_data mapping (from a
    package.json or similar) or None.
    """
    # mapping of top level package.json items to the Package object field name
    plain_fields = OrderedDict([
        ('name', 'name'),
        ('description', 'summary'),
        ('keywords', 'keywords'),
        ('homepage', 'homepage_url'),
    ])

    # mapping of top level package.json items to a function accepting as arguments
    # the package.json element value and returning an iterable of key, values Package Object to update
    field_mappers = OrderedDict([
        ('author', author_mapper),
        ('bugs', bugs_mapper),
        ('contributors', contributors_mapper),
        ('maintainers', maintainers_mapper),
        # current form
        ('license', licensing_mapper),
        # old, deprecated form
        ('licenses', licensing_mapper),
        ('dependencies', dependencies_mapper),
        ('devDependencies', dev_dependencies_mapper),
        ('peerDependencies', peer_dependencies_mapper),
        ('optionalDependencies', optional_dependencies_mapper),
        # legacy, ignored
        # ('url', url_mapper),
        ('dist', dist_mapper),
        ('repository', repository_mapper),
    ])


    if not package_data.get('name') or not package_data.get('version'):
        # a package.json without name and version is not a usable NPM package
        return

    package = NpmPackage()
    # a package.json is at the root of an NPM package
    package.location = base_dir
    package.version = package_data.get('version') or None
    for source, target in plain_fields.items():
        value = package_data.get(source) or None
        if value:
            if isinstance(value, basestring):
                value = value.strip()
            if value:
                setattr(package, target, value)

    for source, func in field_mappers.items():
        logger.debug('parse: %(source)r, %(func)r' % locals())
        value = package_data.get(source) or None
        if value:
            if isinstance(value, basestring):
                value = value.strip()
            if value:
                func(value, package)

    # this should be a mapper function but requires two args.
    # Note: we only add a synthetic download URL if there is none from
    # the dist mapping.
    if not package.download_url:
        tarball = package_download_url(package.name, package.version)
        if tarball:
            package.download_url = tarball

    return package


def licensing_mapper(licenses, package):
    """
    Update package licensing and return package.
    Licensing data structure has evolved over time and is a tad messy.
    https://docs.npmjs.com/files/package.json#license
    license(s) is either:
    - a string with:
     - an SPDX id or expression { "license" : "(ISC OR GPL-3.0)" }
     - some license name or id
     - "SEE LICENSE IN <filename>"
    - (Deprecated) an array or a list of arrays of type, url.
    """
    if not licenses:
        return package

    if isinstance(licenses, basestring):
        # current form
        # TODO:  handle "SEE LICENSE IN <filename>"
        # TODO: parse expression with license_expression library
        package.asserted_license = licenses

    elif isinstance(licenses, dict):
        # old, deprecated form
        """
         "license": {
            "type": "MIT",
            "url": "http://github.com/kriskowal/q/raw/master/LICENSE"
          }
        """
        package.asserted_license = (licenses.get('type') or u'') + (licenses.get('url') or u'')

    elif isinstance(licenses, list):
        # old, deprecated form
        """
        "licenses": [{"type": "Apache License, Version 2.0",
                      "url": "http://www.apache.org/licenses/LICENSE-2.0" } ]
        or
        "licenses": ["MIT"],
        """
        lics = []
        for lic in licenses:
            if not lic:
                continue
            if isinstance(lic, basestring):
                lics.append(lic)
            elif isinstance(lic, dict):
                lics.extend(v for v in (lic.get('type') or None, lic.get('url') or None) if v)
            else:
                lics.append(repr(lic))
        package.asserted_license = u'\n'.join(lics)

    else:
        package.asserted_license = (repr(licenses))

    return package


def author_mapper(author, package):
    """
    Update package author and return package.
    https://docs.npmjs.com/files/package.json#people-fields-author-contributors
    The "author" is one person.
    """
    name, email, url = parse_person(author)
    package.authors = [models.Party(type=models.party_person, name=name, email=email, url=url)]
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

            contribs.append(models.Party(type=models.party_person, name=name, email=email, url=url))

    else:  # a string or dict
        name, email, url = parse_person(contributors)
        contribs.append(models.Party(type=models.party_person, name=name, email=email, url=url))

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
            maintains.append(models.Party(type=models.party_person, name=name, email=email, url=url))
    else:  # a string or dict
        name, email, url = parse_person(maintainers)
        maintains.append(models.Party(type=models.party_person, name=name, email=email, url=url))
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
        # we ignore the bugs e,ail for now
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
        repurl = parse_repo_url(repo.get('url'))
        if repurl:
            package.vcs_tool = repo.get('type') or 'git'
            package.vcs_repository = repurl
    return package


def url_mapper(url, package):
    """
    In a package.json, the "url" field is a legacy field that contained
    various URLs either as a string or as a mapping of type->url
    """
    if not url:
        return package

    if isinstance(url, basestring):
        # TOOD: map to a miscellaneous urls dict
        pass
    elif isinstance(url, dict):
        # typical key is "web"
        # TOOD: map to a miscellaneous urls dict
        pass
    return package


def dist_mapper(dist, package):
    """
    Only present in some package.json forms (as installed or from a
    registry). Not documented.
    "dist": {
      "integrity: "sha512-VmqXvL6aSOb+rmswek7prvdFKsFbfMshcRRi07SdFyDqgG6uXsP276NkPTcrD0DiwVQ8rfnCUP8S90x0OD+2gQ==",
      "shasum": "a124386bce4a90506f28ad4b1d1a804a17baaf32",
      "tarball": "http://registry.npmjs.org/npm/-/npm-2.13.5.tgz"
      },
    """
    integrity = dist.get('integrity') or None
    if integrity:
        algo, _, b64value = integrity.partition('-')
        if algo.lower() != 'sha512':
            raise ('Unknown checksum algorithm for ' + repr(dist))
        as_hex = b64value.decode('base64').encode('hex')
        # FIXME: add sha256 and sha512 to Package model
        # package.download_sha512 = as_hex

    package.download_sha1 = dist.get('shasum') or None
    tarball = dist.get('tarball')
    if tarball:
        package.download_url = tarball.strip()
    return package


def bundle_deps_mapper(bundle_deps, package):
    """
    https://docs.npmjs.com/files/package.json#bundleddependencies
    """
    package.dependencies[models.dep_bundled] = bundle_deps
    return package


def deps_mapper(deps, package, field_name):
    """
    Handle deps such as dependencies, devDependencies, peerDependencies, optionalDependencies
    return a tuple of (dep type, list of deps)
    https://docs.npmjs.com/files/package.json#dependencies
    https://docs.npmjs.com/files/package.json#peerdependencies
    https://docs.npmjs.com/files/package.json#devdependencies
    https://docs.npmjs.com/files/package.json#optionaldependencies
    """
    dep_types = {
        'dependencies': models.dep_runtime,
        'devDependencies': models.dep_dev,
        'peerDependencies': models.dep_optional,
        'optionalDependencies': models.dep_optional,
    }
    resolved_scope = dep_types[field_name]
    dependencies = []
    for name, version in deps.items():
        dep = models.IdentifiablePackage(name=name, version=version)
        dependencies.append(dep)
    if resolved_scope in package.dependencies:
        package.dependencies[resolved_scope].extend(dependencies)
    else:
        package.dependencies[resolved_scope] = dependencies
    return package


dependencies_mapper = partial(deps_mapper, field_name='dependencies')
dev_dependencies_mapper = partial(deps_mapper, field_name='devDependencies')
peer_dependencies_mapper = partial(deps_mapper, field_name='peerDependencies')
optional_dependencies_mapper = partial(deps_mapper, field_name='optionalDependencies')


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

    For example:
    >>> author = {
    ...   "name": "Isaac Z. Schlueter",
    ...   "email": "i@izs.me",
    ...   "url": "http://blog.izs.me"
    ... }
    >>> parse_person(author)
    ('Isaac Z. Schlueter', 'i@izs.me', 'http://blog.izs.me')
    >>> parse_person('Barney Rubble <b@rubble.com> (http://barnyrubble.tumblr.com/)')
    ('Barney Rubble', 'b@rubble.com', 'http://barnyrubble.tumblr.com/')
    >>> parse_person('Barney Rubble <none> (none)')
    ('Barney Rubble', None, None)
    >>> parse_person('Barney Rubble ')
    ('Barney Rubble', None, None)

    # FIXME: this case does not work.
    #>>> parse_person('<b@rubble.com> (http://barnyrubble.tumblr.com/)')
    #(None, 'b@rubble.com', 'http://barnyrubble.tumblr.com/')
    """
    # TODO: detect if this is a person name or a company name

    name = None
    email = None
    url = None

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

    if name:
        name = name.strip()
        if name.lower() == 'none':
            name = None
    name = name or None

    if email:
        email = email.strip('<> ')
        if email.lower() == 'none':
            email = None
    email = email or None

    if url:
        url = url.strip('() ')
        if url.lower() == 'none':
            url = None
    url = url or None
    return name, email, url


def quote_scoped_name(name):
    """
    Return a package name suitable for use in a URL percent-encoding
    as needed for scoped packages.
    For example:
    >>> quote_scoped_name('@invisionag/eslint-config-ivx')
    '@invisionag%2feslint-config-ivx'
    >>> quote_scoped_name('some-package')
    'some-package'
    """
    is_scoped_package = '@' in name
    if is_scoped_package:
        return name.replace('/', '%2f')
    return name


def package_homepage_url(name, registry='https://www.npmjs.com/package'):
    """
    Return an NPM package tarball download URL given a name, version
    and a base registry URL.

    For example:
    >>> package_homepage_url('@invisionag/eslint-config-ivx')
    'https://www.npmjs.com/package/@invisionag/eslint-config-ivx'
    >>> package_homepage_url('angular')
    'https://www.npmjs.com/package/angular'
    """
    registry = registry.rstrip('/')
    return '%(registry)s/%(name)s' % locals()


def package_download_url(name, version, registry='https://registry.npmjs.org'):
    """
    Return an NPM package tarball download URL given a name, version
    and a base registry URL.

    For example:
    >>> package_download_url('@invisionag/eslint-config-ivx', '0.1.4')
    'https://registry.npmjs.org/@invisionag/eslint-config-ivx/-/eslint-config-ivx-0.1.4.tgz'
    >>> package_download_url('angular', '1.6.6')
    'https://registry.npmjs.org/angular/-/angular-1.6.6.tgz'
    """
    registry = registry.rstrip('/')
    _, _, unscoped_name = name.rpartition('/')
    return '%(registry)s/%(name)s/-/%(unscoped_name)s-%(version)s.tgz' % locals()


def package_data_url(name, version=None, registry='https://registry.npmjs.org'):
    """
    Return an NPM package metadata download URL given a name, version
    and a base registry URL. Note that for scoped packages, the URL is
    not version specific but contains the data for all versions as the
    default behvior of the registries is to retuen nothing in this
    case.

    For example:
    >>> package_data_url(
    ... '@invisionag/eslint-config-ivx', '0.1.4',
    ... 'https://registry.yarnpkg.com')
    'https://registry.yarnpkg.com/@invisionag%2feslint-config-ivx'
    >>> package_data_url('angular', '1.6.6')
    'https://registry.npmjs.org/angular/1.6.6'
    """
    registry = registry.rstrip('/')
    is_scoped_package = '@' in name
    if is_scoped_package or not version:
        name = quote_scoped_name(name)
        return '%(registry)s/%(name)s' % locals()
    return '%(registry)s/%(name)s/%(version)s' % locals()
