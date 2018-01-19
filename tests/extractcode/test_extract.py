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
from unittest.case import expectedFailure

from commoncode.testcase import FileBasedTesting
from commoncode import fileutils
from commoncode.fileutils import as_posixpath

import extractcode
from extractcode_assert_utils import check_files
from extractcode_assert_utils import check_no_error
from extractcode import extract


class TestExtract(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_extract_file_function(self):
        test_file = self.get_test_loc('extract/basic_non_nested.tar.gz', copy=True)
        base = fileutils.parent_directory(test_file)
        expected = ['a/b/a.txt', 'a/b/b.txt', 'a/c/c.txt']
        cleaned_test_file = test_file.replace(base, '')
        expected_event = [
            extract.ExtractEvent(
                source=cleaned_test_file,
                target=extractcode.get_extraction_path(cleaned_test_file),
                done=False, warnings=[], errors=[]
            ),
            extract.ExtractEvent(
                source=cleaned_test_file,
                target=extractcode.get_extraction_path(cleaned_test_file),
                done=True, warnings=[], errors=[]
            )
        ]

        target = extractcode.get_extraction_path(test_file)
        result = list(extract.extract_file(test_file, target))
        result = [r._replace(
                    source=cleaned_test_file,
                    target=extractcode.get_extraction_path(cleaned_test_file))
                  for r in result]
        assert expected_event == result
        check_files(target, expected)

    def test_extract_archive_non_nested(self):
        test_dir = self.get_test_loc('extract/basic_non_nested.tar.gz', copy=True)
        expected = (
            'a/b/a.txt',
            'a/b/b.txt',
            'a/c/c.txt',
        )
        result = extract.extract(test_dir, recurse=False)
        check_no_error(result)
        check_files(extractcode.get_extraction_path(test_dir), expected)

        result = extract.extract(test_dir, recurse=True)
        check_no_error(result)
        check_files(extractcode.get_extraction_path(test_dir), expected)

    def test_extract_archive_shallow_with_readonly_inside(self):
        test_file = self.get_test_loc('extract/readonly/read_only.tar.gz', copy=True)
        """
        This test file was created with:
            import tarfile, time, datetime, StringIO, os
            TEXT = 'something\n'
            tar = tarfile.open('read_only.tar.gz', 'w:gz')
            for i in range(0, 2):
                tarinfo = tarfile.TarInfo()
                tarinfo.name = 'somefilename-%i.txt' % i
                tarinfo.uid = 123
                tarinfo.gid = 456
                tarinfo.uname = 'johndoe'
                tarinfo.gname = 'fake'
                tarinfo.type = tarfile.REGTYPE
                tarinfo.mode = 0 # this is the readonly part
                tarinfo.mtime = time.mktime(datetime.datetime.now().timetuple())
                file = StringIO.StringIO()
                file.write(TEXT)
                file.seek(0)
                tarinfo.size = len(TEXT)
                tar.addfile(tarinfo, file)
            tar.close()
        """
        result = list(extract.extract(test_file, recurse=False))
        check_no_error(result)

        expected = (
            'somefilename-0.txt',
            'somefilename-1.txt',
        )
        test_dir = extractcode.get_extraction_path(test_file)
        check_files(test_dir, expected)

    def test_extract_dir_shallow_with_readonly_inside(self):
        test_dir = self.get_test_loc('extract/readonly', copy=True)
        result = list(extract.extract(test_dir, recurse=False))
        check_no_error(result)
        expected = [
            'read_only.tar.gz',
            'read_only.tar.gz-extract/somefilename-0.txt',
            'read_only.tar.gz-extract/somefilename-1.txt',
        ]
        check_files(test_dir, expected)

    def test_extract_tree_shallow_only(self):
        expected = (
            'a/a.tar.gz',
            'a/a.txt',
            'a/a.tar.gz-extract/a/b/a.txt',
            'a/a.tar.gz-extract/a/b/b.txt',
            'a/a.tar.gz-extract/a/c/c.txt',

            'b/a.txt',
            'b/b.tar.gz',
            'b/b.tar.gz-extract/b/.svn/all-wcprops',
            'b/b.tar.gz-extract/b/.svn/entries',
            'b/b.tar.gz-extract/b/.svn/format',
            'b/b.tar.gz-extract/b/a/a.tar.gz',

            'b/b.tar.gz-extract/b/a/a.txt',
            'b/b.tar.gz-extract/b/a/.svn/all-wcprops',
            'b/b.tar.gz-extract/b/a/.svn/entries',
            'b/b.tar.gz-extract/b/a/.svn/format',
            'b/b.tar.gz-extract/b/a/.svn/prop-base/a.tar.gz.svn-base',
            'b/b.tar.gz-extract/b/a/.svn/text-base/a.tar.gz.svn-base',
            'b/b.tar.gz-extract/b/a/.svn/text-base/a.txt.svn-base',
            'b/b.tar.gz-extract/b/b/a.txt',
            'b/b.tar.gz-extract/b/b/.svn/all-wcprops',
            'b/b.tar.gz-extract/b/b/.svn/entries',
            'b/b.tar.gz-extract/b/b/.svn/format',
            'b/b.tar.gz-extract/b/b/.svn/text-base/a.txt.svn-base',
            'b/b.tar.gz-extract/b/c/a.tar.gz',
            'b/b.tar.gz-extract/b/c/a.txt',
            'b/b.tar.gz-extract/b/c/.svn/all-wcprops',
            'b/b.tar.gz-extract/b/c/.svn/entries',
            'b/b.tar.gz-extract/b/c/.svn/format',
            'b/b.tar.gz-extract/b/c/.svn/prop-base/a.tar.gz.svn-base',
            'b/b.tar.gz-extract/b/c/.svn/text-base/a.tar.gz.svn-base',
            'b/b.tar.gz-extract/b/c/.svn/text-base/a.txt.svn-base',

            'c/a.tar.gz',
            'c/a.txt',
            'c/a.tar.gz-extract/a/b/a.txt',
            'c/a.tar.gz-extract/a/b/b.txt',
            'c/a.tar.gz-extract/a/c/c.txt',
        )
        test_dir = self.get_test_loc('extract/tree', copy=True)
        result = list(extract.extract(test_dir, recurse=False))
        check_no_error(result)
        check_files(test_dir, expected)
        # extract again
        result = list(extract.extract(test_dir, recurse=False))
        check_no_error(result)
        check_files(test_dir, expected)

    def test_extract_tree_recursive(self):
        expected = (
            'a/a.tar.gz',
            'a/a.txt',
            'a/a.tar.gz-extract/a/b/a.txt',
            'a/a.tar.gz-extract/a/b/b.txt',
            'a/a.tar.gz-extract/a/c/c.txt',
            'b/a.txt',
            'b/b.tar.gz',
            'b/b.tar.gz-extract/b/.svn/all-wcprops',
            'b/b.tar.gz-extract/b/.svn/entries',
            'b/b.tar.gz-extract/b/.svn/format',
            'b/b.tar.gz-extract/b/a/a.tar.gz',
            'b/b.tar.gz-extract/b/a/a.txt',
            'b/b.tar.gz-extract/b/a/.svn/all-wcprops',
            'b/b.tar.gz-extract/b/a/.svn/entries',
            'b/b.tar.gz-extract/b/a/.svn/format',
            'b/b.tar.gz-extract/b/a/.svn/prop-base/a.tar.gz.svn-base',
            'b/b.tar.gz-extract/b/a/.svn/text-base/a.tar.gz.svn-base',
            'b/b.tar.gz-extract/b/a/.svn/text-base/a.txt.svn-base',
            'b/b.tar.gz-extract/b/a/a.tar.gz-extract/a/b/a.txt',
            'b/b.tar.gz-extract/b/a/a.tar.gz-extract/a/b/b.txt',
            'b/b.tar.gz-extract/b/a/a.tar.gz-extract/a/c/c.txt',
            'b/b.tar.gz-extract/b/b/a.txt',
            'b/b.tar.gz-extract/b/b/.svn/all-wcprops',
            'b/b.tar.gz-extract/b/b/.svn/entries',
            'b/b.tar.gz-extract/b/b/.svn/format',
            'b/b.tar.gz-extract/b/b/.svn/text-base/a.txt.svn-base',
            'b/b.tar.gz-extract/b/c/a.tar.gz',
            'b/b.tar.gz-extract/b/c/a.txt',
            'b/b.tar.gz-extract/b/c/.svn/all-wcprops',
            'b/b.tar.gz-extract/b/c/.svn/entries',
            'b/b.tar.gz-extract/b/c/.svn/format',
            'b/b.tar.gz-extract/b/c/.svn/prop-base/a.tar.gz.svn-base',
            'b/b.tar.gz-extract/b/c/.svn/text-base/a.tar.gz.svn-base',
            'b/b.tar.gz-extract/b/c/.svn/text-base/a.txt.svn-base',
            'b/b.tar.gz-extract/b/c/a.tar.gz-extract/a/b/a.txt',
            'b/b.tar.gz-extract/b/c/a.tar.gz-extract/a/b/b.txt',
            'b/b.tar.gz-extract/b/c/a.tar.gz-extract/a/c/c.txt',
            'c/a.tar.gz',
            'c/a.txt',
            'c/a.tar.gz-extract/a/b/a.txt',
            'c/a.tar.gz-extract/a/b/b.txt',
            'c/a.tar.gz-extract/a/c/c.txt',
        )
        test_dir = self.get_test_loc('extract/tree', copy=True)
        result = list(extract.extract(test_dir, recurse=True))
        check_no_error(result)
        check_files(test_dir, expected)
        # again
        result = list(extract.extract(test_dir, recurse=True))
        check_no_error(result)
        check_files(test_dir, expected)

    def test_extract_tree_shallow_then_recursive(self):
        shallow = (
            'a/a.tar.gz',
            'a/a.txt',
            'a/a.tar.gz-extract/a/b/a.txt',
            'a/a.tar.gz-extract/a/b/b.txt',
            'a/a.tar.gz-extract/a/c/c.txt',

            'b/a.txt',
            'b/b.tar.gz',
            'b/b.tar.gz-extract/b/.svn/all-wcprops',
            'b/b.tar.gz-extract/b/.svn/entries',
            'b/b.tar.gz-extract/b/.svn/format',
            'b/b.tar.gz-extract/b/a/a.tar.gz',
            'b/b.tar.gz-extract/b/a/a.txt',
            'b/b.tar.gz-extract/b/a/.svn/all-wcprops',
            'b/b.tar.gz-extract/b/a/.svn/entries',
            'b/b.tar.gz-extract/b/a/.svn/format',
            'b/b.tar.gz-extract/b/a/.svn/prop-base/a.tar.gz.svn-base',
            'b/b.tar.gz-extract/b/a/.svn/text-base/a.tar.gz.svn-base',
            'b/b.tar.gz-extract/b/a/.svn/text-base/a.txt.svn-base',
            'b/b.tar.gz-extract/b/b/a.txt',
            'b/b.tar.gz-extract/b/b/.svn/all-wcprops',
            'b/b.tar.gz-extract/b/b/.svn/entries',
            'b/b.tar.gz-extract/b/b/.svn/format',
            'b/b.tar.gz-extract/b/b/.svn/text-base/a.txt.svn-base',
            'b/b.tar.gz-extract/b/c/a.tar.gz',
            'b/b.tar.gz-extract/b/c/a.txt',
            'b/b.tar.gz-extract/b/c/.svn/all-wcprops',
            'b/b.tar.gz-extract/b/c/.svn/entries',
            'b/b.tar.gz-extract/b/c/.svn/format',
            'b/b.tar.gz-extract/b/c/.svn/prop-base/a.tar.gz.svn-base',
            'b/b.tar.gz-extract/b/c/.svn/text-base/a.tar.gz.svn-base',
            'b/b.tar.gz-extract/b/c/.svn/text-base/a.txt.svn-base',

            'c/a.tar.gz',
            'c/a.txt',
            'c/a.tar.gz-extract/a/b/a.txt',
            'c/a.tar.gz-extract/a/b/b.txt',
            'c/a.tar.gz-extract/a/c/c.txt',
        )
        recursed = (
            'a/a.tar.gz',
            'a/a.txt',
            'a/a.tar.gz-extract/a/b/a.txt',
            'a/a.tar.gz-extract/a/b/b.txt',
            'a/a.tar.gz-extract/a/c/c.txt',
            'b/a.txt',
            'b/b.tar.gz',
            'b/b.tar.gz-extract/b/.svn/all-wcprops',
            'b/b.tar.gz-extract/b/.svn/entries',
            'b/b.tar.gz-extract/b/.svn/format',
            'b/b.tar.gz-extract/b/a/a.tar.gz',
            'b/b.tar.gz-extract/b/a/a.txt',
            'b/b.tar.gz-extract/b/a/.svn/all-wcprops',
            'b/b.tar.gz-extract/b/a/.svn/entries',
            'b/b.tar.gz-extract/b/a/.svn/format',
            'b/b.tar.gz-extract/b/a/.svn/prop-base/a.tar.gz.svn-base',
            'b/b.tar.gz-extract/b/a/.svn/text-base/a.tar.gz.svn-base',
            'b/b.tar.gz-extract/b/a/.svn/text-base/a.txt.svn-base',
            'b/b.tar.gz-extract/b/a/a.tar.gz-extract/a/b/a.txt',
            'b/b.tar.gz-extract/b/a/a.tar.gz-extract/a/b/b.txt',
            'b/b.tar.gz-extract/b/a/a.tar.gz-extract/a/c/c.txt',
            'b/b.tar.gz-extract/b/b/a.txt',
            'b/b.tar.gz-extract/b/b/.svn/all-wcprops',
            'b/b.tar.gz-extract/b/b/.svn/entries',
            'b/b.tar.gz-extract/b/b/.svn/format',
            'b/b.tar.gz-extract/b/b/.svn/text-base/a.txt.svn-base',
            'b/b.tar.gz-extract/b/c/a.tar.gz',
            'b/b.tar.gz-extract/b/c/a.txt',
            'b/b.tar.gz-extract/b/c/.svn/all-wcprops',
            'b/b.tar.gz-extract/b/c/.svn/entries',
            'b/b.tar.gz-extract/b/c/.svn/format',
            'b/b.tar.gz-extract/b/c/.svn/prop-base/a.tar.gz.svn-base',
            'b/b.tar.gz-extract/b/c/.svn/text-base/a.tar.gz.svn-base',
            'b/b.tar.gz-extract/b/c/.svn/text-base/a.txt.svn-base',
            'b/b.tar.gz-extract/b/c/a.tar.gz-extract/a/b/a.txt',
            'b/b.tar.gz-extract/b/c/a.tar.gz-extract/a/b/b.txt',
            'b/b.tar.gz-extract/b/c/a.tar.gz-extract/a/c/c.txt',
            'c/a.tar.gz',
            'c/a.txt',
            'c/a.tar.gz-extract/a/b/a.txt',
            'c/a.tar.gz-extract/a/b/b.txt',
            'c/a.tar.gz-extract/a/c/c.txt',
        )

        test_dir = self.get_test_loc('extract/tree', copy=True)
        result = list(extract.extract(test_dir, recurse=False))
        check_no_error(result)
        check_files(test_dir, shallow)

        result = list(extract.extract(test_dir, recurse=True))
        check_no_error(result)
        check_files(test_dir, recursed)

    def test_extract_tree_with_corrupted_archives(self):
        expected = (
            'a.tar.gz',
        )
        test_dir = self.get_test_loc('extract/corrupted', copy=True)
        result = list(extract.extract(test_dir, recurse=False))
        check_files(test_dir, expected)
        assert len(result) == 2
        result = result[1]
        errs = ['gzip decompression failed']
        assert errs == result.errors
        assert not result.warnings

    def test_extract_with_empty_dir_and_small_files_ignores_empty_dirs(self):
        expected = (
            'empty_small.zip',
            'empty_small.zip-extract/empty_dirs_and_small_files/small_files/small_file.txt',)
        test_dir = self.get_test_loc('extract/small', copy=True)
        result = list(extract.extract(test_dir, recurse=True))
        check_no_error(result)
        check_files(test_dir, expected)

    def test_extract_tar_with_broken_links(self):
        test_dir = self.get_test_loc('extract/broken_link', copy=True)
        result = list(extract.extract(test_dir, recurse=True))
        expected = (
            'broken-link.tar.bz2',
            'broken-link.tar.bz2-extract/openssl/test/Makefile',
        )
        check_files(test_dir, expected)
        expected_warning = [[], []]
        warns = [r.warnings for r in result]
        assert expected_warning == warns

    def test_extract_nested_tar_file_recurse_only(self):
        test_file = self.get_test_loc('extract/nested/nested_tars.tar.gz', copy=True)
        expected = [
            'nested_tars.tar.gz',
            'nested_tars.tar.gz-extract/b/.svn/all-wcprops',
            'nested_tars.tar.gz-extract/b/.svn/entries',
            'nested_tars.tar.gz-extract/b/.svn/format',
            'nested_tars.tar.gz-extract/b/a/.svn/all-wcprops',
            'nested_tars.tar.gz-extract/b/a/.svn/entries',
            'nested_tars.tar.gz-extract/b/a/.svn/format',
            'nested_tars.tar.gz-extract/b/a/.svn/prop-base/a.tar.gz.svn-base',
            'nested_tars.tar.gz-extract/b/a/.svn/text-base/a.tar.gz.svn-base',
            'nested_tars.tar.gz-extract/b/a/.svn/text-base/a.txt.svn-base',
            'nested_tars.tar.gz-extract/b/a/a.tar.gz',
            'nested_tars.tar.gz-extract/b/a/a.tar.gz-extract/a/b/a.txt',
            'nested_tars.tar.gz-extract/b/a/a.tar.gz-extract/a/b/b.txt',
            'nested_tars.tar.gz-extract/b/a/a.tar.gz-extract/a/c/c.txt',
            'nested_tars.tar.gz-extract/b/a/a.txt',
            'nested_tars.tar.gz-extract/b/b/.svn/all-wcprops',
            'nested_tars.tar.gz-extract/b/b/.svn/entries',
            'nested_tars.tar.gz-extract/b/b/.svn/format',
            'nested_tars.tar.gz-extract/b/b/.svn/text-base/a.txt.svn-base',
            'nested_tars.tar.gz-extract/b/b/a.txt',
            'nested_tars.tar.gz-extract/b/c/.svn/all-wcprops',
            'nested_tars.tar.gz-extract/b/c/.svn/entries',
            'nested_tars.tar.gz-extract/b/c/.svn/format',
            'nested_tars.tar.gz-extract/b/c/.svn/prop-base/a.tar.gz.svn-base',
            'nested_tars.tar.gz-extract/b/c/.svn/text-base/a.tar.gz.svn-base',
            'nested_tars.tar.gz-extract/b/c/.svn/text-base/a.txt.svn-base',
            'nested_tars.tar.gz-extract/b/c/a.tar.gz',
            'nested_tars.tar.gz-extract/b/c/a.tar.gz-extract/a/b/a.txt',
            'nested_tars.tar.gz-extract/b/c/a.tar.gz-extract/a/b/b.txt',
            'nested_tars.tar.gz-extract/b/c/a.tar.gz-extract/a/c/c.txt',
            'nested_tars.tar.gz-extract/b/c/a.txt'
        ]
        result = list(extract.extract(test_file, recurse=True))
        check_no_error(result)
        check_files(test_file, expected)

    def test_extract_nested_tar_file_shallow_only(self):
        test_dir = self.get_test_loc('extract/nested/nested_tars.tar.gz', copy=True)
        expected = [
            'nested_tars.tar.gz',
            'nested_tars.tar.gz-extract/b/.svn/all-wcprops',
            'nested_tars.tar.gz-extract/b/.svn/entries',
            'nested_tars.tar.gz-extract/b/.svn/format',
            'nested_tars.tar.gz-extract/b/a/.svn/all-wcprops',
            'nested_tars.tar.gz-extract/b/a/.svn/entries',
            'nested_tars.tar.gz-extract/b/a/.svn/format',
            'nested_tars.tar.gz-extract/b/a/.svn/prop-base/a.tar.gz.svn-base',
            'nested_tars.tar.gz-extract/b/a/.svn/text-base/a.tar.gz.svn-base',
            'nested_tars.tar.gz-extract/b/a/.svn/text-base/a.txt.svn-base',
            'nested_tars.tar.gz-extract/b/a/a.tar.gz',
            'nested_tars.tar.gz-extract/b/a/a.txt',
            'nested_tars.tar.gz-extract/b/b/.svn/all-wcprops',
            'nested_tars.tar.gz-extract/b/b/.svn/entries',
            'nested_tars.tar.gz-extract/b/b/.svn/format',
            'nested_tars.tar.gz-extract/b/b/.svn/text-base/a.txt.svn-base',
            'nested_tars.tar.gz-extract/b/b/a.txt',
            'nested_tars.tar.gz-extract/b/c/.svn/all-wcprops',
            'nested_tars.tar.gz-extract/b/c/.svn/entries',
            'nested_tars.tar.gz-extract/b/c/.svn/format',
            'nested_tars.tar.gz-extract/b/c/.svn/prop-base/a.tar.gz.svn-base',
            'nested_tars.tar.gz-extract/b/c/.svn/text-base/a.tar.gz.svn-base',
            'nested_tars.tar.gz-extract/b/c/.svn/text-base/a.txt.svn-base',
            'nested_tars.tar.gz-extract/b/c/a.tar.gz',
            'nested_tars.tar.gz-extract/b/c/a.txt'
        ]
        result1 = list(extract.extract(test_dir, recurse=False))
        check_no_error(result1)
        check_files(test_dir, expected)

    def test_extract_nested_tar_file_shallow_then_recurse(self):
        test_file = self.get_test_loc('extract/nested/nested_tars.tar.gz', copy=True)
        expected = [
            'nested_tars.tar.gz',
            'nested_tars.tar.gz-extract/b/.svn/all-wcprops',
            'nested_tars.tar.gz-extract/b/.svn/entries',
            'nested_tars.tar.gz-extract/b/.svn/format',
            'nested_tars.tar.gz-extract/b/a/.svn/all-wcprops',
            'nested_tars.tar.gz-extract/b/a/.svn/entries',
            'nested_tars.tar.gz-extract/b/a/.svn/format',
            'nested_tars.tar.gz-extract/b/a/.svn/prop-base/a.tar.gz.svn-base',
            'nested_tars.tar.gz-extract/b/a/.svn/text-base/a.tar.gz.svn-base',
            'nested_tars.tar.gz-extract/b/a/.svn/text-base/a.txt.svn-base',
            'nested_tars.tar.gz-extract/b/a/a.tar.gz',
            'nested_tars.tar.gz-extract/b/a/a.tar.gz-extract/a/b/a.txt',
            'nested_tars.tar.gz-extract/b/a/a.tar.gz-extract/a/b/b.txt',
            'nested_tars.tar.gz-extract/b/a/a.tar.gz-extract/a/c/c.txt',
            'nested_tars.tar.gz-extract/b/a/a.txt',
            'nested_tars.tar.gz-extract/b/b/.svn/all-wcprops',
            'nested_tars.tar.gz-extract/b/b/.svn/entries',
            'nested_tars.tar.gz-extract/b/b/.svn/format',
            'nested_tars.tar.gz-extract/b/b/.svn/text-base/a.txt.svn-base',
            'nested_tars.tar.gz-extract/b/b/a.txt',
            'nested_tars.tar.gz-extract/b/c/.svn/all-wcprops',
            'nested_tars.tar.gz-extract/b/c/.svn/entries',
            'nested_tars.tar.gz-extract/b/c/.svn/format',
            'nested_tars.tar.gz-extract/b/c/.svn/prop-base/a.tar.gz.svn-base',
            'nested_tars.tar.gz-extract/b/c/.svn/text-base/a.tar.gz.svn-base',
            'nested_tars.tar.gz-extract/b/c/.svn/text-base/a.txt.svn-base',
            'nested_tars.tar.gz-extract/b/c/a.tar.gz',
            'nested_tars.tar.gz-extract/b/c/a.tar.gz-extract/a/b/a.txt',
            'nested_tars.tar.gz-extract/b/c/a.tar.gz-extract/a/b/b.txt',
            'nested_tars.tar.gz-extract/b/c/a.tar.gz-extract/a/c/c.txt',
            'nested_tars.tar.gz-extract/b/c/a.txt'
        ]
        result1 = list(extract.extract(test_file, recurse=False))
        result2 = list(extract.extract(test_file, recurse=True))
        check_no_error(result1)
        check_no_error(result2)
        check_files(test_file, expected)

    def test_extract_dir_with_nested_tar_file_shallow_then_recurse(self):
        test_dir = self.get_test_loc('extract/nested', copy=True)
        expected = [
            'nested_tars.tar.gz',
            'nested_tars.tar.gz-extract/b/.svn/all-wcprops',
            'nested_tars.tar.gz-extract/b/.svn/entries',
            'nested_tars.tar.gz-extract/b/.svn/format',
            'nested_tars.tar.gz-extract/b/a/.svn/all-wcprops',
            'nested_tars.tar.gz-extract/b/a/.svn/entries',
            'nested_tars.tar.gz-extract/b/a/.svn/format',
            'nested_tars.tar.gz-extract/b/a/.svn/prop-base/a.tar.gz.svn-base',
            'nested_tars.tar.gz-extract/b/a/.svn/text-base/a.tar.gz.svn-base',
            'nested_tars.tar.gz-extract/b/a/.svn/text-base/a.txt.svn-base',
            'nested_tars.tar.gz-extract/b/a/a.tar.gz',
            'nested_tars.tar.gz-extract/b/a/a.tar.gz-extract/a/b/a.txt',
            'nested_tars.tar.gz-extract/b/a/a.tar.gz-extract/a/b/b.txt',
            'nested_tars.tar.gz-extract/b/a/a.tar.gz-extract/a/c/c.txt',
            'nested_tars.tar.gz-extract/b/a/a.txt',
            'nested_tars.tar.gz-extract/b/b/.svn/all-wcprops',
            'nested_tars.tar.gz-extract/b/b/.svn/entries',
            'nested_tars.tar.gz-extract/b/b/.svn/format',
            'nested_tars.tar.gz-extract/b/b/.svn/text-base/a.txt.svn-base',
            'nested_tars.tar.gz-extract/b/b/a.txt',
            'nested_tars.tar.gz-extract/b/c/.svn/all-wcprops',
            'nested_tars.tar.gz-extract/b/c/.svn/entries',
            'nested_tars.tar.gz-extract/b/c/.svn/format',
            'nested_tars.tar.gz-extract/b/c/.svn/prop-base/a.tar.gz.svn-base',
            'nested_tars.tar.gz-extract/b/c/.svn/text-base/a.tar.gz.svn-base',
            'nested_tars.tar.gz-extract/b/c/.svn/text-base/a.txt.svn-base',
            'nested_tars.tar.gz-extract/b/c/a.tar.gz',
            'nested_tars.tar.gz-extract/b/c/a.tar.gz-extract/a/b/a.txt',
            'nested_tars.tar.gz-extract/b/c/a.tar.gz-extract/a/b/b.txt',
            'nested_tars.tar.gz-extract/b/c/a.tar.gz-extract/a/c/c.txt',
            'nested_tars.tar.gz-extract/b/c/a.txt'
        ]
        result1 = list(extract.extract(test_dir, recurse=False))
        result2 = list(extract.extract(test_dir, recurse=True))
        check_no_error(result1)
        check_no_error(result2)
        check_files(test_dir, expected)

    def test_extract_zip_with_spaces_in_name(self):
        test_dir = self.get_test_loc('extract/space-zip', copy=True)
        expected = (
            'with spaces in name.zip',
            'with spaces in name.zip-extract/empty_dirs_and_small_files/small_files/small_file.txt'
        )
        result = list(extract.extract(test_dir, recurse=True))
        check_no_error(result)
        check_files(test_dir, expected)

    def test_extract_tar_gz_with_spaces_in_name(self):
        test_dir = self.get_test_loc('extract/space-tgz', copy=True)
        expected = (
            'with spaces in name.tar.gz',
            'with spaces in name.tar.gz-extract/a/b/a.txt',
            'with spaces in name.tar.gz-extract/a/b/b.txt',
            'with spaces in name.tar.gz-extract/a/c/c.txt',
        )
        result = list(extract.extract(test_dir, recurse=True))
        check_no_error(result)
        check_files(test_dir, expected)

    def test_extract_tar_with_special_files(self):
        test_dir = self.get_test_loc('extract/special', copy=True)
        expected = [
            't.tgz',
            't.tgz-extract/0-REGTYPE',
            't.tgz-extract/0-REGTYPE-TEXT',
            't.tgz-extract/0-REGTYPE-VEEEERY_LONG_NAME_____________________________________________________________________________________________________________________155',
            't.tgz-extract/S-SPARSE',
            't.tgz-extract/S-SPARSE-WITH-NULLS',
        ]
        result = list(extract.extract(test_dir, recurse=True))
        check_files(test_dir, expected)

        errs = [r.errors for r in result if r.errors]
        assert [] == errs

        warns = [r.warnings for r in result if r.warnings]
        assert [] == warns

    # FIXME: create test
    @expectedFailure
    def test_extract_with_kinds(self):
        assert False

    @expectedFailure
    def test_extract_directory_of_windows_ar_archives(self):
        # this does not pass yet with libarchive and fails too with 7z
        test_dir = self.get_test_loc('extract/ar_tree/winlib', copy=True)
        result = list(extract.extract(test_dir, recurse=True))
        expected = [
            'freetype.lib',
            'freetype.lib-extract/1.txt',
            'freetype.lib-extract/2.txt',
            'freetype.lib-extract/objs/debug_mt/autofit.obj',
            'freetype.lib-extract/objs/debug_mt/bdf.obj',
            'freetype.lib-extract/objs/debug_mt/cff.obj',
            'freetype.lib-extract/objs/debug_mt/ftbase.obj',
            'freetype.lib-extract/objs/debug_mt/ftbbox.obj',
            'freetype.lib-extract/objs/debug_mt/ftbitmap.obj',
            'freetype.lib-extract/objs/debug_mt/ftcache.obj',
            'freetype.lib-extract/objs/debug_mt/ftdebug.obj',
            'freetype.lib-extract/objs/debug_mt/ftgasp.obj',
            'freetype.lib-extract/objs/debug_mt/ftglyph.obj',
            'freetype.lib-extract/objs/debug_mt/ftgzip.obj',
            'freetype.lib-extract/objs/debug_mt/ftinit.obj',
            'freetype.lib-extract/objs/debug_mt/ftlzw.obj',
            'freetype.lib-extract/objs/debug_mt/ftmm.obj',
            'freetype.lib-extract/objs/debug_mt/ftpfr.obj',
            'freetype.lib-extract/objs/debug_mt/ftstroke.obj',
            'freetype.lib-extract/objs/debug_mt/ftsynth.obj',
            'freetype.lib-extract/objs/debug_mt/ftsystem.obj',
            'freetype.lib-extract/objs/debug_mt/fttype1.obj',
            'freetype.lib-extract/objs/debug_mt/ftwinfnt.obj',
            'freetype.lib-extract/objs/debug_mt/pcf.obj',
            'freetype.lib-extract/objs/debug_mt/pfr.obj',
            'freetype.lib-extract/objs/debug_mt/psaux.obj',
            'freetype.lib-extract/objs/debug_mt/pshinter.obj',
            'freetype.lib-extract/objs/debug_mt/psmodule.obj',
            'freetype.lib-extract/objs/debug_mt/raster.obj',
            'freetype.lib-extract/objs/debug_mt/sfnt.obj',
            'freetype.lib-extract/objs/debug_mt/smooth.obj',
            'freetype.lib-extract/objs/debug_mt/truetype.obj',
            'freetype.lib-extract/objs/debug_mt/type1.obj',
            'freetype.lib-extract/objs/debug_mt/type1cid.obj',
            'freetype.lib-extract/objs/debug_mt/type42.obj',
            'freetype.lib-extract/objs/debug_mt/winfnt.obj',
            'gsdll32.lib',
            'gsdll32.lib-extract/1.GSDLL32.dll',
            'gsdll32.lib-extract/1.txt',
            'gsdll32.lib-extract/10.GSDLL32.dll',
            'gsdll32.lib-extract/11.GSDLL32.dll',
            'gsdll32.lib-extract/12.GSDLL32.dll',
            'gsdll32.lib-extract/13.GSDLL32.dll',
            'gsdll32.lib-extract/14.GSDLL32.dll',
            'gsdll32.lib-extract/15.GSDLL32.dll',
            'gsdll32.lib-extract/16.GSDLL32.dll',
            'gsdll32.lib-extract/17.GSDLL32.dll',
            'gsdll32.lib-extract/18.GSDLL32.dll',
            'gsdll32.lib-extract/19.GSDLL32.dll',
            'gsdll32.lib-extract/2.GSDLL32.dll',
            'gsdll32.lib-extract/2.txt',
            'gsdll32.lib-extract/20.GSDLL32.dll',
            'gsdll32.lib-extract/21.GSDLL32.dll',
            'gsdll32.lib-extract/22.GSDLL32.dll',
            'gsdll32.lib-extract/23.GSDLL32.dll',
            'gsdll32.lib-extract/24.GSDLL32.dll',
            'gsdll32.lib-extract/25.GSDLL32.dll',
            'gsdll32.lib-extract/26.GSDLL32.dll',
            'gsdll32.lib-extract/27.GSDLL32.dll',
            'gsdll32.lib-extract/28.GSDLL32.dll',
            'gsdll32.lib-extract/29.GSDLL32.dll',
            'gsdll32.lib-extract/3.GSDLL32.dll',
            'gsdll32.lib-extract/30.GSDLL32.dll',
            'gsdll32.lib-extract/31.GSDLL32.dll',
            'gsdll32.lib-extract/4.GSDLL32.dll',
            'gsdll32.lib-extract/5.GSDLL32.dll',
            'gsdll32.lib-extract/6.GSDLL32.dll',
            'gsdll32.lib-extract/7.GSDLL32.dll',
            'gsdll32.lib-extract/8.GSDLL32.dll',
            'gsdll32.lib-extract/9.GSDLL32.dll',
            'htmlhelp.lib',
            'htmlhelp.lib-extract/1.txt',
            'htmlhelp.lib-extract/2.txt',
            'htmlhelp.lib-extract/release/init.obj',
            'libmysql.lib',
            'libmysql.lib-extract/1.LIBMYSQL.dll',
            'libmysql.lib-extract/1.txt',
            'libmysql.lib-extract/10.LIBMYSQL.dll',
            'libmysql.lib-extract/100.LIBMYSQL.dll',
            'libmysql.lib-extract/101.LIBMYSQL.dll',
            'libmysql.lib-extract/102.LIBMYSQL.dll',
            'libmysql.lib-extract/103.LIBMYSQL.dll',
            'libmysql.lib-extract/104.LIBMYSQL.dll',
            'libmysql.lib-extract/105.LIBMYSQL.dll',
            'libmysql.lib-extract/106.LIBMYSQL.dll',
            'libmysql.lib-extract/107.LIBMYSQL.dll',
            'libmysql.lib-extract/108.LIBMYSQL.dll',
            'libmysql.lib-extract/109.LIBMYSQL.dll',
            'libmysql.lib-extract/11.LIBMYSQL.dll',
            'libmysql.lib-extract/110.LIBMYSQL.dll',
            'libmysql.lib-extract/111.LIBMYSQL.dll',
            'libmysql.lib-extract/112.LIBMYSQL.dll',
            'libmysql.lib-extract/113.LIBMYSQL.dll',
            'libmysql.lib-extract/114.LIBMYSQL.dll',
            'libmysql.lib-extract/115.LIBMYSQL.dll',
            'libmysql.lib-extract/116.LIBMYSQL.dll',
            'libmysql.lib-extract/117.LIBMYSQL.dll',
            'libmysql.lib-extract/118.LIBMYSQL.dll',
            'libmysql.lib-extract/119.LIBMYSQL.dll',
            'libmysql.lib-extract/12.LIBMYSQL.dll',
            'libmysql.lib-extract/120.LIBMYSQL.dll',
            'libmysql.lib-extract/121.LIBMYSQL.dll',
            'libmysql.lib-extract/122.LIBMYSQL.dll',
            'libmysql.lib-extract/123.LIBMYSQL.dll',
            'libmysql.lib-extract/124.LIBMYSQL.dll',
            'libmysql.lib-extract/125.LIBMYSQL.dll',
            'libmysql.lib-extract/126.LIBMYSQL.dll',
            'libmysql.lib-extract/127.LIBMYSQL.dll',
            'libmysql.lib-extract/128.LIBMYSQL.dll',
            'libmysql.lib-extract/129.LIBMYSQL.dll',
            'libmysql.lib-extract/13.LIBMYSQL.dll',
            'libmysql.lib-extract/130.LIBMYSQL.dll',
            'libmysql.lib-extract/131.LIBMYSQL.dll',
            'libmysql.lib-extract/132.LIBMYSQL.dll',
            'libmysql.lib-extract/133.LIBMYSQL.dll',
            'libmysql.lib-extract/134.LIBMYSQL.dll',
            'libmysql.lib-extract/135.LIBMYSQL.dll',
            'libmysql.lib-extract/136.LIBMYSQL.dll',
            'libmysql.lib-extract/137.LIBMYSQL.dll',
            'libmysql.lib-extract/138.LIBMYSQL.dll',
            'libmysql.lib-extract/139.LIBMYSQL.dll',
            'libmysql.lib-extract/14.LIBMYSQL.dll',
            'libmysql.lib-extract/140.LIBMYSQL.dll',
            'libmysql.lib-extract/141.LIBMYSQL.dll',
            'libmysql.lib-extract/142.LIBMYSQL.dll',
            'libmysql.lib-extract/143.LIBMYSQL.dll',
            'libmysql.lib-extract/144.LIBMYSQL.dll',
            'libmysql.lib-extract/145.LIBMYSQL.dll',
            'libmysql.lib-extract/146.LIBMYSQL.dll',
            'libmysql.lib-extract/147.LIBMYSQL.dll',
            'libmysql.lib-extract/148.LIBMYSQL.dll',
            'libmysql.lib-extract/149.LIBMYSQL.dll',
            'libmysql.lib-extract/15.LIBMYSQL.dll',
            'libmysql.lib-extract/150.LIBMYSQL.dll',
            'libmysql.lib-extract/151.LIBMYSQL.dll',
            'libmysql.lib-extract/152.LIBMYSQL.dll',
            'libmysql.lib-extract/153.LIBMYSQL.dll',
            'libmysql.lib-extract/16.LIBMYSQL.dll',
            'libmysql.lib-extract/17.LIBMYSQL.dll',
            'libmysql.lib-extract/18.LIBMYSQL.dll',
            'libmysql.lib-extract/19.LIBMYSQL.dll',
            'libmysql.lib-extract/2.LIBMYSQL.dll',
            'libmysql.lib-extract/2.txt',
            'libmysql.lib-extract/20.LIBMYSQL.dll',
            'libmysql.lib-extract/21.LIBMYSQL.dll',
            'libmysql.lib-extract/22.LIBMYSQL.dll',
            'libmysql.lib-extract/23.LIBMYSQL.dll',
            'libmysql.lib-extract/24.LIBMYSQL.dll',
            'libmysql.lib-extract/25.LIBMYSQL.dll',
            'libmysql.lib-extract/26.LIBMYSQL.dll',
            'libmysql.lib-extract/27.LIBMYSQL.dll',
            'libmysql.lib-extract/28.LIBMYSQL.dll',
            'libmysql.lib-extract/29.LIBMYSQL.dll',
            'libmysql.lib-extract/3.LIBMYSQL.dll',
            'libmysql.lib-extract/30.LIBMYSQL.dll',
            'libmysql.lib-extract/31.LIBMYSQL.dll',
            'libmysql.lib-extract/32.LIBMYSQL.dll',
            'libmysql.lib-extract/33.LIBMYSQL.dll',
            'libmysql.lib-extract/34.LIBMYSQL.dll',
            'libmysql.lib-extract/35.LIBMYSQL.dll',
            'libmysql.lib-extract/36.LIBMYSQL.dll',
            'libmysql.lib-extract/37.LIBMYSQL.dll',
            'libmysql.lib-extract/38.LIBMYSQL.dll',
            'libmysql.lib-extract/39.LIBMYSQL.dll',
            'libmysql.lib-extract/4.LIBMYSQL.dll',
            'libmysql.lib-extract/40.LIBMYSQL.dll',
            'libmysql.lib-extract/41.LIBMYSQL.dll',
            'libmysql.lib-extract/42.LIBMYSQL.dll',
            'libmysql.lib-extract/43.LIBMYSQL.dll',
            'libmysql.lib-extract/44.LIBMYSQL.dll',
            'libmysql.lib-extract/45.LIBMYSQL.dll',
            'libmysql.lib-extract/46.LIBMYSQL.dll',
            'libmysql.lib-extract/47.LIBMYSQL.dll',
            'libmysql.lib-extract/48.LIBMYSQL.dll',
            'libmysql.lib-extract/49.LIBMYSQL.dll',
            'libmysql.lib-extract/5.LIBMYSQL.dll',
            'libmysql.lib-extract/50.LIBMYSQL.dll',
            'libmysql.lib-extract/51.LIBMYSQL.dll',
            'libmysql.lib-extract/52.LIBMYSQL.dll',
            'libmysql.lib-extract/53.LIBMYSQL.dll',
            'libmysql.lib-extract/54.LIBMYSQL.dll',
            'libmysql.lib-extract/55.LIBMYSQL.dll',
            'libmysql.lib-extract/56.LIBMYSQL.dll',
            'libmysql.lib-extract/57.LIBMYSQL.dll',
            'libmysql.lib-extract/58.LIBMYSQL.dll',
            'libmysql.lib-extract/59.LIBMYSQL.dll',
            'libmysql.lib-extract/6.LIBMYSQL.dll',
            'libmysql.lib-extract/60.LIBMYSQL.dll',
            'libmysql.lib-extract/61.LIBMYSQL.dll',
            'libmysql.lib-extract/62.LIBMYSQL.dll',
            'libmysql.lib-extract/63.LIBMYSQL.dll',
            'libmysql.lib-extract/64.LIBMYSQL.dll',
            'libmysql.lib-extract/65.LIBMYSQL.dll',
            'libmysql.lib-extract/66.LIBMYSQL.dll',
            'libmysql.lib-extract/67.LIBMYSQL.dll',
            'libmysql.lib-extract/68.LIBMYSQL.dll',
            'libmysql.lib-extract/69.LIBMYSQL.dll',
            'libmysql.lib-extract/7.LIBMYSQL.dll',
            'libmysql.lib-extract/70.LIBMYSQL.dll',
            'libmysql.lib-extract/71.LIBMYSQL.dll',
            'libmysql.lib-extract/72.LIBMYSQL.dll',
            'libmysql.lib-extract/73.LIBMYSQL.dll',
            'libmysql.lib-extract/74.LIBMYSQL.dll',
            'libmysql.lib-extract/75.LIBMYSQL.dll',
            'libmysql.lib-extract/76.LIBMYSQL.dll',
            'libmysql.lib-extract/77.LIBMYSQL.dll',
            'libmysql.lib-extract/78.LIBMYSQL.dll',
            'libmysql.lib-extract/79.LIBMYSQL.dll',
            'libmysql.lib-extract/8.LIBMYSQL.dll',
            'libmysql.lib-extract/80.LIBMYSQL.dll',
            'libmysql.lib-extract/81.LIBMYSQL.dll',
            'libmysql.lib-extract/82.LIBMYSQL.dll',
            'libmysql.lib-extract/83.LIBMYSQL.dll',
            'libmysql.lib-extract/84.LIBMYSQL.dll',
            'libmysql.lib-extract/85.LIBMYSQL.dll',
            'libmysql.lib-extract/86.LIBMYSQL.dll',
            'libmysql.lib-extract/87.LIBMYSQL.dll',
            'libmysql.lib-extract/88.LIBMYSQL.dll',
            'libmysql.lib-extract/89.LIBMYSQL.dll',
            'libmysql.lib-extract/9.LIBMYSQL.dll',
            'libmysql.lib-extract/90.LIBMYSQL.dll',
            'libmysql.lib-extract/91.LIBMYSQL.dll',
            'libmysql.lib-extract/92.LIBMYSQL.dll',
            'libmysql.lib-extract/93.LIBMYSQL.dll',
            'libmysql.lib-extract/94.LIBMYSQL.dll',
            'libmysql.lib-extract/95.LIBMYSQL.dll',
            'libmysql.lib-extract/96.LIBMYSQL.dll',
            'libmysql.lib-extract/97.LIBMYSQL.dll',
            'libmysql.lib-extract/98.LIBMYSQL.dll',
            'libmysql.lib-extract/99.LIBMYSQL.dll',
            'php4embed.lib',
            'php4embed.lib-extract/1.txt',
            'php4embed.lib-extract/2.txt',
            'php4embed.lib-extract/Release_TS/php_embed.obj',
            'pyexpat.lib',
            'pyexpat.lib-extract/1.pyexpat.pyd',
            'pyexpat.lib-extract/1.txt',
            'pyexpat.lib-extract/2.pyexpat.pyd',
            'pyexpat.lib-extract/2.txt',
            'pyexpat.lib-extract/3.pyexpat.pyd',
            'pyexpat.lib-extract/4.pyexpat.pyd',
            'zlib.lib',
            'zlib.lib-extract/1.txt',
            'zlib.lib-extract/1.zlib.pyd',
            'zlib.lib-extract/2.txt',
            'zlib.lib-extract/2.zlib.pyd',
            'zlib.lib-extract/3.zlib.pyd',
            'zlib.lib-extract/4.zlib.pyd'
        ]
        check_files(test_dir, expected)
        check_no_error(result)

    def test_extract_nested_arch_with_corrupted_compressed_should_extract_inner_archives_only_once(self):
        test_file = self.get_test_loc('extract/nested_not_compressed/nested_with_not_compressed_gz_file.tgz', copy=True)
        expected = [
            'nested_with_not_compressed_gz_file.tgz',
            'nested_with_not_compressed_gz_file.tgz-extract/top/file',
            'nested_with_not_compressed_gz_file.tgz-extract/top/notcompressed.gz'
        ]
        result = list(extract.extract(test_file, recurse=True))
        check_no_error(result)
        check_files(test_file, expected)

    def touch(self, location):
        with open(location, 'wb') as f:
            f.write('\n')

    def fake_extract(self, location):
        extracted = os.path.join(location + 'extract')
        os.mkdir(extracted)
        self.touch(os.path.join(extracted, 'extracted_file'))
        return extracted

    def extract_walker(self, test_dir):
        for top, dirs, files in os.walk(test_dir, topdown=True):
            for f in files:
                if not f.endswith('-extract') and f.endswith('.gz'):
                    extracted = self.fake_extract(os.path.join(top, f))
                    for x in self.extract_walker(os.path.join(top, extracted)):
                        yield x
            yield top, dirs, files

    def test_walk_can_be_extended_while_walking(self):
        test_dir = self.get_temp_dir()
        self.touch(os.path.join(test_dir, 'file'))
        self.touch(os.path.join(test_dir, 'arch.gz'))
        os.mkdir(os.path.join(test_dir, 'dir'))
        self.touch(os.path.join(test_dir, 'dir', 'otherarch.gz'))
        allpaths = []
        for top, dirs, files in self.extract_walker(test_dir):
            allpaths.extend([as_posixpath(os.path.join(top, d).replace(test_dir, '')) for d in dirs + files])

        expected = [
            '/arch.gzextract/extracted_file',
            '/dir',
            '/arch.gz',
            '/file',
            '/dir/otherarch.gzextract/extracted_file',
            '/dir/otherarch.gz'
        ]

        assert sorted(expected) == sorted(allpaths)

    def test_extract_can_extract_to_relative_paths(self):
        # The setup is a tad complex because we want to have a relative dir
        # to the base dir where we run tests from, ie the scancode-toolkit/ dir
        # To use relative paths, we use our tmp dir at the root of the code tree
        from os.path import dirname, join, abspath
        scancode_root = dirname(dirname(dirname(__file__)))
        scancode_tmp = join(scancode_root, 'tmp')
        fileutils.create_dir(scancode_tmp)
        scancode_root_abs = abspath(scancode_root)
        import tempfile
        test_src_dir = tempfile.mkdtemp(dir=scancode_tmp).replace(scancode_root_abs, '').strip('\\/')
        test_file = self.get_test_loc('extract/relative_path/basic.zip')
        import shutil
        shutil.copy(test_file, test_src_dir)
        test_src_file = join(test_src_dir, 'basic.zip')
        test_tgt_dir = join(scancode_root, test_src_file) + extractcode.EXTRACT_SUFFIX
        result = list(extract.extract(test_src_file))
        expected = ['c/a/a.txt', 'c/b/a.txt', 'c/c/a.txt']
        check_files(test_tgt_dir, expected)
        for r in result:
            assert [] == r.warnings
            assert [] == r.errors
