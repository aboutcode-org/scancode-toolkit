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


class SwiftManifestJsonHandler(models.DatafileHandler):
    datasource_id = "swift_package_manifest_json"
    path_patterns = ("*/Package.swift.json",)
    default_package_type = "swift"
    default_primary_language = "Swift"
    description = "JSON dump of Package.swift created with ``swift package dump-package > Package.swift.json``"
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
        swift_resolved_package_resource = [
            r for r in siblings if r.name == "Package.resolved"
        ]
        dependencies_from_manifest = package_data.dependencies

        processed_dependencies = []
        if swift_resolved_package_resource:
            swift_resolved_package_resource = swift_resolved_package_resource[0]
            swift_resolved_package_data = swift_resolved_package_resource.package_data

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

            if swift_resolved_package_resource:
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
            r for r in siblings if r.name == "Package.swift.json"
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
    path = parsed_url.path.removesuffix(".git")
    canonical_name = hostname + path

    return canonical_name.rsplit("/", 1)
