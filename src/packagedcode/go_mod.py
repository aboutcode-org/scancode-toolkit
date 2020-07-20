
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
import re

import attr


"""
https://golang.org/ref/mod#go.mod-files

For example:

module example.com/my/thing

go 1.12

require example.com/other/thing v1.0.2
require example.com/new/thing v2.3.4
exclude example.com/old/thing v1.2.3
require (
    example.com/new/thing v2.3.4
    example.com/old/thing v1.2.3
)
require (
    example.com/new/thing v2.3.4
    example.com/old/thing v1.2.3
)

"""

"""
module is in the form
module github.com/alecthomas/participle

For example:
>>> ob = GoMod()
>>> p = ob.parse_module('module github.com/alecthomas/participle')
>>> assert p.group('module') == ('github.com/alecthomas/participle')

require or exclude can be in the form
require github.com/davecgh/go-spew v1.1.1
or
exclude github.com/davecgh/go-spew v1.1.1
or
github.com/davecgh/go-spew v1.1.1

For example:
>>> ob = GoMod()

>>> p = ob.parse_require('require github.com/davecgh/go-spew v1.1.1')
>>> assert p.group('namespace') == ('github.com/davecgh')
>>> assert p.group('name') == ('go-spew')
>>> assert p.group('version') == ('v1.1.1')

>>> p = ob.parse_exclude('exclude github.com/davecgh/go-spew v1.1.1')
>>> assert p.group('namespace') == ('github.com/davecgh')
>>> assert p.group('name') == ('go-spew')
>>> assert p.group('version') == ('v1.1.1')

>>> p = ob.parse_dep_link('github.com/davecgh/go-spew v1.1.1')
>>> assert p.group('namespace') == ('github.com/davecgh')
>>> assert p.group('name') == ('go-spew')
>>> assert p.group('version') == ('v1.1.1')
"""


TRACE = False

logger = logging.getLogger(__name__)

if TRACE:
    import sys
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)


@attr.s()
class GoMod(object):
    # Regex expressions to parse different types of dependency
    parse_module = re.compile(
        r'^module\s'
        r'(?P<module>[a-z].*)'
    ).match

    parse_module_name = re.compile(
        r'^module(\s)*'
        r'(?P<namespace>(.*))'
        r'/'
        r'(?P<name>[^\s]*)'
    ).match

    parse_require = re.compile(
        r'^require(\s)*'
        r'(?P<namespace>(.*))'
        r'/'
        r'(?P<name>[^\s]*)'
        r'\s'
        r'(?P<version>(.*))'
    ).match

    parse_exclude = re.compile(
        r'^exclude(\s)*'
        r'(?P<namespace>(.*))'
        r'/'
        r'(?P<name>[^\s]*)'
        r'\s'
        r'(?P<version>(.*))'
    ).match

    parse_dep_link = re.compile(
        r'(?P<namespace>(.*))'
        r'/'
        r'(?P<name>[^\s]*)'
        r'\s'
        r'(?P<version>(.*))'
    ).match

    def preprocess(self, line):
        """
        Return line string after removing commented portion and excess spaces.
        """
        if "//" in line:
            line = line[:line.index('//')]
        line = line.strip()
        return line

    def parse_gomod(self, location):
        """
        Return a dictionary containing all the important go.mod file data.
        """
        with io.open(location, encoding='utf-8', closefd=True) as data:
            lines = data.readlines()

        gomod_data = {}
        require = []
        exclude = []

        for i, line in enumerate(lines):
            line = self.preprocess(line)
            parsed_module = self.parse_module(line)
            if parsed_module:
                gomod_data['module'] = parsed_module.group('module')

            parsed_module_name = self.parse_module_name(line)
            if parsed_module_name:
                gomod_data['name'] = parsed_module_name.group('name')
                gomod_data['namespace'] = parsed_module_name.group('namespace')
                
            parsed_require = self.parse_require(line)
            if parsed_require:
                line_req = [parsed_require.group('namespace'), parsed_require.group('name'), parsed_require.group('version')]
                require.append(line_req)

            parsed_exclude = self.parse_exclude(line)
            if parsed_exclude:
                line_exclude = [parsed_exclude.group('namespace'), parsed_exclude.group('name'), parsed_exclude.group('version')]
                exclude.append(line_exclude)

            if 'require' in line and '(' in line:
                for req in lines[i+1:]:
                    req = self.preprocess(req)
                    if ')' in req:
                        break
                    parsed_dep_link = self.parse_dep_link(req)
                    if parsed_dep_link:
                        line_req = [parsed_dep_link.group('namespace'), parsed_dep_link.group('name'), parsed_dep_link.group('version')]
                        require.append(line_req)

            if 'exclude' in line and '(' in line:
                for exc in lines[i+1:]:
                    exc = self.preprocess(exc)
                    if ')' in exc:
                        break
                    parsed_dep_link = self.parse_dep_link(exc)
                    if parsed_dep_link:
                        line_exclude = [parsed_dep_link.group('namespace'), parsed_dep_link.group('name'), parsed_dep_link.group('version')]
                        exclude.append(line_exclude)

        gomod_data['require'] = require
        gomod_data['exclude'] = exclude

        return gomod_data
