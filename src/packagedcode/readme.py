#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import logging

import attr
from commoncode import filetype
from commoncode import fileutils

from packagedcode import models

"""
Handle README.* package metadata
"""

TRACE = False

logger = logging.getLogger(__name__)

if TRACE:
    import sys
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    logger.setLevel(logging.DEBUG)


@attr.s()
class ReadmePackage(models.Package):
    metafiles = (
        'README.android',
        'README.chromium',
        'README.facebook',
        'README.google',
        'README.thirdparty',
    )
    default_type = 'readme'

    @classmethod
    def recognize(cls, location):
        yield parse(location)

    @classmethod
    def get_package_root(cls, manifest_resource, codebase):
        return manifest_resource.parent(codebase)

    def compute_normalized_license(self):
        return models.compute_normalized_license(self.declared_license)


def is_readme_manifest(location):
    return (filetype.is_file(location)
            and fileutils.file_name(location).lower() in [
                'readme.android',
                'readme.chromium',
                'readme.facebook',
                'readme.google',
                'readme.thirdparty'
            ])


def parse(location):
    """
    Return a Package object from a README manifest file or None.
    """
    if not is_readme_manifest(location):
        return

    with open(location, encoding='utf-8') as loc:
        readme_manifest = loc.read()

    return build_package(readme_manifest)


def build_package(readme_manifest):
    """
    Return a Package object from a readme_manifest mapping (from a
    README.chromium file or similar) or None.
    """
    package = ReadmePackage()

    for line in readme_manifest.splitlines():
        key, sep, value = line.partition(':')

        if not key or not value:
            continue
 
        # Map the key, value pairs to the Package
        key, value = key.lower(), value.strip()
        if key == 'name':
            package.name = value
        if key == 'version':
            package.version = value
        if key == 'url' or key == 'project url':
            package.homepage_url = value
        if key == 'license':
            package.declared_license = value

    return package
