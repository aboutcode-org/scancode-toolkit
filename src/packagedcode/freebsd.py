#
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
import io
import logging

import attr
from six import string_types

from commoncode import filetype
from commoncode import fileutils
from commoncode import saneyaml
from packagedcode import models
from packagedcode.utils import combine_expressions

"""
Handle FreeBSD ports
per https://www.freebsd.org/cgi/man.cgi?pkg-create(8)
"""

TRACE = False

logger = logging.getLogger(__name__)

if TRACE:
    import sys
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    logger.setLevel(logging.DEBUG)


@attr.s()
class FreeBSDPackage(models.Package):
    metafiles = ('+COMPACT_MANIFEST',)
    default_type = 'freebsd'

    @classmethod
    def recognize(cls, location):
        yield parse(location)

    @classmethod
    def get_package_root(cls, manifest_resource, codebase):
        return manifest_resource.parent(codebase)

    def compute_normalized_license(self):
        return compute_normalized_license(self.declared_license)


def compute_normalized_license(declared_license):
    """
    Return a normalized license expression string detected from a list of
    declared license items or an ordered dict.
    """
    if not declared_license:
        return

    licenses = declared_license.get('licenses')
    if not licenses:
        return

    license_logic = declared_license.get('licenselogic')
    relation = 'AND'
    if license_logic:
        if license_logic == 'or' or license_logic == 'dual':
            relation = 'OR'

    detected_licenses = []
    for declared in licenses:
        detected_license = models.compute_normalized_license(declared)
        if detected_license:
            detected_licenses.append(detected_license)

    if detected_licenses:
        return combine_expressions(detected_licenses, relation)


def is_freebsd_manifest(location):
    return (filetype.is_file(location)
            and fileutils.file_name(location).lower() == '+compact_manifest')


def parse(location):
    """
    Return a Package object from a +COMPACT_MANIFEST file or None.
    """
    if not is_freebsd_manifest(location):
        return

    with io.open(location, encoding='utf-8') as loc:
        freebsd_manifest = saneyaml.load(loc)

    return build_package(freebsd_manifest)


def build_package(package_data):
    """
    Return a Package object from a package_data mapping (from a
    +COMPACT_MANIFEST file or similar) or None.
    """
    # construct the package
    package = FreeBSDPackage()

    # add freebsd-specific package 'qualifiers'
    qualifiers = OrderedDict([
        ('arch', package_data.get('arch')),
        ('origin', package_data.get('origin')),
    ])
    package.qualifiers = qualifiers

    # mapping of top level package.json items to the Package object field name
    plain_fields = [
        ('name', 'name'),
        ('version', 'version'),
        ('www', 'homepage_url'),
        ('desc', 'description'),
        ('categories', 'keywords'),
    ]

    for source, target in plain_fields:
        value = package_data.get(source)
        if value:
            if isinstance(value, string_types):
                value = value.strip()
            if value:
                setattr(package, target, value)

    # mapping of top level +COMPACT_MANIFEST items to a function accepting as
    # arguments the package.json element value and returning an iterable of key,
    # values Package Object to update
    field_mappers = [
        ('maintainer', maintainer_mapper),
        ('origin', origin_mapper),
        ('arch', arch_mapper),
    ]

    for source, func in field_mappers:
        logger.debug('parse: %(source)r, %(func)r' % locals())
        value = package_data.get(source) or None
        if value:
            func(value, package)

    # license_mapper needs multiple fields
    license_mapper(package_data, package)

    return package


def license_mapper(package_data, package):
    """
    Update package licensing and return package. Licensing structure for FreeBSD
    packages is a list of (non-scancode) license keys and a 'licenselogic' field.
    """
    license_logic, licenses = package_data.get('licenselogic'), package_data.get('licenses')

    if not licenses:
        return

    declared_license = OrderedDict()
    lics = [l.strip() for l in licenses if l and l.strip()]
    declared_license['licenses'] = lics
    if license_logic:
        declared_license['licenselogic'] = license_logic

    package.declared_license = declared_license
    return package


def maintainer_mapper(maintainer, package):
    """
    Update package parties with FreeBSD port maintainer and return package.
    """
    # maintainer in this case is just an email
    package.parties.append(models.Party(email=maintainer, role='maintainer', type=models.party_person))
    return package


def origin_mapper(origin, package):
    """
    Update package code_view_url using FreeBSD origin information and return package.
    """
    # the 'origin' field allows us to craft a code_view_url
    package.qualifiers['origin'] = origin
    package.code_view_url = 'https://svnweb.freebsd.org/ports/head/{}'.format(origin)


def arch_mapper(arch, package):
    """
    Update package download_url using FreeBSD arch information and return package.
    """
    # the 'arch' field allows us to craft a binary download_url
    # FIXME: due to the rolling-release nature of binary ports, some download URLs
    # will lead to 404 errors if a newer release of a particular port is availible
    package.download_url = 'https://pkg.freebsd.org/{}/latest/All/{}-{}.txz'.format(arch, package.name, package.version)
    return package
