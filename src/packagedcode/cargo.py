
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
import re

import saneyaml
import toml
from packageurl import PackageURL

from packagedcode import models

"""
Handle Rust cargo crates
"""


class CargoBaseHandler(models.DatafileHandler):
    @classmethod
    def assemble(cls, package_data, resource, codebase, package_adder):
        """
        Assemble Cargo.toml and possible Cargo.lock datafiles. Also
        support cargo workspaces where we have multiple packages from
        a repository and some shared information present at top-level.
        """
        workspace = package_data.extra_data.get("workspace", {})
        workspace_members = workspace.get("members", [])
        workspace_package_data = workspace.get("package", {})
        attributes_to_copy = [
            "license_detections",
            "declared_license_expression",
            "declared_license_expression_spdx"
        ]
        if "license" in workspace_package_data:
            for attribute in attributes_to_copy:
                workspace_package_data[attribute] = getattr(package_data, attribute)

        workspace_root_path = resource.parent(codebase).path
        if workspace_package_data and workspace_members:
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

                        updated_package_data = cls.update_resource_package_data(
                            package_data=workspace_package_data,
                            old_package_data=resource.package_data.pop(),
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
    def update_resource_package_data(cls, package_data, old_package_data, mapping=None):

        for attribute in old_package_data.keys():
            if attribute in mapping:
                replace_by_attribute = mapping.get(attribute)
                old_package_data[attribute] = package_data.get(replace_by_attribute)
            elif attribute == "parties":
                old_package_data[attribute] = list(get_parties(
                    person_names=package_data.get("authors"),
                    party_role='author',
                ))

        return old_package_data



class CargoTomlHandler(CargoBaseHandler):
    datasource_id = 'cargo_toml'
    path_patterns = ('*/Cargo.toml', '*/cargo.toml',)
    default_package_type = 'cargo'
    default_primary_language = 'Rust'
    description = 'Rust Cargo.toml package manifest'
    documentation_url = 'https://doc.rust-lang.org/cargo/reference/manifest.html'

    @classmethod
    def parse(cls, location, package_only=False):
        package_data = toml.load(location, _dict=dict)
        core_package_data = package_data.get('package', {})
        workspace = package_data.get('workspace', {})
        extra_data = {}

        name = core_package_data.get('name')
        version = core_package_data.get('version')
        if isinstance(version, dict) and "workspace" in version:
            version = None
            extra_data["version"] = "workspace"

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
        for key, value in core_package_data.items():
            if key.endswith('dependencies'):
                dependencies.extend(dependency_mapper(dependencies=value, scope=key))

        # TODO: add file refs:
        # - readme, include and exclude
        # TODO: other URLs
        # - documentation

        vcs_url = core_package_data.get('repository')
        homepage_url = core_package_data.get('homepage')
        repository_homepage_url = name and f'https://crates.io/crates/{name}'
        repository_download_url = name and version and f'https://crates.io/api/v1/crates/{name}/{version}/download'
        api_data_url = name and f'https://crates.io/api/v1/crates/{name}'
        if workspace:
            extra_data["workspace"] = workspace

        package_data = dict(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            name=name,
            version=version,
            primary_language=cls.default_primary_language,
            description=description,
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
    "homepage_url": "homepage",
    "vcs_url": "repository",
    "keywords": "categories",
    "extracted_license_statement": "license",
    # These are fields carried over to avoid re-detection of licenses
    "license_detections": "license_detections",
    "declared_license_expression": "declared_license_expression",
    "declared_license_expression_spdx": "declared_license_expression_spdx",
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
                    is_resolved=True,
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
        if isinstance(requirement, str):
            # plain version requirement
            is_optional = False
        elif isinstance(requirement, dict):
            # complex requirement, with more than version are harder to handle
            # so we just dump
            is_optional = requirement.pop('optional', False)
            requirement = saneyaml.dump(requirement)

        yield models.DependentPackage(
            purl=PackageURL(
                type='cargo',
                name=name,
            ).to_string(),
            extracted_requirement=requirement,
            scope=scope,
            is_runtime=is_runtime,
            is_optional=is_optional,
            is_resolved=False,
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
