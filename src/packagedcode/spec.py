#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import re

from gemfileparser import GemfileParser

from packagedcode import models
from packageurl import PackageURL
from functools import partial

"""
Handle Cocoapods (.podspec/Pofile) and Ruby(.gemspec/Gemfile) files.
"""

# FIXME: code needs cleanup

parse_name = re.compile(
    r'.*\.name\s*=\s*'
    r'(?P<name>.*)'
)

parse_version = re.compile(
    r'.*\.version\s*=\s*'
    f'(?P<version>.*)'
)

parse_summary = re.compile(
    r'.*\.summary\s*=\s*'
    r'(?P<summary>.*)',
)

# simple single line quoted description
parse_description = re.compile(
    r'.*\.description\s*=\s*'
    r'(?P<description>.*)',
)

parse_homepage = re.compile(
    r'.*\.homepage\s*=\s*'
    r'(?P<homepage>.*)'
)

parse_license = re.compile(
    r'.*\.license\s*=\s*'
    r'(?P<license>.*)'
)

parse_podspec_source = re.compile(
    r'.*\.source\s*=\s*'
    r'(?P<source>.*)'
)

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


def get_value(name, matcher, line, clean=True):
    """
    Return the value for the ``name`` attribute collected using the ``matcher``
    regex in the ``line`` text.
    """
    match = matcher.match(line)
    if match:
        value = match.group(name)
        return get_cleaned_string(value) if clean else value


# FIXME: this does not smell right as we ignore the matched value
def get_podspec_source(line):
    if '.source' in line:
        match = get_value(name='source', matcher=parse_podspec_source, line=line)
        if match:
            source = re.sub(r'/*.*source.*?>', '', line)
            stripped_source = re.sub(r',.*', '', source)
            return get_cleaned_string(stripped_source)


def get_emails(line):
    """
    Return a list of emails extracted from a text ``line``, or None
    """
    if '.email' in line:
        _key, _sep, value = line.rpartition('=')
        stripped_emails = get_cleaned_string(value)
        stripped_emails = stripped_emails.strip()
        stripped_emails = stripped_emails.split(',')
        return stripped_emails


def get_authors(line):
    """
    Return a list of authors extracted from a text ``line``, or None
    """
    if '.author' in line:
        authors = re.sub(r'/*.*author.*?=', '', line)
        stripped_authors = get_cleaned_string(authors)
        stripped_authors = re.sub(r'(\s*=>\s*)', '=>', stripped_authors)
        stripped_authors = stripped_authors.strip()
        stripped_authors = stripped_authors.split(',')
        return stripped_authors


# mapping of parser callable by its field name
PARSER_BY_NAME = {
    'name': partial(get_value, name='name', matcher=parse_name),
    'version': partial(get_value, name='version', matcher=parse_version),
    'license': partial(get_value, name='license', matcher=parse_license),
    'summary': partial(get_value, name='summary', matcher=parse_summary),
    'description': partial(get_value, name='description', matcher=parse_description, clean=False),
    'homepage': partial(get_value, name='homepage', matcher=parse_homepage),
    'source': get_podspec_source,
    'email': get_emails,
    'author': get_authors,
}


def parse_spec(location, package_type):
    """
    Return a mapping of data parsed from a podspec/gemspec/Pofile/Gemfile file
    at ``location``. Use ``package_type`` a Package URL type for dependencies.
    dependencies is a list of DependentPackage.
    """
    spec_data = {}
    with open(location) as spec:
        content = spec.read()

    lines = content.splitlines()
    for line in lines:
        line = pre_process(line)

        for attribute_name, parser in PARSER_BY_NAME.items():
            parsed = parser(line=line)
            if parsed:
                spec_data[attribute_name] = parsed

    # description can be in single or multi-lines
    # There are many different ways to write description.
    # we reparse for multline
    description = spec_data.get("description")
    if description:
        if '<<-' in description:
            # a Ruby multiline text
            spec_data['description'] = get_multiline_description(
                description_start=description,
                lines=lines,
            )
        else:
            # a single quoted description
            spec_data['description'] = get_cleaned_string(description)

    # We avoid reloading twice the file but we are still parsing twice: need to
    # merge all in gemfileparser or write a better parser.
    spec_data['dependencies'] = list(get_dependent_packages(
        lines=lines,
        location=location,
        package_type=package_type,
    ))

    return spec_data


def get_dependent_packages(lines, location, package_type):
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

    dependencies = LinesBasedGemfileParser(lines=lines, filepath=location).parse()

    for key in dependencies:
        depends = dependencies.get(key, []) or []
        for dep in depends:
            flags = flags_by_scope.get(key, 'runtime')

            yield models.DependentPackage(
                purl=PackageURL(type=package_type, name=dep.name).to_string(),
                extracted_requirement=', '.join(dep.requirement),
                scope=key,
                is_resolved=False,
                **flags,
            )


class LinesBasedGemfileParser(GemfileParser):
    """
    A GemfileParser that works from a text lines rather than re-reading a file.
    Done to avoid reading a file twice.
    """

    def __init__(self, lines, filepath, appname=''):
        self.filepath = filepath

        self.current_group = 'runtime'

        self.appname = appname
        self.dependencies = {
            'development': [],
            'runtime': [],
            'dependency': [],
            'test': [],
            'production': [],
            'metrics': [],
        }
        self.contents = lines

        self.gemspec = filepath.endswith(('.gemspec', '.podspec'))


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
        for replaceable in ("'", '"', '{', '}', '[', ']', '%q', '<', '>', '.freeze'):
            string = string.replace(replaceable, '')
        return string.strip()


def get_multiline_description(description_start, lines):
    """
    Return a multiline description given the ``description_start`` start of the
    decsription and a ``lines`` list. These are common in .podspec.

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
    # from "<<-DESC" to "DESC"
    description_end = description_start.strip('<-')
    description_lines = []
    started = False
    for line  in lines:
        if started:
            ended = line.strip().startswith(description_end)
            if not ended:
                description_lines.append(line)
            else:
                break

        elif '.description' in line and description_start in line:
            started = True

    return '\n'.join(description_lines)
