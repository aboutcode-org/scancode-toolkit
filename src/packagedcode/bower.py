
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
#  OR CONDITIONS OF ANY KIND, either express or implied. No package_data created from
#  ScanCode should be considered or used as legal advice. Consult an Attorney
#  for any legal advice.
#  ScanCode is a free software code scanning tool from nexB Inc. and others.
#  Visit https://github.com/nexB/scancode-toolkit/ for support and download.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from collections import OrderedDict
from functools import partial
import io
import json
import logging
import re

import attr
from packageurl import PackageURL
from six import string_types

from commoncode import filetype
from commoncode import fileutils
from packagedcode import models
from packagedcode.utils import combine_expressions
from packagedcode.utils import parse_repo_url


TRACE = False

logger = logging.getLogger(__name__)

if TRACE:
    import sys
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)


@attr.s()
class BowerPackage(models.Package):
    metafiles = ('bower.json', '.bower.json')
    default_type = 'bower'

    @classmethod
    def recognize(cls, location):
        return parse(location)


def is_bower_json(location):
    return (filetype.is_file(location)
            and (fileutils.file_name(location).lower() == 'bower.json'
            or fileutils.file_name(location).lower() == '.bower.json'))


def parse(location):
    """
    Return a Package object from a package.json file or None.
    """
    if not is_bower_json(location):
        return

    with io.open(location, encoding='utf-8') as loc:
        package_data = json.load(loc, object_pairs_hook=OrderedDict)

    return build_package(package_data)


def get_vcs_repo(content):
    """
    Return the repo type and url.
    """
    repo = content.get('repository', {})
    if repo:
        return repo.get('type'), repo.get('url')
    return None, None


def build_packages_from_jsonfile(package_data, uri=None, purl=None):
    """
    Yield Package built from Bower json package_data
    """
    licenses_content = package_data.get('license')
    declared_licenses = set([])
    if licenses_content:
        if isinstance(licenses_content, list):
            for lic in licenses_content:
                declared_licenses.add(lic)
        else:
            declared_licenses.add(licenses_content)

    keywords_content = package_data.get('keywords', [])
    name = package_data.get('name')

    devdependencies = package_data.get('devDependencies')
    dev_dependencies = []
    if devdependencies:
        for key, value in devdependencies.items():
            dev_dependencies.append(
                models.DependentPackage(purl=key, requirement=value, scope='devdependency')
            )

    dependencies = package_data.get('dependencies')
    dependencies_build = []
    if dependencies:
        for key, value in dependencies.items():
            dependencies_build.append(
                models.DependentPackage(purl=key, requirement=value, scope='runtime')
            )

    if name:
        vcs_tool, vcs_repo = get_vcs_repo(package_data)
        if vcs_tool and vcs_repo:
            # Form the vsc_url by
            # https://spdx.org/spdx-specification-21-web-version#h.49x2ik5
            vcs_repo = vcs_tool + '+' + vcs_repo
        common_data = dict(
            type='bower',
            name=name,
            description=package_data.get('description'),
            version=package_data.get('version'),
            vcs_url=vcs_repo,
            keywords=keywords_content,
            homepage_url=package_data.get('homepage'),
        )

        if declared_licenses:
            common_data['declared_license'] = '\n'.join(declared_licenses)

        author_content = package_data.get('authors', [])
        if author_content:
            parties = common_data.get('parties')
            if not parties:
                common_data['parties'] = []
            for author in author_content:
                common_data['parties'].append(models.Party(name=author, role='author',))

        dependencies = []
        if dependencies_build:
            dependencies.extend(dependencies_build)
        if dev_dependencies:
            dependencies.extend(dev_dependencies)
        if len(dependencies) > 0:
            common_data['dependencies'] = dependencies
        package = BowerPackage(**common_data)
        package.set_purl(purl)
        yield package
