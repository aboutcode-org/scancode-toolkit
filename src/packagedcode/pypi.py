#
# Copyright (c) 2016 nexB Inc. and others. All rights reserved.
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

import json
import logging
import os
import re

from commoncode import fileutils
from packagedcode.models import AssertedLicense
from packagedcode.models import PythonPackage


"""
Handle Python PyPi packages
"""


logger = logging.getLogger(__name__)
# import sys
# logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
# logger.setLevel(logging.DEBUG)


PKG_INFO_ATTRIBUTES = [
    'Name',
    'Version',
    'Author',
    'Author-email',
    'License',
    'Description',
    'Platform',
    'Home-page',
    'Summary'
]


def parse_pkg_info(location):
    """
    parse a 'PKG-INFO' file at 'location' and return a PythonPackage object.
    """
    infos = {}
    file_text = open(location, 'rb').read()
    for attribute in PKG_INFO_ATTRIBUTES:
        infos[attribute] = re.findall('^'+attribute+'[\s:]*.*', file_text, flags=re.MULTILINE)[0]
        infos[attribute] = re.sub('^'+attribute+'[\s:]*', '', infos[attribute], flags=re.MULTILINE)
        if infos[attribute] == 'UNKNOWN':
            infos[attribute] = None
    package = PythonPackage(
        name=infos.get('Name'),
        version=infos.get('Version'),
        summary=infos.get('Summary'),
        homepage_url=infos.get('Home-page'),
        asserted_licenses=[AssertedLicense(license=infos.get('License'))],
        authors=[infos.get('Author')],
    )
    return package


def get_attribute(setup_location, attribute):
    """
    Return the value specified for a given 'attribute' mentioned in a 'setup.py'
    file.
    Example :
    setup(
        name='requests',
        version='1.0',
        )
    'requests' is returned for the attribute 'name'
    """
    setup_text = open(setup_location, 'rb').read()
    # FIXME Use a valid parser for parsing 'setup.py'
    values = re.findall('setup\(.*?'+attribute+'=[\"\']{1}.*?\',', setup_text.replace('\n', ''))
    if len(values) > 1:
        return
    else:
        values = ''.join(values)
        output = re.sub('setup\(.*?'+attribute+'=[\"\']{1}', '', values)
        if output.endswith('\','):
            return output.replace('\',', '')
        else:
            return output


def parse_metadata(location):
    parent_dir = fileutils.parent_directory(location)
    if os.path.exists(os.path.join(parent_dir, 'METADATA')) and os.path.exists(os.path.join(parent_dir, 'DESCRIPTION.rst')):
        infos = json.loads(open(location, 'rb').read())
        homepage_url = None
        authors = []
        if infos['extensions']:
            try:
                homepage_url = infos['extensions']['python.details']['project_urls']['Home']
            except:
                pass
            try:
                for contact in infos['extensions']['python.details']['contacts']:
                    authors.append(contact['name'])
            except:
                pass
        package = PythonPackage(
            name=infos.get('name'),
            version=infos.get('version'),
            summary=infos.get('summary'),
            asserted_licenses=[AssertedLicense(license=infos.get('license'))],
            homepage_url=homepage_url,
            authors=authors,
        )
        return package


def parse(location):
    """
    Parse a 'setup.py' and return a PythonPackage object.
    """
    file_name = fileutils.file_name(location)
    if file_name == 'setup.py':
        package = PythonPackage(
            name=get_attribute(location, 'name'),
            homepage_url=get_attribute(location, 'url'),
            description=get_attribute(location, 'description'),
            version=get_attribute(location, 'version'),
            authors=[get_attribute(location, 'author')],
            asserted_licenses=[AssertedLicense(license=get_attribute(location, 'license'))],
        )
        return package
    if file_name == 'metadata.json':
        parse_metadata(location)
    if file_name == 'PKG-INFO':
        parse_pkg_info(location)
