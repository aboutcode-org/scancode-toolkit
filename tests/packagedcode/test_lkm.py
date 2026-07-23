import shutil
from pathlib import Path

from packagedcode import lkm


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

    def test_get_dependencies(self):
        metadata = {
            "depends": [
                "usbcore,cfg80211,mac80211"
            ]
        }

        result = lkm.LinuxKernelModuleHandler.get_dependencies(
            metadata
        )

        assert result == [
            "usbcore",
            "cfg80211",
            "mac80211",
        ]

    def test_get_dependencies_handles_multiple_entries(self):
        metadata = {
            "depends": [
                "usbcore,cfg80211",
                "mac80211,netdev",
            ]
        }

        result = lkm.LinuxKernelModuleHandler.get_dependencies(
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