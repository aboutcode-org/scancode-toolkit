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

from __future__ import absolute_import, print_function

import os
import tempfile
from os.path import abspath
from os.path import dirname
from os.path import join
from os.path import sep
from unittest import TestCase
from unittest import skipIf

from commoncode import filetype
from commoncode import fileutils
from commoncode.fileutils import as_posixpath
from commoncode.fileutils import path_to_bytes
from commoncode.fileutils import path_to_unicode
from commoncode.system import on_linux
from commoncode.system import on_posix
from commoncode.system import on_mac
from commoncode.system import on_windows
from commoncode.testcase import FileBasedTesting
from commoncode.testcase import make_non_executable
from commoncode.testcase import make_non_readable
from commoncode.testcase import make_non_writable


class TestPermissions(FileBasedTesting):
    """
    Several assertions or test are skipped on non posix OSes.
    Windows handles permissions and special files differently.
    """
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_chmod_on_non_existing_file_throws_no_exception(self):
        fileutils.chmod('some non existing dir', fileutils.RWX)

    def test_chmod_read_write_recursively_on_dir(self):
        test_dir = self.get_test_loc('fileutils/executable', copy=True)
        test_file = join(test_dir, 'deep1', 'deep2', 'ctags')
        test_dir2 = join(test_dir, 'deep1', 'deep2')
        parent = join(test_dir, 'deep1')

        try:
            make_non_writable(test_file)
            assert not filetype.is_writable(test_file)
            if on_posix:
                make_non_executable(test_file)
                assert not filetype.is_executable(test_file)

            if on_posix:
                make_non_executable(test_dir2)
                assert not filetype.is_executable(test_dir2)
            make_non_writable(test_dir)
            if on_posix:
                assert not filetype.is_writable(test_dir2)

            fileutils.chmod(parent, fileutils.RW, recurse=True)

            assert filetype.is_readable(test_dir2) is True
            assert filetype.is_writable(test_dir2)
            if on_posix:
                assert filetype.is_executable(test_dir2)
        finally:
            fileutils.chmod(test_dir, fileutils.RW, recurse=True)

    def test_chmod_read_write_non_recursively_on_dir(self):
        test_dir = self.get_test_loc('fileutils/executable', copy=True)
        test_file = join(test_dir, 'deep1', 'deep2', 'ctags')
        test_dir = join(test_dir, 'deep1', 'deep2')
        parent = join(test_dir, 'deep1')

        try:
            # setup
            make_non_writable(test_file)
            assert not filetype.is_writable(test_file)

            make_non_writable(test_dir)
            if on_posix:
                assert not filetype.is_writable(test_dir)
            else:
                # windows is different
                assert filetype.is_writable(test_dir)

            fileutils.chmod(parent, fileutils.RW, recurse=False)
            # test: the perms should be the same
            assert not filetype.is_writable(test_file)

            if on_posix:
                assert not filetype.is_writable(test_dir)
            else:
                # windows is different
                assert filetype.is_writable(test_dir)
        finally:
            fileutils.chmod(test_dir, fileutils.RW, recurse=True)

    def test_chmod_read_write_file(self):
        test_dir = self.get_test_loc('fileutils/executable', copy=True)
        test_file = join(test_dir, 'deep1', 'deep2', 'ctags')

        try:
            make_non_writable(test_file)
            assert not filetype.is_writable(test_file)

            fileutils.chmod(test_file, fileutils.RW)
            assert filetype.is_readable(test_file)
            assert filetype.is_writable(test_file)
        finally:
            fileutils.chmod(test_dir, fileutils.RW, recurse=True)

    def test_chmod_read_write_exec_dir(self):
        test_dir = self.get_test_loc('fileutils/executable', copy=True)
        test_file = join(test_dir, 'deep1', 'deep2', 'ctags')

        try:
            if on_posix:
                make_non_executable(test_dir)
                assert not filetype.is_executable(test_file)
            make_non_writable(test_dir)

            fileutils.chmod(test_dir, fileutils.RWX, recurse=True)
            assert filetype.is_readable(test_file)
            assert filetype.is_writable(test_file)
            if on_posix:
                assert filetype.is_executable(test_file)
        finally:
            fileutils.chmod(test_dir, fileutils.RW, recurse=True)

    def test_copyfile_does_not_keep_permissions(self):
        src_file = self.get_temp_file()
        dest = self.get_temp_dir()
        with open(src_file, 'wb') as f:
            f.write('')
        try:
            make_non_readable(src_file)
            if on_posix:
                assert not filetype.is_readable(src_file)

            fileutils.copyfile(src_file, dest)
            dest_file = join(dest, os.listdir(dest)[0])
            assert filetype.is_readable(dest_file)
        finally:
            fileutils.chmod(src_file, fileutils.RW, recurse=True)
            fileutils.chmod(dest, fileutils.RW, recurse=True)

    def test_copytree_does_not_keep_non_writable_permissions(self):
        src = self.get_test_loc('fileutils/exec', copy=True)
        dst = self.get_temp_dir()

        try:
            src_file = join(src, 'subtxt/a.txt')
            make_non_writable(src_file)
            assert not filetype.is_writable(src_file)

            src_dir = join(src, 'subtxt')
            make_non_writable(src_dir)
            if on_posix:
                assert not filetype.is_writable(src_dir)

            # copy proper
            dest_dir = join(dst, 'dest')
            fileutils.copytree(src, dest_dir)

            dst_file = join(dest_dir, 'subtxt/a.txt')
            assert os.path.exists(dst_file)
            assert filetype.is_writable(dst_file)

            dest_dir2 = join(dest_dir, 'subtxt')
            assert os.path.exists(dest_dir2)
            assert filetype.is_writable(dest_dir)
        finally:
            fileutils.chmod(src, fileutils.RW, recurse=True)
            fileutils.chmod(dst, fileutils.RW, recurse=True)

    def test_copytree_copies_unreadable_files(self):
        src = self.get_test_loc('fileutils/exec', copy=True)
        dst = self.get_temp_dir()
        src_file1 = join(src, 'a.bat')
        src_file2 = join(src, 'subtxt', 'a.txt')

        try:
            # make some unreadable source files
            make_non_readable(src_file1)
            if on_posix:
                assert not filetype.is_readable(src_file1)

            make_non_readable(src_file2)
            if on_posix:
                assert not filetype.is_readable(src_file2)

            # copy proper
            dest_dir = join(dst, 'dest')
            fileutils.copytree(src, dest_dir)

            dest_file1 = join(dest_dir, 'a.bat')
            assert os.path.exists(dest_file1)
            assert filetype.is_readable(dest_file1)

            dest_file2 = join(dest_dir, 'subtxt', 'a.txt')
            assert os.path.exists(dest_file2)
            assert filetype.is_readable(dest_file2)

        finally:
            fileutils.chmod(src, fileutils.RW, recurse=True)
            fileutils.chmod(dst, fileutils.RW, recurse=True)

    def test_delete_unwritable_directory_and_files(self):
        base_dir = self.get_test_loc('fileutils/readwrite', copy=True)
        test_dir = join(base_dir, 'sub')
        test_file = join(test_dir, 'file')

        try:
            # note: there are no unread/writable dir on windows
            make_non_readable(test_file)
            make_non_executable(test_file)
            make_non_writable(test_file)

            make_non_readable(test_dir)
            make_non_executable(test_dir)
            make_non_writable(test_dir)

            fileutils.delete(test_dir)
            assert not os.path.exists(test_dir)
        finally:
            fileutils.chmod(base_dir, fileutils.RW, recurse=True)


class TestFileUtils(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    @skipIf(on_windows, 'Windows handles special files differently.')
    def test_copytree_does_not_copy_fifo(self):
        # Windows does not support pipes
        src = self.get_test_loc('fileutils/filetype', copy=True)
        dest = self.get_temp_dir()
        src_file = join(src, 'myfifo')
        os.mkfifo(src_file)  # @UndefinedVariable
        dest_dir = join(dest, 'dest')
        fileutils.copytree(src, dest_dir)
        assert not os.path.exists(join(dest_dir, 'myfifo'))

    def test_copyfile_keeps_modified_date(self):
        test_file = self.get_test_loc('fileutils/exec/subtxt/a.txt', copy=True)
        dest = self.get_temp_file()
        expected = 1289918700
        os.utime(test_file, (expected, expected))
        fileutils.copyfile(test_file, dest)
        result = os.stat(dest).st_mtime
        assert expected == result

    def test_copyfile_can_copy_file_to_dir_keeping_full_file_name(self):
        test_file = self.get_test_loc('fileutils/exec/subtxt/a.txt', copy=True)
        dest = self.get_temp_dir()
        expected = os.path.join(dest, 'a.txt')
        fileutils.copyfile(test_file, dest)
        assert os.path.exists(expected)

    def test_read_text_file_with_posix_LF_line_endings(self):
        test_file = self.get_test_loc('fileutils/textfiles/unix_newlines.txt')
        result = fileutils.read_text_file(test_file)[:172]
        expected = (
            '/**************************************************************/\n'
            '/* ADDR.C */\n/* Author: John Doe, 7/2000 */\n'
            '/* Copyright 1999 Cornell University.  All rights reserved. */\n')
        assert expected == result

    def test_read_text_file_with_dos_CRLF_line_endings(self):
        test_file = self.get_test_loc('fileutils/textfiles/dos_newlines.txt')
        result = fileutils.read_text_file(test_file)[:70]
        expected = ('package com.somecompany.somepackage;\n'
                  '\n/**\n * Title:        Some Title\n')
        assert expected == result

    def test_read_text_file_with_mac_CR_lines_endings(self):
        test_file = self.get_test_loc('fileutils/textfiles/mac_newlines.txt')
        result = fileutils.read_text_file(test_file)[:55]
        expected = ('package com.mycompany.test.sort;\n\n/*\n'
                    ' * MergeSort.java\n')
        assert expected == result

    def test_resource_name(self):
        assert 'f' == fileutils.resource_name('/a/b/d/f/f')
        assert 'f' == fileutils.resource_name('/a/b/d/f/f/')
        assert 'f' == fileutils.resource_name('a/b/d/f/f/')
        assert 'f.a' == fileutils.resource_name('/a/b/d/f/f.a')
        assert 'f.a' == fileutils.resource_name('/a/b/d/f/f.a/')
        assert 'f.a' == fileutils.resource_name('a/b/d/f/f.a')
        assert 'f.a' == fileutils.resource_name('f.a')

    def test_os_walk_with_unicode_path(self):
        test_dir = self.extract_test_zip('fileutils/walk/unicode.zip')
        test_dir = join(test_dir, 'unicode')

        test_dir = unicode(test_dir)
        result = list(os.walk(test_dir))
        expected = [
            (unicode(test_dir), ['a'], [u'2.csv']),
            (unicode(test_dir) + sep + 'a', [], [u'gru\u0308n.png'])
        ]
        assert expected == result

    def test_fileutils_walk(self):
        test_dir = self.get_test_loc('fileutils/walk')
        base = self.get_test_loc('fileutils')
        result = [(as_posixpath(t.replace(base, '')), d, sorted(f),) for t, d, f in fileutils.walk(test_dir)]
        expected = [
            ('/walk', ['d1'], ['f', 'unicode.zip']),
            ('/walk/d1', ['d2'], ['f1']),
            ('/walk/d1/d2', ['d3'], ['f2']),
            ('/walk/d1/d2/d3', [], ['f3'])
        ]
        assert expected == result

    def test_fileutils_walk_with_unicode_path(self):
        test_dir = self.extract_test_zip('fileutils/walk/unicode.zip')
        test_dir = join(test_dir, 'unicode')

        if on_linux:
            test_dir = unicode(test_dir)
        result = list(x[-1] for x in fileutils.walk(test_dir))
        if on_linux:
            expected = [['2.csv'], ['gru\xcc\x88n.png']]
        else:
            expected = [[u'2.csv'], [u'gru\u0308n.png']]
        assert expected == result

    def test_fileutils_walk_can_walk_a_single_file(self):
        test_file = self.get_test_loc('fileutils/walk/f')
        result = list(fileutils.walk(test_file))
        expected = [
            (fileutils.parent_directory(test_file), [], ['f'])
        ]
        assert expected == result

    def test_fileutils_walk_can_walk_an_empty_dir(self):
        test_dir = self.get_temp_dir()
        result = list(fileutils.walk(test_dir))
        expected = [
            (test_dir, [], [])
        ]
        assert expected == result

    def test_file_iter(self):
        test_dir = self.get_test_loc('fileutils/walk')
        base = self.get_test_loc('fileutils')
        result = [as_posixpath(f.replace(base, '')) for f in fileutils.file_iter(test_dir)]
        expected = [
            '/walk/f',
            '/walk/unicode.zip',
            '/walk/d1/f1',
            '/walk/d1/d2/f2',
            '/walk/d1/d2/d3/f3'
        ]
        assert sorted(expected) == sorted(result)

    def test_file_iter_can_iterate_a_single_file(self):
        test_file = self.get_test_loc('fileutils/walk/f')
        result = [as_posixpath(f) for f in fileutils.file_iter(test_file)]
        expected = [as_posixpath(test_file)]
        assert expected == result

    def test_file_iter_can_walk_an_empty_dir(self):
        test_dir = self.get_temp_dir()
        result = list(fileutils.file_iter(test_dir))
        expected = []
        assert expected == result

    def test_resource_iter_with_files_no_dir(self):
        test_dir = self.get_test_loc('fileutils/walk')
        base = self.get_test_loc('fileutils')
        result = sorted([as_posixpath(f.replace(base, ''))
                         for f in fileutils.resource_iter(test_dir, with_files=True, with_dirs=False)])
        expected = [
            '/walk/f',
            '/walk/unicode.zip',
            '/walk/d1/f1',
            '/walk/d1/d2/f2',
            '/walk/d1/d2/d3/f3'
        ]
        assert sorted(expected) == sorted(result)

    def test_resource_iter_with_files_and_dir(self):
        test_dir = self.get_test_loc('fileutils/walk')
        base = self.get_test_loc('fileutils')
        result = sorted([as_posixpath(f.replace(base, ''))
                         for f in fileutils.resource_iter(test_dir, with_files=True, with_dirs=True)])
        expected = [
            '/walk/d1',
            '/walk/d1/d2',
            '/walk/d1/d2/d3',
            '/walk/d1/d2/d3/f3',
            '/walk/d1/d2/f2',
            '/walk/d1/f1',
            '/walk/f',
            '/walk/unicode.zip'
        ]
        assert sorted(expected) == sorted(result)

    def test_resource_iter_with_dir_only(self):
        test_dir = self.get_test_loc('fileutils/walk')
        base = self.get_test_loc('fileutils')
        result = sorted([as_posixpath(f.replace(base, ''))
                         for f in fileutils.resource_iter(test_dir, with_files=False, with_dirs=True)])
        expected = [
             '/walk/d1',
             '/walk/d1/d2',
             '/walk/d1/d2/d3',
        ]
        assert sorted(expected) == sorted(result)

    def test_resource_iter_return_byte_on_byte_input(self):
        test_dir = self.get_test_loc('fileutils/walk')
        base = self.get_test_loc('fileutils')
        result = sorted([as_posixpath(f.replace(base, ''))
                         for f in fileutils.resource_iter(test_dir, with_files=True, with_dirs=True)])
        expected = [
            '/walk/d1',
            '/walk/d1/d2',
            '/walk/d1/d2/d3',
            '/walk/d1/d2/d3/f3',
            '/walk/d1/d2/f2',
            '/walk/d1/f1',
            '/walk/f',
            '/walk/unicode.zip'
        ]
        assert sorted(expected) == sorted(result)
        if on_linux:
            assert all(isinstance(p, bytes) for p in result)
        else:
            assert all(isinstance(p, unicode) for p in result)

    def test_resource_iter_return_unicode_on_unicode_input(self):
        test_dir = self.get_test_loc('fileutils/walk')
        base = unicode(self.get_test_loc('fileutils'))
        result = sorted([as_posixpath(f.replace(base, ''))
                         for f in fileutils.resource_iter(test_dir, with_files=True, with_dirs=True)])
        expected = [
            u'/walk/d1',
            u'/walk/d1/d2',
            u'/walk/d1/d2/d3',
            u'/walk/d1/d2/d3/f3',
            u'/walk/d1/d2/f2',
            u'/walk/d1/f1',
            u'/walk/f',
            u'/walk/unicode.zip'
        ]
        assert sorted(expected) == sorted(result)
        assert all(isinstance(p, unicode) for p in result)

    def test_resource_iter_can_iterate_a_single_file(self):
        test_file = self.get_test_loc('fileutils/walk/f')
        result = [as_posixpath(f) for f in fileutils.resource_iter(test_file)]
        expected = [as_posixpath(test_file)]
        assert expected == result

    def test_resource_iter_can_walk_an_empty_dir(self):
        test_dir = self.get_temp_dir()
        result = list(fileutils.resource_iter(test_dir))
        expected = []
        assert expected == result

    def test_fileutils_resource_iter_can_walk_unicode_path_with_zip(self):
        test_dir = self.extract_test_zip('fileutils/walk/unicode.zip')
        test_dir = join(test_dir, 'unicode')

        if on_linux:
            EMPTY_STRING = ''
        else:
            test_dir = unicode(test_dir)
            EMPTY_STRING = u''

        result = sorted([p.replace(test_dir, EMPTY_STRING) for p in fileutils.resource_iter(test_dir)])
        if on_linux:
            expected = [
                '/2.csv',
                '/a',
                '/a/gru\xcc\x88n.png'
            ]
        elif on_mac:
            expected = [
                u'/2.csv',
                u'/a',
                u'/a/gru\u0308n.png'
            ]
        elif on_windows:
            expected = [
                u'\\2.csv',
                u'\\a',
                u'\\a\\gru\u0308n.png'
            ]
        assert expected == result

    def test_resource_iter_can_walk_non_utf8_path_from_unicode_path(self):
        test_dir = self.extract_test_tar_raw('fileutils/walk_non_utf8/non_unicode.tgz')
        test_dir = join(test_dir, 'non_unicode')

        if not on_linux:
            test_dir = unicode(test_dir)
        result = list(fileutils.resource_iter(test_dir))
        assert 18 == len(result)

    def test_walk_can_walk_non_utf8_path_from_unicode_path(self):
        test_dir = self.extract_test_tar_raw('fileutils/walk_non_utf8/non_unicode.tgz')
        test_dir = join(test_dir, 'non_unicode')

        if not on_linux:
            test_dir = unicode(test_dir)
        result = list(fileutils.walk(test_dir))[0]
        _dirpath, _dirnames, filenames = result
        assert 18 == len(filenames)

    def test_file_iter_can_walk_non_utf8_path_from_unicode_path(self):
        test_dir = self.extract_test_tar_raw('fileutils/walk_non_utf8/non_unicode.tgz')
        test_dir = join(test_dir, 'non_unicode')

        if not on_linux:
            test_dir = unicode(test_dir)
        result = list(fileutils.file_iter(test_dir))
        assert 18 == len(result)

    def test_os_walk_can_walk_non_utf8_path_from_unicode_path(self):
        test_dir = self.extract_test_tar_raw('fileutils/walk_non_utf8/non_unicode.tgz')
        test_dir = join(test_dir, 'non_unicode')

        if not on_linux:
            test_dir = unicode(test_dir)
        result = list(os.walk(test_dir))[0]
        _dirpath, _dirnames, filenames = result
        assert 18 == len(filenames)

    @skipIf(on_windows, 'Windows FS encoding is ... different')
    def test_path_to_unicode_and_path_to_bytes_are_idempotent(self):
        a = b'foo\xb1bar'
        b = u'foo\udcb1bar'
        assert a == path_to_bytes(path_to_unicode(a))
        assert a == path_to_bytes(path_to_unicode(b))
        assert b == path_to_unicode(path_to_bytes(a))
        assert b == path_to_unicode(path_to_bytes(b))


class TestBaseName(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_file_base_name_on_path_and_location_1(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/.a/file'
        expected_name = 'file'
        result = fileutils.file_base_name(test_file)
        assert expected_name == result
        result = fileutils.file_base_name(join(test_dir, test_file))
        assert expected_name == result

    def test_file_base_name_on_file_path_for_dot_file  (self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/.a/'
        expected_name = '.a'
        result = fileutils.file_base_name(test_file)
        assert expected_name == result
        result = fileutils.file_base_name(join(test_dir, test_file))
        assert expected_name == result

    def test_file_base_name_on_file_path_for_dot_file_with_extension(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/b/.a.b'
        expected_name = '.a'
        result = fileutils.file_base_name(test_file)
        assert expected_name == result
        result = fileutils.file_base_name(join(test_dir, test_file))
        assert expected_name == result

    def test_file_base_name_on_file_path_for_file_with_unknown_composed_extension(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/b/a.tag.gz'
        expected_name = 'a.tag'
        result = fileutils.file_base_name(test_file)
        assert expected_name == result
        result = fileutils.file_base_name(join(test_dir, test_file))
        assert expected_name == result

    def test_file_base_name_on_file_path_for_file_with_known_composed_extension(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/b/a.tar.gz'
        expected_name = 'a'
        result = fileutils.file_base_name(test_file)
        assert expected_name == result
        result = fileutils.file_base_name(join(test_dir, test_file))
        assert expected_name == result

    def test_file_base_name_on_dir_path(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/b/'
        expected_name = 'b'
        result = fileutils.file_base_name(test_file)
        assert expected_name == result
        result = fileutils.file_base_name(join(test_dir, test_file))
        assert expected_name == result

    def test_file_base_name_on_plain_file(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/f.a'
        expected_name = 'f'
        result = fileutils.file_base_name(test_file)
        assert expected_name == result
        result = fileutils.file_base_name(join(test_dir, test_file))
        assert expected_name == result

    def test_file_base_name_on_plain_file_with_parent_dir_extension(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'f.a/a.c'
        expected_name = 'a'
        result = fileutils.file_base_name(test_file)
        assert expected_name == result
        result = fileutils.file_base_name(join(test_dir, test_file))
        assert expected_name == result

    def test_file_base_name_on_path_for_plain_dir(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/'
        expected_name = 'a'
        result = fileutils.file_base_name(test_file)
        assert expected_name == result
        result = fileutils.file_base_name(join(test_dir, test_file))
        assert expected_name == result

    def test_file_base_name_on_path_for_plain_dir_with_extension(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'f.a/'
        expected_name = 'f.a'
        result = fileutils.file_base_name(test_file)
        assert expected_name == result
        result = fileutils.file_base_name(join(test_dir, test_file))
        assert expected_name == result

    def test_file_base_name_on_path_for_plain_file(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'tst'
        expected_name = 'tst'
        result = fileutils.file_base_name(test_file)
        assert expected_name == result
        result = fileutils.file_base_name(join(test_dir, test_file))
        assert expected_name == result


class TestFileName(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_file_name_on_path_and_location_1(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/.a/file'
        expected_name = 'file'
        result = fileutils.file_name(test_file)
        assert expected_name == result
        result = fileutils.file_name((os.path.join(test_dir, test_file)))
        assert expected_name == result

    def test_file_name_on_path_and_location_2(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/.a/'
        expected_name = '.a'
        result = fileutils.file_name(test_file)
        assert expected_name == result
        result = fileutils.file_name((os.path.join(test_dir, test_file)))
        assert expected_name == result

    def test_file_name_on_path_and_location_3(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/b/.a.b'
        expected_name = '.a.b'
        result = fileutils.file_name(test_file)
        assert expected_name == result
        result = fileutils.file_name((os.path.join(test_dir, test_file)))
        assert expected_name == result

    def test_file_name_on_path_and_location_4(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/b/a.tag.gz'
        expected_name = 'a.tag.gz'
        result = fileutils.file_name(test_file)
        assert expected_name == result
        result = fileutils.file_name((os.path.join(test_dir, test_file)))
        assert expected_name == result

    def test_file_name_on_path_and_location_5(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/b/'
        expected_name = 'b'
        result = fileutils.file_name(test_file)
        assert expected_name == result
        result = fileutils.file_name((os.path.join(test_dir, test_file)))
        assert expected_name == result

    def test_file_name_on_path_and_location_6(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/f.a'
        expected_name = 'f.a'
        result = fileutils.file_name(test_file)
        assert expected_name == result
        result = fileutils.file_name((os.path.join(test_dir, test_file)))
        assert expected_name == result

    def test_file_name_on_path_and_location_7(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/'
        expected_name = 'a'
        result = fileutils.file_name(test_file)
        assert expected_name == result
        result = fileutils.file_name((os.path.join(test_dir, test_file)))
        assert expected_name == result

    def test_file_name_on_path_and_location_8(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'f.a/a.c'
        expected_name = 'a.c'
        result = fileutils.file_name(test_file)
        assert expected_name == result
        result = fileutils.file_name((os.path.join(test_dir, test_file)))
        assert expected_name == result

    def test_file_name_on_path_and_location_9(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'f.a/'
        expected_name = 'f.a'
        result = fileutils.file_name(test_file)
        assert expected_name == result
        result = fileutils.file_name((os.path.join(test_dir, test_file)))
        assert expected_name == result

    def test_file_name_on_path_and_location_10(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'tst'
        expected_name = 'tst'
        result = fileutils.file_name(test_file)
        assert expected_name == result
        result = fileutils.file_name((os.path.join(test_dir, test_file)))
        assert expected_name == result


class TestFileExtension(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_file_extension_on_path_and_location_1(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/.a/file'
        expected_name = ''
        result = fileutils.file_extension(test_file)
        assert expected_name == result
        result = fileutils.file_extension((os.path.join(test_dir, test_file)))
        assert expected_name == result

    def test_file_extension_on_path_and_location_2(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/.a/'
        expected_name = ''
        result = fileutils.file_extension(test_file)
        assert expected_name == result
        result = fileutils.file_extension((os.path.join(test_dir, test_file)))
        assert expected_name == result

    def test_file_extension_on_path_and_location_3(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/b/.a.b'
        expected_name = '.b'
        result = fileutils.file_extension(test_file)
        assert expected_name == result
        result = fileutils.file_extension((os.path.join(test_dir, test_file)))
        assert expected_name == result

    def test_file_extension_on_path_and_location_4(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/b/a.tag.gz'
        expected_name = '.gz'
        result = fileutils.file_extension(test_file)
        assert expected_name == result
        result = fileutils.file_extension((os.path.join(test_dir, test_file)))
        assert expected_name == result

    def test_file_extension_on_path_and_location_5(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/b/'
        expected_name = ''
        result = fileutils.file_extension(test_file)
        assert expected_name == result
        result = fileutils.file_extension((os.path.join(test_dir, test_file)))
        assert expected_name == result

    def test_file_extension_on_path_and_location_6(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/f.a'
        expected_name = '.a'
        result = fileutils.file_extension(test_file)
        assert expected_name == result
        result = fileutils.file_extension((os.path.join(test_dir, test_file)))
        assert expected_name == result

    def test_file_extension_on_path_and_location_7(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/'
        expected_name = ''
        result = fileutils.file_extension(test_file)
        assert expected_name == result
        result = fileutils.file_extension((os.path.join(test_dir, test_file)))
        assert expected_name == result

    def test_file_extension_on_path_and_location_8(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'f.a/a.c'
        expected_name = '.c'
        result = fileutils.file_extension(test_file)
        assert expected_name == result
        result = fileutils.file_extension((os.path.join(test_dir, test_file)))
        assert expected_name == result

    def test_file_extension_on_path_and_location_9(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'f.a/'
        expected_name = ''
        result = fileutils.file_extension(test_file)
        assert expected_name == result
        result = fileutils.file_extension((os.path.join(test_dir, test_file)))
        assert expected_name == result

    def test_file_extension_on_path_and_location_10(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'tst'
        expected_name = ''
        result = fileutils.file_extension(test_file)
        assert expected_name == result
        result = fileutils.file_extension((os.path.join(test_dir, test_file)))
        assert expected_name == result


class TestParentDir(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parent_directory_on_path_and_location_1(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/.a/file'
        expected_name = 'a/.a/'
        result = fileutils.parent_directory(test_file)
        result = fileutils.as_posixpath(result)
        assert expected_name == result

        result = fileutils.parent_directory((os.path.join(test_dir, test_file)))
        result = fileutils.as_posixpath(result)
        assert result.endswith(expected_name)

    def test_parent_directory_on_path_and_location_2(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/.a/'
        expected_name = 'a/'
        result = fileutils.parent_directory(test_file)
        result = fileutils.as_posixpath(result)
        assert expected_name == result

        result = fileutils.parent_directory((os.path.join(test_dir, test_file)))
        result = fileutils.as_posixpath(result)
        assert result.endswith(expected_name)

    def test_parent_directory_on_path_and_location_3(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/b/.a.b'
        expected_name = 'a/b/'
        result = fileutils.parent_directory(test_file)
        result = fileutils.as_posixpath(result)
        assert expected_name == result

        result = fileutils.parent_directory((os.path.join(test_dir, test_file)))
        result = fileutils.as_posixpath(result)
        assert result.endswith(expected_name)

    def test_parent_directory_on_path_and_location_4(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/b/a.tag.gz'
        expected_name = 'a/b/'
        result = fileutils.parent_directory(test_file)
        result = fileutils.as_posixpath(result)
        assert expected_name == result

        result = fileutils.parent_directory((os.path.join(test_dir, test_file)))
        result = fileutils.as_posixpath(result)
        assert result.endswith(expected_name)

    def test_parent_directory_on_path_and_location_5(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/b/'
        expected_name = 'a/'
        result = fileutils.parent_directory(test_file)
        result = fileutils.as_posixpath(result)
        assert expected_name == result

        result = fileutils.parent_directory((os.path.join(test_dir, test_file)))
        result = fileutils.as_posixpath(result)
        assert result.endswith(expected_name)

    def test_parent_directory_on_path_and_location_6(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/f.a'
        expected_name = 'a/'
        result = fileutils.parent_directory(test_file)
        result = fileutils.as_posixpath(result)
        assert expected_name == result

        result = fileutils.parent_directory((os.path.join(test_dir, test_file)))
        result = fileutils.as_posixpath(result)
        assert result.endswith(expected_name)

    def test_parent_directory_on_path_and_location_7(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/'
        expected_name = '/'
        result = fileutils.parent_directory(test_file)
        result = fileutils.as_posixpath(result)
        assert expected_name == result

        result = fileutils.parent_directory((os.path.join(test_dir, test_file)))
        result = fileutils.as_posixpath(result)
        assert result.endswith(expected_name)

    def test_parent_directory_on_path_and_location_8(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'f.a/a.c'
        expected_name = 'f.a/'
        result = fileutils.parent_directory(test_file)
        result = fileutils.as_posixpath(result)
        assert expected_name == result

        result = fileutils.parent_directory((os.path.join(test_dir, test_file)))
        result = fileutils.as_posixpath(result)
        assert result.endswith(expected_name)

    def test_parent_directory_on_path_and_location_9(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'f.a/'
        expected_name = '/'
        result = fileutils.parent_directory(test_file)
        result = fileutils.as_posixpath(result)
        assert expected_name == result

        result = fileutils.parent_directory((os.path.join(test_dir, test_file)))
        result = fileutils.as_posixpath(result)
        assert result.endswith(expected_name)

    def test_parent_directory_on_path_and_location_10(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'tst'
        expected_name = '/'
        result = fileutils.parent_directory(test_file)
        result = fileutils.as_posixpath(result)
        assert expected_name == result

        result = fileutils.parent_directory((os.path.join(test_dir, test_file)))
        result = fileutils.as_posixpath(result)
        assert result.endswith(expected_name)


class TestBuildCachePath(TestCase):

    def setUp(self):
        self._old_val = os.environ.get(fileutils.TMP_DIR_ENV)
        if self._old_val:
            del os.environ[fileutils.TMP_DIR_ENV]

    def tearDown(self):
        if self._old_val:
            os.environ[fileutils.TMP_DIR_ENV] = self._old_val
        elif fileutils.TMP_DIR_ENV in os.environ:
            del os.environ[fileutils.TMP_DIR_ENV]

    def test_in_dev_mode(self):
        root_dir = dirname(dirname(dirname(abspath(__file__))))
        expected_path = join(root_dir, '.cache', 'scancode', 'testing')
        cache_path = fileutils.build_cache_path('testing', dev_mode=True)
        assert expected_path == cache_path

    def test_not_in_dev_mode(self):
        expected_path = join(os.path.expanduser('~'), '.cache', 'scancode', 'testing')
        cache_path = fileutils.build_cache_path('testing', dev_mode=False)
        assert expected_path == cache_path

    def test_env_var_overrides(self):
        root_dir = tempfile.gettempdir()
        os.environ[fileutils.TMP_DIR_ENV] = root_dir
        expected_path = join(root_dir, '.cache', 'scancode', 'testing')
        cache_path = fileutils.build_cache_path('testing', dev_mode=True)
        assert cache_path == expected_path

    def test_raises_on_invalid_env_var(self):
        root_dir = '/nosuchdir'
        os.environ[fileutils.TMP_DIR_ENV] = root_dir
        expected_path = join(root_dir, '.cache', 'scancode', 'testing')
        self.assertRaises(OSError, fileutils.build_cache_path, 'testing', dev_mode=True)
