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

from packageurl import PackageURL

from packagedcode import models
from packagedcode.utils import combine_expressions


# TODO: handle complex cases of npms and bower combined
class BowerJsonHandler(models.DatafileHandler):
    datasource_id = 'bower_json'
    path_patterns = ('*/bower.json', '*/.bower.json',)
    default_package_type = 'bower'
    default_primary_language = 'JavaScript'
    description = 'Bower package'
    documentation_url = 'https://bower.io'

    @classmethod
    def compute_normalized_license(cls, package):
        return compute_bower_normalized_license(package.declared_license)

    @classmethod
    def parse(cls, location):
        with io.open(location, encoding='utf-8') as loc:
            package_data = json.load(loc)

        # note: having no name is not a problem for private packages. See #1514
        name = package_data.get('name')

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
            vcs_url = f'{repo_type}+{repo_url}'

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

        yield models.PackageData(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
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


def compute_bower_normalized_license(declared_license):
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
