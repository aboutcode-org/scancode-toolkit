#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import io
import json
import logging

import attr
from packageurl import PackageURL

from commoncode import filetype
from packagedcode import models
from packagedcode.utils import combine_expressions


TRACE = False

logger = logging.getLogger(__name__)

if TRACE:
    import sys
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)


@attr.s()
class BowerPackageData(models.PackageData):
    
    default_type = 'bower'
    default_primary_language = 'JavaScript'

    @classmethod
    def get_package_root(cls, manifest_resource, codebase):
        return manifest_resource.parent(codebase)

    def compute_normalized_license(self):
        return compute_normalized_license(self.declared_license)


@attr.s()
class BowerJson(BowerPackageData, models.PackageDataFile):

    file_patterns = ('bower.json', '.bower.json')
    extensions = ('.json',)

    @classmethod
    def is_package_data_file(cls, location):
        """
        Return True if the file at ``location`` is likely a manifest of this type.
        """
        return filetype.is_file(location) and location.lower().endswith(('bower.json', '.bower.json'))

    @classmethod
    def recognize(cls, location):
        """
        Yield one or more Package manifest objects given a file ``location`` pointing to a
        package archive, manifest or similar.
        """
        with io.open(location, encoding='utf-8') as loc:
            package_data = json.load(loc)

        name = package_data.get('name')
        # FIXME: having no name may not be a problem See #1514
        if not name:
            return

        description = package_data.get('description')
        version = package_data.get('version')
        declared_license = package_data.get('license')
        if declared_license:
            if isinstance(declared_license, str):
                declared_license = [declared_license]
            elif isinstance(declared_license, (list, tuple)):
                declared_license = [l for l in declared_license if l and l.strip()]
            else:
                declared_license = [repr(declared_license)]

        keywords = package_data.get('keywords') or []

        parties = []

        authors = package_data.get('authors') or []
        for author in authors:
            if isinstance(author, dict):
                name = author.get('name')
                email = author.get('email')
                url = author.get('homepage')
                party = models.Party(name=name, role='author', email=email, url=url)
                parties.append(party)
            elif isinstance(author, str):
                parties.append(models.Party(name=author, role='author'))
            else:
                parties.append(models.Party(name=repr(author), role='author'))

        homepage_url = package_data.get('homepage')

        repository = package_data.get('repository') or {}
        repo_type = repository.get('type')
        repo_url = repository.get('url')

        vcs_url = None
        if repo_type and repo_url:
            vcs_url = '{}+{}'.format(repo_type, repo_url)

        deps = package_data.get('dependencies') or {}
        dependencies = []
        for dep_name, requirement in deps.items():
            dependencies.append(
                models.DependentPackage(
                    purl=PackageURL(type='bower', name=dep_name).to_string(),
                    scope='dependencies',
                    extracted_requirement=requirement,
                    is_runtime=True,
                    is_optional=False,
                )
            )

        dev_dependencies = package_data.get('devDependencies') or {}
        for dep_name, requirement in dev_dependencies.items():
            dependencies.append(
                models.DependentPackage(
                    purl=PackageURL(type='bower', name=dep_name).to_string(),
                    scope='devDependencies',
                    extracted_requirement=requirement,
                    is_runtime=False,
                    is_optional=True,
                )
            )

        yield cls(
            name=name,
            description=description,
            version=version,
            declared_license=declared_license,
            keywords=keywords,
            parties=parties,
            homepage_url=homepage_url,
            vcs_url=vcs_url,
            dependencies=dependencies
        )


@attr.s()
class BowerPackage(BowerPackageData, models.Package):
    """
    A Bower Package that is created out of one/multiple bower package
    manifests and package-like data, with it's files.
    """

    @property
    def manifests(self):
        return [
            BowerJson
        ]


def compute_normalized_license(declared_license):
    """
    Return a normalized license expression string detected from a list of
    declared license strings.
    """
    if not declared_license:
        return

    detected_licenses = []

    for declared in declared_license:
        detected_license = models.compute_normalized_license(declared)
        if detected_license:
            detected_licenses.append(detected_license)
        else:
            detected_licenses.append('unknown')

    if detected_licenses:
        return combine_expressions(detected_licenses)
