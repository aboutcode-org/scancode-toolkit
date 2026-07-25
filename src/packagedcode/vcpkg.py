# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import io
import re

from debian_inspector.debcon import get_paragraph_data_from_file
from packageurl import PackageURL

from packagedcode import models


class VcpkgControlHandler(models.DatafileHandler):
    """
    Parse a classic vcpkg CONTROL file, for example::

        Source: libgeotiff
        Version: 1.4.2-10
        Build-Depends: tiff, proj4, zlib
    """

    datasource_id = "vcpkg_control"
    path_patterns = ("*/CONTROL",)
    default_package_type = "vcpkg"
    default_primary_language = "C++"
    description = "vcpkg CONTROL manifest"
    documentation_url = "https://learn.microsoft.com/vcpkg/maintainers/control-files"

    @classmethod
    def parse(cls, location, package_only=False):
        # Feature stanzas describe optional variants. This handler reads only
        # the first stanza, which contains the source package metadata.
        control = get_paragraph_data_from_file(location=location) or {}
        version = control.get("version")
        port_version = control.get("port-version")
        qualifiers = {"port_version": port_version} if port_version else {}

        extra_data = {}
        if port_version:
            extra_data["port_version"] = port_version

        package_data = dict(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            primary_language=cls.default_primary_language,
            namespace=None,
            name=control.get("source"),
            version=version,
            qualifiers=qualifiers,
            homepage_url=control.get("homepage"),
            description=control.get("description"),
            extracted_license_statement=control.get("license"),
            dependencies=get_dependencies(control.get("build-depends")),
            extra_data=extra_data,
        )
        yield models.PackageData.from_data(package_data, package_only)


class VcpkgPortfileHandler(models.DatafileHandler):
    datasource_id = "vcpkg_portfile"
    path_patterns = ("*/portfile.cmake",)
    default_package_type = "vcpkg"
    default_primary_language = "C++"
    description = "vcpkg CMake portfile"
    documentation_url = "https://learn.microsoft.com/vcpkg/maintainers/ports"

    @classmethod
    def parse(cls, location, package_only=False):
        with io.open(location, encoding="utf-8") as portfile:
            content = portfile.read()

        source_data = get_source_data(content)
        package_data = dict(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            primary_language=cls.default_primary_language,
            namespace=None,
            version=source_data.get("version"),
            download_url=source_data.get("download_url"),
            vcs_url=source_data.get("vcs_url"),
            sha512=source_data.get("sha512"),
        )
        yield models.PackageData.from_data(package_data, package_only)


SOURCE_MACRO_PATTERN = re.compile(
    r"\b(?P<name>vcpkg_from_github|vcpkg_from_gitlab|vcpkg_from_git|"
    r"vcpkg_download_distfile)\s*\((?P<body>.*?)\)",
    re.IGNORECASE | re.DOTALL,
)


def get_dependencies(build_depends):
    dependencies = []
    for dependency in (build_depends or "").split(","):
        name = dependency.strip()
        if not name:
            continue
        purl = PackageURL(type="vcpkg", name=name)
        dependencies.append(
            models.DependentPackage(
                purl=purl.to_string(),
                scope="install",
                is_runtime=True,
                is_optional=False,
            )
        )
    return dependencies


def get_source_data(content):
    """
    Return literal source values from standard vcpkg download macros.
    """
    source_data = {}

    # Standard source macros are useful without evaluating CMake. Dynamic values
    # stay unset because their final value is unavailable in this file alone.
    for match in SOURCE_MACRO_PATTERN.finditer(content):
        macro = match.group("name").lower()
        body = match.group("body")
        reference = get_literal_argument(body, "REF")
        checksum = get_literal_argument(body, "SHA512")

        if reference and not source_data.get("version"):
            source_data["version"] = reference
        if checksum and not source_data.get("sha512"):
            source_data["sha512"] = checksum

        if macro == "vcpkg_from_github":
            repository = get_literal_argument(body, "REPO")
            if repository and not source_data.get("vcs_url"):
                source_data["vcs_url"] = f"https://github.com/{repository}"

        elif macro == "vcpkg_from_gitlab":
            repository = get_literal_argument(body, "REPO")
            gitlab_url = (
                get_literal_argument(body, "GITLAB_URL") or "https://gitlab.com"
            )
            if repository and not source_data.get("vcs_url"):
                source_data["vcs_url"] = (
                    f"{gitlab_url.rstrip('/')}/{repository.lstrip('/')}"
                )

        elif macro == "vcpkg_from_git":
            url = get_literal_argument(body, "URL")
            if url and not source_data.get("vcs_url"):
                source_data["vcs_url"] = url

        elif macro == "vcpkg_download_distfile":
            url = get_literal_argument(body, "URLS")
            if url and not source_data.get("download_url"):
                source_data["download_url"] = url

    return source_data


def get_literal_argument(body, name):
    match = re.search(
        rf"(?im)^[ \t]*{re.escape(name)}[ \t\r\n]+"
        r'(?:"(?P<quoted>[^"\r\n]*)"|(?P<bare>[^\s)#]+))',
        body,
    )
    if not match:
        return

    value = match.group("quoted") or match.group("bare")
    if "$" in value:
        return
    return value
