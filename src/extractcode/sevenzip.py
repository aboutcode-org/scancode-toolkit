#
# Copyright (c) 2017 nexB Inc. and others. All rights reserved.
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
from __future__ import print_function
from __future__ import unicode_literals

from collections import defaultdict
import io
import logging
import os
import re

from commoncode  import command
from commoncode.system import on_windows
import extractcode
from extractcode import ExtractErrorFailedToExtract
from extractcode import ExtractWarningIncorrectEntry
from plugincode.location_provider import get_location


"""
Low level support for p/7zip-based archive extraction.
"""

logger = logging.getLogger(__name__)

TRACE = False

if TRACE:
    import sys
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)


# keys for plugin-provided locations
EXTRACTCODE_7ZIP_LIBDIR = 'extractcode.sevenzip.libdir'
EXTRACTCODE_7ZIP_EXE = 'extractcode.sevenzip.exe'


sevenzip_errors = [
    ('unsupported method', 'Unsupported archive or broken archive'),
    ('wrong password', 'Password protected archive, unable to extract'),
    # not being able to open an archive is not an error condition for now
    ('can not open file as archive', None),
    ]

UNKNOWN_ERROR = 'Unknown extraction error'


def get_7z_errors(stdout):
    """
    Return error messages extracted from a 7zip command output stdout string.
    This maps errors found in stdout to error message.
    """
    # FIXME: we should use only one pass over stdout for errors and warnings
    if not stdout or not stdout.strip():
        return

    find_7z_errors = re.compile('^Error:(.*)$',
                                re.MULTILINE | re.DOTALL).findall

    stdlow = stdout.lower()
    for err, msg in sevenzip_errors:
        if err in stdlow:
            return msg

    file_errors = find_7z_errors(stdout)
    if file_errors:
        return ' '.join(file_errors.strip('"\' ')).strip()


def get_7z_warnings(stdout):
    """
    Return a dict path->warning_message of 7zip warnings extracted from a
    stdout text.
    """
    # FIXME: we should use only one pass over stdout for errors and warnings
    cannot_open = 'can not open output file'
    msg_len = len(cannot_open) + 1
    warnings = defaultdict(list)
    for line in stdout.splitlines(False):
        if cannot_open in line.lower():
            path = line[msg_len:]
            if cannot_open not in warnings[path]:
                warnings[path].append(cannot_open)

    # collect warnings
    warning_messages = []
    for pathname, messages in warnings.items():
        msg = pathname + ': ' + '\n'.join(messages.strip('\' "'))
        if msg not in warning_messages:
            warning_messages.append(msg)
    return warning_messages


def list_extracted_7z_files(stdout):
    """
    List all files extracted by 7zip based on the stdout analysis.
    Based on 7zip Client7z.cpp:
        static const char *kExtractingString =  "Extracting  ";
    """
    # FIXME: handle Unicode paths with 7zip command line flags
    get_file_list = re.compile('Extracting  ' + '(.*)$', re.M).findall
    return get_file_list(stdout)


def is_rar(location):
    """
    Return True if the file at location is a RAR archive.
    """
    if not os.path.exists(location):
        return
    from typecode import contenttype
    T = contenttype.get_type(location)
    return T.filetype_file.lower().startswith('rar archive')


def extract(location, target_dir, arch_type='*'):
    """
    Extract all files from a 7zip-supported archive file at location in the
    target_dir directory. Return a list of warning messages.
    Raise exception on errors.

    `arch_type` is the type of 7zip archive passed to the -t 7zip option. Can be
    None.
    """
    assert location
    assert target_dir
    abs_location = os.path.abspath(os.path.expanduser(location))
    abs_target_dir = os.path.abspath(os.path.expanduser(target_dir))

    if is_rar(location):
        raise ExtractErrorFailedToExtract('RAR extraction disactivated')

    # note: there are some issues with the extraction of debian .deb ar files
    # see sevenzip bug http://sourceforge.net/p/sevenzip/bugs/1472/

    # 7z arguments
    extract = 'x'
    yes_to_all = '-y'

    # NB: we use t* to ensure that all archive types are honored
    if not arch_type:
        arch_type = ''
    else:
        arch_type = '-t' + arch_type

    # pass an empty password  so that extraction with passwords WILL fail
    password = '-p'

    # renaming may not behave the same way on all OSes in particular Mac and Windows
    auto_rename_dupe_names = '-aou'

    # These things do not work well with p7zip for now:
    # - ensure that we treat the FS as case insensitive even if it is
    #   this ensure we have consistent names across OSes
    #   case_insensitive = '-ssc-'
    # - force any console output to be UTF-8 encoded
    #   TODO: add this may be for a UTF output on Windows only
    #   output_as_utf = '-sccUTF-8'
    #   working_tmp_dir = '-w<path>'

    # NB: we force running in the GMT timezone, because 7z is unable to set
    # the TZ correctly when the archive does not contain TZ info. This does
    # not work on Windows, because 7z is not using the TZ env var there.
    timezone = os.environ.update({'TZ': 'GMT'})

    # Note: 7z does extract in the current directory so we cwd to the target dir first
    args = [
        extract,
        yes_to_all,
        auto_rename_dupe_names,
        arch_type,
        abs_location,
        password
    ]

    lib_dir = get_location(EXTRACTCODE_7ZIP_LIBDIR)
    cmd_loc = get_location(EXTRACTCODE_7ZIP_EXE)

    rc, stdout, stderr = command.execute2(
        cmd_loc=cmd_loc,
        args=args,
        lib_dir=lib_dir,
        cwd=abs_target_dir,
        env=timezone,
    )

    if rc != 0:
        if TRACE:
            logger.debug('extract failure: {rc}\nstderr: {stderr}\nstdout: {stdout}\n'.format(**locals()))
        error = get_7z_errors(stdout) or UNKNOWN_ERROR
        raise ExtractErrorFailedToExtract(error)

    extractcode.remove_backslashes_and_dotdots(abs_target_dir)
    return get_7z_warnings(stdout)


def list_entries(location, arch_type='*'):
    """
    List entries from a 7zip-supported archive file at location.
    Yield Entry tuples.
    Use the -t* 7z cli type option or the provided arch_type 7z type (can be
    None).
    """
    assert location
    abs_location = os.path.abspath(os.path.expanduser(location))

    if is_rar(location):
        return []

    # 7z arguments
    listing = 'l'

    # NB: we use t* to ensure that all archive types are honored
    if not arch_type:
        arch_type = ''
    else:
        arch_type = '-t' + arch_type

    # pass an empty password  so that extraction with passwords WILL fail
    password = '-p'
    tech_info = '-slt'

    output_as_utf = ''
    if on_windows:
        output_as_utf = '-sccUTF-8'

    # NB: we force running in the GMT timezone, because 7z is unable to set
    # the TZ correctly when the archive does not contain TZ info. This does
    # not work on Windows, because 7z is not using the TZ env var there.
    timezone = os.environ.update({'TZ': 'GMT'})

    args = [
        listing,
        tech_info,
        arch_type,
        output_as_utf,
        abs_location,
        password,
    ]

    lib_dir = get_location(EXTRACTCODE_7ZIP_LIBDIR)
    cmd_loc = get_location(EXTRACTCODE_7ZIP_EXE)

    rc, stdout, _stderr = command.execute2(
        cmd_loc=cmd_loc,
        args=args,
        lib_dir=lib_dir,
        env=timezone,
        to_files=True)

    if rc != 0:
        # FIXME: this test is useless
        _error = get_7z_errors(stdout) or UNKNOWN_ERROR

    # the listing was produced as UTF on windows to avoid damaging binary
    # paths in console outputs
    utf = bool(output_as_utf)

    return parse_7z_listing(stdout, utf)


def as_entry(infos):
    """
    Return an Entry built from 7zip path data.
    """
    e = extractcode.Entry()
    e.path = infos.get('Path')
    e.size = infos.get('Size', 0)
    e.packed_size = infos.get('Packed Size', 0)
    e.date = infos.get('Modified', 0)
    e.is_dir = infos.get('Folder', False) == '+'
    e.is_file = not e.is_dir
    e.is_broken_link = False
    e.mode = infos.get('Mode', '')
    e.user = infos.get('User')
    e.group = infos.get('Group')
    e.is_special = False
    e.is_hardlink = False
    sl = infos.get('Symbolic Link')
    if sl:
        e.is_symlink = True
        e.link_target = sl
    hl = infos.get('Hard Link')
    if hl:
        e.is_hardlink = True
        e.link_target = hl
    if sl and hl:
        raise ExtractWarningIncorrectEntry('A Symlink cannot be a hardlink too')
    e.linkcount = infos.get('Links', 0)
    e.host = infos.get('Host OS')
    e.comment = infos.get('Comment')
    e.encrypted = infos.get('Encrypted')
    return e


def parse_7z_listing(location, utf=False):
    """
    Parse a long format 7zip listing and return an iterable of entry.

    The 7zip -slt format is:
    - copyright and version details
    - '--' line
        - archive header info, varying based on the archive types and subtype
              - lines of key=value pairs
              - Errors: followed by one or more message lines
              - Warnings: followed by one or more message lines
              - Open Warning: : followed by one or more message lines
        - sometimes a '---' line
    - blank line
    - '----------' line
    - for each archive member:
      - lines of either
          - key = value pairs
          - Errors: followed by one or more message lines
          - Warnings: followed by one or more message lines
          - Open Warning: : followed by one or more message lines
      - blank line
    - two blank lines
    - footer sometimes with lines with summary stats
        such as Warnings: 1 Errors: 1
    - a line with two or more dashes or an empty line
    """
    if utf:
        # read to unicode
        with io.open(location, 'r', encoding='utf-8') as listing:
            text = listing.read()
            text = text.replace(u'\r\n', u'\n')
    else:
        # read to bytes
        with io.open(location, 'rb') as listing:
            text = listing.read()

    header_sep = utf and u'\n----------\n' or b'\n----------\n'
    header_tail = re.split(header_sep, text, flags=re.MULTILINE)
    if len(header_tail) != 2:
        # we more than one a header, confusion entails.
        raise ExtractWarningIncorrectEntry('Incorrect 7zip listing with multiple headers')

    if len(header_tail) == 1:
        # we have only a header, likely an error condition or an empty archive
        return []

    empty = utf and u'' or b''

    _header, body = header_tail
    body_sep = utf and u'\n\n\n' or b'\n\n\n'
    body_and_footer = re.split(body_sep, body, flags=re.MULTILINE)
    no_footer = len(body_and_footer) == 1
    multiple_footers = len(body_and_footer) > 2
    _footer = empty
    if no_footer:
        body = body_and_footer[0]
    elif multiple_footers:
        raise ExtractWarningIncorrectEntry('Incorrect 7zip listing with multiple footers')
    else:
        body, _footer == body_and_footer

    # FIXME: do something with header and footer?

    entries = []
    path_sep = utf and u'\n\n' or b'\n\n'
    paths = re.split(path_sep, body, flags=re.MULTILINE)
    msg_sep = utf and u':' or b':'
    equal_sep = utf and u'=' or b'='
    for path in paths:
        is_err = False
        errors = []
        infos = {}
        lines = path.splitlines(False)
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith(('Open Warning:', 'Errors:', 'Warnings:')):
                is_err = True
                messages = line.split(msg_sep, 1)
                errors.append(messages)
                continue
            if equal_sep not in line and is_err:
                # not a key = value line, an error message
                errors.append(line)
                continue
            parts = line.split(equal_sep, 1)
            if len(parts) != 2:
                raise ExtractWarningIncorrectEntry('Incorrect 7zip listing line with no key=value')
            is_err = False
            key, value = parts
            assert key not in infos, 'Duplicate keys in 7zip listing'
            infos[key.strip()] = value.strip() or empty
        if infos:
            entries.append(as_entry(infos))

    return entries
