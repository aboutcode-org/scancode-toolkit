#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import toml
from packagedcode import models
from packageurl import PackageURL
import yaml

class BuildpackHandler(models.NonAssemblableDatafileHandler):
    """
    Handle buildpack.toml manifests.
    See https://buildpacks.io/ for details on buildpack format.
    """
    datasource_id = "buildpack_toml"
    path_patterns = ("*buildpack.toml",)
    default_package_type = "generic"
    description = "Cloud Native Buildpack manifest"
    documentation_url = "https://buildpacks.io/"

    @classmethod
    def parse(cls, location, package_only=False):
        """
        Parse the buildpack.toml file at `location` and yield PackageData.
        """
        with open(location, "r", encoding="utf-8") as f:
            data = toml.load(f)

        api_version = data.get("api")
        buildpack = data.get("buildpack", {})
        if not buildpack:
            return

        buildpack_id = buildpack.get("id")
        name = buildpack.get("name")

        if buildpack_id:
            namespace, name = buildpack_id.split("/", 1)
        
        # Initialize common package data
        package_data = dict(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            name=name,
            version=buildpack.get("version"),
            description=buildpack.get("description"),
            homepage_url=buildpack.get("homepage"),
            keywords=buildpack.get("keywords", []),
            extracted_license_statement=None,
            dependencies=[],
            extra_data={}
        )

        if api_version:
            package_data["extra_data"]["api_version"] = api_version

        # Handle Paketo-specific fields if present
        if "api" in data:
            cls.handle_paketo_buildpack(data, buildpack, package_data)

        # Handle Heroku-specific fields if present
        elif "publish" in data and "Ignore" in data["publish"]:
            cls.handle_heroku_buildpack(data, buildpack, package_data)

        yield models.PackageData.from_data(package_data, package_only)

    @staticmethod
    def handle_paketo_buildpack(data, buildpack, package_data):
        buildpack_id = buildpack.get("id")
        if buildpack_id:
            package_data["extra_data"]["id"] = buildpack_id

        package_data.update({
            "version": buildpack.get("version"),
            "description": buildpack.get("description"),
            "homepage_url": buildpack.get("homepage"),
            "keywords": buildpack.get("keywords", []),
        })

        licenses = buildpack.get("licenses", [])
        if licenses:
            license_statements = [
                yaml.dump({"type": license_entry.get("type")}).strip() 
                for license_entry in licenses
                if license_entry.get("type")  
            ]
            package_data["extracted_license_statement"] = "\n".join(license_statements)


        dependencies = []
        metadata = data.get("metadata", {})
        metadata_dependencies = metadata.get("dependencies", [])
        for dep in metadata_dependencies:
            dep_purl = dep.get("purl")
            dep_name = dep.get("name")
            dep_version = dep.get("version")
            dep_cpes = dep.get("cpes", [])
            extra_data = {"cpes": dep_cpes} if dep_cpes else {}

            if not dep_purl and dep_name and dep_version:
                dep_purl = PackageURL(type="generic", name=dep_name, version=dep_version).to_string()

            if dep_purl:
                dependencies.append(
                    models.DependentPackage(
                        purl=dep_purl,
                        scope="runtime",
                        is_runtime=True,
                        is_optional=False,
                        extra_data=extra_data,
                    )
                )

        orders = data.get("order", [])
        for order in orders:
            for group in order.get("group", []):
                group_id = group.get("id")
                group_version = group.get("version")
                if group_id and group_version:
                    dependencies.append(
                        models.DependentPackage(
                            purl=PackageURL(type="buildpack", name=group_id, version=group_version).to_string(),
                            scope="runtime",
                            is_runtime=True,
                            is_optional=group.get("optional", False),
                        )
                    )

        package_data["dependencies"] = dependencies

        targets = data.get("targets", [])
        if targets:
            package_data["extra_data"]["targets"] = targets

    @staticmethod
    def handle_heroku_buildpack(data, buildpack, package_data):
        publish_section = data.get("publish", {})
        if "Ignore" in publish_section:
            ignore_files = publish_section["Ignore"].get("files", [])
            if ignore_files:  
                package_data["extra_data"]["ignore_files"] = ignore_files
            else:
                package_data["extra_data"]["ignore_files"] = []
        else:
            package_data["extra_data"]["ignore_files"] = []

        package_data["description"] = f"Heroku buildpack for {buildpack.get('name')}"
