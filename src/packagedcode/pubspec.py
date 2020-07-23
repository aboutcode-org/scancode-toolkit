#
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
import sys

import yaml
import attr
from packageurl import PackageUrl
from commoncode import filetype
from packagedcode import models

from packagedcode import models

TRACE = False

def logger_debug(*args):
    pass

logger = logginf.getLogger(__name__)

if TRACE:
    logging.basicConfig(stream = sys.stdout)
    logger.setLevel(logging.DEBUG)
    
    def logger_debug(*args):
        return logger.debug(''.join(isinstance(a, string_types) and a or repr(a) for a in args))

@attr.s()
class PubspecPackage(models.Package):
    metafiles = ('pubspec.yaml',)
    extensions = ('.yaml',)
    default_type = 'pubspec'
    default_primary_language = 'dart'
    default_web_baseurl = 'https://dart.dev/tools/pub/pubspec
    default_download_baseurl = 'https://dart.dev/tools/pub/pubspec'
    default_api_baseurl = 'https://dart.dev/tools/pub/pubspec'

    @classmethod
    def recognize(cls, location):
        yield parse(location)

    def repository_homepage_url(self, baseurl=default_web_baseurl):
        return '{}/pods/{}'.format(baseurl, self.name)

    def repository_download_url(self):
        return '{}/archive/{}.zip'.format(self.homepage_url, self.version)

    def api_data_url(self):
        return self.homepage_url


"""
checking whether the given file is yaml or not (pubspec.yaml) 
"""
def is_yaml(location):
    """
    Check if the file is a yaml file or not
    """
    return (filetype.is_file(location) 
            and location.endswith('.yaml'))

def parse_pubspec(location):
    """
    code to parse pubspec.yaml 
    """
    contents = io.open(location, encoding ='utf-8').readlines()
    with open(location,'r') as stream:
        pubspec_data = pubspec.load(stream)
    return pubspec_data

def parse(location):
    if not is_yaml(location):
        return
    package_data = parse_pubspec(location)
    return build_package(package_data)

def build_package(pubspec_data):
    """
    Return a package object from a package data mapping ir None
    """
    name = pubspec_data.get('name')
    version = pubspec_data.get('version')
    declared_license = pubspec_data.get('license')
    description = pubspec_data.get('description')
    homepage_url = pubspec_data.get('homepage_url')
    repository = pubspec_data.get('repository')
    dependecies = pubspec_data.get('dependencies')
    dev_dependecies = pubspec_data.get('dev_dependencies')
    dependencies_overrides = pubspec_get('dependencies_overrides')
    environment = pubspec_data.get('environment')
    executables = pubspec_data.get('executables')
    publish_to = pubspec_data.get('publish_to')    
    authors = pubspec_data.get('author') or []
    
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
    dependencies = pubspec_data.get('dependencies')
    package_dependencies = []
    if dependencies:
        for dep_name, dep_version in dependencies.items():
            package_dependencies.append(
                    models.DependentPackage(
                            purl=PackageURL(
                                    """
                                    need to specify the type
                                    """
                                    type='',
                                            name=dep_name).toString(),
                                            scope='dependencies',
                                            is_runtime=True,
                                            is_optional=True,
                                            requirement=dep_version,
                                            )
                            )
   """ if dev_dependencies:
                for dep_name, dep_version in dev_dependencies.items():
                    package_dependencies.append(
                            models.DependentPackage(
                                    purl=PackageURL(
                                            """
                                            need to specify the type again
                                            """
                                            type='',
                                            name=dep_name).toString(),
                                            scope='dev_dependencies',
                                            is_runtime=True,
                                            is_optional=True,
                                            requirement=dep_version,
                                            )
                            )
                                    should add the code for dev_dependencies or not ???
                                    """
        
    package = PubspecPackage(
            name = name,
            version = version,
            vcs_url = source,
            source_packages=list(source.split('\n')),
            description=desciption,
            declared_license=declared_license,
            homepage_url=homepage_url,
            parties=parties,
            dependencies=package_dependencies
            )
    return package
     
    
