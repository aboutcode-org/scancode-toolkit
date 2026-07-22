import re
from typing import Iterator, Dict, Any, List, Optional
from packagedcode.models import DatafileHandler, PackageData, DependentPackage, Party
import os

from elftools.common.exceptions import ELFError
from elftools.elf.elffile import ELFFile


# Inside ScanCode, we would import the official classes:
# from packagedcode.models import Package, Party, Dependency
# from packagedcode import DatafileHandler

class LinuxKernelModuleHandler(DatafileHandler):
    """
    DatafileHandler for compiled Linux Kernel Modules (.ko binaries).
    Extracts the .modinfo section and maps it to ScanCode's standard PackageData.
    """

    datasource_id = 'linux_kernel_module'
    datasource_type = 'sys'
    supported_oses = ('linux',)
    default_package_type = 'linux-kernel-module'
    path_patterns = ('*.ko',)
    description = 'Linux Kernel Module'
    documentation_url = "https://docs.kernel.org/kbuild/modules.html"

    @classmethod
    def parse(cls, location: str, package_only=False) -> Iterator[PackageData]:
        #Main entry point called by ScanCode when scanning directories.
        raw_metadata = cls.extract_modinfo(location)
        if not raw_metadata:
            return

        #Ensures no empty or invalid package data is yielded

        yield cls.build_package(
        metadata=raw_metadata,
        location=location,
        package_only=package_only,
        )
    

    @staticmethod
    def extract_modinfo(location: str) -> Dict[str, List[str]]:
        """
        Reads the .modinfo byte section from the ELF file in-memory.
        Uses pyelftools (which is already a ScanCode dependency).
        """

        metadata: Dict[str, List[str]] = {}

        try:
            with open(location, 'rb') as module_file:
                elffile = ELFFile(module_file)

                # Locate the specific .modinfo section in the ELF structure
                modinfo_sec = elffile.get_section_by_name('.modinfo')
                if modinfo_sec is None:
                    return {}

                # Extract the raw binary block
                raw_bytes = modinfo_sec.data()

        except (ELFError, OSError):
            return {}
            # Split null-terminated bytes on \x00
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
    def get_dependencies(metadata: Dict[str, List[str]]) -> List[str]:
        dependencies = []

        for depends_entry in metadata.get('depends', []):
            dependencies.extend(
                dependency.strip()
                for dependency in depends_entry.split(',')
                if dependency.strip()
            )

        return dependencies

    @classmethod
    def build_package(cls, metadata: Dict[str, Any], location: str, package_only: bool = False) -> PackageData:
        """
        Maps raw .modinfo dictionary keys into ScanCode's standard PackageData models.
        """
        # 1. Map Authors to standard 'Party' objects

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
        }

        extra_data = {
            key: values
            for key, values in metadata.items()
            if key not in normalized_keys
        }

        dependency_names = cls.get_dependency_names(metadata)

        if dependency_names:
            extra_data['depends'] = dependency_names

        package_data = dict(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            name=name,
            version=cls.get_first(metadata, 'version'),
            description=cls.get_first(metadata, 'description'),
            extracted_license_statement=cls.get_first(metadata,'license'),
            parties=parties,
            extra_data=extra_data,
        )

        return PackageData.from_data(
            package_data=package_data,
            package_only=package_only,
        )
    