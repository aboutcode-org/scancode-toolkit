#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import io
import logging

import attr
import saneyaml

from commoncode import filetype
from commoncode import fileutils
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
    file_patterns = ('+COMPACT_MANIFEST',)
    default_type = 'freebsd'

    @classmethod
    def get_package_root(cls, manifest_resource, codebase):
        return manifest_resource.parent(codebase)

    def compute_normalized_license(self):
        return compute_normalized_license(self.declared_license)


@attr.s()
class CompactManifest(FreeBSDPackage, models.PackageManifest):

    file_patterns = ('+COMPACT_MANIFEST',)

    @classmethod
    def is_manifest(cls, location):
        """
        Return True if the file at ``location`` is likely a manifest of this type.
        """
        return (filetype.is_file(location)
            and fileutils.file_name(location).lower() == '+compact_manifest')

    @classmethod
    def recognize(cls, location):
        """
        Yield one or more Package manifest objects given a file ``location`` pointing to a
        package archive, manifest or similar.
        """
        with io.open(location, encoding='utf-8') as loc:
            freebsd_manifest = saneyaml.load(loc)

        # construct the package
        package = cls()

        # add freebsd-specific package 'qualifiers'
        qualifiers = dict([
            ('arch', freebsd_manifest.get('arch')),
            ('origin', freebsd_manifest.get('origin')),
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
            value = freebsd_manifest.get(source)
            if value:
                if isinstance(value, str):
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
            value = freebsd_manifest.get(source) or None
            if value:
                func(value, package)

        # license_mapper needs multiple fields
        license_mapper(freebsd_manifest, package)

        yield package


@attr.s()
class FreebsdPackageInstance(FreeBSDPackage, models.PackageInstance):
    """
    A Freebsd PackageInstance that is created out of one/multiple Freebsd package
    manifests and package-like data, with it's files.
    """

    @property
    def manifests(self):
        return [
            CompactManifest
        ]


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


def license_mapper(package_data, package):
    """
    Update package licensing and return package. Licensing structure for FreeBSD
    packages is a list of (non-scancode) license keys and a 'licenselogic' field.
    """
    license_logic, licenses = package_data.get('licenselogic'), package_data.get('licenses')

    if not licenses:
        return

    declared_license = {}
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
