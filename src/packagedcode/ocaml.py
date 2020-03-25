# All rights reserved.
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
import logging
import re

import attr
import io

from commoncode.fileutils import py2
from commoncode import filetype
from commoncode import fileutils
from packagedcode import models


"""
Handle Opam Package Manager
"""

TRACE = False

logger = logging.getLogger(__name__)

if TRACE:
    import sys
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)


@attr.s()
class OpamPackageManager(models.Package):
    metafiles = ('*.opam',)
    extensions = ('.opam',)
    default_type = 'opam'
    default_primary_language = 'Ocaml'
    default_web_baseurl = 'https://opam.ocaml.org/'
    default_download_baseurl = 'https://opam.ocaml.org/doc/Install.html'
    default_api_baseurl = 'https://opam.ocaml.org/doc/Install.html'

    @classmethod
    def recognize(cls, location):
        yield parse(location)

    @classmethod
    def get_package_root(cls, manifest_resource, codebase):
        return manifest_resource.parent(codebase)

    def repository_homepage_url(self, baseurl=default_web_baseurl):
        return '{}/crates/{}'.format(baseurl, self.name)

    def repository_download_url(self, baseurl=default_download_baseurl):
        return '{}/crates/{}/{}/download'.format(baseurl, self.name, self.version)

    def api_data_url(self, baseurl=default_api_baseurl):
        return '{}/crates/{}'.format(baseurl, self.name)


def is_opam(location):
    return (filetype.is_file(location) and location.endswith('.opam'))


def parse(location):
    """
    Return a Package object from a .opam file or None.
    """
    if not is_opam(location):
        return

    package_data = load(location)
    return build_package(package_data)


def build_package(package_data):
    """
    Return a Pacakge object from a package data mapping or None.
    """

    version = get_version(package_data)
    # maintainer = get_maintainer(package_data)

    package = OpamPackageManager(
        version=version or None,
        # maintainer=maintainer
    )

    return package


def load(file_name):
    file_data = []
    with io.open(file_name, "r", encoding="utf-8") as f:
        file_data = [line.rstrip('\n') for line in f]
    return file_data


def get_version(file_data):
    for individual in file_data:
        if 'opam-version' in individual:
            version = individual.split('"')
            return version[1]


def get_maintainer(file_data):
    for individual in file_data:
        if 'maintainer' in individual:
            maintainer = individual.split('"')
            return maintainer[1]


def get_synopsis(file_data):
    for individual in file_data:
        if 'synopsis' in individual:
            synopsis = individual.split('"')
            return synopsis[1]
