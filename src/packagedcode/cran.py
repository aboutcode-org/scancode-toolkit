
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import io
import logging

import attr
import saneyaml

from commoncode import filetype
from commoncode import fileutils
from packagedcode import models
from packageurl import PackageURL


"""
Handle CRAN package.
R is a programming languages and CRAN its package repository.
https://cran.r-project.org/
"""

TRACE = False

logger = logging.getLogger(__name__)

if TRACE:
    import sys
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)


@attr.s()
class CranPackageData(models.PackageData):
    default_type = 'cran'
    default_web_baseurl = 'https://cran.r-project.org/package='

    @classmethod
    def get_package_root(cls, manifest_resource, codebase):
        return manifest_resource.parent(codebase)

    def repository_homepage_url(self, baseurl=default_web_baseurl):
        return '{}{}'.format(baseurl, self.name)


@attr.s()
class DescriptionFile(CranPackageData, models.PackageDataFile):

    file_patterns = ('DESCRIPTION',)

    @classmethod
    def is_package_data_file(cls, location):
        """
        Return True if `location` path is for a Cran DESCRIPTION file.
        """
        return (filetype.is_file(location)
            and fileutils.file_name(location) == 'DESCRIPTION')

    @classmethod
    def recognize(cls, location):
        """
        Yield one or more Package manifest objects given a file ``location`` pointing to a
        package archive, manifest or similar.
        """
        package_data = get_yaml_data(location)

        name = package_data.get('Package')
        if name:
            parties = []
            maintainers = package_data.get('Maintainer')
            if maintainers:
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
            authors = package_data.get('Author')
            if authors:
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
            dependencies = package_data.get('Depends')
            if dependencies:
                for dependency in dependencies.split(',\n'):
                    requirement = None
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
            yield cls(
                name=name,
                version=package_data.get('Version'),
                description=package_data.get('Description', '') or package_data.get('Title', ''),
                declared_license=package_data.get('License'),
                parties=parties,
                dependencies=package_dependencies,
                # TODO: Let's handle the release date as a Date type
                # release_date = package_data.get('Date/Publication'),
            )


@attr.s()
class CranPackage(CranPackageData, models.Package):
    """
    A cran Package that is created out of one/multiple cran package
    manifests.
    """

    @property
    def manifests(self):
        return [
            DescriptionFile
        ]


def get_yaml_data(location):
    """
    Parse the yaml file and return the metadata in dictionary format.
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
