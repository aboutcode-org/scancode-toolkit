
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

"""
Handle haxelib Haxe packages

See
- https://lib.haxe.org/all/ this lists all the packages.
- https://lib.haxe.org/documentation/creating-a-haxelib-package/
- https://github.com/HaxeFoundation/haxelib
- https://github.com/gogoprog/hxsocketio/blob/master/haxelib.json
- https://github.com/HaxeFoundation/haxelib/blob/development/haxelib.json

Download and homepage are using these conventions:
- https://lib.haxe.org/p/format/
- https://lib.haxe.org/files/3.0/tweenx-1,0,4.zip
- https://lib.haxe.org/p/format/3.4.1/download/
- https://lib.haxe.org/files/3.0/format-3,4,1.zip
"""

# TODO: Update the license based on a mapping:
# Per the doc:
# Can be GPL, LGPL, BSD, Public (for Public Domain), MIT, or Apache.


class HaxelibJsonHandler(models.DatafileHandler):
    datasource_id = 'haxelib_json'
    path_patterns = ('*/haxelib.json',)
    default_package_type = 'haxe'
    default_primary_language = 'Haxe'
    description = 'Haxe haxelib.json metadata file'
    documentation_url = 'https://lib.haxe.org/documentation/creating-a-haxelib-package/'

    @classmethod
    def _parse(cls, json_data, package_only=False):
        name = json_data.get('name')
        version = json_data.get('version')

        tags = json_data.get('tags') or []
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(',') if t.strip()]

        package_mapping = dict(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            name=name,
            version=version,
            homepage_url=json_data.get('url'),
            extracted_license_statement=json_data.get('license'),
            keywords=tags,
            description=json_data.get('description'),
            primary_language=cls.default_primary_language,
        )
        package_data = models.PackageData.from_data(package_mapping, package_only)

        if name and version:
            download_url = f'https://lib.haxe.org/p/{name}/{version}/download/'
            package_data.repository_download_url = download_url
            package_data.download_url = download_url

        if name:
            package_data.repository_homepage_url = f'https://lib.haxe.org/p/{name}'

        contributors = json_data.get('contributors') or []
        if isinstance(contributors, (str, dict)):
            contributors = [contributors]
        for contrib in contributors:
            if isinstance(contrib, dict):
                contrib_name = contrib.get('name') or repr(contrib)
            else:
                contrib_name = str(contrib)
            party = models.Party(
                type=models.party_person,
                name=contrib_name,
                role='contributor',
                url=f'https://lib.haxe.org/u/{contrib_name}')
            package_data.parties.append(party)

        deps = json_data.get('dependencies') or {}
        if isinstance(deps, dict):
            dep_items = deps.items()
        elif isinstance(deps, list):
            dep_items = [(dep_name, None) for dep_name in deps]
        else:
            dep_items = []

        for dep_name, dep_version in dep_items:
            if not dep_name or not isinstance(dep_name, str):
                continue
            dep_name = dep_name.strip()
            if not dep_name:
                continue

            extracted_requirement = None
            if dep_version and isinstance(dep_version, str):
                extracted_requirement = dep_version.strip() or None

            is_pinned = False
            purl_version = None
            if extracted_requirement:
                if not any(c in extracted_requirement for c in ('<', '>', '=', '^', '~', ':', ' ')):
                    is_pinned = True
                    purl_version = extracted_requirement

            dep_purl = PackageURL(
                type=cls.default_package_type,
                name=dep_name,
                version=purl_version
            ).to_string()
            dep = models.DependentPackage(
                purl=dep_purl,
                extracted_requirement=extracted_requirement,
                scope='dependencies',
                is_runtime=True,
                is_optional=False,
                is_pinned=is_pinned,
            )
            package_data.dependencies.append(dep)

        return package_data

    @classmethod
    def parse(cls, location, package_only=False):
        """
        Yield one or more Package manifest objects given a file ``location`` pointing to a
        package_data archive, manifest or similar.

        {
            "name": "haxelib",
            "url" : "https://lib.haxe.org/documentation/",
            "license": "GPL",
            "tags": ["haxelib", "core"],
            "description": "The haxelib client",
            "classPath": "src",
            "version": "3.4.0",
            "releasenote": " * Fix password input issue in Windows (#421).\n * ....",
            "contributors": ["back2dos", "ncannasse", "jason", "Simn", "nadako", "andyli"]
        }
        """
        with io.open(location, encoding='utf-8') as loc:
            json_data = json.load(loc)

        yield cls._parse(json_data, package_only)
