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
from functools import partial
import io
import json
import logging
import sys

import attr
from six import string_types

from commoncode import filetype
from commoncode import fileutils
from packagedcode import models

"""
Parse PHP composer package manifests, see https://getcomposer.org/ and
https://packagist.org/

TODO: add support for composer.lock and packagist formats: both are fairly
similar.
"""

TRACE = False


def logger_debug(*args):
    pass


logger = logging.getLogger(__name__)

if TRACE:
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, string_types) and a or repr(a) for a in args))


@attr.s()
class PHPComposerPackage(models.Package):
    metafiles = ('composer.json',)
    filetypes = ('.json',)
    mimetypes = ('application/json',)
    default_type = 'composer'
    default_primary_language = 'PHP'
    default_web_baseurl = 'https://packagist.org'
    default_download_baseurl = None
    default_api_baseurl = 'https://packagist.org/p'

    @classmethod
    def recognize(cls, location):
        return parse(location)

    @classmethod
    def get_package_root(cls, manifest_resource, codebase):
        return manifest_resource.parent(codebase)

    def repository_homepage_url(self, baseurl=default_web_baseurl):
        return '{}/packages/{}/{}'.format(baseurl, self.namespace, self.name)

    def api_data_url(self, baseurl=default_api_baseurl):
        return '{}/packages/{}/{}.json'.format(baseurl, self.namespace, self.name)

    def normalize_license(self, as_expression=True):
        """
        Per https://getcomposer.org/doc/04-schema.md#license this is an expression
        """
        return models.Package.normalize_license(self, as_expression=as_expression)


def is_phpcomposer_json(location):
    return (filetype.is_file(location) and fileutils.file_name(location).lower() == 'composer.json')


def parse(location):
    """
    Return a Package object from a composer.json file or None.
    Note that this is NOT exactly the packagist .json format and this is NOT the
    composer.lock format (allare closely related of course but have important
    (even if minor) differences.
    """
    if not is_phpcomposer_json(location):
        return

    with io.open(location, encoding='utf-8') as loc:
        package_data = json.load(loc, object_pairs_hook=OrderedDict)

    return build_package(package_data)


def build_package(package_data):
    """
    Return a composer Package object from a package data mapping or None.
    """
    # A composer.json without name and description is not a usable PHP
    # composer package. Name and description fields are required but
    # only for published packages:
    # https://getcomposer.org/doc/04-schema.md#name
    # We want to catch both published and non-published packages here.
    # Therefore, we use "private-package-without-a-name" as a package name if
    # there is no name.

    ns_name = package_data.get('name')
    is_private = False
    if not ns_name:
        ns = None
        name = 'private-package-without-a-name'
        is_private = True
    else:
        ns, _, name = ns_name.rpartition('/')

    package = PHPComposerPackage(
        namespace=ns,
        name=name,
    )

    # mapping of top level composer.json items to the Package object field name
    plain_fields = [
        ('version', 'version'),
        ('description', 'summary'),
        ('keywords', 'keywords'),
        ('homepage', 'homepage_url'),
    ]

    for source, target in plain_fields:
        value = package_data.get(source)
        if isinstance(value, string_types):
            value = value.strip()
            if value:
                setattr(package, target, value)

    # mapping of top level composer.json items to a function accepting as
    # arguments the composer.json element value and returning an iterable of
    # key, values Package Object to update
    field_mappers = [
        ('authors', author_mapper),
        ('license', partial(licensing_mapper, is_private=is_private)),
        ('support', support_mapper),
        ('require', partial(_deps_mapper, scope='require', is_runtime=True)),
        ('require-dev', partial(_deps_mapper, scope='require-dev', is_optional=True)),
        ('provide', partial(_deps_mapper, scope='provide', is_runtime=True)),
        ('conflict', partial(_deps_mapper, scope='conflict', is_runtime=True, is_optional=True)),
        ('replace', partial(_deps_mapper, scope='replace', is_runtime=True, is_optional=True)),
        ('suggest', partial(_deps_mapper, scope='suggest', is_runtime=True, is_optional=True)),

    ]

    for source, func in field_mappers:
        logger.debug('parse: %(source)r, %(func)r' % locals())
        value = package_data.get(source)
        if value:
            if isinstance(value, string_types):
                value = value.strip()
            if value:
                func(value, package)
    # Parse vendor from name value
    vendor_mapper(package)
    return package


def licensing_mapper(licenses, package, is_private=False):
    """
    Update package licensing and return package.
    Licensing data structure has evolved over time and is a tad messy.
    https://getcomposer.org/doc/04-schema.md#license
    The value of license is either:
    - an SPDX expression string:  {  "license": "(LGPL-2.1 or GPL-3.0+)" }
    - a list of SPDX license ids choices: "license": ["LGPL-2.1","GPL-3.0+"]

    Some older licenses are plain strings and not SPDX ids. Also if there is no
    license and the `is_private` Fkag is True, we return a "proprietary-license"
    license.
    """
    if not licenses:
        return package

    if isinstance(licenses, list):
        # For a package, when there is a choice between licenses
        # ("disjunctive license"), multiple can be specified as array.
        # build a proper license expression: the defaultfor composer is OR
        lics = [l.strip() for l in licenses if l and l.strip()]
        lics = ' OR '.join(lics)

    elif not isinstance(licenses, string_types):
        lics = repr(licenses)
    else:
        lics = licenses

    if not lics and is_private:
        lics ='proprietary-license'

    package.declared_license = lics or None
    return package


def author_mapper(authors_content, package):
    """
    Update package parties with authors and return package.
    https://getcomposer.org/doc/04-schema.md#authors
    """
    for name, role, email, url in parse_person(authors_content):
        role = role or 'author'
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
        package.parties.append(
            models.Party(type=models.party_person,
                         name=package.namespace, role='vendor'))
    return package


def _deps_mapper(deps, package, scope, is_runtime=False, is_optional=False):
    """
    Handle deps such as dependencies, devDependencies
    return a tuple of (dep type, list of deps)
    https://getcomposer.org/doc/04-schema.md#package-links
    """
    for ns_name, requirement in deps.items():
        ns, _, name = ns_name.rpartition('/')
        purl = models.PackageURL(type='composer', namespace=ns, name=name).to_string()
        dep = models.DependentPackage(
            purl=purl,
            requirement=requirement,
            scope=scope,
            is_runtime=is_runtime,
            is_optional=is_optional)
        package.dependencies.append(dep)
    return package


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
                url and url.strip('() '))
    else:
        raise ValueError('Incorrect PHP composer persons: %(persons)r' % locals())
