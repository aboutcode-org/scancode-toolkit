#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
#

import logging
import re

from packageurl import PackageURL

from packagedcode import models


logger = logging.getLogger(__name__)

ARCHITECTURE_FIELDS = {
    "checkdepends",
    "conflicts",
    "depends",
    "makedepends",
    "optdepends",
    "provides",
    "replaces",
    "source",
}
ARCHITECTURE_SUFFIX = re.compile(
    r"^(?P<field>[a-z][a-z0-9]*)_(?P<architecture>[a-z0-9][a-z0-9_]*)$"
)
DEPENDENCY_FIELDS = (
    ("depends", "depends", True, False),
    ("makedepends", "makedepends", False, False),
    ("checkdepends", "checkdepends", False, False),
    ("optdepends", "optdepends", True, True),
)


class SrcinfoHandler(models.DatafileHandler):
    """
    Parse Arch Linux makepkg ``.SRCINFO`` package metadata.
    """

    datasource_id = "arch_srcinfo"
    path_patterns = ("*.SRCINFO", "*/.SRCINFO")
    default_package_type = "arch"
    default_primary_language = None
    description = "Arch Linux .SRCINFO package metadata"
    documentation_url = "https://wiki.archlinux.org/title/.SRCINFO"

    @classmethod
    def parse(cls, location, package_only=False):
        with open(location, encoding="utf-8") as srcinfo_file:
            sections = cls._parse(srcinfo_file)

        if not sections:
            return

        base = sections[0]
        package_sections = sections[1:] or [base]
        for package_section in package_sections:
            data = dict(base)
            data.update(package_section)
            package_name = data.get("pkgname") or data.get("pkgbase")
            if not package_name:
                logger.warning("No package name found in .SRCINFO: %s", location)
                continue
            yield cls._to_package_data(data, package_only)

    @staticmethod
    def _add_value(section, key, value):
        existing = section.get(key)
        if existing is None:
            section[key] = value
        elif isinstance(existing, list):
            existing.append(value)
        else:
            section[key] = [existing, value]

    @classmethod
    def _parse(cls, file_object):
        base = None
        packages = []
        current = None

        for line_number, line in enumerate(file_object, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                logger.debug("Ignoring invalid .SRCINFO line %d: %s", line_number, line)
                continue

            key, value = (part.strip() for part in line.split("=", 1))
            if key == "pkgbase":
                base = {"pkgbase": value}
                current = base
                continue
            if current is None:
                logger.debug("Ignoring .SRCINFO field before pkgbase on line %d", line_number)
                continue
            if key == "pkgname":
                current = {"pkgbase": base.get("pkgbase"), "pkgname": value}
                packages.append(current)
                continue

            match = ARCHITECTURE_SUFFIX.match(key)
            if match and match.group("field") in ARCHITECTURE_FIELDS:
                key = match.group("field")
                value = (value, match.group("architecture"))
            SrcinfoHandler._add_value(current, key, value)

        if base is None:
            return []
        return [base, *packages]

    @classmethod
    def _to_package_data(cls, data, package_only):
        package_name = data.get("pkgname") or data["pkgbase"]
        version = data.get("pkgver")
        if data.get("pkgrel"):
            version = f"{version}-{data['pkgrel']}" if version else data["pkgrel"]
        if data.get("epoch"):
            version = f"{data['epoch']}:{version}" if version else data["epoch"]

        dependencies = []
        for field, scope, is_runtime, is_optional in DEPENDENCY_FIELDS:
            for requirement in cls._as_list(data.get(field)):
                architecture = None
                if isinstance(requirement, tuple):
                    requirement, architecture = requirement
                dependency_name = re.split(r"[<>=:]", requirement, maxsplit=1)[0].strip()
                if not dependency_name:
                    continue
                dependencies.append(
                    models.DependentPackage(
                        purl=PackageURL(type="arch", name=dependency_name).to_string(),
                        extracted_requirement=requirement,
                        scope=f"{scope}_{architecture}" if architecture else scope,
                        is_runtime=is_runtime,
                        is_optional=is_optional,
                    )
                )

        extra_data = {}
        for field in (
            "arch",
            "source",
            "md5sums",
            "sha1sums",
            "sha256sums",
            "sha512sums",
            "conflicts",
            "provides",
            "replaces",
        ):
            values = cls._as_list(data.get(field))
            if values:
                extra_data[field] = values

        extracted_license_statement = cls._join_values(data.get("license"))
        package_data = {
            "datasource_id": cls.datasource_id,
            "type": cls.default_package_type,
            "name": package_name,
            "version": version,
            "description": data.get("pkgdesc"),
            "homepage_url": data.get("url"),
            "extracted_license_statement": extracted_license_statement,
            "dependencies": dependencies,
            "extra_data": extra_data,
        }
        if extracted_license_statement and cls._is_custom_license(extracted_license_statement):
            package_data["declared_license_expression"] = "unknown-license-reference"
        return models.PackageData.from_data(package_data, package_only=package_only)

    @staticmethod
    def _as_list(value):
        if value is None:
            return []
        return value if isinstance(value, list) else [value]

    @staticmethod
    def _join_values(value):
        values = SrcinfoHandler._as_list(value)
        return " AND ".join(item if isinstance(item, str) else item[0] for item in values) or None

    @staticmethod
    def _is_custom_license(license_statement):
        return all(
            value.strip().lower().startswith("custom") for value in license_statement.split(" AND ")
        )
