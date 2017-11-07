#
# Copyright (c) 2017 nexB Inc. and others. All rights reserved.
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
import sys

from commoncode import fileutils
from packagedcode.models import PythonPackage
from packagedcode import models
from packagedcode.utils import join_texts

"""
Detect and collect Python packages information.

"""

TRACE = False

def logger_debug(*args):
    pass

logger = logging.getLogger(__name__)

if TRACE:
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, basestring) and a or repr(a) for a in args))


# FIXME: this whole modeul is a mess

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
        # FIXME: what is this code doing? this is cryptic at best and messy
        infos[attribute] = re.findall('^' + attribute + '[\s:]*.*', pkg_info, flags=re.MULTILINE)[0]
        infos[attribute] = re.sub('^' + attribute + '[\s:]*', '', infos[attribute], flags=re.MULTILINE)
        if infos[attribute] == 'UNKNOWN':
            infos[attribute] = None

    description = join_texts(infos.get('Summary'), infos.get('Description'))
    parties = []
    author = infos.get('Author')
    if author:
        parties.append(models.Party(type=models.party_person, name=author, role=''))

    package = PythonPackage(
        name=infos.get('Name'),
        version=infos.get('Version'),
        description=description or None,
        homepage_url=infos.get('Home-page') or None,
        asserted_license=infos.get('License') or None,
        # FIXME: what about email?
        # FIXME: what about maintainers?
        parties=parties,
    )
    return package


# FIXME: each attribute require reparsing the setup.py: this is nuts!

def get_setup_attribute(location, attribute):
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

# FIXME: use proper library for parsing these

def parse_metadata(location):
    """
    Return a Package object from the Python wheel 'metadata.json' file
    at 'location' or None. Check if the parent directory of 'location'
    contains both a 'METADATA' and a 'DESCRIPTION.rst' file to ensure
    this is a proper metadata.json file..
    """
    if not location or not location.endswith('metadata.json'):
        if TRACE: logger_debug('parse_metadata: not metadata.json:', location)
        return
    parent_dir = fileutils.parent_directory(location)
    # FIXME: is the absence of these two files a show stopper?
    paths = [os.path.join(parent_dir, n) for n in ('METADATA', 'DESCRIPTION.rst')]
    if not all(os.path.exists(p) for p in paths):
        if TRACE: logger_debug('parse_metadata: not extra paths', paths)
        return

    with open(location, 'rb') as infs:
        infos = json.load(infs)

    extensions = infos.get('extensions')
    if TRACE: logger_debug('parse_metadata: extensions:', extensions)
    details = extensions and extensions.get('python.details')
    urls = details and details.get('project_urls')
    homepage_url = urls and urls.get('Home')

    parties = []
    if TRACE: logger_debug('parse_metadata: contacts:', details.get('contacts'))
    contacts = details and details.get('contacts') or []
    for contact in contacts:
        if TRACE: logger_debug('parse_metadata: contact:', contact)
        name = contact and contact.get('name')
        if not name:
            if TRACE: logger_debug('parse_metadata: no name:', contact)
            continue
        parties.append(models.Party(type=models.party_person, name=name, role='contact'))

    description = join_texts(infos.get('summary') , infos.get('description'))

    package = PythonPackage(
        name=infos.get('name'),
        version=infos.get('version'),
        description=description or None,
        asserted_license=infos.get('license') or None,
        homepage_url=homepage_url or None,
        parties=parties,
    )
    return package


# FIXME: this is not the way to parse a python script

def parse_setup_py(location):
    """
    Return a package built from setup.py data.
    """

    description = join_texts(
        get_setup_attribute(location, 'summary') ,
        get_setup_attribute(location, 'description'))

    parties = []
    author = get_setup_attribute(location, 'author')
    if author:
        parties.append(
            models.Party(
            type=models.party_person,
            name=author, role='author'))

    package = PythonPackage(
        name=get_setup_attribute(location, 'name'),
        version=get_setup_attribute(location, 'version'),
        description=description or None,
        homepage_url=get_setup_attribute(location, 'url') or None,
        parties=parties,
        asserted_license=get_setup_attribute(location, 'license') or None,
    )
    return package



def parse(location):
    """
    Return a Package built from parsing a file at 'location' The file
    name can be either a 'setup.py', 'metadata.json' or 'PKG-INFO'
    file.
    """
    file_name = fileutils.file_name(location)
    parsers = {
        'setup.py': parse_setup_py,
        'metadata.json': parse_metadata,
        'PKG-INFO': parse_pkg_info
    }
    parser = parsers.get(file_name)
    if parser:
        return parser(location)
