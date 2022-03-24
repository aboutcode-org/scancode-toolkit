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

# TODO: Override get_package_resource so it returns the Resource that the ABOUT file is describing


class AboutFileHandler(models.DatafileHandler):
    datasource_id = 'about_file'
    default_package_type = 'about'
    path_patterns = ('*.ABOUT',)
    description = 'AboutCode ABOUT file'
    documentation_url = 'https://aboutcode-toolkit.readthedocs.io/en/latest/specification.html'

    @classmethod
    def parse(cls, location):
        """
        Yield one or more Package manifest objects given a file ``location`` pointing to a
        package archive, manifest or similar.
        """
        with io.open(location, encoding='utf-8') as loc:
            package_data = saneyaml.load(loc.read())

        # FIXME: About files can contain any purl and also have a namespace
        package_type = cls.default_package_type
        name = package_data.get('name')
        version = package_data.get('version')

        homepage_url = package_data.get('home_url') or package_data.get('homepage_url')
        download_url = package_data.get('download_url')
        declared_license = license_expression = package_data.get('license_expression')
        copyright_statement = package_data.get('copyright')

        owner = package_data.get('owner')
        if not isinstance(owner, str):
            owner = repr(owner)
        parties = [models.Party(type=models.party_person, name=owner, role='owner')]

        yield models.PackageData(
            datasource_id=cls.datasource_id,
            type=package_type,
            name=name,
            version=version,
            declared_license=declared_license,
            license_expression=license_expression,
            copyright=copyright_statement,
            parties=parties,
            homepage_url=homepage_url,
            download_url=download_url,
            # FIXME: we should put the unprocessed attributes in extra data
            extra_data=dict(about_resource=package_data.get('about_resource'))
        )

    @classmethod
    def assemble(cls, package_data, resource, codebase):
        """
        Yield a Package. Note that ABOUT files do not carry dependencies.
        """
        datafile_path = resource.path
        # do we have enough to create a package?
        if package_data.purl:
            package = models.Package.from_package_data(
                package_data=package_data,
                datafile_path=datafile_path,
            )
            package_uid = package.package_uid

            # NOTE: we do not attach files to the Package level. Instead we
            # update `for_package` in the file
            resource.for_packages.append(package_uid)
            resource.save(codebase)

            package.license_expression = cls.compute_normalized_license(package)

            yield package

            # FIXME: also include notice_file and license_file(s)
            about_resource = package_data.extra_data.get('about_resource')
            if about_resource:
                parent = resource.parent(codebase)
                # FIXME: we should be able to get the path relatively to the ABOUT file resource
                for child in parent.children(codebase):
                    if child.name == about_resource:
                        child.for_packages.append(package_uid)
                        child.save()

        # we yield this as we do not want this further processed
        yield resource
