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

# add lock files and yarn details

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
        ('repository', vcs_repository_mapper),
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

    asserted_license = None
    if isinstance(licenses, basestring):
        # current form
        # TODO:  handle "SEE LICENSE IN <filename>"
        # TODO: parse expression with license_expression library
        asserted_license = licenses

    elif isinstance(licenses, dict):
        # old, deprecated form
        """
         "license": {
            "type": "MIT",
            "url": "http://github.com/kriskowal/q/raw/master/LICENSE"
          }
        """
        asserted_license = (licenses.get('type') or u'') + (licenses.get('url') or u'')

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
        asserted_license = u'\n'.join(lics)

    else:
        asserted_license = (repr(licenses))

    package.asserted_license = asserted_license or None
    return package


def author_mapper(author, package):
    """
    Update package parties with author and return package.
    https://docs.npmjs.com/files/package.json#people-fields-author-contributors
    The "author" is one person.
    """
    name, email, url = parse_person(author)
    package.parties.append(
        models.Party(
            type=models.party_person,
            name=name,
            role='author',
            email=email, url=url))
    return package


def contributors_mapper(contributors, package):
    """
    Update package parties with contributors and return package.
    https://docs.npmjs.com/files/package.json#people-fields-author-contributors
    "contributors" is an array of people.
    """
    if isinstance(contributors, list):
        for contrib in contributors:
            name, email, url = parse_person(contrib)
            package.parties.append(models.Party(type=models.party_person, name=name, role='contributor', email=email, url=url))
    else:
        # a string or dict
        name, email, url = parse_person(contributors)
        package.parties.append(models.Party(type=models.party_person, name=name, role='contributor', email=email, url=url))
    return package


def maintainers_mapper(maintainers, package):
    """
    Update package parties with maintainers and return package.
    https://docs.npmjs.com/files/package.json#people-fields-author-contributors
    npm also sets a top-level "maintainers" field with your npm user info.
    """
    # note this is the same code as contributors_mappers... should be refactored
    if isinstance(maintainers, list):
        for contrib in maintainers:
            name, email, url = parse_person(contrib)
            package.parties.append(
                models.Party(
                    type=models.party_person,
                    name=name,
                    role='maintainer',
                    email=email, url=url))
    else:
        # a string or dict
        name, email, url = parse_person(maintainers)
        package.parties.append(
            models.Party(
                type=models.party_person,
                name=name,
                role='maintainer',
                email=email, url=url))
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
        raise ValueError('Invalid package.json "bugs" item:' + repr(bugs))

    return package


def vcs_repository_mapper(repo, package):
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
        algo = algo.lower()
        sha512 = b64value.decode('base64').encode('hex')
        package.download_checksums.append('{}:{}'.format(algo, sha512))

    sha1 = dist.get('shasum')
    if sha1:
        package.download_checksums.append('sha1:{}'.format(sha1))

    tarball = dist.get('tarball')
    if tarball:
        package.download_url = tarball.strip()
    return package


def bundle_deps_mapper(bundle_deps, package):
    """
    https://docs.npmjs.com/files/package.json#bundleddependencies
        "This defines an array of package names that will be bundled
        when publishing the package."
    """
    for bdep in (bundle_deps or []):
        bdep = bdep and bdep.strip()
        if not bdep:
            continue

        ns, name = split_scoped_package_name(bdep)
        purl = models.PackageURL(
            type='npm', namespace=ns, name=name)

        dep = models.DependentPackage(
            purl=purl.to_string(),
            scope='bundledDependencies',
            is_runtime=True,
            )
        package.dependencies.append(dep)

    return package


def split_scoped_package_name(name):
    """
    Return a tuple of (namespace, name) given a package name.
    Namespace is the "scope" for a scoped package.
    """
    name = name and name.strip()
    if not name:
        return None, None
    ns, _, name = name.rpartition('/')
    ns = ns.strip() or None
    name = name.strip() or None
    return ns, name


def deps_mapper(deps, package, field_name):
    """
    Handle deps such as dependencies, devDependencies, peerDependencies, optionalDependencies
    return a tuple of (dep type, list of deps)
    https://docs.npmjs.com/files/package.json#dependencies
    https://docs.npmjs.com/files/package.json#peerdependencies
    https://docs.npmjs.com/files/package.json#devdependencies
    https://docs.npmjs.com/files/package.json#optionaldependencies
    """
    npm_dep_scopes_attrs = {
        'dependencies': dict(is_runtime=True, is_optional=False),
        'devDependencies': dict(is_runtime=False, is_optional=True),
        'peerDependencies': dict(is_runtime=True, is_optional=False),
        'optionalDependencies': dict(is_runtime=True, is_optional=True),
    }
    dependencies = package.dependencies

    deps_by_name = {}
    if field_name == 'optionalDependencies':
        # optionalDependencies override the dependencies with the same name
        # so we build a map of name->dep object for use later
        for d in dependencies:
            if d.scope != 'dependencies':
                continue
            purl = models.PackageURL.from_string(d.purl)
            npm_name = purl.name
            if purl.namespace:
                npm_name = '/'.join([purl.namespace, purl.name])
            deps_by_name[npm_name] = d

    for fqname, requirement in deps.items():
        ns, name = split_scoped_package_name(fqname)
        purl = models.PackageURL(type='npm', namespace=ns, name=name).to_string()

        # optionalDependencies override the dependencies with the same name
        # https://docs.npmjs.com/files/package.json#optionaldependencies
        # therefore we update/override the dependency of the same name
        overridable = deps_by_name.get(fqname)

        if overridable and field_name == 'optionalDependencies':
            overridable.purl = purl
            overridable.is_optional = True
            overridable.scope = field_name
        else:
            dep_attrs = npm_dep_scopes_attrs.get(field_name, dict())
            dep = models.DependentPackage(
                purl=purl,
                scope=field_name,
                requirement=requirement,
                **dep_attrs
            )
            dependencies.append(dep)

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
    (u'Isaac Z. Schlueter', u'i@izs.me', u'http://blog.izs.me')
    >>> parse_person('Barney Rubble <b@rubble.com> (http://barnyrubble.tumblr.com/)')
    (u'Barney Rubble', u'b@rubble.com', u'http://barnyrubble.tumblr.com/')
    >>> parse_person('Barney Rubble <none> (none)')
    (u'Barney Rubble', None, None)
    >>> parse_person('Barney Rubble ')
    (u'Barney Rubble', None, None)

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


def is_scoped_package(name):
    return '@' in name


def quote_scoped_name(name):
    """
    Return a package name suitable for use in a URL percent-encoding
    as needed for scoped packages.
    For example:
    >>> quote_scoped_name('@invisionag/eslint-config-ivx')
    u'@invisionag%2feslint-config-ivx'
    >>> quote_scoped_name('some-package')
    u'some-package'
    """
    if is_scoped_package(name):
        return name.replace('/', '%2f')
    return name


def package_homepage_url(name, registry='https://www.npmjs.com/package'):
    """
    Return an NPM package tarball download URL given a name, version
    and a base registry URL.

    For example:
    >>> package_homepage_url('@invisionag/eslint-config-ivx')
    u'https://www.npmjs.com/package/@invisionag/eslint-config-ivx'
    >>> package_homepage_url('angular')
    u'https://www.npmjs.com/package/angular'
    """
    registry = registry.rstrip('/')
    return '%(registry)s/%(name)s' % locals()


def package_download_url(name, version, registry='https://registry.npmjs.org'):
    """
    Return an NPM package tarball download URL given a name, version
    and a base registry URL.

    For example:
    >>> package_download_url('@invisionag/eslint-config-ivx', '0.1.4')
    u'https://registry.npmjs.org/@invisionag/eslint-config-ivx/-/eslint-config-ivx-0.1.4.tgz'
    >>> package_download_url('angular', '1.6.6')
    u'https://registry.npmjs.org/angular/-/angular-1.6.6.tgz'
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
    u'https://registry.yarnpkg.com/@invisionag%2feslint-config-ivx'
    >>> package_data_url('angular', '1.6.6')
    u'https://registry.npmjs.org/angular/1.6.6'
    """
    registry = registry.rstrip('/')
    if is_scoped_package(name) or not version:
        name = quote_scoped_name(name)
        return '%(registry)s/%(name)s' % locals()
    return '%(registry)s/%(name)s/%(version)s' % locals()
