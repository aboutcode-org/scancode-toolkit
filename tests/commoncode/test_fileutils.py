#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/commoncode for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
from os.path import join
from os.path import sep
from unittest.case import skip
from unittest.case import skipIf

from commoncode import filetype
from commoncode import fileutils
from commoncode.fileutils import as_posixpath
from commoncode.system import on_linux
from commoncode.system import on_posix
from commoncode.system import on_mac
from commoncode.system import on_macos_14_or_higher
from commoncode.system import on_windows
from commoncode.testcase import FileBasedTesting
from commoncode.testcase import make_non_executable
from commoncode.testcase import make_non_readable
from commoncode.testcase import make_non_writable


@skip('Somehow permissions tests do not work OK yet on Python 3')
class TestPermissionsDeletions(FileBasedTesting):
    """
    This is failing for now on Python 3
    """
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

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
        with open(src_file, 'w') as f:
            f.write(u'')
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


class TestFileUtils(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    @skipIf(on_windows, 'Windows handles special files differently.')
    def test_copytree_does_not_copy_fifo(self):
        # Windows does not support pipes
        src = self.get_test_loc('fileutils/filetype', copy=True)
        dest = self.get_temp_dir()
        src_file = join(src, 'myfifo')
        os.mkfifo(src_file)  # NOQA
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
        assert result == expected

    def test_copyfile_can_copy_file_to_dir_keeping_full_file_name(self):
        test_file = self.get_test_loc('fileutils/exec/subtxt/a.txt', copy=True)
        dest = self.get_temp_dir()
        expected = os.path.join(dest, 'a.txt')
        fileutils.copyfile(test_file, dest)
        assert os.path.exists(expected)

    def test_resource_name(self):
        assert fileutils.resource_name('/a/b/d/f/f') == 'f'
        assert fileutils.resource_name('/a/b/d/f/f/') == 'f'
        assert fileutils.resource_name('a/b/d/f/f/') == 'f'
        assert fileutils.resource_name('/a/b/d/f/f.a') == 'f.a'
        assert fileutils.resource_name('/a/b/d/f/f.a/') == 'f.a'
        assert fileutils.resource_name('a/b/d/f/f.a') == 'f.a'
        assert fileutils.resource_name('f.a') == 'f.a'

    @skipIf(on_windows, 'Windows FS encoding is ... different!')
    def test_fsdecode_and_fsencode_are_idempotent(self):
        a = b'foo\xb1bar'
        b = u'foo\udcb1bar'
        assert os.fsencode(os.fsdecode(a)) == a
        assert os.fsencode(os.fsdecode(b)) == a
        assert os.fsdecode(os.fsencode(a)) == b
        assert os.fsdecode(os.fsencode(b)) == b


class TestFileUtilsWalk(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_os_walk_with_unicode_path(self):
        test_dir = self.extract_test_zip('fileutils/walk/unicode.zip')
        test_dir = join(test_dir, 'unicode')

        test_dir = str(test_dir)
        result = list(os.walk(test_dir))
        expected = [
            (str(test_dir), ['a'], [u'2.csv']),
            (str(test_dir) + sep + 'a', [], [u'gru\u0308n.png'])
        ]
        assert result == expected

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
        assert result == expected

    def test_fileutils_walk_with_unicode_path(self):
        test_dir = self.extract_test_zip('fileutils/walk/unicode.zip')
        test_dir = join(test_dir, 'unicode')

        result = list(x[-1] for x in fileutils.walk(test_dir))
        expected = [[u'2.csv'], [u'gru\u0308n.png']]
        assert result == expected

    def test_fileutils_walk_can_walk_a_single_file(self):
        test_file = self.get_test_loc('fileutils/walk/f')
        result = list(fileutils.walk(test_file))
        expected = [
            (fileutils.parent_directory(test_file), [], ['f'])
        ]
        assert result == expected

    def test_fileutils_walk_can_walk_an_empty_dir(self):
        test_dir = self.get_temp_dir()
        result = list(fileutils.walk(test_dir))
        expected = [
            (test_dir, [], [])
        ]
        assert result == expected

    @skipIf(on_macos_14_or_higher, 'Cannot handle yet byte paths on macOS 10.14+. See https://github.com/nexB/scancode-toolkit/issues/1635')
    def test_walk_can_walk_non_utf8_path_from_unicode_path(self):
        test_dir = self.extract_test_tar_raw('fileutils/walk_non_utf8/non_unicode.tgz')
        test_dir = join(test_dir, 'non_unicode')

        if not on_linux:
            test_dir = str(test_dir)
        result = list(fileutils.walk(test_dir))[0]
        _dirpath, _dirnames, filenames = result
        assert len(filenames) == 18

    @skipIf(on_macos_14_or_higher, 'Cannot handle yet byte paths on macOS 10.14+. See https://github.com/nexB/scancode-toolkit/issues/1635')
    def test_os_walk_can_walk_non_utf8_path_from_unicode_path(self):
        test_dir = self.extract_test_tar_raw('fileutils/walk_non_utf8/non_unicode.tgz')
        test_dir = join(test_dir, 'non_unicode')

        result = list(os.walk(test_dir))[0]
        _dirpath, _dirnames, filenames = result
        assert len(filenames) == 18

    @skipIf(on_windows, 'os.symlink does not work on Windows')
    def test_walk_on_symlinks(self):
        test_dir = self.get_test_loc('symlink/walk', copy=True)
        temp_dir = fileutils.get_temp_dir()
        test_link = join(temp_dir, 'test-dir-link')
        os.symlink(test_dir, test_link)
        results = list(fileutils.walk(test_link, follow_symlinks=True))
        results = [(os.path.basename(top), dirs, files) for top, dirs, files in results]
        expected = [
            ('test-dir-link', ['dir'], ['a']),
            ('dir', [], ['b'])
        ]
        assert results == expected


class TestFileUtilsIter(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_resource_iter(self):
        test_dir = self.get_test_loc('fileutils/walk')
        base = self.get_test_loc('fileutils')
        result = [as_posixpath(f.replace(base, '')) for f in fileutils.resource_iter(test_dir, with_dirs=False)]
        expected = [
            '/walk/f',
            '/walk/unicode.zip',
            '/walk/d1/f1',
            '/walk/d1/d2/f2',
            '/walk/d1/d2/d3/f3'
        ]
        assert sorted(result) == sorted(expected)

    def test_resource_iter_can_iterate_a_single_file(self):
        test_file = self.get_test_loc('fileutils/walk/f')
        result = [as_posixpath(f) for f in fileutils.resource_iter(test_file, with_dirs=False)]
        expected = [as_posixpath(test_file)]
        assert result == expected

    def test_resource_iter_can_iterate_a_single_file_with_dirs(self):
        test_file = self.get_test_loc('fileutils/walk/f')
        result = [as_posixpath(f) for f in fileutils.resource_iter(test_file, with_dirs=True)]
        expected = [as_posixpath(test_file)]
        assert result == expected

    def test_resource_iter_can_walk_an_empty_dir(self):
        test_dir = self.get_temp_dir()
        result = list(fileutils.resource_iter(test_dir, with_dirs=False))
        expected = []
        assert result == expected

    def test_resource_iter_can_walk_an_empty_dir_with_dirs(self):
        test_dir = self.get_temp_dir()
        result = list(fileutils.resource_iter(test_dir, with_dirs=False))
        expected = []
        assert result == expected

    def test_resource_iter_without_dir(self):
        test_dir = self.get_test_loc('fileutils/walk')
        base = self.get_test_loc('fileutils')
        result = sorted([as_posixpath(f.replace(base, ''))
                         for f in fileutils.resource_iter(test_dir, with_dirs=False)])
        expected = [
            '/walk/f',
            '/walk/unicode.zip',
            '/walk/d1/f1',
            '/walk/d1/d2/f2',
            '/walk/d1/d2/d3/f3'
        ]
        assert sorted(result) == sorted(expected)

    def test_resource_iter_with_dirs(self):
        test_dir = self.get_test_loc('fileutils/walk')
        base = self.get_test_loc('fileutils')
        result = sorted([as_posixpath(f.replace(base, ''))
                         for f in fileutils.resource_iter(test_dir, with_dirs=True)])
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
        assert sorted(result) == sorted(expected)

    def test_resource_iter_return_byte_on_byte_input(self):
        test_dir = self.get_test_loc('fileutils/walk')
        base = self.get_test_loc('fileutils')
        result = sorted([as_posixpath(f.replace(base, ''))
                         for f in fileutils.resource_iter(test_dir, with_dirs=True)])
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
        assert sorted(result) == sorted(expected)
        assert all(isinstance(p, str) for p in result)

    def test_resource_iter_return_unicode_on_unicode_input(self):
        test_dir = self.get_test_loc('fileutils/walk')
        base = str(self.get_test_loc('fileutils'))
        result = sorted([as_posixpath(f.replace(base, ''))
                         for f in fileutils.resource_iter(test_dir, with_dirs=True)])
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
        assert sorted(result) == sorted(expected)
        assert all(isinstance(p, str) for p in result)

    def test_resource_iter_can_walk_unicode_path_with_zip(self):
        test_dir = self.extract_test_zip('fileutils/walk/unicode.zip')
        test_dir = join(test_dir, 'unicode')

        test_dir = str(test_dir)

        result = sorted([p.replace(test_dir, '') for p in fileutils.resource_iter(test_dir)])
        if on_linux:
            expected = [
                u'/2.csv',
                u'/a',
                u'/a/gru\u0308n.png'
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
        assert result == expected

    @skipIf(on_macos_14_or_higher, 'Cannot handle yet byte paths on macOS 10.14+. See https://github.com/nexB/scancode-toolkit/issues/1635')
    def test_resource_iter_can_walk_non_utf8_path_from_unicode_path_with_dirs(self):
        test_dir = self.extract_test_tar_raw('fileutils/walk_non_utf8/non_unicode.tgz')
        test_dir = join(test_dir, 'non_unicode')

        result = list(fileutils.resource_iter(test_dir, with_dirs=True))
        assert len(result) == 18

    @skipIf(on_macos_14_or_higher, 'Cannot handle yet byte paths on macOS 10.14+. See https://github.com/nexB/scancode-toolkit/issues/1635')
    def test_resource_iter_can_walk_non_utf8_path_from_unicode_path(self):
        test_dir = self.extract_test_tar_raw('fileutils/walk_non_utf8/non_unicode.tgz')
        test_dir = join(test_dir, 'non_unicode')

        result = list(fileutils.resource_iter(test_dir, with_dirs=False))
        assert len(result) == 18

    @skipIf(on_windows, 'Symlinks do not work well on Windows')
    def test_resource_iter_follow_symlinks(self):
        test_dir = self.get_test_loc('symlink/walk', copy=True)
        temp_dir = fileutils.get_temp_dir()
        test_link = join(temp_dir, 'test-dir-link')
        os.symlink(test_dir, test_link)
        result = [os.path.basename(f) for f in fileutils.resource_iter(test_dir, follow_symlinks=True)]
        expected = [
            'dir',
            'a',
            'b'
        ]
        assert sorted(result) == sorted(expected)


class TestBaseName(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_file_base_name_on_path_and_location_1(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/.a/file'
        expected_name = 'file'
        result = fileutils.file_base_name(test_file)
        assert result == expected_name
        result = fileutils.file_base_name(join(test_dir, test_file))
        assert result == expected_name

    def test_file_base_name_on_file_path_for_dot_file  (self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/.a/'
        expected_name = '.a'
        result = fileutils.file_base_name(test_file)
        assert result == expected_name
        result = fileutils.file_base_name(join(test_dir, test_file))
        assert result == expected_name

    def test_file_base_name_on_file_path_for_dot_file_with_extension(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/b/.a.b'
        expected_name = '.a'
        result = fileutils.file_base_name(test_file)
        assert result == expected_name
        result = fileutils.file_base_name(join(test_dir, test_file))
        assert result == expected_name

    def test_file_base_name_on_file_path_for_file_with_unknown_composed_extension(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/b/a.tag.gz'
        expected_name = 'a.tag'
        result = fileutils.file_base_name(test_file)
        assert result == expected_name
        result = fileutils.file_base_name(join(test_dir, test_file))
        assert result == expected_name

    def test_file_base_name_on_file_path_for_file_with_known_composed_extension(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/b/a.tar.gz'
        expected_name = 'a'
        result = fileutils.file_base_name(test_file)
        assert result == expected_name
        result = fileutils.file_base_name(join(test_dir, test_file))
        assert result == expected_name

    def test_file_base_name_on_dir_path(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/b/'
        expected_name = 'b'
        result = fileutils.file_base_name(test_file)
        assert result == expected_name
        result = fileutils.file_base_name(join(test_dir, test_file))
        assert result == expected_name

    def test_file_base_name_on_plain_file(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/f.a'
        expected_name = 'f'
        result = fileutils.file_base_name(test_file)
        assert result == expected_name
        result = fileutils.file_base_name(join(test_dir, test_file))
        assert result == expected_name

    def test_file_base_name_on_plain_file_with_parent_dir_extension(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'f.a/a.c'
        expected_name = 'a'
        result = fileutils.file_base_name(test_file)
        assert result == expected_name
        result = fileutils.file_base_name(join(test_dir, test_file))
        assert result == expected_name

    def test_file_base_name_on_path_for_plain_dir(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/'
        expected_name = 'a'
        result = fileutils.file_base_name(test_file)
        assert result == expected_name
        result = fileutils.file_base_name(join(test_dir, test_file))
        assert result == expected_name

    def test_file_base_name_on_path_for_plain_dir_with_extension(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'f.a/'
        expected_name = 'f.a'
        result = fileutils.file_base_name(test_file)
        assert result == expected_name
        result = fileutils.file_base_name(join(test_dir, test_file))
        assert result == expected_name

    def test_file_base_name_on_path_for_plain_file(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'tst'
        expected_name = 'tst'
        result = fileutils.file_base_name(test_file)
        assert result == expected_name
        result = fileutils.file_base_name(join(test_dir, test_file))
        assert result == expected_name


class TestFileName(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_file_name_on_path_and_location_1(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/.a/file'
        expected_name = 'file'
        result = fileutils.file_name(test_file)
        assert result == expected_name
        result = fileutils.file_name((os.path.join(test_dir, test_file)))
        assert result == expected_name

    def test_file_name_on_path_and_location_2(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/.a/'
        expected_name = '.a'
        result = fileutils.file_name(test_file)
        assert result == expected_name
        result = fileutils.file_name((os.path.join(test_dir, test_file)))
        assert result == expected_name

    def test_file_name_on_path_and_location_3(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/b/.a.b'
        expected_name = '.a.b'
        result = fileutils.file_name(test_file)
        assert result == expected_name
        result = fileutils.file_name((os.path.join(test_dir, test_file)))
        assert result == expected_name

    def test_file_name_on_path_and_location_4(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/b/a.tag.gz'
        expected_name = 'a.tag.gz'
        result = fileutils.file_name(test_file)
        assert result == expected_name
        result = fileutils.file_name((os.path.join(test_dir, test_file)))
        assert result == expected_name

    def test_file_name_on_path_and_location_5(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/b/'
        expected_name = 'b'
        result = fileutils.file_name(test_file)
        assert result == expected_name
        result = fileutils.file_name((os.path.join(test_dir, test_file)))
        assert result == expected_name

    def test_file_name_on_path_and_location_6(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/f.a'
        expected_name = 'f.a'
        result = fileutils.file_name(test_file)
        assert result == expected_name
        result = fileutils.file_name((os.path.join(test_dir, test_file)))
        assert result == expected_name

    def test_file_name_on_path_and_location_7(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/'
        expected_name = 'a'
        result = fileutils.file_name(test_file)
        assert result == expected_name
        result = fileutils.file_name((os.path.join(test_dir, test_file)))
        assert result == expected_name

    def test_file_name_on_path_and_location_8(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'f.a/a.c'
        expected_name = 'a.c'
        result = fileutils.file_name(test_file)
        assert result == expected_name
        result = fileutils.file_name((os.path.join(test_dir, test_file)))
        assert result == expected_name

    def test_file_name_on_path_and_location_9(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'f.a/'
        expected_name = 'f.a'
        result = fileutils.file_name(test_file)
        assert result == expected_name
        result = fileutils.file_name((os.path.join(test_dir, test_file)))
        assert result == expected_name

    def test_file_name_on_path_and_location_10(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'tst'
        expected_name = 'tst'
        result = fileutils.file_name(test_file)
        assert result == expected_name
        result = fileutils.file_name((os.path.join(test_dir, test_file)))
        assert result == expected_name


class TestFileExtension(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_file_extension_on_path_and_location_1(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/.a/file'
        expected_name = ''
        result = fileutils.file_extension(test_file)
        assert result == expected_name
        result = fileutils.file_extension((os.path.join(test_dir, test_file)))
        assert result == expected_name

    def test_file_extension_on_path_and_location_2(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/.a/'
        expected_name = ''
        result = fileutils.file_extension(test_file)
        assert result == expected_name
        result = fileutils.file_extension((os.path.join(test_dir, test_file)))
        assert result == expected_name

    def test_file_extension_on_path_and_location_3(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/b/.a.b'
        expected_name = '.b'
        result = fileutils.file_extension(test_file)
        assert result == expected_name
        result = fileutils.file_extension((os.path.join(test_dir, test_file)))
        assert result == expected_name

    def test_file_extension_on_path_and_location_4(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/b/a.tag.gz'
        expected_name = '.gz'
        result = fileutils.file_extension(test_file)
        assert result == expected_name
        result = fileutils.file_extension((os.path.join(test_dir, test_file)))
        assert result == expected_name

    def test_file_extension_on_path_and_location_5(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/b/'
        expected_name = ''
        result = fileutils.file_extension(test_file)
        assert result == expected_name
        result = fileutils.file_extension((os.path.join(test_dir, test_file)))
        assert result == expected_name

    def test_file_extension_on_path_and_location_6(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/f.a'
        expected_name = '.a'
        result = fileutils.file_extension(test_file)
        assert result == expected_name
        result = fileutils.file_extension((os.path.join(test_dir, test_file)))
        assert result == expected_name

    def test_file_extension_on_path_and_location_7(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/'
        expected_name = ''
        result = fileutils.file_extension(test_file)
        assert result == expected_name
        result = fileutils.file_extension((os.path.join(test_dir, test_file)))
        assert result == expected_name

    def test_file_extension_on_path_and_location_8(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'f.a/a.c'
        expected_name = '.c'
        result = fileutils.file_extension(test_file)
        assert result == expected_name
        result = fileutils.file_extension((os.path.join(test_dir, test_file)))
        assert result == expected_name

    def test_file_extension_on_path_and_location_9(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'f.a/'
        expected_name = ''
        result = fileutils.file_extension(test_file)
        assert result == expected_name
        result = fileutils.file_extension((os.path.join(test_dir, test_file)))
        assert result == expected_name

    def test_file_extension_on_path_and_location_10(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'tst'
        expected_name = ''
        result = fileutils.file_extension(test_file)
        assert result == expected_name
        result = fileutils.file_extension((os.path.join(test_dir, test_file)))
        assert result == expected_name

    def test_splitext_base(self):
        expected = 'path', '.ext'
        assert fileutils.splitext('C:\\dir\\path.ext') == expected

    def test_splitext_directories_even_with_dotted_names_have_no_extension(self):
        import ntpath
        expected = 'path.ext', ''
        assert fileutils.splitext('C:\\dir\\path.ext' + ntpath.sep) == expected

        expected = 'path.ext', ''
        assert fileutils.splitext('/dir/path.ext/') == expected

        expected = 'file', '.txt'
        assert fileutils.splitext('/some/file.txt') == expected

    def test_splitext_composite_extensions_for_tarballs_are_properly_handled(self):
        expected = 'archive', '.tar.gz'
        assert fileutils.splitext('archive.tar.gz') == expected

    def test_splitext_name_base(self):
        expected = 'path', '.ext'
        assert fileutils.splitext_name('path.ext') == expected

    def test_splitext_name_directories_have_no_extension(self):
        expected = 'path.ext', ''
        assert fileutils.splitext_name('path.ext', is_file=False) == expected

        expected = 'file', '.txt'
        assert fileutils.splitext_name('file.txt') == expected

    def test_splitext_name_composite_extensions_for_tarballs_are_properly_handled(self):
        expected = 'archive', '.tar.gz'
        assert fileutils.splitext_name('archive.tar.gz') == expected

    def test_splitext_name_dotfile_are_properly_handled(self):
        expected = '.dotfile', ''
        assert fileutils.splitext_name('.dotfile') == expected
        expected = '.dotfile', '.this'
        assert fileutils.splitext_name('.dotfile.this') == expected


class TestParentDir(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parent_directory_on_path_and_location_1(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/.a/file'
        expected_name = 'a/.a/'
        result = fileutils.parent_directory(test_file)
        result = fileutils.as_posixpath(result)
        assert result == expected_name

        result = fileutils.parent_directory((os.path.join(test_dir, test_file)))
        result = fileutils.as_posixpath(result)
        assert result.endswith(expected_name)

    def test_parent_directory_on_path_and_location_2(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/.a/'
        expected_name = 'a/'
        result = fileutils.parent_directory(test_file)
        result = fileutils.as_posixpath(result)
        assert result == expected_name

        result = fileutils.parent_directory((os.path.join(test_dir, test_file)))
        result = fileutils.as_posixpath(result)
        assert result.endswith(expected_name)

    def test_parent_directory_on_path_and_location_3(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/b/.a.b'
        expected_name = 'a/b/'
        result = fileutils.parent_directory(test_file)
        result = fileutils.as_posixpath(result)
        assert result == expected_name

        result = fileutils.parent_directory((os.path.join(test_dir, test_file)))
        result = fileutils.as_posixpath(result)
        assert result.endswith(expected_name)

    def test_parent_directory_on_path_and_location_4(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/b/a.tag.gz'
        expected_name = 'a/b/'
        result = fileutils.parent_directory(test_file)
        result = fileutils.as_posixpath(result)
        assert result == expected_name

        result = fileutils.parent_directory((os.path.join(test_dir, test_file)))
        result = fileutils.as_posixpath(result)
        assert result.endswith(expected_name)

    def test_parent_directory_on_path_and_location_5(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/b/'
        expected_name = 'a/'
        result = fileutils.parent_directory(test_file)
        result = fileutils.as_posixpath(result)
        assert result == expected_name

        result = fileutils.parent_directory((os.path.join(test_dir, test_file)))
        result = fileutils.as_posixpath(result)
        assert result.endswith(expected_name)

    def test_parent_directory_on_path_and_location_6(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/f.a'
        expected_name = 'a/'
        result = fileutils.parent_directory(test_file)
        result = fileutils.as_posixpath(result)
        assert result == expected_name

        result = fileutils.parent_directory((os.path.join(test_dir, test_file)))
        result = fileutils.as_posixpath(result)
        assert result.endswith(expected_name)

    def test_parent_directory_on_path_and_location_7(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'a/'
        expected_name = '/'
        result = fileutils.parent_directory(test_file)
        result = fileutils.as_posixpath(result)
        assert result == expected_name

        result = fileutils.parent_directory((os.path.join(test_dir, test_file)))
        result = fileutils.as_posixpath(result)
        assert result.endswith(expected_name)

    def test_parent_directory_on_path_and_location_8(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'f.a/a.c'
        expected_name = 'f.a/'
        result = fileutils.parent_directory(test_file)
        result = fileutils.as_posixpath(result)
        assert result == expected_name

        result = fileutils.parent_directory((os.path.join(test_dir, test_file)))
        result = fileutils.as_posixpath(result)
        assert result.endswith(expected_name)

    def test_parent_directory_on_path_and_location_9(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'f.a/'
        expected_name = '/'
        result = fileutils.parent_directory(test_file)
        result = fileutils.as_posixpath(result)
        assert result == expected_name

        result = fileutils.parent_directory((os.path.join(test_dir, test_file)))
        result = fileutils.as_posixpath(result)
        assert result.endswith(expected_name)

    def test_parent_directory_on_path_and_location_10(self):
        test_dir = self.get_test_loc('fileutils/basename')
        test_file = 'tst'
        expected_name = '/'
        result = fileutils.parent_directory(test_file)
        result = fileutils.as_posixpath(result)
        assert result == expected_name

        result = fileutils.parent_directory((os.path.join(test_dir, test_file)))
        result = fileutils.as_posixpath(result)
        assert result.endswith(expected_name)
