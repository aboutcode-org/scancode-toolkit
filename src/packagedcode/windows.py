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
from commoncode import filetype


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
class MicrosoftUpdatePackage(models.PackageData):
    extensions = ('.mum',)
    filetypes = ('xml 1.0 document',)
    mimetypes = ('text/xml',)

    default_type = 'windows-update'


@attr.s()
class MicrosoftUpdateManifest(MicrosoftUpdatePackage, models.PackageDataFile):

    @classmethod
    def is_package_data_file(cls, location):
        """
        Return True if the file at ``location`` is likely a manifest of this type.
        """
        return filetype.is_file(location) and location.endswith('.mum')

    @classmethod
    def recognize(cls, location):
        """
        Yield one or more Package manifest objects given a file ``location`` pointing to a
        package archive, manifest or similar.
        """
        with open(location , 'rb') as loc:
            parsed = xmltodict.parse(loc)

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

        yield cls(
            name=name,
            version=version,
            description=description,
            homepage_url=support_url,
            parties=parties,
            copyright=copyright,
        )
