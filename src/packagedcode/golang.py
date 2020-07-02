
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
from packagedcode import models


"""
Handle Go packages including go.mod and go.sum files.
"""

TRACE = False

logger = logging.getLogger(__name__)

if TRACE:
    import sys
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)


@attr.s()
class GolangPackage(models.Package):
    metafiles = ('go.mod',)
    default_type = 'gopkg'
    default_primary_language = 'Go'
    default_web_baseurl = None
    default_download_baseurl = None
    default_api_baseurl = None

    @classmethod
    def recognize(cls, location):
        if fileutils.file_name(location).lower() == 'go.mod':
            gomod_obj = GoMod()
            gomod_data = gomod_obj.parse_gomod(location)
            yield build_gomod_package(gomod_data)

    @classmethod
    def get_package_root(cls, manifest_resource, codebase):
        return manifest_resource.parent(codebase)

    def repository_homepage_url(self):
        return self.homepage_url

    def repository_download_url(self):
        return self.download_url


def build_gomod_package(gomod_data):
    """
    Return a Package object from a go.mod file or None.
    """
    name = gomod_data.get('name')
    homepage_url = "https://{}".format(gomod_data.get('module'))  
    download_url = "https://{}/archive/master.zip".format(gomod_data.get('module')) 

    package_dependencies = []
    require = gomod_data.get('require')
    if require:
        for name, version in require:
            package_dependencies.append(
                models.DependentPackage(
                    purl=PackageURL(
                        type='gopkg',
                        name=name
                    ).to_string(),
                    requirement=version,
                    scope='require',
                    is_runtime=True,
                    is_optional=False,
                    is_resolved=False,
                )
            )
    exclude = gomod_data.get('exclude')
    if exclude:
        for name, version in exclude:
            package_dependencies.append(
                models.DependentPackage(
                    purl=PackageURL(
                        type='gopkg',
                        name=name
                    ).to_string(),
                    requirement=version,
                    scope='exclude',
                    is_runtime=True,
                    is_optional=False,
                    is_resolved=False,
                )
            )

    return GolangPackage(
        name=name,
        homepage_url=homepage_url,
        download_url=download_url,
        code_view_url=homepage_url,
        dependencies=package_dependencies
    )