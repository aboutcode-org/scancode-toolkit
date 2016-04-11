#
# Copyright (c) 2015 nexB Inc. and others. All rights reserved.
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

from __future__ import absolute_import, print_function

from collections import OrderedDict
import logging

from lxml import etree

from packagedcode.models import AssertedLicense
from packagedcode.models import NugetPackage
from packagedcode.maven import get_xml_parser
from packagedcode.maven import find
from packagedcode.maven import xpath_ns_expr

"""
Handle nuget.org Nuget packages
"""

logger = logging.getLogger(__name__)
# import sys
# logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
# logger.setLevel(logging.DEBUG)

nuspec_tags = [
    'id',
    'version',
    'title',
    'authors',
    'owners',
    'licenseUrl',
    'projectUrl',
    'requireLicenseAcceptance',
    'description',
    'summary',
    'releaseNotes',
    'copyright'
]


def get_nuspec_tags(location):
    """
    Parse a .nuspec file at location and returns a dictionary of data.
    """
    tags = OrderedDict()
    doc = etree.parse(location, get_xml_parser())
    for tag in nuspec_tags:
        xpath = '/package/metadata/' + tag
        values = find(doc, xpath_ns_expr(xpath))
        value = u''.join(values)
        tags[tag] = value and value or None
    return tags


def parse(location):
    """
    Returns a nuget package object from data collected from nuspec file at
    'nuspec_file'.
    """
    if location.endswith('.nuspec'):
        nuspec_data = get_nuspec_tags(location)
        asserted_license = AssertedLicense(url=nuspec_data['licenseUrl'])
        package = NugetPackage(
            # FIXME: this mapping is not correct: owners and authors should be Party objects
            id=nuspec_data['id'],
            asserted_licenses=[asserted_license],
            copyrights=[nuspec_data['copyright']],
            version=nuspec_data['version'],
            homepage_url=nuspec_data['projectUrl'],
            name=nuspec_data['id'],
            description=nuspec_data['description'],
            authors=nuspec_data['authors'],
            owners=nuspec_data['owners'],
            summary=nuspec_data['title'],
            location=location,
        )
        return package
