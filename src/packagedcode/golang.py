
# Copyright (c) 2019 nexB Inc. and others. All rights reserved.
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
from packagedcode.go_mod import GoMod
from packagedcode import go_sum
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
            gomod_data = GoMod.parse_gomod(location)
            yield build_gomod_package(gomod_data)
        elif filename == 'go.sum':
            gosum_objs = go_sum.parse_gosum(location)
            yield build_gosum_package(gosum_objs)

    @classmethod
    def get_package_root(cls, manifest_resource, codebase):
        return manifest_resource.parent(codebase)

    def repository_homepage_url(self, baseurl=default_web_baseurl):
        return '{}/{}/{}'.format(baseurl, self.namespace, self.name)


def build_gomod_package(gomod_data):
    """
    Return a Package object from a go.mod file or None.
    """
    package_dependencies = []
    require = gomod_data.get('require') or []
    for namespace, name, version in require:
        package_dependencies.append(
            models.DependentPackage(
                purl=PackageURL(
                    type='golang',
                    namespace=namespace,
                    name=name
                ).to_string(),
                requirement=version,
                scope='require',
                is_runtime=True,
                is_optional=False,
                is_resolved=False,
            )
        )

    exclude = gomod_data.get('exclude') or []
    for namespace, name, version in exclude:
        package_dependencies.append(
            models.DependentPackage(
                purl=PackageURL(
                    type='golang',
                    namespace=namespace,
                    name=name
                ).to_string(),
                requirement=version,
                scope='exclude',
                is_runtime=True,
                is_optional=False,
                is_resolved=False,
            )
        )

    name = gomod_data.get('name')
    namespace = gomod_data.get('namespace')
    homepage_url = 'https://pkg.go.dev/{}'.format(gomod_data.get('module'))
    vcs_url = 'https://{}.git'.format(gomod_data.get('module'))

    return GolangPackage(
        name=name,
        namespace=namespace,
        vcs_url=vcs_url,
        homepage_url=homepage_url,
        dependencies=package_dependencies
    )


def build_gosum_package(gosum_objs):
    """
    Return a Package object from a go.sum file.
    """
    package_dependencies = []
    for obj in gosum_objs:
        package_dependencies.append(
            models.DependentPackage(
                purl=PackageURL(
                    type='golang',
                    namespace=obj.namespace,
                    name=obj.name,
                    version=obj.version
                ).to_string(),
                requirement=obj.version,
                scope='dependency',
                is_runtime=True,
                is_optional=False,
                is_resolved=True,
            )
        )

    return GolangPackage(dependencies=package_dependencies)
