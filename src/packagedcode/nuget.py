#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import xmltodict

from packagedcode import models
from packagedcode.utils import build_description

"""
Handle NuGet packages and their manifests.
"""
# TODO: add dependencies


def get_urls(name, version):
    return dict(
        repository_homepage_url=f'https://www.nuget.org/packages/{name}/{version}',
        repository_download_url=f'https://www.nuget.org/api/v2/package/{name}/{version}',
        # the name is lowercased as in
        # https://api.nuget.org/v3/registration3/newtonsoft.json/10.0.1.json
        api_data_url=f'https://api.nuget.org/v3/registration3/{name.lower()}/{version}.json',
    )


class NugetNupkgHandler(models.NonAssemblableDatafileHandler):
    datasource_id = 'nuget_nupkg'
    path_patterns = ('*.nupkg',)
    default_package_type = 'nuget'
    filetypes = ('zip archive', 'microsoft ooxml',)
    description = 'NuGet nupkg package archive'
    documentation_url = 'https://en.wikipedia.org/wiki/Open_Packaging_Conventions'


class NugetNuspecHandler(models.DatafileHandler):
    datasource_id = 'nuget_nupsec'
    path_patterns = ('*.nuspec',)
    default_package_type = 'nuget'
    description = 'NuGet nuspec package manifest'
    documentation_url = 'https://docs.microsoft.com/en-us/nuget/reference/nuspec'

    @classmethod
    def parse(cls, location):
        with open(location , 'rb') as loc:
            parsed = xmltodict.parse(loc)

        if not parsed:
            return

        pack = parsed.get('package') or {}
        nuspec = pack.get('metadata')
        if not nuspec:
            return

        name = nuspec.get('id')
        version = nuspec.get('version')

        # Summary: A short description of the package for UI display. If omitted, a
        # truncated version of description is used.
        description = build_description(nuspec.get('summary') , nuspec.get('description'))

        # title: A human-friendly title of the package, typically used in UI
        # displays as on nuget.org and the Package Manager in Visual Studio. If not
        # specified, the package ID is used.
        title = nuspec.get('title')
        if title and title != name:
            description = build_description(nuspec.get('title') , description)

        parties = []
        authors = nuspec.get('authors')
        if authors:
            parties.append(models.Party(name=authors, role='author'))

        owners = nuspec.get('owners')
        if owners:
            parties.append(models.Party(name=owners, role='owner'))

        vcs_url = None

        repo = nuspec.get('repository') or {}
        vcs_repository = repo.get('@url') or ''
        if vcs_repository:
            vcs_tool = repo.get('@type') or ''
            if vcs_tool:
                vcs_url = f'{vcs_tool}+{vcs_repository}'
            else:
                vcs_url = vcs_repository

        urls = get_urls(name, version)

        package_data = models.PackageData(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            name=name,
            version=version,
            description=description or None,
            homepage_url=nuspec.get('projectUrl') or None,
            parties=parties,
            # FIXME: license has evolved and is now SPDX...
            declared_license=nuspec.get('licenseUrl') or None,
            copyright=nuspec.get('copyright') or None,
            vcs_url=vcs_url,
            **urls,
        )

        if not package_data.license_expression and package_data.declared_license:
            package_data.license_expression = cls.compute_normalized_license(package_data)

        yield package_data
