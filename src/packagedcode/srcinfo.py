#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/aboutcode-org/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import logging
import re

from packagedcode import models
from packageurl import PackageURL

"""
See: https://wiki.archlinux.org/title/.SRCINFO
"""

logger = logging.getLogger(__name__)


class SrcinfoHandler(models.DatafileHandler):
    
    datasource_id = 'arch_srcinfo'
    path_patterns = ('*/.SRCINFO', '*.SRCINFO')
    default_package_type = 'arch'
    default_primary_language = None  # Can be any language
    description = 'Arch Linux .SRCINFO file'
    documentation_url = 'https://wiki.archlinux.org/title/.SRCINFO'

    @classmethod
    def parse(cls, location):
        with open(location, 'r', encoding='utf-8') as f:
            content = f.read()

        srcinfo_data = cls._parse_srcinfo(content)
        
        if not srcinfo_data:
            return

        pkgbase_data = srcinfo_data.get('pkgbase', {})
        
        packages = srcinfo_data.get('packages', [])
        
        if not packages:
            packages = [pkgbase_data.copy()]

        for pkg_data in packages:
            merged_data = pkgbase_data.copy()
            merged_data.update(pkg_data)
            
            package = cls._create_package_from_data(merged_data)
            if package:
                yield package

    @classmethod
    def _parse_srcinfo(cls, content):
        lines = content.splitlines()
        
        pkgbase_data = {}
        packages = []
        current_section = pkgbase_data
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            if not line or line.startswith('#'):
                continue
            
            if '=' not in line:
                logger.debug(f'Line {line_num}: No = found, skipping: {line}')
                continue
            
            key, _, value = line.partition('=')
            key = key.strip()
            value = value.strip()
            
            if key == 'pkgbase':
                pkgbase_data['pkgbase'] = value
                current_section = pkgbase_data
                continue
            elif key == 'pkgname':
                pkg = {'pkgname': value}
                packages.append(pkg)
                current_section = pkg
                continue
            
            arch_match = re.match(r'(.+)_([^_]+)$', key)
            if arch_match:
                base_key = arch_match.group(1)
                arch = arch_match.group(2)
                if base_key not in current_section:
                    current_section[base_key] = []
                elif not isinstance(current_section[base_key], list):
                   current_section[base_key] = [current_section[base_key]]
                current_section[base_key].append((value, arch))
            else:
                if key in current_section:
                    if not isinstance(current_section[key], list):
                        current_section[key] = [current_section[key]]
                    current_section[key].append(value)
                else:
                    current_section[key] = value
        
        return {
            'pkgbase': pkgbase_data,
            'packages': packages if packages else [pkgbase_data]
        }

    @classmethod
    def _create_package_from_data(cls, data):
        pkgname = data.get('pkgname')
        if not pkgname:
            pkgname = data.get('pkgbase')
        
        if not pkgname:
            return None
        
        pkgver = data.get('pkgver', '')
        pkgrel = data.get('pkgrel', '')
        
        if pkgver and pkgrel:
            version = f'{pkgver}-{pkgrel}'
        elif pkgver:
            version = pkgver
        else:
            version = None
        
        purl = PackageURL(
            type='arch',
            name=pkgname,
            version=version
        ).to_string()
        
        description = data.get('pkgdesc', '')
        homepage_url = data.get('url')
        
        declared_license_expression = None
        licenses = data.get('license')
        if licenses:
            if isinstance(licenses, list):
                declared_license_expression = ' AND '.join(licenses)
            else:
                declared_license_expression = licenses

        arch = data.get('arch')
        if arch:
            if isinstance(arch, list):
                arch = ', '.join(arch)
        
        dependencies = []
        
        depends = data.get('depends', [])
        if not isinstance(depends, list):
            depends = [depends]
        
        for dep in depends:
            if isinstance(dep, tuple):
                dep_name, dep_arch = dep
                dependencies.append(
                    models.DependentPackage(
                        purl=PackageURL(type='arch', name=dep_name.split('>')[0].split('<')[0].split('=')[0].strip()).to_string(),
                        extracted_requirement=dep_name,
                        scope=f'depends_{dep_arch}',
                        is_runtime=True,
                        is_optional=False
                    )
                )
            else:
                dependencies.append(
                    models.DependentPackage(
                        purl=PackageURL(type='arch', name=dep.split('>')[0].split('<')[0].split('=')[0].strip()).to_string(),
                        extracted_requirement=dep,
                        scope='depends',
                        is_runtime=True,
                        is_optional=False
                    )
                )
        
        makedepends = data.get('makedepends', [])
        if not isinstance(makedepends, list):
            makedepends = [makedepends]
        
        for dep in makedepends:
            if isinstance(dep, tuple):
                dep_name, dep_arch = dep
                dependencies.append(
                    models.DependentPackage(
                        purl=PackageURL(type='arch', name=dep_name.split('>')[0].split('<')[0].split('=')[0].strip()).to_string(),
                        extracted_requirement=dep_name,
                        scope=f'makedepends_{dep_arch}',
                        is_runtime=False,
                        is_optional=False
                    )
                )
            else:
                dependencies.append(
                    models.DependentPackage(
                        purl=PackageURL(type='arch', name=dep.split('>')[0].split('<')[0].split('=')[0].strip()).to_string(),
                        extracted_requirement=dep,
                        scope='makedepends',
                        is_runtime=False,
                        is_optional=False
                    )
                )
        
        optdepends = data.get('optdepends', [])
        if not isinstance(optdepends, list):
            optdepends = [optdepends]
        
        for dep in optdepends:
            if isinstance(dep, tuple):
                dep_name, dep_arch = dep
                pkg_part = dep_name.split(':')[0].strip()
                dependencies.append(
                    models.DependentPackage(
                        purl=PackageURL(type='arch', name=pkg_part).to_string(),
                        extracted_requirement=dep_name,
                        scope=f'optdepends_{dep_arch}',
                        is_runtime=True,
                        is_optional=True
                    )
                )
            else:
                pkg_part = dep.split(':')[0].strip()
                dependencies.append(
                    models.DependentPackage(
                        purl=PackageURL(type='arch', name=pkg_part).to_string(),
                        extracted_requirement=dep,
                        scope='optdepends',
                        is_runtime=True,
                        is_optional=True
                    )
                )
        
        package_data = dict(
        datasource_id=cls.datasource_id,
        type=cls.default_package_type,
        name=pkgname,
        version=version,
        description=description,
        homepage_url=homepage_url,
        declared_license_expression=declared_license_expression,
        dependencies=dependencies,
        purl=purl,
     )
     
        
        extra_data = {}
        
        if arch:
            extra_data['arch'] = arch
        
        source = data.get('source')
        if source:
            extra_data['source'] = source if isinstance(source, list) else [source]
        
        for checksum_type in ['md5sums', 'sha1sums', 'sha256sums', 'sha512sums']:
            if checksum_type in data:
                checksums = data[checksum_type]
                extra_data[checksum_type] = checksums if isinstance(checksums, list) else [checksums]
        
        if 'epoch' in data:
            extra_data['epoch'] = data['epoch']
        
        for key in ['conflicts', 'provides', 'replaces']:
            if key in data:
                values = data[key]
                extra_data[key] = values if isinstance(values, list) else [values]
        
        if extra_data:
            package_data['extra_data'] = extra_data
        
        return models.PackageData.from_data(package_data, package_only=False)
