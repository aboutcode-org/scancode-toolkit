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

from __future__ import absolute_import, print_function

import os
import re

from commoncode import command
from commoncode.functional import flatten
from commoncode import fileutils
from plugincode.location_provider import get_location

"""
Functions and objects to extract information from binary Elf files from a
readelf and c++filt outputs.

For a good introduction on readelf and ELF see:
    http://www.linuxforums.org/misc/understanding_elf_using_readelf_and_objdump.html
"""


SCANCODE_READELF_EXE = 'scancode.readelf.exe'
SCANCODE_READELF_LIB = 'scancode.readelf.lib'

SCANCODE_CPLUSPLUSFILT_EXE = 'scancode.cplusplusfilt.exe'
SCANCODE_CPLUSPLUSFILT_LIB = 'scancode.cplusplusfilt.lib'


def next_line(file_desc):
    try:
        return  file_desc.next()
    except:
        return None


def EMPTY_LINE_RE():
    return re.compile("^\s*$")


#################################################
# READELF PARSING
################################################

class Elf(object):
    """
    Represents an Elf object
    http://en.wikipedia.org/wiki/Executable_and_Linkable_Format
    """
    def __init__(self, location):
        # Dynamic libraries needed by this Elf at runtime
        self.needed_libraries = set()

        # Symbols is an instance of ElfSymbolsTableSection
        self.symbols_section = ElfSymbolsTableSection()
        self.files = self.symbols_section.files

        # sections parsers
        self.readelf_sections = [ElfDynamicSection(), self.symbols_section]
        self.handlers = {}
        self.readelf_options = []

        # The elf location
        self.elf_location = location
        
        
        self.cmd_loc = get_location(SCANCODE_READELF_EXE)
        self.lib_loc = get_location(SCANCODE_READELF_LIB)

        # Information contained in the elf header
        self.info = {}

        self.setup_handlers()
        # now parse thyself
        self.parse()

    def symbols(self):
        return sorted(flatten([list(self.symbols_section.local_functions),
                        list(self.symbols_section.global_functions)]))

    def setup_handlers(self):
        self.readelf_options = set([s.readelf_option
                                     for s in self.readelf_sections])
        for s in self.readelf_sections:
            self.handlers[s.start_re] = s

    def get_handler(self, line):
        """
        Return a parsing function for a readelf section parsing from that start
        line onwards.
        """
        for start_re, section in self.handlers.items():
            if re.match(start_re, line):
                return section.parse

    def parse(self):
        """
        Parse readelf sections to populates the Elf object for an elf location.
        """
        readelf_args = ['--wide']
        readelf_args.extend(self.readelf_options)
        readelf_args.append(self.elf_location)

        rc, out, err = command.execute2(cmd_loc=self.cmd_loc,
                                        args=readelf_args,
                                        lib_dir=self.lib_loc,
                                        to_files=True)
        if rc != 0:
            raise Exception(open(err).read() + '\n' + open(out).read())

        # loop through each line passing control to a handler as needed
        with open(out, 'rb') as elf_lines:
            for line in elf_lines:
                # get the handler for this line
                line = line.strip()
                if line:
                    handler = self.get_handler(line)
                    if handler:
                        handler(self, elf_lines)


###################################
# READELF Sections handlers
# Each section handler has
# - a start_re that matches a start lines that it can parse onward
# - a parse method that accept an elf object, a file like object and the lastline processed
###################################
def DYNAMIC_START_RE():
    return re.compile("^Dynamic section at offset")

# 0x00000001 (NEEDED)                     Shared library: [libc.so.6]
# 0x00000001 (NEEDED)                     Shared library: [libc.so.6]
def DYNAMIC_NEEDED_RE():
    return re.compile(r'^.*'
                      r'\(NEEDED\)'
                      r'\s*'
                      r'Shared library:\s*'
                      r'\[(.*)\]')


class ElfDynamicSection(object):
    """
    $ readelf --wide --dynamic /tests/dependencies-testfiles/elf/ssdeep.i686
    
    Dynamic section at offset 0x4f20 contains 21 entries:
      Tag        Type                         Name/Value
     0x00000001 (NEEDED)                     Shared library: [libc.so.6]
     0x0000000c (INIT)                       0x8048ae0
     0x0000000d (FINI)                       0x804bf5c
     0x00000004 (HASH)                       0x80481a0
     0x6ffffef5 (GNU_HASH)                   0x8048314
     0x00000005 (STRTAB)                     0x80486b4
     0x00000006 (SYMTAB)                     0x8048354
     0x0000000a (STRSZ)                      480 (bytes)
     0x0000000b (SYMENT)                     16 (bytes)
     0x00000015 (DEBUG)                      0x0
     0x00000003 (PLTGOT)                     0x804dff4
     0x00000002 (PLTRELSZ)                   368 (bytes)
     0x00000014 (PLTREL)                     REL
     0x00000017 (JMPREL)                     0x8048970
     0x00000011 (REL)                        0x8048940
     0x00000012 (RELSZ)                      48 (bytes)
     0x00000013 (RELENT)                     8 (bytes)
     0x6ffffffe (VERNEED)                    0x8048900
     0x6fffffff (VERNEEDNUM)                 1
     0x6ffffff0 (VERSYM)                     0x8048894
     0x00000000 (NULL)                       0x0
    """
    def __init__(self):
        self.readelf_option = '--dynamic'
        self.start_re = DYNAMIC_START_RE()
        self.end_re = EMPTY_LINE_RE()
        self.needed_libs = set()

    def parse(self, elf, file_like):
        while 1:
            line = next_line(file_like)
            if not line or re.match(self.end_re, line):
                break
            line = line.strip()
            match = DYNAMIC_NEEDED_RE().match(line)
            if match:
                name = match.groups()[0]
                self.needed_libs.add(name)
                continue
        elf.needed_libraries.update(self.needed_libs)


demangled_junk = ['global constructors keyed to main',
                  '__static_initialization_and_destruction',
                  '__tcf']


def demangle(symbols, max_symbols=50):
    """
    Demangle C++ mangled symbols.
    Only demangle up to max_symbols at a time. Why 100? This small enough
    to be safe. Bigger numbers will make c++filt fail randomly.
    """
    demangled = set()
    symbols = list(symbols)
    chunks = (symbols[i:i + max_symbols]
              for i in xrange(0, len(symbols), max_symbols))
    for chunk in chunks:
        demang = set(demangle_chunk(chunk))
        demangled.update(demang)
    return list(demangled)


def demangle_chunk(symbols):
    """
    Return a set of demangled Elf symbol names using binutils
    c++filt. The symbols are filtered for eventual known junk.
    """
    if not symbols:
        return []

    cppfilt_command = 'c++filt'

    args = ['--no-strip-underscores',
            '--no-verbose',
            '--no-params'] + symbols
    
    cmd_loc = get_location(SCANCODE_CPLUSPLUSFILT_EXE)
    lib_loc = get_location(SCANCODE_CPLUSPLUSFILT_LIB)
    rc, out, err = command.execute2(cmd_loc, args,
                                    lib_dir=lib_loc, to_files=True)
    if rc != 0:
        raise Exception(open(err).read())

    demangled = set()
    with open(out, 'rb') as names:
        for name in names:
            # ignore junk injected by the compiler
            isjunk = False
            for junk in demangled_junk:
                if name.startswith(junk):
                    isjunk = True
                    break
            if isjunk:
                continue
            # do not keep params for CPP functions, just the function
            if '(' in name:
                name = name.split('(')[0]
            demangled.add(name.strip())
    return list(demangled)


def SYMBOLS_START_RE():
    return re.compile("Symbol table '.symtab' contains")


def SYMBOLS_INTERESTING_RE():
#                                       51:    0804bf30       0     FUNC                 LOCAL           DEFAULT    14    __do_global_ctors_aux
    return re.compile(r"^\d*:\s+[A-Fa-f0-9]+\s+\d+\s+(FILE|FUNC|OBJECT)\s+(LOCAL|GLOBAL)\s+DEFAULT\s+\w+\s+(.*)$")


# FIXME: the exclusion lists are not comprehensive
standardfiles = ['init.c', 'initfini.c', 'crtstuff.c']


standardfunc = ['__do_global_dtors_aux',
                'frame_dummy',
                '__do_global_ctors_aux',
                '__libc_csu_fini',
                '_start',
                '_fini',
                '__libc_csu_init',
                '_init',
                'call_gmon_start']


standardobj = ['__CTOR_LIST__',
                '__DTOR_LIST__',
                '__JCR_LIST__',
                '__CTOR_END__',
                '__DTOR_END__',
                '__FRAME_END__',
                '__JCR_END__',
                '_fp_hw',
                '_IO_stdin_used']


class ElfSymbolsTableSection(object):
    """
    $ readelf --wide --symbols bin/3rdparty/ssdeep/Linux/i686/ssdeep | more
    
    Symbol table '.symtab' contains 188 entries:
      Num:    Value  Size Type    Bind   Vis      Ndx Name
        0: 00000000     0 NOTYPE  LOCAL  DEFAULT  UND
        1: 08048154     0 SECTION LOCAL  DEFAULT    1
       36: 00000000     0 FILE    LOCAL  DEFAULT  ABS init.c
       37: 00000000     0 FILE    LOCAL  DEFAULT  ABS initfini.c
       38: 00000000     0 FILE    LOCAL  DEFAULT  ABS crtstuff.c
       46: 00000000     0 FILE    LOCAL  DEFAULT  ABS crtstuff.c
       47: 0804df10     0 OBJECT  LOCAL  DEFAULT   18 __CTOR_END__
       51: 0804bf30     0 FUNC    LOCAL  DEFAULT   14 __do_global_ctors_aux
       52: 00000000     0 FILE    LOCAL  DEFAULT  ABS initfini.c
       53: 00000000     0 FILE    LOCAL  DEFAULT  ABS main.c
       54: 00000000     0 FILE    LOCAL  DEFAULT  ABS match.c
       58: 0804a1a0   497 FUNC    LOCAL  DEFAULT   14 process_dir
       59: 00000000     0 FILE    LOCAL  DEFAULT  ABS cycles.c
       62: 00000000     0 FILE    LOCAL  DEFAULT  ABS fuzzy.c
       78: 00000000     0 FILE    LOCAL  DEFAULT  ABS find-file-size.c
       79: 0804dff4     0 OBJECT  LOCAL  HIDDEN   23 _GLOBAL_OFFSET_TABLE_
       80: 0804df0c     0 NOTYPE  LOCAL  HIDDEN   18 __init_array_end
       81: 0804df0c     0 NOTYPE  LOCAL  HIDDEN   18 __init_array_start
       82: 0804df20     0 OBJECT  LOCAL  HIDDEN   21 _DYNAMIC
       83: 00000000    59 FUNC    GLOBAL DEFAULT  UND fileno@@GLIBC_2.0
       84: 0804e0b8     0 NOTYPE  WEAK   DEFAULT   24 data_start
       85: 00000000   347 FUNC    GLOBAL DEFAULT  UND fputs@@GLIBC_2.0
       86: 00000000    29 FUNC    GLOBAL DEFAULT  UND __errno_location@@GLIBC_2
       87: 080499a0    82 FUNC    GLOBAL DEFAULT   14 match_pretty    
      140: 00000000    57 FUNC    GLOBAL DEFAULT  UND printf@@GLIBC_2.0
      141: 0804a9f0    83 FUNC    GLOBAL DEFAULT   14 chop_line_tchar
      142: 0804aa50    20 FUNC    GLOBAL DEFAULT   14 mm_magic
      143: 0804ae10    99 FUNC    GLOBAL DEFAULT   14 print_error
      144: 0804b180   388 FUNC    GLOBAL DEFAULT   14 fuzzy_hash_buf
      145: 00000000    92 FUNC    GLOBAL DEFAULT  UND closedir@@GLIBC_2.0
      146: 00000000   355 FUNC    GLOBAL DEFAULT  UND fwrite@@GLIBC_2.0
      147: 00000000    36 FUNC    GLOBAL DEFAULT  UND fprintf@@GLIBC_2.0
      148: 00000000   367 FUNC    GLOBAL DEFAULT  UND strstr@@GLIBC_2.0
      149: 0804e0c4     0 NOTYPE  GLOBAL DEFAULT  ABS __bss_start
      150: 00000000   383 FUNC    GLOBAL DEFAULT  UND malloc@@GLIBC_2.0
      151: 00000000   265 FUNC    GLOBAL DEFAULT  UND fseeko@@GLIBC_2.1
      152: 08049820   382 FUNC    GLOBAL DEFAULT   14 match_compare
      153: 0804abd0    21 FUNC    GLOBAL DEFAULT   14 display_filename
      154: 0804a650   110 FUNC    GLOBAL DEFAULT   14 find_next_comma
      155: 00000000   261 FUNC    GLOBAL DEFAULT  UND fputc@@GLIBC_2.0
      156: 08049a00   846 FUNC    GLOBAL DEFAULT   14 hash_file
      157: 00000000    88 FUNC    GLOBAL DEFAULT  UND memmove@@GLIBC_2.0
      158: 00000000   492 FUNC    GLOBAL DEFAULT  UND ftello@@GLIBC_2.1
      159: 0804b310   511 FUNC    GLOBAL DEFAULT   14 fuzzy_hash_file
      160: 00000000   426 FUNC    GLOBAL DEFAULT  UND strcat@@GLIBC_2.0
      161: 00000000   339 FUNC    GLOBAL DEFAULT  UND getcwd@@GLIBC_2.0
      162: 0804f0f4     0 NOTYPE  GLOBAL DEFAULT  ABS _end
      163: 0804e100     4 OBJECT  GLOBAL DEFAULT   25 stdout@@GLIBC_2.0
      164: 00000000   426 FUNC    GLOBAL DEFAULT  UND puts@@GLIBC_2.0
      165: 08049ef0   674 FUNC    GLOBAL DEFAULT   14 process_normal
      166: 00000000    52 FUNC    GLOBAL DEFAULT  UND sscanf@@GLIBC_2.0
      167: 00000000   191 FUNC    GLOBAL DEFAULT  UND __fxstat@@GLIBC_2.0
      168: 00000000   243 FUNC    GLOBAL DEFAULT  UND strncmp@@GLIBC_2.0
      169: 00000000 16699 FUNC    GLOBAL DEFAULT  UND vfprintf@@GLIBC_2.0
      170: 08049470    23 FUNC    GLOBAL DEFAULT   14 lsh_list_init
      171: 0804ac70   155 FUNC    GLOBAL DEFAULT   14 internal_error
      172: 0804e104     4 OBJECT  GLOBAL DEFAULT   25 optarg@@GLIBC_2.0
      173: 00000000   311 FUNC    GLOBAL DEFAULT  UND fread@@GLIBC_2.0
      174: 0804ab80    79 FUNC    GLOBAL DEFAULT   14 sanity_check
    """
    def __init__(self):
        self.readelf_option = '--symbols'
        self.start_re = SYMBOLS_START_RE()
        self.end_re = EMPTY_LINE_RE()

        self.files = set()
        self.standard_files = set()

        # FIXME: add support for weak and notype symbols.
        # FIXME: discard symbols with hidddicten visbility
        # FIXME: keep pointers to GCC and GLibC symbols

        # dictioanries keys below map to keyword in a line dump from readlef
        # see output exmaple above
        self.local_functions = set()
        self.local_objects = set()
        self.global_objects = set()
        self.global_functions = set()
        self.locals = {"FUNC": self.local_functions, "OBJECT": self.local_objects}
        self.globals = {"FUNC": self.global_functions, "OBJECT": self.global_objects}
        self.locglobs = {"LOCAL": self.locals, "GLOBAL": self.globals}

        self.external_libs_functions = set()
        self.external_libs_objects = set()
        self.externals = {"FUNC": self.external_libs_functions, "OBJECT": self.external_libs_objects}

        self.standard_functions = set()
        self.standard_objects = set()
        self.standards = {"FUNC": self.standard_functions, "OBJECT": self.standard_objects}

        self.shared_libs_references = set()

    def parse(self, elf, file_like):
        while 1:
            line = next_line(file_like)
            if not line or re.match(self.end_re, line):
                break
            line = line.strip()
            match = SYMBOLS_INTERESTING_RE().match(line)
            if match:
                _type = match.groups()[0]
                scope = match.groups()[1]
                name = match.groups()[2]
                sharedlib = None
                if '@@' in name:
                    name, sharedlib = name.split("@@")
                    self.shared_libs_references.add(name)

                if _type == 'FILE' and not name.startswith("<") :
                    if name in standardfiles:
                        self.standard_files.add(name)
                    else:
                        self.files.add(name)

                if ((_type == 'FUNC' or _type == 'OBJECT')
                    and not name.startswith("$")):
                    if sharedlib:
                        self.externals[_type].add((name, sharedlib))
                    elif name in standardfunc or name in standardobj:
                        self.standards[_type].add(name)
                    elif '.' not in name:
                        self.locglobs[scope][_type].add(name)
                continue

        self.local_functions = demangle(self.local_functions)
        self.local_objects = demangle(self.local_objects)

        self.global_objects = demangle(self.global_objects)
        self.global_functions = demangle(self.global_functions)

        self.standard_functions = demangle(self.standard_functions)
        self.standard_objects = demangle(self.standard_objects)


class ElfHeaderSection(object):
    start_line = 'ELF Header:'
    readelf_option = '--file-header'
    """
    $ readelf --wide --file-header ~/c/tmp/testelf/arm_scatter_load
    ELF Header:
      Magic:   7f 45 4c 46 01 01 01 00 00 00 00 00 00 00 00 00
      Class:                             ELF32
      Data:                              2's complement, little endian
      Version:                           1 (current)
      OS/ABI:                            UNIX - System V
      ABI Version:                       0
      Type:                              EXEC (Executable file)
      Machine:                           ARM
      Version:                           0x1
      Entry point address:               0x100000
      Start of program headers:          42228 (bytes into file)
      Start of section headers:          42260 (bytes into file)
      Flags:                             0x4000016, has entry point, Version4 EABI, <unknown>
      Size of this header:               52 (bytes)
      Size of program headers:           32 (bytes)
      Number of program headers:         1
      Size of section headers:           40 (bytes)
      Number of section headers:         17
      Section header string table index: 16
    """
    pass


class ElfProgramHeadersSection(object):
    start_line = "Program Headers:"
    readelf_option = '--program-headers'
    """
    Program Headers:
      Type           Offset   VirtAddr   PhysAddr   FileSiz MemSiz  Flg Align
      PHDR           0x000034 0x08048034 0x08048034 0x00120 0x00120 R E 0x4
      INTERP         0x000154 0x08048154 0x08048154 0x00013 0x00013 R   0x1
          [Requesting program interpreter: /lib/ld-linux.so.2]
      LOAD           0x000000 0x08048000 0x08048000 0x04868 0x04868 R E 0x1000
      LOAD           0x004f0c 0x0804df0c 0x0804df0c 0x001b8 0x011e8 RW  0x1000
      DYNAMIC        0x004f20 0x0804df20 0x0804df20 0x000d0 0x000d0 RW  0x4
      NOTE           0x000168 0x08048168 0x08048168 0x00020 0x00020 R   0x4
      NOTE           0x000188 0x08048188 0x08048188 0x00018 0x00018 R   0x4
      GNU_STACK      0x000000 0x00000000 0x00000000 0x00000 0x00000 RW  0x4
      GNU_RELRO      0x004f0c 0x0804df0c 0x0804df0c 0x000f4 0x000f4 R   0x1
    
     Section to Segment mapping:
      Segment Sections...
       00
       01     .interp
       02     .interp .note.ABI-tag .note.SuSE .hash .gnu.hash .dynsym .dynstr .gnu.version .gnu.version_r .rel.dyn .rel.plt .ini
       03     .ctors .dtors .jcr .dynamic .got .got.plt .data .bss
       04     .dynamic
       05     .note.ABI-tag
       06     .note.SuSE
       07
       08     .ctors .dtors .jcr .dynamic .got
    """


class ElfSectionHeadersSection(object):
    start_line = "Section Headers:"
    readelf_option = '--section-headers'

    # note: the first line starting with "There are... " only exist if that
    # option is invoked alone. when invoked with other options, The section
    # starts with start_line

    # we need some sections to be able to et anything
    needed_sections = ['.debug_info', '.debug_line', '.symtab', '.dynsym', '.dynstr']
    """
    $ readelf --wide --section-headers tests/dependencies-testfiles/elf/ssdeep.i686  | more
    There are 39 section headers, starting at offset 0xf5ec:
    
    Section Headers:
      [Nr] Name              Type            Addr     Off    Size   ES Flg Lk Inf Al
      [ 0]                   NULL            00000000 000000 000000 00      0   0  0
      [ 1] .interp           PROGBITS        08048154 000154 000013 00   A  0   0  1
      [ 2] .note.ABI-tag     NOTE            08048168 000168 000020 00   A  0   0  4
      [ 3] .note.SuSE        NOTE            08048188 000188 000018 00   A  0   0  4
      [ 4] .hash             HASH            080481a0 0001a0 000174 04   A  6   0  4
      [ 5] .gnu.hash         GNU_HASH        08048314 000314 000040 04   A  6   0  4
      [ 6] .dynsym           DYNSYM          08048354 000354 000360 10   A  7   1  4
      [ 7] .dynstr           STRTAB          080486b4 0006b4 0001e0 00   A  0   0  1
      [ 8] .gnu.version      VERSYM          08048894 000894 00006c 02   A  6   0  2
      [ 9] .gnu.version_r    VERNEED         08048900 000900 000040 00   A  7   1  4
      [10] .rel.dyn          REL             08048940 000940 000030 08   A  6   0  4
      [11] .rel.plt          REL             08048970 000970 000170 08   A  6  13  4
      [12] .init             PROGBITS        08048ae0 000ae0 000030 00  AX  0   0  4
      [13] .plt              PROGBITS        08048b10 000b10 0002f0 04  AX  0   0  4
      [14] .text             PROGBITS        08048e00 000e00 00315c 00  AX  0   0 16
      [15] .fini             PROGBITS        0804bf5c 003f5c 00001c 00  AX  0   0  4
      [16] .rodata           PROGBITS        0804bf78 003f78 0008ec 00   A  0   0  4
      [17] .eh_frame         PROGBITS        0804c864 004864 000004 00   A  0   0  4
      [18] .ctors            PROGBITS        0804df0c 004f0c 000008 00  WA  0   0  4
      [19] .dtors            PROGBITS        0804df14 004f14 000008 00  WA  0   0  4
      [20] .jcr              PROGBITS        0804df1c 004f1c 000004 00  WA  0   0  4
      [21] .dynamic          DYNAMIC         0804df20 004f20 0000d0 08  WA  7   0  4
      [22] .got              PROGBITS        0804dff0 004ff0 000004 04  WA  0   0  4
      [23] .got.plt          PROGBITS        0804dff4 004ff4 0000c4 04  WA  0   0  4
      [24] .data             PROGBITS        0804e0b8 0050b8 00000c 00  WA  0   0  4
      [25] .bss              NOBITS          0804e0e0 0050c4 001014 00  WA  0   0 32
      [26] .comment          PROGBITS        00000000 0050c4 0001f0 00      0   0  1
      [27] .debug_aranges    PROGBITS        00000000 0052b8 000190 00      0   0  8
      [28] .debug_pubnames   PROGBITS        00000000 005448 0003ae 00      0   0  1
      [29] .debug_info       PROGBITS        00000000 0057f6 00439a 00      0   0  1
      [30] .debug_abbrev     PROGBITS        00000000 009b90 001209 00      0   0  1
      [31] .debug_line       PROGBITS        00000000 00ad99 0011c4 00      0   0  1
      [32] .debug_frame      PROGBITS        00000000 00bf60 000618 00      0   0  4
      [33] .debug_str        PROGBITS        00000000 00c578 000a6c 01  MS  0   0  1
      [34] .debug_loc        PROGBITS        00000000 00cfe4 002122 00      0   0  1
      [35] .debug_ranges     PROGBITS        00000000 00f108 000388 00      0   0  8
      [36] .shstrtab         STRTAB          00000000 00f490 00015c 00      0   0  1
      [37] .symtab           SYMTAB          00000000 00fc04 000bc0 10     38  83  4
      [38] .strtab           STRTAB          00000000 0107c4 0008b0 00      0   0  1
    Key to Flags:
      W (write), A (alloc), X (execute), M (merge), S (strings)
      I (info), L (link order), G (group), x (unknown)
      O (extra OS processing required) o (OS specific), p (processor specific)
    """
    # if we do not have debug info and debug line we are not able to get mucho
    pass


class ElfVersionSymbolsSection(object):
    start_line = 'Version symbols section'
    readelf_option = '--version-info'
    """
    $ readelf --wide --version-info  tests/dependencies-testfiles/elf/ssdeep.i686
    
    Version symbols section '.gnu.version' contains 54 entries:
     Addr: 0000000008048894  Offset: 0x000894  Link: 6 (.dynsym)
      000:   0 (*local*)       2 (GLIBC_2.0)     2 (GLIBC_2.0)     2 (GLIBC_2.0)
      004:   2 (GLIBC_2.0)     2 (GLIBC_2.0)     0 (*local*)       2 (GLIBC_2.0)
      008:   2 (GLIBC_2.0)     2 (GLIBC_2.0)     2 (GLIBC_2.0)     2 (GLIBC_2.0)
      00c:   2 (GLIBC_2.0)     2 (GLIBC_2.0)     2 (GLIBC_2.0)     2 (GLIBC_2.0)
      010:   2 (GLIBC_2.0)     2 (GLIBC_2.0)     2 (GLIBC_2.0)     2 (GLIBC_2.0)
      014:   2 (GLIBC_2.0)     3 (GLIBC_2.3)     4 (GLIBC_2.1)     2 (GLIBC_2.0)
      018:   2 (GLIBC_2.0)     4 (GLIBC_2.1)     2 (GLIBC_2.0)     2 (GLIBC_2.0)
      01c:   2 (GLIBC_2.0)     2 (GLIBC_2.0)     2 (GLIBC_2.0)     2 (GLIBC_2.0)
      020:   4 (GLIBC_2.1)     2 (GLIBC_2.0)     2 (GLIBC_2.0)     4 (GLIBC_2.1)
      024:   2 (GLIBC_2.0)     2 (GLIBC_2.0)     2 (GLIBC_2.0)     2 (GLIBC_2.0)
      028:   2 (GLIBC_2.0)     2 (GLIBC_2.0)     2 (GLIBC_2.0)     2 (GLIBC_2.0)
      02c:   2 (GLIBC_2.0)     2 (GLIBC_2.0)     2 (GLIBC_2.0)     2 (GLIBC_2.0)
      030:   2 (GLIBC_2.0)     1 (*global*)      2 (GLIBC_2.0)     2 (GLIBC_2.0)
      034:   2 (GLIBC_2.0)     2 (GLIBC_2.0)
    
    Version needs section '.gnu.version_r' contains 1 entries:
     Addr: 0x0000000008048900  Offset: 0x000900  Link: 7 (.dynstr)
      000000: Version: 1  File: libc.so.6  Cnt: 3
      0x0010:   Name: GLIBC_2.1  Flags: none  Version: 4
      0x0020:   Name: GLIBC_2.3  Flags: none  Version: 3
      0x0030:   Name: GLIBC_2.0  Flags: none  Version: 2    
    """
    pass


class ElfDebugPubnamesSection(object):
    """
    $ readelf --wide --debug-dump=pubnames  tests/dependencies-testfiles/elf/ssdeep.i686   |less
    Contents of the .debug_pubnames section:
    
      Length:                              33
      Version:                             2
      Offset into .debug_info section:     0x0
      Size of area in .debug_info section: 141
    
        Offset      Name
        117                 _IO_stdin_used
      Length:                              23
      Version:                             2
      Offset into .debug_info section:     0x111
      Size of area in .debug_info section: 1676
    
        Offset      Name
        1285                main
      Length:                              111
      Version:                             2
      Offset into .debug_info section:     0x79d
      Size of area in .debug_info section: 1677
    
        Offset      Name
        1003                lsh_list_init
        1045                match_init
        1162                match_add
        1281                match_load
        1435                match_compare
        1579                match_pretty
      Length:                              28
      Version:                             2
      Offset into .debug_info section:     0xe2a
      Size of area in .debug_info section: 1171
    
        Offset      Name
        1003                hash_file
      Length:                              56
      Version:                             2
      Offset into .debug_info section:     0x12bd
      Size of area in .debug_info section: 2732
    
        Offset      Name
        1676                remove_double_dirs
        2129                process_normal
      Length:                              93
      Version:                             2
      Offset into .debug_info section:     0x1d69
      Size of area in .debug_info section: 1083
    
        Offset      Name
        787                 have_processed_dir
        863                 processing_dir
        944                 done_processing_dir
        1064                my_table
      Length:                              294
      Version:                             2
      Offset into .debug_info section:     0x21a4
      Size of area in .debug_info section: 2014
    """
    pass


class ElfRelocatablesSection(object):
    """
    $ readelf --relocs ssdeep.i686 | less
    
    Relocation section '.rel.dyn' at offset 0x940 contains 6 entries:
     Offset     Info    Type            Sym.Value  Sym. Name
    0804dff0  00000606 R_386_GLOB_DAT    00000000   __gmon_start__
    0804e0e0  00003005 R_386_COPY        0804e0e0   __progname
    0804e0f0  00003405 R_386_COPY        0804e0f0   optind
    0804e0f4  00003205 R_386_COPY        0804e0f4   stderr
    0804e100  00002f05 R_386_COPY        0804e100   stdout
    0804e104  00003505 R_386_COPY        0804e104   optarg
    
    Relocation section '.rel.plt' at offset 0x970 contains 46 entries:
     Offset     Info    Type            Sym.Value  Sym. Name
    0804e000  00000107 R_386_JUMP_SLOT   00000000   fileno
    0804e004  00000207 R_386_JUMP_SLOT   00000000   fputs
    0804e008  00000307 R_386_JUMP_SLOT   00000000   __errno_location
    0804e00c  00000407 R_386_JUMP_SLOT   00000000   strerror
    0804e010  00000507 R_386_JUMP_SLOT   00000000   __xstat
    0804e014  00000607 R_386_JUMP_SLOT   00000000   __gmon_start__
    0804e018  00000707 R_386_JUMP_SLOT   00000000   __lxstat
    0804e01c  00000807 R_386_JUMP_SLOT   00000000   strchr
    0804e020  00000907 R_386_JUMP_SLOT   00000000   strncpy
    0804e024  00000a07 R_386_JUMP_SLOT   00000000   putchar
    0804e028  00000b07 R_386_JUMP_SLOT   00000000   fgets
    0804e02c  00000c07 R_386_JUMP_SLOT   00000000   memset
    0804e030  00000d07 R_386_JUMP_SLOT   00000000   __strtol_internal
    0804e034  00000e07 R_386_JUMP_SLOT   00000000   __libc_start_main
    0804e038  00000f07 R_386_JUMP_SLOT   00000000   strrchr
    0804e03c  00001007 R_386_JUMP_SLOT   00000000   perror
    0804e040  00001107 R_386_JUMP_SLOT   00000000   readdir
    0804e044  00001207 R_386_JUMP_SLOT   00000000   free
    0804e048  00001307 R_386_JUMP_SLOT   00000000   opendir
    0804e04c  00001407 R_386_JUMP_SLOT   00000000   ioctl
    0804e050  00001507 R_386_JUMP_SLOT   00000000   realpath
    0804e054  00001607 R_386_JUMP_SLOT   00000000   fclose
    0804e058  00001707 R_386_JUMP_SLOT   00000000   getopt
    0804e05c  00001807 R_386_JUMP_SLOT   00000000   strlen
    0804e060  00001907 R_386_JUMP_SLOT   00000000   fopen
    0804e064  00001a07 R_386_JUMP_SLOT   00000000   printf
    0804e068  00001b07 R_386_JUMP_SLOT   00000000   closedir
    0804e06c  00001c07 R_386_JUMP_SLOT   00000000   fwrite
    0804e070  00001d07 R_386_JUMP_SLOT   00000000   fprintf
    0804e074  00001e07 R_386_JUMP_SLOT   00000000   strstr
    0804e078  00001f07 R_386_JUMP_SLOT   00000000   malloc
    0804e07c  00002007 R_386_JUMP_SLOT   00000000   fseeko
    0804e080  00002107 R_386_JUMP_SLOT   00000000   fputc
    0804e084  00002207 R_386_JUMP_SLOT   00000000   memmove
    0804e088  00002307 R_386_JUMP_SLOT   00000000   ftello
    0804e08c  00002407 R_386_JUMP_SLOT   00000000   strcat
    0804e090  00002507 R_386_JUMP_SLOT   00000000   getcwd
    0804e094  00002607 R_386_JUMP_SLOT   00000000   puts
    0804e098  00002707 R_386_JUMP_SLOT   00000000   sscanf
    0804e09c  00002807 R_386_JUMP_SLOT   00000000   __fxstat
    0804e0a0  00002907 R_386_JUMP_SLOT   00000000   strncmp
    0804e0a4  00002a07 R_386_JUMP_SLOT   00000000   vfprintf
    0804e0a8  00002b07 R_386_JUMP_SLOT   00000000   fread
    0804e0ac  00002c07 R_386_JUMP_SLOT   00000000   snprintf
    0804e0b0  00002d07 R_386_JUMP_SLOT   00000000   __strdup
    0804e0b4  00002e07 R_386_JUMP_SLOT   00000000   exit
    """
    pass
