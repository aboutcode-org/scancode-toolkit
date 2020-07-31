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

import io
import itertools
import logging
import re

import attr


"""
This modules handles go.sum files from Go.
See https://blog.golang.org/using-go-modules for details

A go.sum file contains pinned Go modules checksums of two styles:

For example:
github.com/BurntSushi/toml v0.3.1 h1:WXkYYl6Yr3qBf1K79EBnL4mak0OimBfB0XUf9Vl28OQ=
github.com/BurntSushi/toml v0.3.1/go.mod h1:xHWCNGjB5oqiDr8zfno3MHue2Ht5sIBksp03qcyfWMU=

... where the line with /go.mod is for a check of that go.mod file 
and the other line contains a dirhash for that path as documented as
https://pkg.go.dev/golang.org/x/mod/sumdb/dirhash

Here are some example of usage of this module::

>>> p = parse_dep_type2('github.com/BurntSushi/toml v0.3.1 h1:WXkYYl6Yr3qBf1K79EBnL4mak0OimBfB0XUf9Vl28OQ=')
>>> assert p.group('namespace') == ('github.com/BurntSushi')
>>> assert p.group('name') == ('toml')
>>> assert p.group('version') == ('v0.3.1')
>>> assert p.group('checksum') == ('WXkYYl6Yr3qBf1K79EBnL4mak0OimBfB0XUf9Vl28OQ=')

>>> p = parse_dep_type1('github.com/BurntSushi/toml v0.3.1/go.mod h1:xHWCNGjB5oqiDr8zfno3MHue2Ht5sIBksp03qcyfWMU=')
>>> assert p.group('namespace') == ('github.com/BurntSushi')
>>> assert p.group('name') == ('toml')
>>> assert p.group('version') == ('v0.3.1')
>>> assert p.group('checksum') == ('xHWCNGjB5oqiDr8zfno3MHue2Ht5sIBksp03qcyfWMU=')
"""


TRACE = False

logger = logging.getLogger(__name__)

if TRACE:
    import sys
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)


@attr.s()
class GoSum(object):
    namespace = attr.ib(default=None)
    name = attr.ib(default=None)
    version = attr.ib(default=None)

    def __init__(self, namespace, name, version):
        self.namespace = namespace
        self.name = name
        self.version = version

# Regex expressions to parse different types of dependency
# dep_type1 example: github.com/BurntSushi/toml v0.3.1 h1:WXkYY....
parse_dep_type1 = re.compile(
    r'(?P<namespace>(.*))'
    r'\/'
    r'(?P<name>[^\s]*)'
    r'(\s)*'
    r'(?P<version>(.*))'
    r'/go.mod(\s)*h1:'
    r'(?P<checksum>(.*))'
).match

# dep_type2 example: github.com/BurntSushi/toml v0.3.1/go.mod h1:xHWCN....
parse_dep_type2 = re.compile(
    r'(?P<namespace>(.*))'
    r'/'
    r'(?P<name>[^\s]*)'
    r'(\s)*'
    r'(?P<version>(.*))'
    r'(\s)*h1:'
    r'(?P<checksum>(.*))'
).match


def parse_gosum(location):
    """
    Return a list containing all the go.sum dependency data.
    """
    with io.open(location, encoding='utf-8', closefd=True) as data:
        lines = data.readlines()

    gosums = []

    for line in lines:
        parsed_dep = parse_dep_type1(line)
        if not parsed_dep:
            parsed_dep = parse_dep_type2(line)

        dep_obj = GoSum(
                namespace=parsed_dep.group('namespace').strip(),
                name=parsed_dep.group('name').strip(),
                version=parsed_dep.group('version').strip()
            )

        if dep_obj not in gosums:
            gosums.append(dep_obj)

    return gosums
