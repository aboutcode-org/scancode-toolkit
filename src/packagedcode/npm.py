
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#
import base64
import io
import fnmatch
import os
import logging
import json
import re
import sys
import urllib.parse
from functools import partial
from itertools import islice

from packageurl import PackageURL

from packagedcode import models
from packagedcode.utils import normalize_vcs_url
from packagedcode.utils import yield_dependencies_from_package_data
from packagedcode.utils import yield_dependencies_from_package_resource
from packagedcode.utils import update_dependencies_as_resolved
from packagedcode.utils import is_simple_path
from packagedcode.utils import is_simple_path_pattern
import saneyaml

"""
Handle Node.js npm packages
per https://docs.npmjs.com/files/package.json
"""

"""
To check https://github.com/npm/normalize-package-data
"""


SCANCODE_DEBUG_PACKAGE = os.environ.get('SCANCODE_DEBUG_PACKAGE', False)
SCANCODE_DEBUG_PACKAGE_NPM = os.environ.get('SCANCODE_DEBUG_PACKAGE_NPM', False)

TRACE = SCANCODE_DEBUG_PACKAGE
TRACE_NPM = SCANCODE_DEBUG_PACKAGE_NPM


def logger_debug(*args):
    pass


logger = logging.getLogger(__name__)

if TRACE or TRACE_NPM:
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(
            ' '.join(isinstance(a, str) and a or repr(a) for a in args)
        )

# TODO: add os and engines from package.json??
# TODO: add new yarn v2 lock file format
# TODO: add pnp.js and pnpm-lock.yaml https://pnpm.io/
# TODO: add support for "lockfileVersion": 2 for package-lock.json and lockfileVersion: 3


class BaseNpmHandler(models.DatafileHandler):

    lockfile_names = {
        'package-lock.json',
        '.package-lock.json',
        'npm-shrinkwrap.json',
        'yarn.lock',
        'shrinkwrap.yaml',
        'pnpm-lock.yaml'
    }

    @classmethod
    def assemble(cls, package_data, resource, codebase, package_adder):
        """
        If ``resource``, or one of its siblings, is a package.json file, use it
        to create and yield the package, the package dependencies, and the
        package resources.

        When reporting the resources of a package, we walk the codebase, skipping
        the node_modules directory, assign resources to the package and yield
        resources.

        For each lock file, assign dependencies to package instances and yield dependencies.

        If there is no package.json, we do not have a package instance. In this
        case, we yield each of the dependencies in each lock file.
        """

        package_resource = None
        if resource.name == 'package.json':
            package_resource = resource
        elif resource.name in cls.lockfile_names:
            if resource.has_parent():
                siblings = resource.siblings(codebase)
                package_resource = [r for r in siblings if r.name == 'package.json']
                if package_resource:
                    package_resource = package_resource[0]

        if not package_resource:
            # we do not have a package.json
            yield from yield_dependencies_from_package_resource(resource)
            return

        if codebase.has_single_resource:
            yield from models.DatafileHandler.assemble(package_data, resource, codebase, package_adder)
            return

        # We do not have any package data detected here
        if not package_resource.package_data:
            return

        assert len(package_resource.package_data) == 1, f'Invalid package.json for {package_resource.path}'
        pkg_data = package_resource.package_data[0]
        pkg_data = models.PackageData.from_dict(pkg_data)

        workspace_root = package_resource.parent(codebase)
        workspace_root_path = None
        if workspace_root:
            workspace_root_path = package_resource.parent(codebase).path
        workspaces = pkg_data.extra_data.get('workspaces') or []

        # Also look for pnpm workspaces
        pnpm_workspace = None
        if not workspaces and workspace_root:
            pnpm_workspace_path = os.path.join(workspace_root_path, 'pnpm-workspace.yaml')
            pnpm_workspace = codebase.get_resource(path=pnpm_workspace_path)
            if pnpm_workspace:
                pnpm_workspace_pkg_data = pnpm_workspace.package_data
                if pnpm_workspace_pkg_data:
                    workspace_package = pnpm_workspace_pkg_data[0]
                    extra_data = workspace_package.get('extra_data')
                    workspaces = extra_data.get('workspaces')

        workspace_members = cls.get_workspace_members(
            workspaces=workspaces,
            codebase=codebase,
            workspace_root_path=workspace_root_path,
        )

        cls.update_workspace_members(workspace_members, codebase)

        # do we have enough to create a package?
        if pkg_data.purl and not workspaces:
            package = models.Package.from_package_data(
                package_data=pkg_data,
                datafile_path=package_resource.path,
            )
            package_uid = package.package_uid

            package.populate_license_fields()

            # Always yield the package resource in all cases and first!
            yield package

            if workspace_root:
                for npm_res in cls.walk_npm(resource=workspace_root, codebase=codebase):
                    if package_uid and package_uid not in npm_res.for_packages:
                        package_adder(package_uid, npm_res, codebase)
                    yield npm_res
            yield package_resource

        elif workspaces:
            yield from cls.create_packages_from_workspaces(
                workspace_members=workspace_members,
                workspace_root=workspace_root,
                codebase=codebase,
                package_adder=package_adder,
                pnpm=pnpm_workspace and pkg_data.purl,
            )

            package_uid = None
            if pnpm_workspace and pkg_data.purl:
                package = models.Package.from_package_data(
                    package_data=pkg_data,
                    datafile_path=package_resource.path,
                )
                package_uid = package.package_uid

                package.populate_license_fields()

                # Always yield the package resource in all cases and first!
                yield package

                if workspace_root:
                    for npm_res in cls.walk_npm(resource=workspace_root, codebase=codebase):
                        if package_uid and not npm_res.for_packages:
                            package_adder(package_uid, npm_res, codebase)
                        yield npm_res
                yield package_resource

        else:
            # we have no package, so deps are not for a specific package uid
            package_uid = None

        yield from cls.yield_npm_dependencies_and_resources(
            package_resource=package_resource,
            package_data=pkg_data,
            package_uid=package_uid,
            codebase=codebase,
            package_adder=package_adder,
        )

    @classmethod
    def yield_npm_dependencies_and_resources(cls, package_resource, package_data, package_uid, codebase, package_adder):

        # in all cases yield possible dependencies
        yield from yield_dependencies_from_package_data(package_data, package_resource.path, package_uid)

        # we yield this as we do not want this further processed
        yield package_resource

        for lock_file in package_resource.siblings(codebase):
            if lock_file.name in cls.lockfile_names:
                yield from yield_dependencies_from_package_resource(lock_file, package_uid)

                if package_uid and package_uid not in lock_file.for_packages:
                    package_adder(package_uid, lock_file, codebase)
                yield lock_file

    @classmethod
    def create_packages_from_workspaces(
        cls,
        workspace_members,
        workspace_root,
        codebase,
        package_adder,
        pnpm=False,
    ):

        workspace_package_uids = []
        for workspace_member in workspace_members:
            if not workspace_member.package_data:
                continue

            pkg_data = workspace_member.package_data[0]
            pkg_data = models.PackageData.from_dict(pkg_data)

            package = models.Package.from_package_data(
                package_data=pkg_data,
                datafile_path=workspace_member.path,
            )
            package_uid = package.package_uid
            workspace_package_uids.append(package_uid)

            package.populate_license_fields()

            # Always yield the package resource in all cases and first!
            yield package

            member_root = workspace_member.parent(codebase)
            package_adder(package_uid, member_root, codebase)
            for npm_res in cls.walk_npm(resource=member_root, codebase=codebase):
                if package_uid and package_uid not in npm_res.for_packages:
                    package_adder(package_uid, npm_res, codebase)
                yield npm_res

            yield from cls.yield_npm_dependencies_and_resources(
                package_resource=workspace_member,
                package_data=pkg_data,
                package_uid=package_uid,
                codebase=codebase,
                package_adder=package_adder,
            )

        # All resources which are not part of a workspace package exclusively
        # are a part of all packages (this is skipped if we have a root pnpm
        # package)
        if pnpm:
            return
        for npm_res in cls.walk_npm(resource=workspace_root, codebase=codebase):
            if npm_res.for_packages:
                continue

            for package_uid in workspace_package_uids:
                package_adder(package_uid, npm_res, codebase)

            npm_res.save(codebase)

    @classmethod
    def walk_npm(cls, resource, codebase, depth=0):
        """
        Walk the ``codebase`` Codebase top-down, breadth-first starting from the
        ``resource`` Resource.

        Skip a first level child directory named "node_modules": this avoids
        reporting nested vendored packages as being part of their parent.
        Instead they will be reported on their own.
        """
        for child in resource.children(codebase):
            if depth == 0 and child.name == 'node_modules':
                continue

            yield child

            if child.is_dir:
                depth += 1
                for subchild in cls.walk_npm(child, codebase, depth=depth):
                    yield subchild

    @classmethod
    def update_dependencies_by_purl(
        cls,
        dependencies,
        scope,
        dependencies_by_purl,
        is_runtime=False,
        is_optional=False,
        is_pinned=False,
        is_direct=True,
    ):
        """
        Update the `dependencies_by_purl` mapping (which contains the cumulative
        dependencies for a package metadata) from a list of `dependencies` which
        have new dependencies or metadata for already existing dependencies.
        """
        # npm/pnpm Dependency scopes which contain metadata for dependencies
        # see documentation below for more details
        # https://docs.npmjs.com/cli/v10/configuring-npm/package-json#peerdependenciesmeta
        # https://pnpm.io/package_json#dependenciesmeta
        metadata_deps = ['peerDependenciesMeta', 'dependenciesMeta']

        if isinstance(dependencies, list):
            for subdep in dependencies:
                sdns, _ , sdname = subdep.rpartition('/')
                dep_purl = PackageURL(
                    type=cls.default_package_type,
                    namespace=sdns,
                    name=sdname
                ).to_string()
                dep_package = models.DependentPackage(
                    purl=dep_purl,
                    scope=scope,
                    is_runtime=is_runtime,
                    is_optional=is_optional,
                    is_pinned=is_pinned,
                    is_direct=is_direct,
                )
                dependencies_by_purl[dep_purl] = dep_package

        elif isinstance(dependencies, dict):
            for subdep, metadata in dependencies.items():
                sdns, _ , sdname = subdep.rpartition('/')
                dep_purl = PackageURL(
                    type=cls.default_package_type,
                    namespace=sdns,
                    name=sdname
                ).to_string()

                if scope in metadata_deps :
                    dep_package = dependencies_by_purl.get(dep_purl)
                    if dep_package:
                        dep_package.is_optional = metadata.get("optional")
                    else:
                        dep_package = models.DependentPackage(
                            purl=dep_purl,
                            scope=scope,
                            is_runtime=is_runtime,
                            is_optional=metadata.get("optional"),
                            is_pinned=is_pinned,
                            is_direct=is_direct,
                        )
                        dependencies_by_purl[dep_purl] = dep_package
                    continue

                # pnpm has peer dependencies also sometimes in version?
                # dependencies:
                #   '@react-spring/animated': 9.5.5_react@18.2.0
                # TODO: store this relation too?
                requirement = metadata
                if 'pnpm' in cls.datasource_id:
                    if '_' in metadata:
                        requirement, _extra = metadata.split('_')

                if ':' in requirement and '@' in requirement:
                    # dependencies with requirements like this are aliases and should be reported
                    aliased_package, _, constraint = requirement.rpartition('@')
                    _, _, aliased_package_name = aliased_package.rpartition(':')
                    sdns, _ , sdname = aliased_package_name.rpartition('/')
                    dep_purl = PackageURL(
                        type=cls.default_package_type,
                        namespace=sdns,
                        name=sdname
                    ).to_string()
                    requirement = constraint

                dep_package = models.DependentPackage(
                    purl=dep_purl,
                    scope=scope,
                    extracted_requirement=requirement,
                    is_runtime=is_runtime,
                    is_optional=is_optional,
                    is_pinned=is_pinned,
                    is_direct=is_direct,
                )
                dependencies_by_purl[dep_purl] = dep_package

    @classmethod
    def get_workspace_members(cls, workspaces, codebase, workspace_root_path):
        """
        Given the workspaces, a list of paths/glob path patterns for npm
        workspaces present in package.json, the codebase, and the
        workspace_root_path, which is the parent directory of the
        package.json which contains the workspaces, get a list of
        workspace member package.json resources.
        """

        workspace_members = []

        for workspace_path in workspaces:

            # Case 1: A definite path, instead of a pattern (only one package.json)
            if is_simple_path(workspace_path):
                workspace_dir_path = os.path.join(workspace_root_path, workspace_path)
                workspace_member_path = os.path.join(workspace_dir_path, 'package.json')
                workspace_member = codebase.get_resource(path=workspace_member_path)
                if workspace_member and workspace_member.package_data:
                    workspace_members.append(workspace_member)

            # Case 2: we have glob path which is a directory, relative to the workspace root
            # Here we have only one * at the last (This is an optimization, this is a very
            # commonly encountered subcase of case 3)
            elif is_simple_path_pattern(workspace_path):
                workspace_pattern_prefix = workspace_path.rstrip('*')
                workspace_dir_path = os.path.join(workspace_root_path, workspace_pattern_prefix)
                workspace_search_dir = codebase.get_resource(path=workspace_dir_path)
                if not workspace_search_dir:
                    continue

                for resource in workspace_search_dir.walk(codebase):
                    if resource.package_data and NpmPackageJsonHandler.is_datafile(
                        location=resource.location,
                    ):
                        workspace_members.append(resource)

            # Case 3: This is a complex glob pattern, we are doing a full codebase walk
            # and glob matching each resource
            else:
                workspace_root = codebase.get_resource(path=workspace_root_path)
                for resource in workspace_root.walk(codebase):
                    if NpmPackageJsonHandler.is_datafile(resource.location) and fnmatch.fnmatch(
                        name=resource.location, pat=workspace_path,
                    ):
                        workspace_members.append(resource)

        return workspace_members

    @classmethod
    def update_workspace_members(cls, workspace_members, codebase):
        """
        Update all version requirements referencing workspace level
        package versions with data from all the `workspace_members`.
        Example: "ruru-components@workspace:^"
        """
        # Collect info needed from all workspace member
        workspace_package_versions_by_base_purl = {}
        workspace_dependencies_by_base_purl = {}
        for workspace_manifest in workspace_members:
            workspace_package_data = workspace_manifest.package_data[0]

            dependencies = workspace_package_data.get('dependencies')
            for dependency in dependencies:
                dep_purl = dependency.get('purl')
                workspace_dependencies_by_base_purl[dep_purl] = dependency

            is_private = workspace_package_data.get("is_private")
            package_url = workspace_package_data.get('purl')
            if is_private or not package_url:
                continue

            purl = PackageURL.from_string(package_url)
            base_purl = PackageURL(
                type=purl.type,
                namespace=purl.namespace,
                name=purl.name,
            ).to_string()

            version = workspace_package_data.get('version')
            if purl and version:
                workspace_package_versions_by_base_purl[base_purl] = version

        # Update workspace member package information from
        # workspace level data
        for base_purl, dependency in workspace_dependencies_by_base_purl.items():
            extracted_requirement = dependency.get('extracted_requirement')
            if 'workspace' in extracted_requirement:
                version = workspace_package_versions_by_base_purl.get(base_purl)
                if version:
                    new_requirement = extracted_requirement.replace('workspace', version)
                    dependency['extracted_requirement'] = new_requirement

        for member in workspace_members:
            member.save(codebase)


def get_urls(namespace, name, version, **kwargs):
    return dict(
        repository_homepage_url=npm_homepage_url(namespace, name, registry='https://www.npmjs.com/package'),
        repository_download_url=npm_download_url(namespace, name, version, registry='https://registry.npmjs.org'),
        api_data_url=npm_api_url(namespace, name, version, registry='https://registry.npmjs.org'),
    )


class NpmPackageJsonHandler(BaseNpmHandler):
    datasource_id = 'npm_package_json'
    path_patterns = ('*/package.json',)
    default_package_type = 'npm'
    default_primary_language = 'JavaScript'
    description = 'npm package.json'
    documentation_url = 'https://docs.npmjs.com/cli/v8/configuring-npm/package-json'

    @classmethod
    def _parse(cls, json_data, package_only=False):
        name = json_data.get('name')
        version = json_data.get('version')
        homepage_url = json_data.get('homepage', '')

        # a package.json without name and version can be a private package

        if homepage_url and isinstance(homepage_url, list):
            # TODO: should we keep other URLs
            homepage_url = homepage_url[0]
        homepage_url = homepage_url.strip() or None

        namespace, name = split_scoped_package_name(name)

        is_private = json_data.get('private') or False
        if is_private:
            urls = {}
        else:
            urls = get_urls(namespace, name, version)
        package_data = dict(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            primary_language=cls.default_primary_language,
            namespace=namespace or None,
            name=name,
            version=version or None,
            description=json_data.get('description', '').strip() or None,
            homepage_url=homepage_url,
            is_private=is_private,
            **urls,
        )
        package = models.PackageData.from_data(package_data, package_only)
        vcs_revision = json_data.get('gitHead') or None

        # mapping of top level package.json items to a function accepting as
        # arguments the package.json element value and returning an iterable of (key,
        # values) to update on a package
        field_mappers = [
            ('author', partial(party_mapper, party_type='author')),
            ('contributors', partial(party_mapper, party_type='contributor')),
            ('maintainers', partial(party_mapper, party_type='maintainer')),
            ('dependencies', partial(deps_mapper, field_name='dependencies')),
            ('devDependencies', partial(deps_mapper, field_name='devDependencies')),
            ('peerDependencies', partial(deps_mapper, field_name='peerDependencies')),
            ('optionalDependencies', partial(deps_mapper, field_name='optionalDependencies')),
            ('bundledDependencies', bundle_deps_mapper),
            ('resolutions', partial(deps_mapper, field_name='resolutions')),
            ('repository', partial(vcs_repository_mapper, vcs_revision=vcs_revision)),
            ('keywords', keywords_mapper,),
            ('bugs', bugs_mapper),
            ('dist', dist_mapper),
        ]

        extra_data = {}
        extra_data_fields = ['workspaces', 'engines', 'packageManager']
        for extra_data_field in extra_data_fields:
            value = json_data.get(extra_data_field)
            if value:
                extra_data[extra_data_field] = value

        package.extra_data = extra_data

        for source, func in field_mappers:
            value = json_data.get(source) or None
            if value:
                if isinstance(value, str):
                    value = value.strip()
                if value:
                    func(value, package)

        if not package.download_url:
            # Only add a synthetic download URL if there is none from the dist mapping.
            package.download_url = npm_download_url(package.namespace, package.name, package.version)

        # licenses are a tad special with many different data structures
        lic = json_data.get('license')
        lics = json_data.get('licenses')
        package = licenses_mapper(lic, lics, package)

        if not package_only:
            package.populate_license_fields()

        if TRACE:
            logger_debug(f'NpmPackageJsonHandler: parse: package: {package.to_dict()}')

        return package

    @classmethod
    def parse(cls, location, package_only=False):
        with io.open(location, encoding='utf-8') as loc:
            json_data = json.load(loc)

        yield cls._parse(json_data, package_only)


class BaseNpmLockHandler(BaseNpmHandler):

    @classmethod
    def parse(cls, location, package_only=False):

        with io.open(location, encoding='utf-8') as loc:
            package_data = json.load(loc)

        # we have two formats: v1 and v2
        lockfile_version = package_data.get('lockfileVersion', 1)
        root_name = package_data.get('name')
        root_version = package_data.get('version')
        root_ns, _ , root_name = root_name.rpartition('/')

        extra_data = dict(lockfile_version=lockfile_version)
        # this is the top level element that we return
        root_package_mapping = dict(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            primary_language=cls.default_primary_language,
            namespace=root_ns,
            name=root_name,
            version=root_version,
            extra_data=extra_data,
            **get_urls(root_ns, root_name, root_version)
        )
        root_package_data = models.PackageData.from_data(root_package_mapping, package_only)

        # https://docs.npmjs.com/cli/v8/configuring-npm/package-lock-json#lockfileversion
        if lockfile_version == 1:
            deps_key = 'dependencies'
        else:
            # v2 and may be v3???
            deps_key = 'packages'

        deps_mapping = package_data.get(deps_key) or {}

        # Top level package metadata is present here
        root_pkg = deps_mapping.get("")
        if root_pkg:
            pkg_name = root_pkg.get('name')
            pkg_ns, _ , pkg_name = pkg_name.rpartition('/')
            pkg_version = root_pkg.get('version')
            pkg_purl = PackageURL(
                type=cls.default_package_type,
                namespace=pkg_ns,
                name=pkg_name,
                version=pkg_version,
            ).to_string()
            if pkg_purl != root_package_data.purl:
                if TRACE_NPM:
                    logger_debug(f'BaseNpmLockHandler: parse: purl mismatch: {pkg_purl} vs {root_package_data.purl}')
            else:
                extracted_license_statement = root_pkg.get('license')
                if extracted_license_statement:
                    root_package_data.extracted_license_statement = extracted_license_statement
                    root_package_data.populate_license_fields()

                deps_mapper(
                    deps=root_pkg.get('devDependencies') or {},
                    package=root_package_data,
                    field_name='devDependencies',
                )
                deps_mapper(
                    deps=root_pkg.get('optionalDependencies') or {},
                    package=root_package_data,
                    field_name='optionalDependencies',
                )

        dependencies = []

        for dep, dep_data in deps_mapping.items():
            is_dev = dep_data.get('dev', False)
            is_optional = dep_data.get('optional', False)
            is_devoptional = dep_data.get('devOptional', False)
            if is_dev or is_devoptional:
                is_runtime = False
                is_optional = True
                scope = 'devDependencies'
            else:
                is_runtime = True
                is_optional = is_optional
                scope = 'dependencies'

            if not dep:
                # in v2 format the first dep is the same as the top level
                # package and has no name
                continue

            # only present for first top level
            # otherwise get name from dep
            name = dep_data.get('name')
            if not name:
                if 'node_modules/' in dep:
                    # the name is the last segment as the dep can be:
                    # "node_modules/ansi-align/node_modules/ansi-regex"
                    _, _, name = dep.rpartition('node_modules/')
                else:
                    name = dep
            ns, _ , name = name.rpartition('/')
            version = dep_data.get('version')

            dep_purl = PackageURL(
                type=cls.default_package_type,
                namespace=ns,
                name=name,
                version=version,
            ).to_string()

            dependency = models.DependentPackage(
                purl=dep_purl,
                extracted_requirement=version,
                scope=scope,
                is_runtime=is_runtime,
                is_optional=is_optional,
                is_pinned=True,
                is_direct=False,
            )

            # URLs and checksums
            misc = get_urls(ns, name, version)
            resolved = dep_data.get('resolved')
            misc.update(get_checksum_and_url(resolved).items())
            integrity = dep_data.get('integrity')
            misc.update(get_algo_hexsum(integrity).items())

            resolved_package_mapping = dict(
                datasource_id=cls.datasource_id,
                type=cls.default_package_type,
                primary_language=cls.default_primary_language,
                namespace=ns,
                name=name,
                version=version,
                **misc,
                is_virtual=True,
            )
            resolved_package = models.PackageData.from_data(resolved_package_mapping, package_only)
            # these are paths t the root of the installed package in v2
            if dep:
                resolved_package.file_references = [models.FileReference(path=dep)],

            # v1 as name/constraint pairs
            subrequires = dep_data.get('requires') or {}

            # in v1 these are further nested dependencies (TODO: handle these with tests)
            # in v2 these are name/constraint pairs like v1 requires
            subdependencies = dep_data.get('dependencies')

            # v2? ignored for now
            engines = dep_data.get('engines')
            funding = dep_data.get('funding')

            if lockfile_version == 1:
                subdeps_data = subrequires
            else:
                subdeps_data = subdependencies
            subdeps_data = subdeps_data or {}

            sub_deps_by_purl = {}
            cls.update_dependencies_by_purl(
                dependencies=subdeps_data,
                scope=scope,
                dependencies_by_purl=sub_deps_by_purl,
                is_runtime=is_runtime,
                is_optional=is_optional,
                is_pinned=False,
                is_direct=True,
            )

            resolved_package.dependencies = [
                sub_dep.to_dict()
                for sub_dep in sub_deps_by_purl.values()
            ]
            dependency.resolved_package = resolved_package.to_dict()
            dependencies.append(dependency.to_dict())

        update_dependencies_as_resolved(dependencies=dependencies)
        root_package_data.dependencies = dependencies

        yield root_package_data


class NpmPackageLockJsonHandler(BaseNpmLockHandler):
    # Note that there are multiple lockfileVersion 1 and 2 (and even 3)
    # and each have a different layout
    datasource_id = 'npm_package_lock_json'
    path_patterns = (
        '*/package-lock.json',
        '*/.package-lock.json',
    )
    default_package_type = 'npm'
    default_primary_language = 'JavaScript'
    is_lockfile = True
    description = 'npm package-lock.json lockfile'
    documentation_url = 'https://docs.npmjs.com/cli/v8/configuring-npm/package-lock-json'


class NpmShrinkwrapJsonHandler(BaseNpmLockHandler):
    datasource_id = 'npm_shrinkwrap_json'
    path_patterns = ('*/npm-shrinkwrap.json',)
    default_package_type = 'npm'
    default_primary_language = 'JavaScript'
    is_lockfile = True
    description = 'npm shrinkwrap.json lockfile'
    documentation_url = 'https://docs.npmjs.com/cli/v8/configuring-npm/npm-shrinkwrap-json'


class UnknownYarnLockFormat(Exception):
    pass


def is_yarn_v2(location):
    """
    Return True if this is a yarn.lock format version 2 and False if this is
    version 1. Raise an UnknownYarnLockFormat exception if neither v1 or v2.

    v1 is a custom, almost-like-YAMl format. v2 is a proper subset of YAML.

    The start of v1 file has this:
        # THIS IS AN AUTOGENERATED FILE. DO NOT EDIT THIS FILE DIRECTLY.
        # yarn lockfile v1

    The start of v2 file has this:
        # This file is generated by running "yarn install" inside your project.
        # Manual changes might be lost - proceed with caution!

        __metadata:
    """
    with open(location) as ylf:
        # check only in the first 10 lines
        for line in islice(ylf, 0, 10):
            if '__metadata:' in line:
                return True
            if 'yarn lockfile v1' in line:
                return False

    raise UnknownYarnLockFormat(location)


class YarnLockV2Handler(BaseNpmHandler):
    """
    Handle yarn.lock v2 format, which is YAML
    """
    datasource_id = 'yarn_lock_v2'
    path_patterns = ('*/yarn.lock',)
    default_package_type = 'npm'
    default_primary_language = 'JavaScript'
    is_lockfile = True
    description = 'yarn.lock lockfile v2 format'
    documentation_url = 'https://classic.yarnpkg.com/lang/en/docs/yarn-lock/'

    @classmethod
    def is_datafile(cls, location, filetypes=tuple()):
        return super().is_datafile(location, filetypes=filetypes) and is_yarn_v2(location)

    @classmethod
    def parse(cls, location, package_only=False):
        """
        Parse a bew yarn.lock v2 YAML format which looks like this:

        "@algolia/cache-browser-local-storage@npm:4.2.0":
          version: 4.2.0
          resolution: "@algolia/cache-browser-local-storage@npm:4.2.0"
          dependencies:
            "@algolia/cache-common": 4.2.0
          checksum: 72ac158925eb5a51e015aa22df5d2026fc0c0b6b58eb8c1290712e0
          languageName: node
          linkType: hard

        Yield a single PackageData
        """
        with open(location) as yl:
            lock_data = saneyaml.load(yl.read())
        top_dependencies = []

        for spec, details in lock_data.items():
            if spec == '__metadata':
                continue
            version = details.get('version')
            resolution = details.get('resolution')
            ns_name, _, version = resolution.rpartition('@')
            ns, _, name = ns_name.rpartition('/')
            if version.startswith('npm:'):
                _npm, _, version = version.partition(':')
            purl = PackageURL(
                type=cls.default_package_type,
                namespace=ns,
                name=name,
                version=version,
            )

            # TODO: what type of checksum is this? ... this is a complex one
            # See https://github.com/yarnpkg/berry/blob/f1edfae49d1bab7679ce3061e2749113dc3b80e8/packages/yarnpkg-core/sources/tgzUtils.ts
            checksum = details.get('checksum')
            dependencies = details.get('dependencies') or {}
            peer_dependencies = details.get('peerDependencies') or {}
            dependencies_meta = details.get('dependenciesMeta') or {}
            # these are file references
            bin = details.get('bin') or []

            deps_for_resolved_by_purl = {}
            cls.update_dependencies_by_purl(
                dependencies=dependencies,
                scope="dependencies",
                dependencies_by_purl=deps_for_resolved_by_purl,
            )
            cls.update_dependencies_by_purl(
                dependencies=peer_dependencies,
                scope="peerDependencies",
                dependencies_by_purl=deps_for_resolved_by_purl,
            )
            cls.update_dependencies_by_purl(
                dependencies=dependencies_meta,
                scope="dependenciesMeta",
                dependencies_by_purl=deps_for_resolved_by_purl,
            )

            dependencies_for_resolved = [
                dep_package.to_dict()
                for dep_package in deps_for_resolved_by_purl.values()
            ]

            resolved_package_mapping = dict(
                datasource_id=cls.datasource_id,
                type=cls.default_package_type,
                primary_language=cls.default_primary_language,
                namespace=ns,
                name=name,
                version=version,
                dependencies=dependencies_for_resolved,
                is_virtual=True,
            )
            resolved_package = models.PackageData.from_data(resolved_package_mapping)

            # These are top level dependencies which do not have a
            # scope defined there, so we are assigning the default
            # scope, this would be merged with the dependency having
            # correct scope value when resolved
            dependency = models.DependentPackage(
                purl=str(purl),
                extracted_requirement=version,
                is_pinned=True,
                resolved_package=resolved_package.to_dict(),
                scope='dependencies',
                is_optional=False,
                is_runtime=True,
            )
            top_dependencies.append(dependency.to_dict())

        update_dependencies_as_resolved(dependencies=top_dependencies)
        package_data = dict(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            primary_language=cls.default_primary_language,
            dependencies=top_dependencies,
        )
        yield models.PackageData.from_data(package_data, package_only)


class YarnLockV1Handler(BaseNpmHandler):
    """
    Handle yarn.lock v1 format, which is more or less but not quite like YAML
    """
    datasource_id = 'yarn_lock_v1'
    path_patterns = ('*/yarn.lock',)
    default_package_type = 'npm'
    default_primary_language = 'JavaScript'
    is_lockfile = True
    description = 'yarn.lock lockfile v1 format'
    documentation_url = 'https://classic.yarnpkg.com/lang/en/docs/yarn-lock/'

    @classmethod
    def is_datafile(cls, location, filetypes=tuple()):
        return super().is_datafile(location, filetypes=filetypes) and not is_yarn_v2(location)

    @classmethod
    def parse(cls, location, package_only=False):
        """
        Parse a classic yarn.lock format which looks like this:
            "@babel/core@^7.1.0", "@babel/core@^7.3.4":
              version "7.3.4"
              resolved "https://registry.yarnpkg.com/@babel/core/-/core-7.3.4.tgz#921a5a13746c21e32445bf0798680e9d11a6530b"
              integrity sha512-jRsuseXBo9pN197KnDwhhaaBzyZr2oIcLHHTt2oDdQrej5Qp57dCCJafWx5ivU8/alEYDpssYqv1MUqcxwQlrA==
              dependencies:
                "@babel/code-frame" "^7.0.0"
                "@babel/generator" "^7.3.4"

        Yield a single PackageData
        """
        with io.open(location, encoding='utf-8') as yl:
            yl_dependencies = yl.read().split('\n\n')

        dependencies_by_purl = {}
        for yl_dependency in yl_dependencies:
            lines = yl_dependency.splitlines(False)
            if all(l.startswith('#') or not l.strip() for l in lines):
                # header or empty blocks are all comments or empties
                continue

            top_requirements = []
            dependency_data = {}
            sub_dependencies = []

            for line in lines:
                stripped = line.strip()
                comment = line.startswith('#')
                if not stripped or comment:
                    continue

                if line.startswith(' ' * 4):
                    # "@babel/code-frame" "^7.0.0"
                    # hosted-git-info "^2.1.4"
                    # semver "2 || 3 || 4 || 5"
                    ns_name, _, constraint = stripped.partition(' ')
                    if '"' in ns_name:
                        ns_name = ns_name.replace('"', '')
                    ns, _ , name = ns_name.rpartition('/')

                    if ':' in constraint and '@' in constraint:
                        # dependencies with requirements like this are aliases and should be reported
                        aliased_package, _, constraint = constraint.rpartition('@')
                        _, _, aliased_package_name = aliased_package.rpartition(':')
                        ns, _ , name = aliased_package_name.rpartition('/')

                    sub_dependencies.append((ns, name, constraint,))

                elif line.startswith(' ' * 2):
                    # version "7.3.4"
                    # resolved "https://registry.yarnpkg.com/@babel...."
                    # integrity sha512-jRsuseXBo9
                    key, _, value = stripped.partition(' ')
                    value = value.strip().strip("\"'")
                    key = key.strip()
                    if key != 'dependencies':
                        dependency_data[key] = value

                elif not line.startswith(' ') and stripped.endswith(':'):
                    # the first line of a dependency has the name and requirements
                    # "@babel/core@^7.1.0", "@babel/core@^7.3.4":
                    # For aliases: "@alias@npm:@package@^12":
                    requirements = stripped.strip(':').split(', ')
                    requirements = [r.strip().strip("\"'") for r in requirements]
                    for req in requirements:
                        if req.startswith('@'):
                            # 2 = package, 4 = alias
                            assert req.count('@') in [2, 4]

                        ns_name, _, constraint = req.rpartition('@')
                        ns, _ , name = ns_name.rpartition('/')
                        constraint = constraint.strip("\"'")
                        # If we have an alias, just keep the package part:
                        # <alias-package>@npm:<package>
                        if "@npm:" in ns:
                            ns = ns.split(':')[1]
                        if "@npm:" in name:
                            name = name.split(':')[1]
                        top_requirements.append((ns, name, constraint,))

                else:
                    raise Exception('Inconsistent content')

            if TRACE_NPM:
                logger_debug(f'YarnLockV1Handler: parse: top_requirements: {top_requirements}')

            # top_requirements should be all for the same package
            ns_names = set([(ns, name) for ns, name, _constraint in top_requirements])
            assert len(ns_names) == 1, f'Different names for same dependency is not supported: {ns_names!r}'
            ns, name = ns_names.pop()
            version = dependency_data.get('version')
            extracted_requirement = ' '.join(constraint for _ns, _name, constraint in top_requirements)

            misc = get_urls(ns, name, version)
            resolved = dependency_data.get('resolved')
            misc.update(get_checksum_and_url(resolved).items())
            integrity = dependency_data.get('integrity')
            misc.update(get_algo_hexsum(integrity).items())

            # we create a resolve package with the details
            resolved_package_mapping = dict(
                datasource_id=cls.datasource_id,
                type=cls.default_package_type,
                namespace=ns,
                name=name,
                version=version,
                primary_language=cls.default_primary_language,
                is_virtual=True,
                **misc,
            )
            resolved_package_data = models.PackageData.from_data(resolved_package_mapping, package_only)

            # we add the sub-deps to the resolved package
            for subns, subname, subconstraint in sub_dependencies:
                subpurl = PackageURL(type=cls.default_package_type, namespace=subns, name=subname)
                subconstraint = subconstraint.strip("\"'")
                subdep = models.DependentPackage(
                    purl=str(subpurl),
                    extracted_requirement=subconstraint,
                    # FIXME: these are NOT correct
                    scope='dependencies',
                    is_optional=False,
                    is_runtime=True,
                    is_direct=True,
                )
                resolved_package_data.dependencies.append(subdep)

            # we create a purl with a version, since we are resolved
            dep_purl = str(PackageURL(
                type=cls.default_package_type,
                namespace=ns,
                name=name,
                version=version,
            ))

            dep = models.DependentPackage(
                purl=dep_purl,
                extracted_requirement=extracted_requirement,
                is_pinned=True,
                # FIXME: these are NOT correct
                scope='dependencies',
                is_optional=False,
                is_runtime=True,
                is_direct=False,
                resolved_package=resolved_package_data.to_dict(),
            )

            if not dep_purl in dependencies_by_purl:
                dependencies_by_purl[dep_purl] = dep.to_dict()
            else:
                # FIXME: We have duplicate dependencies because of aliases
                # should we do something?
                pass

        dependencies = list(dependencies_by_purl.values())
        update_dependencies_as_resolved(dependencies=dependencies)
        package_data = dict(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            primary_language=cls.default_primary_language,
            dependencies=dependencies,
        )
        yield models.PackageData.from_data(package_data, package_only)


class UnknownPnpmLockFormat(Exception):
    pass


class BasePnpmLockHandler(BaseNpmHandler):

    @classmethod
    def parse(cls, location, package_only=False):
        """
        Parses and yields package dependencies for all lockfile versions
        present in the spec: https://github.com/pnpm/spec/blob/master/lockfile/
        """

        with open(location) as yl:
            lock_data = saneyaml.load(yl.read())

        lockfile_version = lock_data.get("lockfileVersion")
        is_shrinkwrap = False
        if not lockfile_version:
            lockfile_version = lock_data.get("shrinkwrapVersion")
            lockfile_minor_version = lock_data.get("shrinkwrapMinorVersion")
            if lockfile_minor_version:
                lockfile_version = f"{lockfile_version}.{lockfile_minor_version}"
            is_shrinkwrap = True

        extra_data = {
            "lockfileVersion": lockfile_version,
        }
        major_v, minor_v = lockfile_version.split(".")

        resolved_packages = lock_data.get("packages", {})
        dependency_relations = lock_data.get("snapshots", {})
        dependency_relations_by_purl = {}
        if dependency_relations:
            for purl_fields, relations in dependency_relations.items():
                clean_purl_fields = purl_fields.split("(")[0]
                sections = clean_purl_fields.split("/")
                namespace = None
                if len(sections) == 2:
                    namespace, name_version = sections
                elif len(sections) == 1:
                    name_version, = sections
                name, version = name_version.split("@")

                purl = PackageURL(
                    type=cls.default_package_type,
                    name=name,
                    namespace=namespace,
                    version=version,
                ).to_string()
                dependency_relations_by_purl[purl] = relations

        dependencies_by_purl = {}

        for purl_fields, data in resolved_packages.items():
            if major_v == "6":
                clean_purl_fields = purl_fields.split("(")[0]
            elif major_v == "5" or is_shrinkwrap:
                clean_purl_fields = purl_fields.split("_")[0]
            elif major_v == "9":
                clean_purl_fields = purl_fields
            else:
                message = f"Unknown pnpm lockfile format: {lockfile_version}"
                raise UnknownPnpmLockFormat(message, purl_fields)

            sections = clean_purl_fields.split("/")
            name_version = None
            namespace = None
            if major_v == "6":
                if len(sections) == 2:
                    _, name_version = sections
                elif len(sections) == 3:
                    _, namespace, name_version = sections
                elif len(sections) == 1:
                    name_version, = sections

                name, version = name_version.split("@")
            elif major_v == "9":
                if len(sections) == 2:
                    namespace, name_version = sections
                elif len(sections) == 1:
                    name_version, = sections

                name, version = name_version.split("@")
            elif major_v == "5" or is_shrinkwrap:
                if len(sections) == 3:
                    _, name, version = sections
                elif len(sections) == 4:
                    _, namespace, name, version = sections

            purl = PackageURL(
                type=cls.default_package_type,
                name=name,
                namespace=namespace,
                version=version,
            ).to_string()

            checksum = data.get('resolution') or {}
            integrity = checksum.get('integrity')
            misc = get_algo_hexsum(integrity)

            dependencies = data.get('dependencies') or {}
            optional_dependencies = data.get('optionalDependencies') or {}
            transitive_peer_dependencies = data.get('transitivePeerDependencies') or []

            if purl in dependency_relations_by_purl:
                dependency_relations = dependency_relations_by_purl.get(purl)
                if dependency_relations:
                    deps = dependency_relations.get('dependencies')
                    if deps:
                        dependencies.update(deps)
                    optional_deps = dependency_relations.get('optionalDependencies')
                    if optional_deps:
                        optional_dependencies.update(optional_deps)
                    transitive_peer_deps = dependency_relations.get('transitivePeerDependencies')
                    if transitive_peer_deps:
                        transitive_peer_dependencies.extend(transitive_peer_deps)

            peer_dependencies = data.get('peerDependencies') or {}
            peer_dependencies_meta = data.get('peerDependenciesMeta') or {}

            deps_for_resolved_by_purl = {}
            cls.update_dependencies_by_purl(
                dependencies=dependencies,
                scope='dependencies',
                dependencies_by_purl=deps_for_resolved_by_purl,
                is_pinned=True,
                is_direct=False,
            )
            cls.update_dependencies_by_purl(
                dependencies=peer_dependencies,
                scope='peerDependencies',
                dependencies_by_purl=deps_for_resolved_by_purl,
                is_optional=True,
                is_direct=False,
            )
            cls.update_dependencies_by_purl(
                dependencies=optional_dependencies,
                scope='optionalDependencies',
                dependencies_by_purl=deps_for_resolved_by_purl,
                is_pinned=True,
                is_optional=True,
                is_direct=False,
            )
            cls.update_dependencies_by_purl(
                dependencies=peer_dependencies_meta,
                scope='peerDependenciesMeta',
                dependencies_by_purl=deps_for_resolved_by_purl,
            )
            cls.update_dependencies_by_purl(
                dependencies=transitive_peer_dependencies,
                scope='transitivePeerDependencies',
                dependencies_by_purl=deps_for_resolved_by_purl,
            )

            dependencies_for_resolved = [
                dep_package.to_dict()
                for dep_package in deps_for_resolved_by_purl.values()
            ]

            resolved_package_mapping = dict(
                datasource_id=cls.datasource_id,
                type=cls.default_package_type,
                primary_language=cls.default_primary_language,
                namespace=namespace,
                name=name,
                version=version,
                dependencies=dependencies_for_resolved,
                is_virtual=True,
                **misc,
            )
            resolved_package = models.PackageData.from_data(resolved_package_mapping)

            extra_data_fields = ["cpu", "os", "engines", "deprecated", "hasBin"]

            is_dev = data.get("dev", False)
            is_runtime = not is_dev
            is_optional = data.get("optional", False)

            extra_data_deps = {}
            for key in extra_data_fields:
                value = data.get(key, None)
                if value is not None:
                    extra_data_deps[key] = value

            dependency_data = models.DependentPackage(
                purl=purl,
                is_optional=is_optional,
                is_runtime=is_runtime,
                is_pinned=True,
                is_direct=True,
                resolved_package=resolved_package.to_dict(),
                extra_data=extra_data_deps,
            )
            dependencies_by_purl[purl] = dependency_data

        dependencies = [
            dep.to_dict()
            for dep in dependencies_by_purl.values()
        ]
        update_dependencies_as_resolved(dependencies=dependencies)
        root_package_data = dict(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            primary_language=cls.default_primary_language,
            dependencies=dependencies,
            extra_data=extra_data,
        )
        yield models.PackageData.from_data(root_package_data)


class PnpmShrinkwrapYamlHandler(BasePnpmLockHandler):
    datasource_id = 'pnpm_shrinkwrap_yaml'
    path_patterns = ('*/shrinkwrap.yaml',)
    default_package_type = 'npm'
    default_primary_language = 'JavaScript'
    is_lockfile = True
    description = 'pnpm shrinkwrap.yaml lockfile'
    documentation_url = 'https://github.com/pnpm/spec/blob/master/lockfile/4.md'


class PnpmLockYamlHandler(BasePnpmLockHandler):
    datasource_id = 'pnpm_lock_yaml'
    path_patterns = ('*/pnpm-lock.yaml',)
    default_package_type = 'npm'
    default_primary_language = 'JavaScript'
    is_lockfile = True
    description = 'pnpm pnpm-lock.yaml lockfile'
    documentation_url = 'https://github.com/pnpm/spec/blob/master/lockfile/6.0.md'


class PnpmWorkspaceYamlHandler(models.NonAssemblableDatafileHandler):
    datasource_id = 'pnpm_workspace_yaml'
    path_patterns = ('*/pnpm-workspace.yaml',)
    default_package_type = 'npm'
    default_primary_language = 'JavaScript'
    description = 'pnpm workspace yaml file'
    documentation_url = 'https://pnpm.io/pnpm-workspace_yaml'

    @classmethod
    def parse(cls, location, package_only=False):
        """
        Parses and gets pnpm workspace locations from the file.
        """
        with open(location) as yl:
            workspace_data = saneyaml.load(yl.read())

        workspaces = workspace_data.get('packages')
        if workspaces:
            extra_data = {
                'workspaces': workspaces,
            }
            root_package_data = dict(
                datasource_id=cls.datasource_id,
                type=cls.default_package_type,
                primary_language=cls.default_primary_language,
                extra_data=extra_data,
            )
            yield models.PackageData.from_data(root_package_data)


def get_checksum_and_url(url):
    """
    Return a mapping of {download_url, sha1} where the checksum can be a
    fragment for a sha1.
    """
    if not url:
        return {}

    url, checksum = urllib.parse.urldefrag(url)
    sha1_hex_len = 40
    if checksum and len(checksum) == sha1_hex_len:
        return dict(download_url=url, sha1=checksum)
    else:
        return dict(download_url=url)


def get_algo_hexsum(checksum):
    """
    Return a mapping of {alogo: checksum in hex} given a prefixed checksum from
    an npm manifest.
    """
    if not checksum or '-' not in checksum:
        return {}

    algo, _, checksum = checksum.partition('-')
    # value is base64 encoded: we convert to hex
    checksum = base64.b64decode(checksum.encode('ascii')).hex()
    return {algo: checksum}


def npm_homepage_url(namespace, name, registry='https://www.npmjs.com/package'):
    """
    Return an npm package registry homepage URL given a namespace, name,
    version and a base registry web interface URL.

    For example:
    >>> expected = 'https://www.npmjs.com/package/@invisionag/eslint-config-ivx'
    >>> assert npm_homepage_url('@invisionag', 'eslint-config-ivx') == expected

    >>> expected = 'https://www.npmjs.com/package/angular'
    >>> assert npm_homepage_url(None, 'angular') == expected

    >>> expected = 'https://www.npmjs.com/package/angular'
    >>> assert npm_homepage_url('', 'angular') == expected

    >>> expected = 'https://yarnpkg.com/en/package/angular'
    >>> assert npm_homepage_url('', 'angular', 'https://yarnpkg.com/en/package') == expected

    >>> expected = 'https://yarnpkg.com/en/package/@ang/angular'
    >>> assert npm_homepage_url('@ang', 'angular', 'https://yarnpkg.com/en/package') == expected

    >>> assert not npm_homepage_url(None, None)
    """
    if name:
        if namespace:
            ns_name = f'{namespace}/{name}'
        else:
            ns_name = name
        return f'{registry}/{ns_name}'


def npm_download_url(namespace, name, version, registry='https://registry.npmjs.org'):
    """
    Return an npm package tarball download URL given a namespace, name, version
    and a base registry URL.

    For example:
    >>> expected = 'https://registry.npmjs.org/@invisionag/eslint-config-ivx/-/eslint-config-ivx-0.1.4.tgz'
    >>> assert npm_download_url('@invisionag', 'eslint-config-ivx', '0.1.4') == expected

    >>> expected = 'https://registry.npmjs.org/angular/-/angular-1.6.6.tgz'
    >>> assert npm_download_url('', 'angular', '1.6.6') == expected

    >>> expected = 'https://registry.npmjs.org/angular/-/angular-1.6.6.tgz'
    >>> assert npm_download_url(None, 'angular', '1.6.6') == expected

    >>> assert not npm_download_url(None, None, None)
    """
    if name and version:
        if namespace:
            ns_name = f'{namespace}/{name}'
        else:
            ns_name = name
        return f'{registry}/{ns_name}/-/{name}-{version}.tgz'


def npm_api_url(namespace, name, version=None, registry='https://registry.npmjs.org'):
    """
    Return a package API data URL given a namespace, name, version and a base
    registry URL.

    Special quoting rules are applied for scoped npms.

    For example:
    >>> result = npm_api_url('@invisionag', 'eslint-config-ivx', '0.1.4', 'https://registry.yarnpkg.com')
    >>> assert result == 'https://registry.yarnpkg.com/@invisionag%2feslint-config-ivx/0.1.4'

    >>> result = npm_api_url('@invisionag', 'eslint-config-ivx', registry='https://registry.yarnpkg.com')
    >>> assert result == 'https://registry.yarnpkg.com/@invisionag%2feslint-config-ivx'

    >>> assert npm_api_url(None, 'angular', '1.6.6') == 'https://registry.npmjs.org/angular/1.6.6'
    >>> assert npm_api_url(None, 'angular') == 'https://registry.npmjs.org/angular'

    >>> assert not npm_api_url(None, None, None)
    """
    if name:
        if namespace:
            # this is a legacy wart: older registries used to always encode this /
            # FIXME: do NOT encode and use plain / instead
            ns_name = '%2f'.join([namespace, name])
        else:
            ns_name = name

        if version:
            version = f'/{version}'
        else:
            version = ''

        return f'{registry}/{ns_name}{version}'


def is_scoped_package(name):
    """
    Return True if name contains a namespace.

    For example::
    >>> is_scoped_package('@angular')
    True
    >>> is_scoped_package('some@angular')
    False
    >>> is_scoped_package('linq')
    False
    >>> is_scoped_package('%40angular')
    True
    """
    return name.startswith(('@', '%40',))


def split_scoped_package_name(name):
    """
    Return a tuple of (namespace, name) given a package name.
    Namespace is the "scope" of a scoped package.
    / and @ can be url-quoted and will be unquoted.

    For example:
    >>> nsn = split_scoped_package_name('@linclark/pkg')
    >>> assert ('@linclark', 'pkg') == nsn, nsn
    >>> nsn = split_scoped_package_name('@linclark%2fpkg')
    >>> assert ('@linclark', 'pkg') == nsn, nsn
    >>> nsn = split_scoped_package_name('angular')
    >>> assert (None, 'angular') == nsn, nsn
    >>> nsn = split_scoped_package_name('%40angular%2fthat')
    >>> assert ('@angular', 'that') == nsn, nsn
    >>> nsn = split_scoped_package_name('%40angular')
    >>> assert ('@angular', None) == nsn, nsn
    >>> nsn = split_scoped_package_name('@angular')
    >>> assert ('@angular', None) == nsn, nsn
    >>> nsn = split_scoped_package_name('angular/')
    >>> assert (None, 'angular') == nsn, nsn
    >>> nsn = split_scoped_package_name('%2fangular%2f/ ')
    >>> assert (None, 'angular') == nsn, nsn
    """
    if not name:
        return None, None

    name = name and name.strip()
    if not name:
        return None, None

    # FIXME: this legacy percent encoding/decoding should no longer be needed
    name = name.replace('%40', '@').replace('%2f', '/').replace('%2F', '/')
    name = name.rstrip('@').strip('/').strip()
    if not name:
        return None, None

    # this should never happen: wee only have a scope.
    # TODO: raise an  exception?
    if is_scoped_package(name) and '/' not in name:
        return name, None

    ns, _, name = name.rpartition('/')
    ns = ns.strip() or None
    name = name.strip() or None
    return ns, name


def get_declared_licenses(license_object):
    """
    Return a list of declared licenses, either strings or dicts.
    """
    if not license_object:
        return []

    if isinstance(license_object, str):
        # current, up to date form
        return [license_object]

    declared_licenses = []
    if isinstance(license_object, dict):
        # old, deprecated forms
        """
         "license": {
            "type": "MIT",
            "url": "http://github.com/kriskowal/q/raw/master/LICENSE"
          }
        """
        declared_licenses.append(license_object)

    elif isinstance(license_object, list):
        # old, deprecated forms
        """
        "licenses": [{"type": "Apache License, Version 2.0",
                      "url": "http://www.apache.org/licenses/LICENSE-2.0" } ]
        or
        "licenses": ["MIT"],
        """
        declared_licenses.extend(license_object)
    return declared_licenses


def licenses_mapper(license, licenses, package):  # NOQA
    """
    Update package licensing and return package based on the `license` and
    `licenses` values found in a package.

    Licensing data structure has evolved over time and is a tad messy.
    https://docs.npmjs.com/files/package.json#license
    license(s) is either:
    - a string with:
     - an SPDX id or expression { "license" : "(ISC OR GPL-3.0)" }
     - some license name or id
     - "SEE LICENSE IN <filename>"
    - (Deprecated) an array or a list of arrays of type, url.
    -  "license": "UNLICENSED" means this is proprietary
    """
    declared_license = get_declared_licenses(license) or []
    declared_license.extend(get_declared_licenses(licenses)  or [])
    if declared_license:
        package.extracted_license_statement = declared_license
    return package


def party_mapper(party, package, party_type):
    """
    Update package parties with party of `party_type` and return package.
    https://docs.npmjs.com/files/package.json#people-fields-author-contributors
    """
    if isinstance(party, list):
        for auth in party:
            name, email, url = parse_person(auth)
            package.parties.append(models.Party(
                type=models.party_person,
                name=name,
                role=party_type,
                email=email,
                url=url))
    else:
        # a string or dict
        name, email, url = parse_person(party)
        package.parties.append(models.Party(
            type=models.party_person,
            name=name,
            role=party_type,
            email=email,
            url=url))

    return package


def bugs_mapper(bugs, package):
    """
    Update package bug tracker and support email and return package.
    https://docs.npmjs.com/files/package.json#bugs
    The url to your project's issue tracker and / or the email address to
    which issues should be reported.
    { "url" : "https://github.com/owner/project/issues"
    , "email" : "project@hostname.com"
    }
    You can specify either one or both values. If you want to provide only a
    url, you can specify the value for "bugs" as a simple string instead of an
    object.
    """
    if isinstance(bugs, str):
        package.bug_tracking_url = bugs
    elif isinstance(bugs, dict):
        # we ignore the bugs email for now
        package.bug_tracking_url = bugs.get('url')
    return package


def vcs_repository_mapper(repo, package, vcs_revision=None):
    """
    https://docs.npmjs.com/files/package.json#repository
    "repository" :
      { "type" : "git"
      , "url" : "https://github.com/npm/npm.git"
      }
    "repository" :
      { "type" : "svn"
      , "url" : "https://v8.googlecode.com/svn/trunk/"
      }
    """
    if not repo:
        return package

    if isinstance(repo, list):
        # There is a case where we can have a list with a single element
        repo = repo[0]

    vcs_tool = ''
    vcs_repository = ''

    if isinstance(repo, str):
        vcs_repository = normalize_vcs_url(repo)

    elif isinstance(repo, dict):
        repo_url = normalize_vcs_url(repo.get('url'))
        if repo_url:
            vcs_tool = repo.get('type') or 'git'
            # remove vcs_tool string if repo_url already contains it
            if repo_url.startswith(vcs_tool):
                vcs_tool = ''
            vcs_repository = repo_url

    if vcs_repository:
        if vcs_tool:
            vcs_url = '{}+{}'.format(vcs_tool, vcs_repository)
        else:
            vcs_url = vcs_repository

        if vcs_revision:
            vcs_url += '@' + vcs_revision
        package.vcs_url = vcs_url
    return package


def dist_mapper(dist, package):
    """
    Only present in some package.json forms (as installed or from a
    registry). Not documented.
    "dist": {
      "integrity: "sha512-VmqXvL6aSOb+rmswek7prvdFKsFbfMshcRRi07SdFyDqgG6uXsP276NkPTcrD0DiwVQ8rfnCUP8S90x0OD+2gQ==",
      "shasum": "a124386bce4a90506f28ad4b1d1a804a17baaf32",
      "dnl_url": "http://registry.npmjs.org/npm/-/npm-2.13.5.tgz"
      },
    """
    if not isinstance(dist, dict):
        return

    integrity = dist.get('integrity')
    for algo, hexsum in get_algo_hexsum(integrity).items():
        if hasattr(package, algo):
            setattr(package, algo, hexsum)

    package.sha1 = dist.get('shasum') or None

    dnl_url = dist.get('dnl_url')
    if not dnl_url:
        # Only add a synthetic download URL if there is none from the dist mapping.
        dnl_url = npm_download_url(package.namespace, package.name, package.version)
    package.download_url = dnl_url.strip()

    return package


def bundle_deps_mapper(bundle_deps, package):
    """
    https://docs.npmjs.com/files/package.json#bundleddependencies
        "This defines an array of package names that will be bundled
        when publishing the package."
    """
    for bdep in (bundle_deps or []):
        bdep = bdep and bdep.strip()
        if not bdep:
            continue

        ns, name = split_scoped_package_name(bdep)
        purl = models.PackageURL(type='npm', namespace=ns, name=name)

        dep = models.DependentPackage(purl=purl.to_string(),
            scope='bundledDependencies', is_runtime=True,
        )
        package.dependencies.append(dep)

    return package


def deps_mapper(deps, package, field_name, is_direct=True):
    """
    Handle deps such as dependencies, devDependencies, peerDependencies, optionalDependencies
    return a tuple of (dep type, list of deps)
    https://docs.npmjs.com/files/package.json#dependencies
    https://docs.npmjs.com/files/package.json#peerdependencies
    https://docs.npmjs.com/files/package.json#devdependencies
    https://docs.npmjs.com/files/package.json#optionaldependencies
    """
    #TODO: verify, merge and use logic at BaseNpmHandler.update_dependencies_by_purl
    npm_dependency_scopes_attributes = {
        'dependencies': dict(is_runtime=True, is_optional=False),
        'devDependencies': dict(is_runtime=False, is_optional=True),
        'peerDependencies': dict(is_runtime=True, is_optional=False),
        'optionalDependencies': dict(is_runtime=True, is_optional=True),
        'resolutions': dict(is_runtime=True, is_optional=False, is_pinned=True),
    }
    dependencies = package.dependencies

    deps_by_name = {}
    if field_name == 'optionalDependencies':
        # optionalDependencies override the dependencies with the same name
        # so we build a map of name->dep object for use later
        for d in dependencies:
            if d.scope != 'dependencies':
                continue
            purl = PackageURL.from_string(d.purl)
            npm_name = purl.name
            if purl.namespace:
                npm_name = '/'.join([purl.namespace, purl.name])
            deps_by_name[npm_name] = d

    for fqname, requirement in deps.items():
        # Handle cases in ``resolutions`` with ``**``
        # "resolutions": {
        #   "**/@typescript-eslint/eslint-plugin": "^4.1.1",
        if fqname.startswith('**'):
            fqname = fqname.replace('**', '')
        ns, name = split_scoped_package_name(fqname)
        if not name:
            continue

        if ':' in requirement and '@' in requirement:
            # dependencies with requirements like this are aliases and should be reported
            aliased_package, _, requirement = requirement.rpartition('@')
            _, _, aliased_package_name = aliased_package.rpartition(':')
            ns, _ , name = aliased_package_name.rpartition('/')

        purl = PackageURL(type='npm', namespace=ns, name=name).to_string()

        # optionalDependencies override the dependencies with the same name
        # https://docs.npmjs.com/files/package.json#optionaldependencies
        # therefore we update/override the dependency of the same name
        overridable = deps_by_name.get(fqname)

        if overridable and field_name == 'optionalDependencies':
            overridable.purl = purl
            overridable.is_optional = True
            overridable.scope = field_name
        else:
            dependency_attributes = npm_dependency_scopes_attributes.get(field_name, dict())
            dep = models.DependentPackage(
                purl=purl,
                scope=field_name,
                extracted_requirement=requirement,
                is_direct=is_direct,
                **dependency_attributes
            )
            dependencies.append(dep)

    return package


person_parser = re.compile(
    r'^(?P<name>[^\(<]+)'
    r'\s?'
    r'(?P<email><([^>]+)>)?'
    r'\s?'
    r'(?P<url>\([^\)]+\))?$'
).match

person_parser_no_name = re.compile(
    r'(?P<email><([^>]+)>)?'
    r'\s?'
    r'(?P<url>\([^\)]+\))?$'
).match


class NpmInvalidPerson(Exception):
    pass


def parse_person(person):
    """
    https://docs.npmjs.com/files/package.json#people-fields-author-contributors
    A "person" is an object with a "name" field and optionally "url" and "email".

    Return a name, email, url tuple for a person object
    A person can be in the form:
      "author": {
        "name": "Isaac Z. Schlueter",
        "email": "i@izs.me",
        "url": "http://blog.izs.me"
      },
    or in the form:
      "author": "Isaac Z. Schlueter <i@izs.me> (http://blog.izs.me)",

    Both forms are equivalent.

    For example:
    >>> author = {
    ...   "name": "Isaac Z. Schlueter",
    ...   "email": "i@izs.me",
    ...   "url": "http://blog.izs.me"
    ... }
    >>> p = parse_person(author)
    >>> assert p == (u'Isaac Z. Schlueter', u'i@izs.me', u'http://blog.izs.me')
    >>> p = parse_person('Barney Rubble <b@rubble.com> (http://barnyrubble.tumblr.com/)')
    >>> assert p == (u'Barney Rubble', u'b@rubble.com', u'http://barnyrubble.tumblr.com/')
    >>> p = parse_person('Barney Rubble <none> (none)')
    >>> assert p == (u'Barney Rubble', None, None)
    >>> p = parse_person('Barney Rubble ')
    >>> assert p == (u'Barney Rubble', None, None)
    >>> author = {
    ...   "name": "Isaac Z. Schlueter",
    ...   "email": ["i@izs.me", "<jo2@todo.com> "],
    ...   "url": "http://blog.izs.me"
    ... }
    >>> p = parse_person(author)
    >>> assert p == (u'Isaac Z. Schlueter', u'i@izs.me\\njo2@todo.com', u'http://blog.izs.me')
    >>> p = parse_person('<b@rubble.com> (http://barnyrubble.tumblr.com/)')
    >>> assert p == (None, u'b@rubble.com', u'http://barnyrubble.tumblr.com/')
    """
    # TODO: detect if this is a person name or a company name e.g. the type?

    name = None
    email = None
    url = None

    if isinstance(person, str):
        parsed = person_parser(person)
        if not parsed:
            parsed = person_parser_no_name(person)
            if not parsed:
                return person, None, None
            else:
                name = None
                email = parsed.group('email')
                url = parsed.group('url')
        else:
            name = parsed.group('name')
            email = parsed.group('email')
            url = parsed.group('url')

    elif isinstance(person, dict):
        # ensure we have our three values
        name = person.get('name')
        email = person.get('email')
        url = person.get('url')

    else:
        return None, None, None

    if name:
        if isinstance(name, str):
            name = name.strip()
            if name.lower() == 'none':
                name = None
        else:
            name = None
    name = name or None

    if email:
        if isinstance(email, list):
            # legacy weirdness
            email = [e.strip('<> ') for e in email if e and e.strip()]
            email = '\n'.join([e.strip() for e in email
                               if e.strip() and e.strip().lower() != 'none'])
        if isinstance(email, str):
            email = email.strip('<> ').strip()
            if email.lower() == 'none':
                email = None
        else:
            email = None
    email = email or None

    if url:
        if isinstance(url, list):
            # legacy weirdness
            url = [u.strip('() ') for u in email if u and u.strip()]
            url = '\n'.join([u.strip() for u in url
                               if u.strip() and u.strip().lower() != 'none'])
        if isinstance(url, str):
            url = url.strip('() ').strip()
            if url.lower() == 'none':
                url = None
        else:
            url = None
    url = url or None

    return name, email, url


def keywords_mapper(keywords, package):
    """
    Update package keywords and return package.
    This is supposed to be an array of strings, but sometimes this is a string.
    https://docs.npmjs.com/files/package.json#keywords
    """
    if isinstance(keywords, str):
        if ',' in keywords:
            keywords = [k.strip() for k in keywords.split(',') if k.strip()]
        else:
            keywords = [keywords]

    package.keywords = keywords
    return package
