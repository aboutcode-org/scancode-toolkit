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
from __future__ import print_function
from __future__ import unicode_literals

# Python 2 and 3 support
try:
    # Python 2
    unicode
    str = unicode  # NOQA
except NameError:
    # Python 3
    unicode = str  # NOQA

try:
    from os import fsencode
    from os import fsdecode
except ImportError:
    from backports.os import fsencode
    from backports.os import fsdecode  # NOQA

import errno
import os
import ntpath
import posixpath
import shutil
import stat
import sys
import tempfile

try:
    from scancode_config import scancode_temp_dir
except ImportError:
    scancode_temp_dir = None

from commoncode import filetype
from commoncode.filetype import is_rwx
from commoncode.system import on_linux

# this exception is not available on posix
try:
    WindowsError  # NOQA
except NameError:
    WindowsError = None  # NOQA

TRACE = False

import logging

logger = logging.getLogger(__name__)


def logger_debug(*args):
    pass


if TRACE:
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, basestring) and a or repr(a) for a in args))

# Paths can only be sanely handled as raw bytes on Linux
PATH_TYPE = bytes if on_linux else unicode
POSIX_PATH_SEP = b'/' if on_linux else '/'
WIN_PATH_SEP = b'\\' if on_linux else '\\'
ALL_SEPS = POSIX_PATH_SEP + WIN_PATH_SEP
EMPTY_STRING = b'' if on_linux else ''
DOT = b'.' if on_linux else '.'

"""
File, paths and directory utility functions.
"""

#
# DIRECTORIES
#


def create_dir(location):
    """
    Create directory and all sub-directories recursively at location ensuring these
    are readable and writeable.
    Raise Exceptions if it fails to create the directory.
    """

    if os.path.exists(location):
        if not os.path.isdir(location):
            err = ('Cannot create directory: existing file '
                   'in the way ''%(location)s.')
            raise OSError(err % locals())
    else:
        # may fail on win if the path is too long
        # FIXME: consider using UNC ?\\ paths

        if on_linux:
            location = fsencode(location)
        try:
            os.makedirs(location)
            chmod(location, RW, recurse=False)

        # avoid multi-process TOCTOU conditions when creating dirs
        # the directory may have been created since the exist check
        except WindowsError, e:
            # [Error 183] Cannot create a file when that file already exists
            if e and e.winerror == 183:
                if not os.path.isdir(location):
                    raise
            else:
                raise
        except (IOError, OSError), o:
            if o.errno == errno.EEXIST:
                if not os.path.isdir(location):
                    raise
            else:
                raise


def get_temp_dir(base_dir=scancode_temp_dir, prefix=''):
    """
    Return the path to a new existing unique temporary directory, created under
    the `base_dir` base directory using the `prefix` prefix.
    If `base_dir` is not provided, use the 'SCANCODE_TMP' env var or the system
    temp directory.

    WARNING: do not change this code without changing scancode_config.py too
    """

    has_base = bool(base_dir)
    if not has_base:
        base_dir = os.getenv('SCANCODE_TMP')
        if not base_dir:
            base_dir = tempfile.gettempdir()
        else:
            if on_linux:
                base_dir = fsencode(base_dir)
            create_dir(base_dir)

    if not has_base:
        prefix = 'scancode-tk-'

    if on_linux:
        prefix = fsencode(prefix)

    return tempfile.mkdtemp(prefix=prefix, dir=base_dir)

#
# PATHS AND NAMES MANIPULATIONS
#

# TODO: move these functions to paths.py


def is_posixpath(location):
    """
    Return True if the `location` path is likely a POSIX-like path using POSIX path
    separators (slash or "/")or has no path separator.

    Return False if the `location` path is likely a Windows-like path using backslash
    as path separators (e.g. "\").
    """
    has_slashes = POSIX_PATH_SEP in location
    has_backslashes = WIN_PATH_SEP in location
    # windows paths with drive
    if location:
        drive, _ = ntpath.splitdrive(location)
        if drive:
            return False

    # a path is always POSIX unless it contains ONLY backslahes
    # which is a rough approximation (it could still be posix)
    is_posix = True
    if has_backslashes and not has_slashes:
        is_posix = False
    return is_posix


def as_posixpath(location):
    """
    Return a POSIX-like path using POSIX path separators (slash or "/") for a
    `location` path. This converts Windows paths to look like POSIX paths: Python
    accepts gracefully POSIX paths on Windows.
    """
    return location.replace(WIN_PATH_SEP, POSIX_PATH_SEP)


def as_winpath(location):
    """
    Return a Windows-like path using Windows path separators (backslash or "\") for a
    `location` path.
    """
    return location.replace(POSIX_PATH_SEP, WIN_PATH_SEP)


def split_parent_resource(path, force_posix=False):
    """
    Return a tuple of (parent directory path, resource name).
    """
    use_posix = force_posix or is_posixpath(path)
    splitter = use_posix and posixpath or ntpath
    path = path.rstrip(ALL_SEPS)
    return splitter.split(path)


def resource_name(path, force_posix=False):
    """
    Return the resource name (file name or directory name) from `path` which
    is the last path segment.
    """
    _left, right = split_parent_resource(path, force_posix)
    return right or EMPTY_STRING


def file_name(path, force_posix=False):
    """
    Return the file name (or directory name) of a path.
    """
    return resource_name(path, force_posix)


def parent_directory(path, force_posix=False):
    """
    Return the parent directory path of a file or directory `path`.
    """
    left, _right = split_parent_resource(path, force_posix)
    use_posix = force_posix or is_posixpath(path)
    sep = POSIX_PATH_SEP if use_posix else WIN_PATH_SEP
    trail = sep if left != sep else EMPTY_STRING
    return left + trail


def file_base_name(path, force_posix=False):
    """
    Return the file base name for a path. The base name is the base name of
    the file minus the extension. For a directory return an empty string.
    """
    return splitext(path, force_posix)[0]


def file_extension(path, force_posix=False):
    """
    Return the file extension for a path.
    """
    return splitext(path, force_posix)[1]


def splitext_name(file_name, is_file=True):
    """
    Return a tuple of Unicode strings (basename, extension) for a file name. The
    basename is the file name minus its extension. Return an empty extension
    string for a directory. Not the same as os.path.splitext_name.

    For example:
    >>> expected = 'path', '.ext'
    >>> assert expected == splitext_name('path.ext')

    Directories even with dotted names have no extension:
    >>> expected = 'path.ext', ''
    >>> assert expected == splitext_name('path.ext', is_file=False)

    >>> expected = 'file', '.txt'
    >>> assert expected == splitext_name('file.txt')

    Composite extensions for tarballs are properly handled:
    >>> expected = 'archive', '.tar.gz'
    >>> assert expected == splitext_name('archive.tar.gz')

    dotfile are properly handled:
    >>> expected = '.dotfile', ''
    >>> assert expected == splitext_name('.dotfile')
    >>> expected = '.dotfile', '.this'
    >>> assert expected == splitext_name('.dotfile.this')
    """

    if not file_name:
        return '', ''
    file_name = fsdecode(file_name)

    if not is_file:
        return file_name, ''

    if file_name.startswith('.') and '.' not in file_name[1:]:
        # .dot files base name is the full name and they do not have an extension
        return file_name, ''

    base_name, extension = posixpath.splitext(file_name)
    # handle composed extensions of tar.gz, bz, zx,etc
    if base_name.endswith('.tar'):
        base_name, extension2 = posixpath.splitext(base_name)
        extension = extension2 + extension
    return base_name, extension


# TODO: FIXME: this is badly broken!!!!
def splitext(path, force_posix=False):
    """
    Return a tuple of strings (basename, extension) for a path. The basename is
    the file name minus its extension. Return an empty extension string for a
    directory. A directory is identified by ending with a path separator. Not
    the same as os.path.splitext.

    For example:
    >>> expected = 'path', '.ext'
    >>> assert expected == splitext('C:\\dir\path.ext')

    Directories even with dotted names have no extension:
    >>> import ntpath
    >>> expected = 'path.ext', ''
    >>> assert expected == splitext('C:\\dir\\path.ext' + ntpath.sep)

    >>> expected = 'path.ext', ''
    >>> assert expected == splitext('/dir/path.ext/')

    >>> expected = 'file', '.txt'
    >>> assert expected == splitext('/some/file.txt')

    Composite extensions for tarballs are properly handled:
    >>> expected = 'archive', '.tar.gz'
    >>> assert expected == splitext('archive.tar.gz')
    """
    base_name = EMPTY_STRING
    extension = EMPTY_STRING
    if not path:
        return base_name, extension

    ppath = as_posixpath(path)
    name = resource_name(path, force_posix)
    name = name.strip(ALL_SEPS)
    if ppath.endswith(POSIX_PATH_SEP):
        # directories never have an extension
        base_name = name
        extension = EMPTY_STRING
    elif name.startswith(DOT) and DOT not in name[1:]:
        # .dot files base name is the full name and they do not have an extension
        base_name = name
        extension = EMPTY_STRING
    else:
        base_name, extension = posixpath.splitext(name)
        # handle composed extensions of tar.gz, bz, zx,etc
        if base_name.endswith(b'.tar' if on_linux else '.tar'):
            base_name, extension2 = posixpath.splitext(base_name)
            extension = extension2 + extension
    return base_name, extension

#
# DIRECTORY AND FILES WALKING/ITERATION
#


ignore_nothing = lambda _: False


def walk(location, ignored=ignore_nothing):
    """
    Walk location returning the same tuples as os.walk but with a different
    behavior:
     - always walk top-down, breadth-first.
     - always ignore and never follow symlinks, .
     - always ignore special files (FIFOs, etc.)
     - optionally ignore files and directories by invoking the `ignored`
       callable on files and directories returning True if it should be ignored.
     - location is a directory or a file: for a file, the file is returned.
    """
    if on_linux:
        location = fsencode(location)

    # TODO: consider using the new "scandir" module for some speed-up.
    if TRACE:
        ign = ignored(location)
        logger_debug('walk: ignored:', location, ign)
    if ignored(location):
        return

    if filetype.is_file(location) :
        yield parent_directory(location), [], [file_name(location)]

    elif filetype.is_dir(location):
        dirs = []
        files = []
        # TODO: consider using scandir
        for name in os.listdir(location):
            loc = os.path.join(location, name)
            if filetype.is_special(loc) or ignored(loc):
                if TRACE:
                    ign = ignored(loc)
                    logger_debug('walk: ignored:', loc, ign)
                continue
            # special files and symlinks are always ignored
            if filetype.is_dir(loc):
                dirs.append(name)
            elif filetype.is_file(loc):
                files.append(name)
        yield location, dirs, files

        for dr in dirs:
            for tripple in walk(os.path.join(location, dr), ignored):
                yield tripple


def resource_iter(location, ignored=ignore_nothing, with_dirs=True):
    """
    Return an iterable of paths at `location` recursively.

    :param location: a file or a directory.
    :param ignored: a callable accepting a location argument and returning True
                    if the location should be ignored.
    :return: an iterable of file and directory locations.
    """
    if on_linux:
        location = fsencode(location)
    for top, dirs, files in walk(location, ignored):
        if with_dirs:
            for d in dirs:
                yield os.path.join(top, d)
        for f in files:
            yield os.path.join(top, f)
#
# COPY
#


def copytree(src, dst):
    """
    Copy recursively the `src` directory to the `dst` directory. If `dst` is an
    existing directory, files in `dst` may be overwritten during the copy.
    Preserve timestamps.
    Ignores:
     -`src` permissions: `dst` files are created with the default permissions.
     - all special files such as FIFO or character devices and symlinks.

    Raise an shutil.Error with a list of reasons.

    This function is similar to and derived from the Python shutil.copytree
    function. See fileutils.py.ABOUT for details.
    """
    if on_linux:
        src = fsencode(src)
        dst = fsencode(dst)

    if not filetype.is_readable(src):
        chmod(src, R, recurse=False)

    names = os.listdir(src)

    if not os.path.exists(dst):
        os.makedirs(dst)

    errors = []
    errors.extend(copytime(src, dst))

    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)

        # skip anything that is not a regular file, dir or link
        if not filetype.is_regular(srcname):
            continue

        if not filetype.is_readable(srcname):
            chmod(srcname, R, recurse=False)
        try:
            if os.path.isdir(srcname):
                copytree(srcname, dstname)
            elif filetype.is_file(srcname):
                copyfile(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except shutil.Error, err:
            errors.extend(err.args[0])
        except EnvironmentError, why:
            errors.append((srcname, dstname, str(why)))

    if errors:
        raise shutil.Error, errors


def copyfile(src, dst):
    """
    Copy src file to dst file preserving timestamps.
    Ignore permissions and special files.

    Similar to and derived from Python shutil module. See fileutils.py.ABOUT
    for details.
    """
    if on_linux:
        src = fsencode(src)
        dst = fsencode(dst)

    if not filetype.is_regular(src):
        return
    if not filetype.is_readable(src):
        chmod(src, R, recurse=False)
    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    shutil.copyfile(src, dst)
    copytime(src, dst)


def copytime(src, dst):
    """
    Copy timestamps from `src` to `dst`.

    Similar to and derived from Python shutil module. See fileutils.py.ABOUT
    for details.
    """
    if on_linux:
        src = fsencode(src)
        dst = fsencode(dst)

    errors = []
    st = os.stat(src)
    if hasattr(os, 'utime'):
        try:
            os.utime(dst, (st.st_atime, st.st_mtime))
        except OSError, why:
            if WindowsError is not None and isinstance(why, WindowsError):
                # File access times cannot be copied on Windows
                pass
            else:
                errors.append((src, dst, str(why)))
    return errors

#
# PERMISSIONS
#


# modes: read, write, executable
R = stat.S_IRUSR
RW = stat.S_IRUSR | stat.S_IWUSR
RX = stat.S_IRUSR | stat.S_IXUSR
RWX = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR


# FIXME: This was an expensive operation that used to recurse of the parent directory
def chmod(location, flags, recurse=False):
    """
    Update permissions for `location` with with `flags`. `flags` is one of R,
    RW, RX or RWX with the same semantics as in the chmod command. Update is
    done recursively if `recurse`.
    """
    if not location or not os.path.exists(location):
        return
    if on_linux:
        location = fsencode(location)

    location = os.path.abspath(location)

    new_flags = flags
    if filetype.is_dir(location):
        # POSIX dirs need to be executable to be readable,
        # and to be writable so we can change perms of files inside
        new_flags = RWX

    # FIXME: do we really need to change the parent directory perms?
    # FIXME: may just check them instead?
    parent = os.path.dirname(location)
    current_stat = stat.S_IMODE(os.stat(parent).st_mode)
    if not is_rwx(parent):
        os.chmod(parent, current_stat | RWX)

    if filetype.is_regular(location):
        current_stat = stat.S_IMODE(os.stat(location).st_mode)
        os.chmod(location, current_stat | new_flags)

    if recurse:
        chmod_tree(location, flags)


def chmod_tree(location, flags):
    """
    Update permissions recursively in a directory tree `location`.
    """
    if on_linux:
        location = fsencode(location)
    if filetype.is_dir(location):
        for top, dirs, files in walk(location):
            for d in dirs:
                chmod(os.path.join(top, d), flags, recurse=False)
            for f in files:
                chmod(os.path.join(top, f), flags, recurse=False)

#
# DELETION
#


def _rm_handler(function, path, excinfo):  # NOQA
    """
    shutil.rmtree handler invoked on error when deleting a directory tree.
    This retries deleting once before giving up.
    """
    if on_linux:
        path = fsencode(path)
    if function == os.rmdir:
        try:
            chmod(path, RW, recurse=True)
            shutil.rmtree(path, True)
        except Exception:
            pass

        if os.path.exists(path):
            logger.warning('Failed to delete directory %s', path)

    elif function == os.remove:
        try:
            delete(path, _err_handler=None)
        except:
            pass

        if os.path.exists(path):
            logger.warning('Failed to delete file %s', path)


def delete(location, _err_handler=_rm_handler):
    """
    Delete a directory or file at `location` recursively. Similar to "rm -rf"
    in a shell or a combo of os.remove and shutil.rmtree.
    """
    if not location:
        return

    if on_linux:
        location = fsencode(location)

    if os.path.exists(location) or filetype.is_broken_link(location):
        chmod(os.path.dirname(location), RW, recurse=False)
        if filetype.is_dir(location):
            shutil.rmtree(location, False, _rm_handler)
        else:
            os.remove(location)
