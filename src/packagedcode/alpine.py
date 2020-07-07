#
# Copyright (c) 2020 nexB Inc. and others. All rights reserved.
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

import attr
from debut import debcon
from six import string_types

from commoncode import filetype
from commoncode import fileutils
from packagedcode import models


@attr.s()
class AlpinePackage(models.Package):
    extensions = ('.apk',)
    default_type = 'alp'

    def compute_normalized_license(self):
        return models.compute_normalized_license(self.declared_license)


def is_alpine_installed_file(location):
    return (filetype.is_file(location)
            and fileutils.file_name(location).lower() == 'installed')


def build_package(package_data):
    """
    Return a Package object from a package_data mapping or None.
    """
    # construct the package
    package = AlpinePackage()
    # mapping of top level `status` file items to the Package object field name
    plain_fields = [
        ('T', 'description'),
        ('U', 'homepage_url'),
        ('S', 'size'),
        ('P', 'name'),
        ('V', 'version'),
        ('m', 'maintainer'),
        ('L', 'declared_license'),
    ]

    for source, target in plain_fields:
        value = package_data.get(source)
        if value:
            if isinstance(value, string_types):
                value = value.strip()
            if value:
                setattr(package, target, value)

    return package


def parse_alpine_installed_file(location):
    """
    Yield Alpine Package objects from an `installed` file or None.
    """
    if not is_alpine_installed_file(location):
        return

    for alpine_pkg_data in debcon.get_paragraphs_data_from_file(location):
        yield build_package(alpine_pkg_data)
