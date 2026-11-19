#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import json

from packageurl import PackageURL

from packagedcode import models


class GradleModuleHandler(models.DatafileHandler):
    datasource_id = 'gradle_module'
    path_patterns = ('*.module',)
    default_package_type = 'maven'
    description = 'Gradle module metadata file'

    @classmethod
    def is_datafile(cls, location, filetypes=tuple()):
        if super().is_datafile(location, filetypes=filetypes):
            return True
        return str(location).endswith('.module')

    @classmethod
    def parse(cls, location, package_only=False):
        try:
            with open(location, 'r') as f:
                data = json.load(f)
        except Exception:
            return

        if not data or not isinstance(data, dict):
            return

        component = data.get('component', {})
        if not component:
            return

        namespace = component.get('group', '')
        name = component.get('module', '')
        version = component.get('version', '')

        created_by = data.get('createdBy', {})
        gradle_version = created_by.get('gradle', {}).get('version')

        variants = data.get('variants', [])
        seen_deps = {}
        files = []

        for variant in variants:
            variant_name = variant.get('name', '')
            attributes = variant.get('attributes', {})
            usage = attributes.get('org.gradle.usage', variant_name)

            is_runtime = 'runtime' in usage.lower()
            scope = 'runtime' if is_runtime else 'api'

            for dep in variant.get('dependencies', []):
                dep_namespace = dep.get('group', '')
                dep_name = dep.get('module', '')
                dep_version_info = dep.get('version', {})

                if isinstance(dep_version_info, dict):
                    dep_version = dep_version_info.get('requires') or \
                                  dep_version_info.get('prefers') or \
                                  dep_version_info.get('strictly', '')
                else:
                    dep_version = str(dep_version_info) if dep_version_info else ''

                key = (dep_namespace, dep_name, dep_version)
                if key not in seen_deps:
                    seen_deps[key] = models.DependentPackage(
                        purl=str(PackageURL(
                            type='maven',
                            namespace=dep_namespace,
                            name=dep_name,
                            version=dep_version
                        )),
                        extracted_requirement=dep_version,
                        scope=scope,
                        is_runtime=is_runtime,
                        is_optional=False,
                    )

            # Extract files from the first variant that has them
            if not files and variant.get('files'):
                files = variant.get('files', [])

        extra_data = {}
        if gradle_version:
            extra_data['gradle_version'] = gradle_version
        format_version = data.get('formatVersion')
        if format_version:
            extra_data['format_version'] = format_version

        package_data = dict(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            namespace=namespace,
            name=name,
            version=version,
            dependencies=list(seen_deps.values()),
            extra_data=extra_data,
        )

        # Store file checksums on the PackageData if available from the first variant files
        for f in files:
            for algo in ('sha1', 'sha256', 'sha512', 'md5'):
                if f.get(algo):
                    package_data[algo] = f.get(algo)
            break

        yield models.PackageData.from_data(package_data, package_only)
