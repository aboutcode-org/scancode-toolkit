
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import re

from packageurl import PackageURL

from packagedcode import models

"""
Handle OCaml opam package.
"""


class OpamFileHandler(models.DatafileHandler):
    datasource_id = 'opam_file'
    path_patterns = ('*opam',)
    default_package_type = 'opam'
    default_primary_language = 'Ocaml'
    description = 'Ocaml Opam file'
    documentation_url = 'https://opam.ocaml.org/doc/Manual.html#Common-file-format'

    @classmethod
    def get_package_root(cls, resource, codebase):
        return resource.parent(codebase)

    @classmethod
    def parse(cls, location):
        opams = parse_opam(location)

        package_dependencies = []
        deps = opams.get('depends') or []
        for dep in deps:
            package_dependencies.append(
                models.DependentPackage(
                    purl=dep["purl"],
                    extracted_requirement=dep["version"],
                    scope='dependency',
                    is_runtime=True,
                    is_optional=False,
                    is_resolved=False,
                )
            )

        name = opams.get('name')
        version = opams.get('version')

        homepage_url = opams.get('homepage')
        download_url = opams.get('src')
        vcs_url = opams.get('dev-repo')
        bug_tracking_url = opams.get('bug-reports')
        declared_license = opams.get('license')
        sha1 = opams.get('sha1')
        md5 = opams.get('md5')
        sha256 = opams.get('sha256')
        sha512 = opams.get('sha512')
        repository_homepage_url = get_repository_homepage_url(name)
        api_data_url = get_api_data_url(name, version)

        short_desc = opams.get('synopsis') or ''
        long_desc = opams.get('description') or ''
        if long_desc == short_desc:
            long_desc = None
        descriptions = [d for d in (short_desc, long_desc) if d and d.strip()]
        description = '\n'.join(descriptions)

        parties = []
        authors = opams.get('authors') or []
        for author in authors:
            parties.append(
                models.Party(
                    type=models.party_person,
                    name=author,
                    role='author'
                )
            )
        maintainers = opams.get('maintainer') or []
        for maintainer in maintainers:
            parties.append(
                models.Party(
                    type=models.party_person,
                    email=maintainer,
                    role='maintainer'
                )
            )

        package_data = models.PackageData(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            name=name,
            version=version,
            vcs_url=vcs_url,
            homepage_url=homepage_url,
            download_url=download_url,
            sha1=sha1,
            md5=md5,
            sha256=sha256,
            sha512=sha512,
            bug_tracking_url=bug_tracking_url,
            declared_license=declared_license,
            description=description,
            parties=parties,
            dependencies=package_dependencies,
            api_data_url=api_data_url,
            repository_homepage_url=repository_homepage_url,
            primary_language=cls.default_primary_language
        )

        if not package_data.license_expression and package_data.declared_license:
            package_data.license_expression = models.compute_normalized_license(package_data.declared_license)

        yield package_data

    @classmethod
    def assign_package_to_resources(cls, package, resource, codebase, package_adder):
        return models.DatafileHandler.assign_package_to_parent_tree(package, resource, codebase, package_adder)


def get_repository_homepage_url(name):
    return name and '{https://opam.ocaml.org/packages}/{name}'


def get_api_data_url(name, version):
    if name and version:
        return f'https://github.com/ocaml/opam-repository/blob/master/packages/{name}/{name}.{version}/opam'


# Regex expressions to parse file lines
parse_file_line = re.compile(
    r'(?P<key>^(.+?))'
    r'\:\s*'
    r'(?P<value>(.*))'
).match

parse_checksum = re.compile(
    r'(?P<key>^(.+?))'
    r'\='
    r'(?P<value>(.*))'
).match

parse_dep = re.compile(
    r'^\s*\"'
    r'(?P<name>[A-z0-9\-]*)'
    r'\"\s*'
    r'(?P<version>(.*))'
).match

"""
Example:
>>> p = parse_file_line('authors: "BAP Team"')
>>> assert p.group('key') == ('authors')
>>> assert p.group('value') == ('"BAP Team"')

>>> p = parse_file_line('md5=b7a7b7cce64eabf224d05ed9f2b9d471')
>>> assert p.group('key') == ('md5')
>>> assert p.group('value') == ('b7a7b7cce64eabf224d05ed9f2b9d471')

>>> p = parse_dep('"bap-std" {= "1.0.0"}')
>>> assert p.group('name') == ('bap-std')
>>> assert p.group('version') == ('{= "1.0.0"}')
"""


def parse_opam(location):
    """
    Return a mapping of package data collected from the opam OCaml package
    manifest file at ``location``.
    """
    with open(location) as od:
        text = od.read()
    return parse_opam_from_text(text)


def parse_opam_from_text(text):
    """
    Return a mapping of package data collected from the opam OCaml package
    manifest ``text``.
    """

    opam_data = {}

    lines = text.splitlines()
    for i, line in enumerate(lines):
        parsed_line = parse_file_line(line)
        if not parsed_line:
            continue
        key = parsed_line.group('key').strip()
        value = parsed_line.group('value').strip()
        if key == 'description':  # Get multiline description
            value = ''
            for cont in lines[i + 1:]:
                value += ' ' + cont.strip()
                if '"""' in cont:
                    break

        opam_data[key] = clean_data(value)

        if key == 'maintainer':
            stripped_val = value.strip('["] ')
            stripped_val = stripped_val.split('" "')
            opam_data[key] = stripped_val
        elif key == 'authors':
            if '[' in line:  # If authors are present in multiple lines
                for authors in lines[i + 1:]:
                    value += ' ' + authors.strip()
                    if ']' in authors:
                        break
                value = value.strip('["] ')
            else:
                value = clean_data(value)
            value = value.split('" "')
            opam_data[key] = value
        elif key == 'depends':  # Get multiline dependencies
            value = []
            for dep in lines[i + 1:]:
                if ']' in dep:
                    break
                parsed_dep = parse_dep(dep)
                if parsed_dep:
                    version = parsed_dep.group('version').strip('{ } ').replace('"', '')
                    name = parsed_dep.group('name').strip()
                    value.append(dict(
                        purl=PackageURL(type='opam', name=name).to_string(),
                        version=version,
                    ))
            opam_data[key] = value

        elif key == 'src':  # Get multiline src
            if not value:
                value = lines[i + 1].strip()
            opam_data[key] = clean_data(value)
        elif key == 'checksum':  # Get checksums
            if '[' in line:
                for checksum in lines[i + 1:]:
                    checksum = checksum.strip('" ')
                    if ']' in checksum:
                        break
                    parsed_checksum = parse_checksum(checksum)
                    key = clean_data(parsed_checksum.group('key').strip())
                    value = clean_data(parsed_checksum.group('value').strip())
                    opam_data[key] = value
            else:
                value = value.strip('" ')
                parsed_checksum = parse_checksum(value)
                if parsed_checksum:
                    key = clean_data(parsed_checksum.group('key').strip())
                    value = clean_data(parsed_checksum.group('value').strip())
                    opam_data[key] = value

    return opam_data


def clean_data(data):
    """
    Return data after removing unnecessary special character.
    """
    for strippable in ("'", '"', '[', ']',):
        data = data.replace(strippable, '')

    return data.strip()
