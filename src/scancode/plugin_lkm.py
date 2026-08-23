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
    Extract '.modinfo' metadata from the Linux kernel module file at 'location'
    using a custom minimal ELF parser.

    Return '.modinfo' metadata as a mapping of keys to lists of values.

    Multiple values are preserved because fields such as 'author', 'alias',
    and 'firmware' may occur more than once.
    """
    import struct

    metadata: Dict[str, List[str]] = {}
    raw_bytes = b''

    try:
        with open(location, 'rb') as f:
            e_ident = f.read(16)
            if len(e_ident) == 16 and e_ident[0:4] == b'\x7fELF':
                ei_class = e_ident[4]  # 1 = 32-bit, 2 = 64-bit
                ei_data = e_ident[5]   # 1 = LSB, 2 = MSB
                
                if ei_class in (1, 2) and ei_data in (1, 2):
                    endian = '<' if ei_data == 1 else '>'
                    
                    if ei_class == 1:
                        # 32-bit ELF
                        f.seek(32)
                        header_data = f.read(20)
                        if len(header_data) == 20:
                            e_shoff, _, _, _, _, e_shentsize, e_shnum, e_shstrndx = struct.unpack(
                                endian + 'IIHHHHHH', header_data
                            )
                    else:
                        # 64-bit ELF
                        f.seek(40)
                        header_data = f.read(24)
                        if len(header_data) == 24:
                            e_shoff, _, _, _, _, e_shentsize, e_shnum, e_shstrndx = struct.unpack(
                                endian + 'QIHHHHHH', header_data
                            )
                    
                    if e_shnum > 0 and e_shentsize > 0:
                        f.seek(e_shoff)
                        section_headers_data = f.read(e_shnum * e_shentsize)
                        if len(section_headers_data) == e_shnum * e_shentsize:
                            
                            # Helper to parse section header at index
                            def get_section_header(idx):
                                offset = idx * e_shentsize
                                entry_data = section_headers_data[offset:offset + e_shentsize]
                                if len(entry_data) < e_shentsize:
                                    return None
                                if ei_class == 1:
                                    sh_name, _, _, _, sh_offset, sh_size = struct.unpack(
                                        endian + 'IIIIII', entry_data[:24]
                                    )
                                else:
                                    sh_name, _, _, _, sh_offset, sh_size = struct.unpack(
                                        endian + 'IIQQQQ', entry_data[:40]
                                    )
                                return sh_name, sh_offset, sh_size

                            shstr_header = get_section_header(e_shstrndx)
                            if shstr_header:
                                _, shstr_offset, shstr_size = shstr_header
                                f.seek(shstr_offset)
                                shstr_table = f.read(shstr_size)
                                if len(shstr_table) == shstr_size:
                                    for i in range(e_shnum):
                                        header = get_section_header(i)
                                        if not header:
                                            continue
                                        sh_name, sh_offset, sh_size = header
                                        
                                        end = shstr_table.find(b'\x00', sh_name)
                                        if end != -1:
                                            name = shstr_table[sh_name:end].decode('utf-8', errors='ignore')
                                        else:
                                            name = shstr_table[sh_name:].decode('utf-8', errors='ignore')
                                        
                                        if name == '.modinfo':
                                            f.seek(sh_offset)
                                            raw_bytes = f.read(sh_size)
                                            break
    except Exception:
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
    Return normalized kernel module dependency names from '.modinfo' metadata.
    The 'depends' field is a comma-separated list of required module names.
    """
    dependency_names = []

    for depends_entry in metadata.get('depends', []):
        dependency_names.extend(
            dependency.strip()
            for dependency in depends_entry.split(',')
            if dependency.strip()
        )

    return dependency_names
