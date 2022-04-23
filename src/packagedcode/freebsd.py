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

import saneyaml

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

# see also https://github.com/freebsd/pkg#the-metadata
# TODO: use the libucl Python binding
# TODO: support +MANIFETS and its file references


class CompactManifestHandler(models.DatafileHandler):
    datasource_id = 'freebsd_compact_manifest'
    path_patterns = ('*/+COMPACT_MANIFEST',)
    default_package_type = 'freebsd'
    description = 'FreeBSD compact package manifest'
    documentation_url = 'https://www.freebsd.org/cgi/man.cgi?pkg-create(8)#MANIFEST_FILE_DETAILS'

    @classmethod
    def parse(cls, location):
        """
        Yield one or more Package manifest objects given a file ``location`` pointing to a
        package archive, manifest or similar.
        """
        with io.open(location, encoding='utf-8') as loc:
            freebsd_manifest = saneyaml.load(loc)

        package_data = models.PackageData(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            qualifiers=dict(
                arch=freebsd_manifest.get('arch'),
                origin=freebsd_manifest.get('origin'),
            )
        )

        # mapping of top level manifest items to the PackageData object field name
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
                    setattr(package_data, target, value)

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
                func(value, package_data)

        # license_mapper needs multiple fields
        license_mapper(freebsd_manifest, package_data)

        if package_data.declared_license:
            package_data.license_expression = cls.compute_normalized_license(package_data)

        yield package_data

    @classmethod
    def compute_normalized_license(cls, package):
        """
        Return a normalized license expression string or None detected from a ``package`` Package
        declared license items or an ordered dict.
        """
        declared_license = package.declared_license
        if not declared_license:
            return

        if not isinstance(declared_license, dict):
            return models.compute_normalized_license(declared_license=declared_license)

        licenses = declared_license.get('licenses')
        if not licenses:
            return

        license_logic = declared_license.get('licenselogic')
        # the default in FreebSD expressions is AND
        relation = 'AND'
        if license_logic:
            if license_logic == 'or' or license_logic == 'dual':
                relation = 'OR'

        detected_licenses = []
        for lic in licenses:
            detected = models.compute_normalized_license(declared_license=lic)
            if detected:
                detected_licenses.append(detected)

        if detected_licenses:
            return combine_expressions(expressions=detected_licenses, relation=relation)


def license_mapper(freebsd_manifest, package):
    """
    Update ``package`` Package declared licensing using ``freebsd_manifest`` and
    return package. Licensing structure for FreeBSD packages is a list of
    FreeBSD own license keys and a 'licenselogic' field.
    """
    licenses = freebsd_manifest.get('licenses')

    if not licenses:
        return

    declared_license = {}
    lics = [l.strip() for l in licenses if l and l.strip()]
    declared_license['licenses'] = lics

    license_logic = freebsd_manifest.get('licenselogic')
    if license_logic:
        declared_license['licenselogic'] = license_logic

    package.declared_license = declared_license
    return


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
    # TODO: the origin may need to be the namespace??
    package.qualifiers['origin'] = origin
    package.code_view_url = f'https://svnweb.freebsd.org/ports/head/{origin}'
    return package


def arch_mapper(arch, package):
    """
    Update package download_url using FreeBSD arch information and return package.
    """
    # the 'arch' field allows us to craft a binary download_url
    # FIXME: due to the rolling-release nature of binary ports, some download URLs
    # will lead to 404 errors if a newer release of a particular port is availible
    package.download_url = f'https://pkg.freebsd.org/{arch}/latest/All/{package.name}-{package.version}.txz'
    return package
