#
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
import logging

import attr
from six import string_types
from debut import debcon

from commoncode import filetype
from commoncode import fileutils
from packagedcode import models

"""
Handle FreeBSD ports
per https://www.freebsd.org/cgi/man.cgi?pkg-create(8)
"""

TRACE = False

logger = logging.getLogger(__name__)

if TRACE:
    import sys
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    logger.setLevel(logging.DEBUG)


@attr.s()
class DebianPackage(models.Package):
    metafiles = ('status',)
    default_type = 'debian'

#    @classmethod
#    def recognize(cls, location):
#        yield parse(location)


def is_debian_status_file(location):
    return (filetype.is_file(location)
            and fileutils.file_name(location).lower() == 'status')


def parse_status_file(location):
    """
    Yield Debian Package objects from a dpkg `status` file or None.
    """
    if not is_debian_status_file(location):
        return

    for debian_pkg_data in debcon.get_paragraphs_data_from_file(location):
        yield build_package(debian_pkg_data)


def build_package(package_data):
    """
    Return a Package object from a package_data mapping (from a dpkg status file) 
    or None.
    """
    # construct the package
    package = DebianPackage()

    # add debian-specific package 'qualifiers'
    qualifiers = OrderedDict([
        ('arch', package_data.get('architecture')),
    ])
    package.qualifiers = qualifiers

    # mapping of top level `status` file items to the Package object field name
    plain_fields = [
        ('description', 'description'),
        ('homepage', 'homepage_url'),
        ('installed-size', 'size'),
        ('package', 'name'),
        ('version', 'version'),
        ('maintainer', 'maintainer'),
    ]

    for source, target in plain_fields:
        value = package_data.get(source)
        if value:
            if isinstance(value, string_types):
                value = value.strip()
            if value:
                setattr(package, target, value)

    # mapping of top level `status` file items to a function accepting as
    # arguments the package.json element value and returning an iterable of key,
    # values Package Object to update
    field_mappers = [
        #('depends', dependency_mapper),
    ]

    for source, func in field_mappers:
        logger.debug('parse: %(source)r, %(func)r' % locals())
        value = package_data.get(source) or None
        if value:
            func(value, package)

    return package
