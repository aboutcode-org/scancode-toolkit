#
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

import io
import logging

import attr
import saneyaml
from six import string_types

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
class AboutPackage(models.Package):
    metafiles = ('*.ABOUT',)
    default_type = 'about'

    @classmethod
    def recognize(cls, location):
        yield parse(location)

    @classmethod
    def get_package_root(cls, manifest_resource, codebase):
        # FIXME: this should have been already stored with the Package itself as extra_data
        with io.open(manifest_resource.location, encoding='utf-8') as loc:
            package_data = saneyaml.load(loc.read())
        about_resource = package_data.get('about_resource')
        if about_resource:
            manifest_resource_parent = manifest_resource.parent(codebase)
            for child in manifest_resource_parent.children(codebase):
                if child.name == about_resource:
                    return child
        return manifest_resource


def is_about_file(location):
    return (filetype.is_file(location)
            and location.lower().endswith(('.about',)))


def parse(location):
    """
    Return a Package object from an ABOUT file or None.
    """
    if not is_about_file(location):
        return

    with io.open(location, encoding='utf-8') as loc:
        package_data = saneyaml.load(loc.read())

    return build_package(package_data)


def build_package(package_data):
    """
    Return a Package built from `package_data` obtained by an ABOUT file.
    """
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
    if not isinstance(owner, string_types):
        owner = repr(owner)
    parties = [models.Party(type=models.party_person, name=owner, role='owner')]

    return AboutPackage(
        type='about',
        name=name,
        version=version,
        declared_license=declared_license,
        copyright=copyright_statement,
        parties=parties,
        homepage_url=homepage_url,
        download_url=download_url,
    )
