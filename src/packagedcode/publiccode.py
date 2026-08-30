#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import io

import saneyaml

from packagedcode import models

"""
Handle publiccode.yml metadata files.
publiccode.yml is a metadata standard for public sector open source software.
See https://github.com/publiccodeyml/publiccode.yml
"""

EXTRA_DATA_KEYS = (
    'publiccodeYmlVersion',
    'platforms',
    'developmentStatus',
    'softwareType',
)


class PubliccodeYmlHandler(models.DatafileHandler):
    datasource_id = 'publiccode_yml'
    path_patterns = ('*publiccode.yml', '*publiccode.yaml')
    default_package_type = 'publiccode'
    default_primary_language = None
    description = 'publiccode.yml metadata file'
    documentation_url = 'https://github.com/publiccodeyml/publiccode.yml'

    @classmethod
    def parse(cls, location, package_only=False):
        with io.open(location, encoding='utf-8') as loc:
            data = saneyaml.load(loc.read())

        if not is_publiccode_yml_data(data):
            return

        package_data = dict(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            name=data.get('name'),
            version=data.get('softwareVersion'),
            vcs_url=data.get('url'),
            homepage_url=data.get('landingURL') or data.get('url'),
            description=get_description(data),
            extracted_license_statement=get_extracted_license_statement(data),
            copyright=get_copyright_statement(data),
            keywords=get_categories(data),
            parties=get_parties(data),
            extra_data=get_extra_data(data) or None,
        )
        yield models.PackageData.from_data(package_data, package_only)


def is_publiccode_yml_data(data):
    return isinstance(data, dict) and 'publiccodeYmlVersion' in data


def get_description(data):
    """
    Extract the best available description from publiccode.yml's
    multilingual 'description' block. Prefer English, fall back to
    any available language. Returns longDescription, else shortDescription.
    """
    description_block = data.get('description') or {}
    if not description_block:
        return

    lang_data = None
    for language, localized_description in description_block.items():
        primary_language = language.lower().split('-')[0]
        if primary_language == 'en':
            lang_data = localized_description
            break

    if not lang_data:
        lang_data = next(iter(description_block.values()), None)

    if not lang_data:
        return

    long_desc = lang_data.get('longDescription', '').strip()
    short_desc = lang_data.get('shortDescription', '').strip()

    return long_desc or short_desc or None


def get_extracted_license_statement(data):
    legal = data.get('legal') or {}
    return legal.get('license')


def get_copyright_statement(data):
    legal = data.get('legal') or {}
    copyright_holders = []

    for key in ('mainCopyrightOwner', 'repoOwner'):
        value = legal.get(key)
        if value and value not in copyright_holders:
            copyright_holders.append(value)

    return '\n'.join(copyright_holders) or None


def get_categories(data):
    categories = data.get('categories') or []
    if isinstance(categories, str):
        return [categories]
    return categories


def get_parties(data):
    parties = []
    maintenance = data.get('maintenance') or {}

    for contact in maintenance.get('contacts') or []:
        contact_name = contact.get('name')
        contact_email = contact.get('email')

        if not (contact_name or contact_email):
            continue

        parties.append(
            models.Party(
                type=models.party_person,
                name=contact_name,
                email=contact_email,
                role='maintainer',
            )
        )

    return parties


def get_extra_data(data):
    extra_data = {}

    for key in EXTRA_DATA_KEYS:
        value = data.get(key)
        if value:
            extra_data[key] = value

    return extra_data
