#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import json
from packagedcode import models
from packageurl import PackageURL
import yaml

class ComponentJSONMetadataHandler(models.NonAssemblableDatafileHandler):
    """
    Handle component JSON metadata files for package analysis.
    """
    datasource_id = "component_json_metadata"
    path_patterns = ("*component.json",)
    default_package_type = "library"
    description = "component JSON package metadata file"

    @classmethod
    def parse(cls, location, package_only=False):
        """
        Parse the JSON metadata file at `location` and yield PackageData.
        """
        with open(location, "r", encoding="utf-8") as f:
            data = json.load(f)

        name = data.get('name') or data.get('repo', '').split('/')[-1]
        if not name:
            return

        namespace = None
        if 'repo' in data and '/' in data['repo']:
            namespace, name = data['repo'].split('/', 1)
        
        package_data = dict(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            name=name,
            namespace=namespace,
            version=data.get('version'),
            description=data.get('description', ''),
            homepage_url=cls._extract_homepage(data),
            keywords=data.get('keywords', []),
            dependencies=cls._process_dependencies(data),
            extracted_license_statement=cls._extract_license_statement(data),
            extra_data=cls._extract_extra_data(data)
        )

        if namespace and name:
            package_data['purl'] = PackageURL(
                type='generic', 
                namespace=namespace, 
                name=name, 
                version=package_data.get('version')
            ).to_string()


        yield models.PackageData.from_data(package_data, package_only)

    @staticmethod
    def _extract_homepage(data):
        """
        Extract homepage URL from various possible sources.
        """
        if data.get('homepage'):
            return data['homepage']
        
        if data.get('repo'):
            return f'https://github.com/{data["repo"]}'
        
        desc = data.get('description', '')
        if 'http' in desc:
            urls = [word for word in desc.split() if word.startswith('http')]
            return urls[0] if urls else None
        
        return None

    @staticmethod
    def _process_dependencies(data):
        """
        Process dependencies into DependentPackage objects.
        """
        dependencies = []
        
        for dep_name, dep_version in data.get('dependencies', {}).items():
            try:
                if '/' in dep_name:
                    namespace, name = dep_name.split('/', 1)
                else:
                    namespace, name = None, dep_name
                
                purl = PackageURL(
                    type='generic', 
                    namespace=namespace, 
                    name=name, 
                    version=dep_version
                ).to_string()
                
                dependencies.append(
                    models.DependentPackage(
                        purl=purl,
                        scope='runtime',
                        is_runtime=True,
                        is_optional=False
                    )
                )
            except Exception:
                continue
        
        return dependencies

    @classmethod
    def _extract_license_statement(cls, data):
        """
        Extract license statement.

        """
        license_field = data.get('license')
        if not license_field:
            return None

        if isinstance(license_field, str):
            return yaml.dump({"type": license_field.strip()}).strip()
        
        if isinstance(license_field, list):
            license_statements = [
                yaml.dump({"type": lic.strip()}).strip() 
                for lic in license_field 
                if lic.strip()
            ]
            return "\n".join(license_statements) if license_statements else None
        
        return None

    @staticmethod
    def _extract_extra_data(data):
        """
        Extract additional metadata not in core package data.
        """
        extra_fields = [
            'main', 'scripts', 'styles', 'bin', 
            'repository', 'private', 'dev', 'development'
        ]
        
        return {
            field: data[field] 
            for field in extra_fields 
            if field in data
        }
