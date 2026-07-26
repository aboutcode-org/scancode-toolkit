#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os

from typing import Dict
from typing import Iterator
from typing import List
from typing import Optional

from elftools.common.exceptions import ELFError
from elftools.elf.elffile import ELFFile
from packageurl import PackageURL

from packagedcode.models import DatafileHandler
from packagedcode.models import DependentPackage
from packagedcode.models import PackageData
from packagedcode.models import Party


class LinuxKernelModuleHandler(DatafileHandler):
    """
    Extract package metadata from compiled Linux Kernel Module ELF files.
    """
    datasource_id = 'linux_kernel_module'
    datasource_type = 'sys'
    supported_oses = ('linux',)
    default_package_type = 'linux-kernel-module'
    path_patterns = ('*.ko',)
    description = 'Linux Kernel Module'
    documentation_url = 'https://docs.kernel.org/kbuild/modules.html'

    @classmethod
    def parse(cls, location: str, package_only=False) -> Iterator[PackageData]:
        metadata = cls.extract_modinfo(location)
        
        if not metadata:
            return

        yield cls.build_package_data(
            metadata=metadata,
            location=location,
            package_only=package_only,
        )
    

    @staticmethod
    def extract_modinfo(location: str) -> Dict[str, List[str]]:
        """
        Return .modinfo metadata as a mapping of keys to lists of values.

        Multiple values are preserved because fields such as 'author', 'alias',
        and 'firmware' may appear more than once.
        """

        metadata: Dict[str, List[str]] = {}

        try:
            with open(location, 'rb') as module_file:
                elf_file = ELFFile(module_file)

                # Restrict parsing to .modinfo instead of searching arbitrary binary data.
                modinfo_section = elf_file.get_section_by_name('.modinfo')
                if modinfo_section is None:
                    return {}

                # Read only the raw bytes stored in the ELF .modinfo section.
                raw_bytes = modinfo_section.data()

        except (ELFError, OSError):
            return {}
        
        # Entries in .modinfo are NUL-terminated key=value strings.
        for raw_entry in raw_bytes.split(b'\x00'):
            if not raw_entry:
                continue

            entry = raw_entry.decode('utf-8', errors='replace')

            if '=' not in entry:
                continue

            key, value = entry.split('=', 1)

            if not key:
                continue

            metadata.setdefault(key, []).append(value)

        return metadata
    
    @staticmethod
    def get_first(metadata: Dict[str, List[str]], key: str) -> Optional[str]:
        values = metadata.get(key) or []
        return values[0] if values else None
    
    @staticmethod
    def get_dependency_names(
        metadata: Dict[str, List[str]]
    ) -> List[str]:
        dependencies = []

        # The depends field lists modules required when this module is loaded.
        for depends_entry in metadata.get('depends', []):
            dependencies.extend(
                dependency.strip()
                for dependency in depends_entry.split(',')
                if dependency.strip()
            )

        return dependencies
    
    @classmethod
    def get_dependent_packages(
        cls,
        metadata: Dict[str, List[str]],
    ) -> List[DependentPackage]:
        dependency_names = cls.get_dependency_names(metadata)

        return [
            DependentPackage(
                purl=PackageURL(
                    type=cls.default_package_type,
                    name=dependency_name,
                ).to_string(),
                extracted_requirement=None,
                scope='runtime',
                is_runtime=True,
                is_optional=False,
            )
            for dependency_name in dependency_names
        ]

    @classmethod
    def build_package_data(
        cls,
        metadata: Dict[str, List[str]],
        location: str,
        package_only: bool = False,
    ) -> PackageData:
        """
        Return PackageData built from raw .modinfo metadata.
        """

        # Represent every declared author as a package party.
        parties = []
        for author in metadata.get('author', []):
            author = author.strip()

            if author:
                parties.append(
                    Party(
                        type='person',
                        role='author',
                        name=author,
                    )
                )

        filename = os.path.basename(location)
        name = filename[:-3] if filename.endswith('.ko') else filename

        normalized_keys = {
            'author',
            'description',
            'license',
            'version',
            'depends',
        }

        #Preserve additional metadata that is not mapped to PackageData fields.
        extra_data = {
            key: values
            for key, values in metadata.items()
            if key not in normalized_keys
        }

        # PackageData stores only the first value for these normalized fields.
        # Preserve all values in extra_data when a field occurs more than once.
        for key in ('description', 'license', 'version'):
            values = metadata.get(key, [])
            if len(values) > 1:
                extra_data[key] = values

        dependencies = cls.get_dependent_packages(metadata)

        package_data = dict(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            name=name,
            version=cls.get_first(metadata, 'version'),
            description=cls.get_first(metadata, 'description'),
            extracted_license_statement=cls.get_first(metadata, 'license'),
            parties=parties,
            dependencies=dependencies,
            extra_data=extra_data,
        )

        return PackageData.from_data(
            package_data=package_data,
            package_only=package_only,
        )
    