#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import io
import os
import logging

import saneyaml

from packagedcode import models

"""
Handle FreeBSD ports
per https://www.freebsd.org/cgi/man.cgi?pkg-create(8)
"""
SCANCODE_DEBUG_PACKAGE = os.environ.get('SCANCODE_DEBUG_PACKAGE', False)
TRACE = SCANCODE_DEBUG_PACKAGE


def logger_debug(*args):
    pass


logger = logging.getLogger(__name__)

if TRACE:
    import sys
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(
            ' '.join(isinstance(a, str) and a or repr(a) for a in args)
        )

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
    def _parse(cls, yaml_data, purl_only=False):
        package_data = models.PackageData(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            qualifiers=dict(
                arch=yaml_data.get('arch'),
                origin=yaml_data.get('origin'),
            )
        )

        # mapping of top level manifest items to the PackageData object field name
        purl_fields = [
            ('name', 'name'),
            ('version', 'version'),
        ]

        for source, target in purl_fields:
            value = yaml_data.get(source)
            if value:
                if isinstance(value, str):
                    value = value.strip()
                if value:
                    setattr(package_data, target, value)

        if purl_only:
            return package_data

        plain_fields = [
            ('www', 'homepage_url'),
            ('desc', 'description'),
            ('categories', 'keywords'),
        ]

        for source, target in plain_fields:
            value = yaml_data.get(source)
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
            value = yaml_data.get(source) or None
            if value:
                func(value, package_data)

        # license_mapper needs multiple fields
        license_mapper(yaml_data, package_data)
        cls.populate_license_fields(package_data)

        if TRACE:
            logger_debug(
                f"package_data: {package_data}"
            )

        return package_data

    @classmethod
    def parse(cls, location, purl_only=False):
        """
        Yield one or more Package manifest objects given a file ``location``
        pointing to a package archive, manifest or similar.
        """
        with io.open(location, encoding='utf-8') as loc:
            yaml_data = saneyaml.load(loc)

        yield cls._parse(yaml_data=yaml_data, purl_only=purl_only)

    @staticmethod
    def get_license_detections_and_expression(package_data):

        from packagedcode.licensing import get_license_detections_and_expression
        from packagedcode.licensing import get_license_detections_for_extracted_license_statement
        from packagedcode.licensing import get_mapping_and_expression_from_detections

        detections = []
        expression = None

        if not package_data.extracted_license_statement:
            return detections, expression

        if not isinstance(package_data.extracted_license_statement, dict):
            return get_license_detections_and_expression(package_data.extracted_license_statement)

        licenses = package_data.extracted_license_statement.get('licenses')
        if not licenses:
            return detections, expression

        license_logic = package_data.extracted_license_statement.get('licenselogic')
        relation = 'AND'
        if license_logic:
            if license_logic == 'or' or license_logic == 'dual':
                relation = 'OR'

        for lic in licenses:
            detected = get_license_detections_for_extracted_license_statement(extracted_license_statement=lic)
            if detected:
                detections.extend(detected)

        if TRACE:
            logger_debug(
                f"licenses: {licenses}"
            )
            logger_debug(
                f"detections: {detections}"
            )

        return get_mapping_and_expression_from_detections(
            license_detections=detections,
            relation=relation,
        )


def license_mapper(freebsd_manifest, package):
    """
    Update ``package`` Package declared licensing using ``freebsd_manifest`` and
    return package. Licensing structure for FreeBSD packages is a list of
    FreeBSD own license keys and a 'licenselogic' field.
    """
    licenses = freebsd_manifest.get('licenses')

    if not licenses:
        return

    extracted_license_statement = {}
    lics = [l.strip() for l in licenses if l and l.strip()]
    extracted_license_statement['licenses'] = lics

    license_logic = freebsd_manifest.get('licenselogic')
    if license_logic:
        extracted_license_statement['licenselogic'] = license_logic

    package.extracted_license_statement = extracted_license_statement
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
