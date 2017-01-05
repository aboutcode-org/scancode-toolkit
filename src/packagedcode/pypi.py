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
import os
import re

from commoncode import fileutils
from packagedcode.models import AssertedLicense
from packagedcode.models import PythonPackage
from packagedcode import models


"""
Detect and collect Python packages information.
"""


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
    Return a Package from a a 'PKG-INFO' file at 'location' or None.
    """
    if not location or not location.endswith('PKG-INFO'):
        return
    infos = {}
    # FIXME: wrap in a with statement
    pkg_info = open(location, 'rb').read()
    for attribute in PKG_INFO_ATTRIBUTES:
        # FIXME: what is this code doing? this is cryptic
        infos[attribute] = re.findall('^' + attribute + '[\s:]*.*', pkg_info, flags=re.MULTILINE)[0]
        infos[attribute] = re.sub('^' + attribute + '[\s:]*', '', infos[attribute], flags=re.MULTILINE)
        if infos[attribute] == 'UNKNOWN':
            infos[attribute] = None

    package = PythonPackage(
        name=infos.get('Name'),
        version=infos.get('Version'),
        summary=infos.get('Summary'),
        homepage_url=infos.get('Home-page'),
        asserted_licenses=[AssertedLicense(license=infos.get('License'))],
        # FIXME: what about Party objects and email?
        # FIXME: what about maintainers?
        authors=[models.Party(type=models.party_person, name=infos.get('Author'))],
    )
    return package


def get_attribute(location, attribute):
    """
    Return the the value for an `attribute` if found in the 'setup.py' file at
    `location` or None.

    For example with this setup.py file:
    setup(
        name='requests',
        version='1.0',
        )
    the value 'request' is returned for the attribute 'name'
    """
    if not location or not location.endswith('setup.py'):
        return
    # FIXME: what if this is unicode text?
    # FIXME: wrap in a with statement
    setup_text = open(location, 'rb').read()
    # FIXME Use a valid parser for parsing 'setup.py'
    # FIXME: it does not make sense to reread a setup.py once for each attribute

    # FIXME: what are these regex doing?
    values = re.findall('setup\(.*?' + attribute + '=[\"\']{1}.*?\',', setup_text.replace('\n', ''))
    if len(values) > 1 or len(values) == 0:
        return
    else:
        values = ''.join(values)
        output = re.sub('setup\(.*?' + attribute + '=[\"\']{1}', '', values)
        if output.endswith('\','):
            return output.replace('\',', '')
        else:
            return output


def parse_metadata(location):
    """
    Return a Package object from the Python wheel 'metadata.json' file at 'location'
    or None. Check if the parent directory of 'location' contains both a 'METADATA'
    and a 'DESCRIPTION.rst' file.
    """
    if not location or not location.endswith('metadata.json'):
        return
    parent_dir = fileutils.parent_directory(location)
    # FIXME: is the absence of these two files a show stopper?
    if not all(os.path.exists(os.path.join(parent_dir, fname))
               for fname in ('METADATA', 'DESCRIPTION.rst')):
        return
    # FIXME: wrap in a with statement
    infos = json.loads(open(location, 'rb').read())
    print(infos)
    homepage_url = None
    authors = []
    if infos['extensions']:
        try:
            homepage_url = infos['extensions']['python.details']['project_urls']['Home']
        except:
            # FIXME: why catch all expections?
            pass
        try:
            for contact in infos['extensions']['python.details']['contacts']:
                authors.append(models.Party(type=models.party_person, name=contact['name'],))
        except:
            # FIXME: why catch all expections?
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
    Return a Package built from parsing a file at 'location'
    The file name can be either a 'setup.py', 'metadata.json' or 'PKG-INFO' file.
    """
    file_name = fileutils.file_name(location)
    if file_name == 'setup.py':
        package = PythonPackage(
            name=get_attribute(location, 'name'),
            homepage_url=get_attribute(location, 'url'),
            description=get_attribute(location, 'description'),
            version=get_attribute(location, 'version'),
            authors=[models.Party(type=models.party_person, name=get_attribute(location, 'author'))],
            asserted_licenses=[AssertedLicense(license=get_attribute(location, 'license'))],
        )
        return package
    if file_name == 'metadata.json':
        parse_metadata(location)
    if file_name == 'PKG-INFO':
        parse_pkg_info(location)
