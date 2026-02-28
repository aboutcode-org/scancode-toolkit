#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import io
import json

from packageurl import PackageURL

from packagedcode import models

"""
Support for Gradle module metadata (.module) files.

Gradle module metadata is a JSON file format used by Gradle to describe
a published module's variants, dependencies, and artifact files.

Specification:
https://github.com/gradle/gradle/blob/master/subprojects/docs/src/docs/design/gradle-module-metadata-latest-specification.md
"""


class GradleModuleHandler(models.DatafileHandler):
    datasource_id = 'gradle_module'
    path_patterns = ('*.module',)
    default_package_type = 'maven'
    default_primary_language = 'Java'
    description = 'Gradle module metadata'
    documentation_url = (
        'https://github.com/gradle/gradle/blob/master/subprojects/docs/src/docs/'
        'design/gradle-module-metadata-latest-specification.md'
    )

    @classmethod
    def is_datafile(cls, location, filetypes=tuple(), _bare_filename=False):
        """
        Return True only for .module files that contain valid Gradle module
        metadata, identified by the presence of 'formatVersion' and 'component'
        top-level keys.
        """
        if not super().is_datafile(location, filetypes=filetypes):
            return False
        if _bare_filename:
            return True
        try:
            with io.open(location, encoding='utf-8') as f:
                data = json.load(f)
            return 'formatVersion' in data and 'component' in data
        except Exception:
            return False

    @classmethod
    def parse(cls, location, package_only=False):
        with io.open(location, encoding='utf-8') as f:
            data = json.load(f)

        component = data.get('component') or {}
        group = component.get('group')
        module = component.get('module')
        version = component.get('version')

        # Collect dependencies from all non-documentation variants,
        # deduplicating by (group, module) key.
        seen_deps = set()
        dependencies = []
        for variant in (data.get('variants') or []):
            attributes = variant.get('attributes') or {}
            # Skip documentation variants (sources, javadoc, etc.)
            if attributes.get('org.gradle.category') == 'documentation':
                continue

            scope = _get_scope_from_variant(variant)
            is_optional = scope == 'test'
            is_runtime = scope != 'test'

            for dep in (variant.get('dependencies') or []):
                dep_group = dep.get('group', '')
                dep_module = dep.get('module', '')
                dep_key = (dep_group, dep_module)
                if dep_key in seen_deps:
                    continue
                seen_deps.add(dep_key)

                dep_version_data = dep.get('version') or {}
                dep_version = (
                    dep_version_data.get('requires')
                    or dep_version_data.get('prefers')
                    or dep_version_data.get('strictly')
                    or None
                )

                dep_purl = PackageURL(
                    type='maven',
                    namespace=dep_group or None,
                    name=dep_module,
                    version=dep_version,
                ).to_string()

                dependencies.append(
                    models.DependentPackage(
                        purl=dep_purl,
                        scope=scope,
                        extracted_requirement=dep_version,
                        is_runtime=is_runtime,
                        is_optional=is_optional,
                        is_pinned=bool(dep_version),
                    )
                )

        # Extract checksums and size from the first primary (non-documentation)
        # variant's file entry.
        sha1 = None
        md5 = None
        sha256 = None
        sha512 = None
        size = None

        for variant in (data.get('variants') or []):
            attributes = variant.get('attributes') or {}
            if attributes.get('org.gradle.category') == 'documentation':
                continue
            files = variant.get('files') or []
            if files:
                primary_file = files[0]
                sha1 = primary_file.get('sha1')
                md5 = primary_file.get('md5')
                sha256 = primary_file.get('sha256')
                sha512 = primary_file.get('sha512')
                size = primary_file.get('size')
                break

        package_data = dict(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            namespace=group,
            name=module,
            version=version,
            primary_language=cls.default_primary_language,
            sha1=sha1,
            md5=md5,
            sha256=sha256,
            sha512=sha512,
            size=size,
            dependencies=dependencies,
        )
        yield models.PackageData.from_data(package_data, package_only)


def _get_scope_from_variant(variant):
    """
    Return a scope string ('compile', 'runtime', or 'test') for a Gradle
    module variant, using the org.gradle.usage attribute when available and
    falling back to the variant name.
    """
    variant_name = variant.get('name', '').lower()
    attributes = variant.get('attributes') or {}
    usage = attributes.get('org.gradle.usage', '')

    if 'test' in variant_name:
        return 'test'
    if usage == 'java-api' or ('api' in variant_name and 'runtime' not in variant_name):
        return 'compile'
    if usage == 'java-runtime' or 'runtime' in variant_name:
        return 'runtime'
    return 'compile'
