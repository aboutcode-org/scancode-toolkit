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

from collections import OrderedDict
import csv
import glob
import io
import logging
import os
import re

import attr
from packageurl import PackageURL

from commoncode.fileutils import py2
from commoncode import filetype
from commoncode import fileutils
from packagedcode import models


"""
Handle Podspec Package Manager
"""

TRACE = False

logger = logging.getLogger(__name__)

if TRACE:
    import sys
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)


@attr.s()
class PodspecPackage(models.Package):
    metafiles = ('*.podspec',)
    extensions = ('.podspec',)
    default_type = 'pods'
    default_primary_language = 'Objective-C'
    default_web_baseurl = 'https://cocoapods.org'
    default_download_baseurl = 'https://cocoapods.org'
    default_api_baseurl = 'https://cocoapods.org'

    @classmethod
    def recognize(cls, location):
        yield parse(location)

    def repository_homepage_url(self, baseurl=default_web_baseurl):
        return '{}/pods/{}'.format(baseurl, self.name)

    def repository_download_url(self):
        return '{}/archive/{}.zip'.format(self.homepage_url, self.version)

    def api_data_url(self):
        return self.homepage_url


def is_podspec(location):
    """
    Checks is the file is a podspec file or not.
    """
    return (filetype.is_file(location) and location.endswith('.podspec'))


def parse(location):
    """
    Return a Package object from a .podspec file or None.
    """
    if not is_podspec(location):
        return

    package_data = parse_podspec(location)
    return build_package(package_data)


def build_package(podspec_data):
    """
    Return a Pacakge object from a package data mapping or None.
    """
    name = podspec_data.get('name')
    version = podspec_data.get('version')
    declared_license = podspec_data.get('license')
    description = podspec_data.get('description')
    homepage_url = podspec_data.get('homepage_url')
    source = podspec_data.get('source')
    authors = podspec_data.get('author') or []
    email = podspec_data.get('email') or []

    parties = []
    if authors:
        parties.append(
            models.Party(
                type=models.party_person,
                name=', '.join(authors),
                email=', '.join(email),
                role='author'
            )
        )

    dependencies = podspec_data.get('dependencies')
    package_dependencies = []
    if dependencies:
        for dep_name, dep_version in dependencies.items():
            package_dependencies.append(
                models.DependentPackage(
                    purl=PackageURL(
                        type='pods', name=dep_name).to_string(),
                    scope='dependencies',
                    is_runtime=True,
                    is_optional=False,
                    requirement=dep_version,
                )
            )
    package = PodspecPackage(
        name=name,
        version=version,
        vcs_url=source,
        source_packages=list(source.split('\n')),
        description=description,
        declared_license=declared_license,
        homepage_url=homepage_url,
        parties=parties,
        dependencies=package_dependencies
    )
    return package


def preprocess(line):
    """
    Removes the comment portion and excess spaces.
    """
    if "#" in line:
        line = line[:line.index('#')]
    line = line.strip()
    return line


def parse_line(line):
    """
    Parses each line and creates dependency objects accordingly
    """
    try:

        # StringIO requires a unicode object.
        # But unicode() doesn't work with Python3
        # as it is already in unicode format.
        # So, first try converting and if that fails, use original.

        line = unicode(line)
    except NameError:
        pass
    linefile = io.StringIO(line)    # csv requires a file object
    for line in csv.reader(linefile, delimiter=','):
        column_list = []
        for column in line:
            stripped_column = column.replace("'", "")
            stripped_column = stripped_column.replace('"', "")
            stripped_column = stripped_column.replace('(%q<', "")
            stripped_column = stripped_column.replace('[', "")
            stripped_column = stripped_column.strip()
            column_list.append(stripped_column)
    return column_list


def parse_podspec(location):
    """
    Method to handle podspec files.
    """
    contents = io.open(location, encoding='utf-8').readlines()
    podspec_data = {}
    for line in contents:
        line = preprocess(line)
        if '.name' in line:
            name = re.sub(r"/*.*name.*= ", "", line)
            stripped_name = name.replace("'", "")
            stripped_name = stripped_name.replace('"', "")
            stripped_name = stripped_name.strip()
            podspec_data['name'] = stripped_name
        elif '.version' in line and '.version.' not in line:
            version = re.sub(r"/*.*version.*= ", "", line)
            stripped_version = version.replace("'", "")
            stripped_version = stripped_version.replace('"', "")
            stripped_version = stripped_version.strip()
            podspec_data['version'] = stripped_version
        elif '.license' in line:
            license_type = re.sub(r"/*.*license.*= ", "", line)
            stripped_license = license_type.replace("'", "")
            stripped_license = stripped_license.replace('"', "")
            stripped_license = stripped_license.replace('{', "")
            stripped_license = stripped_license.replace('}', "")
            stripped_license = stripped_license.strip()
            podspec_data['license'] = stripped_license
        elif '.source' in line and '.source_files' not in line:
            source = re.sub(r"/*.*source.*= ", "", line)
            stripped_source = source.replace("'", "")
            stripped_source = stripped_source.replace('"', "")
            stripped_source = stripped_source.replace('{', "")
            stripped_source = stripped_source.replace('}', "")
            stripped_source = stripped_source.strip()
            podspec_data['source'] = stripped_source
        elif '.author' in line:
            authors = re.sub(r"/*.*author.*= ", "", line)
            stripped_authors = authors.replace("'", "")
            stripped_authors = stripped_authors.replace('"', "")
            stripped_authors = stripped_authors.replace('{', "")
            stripped_authors = stripped_authors.replace('}', "")
            stripped_authors = stripped_authors.replace(' => ', "=>")
            stripped_authors = stripped_authors.strip()
            stripped_authors = stripped_authors.split(',')
            author_names = []
            author_email = []
            for split_author in stripped_authors:
                split_author = split_author.strip()
                author, email = parse_person(split_author)
                author_names.append(author)
                author_email.append(email)
            podspec_data['author'] = author_names
            podspec_data['email'] = author_email
        elif '.summary' in line:
            summary = re.sub(r"/*.*summary.*= ", "", line)
            stripped_summary = summary.replace("'", "")
            stripped_summary = stripped_summary.replace('"', "")
            stripped_summary = stripped_summary.strip()
            podspec_data['summary'] = stripped_summary
        elif '.description' in line:
            podspec_data['description'] = get_description(location)
        elif '.homepage' in line:
            homepage_url = re.sub(r"/*.*homepage.*= ", "", line)
            stripped_homepage_url = homepage_url.replace("'", "")
            stripped_homepage_url = stripped_homepage_url.replace('"', "")
            stripped_homepage_url = stripped_homepage_url.strip()
            podspec_data['homepage_url'] = stripped_homepage_url
        elif '.dependency' in line:
            match = add_dependency_regex(line)
            line = match.group('line')
            podspec_data['dependencies'] = parse_line(line)

    deps = OrderedDict()
    dependency = podspec_data.get('dependencies')
    if dependency:
        for dep in dependency:
            # dep = ['AFNetworking', '~> 2.3']
            dep_name = dep[0]
            dep.pop(0) # delete dependency name
            dep_version = dep
            deps[dep_name] = dep_version
    podspec_data['dependencies'] = deps
    return podspec_data


def get_description(location):
    """
    https://guides.cocoapods.org/syntax/podspec.html#description
    description is in the form:
    spec.description = <<-DESC
                     Computes the meaning of life.
                     Features:
                     1. Is self aware
                     ...
                     42. Likes candies.
                    DESC

    This function will return the multiline desciption.
    """
    contents = io.open(location, encoding='utf-8').readlines()
    description = ''
    for i, content in enumerate(contents):
        if '.description' in content:
            for j, cont in enumerate(contents[i+1:]):
                if 'DESC' in cont:
                    break
                description += ' '.join([description, cont.strip()])
            break
    return description


def parse_person(person):
    """
    https://guides.cocoapods.org/syntax/podspec.html#authors
    Author can be in the form:
        s.author = 'Rohit Potter'
        or
        s.author = 'Rohit Potter=>rohit@gmail.com'

    Author check:
    >>> p = parse_person('Rohit Potter=>rohit@gmail.com')
    >>> assert p == ('Rohit Potter', 'rohit@gmail.com')
    >>> p = parse_person('Rohit Potter')
    >>> assert p == ('Rohit Potter', None)
    """
    parsed = person_parser(person)
    if not parsed:
        parsed = person_parser_only_name(person)
        name = parsed.group('name')
        email = None
    else:
        name = parsed.group('name')
        email = parsed.group('email')

    return name, email


person_parser = re.compile(
    r'^(?P<name>[a-zA-Z0-9\s]+)'
    r'=>'
    r'(?P<email>[\S+]+$)'
).match

person_parser_only_name = re.compile(
    r'^(?P<name>[a-zA-Z0-9\s]+)'
).match

add_dependency_regex = re.compile(
    r'.*.dependency (?P<line>.*)'
).match