
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import logging
import os
import re
import sys

import toml
from packageurl import PackageURL

from packagedcode import models

"""
Handle Rust cargo crates
"""

TRACE = os.environ.get('SCANCODE_DEBUG_PACKAGE_CARGO', False)


def logger_debug(*args):
    pass


logger = logging.getLogger(__name__)

if TRACE:
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, str) and a or repr(a) for a in args))


class CargoBaseHandler(models.DatafileHandler):
    @classmethod
    def assemble(cls, package_data, resource, codebase, package_adder):
        """
        Assemble Cargo.toml and possible Cargo.lock datafiles. Also
        support cargo workspaces where we have multiple packages from
        a repository and some shared information present at top-level.
        """
        workspace = package_data.extra_data.get('workspace', {})
        workspace_members = workspace.get("members", [])
        workspace_package_data = workspace.get("package", {})
        attributes_to_copy = [
            "license_detections",
            "declared_license_expression",
            "declared_license_expression_spdx"
        ]
        if "license" in workspace_package_data:
            for attribute in attributes_to_copy:
                package_data.extra_data[attribute] = 'workspace'
                workspace_package_data[attribute] = getattr(package_data, attribute)

        workspace_root_path = resource.parent(codebase).path
        if workspace_package_data and workspace_members:

            # TODO: support glob patterns found in cargo workspaces
            for workspace_member_path in workspace_members:
                workspace_directory_path = os.path.join(workspace_root_path, workspace_member_path)
                workspace_directory = codebase.get_resource(path=workspace_directory_path)
                if not workspace_directory:
                    continue

                # Update the package data for all members with the
                # workspace package data
                for resource in workspace_directory.children(codebase):
                    if cls.is_datafile(location=resource.location):
                        if not resource.package_data:
                            continue

                        if TRACE:
                            logger_debug(f"Resource manifest to update: {resource.path}")

                        updated_package_data = cls.update_resource_package_data(
                            workspace=workspace,
                            workspace_package_data=workspace_package_data,
                            resource_package_data=resource.package_data.pop(),
                            mapping=CARGO_ATTRIBUTE_MAPPING,
                        )
                        resource.package_data.append(updated_package_data)
                        resource.save(codebase)

                yield from cls.assemble_from_many_datafiles(
                    datafile_name_patterns=('Cargo.toml', 'cargo.toml', 'Cargo.lock', 'cargo.lock'),
                    directory=workspace_directory,
                    codebase=codebase,
                    package_adder=package_adder,
                )
        else:
            yield from cls.assemble_from_many_datafiles(
                datafile_name_patterns=('Cargo.toml', 'cargo.toml', 'Cargo.lock', 'cargo.lock'),
                directory=resource.parent(codebase),
                codebase=codebase,
                package_adder=package_adder,
            )

    @classmethod
    def update_resource_package_data(cls, workspace, workspace_package_data, resource_package_data, mapping=None):

        extra_data = resource_package_data["extra_data"]
        for attribute in resource_package_data.keys():
            if attribute in mapping:
                replace_by_attribute = mapping.get(attribute)
                if not replace_by_attribute in extra_data:
                    continue

                extra_data.pop(replace_by_attribute)
                replace_by_value = workspace_package_data.get(replace_by_attribute)
                if replace_by_value:
                    resource_package_data[attribute] = replace_by_value
            elif attribute == "parties":
                resource_package_data[attribute] = list(get_parties(
                    person_names=workspace_package_data.get("authors", []),
                    party_role='author',
                ))
                if "authors" in extra_data:
                    extra_data.pop("authors")

        extra_data_copy = extra_data.copy()
        for key, value in extra_data_copy.items():
            if value == 'workspace':
                extra_data.pop(key)

            if key in workspace_package_data:
                workspace_value = workspace_package_data.get(key)
                if workspace_value and key in mapping:
                    replace_by_attribute = mapping.get(key)
                    extra_data[replace_by_attribute] = workspace_value

        # refresh purl if version updated from workspace
        if "version" in workspace_package_data:
            resource_package_data["purl"] = PackageURL(
                type=cls.default_package_type,
                name=resource_package_data["name"],
                namespace=resource_package_data["namespace"],
                version=resource_package_data["version"],
            ).to_string()

        workspace_dependencies = dependency_mapper(dependencies=workspace.get('dependencies', {}))
        deps_by_purl = {}
        for dependency in workspace_dependencies:
            deps_by_purl[dependency.purl] = dependency
        
        for dep_mapping in resource_package_data['dependencies']:
            workspace_dependency = deps_by_purl.get(dep_mapping['purl'], None)
            if workspace_dependency and workspace_dependency.extracted_requirement:
                dep_mapping['extracted_requirement'] = workspace_dependency.extracted_requirement
            
            if 'workspace' in dep_mapping["extra_data"]:
                dep_mapping['extra_data'].pop('workspace')

        return resource_package_data


class CargoTomlHandler(CargoBaseHandler):
    datasource_id = 'cargo_toml'
    path_patterns = ('*/Cargo.toml', '*/cargo.toml',)
    default_package_type = 'cargo'
    default_primary_language = 'Rust'
    description = 'Rust Cargo.toml package manifest'
    documentation_url = 'https://doc.rust-lang.org/cargo/reference/manifest.html'

    @classmethod
    def parse(cls, location, package_only=False):
        package_data_toml = toml.load(location, _dict=dict)
        workspace = package_data_toml.get('workspace', {})
        core_package_data = package_data_toml.get('package', {})
        extra_data = {}
        if workspace:
            extra_data['workspace'] = workspace

        package_data = core_package_data.copy()
        for key, value in package_data.items():
            if isinstance(value, dict) and 'workspace' in value:
                core_package_data.pop(key)
                extra_data[key] = 'workspace'

        name = core_package_data.get('name')
        version = core_package_data.get('version')

        description = core_package_data.get('description') or ''
        description = description.strip()

        authors = core_package_data.get('authors') or []
        parties = list(get_parties(person_names=authors, party_role='author'))

        extracted_license_statement = core_package_data.get('license')
        # TODO: load as a notice_text
        license_file = core_package_data.get('license-file')

        keywords = core_package_data.get('keywords') or []
        categories = core_package_data.get('categories') or []
        keywords.extend(categories)

        # cargo dependencies are complex and can be overriden at multiple levels
        dependencies = []
        for key, value in package_data_toml.items():
            if key.endswith('dependencies'):
                dependencies.extend(dependency_mapper(dependencies=value, scope=key))

        # TODO: add file refs:
        # - readme, include and exclude

        vcs_url = core_package_data.get('repository')
        homepage_url = core_package_data.get('homepage')
        repository_homepage_url = name and f'https://crates.io/crates/{name}'
        repository_download_url = name and version and f'https://crates.io/api/v1/crates/{name}/{version}/download'
        api_data_url = name and f'https://crates.io/api/v1/crates/{name}'

        extra_data_mappings = {
            "documentation": "documentation_url",
            "rust-version": "rust_version",
            "edition": "rust_edition",
        }
        for cargo_attribute, extra_attribute in extra_data_mappings.items():
            value = core_package_data.get(cargo_attribute)
            if value:
                extra_data[extra_attribute] = value

        package_data = dict(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            name=name,
            version=version,
            primary_language=cls.default_primary_language,
            description=description,
            keywords=keywords,
            parties=parties,
            extracted_license_statement=extracted_license_statement,
            vcs_url=vcs_url,
            homepage_url=homepage_url,
            repository_homepage_url=repository_homepage_url,
            repository_download_url=repository_download_url,
            api_data_url=api_data_url,
            dependencies=dependencies,
            extra_data=extra_data,
        )
        yield models.PackageData.from_data(package_data, package_only)


CARGO_ATTRIBUTE_MAPPING = {
    # Fields in PackageData model: Fields in cargo
    "version": "version",
    "homepage_url": "homepage",
    "vcs_url": "repository",
    "keywords": "categories",
    "extracted_license_statement": "license",
    # These are fields carried over to avoid re-detection of licenses
    "license_detections": "license_detections",
    "declared_license_expression": "declared_license_expression",
    "declared_license_expression_spdx": "declared_license_expression_spdx",
    # extra data fields (reverse mapping)
    "edition": "rust_edition",
    "rust-version": "rust_version",
}


class CargoLockHandler(CargoBaseHandler):
    datasource_id = 'cargo_lock'
    path_patterns = ('*/Cargo.lock', '*/cargo.lock',)
    default_package_type = 'cargo'
    default_primary_language = 'Rust'
    description = 'Rust Cargo.lock dependencies lockfile'
    documentation_url = 'https://doc.rust-lang.org/cargo/guide/cargo-toml-vs-cargo-lock.html'

    # TODO: also add extra package data found such as version control and commits
    # [[package]]
    # name = "ansi_term"
    # version = "0.11.0"
    # source = "registry+https://github.com/rust-lang/crates.io-index"
    # checksum = "ee49baf6cb617b853aa8d93bf420db2383fab46d314482ca2803b40d5fde979b"
    # dependencies = [
    #  "winapi",
    # ]

    @classmethod
    def parse(cls, location, package_only=False):
        cargo_lock = toml.load(location, _dict=dict)
        dependencies = []
        package = cargo_lock.get('package', [])
        for dep in package:
            # TODO: add missing "source" vs. "dependencies" and checksum
            dependencies.append(
                models.DependentPackage(
                    purl=PackageURL(
                        type='cargo',
                        name=dep.get('name'),
                        version=dep.get('version')
                    ).to_string(),
                    extracted_requirement=dep.get('version'),
                    scope='dependencies',
                    is_runtime=True,
                    is_optional=False,
                    is_pinned=True,
                )
            )

        package_data = dict(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            primary_language=cls.default_primary_language,
            dependencies=dependencies,
        )
        yield models.PackageData.from_data(package_data, package_only)


def dependency_mapper(dependencies, scope='dependencies'):
    """
    Yield DependentPackage collected from a list of cargo dependencies
    """
    is_runtime = not scope.endswith(('dev-dependencies', 'build-dependencies'))
    for name, requirement in dependencies.items():
        extra_data = {}
        extracted_requirement = None
        if isinstance(requirement, str):
            # plain version requirement
            is_optional = False
            extracted_requirement = requirement

        elif isinstance(requirement, dict):
            # complex requirement, we extract version if available
            # everything else is just dumped in extra data
            # here {workspace = true} means dependency version
            # should be inherited
            is_optional = requirement.pop('optional', False)
            if 'version' in requirement:
                extracted_requirement = requirement.get('version')

            if requirement:
                extra_data = requirement

        yield models.DependentPackage(
            purl=PackageURL(
                type='cargo',
                name=name,
            ).to_string(),
            extracted_requirement=extracted_requirement,
            scope=scope,
            is_runtime=is_runtime,
            is_optional=is_optional,
            is_pinned=False,
            extra_data=extra_data,
        )


def get_parties(person_names, party_role):
    """
    Yields Party of `party_role` given a list of ``person_names`` strings.
    https://doc.rust-lang.org/cargo/reference/manifest.html#the-authors-field-optional
    """
    for person_name in person_names:
        name, email = parse_person(person_name)
        yield models.Party(
            type=models.party_person,
            name=name,
            role=party_role,
            email=email,
        ).to_dict()


person_parser = re.compile(
    r'^(?P<name>[^\(<]+)'
    r'\s?'
    r'(?P<email><([^>]+)>)?'
).match

person_parser_no_name = re.compile(
    r'(?P<email><([^>]+)>)?'
).match


def parse_person(person):
    """
    https://doc.rust-lang.org/cargo/reference/manifest.html#the-authors-field-optional
    A "person" is an object with an optional "name" or "email" field.

    A person can be in the form:
      "author": "Isaac Z. Schlueter <i@izs.me>"

    For example:
    >>> p = parse_person('Barney Rubble <b@rubble.com>')
    >>> assert p == ('Barney Rubble', 'b@rubble.com')
    >>> p = parse_person('Barney Rubble')
    >>> assert p == ('Barney Rubble', None)
    >>> p = parse_person('<b@rubble.com>')
    >>> assert p == (None, 'b@rubble.com')
    """

    parsed = person_parser(person)
    if not parsed:
        name = None
        parsed = person_parser_no_name(person)
    else:
        name = parsed.group('name')

    email = parsed.group('email')

    if name:
        name = name.strip()
    if email:
        email = email.strip('<> ')

    return name, email
