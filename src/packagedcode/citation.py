#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

"""
Handle Citation File Format (CFF) files.

Citation File Format is a human- and machine-readable format for providing
citation metadata for software and datasets. CITATION.cff files are YAML 1.2
files placed in repository roots to provide structured citation information.

This mirrors how other YAML-based metadata files are handled in ScanCode.
"""

import logging
import os
import sys

import yaml

from packagedcode import models

TRACE = os.environ.get('SCANCODE_DEBUG_PACKAGE_CITATION', False)


def logger_debug(*args):
    pass


logger = logging.getLogger(__name__)

if TRACE:
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, str) and a or repr(a) for a in args))


class CitationFileHandler(models.DatafileHandler):
    datasource_id = 'citation_cff'
    path_patterns = ('*/CITATION.cff',)
    default_package_type = 'generic'
    default_primary_language = None
    description = 'Citation File Format (CFF) metadata'
    documentation_url = 'https://citation-file-format.github.io/'

    @classmethod
    def parse(cls, location, package_only=False):
        """
        Yield PackageData from a CITATION.cff file.
        
        Best-effort extraction: parse what exists, don't crash on missing fields.
        Only hard requirement is cff-version field.
        """
        try:
            with open(location, 'r', encoding='utf-8') as f:
                cff_data = yaml.safe_load(f)
        except (yaml.YAMLError, UnicodeDecodeError, IOError) as e:
            # Invalid YAML or file read error - return nothing (silent skip)
            if TRACE:
                logger_debug(f'Error parsing CITATION.cff at {location}: {e}')
            return

        if not isinstance(cff_data, dict):
            # Not a valid CFF structure - return nothing
            if TRACE:
                logger_debug(f'CFF data is not a dictionary at {location}')
            return

        # Hard requirement: cff-version must exist
        cff_version = cff_data.get('cff-version')
        if not cff_version:
            if TRACE:
                logger_debug(f'Missing required cff-version field at {location}')
            return

        # Extract basic metadata - all soft requirements
        title = cff_data.get('title', '').strip()
        version = cff_data.get('version', '').strip()
        
        # Prefer abstract, fallback to message for description
        abstract = cff_data.get('abstract', '').strip()
        message = cff_data.get('message', '').strip()
        description = abstract or message or ''

        # Extract authors and convert to Party objects
        authors = cff_data.get('authors', [])
        parties = list(get_parties(authors, party_role='author'))

        # Extract license
        license_value = cff_data.get('license')
        extracted_license_statement = None
        if license_value:
            # CFF license may be free-form text or SPDX identifier
            # We store as extracted_license_statement to avoid asserting SPDX correctness
            if isinstance(license_value, str):
                extracted_license_statement = license_value.strip()
            elif isinstance(license_value, dict):
                # Some CFF files may use structured license objects with 'name' key
                extracted_license_statement = license_value.get('name') or repr(license_value)

        # Extract keywords
        keywords = cff_data.get('keywords', [])
        if not isinstance(keywords, list):
            keywords = []

        # Extract URLs
        homepage_url = cff_data.get('url', '').strip() or None
        # Only use standard CFF field 'repository-code' for version control URL
        vcs_url = cff_data.get('repository-code', '').strip() or None

        # Store additional metadata  in extra_data
        extra_data = {}
        
        # Store cff-version
        extra_data['cff_version'] = cff_version
        
        # Store CFF type if present (e.g., "software", "dataset")
        cff_type = cff_data.get('type')
        if cff_type:
            extra_data['cff_type'] = cff_type

        # Store date-released
        date_released = cff_data.get('date-released')
        if date_released:
            extra_data['date_released'] = str(date_released)

        # Store DOI
        doi = cff_data.get('doi')
        if doi:
            extra_data['doi'] = doi

        # Store identifiers
        identifiers = cff_data.get('identifiers', [])
        if identifiers and isinstance(identifiers, list):
            extra_data['identifiers'] = identifiers

        # Build package data
        package_data = dict(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            name=title or None,
            version=version or None,
            description=description or None,
            extracted_license_statement=extracted_license_statement,
            keywords=keywords,
            parties=parties if parties else None,
            homepage_url=homepage_url,
            vcs_url=vcs_url,
            extra_data=extra_data if extra_data else None,
        )

        yield models.PackageData.from_data(package_data, package_only)


def get_parties(authors, party_role='author'):
    """
    Yield Party objects from a list of CFF author entries.
    
    CFF supports multiple author formats:
    - family-names + given-names
    - name (single string)
    - family-names only
    - given-names only
    - with optional orcid
    
    Skip malformed entries, continue with others (best-effort).
    """
    if not isinstance(authors, list):
        return []

    for author_entry in authors:
        if not isinstance(author_entry, dict):
            # Skip non-dict entries (best-effort parsing)
            if TRACE:
                logger_debug(f'Skipping non-dict author entry: {author_entry}')
            continue

        # Extract name components
        family_names = author_entry.get('family-names', '').strip()
        given_names = author_entry.get('given-names', '').strip()
        name_field = author_entry.get('name', '').strip()

        # Build full name
        name = None
        if name_field:
            # Use single name field if present
            name = name_field
        elif family_names and given_names:
            # Combine family and given names
            name = f'{given_names} {family_names}'
        elif family_names:
            # Family names only
            name = family_names
        elif given_names:
            # Given names only  
            name = given_names

        if not name:
            # Skip entries with no usable name
            if TRACE:
                logger_debug(f'Skipping author entry with no name: {author_entry}')
            continue

        # Extract email
        email = author_entry.get('email', '').strip() or None

        # Extract ORCID and store in extra_data
        party_extra_data = {}
        orcid = author_entry.get('orcid')
        if orcid:
            party_extra_data['orcid'] = orcid

        affiliation = author_entry.get('affiliation')
        if affiliation:
            party_extra_data['affiliation'] = affiliation

        yield models.Party(
            type=models.party_person,
            name=name,
            role=party_role,
            email=email,
            extra_data=party_extra_data if party_extra_data else None,
        ).to_dict()
