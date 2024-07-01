# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import io
import json
import logging
import os
from urllib import parse

from packagedcode import models
from packageurl import PackageURL

"""
Handle the resolved file and JSON dump of the manifest for Swift packages.
https://docs.swift.org/package-manager/PackageDescription/PackageDescription.html

Run the commands below before running the scan:

-  To create a parsable JSON version of the Package.swift manifest, run this: ``swift package dump-package > Package.swift.json``
-  To create the Package.resolved lock file, run this: ``swift package resolve``
"""


SCANCODE_DEBUG_PACKAGE = os.environ.get("SCANCODE_DEBUG_PACKAGE", False)

TRACE = SCANCODE_DEBUG_PACKAGE


def logger_debug(*args):
    pass


logger = logging.getLogger(__name__)

if TRACE:
    import sys

    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(" ".join(isinstance(a, str) and a or repr(a) for a in args))


class SwiftShowDependenciesDepLockHandler(models.DatafileHandler):
    datasource_id = "swift_package_show_dependencies"
    path_patterns = ("*/swift-show-dependencies.deplock",)
    default_package_type = "swift"
    default_primary_language = "Swift"
    description = "Swift dependency graph created by DepLock"
    documentation_url = "https://forums.swift.org/t/swiftpm-show-dependencies-without-fetching-dependencies/51154"

    @classmethod
    def _parse(cls, swift_dependency_relation, package_only=False):

        if TRACE:
            logger_debug(
                f"SwiftShowDependenciesDepLockHandler: deplock: package: {swift_dependency_relation}"
            )

        dependencies = get_flatten_dependencies(
            dependency_tree=swift_dependency_relation.get("dependencies")
        )

        package_data = dict(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            primary_language=cls.default_primary_language,
            # ``namespace`` is derived from repo URL and same is not available in dependency graph
            # See related issue: https://github.com/nexB/scancode-toolkit/issues/3793
            name=swift_dependency_relation.get("name"),
            dependencies=dependencies,
        )

        return models.PackageData.from_data(package_data, package_only)

    @classmethod
    def parse(cls, location, package_only=False):
        with io.open(location, encoding="utf-8") as loc:
            swift_dependency_relation = json.load(loc)

        yield cls._parse(swift_dependency_relation, package_only)

    @classmethod
    def assemble(
        cls, package_data, resource, codebase, package_adder=models.add_to_package
    ):
        siblings = resource.siblings(codebase)
        swift_manifest_resource = [
            r
            for r in siblings
            if r.name in ("Package.swift.json", "Package.swift.deplock")
        ]

        # Skip the assembly if the Swift manifest is present.
        # SwiftManifestJsonHandler's assembly will take care of the
        # dependencies from swift-show-dependencies.deplock file.
        if swift_manifest_resource:
            return []

        yield from super(SwiftShowDependenciesDepLockHandler, cls).assemble(
            package_data=package_data,
            resource=resource,
            codebase=codebase,
            package_adder=package_adder,
        )


class SwiftManifestJsonHandler(models.DatafileHandler):
    datasource_id = "swift_package_manifest_json"
    path_patterns = ("*/Package.swift.json", "*/Package.swift.deplock")
    default_package_type = "swift"
    default_primary_language = "Swift"
    description = "JSON dump of Package.swift created by DepLock or with ``swift package dump-package > Package.swift.json``"
    documentation_url = "https://docs.swift.org/package-manager/PackageDescription/PackageDescription.html"

    @classmethod
    def _parse(cls, swift_manifest, package_only=False):

        if TRACE:
            logger_debug(
                f"SwiftManifestJsonHandler: manifest: package: {swift_manifest}"
            )

        dependencies = get_dependencies(swift_manifest.get("dependencies"))
        platforms = swift_manifest.get("platforms", [])

        package_data = dict(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            primary_language=cls.default_primary_language,
            namespace=None,
            name=swift_manifest.get("name"),
            dependencies=dependencies,
            extra_data={"platforms": platforms},
        )

        return models.PackageData.from_data(package_data, package_only)

    @classmethod
    def parse(cls, location, package_only=False):
        with io.open(location, encoding="utf-8") as loc:
            swift_manifest = json.load(loc)

        yield cls._parse(swift_manifest, package_only)

    @classmethod
    def assemble(
        cls,
        package_data,
        resource,
        codebase,
        package_adder=models.add_to_package,
    ):
        """
        Use the dependencies from `Package.resolved` to create the
        top-level package with resolved dependencies.
        """
        siblings = resource.siblings(codebase)
        processed_dependencies = []
        swift_resolved_package_resource = [
            r for r in siblings if r.name == "Package.resolved"
        ]

        swift_show_dependencies_resources = [
            r for r in siblings if r.name == "swift-show-dependencies.deplock"
        ]

        if swift_show_dependencies_resources:
            swift_show_dependencies_resource = swift_show_dependencies_resources[0]
            swift_show_dependencies_package_data = (
                swift_show_dependencies_resource.package_data
            )

            # Dependencies from `swift-show-dependencies.deplock` supersede dependencies from other datafiles.
            processed_dependencies = swift_show_dependencies_package_data[0][
                "dependencies"
            ]
            processed_dependencies = [
                models.DependentPackage.from_dict(i) for i in processed_dependencies
            ]

        # Use dependencies from `Package.resolved` when `swift-show-dependencies.deplock` is not present.
        else:
            dependencies_from_manifest = package_data.dependencies

            if swift_resolved_package_resource:
                swift_resolved_package_resource = swift_resolved_package_resource[0]
                swift_resolved_package_data = (
                    swift_resolved_package_resource.package_data
                )

                for package in swift_resolved_package_data:
                    version = package.get("version")
                    name = package.get("name")

                    purl = PackageURL(
                        type=cls.default_package_type, name=name, version=version
                    )
                    processed_dependencies.append(
                        models.DependentPackage(
                            purl=purl.to_string(),
                            scope="dependencies",
                            is_runtime=True,
                            is_optional=False,
                            is_resolved=True,
                            extracted_requirement=version,
                        )
                    )

                    for dependency in dependencies_from_manifest[:]:
                        dependency_purl = PackageURL.from_string(dependency.purl)

                        if dependency_purl.name == name:
                            dependencies_from_manifest.remove(dependency)

            processed_dependencies.extend(dependencies_from_manifest)

        datafile_path = resource.path
        if package_data.purl:
            package = models.Package.from_package_data(
                package_data=package_data,
                datafile_path=datafile_path,
            )

            if swift_show_dependencies_resources:
                package.datafile_paths.append(swift_show_dependencies_resource.path)
                package.datasource_ids.append(
                    SwiftShowDependenciesDepLockHandler.datasource_id
                )
            elif swift_resolved_package_resource:
                package.datafile_paths.append(swift_resolved_package_resource.path)
                package.datasource_ids.append(SwiftPackageResolvedHandler.datasource_id)

            package.populate_license_fields()
            yield package

            parent = resource.parent(codebase)
            cls.assign_package_to_resources(
                package=package,
                resource=parent,
                codebase=codebase,
                package_adder=package_adder,
            )

        if processed_dependencies:
            yield from models.Dependency.from_dependent_packages(
                dependent_packages=processed_dependencies,
                datafile_path=datafile_path,
                datasource_id=package_data.datasource_id,
                package_uid=package.package_uid,
            )
        yield resource


class SwiftPackageResolvedHandler(models.DatafileHandler):
    datasource_id = "swift_package_resolved"
    path_patterns = ("*/Package.resolved", "*/.package.resolved")
    default_package_type = "swift"
    default_primary_language = "swift"
    description = "Resolved full dependency lockfile for Package.swift created with ``swift package resolve``"
    documentation_url = (
        "https://docs.swift.org/package-manager/PackageDescription/"
        "PackageDescription.html#package-dependency"
    )

    @classmethod
    def parse(cls, location, package_only=False):
        with io.open(location, encoding="utf-8") as loc:
            package_resolved = json.load(loc)

        resolved_doc_version = package_resolved.get("version")

        if resolved_doc_version in [2, 3]:
            yield from packages_from_resolved_v2_and_v3(package_resolved)

        if resolved_doc_version == 1:
            yield from packages_from_resolved_v1(package_resolved)

    @classmethod
    def assemble(
        cls, package_data, resource, codebase, package_adder=models.add_to_package
    ):
        siblings = resource.siblings(codebase)
        swift_manifest_resource = [
            r
            for r in siblings
            if r.name in ("Package.swift.json", "Package.swift.deplock")
        ]

        # Skip the assembly if the ``Package.swift.json`` manifest is present.
        # SwiftManifestJsonHandler's assembly will take care of the resolved
        # dependencies from Package.resolved file.
        if swift_manifest_resource:
            return []

        yield from super(SwiftPackageResolvedHandler, cls).assemble(
            package_data=package_data,
            resource=resource,
            codebase=codebase,
            package_adder=package_adder,
        )


def packages_from_resolved_v2_and_v3(package_resolved):
    pinned = package_resolved.get("pins", [])

    for dependency in pinned:
        name = dependency.get("identity")
        kind = dependency.get("kind")
        location = dependency.get("location")
        state = dependency.get("state", {})
        version = None
        namespace = None

        if location and kind == "remoteSourceControl":
            namespace, name = get_namespace_and_name(location)

        version = state.get("version")

        if not version:
            version = state.get("revision")

        package_data = dict(
            datasource_id=SwiftPackageResolvedHandler.datasource_id,
            type=SwiftPackageResolvedHandler.default_package_type,
            primary_language=SwiftPackageResolvedHandler.default_primary_language,
            namespace=namespace,
            name=name,
            version=version,
        )
        yield models.PackageData.from_data(package_data, False)


def packages_from_resolved_v1(package_resolved):
    object = package_resolved.get("object", {})
    pinned = object.get("pins", [])

    for dependency in pinned:
        name = dependency.get("package")

        repository_url = dependency.get("repositoryURL")
        state = dependency.get("state", {})
        version = None
        namespace = None

        if repository_url:
            namespace, name = get_namespace_and_name(repository_url)

        version = state.get("version")

        if not version:
            version = state.get("revision")

        package_data = dict(
            datasource_id=SwiftPackageResolvedHandler.datasource_id,
            type=SwiftPackageResolvedHandler.default_package_type,
            primary_language=SwiftPackageResolvedHandler.default_primary_language,
            namespace=namespace,
            name=name,
            version=version,
        )
        yield models.PackageData.from_data(package_data, False)


def get_dependencies(dependencies):
    dependent_packages = []
    for dependency in dependencies or []:
        source = dependency.get("sourceControl")
        if not source:
            continue

        source = source[0]
        namespace = None
        name = source.get("identity")
        version = None
        is_resolved = False

        location = source.get("location")
        if remote := location.get("remote"):
            namespace, name = get_namespace_and_name(remote[0].get("urlString"))

        requirement = source.get("requirement")
        if exact := requirement.get("exact"):
            version = exact[0]
            is_resolved = True
        elif range := requirement.get("range"):
            bound = range[0]
            lower_bound = bound.get("lowerBound")
            upper_bound = bound.get("upperBound")
            version = f"vers:swift/>={lower_bound}|<{upper_bound}"

        purl = PackageURL(
            type="swift",
            namespace=namespace,
            name=name,
            version=version if is_resolved else None,
        )

        dependent_packages.append(
            models.DependentPackage(
                purl=purl.to_string(),
                scope="dependencies",
                is_runtime=True,
                is_optional=False,
                is_resolved=is_resolved,
                extracted_requirement=version,
            )
        )
    return dependent_packages


def get_namespace_and_name(url):
    parsed_url = parse.urlparse(url)
    hostname = parsed_url.hostname
    path = parsed_url.path.replace(".git", "")
    canonical_name = hostname + path

    return canonical_name.rsplit("/", 1)


def get_flatten_dependencies(dependency_tree):
    """
    Get the list of dependencies from the dependency graph where each
    element is a DependentPackage containing its 1st order dependencies.
    """
    dependencies = []
    transitive_dependencies = []

    # process direct dependency
    for dependency in dependency_tree:
        transitives = dependency.get("dependencies", [])
        transitive_dependencies.append(transitives)
        parent_child_dep = get_dependent_package_from_subtree(
            dependency=dependency,
            is_top_level_dependency=True,
        )
        dependencies.append(parent_child_dep)

    # process all transitive dependencies
    while transitive_dependencies:
        transitive_dependency_tree = transitive_dependencies.pop(0)
        if not transitive_dependency_tree:
            continue

        for transitive in transitive_dependency_tree:
            dependencies_of_transitive_dependency = transitive.get("dependencies", [])
            # add nested dependencies in transitive_dependencies queue for processing
            transitive_dependencies.append(dependencies_of_transitive_dependency)

            parent_child_dep = get_dependent_package_from_subtree(
                dependency=transitive,
                is_top_level_dependency=False,
            )

            dependencies.append(parent_child_dep)

    return dependencies


def get_dependent_package_from_subtree(dependency, is_top_level_dependency):
    """
    Get the DependentPackage for a ``dependency`` subtree along with its 1st
    order dependencies. Set `is_direct` to True if the subtree is a direct
    dependency for the top-level package.
    """
    dependencies_of_parent = []
    repository_url = dependency.get("url")
    version = dependency.get("version")
    transitives = dependency.get("dependencies", [])
    namespace, name = get_namespace_and_name(repository_url)
    purl = PackageURL(
        type="swift",
        namespace=namespace,
        name=name,
        version=version,
    )

    for transitive in transitives:
        transitive_repository_url = transitive.get("url")
        transitive_version = transitive.get("version")
        transitive_namespace, transitive_name = get_namespace_and_name(
            transitive_repository_url
        )
        transitive_purl = PackageURL(
            type="swift",
            namespace=transitive_namespace,
            name=transitive_name,
            version=transitive_version,
        )

        child_dependency = models.DependentPackage(
            purl=transitive_purl.to_string(),
            scope="dependencies",
            extracted_requirement=transitive_version,
            is_runtime=False,
            is_optional=False,
            is_resolved=True,
            is_direct=True,
        ).to_dict()

        dependencies_of_parent.append(child_dependency)

    parent_package_data_mapping = dict(
        datasource_id=SwiftShowDependenciesDepLockHandler.datasource_id,
        type=SwiftShowDependenciesDepLockHandler.default_package_type,
        primary_language=SwiftShowDependenciesDepLockHandler.default_primary_language,
        namespace=namespace,
        name=name,
        version=version,
        dependencies=dependencies_of_parent,
        is_virtual=True,
    )
    parent_dependency = models.PackageData.from_data(parent_package_data_mapping)

    return models.DependentPackage(
        purl=purl.to_string(),
        scope="dependencies",
        extracted_requirement=version,
        is_runtime=False,
        is_optional=False,
        is_resolved=True,
        is_direct=is_top_level_dependency,
        resolved_package=parent_dependency,
    )
