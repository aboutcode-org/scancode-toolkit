
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
import io
import logging
import re

import attr
from packageurl import PackageURL

from commoncode import filetype
from commoncode import fileutils
from packagedcode import models


"""
Handle opam package.
"""

TRACE = False

logger = logging.getLogger(__name__)

if TRACE:
    import sys
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)


@attr.s()
class OpamPackage(models.Package):
    metafiles = ('*.opam', 'opam')
    extensions = ('.opam',)
    default_type = 'opam'
    default_primary_language = 'Ocaml'
    default_web_baseurl = 'https://opam.ocaml.org/packages'
    default_download_baseurl = None
    default_api_baseurl = None

    @classmethod
    def recognize(cls, location):
        yield parse(location)

    @classmethod
    def get_package_root(cls, manifest_resource, codebase):
        return manifest_resource.parent(codebase)

    def repository_homepage_url(self, baseurl=default_web_baseurl):
        if self.name:
            return '{}/{}'.format(baseurl, self.name)


def is_opam(location):
    if location.endswith('.opam') or (filetype.is_file(location) and fileutils.file_name(location).lower() == 'opam'):
        return True
    return False


def parse(location):
    if not is_opam(location):
        return

    package_data = parse_opam(location)
    return build_opam_package(package_data)


def build_opam_package(package_data):
    """
    Return a Package object from a opam file or None.
    """
    package_dependencies = []
    deps = package_data.get('depends') or []
    for dep in deps:
        package_dependencies.append(
            models.DependentPackage(
                purl=dep.purl,
                requirement=dep.version,
                scope='dependency',
                is_runtime=True,
                is_optional=False,
                is_resolved=False,
            )
        )

    name = package_data.get('name')
    maintainers = package_data.get('maintainer') or []
    authors = package_data.get('authors') or []
    homepage_url = package_data.get('homepage')
    vcs_url = package_data.get('dev-repo')
    summary = package_data.get('synopsis')
    description = package_data.get('description')
    if summary and description:
        if len(summary) > len(description):
            description = summary
    
    parties = []
    for author in authors:
        parties.append(
            models.Party(
                type=models.party_person,
                name=author,
                email=None,
                role='author'
            )
        )
    
    for maintainer in maintainers:
        parties.append(
            models.Party(
                type=models.party_person,
                name=None,
                email=maintainer,
                role='email'
            )
        )

    package = OpamPackage(
        name=name or None,
        vcs_url=vcs_url or None,
        homepage_url=homepage_url,
        description=description,
        parties=parties,
        dependencies=package_dependencies
    )

    return package


@attr.s()
class Opam(object):
    name = attr.ib(default=None)
    version = attr.ib(default=None)

    @property
    def purl(self):
        return PackageURL(
                    type='opam',
                    name=self.name
                ).to_string()


# Regex expressions to parse file lines
parse_file_line = re.compile(
    r'(?P<key>^(.+?))'
    r'\:\s*'
    r'(?P<value>(.*))'
).match

parse_dep = re.compile(
    r'^\s*\"'
    r'(?P<name>[A-z0-9\-]*)'
    r'\"\s*'
    r'(?P<version>(.*))'
).match


def parse_opam(location):
    """
    Return a dictionary containing all the opam data.
    """
    with io.open(location, encoding='utf-8', closefd=True) as data:
        lines = data.readlines()

    opam_data = {}

    for i, line in enumerate(lines):
        parsed_line = parse_file_line(line)
        if parsed_line:
            key = parsed_line.group('key').strip()
            value = parsed_line.group('value').strip()
            if 'maintainer' == key:
                stripped_val = value.strip('["] ')
                stripped_val = stripped_val.split('" "')
                opam_data[key] = stripped_val
                continue
            if 'authors' == key:
                if '[' in line:
                    for authors in lines[i+1:]:
                        value += ' ' + authors.strip()
                        if ']' in authors:
                            break
                    value = value.strip('["] ')
                else:
                    value = get_stripped_data(value)   
                value = value.split('" "')
                opam_data[key] = value
                continue
            if 'depends' == key:
                value = []
                for dep in lines[i+1:]:
                    if ']' in dep:
                        break
                    parsed_dep = parse_dep(dep)
                    if parsed_dep:
                        value.append(Opam(
                                name=parsed_dep.group('name').strip(),
                                version=parsed_dep.group('version').strip('{ } ').replace('"', '')
                            )
                        )
                opam_data[key] = value
                continue
            if 'description' == key:
                value = ''
                for cont in lines[i+1:]:
                    value += ' ' + cont.strip()
                    if '"""' in cont:
                        break

            opam_data[key] = get_stripped_data(value)

    return opam_data


def get_stripped_data(data):
    """
    Return data after removing unnecessary special character
    """
    for strippable in ("'", '"', '[', ']',):
        data = data.replace(strippable, '')

    return data.strip()
