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
from __future__ import division
from __future__ import unicode_literals

import filecmp
from functools import partial
import os
import shutil
import stat
import sys
import tarfile
from unittest import TestCase as TestCaseClass
import zipfile

from commoncode import fileutils
from commoncode.fileutils import fsencode
from commoncode import filetype
from commoncode.system import on_linux
from commoncode.system import on_posix
from commoncode.system import on_windows


# a base test dir specific to a given test run
# to ensure that multiple tests run can be launched in parallel
test_run_temp_dir = None

# set to 1 to see the slow tests
timing_threshold = sys.maxint

POSIX_PATH_SEP = b'/' if on_linux else '/'
WIN_PATH_SEP = b'\\' if on_linux else '\\'
EMPTY_STRING = b'' if on_linux else ''
DOT = b'.' if on_linux else '.'

if on_windows:
    OS_PATH_SEP = WIN_PATH_SEP
else:
    OS_PATH_SEP = POSIX_PATH_SEP


def to_os_native_path(path):
    """
    Normalize a path to use the native OS path separator.
    """
    if on_linux:
        path = fsencode(path)
    path = path.replace(POSIX_PATH_SEP, OS_PATH_SEP)
    path = path.replace(WIN_PATH_SEP, OS_PATH_SEP)
    path = path.rstrip(OS_PATH_SEP)
    return path


def get_test_loc(test_path, test_data_dir, debug=False, exists=True):
    """
    Given a `test_path` relative to the `test_data_dir` directory, return the
    location to a test file or directory for this path. No copy is done.
    """
    if on_linux:
        test_path = fsencode(test_path)
        test_data_dir = fsencode(test_data_dir)

    if debug:
        import inspect
        caller = inspect.stack()[1][3]
        print('\nget_test_loc,%(caller)s,"%(test_path)s","%(test_data_dir)s"' % locals())

    assert test_path
    assert test_data_dir

    if not os.path.exists(test_data_dir):
        raise IOError("[Errno 2] No such directory: test_data_dir not found:"
                      " '%(test_data_dir)s'" % locals())

    tpath = to_os_native_path(test_path)
    test_loc = os.path.abspath(os.path.join(test_data_dir, tpath))

    if exists and not os.path.exists(test_loc):
        raise IOError("[Errno 2] No such file or directory: "
                      "test_path not found: '%(test_loc)s'" % locals())

    return test_loc


class FileDrivenTesting(object):
    """
    Add support for handling test files and directories, including managing
    temporary test resources and doing file-based assertions.
    This can be used as a standalone object if needed.
    """
    test_data_dir = None

    def get_test_loc(self, test_path, copy=False, debug=False):
        """
        Given a `test_path` relative to the self.test_data_dir directory, return the
        location to a test file or directory for this path. Copy to a temp
        test location if `copy` is True.
        """
        test_data_dir = self.test_data_dir
        if on_linux:
            test_path = fsencode(test_path)
            test_data_dir = fsencode(test_data_dir)

        if debug:
            import inspect
            caller = inspect.stack()[1][3]
            print('\nself.get_test_loc,%(caller)s,"%(test_path)s"' % locals())

        test_loc = get_test_loc(test_path, test_data_dir, debug=debug)
        if copy:
            base_name = os.path.basename(test_loc)
            if filetype.is_file(test_loc):
                # target must be an existing dir
                target_dir = self.get_temp_dir()
                fileutils.copyfile(test_loc, target_dir)
                test_loc = os.path.join(target_dir, base_name)
            else:
                # target must be a NON existing dir
                target_dir = os.path.join(self.get_temp_dir(), base_name)
                fileutils.copytree(test_loc, target_dir)
                # cleanup of VCS that could be left over from checkouts
                self.remove_vcs(target_dir)
                test_loc = target_dir
        return test_loc

    def get_temp_file(self, extension=None, dir_name='td', file_name='tf'):
        """
        Return a unique new temporary file location to a non-existing
        temporary file that can safely be created without a risk of name
        collision.
        """
        if extension is None:
            extension = '.txt'

        if on_linux:
            extension = fsencode(extension)
            dir_name = fsencode(dir_name)
            file_name = fsencode(file_name)

        if extension and not extension.startswith(DOT):
                extension = DOT + extension

        file_name = file_name + extension
        temp_dir = self.get_temp_dir(dir_name)
        location = os.path.join(temp_dir, file_name)
        return location

    def get_temp_dir(self, sub_dir_path=None):
        """
        Create a unique new temporary directory location. Create directories
        identified by sub_dir_path if provided in this temporary directory.
        Return the location for this unique directory joined with the
        sub_dir_path if any.
        """
        # ensure that we have a new unique temp directory for each test run
        global test_run_temp_dir
        if not test_run_temp_dir:
            # not we add a space in the path for testing path with spaces
            test_run_temp_dir = fileutils.get_temp_dir(prefix='scancode-tests -')
        if on_linux:
            test_run_temp_dir = fsencode(test_run_temp_dir)

        new_temp_dir = fileutils.get_temp_dir(base_dir=test_run_temp_dir, prefix='')

        if sub_dir_path:
            # create a sub directory hierarchy if requested
            sub_dir_path = to_os_native_path(sub_dir_path)
            new_temp_dir = os.path.join(new_temp_dir, sub_dir_path)
            fileutils.create_dir(new_temp_dir)
        return new_temp_dir

    def remove_vcs(self, test_dir):
        """
        Remove some version control directories and some temp editor files.
        """
        vcses = ('CVS', '.svn', '.git', '.hg')
        if on_linux:
            vcses = tuple(fsencode(p) for p in vcses)
            test_dir = fsencode(test_dir)

        for root, dirs, files in os.walk(test_dir):
            for vcs_dir in vcses:
                if vcs_dir in dirs:
                    for vcsroot, vcsdirs, vcsfiles in os.walk(test_dir):
                        for vcsfile in vcsdirs + vcsfiles:
                            vfile = os.path.join(vcsroot, vcsfile)
                            fileutils.chmod(vfile, fileutils.RW, recurse=False)
                    shutil.rmtree(os.path.join(root, vcs_dir), False)

            # editors temp file leftovers
            tilde = b'~' if on_linux else '~'
            map(os.remove, [os.path.join(root, file_loc)
                            for file_loc in files if file_loc.endswith(tilde)])

    def __extract(self, test_path, extract_func=None, verbatim=False):
        """
        Given an archive file identified by test_path relative
        to a test files directory, return a new temp directory where the
        archive file has been extracted using extract_func.
        If `verbatim` is True preserve the permissions.
        """
        assert test_path and test_path != ''
        if on_linux:
            test_path = fsencode(test_path)
        test_path = to_os_native_path(test_path)
        target_path = os.path.basename(test_path)
        target_dir = self.get_temp_dir(target_path)
        original_archive = self.get_test_loc(test_path)
        if on_linux:
            target_dir = fsencode(target_dir)
            original_archive = fsencode(original_archive)
        extract_func(original_archive, target_dir,
                     verbatim=verbatim)
        return target_dir

    def extract_test_zip(self, test_path, *args, **kwargs):
        return self.__extract(test_path, extract_zip)

    def extract_test_zip_raw(self, test_path, *args, **kwargs):
        return self.__extract(test_path, extract_zip_raw)

    def extract_test_tar(self, test_path, verbatim=False):
        return self.__extract(test_path, extract_tar, verbatim)

    def extract_test_tar_raw(self, test_path, *args, **kwargs):
        return self.__extract(test_path, extract_tar_raw)

    def extract_test_tar_unicode(self, test_path, *args, **kwargs):
        return self.__extract(test_path, extract_tar_uni)


def _extract_tar_raw(test_path, target_dir, to_bytes, *args, **kwargs):
    """
    Raw simplified extract for certain really weird paths and file
    names.
    """
    if to_bytes:
        # use bytes for paths on ALL OSes (though this may fail on macOS)
        target_dir = fsencode(target_dir)
        test_path = fsencode(test_path)
    tar = tarfile.open(test_path)
    tar.extractall(path=target_dir)
    tar.close()


extract_tar_raw = partial(_extract_tar_raw, to_bytes=True)

extract_tar_uni = partial(_extract_tar_raw, to_bytes=False)


def extract_tar(location, target_dir, verbatim=False, *args, **kwargs):
    """
    Extract a tar archive at location in the target_dir directory.
    If `verbatim` is True preserve the permissions.
    """
    # always for using bytes for paths on all OSses... tar seems to use bytes internally
    # and get confused otherwise
    location = fsencode(location)
    target_dir = fsencode(target_dir)

    with open(location, 'rb') as input_tar:
        tar = None
        try:
            tar = tarfile.open(fileobj=input_tar)
            tarinfos = tar.getmembers()
            to_extract = []
            for tarinfo in tarinfos:
                if tar_can_extract(tarinfo, verbatim):
                    if not verbatim:
                        tarinfo.mode = 0700
                    to_extract.append(tarinfo)
            tar.extractall(target_dir, members=to_extract)
        finally:
            if tar:
                tar.close()


def extract_zip(location, target_dir, *args, **kwargs):
    """
    Extract a zip archive file at location in the target_dir directory.
    """
    if not os.path.isfile(location) and zipfile.is_zipfile(location):
        raise Exception('Incorrect zip file %(location)r' % locals())

    if on_linux:
        location = fsencode(location)
        target_dir = fsencode(target_dir)

    with zipfile.ZipFile(location) as zipf:
        for info in zipf.infolist():
            name = info.filename
            content = zipf.read(name)
            target = os.path.join(target_dir, name)
            if not os.path.exists(os.path.dirname(target)):
                os.makedirs(os.path.dirname(target))
            if not content and target.endswith(os.path.sep):
                if not os.path.exists(target):
                    os.makedirs(target)
            if not os.path.exists(target):
                with open(target, 'wb') as f:
                    f.write(content)


def extract_zip_raw(location, target_dir, *args, **kwargs):
    """
    Extract a zip archive file at location in the target_dir directory.
    Use the builtin extractall function
    """
    if not os.path.isfile(location) and zipfile.is_zipfile(location):
        raise Exception('Incorrect zip file %(location)r' % locals())

    if on_linux:
        location = fsencode(location)
        target_dir = fsencode(target_dir)

    with zipfile.ZipFile(location) as zipf:
        zipf.extractall(path=target_dir)


def tar_can_extract(tarinfo, verbatim):
    """
    Return True if a tar member can be extracted to handle OS specifics.
    If verbatim is True, always return True.
    """
    if tarinfo.ischr():
        # never extract char devices
        return False

    if verbatim:
        # extract all on all OSse
        return True

    # FIXME: not sure hard links are working OK on Windows
    include = tarinfo.type in tarfile.SUPPORTED_TYPES
    exclude = tarinfo.isdev() or (on_windows and tarinfo.issym())

    if include and not exclude:
        return True


class FileBasedTesting(TestCaseClass, FileDrivenTesting):
    pass


class dircmp(filecmp.dircmp):
    """
    Compare the content of dir1 and dir2. In contrast with filecmp.dircmp,
    this subclass also compares the content of files with the same path.
    """

    def phase3(self):
        """
        Find out differences between common files.
        Ensure we are using content comparison, not os.stat-only.
        """
        comp = filecmp.cmpfiles(self.left, self.right, self.common_files, shallow=False)
        self.same_files, self.diff_files, self.funny_files = comp


def is_same(dir1, dir2):
    """
    Compare two directory trees for structure and file content.
    Return False if they differ, True is they are the same.
    """
    compared = dircmp(dir1, dir2)
    if (compared.left_only or compared.right_only or compared.diff_files
        or compared.funny_files):
        return False

    for subdir in compared.common_dirs:
        if not is_same(os.path.join(dir1, subdir),
                       os.path.join(dir2, subdir)):
            return False
    return True


def file_cmp(file1, file2, ignore_line_endings=False):
    """
    Compare two files content.
    Return False if they differ, True is they are the same.
    """
    with open(file1, 'rb') as f1:
        f1c = f1.read()
        if ignore_line_endings:
            f1c = b'\n'.join(f1c.splitlines(False))
    with open(file2, 'rb') as f2:
        f2c = f2.read()
        if ignore_line_endings:
            f2c = b'\n'.join(f2c.splitlines(False))
    assert f1c == f2c


def make_non_readable(location):
    """
    Make location non readable for tests purpose.
    """
    if on_posix:
        current_stat = stat.S_IMODE(os.lstat(location).st_mode)
        os.chmod(location, current_stat & ~stat.S_IREAD)
    else:
        os.chmod(location, 0555)


def make_non_writable(location):
    """
    Make location non writable for tests purpose.
    """
    if on_posix:
        current_stat = stat.S_IMODE(os.lstat(location).st_mode)
        os.chmod(location, current_stat & ~stat.S_IWRITE)
    else:
        make_non_readable(location)


def make_non_executable(location):
    """
    Make location non executable for tests purpose.
    """
    if on_posix:
        current_stat = stat.S_IMODE(os.lstat(location).st_mode)
        os.chmod(location, current_stat & ~stat.S_IEXEC)
