#
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
from packagedcode import models


TRACE = False

logger = logging.getLogger(__name__)

if TRACE:
    import sys
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

# TODO: Override get_package_resource so it returns the Resource that the ABOUT file is describing

@attr.s()
class AboutPackageData(models.PackageData):

    default_type = 'about'

    def get_package_root(self, manifest_resource, codebase):
        about_resource = self.extra_data.get('about_resource')
        if about_resource:
            manifest_resource_parent = manifest_resource.parent(codebase)
            for child in manifest_resource_parent.children(codebase):
                if child.name == about_resource:
                    return child
        return manifest_resource


@attr.s()
class Aboutfile(AboutPackageData, models.PackageDataFile):

    file_patterns = ('*.ABOUT',)
    extensions = ('.ABOUT',)

    @classmethod
    def is_package_data_file(cls, location):
        """
        Return True if the file at ``location`` is likely a manifest of this type.
        """
        return filetype.is_file(location) and location.lower().endswith(('.about',))

    @classmethod
    def recognize(cls, location):
        """
        Yield one or more Package manifest objects given a file ``location`` pointing to a
        package archive, manifest or similar.
        """
        with io.open(location, encoding='utf-8') as loc:
            package_data = saneyaml.load(loc.read())

        name = package_data.get('name')
        # FIXME: having no name may not be a problem See #1514
        if not name:
            return

        version = package_data.get('version')
        homepage_url = package_data.get('home_url') or package_data.get('homepage_url')
        download_url = package_data.get('download_url')
        declared_license = package_data.get('license_expression')
        copyright_statement = package_data.get('copyright')

        owner = package_data.get('owner')
        if not isinstance(owner, str):
            owner = repr(owner)
        parties = [models.Party(type=models.party_person, name=owner, role='owner')]

        about_package = cls(
            type='about',
            name=name,
            version=version,
            declared_license=declared_license,
            copyright=copyright_statement,
            parties=parties,
            homepage_url=homepage_url,
            download_url=download_url,
        )

        about_package.extra_data['about_resource'] = package_data.get('about_resource')
        yield about_package
