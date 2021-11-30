
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#
import logging

import attr

from commoncode import fileutils
from commoncode import filetype
from packagedcode import go_mod
from packagedcode import models

"""
Handle Go packages including go.mod and go.sum files.
"""

# TODO:
# go.mod file does not contain version number.
# valid download url need version number
# CHECK: https://forum.golangbridge.org/t/url-to-download-package/19811

TRACE = False

logger = logging.getLogger(__name__)

if TRACE:
    import sys
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)


@attr.s()
class GolangPackage(models.Package):
    default_type = 'golang'
    default_primary_language = 'Go'
    default_web_baseurl = 'https://pkg.go.dev'
    default_download_baseurl = None
    default_api_baseurl = None

    @classmethod
    def get_package_root(cls, manifest_resource, codebase):
        return manifest_resource.parent(codebase)

    def repository_homepage_url(self, baseurl=default_web_baseurl):
        if self.namespace and self.name:
            return '{}/{}/{}'.format(baseurl, self.namespace, self.name)


@attr.s()
class GoMod(GolangPackage, models.PackageManifest):

    file_patterns = ('go.mod',)
    extensions = ('.mod',)

    @classmethod
    def is_manifest(cls, location):
        """
        Return True if the file at ``location`` is likely a manifest of this type.
        """
        filename = fileutils.file_name(location).lower()
        return filetype.is_file(location) and filename == 'go.mod'

    @classmethod
    def recognize(cls, location):
        """
        Yield one or more Package manifest objects given a file ``location`` pointing to a
        package archive, manifest or similar.
        """
        gomods = go_mod.parse_gomod(location)

        package_dependencies = []
        require = gomods.require or []
        for gomod in require:
            package_dependencies.append(
                models.DependentPackage(
                    purl=gomod.purl(include_version=True),
                    requirement=gomod.version,
                    scope='require',
                    is_runtime=True,
                    is_optional=False,
                    is_resolved=False,
                )
            )

        exclude = gomods.exclude or []
        for gomod in exclude:
            package_dependencies.append(
                models.DependentPackage(
                    purl=gomod.purl(include_version=True),
                    requirement=gomod.version,
                    scope='exclude',
                    is_runtime=True,
                    is_optional=False,
                    is_resolved=False,
                )
            )

        name = gomods.name
        namespace = gomods.namespace
        homepage_url = 'https://pkg.go.dev/{}/{}'.format(gomods.namespace, gomods.name)
        vcs_url = 'https://{}/{}.git'.format(gomods.namespace, gomods.name)

        yield cls(
            name=name,
            namespace=namespace,
            vcs_url=vcs_url,
            homepage_url=homepage_url,
            dependencies=package_dependencies
        )


@attr.s()
class GoSum(GolangPackage, models.PackageManifest):

    file_patterns = ('go.sum',)
    extensions = ('.sum',)

    @classmethod
    def is_manifest(cls, location):
        """
        Return True if the file at ``location`` is likely a manifest of this type.
        """
        filename = fileutils.file_name(location).lower()
        return filetype.is_file(location) and filename == 'go.sum'

    @classmethod
    def recognize(cls, location):
        """
        Yield one or more Package manifest objects given a file ``location`` pointing to a
        package archive, manifest or similar.
        """
        gosums = go_mod.parse_gosum(location)

        package_dependencies = []
        for gosum in gosums:
            package_dependencies.append(
                models.DependentPackage(
                    purl=gosum.purl(),
                    requirement=gosum.version,
                    scope='dependency',
                    is_runtime=True,
                    is_optional=False,
                    is_resolved=True,
                )
            )

        yield cls(dependencies=package_dependencies)
