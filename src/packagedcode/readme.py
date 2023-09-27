#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from commoncode import fileutils

from packagedcode import models

"""
Handle README.*-style semi-structured package metadata.
These are seen in Android, Chromium and a few more places.
"""

# Common README field name mapped to known PackageData field name
PACKAGE_FIELD_BY_README_FIELD = {
    'name': 'name',
    'project': 'name',
    'version': 'version',

    'copyright': 'copyright',

    'download link': 'download_url',
    'downloaded from': 'download_url',

    'homepage': 'homepage_url',
    'website': 'homepage_url',
    'repo': 'homepage_url',
    'source': 'homepage_url',
    'upstream': 'homepage_url',
    'url': 'homepage_url',
    'project url': 'homepage_url',

    'licence': 'extracted_license_statement',
    'license': 'extracted_license_statement',
    # This also has License File sometimes
}


class ReadmeHandler(models.NonAssemblableDatafileHandler):
    datasource_id = 'readme'
    default_package_type = 'readme'
    path_patterns = (
        '*/README.android',
        '*/README.chromium',
        '*/README.facebook',
        '*/README.google',
        '*/README.thirdparty',
    )
    description = ''
    documentation_url = ''

    @classmethod
    def parse(cls, location, purl_only=False):
        with open(location, encoding='utf-8') as loc:
            readme_manifest = loc.read()

        package_data = build_package(
            readme_manifest=readme_manifest,
            purl_only=purl_only
        )

        if not package_data.name:
            # If no name was detected for the Package, then we use the basename
            # of the parent directory as the Package name
            parent_dir = fileutils.parent_directory(location)
            parent_dir_basename = fileutils.file_base_name(parent_dir)
            package_data.name = parent_dir_basename

        yield package_data


def build_package(readme_manifest, purl_only=False):
    """
    Return a Package object from a readme_manifest mapping (from a
    README.chromium file or similar) or None.
    """
    package = models.PackageData(
        datasource_id=ReadmeHandler.datasource_id,
        type=ReadmeHandler.default_package_type,
    )

    for line in readme_manifest.splitlines():
        line = line.strip()

        if ':' in line:
            key, _sep, value = line.partition(':')
        elif '=' in line:
            key, _sep, value = line.partition('=')
        else:
            key = None
            value = None

        if key:
            key = key.lower().strip()
        if value:
            value = value.strip()

        if not key or not value:
            continue
        package_key = PACKAGE_FIELD_BY_README_FIELD.get(key)
        if not package_key:
            continue
        if purl_only and package_key not in ["name", "version"]:
            continue

        setattr(package, package_key, value)

    if not purl_only:
        package.populate_license_fields()
    return package
