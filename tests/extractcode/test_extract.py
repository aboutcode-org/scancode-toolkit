# -*- coding: utf-8 -*-
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

import io
import os
from types import GeneratorType

import pytest

from commoncode import fileutils
from commoncode.fileutils import as_posixpath
from commoncode.system import on_linux
from commoncode.system import on_windows
from commoncode.system import py3
from commoncode.testcase import FileBasedTesting

import extractcode
from extractcode import extract
from extractcode_assert_utils import check_files
from extractcode_assert_utils import check_no_error
from extractcode_assert_utils import BaseArchiveTestCase


class TestExtract(BaseArchiveTestCase):
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
            import tarfile, time, datetime, io, os
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
                file = io.StringIO()
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

    def test_extract_tree_recursive_replace_originals(self):
        expected = (
            'a/a.txt',
            'a/a.tar.gz/a/b/a.txt',
            'a/a.tar.gz/a/b/b.txt',
            'a/a.tar.gz/a/c/c.txt',
            'b/a.txt',
            'b/b.tar.gz/b/.svn/all-wcprops',
            'b/b.tar.gz/b/.svn/entries',
            'b/b.tar.gz/b/.svn/format',
            'b/b.tar.gz/b/a/a.txt',
            'b/b.tar.gz/b/a/.svn/all-wcprops',
            'b/b.tar.gz/b/a/.svn/entries',
            'b/b.tar.gz/b/a/.svn/format',
            'b/b.tar.gz/b/a/.svn/prop-base/a.tar.gz.svn-base',
            'b/b.tar.gz/b/a/.svn/text-base/a.tar.gz.svn-base',
            'b/b.tar.gz/b/a/.svn/text-base/a.txt.svn-base',
            'b/b.tar.gz/b/a/a.tar.gz/a/b/a.txt',
            'b/b.tar.gz/b/a/a.tar.gz/a/b/b.txt',
            'b/b.tar.gz/b/a/a.tar.gz/a/c/c.txt',
            'b/b.tar.gz/b/b/a.txt',
            'b/b.tar.gz/b/b/.svn/all-wcprops',
            'b/b.tar.gz/b/b/.svn/entries',
            'b/b.tar.gz/b/b/.svn/format',
            'b/b.tar.gz/b/b/.svn/text-base/a.txt.svn-base',
            'b/b.tar.gz/b/c/a.txt',
            'b/b.tar.gz/b/c/.svn/all-wcprops',
            'b/b.tar.gz/b/c/.svn/entries',
            'b/b.tar.gz/b/c/.svn/format',
            'b/b.tar.gz/b/c/.svn/prop-base/a.tar.gz.svn-base',
            'b/b.tar.gz/b/c/.svn/text-base/a.tar.gz.svn-base',
            'b/b.tar.gz/b/c/.svn/text-base/a.txt.svn-base',
            'b/b.tar.gz/b/c/a.tar.gz/a/b/a.txt',
            'b/b.tar.gz/b/c/a.tar.gz/a/b/b.txt',
            'b/b.tar.gz/b/c/a.tar.gz/a/c/c.txt',
            'c/a.txt',
            'c/a.tar.gz/a/b/a.txt',
            'c/a.tar.gz/a/b/b.txt',
            'c/a.tar.gz/a/c/c.txt',
        )
        test_dir = self.get_test_loc('extract/tree', copy=True)
        result = list(extract.extract(test_dir, recurse=True, replace_originals=True))
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

    def test_uncompress_corrupted_archive_with_zlib(self):
        from extractcode import archive
        import zlib
        test_file = self.get_test_loc('extract/corrupted/a.tar.gz', copy=True)
        test_dir = self.get_temp_dir()
        expected = Exception('Error -3 while decompressing')
        self.assertRaisesInstance(expected, archive.uncompress_gzip, test_file, test_dir)

    def test_uncompress_corrupted_archive_with_libarchive(self):
        from extractcode import libarchive2
        test_file = self.get_test_loc('extract/corrupted/a.tar.gz', copy=True)
        test_dir = self.get_temp_dir()
        expected = Exception('gzip decompression failed')
        self.assertRaisesInstance(expected, libarchive2.extract, test_file, test_dir)

    @pytest.mark.skipif(py3 and not on_linux, reason='Expectations are different on Windows and macOS')
    def test_extract_tree_with_corrupted_archives_linux(self):
        expected = (
            'a.tar.gz',
        )
        test_dir = self.get_test_loc('extract/corrupted', copy=True)
        result = list(extract.extract(test_dir, recurse=False))
        check_files(test_dir, expected)
        assert len(result) == 2
        result = result[1]
        assert len(result.errors) == 1
        assert result.errors[0].startswith('gzip decompression failed')
        assert not result.warnings

    @pytest.mark.skipif(py3 and on_linux, reason='Expectations are different on Windows and macOS')
    def test_extract_tree_with_corrupted_archives_mac_win(self):
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
            # we skip links but not hardlinks
            't.tgz-extract/1-LNKTYPE',
            't.tgz-extract/S-SPARSE',
            't.tgz-extract/S-SPARSE-WITH-NULLS',
        ]
        result = list(extract.extract(test_dir, recurse=True))
        check_files(test_dir, expected)

        errs = [r.errors for r in result if r.errors]
        assert [] == errs

        warns = [r.warnings for r in result if r.warnings]
        assert [] == warns

    def test_extract_directory_of_windows_ar_archives(self):
        test_dir = self.get_test_loc('extract/ar_tree/winlib', copy=True)
        result = list(extract.extract(test_dir, recurse=True))
        expected = self.get_test_loc('extract/ar_tree/winlib-expected.json')
        check_files(test_dir, expected, regen=False)
        check_no_error(result)

    def test_extract_nested_arch_with_corruption_should_extract_inner_archives_only_once(self):
        test_file = self.get_test_loc(
            'extract/nested_not_compressed/nested_with_not_compressed_gz_file.tgz', copy=True)
        expected = [
            'nested_with_not_compressed_gz_file.tgz',
            'nested_with_not_compressed_gz_file.tgz-extract/top/file',
            'nested_with_not_compressed_gz_file.tgz-extract/top/notcompressed.gz'
        ]
        result = list(extract.extract(test_file, recurse=True))
        check_no_error(result)
        check_files(test_file, expected)

    def test_extract_directory_with_office_docs(self):
        test_dir = self.get_test_loc('extract/office_docs', copy=True)
        result = list(extract.extract(test_dir, kinds=(extractcode.docs,), recurse=True))
        expected = [
            'abc.docx',
            'abc.docx-extract/[Content_Types].xml',
            'abc.docx-extract/docProps/app.xml',
            'abc.docx-extract/docProps/core.xml',
            'abc.docx-extract/_rels/.rels',
            'abc.docx-extract/word/fontTable.xml',
            'abc.docx-extract/word/document.xml',
            'abc.docx-extract/word/settings.xml',
            'abc.docx-extract/word/numbering.xml',
            'abc.docx-extract/word/activeX/activeX1.xml',
            'abc.docx-extract/word/activeX/activeX2.xml',
            'abc.docx-extract/word/activeX/activeX3.xml',
            'abc.docx-extract/word/activeX/_rels/activeX1.xml.rels',
            'abc.docx-extract/word/activeX/_rels/activeX2.xml.rels',
            'abc.docx-extract/word/activeX/_rels/activeX3.xml.rels',
            'abc.docx-extract/word/activeX/activeX1.bin',
            'abc.docx-extract/word/activeX/activeX3.bin',
            'abc.docx-extract/word/activeX/activeX2.bin',
            'abc.docx-extract/word/webSettings.xml',
            'abc.docx-extract/word/styles.xml',
            'abc.docx-extract/word/theme/theme1.xml',
            'abc.docx-extract/word/_rels/document.xml.rels',
            'abc.docx-extract/word/stylesWithEffects.xml',
            'abc.docx-extract/word/media/image1.gif',
            'abc.docx-extract/word/media/image4.wmf',
            'abc.docx-extract/word/media/image2.wmf',
            'abc.docx-extract/word/media/image3.wmf',

            'excel.xlsx',
            'excel.xlsx-extract/[Content_Types].xml',
            'excel.xlsx-extract/docProps/app.xml',
            'excel.xlsx-extract/docProps/core.xml',
            'excel.xlsx-extract/_rels/.rels',
            'excel.xlsx-extract/xl/workbook.xml',
            'excel.xlsx-extract/xl/worksheets/sheet2.xml',
            'excel.xlsx-extract/xl/worksheets/sheet3.xml',
            'excel.xlsx-extract/xl/worksheets/sheet1.xml',
            'excel.xlsx-extract/xl/styles.xml',
            'excel.xlsx-extract/xl/theme/theme1.xml',
            'excel.xlsx-extract/xl/_rels/workbook.xml.rels',
            'excel.xlsx-extract/xl/sharedStrings.xml',

            'ppt.pptx',
            'ppt.pptx-extract/[Content_Types].xml',
            'ppt.pptx-extract/docProps/app.xml',
            'ppt.pptx-extract/docProps/thumbnail.jpeg',
            'ppt.pptx-extract/docProps/core.xml',
            'ppt.pptx-extract/_rels/.rels',
            'ppt.pptx-extract/ppt/viewProps.xml',
            'ppt.pptx-extract/ppt/slideLayouts/slideLayout9.xml',
            'ppt.pptx-extract/ppt/slideLayouts/slideLayout8.xml',
            'ppt.pptx-extract/ppt/slideLayouts/_rels/slideLayout5.xml.rels',
            'ppt.pptx-extract/ppt/slideLayouts/_rels/slideLayout4.xml.rels',
            'ppt.pptx-extract/ppt/slideLayouts/_rels/slideLayout2.xml.rels',
            'ppt.pptx-extract/ppt/slideLayouts/_rels/slideLayout3.xml.rels',
            'ppt.pptx-extract/ppt/slideLayouts/_rels/slideLayout8.xml.rels',
            'ppt.pptx-extract/ppt/slideLayouts/_rels/slideLayout9.xml.rels',
            'ppt.pptx-extract/ppt/slideLayouts/_rels/slideLayout11.xml.rels',
            'ppt.pptx-extract/ppt/slideLayouts/_rels/slideLayout10.xml.rels',
            'ppt.pptx-extract/ppt/slideLayouts/_rels/slideLayout6.xml.rels',
            'ppt.pptx-extract/ppt/slideLayouts/_rels/slideLayout7.xml.rels',
            'ppt.pptx-extract/ppt/slideLayouts/_rels/slideLayout1.xml.rels',
            'ppt.pptx-extract/ppt/slideLayouts/slideLayout3.xml',
            'ppt.pptx-extract/ppt/slideLayouts/slideLayout2.xml',
            'ppt.pptx-extract/ppt/slideLayouts/slideLayout1.xml',
            'ppt.pptx-extract/ppt/slideLayouts/slideLayout5.xml',
            'ppt.pptx-extract/ppt/slideLayouts/slideLayout4.xml',
            'ppt.pptx-extract/ppt/slideLayouts/slideLayout6.xml',
            'ppt.pptx-extract/ppt/slideLayouts/slideLayout10.xml',
            'ppt.pptx-extract/ppt/slideLayouts/slideLayout11.xml',
            'ppt.pptx-extract/ppt/slideLayouts/slideLayout7.xml',
            'ppt.pptx-extract/ppt/presentation.xml',
            'ppt.pptx-extract/ppt/slideMasters/slideMaster1.xml',
            'ppt.pptx-extract/ppt/slideMasters/_rels/slideMaster1.xml.rels',
            'ppt.pptx-extract/ppt/slides/slide1.xml',
            'ppt.pptx-extract/ppt/slides/_rels/slide1.xml.rels',
            'ppt.pptx-extract/ppt/theme/theme1.xml',
            'ppt.pptx-extract/ppt/_rels/presentation.xml.rels',
            'ppt.pptx-extract/ppt/presProps.xml',
            'ppt.pptx-extract/ppt/tableStyles.xml',
            'ppt.pptx-extract/ppt/media/image1.png'
        ]
        check_files(test_dir, expected)
        check_no_error(result)

    def touch(self, location):
        with io.open(location, 'w') as f:
            f.write(u'\n')

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
        # to the base dir where we run tests from, i.e. the git checkout dir
        # To use relative paths, we use our tmp dir at the root of the code tree
        from os.path import dirname, join, abspath
        import shutil
        import tempfile

        project_root = dirname(dirname(dirname(__file__)))
        project_tmp = join(project_root, 'tmp')
        fileutils.create_dir(project_tmp)
        project_root_abs = abspath(project_root)
        test_src_dir = tempfile.mkdtemp(dir=project_tmp).replace(project_root_abs, '').strip('\\/')
        test_file = self.get_test_loc('extract/relative_path/basic.zip')
        shutil.copy(test_file, test_src_dir)
        test_src_file = join(test_src_dir, 'basic.zip')
        test_tgt_dir = join(project_root, test_src_file) + extractcode.EXTRACT_SUFFIX
        result = list(extract.extract(test_src_file))
        expected = ['c/a/a.txt', 'c/b/a.txt', 'c/c/a.txt']
        check_files(test_tgt_dir, expected)
        for r in result:
            assert [] == r.warnings
            assert [] == r.errors

    def test_recursive_import(self):
        from extractcode.extract import extract  # NOQA

    @pytest.mark.skipif(on_windows, reason='Windows behavior is slightly different with relative paths')
    def test_extract_zipslip_tar_posix(self):
        test_dir = self.get_test_loc('extract/zipslip', copy=True)
        expected = [
            'README.md',
            'zip-slip-win.tar',
            'zip-slip-win.tar-extract/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/Temp/evil.txt',
            'zip-slip-win.tar-extract/good.txt',
            'zip-slip-win.tar.ABOUT',
            'zip-slip-win.zip',
            'zip-slip-win.zip-extract/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/Temp/evil.txt',
            'zip-slip-win.zip-extract/good.txt',
            'zip-slip-win.zip.ABOUT',
            'zip-slip.tar',
            'zip-slip.tar-extract/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/tmp/evil.txt',
            'zip-slip.tar-extract/good.txt',
            'zip-slip.tar.ABOUT',
            'zip-slip.zip',
            'zip-slip.zip-extract/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/tmp/evil.txt',
            'zip-slip.zip-extract/good.txt',
            'zip-slip.zip.ABOUT',
        ]

        result = list(extract.extract(test_dir, recurse=True))
        check_files(test_dir, expected)

        errs = [r.errors for r in result if r.errors]
        assert [] == errs

        warns = [r.warnings for r in result if r.warnings]
        assert [] == warns

    def test_extract_always_returns_a_generator_and_not_a_list(self):
        # a test for #1996 to ensure that progress is displayed "progressively"
        test_dir = self.get_test_loc('extract/generator', copy=True)
        result = extract.extract(test_dir)
        assert isinstance(result, GeneratorType)
    
    def test_extract_ignore_file(self):
        test_dir = self.get_test_loc('extract/ignore', copy=True)
        expected = [
            'alpha.zip',
            'beta.tar',
            'beta.tar-extract/a.txt',
            'beta.tar-extract/b.txt',
            'beta.tar-extract/c.txt',
            'gamma/gamma.zip',
            'gamma/gamma.zip-extract/c.txt'
        ]
        from extractcode import default_kinds
        result = list(extract.extract(test_dir, recurse=True, ignore_pattern=('alpha.zip',)))
        check_no_error(result)
        check_files(test_dir, expected)

    def test_extract_ignore_directory(self):
        test_dir = self.get_test_loc('extract/ignore', copy=True)
        expected = [
            'alpha.zip',
            'alpha.zip-extract/a.txt',
            'alpha.zip-extract/beta.zip',
            'alpha.zip-extract/beta.zip-extract/b.txt',
            'alpha.zip-extract/gamma.tar',
            'alpha.zip-extract/gamma.tar-extract/c.txt',
            'beta.tar',
            'beta.tar-extract/a.txt',
            'beta.tar-extract/b.txt',
            'beta.tar-extract/c.txt',
            'gamma/gamma.zip',
        ]
        from extractcode import default_kinds
        result = list(extract.extract(test_dir, recurse=True, ignore_pattern=('gamma',)))
        check_no_error(result)
        check_files(test_dir, expected)

    def test_extract_ignore_pattern(self):
        test_dir = self.get_test_loc('extract/ignore', copy=True)
        expected = [
            'alpha.zip',
            'alpha.zip-extract/a.txt',
            'alpha.zip-extract/beta.zip',
            'alpha.zip-extract/gamma.tar',
            'alpha.zip-extract/gamma.tar-extract/c.txt',
            'beta.tar',
            'beta.tar-extract/a.txt',
            'beta.tar-extract/b.txt',
            'beta.tar-extract/c.txt',
            'gamma/gamma.zip',
            'gamma/gamma.zip-extract/c.txt'
        ]
        from extractcode import default_kinds
        result = list(extract.extract(test_dir, recurse=True, ignore_pattern=('b*.zip',)))
        check_no_error(result)
        check_files(test_dir, expected)