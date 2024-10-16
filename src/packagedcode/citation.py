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
Handle CITATION.cff files, see https://citation-file-format.github.io/
https://github.com/citation-file-format/citation-file-format/blob/main/schema-guide.md

See https://github.com/citation-file-format/citation-file-format/tree/main/examples/1.2.0/pass for examples.
"""

class CitationHandler(models.DatafileHandler):
    datasource_id = 'citation_cff'
    default_package_type = 'citation'
    path_patterns = ('*/CITATION.cff',)
    description = 'Citation file format'
    documentation_url = 'https://citation-file-format.github.io/'

    @classmethod
    def parse(cls, location):
        metayaml = get_cff_data(location)
        title = metayaml.get('title')
        abstract = metayaml.get('abstract')
        keywords = metayaml.get('keywords')
        release_date = metayaml.get('date-released')
        # This is the version of the software/item and not cff-version
        version = metayaml.get('version')
        parties = []
        authors = metayaml.get('authors')
        if authors:
            for author in authors:
                name = author.get('family-names') or author.get('name')
                email = author.get('email')
                url = author.get('orcid')
                parties.append(models.Party(
                    name=name,
                    email=email,
                    url=url
                ))
        repository_homepage_url = metayaml.get('repository')
        repository_download_url = metayaml.get('repository-code')
        extracted_license_statement = metayaml.get('license')
        homepage_url = metayaml.get('url')

        yield models.PackageData(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            name=title,
            description=abstract,
            keywords=keywords,
            release_date=release_date,
            parties=parties,
            version=version,
            repository_homepage_url=repository_homepage_url,
            repository_download_url=repository_download_url,
            extracted_license_statement=extracted_license_statement,
            homepage_url=homepage_url
          )


def get_cff_data(location):
    """
    Return a mapping of yaml/cff data loaded from a CITATION.cff files.
    """

    # TODO: Should this be Jinja-based?
    yaml_lines = []
    with io.open(location, encoding='utf-8') as citationcff:
        for line in citationcff:
            if not line:
                continue
            yaml_lines.append(line)

    return saneyaml.load('\n'.join(yaml_lines))


