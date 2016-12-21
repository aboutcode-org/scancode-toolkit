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

from __future__ import absolute_import
from __future__ import print_function

import codecs
import logging
import json
from collections import OrderedDict
from functools import partial


from commoncode import filetype
from commoncode import fileutils

from packagedcode import models
from packagedcode.utils import parse_repo_url

"""
Handle PHP composer packages, refer to https://getcomposer.org/
"""


logger = logging.getLogger(__name__)
# import sys
# logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
# logger.setLevel(logging.DEBUG)


class PHPComposerPackage(models.Package):
    metafiles = ('composer.json')
    filetypes = ('.json',)
    mimetypes = ('application/json')
    repo_types = (models.repo_phpcomposer,)

    type = models.StringType(default='phpcomposer')
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
    # mapping of top level composer.json items to the Package object field name
    plain_fields = OrderedDict([
        ('name', 'name'),
        ('description', 'summary'),
        ('keywords', 'keywords'),
        ('version', 'version'),
        ('homepage', 'homepage_url'),
    ])

    # mapping of top level composer.json items to a function accepting as arguments
    # the composer.json element value and returning an iterable of key, values Package Object to update
    field_mappers = OrderedDict([
        ('authors', author_mapper),
        ('license', licensing_mapper),
        ('require', dependencies_mapper),
        ('require-dev', dev_dependencies_mapper),
        ('repositories', repository_mapper),
        ('support', support_mapper),
    ])

    with codecs.open(location, encoding='utf-8') as loc:
        data = json.load(loc, object_pairs_hook=OrderedDict)

    if not data.get('name') or not data.get('description'):
        # a composer.json without name and description is not a usable PHP composer package
        # name and description fields are required: https://getcomposer.org/doc/04-schema.md#name
        return

    package = PHPComposerPackage()
    # a composer.json is at the root of a PHP composer package
    base_dir = fileutils.parent_directory(location)
    package.location = base_dir
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
    vendor_mapper(package)  # Parse vendor from name value
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

    if isinstance(licenses, basestring):
        package.asserted_licenses.append(models.AssertedLicense(license=licenses))
    elif isinstance(licenses, list):
        """
        "license": [
               "LGPL-2.1",
               "GPL-3.0+"
            ]
        """
        for lic in licenses:
            if isinstance(lic, basestring):
                package.asserted_licenses.append(models.AssertedLicense(license=lic))
            else:
                # use the bare repr
                if lic:
                    package.asserted_licenses.append(models.AssertedLicense(license=repr(lic)))

    else:
        # use the bare repr
        package.asserted_licenses.append(models.AssertedLicense(license=repr(licenses)))

    return package


def author_mapper(authors_content, package):
    """
    Update package authors and return package.
    https://getcomposer.org/doc/04-schema.md#authors
    """
    authors = []
    for name, email, url in parse_person(authors_content):
        authors.append(models.Party(type=models.party_person, name=name, email=email, url=url))
    package.authors = authors
    return package


def support_mapper(support, package):
    """
    Update support and bug tracking url.
    https://getcomposer.org/doc/04-schema.md#support
    """
    package.support_contacts = [support.get('email')]
    package.bug_tracking_url = support.get('issues')
    package.code_view_url = support.get('source')
    return package


def vendor_mapper(package):
    """
    Vender is part of name element.
    https://getcomposer.org/doc/04-schema.md#name
    """
    name = package.name
    if name and '/' in name:
        vendors = name.split('/')
        if vendors[0]:
            package.vendors = [models.Party(name=vendors[0])]
    return package


def repository_mapper(repos, package):
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
    dep_types = {
        'dependencies': models.dep_runtime,
        'devDependencies': models.dep_dev,
    }
    resolved_type = dep_types[field_name]
    dependencies = []
    for name, version_constraint in deps.items():
        dep = models.Dependency(name=name, version_constraint=version_constraint)
        dependencies.append(dep)
    if resolved_type in package.dependencies:
        package.dependencies[resolved_type].extend(dependencies)
    else:
        package.dependencies[resolved_type] = dependencies
    return package


dependencies_mapper = partial(deps_mapper, field_name='dependencies')
dev_dependencies_mapper = partial(deps_mapper, field_name='devDependencies')


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
            email = person.get('email')
            url = person.get('homepage')
            yield name and name.strip(), email and email.strip('<> '), url and url.strip('() ')
    else:
        raise Exception('Incorrect PHP composer composer.json person: %(person)r' % locals())
