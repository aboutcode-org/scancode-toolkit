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

from collections import OrderedDict
import io
import logging

import attr
from packageurl import PackageURL
from six import string_types

from commoncode import filetype
from packagedcode import models
from packagedcode.utils import combine_expressions
import saneyaml


TRACE = False

logger = logging.getLogger(__name__)

if TRACE:
    import sys
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)


@attr.s()
class AboutPackage(models.Package):
    metafiles = ('*.ABOUT',)

    @classmethod
    def recognize(cls, location):
        return parse(location)


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

    owner = package_data.get('owner')
    parties = [models.Party(name=repr(owner), role='owner')]

    return AboutPackage(
        name=name,
        version=version,
        declared_license=declared_license,
        parties=parties,
        homepage_url=homepage_url,
        download_url=download_url,
    )
