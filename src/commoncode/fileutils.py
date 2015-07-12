#
# Copyright (c) 2015 nexB Inc. and others. All rights reserved.
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

import codecs
import errno
import logging
import os
import ntpath
import posixpath
import shutil
import stat
import tempfile

from commoncode import system
from commoncode import text
from commoncode import filetype
from commoncode.filetype import is_rwx


# this exception is not available on posix
try:
    WindowsError  # @UndefinedVariable
except NameError:
    WindowsError = None  # @ReservedAssignment

DEBUG = False
logger = logging.getLogger(__name__)

"""
File, paths and directory utility functions.
"""

#
# DIRECTORIES
#

def create_dir(location):
    """
    Create directory and all sub-directories recursively at location ensuring
    these are readable and writeable.
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


def system_temp_dir():
    """
    Return the global temp directory for the current user.
    """
    temp_dir = os.getenv('SCANCODE_TMP')
    if not temp_dir:
        sc = text.python_safe_name('scancode_' + system.username)
        temp_dir = os.path.join(tempfile.gettempdir(), sc)
    create_dir(temp_dir)
    return temp_dir


def get_temp_dir(base_dir, prefix=''):
    """
    Return the path to base a new unique temporary directory, created under
    the system-wide `system_temp_dir` temp directory and as a subdir of the
    base_dir path, a path relative to the `system_temp_dir`.
    """
    base = os.path.join(system_temp_dir(), base_dir)
    create_dir(base)
    return tempfile.mkdtemp(prefix=prefix, dir=base)

#
# FILE READING
#

def file_chunks(file_object, chunk_size=1024):
    """
    Yield a file piece by piece. Default chunk size: 1k.
    """
    while True:
        data = file_object.read(chunk_size)
        if data:
            yield data
        else:
            break


# FIXME: reading a whole file could be an issue: could we stream by line?
def _text(location, encoding, universal_new_lines=True):
    """
    Read file at `location` as a text file with the specified `encoding`. If
    `universal_new_lines` is True, update lines endings to be posix LF \n.
    Return a unicode string.
    Note:  Universal newlines in the codecs package was removed in
    Python2.6 see http://bugs.python.org/issue691291
    """
    with codecs.open(location, 'r', encoding) as f:
        text = f.read()
        if universal_new_lines:
            text = u'\n'.join(text.splitlines(False))
        return text


def read_text_file(location, universal_new_lines=True):
    """
    Return the text content of file at `location` trying to find the best
    encoding.
    """
    try:
        text = _text(location, 'utf-8', universal_new_lines)
    except:
        text = _text(location, 'latin-1', universal_new_lines)
    return text

#
# PATHS AND NAMES MANIPULATIONS
#

def as_posixpath(location):
    """
    Return a posix-like path using posix path separators (slash or "/") for a
    `location` path. This converts Windows paths to look like posix paths that
    Python accepts gracefully on Windows for path handling.
    """
    return location.replace(ntpath.sep, posixpath.sep)


def resource_name(path):
    """
    Return the resource name (file name or directory name) from `path` which
    is the last path segment.
    """
    path = as_posixpath(path)
    path = path.rstrip('/')
    _left, right = posixpath.split(path)
    return right or  ''


def file_name(path):
    """
    Return the file name (or directory name) of a path.
    """
    return resource_name(path)


def parent_directory(path):
    """
    Return the parent directory of a file or directory path.
    """
    path = as_posixpath(path)
    path = path.rstrip('/')
    left, _ = posixpath.split(path)
    trail = '/' if left != '/' else ''
    return left + trail


def file_base_name(path):
    """
    Return the file base name for a path. The base name is the base name of
    the file minus the extension. For a directory return an empty string.
    """
    return splitext(path)[0]


def file_extension(path):
    """
    Return the file extension for a path.
    """
    return splitext(path)[1]


def splitext(path):
    """
    Return a tuple of strings (basename, extension) for a path. The basename is
    the file name minus its extension. Return an empty extension string for a
    directory. A directory is identified by ending with a path separator. Not
    the same as os.path.splitext.
    """
    base_name = ''
    extension = ''
    if not path:
        return base_name, extension

    path = as_posixpath(path)
    name = resource_name(path)
    if path.endswith('/'):
        # directories have no extension
        base_name = name
        extension = ''
    elif name.startswith('.') and '.' not in name[1:]:
        base_name = ''
        extension = name
    else:
        base_name, extension = posixpath.splitext(name)
    return base_name or '', extension or ''

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
    if DEBUG:
        ign = ignored(location)
        logger.debug('walk: ignored:', location, ign)
    if not ignored(location):
        if filetype.is_file(location) :
            yield parent_directory(location), [], [file_name(location)]
        elif filetype.is_dir(location):
            dirs = []
            files = []
            # TODO: consider using scandir
            for name in os.listdir(location):
                loc = os.path.join(location, name)
                if filetype.is_special(loc) or ignored(loc):
                    if DEBUG:
                        ign = ignored(loc)
                        logger.debug('walk: ignored:', loc, ign)
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


def file_iter(location, ignored=ignore_nothing):
    """
    Return an iterable of files at `location` recursively.

    :param location: a file or a directory.
    :param ignored: a callable accepting a location argument and returning True
                    if the location should be ignored.
    :return: an iterable of file locations.
    """
    for top, _dirs, files in walk(location, ignored):
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
    if filetype.is_dir(location):
        for top, dirs, files in walk(location):
            for d in dirs:
                chmod(os.path.join(top, d), flags, recurse=False)
            for f in files:
                chmod(os.path.join(top, f), flags, recurse=False)

#
# DELETION
#

def _rm_handler(function, path, excinfo):  # @UnusedVariable
    """
    shutil.rmtree handler invoked on error when deleting a directory tree.
    This retries deleting once before giving up.
    """
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

    if os.path.exists(location) or filetype.is_broken_link(location):
        chmod(os.path.dirname(location), RW, recurse=False)
        if filetype.is_dir(location):
            shutil.rmtree(location, False, _rm_handler)
        else:
            os.remove(location)
