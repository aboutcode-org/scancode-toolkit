#
# Copyright (c) nexB Inc. and others. All rights reserved.
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
import pprint
import re

import attr

from commoncode  import command
from commoncode import fileutils
from commoncode import paths
from commoncode.system import is_case_sensitive_fs
from commoncode.system import on_mac
from commoncode.system import on_macos_14_or_higher
from commoncode.system import on_windows
from commoncode.system import py3
from commoncode import text

import extractcode
from extractcode import ExtractErrorFailedToExtract
from extractcode import ExtractWarningIncorrectEntry

if py3:
    from shlex import quote as shlex_quote  # NOQA
else:
    from pipes import quote as shlex_quote  # NOQA


"""
Low level support for p/7zip-based archive extraction.
"""

logger = logging.getLogger(__name__)

TRACE = False
TRACE_DEEP = False
TRACE_ENTRIES = False

if TRACE or TRACE_DEEP or TRACE_ENTRIES:
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
    ('no files to process', 'Empty archive or incorrect arguments'),
]

UNKNOWN_ERROR = 'Unknown extraction error'


def get_7z_errors(stdout, stderr):
    """
    Return error messages extracted from a 7zip command output `stdout` and
    `stderr` strings. This maps errors found in `stdout` to human-readable error
    messages.
    """
    # FIXME: we should use only one pass over stdout for errors and warnings
    if not stdout or not stdout.strip():
        return

    # ERROR: Can not create symbolic link : A required privilege is not held by the client. : .\2-SYMTYPE
    find_7z_errors = re.compile('^Error:(.*)$', re.MULTILINE | re.DOTALL | re.IGNORECASE).findall  # NOQA

    stdlow = stderr.lower()
    for err, msg in sevenzip_errors:
        if err in stdlow:
            return msg

    stdlow = stdout.lower()
    for err, msg in sevenzip_errors:
        if err in stdlow:
            return msg

    file_errors = find_7z_errors(stderr)
    if file_errors:
        return ' '.join(fe.strip('"\' ') for fe in file_errors).strip()

    file_errors = find_7z_errors(stdout)
    if file_errors:
        return ' '.join(fe.strip('"\' ') for fe in file_errors).strip()


def get_7z_warnings(stdout):
    """
    Return a mapping of {path: warning_message} of 7zip warnings extracted from a
    `stdout` text.
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

    return warnings


def convert_warnings_to_list(warnings):
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
    get_file_list = re.compile('Extracting  ' + '(.*)$', re.MULTILINE).findall  # NOQA
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


def get_bin_locations():
    """
    Return a tuple of (lib_dir, cmd_loc) for 7zip loaded from plugin-provided path.
    """
    from plugincode.location_provider import get_location

    # get paths from plugins
    lib_dir = get_location(EXTRACTCODE_7ZIP_LIBDIR)
    cmd_loc = get_location(EXTRACTCODE_7ZIP_EXE)
    return lib_dir, cmd_loc


def extract(location, target_dir, arch_type='*', file_by_file=on_mac, skip_symlinks=True):
    """
    Extract all files from a 7zip-supported archive file at location in the
    target_dir directory. `skip_symlinks` by default.
    Return a list of warning messages.
    Raise exception on errors.

    The extraction will either be done all-files-at-once (default on most OSes)
    or one-file-at-a-time after collecting a directory listing (for some
    problematic OSes such as recent macOS)

    `arch_type` is the type of 7zip archive passed to the -t 7zip option. Can be
    None.
    """
    assert location
    abs_location = os.path.abspath(os.path.expanduser(location))
    if not os.path.exists(abs_location):
        raise ExtractErrorFailedToExtract(
            'The system cannot find the path specified: {}'.format(repr(abs_location)))

    if is_rar(location):
        raise ExtractErrorFailedToExtract(
            'RAR extraction disactivated: {}'.format(repr(location)))

    assert target_dir
    abs_target_dir = os.path.abspath(os.path.expanduser(target_dir))
    if not os.path.exists(abs_target_dir):
        raise ExtractErrorFailedToExtract(
            'The system cannot find the target path specified: {}'.format(repr(target_dir)))

    extractor = extract_file_by_file if file_by_file else extract_all_files_at_once
    return extractor(
        location=abs_location,
        target_dir=abs_target_dir,
        arch_type=arch_type,
        skip_symlinks=skip_symlinks)


def extract_all_files_at_once(location, target_dir, arch_type='*', skip_symlinks=True):
    """
    Extract all files from a 7zip-supported archive file at `location` in the
    `target_dir` directory.

    Return a list of warning messages.
    Raise exception on errors.

    `arch_type` is the type of 7zip archive passed to the -t 7zip option. Can be
    None.
    """
    abs_location = os.path.abspath(os.path.expanduser(location))
    abs_target_dir = os.path.abspath(os.path.expanduser(target_dir))

    # note: there are some issues with the extraction of debian .deb ar files
    # see sevenzip bug http://sourceforge.net/p/sevenzip/bugs/1472/
    ex_args = build_7z_extract_command(
        location=location, target_dir=target_dir, arch_type=arch_type)

    rc, stdout, stderr = command.execute2(**ex_args)

    if rc != 0:
        if TRACE:
            logger.debug(
                'extract: failure: {rc}\n'
                'stderr: {stderr}\n'
                'stdout: {stdout}\n'.format(**locals()))
        error = get_7z_errors(stdout, stderr) or UNKNOWN_ERROR
        raise ExtractErrorFailedToExtract(error)

    extractcode.remove_backslashes_and_dotdots(target_dir)
    return convert_warnings_to_list(get_7z_warnings(stdout))


def build_7z_extract_command(location, target_dir, single_entry=None, arch_type='*'):
    """
    Return a mapping of 7z command line aguments to extract the archive at
    `location` to `target_dir`.

    If `single_entry` contains an Entry, provide the command to extract only
    that single entry "path" in the current directory without any leading path.
    """

    # 7z arguments
    if single_entry:
        # do not use full path
        extract = 'e'
    else:
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

    # Ensure that we treat the FS as case insensitive if that's what it is
    # -ssc    Set case-sensitive mode. It's default for Posix/Linux systems.
    # -ssc-    Set case-insensitive mode. It's default for Windows systems.
    # historically, this was not needed on macOS, but now APFS is case
    # insentitive as a default
    if on_windows or on_macos_14_or_higher or not is_case_sensitive_fs:
        case_sensitive = '-ssc-'
    else:
        case_sensitive = '-ssc'

    # These does not work well with p7zip for now:
    # - force any console output to be UTF-8 encoded
    #   TODO: add this may be for a UTF output on Windows only
    #   output_as_utf = '-sccUTF-8'
    #   working_tmp_dir = '-w<path>'

    # NB: we force running in the GMT timezone, because 7z is unable to set
    # the TZ correctly when the archive does not contain TZ info. This does
    # not work on Windows, because 7z is not using the TZ env var there.
    timezone = dict(os.environ)
    timezone.update({u'TZ': u'GMT'})
    timezone = command.get_env(timezone)
    # Note: 7z does extract in the current directory so we cwd to the target dir first
    args = [
        extract,
        yes_to_all,
        case_sensitive,
        auto_rename_dupe_names,
        arch_type,
        password,
        '--',
        location,
    ]

    if single_entry:
        args += [shlex_quote(single_entry.path)]

    lib_dir, cmd_loc = get_bin_locations()

    ex_args = dict(
        cmd_loc=cmd_loc,
        args=args,
        lib_dir=lib_dir,
        cwd=target_dir,
        env=timezone,
    )

    if TRACE:
        logger.debug('extract: args:')
        pprint.pprint(ex_args)

    return ex_args


def extract_file_by_file(location, target_dir, arch_type='*', skip_symlinks=True):
    """
    Extract all files using a one-by-one process from a 7zip-supported archive
    file at location in the `target_dir` directory.

    Return a list of warning messages if any or an empty list.
    Raise exception on errors.

    `arch_type` is the type of 7zip archive passed to the -t 7zip option.
    Can be None.
    """
    abs_location = os.path.abspath(os.path.expanduser(location))
    abs_target_dir = os.path.abspath(os.path.expanduser(target_dir))

    entries, errors_msgs = list_entries(location, arch_type)
    entries = list(entries)

    # Determine if we need a one-by-one approach: technically the aproach is to
    # check if we have files that are in the same dir and have the same name
    # when the case is ignored. We take a simpler approach: we check if all
    # paths are unique when we ignore the case: for that we only check that the
    # length of two paths sets are the same: one set as-is and the other
    # lowercased.

    paths_as_is = set(e.path for e in entries)
    paths_no_case = set(p.lower() for p in paths_as_is)
    need_by_file = len(paths_as_is) != len(paths_no_case)

    if not need_by_file:
        # use regular extract
        return extract_all_files_at_once(
            location=location,
            target_dir=target_dir,
            arch_type=arch_type)

    # now we are extracting one file at a time. this is a tad painful because we
    # are dealing with a full command execution at each time.

    errors = {}
    warnings = {}
    tmp_dir = fileutils.get_temp_dir(prefix='extractcode-extract-')
    for i, entry in enumerate(entries):

        if not entry.is_file:
            continue

        tmp_extract_dir = os.path.join(tmp_dir, str(i))
        fileutils.create_dir(tmp_extract_dir)

        ex_args = build_7z_extract_command(
            location=location,
            target_dir=tmp_extract_dir,
            single_entry=entry,
            arch_type=arch_type,
        )
        rc, stdout, stderr = command.execute2(**ex_args)

        error = get_7z_errors(stdout, stderr)
        if error or rc != 0:
            error = error or UNKNOWN_ERROR
            if TRACE:
                logger.debug(
                    'extract: failure: {rc}\n'
                    'stderr: {stderr}\nstdout: {stdout}'.format(**locals()))
            errors[entry.path] = error
            continue

        # these are all for a single file path
        warns = get_7z_warnings(stdout) or {}
        wmsg = '\n'.join(warns.values())
        if wmsg:
            if entry.path in warnings:
                warnings[entry.path] += '\n' + wmsg
            else:
                warnings[entry.path] = wmsg

        # finally move that extracted file to its target location, possibly renamed
        source_file_name = fileutils.file_name(entry.path)
        source_file_loc = os.path.join(tmp_extract_dir, source_file_name)
        if not os.path.exists(source_file_loc):
            if entry.path in errors:
                errors[entry.path] += '\nNo file name extracted.'
            else:
                errors[entry.path] = 'No file name extracted.'
            continue

        safe_path = paths.safe_path(entry.path, posix=True)
        target_file_loc = os.path.join(target_dir, safe_path)
        target_file_dir = os.path.dirname(target_file_loc)
        fileutils.create_dir(target_file_dir)

        unique_target_file_loc = extractcode.new_name(target_file_loc, is_dir=False)

        if TRACE:
            logger.debug('extract: unique_target_file_loc: from {} to {}'.format(
                target_file_loc, unique_target_file_loc))

        if os.path.isfile(source_file_loc):
            fileutils.copyfile(source_file_loc, unique_target_file_loc)
        else:
            fileutils.copytree(source_file_loc, unique_target_file_loc)

    extractcode.remove_backslashes_and_dotdots(abs_target_dir)
    if errors:
        raise ExtractErrorFailedToExtract(errors)

    return convert_warnings_to_list(warnings)


def list_entries(location, arch_type='*'):
    """
    Return a tuple of (iterator of Entry, error_messages). The generator contains
    each entry found in a 7zip-supported archive file at `location`. Use the
    provided 7zip `arch_type` CLI archive type code (e.g. with the "-t* 7z" cli
    type option) (can be None).
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
    timezone = dict(os.environ)
    timezone.update({u'TZ': u'GMT'})
    timezone = command.get_env(timezone)

    args = [
        listing,
        tech_info,
        arch_type,
        output_as_utf,
        password,
        '--',
        abs_location,
    ]

    lib_dir, cmd_loc = get_bin_locations()

    rc, stdout, stderr = command.execute2(
        cmd_loc=cmd_loc,
        args=args,
        lib_dir=lib_dir,
        env=timezone,
        to_files=True)

    if TRACE:
        logger.debug(
            'list_entries: rc: {rc}\n'
            'stderr: file://{stderr}\n'
            'stdout: file://{stdout}\n'.format(**locals()))

    error_messages = []
    if rc != 0:
        error_messages = get_7z_errors(stdout, stderr) or UNKNOWN_ERROR

    # the listing was produced as UTF on windows to avoid damaging binary
    # paths in console outputs
    utf = bool(output_as_utf)

    return parse_7z_listing(stdout, utf), error_messages


def parse_7z_listing(location, utf=False):
    """
    Return a list Entry objects from parsing a long format 7zip listing from a
    file at `location`.

    If `utf` is True or if on Python 3, the console output will treated as
    utf-8-encoded text. Otherwise it is treated as bytes.

    The 7zip -slt format looks like this:

    1. a header with:
    - copyright and version details
    - '--' line
        - archive header info, varying based on the archive types and subtype
              - lines of key=value pairs
              - ERRORS: followed by one or more message lines
              - WARNINGS: followed by one or more message lines
    - blank line

    2. blocks of path aka. entry data, one for each path with:

    - '----------' line once as the indicator of path blocks starting
    - for each archive member:
      - lines of either
          - key = value pairs, with a possible twist that the Path may
            contain a line return since a filename may. The first key is the Path.
          - Errors: followed by one or more message lines
          - Warnings: followed by one or more message lines
          - Open Warning: : followed by one or more message lines
      - blank line

    3. a footer
    - blank line
    - footer sometimes with lines with summary stats
        such as Warnings: 1 Errors: 1
    - a line with two or more dashes or an empty line

    We ignore the header and footer in a listing.
    """

    if utf or py3:
        # read to unicode
        with io.open(location, 'r', encoding='utf-8') as listing:
            text = listing.read()
            text = text.replace(u'\r\n', u'\n')

        end_of_header = u'----------\n'
        path_key = u'Path'
        kv_sep = u'='
        path_blocks_sep = u'\n\n'
        line_sep = u'\n'

    else:
        # read to bytes
        with io.open(location, 'rb') as listing:
            text = listing.read()
            text = text.replace(b'\r\n', b'\n')

        end_of_header = b'----------\n'
        path_key = b'Path'
        kv_sep = b'='
        path_blocks_sep = b'\n\n'
        line_sep = b'\n'

    if TRACE:
        logger.debug('parse_7z_listing: initial text: type: ' + repr(type(text)))
        print('--------------------------------------')
        print(text)
        print('--------------------------------------')

    # for now we ignore the header
    _header, _, paths = text.rpartition(end_of_header)

    if not paths:
        # we have only a header, likely an error condition or an empty archive
        return []

    # each block representing one path or file:
    # - starts with a "Path = <some/path>" key/value
    # - continues with key = value pairs each on a single line
    #   (unless there is a \n in file name which is an error condition)
    # - ends with an empty line
    # then we have a global footer

    path_blocks = [pb for pb in paths.split(path_blocks_sep) if pb and path_key in pb]

    entries = []

    for path_block in path_blocks:
        # we ignore empty lines as well as lines that do not contain a key
        lines = [line.strip() for line in path_block.splitlines(False) if line.strip()]
        if not lines:
            continue
        # we have a weird case of path with line returns in the file name
        # we concatenate these in the first Path line
        while len(lines) > 1 and lines[0].startswith(path_key) and kv_sep not in lines[1]:
            first_line = lines[0]
            second_line = lines.pop(1)
            first_line = line_sep.join([first_line, second_line])
            lines[0] = first_line

        dangling_lines = [line  for line in lines if kv_sep not in line]
        entry_errors = []
        if dangling_lines:
            emsg = 'Invalid 7z listing path block missing "=" as key/value separator: {}'.format(repr(path_block))
            entry_errors.append(emsg)

        entry_attributes = {}
        key_lines = [line  for line in lines if kv_sep in line]
        for line in key_lines:
            k, _, v = line.partition(kv_sep)
            k = k.strip()
            v = v.strip()
            entry_attributes[k] = v

        entries.append(Entry.from_dict(infos=entry_attributes, errors=entry_errors))

    if TRACE_ENTRIES:
        logger.debug('parse_7z_listing: entries# {}\n'.format(len(entries)))
        for entry in entries:
            logger.debug('    ' + repr(entry.to_dict()))

    return entries


def filter_entries(entries):
    """
    Given an iterable of entries, return two list of entries:
    a list of valid entries that can be extracted and a list entries that cannot
    be extracted.
    """
    # extractible


@attr.s(slots=True)
class Entry(object):
    """
    Represent an Archive entry for a directory, file or link in an archive
    with its path and attributes.
    """
    # the actual posix path as-is as in the archive (relative, absolute, etc)
    path = attr.ib()
    # bytes
    size = attr.ib(default=0)
    date = attr.ib(default=None)
    is_file = attr.ib(default=True)
    is_dir = attr.ib(default=False)
    is_special = attr.ib(default=False)
    is_hardlink = attr.ib(default=False)
    is_symlink = attr.ib(default=False)
    is_broken_link = attr.ib(default=False)
    link_target = attr.ib(default=None)
    errors = attr.ib(default=attr.Factory(list))

    def to_dict(self, full=False):
        data = attr.asdict(self)
        # data.pop('errors', None)
        if not full:
            data.pop('date', None)
        return data

    def has_illegal_path(self):
        return '\n' in self.path

    def is_relative_path(self):
        return '..' in self.path

    def is_empty(self):
        return not self.size

    @classmethod
    def from_dict(cls, infos, errors=None):
        """
        Return an Entry built from a 7zip path listing data in the `infos` mapping.
        """
        is_symlink = False
        is_hardlink = False
        link_target = None

        sl = infos.get('Symbolic Link')

        if sl:
            is_symlink = True
            link_target = sl

        hl = infos.get('Hard Link')
        if hl:
            is_hardlink = True
            link_target = hl

        if sl and hl:
            from pprint import pformat
            raise ExtractWarningIncorrectEntry(
                'A symlink cannot be also a hardlink: {}'.format(pformat(infos)))

        # depending on the type of arhcive the file vs dir flags are in
        # diiferent attributes :|
        is_dir = (
            # in some listings we have this: Mode = drwxrwxr-x
            infos.get('Mode', '').lower().startswith('d')
            or
            # in cpio and a few more we have a Folder attrib
            infos.get('Folder', '').startswith('+')
            or
            # in 7z listing we have this: Attributes = D_ drwxrwxr-x
            infos.get('Attributes', '').lower().startswith('d_')
        ) or False

        is_file = not is_dir

        e = cls(
            path=infos.get('Path'),
            size=infos.get('Size', 0),
            date=infos.get('Modified', None),
            is_dir=is_dir,
            is_file=is_file,
            is_symlink=is_symlink,
            is_hardlink=is_hardlink,
            link_target=link_target,
            errors=errors or [],
        )
        return e
