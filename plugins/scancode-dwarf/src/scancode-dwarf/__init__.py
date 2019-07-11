#
# Copyright (c) 2019 nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/scancode-toolkit/
# The ScanCode software is licensed under the Apache License version 2.0.
# Data generated with ScanCode require an acknowledgment.
# ScanCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# When you publish or redistribute any data created with ScanCode or any ScanCode
# derivative work, you must accompany this data with the following acknowledgment:
#
#  Generated with ScanCode and provided on an "AS IS" BASIS, WITHOUT WARRANTIES
#  OR CONDITIONS OF ANY KIND, either express or implied. No content created from
#  ScanCode should be considered or used as legal advice. Consult an Attorney
#  for any legal advice.
#  ScanCode is a free software code scanning tool from nexB Inc. and others.
#  Visit https://github.com/nexB/scancode-toolkit/ for support and download.

from __future__ import absolute_import
from __future__ import unicode_literals

from functools import partial

from plugincode.scan import ScanPlugin
from plugincode.scan import scan_impl
from scancode import CommandLineOption
from scancode import SCAN_GROUP
from typecode.contenttype import get_type

import dwarf
import dwarf2

@scan_impl
class Dwarfcanner(ScanPlugin):
    """
    Scan a dwarf infos for URLs.
    """
    resource_attributes = dict(packages=attr.ib(default=attr.Factory(list), repr=False))

    options = [
        CommandLineOption(('--dwarf',),
            is_flag=True, default=False,
            help='Scan dwarf info.',
            help_group=SCAN_GROUP,
            sort_order=50),
    ]

    def is_enabled(self, dwarf, **kwargs):
        return dwarf

    def get_scanner(self, **kwargs):
        return get_dwarfs


def get_dwarfs(location, **kwargs):
    """
    Return a mapping with original_source_files and included_source_files
    """
    d = dwarf.Dwarf(location)
    if d:
        dwarf_source_path_result = dwarf_source_path
        if dwarf_source_path_result:
            results = OrderedDict([
                ('dwarf_source_path', list(dwarf_source_path)),
            ])
            return results


def dwarf_source_path(location):
    """Collect unique paths to compiled source code found in Elf binaries DWARF sections for D2D."""
    location = location
    T = contenttype.get_type(location)
    if not (T.is_elf or T.is_stripped_elf):
        return
    seen_paths = set()
    path_file_names = set()
    bare_file_names = set()
    for dpath in chain(get_dwarf1(location), get_dwarf2(location)):
        if dpath in seen_paths:
            continue
        fn = fileutils.file_name(dpath)
        if fn == dpath:
            bare_file_names.add(fn)
            continue
        else:
            path_file_names.add(fn)
        seen_paths.add(dpath)
        yield dpath
    # only yield filename that do not exist as full paths
    for bfn in sorted(bare_file_names):
        if bfn not in path_file_names and bfn not in seen_paths:
            yield bfn
            seen_paths.add(bfn)


def get_dwarf1(location):
    """Using Dwarfdump"""
    d = dwarf.Dwarf(location)
    if d:
        # Note: we return all paths at once, when we should probably return the
        # std and original path as separate annotations
        for p in d.original_source_files + d.included_source_files:
            yield p


def get_dwarf2(location):
    """Using NM"""
    for _, _, path_to_source, _ in dwarf2.get_dwarfs(location):
        if path_to_source:
            yield path_to_source
