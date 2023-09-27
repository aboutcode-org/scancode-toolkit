#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import xmltodict

from packagedcode import models


class MicrosoftUpdateManifestHandler(models.NonAssemblableDatafileHandler):
    datasource_id = 'microsoft_update_manifest_mum'
    path_patterns = ('*.mum',)
    filetypes = ('xml 1.0 document',)
    default_package_type = 'windows-update'
    description = 'Microsoft Update Manifest .mum file'

    @classmethod
    def parse(cls, location, purl_only=False):
        with open(location , 'rb') as loc:
            parsed = xmltodict.parse(loc)

        if not parsed:
            return

        assembly = parsed.get('assembly', {})
        assembly_identity = assembly.get('assemblyIdentity', {})
        package = models.PackageData(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            name=assembly_identity.get('@name', ''),
            version=assembly_identity.get('@version', ''),
        )
        if purl_only:
            yield package
            return

        package.description = assembly.get('@description', '')
        company = assembly.get('@company', '')
        package.copyright = assembly.get('@copyright', '')
        package.homepage_url = assembly.get('@supportInformation', '')

        parties = []
        if company:
            parties.append(
                models.Party(
                    name=company,
                    type=models.party_org,
                    role='owner',
                )
            )
        package.parties = parties
        package.populate_holder_field()
        yield package
