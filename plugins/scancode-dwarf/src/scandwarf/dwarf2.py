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
Functions to extract information from binary Elf files DWARF debug data from
the standard nm command output.
"""

from __future__ import absolute_import
from __future__ import print_function

from collections import namedtuple
import logging
import re

from commoncode import command
from plugincode.location_provider import get_location
from typecode import contenttype


# TODO: implement a plugin for this
SCANCODE_BINUTILS_NM_EXE = 'scancode.binutils.nm.exe'

logger = logging.getLogger(__name__)


################################################################
# NM PARSING
################################################################
# 0804871c<space>T<space>_init<tab>/usr/src//glibc-2.6.1/cc-nptl/csu/crti.S:15
def LINE_WITH_SOURCE_PATH():
    return re.compile(
    r'^'
    # the line starts with 8 or 16 hex chars
    r'([0-9a-fA-F]{8}|[0-9a-fA-F]{16})'
    r'\s'
    # type of lines/symbol
    r'(?P<type>[a-zA-Z])'
    r'\s'
    # symbol name
    r'(?P<symbol>.*)'
    # tab
    r'\t'
    # full path to source file
    r'(?P<path>.*)'
    r':'
    r'(?P<linenum>\d*)'
    r'$').match


def POSSIBLE_SOURCE_PATH():
    return re.compile(
    r'^'
    # the line starts with 8 or 16 hex chars
    r'([0-9a-fA-F]{8}|[0-9a-fA-F]{16})'
    r'\s'
    # type of lines/symbol
    r'(?P<type>[a-zA-Z])'
    r'\s'
    # symbol name which is a path possibly
    r'(?P<path>.*\.(c|cc|cpp|cxx|h|hh|hpp|hxx|i|m|y|s)?)'
    r'$', re.IGNORECASE).match


def call_nm(elffile):
    """
    Call nm and returns the returncode, and the filepaths containing the
    stdout and stderr.
    """
    logger.debug('Executing nm command on %(elffile)r' % locals())

    nm_command = get_location(SCANCODE_BINUTILS_NM_EXE)
    return command.execute2(
        cmd_loc=nm_command, 
        args=['-al', elffile], to_files=True)


Entry = namedtuple('Entry', ['type', 'symbol', 'path', 'linenum'])

def parse(location):
    """
    Yield Entry tuples from parsing the `nm` output file at `location`.
    """
    # do not report duplicate symbols
    seen = set()

    # We loop through each line passing control to a handler as needed
    with open(location, 'r') as lines:
        for line in lines:
            line = line.strip()
            if not line:
                continue

            withpath = LINE_WITH_SOURCE_PATH()(line)
            if withpath:
                logger.debug('Processing path line     : %(line)r' % locals())
                symbol_type = withpath.group('type')
                symbol = withpath.group('symbol')
                debug_path = withpath.group('path')
                lineno = withpath.group('linenum')
                entry = Entry(symbol_type, symbol, debug_path, lineno)
                if entry not in seen:
                    yield entry
                    seen.add(entry)
                continue

            possible_path = POSSIBLE_SOURCE_PATH()(line)
            if possible_path:
                logger.debug('Processing path-like line: %(line)r' % locals())
                symbol_type = possible_path.group('type')
                symbol = ''
                debug_path = possible_path.group('path')
                lineno = ''
                entry = Entry(symbol_type, symbol, debug_path, lineno)
                if entry not in seen:
                    yield entry
                    seen.add(entry)

# TODO: demangle symbols

def get_dwarfs(location):
    """
    Yield tuples with debug information extracted from the DWARF
    debug symbols. Return also the symbol type, the symbol value itself and
    the line number in the source code at where the symbol is used or defined.

    Yields this tuple:
        (symbol_type, symbol, path_to_source, symbol_source_line)
    """

    T = contenttype.get_type(location)
    if T.is_elf:
        rc, out, err = call_nm(location)
        if rc != 0:
            raise Exception(repr(open(err).read()))
        for res in parse(out):
            yield res
