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


import csv
import glob
import io
import os
import re


"""
Handle Cocoapods(.podspec) and Ruby(.gemspec) files.
"""


def get_stripped_data(line):
    """
    Return data after removing unnecessary special character and space.
    """
    if '#' in line:
        line = line[:line.index('#')]
    stripped_data = line.strip()
    stripped_data = stripped_data.replace("'", '')
    stripped_data = stripped_data.replace('"', '')
    stripped_data = stripped_data.replace('{', '')
    stripped_data = stripped_data.replace('}', '')
    stripped_data = stripped_data.strip()
    return stripped_data


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
    Return description from podspec.
    """
    with io.open(location, encoding='utf-8', closefd=True) as data:
        lines = data.readlines()
    description = ''
    for i, content in enumerate(lines):
        if '.description' in content:
            for cont in lines[i+1:]:
                if 'DESC' in cont:
                    break
                description += ' '.join([description, cont.strip()])
            break
    description.strip()
    return description


def parse_spec(location):
    """
    Return dictionary contains podspec or gemspec file data.
    """
    with io.open(location, encoding='utf-8', closefd=True) as data:
        lines = data.readlines()

    spec_data = {}

    for line in lines:
        if '.name' in line:
            name = re.sub(r'/*.*name.*?=', '', line)
            spec_data['name'] = get_stripped_data(name)
        elif '.version' in line and '.version.' not in line:
            version = re.sub(r'/*.*version.*?=', '', line)
            spec_data['version'] = get_stripped_data(version)
        elif '.license' in line:
            license_type = re.sub(r'/*.*license.*?=', '', line)
            spec_data['license'] = get_stripped_data(license_type)
        elif '.source' in line and '.source_files' not in line:
            source = re.sub(r'/*.*source.*?>', '', line)
            stripped_source = re.sub(r',.*', '', source)
            spec_data['source'] = get_stripped_data(stripped_source)
        elif '.author' in line:
            authors = re.sub(r'/*.*author.*?=', '', line)
            stripped_authors = get_stripped_data(authors)
            stripped_authors = stripped_authors.replace(' => ', "=>")
            stripped_authors = stripped_authors.strip()
            stripped_authors = stripped_authors.split(',')
            spec_data['author'] = stripped_authors
        elif '.summary' in line:
            summary = re.sub(r'/*.*summary.*?=', '', line)
            spec_data['summary'] = get_stripped_data(summary)
        elif '.description' in line:
            spec_data['description'] = get_description(location)
        elif '.homepage' in line:
            homepage_url = re.sub(r'/*.*homepage.*?=', '', line)
            spec_data['homepage_url'] = get_stripped_data(homepage_url)

    return spec_data