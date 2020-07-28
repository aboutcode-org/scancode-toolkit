
# All rights reserved.
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
https://blog.golang.org/using-go-modules

For example:

golang.org/x/text v0.0.0-20170915032832-14c0d48ead0c h1:qgOY6WgZO...
golang.org/x/text v0.0.0-20170915032832-14c0d48ead0c/go.mod h1:Nq...
rsc.io/quote v1.5.2 h1:w5fcysjrx7yqtD/aO+QwRjYZOKnaM9Uh2b40tElTs3...
rsc.io/quote v1.5.2/go.mod h1:LzX7hefJvL54yjefDEDHNONDjII0t9xZLPX...
rsc.io/sampler v1.3.0 h1:7uVkIFmeBqHfdjD+gZwtXXI+RODJ2Wc4O7MPEh/Q...
rsc.io/sampler v1.3.0/go.mod h1:T1hPZKmBbMNahiBKFy5HrXp6adAjACjK9...

"""

"""
go.sum file contains certain things in 2 formats.

For example:
github.com/BurntSushi/toml v0.3.1 h1:WXkYYl6Yr3qBf1K79EBnL4mak0OimBfB0XUf9Vl28OQ=
github.com/BurntSushi/toml v0.3.1/go.mod h1:xHWCNGjB5oqiDr8zfno3MHue2Ht5sIBksp03qcyfWMU=


>>> ob = GoSum()
>>> p = ob.parse_dep_type2('github.com/BurntSushi/toml v0.3.1 h1:WXkYYl6Yr3qBf1K79EBnL4mak0OimBfB0XUf9Vl28OQ=')
>>> assert p.group('namespace') == ('github.com/BurntSushi')
>>> assert p.group('name') == ('toml')
>>> assert p.group('version') == ('v0.3.1')
>>> assert p.group('checksum') == ('WXkYYl6Yr3qBf1K79EBnL4mak0OimBfB0XUf9Vl28OQ=')

>>> p = ob.parse_dep_type1('github.com/BurntSushi/toml v0.3.1/go.mod h1:xHWCNGjB5oqiDr8zfno3MHue2Ht5sIBksp03qcyfWMU=')
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

    @classmethod
    def parse_gosum(cls, location):
        """
        Return a list containing all the go.sum dependency data.
        """
        with io.open(location, encoding='utf-8', closefd=True) as data:
            lines = data.readlines()

        gosum_data = []

        for line in lines:
            parsed_dep = cls.parse_dep_type1(line)
            if not parsed_dep:
                parsed_dep = cls.parse_dep_type2(line)

            dep_data = [parsed_dep.group('namespace').strip(),
                    parsed_dep.group('name').strip(),
                    parsed_dep.group('version').strip()]

            gosum_data.append(dep_data)

        gosum_data.sort()
        gosum_data = list(gosum_data for gosum_data, _ in itertools.groupby(gosum_data))

        return gosum_data
