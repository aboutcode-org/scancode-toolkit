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
from packagedcode.pypi import BaseExtractedPythonLayout
from packagedcode.pypi import get_pypi_urls

# tomli was added to the stdlib as tomllib in Python 3.11.
# It's the same code.
# Still, prefer tomli if it's installed, as on newer Python versions, it is
# compiled with mypyc and is more performant.
try:
    import tomli as tomllib
except ImportError:
    import tomllib

"""
Detect and collect Python pylock.toml lockfile information.
Support for PEP 751: A file format to record Python dependencies for installation reproducibility.
See https://peps.python.org/pep-0751/
"""

TRACE = os.environ.get('SCANCODE_DEBUG_PACKAGE', False)


def logger_debug(*args):
    pass


logger = logging.getLogger(__name__)

if TRACE:
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, str) and a or repr(a) for a in args))


class PylockTomlHandler(BaseExtractedPythonLayout):
    datasource_id = 'pypi_pylock_toml'
    path_patterns = ('*pylock.toml',)
    default_package_type = 'pypi'
    default_primary_language = 'Python'
    description = 'Python pylock.toml lockfile (PEP 751)'
    documentation_url = 'https://peps.python.org/pep-0751/'

    @classmethod
    def parse(cls, location, package_only=False):
        """
        Parse a pylock.toml file and yield PackageData with dependencies.
        """
        with open(location, "rb") as fp:
            toml_data = tomllib.load(fp)

        metadata = toml_data.get('metadata', {})
        packages = toml_data.get('package', [])
        if not packages:
            return

        dependencies = []
        
        for package in packages:
            name = package.get('name')
            version = package.get('version')
            
            if not name or not version:
                continue

            dependencies_for_resolved = []
            
            pkg_dependencies = package.get('dependencies', [])
            for dep in pkg_dependencies:
                if isinstance(dep, str):
                    dep_name = dep.split('==')[0].split('>=')[0].split('<=')[0].split('>')[0].split('<')[0].strip()
                    dep_requirement = dep
                elif isinstance(dep, dict):
                    dep_name = dep.get('name')
                    dep_requirement = dep.get('version')
                else:
                    continue
                
                if not dep_name:
                    continue
                
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

            source = package.get('source', {})
            source_url = source.get('url') if isinstance(source, dict) else None
            
            hashes = package.get('hashes', [])
            hash_data = {}
            if hashes:
                for hash_entry in hashes:
                    if isinstance(hash_entry, str):
                        if ':' in hash_entry:
                            algo, value = hash_entry.split(':', 1)
                            hash_data[algo] = value
                    elif isinstance(hash_entry, dict):
                        hash_data.update(hash_entry)
            
            extra_data = {}
            if source_url:
                extra_data['source_url'] = source_url
            if hash_data:
                extra_data['hashes'] = hash_data
            
            markers = package.get('markers')
            if markers:
                extra_data['markers'] = markers
            
            urls = get_pypi_urls(name, version)
            
            package_data = dict(
                datasource_id=cls.datasource_id,
                type=cls.default_package_type,
                primary_language='Python',
                name=name,
                version=version,
                is_virtual=True,
                dependencies=dependencies_for_resolved,
                extra_data=extra_data,
                **urls,
            )
            
            if 'sha256' in hash_data:
                package_data['sha256'] = hash_data['sha256']
            if 'sha384' in hash_data:
                extra_data['sha384'] = hash_data['sha384']
            if 'sha512' in hash_data:
                package_data['sha512'] = hash_data['sha512']
            
            resolved_package = models.PackageData.from_data(package_data, package_only)
            groups = package.get('groups', [])
            is_optional = 'dev' in groups or 'optional' in groups if groups else False
            
            dependency = models.DependentPackage(
                purl=resolved_package.purl,
                extracted_requirement=version,
                scope='dependencies' if not is_optional else 'dev-dependencies',
                is_runtime=not is_optional,
                is_optional=is_optional,
                is_direct=False,
                is_pinned=True,
                resolved_package=resolved_package.to_dict()
            )
            dependencies.append(dependency.to_dict())

        lockfile_extra_data = {}
        
        if 'version' in metadata:
            lockfile_extra_data['lock_version'] = metadata['version']
        if 'requires-python' in metadata:
            lockfile_extra_data['requires_python'] = metadata['requires-python']
        if 'resolution-mode' in metadata:
            lockfile_extra_data['resolution_mode'] = metadata['resolution-mode']
        
        package_data = dict(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            primary_language='Python',
            extra_data=lockfile_extra_data,
            dependencies=dependencies,
        )
        
        yield models.PackageData.from_data(package_data, package_only)
