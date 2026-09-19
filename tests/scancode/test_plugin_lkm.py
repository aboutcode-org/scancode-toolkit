#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import json
from pathlib import Path

from scancode import plugin_lkm
from scancode.cli_test_utils import run_scan_click


class TestLinuxKernelModuleScanner:

    test_data_dir = (
        Path(__file__).resolve().parents[2]
        / 'tests'
        / 'licensedcode'
        / 'data'
        / 'query'
    )

    def test_extract_modinfo(self):
        test_file = self.test_data_dir / 'eeepc_acpi.ko'

        metadata = plugin_lkm.extract_modinfo(str(test_file))

        assert 'license' in metadata
        assert 'description' in metadata
        assert 'author' in metadata

    def test_get_dependency_names(self):
        metadata = {
            'depends': [
                'usbcore,cfg80211,mac80211',
            ]
        }

        result = plugin_lkm.get_dependency_names(metadata)

        assert result == [
            'usbcore',
            'cfg80211',
            'mac80211',
        ]

    def test_get_dependency_names_handles_multiple_entries(self):
        metadata = {
            'depends': [
                'usbcore,cfg80211',
                'mac80211,netdev',
            ]
        }

        result = plugin_lkm.get_dependency_names(metadata)

        assert result == [
            'usbcore',
            'cfg80211',
            'mac80211',
            'netdev',
        ]

    def test_scan_unrelated_file_returns_empty_mapping(self):
        test_file = self.test_data_dir / 'apache-2.0.LICENSE'

        result = plugin_lkm.scan_linux_kernel_module(str(test_file))

        assert result == {}

    def test_scan_invalid_lkm_returns_empty_mapping(self, tmp_path):
        test_file = tmp_path / 'fake.ko'
        test_file.write_bytes(b'not an elf file')

        result = plugin_lkm.scan_linux_kernel_module(str(test_file))

        assert result == {}

    def test_scan_linux_kernel_module(self):
        test_file = self.test_data_dir / 'eeepc_acpi.ko'

        result = plugin_lkm.scan_linux_kernel_module(str(test_file))

        assert list(result) == ['linux_kernel_module']

        metadata = result['linux_kernel_module']
        assert metadata['license'] == ['GPL']
        assert metadata['description'] == ['Asus EeePC Hotkey Driver']
        assert metadata['author'] == [
            'Julien Lerouge, Karol Kozimor, Eric Cooper',
        ]
        assert metadata['depends'] == []
        assert metadata['srcversion'] == ['7FD8A46D43685ADB0819A28']
        assert metadata['vermagic'] == [
            '2.6.24-19-generic SMP mod_unload 586 ',
        ]

    def test_plugin_supplies_file_scanner(self):
        scanner = plugin_lkm.LinuxKernelModuleScanner()

        assert scanner.get_scanner() is plugin_lkm.scan_linux_kernel_module
        assert scanner.is_enabled(lkm=True)
        assert not scanner.is_enabled(lkm=False)
        assert list(scanner.resource_attributes) == ['linux_kernel_module']

    def test_lkm_scan_adds_file_metadata_without_package_data(self, tmp_path):
        test_file = self.test_data_dir / 'eeepc_acpi.ko'
        result_file = tmp_path / 'lkm-scan.json'

        run_scan_click([
            '--lkm',
            '--json-pp',
            str(result_file),
            str(test_file),
        ])

        with result_file.open(encoding='utf-8') as results:
            scanned_file = json.load(results)['files'][0]

        metadata = scanned_file['linux_kernel_module']
        assert metadata['license'] == ['GPL']
        assert metadata['depends'] == []
        assert 'package_data' not in scanned_file
