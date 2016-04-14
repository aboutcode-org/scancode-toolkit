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

from __future__ import absolute_import
from __future__ import print_function

import logging
import re

from packagedcode.models import AssertedLicense
from packagedcode.models import PythonPackage

"""
Handle Python PyPi packages
"""


logger = logging.getLogger(__name__)
# import sys
# logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
# logger.setLevel(logging.DEBUG)


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
    setup_text = setup_text.replace('\n', '')
    # FIXME Use a valid parser for parsing 'setup.py'
    values = re.findall('setup\(.*?'+attribute+'=[\"\']{1}.*?\',', setup_text)
    if len(values) > 1:
        return
    else:
        values = ''.join(values)
        output = re.sub('setup\(.*?'+attribute+'=[\"\']{1}', '', values)
        if output.endswith('\','):
            return output.replace('\',', '')
        else:
            return output


def parse(location):
    """
    Parse a 'setup.py' and return a PythonPackage object.
    """
    if not location.endswith('setup.py'):
        return
    package = PythonPackage(
        name=get_attribute(location, 'name'),
        homepage_url=get_attribute(location, 'url'),
        description=get_attribute(location, 'description'),
        version=get_attribute(location, 'version'),
        authors=[get_attribute(location, 'author')],
        asserted_licenses=[AssertedLicense(license=get_attribute(location, 'license'))],
    )
    return package
