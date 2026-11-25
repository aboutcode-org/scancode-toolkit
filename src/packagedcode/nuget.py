#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import json
import xmltodict
from packageurl import PackageURL

from packagedcode import models
from packagedcode.utils import build_description

"""
Handle NuGet packages and their manifests.
"""


def get_dependencies(nuspec):
    """
    Yield DependentPackage found in a NuGet ``nuspec`` object.
    """
    # This is either a list of dependency or a list of group/dependency
    # or a single dep or a single group mapping

    dependencies = nuspec.get('dependencies') or []
    if isinstance(dependencies, dict):
        # wrap the mapping in a list if we have more than one dependencies
        dependencies = [dependencies]

    for depends in dependencies:
        groups = depends.get('group') or []
        if groups:
            if isinstance(groups, dict):
                # wrap the mapping in a list
                groups = [groups]

            for group in groups:
                extra_data = dict(framework=group['@targetFramework'])
                deps = group.get('dependency') or []
                yield from _get_dep_packs(deps, extra_data)
        else:
            # {'dependency': {'@id': 'jQuery', '@version': '1.9.1'}}
            deps = depends.get('dependency') or []
            yield from _get_dep_packs(deps, extra_data={})


def _get_dep_packs(deps, extra_data):
    """
    Yield DependentPackage found in a NuGet ``deps`` mapping or list of mappings.
    """
    if not deps:
        return

    if isinstance(deps, dict):
        # wrap the mapping in a list
        deps = [deps]

    for dep in deps:
        extra = dict(extra_data) or {}
        include = dep.get('@include')
        if include:
            extra['include'] = include
        exclude = dep.get('@exclude')
        if exclude:
            extra['exclude'] = exclude

        yield models.DependentPackage(
            purl=str(PackageURL(type='nuget', name=dep.get('@id'))),
            # this is a range, not a version
            extracted_requirement=dep.get('@version'),
            scope='dependency',
            is_runtime=True,
            is_optional=False,
            is_pinned=False,
            extra_data=extra,
        )


def get_urls(name, version, **kwargs):
    return dict(
        repository_homepage_url=f'https://www.nuget.org/packages/{name}/{version}',
        repository_download_url=f'https://www.nuget.org/api/v2/package/{name}/{version}',
        # the name is lowercased as in
        # https://api.nuget.org/v3/registration3/newtonsoft.json/10.0.1.json
        api_data_url=f'https://api.nuget.org/v3/registration3/{name.lower()}/{version}.json',
    )


class NugetNupkgHandler(models.NonAssemblableDatafileHandler):
    datasource_id = 'nuget_nupkg'
    path_patterns = ('*.nupkg',)
    default_package_type = 'nuget'
    filetypes = ('zip archive', 'microsoft ooxml',)
    description = 'NuGet nupkg package archive'
    documentation_url = 'https://en.wikipedia.org/wiki/Open_Packaging_Conventions'


class NugetNuspecHandler(models.DatafileHandler):
    datasource_id = 'nuget_nupsec'
    path_patterns = ('*.nuspec',)
    default_package_type = 'nuget'
    description = 'NuGet nuspec package manifest'
    documentation_url = 'https://docs.microsoft.com/en-us/nuget/reference/nuspec'

    @classmethod
    def parse(cls, location, package_only=False):
        with open(location, 'rb') as loc:
            parsed = xmltodict.parse(loc)

        if not parsed:
            return

        pack = parsed.get('package') or {}
        nuspec = pack.get('metadata')
        if not nuspec:
            return

        name = nuspec.get('id')
        version = nuspec.get('version')

        # Summary: A short description of the package for UI display. If omitted, a
        # truncated version of description is used.
        description = build_description(nuspec.get('summary'), nuspec.get('description'))

        # title: A human-friendly title of the package, typically used in UI
        # displays as on nuget.org and the Package Manager in Visual Studio. If not
        # specified, the package ID is used.
        title = nuspec.get('title')
        if title and title != name:
            description = build_description(title, description)

        parties = []
        authors = nuspec.get('authors')
        if authors:
            parties.append(models.Party(name=authors, role='author'))

        owners = nuspec.get('owners')
        if owners:
            parties.append(models.Party(name=owners, role='owner'))

        vcs_url = None

        repo = nuspec.get('repository') or {}
        vcs_repository = repo.get('@url') or ''
        if vcs_repository:
            vcs_tool = repo.get('@type') or ''
            if vcs_tool:
                vcs_url = f'{vcs_tool}+{vcs_repository}'
            else:
                vcs_url = vcs_repository

        urls = get_urls(name, version)

        extracted_license_statement = None
        # See https://docs.microsoft.com/en-us/nuget/reference/nuspec#license
        # This is a SPDX license expression
        if 'license' in nuspec:
            extracted_license_statement = nuspec.get('license')
        # Deprecated and not a license expression, just a URL
        elif 'licenseUrl' in nuspec:
            extracted_license_statement = nuspec.get('licenseUrl')

        package_data = dict(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            name=name,
            version=version,
            description=description or None,
            homepage_url=nuspec.get('projectUrl') or None,
            parties=parties,
            dependencies=list(get_dependencies(nuspec)),
            extracted_license_statement=extracted_license_statement,
            copyright=nuspec.get('copyright') or None,
            vcs_url=vcs_url,
            **urls,
        )
        yield models.PackageData.from_data(package_data, package_only)


class NugetPackagesLockHandler(models.DatafileHandler):
    datasource_id = 'nuget_packages_lock'
    path_patterns = ('*packages.lock.json',)
    default_package_type = 'nuget'
    description = 'NuGet packages.lock.json file'
    documentation_url = 'https://learn.microsoft.com/en-us/nuget/reference/cli-reference/cli-ref-restore'

    @classmethod
    def get_dependencies(cls, package_info, scope):
        dependencies = []
        dependencies_mapping = package_info.get("dependencies") or {}
        for name, version in dependencies_mapping.items():
            dependency = models.DependentPackage(
                purl=str(PackageURL(type='nuget', name=name, version=version)),
                extracted_requirement=version,
                is_pinned=True,
                scope=scope,
                is_optional=False,
                is_runtime=True,
                is_direct=True,
            )
            dependencies.append(dependency)
        return dependencies

    @classmethod
    def parse(cls, location, package_only=False):
        with open(location) as loc:
            parsed = json.load(loc)

        if not parsed:
            return

        top_dependencies = []
        for target_framework, packages in parsed.get('dependencies', {}).items():
            extra_data = dict(
                target_framework=target_framework,
            )
            for package_name, package_info in packages.items():
                dependencies = cls.get_dependencies(package_info=package_info, scope=target_framework)
                resolved_package_mapping = dict(
                datasource_id=cls.datasource_id,
                type=cls.default_package_type,
                primary_language=cls.default_primary_language,
                name=package_name,
                dependencies=[
                    dep.to_dict() for dep in dependencies
                ],
                is_virtual=True,
                version=package_info.get('resolved'),
                )
                resolved_package = models.PackageData.from_data(resolved_package_mapping)
                package_type = package_info.get('type')
                if package_type == "Direct":
                    is_direct = True
                elif package_type == "Transitive":
                    is_direct = False
                else:
                    raise Exception(f"Unknown package type: {package_type} for package {package_name} in {location}")
                    

                version = package_info.get('resolved')
                requested = package_info.get('requested')
                dependency = models.DependentPackage(
                    purl=str(PackageURL(type='nuget', name=package_name, version=version)),
                    extracted_requirement=requested or version,
                    is_pinned=True,
                    resolved_package=resolved_package.to_dict(),
                    # We use the target framework as scope since there is no concept of scope in .NET
                    # and we may have different resolutions for different target frameworks
                    scope=target_framework,
                    is_optional=False,
                    is_runtime=True,
                    is_direct=is_direct,
                )
                top_dependencies.append(dependency.to_dict())
        package_data = dict(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            primary_language=cls.default_primary_language,
            extra_data=extra_data,
            dependencies=top_dependencies,
        )
        yield models.PackageData.from_data(package_data, package_only)


class DotNetDepsJsonHandler(models.DatafileHandler):
    datasource_id = 'nuget_deps_json'
    path_patterns = ('*.deps.json',)
    default_package_type = 'nuget'
    description = 'NuGet .deps.json lockfile'
    documentation_url = 'https://github.com/dotnet/sdk/blob/main/documentation/specs/runtime-configuration-file.md'

    @classmethod
    def parse(cls, location, package_only=False):
        with open(location) as loc:
            parsed = json.load(loc)

        if not parsed or not isinstance(parsed, dict):
            return

        libraries = parsed.get('libraries')
        if not libraries or not isinstance(libraries, dict):
            return

        target_framework = None
        runtime_target = parsed.get('runtimeTarget')
        if runtime_target and isinstance(runtime_target, dict):
            target_framework = runtime_target.get('name')

        # Collect target sections to look up dependencies. We prefer the runtime
        # target when available, but fall back to other targets to avoid missing
        # dependencies in valid .deps.json files without runtimeTarget.
        targets_dict = parsed.get('targets') or {}
        if not isinstance(targets_dict, dict):
            targets_dict = {}

        available_targets = [
            (target_name, target_obj)
            for target_name, target_obj in targets_dict.items()
            if isinstance(target_obj, dict)
        ]

        runtime_target_matched = False
        if target_framework:
            selected_targets = [
                (target_name, target_obj)
                for target_name, target_obj in available_targets
                if target_name == target_framework
            ]
            runtime_target_matched = bool(selected_targets)
        else:
            selected_targets = []

        if not selected_targets:
            selected_targets = available_targets

        packages = parse_deps_json_libraries(
            libraries=libraries,
            selected_targets=selected_targets,
            runtime_target_matched=runtime_target_matched,
            target_framework=target_framework,
            datasource_id=cls.datasource_id,
            default_package_type=cls.default_package_type,
        )

        for package_data in packages:
            yield models.PackageData.from_data(package_data, package_only)


def parse_deps_json_libraries(
    libraries,
    selected_targets,
    runtime_target_matched,
    target_framework,
    datasource_id,
    default_package_type,
):
    """
    Parse the libraries and targets sections of a .deps.json file.
    Returns a list of package dictionaries.
    """
    packages = []
    if not selected_targets:
        selected_targets = []

    for lib_key, lib_info in libraries.items():
        if not lib_key or '/' not in lib_key:
            continue
        if not isinstance(lib_info, dict):
            continue

        name, version = lib_key.split('/', 1)
        package_type = lib_info.get('type')
        dependencies = get_deps_json_dependencies(
            lib_key=lib_key,
            selected_targets=selected_targets,
            default_package_type=default_package_type,
        )

        extra_data = {}
        if runtime_target_matched:
            extra_data['target_framework'] = target_framework
        elif len(selected_targets) == 1:
            extra_data['target_framework'] = selected_targets[0][0]
        elif selected_targets:
            extra_data['target_frameworks'] = [scope for scope, _target_obj in selected_targets]

        if package_type:
            extra_data['type'] = package_type

        package_data = dict(
            datasource_id=datasource_id,
            type=default_package_type,
            name=name,
            version=version,
            dependencies=dependencies,
            extra_data=extra_data,
        )
        packages.append(package_data)

    return packages


def get_deps_json_dependencies(lib_key, selected_targets, default_package_type):
    """
    Return dependency mappings for ``lib_key`` gathered from all ``selected_targets``.
    """
    dependencies = []
    seen_dependencies = set()

    for scope, target_obj in selected_targets:
        target_lib = target_obj.get(lib_key) or {}
        if not isinstance(target_lib, dict):
            continue

        deps = target_lib.get('dependencies')
        if not deps or not isinstance(deps, dict):
            continue

        for dep_name, dep_version in deps.items():
            if not dep_name:
                continue

            dep_key = (dep_name, dep_version, scope)
            if dep_key in seen_dependencies:
                continue
            seen_dependencies.add(dep_key)

            purl = PackageURL(type=default_package_type, name=dep_name, version=dep_version)
            resolved_package = models.PackageData(
                type=purl.type,
                name=dep_name,
                version=dep_version,
            ).to_dict()

            dependency = models.DependentPackage(
                purl=str(purl),
                extracted_requirement=dep_version,
                scope=scope,
                is_runtime=True,
                is_optional=False,
                is_pinned=True,
                is_direct=True,
                resolved_package=resolved_package,
            )
            dependencies.append(dependency.to_dict())

    return dependencies
