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


"""
A set of functions and objects to extract information from binary Elf files
DWARF debug data.
"""

from __future__ import absolute_import
from __future__ import print_function

from collections import OrderedDict
import posixpath
import re

from commoncode import command
from plugincode.location_provider import get_location
from typecode import contenttype


SCANCODE_DWARFDUMP_EXE = 'scancode.dwarfdump.exe'


################################################################
# DWARFDUMP PARSING
################################################################
def EMPTY_LINE_RE():
    return re.compile('^\s*$')

def DCOMP_UNIT_START_RE():
    return re.compile('^COMPILE_UNIT<header overall offset =.*$')

def DCMPDIR_RE():
    return re.compile(r'^DW_AT_comp_dir\s*(.*)$')

def DCMPDIR_FILE_RE():
    return re.compile(r'^DW_AT_name\s*(.*)$')

def DLOCAL_SYMBOLS_RE():
    return re.compile(r'^LOCAL_SYMBOLS:$')

def DWARF_FILES_RE():
    return re.compile(r'^DW_AT_(?:decl|call)_file\s*\d*\s*(.*)$')


class Dwarf(object):
    """
    This class represents the Dwarf content of an Elf object
    http://en.wikipedia.org/wiki/Executable_and_Linkable_Format.
    """

    def __init__(self, location):

        self.cmd_loc = get_location(SCANCODE_DWARFDUMP_EXE)

        # The elf location
        self.elf_location = location
        # Source files that were compiled and linked explicitly to create this
        # Elf This are the source files that a developer typically edits.
        self.original_source_files = []

        # Source files that were compiled and linked implicitly from the
        # standard library or by the toolchain when this Elf was created.

        # These files may vary from platform to platform and version of the Gnu
        # toolchain. They are not always relevant from an interaction perspective
        # except in a few cases, such as LKM.
        self.included_source_files = []

        self._files = []

        # now parse thyself
        self._parseinfo()
        # and cleanup thyself
        self.cleanup()

    def _parseinfo(self):
        """
        Parse dwarfdump info section of an elf file.
        """
        rc, out, err = command.execute2(
            cmd_loc=self.cmd_loc,
            args=['-i', self.elf_location],
            to_files=True
        )

        if rc != 0:
            raise Exception(open(err).read())

        # loop through each returned line passing control to a handler
        with open(out, 'rb') as lines:
            for line in lines:
                line = line.strip()
                if DCOMP_UNIT_START_RE().match(line):
                    dwarfinfo = DwarfInfo()
                    dwarfinfo.parse(self, lines)

    def cleanup(self):
        original, std_includes = cleanup(self._files)

        self.included_source_files.extend(x for x in std_includes
            if x not in self.included_source_files)

        self.original_source_files.extend(x for x in original
            if x not in self.original_source_files)

    def asdict(self):
        return OrderedDict([
            ('original_source_files', self.original_source_files),
            ('included_source_files', self.included_source_files)
        ])


def cleanup(paths):
    """
    Given a list of paths, returns two lists: a list of paths likely to be
    original code and a list of paths likely to be standard includes.
    """
    # TODO: mostly copied from dwarf.Dwarf._cleanup ...
    # the code should not be duplicated
    std_includes = []
    original = []
    for p in paths:
        # FIXME: this will NOT work on windows paths
        p = posixpath.normpath(p)
        if contenttype.is_standard_include(p):
            std_includes.append(p)
        else:
            original.append(p)
    return original, std_includes


class DwarfInfo(object):
    """
    .debug_info

    COMPILE_UNIT<header overall offset = 0>:
    <0><   11>      DW_TAG_compile_unit
                    DW_AT_producer              GNU C 4.2.1 (SUSE Linux)
                    DW_AT_language              DW_LANG_C89
                    DW_AT_name                  init.c
                    DW_AT_comp_dir              /usr/src/packages/BUILD/glibc-2.6.1/csu
                    DW_AT_low_pc                0x8048e24
                    DW_AT_high_pc               0x8048e24
                    DW_AT_stmt_list             0

    LOCAL_SYMBOLS:
    <1><   37>      DW_TAG_base_type
                    DW_AT_byte_size             4
                    DW_AT_encoding              DW_ATE_unsigned
                    DW_AT_name                  unsigned int
    <1><  122>      DW_TAG_typedef
                    DW_AT_name                  __off_t
                    DW_AT_decl_file             4 /usr/include/bits/types.h
                    DW_AT_decl_line             144
                    DW_AT_type                  <133>
    <1><  133>      DW_TAG_base_type
                    DW_AT_byte_size             4
                    DW_AT_encoding              DW_ATE_signed
                    DW_AT_name                  long int
    <1><  140>      DW_TAG_typedef
                    DW_AT_name                  __off64_t
                    DW_AT_decl_file             4 /usr/include/bits/types.h
                    DW_AT_decl_line             145
                    DW_AT_type                  <111>
    <1><  151>      DW_TAG_base_type
                    DW_AT_byte_size             4
                    DW_AT_encoding              DW_ATE_unsigned
    <1><  154>      DW_TAG_pointer_type
                    DW_AT_byte_size             4
    <1><  156>      DW_TAG_pointer_type
                    DW_AT_byte_size             4
                    DW_AT_type                  <162>
    <1><  162>      DW_TAG_base_type
                    DW_AT_byte_size             1
                    DW_AT_encoding              DW_ATE_signed_char
                    DW_AT_name                  char
    <1><  169>      DW_TAG_structure_type
                    DW_AT_name                  _IO_FILE
                    DW_AT_byte_size             148
                    DW_AT_decl_file             6 /usr/include/stdio.h
                    DW_AT_decl_line             45
    <2>< 1429>      DW_TAG_inlined_subroutine
                    DW_AT_abstract_origin       <1125>
                    DW_AT_ranges                32
                    ranges: 4 at .debug_ranges offset 32 (0x20) (32 bytes)
                            [ 0] range entry    0x00000061 0x0000029a
                            [ 1] range entry    0x000004e7 0x00000538
                            [ 2] range entry    0x000002b4 0x0000037f
                            [ 3] range end      0x00000000 0x00000000
                    DW_AT_call_file             1 /home/jqbx34/ssdeep-2.0/main.c
                    DW_AT_call_line             209
                    DW_AT_sibling               <1556>
    <3>< 1444>      DW_TAG_formal_parameter
                    DW_AT_abstract_origin       <1158>
    <3>< 1449>      DW_TAG_formal_parameter
                    DW_AT_abstract_origin       <1147>
    """
    def __init__(self):
        self.dwarfdump_option = "-l"
        self.start_re = DCOMP_UNIT_START_RE()
        self.cu_filename = ''
        self.cu_comp_dir = ''
        self.files = []

    def parse(self, dwarf, location):
        for line in location:
            if re.match(DCOMP_UNIT_START_RE(), line):
                break
            line = line.strip()
            # we have a filename followed by a compilation dir name
            match = DCMPDIR_FILE_RE().match(line)
            if match:
                self.cu_filename = match.groups()[0]
                continue
            match = DCMPDIR_RE().match(line)
            if match:
                self.cu_comp_dir = match.groups()[0]
                self.parse_local_symbols(location)

        if posixpath.isabs(self.cu_filename):
            dwarf._files.append(self.cu_filename)
        else:
            dwarf._files.append(posixpath.join(self.cu_comp_dir, self.cu_filename))

        dwarf._files.extend(self.files)

    def parse_local_symbols(self, location):
        for line in location:
            if not line or re.match(DCOMP_UNIT_START_RE(), line):
                return
            line = line.strip()
            match = DWARF_FILES_RE() .match(line)
            if match:
                filename = match.groups()[0]
                if posixpath.isabs(filename):
                    self.files.append(filename)
                else:
                    self.files.append(posixpath.join(self.cu_comp_dir, filename))
