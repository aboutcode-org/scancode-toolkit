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
import sys

from commoncode import filetype
from commoncode import fileutils
from packagedcode import models
from packagedcode.utils import parse_repo_url

"""
Parse PHP composer package manifests, see https://getcomposer.org/ and
https://packagist.org/
"""


TRACE = False

def logger_debug(*args):
    pass

logger = logging.getLogger(__name__)

if TRACE:
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, basestring) and a or repr(a) for a in args))


class PHPComposerPackage(models.Package):
    metafiles = ('composer.json',)
    filetypes = ('.json',)
    mimetypes = ('application/json',)
    type = models.StringType(default='composer')
    primary_language = models.StringType(default='PHP')

    @classmethod
    def recognize(cls, location):
        return parse(location)


def is_phpcomposer_json(location):
    return (filetype.is_file(location)
            and fileutils.file_name(location).lower() == 'composer.json')


def parse(location):
    """
    Return a Package object from a composer.json file or None.
    """
    if not is_phpcomposer_json(location):
        return

    with codecs.open(location, encoding='utf-8') as loc:
        package_data = json.load(loc, object_pairs_hook=OrderedDict)

    base_dir = fileutils.parent_directory(location)
    return build_package(package_data, base_dir)


def build_package(package_data, base_dir=None):
    """
    Return a composer Package object from a package data mapping or
    None.
    """

    # mapping of top level composer.json items to the Package object
    # field name
    plain_fields = OrderedDict([
        ('version', 'version'),
        ('description', 'summary'),
        ('keywords', 'keywords'),
        ('homepage', 'homepage_url'),
    ])

    # mapping of top level composer.json items to a function accepting
    # as arguments the composer.json element value and returning an
    # iterable of key, values Package Object to update
    field_mappers = OrderedDict([
        ('authors', author_mapper),
        ('license', licensing_mapper),
        ('require', deps_mapper),
        ('require-dev', dev_deps_mapper),
        ('provide', provide_deps_mapper),
        ('conflict', conflict_deps_mapper),
        ('replace', replace_deps_mapper),
        ('suggest', suggest_deps_mapper),
        ('repositories', vcs_repository_mapper),
        ('support', support_mapper),
    ])

    # A composer.json without name and description is not a usable PHP
    # composer package. Name and description fields are required but
    # only for published packages:
    # https://getcomposer.org/doc/04-schema.md#name
    # We want to catch both published and non-published packages here.
    # Therefore, we use "private-package-without-a-name" as a package name if there is no name.

    ns_name = package_data.get('name')
    if not ns_name:
        ns_name ='private-package-without-a-name'
    ns, _, name = ns_name.rpartition('/')

    package = PHPComposerPackage(
        namespace=ns,
        name=name,
    )

    for source, target in plain_fields.items():
        value = package_data.get(source)
        if value:
            if isinstance(value, basestring):
                value = value.strip()
            if value:
                setattr(package, target, value)

    for source, func in field_mappers.items():
        logger.debug('parse: %(source)r, %(func)r' % locals())
        value = package_data.get(source)
        if value:
            if isinstance(value, basestring):
                value = value.strip()
            if value:
                func(value, package)
    # Parse vendor from name value
    vendor_mapper(package)
    return package


def licensing_mapper(licenses, package):
    """
    Update package licensing and return package.
    Licensing data structure has evolved over time and is a tad messy.
    https://getcomposer.org/doc/04-schema.md#license
    licenses is either:
    - a string with:
     - an SPDX id or expression {  "license": "(LGPL-2.1 or GPL-3.0+)" }
    - array:
        "license": [
           "LGPL-2.1",
           "GPL-3.0+"
        ]
        """
    if not licenses:
        return package

    if isinstance(licenses, list):
        # For a package, when there is a choice between licenses
        # ("disjunctive license"), multiple can be specified as array.
        """
        "license": [
               "LGPL-2.1",
               "GPL-3.0+"
            ]
        """
        # build a proper license expression: the defaultfor composer is OR
        lics = [l.strip() for l in licenses if l and l.strip()]
        lics = ' OR '.join(lics)

    elif not isinstance(licenses, basestring):
        lics = repr(licenses)
    else:
        lics = licenses

    package.asserted_license = lics or None
    return package


def author_mapper(authors_content, package):
    """
    Update package parties with authors and return package.
    https://getcomposer.org/doc/04-schema.md#authors
    """
    for name, role, email, url in parse_person(authors_content):
        package.parties.append(
            models.Party(type=models.party_person, name=name,
                         role=role, email=email, url=url))
    return package


def support_mapper(support, package):
    """
    Update support and bug tracking url.
    https://getcomposer.org/doc/04-schema.md#support
    """
    # TODO: there are many other information we ignore for now
    package.bug_tracking_url = support.get('issues') or None
    package.code_view_url = support.get('source') or None
    return package


def vendor_mapper(package):
    """
    Vendor is the first part of the name element.
    https://getcomposer.org/doc/04-schema.md#name
    """
    if package.namespace:
        package.parties.append(models.Party(name=package.namespace, role='vendor'))
    return package


def vcs_repository_mapper(repos, package):
    """
    https://getcomposer.org/doc/04-schema.md#repositories
    "repositories": [
        {
            "type": "composer",
            "url": "http://packages.example.com"
        },
        {
            "type": "composer",
            "url": "https://packages.example.com",
            "options": {
                "ssl": {
                    "verify_peer": "true"
                }
            }
        },
        {
            "type": "vcs",
            "url": "https://github.com/Seldaek/monolog"
        },
        {
            "type": "pear",
            "url": "https://pear2.php.net"
        },
        {
            "type": "package",
            "package": {
                "name": "smarty/smarty",
                "version": "3.1.7",
                "dist": {
                    "url": "http://www.smarty.net/files/Smarty-3.1.7.zip",
                    "type": "zip"
                },
                "source": {
                    "url": "https://smarty-php.googlecode.com/svn/",
                    "type": "svn",
                    "reference": "tags/Smarty_3_1_7/distribution/"
                }
            }
        }
    ]
    """
    if not repos:
        return package
    if isinstance(repos, basestring):
        package.vcs_repository = parse_repo_url(repos)
    elif isinstance(repos, list):
        for repo in repos:
            if repo.get('type') == 'vcs':
                # vcs type includes git, svn, fossil or hg.
                # refer to https://getcomposer.org/doc/05-repositories.md#vcs
                repo_url = repo.get('url')
                if repo_url.startswith('svn') or 'subversion.apache.org' in repo_url:
                    package.vcs_tool = 'svn'
                elif repo_url.startswith('hg') or 'mercurial.selenic.com' in repo_url:
                    package.vcs_tool = 'hg'
                elif repo_url.startswith('fossil') or 'fossil-scm.org' in repo_url:
                    package.vcs_tool = 'fossil'
                else:
                    package.vcs_tool = 'git'
                package.vcs_repository = parse_repo_url(repo.get('url'))
    return package


def deps_mapper(deps, package, field_name):
    """
    Handle deps such as dependencies, devDependencies
    return a tuple of (dep type, list of deps)
    https://getcomposer.org/doc/04-schema.md#package-links
    """
    dep_scopes = {
        'require': dict(is_runtime=True),
        'require-dev': dict(is_runtime=False, is_optional=True),
        'provide': dict(is_runtime=True),
        'conflict': dict(is_runtime=False, is_optional=True),
        'replace': dict(is_runtime=True, is_optional=True),
        'suggest': dict(is_runtime=True, is_optional=True),
    }
    dep_scope = dep_scopes.get(field_name)

    dependencies = package.dependencies
    for ns_name, requirement in deps.items():
        ns, _, name = ns_name.rpartition('/')

        did = models.PackageIdentifier(
            type='composer',
            namespace=ns,
            name=name
            ).to_string()

        dep = models.DependentPackage(
            identifier=did,
            requirement=requirement,
            scope=field_name,
            **dep_scope
        )
        dependencies.append(dep)
    return package


deps_mapper = partial(deps_mapper, field_name='require')
dev_deps_mapper = partial(deps_mapper, field_name='require-dev')
provide_deps_mapper = partial(deps_mapper, field_name='provide')
conflict_deps_mapper = partial(deps_mapper, field_name='conflict')
replace_deps_mapper = partial(deps_mapper, field_name='replace')
suggest_deps_mapper = partial(deps_mapper, field_name='suggest')


def parse_person(persons):
    """
    https://getcomposer.org/doc/04-schema.md#authors
    A "person" is an object with a "name" field and optionally "url" and "email".

    Yield  a name, email, url tuple for a person object
    A person can be in the form:
        "authors": [
            {
                "name": "Nils Adermann",
                "email": "naderman@naderman.de",
                "homepage": "http://www.naderman.de",
                "role": "Developer"
            },
            {
                "name": "Jordi Boggiano",
                "email": "j.boggiano@seld.be",
                "homepage": "http://seld.be",
                "role": "Developer"
            }
        ]

    Both forms are equivalent.
    """
    if isinstance(persons, list):
        for person in persons:
            # ensure we have our three values
            name = person.get('name')
            role = person.get('role')
            email = person.get('email')
            url = person.get('homepage')
            # FIXME: this got cargoculted from npm package.json parsing
            yield (
                name and name.strip(),
                role and role.strip(),
                email and email.strip('<> '),
                url and url.strip('() ')
            )
    else:
        raise ValueError('Incorrect PHP composer persons: %(persons)r' % locals())
