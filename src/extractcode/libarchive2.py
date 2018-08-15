#
# Copyright (c) 2018 nexB Inc. and others. All rights reserved.
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
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from functools import partial
import locale
import logging
import os

from ctypes import c_char_p, c_wchar_p
from ctypes import c_int, c_longlong
from ctypes import c_size_t, c_ssize_t
from ctypes import c_void_p
from ctypes import POINTER
from ctypes import create_string_buffer

from commoncode import command
from commoncode import fileutils
from commoncode import paths

import extractcode
from extractcode import ExtractError
from extractcode import ExtractErrorPasswordProtected
from plugincode.location_provider import get_location

# Python 2 and 3 support
try:
    from os import fsencode
except ImportError:
    from backports.os import fsencode  # NOQA

logger = logging.getLogger(__name__)
DEBUG = False
# logging.basicConfig(level=logging.DEBUG)

"""
libarchive2 is a minimal and specialized wrapper around a vendored libarchive archive
extraction library. It only deals with archive extraction and does not know how to
create archives.

Its main purpose is to try hard to extract files from archives on multiple OSes and
makes some compromises in doing so:

- special files and links may be skipped entirely and not extracted at all.

- relative paths are resolved to ensure that files are always extracted under a root
  extraction directory.

- files and directories may be renamed if they are not unique (ignoring case) in
  their extraction directory.

- files and directories are renamed by "transliterating" their names to plain ASCII
  if their name contain non-ASCI characters.

- files and directories are renamed if they contain characters or names that are not
  portable on common OSes (e.g. COM1, ":", "*", etc)

- permissions and modes are ignored entirely when extracting files to esnure that
  extracted files are always readable.

It is inspired from several libarchive bindings such as libarchive_c and
python-libarchive for Python and other similar wrappers for Ruby such as
ffi-libarchive.
"""

# keys for plugin-provided locations
EXTRACTCODE_LIBARCHIVE_LIBDIR = 'extractcode.libarchive.libdir'
EXTRACTCODE_LIBARCHIVE_DLL = 'extractcode.libarchive.dll'


def load_lib():
    """
    Return the loaded libarchive shared library object from plugin provided or
    default "vendored" paths.
    """
    # get paths from plugins
    dll = get_location(EXTRACTCODE_LIBARCHIVE_DLL)
    libdir = get_location(EXTRACTCODE_LIBARCHIVE_LIBDIR)
    return command.load_shared_library(dll, libdir)


# NOTE: this is important to avoid timezone differences
os.environ['TZ'] = 'UTC'

# NOTE: this is important to avoid locale-specific errors on various OS
locale.setlocale(locale.LC_ALL, '')

# load and initialize the shared library
libarchive = load_lib()


def extract(location, target_dir):
    """
    Extract files from a libarchive-supported archive file at `location` in the
    `target_dir`.
    Return a list of warning messages if any or an empty list.
    Raise Exceptions on errors.
    """
    assert location
    assert target_dir
    abs_location = os.path.abspath(os.path.expanduser(location))
    abs_target_dir = os.path.abspath(os.path.expanduser(target_dir))
    warnings = []

    for entry in list_entries(abs_location):

        if entry and entry.warnings:
            if not entry.is_empty():
                entry_path = entry.path
                msgs = ['%(entry_path)r: ' % locals()]
            else:
                msgs = ['No path available: ']

            msgs.extend([w.strip('"\' ') for w in entry.warnings if w and w.strip('"\' ')])
            msgs = '\n'.join(msgs) or 'No message provided'

            if msgs not in warnings:
                warnings.append(msgs)

        if not entry.is_empty():
            if not (entry.isdir or entry.isfile):
                # skip special files and links
                # TODO: this could be made an argument
                continue
            _target_path = entry.write(abs_target_dir, transform_path=paths.safe_path)
    return warnings


def list_entries(location):
    """
    Return an archive entries list for the archive file at `location`.
    """
    assert location
    abs_location = os.path.abspath(os.path.expanduser(location))
    assert os.path.isfile(abs_location)

    # TODO: harden error handling
    with Archive(abs_location) as archive:
        for entry in archive:
            yield entry


class Archive(object):
    """
    Represent an iterable archive containing a list of Entry objects.

    Archive is designed to be used as a context manager with the "with" syntax:
        with Archive('some.tgz') as archive:
            for entry in archive:
                # dome something with entry
    """

    def __init__(self, location, uncompress=True, extract=True, block_size=10240):
        """
        Build an Archive object from file at `location`.

        If `uncompress` is True, the archive will be uncompressed first if compressed.
        (e.g. a tar.gz will be ungzipped).

        If `extract` is True, the archive will be extracted if this is an archive.
        (e.g. a cpio will be extracted).

        If both are True, the archive will be uncompressed then extracted as needed.
        (e.g. a tar.xz will be unxzed then untarred at once).
        """
        msg = 'At least one of `uncompress` or `extract` flag is required.'
        assert uncompress or extract, msg
        self.location = location
        self.uncompress = uncompress
        self.extract = extract
        self.block_size = block_size
        # pointer to the libarchive structure
        self.archive_struct = None

    def open(self):
        """
        Open the archive for reading.
        You must call close() when done to free up resources and avoid leaks.
        Or use instead the Archive class as a context manager with the "with" keyword.
        """
        # first close any existing opened struct for this file
        self.close()
        self.archive_struct = archive_reader()
        if self.uncompress:
            use_all_filters(self.archive_struct)
        if extract:
            use_all_formats(self.archive_struct)
        try:
            # TODO: ensure that we have proper exceptions raised?
            open_file(self.archive_struct, self.location, self.block_size)
        except:
            open_file_w(self.archive_struct, self.location, self.block_size)
        return self

    def close(self):
        """
        Release any memory held by the underlying librachive for this archive. You
        must call close() when done with an archive to free up resources and avoid
        leaks.
        """
        if self.archive_struct:
            free_archive(self.archive_struct)
            self.archive_struct = None

    def iter(self, verbose=False):
        """
        Yield Entry for this archive.
        """
        assert self.archive_struct, 'Archive must be used as a context manager.'
        entry_struct = new_entry()
        try:
            while True:
                entry = None
                warnings = []
                try:
                    r = next_entry(self.archive_struct, entry_struct)
                    if r == ARCHIVE_EOF:
                        return
                    entry = Entry(self, entry_struct)
                except ArchiveWarning, aw:
                    if not entry:
                        entry = Entry(self, entry_struct)
                    if aw.msg and aw.msg not in entry.warnings:
                        entry.warnings.append(aw.msg)

#                     msg = 'WARNING: '
#                     if aw.msg and aw.msg not in entry.warnings:
#                         msg += repr(aw.msg) + '\n'
#                     if verbose:
#                         msg += traceback.format_exc()
#                     warnings.append(msg % locals())
                finally:
                    if entry:
                        entry.warnings.extend(warnings)
                        yield entry
        finally:
            if entry_struct:
                free_entry(entry_struct)

    def __enter__(self):
        return self.open()

    def __exit__(self, _type, _value, _traceback):
        return self.close()

    def __iter__(self):
        return self.iter()


class Entry(object):
    """
    Represent an Archive entry which is either a file or a directory.

    The attribute names are loosely based on the stdlib module tarfile.Tarfile class
    attributes. Some attributes are not handled on purpose because they are never
    used: things such as modes/perms/users/groups are never restored by design to
    ensure extracted files are readable/writable and owned by the extracting user.
    """
    # TODO: users and groups may have some value for origin determination?

    def __init__(self, archive, entry_struct):
        self.archive = archive
        self.entry_struct = entry_struct

        self.filetype = None
        self.isfile = None
        self.isdir = None
        self.isblk = None
        self.ischr = None
        self.isfifo = None
        self.issock = None
        self.isspecial = None

        # bytes
        self.size = None
        # sec since epoch
        self.time = None

        # all paths are byte strings not unicode
        self.path = None

        self.issym = None
        self.symlink_path = None

        self.islnk = None
        self.hardlink_path = None

        # list of strings
        self.warnings = []

        if self.entry_struct:
            self.filetype = entry_type(self.entry_struct)
            self.isfile = self.filetype & AE_IFMT == AE_IFREG
            self.isdir = self.filetype & AE_IFMT == AE_IFDIR
            self.isblk = self.filetype & AE_IFMT == AE_IFBLK
            self.ischr = self.filetype & AE_IFMT == AE_IFCHR
            self.isfifo = self.filetype & AE_IFMT == AE_IFIFO
            self.issock = self.filetype & AE_IFMT == AE_IFSOCK
            self.isspecial = self.ischr or self.isblk or self.isfifo or self.issock
            self.size = entry_size(self.entry_struct) or 0
            self.time = entry_time(self.entry_struct) or 0
            self.path = self._path_bytes(entry_path, entry_path_w)
            self.issym = self.filetype & AE_IFMT == AE_IFLNK
            # FIXME: could there be cases with link path and symlink is False?
            if self.issym:
                self.symlink_path = self._path_bytes(symlink_path, symlink_path_w)
            self.hardlink_path = self._path_bytes(hardlink_path, hardlink_path_w)
            # hardlinks do not have a filetype: we test the path instead
            self.islnk = bool(self.hardlink_path)

    def is_empty(self):
        return not self.archive or not self.entry_struct

    def _path_bytes(self, func, func_w):
        """
        Return a path as a byte string converted to UTF-8-encoded bytes if this is
        unicode. First call the path function `func` then call the wide char
        equivalent `func_w` if `func` did not provide a path.
        """
        path = func(self.entry_struct)
        if not path:
            path = func_w(self.entry_struct)
        if isinstance(path, unicode):
            # FIXME: encoding MAY fail if the encoding is NOT UTF-8!
            # .... should we transliterate there?
            path = path.encode('utf-8')
        return path

    def write(self, target_dir, transform_path=lambda x: x):
        """
        Write entry to a file or directory saved relatively to the `target_dir` and
        return the path where the file or directory was written or None if nothing
        was written to disk. `transform_path` is a callable taking a path and
        returning a transformed path such as resolving relative paths,
        transliterating non-portable characters or other path transformations.
        The default is a no-op lambda.
        """
        if not self.archive.archive_struct:
            raise ArchiveErrorIllegalOperationOnClosedArchive()
        # skip links and special files
        if not (self.isfile or self.isdir):
            return
        abs_target_dir = os.path.abspath(os.path.expanduser(target_dir))
        # TODO: return some warning when original path has been transformed
        clean_path = transform_path(self.path)

        if self.isdir:
            # TODO: also rename directories to a new name if needed segment by segment
            dir_path = os.path.join(abs_target_dir, clean_path)
            fileutils.create_dir(dir_path)
            return dir_path

        # note: here isfile=True
        try:
            # create parent directories if needed
            target_path = os.path.join(abs_target_dir, clean_path)
            parent_path = os.path.dirname(target_path)

            # TODO: also rename directories to a new name if needed segment by segment
            fileutils.create_dir(parent_path)

            # TODO: return some warning when original path has been renamed?
            unique_path = extractcode.new_name(target_path, is_dir=False)

            chunk_len = 10240
            sbuffer = create_string_buffer(chunk_len)
            with open(unique_path, 'wb') as target:
                chunk_size = 1
                while chunk_size:
                    chunk_size = read_entry_data(self.archive.archive_struct,
                                                 sbuffer, chunk_len)
                    data = sbuffer.raw[0:chunk_size]
                    target.write(data)
            os.utime(unique_path, (self.time, self.time))
            return target_path

        except ArchiveWarning, aw:
            msg = aw.args and '\n'.join(aw.args) or 'No message provided.'
            if msg not in self.warnings:
                self.warnings.append(msg)
            return target_path

    def __repr__(self):
        return ('Entry('
            'path=%(path)r, size=%(size)r, isfile=%(isfile)r, isdir=%(isdir)r,'
            'islnk=%(islnk)r, issym=%(issym)r, isspecial=%(isspecial)r'
        ')'
        ) % self.__dict__


class ArchiveException(ExtractError):

    def __init__(self, rc=None, archive_struct=None, archive_func=None, root_ex=None):
        self.root_ex = root_ex
        if root_ex and isinstance(root_ex, ArchiveException):
            self.rc = root_ex.rc
            self.errno = root_ex.errno
            self.msg = root_ex.args and '\n'.join(root_ex.args)
            self.func = root_ex.func
        else:
            self.rc = rc
            self.errno = archive_struct and errno(archive_struct) or None
            self.msg = archive_struct and err_msg(archive_struct) or None
            self.func = archive_func and archive_func.__name__ or None

    def __str__(self):
        msg = '%(msg)s'
        if DEBUG:
            msg += (': in function %(func)r with rc=%(rc)r, errno=%(errno)r, '
                    'root_ex=%(root_ex)s')
        return msg % self.__dict__


class ArchiveWarning(ArchiveException):
    pass


class ArchiveErrorRetryable(ArchiveException):
    pass


class ArchiveError(ArchiveException):
    pass


class ArchiveErrorFatal(ArchiveException):
    pass


class ArchiveErrorFailedToWriteEntry(ArchiveException):
    pass


class ArchiveErrorPasswordProtected(ArchiveException, ExtractErrorPasswordProtected):
    pass


class ArchiveErrorIllegalOperationOnClosedArchive(ArchiveException):
    pass

#################################################
# ctypes defintion of the interface to libarchive
#################################################


def errcheck(rc, archive_func, args, null=False):
    """
    ctypes error check handler for functions returning int, or null if null is True.
    """
    if null:
        if rc is None:
            archive_struct = args and len(args) > 1 and args[0] or None
            raise ArchiveError(rc, archive_struct, archive_func)
        else:
            return rc

    if rc >= ARCHIVE_OK:
        return rc

    archive_struct = args[0]
    if rc == ARCHIVE_RETRY:
        raise ArchiveErrorRetryable(rc, archive_struct, archive_func)

    if rc == ARCHIVE_WARN:
        raise ArchiveWarning(rc, archive_struct, archive_func)

    # anything else is a serious error, in general not recoverable.
    raise ArchiveError(rc, archive_struct, archive_func)


errcheck_null = partial(errcheck, null=True)

# libarchive return codes
ARCHIVE_EOF = 1
ARCHIVE_OK = 0
ARCHIVE_RETRY = -10
ARCHIVE_WARN = -20
ARCHIVE_FAILED = -25
ARCHIVE_FATAL = -30

# libarchive stat/file types
AE_IFREG = 0o0100000  # Regular file
AE_IFLNK = 0o0120000  # Symbolic link
AE_IFSOCK = 0o0140000  # Socket
AE_IFCHR = 0o0020000  # Character device
AE_IFBLK = 0o0060000  # Block device
AE_IFDIR = 0o0040000  # Directory
AE_IFIFO = 0o0010000  # Named pipe (fifo)

AE_IFMT = 0o0170000  # Format mask

#####################################
# libarchive C functions declarations
#####################################
# NOTE: these declaration come with verbose doc to help with debugging and tracing
# lower level errors and issues. Some comments and the function signatures are
# copied from libarchve.
#
# NOTE: String data in librachive can be set or accessed as wide character strings or
# narrow char strings. The functions that use wide character strings are suffixed
# with _w. These are different representations of the same data: For example, if you
# store a narrow string and read the corresponding wide string, the object will
# transparently convert formats using the current locale. Similarly, if you store a
# wide string and then store a narrow string for the same data, the previously-set
# wide string will be discarded in favor of the new data.

"""
To read an archive, you must first obtain an initialized struct archive object
from archive_read_new()

Allocates and initializes a struct archive object suitable for reading from an
archive. NULL is returned on error.
"""
# struct archive * archive_read_new(void);
archive_reader = libarchive.archive_read_new
archive_reader.argtypes = []
archive_reader.restype = c_void_p
archive_reader.errcheck = errcheck_null

"""
Given a struct archive object, you can enable support for formats and filters.
Enables support for all available formats except the "raw" format.

Return ARCHIVE_OK on success, or ARCHIVE_FATAL.
Detailed error codes and textual descriptions are available from the
archive_errno() and archive_error_string() functions.
"""

# int archive_read_support_format_all(struct archive *);
use_all_formats = libarchive.archive_read_support_format_all
use_all_formats.argtypes = [c_void_p]
use_all_formats.restype = c_int
use_all_formats.errcheck = errcheck

"""
Given a struct archive object, you can enable support for formats and filters.

Enables support for the "raw" format.
The "raw" format handler allows libarchive to be used to read arbitrary
data. It treats any data stream as an archive with a single entry. The
pathname of this entry is "data ;" all other entry fields are unset. This is
not enabled by archive_read_support_format_all() in order to avoid erroneous
handling of damaged archives.
"""
# int archive_read_support_format_raw(struct archive *);
use_raw_formats = libarchive.archive_read_support_format_raw
use_raw_formats.argtypes = [c_void_p]
use_raw_formats.restype = c_int
use_raw_formats.errcheck = errcheck

"""
Given a struct archive object, you can enable support for formats and filters.

Enables all available decompression filters.
Return ARCHIVE_OK if the compression is fully supported, ARCHIVE_WARN if the
compression is supported only through an external program.
Detailed error codes and textual descriptions are available from the
archive_errno() and archive_error_string() functions.
"""
# int archive_read_support_filter_all(struct archive *);
use_all_filters = libarchive.archive_read_support_filter_all
use_all_filters.argtypes = [c_void_p]
use_all_filters.restype = c_int
use_all_filters.errcheck = errcheck

"""
Once formats and filters have been set, you open an archive filename for
actual reading.

Freeze the settings, open the archive, and prepare for reading entries.
Accepts a simple filename and a block size. A NULL filename represents
standard input.

Return ARCHIVE_OK on success, or ARCHIVE_FATAL.
Once you have finished reading data from the archive, you should call
archive_read_close() to close the archive, then call archive_read_free() to
release all resources, including all memory allocated by the library.
"""
# int archive_read_open_filename(struct archive *, const char *filename, size_t block_size);
open_file = libarchive.archive_read_open_filename
open_file.argtypes = [c_void_p, c_char_p, c_size_t]
open_file.restype = c_int
open_file.errcheck = errcheck

"""
Wide char version of archive_read_open_filename.
"""
# int archive_read_open_filename_w(struct archive *, const wchar_t *_filename, size_t _block_size);
open_file_w = libarchive.archive_read_open_filename_w
open_file_w.argtypes = [c_void_p, c_wchar_p, c_size_t]
open_file_w.restype = c_int
open_file_w.errcheck = errcheck

"""
When done with reading an archive you must free its resources.

Invokes archive_read_close() if it was not invoked manually, then release all
resources.
Return ARCHIVE_OK on success, or ARCHIVE_FATAL.
"""
# int  archive_read_free(struct archive *);
free_archive = libarchive.archive_read_free
free_archive.argtypes = [c_void_p]
free_archive.restype = c_int
free_archive.errcheck = errcheck

#
# entry level functions
#
"""
You can think of a struct archive_entry as a heavy-duty version of struct stat
: it includes everything from struct stat plus associated pathname, textual
group and user names, etc. These objects are used by ManPageLibarchive3 to
represent the metadata associated with a particular entry in an archive.
"""

"""
Allocate and return a blank struct archive_entry object.
"""
# struct archive_entry * archive_entry_new(void);
new_entry = libarchive.archive_entry_new
new_entry.argtypes = []
new_entry.restype = c_void_p
new_entry.errcheck = errcheck_null

"""
Given an opened archive struct object, you can iterate through the archive
entries. An entry has a header with various data and usually a payload that is
the archived content.

Read the header for the next entry and populate the provided struct
archive_entry.

Return ARCHIVE_OK (the operation succeeded), ARCHIVE_WARN (the operation
succeeded but a non-critical error was encountered), ARCHIVE_EOF (end-of-
archive was encountered), ARCHIVE_RETRY (the operation failed but can be
retried), and ARCHIVE_FATAL (there was a fatal error; the archive should be
closed immediately).
"""
# int archive_read_next_header2(struct archive *, struct archive_entry *);
next_entry = libarchive.archive_read_next_header2
next_entry.argtypes = [c_void_p, c_void_p]
next_entry.restype = c_int
next_entry.errcheck = errcheck

"""
Read data associated with the header just read. Internally, this is a
convenience function that calls archive_read_data_block() and fills any gaps
with nulls so that callers see a single continuous stream of data.
"""
# ssize_t archive_read_data(struct archive *, void *buff, size_t len);
read_entry_data = libarchive.archive_read_data
read_entry_data.argtypes = [c_void_p, c_void_p, c_size_t]
read_entry_data.restype = c_ssize_t
read_entry_data.errcheck = errcheck

"""
Return the next available block of data for this entry. Unlike
archive_read_data(), the archive_read_data_block() function avoids copying
data and allows you to correctly handle sparse files, as supported by some
archive formats. The library guarantees that offsets will increase and that
blocks will not overlap. Note that the blocks returned from this function can
be much larger than the block size read from disk, due to compression and
internal buffer optimizations.
"""
# int archive_read_data_block(struct archive *, const void **buff, size_t *len, off_t *offset);
read_entry_data_block = libarchive.archive_read_data_block
read_entry_data_block.argtypes = [c_void_p, POINTER(c_void_p), POINTER(c_size_t), POINTER(c_longlong)]
read_entry_data_block.restype = c_int
read_entry_data_block.errcheck = errcheck

"""
Releases the struct archive_entry object.
The struct entry object must be freed when no longer needed.
"""
# void archive_entry_free(struct archive_entry *);
free_entry = libarchive.archive_entry_free
free_entry.argtypes = [c_void_p]
free_entry.restype = None

#
# Entry attributes: path, type, size, etc. are collected with these functions:
#

"""
The functions archive_entry_filetype() and archive_entry_set_filetype() get
respectively set the filetype. The file type is one of the following
constants:
AE_IFREG    Regular file
AE_IFLNK    Symbolic link
AE_IFSOCK   Socket
AE_IFCHR    Character device
AE_IFBLK    Block device
AE_IFDIR    Directory
AE_IFIFO    Named pipe (fifo)

Not all file types are supported by all platforms. The constants used by
stat(2) may have different numeric values from the corresponding constants
above.
"""
# struct archive_entry * archive_entry_filetype(struct archive_entry *);
# TODO: check for nulls
entry_type = libarchive.archive_entry_filetype
entry_type.argtypes = [c_void_p]
entry_type.restype = c_int

"""
This function retrieves the mtime field in an archive_entry. (modification
time).

The timestamps are truncated automatically depending on the archive format
(for archiving) or the filesystem capabilities (for restoring).
All timestamp fields are optional.
"""
# time_t archive_entry_mtime(struct archive_entry *);
entry_time = libarchive.archive_entry_mtime
entry_time.argtypes = [c_void_p]
entry_time.restype = c_int

"""
Path in the archive.

char *        Multibyte strings in the current locale.
wchar_t *     Wide character strings in the current locale.
"""
# const char * archive_entry_pathname(struct archive_entry *a);
# TODO: check for nulls
entry_path = libarchive.archive_entry_pathname
entry_path.argtypes = [c_void_p]
entry_path.restype = c_char_p

# const wchar_t * archive_entry_pathname_w(struct archive_entry *a);
# TODO: check for nulls?
entry_path_w = libarchive.archive_entry_pathname_w
entry_path_w.argtypes = [c_void_p]
entry_path_w.restype = c_wchar_p

# int64_t archive_entry_size(struct archive_entry *a);
entry_size = libarchive.archive_entry_size
entry_size.argtypes = [c_void_p]
entry_size.restype = c_longlong
entry_size.errcheck = errcheck

"""
Destination of the hardlink.
"""
# const char * archive_entry_hardlink(struct archive_entry *a);
hardlink_path = libarchive.archive_entry_hardlink
hardlink_path.argtypes = [c_void_p]
hardlink_path.restype = c_char_p

# const wchar_t * archive_entry_hardlink_w(struct archive_entry *a);
hardlink_path_w = libarchive.archive_entry_hardlink_w
hardlink_path_w.argtypes = [c_void_p]
hardlink_path_w.restype = c_wchar_p

"""
The number of references (hardlinks) can be obtained by calling
archive_entry_nlinks()
"""
# unsigned int archive_entry_nlink(struct archive_entry *a);
hardlink_count = libarchive.archive_entry_nlink
hardlink_count.argtypes = [c_void_p]
hardlink_count.restype = c_int

"""
The functions archive_entry_dev() and archive_entry_ino64() are used by
ManPageArchiveEntryLinkify3 to find hardlinks. The pair of device and inode is
supposed to identify hardlinked files.
"""
# int64_t archive_entry_ino64(struct archive_entry *a);
# dev_t archive_entry_dev(struct archive_entry *a);
# int archive_entry_dev_is_set(struct archive_entry *a);

"""
Destination of the symbolic link.
"""
# const char * archive_entry_symlink(struct archive_entry *);
symlink_path = libarchive.archive_entry_symlink
symlink_path.argtypes = [c_void_p]
symlink_path.restype = c_char_p
symlink_path.errcheck = errcheck_null

# const wchar_t * archive_entry_symlink_w(struct archive_entry *);
symlink_path_w = libarchive.archive_entry_symlink_w
symlink_path_w.argtypes = [c_void_p]
symlink_path_w.restype = c_wchar_p
symlink_path_w.errcheck = errcheck_null

#
# Utilities and error handling: not all are defined for now
#

"""
Returns a numeric error code (see errno(2)) indicating the reason for the most
recent error return. Note that this can not be reliably used to detect whether
an error has occurred. It should be used only after another libarchive
function has returned an error status.
"""
# int archive_errno(struct archive *);
errno = libarchive.archive_errno
errno.argtypes = [c_void_p]
errno.restype = c_int

"""
Returns a textual error message suitable for display. The error message here
is usually more specific than that obtained from passing the result of
archive_errno() to strerror(3).
"""
# const char * archive_error_string(struct archive *);
err_msg = libarchive.archive_error_string
err_msg.argtypes = [c_void_p]
err_msg.restype = c_char_p

"""
Returns a count of the number of files processed by this archive object. The
count is incremented by calls to ManPageArchiveWriteHeader3 or
ManPageArchiveReadNextHeader3.
"""
# int archive_file_count(struct archive *);

"""
Returns a numeric code identifying the indicated filter. See
archive_filter_count() for details of the numbering.
"""
# int archive_filter_code(struct archive *, int);

"""
Returns the number of filters in the current pipeline. For read archive
handles, these filters are added automatically by the automatic format
detection.
"""
# int archive_filter_count(struct archive *, int);

"""
Synonym for archive_filter_code(a,(0)).
"""
# int archive_compression(struct archive *);

"""
Returns a textual name identifying the indicated filter. See
archive_filter_count() for details of the numbering.
"""
# const char * archive_filter_name(struct archive *, int);

"""
Synonym for archive_filter_name(a,(0)).
"""
# const char * archive_compression_name(struct archive *);

"""
Returns a numeric code indicating the format of the current archive entry.
This value is set by a successful call to archive_read_next_header(). Note
that it is common for this value to change from entry to entry. For example, a
tar archive might have several entries that utilize GNU tar extensions and
several entries that do not. These entries will have different format codes.
"""
# int archive_format(struct archive *);

"""
A textual description of the format of the current entry.
"""
# const char * archive_format_name(struct archive *);
