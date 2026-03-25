#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import logging
import os

import saneyaml

from packagedcode import models

"""
Handle publiccode.yml metadata files.
publiccode.yml is a metadata standard for public sector open source software.
See https://github.com/publiccodeyml/publiccode.yml
"""

TRACE = os.environ.get('SCANCODE_DEBUG_PACKAGE', False)

logger = logging.getLogger(__name__)


class PubliccodeYmlHandler(models.DatafileHandler):
    datasource_id = 'publiccode_yml'
    path_patterns = ('*/publiccode.yml', '*/publiccode.yaml')
    default_package_type = 'publiccode'
    default_primary_language = None
    description = 'publiccode.yml metadata file'
    documentation_url = 'https://github.com/publiccodeyml/publiccode.yml'

    @classmethod
    def parse(cls, location, package_only=False):
        with open(location, 'rb') as f:
            data = saneyaml.load(f.read())

        if not data or not isinstance(data, dict):
            return

        # Validate: a publiccode.yml must have 'publiccodeYmlVersion'
        if 'publiccodeYmlVersion' not in data:
            return

        name = data.get('name')
        version = data.get('softwareVersion')
        vcs_url = data.get('url')
        homepage_url = data.get('landingURL') or vcs_url

        # License is under legal.license (SPDX expression)
        legal = data.get('legal') or {}
        declared_license = legal.get('license')
        copyright_statement = legal.get('mainCopyrightOwner') or legal.get('repoOwner')

        # Description: prefer English, fall back to first available language
        description = _get_description(data)

        # Keywords from categories
        categories = data.get('categories') or []
        keywords = ', '.join(categories) if categories else None

        # Parties from maintenance.contacts
        parties = []
        maintenance = data.get('maintenance') or {}
        for contact in maintenance.get('contacts') or []:
            contact_name = contact.get('name')
            contact_email = contact.get('email')
            if contact_name or contact_email:
                parties.append(
                    models.Party(
                        type=models.party_person,
                        name=contact_name,
                        email=contact_email,
                        role='maintainer',
                    )
                )

        # Extra data
        extra_data = {}
        schema_version = data.get('publiccodeYmlVersion')
        if schema_version:
            extra_data['publiccodeYmlVersion'] = schema_version
        platforms = data.get('platforms')
        if platforms:
            extra_data['platforms'] = platforms
        development_status = data.get('developmentStatus')
        if development_status:
            extra_data['developmentStatus'] = development_status
        software_type = data.get('softwareType')
        if software_type:
            extra_data['softwareType'] = software_type

        yield models.PackageData(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            name=name,
            version=version,
            vcs_url=vcs_url,
            homepage_url=homepage_url,
            description=description,
            declared_license_expression=declared_license,
            copyright=copyright_statement,
            keywords=keywords,
            parties=parties,
            extra_data=extra_data or None,
        )


def _get_description(data):
    """
    Extract the best available description from publiccode.yml's
    multilingual 'description' block. Prefer English, fall back to
    any available language. Returns longDescription, else shortDescription.
    """
    description_block = data.get('description') or {}
    if not description_block:
        return

    lang_data = (
        description_block.get('en')
        or description_block.get('eng')
        or next(iter(description_block.values()), None)
    )
    if not lang_data:
        return

    long_desc = lang_data.get('longDescription', '').strip()
    short_desc = lang_data.get('shortDescription', '').strip()

    return long_desc or short_desc or None
