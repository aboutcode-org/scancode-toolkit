
# Copyright (c) nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/scancode-toolkit/
# The ScanCode software is licensed under the Apache License version 2.0.
# Data generated with ScanCode require an acknowledgment.
# ScanCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# When you publish or redistribute any data created with ScanCode or any ScanCode
# derivative work, you must accompany this data with the following acknowledgment:
#
#  Generated with ScanCode and provided on an "AS IS" BASIS, WITHOUT WARRANTIES
#  OR CONDITIONS OF ANY KIND, either express or implied. No content created from
#  ScanCode should be considered or used as legal advice. Consult an Attorney
#  for any legal advice.
#  ScanCode is a free software code scanning tool from nexB Inc. and others.
#  Visit https://github.com/nexB/scancode-toolkit/ for support and download.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from collections import OrderedDict
import io
import logging
import re

import attr
from packageurl import PackageURL

from commoncode import filetype
from commoncode import fileutils
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
    metafiles = ('go.mod', 'go.sum')
    default_type = 'golang'
    default_primary_language = 'Go'
    default_web_baseurl = 'https://pkg.go.dev'
    default_download_baseurl = None
    default_api_baseurl = None

    @classmethod
    def recognize(cls, location):
        filename = fileutils.file_name(location).lower()
        if filename == 'go.mod':
            gomods = go_mod.parse_gomod(location)
            yield build_gomod_package(gomods)
        elif filename == 'go.sum':
            gosums = go_mod.parse_gosum(location)
            yield build_gosum_package(gosums)

    @classmethod
    def get_package_root(cls, manifest_resource, codebase):
        return manifest_resource.parent(codebase)

    def repository_homepage_url(self, baseurl=default_web_baseurl):
        if self.namespace and self.name:
            return '{}/{}/{}'.format(baseurl, self.namespace, self.name)


def build_gomod_package(gomods):
    """
    Return a Package object from a go.mod file or None.
    """
    package_dependencies = []
    require = gomods.require or []
    for gomod in require:
        package_dependencies.append(
            models.DependentPackage(
                purl=gomod.purl(include_version=False),
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
                purl=gomod.purl(include_version=False),
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

    return GolangPackage(
        name=name,
        namespace=namespace,
        vcs_url=vcs_url,
        homepage_url=homepage_url,
        dependencies=package_dependencies
    )


def build_gosum_package(gosums):
    """
    Return a Package object from a go.sum file.
    """
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

    return GolangPackage(dependencies=package_dependencies)
