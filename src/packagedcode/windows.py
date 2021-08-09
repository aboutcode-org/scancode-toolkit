#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import attr
import xmltodict

from packagedcode import models


# Tracing flags
TRACE = False


def logger_debug(*args):
    pass


if TRACE:
    import logging
    import sys
    logger = logging.getLogger(__name__)
    # logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, str) and a or repr(a) for a in args))


@attr.s()
class MicrosoftUpdateManifestPackage(models.Package):
    extensions = ('.mum',)
    filetypes = ('xml 1.0 document',)
    mimetypes = ('text/xml',)

    default_type = 'windows-update'

    @classmethod
    def recognize(cls, location):
        yield parse(location)


def parse_mum(location):
    """
    Return a dictionary of Microsoft Update Manifest (mum) metadata from a .mum
    file at `location`. Return None if this is not a parsable mum file. Raise
    Exceptions on errors.
    """
    if not location.endswith('.mum'):
        return
    with open(location , 'rb') as loc:
        return xmltodict.parse(loc)


def parse(location):
    """
    Return a MicrosoftUpdateManifestPackage from a .mum XML file at `location`.
    Return None if this is not a parsable .mum file.
    """
    parsed = parse_mum(location)
    if TRACE:
        logger_debug('parsed:', parsed)
    if not parsed:
        return

    assembly = parsed.get('assembly', {})
    description = assembly.get('@description', '')
    company = assembly.get('@company', '')
    copyright = assembly.get('@copyright', '')
    support_url = assembly.get('@supportInformation', '')

    assembly_identity = assembly.get('assemblyIdentity', {})
    name = assembly_identity.get('@name', '')
    version = assembly_identity.get('@version', '')

    parties = []
    if company:
        parties.append(
            models.Party(
                name=company,
                type=models.party_org,
                role='owner',
            )
        )

    return MicrosoftUpdateManifestPackage(
        name=name,
        version=version,
        description=description,
        homepage_url=support_url,
        parties=parties,
        copyright=copyright,
    )
