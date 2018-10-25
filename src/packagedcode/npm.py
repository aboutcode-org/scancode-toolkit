
# Copyright (c) 2018 nexB Inc. and others. All rights reserved.
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
import json
import logging
import re

import attr
from packageurl import PackageURL
from six import string_types

from commoncode import filetype
from commoncode import fileutils
from packagedcode import models
from packagedcode.utils import parse_repo_url

# Python 2 and 3 support
try:
    # Python 2
    unicode
    str = unicode  # NOQA
except NameError:
    # Python 3
    unicode = str  # NOQA

"""
Handle Node.js npm packages
per https://docs.npmjs.com/files/package.json
"""

"""
To check https://github.com/npm/normalize-package-data
"""

TRACE = False

logger = logging.getLogger(__name__)

if TRACE:
    import sys
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

# TODO: add os and engines from package.json??
# add lock files and yarn details


@attr.s()
class NpmPackage(models.Package):
    # TODO: add new lock files and yarn lock files
    metafiles = ('package.json', 'npm-shrinkwrap.json')
    filetypes = ('.tgz',)
    mimetypes = ('application/x-tar',)
    default_type = 'npm'
    default_primary_language = 'JavaScript'
    default_web_baseurl = 'https://www.npmjs.com/package'
    default_download_baseurl = 'https://registry.npmjs.org'
    default_api_baseurl = 'https://registry.npmjs.org'

    @classmethod
    def recognize(cls, location):
        return parse(location)

    @classmethod
    def get_package_root(cls, manifest_resource, codebase):
        return manifest_resource.parent(codebase)

    def repository_homepage_url(self, baseurl=default_web_baseurl):
        return npm_homepage_url(self.namespace, self.name, registry=baseurl)

    def repository_download_url(self, baseurl=default_download_baseurl):
        return npm_download_url(self.namespace, self.name, self.version, registry=baseurl)

    def api_data_url(self, baseurl=default_api_baseurl):
        return npm_api_url(self.namespace, self.name, self.version, registry=baseurl)


def npm_homepage_url(namespace, name, registry='https://www.npmjs.com/package'):
    """
    Return an npm package registry homepage URL given a namespace, name,
    version and a base registry web interface URL.

    For example:
    >>> npm_homepage_url('@invisionag', 'eslint-config-ivx')
    u'https://www.npmjs.com/package/@invisionag/eslint-config-ivx'
    >>> npm_homepage_url(None, 'angular')
    u'https://www.npmjs.com/package/angular'
    >>> npm_homepage_url('', 'angular')
    u'https://www.npmjs.com/package/angular'
    >>> npm_homepage_url('', 'angular', 'https://yarnpkg.com/en/package/')
    u'https://yarnpkg.com/en/package/angular'
    >>> npm_homepage_url('@ang', 'angular', 'https://yarnpkg.com/en/package')
    u'https://yarnpkg.com/en/package/@ang/angular'
    """
    registry = registry.rstrip('/')

    if namespace:
        ns_name = '/'.join([namespace, name])
    else:
        ns_name = name
    return '%(registry)s/%(ns_name)s' % locals()


def npm_download_url(namespace, name, version, registry='https://registry.npmjs.org'):
    """
    Return an npm package tarball download URL given a namespace, name, version
    and a base registry URL.

    For example:
    >>> npm_download_url('@invisionag', 'eslint-config-ivx', '0.1.4')
    u'https://registry.npmjs.org/@invisionag/eslint-config-ivx/-/eslint-config-ivx-0.1.4.tgz'
    >>> npm_download_url('', 'angular', '1.6.6')
    u'https://registry.npmjs.org/angular/-/angular-1.6.6.tgz'
    >>> npm_download_url(None, 'angular', '1.6.6')
    u'https://registry.npmjs.org/angular/-/angular-1.6.6.tgz'
    """
    registry = registry.rstrip('/')
    if namespace:
        ns_name = '/'.join([namespace, name])
    else:
        ns_name = name
    return '{registry}/{ns_name}/-/{name}-{version}.tgz'.format(**locals())


def npm_api_url(namespace, name, version=None, registry='https://registry.npmjs.org'):
    """
    Return a package API data URL given a namespace, name, version and a base
    registry URL.

    Note that for scoped packages (with a namespace), the URL is not version
    specific but contains the data for all versions as the default behvior of
    the registries is to return nothing in this case. Special quoting rules are
    applied for scoped npms.

    For example:
    >>> npm_api_url(
    ... '@invisionag', 'eslint-config-ivx', '0.1.4',
    ... 'https://registry.yarnpkg.com')
    u'https://registry.yarnpkg.com/@invisionag%2feslint-config-ivx'
    >>> npm_api_url(None, 'angular', '1.6.6')
    u'https://registry.npmjs.org/angular/1.6.6'
    """
    registry = registry.rstrip('/')
    version = version or ''
    if namespace:
        ns_name = '%2f'.join([namespace, name])
        # there is no version-specific URL for scoped packages
        version = ''
    else:
        ns_name = name

    if version:
        version = '/' + version
    return '{registry}/{ns_name}{version}'.format(**locals())


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

    with io.open(location, encoding='utf-8') as loc:
        package_data = json.load(loc, object_pairs_hook=OrderedDict)

    return build_package(package_data)


def build_package(package_data):
    """
    Return a Package object from a package_data mapping (from a package.json or
    similar) or None.
    """

    name = package_data.get('name')
    version = package_data.get('version')

    if not name or not version:
        # a package.json without name and version is not a usable npm package
        # FIXME: raise error?
        return

    namespace, name = split_scoped_package_name(name)
    package = NpmPackage(
        namespace=namespace or None,
        name=name,
        version=version or None,
        description=package_data.get('description', '').strip() or None,
        homepage_url=package_data.get('homepage', '').strip() or None,
        vcs_revision=package_data.get('gitHead') or None
    )

    # mapping of top level package.json items to a function accepting as
    # arguments the package.json element value and returning an iterable of (key,
    # values) to update on a package
    field_mappers = [
        ('author', partial(party_mapper, party_type='author')),
        ('contributors', partial(party_mapper, party_type='contributor')),
        ('maintainers', partial(party_mapper, party_type='maintainer')),

        ('dependencies', partial(deps_mapper, field_name='dependencies')),
        ('devDependencies', partial(deps_mapper, field_name='devDependencies')),
        ('peerDependencies', partial(deps_mapper, field_name='peerDependencies')),
        ('optionalDependencies', partial(deps_mapper, field_name='optionalDependencies')),
        ('bundledDependencies', bundle_deps_mapper),
        ('repository', vcs_repository_mapper),
        ('keywords', keywords_mapper,),
        ('bugs', bugs_mapper),
        ('dist', dist_mapper),
    ]

    for source, func in field_mappers:
        if TRACE: logger.debug('parse: %(source)r, %(func)r' % locals())
        value = package_data.get(source) or None
        if value:
            if isinstance(value, string_types):
                value = value.strip()
            if value:
                func(value, package)

    if not package.download_url:
        # Only add a synthetic download URL if there is none from the dist mapping.
        dnl_url = npm_download_url(package.namespace, package.name, package.version)
        package.download_url = dnl_url.strip()

    # licenses are a tad specialwith many different data structures
    lic = package_data.get('license')
    lics = package_data.get('licenses')
    package = licenses_mapper(lic, lics, package)
    if TRACE:
        declared_license = package.declared_license
        logger.debug(
            'parse: license: {lic} licenses: {lics} declared_license: {declared_license}'.format(locals()))

    return package


def is_scoped_package(name):
    """
    Return True if name contains a namespace.

    For example::
    >>> is_scoped_package('@angular')
    True
    >>> is_scoped_package('some@angular')
    False
    >>> is_scoped_package('linq')
    False
    >>> is_scoped_package('%40angular')
    True
    """
    return name.startswith(('@', '%40',))


def split_scoped_package_name(name):
    """
    Return a tuple of (namespace, name) given a package name.
    Namespace is the "scope" of a scoped package.
    / and @ can be url-quoted and will be unquoted.

    For example:
    >>> nsn = split_scoped_package_name('@linclark/pkg')
    >>> assert ('@linclark', 'pkg') == nsn, nsn
    >>> nsn = split_scoped_package_name('@linclark%2fpkg')
    >>> assert ('@linclark', 'pkg') == nsn, nsn
    >>> nsn = split_scoped_package_name('angular')
    >>> assert (None, 'angular') == nsn, nsn
    >>> nsn = split_scoped_package_name('%40angular%2fthat')
    >>> assert ('@angular', 'that') == nsn, nsn
    >>> nsn = split_scoped_package_name('%40angular')
    >>> assert ('@angular', None) == nsn, nsn
    >>> nsn = split_scoped_package_name('@angular')
    >>> assert ('@angular', None) == nsn, nsn
    >>> nsn = split_scoped_package_name('angular/')
    >>> assert (None, 'angular') == nsn, nsn
    >>> nsn = split_scoped_package_name('%2fangular%2f/ ')
    >>> assert (None, 'angular') == nsn, nsn
    """
    if not name:
        return None, None

    name = name and name.strip()
    if not name:
        return None, None

    name = name.replace('%40', '@').replace('%2f', '/').replace('%2F', '/')
    name = name.rstrip('@').strip('/').strip()
    if not name:
        return None, None

    # this should never happen: wee only have a scope.
    # TODO: raise an  exception?
    if is_scoped_package(name) and '/' not in name:
        return name, None

    ns, _, name = name.rpartition('/')
    ns = ns.strip() or None
    name = name.strip() or None
    return ns, name


def get_licensing(license_object):
    """
    Return actual declared licensing info from a license_data object that can be
    a string, list, dict or dict list and come from the license or licenses
    package.json tag.
    """
    if not license_object:
        return

    declared_license = None
    if isinstance(license_object, string_types):
        # current form
        # TODO: handle "SEE LICENSE IN <filename>"
        # TODO: handle UNLICENSED
        # TODO: parse expression with license_expression library
        declared_license = license_object

    elif isinstance(license_object, dict):
        # old, deprecated form
        """
         "license": {
            "type": "MIT",
            "url": "http://github.com/kriskowal/q/raw/master/LICENSE"
          }
        """
        declared_license = '\n'.join(v for v in license_object.values() if v)

    elif isinstance(license_object, list):
        # old, deprecated form
        """
        "licenses": [{"type": "Apache License, Version 2.0",
                      "url": "http://www.apache.org/licenses/LICENSE-2.0" } ]
        or
        "licenses": ["MIT"],
        """
        lics = []
        for lic in license_object:
            if not lic:
                continue
            if isinstance(lic, string_types):
                lics.append(lic)
            elif isinstance(lic, dict):
                lics_val = '\n'.join(v for v in lic.values() if v)
                lics.append(lics_val)
            else:
                lics.append(repr(lic))
        declared_license = u'\n'.join(lics)

    else:
        declared_license = repr(license_object)
    return declared_license


def licenses_mapper(license, licenses, package):  # NOQA
    """
    Update package licensing and return package based on the `license` and
    `licenses` values found in a package.

    Licensing data structure has evolved over time and is a tad messy.
    https://docs.npmjs.com/files/package.json#license
    license(s) is either:
    - a string with:
     - an SPDX id or expression { "license" : "(ISC OR GPL-3.0)" }
     - some license name or id
     - "SEE LICENSE IN <filename>"
    - (Deprecated) an array or a list of arrays of type, url.
    -  "license": "UNLICENSED" means this is proprietary
    """
    licensing1 = get_licensing(license)
    licensing2 = get_licensing(licenses)
    declared_license = '\n'.join([v for v in (licensing1, licensing2) if v])

    if declared_license:
        if package.declared_license:
            package.declared_license = '\n'.join([package.declared_license, declared_license])
        else:
            package.declared_license = declared_license
    return package


def party_mapper(party, package, party_type):
    """
    Update package parties with party of `party_type` and return package.
    https://docs.npmjs.com/files/package.json#people-fields-author-contributors
    """
    if isinstance(party, list):
        for auth in party:
            name, email, url = parse_person(auth)
            package.parties.append(models.Party(
                type=models.party_person,
                name=name,
                role=party_type,
                email=email,
                url=url))
    else:
        # a string or dict
        name, email, url = parse_person(party)
        package.parties.append(models.Party(
            type=models.party_person,
            name=name,
            role=party_type,
            email=email,
            url=url))

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
    if isinstance(bugs, string_types):
        package.bug_tracking_url = bugs
    elif isinstance(bugs, dict):
        # we ignore the bugs email for now
        package.bug_tracking_url = bugs.get('url')
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

    if isinstance(repo, list):
        # There is a case where we can have a list with a single element
        repo = repo[0]

    if isinstance(repo, string_types):
        package.vcs_repository = parse_repo_url(repo)

    elif isinstance(repo, dict):
        repo_url = parse_repo_url(repo.get('url'))
        if repo_url:
            package.vcs_tool = repo.get('type') or 'git'
            package.vcs_repository = repo_url

    return package


def dist_mapper(dist, package):
    """
    Only present in some package.json forms (as installed or from a
    registry). Not documented.
    "dist": {
      "integrity: "sha512-VmqXvL6aSOb+rmswek7prvdFKsFbfMshcRRi07SdFyDqgG6uXsP276NkPTcrD0DiwVQ8rfnCUP8S90x0OD+2gQ==",
      "shasum": "a124386bce4a90506f28ad4b1d1a804a17baaf32",
      "dnl_url": "http://registry.npmjs.org/npm/-/npm-2.13.5.tgz"
      },
    """
    if not isinstance(dist, dict):
        return

    integrity = dist.get('integrity') or None
    if integrity:
        algo, _, b64value = integrity.partition('-')
        assert 'sha512' == algo
        algo = algo.lower()
        sha512 = b64value.decode('base64').encode('hex')
        package.download_sha512 = sha512

    sha1 = dist.get('shasum')
    if sha1:
        package.download_sha1 = sha1

    dnl_url = dist.get('dnl_url')
    if not dnl_url:
        # Only add a synthetic download URL if there is none from the dist mapping.
        dnl_url = npm_download_url(package.namespace, package.name, package.version)
    package.download_url = dnl_url.strip()

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
        purl = models.PackageURL(type='npm', namespace=ns, name=name)

        dep = models.DependentPackage(purl=purl.to_string(),
            scope='bundledDependencies', is_runtime=True,
        )
        package.dependencies.append(dep)

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
    npm_dependency_scopes_attributes = {
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
            purl = PackageURL.from_string(d.purl)
            npm_name = purl.name
            if purl.namespace:
                npm_name = '/'.join([purl.namespace, purl.name])
            deps_by_name[npm_name] = d

    for fqname, requirement in deps.items():
        ns, name = split_scoped_package_name(fqname)
        purl = PackageURL(type='npm', namespace=ns, name=name).to_string()

        # optionalDependencies override the dependencies with the same name
        # https://docs.npmjs.com/files/package.json#optionaldependencies
        # therefore we update/override the dependency of the same name
        overridable = deps_by_name.get(fqname)

        if overridable and field_name == 'optionalDependencies':
            overridable.purl = purl
            overridable.is_optional = True
            overridable.scope = field_name
        else:
            dependency_attributes = npm_dependency_scopes_attributes.get(field_name, dict())
            dep = models.DependentPackage(
                purl=purl,
                scope=field_name,
                requirement=requirement,
                **dependency_attributes
            )
            dependencies.append(dep)

    return package


person_parser = re.compile(
    r'^(?P<name>[^\(<]+)'
    r'\s?'
    r'(?P<email><([^>]+)>)?'
    r'\s?'
    r'(?P<url>\([^\)]+\))?$'
).match

person_parser_no_name = re.compile(
    r'(?P<email><([^>]+)>)?'
    r'\s?'
    r'(?P<url>\([^\)]+\))?$'
).match


class NpmInvalidPerson(Exception):
    pass


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
    >>> author = {
    ...   "name": "Isaac Z. Schlueter",
    ...   "email": ["i@izs.me", "<jo2@todo.com> "],
    ...   "url": "http://blog.izs.me"
    ... }
    >>> parse_person(author)
    (u'Isaac Z. Schlueter', u'i@izs.me\\njo2@todo.com', u'http://blog.izs.me')
    >>> parse_person('<b@rubble.com> (http://barnyrubble.tumblr.com/)')
    (None, u'b@rubble.com', u'http://barnyrubble.tumblr.com/')
    """
    # TODO: detect if this is a person name or a company name e.g. the type?

    name = None
    email = None
    url = None

    if isinstance(person, string_types):
        parsed = person_parser(person)
        if not parsed:
            parsed = person_parser_no_name(person)
            if not parsed:
                return person, None, None
            else:
                name = None
                email = parsed.group('email')
                url = parsed.group('url')
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
        return None, None, None

    if name:
        if isinstance(name, string_types):
            name = name.strip()
            if name.lower() == 'none':
                name = None
        else:
            name = None
    name = name or None

    if email:
        if isinstance(email, list):
            # legacy weirdness
            email = [e.strip('<> ') for e in email if e and e.strip()]
            email = '\n'.join([e.strip() for e in email
                               if e.strip() and e.strip().lower() != 'none'])
        if isinstance(email, string_types):
            email = email.strip('<> ').strip()
            if email.lower() == 'none':
                email = None
        else:
            email = None
    email = email or None

    if url:
        if isinstance(url, list):
            # legacy weirdness
            url = [u.strip('() ') for u in email if u and u.strip()]
            url = '\n'.join([u.strip() for u in url
                               if u.strip() and u.strip().lower() != 'none'])
        if isinstance(url, string_types):
            url = url.strip('() ').strip()
            if url.lower() == 'none':
                url = None
        else:
            url = None
    url = url or None

    return name, email, url



def keywords_mapper(keywords, package):
    """
    Update package keywords and return package.
    This is supposed to be an array of strings, but sometimes this is a string.
    https://docs.npmjs.com/files/package.json#keywords
    """
    if isinstance(keywords, string_types):
        if ',' in keywords:
            keywords = [k.strip() for k in keywords.split(',') if k.strip()]
        else:
            keywords =[keywords]

    package.keywords = keywords
    return package

