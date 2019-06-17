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

from collections import OrderedDict
import io
import logging
import sys

import attr
from  saneyaml import load as yamlload
from six import string_types

from commoncode import filetype
from commoncode import fileutils
from packagedcode import models


"""
Parse Conda manifests, see https://getcomposer.org/ and
https://packagist.org/

"""

TRACE = False


def logger_debug(*args):
    pass


logger = logging.getLogger(__name__)

if TRACE:
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, string_types) and a or repr(a) for a in args))


@attr.s()
class CondaPackage(models.Package):
    metafiles = ('meta.yaml',)
    filetypes = ('.yaml',)
    mimetypes = ('application/json',)
    default_type = 'conda'
    default_web_baseurl = None
    default_download_baseurl = None
    default_api_baseurl = None

    @classmethod
    def recognize(cls, location):
        return parse(location)


def is_conda_yaml(location):
    return (filetype.is_file(location) and fileutils.file_name(location).lower() == 'meta.yaml')


def parse(location):
    """
    Return a Package object from a meta.yaml file or None.
    """
    if not is_conda_yaml(location):
        return

    yaml_data = get_yaml_data(location)
    return build_package(yaml_data)


def build_package(package_data):
    """
    Return a Conda Package object from a dictionary yaml data.
    """
    for key, value in package_data.items():
            print('eeeeeeeee')
            print(key)
            print(value)
    
    name = None
    version = None
    package_element = package_data.get('package')
    if package_element:
        for key, value in package_element.items():
            if key == 'name':
                name = value
            if key == 'version':
                version = value
    if name:
        package = CondaPackage(
            name=name,
            version=version or None,
        )
        return package
       
   
def get_yaml_data(location):
    """
    Get variables and parse the yaml file, replace the variable with the value and return dictionary.
    """
    variables = get_variables(location)
    yaml_lines = []
    with io.open(location, encoding='utf-8') as loc:
        for line in loc.readlines():
            if not line:
                continue
            pure_line = line.strip()
            if pure_line.startswith('{%') and pure_line.endswith('%}') and '=' in pure_line:
                continue
            # Replace the variable with the value
            if '{{' in line and '}}' in line:
                for variable, value in variables.items():
                    line = line.replace('{{ ' + variable + ' }}', value)                        
            yaml_lines.append(line)
    return yamlload('\n'.join(yaml_lines))
    
    
def get_variables(location):
    """
    Conda yaml will have variables defined at the beginning of the file, the idea is to parse it and return a dictionary of the variable and value
    For example:
    {% set version = "0.45.0" %}
    {% set sha256 = "bc7512f2eef785b037d836f4cc6faded457ac277f75c6e34eccd12da7c85258f" %}
    """
    result = OrderedDict()
    with io.open(location, encoding='utf-8') as loc:
        for line in loc.readlines():
            if not line:
                continue
            line = line.strip()
            if line.startswith('{%') and line.endswith('%}') and '=' in line:
                line = line.lstrip('{%').rstrip('%}').strip().lstrip('set').lstrip()
                parts = line.split('=')
                result[parts[0].strip()] = parts[-1].strip().strip('"')
    return result
