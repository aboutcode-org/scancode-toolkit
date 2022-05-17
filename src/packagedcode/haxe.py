
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
    def parse(cls, location):
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

        name = json_data.get('name')
        version = json_data.get('version')

        package_data = models.PackageData(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            name=name,
            version=version,
            homepage_url=json_data.get('url'),
            declared_license=json_data.get('license'),
            keywords=json_data.get('tags'),
            description=json_data.get('description'),
            primary_language=cls.default_primary_language,
        )

        if not package_data.license_expression and package_data.declared_license:
            package_data.license_expression = cls.compute_normalized_license(package_data)

        if name and version:
            download_url = f'https://lib.haxe.org/p/{name}/{version}/download/'
            package_data.repository_download_url = download_url
            package_data.download_url = download_url

        if name:
            package_data.repository_homepage_url = f'https://lib.haxe.org/p/{name}'

        for contrib in json_data.get('contributors', []):
            party = models.Party(
                type=models.party_person,
                name=contrib,
                role='contributor',
                url='https://lib.haxe.org/u/{}'.format(contrib))
            package_data.parties.append(party)

        for dep_name, dep_version in json_data.get('dependencies', {}).items():
            dep_version = dep_version and dep_version.strip()
            is_resolved = bool(dep_version)
            dep_purl = PackageURL(
                type=cls.default_package_type,
                name=dep_name,
                version=dep_version
            ).to_string()
            dep = models.DependentPackage(purl=dep_purl, is_resolved=is_resolved,)
            package_data.dependencies.append(dep)

        yield package_data
