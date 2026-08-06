#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from typing import Dict
from typing import List

import attr

from commoncode.cliutils import OTHER_SCAN_GROUP
from commoncode.cliutils import PluggableCommandLineOption
from elftools.common.exceptions import ELFError
from elftools.elf.elffile import ELFFile
from plugincode.scan import ScanPlugin
from plugincode.scan import scan_impl


@scan_impl
class LinuxKernelModuleScanner(ScanPlugin):
    """
    Scan Linux kernel module files for metadata stored in their ELF
    '.modinfo' section.
    """

    resource_attributes = dict(
        linux_kernel_module=attr.ib(default=None, repr=False),
    )

    run_order = 9
    sort_order = 9

    options = [
        PluggableCommandLineOption(
            ('--lkm',),
            is_flag=True,
            default=False,
            help='Scan Linux kernel module files for .modinfo metadata.',
            help_group=OTHER_SCAN_GROUP,
        )
    ]

    def is_enabled(self, lkm, **kwargs):
        return lkm

    def get_scanner(self, **kwargs):
        return scan_linux_kernel_module


def scan_linux_kernel_module(location, **kwargs):
    """
    Return a mapping of Linux kernel module metadata found in the '.ko' file
    at 'location'. Return an empty mapping for other files and for files that
    do not contain usable '.modinfo' metadata.
    """
    if not location.lower().endswith('.ko'):
        return {}

    metadata = extract_modinfo(location)
    if not metadata:
        return {}

    # The .modinfo "depends" value is a comma-separated list of required
    # kernel module names, not a list of package-management dependencies.
    metadata['depends'] = get_dependency_names(metadata)

    return dict(linux_kernel_module=metadata)


def extract_modinfo(location: str) -> Dict[str, List[str]]:
    """
    Extract '.modinfo' metadata from the Linux kernel module file at 'location'.

    Return '.modinfo' metadata as a mapping of keys to lists of values.

    Multiple values are preserved because fields such as 'author', 'alias',
    and 'firmware' may occur more than once.
    """
    metadata: Dict[str, List[str]] = {}

    try:
        with open(location, 'rb') as module_file:
            elf_file = ELFFile(module_file)
            modinfo_section = elf_file.get_section_by_name('.modinfo')
            if modinfo_section is None:
                return {}

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


def get_dependency_names(metadata: Dict[str, List[str]]) -> List[str]:
    """
    Returns a list of strings, each being a kernel module name
    Normalized fields to a list of strings derived from the '.modinfo' metadata. The 'depends' field is a
    comma-separated list of required kernel module names 
    """
    dependency_names = []

    for depends_entry in metadata.get('depends', []):
        dependency_names.extend(
            dependency.strip()
            for dependency in depends_entry.split(',')
            if dependency.strip()
        )

    return dependency_names
