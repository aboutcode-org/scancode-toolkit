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

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
from unittest.case import skipIf

import commoncode
from extractcode_assert_utils import check_files
from extractcode import tar

from test_archive import BaseArchiveTestCase


class TestTarGzip(BaseArchiveTestCase):

    def test_extract_targz_basic(self):
        test_file = self.get_test_loc('archive/tgz/tarred_gzipped.tar.gz')
        test_dir = self.get_temp_dir()
        tar.extract(test_file, test_dir)
        result = os.path.join(test_dir, 'e/a/b.txt')
        assert os.path.exists(result)

    def test_extract_targz_with_trailing_data(self):
        test_file = self.get_test_loc('archive/tgz/trailing.tar.gz')
        test_dir = self.get_temp_dir()
        tar.extract(test_file, test_dir)
        result = os.path.join(test_dir, 'a.txt')
        assert os.path.exists(result)

    def test_extract_targz_broken(self):
        test_file = self.get_test_loc('archive/tgz/broken.tar.gz')
        test_dir = self.get_temp_dir()
        expected = Exception('Error -3 while decompressing: invalid distance too far back')
        self.assertRaisesInstance(expected, tar.extract, test_file, test_dir)

    def test_extract_targz_with_absolute_path(self):
        non_result = '/tmp/subdir'
        assert not os.path.exists(non_result)

        test_dir = self.get_temp_dir()
        test_file = self.get_test_loc('archive/tgz/absolute_path.tar.gz')
        tar.extract(test_file, test_dir)
        assert not os.path.exists(non_result)
        result = os.path.join(test_dir, 'tmp/subdir/a.txt')
        assert os.path.exists(result)

    def test_extract_targz_with_relative_path(self):
        test_file = self.get_test_loc('archive/tgz/relative.tar.gz')
        """
        This test file was created with:
            import tarfile
            tar = tarfile.open("TarTest.tar.gz", "w:gz")
            tar.add('a.txt', '../a_parent_folder.txt')
            tar.add('b.txt', '../../another_folder/b_two_root.txt')
            tar.add('b.txt', '../folder/subfolder/b_subfolder.txt')
            tar.close()
        """
        test_dir = self.get_temp_dir()
        tar.extract(test_file, test_dir)

        non_result = os.path.join(test_dir, '../a_parent_folder.txt')
        assert not os.path.exists(non_result)

        expected = [
            'dotdot/dotdot/another_folder/b_two_root.txt',
            'dotdot/a_parent_folder.txt',
            'dotdot/folder/subfolder/b_subfolder.txt'
        ]
        check_files(test_dir, expected)

    def test_extract_targz_with_trailing_data2(self):
        test_dir1 = self.get_temp_dir()
        test_file = self.get_test_loc('archive/tgz/trailing2.tar.gz')
        tar.extract(test_file, test_dir1)

        test_dir2 = self.get_temp_dir()
        test_file2 = self.get_test_loc('archive/tgz/no_trailing.tar.gz')
        tar.extract(test_file2, test_dir2)
        assert commoncode.testcase.is_same(test_dir1, test_dir2)

    def test_extract_targz_with_mixed_case_and_symlink(self):
        test_file = self.get_test_loc('archive/tgz/mixed_case_and_symlink.tgz')
        test_dir = self.get_temp_dir()
        expected = [
            'skinenigmang/hqlogos/arte.xpm: Skipping duplicate file name.',
            'skinenigmang/hqlogos/MTV Hits.xpm: Skipping duplicate file name.',
            'skinenigmang/hqlogos/Disney Channel.xpm: Skipping duplicate file name.',
            'skinenigmang/hqlogos/EuroNews.xpm: Skipping duplicate file name.',
            'skinenigmang/hqlogos/Jetix.xpm: Skipping duplicate file name.',
            "skinenigmang/hqlogos/MTV France.xpm: Skipping link to special file: skinenigmang/hqlogos/MTV F.xpm"
        ]
        result = tar.extract(test_file, test_dir)
        result = [m.replace(test_dir, '').strip('\\/') for m in result]
        assert expected == result
#         expected_files = []
#         check_files(test_dir, expected_files)

    def test_extract_targz_symlinks(self):
        test_file = self.get_test_loc('archive/tgz/symlink.tar.gz')
        test_dir = self.get_temp_dir()
        tar.extract(test_file, test_dir)
        expected = [
            'z/x/a',
            'z/y/a'
        ]
        check_files(test_dir, expected)

    def test_extract_targz_from_apache_should_not_return_errors(self):
        # from http://archive.apache.org/dist/commons/logging/source/commons-logging-1.1.2-src.tar.gz
        # failed with ReadError('not a bzip2 file',)
        test_file = self.get_test_loc('archive/tgz/commons-logging-1.1.2-src.tar.gz')
        test_dir = self.get_temp_dir()
        result = tar.extract(test_file, test_dir)
        assert [] == result
        assert os.listdir(test_dir)


class TestTarBz2(BaseArchiveTestCase):

    def test_extract_tar_bz2_basic(self):
        test_file = self.get_test_loc('archive/tbz/tarred_bzipped.tar.bz2')
        test_dir = self.get_temp_dir()
        tar.extract(test_file, test_dir)
        result = os.path.join(test_dir, 'e/a/b.txt')
        assert os.path.exists(result)

    def test_extract_tar_bz2_basic_bz(self):
        test_file = self.get_test_loc('archive/tbz/tarred_bzipped.bz')
        test_dir = self.get_temp_dir()
        tar.extract(test_file, test_dir)
        result = os.path.join(test_dir, 'e/a/b.txt')
        assert os.path.exists(result)

    def test_extract_tar_bz2_with_trailing_data__and_wrong_extension(self):
        test_file = self.get_test_loc('archive/tbz/single_file_trailing_data.tar.gz')
        test_dir = self.get_temp_dir()
        tar.extract(test_file, test_dir)
        result = os.path.join(test_dir, 'a.txt')
        assert os.path.exists(result)

    def test_extract_tar_bz2_broken(self):
        test_file = self.get_test_loc('archive/tbz/tarred_bzipped_broken.tar.bz2')
        test_dir = self.get_temp_dir()
        expected = Exception('file could not be opened successfully')
        self.assertRaisesInstance(expected, tar.extract,
                                  test_file, test_dir)

    def test_extract_tar_bz2_absolute_path(self):
        assert not os.path.exists('/tmp/subdir')
        test_dir = self.get_temp_dir()
        test_file = self.get_test_loc('archive/tbz/absolute_path.tar.bz2')
        tar.extract(test_file, test_dir)
        assert not os.path.exists('/tmp/subdir')
        result = os.path.join(test_dir, 'tmp/subdir/a.txt')
        assert os.path.exists(result)

    def test_extract_tar_bz2_relative_path(self):
        test_file = self.get_test_loc('archive/tbz/bz2withtar_relative.tar.bz2')
        """
        This test file was created with:
            import tarfile
            tar = tarfile.open("TarTest.tar.gz", "w:bz")
            tar.add('a.txt', '../a_parent_folder.txt')
            tar.add('b.txt', '../../another_folder/b_two_root.txt')
            tar.add('b.txt', '../folder/subfolder/b_subfolder.txt')
            tar.close()
        """
        test_dir = self.get_temp_dir()
        tar.extract(test_file, test_dir)

        non_result = os.path.join(test_dir, '../a_parent_folder.txt')
        assert not os.path.exists(non_result)

        result = os.path.join(test_dir, 'dotdot/folder/subfolder/b_subfolder.txt')
        assert os.path.exists(result)
        result = os.path.join(test_dir, 'dotdot', 'a_parent_folder.txt')
        assert os.path.exists(result)

    def test_extract_tar_bz2_iproute(self):
        test_file = self.get_test_loc('archive/tbz/iproute2.tar.bz2')
        test_dir = self.get_temp_dir()
        tar.extract(test_file, test_dir)
        result = os.path.join(test_dir, 'iproute2/README')
        assert os.path.exists(result)

    def test_extract_tar_bz2_multistream(self):
        test_file = self.get_test_loc('archive/tbz/bzip2_multistream/example-file.csv.tar.bz2')
        test_dir = self.get_temp_dir()
        tar.extract(test_file, test_dir)
        expected = self.get_test_loc('archive/tbz/bzip2_multistream/example-file.csv')
        result = os.path.join(test_dir, 'example-file.csv')
        assert open(expected, 'rb').read() == open(result, 'rb').read()


class TestTar(BaseArchiveTestCase):

    def test_extract_tar_basic(self):
        test_file = self.get_test_loc('archive/tar/tarred.tar')
        test_dir = self.get_temp_dir()
        tar.extract(test_file, test_dir)
        result = os.path.join(test_dir, 'e/a/b.txt')
        assert os.path.exists(result)

    def test_extract_tar_broken(self):
        test_file = self.get_test_loc('archive/tar/tarred_broken.tar')
        test_dir = self.get_temp_dir()
        expected = Exception('file could not be opened successfully')
        self.assertRaisesInstance(expected, tar.extract,
                                  test_file, test_dir)

    def test_extract_tar_absolute_path(self):
        non_result = '/home/li/Desktop/absolute_folder'
        assert not os.path.exists(non_result)

        test_dir = self.get_temp_dir()
        test_file = self.get_test_loc('archive/tar/tar_absolute.tar')
        tar.extract(test_file, test_dir)

        assert not os.path.exists(non_result)
        result = os.path.join(test_dir, 'home/li/Desktop/absolute_folder/absolute_file')
        assert os.path.exists(result)

    def test_extract_tar_with_absolute_path2(self):
        assert not os.path.exists('/tmp/subdir')

        test_file = self.get_test_loc('archive/tar/absolute_path.tar')
        test_dir = self.get_temp_dir()
        tar.extract(test_file, test_dir)

        assert not os.path.exists('/tmp/subdir')
        result = os.path.join(test_dir, 'tmp/subdir/a.txt')
        assert os.path.exists(result)

    def test_extract_tar_with_relative_path(self):
        test_file = self.get_test_loc('archive/tar/tar_relative.tar')
        """
        This test file was created with:
            import tarfile
            tar = tarfile.open("TarTest.tar.gz", "w")
            tar.add('a.txt', '../a_parent_folder.txt')
            tar.add('b.txt', '../../another_folder/b_two_root.txt')
            tar.add('b.txt', '../folder/subfolder/b_subfolder.txt')
            tar.close()
        """
        test_dir = self.get_temp_dir()
        tar.extract(test_file, test_dir)
        non_result = os.path.abspath(test_file + '/../a_parent_folder.txt')
        assert not os.path.exists(non_result)
        extracted = self.collect_extracted_path(test_dir)
        expected = [
            '/dotdot/',
            '/dotdot/dotdot/',
            '/dotdot/a_parent_folder.txt',
            '/dotdot/dotdot/another_folder/',
            '/dotdot/dotdot/another_folder/b_two_root.txt',
            '/dotdot/folder/',
            '/dotdot/folder/subfolder/',
            '/dotdot/folder/subfolder/b_subfolder.txt'
        ]
        assert sorted(expected) == sorted(extracted)

    def test_extract_tar_archive_with_special_files(self):
        test_file = self.get_test_loc('archive/tar/special.tar')
        test_dir = self.get_temp_dir()
        result = tar.extract(test_file, test_dir)
        expected = [
            '0-REGTYPE',
            '0-REGTYPE-TEXT',
            '0-REGTYPE-VEEEERY_LONG_NAME_____________________________________________________________________________________________________________________155',
            '1-LNKTYPE',
            'S-SPARSE',
            'S-SPARSE-WITH-NULLS',
        ]
        check_files(test_dir, expected)

        expected_warnings = [
            "2-SYMTYPE: Skipping broken link to: testtar/0-REGTYPE",
            '3-CHRTYPE: Skipping special file.',
            '6-FIFOTYPE: Skipping special file.'
        ]
        assert sorted(expected_warnings) == sorted(result)

    @skipIf(True, 'Unicode tar paths are not handled well yet: we use libarchive instead')
    def test_tar_extract_python_testtar_tar_archive_with_special_files(self):
        test_file = self.get_test_loc('archive/tar/testtar.tar')
        # this is from:
        # https://hg.python.org/cpython/raw-file/bff88c866886/Lib/test/testtar.tar
        test_dir = self.get_temp_dir()
        result = tar.extract(test_file, test_dir)
        expected_warnings = []
#             "Skipping broken link to: testtar/0-REGTYPE",
#             'Skipping special file.',
#             'Skipping special file.'
#         ]
        assert sorted(expected_warnings) == sorted(result)
        expected = [
        ]
        check_files(test_dir, expected)

