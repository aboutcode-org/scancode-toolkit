
# Copyright (c) 2019 nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/scancode-toolkit/
# The ScanCode software is licensed under the Apache License version 2.0.
# Data generated with ScanCode require an acknowledgment.
# ScanCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# When you publish or redistribute any data created with ScanCode or any ScanCode
# derivative work, you must accompany this data with the following acknowledgment:
#
#  Generated with ScanCode and provided on an "AS IS" BASIS, WITHOUT WARRANTIES
#  OR CONDITIONS OF ANY KIND, either express or implied. No content created from
#  ScanCode should be considered or used as legal advice. Consult an Attorney
#  for any legal advice.
#  ScanCode is a free software code scanning tool from nexB Inc. and others.
#  Visit https://github.com/nexB/scancode-toolkit/ for support and download.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import io
import logging

import attr
import saneyaml

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
class CranPackage(models.Package):
    metafiles = ('DESCRIPTION',)
    default_type = 'cran'
    default_web_baseurl = 'https://cran.r-project.org/package='

    @classmethod
    def recognize(cls, location):
        yield parse(location)

    @classmethod
    def get_package_root(cls, manifest_resource, codebase):
        return manifest_resource.parent(codebase)

    def repository_homepage_url(self, baseurl=default_web_baseurl):
        return '{}{}'.format(baseurl, self.name)


def parse(location):
    """
    Return a Package object from a DESCRIPTION file or None.
    """
    yaml_data = get_yaml_data(location)
    return build_package(yaml_data)


def build_package(package_data):
    """
    Return a cran Package object from a dictionary yaml data.
    """
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
                        requirement=requirement,
                        scope='dependencies',
                        is_runtime=True,
                        is_optional=False,
                    )
                )
        package = CranPackage(
            name=name,
            version=package_data.get('Version'),
            description=package_data.get('Description', '') or package_data.get('Title', ''),
            declared_license=package_data.get('License'),
            parties=parties,
            dependencies=package_dependencies,
            # TODO: Let's handle the release date as a Date type
            # release_date = package_data.get('Date/Publication'),
        )
        return package


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
