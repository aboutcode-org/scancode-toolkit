#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import io
import re

from gemfileparser import GemfileParser

from packagedcode import models
from packageurl import PackageURL
from functools import partial

"""
Handle Cocoapods (.podspec/Pofile) and Ruby(.gemspec/Gemfile) files.
"""

# FIXME: code needs cleanup

parse_name = re.compile(r'.*\.name(\s*)=(?P<name>.*)')
parse_version = re.compile(r'.*\.version(\s*)=(?P<version>.*)')
parse_summary = re.compile(r'.*\.summary(\s*)=(?P<summary>.*)')
parse_description = re.compile(r'.*\.description(\s*)=(?P<description>.*)')
parse_homepage = re.compile(r'.*\.homepage(\s*)=(?P<homepage>.*)')

parse_license = re.compile(r'.*\.license(\s*)=(?P<license>.*)')
parse_source = re.compile(r'.*\.source(\s*)=(?P<source>.*)')

# See in gemspec
# for file refs:
#  files
#  test_files
#  extensions
#  executables
#  extra_rdoc_files
# date = "2017-11-07" 
# metadata
# rubygems_version
# licenses = ['MIT']
# authors = ["Javan Makhmali".freeze, "Sam Stephenson".freeze, "David Heinemeier Hansson".freeze]
# email = ["javan@javan.us".freeze, "sstephenson@gmail.com".freeze, "david@loudthinking.com".freeze]
# email = 'rubocop@googlegroups.com'

def get_value(name, matcher, line):
    """
    Return the value for the ``name`` attribute collected using the ``matcher``
    regex in the ``line`` text.
    """
    match = matcher.match(line)
    if match:
        name = match.group(name)
        return get_cleaned_string(name)


# FIXME: this does not smell right as we ignore the matched value
def get_source(line):
    if '.source' in line:
        match = get_value(name='source', matcher=parse_source, line=line)
        if match:
            source = re.sub(r'/*.*source.*?>', '', line)
            stripped_source = re.sub(r',.*', '', source)
            return get_cleaned_string(stripped_source)


# mapping of parser callable by its field name
PARSER_BY_NAME = {
    'name': partial(get_value, name='name', match=parse_name),
    'version': partial(get_value, name='version', match=parse_version),
    'license': partial(get_value, name='license', match=parse_license),
    'summary': partial(get_value, name='summary', match=parse_summary),
    'description': partial(get_value, name='description', match=parse_description),
    'homepage': partial(get_value, name='homepage', match=parse_homepage),
    'source': get_source,
}


def parse_spec(location, package_type):
    """
    Return a mapping of data parsed from a podspec/gemspec/Pofile/Gemfile file
    at ``location``. Use ``package_type`` a Package URL type for dependencies.
    dependencies is a list of DependentPackage.
    """
    spec_data = {}
    with open(location) as lines:

        for line in lines:
            line = pre_process(line)

            for attribute_name, parser in PARSER_BY_NAME.items():
                parsed = parser(line)
                if parsed:
                    spec_data[attribute_name] = parsed

            match = parse_description(line)
            if match:
                if location.endswith('.gemspec'):
                    # FIXME: description can be in single or multi-lines
                    # There are many different ways to write description.
                    description = match.group('description')
                    spec_data['description'] = get_cleaned_string(description)
                else:
                    spec_data['description'] = get_description(location)

            if '.email' in line:
                _key, _sep, value = line.rpartition('=')
                stripped_emails = get_cleaned_string(value)
                stripped_emails = stripped_emails.strip()
                stripped_emails = stripped_emails.split(',')
                spec_data['email'] = stripped_emails

            elif '.author' in line:
                authors = re.sub(r'/*.*author.*?=', '', line)
                stripped_authors = get_cleaned_string(authors)
                stripped_authors = re.sub(r'(\s*=>\s*)', '=>', stripped_authors)
                stripped_authors = stripped_authors.strip()
                stripped_authors = stripped_authors.split(',')
                spec_data['author'] = stripped_authors

    # FIXME: why are we parsing twice?: merge all in gemfileparser
    spec_data['dependencies'] = list(get_dependent_packages(
        location=location,
        package_type=package_type,
    ))

    return spec_data


def get_dependent_packages(location, package_type):
    """
    Yield DependentPackage from the file at ``location`` for the given
    ``package_type``.
    """
    flags_by_scope = {
        'runtime': dict(is_runtime=True, is_optional=False),
        'dependency': dict(is_runtime=True, is_optional=False),
        'production': dict(is_runtime=True, is_optional=False),

        'development': dict(is_runtime=False, is_optional=True),
        'test': dict(is_runtime=False, is_optional=True),
        'metrics': dict(is_runtime=False, is_optional=True),
        }

    dependencies = GemfileParser(location).parse()
    for deps in dependencies.values():
        for dep in deps:
            scope = dep['scope']
            flags = flags_by_scope.get(scope, 'runtime')
            yield models.DependentPackage(
                purl=PackageURL(type=package_type, name=dep['name']),
                extracted_requirement=', '.join(dep['requirement']),
                scope=scope,
                is_resolved=False,
                **flags,
            )


def pre_process(line):
    """
    Return a ``line`` cleaned from comments markers and space.
    """
    if '#' in line:
        line = line[:line.index('#')]
    return line.strip()


def get_cleaned_string(string):
    """
    Return ``string`` removing unnecessary special character
    """
    if string:
        for replaceable in ("'", '"', '{', '}', '[', ']', '%q','<', '>', '.freeze'):
            string = string.replace(replaceable, '')
        return string.strip()


def get_description(location):
    """
    Return description from podspec.

    https://guides.cocoapods.org/syntax/podspec.html#description
    description is in the form:
    spec.description = <<-DESC
         Computes the meaning of life.
         Features:
         1. Is self aware
         ...
         42. Likes candies.
        DESC
    """
    with io.open(location, encoding='utf-8', closefd=True) as data:
        lines = data.readlines()
    description = ''
    for i, content in enumerate(lines):
        if '.description' in content:
            for cont in lines[i + 1:]:
                if 'DESC' in cont:
                    break
                description += ' '.join([description, cont.strip()])
            break
    description.strip()
    return description
