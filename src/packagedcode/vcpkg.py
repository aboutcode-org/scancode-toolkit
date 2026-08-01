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

from debian_inspector import debcon
from packageurl import PackageURL

from packagedcode import models

"""
Handle vcpkg package manifests (vcpkg.json) and legacy CONTROL files.
https://learn.microsoft.com/en-us/vcpkg/reference/vcpkg-json
https://learn.microsoft.com/en-us/vcpkg/maintainers/ports
"""

logger = logging.getLogger(__name__)


class VcpkgJsonHandler(models.DatafileHandler):
    datasource_id = "vcpkg_json"
    path_patterns = (
        "*/vcpkg.json",
        "vcpkg.json",
    )
    default_package_type = "vcpkg"
    default_primary_language = "C++"
    description = "vcpkg package manifest"
    documentation_url = "https://learn.microsoft.com/en-us/vcpkg/reference/vcpkg-json"

    @classmethod
    def _parse(cls, manifest_data, package_only=False):
        if not isinstance(manifest_data, dict):
            return

        name = manifest_data.get("name")
        if not name:
            return

        version = (
            manifest_data.get("version-string")
            or manifest_data.get("version")
            or manifest_data.get("version-date")
            or manifest_data.get("version-semver")
        )

        port_version = manifest_data.get("port-version")
        qualifiers = {}
        if port_version is not None:
            qualifiers["port_version"] = str(port_version)

        description = manifest_data.get("description")
        if isinstance(description, list):
            description = "\n".join(description)

        homepage_url = manifest_data.get("homepage")
        documentation_url = manifest_data.get("documentation")

        extracted_license_statement = manifest_data.get("license")

        parties = []
        maintainers = manifest_data.get("maintainers")
        if maintainers:
            if isinstance(maintainers, str):
                maintainers = [maintainers]
            if isinstance(maintainers, list):
                for m in maintainers:
                    if isinstance(m, str):
                        parties.append(models.Party(name=m, role="maintainer"))
                    elif isinstance(m, dict) and m.get("name"):
                        parties.append(
                            models.Party(
                                name=m.get("name"),
                                email=m.get("email"),
                                url=m.get("homepage"),
                                role="maintainer",
                            )
                        )

        dependencies = []
        deps = manifest_data.get("dependencies") or []
        for dep in deps:
            dep_name = None
            req = None
            if isinstance(dep, str):
                dep_name = dep
            elif isinstance(dep, dict):
                dep_name = dep.get("name")
                req = (
                    dep.get("version>=")
                    or dep.get("version")
                    or dep.get("version-string")
                )
                if req and not str(req).startswith(">=") and dep.get("version>="):
                    req = f">= {req}"

            if dep_name:
                dependencies.append(
                    models.DependentPackage(
                        purl=PackageURL(type="vcpkg", name=dep_name).to_string(),
                        extracted_requirement=str(req) if req is not None else None,
                        scope="dependencies",
                        is_runtime=True,
                        is_optional=False,
                    )
                )

        features = manifest_data.get("features") or {}
        if isinstance(features, dict):
            for feature_name, feature_data in features.items():
                if isinstance(feature_data, dict):
                    feature_deps = feature_data.get("dependencies") or []
                    for dep in feature_deps:
                        dep_name = None
                        req = None
                        if isinstance(dep, str):
                            dep_name = dep
                        elif isinstance(dep, dict):
                            dep_name = dep.get("name")
                            req = dep.get("version>=") or dep.get("version")
                            if req and not str(req).startswith(">=") and dep.get("version>="):
                                req = f">= {req}"
                        if dep_name:
                            dependencies.append(
                                models.DependentPackage(
                                    purl=PackageURL(
                                        type="vcpkg", name=dep_name
                                    ).to_string(),
                                    extracted_requirement=str(req) if req is not None else None,
                                    scope=f"features:{feature_name}",
                                    is_runtime=True,
                                    is_optional=True,
                                )
                            )

        extra_data = {}
        if documentation_url:
            extra_data["documentation"] = documentation_url
        supports = manifest_data.get("supports")
        if supports:
            extra_data["supports"] = supports

        package_data = dict(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            name=name,
            version=version,
            qualifiers=qualifiers or None,
            primary_language=cls.default_primary_language,
            description=description,
            homepage_url=homepage_url,
            extracted_license_statement=extracted_license_statement,
            parties=parties,
            dependencies=dependencies,
            extra_data=extra_data or None,
        )
        return models.PackageData.from_data(package_data, package_only)

    @classmethod
    def parse(cls, location, package_only=False):
        with io.open(location, encoding="utf-8") as loc:
            try:
                manifest_data = json.load(loc)
            except Exception as e:
                logger.warning(f"Failed to parse vcpkg.json at {location}: {e}")
                return

        package_data = cls._parse(manifest_data, package_only)
        if package_data:
            yield package_data


class VcpkgControlHandler(models.DatafileHandler):
    datasource_id = "vcpkg_control"
    path_patterns = (
        "*/CONTROL",
        "CONTROL",
    )
    default_package_type = "vcpkg"
    default_primary_language = "C++"
    description = "vcpkg legacy port CONTROL file"
    documentation_url = "https://learn.microsoft.com/en-us/vcpkg/maintainers/ports"

    @classmethod
    def parse(cls, location, package_only=False):
        try:
            paragraphs = list(debcon.get_paragraphs_data_from_file(location))
        except Exception as e:
            logger.warning(f"Failed to parse CONTROL file at {location}: {e}")
            return

        if not paragraphs:
            return

        main_para = paragraphs[0]
        name = main_para.get("source") or main_para.get("package")
        if not name:
            return

        version = main_para.get("version")
        port_version = main_para.get("port-version")
        qualifiers = {}
        if port_version is not None:
            qualifiers["port_version"] = str(port_version)

        description = main_para.get("description")
        homepage_url = main_para.get("homepage")

        dependencies = []
        build_depends = main_para.get("build-depends")
        if build_depends:
            for dep_str in build_depends.split(","):
                dep_str = dep_str.strip()
                if not dep_str:
                    continue
                dep_name = dep_str.split()[0]
                dependencies.append(
                    models.DependentPackage(
                        purl=PackageURL(type="vcpkg", name=dep_name).to_string(),
                        extracted_requirement=None,
                        scope="dependencies",
                        is_runtime=True,
                        is_optional=False,
                    )
                )

        for feature_para in paragraphs[1:]:
            feature_name = feature_para.get("feature")
            if not feature_name:
                continue
            feature_deps = feature_para.get("build-depends")
            if feature_deps:
                for dep_str in feature_deps.split(","):
                    dep_str = dep_str.strip()
                    if not dep_str:
                        continue
                    dep_name = dep_str.split()[0]
                    dependencies.append(
                        models.DependentPackage(
                            purl=PackageURL(type="vcpkg", name=dep_name).to_string(),
                            extracted_requirement=None,
                            scope=f"features:{feature_name}",
                            is_runtime=True,
                            is_optional=True,
                        )
                    )

        package_data = dict(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            name=name,
            version=version,
            qualifiers=qualifiers or None,
            primary_language=cls.default_primary_language,
            description=description,
            homepage_url=homepage_url,
            dependencies=dependencies,
        )
        package_obj = models.PackageData.from_data(package_data, package_only)
        if package_obj:
            yield package_obj
