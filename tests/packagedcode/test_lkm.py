import shutil
import os
from pathlib import Path
from xml.sax import handler

import pytest

from packagedcode import lkm
from packagedcode.models import DatafileHandler
from packagedcode.models import PackageData
from packagedcode.models import Party
from packagedcode.models import DependentPackage
from packagedcode import HANDLER_BY_DATASOURCE_ID


class TestLinuxKernelModule:

    test_data_dir = Path(__file__).resolve().parents[2] / "tests" / "licensedcode" / "data" / "query"

    def test_is_linux_kernel_module(self):
        test_file = self.test_data_dir / "eeepc_acpi.ko"

        assert lkm.LinuxKernelModuleHandler.is_datafile(
            str(test_file)
        )

    def test_extract_modinfo(self):
        test_file = self.test_data_dir / "eeepc_acpi.ko"

        metadata = lkm.LinuxKernelModuleHandler.extract_modinfo(
            str(test_file)
        )

        assert "license" in metadata
        assert "description" in metadata
        assert "author" in metadata

    def test_get_first(self):
        metadata = {
            "license": [
                "GPL",
                "MIT",
            ]
        }

        result = lkm.LinuxKernelModuleHandler.get_first(
            metadata,
            "license",
        )

        assert result == "GPL"

    def test_get_dependency_names(self):
        metadata = {
            "depends": [
                "usbcore,cfg80211,mac80211"
            ]
        }

        result = lkm.LinuxKernelModuleHandler.get_dependency_names(
            metadata
        )

        assert result == [
            "usbcore",
            "cfg80211",
            "mac80211",
        ]

    def test_get_dependency_names_handles_multiple_entries(self):
        metadata = {
            "depends": [
                "usbcore,cfg80211",
                "mac80211,netdev",
            ]
        }

        result = lkm.LinuxKernelModuleHandler.get_dependency_names(
            metadata
        )

        assert result == [
            "usbcore",
            "cfg80211",
            "mac80211",
            "netdev",
        ]

    def test_get_first_missing_optional_value_returns_none(self):
        metadata = {
            "license": [
                "GPL",
            ]
        }

        result = lkm.LinuxKernelModuleHandler.get_first(
            metadata,
            "version",
        )

        assert result is None

    def test_parse_elf_without_modinfo_section_returns_empty(self, tmp_path):
        if os.name == 'nt':
            pytest.skip("Test currently depends on the Unix /bin/ls ELF binary'")
        test_file = tmp_path / "no-modinfo.ko"
        shutil.copyfile("/bin/ls", test_file)

        package = list(
            lkm.LinuxKernelModuleHandler.parse(
                str(test_file)
            )
        )

        assert package == []
    
    def test_parse_invalid_lkm(self, tmp_path):
        test_file = tmp_path / "fake.ko"
        test_file.write_bytes(b"not an elf file")

        package = list(
            lkm.LinuxKernelModuleHandler.parse(
                str(test_file)
            )
        )

        assert package == []
    
    def test_parse_linux_kernel_module(self):
        test_file = self.test_data_dir / 'eeepc_acpi.ko'

        packages = list(
            lkm.LinuxKernelModuleHandler.parse(
                str(test_file)
            )
        )

        assert len(packages) == 1

        package = packages[0]

        assert package.datasource_id == 'linux_kernel_module'
        assert package.type == 'linux-kernel-module'
        assert package.name == 'eeepc_acpi'
        assert package.extracted_license_statement
        assert package.description
        assert package.parties
    
    def test_get_dependent_packages(self):
        metadata = {
            'depends': [
                'usbcore,cfg80211',
            ]
        }

        dependencies = (
            lkm.LinuxKernelModuleHandler.get_dependent_packages(metadata)
        )

        assert len(dependencies) == 2

        assert dependencies[0].purl == (
            'pkg:linux-kernel-module/usbcore'
        )
        assert dependencies[0].scope == 'runtime'
        assert dependencies[0].is_runtime is True
        assert dependencies[0].is_optional is False
        assert dependencies[0].extracted_requirement is None

        assert dependencies[1].purl == (
            'pkg:linux-kernel-module/cfg80211'
        )

    def test_build_package_data_includes_dependencies(self):
        metadata = {
            'license': ['GPL'],
            'depends': ['usbcore,cfg80211'],
        }

        package_data = (
            lkm.LinuxKernelModuleHandler.build_package_data(
                metadata=metadata,
                location='/tmp/example.ko',
            )
        )

        assert package_data.name == 'example'
        assert len(package_data.dependencies) == 2
        assert package_data.dependencies[0].purl == (
            'pkg:linux-kernel-module/usbcore'
        )
        assert package_data.dependencies[1].purl == (
            'pkg:linux-kernel-module/cfg80211'
        )

    def test_build_package_data_preserves_unknown_metadata(self):
        metadata = {
            'license': ['GPL'],
            'vermagic': ['6.8.0 SMP preempt mod_unload'],
            'srcversion': ['ABC123'],
            'firmware': ['example.bin'],
        }

        package_data = (
            lkm.LinuxKernelModuleHandler.build_package_data(
                metadata=metadata,
                location='/tmp/example.ko',
            )
        )

        assert package_data.extra_data["vermagic"] == [
            "6.8.0 SMP preempt mod_unload"
        ]

        assert package_data.extra_data["srcversion"] == [
            "ABC123"
        ]

        assert package_data.extra_data["firmware"] == [
            "example.bin"
        ]
    
    def test_build_package_data_handles_multiple_authors(self):
        metadata = {
            'author': [
                'Alice',
                'Bob',
            ],
        }

        package_data = (
            lkm.LinuxKernelModuleHandler.build_package_data(
                metadata=metadata,
                location='/tmp/example.ko',
            )
        )

        assert [party.name for party in package_data.parties] == [
            'Alice',
            'Bob',
        ]

    def test_datasource_id_is_registered(self):
        handler = HANDLER_BY_DATASOURCE_ID[
            lkm.LinuxKernelModuleHandler.datasource_id
        ]

        assert handler is lkm.LinuxKernelModuleHandler

    def test_build_package_data_multiple_alias_entries(self):
        metadata = {
            'license': ['GPL'],
            'alias': ['usbcore', 'cfg80211'],
        }

        package_data = lkm.LinuxKernelModuleHandler.build_package_data(
            metadata=metadata,
            location='/tmp/example.ko',
        )

        assert package_data.extra_data['alias'] == ['usbcore', 'cfg80211']
        assert 'depends' not in package_data.extra_data