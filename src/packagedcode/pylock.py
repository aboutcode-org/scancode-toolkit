#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import logging
import os
import sys

from packageurl import PackageURL

from packagedcode import models
from packagedcode.pypi import BaseExtractedPythonLayout, get_pypi_urls

try:
    import tomli as tomllib
except ImportError:
    import tomllib

"""
Detect and collect Python pylock.toml lockfile information.
Support for PEP 751: A file format to record Python dependencies for installation reproducibility.
See https://packaging.python.org/en/latest/specifications/pylock-toml/
"""

TRACE = os.environ.get("SCANCODE_DEBUG_PACKAGE", False)


def logger_debug(*args):
    pass


logger = logging.getLogger(__name__)

if TRACE:
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(" ".join(isinstance(a, str) and a or repr(a) for a in args))


class PylockTomlHandler(BaseExtractedPythonLayout):
    datasource_id = "pypi_pylock_toml"
    path_patterns = ("*pylock.toml",)
    default_package_type = "pypi"
    default_primary_language = "Python"
    description = "Python pylock.toml lockfile (PEP 751)"
    documentation_url = (
        "https://packaging.python.org/en/latest/specifications/pylock-toml/"
    )

    @classmethod
    def parse(cls, location, package_only=False):
        """
        Parse a pylock.toml file and yield PackageData with dependencies.
        """
        with open(location, "rb") as fp:
            toml_data = tomllib.load(fp)

        lock_ver = toml_data.get("lock-version")
        packages = toml_data.get("packages", [])

        if not packages:
            return

        dependencies = []

        for package in packages:
            name = package.get("name")
            version = package.get("version")

            if not name or not version:
                continue

            dependencies_for_resolved = []

            pkg_dependencies = package.get("dependencies", [])
            for dep in pkg_dependencies:
                if not isinstance(dep, dict):
                    continue

                dep_name = dep.get("name")
                if not dep_name:
                    continue

                dep_requirement = dep.get("version")

                dep_purl = PackageURL(
                    type=cls.default_package_type,
                    name=dep_name,
                )

                dependency = models.DependentPackage(
                    purl=dep_purl.to_string(),
                    extracted_requirement=dep_requirement,
                    scope="dependencies",
                    is_runtime=True,
                    is_optional=False,
                    is_direct=True,
                    is_pinned=True,
                )
                dependencies_for_resolved.append(dependency.to_dict())

            download_url = None
            hash_data = {}
            extra_data = {}

            vcs = package.get("vcs")
            if vcs:
                vcs_type = vcs.get("type")
                vcs_url = vcs.get("url")
                commit_id = vcs.get("commit-id")
                if vcs_type and vcs_url and commit_id:
                    download_url = f"{vcs_type}+{vcs_url}@{commit_id}"
                extra_data["vcs"] = vcs

            sdist = package.get("sdist")
            if sdist:
                if not download_url:
                    download_url = sdist.get("url")
                if "hashes" in sdist:
                    hash_data.update(sdist["hashes"])

            wheels = package.get("wheels", [])
            if wheels:
                if not download_url and len(wheels) > 0:
                    download_url = wheels[0].get("url")

                if not hash_data and len(wheels) > 0:
                    first_wheel_hashes = wheels[0].get("hashes", {})
                    hash_data.update(first_wheel_hashes)

            if hash_data:
                extra_data["hashes"] = hash_data

            markers = package.get("marker")
            if markers:
                extra_data["markers"] = markers

            urls = get_pypi_urls(name, version)

            package_data = dict(
                datasource_id=cls.datasource_id,
                type=cls.default_package_type,
                primary_language="Python",
                name=name,
                version=version,
                is_virtual=True,
                dependencies=dependencies_for_resolved,
                extra_data=extra_data,
                download_url=download_url,
                **urls,
            )

            if "sha256" in hash_data:
                package_data["sha256"] = hash_data["sha256"]
            if "sha512" in hash_data:
                package_data["sha512"] = hash_data["sha512"]
            if "md5" in hash_data:
                package_data["md5"] = hash_data["md5"]

            resolved_package = models.PackageData.from_data(package_data, package_only)

            dependency = models.DependentPackage(
                purl=resolved_package.purl,
                extracted_requirement=version,
                scope="dependencies",
                is_runtime=True,
                is_optional=False,
                is_direct=False,
                is_pinned=True,
                resolved_package=resolved_package.to_dict(),
            )
            dependencies.append(dependency.to_dict())

        lockfile_extra_data = {}

        if lock_ver:
            lockfile_extra_data["lock_version"] = lock_ver

        req_python = toml_data.get("requires-python")
        if req_python:
            lockfile_extra_data["requires_python"] = req_python

        created_by = toml_data.get("created-by")
        if created_by:
            lockfile_extra_data["created_by"] = created_by

        root_package_data = dict(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            primary_language="Python",
            name="pylock-toml-project",
            version=None,
            extra_data=lockfile_extra_data,
            dependencies=dependencies,
        )

        yield models.PackageData.from_data(root_package_data, package_only)
