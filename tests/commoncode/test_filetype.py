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

import os

import commoncode.testcase
from commoncode.testcase import make_non_readable
from commoncode.testcase import make_non_writable

from commoncode import filetype
from commoncode.system import on_posix
from commoncode import fileutils
from commoncode.testcase import FileBasedTesting
from os.path import join
from os.path import exists


class TypeTest(commoncode.testcase.FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_get_size_on_file(self):
        test_file = self.get_test_loc('filetype/size/Image1.eps')
        assert 12388 == filetype.get_size(test_file)

    def test_get_size_on_directory(self):
        test_dir = self.get_test_loc('filetype/size', copy=True)
        assert 12400 == filetype.get_size(test_dir)

    def test_get_type(self):
        test_dir = self.extract_test_tar('filetype/types.tar', verbatim=True)
        results = []
        for root, dirs, files in os.walk(test_dir):
            for d in dirs:
                results.append((d, filetype.get_type(os.path.join(root, d))))
            for f in files:
                results.append((f, filetype.get_type(os.path.join(root, f))))

        expected = [
            ('5-DIRTYPE', 'd'),
            ('0-REGTYPE', 'f'),
            ('0-REGTYPE-TEXT', 'f'),
            ('0-REGTYPE-VEEEERY_LONG_NAME___________________________________'
             '______________________________________________________________'
             '____________________155', 'f'),
            ('1-LNKTYPE', 'f'),
            ('S-SPARSE', 'f'),
            ('S-SPARSE-WITH-NULLS', 'f')
        ]

        # symlinks and special files are not supported on win
        if on_posix:
            expected += [ ('2-SYMTYPE', 'l'), ('6-FIFOTYPE', 's'), ]

        assert sorted(expected) == sorted(results)

    def test_is_rwx_with_none(self):
        assert not filetype.is_writable(None)
        assert not filetype.is_readable(None)
        assert not filetype.is_executable(None)

    def test_is_readable_is_writeable_file(self):
        base_dir = self.get_test_loc('filetype/readwrite', copy=True)
        test_file = os.path.join(os.path.join(base_dir, 'sub'), 'file')

        try:
            assert filetype.is_readable(test_file)
            assert filetype.is_writable(test_file)

            make_non_readable(test_file)
            if on_posix:
                assert not filetype.is_readable(test_file)

            make_non_writable(test_file)
            assert not filetype.is_writable(test_file)
        finally:
            fileutils.chmod(base_dir, fileutils.RW, recurse=True)

    def test_is_readable_is_writeable_dir(self):
        base_dir = self.get_test_loc('filetype/readwrite', copy=True)
        test_dir = os.path.join(base_dir, 'sub')

        try:
            assert filetype.is_readable(test_dir)
            assert filetype.is_writable(test_dir)

            make_non_readable(test_dir)
            if on_posix:
                assert not filetype.is_readable(test_dir)
            else:
                # dirs are always RW on windows
                assert filetype.is_readable(test_dir)
            make_non_writable(test_dir)
            if on_posix:
                assert not filetype.is_writable(test_dir)
            else:
                # dirs are always RW on windows
                assert filetype.is_writable(test_dir)
            # finally
        finally:
            fileutils.chmod(base_dir, fileutils.RW, recurse=True)


class CountTest(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def get_test_count_dir(self):
        test_dir = self.get_test_loc('count/filecount', copy=True)
        sub3 = join(test_dir, 'dir', 'sub3')
        if not exists(sub3):
            os.makedirs(sub3)
        return test_dir

    def test_get_file_count_with_empty_dir(self):
        test_dir = self.get_temp_dir()
        assert 0 == filetype.get_file_count(test_dir)

    def test_get_file_count_with_single_file(self):
        test_file = self.get_temp_file()
        with open(test_file, 'wb') as f:
            f.write('')
        assert filetype.is_file(test_file)
        assert 1 == filetype.get_file_count(test_file)

    def test_get_file_count_with_empty_folders(self):
        test_dir = self.get_test_count_dir()
        result = filetype.get_file_count(test_dir)
        assert 9 == result

    def test_get_file_size_and_count(self):
        test_dir = self.get_test_count_dir()
        result = filetype.get_size(test_dir)
        assert 18 == result

    def test_get_file_size(self):
        test_dir = self.get_test_count_dir()
        tests = (
            ('dir/a.txt', 2),
            ('dir/b.txt', 2),
            ('dir/c.txt', 2),
            ('dir/sub1/a.txt', 2),
            ('dir/sub1/b.txt', 2),
            ('dir/sub1/c.txt', 2),
            ('dir/sub1/subsub/a.txt', 2),
            ('dir/sub1/subsub/b.txt', 2),
            ('dir/sub1/subsub', 4),
            ('dir/sub1', 10),
            ('dir/sub2/a.txt', 2),
            ('dir/sub2', 2),
            ('dir/sub3', 0),
            ('dir/', 18),
            ('', 18),
        )
        for test_file, size in tests:
            result = filetype.get_size(os.path.join(test_dir, test_file))
            assert size == result

    def test_get_file_count(self):
        test_dir = self.get_test_count_dir()
        tests = (
            ('dir/a.txt', 1),
            ('dir/b.txt', 1),
            ('dir/c.txt', 1),
            ('dir/sub1/a.txt', 1),
            ('dir/sub1/b.txt', 1),
            ('dir/sub1/c.txt', 1),
            ('dir/sub1/subsub/a.txt', 1),
            ('dir/sub1/subsub/b.txt', 1),
            ('dir/sub1/subsub', 2),
            ('dir/sub1', 5),
            ('dir/sub2/a.txt', 1),
            ('dir/sub2', 1),
            ('dir/sub3', 0),
            ('dir/', 9),
            ('', 9),
        )
        for test_file, count in tests:
            result = filetype.get_file_count(os.path.join(test_dir, test_file))
            assert count == result
