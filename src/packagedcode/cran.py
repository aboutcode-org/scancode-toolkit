
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import io

import saneyaml
from packageurl import PackageURL

from packagedcode import models

"""
Handle CRAN packages.
R is a programming languages and CRAN is its package repository.
See https://cran.r-project.org/
"""


class CranDescriptionFileHandler(models.DatafileHandler):
    datasource_id = 'cran_description'
    default_package_type = 'cran'
    path_patterns = ('*/DESCRIPTION',)
    default_primary_language = 'R'
    description = 'CRAN package DESCRIPTION'
    documentation_url = 'https://r-pkgs.org/description.html'

    @classmethod
    def parse(cls, location):
        cran_desc = get_cran_description(location)

        name = cran_desc.get('Package')
        if not name:
            return

        parties = []
        maintainers = cran_desc.get('Maintainer') or ''
        for maintainer in maintainers.split(',\n'):
            maintainer_name, maintainer_email = get_party_info(maintainer)
            if maintainer_name or maintainer_email:
                parties.append(
                    models.Party(
                        name=maintainer_name,
                        role='maintainer',
                        email=maintainer_email,
                    )
                )

        authors = cran_desc.get('Author') or ''
        for author in authors.split(',\n'):
            author_name, author_email = get_party_info(author)
            if author_name or author_email:
                parties.append(
                    models.Party(
                        name=author_name,
                        role='author',
                        email=author_email,
                    )
                )

        package_dependencies = []
        dependencies = cran_desc.get('Depends') or ''
        for dependency in dependencies.split(',\n'):
            requirement = None
            # TODO: IMHO we could do simpler and better here

            for splitter in ('==', '>=', '<=', '>', '<'):
                if splitter in dependency:
                    splits = dependency.split(splitter)
                    # Replace the package name and keep the relationship and version
                    # For example: R (>= 2.1)
                    requirement = dependency.replace(splits[0], '').strip().strip(')').strip()
                    dependency = splits[0].strip().strip('(').strip()
                    break

            package_dependencies.append(
                models.DependentPackage(
                    purl=PackageURL(
                        type='cran', name=dependency).to_string(),
                    extracted_requirement=requirement,
                    scope='dependencies',
                    is_runtime=True,
                    is_optional=False,
                )
            )

        declared_license=cran_desc.get('License')
        license_expression = None
        if declared_license:
            license_expression = models.compute_normalized_license(declared_license)

        # TODO: Let's handle the release date as a Date type
        # release_date = cran_desc.get('Date/Publication'),

        yield models.PackageData(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            name=name,
            version=cran_desc.get('Version'),
            # TODO: combine both together
            description=cran_desc.get('Description', '') or cran_desc.get('Title', ''),
            declared_license=declared_license,
            license_expression=license_expression,
            parties=parties,
            dependencies=package_dependencies,
            repository_homepage_url=f'https://cran.r-project.org/package={name}',
        )

# FIXME: THIS IS NOT YAML but RFC 822


def get_cran_description(location):
    """
    Parse a CRAN DESCRIPTION file as YAML and return a mapping of metadata.
    """
    yaml_lines = []
    with io.open(location, encoding='utf-8') as loc:
        for line in loc.readlines():
            if not line:
                continue
            yaml_lines.append(line)
    return saneyaml.load('\n'.join(yaml_lines))


def get_party_info(info):
    """
    Parse the info and return name, email.
    """
    if not info:
        return
    if '@' in info and '<' in info:
        splits = info.strip().strip(',').strip('>').split('<')
        name = splits[0].strip()
        email = splits[1].strip()
    else:
        name = info
        email = None
    return name, email
