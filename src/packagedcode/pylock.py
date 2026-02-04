#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import logging
try:
    import tomllib
except ImportError:
    # Fallback for Python < 3.11
    import tomli as tomllib

from packagedcode import models
from packaging.utils import canonicalize_name
from packageurl import PackageURL

logger = logging.getLogger(__name__)


class PyLockHandler(models.DatafileHandler):
    """
    Handler for PEP 751 pylock.toml lockfiles.
    
    PyLock is a standardized lockfile format for Python packages defined in PEP 751.
    It provides a machine-readable record of the exact package versions and metadata
    used in a Python environment.
    See https://peps.python.org/pep-0751/
    """

    datasource_id = 'pylock'
    path_patterns = ('*/pylock.toml',)
    default_package_type = 'pypi'
    default_primary_language = 'Python'
    is_lockfile = True
    description = 'Python pylock.toml lockfile (PEP 751)'
    documentation_url = 'https://peps.python.org/pep-0751/'

    @classmethod
    def parse(cls, location, package_only=False):
        """
        Parse a pylock.toml file and extract package information.
        
        Returns a generator of Package objects representing the packages
        listed in the lockfile.
        """
        try:
            with open(location, 'rb') as f:
                data = tomllib.load(f)
        except (OSError, tomllib.TOMLDecodeError) as e:
            logger.warning(
                'Failed to parse pylock.toml at %r: %s',
                location,
                e,
            )
            return
            
        # Validate PEP 751 requirement - 'lock-version' is required
        if 'lock-version' not in data:
            logger.warning(
                'Missing required lock-version in pylock.toml at %r',
                location,
            )
            return

        packages = data.get('packages', [])
        if not packages:
            logger.debug(
                'No packages found in pylock.toml at %r',
                location,
            )
            return

        dependencies = []
        if not package_only:
            for pkg in packages:
                if not isinstance(pkg, dict):
                    continue
                    
                raw_name = pkg.get('name')
                version = pkg.get('version')

                # Required fields validation
                if not raw_name or not version:
                    logger.debug(
                        'Skipping package with missing name or version in %r',
                        location,
                    )
                    continue

                name = canonicalize_name(raw_name)

                purl = PackageURL(
                    type='pypi',
                    name=name,
                    version=version,
                ).to_string()

                # Extract optional dependency metadata
                dep_extra_data = {}
                if 'marker' in pkg:
                    dep_extra_data['marker'] = pkg['marker']
                if 'requires-python' in pkg:
                    dep_extra_data['requires_python'] = pkg['requires-python']
                
                # Check if dependency is optional based on marker
                is_optional = 'marker' in pkg and 'extra' in pkg.get('marker', '')

                dependencies.append(
                    models.DependentPackage(
                        purl=purl,
                        extracted_requirement=version,
                        scope='runtime',
                        is_runtime=True,
                        is_optional=is_optional,
                        is_pinned=True,
                        extra_data=dep_extra_data,
                    )
                )

        package_data = dict(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            name='python-environment',
            version=None,
            primary_language=cls.default_primary_language,
            dependencies=dependencies,
            is_virtual=True,
            extra_data={
                'lock_version': data.get('lock-version'),
                'package_count': len(packages),
                'created_by': data.get('created-by'),
                'requires_python': data.get('requires-python'),
                'environments': data.get('environments'),
                'dependency_groups': data.get('dependency-groups'),
                'default_groups': data.get('default-groups'),
            }
        )

        yield models.PackageData(**package_data)
