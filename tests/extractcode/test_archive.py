# -*- coding: utf-8 -*-
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

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import io
import os
from unittest.case import skipIf

import pytest

import commoncode.date
from commoncode import compat
from commoncode import fileutils
from commoncode.system import on_linux
from commoncode.system import on_mac
from commoncode.system import on_windows
from commoncode.system import py2
from commoncode.system import py3

from extractcode_assert_utils import BaseArchiveTestCase
from extractcode_assert_utils import check_files
from extractcode_assert_utils import check_size
from extractcode_assert_utils import to_posix

import extractcode
from extractcode import archive
from extractcode import ExtractErrorFailedToExtract
from extractcode import libarchive2
from extractcode import sevenzip
from extractcode.libarchive2 import ArchiveError

"""
For each archive type --when possible-- we are testing extraction of:
 - basic, plain archive, no tricks
 - with trailing data appended to archive
 - broken, either truncated or with extra junk inserted
 - with hardlinks and symlinks, either  valid or broken when supported
 - with hardlinks and symlinks loops (aka. tarbomb) when supported
 - with FIFO, character, sparse and other special files when supported
 - with relative paths pointing outside of the archive when supported
 - with absolute paths when supported
 - with invalid paths or mixed slash paths when supported
 - with unicode or binary path names
 - with duplicate names or paths when case is ignored
 - password-protected when supported
"""


class TestGetExtractorTest(BaseArchiveTestCase):

    def test_get_extractors_1(self):
        test_file = 'archive/zip/basic.zip'
        expected = [archive.extract_zip]
        self.check_get_extractors(test_file, expected)

    def test_get_extractors_2(self):
        test_file = 'archive/rar/basic.rar'
        expected = [archive.extract_rar]
        self.check_get_extractors(test_file, expected)

    def test_get_extractors_3(self):
        test_file = 'archive/deb/adduser_3.112ubuntu1_all.deb'
        expected = [archive.extract_deb]
        self.check_get_extractors(test_file, expected)

    def test_get_extractors_4(self):
        test_file = 'archive/cpio/elfinfo-1.0-1.fc9.src.cpio'
        expected = [archive.extract_cpio]
        self.check_get_extractors(test_file, expected)

    def test_get_extractors_5(self):
        test_file = 'archive/rpm/elfinfo-1.0-1.fc9.src.rpm'
        expected = [archive.extract_rpm, archive.extract_cpio]
        self.check_get_extractors(test_file, expected)

    def test_get_extractors_6(self):
        test_file = 'archive/gzip/file_4.26-1.diff.gz'
        expected = [archive.uncompress_gzip]
        self.check_get_extractors(test_file, expected)

    def test_get_extractors_7(self):
        test_file = 'archive/ar/liby.a'
        expected = [archive.extract_ar]
        self.check_get_extractors(test_file, expected)

    def test_get_extractors_8(self):
        test_file = 'archive/bz2/single_file_not_tarred.bz2'
        expected = [archive.uncompress_bzip2]
        self.check_get_extractors(test_file, expected)

    def test_get_extractors_9(self):
        test_file = 'archive/tar/tarred.tar'
        expected = [archive.extract_tar]
        self.check_get_extractors(test_file, expected)

    def test_get_extractors_10(self):
        test_file = 'archive/tbz/tarred_bzipped.bz'
        expected = [archive.uncompress_bzip2]
        self.check_get_extractors(test_file, expected)

    def test_get_extractors_11(self):
        test_file = 'archive/tbz/tarred_bzipped.tar.bz2'
        expected = [archive.extract_tar]
        self.check_get_extractors(test_file, expected)

    def test_get_extractors_12(self):
        test_file = 'archive/tbz/tarred_bzipped.tbz'
        expected = [archive.extract_tar]
        self.check_get_extractors(test_file, expected)

    def test_get_extractors_13(self):
        test_file = 'archive/tgz/tarred_gzipped.gz'
        expected = [archive.uncompress_gzip]
        self.check_get_extractors(test_file, expected)

    def test_get_extractors_14(self):
        test_file = 'archive/tgz/tarred_gzipped.tar.gz'
        expected = [archive.extract_tar]
        self.check_get_extractors(test_file, expected)

    def test_get_extractors_15(self):
        test_file = 'archive/tgz/tarred_gzipped.tgz'
        expected = [archive.extract_tar]
        self.check_get_extractors(test_file, expected)

    def test_get_extractors_16(self):
        test_file = 'archive/7z/z.7z'
        expected = [archive.extract_7z]
        self.check_get_extractors(test_file, expected)

    def test_get_extractors_17(self):
        test_file = 'archive/Z/tr2tex.Z'
        expected = [archive.extract_Z, ]
        self.check_get_extractors(test_file, expected)

    def test_get_extractors_18(self):
        test_file = 'archive/Z/tkWWW-0.11.tar.Z'
        expected = [archive.extract_Z, archive.extract_tar]
        self.check_get_extractors(test_file, expected)

    def test_get_extractors_19(self):
        test_file = 'archive/xar/xar-1.4.xar'
        expected = [archive.extract_xarpkg]
        self.check_get_extractors(test_file, expected)

    def test_get_extractor_with_kinds_deb(self):
        test_file = 'archive/deb/adduser_3.112ubuntu1_all.deb'
        expected = [archive.extract_deb]
        self.check_get_extractors(test_file, expected, (archive.package,))

    def test_get_extractor_with_kinds_rpm(self):
        test_file = 'archive/rpm/elfinfo-1.0-1.fc9.src.rpm'
        kinds = (archive.regular, archive.file_system, archive.docs)
        expected = []
        self.check_get_extractors(test_file, expected, kinds)

    def test_get_extractor_with_kinds_rpm_2(self):
        test_file = 'archive/rpm/elfinfo-1.0-1.fc9.src.rpm'
        kinds = (archive.regular, archive.file_system, archive.docs, archive.package)
        expected = [sevenzip.extract, libarchive2.extract]
        self.check_get_extractors(test_file, expected, kinds)

    def test_get_extractor_with_kinds_deb2(self):
        test_file = 'archive/deb/adduser_3.112ubuntu1_all.deb'
        expected = []
        self.check_get_extractors(test_file, expected, (archive.regular,))

    def test_get_extractor_with_kinds_ar(self):
        test_file = 'archive/ar/liby.a'
        kinds = (archive.regular, archive.file_system, archive.docs)
        expected = []
        self.check_get_extractors(test_file, expected, kinds)

    def test_get_extractor_with_kinds_bzip(self):
        test_file = 'archive/tbz/tarred_bzipped.tar.bz2'
        expected = []
        self.check_get_extractors(test_file, expected, (archive.package,))

    def test_get_extractor_with_kinds_plain_tar(self):
        test_file = 'archive/tar/tarred.tar'
        expected = []
        self.check_get_extractors(test_file, expected, (archive.package,))

        expected = [archive.extract_tar]
        self.check_get_extractors(test_file, expected, (archive.regular,))

    def test_get_extractor_for_graffle_docs(self):
        test_file = 'archive/graffle/example.graffle'

        expected = [archive.uncompress_gzip]
        self.check_get_extractors(test_file, expected, (archive.docs,))

        expected = []
        self.check_get_extractors(test_file, expected, kinds=extractcode.default_kinds)

    def test_get_extractor_for_compressed_svgz_docs(self):
        test_file = 'archive/svgz/insert-emptyframe.svgz'

        expected = [archive.uncompress_gzip]
        self.check_get_extractors(test_file, expected, (archive.docs,))

        expected = []
        self.check_get_extractors(test_file, expected, kinds=extractcode.default_kinds)

    def test_get_extractor_for_dia(self):
        test_file = self.get_test_loc('archive/dia/dia.dia', copy=True)

        expected = [archive.uncompress_gzip]
        self.check_get_extractors(test_file, expected, kinds=extractcode.all_kinds)

        expected = []
        self.check_get_extractors(test_file, expected, kinds=extractcode.default_kinds)

    def test_get_handlers(self):
        test_data = [
            ('archive/deb/adduser_3.112ubuntu1_all.deb', ['Tar', 'Debian package']),
            ('archive/rpm/elfinfo-1.0-1.fc9.src.rpm', ['RPM package']),
            ('archive/ar/liby.a', ['ar archive', 'Static Library']),
            ('archive/tar/tarred.tar', ['Tar']),
            ('archive/tbz/tarred_bzipped.tar.bz2', ['bzip2', 'Tar bzip2']),
            ('archive/tbz/tarred_bzipped.bz', ['bzip2', 'Tar bzip2']),
            ('archive/tgz/tarred_gzipped.gz', ['Tar gzip', 'Gzip']),
            ('archive/gzip/mysql-arch.ARZ', ['Tar gzip', 'Gzip']),
        ]

        for test_file, expected in test_data:
            test_loc = self.get_test_loc(test_file)
            handlers = archive.get_handlers(test_loc)
            assert expected == [h[0].name for h in handlers]

    def test_score_handlers(self):
        test_data = [
            ('archive/deb/adduser_3.112ubuntu1_all.deb', [(31, 'Debian package'), (11, 'Tar')]),
            ('archive/rpm/elfinfo-1.0-1.fc9.src.rpm', [(32, 'RPM package')]),
            ('archive/ar/liby.a', [(31, 'Static Library'), (17, 'ar archive')]),
            ('archive/tar/tarred.tar', [(29, 'Tar')]),
            ('archive/tar/gem/panchira-0.1.1.gem', [(31, 'Ruby Gem package'), (17, 'Tar')]),
            ('archive/tbz/tarred_bzipped.tar.bz2', [(30, 'Tar bzip2'), (29, 'bzip2')]),
            ('archive/tbz/tarred_bzipped.bz', [(29, 'bzip2'), (18, 'Tar bzip2')]),
            ('archive/tgz/tarred_gzipped.gz', [(29, 'Gzip'), (18, 'Tar gzip')]),
            ('archive/gzip/mysql-arch.ARZ', [(29, 'Gzip'), (18, 'Tar gzip')]),
        ]

        for test_file, expected in test_data:
            test_loc = self.get_test_loc(test_file)
            handlers = archive.get_handlers(test_loc)
            scored = archive.score_handlers(handlers)
            assert expected == sorted([(h[0], h[1].name) for h in scored], reverse=True)

    def test_no_handler_is_selected_for_a_non_archive(self):
        # failed because of libmagic bug: http://bugs.gw.com/view.php?id=467
        # passing by introducing strict flag for handlers
        test_loc = self.get_test_loc('archive/not_archive/hashfile')
        assert [] == list(archive.get_handlers(test_loc))
        assert None == archive.get_extractor(test_loc)
        assert None == archive.get_extractor(test_loc, kinds=extractcode.all_kinds)
        assert not archive.should_extract(test_loc, kinds=extractcode.default_kinds)

    def test_no_handler_is_selected_for_a_non_archive2(self):
        # FWIW there is a related libmagic bug: http://bugs.gw.com/view.php?id=473
        test_loc = self.get_test_loc('archive/not_archive/wildtest.txt')
        assert [] == list(archive.get_handlers(test_loc))
        assert None == archive.get_extractor(test_loc)
        assert None == archive.get_extractor(test_loc, kinds=extractcode.all_kinds)
        assert not archive.should_extract(test_loc, kinds=extractcode.default_kinds)

    def test_no_handler_is_selected_for_a_non_archive3(self):
        test_loc = self.get_test_loc('archive/not_archive/savetransfer.c')
        assert [] == list(archive.get_handlers(test_loc))
        assert None == archive.get_extractor(test_loc)
        assert None == archive.get_extractor(test_loc, kinds=extractcode.all_kinds)
        assert not archive.should_extract(test_loc, kinds=extractcode.default_kinds)

    def test_7zip_extract_can_extract_to_relative_paths(self):
        # The setup is a tad complex because we want to have a relative dir
        # to the base dir where we run tests from, ie the scancode-toolkit/ dir
        # To use relative paths, we use our tmp dir at the root of the code tree
        from os.path import dirname, join, abspath
        import tempfile
        import shutil
        from extractcode.sevenzip import extract

        test_file = self.get_test_loc('archive/relative_path/basic.zip', copy=True)
        scancode_root = dirname(dirname(dirname(__file__)))
        scancode_tmp = join(scancode_root, 'tmp')
        fileutils.create_dir(scancode_tmp)
        scancode_root_abs = abspath(scancode_root)
        test_src_dir = tempfile.mkdtemp(dir=scancode_tmp).replace(scancode_root_abs, '').strip('\\/')
        test_tgt_dir = tempfile.mkdtemp(dir=scancode_tmp).replace(scancode_root_abs, '').strip('\\/')
        shutil.copy(test_file, test_src_dir)
        test_src_file = join(test_src_dir, 'basic.zip')
        result = list(extract(test_src_file, test_tgt_dir))
        assert [] == result
        expected = ['c/a/a.txt', 'c/b/a.txt', 'c/c/a.txt']
        check_files(test_tgt_dir, expected)

    def test_windows_media_player_skins_are_zip(self):
        test_file = self.get_test_loc('archive/wmz/Go.wmz')
        extractors = archive.get_extractors(test_file)
        assert [archive.extract_zip] == extractors

    def test_windows_ntfs_wmz_are_sometimes_gzip(self):
        test_file = self.get_test_loc('archive/wmz/image003.wmz')
        extractors = archive.get_extractors(test_file)
        assert [archive.uncompress_gzip] == extractors


class TestTarGzip(BaseArchiveTestCase):

    def test_extract_targz_basic(self):
        test_file = self.get_test_loc('archive/tgz/tarred_gzipped.tar.gz')
        test_dir = self.get_temp_dir()
        archive.extract_tar(test_file, test_dir)
        result = os.path.join(test_dir, 'e/a/b.txt')
        assert os.path.exists(result)

    def test_extract_targz_with_trailing_data(self):
        test_file = self.get_test_loc('archive/tgz/trailing.tar.gz')
        test_dir = self.get_temp_dir()
        archive.extract_tar(test_file, test_dir)
        result = os.path.join(test_dir, 'a.txt')
        assert os.path.exists(result)

    def test_extract_targz_broken(self):
        test_file = self.get_test_loc('archive/tgz/broken.tar.gz')
        test_dir = self.get_temp_dir()
        expected = Exception('Unrecognized archive format')
        self.assertRaisesInstance(expected, archive.extract_tar, test_file, test_dir)

    def test_extract_targz_with_absolute_path(self):
        non_result = '/tmp/subdir'
        assert not os.path.exists(non_result)

        test_dir = self.get_temp_dir()
        test_file = self.get_test_loc('archive/tgz/absolute_path.tar.gz')
        archive.extract_tar(test_file, test_dir)
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
        archive.extract_tar(test_file, test_dir)

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
        archive.extract_tar(test_file, test_dir1)

        test_dir2 = self.get_temp_dir()
        test_file2 = self.get_test_loc('archive/tgz/no_trailing.tar.gz')
        archive.extract_tar(test_file2, test_dir2)
        assert commoncode.testcase.is_same(test_dir1, test_dir2)

    def test_extract_targz_with_mixed_case_and_symlink(self):
        test_file = self.get_test_loc('archive/tgz/mixed_case_and_symlink.tgz')
        test_dir = self.get_temp_dir()
        result = archive.extract_tar(test_file, test_dir)
        assert [] == result
        import json
        exp_file = self.get_test_loc('archive/tgz/mixed_case_and_symlink.tgz.expected')
        with io.open(exp_file, encoding='utf-8') as ef:
            expected_files = json.load(ef)
        check_files(test_dir, list(map(str, expected_files)))

    def test_extract_targz_symlinks(self):
        test_file = self.get_test_loc('archive/tgz/symlink.tar.gz')
        test_dir = self.get_temp_dir()
        archive.extract_tar(test_file, test_dir)
        expected = [
            'z/x/a',
            # these are skipped
            # this is a link: a -> ../x/a
            # 'z/y/a',
            # this is a broken link: x.a -> ../x.a
            # 'z/y/x.a',
            # this is a broken link: broken -> ../x/broken
            # 'z/z/broken',
        ]
        check_files(test_dir, expected)

    def test_extract_targz_from_apache_should_not_return_errors(self):
        # from http://archive.apache.org/dist/commons/logging/source/commons-logging-1.1.2-src.tar.gz
        # failed with ReadError('not a bzip2 file',)
        test_file = self.get_test_loc('archive/tgz/commons-logging-1.1.2-src.tar.gz')
        test_dir = self.get_temp_dir()
        extractor = archive.get_extractor(test_file)
        assert archive.extract_tar == extractor
        result = archive.extract_tar(test_file, test_dir)
        assert [] == result
        assert os.listdir(test_dir)

    def test_extract_targz_with_unicode_path_should_extract_without_error(self):
        test_file = self.get_test_loc('archive/tgz/tgz_unicode.tgz')
        test_dir = self.get_temp_dir()
        extractor = archive.get_extractor(test_file)
        assert archive.extract_tar == extractor
        result = archive.extract_tar(test_file, test_dir)
        assert [] == result
        assert os.listdir(test_dir)


class TestUncompressGzip(BaseArchiveTestCase):

    def test_uncompress_gzip_basic(self):
        test_file = self.get_test_loc('archive/gzip/file_4.26-1.diff.gz')
        test_dir = self.get_temp_dir()
        archive.uncompress_gzip(test_file, test_dir)
        result = os.path.join(test_dir, 'file_4.26-1.diff.gz-extract')
        assert os.path.exists(result)

    def test_uncompress_concatenated_gzip(self):
        # Archive created with:
        # echo "f1content" > f1
        # echo "f2content" > f2
        # gzip -k f1
        # gzip -k -c f2 >> twofiles.gz
        test_file = self.get_test_loc('archive/gzip/twofiles.gz')
        test_dir = self.get_temp_dir()
        warnings = archive.uncompress_gzip(test_file, test_dir)
        result = os.path.join(test_dir, 'twofiles.gz-extract')
        assert os.path.exists(result)
        assert b'f1content\nf2content\n' == open(result, 'rb').read()
        assert [] == warnings

    @pytest.mark.skipif(py3, reason='Fails for now on Python 3')
    def test_uncompress_gzip_with_trailing_data_py2(self):
        test_file = self.get_test_loc('archive/gzip/trailing_data.gz')
        test_dir = self.get_temp_dir()
        warnings = archive.uncompress_gzip(test_file, test_dir)
        result = os.path.join(test_dir, 'trailing_data.gz-extract')
        assert os.path.exists(result)
        assert [] == warnings

    @pytest.mark.xfail
    @pytest.mark.skipif(py2, reason='Fails for now on Python 3')
    def test_uncompress_gzip_with_trailing_data_py3(self):
        test_file = self.get_test_loc('archive/gzip/trailing_data.gz')
        test_dir = self.get_temp_dir()
        warnings = archive.uncompress_gzip(test_file, test_dir)
        result = os.path.join(test_dir, 'trailing_data.gz-extract')
        assert os.path.exists(result)
        assert [] == warnings

    def test_uncompress_gzip_with_leading_data(self):
        # even though we do not fail when there is invalid trailing data we
        # should still fail on invalid leading data
        test_file = self.get_test_loc('archive/gzip/leading_data.gz')
        test_dir = self.get_temp_dir()
        expected = Exception('Not a gzipped file')
        self.assertRaisesInstance(expected, archive.uncompress_gzip, test_file, test_dir)

    def test_uncompress_gzip_with_random_data(self):
        test_file = self.get_test_loc('archive/gzip/random_binary.data')
        test_dir = self.get_temp_dir()
        expected = Exception('Not a gzipped file')
        self.assertRaisesInstance(expected, archive.uncompress_gzip, test_file, test_dir)

    def test_uncompress_gzip_with_backslash_in_path(self):
        # weirdly enough, gzip keeps the original path/name
        test_file = self.get_test_loc('archive/gzip/backslash_path.gz')
        test_dir = self.get_temp_dir()
        archive.uncompress_gzip(test_file, test_dir)
        result = os.path.join(test_dir, 'backslash_path.gz-extract')
        assert os.path.exists(result)

    def test_uncompress_gzip_can_uncompress_windows_ntfs_wmz(self):
        test_file = self.get_test_loc('archive/wmz/image003.wmz')
        test_dir = self.get_temp_dir()
        archive.uncompress_gzip(test_file, test_dir)
        result = os.path.join(test_dir, 'image003.wmz-extract')
        assert os.path.exists(result)

    def test_uncompress_gzip_can_uncompress_mysql_arz(self):
        test_file = self.get_test_loc('archive/gzip/mysql-arch.ARZ')
        test_dir = self.get_temp_dir()
        archive.uncompress_gzip(test_file, test_dir)
        result = os.path.join(test_dir, 'mysql-arch.ARZ-extract')
        assert os.path.exists(result)


class TestTarBz2(BaseArchiveTestCase):

    def test_extract_tar_bz2_basic(self):
        test_file = self.get_test_loc('archive/tbz/tarred_bzipped.tar.bz2')
        test_dir = self.get_temp_dir()
        archive.extract_tar(test_file, test_dir)
        result = os.path.join(test_dir, 'e/a/b.txt')
        assert os.path.exists(result)

    def test_extract_tar_bz2_basic_bz(self):
        test_file = self.get_test_loc('archive/tbz/tarred_bzipped.bz')
        test_dir = self.get_temp_dir()
        archive.extract_tar(test_file, test_dir)
        result = os.path.join(test_dir, 'e/a/b.txt')
        assert os.path.exists(result)

    def test_extract_tar_bz2_with_trailing_data__and_wrong_extension(self):
        test_file = self.get_test_loc('archive/tbz/single_file_trailing_data.tar.gz')
        test_dir = self.get_temp_dir()
        archive.extract_tar(test_file, test_dir)
        result = os.path.join(test_dir, 'a.txt')
        assert os.path.exists(result)

    def test_extract_tar_bz2_broken(self):
        test_file = self.get_test_loc('archive/tbz/tarred_bzipped_broken.tar.bz2')
        test_dir = self.get_temp_dir()
        expected = Exception('bzip decompression failed')
        self.assertRaisesInstance(expected, archive.extract_tar, test_file, test_dir)

    def test_extract_tar_bz2_absolute_path(self):
        assert not os.path.exists('/tmp/subdir')
        test_dir = self.get_temp_dir()
        test_file = self.get_test_loc('archive/tbz/absolute_path.tar.bz2')
        archive.extract_tar(test_file, test_dir)
        assert not os.path.exists('/tmp/subdir')
        result = os.path.join(test_dir, 'tmp/subdir/a.txt')
        assert os.path.exists(result)

    def test_extract_tar_bz2_relative_path(self):
        """
        This test file was created with:
            import tarfile
            tar = tarfile.open("TarTest.tar.gz", "w:bz")
            tar.add('a.txt', '../a_parent_folder.txt')
            tar.add('b.txt', '../../another_folder/b_two_root.txt')
            tar.add('b.txt', '../folder/subfolder/b_subfolder.txt')
            tar.close()
        """
        test_file = self.get_test_loc('archive/tbz/bz2withtar_relative.tar.bz2')
        test_dir = self.get_temp_dir()
        archive.extract_tar(test_file, test_dir)

        non_result = os.path.join(test_dir, '../a_parent_folder.txt')
        assert not os.path.exists(non_result)

        result = os.path.join(test_dir, 'dotdot/folder/subfolder/b_subfolder.txt')
        assert os.path.exists(result)
        result = os.path.join(test_dir, 'dotdot', 'a_parent_folder.txt')
        assert os.path.exists(result)

    def test_extract_tar_bz2_iproute(self):
        test_file = self.get_test_loc('archive/tbz/iproute2.tar.bz2')
        test_dir = self.get_temp_dir()
        archive.extract_tar(test_file, test_dir)
        result = os.path.join(test_dir, 'iproute2/README')
        assert os.path.exists(result)

    def test_extract_tar_bz2_multistream(self):
        test_file = self.get_test_loc('archive/tbz/bzip2_multistream/example-file.csv.tar.bz2')
        test_dir = self.get_temp_dir()
        archive.extract_tar(test_file, test_dir)
        expected = self.get_test_loc('archive/tbz/bzip2_multistream/example-file.csv')
        result = os.path.join(test_dir, 'example-file.csv')
        assert open(expected, 'rb').read() == open(result, 'rb').read()


class TestUncompressBz2(BaseArchiveTestCase):

    def test_uncompress_bzip2_basic(self):
        test_file = self.get_test_loc('archive/bz2/single_file_not_tarred.bz2')
        test_dir = self.get_temp_dir()
        archive.uncompress_bzip2(test_file, test_dir)
        result = os.path.join(test_dir, 'single_file_not_tarred.bz2-extract')
        assert os.path.exists(result)

    def test_uncompress_bzip2_with_trailing_data(self):
        test_file = self.get_test_loc('archive/bz2/single_file_trailing_data.bz2')
        test_dir = self.get_temp_dir()
        archive.uncompress_bzip2(test_file, test_dir)
        result = os.path.join(test_dir, 'single_file_trailing_data.bz2-extract')
        assert os.path.exists(result)

    def test_uncompress_bzip2_broken(self):
        test_file = self.get_test_loc('archive/bz2/bz2_not_tarred_broken.bz2')
        test_dir = self.get_temp_dir()
        if py2:
            expected = Exception('invalid data stream')
        else:
            expected = Exception('Invalid data stream')

        self.assertRaisesInstance(expected, archive.uncompress_bzip2,
                                  test_file, test_dir)

    def test_uncompress_bzip2_with_invalid_path(self):
        test_file = self.get_test_loc('archive/bz2/bz_invalidpath.bz2')
        test_dir = self.get_temp_dir()
        archive.uncompress_bzip2(test_file, test_dir)
        result = os.path.join(test_dir, 'bz_invalidpath.bz2-extract')
        assert os.path.exists(result)

    def test_uncompress_bzip2_multistream(self):
        test_file = self.get_test_loc('archive/bz2/bzip2_multistream/example-file.csv.bz2')
        test_dir = self.get_temp_dir()
        archive.uncompress_bzip2(test_file, test_dir)
        expected = self.get_test_loc('archive/bz2/bzip2_multistream/expected.csv')
        result = os.path.join(test_dir, 'example-file.csv.bz2-extract')
        assert open(expected, 'rb').read() == open(result, 'rb').read()


class TestSevenzipBz2(BaseArchiveTestCase):

    def test_sevenzip_extract_can_handle_bz2_multistream_differently(self):
        test_file = self.get_test_loc('archive/bz2/bzip2_multistream/example-file.csv.bz2')
        test_dir = self.get_temp_dir()
        sevenzip.extract(test_file, test_dir)
        expected = self.get_test_loc('archive/bz2/bzip2_multistream/expected.csv')
        # the extraction dir is not created with suffix by z7
        result = os.path.join(test_dir, 'example-file.csv')
        expected_extracted = open(expected, 'rb').read()
        expected_result = open(result, 'rb').read()
        assert  expected_extracted == expected_result


class TestShellArchives(BaseArchiveTestCase):

    def test_extract_springboot(self):
        # a self executable springboot Jar is a zip with a shell script prefix
        test_file = self.get_test_loc('archive/shar/demo-spring-boot.jar')
        test_dir = self.get_temp_dir()
        result = archive.extract_springboot(test_file, test_dir)
        assert [] == result
        expected = ['META-INF/MANIFEST.MF', 'application.properties']
        check_files(test_dir, expected)

    def test_springboot_is_not_recognized_without_jar_extension(self):
        test_file = self.get_test_loc('archive/shar/demo-spring-boot.sh')
        handler = archive.get_best_handler(test_file)
        assert None == handler

    def test_springboot_is_recognized_with_jar_extension(self):
        test_file = self.get_test_loc('archive/shar/demo-spring-boot.jar')
        handler = archive.get_best_handler(test_file)
        assert handler.name == 'Springboot Java Jar package'


class TestZip(BaseArchiveTestCase):

    def test_extract_zip_basic(self):
        test_file = self.get_test_loc('archive/zip/basic.zip')
        test_dir = self.get_temp_dir()
        result = archive.extract_zip(test_file, test_dir)
        assert [] == result
        expected = ['c/a/a.txt', 'c/b/a.txt', 'c/c/a.txt']
        check_files(test_dir, expected)

    def test_extract_zip_broken(self):
        test_file = self.get_test_loc('archive/zip/zip_broken.zip')
        test_dir = self.get_temp_dir()
        archive.extract_zip(test_file, test_dir)
        # note: broken zip opens and extracts with 7z sometimes
        assert [] == os.listdir(test_dir)

    def test_extract_zip_with_invalid_path(self):
        test_file = self.get_test_loc('archive/zip/zip_invalidpath.zip')
        test_dir = self.get_temp_dir()
        archive.extract_zip(test_file, test_dir)
        result = os.path.join(test_dir, 'this/that')
        assert os.path.exists(result)

    def test_extract_zip_with_trailing_data(self):
        test_file = self.get_test_loc('archive/zip/zip_trailing_data.zip')
        test_dir = self.get_temp_dir()
        try:
            archive.extract_zip(test_file, test_dir)
        except libarchive2.ArchiveError as ae:
            assert 'Invalid central directory signature' in str(ae)

        # fails because of https://github.com/libarchive/libarchive/issues/545
        result = os.path.join(test_dir, 'a.txt')
        assert os.path.exists(result)

    def test_extract_zip_with_trailing_data2(self):
        # test archive created on cygwin with:
        # $ echo "test content" > f1
        # $ zip test f1
        # $ echo "some junk" >> test.zip
        test_file = self.get_test_loc('archive/zip/zip_trailing_data2.zip')
        test_dir = self.get_temp_dir()
        try:
            archive.extract_zip(test_file, test_dir)
        except libarchive2.ArchiveError as ae:
            assert 'Invalid central directory signature' in str(ae)
        # fails because of https://github.com/libarchive/libarchive/issues/545
        result = os.path.join(test_dir, 'f1')
        assert os.path.exists(result)

    def test_extract_zip_with_relative_path_using_default_function(self):
        # The test files for this test and the next one were created with:
        # from zipfile import ZipFile
        # f = open('/tmp/a.txt', 'w')
        # f.write('some data')
        # f.close()
        # f = open('/tmp/b.txt', 'w')
        # f.write('some data')
        # f.close()
        # f = ZipFile(os.path.join(self.get_test_loc('archive'), 'relative_parent_folders.zip'), 'w')
        # f.write('/tmp/a.txt', '../a_parent_folder.txt')
        # f.write('/tmp/b.txt', '../../another_folder/b_two_root.txt')
        # f.write('/tmp/b.txt', '../folder/subfolder/b_subfolder.txt')
        # f.close()
        # f = ZipFile(os.path.join(self.get_test_loc('archive'), 'high_ancest.zip'), 'w')
        # f.write('/tmp/a.txt', ('../' * 12) +  'a_parent_folder.txt')
        # f.write('/tmp/a.txt', ('../' * 12) +  ('sub/' * 6) + 'a_parent_folder_in_sub_1.txt')
        # f.write('/tmp/a.txt', ('../' * 6) +  ('sub/' * 12) + 'a_parent_folder_in_sub_2.txt')
        # f.write('/tmp/a.txt', ('../' * 12) +  ('sub/' * 12) + 'a_parent_folder_in_sub_3.txt')
        # f.close()

        test_file = self.get_test_loc('archive/zip/relative_parent_folders.zip')
        test_dir = self.get_temp_dir()
        archive.extract_zip(test_file, test_dir)

        abs_path = os.path.join(test_dir , '../a_parent_folder.txt')
        assert not os.path.exists(abs_path)

        result = self.collect_extracted_path(test_dir)
        expected = [
            '/dotdot/',
            '/dotdot/a_parent_folder.txt',
            '/dotdot/dotdot/',
            '/dotdot/dotdot/another_folder/',
            '/dotdot/dotdot/another_folder/b_two_root.txt',
            '/dotdot/folder/',
            '/dotdot/folder/subfolder/',
            '/dotdot/folder/subfolder/b_subfolder.txt'
        ]
        assert expected == result

    def test_extract_zip_with_relative_path_using_libarchive(self):
        test_file = self.get_test_loc('archive/zip/relative_parent_folders.zip')
        test_dir = self.get_temp_dir()
        result = libarchive2.extract(test_file, test_dir)
        assert [] == result
        abs_path = os.path.join(test_dir , '../a_parent_folder.txt')
        assert not os.path.exists(abs_path)
        result = os.path.join(test_dir, 'dotdot/folder/subfolder/b_subfolder.txt')
        assert os.path.exists(result)
        result = os.path.join(test_dir, 'dotdot/a_parent_folder.txt')
        assert os.path.exists(result)
        result = os.path.join(test_dir, 'dotdot/dotdot/another_folder/b_two_root.txt')
        assert os.path.exists(result)

    expected_deeply_nested_relative_path = [
        '/dotdot/',
        '/dotdot/dotdot/',
        '/dotdot/dotdot/dotdot/',
        '/dotdot/dotdot/dotdot/dotdot/',
        '/dotdot/dotdot/dotdot/dotdot/dotdot/',
        '/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/',
        '/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/',
        '/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/',
        '/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/',
        '/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/',
        '/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/',
        '/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/',
        '/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/a_parent_folder.txt',
        '/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/sub/',
        '/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/sub/sub/',
        '/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/sub/sub/sub/',
        '/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/sub/sub/sub/sub/',
        '/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/sub/sub/sub/sub/sub/',
        '/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/sub/sub/sub/sub/sub/sub/',
        '/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/sub/sub/sub/sub/sub/sub/a_parent_folder_in_sub_1.txt',
        '/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/sub/sub/sub/sub/sub/sub/sub/',
        '/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/sub/sub/sub/sub/sub/sub/sub/sub/',
        '/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/sub/sub/sub/sub/sub/sub/sub/sub/sub/',
        '/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/sub/sub/sub/sub/sub/sub/sub/sub/sub/sub/',
        '/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/sub/sub/sub/sub/sub/sub/sub/sub/sub/sub/sub/',
        '/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/sub/sub/sub/sub/sub/sub/sub/sub/sub/sub/sub/sub/',
        '/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/sub/sub/sub/sub/sub/sub/sub/sub/sub/sub/sub/sub/a_parent_folder_in_sub_3.txt',
        '/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/sub/',
        '/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/sub/sub/',
        '/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/sub/sub/sub/',
        '/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/sub/sub/sub/sub/',
        '/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/sub/sub/sub/sub/sub/',
        '/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/sub/sub/sub/sub/sub/sub/',
        '/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/sub/sub/sub/sub/sub/sub/sub/',
        '/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/sub/sub/sub/sub/sub/sub/sub/sub/',
        '/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/sub/sub/sub/sub/sub/sub/sub/sub/sub/',
        '/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/sub/sub/sub/sub/sub/sub/sub/sub/sub/sub/',
        '/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/sub/sub/sub/sub/sub/sub/sub/sub/sub/sub/sub/',
        '/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/sub/sub/sub/sub/sub/sub/sub/sub/sub/sub/sub/sub/',
        '/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/sub/sub/sub/sub/sub/sub/sub/sub/sub/sub/sub/sub/a_parent_folder_in_sub_2.txt'
    ]

    # somehow Windows fails randomly and only on certain windows machines at Appveyor
    # so we retest with a skinny expectation
    expected_deeply_nested_relative_path_alternative = [
        u'/a_parent_folder.txt',
        u'/sub/',
        u'/sub/sub/',
        u'/sub/sub/sub/',
        u'/sub/sub/sub/sub/',
        u'/sub/sub/sub/sub/sub/',
        u'/sub/sub/sub/sub/sub/sub/',
        u'/sub/sub/sub/sub/sub/sub/a_parent_folder_in_sub_1.txt',
        u'/sub/sub/sub/sub/sub/sub/sub/',
        u'/sub/sub/sub/sub/sub/sub/sub/sub/',
        u'/sub/sub/sub/sub/sub/sub/sub/sub/sub/',
        u'/sub/sub/sub/sub/sub/sub/sub/sub/sub/sub/',
        u'/sub/sub/sub/sub/sub/sub/sub/sub/sub/sub/sub/',
        u'/sub/sub/sub/sub/sub/sub/sub/sub/sub/sub/sub/sub/',
        u'/sub/sub/sub/sub/sub/sub/sub/sub/sub/sub/sub/sub/a_parent_folder_in_sub_2.txt',
        u'/sub/sub/sub/sub/sub/sub/sub/sub/sub/sub/sub/sub/a_parent_folder_in_sub_3.txt']

    def test_extract_zip_with_relative_path_deeply_nested(self):
        test_file = self.get_test_loc('archive/zip/relative_nested.zip')
        test_dir = self.get_temp_dir()
        archive.extract_zip(test_file, test_dir)
        result = self.collect_extracted_path(test_dir)

        try:
            assert self.expected_deeply_nested_relative_path == result
        except:
            assert self.expected_deeply_nested_relative_path_alternative == result

    @pytest.mark.xfail
    @pytest.mark.skipif(on_windows or py3, reason='Expectations are different on Windows')
    def test_extract_zip_with_relative_path_deeply_nested_with_7zip_posix_py2(self):
        test_file = self.get_test_loc('archive/zip/relative_nested.zip')
        test_dir = self.get_temp_dir()
        try:
            sevenzip.extract(test_file, test_dir)
            self.fail('Should raise an exception')
        except ExtractErrorFailedToExtract as e:
            assert 'Unknown extraction error' == str(e)

    @pytest.mark.xfail
    @pytest.mark.skipif(on_windows or py2, reason='Expectations are different on Windows')
    def test_extract_zip_with_relative_path_deeply_nested_with_7zip_posix_py3(self):
        test_file = self.get_test_loc('archive/zip/relative_nested.zip')
        test_dir = self.get_temp_dir()
        try:
            sevenzip.extract(test_file, test_dir)
            self.fail('Should raise an exception')
        except ExtractErrorFailedToExtract as e:
            assert 'Unknown extraction error' == str(e)

    @pytest.mark.skipif(not on_windows, reason='Expectations are different on Windows')
    def test_extract_zip_with_relative_path_deeply_nested_with_7zip_windows(self):
        test_file = self.get_test_loc('archive/zip/relative_nested.zip')
        test_dir = self.get_temp_dir()
        sevenzip.extract(test_file, test_dir)
        result = self.collect_extracted_path(test_dir)
        assert self.expected_deeply_nested_relative_path_alternative == result

    def test_list_zip_with_relative_path_deeply_nested_with_7zip(self):
        test_file = self.get_test_loc('archive/zip/relative_nested.zip')
        result = []
        entries, errors = sevenzip.list_entries(test_file)
        assert not errors
        for entry in entries:
            if on_windows:
                entry.path = entry.path.replace('\\', '/')
            result.append(entry.to_dict(full=False))

        expected = [
            {'errors': [],
             u'is_broken_link': False,
             u'is_dir': False,
             u'is_file': True,
             u'is_hardlink': False,
             u'is_special': False,
             u'is_symlink': False,
             u'link_target': None,
             u'path': '../../../../../../../../../../../../a_parent_folder.txt',
             u'size': '9'},
            {'errors': [],
             u'is_broken_link': False,
             u'is_dir': False,
             u'is_file': True,
             u'is_hardlink': False,
             u'is_special': False,
             u'is_symlink': False,
             u'link_target': None,
             u'path': '../../../../../../../../../../../../sub/sub/sub/sub/sub/sub/a_parent_folder_in_sub_1.txt',
             u'size': '9'},
            {'errors': [],
             u'is_broken_link': False,
             u'is_dir': False,
             u'is_file': True,
             u'is_hardlink': False,
             u'is_special': False,
             u'is_symlink': False,
             u'link_target': None,
             u'path': '../../../../../../sub/sub/sub/sub/sub/sub/sub/sub/sub/sub/sub/sub/a_parent_folder_in_sub_2.txt',
             u'size': '9'},
            {'errors': [],
             u'is_broken_link': False,
             u'is_dir': False,
             u'is_file': True,
             u'is_hardlink': False,
             u'is_special': False,
             u'is_symlink': False,
             u'link_target': None,
             u'path': '../../../../../../../../../../../../sub/sub/sub/sub/sub/sub/sub/sub/sub/sub/sub/sub/a_parent_folder_in_sub_3.txt',
             u'size': '9'}]
        assert expected == result

    def test_extract_zip_with_relative_path_deeply_nested_with_libarchive(self):
        test_file = self.get_test_loc('archive/zip/relative_nested.zip')
        test_dir = self.get_temp_dir()
        libarchive2.extract(test_file, test_dir)
        result = self.collect_extracted_path(test_dir)
        assert self.expected_deeply_nested_relative_path == result

    def test_extract_zip_with_password(self):
        test_file = self.get_test_loc('archive/zip/zip_password_nexb.zip')
        test_dir = self.get_temp_dir()
        try:
            archive.extract_zip(test_file, test_dir)
        except Exception as e:
            assert isinstance(e, ExtractErrorFailedToExtract)
            assert 'Password protected archive, unable to extract' in str(e)

    def test_extract_zip_java_jar(self):
        test_file = self.get_test_loc('archive/zip/jar/simple.jar')
        test_dir = self.get_temp_dir()
        archive.extract_zip(test_file, test_dir)
        extracted = self.collect_extracted_path(test_dir)
        expected = [
            '/META-INF/',
            '/META-INF/MANIFEST.MF',
            '/org/',
            '/org/jvnet/',
            '/org/jvnet/glassfish/',
            '/org/jvnet/glassfish/comms/',
            '/org/jvnet/glassfish/comms/sipagent/',
            '/org/jvnet/glassfish/comms/sipagent/actions/',
            '/org/jvnet/glassfish/comms/sipagent/actions/Bundle.properties',
            '/org/jvnet/glassfish/comms/sipagent/actions/SipAgentCookieAction.class',
            '/org/jvnet/glassfish/comms/sipagent/actions/bd.png',
            '/org/jvnet/glassfish/comms/sipagent/actions/bd24.png',
            '/org/jvnet/glassfish/comms/sipagent/org-jvnet-glassfish-comms-sipagent-actions-SipAgentCookieAction.instance',
            '/org/jvnet/glassfish/comms/sipagent/org-jvnet-glassfish-comms-sipagent-actions-SipAgentCookieAction_1.instance'
        ]
        assert sorted(expected) == sorted(extracted)

    def test_extract_zip_with_duplicated_lowercase_paths(self):
        test_file = self.get_test_loc('archive/zip/dup_names.zip')
        expected = {'META-INF/license/': None,  # a directory
                    'META-INF/license/LICENSE.base64.txt': 1618,
                    'META-INF/LICENSE_1': 11366}
        self.check_extract(archive.extract_zip, test_file, expected)

    def test_extract_zip_with_timezone(self):
        test_file = self.get_test_loc('archive/zip/timezone/c.zip')
        test_dir = self.get_temp_dir()
        archive.extract_zip(test_file, test_dir)
        expected = [
            (os.path.join(test_dir, 'c/a/a.txt'), '2008-07-29'),
            (os.path.join(test_dir, 'c/b/a.txt'), '2008-07-29'),
            (os.path.join(test_dir, 'c/c/a.txt'), '2008-07-29'),
        ]
        # DST sends a monkey wrench.... so we only test the date, not the time
        for loc, expected_date in expected:
            result = commoncode.date.get_file_mtime(loc)
            assert result.startswith(expected_date)

    def test_extract_zip_with_timezone_2(self):
        test_file = self.get_test_loc('archive/zip/timezone/projecttest.zip')
        test_dir = self.get_temp_dir()
        archive.extract_zip(test_file, test_dir)
        # DST sends a monkey wrench.... so we only test the date, not the time
        # and we accept some varation in the date ...
        expected = [
            (os.path.join(test_dir, 'primes.txt'), ('2009-12-05', '2009-12-06',)),
            (os.path.join(test_dir, 'primes2.txt'), ('2009-12-05', '2009-12-06',))
        ]
        for loc, expected_date in expected:
            result = commoncode.date.get_file_mtime(loc)
            assert result.startswith(expected_date)

    def test_extract_zip_with_backslash_in_path_1(self):
        test_file = self.get_test_loc('archive/zip/backslash/backslash1.zip')
        test_dir = self.get_temp_dir()
        archive.extract_zip(test_file, test_dir)
        # Info-ZIP 'zip' displays:
        # warning: booxw-1202-bin.distribution.zip appears to use
        # backslashes as path separators (which is the right thing to do)
        expected = ['scripts/AutomaticClose.int']
        check_files(test_dir, expected)

        result = os.path.join(test_dir, 'scripts/AutomaticClose.int')
        assert os.path.exists(result)

    def test_extract_zip_with_backslash_in_path_2(self):
        test_file = self.get_test_loc('archive/zip/backslash/AspectJTest.zip')
        test_dir = self.get_temp_dir()
        archive.extract_zip(test_file, test_dir)
        expected = '''
            AspectJTest/.classpath
            AspectJTest/.project
            AspectJTest/src/META-INF/aop.xml
            AspectJTest/src/p3/ExpertFlyable.java
            AspectJTest/src/p3/MakeFlyableAspect.java
            AspectJTest/src/p3/Flyable.java
            AspectJTest/src/p3/MakeFlyable.java
            AspectJTest/src/p3/Main2.java
            AspectJTest/src/p3/p4/Person.java
            AspectJTest/src/p2/MyLoggingAspect.java
            AspectJTest/src/p1/MyService.java
            AspectJTest/src/p1/Main1.java
            AspectJTest/bin/META-INF/aop.xml
            AspectJTest/bin/p3/MakeFlyableAspect.class
            AspectJTest/bin/p3/ExpertFlyable.class
            AspectJTest/bin/p3/Flyable.class
            AspectJTest/bin/p3/Main2.class
            AspectJTest/bin/p3/MakeFlyable.class
            AspectJTest/bin/p3/p4/Person.class
            AspectJTest/bin/p2/MyLoggingAspect.class
            AspectJTest/bin/p1/Main1.class
            AspectJTest/bin/p1/MyService.class
            '''.split()
        check_files(test_dir, expected)

    def test_extract_zip_with_backslash_in_path_3(self):
        test_file = self.get_test_loc('archive/zip/backslash/boo-0.3-src.zip')
        test_dir = self.get_temp_dir()
        archive.extract_zip(test_file, test_dir)
        result = os.path.join(test_dir, 'src/Boo.Lang.Compiler/TypeSystem/InternalCallableType.cs')
        assert os.path.exists(result)

    def test_get_best_handler_nuget_is_selected_over_zip(self):
        test_file = self.get_test_loc('archive/zip/moq.4.2.1507.118.nupkg')
        handler = archive.get_best_handler(test_file)
        assert archive.NugetHandler == handler

    def test_get_best_handler_nuget_is_selected_over_zip2(self):
        test_file = self.get_test_loc('archive/zip/exceptionhero.javascript.1.0.5.nupkg')
        handler = archive.get_best_handler(test_file)
        assert archive.NugetHandler == handler

    def test_get_best_handler_nuget_is_selected_over_zip3(self):
        test_file = self.get_test_loc('archive/zip/javascript-fastclass.1.1.729.121805.nupkg')
        handler = archive.get_best_handler(test_file)
        assert archive.NugetHandler == handler

    def test_extract_zip_can_extract_windows_media_player_skins(self):
        test_file = self.get_test_loc('archive/wmz/Go.wmz')
        test_dir = self.get_temp_dir()
        result = archive.extract_zip(test_file, test_dir)
        assert [] == result
        expected = ['32px.png', 'go.js', 'go.wms']
        check_files(test_dir, expected)

    def test_extract_zip_with_unicode_path_should_extract_without_error(self):
        test_file = self.get_test_loc('archive/zip/zip_unicode.zip')
        test_dir = self.get_temp_dir()
        result = archive.extract_zip(test_file, test_dir)
        assert [] == result
        assert os.listdir(test_dir)

    def test_extract_zip_can_extract_zip_with_directory_not_marked_with_trailing_slash(self):
        test_file = self.get_test_loc('archive/zip/directory-with-no-trailing-slash.zip')
        test_dir = self.get_temp_dir()
        result = archive.extract_zip(test_file, test_dir)
        assert [] == result
        expected = ['online_upgrade_img/machine_type']
        check_files(test_dir, expected)


class TestTar(BaseArchiveTestCase):

    def test_extract_tar_basic(self):
        test_file = self.get_test_loc('archive/tar/tarred.tar')
        test_dir = self.get_temp_dir()
        archive.extract_tar(test_file, test_dir)
        result = os.path.join(test_dir, 'e/a/b.txt')
        assert os.path.exists(result)

    def test_extract_tar_broken(self):
        test_file = self.get_test_loc('archive/tar/tarred_broken.tar')
        test_dir = self.get_temp_dir()
        expected = Exception("Unrecognized archive format")
        self.assertRaisesInstance(
            expected, archive.extract_tar, test_file, test_dir)

    def test_extract_tar_absolute_path(self):
        non_result = '/home/li/Desktop/absolute_folder'
        assert not os.path.exists(non_result)

        test_dir = self.get_temp_dir()
        test_file = self.get_test_loc('archive/tar/tar_absolute.tar')
        archive.extract_tar(test_file, test_dir)

        assert not os.path.exists(non_result)
        result = os.path.join(test_dir, 'home/li/Desktop/absolute_folder/absolute_file')
        assert os.path.exists(result)

    def test_extract_tar_with_absolute_path2(self):
        assert not os.path.exists('/tmp/subdir')

        test_file = self.get_test_loc('archive/tar/absolute_path.tar')
        test_dir = self.get_temp_dir()
        archive.extract_tar(test_file, test_dir)

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
        archive.extract_tar(test_file, test_dir)
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
        result = archive.extract_tar(test_file, test_dir)
        expected = [
            '0-REGTYPE',
            '0-REGTYPE-TEXT',
            '0-REGTYPE-VEEEERY_LONG_NAME_____________________________________________________________________________________________________________________155',
            # we skip links but not hardlinks
            '1-LNKTYPE',
            'S-SPARSE',
            'S-SPARSE-WITH-NULLS',
        ]
        check_files(test_dir, expected)
        # special files are skipped too
        # '2-SYMTYPE: Skipping broken link to: testtar/0-REGTYPE',
        # '3-CHRTYPE: Skipping special file.',
        # '6-FIFOTYPE: Skipping special file.'
        assert [] == result

    @pytest.mark.skipif(on_windows, reason='Unicode and/or Long paths are not handled well yet on windows')
    def test_extract_python_testtar_tar_archive_with_special_files(self):
        test_file = self.get_test_loc('archive/tar/testtar.tar')
        # this is from:
        # https://hg.python.org/cpython/raw-file/bff88c866886/Lib/test/testtar.tar
        test_dir = self.get_temp_dir()
        result = archive.extract_tar(test_file, test_dir)
        if py2:
            expected_warnings = [
                "'pax/bad-pax-\\xe4\\xf6\\xfc': \nPathname can't be converted from UTF-8 to current locale."]
        else:
            expected_warnings = [
                 u"'pax/bad-pax-äöü': \nPathname can't be converted from UTF-8 to current locale."]

        assert sorted(expected_warnings) == sorted(result)

        expected = [
            'gnu/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/longlink',
            'gnu/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/longname',
            'gnu/regtype-gnu-uid',
            'gnu/sparse',
            'gnu/sparse-0.0',
            'gnu/sparse-0.1',
            'gnu/sparse-1.0',
            'misc/eof',
            'misc/regtype-hpux-signed-chksum-AOUaouss',
            'misc/regtype-old-v7',
            'misc/regtype-old-v7-signed-chksum-AOUaouss',
            'misc/regtype-suntar',
            'misc/regtype-xstar',
            'pax/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/longlink',
            'pax/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/longname',
            'pax/bad-pax-aou',
            'pax/hdrcharset-aou',
            'pax/regtype1',
            'pax/regtype2',
            'pax/regtype3',
            'pax/regtype4',
            'pax/umlauts-AOUaouss',
            'ustar/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/1234567/longname',
            'ustar/conttype',
            'ustar/linktest1/regtype',
            'ustar/linktest2/lnktype',
            'ustar/lnktype',
            'ustar/regtype',
            'ustar/sparse',
            'ustar/umlauts-AOUaouss'
        ]
        if on_linux and py2:
            expected = [bytes(e) for e in expected]
        check_files(test_dir, expected)

    def test_extract_rubygem(self):
        test_file = self.get_test_loc('archive/tar/gem/panchira-0.1.1.gem')
        test_dir = self.get_temp_dir()
        archive.extract_tar(test_file, test_dir)
        expected = ['checksums.yaml.gz', 'data.tar.gz', 'metadata.gz']
        if on_linux and py2:
            expected = [bytes(e) for e in expected]
        check_files(test_dir, expected)


class TestDebian(BaseArchiveTestCase):

    def test_extract_deb_package_1(self):
        test_file = self.get_test_loc('archive/deb/adduser_3.112ubuntu1_all.deb')
        test_dir = self.get_temp_dir()
        archive.extract_ar(test_file, test_dir)
        check_size(110198, os.path.join(test_dir, 'data.tar.gz'))

    def test_extract_deb_package_2(self):
        test_file = self.get_test_loc('archive/deb/adduser_3.113+nmu3ubuntu3_all.deb')
        test_dir = self.get_temp_dir()
        archive.extract_ar(test_file, test_dir)
        check_size(158441, os.path.join(test_dir, 'data.tar.gz'))

    def test_get_best_handler_deb_package_is_an_archive(self):
        test_file = self.get_test_loc('archive/deb/libjama-dev_1.2.4-2_all.deb')
        handler = archive.get_best_handler(test_file)
        assert archive.DebHandler == handler

    def test_extract_deb_package_3(self):
        test_file = self.get_test_loc('archive/deb/wget-el_0.5.0-8_all.deb')
        test_dir = self.get_temp_dir()
        archive.extract_ar(test_file, test_dir)
        check_size(36376, os.path.join(test_dir, 'data.tar.gz'))


class TestAr(BaseArchiveTestCase):

    def test_extract_ar_basic_7z(self):
        test_file = self.get_test_loc('archive/ar/liby.a')
        test_dir = self.get_temp_dir()
        result = sevenzip.extract(test_file, test_dir)
        expected = ['1.txt', 'main.o', 'yyerror.o']
        check_files(test_dir, expected)
        assert [] == result

    def test_extract_ar_basic(self):
        test_file = self.get_test_loc('archive/ar/liby.a')
        test_dir = self.get_temp_dir()
        result = archive.extract_ar(test_file, test_dir)
        expected = ['__.SYMDEF', 'main.o', 'yyerror.o']
        check_files(test_dir, expected)
        assert [] == result

    def test_extract_ar_libarchive(self):
        test_file = self.get_test_loc('archive/ar/liby.a')
        test_dir = self.get_temp_dir()
        result = libarchive2.extract(test_file, test_dir)
        expected = ['__.SYMDEF', 'main.o', 'yyerror.o']
        check_files(test_dir, expected)
        assert [] == result

    def test_extract_ar_verify_dates(self):
        test_file = self.get_test_loc('archive/ar/liby.a')
        test_dir = self.get_temp_dir()
        archive.extract_ar(test_file, test_dir)
        expected = [
            (os.path.join(test_dir, 'main.o'), '2007-06-12'),
            (os.path.join(test_dir, 'yyerror.o'), '2007-06-12'),
        ]
        # DST sends a monkey wrench.... so we only test the date, not the time
        for loc, expected_date in expected:
            result = commoncode.date.get_file_mtime(loc)
            assert result.startswith(expected_date)

    def test_extract_ar_broken_7z(self):
        test_file = self.get_test_loc('archive/ar/liby-corrupted.a')
        test_dir = self.get_temp_dir()
        result = sevenzip.extract(test_file, test_dir)
        expected = ['__.SYMDEF', 'main.o']
        check_files(test_dir, expected)
        assert [] == result

    def test_extract_ar_broken_libarchive(self):
        test_file = self.get_test_loc('archive/ar/liby-corrupted.a')
        test_dir = self.get_temp_dir()
        self.assertRaisesInstance(
            Exception('Incorrect file header signature'),
            libarchive2.extract, test_file, test_dir)
        expected = ['__.SYMDEF', 'main.o']
        check_files(test_dir, expected)

    def test_extract_ar_broken(self):
        test_file = self.get_test_loc('archive/ar/liby-corrupted.a')
        test_dir = self.get_temp_dir()
        result = archive.extract_ar(test_file, test_dir)
        expected = ['__.SYMDEF', 'main.o']
        check_files(test_dir, expected)
        assert [] == result

    def test_extract_ar_with_invalid_path(self):
        test_file = self.get_test_loc('archive/ar/ar_invalidpath.ar')
        test_dir = self.get_temp_dir()
        result = archive.extract_ar(test_file, test_dir)
        expected = ['this/that']
        check_files(test_dir, expected)
        assert [] == result

    def test_extract_ar_with_relative_path_sevenzip(self):
        test_file = self.get_test_loc('archive/ar/winlib/htmlhelp.lib')
        test_dir = self.get_temp_dir()
        result = sevenzip.extract(test_file, test_dir)
        expected = [
            '1.txt',
            '2.txt',
            'release/init.obj'
        ]
        check_files(test_dir, expected)
        assert [] == result

    def test_extract_ar_with_relative_path_libarch(self):
        test_file = self.get_test_loc('archive/ar/winlib/htmlhelp.lib')
        test_dir = self.get_temp_dir()
        self.assertRaisesInstance(
            Exception('Invalid string table'),
            archive.libarchive2.extract, test_file, test_dir)

        # inccorrect for now: need this: ['__.SYMDEF', 'release/init.obj']
        expected = ['dot', 'dot_1']
        check_files(test_dir, expected)

    def test_extract_ar_with_relative_path_and_backslashes_in_names_libarch(self):
        test_file = self.get_test_loc('archive/ar/winlib/freetype.lib')
        test_dir = self.get_temp_dir()
        self.assertRaisesInstance(
            Exception('Invalid string table'),
            archive.libarchive2.extract, test_file, test_dir)
        # 7zip is better, but has a security bug for now
        # GNU ar works fine otherwise, but there are portability issues
        expected = ['dot', 'dot_1']

        if on_linux and py2:
            expected = [bytes(e) for e in expected]

        check_files(test_dir, expected)

    def test_extract_ar_with_relative_path_and_backslashes_in_names_7z(self):
        test_file = self.get_test_loc('archive/ar/winlib/freetype.lib')
        test_dir = self.get_temp_dir()
        result = sevenzip.extract(test_file, test_dir)
        assert [] == result
        expected = [
            '1.txt',
            '2.txt',
            'objs/debug_mt/autofit.obj',
            'objs/debug_mt/bdf.obj',
            'objs/debug_mt/cff.obj',
            'objs/debug_mt/ftbase.obj',
            'objs/debug_mt/ftbbox.obj',
            'objs/debug_mt/ftbitmap.obj',
            'objs/debug_mt/ftcache.obj',
            'objs/debug_mt/ftdebug.obj',
            'objs/debug_mt/ftgasp.obj',
            'objs/debug_mt/ftglyph.obj',
            'objs/debug_mt/ftgzip.obj',
            'objs/debug_mt/ftinit.obj',
            'objs/debug_mt/ftlzw.obj',
            'objs/debug_mt/ftmm.obj',
            'objs/debug_mt/ftpfr.obj',
            'objs/debug_mt/ftstroke.obj',
            'objs/debug_mt/ftsynth.obj',
            'objs/debug_mt/ftsystem.obj',
            'objs/debug_mt/fttype1.obj',
            'objs/debug_mt/ftwinfnt.obj',
            'objs/debug_mt/pcf.obj',
            'objs/debug_mt/pfr.obj',
            'objs/debug_mt/psaux.obj',
            'objs/debug_mt/pshinter.obj',
            'objs/debug_mt/psmodule.obj',
            'objs/debug_mt/raster.obj',
            'objs/debug_mt/sfnt.obj',
            'objs/debug_mt/smooth.obj',
            'objs/debug_mt/truetype.obj',
            'objs/debug_mt/type1.obj',
            'objs/debug_mt/type1cid.obj',
            'objs/debug_mt/type42.obj',
            'objs/debug_mt/winfnt.obj'
        ]
        check_files(test_dir, expected)

    def test_extract_ar_static_library_does_not_delete_symdefs_7z(self):
        test_file = self.get_test_loc('archive/ar/liby.a')
        test_dir = self.get_temp_dir()
        result = sevenzip.extract(test_file, test_dir)
        # the symdef file is 1.txt with 7z
        expected = ['1.txt', 'main.o', 'yyerror.o']
        check_files(test_dir, expected)
        assert [] == result

    def test_extract_ar_static_library_does_not_delete_symdefs(self):
        test_file = self.get_test_loc('archive/ar/liby.a')
        test_dir = self.get_temp_dir()
        result = archive.extract_ar(test_file, test_dir)
        # we use libarchive first
        expected = ['__.SYMDEF', 'main.o', 'yyerror.o']
        check_files(test_dir, expected)
        assert [] == result

    def test_extract_ar_with_trailing_data(self):
        test_file = self.get_test_loc('archive/ar/ar_trailing.a')
        test_dir = self.get_temp_dir()
        archive.extract_ar(test_file, test_dir)
        result = os.path.join(test_dir, 'main.o')
        assert os.path.exists(result)
        result = os.path.join(test_dir, 'yyerror.o')
        assert os.path.exists(result)

    def test_extract_ar_with_permissions_7z(self):
        test_file = self.get_test_loc('archive/ar/winlib/zlib.lib')
        test_dir = self.get_temp_dir()
        result = sevenzip.extract(test_file, test_dir)
        expected = ['1.txt', '1.zlib.pyd', '2.txt', '2.zlib.pyd', '3.zlib.pyd', '4.zlib.pyd']
        check_files(test_dir, expected)
        assert [] == result

    def test_extract_ar_with_permissions(self):
        test_file = self.get_test_loc('archive/ar/winlib/zlib.lib')
        test_dir = self.get_temp_dir()
        result = archive.extract_ar(test_file, test_dir)
        # with 7zip
        # expected = ['1.txt', '1.zlib.pyd', '2.txt', '2.zlib.pyd', '3.zlib.pyd', '4.zlib.pyd']
        # with libarchive
        expected = ['dot', 'dot_1', 'zlib.pyd', 'zlib_1.pyd', 'zlib_2.pyd', 'zlib_3.pyd']
        check_files(test_dir, expected)
        assert [] == result

    def test_extract_ar_with_permissions_libarchive(self):
        test_file = self.get_test_loc('archive/ar/winlib/zlib.lib')
        test_dir = self.get_temp_dir()
        result = libarchive2.extract(test_file, test_dir)
        assert [] == result
        expected = ['dot', 'dot_1', 'zlib.pyd', 'zlib_1.pyd', 'zlib_2.pyd', 'zlib_3.pyd']
        check_files(test_dir, expected)


class TestCpio(BaseArchiveTestCase):

    def test_extract_cpio_basic(self):
        test_file = self.get_test_loc('archive/cpio/elfinfo-1.0-1.fc9.src.cpio')
        test_dir = self.get_temp_dir()
        archive.extract_cpio(test_file, test_dir)
        result = os.path.join(test_dir, 'elfinfo-1.0.tar.gz')
        assert os.path.exists(result)

    def test_extract_cpio_with_trailing_data(self):
        test_file = self.get_test_loc('archive/cpio/cpio_trailing.cpio')
        test_dir = self.get_temp_dir()
        archive.extract_cpio(test_file, test_dir)
        result = os.path.join(test_dir, 'elfinfo-1.0.tar.gz')
        assert os.path.exists(result)

    def test_extract_cpio_broken_7z(self):
        test_file = self.get_test_loc('archive/cpio/cpio_broken.cpio')
        test_dir = self.get_temp_dir()
        self.assertRaisesInstance(Exception('CRC Failed : elfinfo-1.0.tar'), sevenzip.extract, test_file, test_dir)

    def test_extract_cpio_broken2(self):
        test_file = self.get_test_loc('archive/cpio/cpio_broken.cpio')
        test_dir = self.get_temp_dir()
        result = archive.extract_cpio(test_file, test_dir)
        expected = sorted(['elfinfo-1.0.tar.gz', 'elfinfo.spec'])
        if on_linux and py2:
            expected = [e.encode('utf-8')  for e in expected]

        assert expected == sorted(os.listdir(test_dir))
        assert ["'elfinfo.spec': \nSkipped 72 bytes before finding valid header"] == result

    def test_extract_cpio_with_absolute_path(self):
        assert not os.path.exists('/tmp/subdir')
        test_dir = self.get_temp_dir()
        test_file = self.get_test_loc('archive/cpio/cpio_absolute.cpio')
        archive.extract_cpio(test_file, test_dir)
        assert not os.path.exists('/tmp/subdir')
        result = os.path.join(test_dir, 'home/li/Desktop/absolute_folder/absolute_file')
        assert os.path.exists(result)

    def test_extract_cpio_with_relative_path(self):
        # test file is created by cmd: find ../.. - |cpio -ov >relative.cpio
        # We should somehow add a "parent" folder to extract relative paths
        test_file = self.get_test_loc('archive/cpio/cpio_relative.cpio')
        test_dir = self.get_temp_dir()
        result = archive.extract_cpio(test_file, test_dir)
        assert [] == result
        extracted = self.collect_extracted_path(test_dir)
        expected = [
            '/dotdot/',
            '/dotdot/dotdot/',
            '/dotdot/dotdot/2folder/',
            '/dotdot/dotdot/2folder/3folder/',
            '/dotdot/dotdot/2folder/3folder/cpio_relative.cpio',
            '/dotdot/dotdot/2folder/3folder/relative_file',
            '/dotdot/dotdot/2folder/3folder/relative_file~',
            '/dotdot/dotdot/2folder/relative_file',
            '/dotdot/dotdot/relative_file'
        ]
        assert expected == extracted

    def test_extract_cpio_with_invalidpath(self):
        test_file = self.get_test_loc('archive/cpio/cpio-invalidpath.cpio')
        test_dir = self.get_temp_dir()
        archive.extract_cpio(test_file, test_dir)

        result = os.path.join(test_dir, 'backup')
        assert os.path.exists(result)

        result = os.path.join(test_dir, 'this/that')
        assert os.path.exists(result)

    def test_extract_cpio_with_weird_filename_extension(self):
        test_file = self.get_test_loc('archive/cpio/t.cpio.foo')
        test_dir = self.get_temp_dir()
        result = archive.extract_cpio(test_file, test_dir)
        assert [] == result
        extracted = self.collect_extracted_path(test_dir)
        expected = ['/t/', '/t/t.txt']
        assert expected == extracted


class TestRpm(BaseArchiveTestCase):

    def test_extract_rpm_basic_1(self):
        test_file = self.get_test_loc('archive/rpm/elfinfo-1.0-1.fc9.src.rpm')
        test_dir = self.get_temp_dir()
        archive.extract_rpm(test_file, test_dir)
        result = os.path.join(test_dir, 'elfinfo-1.0-1.fc9.src.cpio.gz')
        assert os.path.exists(result)

    def test_extract_rpm_basic_2(self):
        test_file = self.get_test_loc('archive/rpm/python-glc-0.7.1-1.src.rpm')
        test_dir = self.get_temp_dir()
        archive.extract_rpm(test_file, test_dir)
        result = os.path.join(test_dir, 'python-glc-0.7.1-1.src.cpio.gz')
        assert os.path.exists(result)

    def test_extract_rpm_nested_correctly(self):
        test_file = self.get_test_loc('archive/rpm/extract_once/libsqueeze0.2_0-0.2.3-8mdv2010.0.i586.rpm')
        test_dir = self.get_temp_dir()
        archive.extract_rpm(test_file, test_dir)
        result = os.path.join(test_dir, 'libsqueeze0.2_0-0.2.3-8mdv2010.0.i586.cpio.lzma')
        assert os.path.exists(result)

    def test_extract_rpm_with_trailing_data(self):
        test_file = self.get_test_loc('archive/rpm/rpm_trailing.rpm')
        test_dir = self.get_temp_dir()
        result = archive.extract_rpm(test_file, test_dir)
        expected = ['elfinfo-1.0-1.fc9.src.cpio.gz']
        check_files(test_dir, expected)
        assert [] == result

    def test_extract_rpm_with_renamed_content(self):
        # When the RPM is renamed, we should still be able to find the cpio
        test_file = self.get_test_loc('archive/rpm/renamed.rpm')
        test_dir = self.get_temp_dir()
        result = archive.extract_rpm(test_file, test_dir)
        expected = ['python-glc-0.7.1-1.src.cpio.gz']
        check_files(test_dir, expected)
        assert [] == result

    def test_extract_rpm_broken(self):
        test_file = self.get_test_loc('archive/rpm/broken.rpm')
        test_dir = self.get_temp_dir()
        expected = Exception('CRC Failed : broken')
        self.assertRaisesInstance(expected, archive.extract_rpm,
                                  test_file, test_dir)


class TestExtractTwice(BaseArchiveTestCase):

    def test_extract_twice_with_rpm_with_xz_compressed_cpio(self):
        test_file = self.get_test_loc('archive/rpm/xz-compressed-cpio.rpm')
        test_dir = self.get_temp_dir()
        # this will return an extractor that extracts twice
        extractor = archive.get_extractor(test_file)
        result = list(extractor(test_file, test_dir))
        assert [] == result
        expected = [
            'etc/abrt/abrt-action-save-package-data.conf',
            'etc/abrt/abrt.conf',
            'etc/abrt/gpg_keys',
            'etc/dbus-1/system.d/dbus-abrt.conf',
            'etc/libreport/events.d/abrt_event.conf',
            'etc/libreport/events.d/smart_event.conf',
            'etc/rc.d/init.d/abrtd',
            'usr/bin/abrt-action-save-package-data',
            'usr/bin/abrt-handle-upload',
            'usr/libexec/abrt-handle-event',
            'usr/libexec/abrt1-to-abrt2',
            'usr/sbin/abrt-dbus',
            'usr/sbin/abrt-server',
            'usr/sbin/abrtd',
            'usr/share/dbus-1/system-services/com.redhat.abrt.service',
            'usr/share/doc/abrt-2.0.8/COPYING',
            'usr/share/doc/abrt-2.0.8/README',
            'usr/share/locale/ar/LC_MESSAGES/abrt.mo',
            'usr/share/locale/as/LC_MESSAGES/abrt.mo',
            'usr/share/locale/ast/LC_MESSAGES/abrt.mo',
            'usr/share/locale/bg/LC_MESSAGES/abrt.mo',
            'usr/share/locale/bn_IN/LC_MESSAGES/abrt.mo',
            'usr/share/locale/ca/LC_MESSAGES/abrt.mo',
            'usr/share/locale/cs/LC_MESSAGES/abrt.mo',
            'usr/share/locale/da/LC_MESSAGES/abrt.mo',
            'usr/share/locale/de/LC_MESSAGES/abrt.mo',
            'usr/share/locale/el/LC_MESSAGES/abrt.mo',
            'usr/share/locale/en_GB/LC_MESSAGES/abrt.mo',
            'usr/share/locale/es/LC_MESSAGES/abrt.mo',
            'usr/share/locale/fa/LC_MESSAGES/abrt.mo',
            'usr/share/locale/fi/LC_MESSAGES/abrt.mo',
            'usr/share/locale/fr/LC_MESSAGES/abrt.mo',
            'usr/share/locale/gu/LC_MESSAGES/abrt.mo',
            'usr/share/locale/he/LC_MESSAGES/abrt.mo',
            'usr/share/locale/hi/LC_MESSAGES/abrt.mo',
            'usr/share/locale/hu/LC_MESSAGES/abrt.mo',
            'usr/share/locale/id/LC_MESSAGES/abrt.mo',
            'usr/share/locale/it/LC_MESSAGES/abrt.mo',
            'usr/share/locale/ja/LC_MESSAGES/abrt.mo',
            'usr/share/locale/kn/LC_MESSAGES/abrt.mo',
            'usr/share/locale/ko/LC_MESSAGES/abrt.mo',
            'usr/share/locale/ml/LC_MESSAGES/abrt.mo',
            'usr/share/locale/mr/LC_MESSAGES/abrt.mo',
            'usr/share/locale/nb/LC_MESSAGES/abrt.mo',
            'usr/share/locale/nl/LC_MESSAGES/abrt.mo',
            'usr/share/locale/or/LC_MESSAGES/abrt.mo',
            'usr/share/locale/pa/LC_MESSAGES/abrt.mo',
            'usr/share/locale/pl/LC_MESSAGES/abrt.mo',
            'usr/share/locale/pt/LC_MESSAGES/abrt.mo',
            'usr/share/locale/pt_BR/LC_MESSAGES/abrt.mo',
            'usr/share/locale/ru/LC_MESSAGES/abrt.mo',
            'usr/share/locale/sk/LC_MESSAGES/abrt.mo',
            'usr/share/locale/sr/LC_MESSAGES/abrt.mo',
            'usr/share/locale/sr@latin/LC_MESSAGES/abrt.mo',
            'usr/share/locale/sv/LC_MESSAGES/abrt.mo',
            'usr/share/locale/ta/LC_MESSAGES/abrt.mo',
            'usr/share/locale/te/LC_MESSAGES/abrt.mo',
            'usr/share/locale/uk/LC_MESSAGES/abrt.mo',
            'usr/share/locale/zh_CN/LC_MESSAGES/abrt.mo',
            'usr/share/locale/zh_TW/LC_MESSAGES/abrt.mo',
            'usr/share/man/man1/abrt-action-save-package-data.1.gz',
            'usr/share/man/man1/abrt-handle-upload.1.gz',
            'usr/share/man/man1/abrt-server.1.gz',
            'usr/share/man/man5/abrt-action-save-package-data.conf.5.gz',
            'usr/share/man/man5/abrt.conf.5.gz',
            'usr/share/man/man8/abrt-dbus.8.gz',
            'usr/share/man/man8/abrtd.8.gz'
        ]
        check_files(test_dir, expected)

    def test_extract_twice_can_extract_to_relative_paths(self):
        # The setup is a tad complex because we want to have a relative dir
        # to the base dir where we run tests from, ie the scancode-toolkit/ dir
        # To use relative paths, we use our tmp dir at the root of the code tree
        from os.path import dirname, join, abspath, exists
        import shutil
        import tempfile

        test_file = self.get_test_loc('archive/rpm/xz-compressed-cpio.rpm')
        # this will return an extractor that extracts twice
        extractor = archive.get_extractor(test_file)

        scancode_root = dirname(dirname(dirname(__file__)))
        scancode_tmp = join(scancode_root, 'tmp')
        fileutils.create_dir(scancode_tmp)
        scancode_root_abs = abspath(scancode_root)
        test_src_dir = tempfile.mkdtemp(dir=scancode_tmp).replace(scancode_root_abs, '').strip('\\/')
        test_tgt_dir = tempfile.mkdtemp(dir=scancode_tmp).replace(scancode_root_abs, '').strip('\\/')
        shutil.copy(test_file, test_src_dir)
        test_src_file = join(test_src_dir, 'xz-compressed-cpio.rpm')

        result = list(extractor(test_src_file, test_tgt_dir))
        assert [] == result
        assert exists(join(test_tgt_dir, 'usr/sbin/abrt-dbus'))


class TestRar(BaseArchiveTestCase):

    def test_extract_rar_basic(self):
        test_file = self.get_test_loc('archive/rar/basic.rar')
        test_dir = self.get_temp_dir()
        archive.extract_rar(test_file, test_dir)
        result = os.path.join(test_dir, 'd', 'b', 'a.txt')
        assert os.path.exists(result)

    def test_extract_rar_with_invalid_path(self):
        test_file = self.get_test_loc('archive/rar/rar_invalidpath.rar')
        test_dir = self.get_temp_dir()
        archive.extract_rar(test_file, test_dir)
        result = os.path.join(test_dir, 'this/that')
        assert os.path.exists(result)

    def test_extract_rar_with_trailing_data(self):
        test_file = self.get_test_loc('archive/rar/rar_trailing.rar')
        test_dir = self.get_temp_dir()
        expected = Exception('Unknown error')
        self.assertRaisesInstance(expected, archive.extract_rar, test_file, test_dir)
        result = os.path.join(test_dir, 'd', 'b', 'a.txt')
        assert os.path.exists(result)

    def test_extract_rar_broken(self):
        test_file = self.get_test_loc('archive/rar/broken.rar')
        test_dir = self.get_temp_dir()
        expected = Exception('Header CRC error')
        self.assertRaisesInstance(expected, archive.extract_rar, test_file, test_dir)

    def test_extract_rar_with_relative_path(self):
        # FIXME: this file may not have a real relative path
        test_file = self.get_test_loc('archive/rar/rar_relative.rar', copy=True)
        test_dir = self.get_temp_dir()
        archive.extract_rar(test_file, test_dir)
        result = os.path.abspath(test_file + '/../a_parent_folder.txt')
        assert not os.path.exists(result)

        result = os.path.join(test_dir, '2folder/relative_file')
        assert os.path.exists(result)

        result = os.path.join(test_dir, '2folder/3folder/relative_file')
        assert os.path.exists(result)

    def test_extract_rar_with_absolute_path(self):
        # FIXME: this file may not have a real absolute path
        assert not os.path.exists('/home/li/Desktop/zip_folder')
        test_file = self.get_test_loc('archive/rar/rar_absolute.rar', copy=True)
        test_dir = self.get_temp_dir()
        archive.extract_rar(test_file, test_dir)
        assert not os.path.exists('/home/li/Desktop/absolute_folder')
        result = os.path.join(test_dir, 'home/li/Desktop',
                                'absolute_folder/absolute_file')
        assert os.path.exists(result)

    def test_extract_rar_with_password(self):
        test_file = self.get_test_loc('archive/rar/rar_password.rar')
        test_dir = self.get_temp_dir()
        expected = Exception('Prefix found')
        self.assertRaisesInstance(expected, archive.extract_rar,
                                  test_file, test_dir)

    def test_extract_rar_with_non_ascii_path(self):
        test_file = self.get_test_loc('archive/rar/non_ascii_corrupted.rar')
        # The bug only occurs if the path was given as Unicode
        test_file = compat.unicode(test_file)
        test_dir = self.get_temp_dir()
        # raise an exception but still extracts some
        expected = Exception('Prefix found')
        self.assertRaisesInstance(expected, archive.extract_rar, test_file, test_dir)
        result = os.path.join(test_dir, 'EdoProject_java/WebContent/WEB-INF/lib/cos.jar')
        assert os.path.exists(result)


class TestSevenZip(BaseArchiveTestCase):

    def test_extract_7z_basic(self):
        test_file = self.get_test_loc('archive/7z/z.7z')
        test_dir = self.get_temp_dir()
        result = archive.extract_7z(test_file, test_dir)
        assert [] == result
        expected = ['z/a/a.txt', 'z/b/a.txt', 'z/c/a.txt']
        check_files(test_dir, expected)

    def test_extract_7z_with_trailing_data(self):
        test_file = self.get_test_loc('archive/7z/7zip_trailing.7z')
        test_dir = self.get_temp_dir()
        result = archive.extract_7z(test_file, test_dir)
        assert [] == result
        expected = ['z/a/a.txt', 'z/b/a.txt', 'z/c/a.txt']
        check_files(test_dir, expected)

    def test_extract_7z_with_broken_archive_with7z(self):
        test_file = self.get_test_loc('archive/7z/corrupted7z.7z')
        test_dir = self.get_temp_dir()
        msg = 'There are data after the end of archive'
        self.assertExceptionContains(msg, sevenzip.extract, test_file, test_dir)

    def test_extract_7z_with_broken_archive_does_not_fail_when_using_fallback(self):
        test_file = self.get_test_loc('archive/7z/corrupted7z.7z')
        test_dir = self.get_temp_dir()
        msg = 'There are data after the end of archive'
        self.assertExceptionContains(msg, archive.extract_7z, test_file, test_dir)

    def test_extract_7z_with_non_existing_archive(self):
        test_file = 'archive/7z/I_DO_NOT_EXIST.zip'
        test_dir = self.get_temp_dir()
        msg = 'The system cannot find the path specified'
        self.assertExceptionContains(msg, sevenzip.extract, test_file, test_dir)

    def test_extract_7z_with_invalid_path_using_7z(self):
        test_file = self.get_test_loc('archive/7z/7zip_invalidpath.7z')
        test_dir = self.get_temp_dir()
        result = sevenzip.extract(test_file, test_dir)
        assert [] == result
        extracted = self.collect_extracted_path(test_dir)
        expected = ['/this/', '/this/that']
        assert expected == extracted

    def test_extract_7z_with_invalid_path(self):
        test_file = self.get_test_loc('archive/7z/7zip_invalidpath.7z')
        test_dir = self.get_temp_dir()
        result = archive.extract_7z(test_file, test_dir)
        assert [] == result
        extracted = self.collect_extracted_path(test_dir)
        expected = ['/this/', '/this/that']
        assert expected == extracted

    def test_extract_7z_with_relative_path(self):
        test_file = self.get_test_loc('archive/7z/7zip_relative.7z')
        test_dir = self.get_temp_dir()
        result = archive.extract_7z(test_file, test_dir)
        non_result = os.path.join(test_dir, '../a_parent_folder.txt')
        assert not os.path.exists(non_result)
        assert [] == result
        extracted = self.collect_extracted_path(test_dir)
        expected = [
            '/dotdot/',
            '/dotdot/2folder/',
            '/dotdot/2folder/3folder/',
            '/dotdot/2folder/3folder/relative_file',
            '/dotdot/2folder/3folder/relative_file~',
            '/dotdot/2folder/relative_file',
            '/dotdot/relative_file'
        ]
        assert expected == extracted

    def test_extract_7z_with_password_with_7z(self):
        test_file = self.get_test_loc('archive/7z/7zip_password.7z')
        test_dir = self.get_temp_dir()
        expected = Exception('Password protected archive, unable to extract')
        self.assertRaisesInstance(expected, sevenzip.extract, test_file, test_dir)

    def test_extract_7z_with_password(self):
        test_file = self.get_test_loc('archive/7z/7zip_password.7z')
        test_dir = self.get_temp_dir()
        expected = Exception('Password protected archive, unable to extract')
        self.assertRaisesInstance(expected, archive.extract_7z, test_file, test_dir)

    def test_extract_7zip_native_with_unicode_path_should_extract_without_error(self):
        test_file = self.get_test_loc('archive/7z/7zip_unicode.7z')
        test_dir = self.get_temp_dir()
        result = sevenzip.extract(test_file, test_dir)
        assert [] == result
        assert 2 == len(os.listdir(os.path.join(test_dir, 'zip')))

    def test_extract_7zip_with_fallback_with_unicode_path_should_extract_without_error(self):
        test_file = self.get_test_loc('archive/7z/7zip_unicode.7z')
        test_dir = self.get_temp_dir()
        result = archive.extract_7z(test_file, test_dir)
        assert [] == result
        assert 2 == len(os.listdir(os.path.join(test_dir, 'zip')))

    def test_extract_7zip_extract_with_unicode_path_extracts_with_errors(self):
        test_file = self.get_test_loc('archive/7z/7zip_unicode.7z')
        test_dir = self.get_temp_dir()
        try:
            archive.extract_7z(test_file, test_dir)
        except libarchive2.ArchiveError as e:
            assert 'Damaged 7-Zip archive' in e.msg

    def test_extract_7z_basic_with_space_in_file_name(self):
        test_file = self.get_test_loc('archive/7z/t .7z')
        test_dir = self.get_temp_dir()
        result = archive.extract_7z(test_file, test_dir)
        assert [] == result
        expected = ['t/t.txt']
        check_files(test_dir, expected)


class TestIso(BaseArchiveTestCase):

    def test_extract_iso_basic(self):
        test_file = self.get_test_loc('archive/iso/small.iso')
        test_dir = self.get_temp_dir()
        archive.extract_iso(test_file, test_dir)
        extracted = self.collect_extracted_path(test_dir)
        expected = [
            '/ChangeLog',
            '/ChangeLog (copy)',
            '/freebase.ABOUT',
            '/this/',
            '/this/that'
        ]
        assert sorted(expected) == sorted(extracted)

    def test_get_extractor_not_iso_text_is_not_mistaken_for_an_iso_image(self):
        test_file = self.get_test_loc('archive/iso/ChangeLog')
        extractor = archive.get_extractor(test_file)
        assert not extractor

    def test_extract_iso_basic_with_with_weird_filename_extension(self):
        test_file = self.get_test_loc('archive/iso/t.iso.foo')
        test_dir = self.get_temp_dir()
        archive.extract_iso(test_file, test_dir)
        extracted = self.collect_extracted_path(test_dir)
        expected = ['/t/', '/t/t.txt']
        assert expected == extracted


class TestXzLzma(BaseArchiveTestCase):

    def check_lzma_extract(self, extract_fun, test_file, expected):
        test_file = self.get_test_loc(test_file)
        extract_dir = self.get_temp_dir()
        expected_file = os.path.join(extract_dir, expected)
        extract_fun(test_file, extract_dir)
        assert  os.path.exists(expected_file), (
                        '%(expected_file)s file was not extracted '
                        'correctly from archive %(test_file)s'
                        % locals())

    def test_extract_archive_tar_xz_1(self):
        test_file = 'archive/lzma_xz/texlive-core-patches-20.tar.xz'
        self.check_lzma_extract(extract_fun=archive.extract_lzma,
                                test_file=test_file,
                                expected='texlive-core-patches-20.tar')

    def test_extract_archive_tar_xz_2(self):
        test_file = 'archive/lzma_xz/texlive-core-patches-20.tar.xz'
        self.check_lzma_extract(extract_fun=archive.extract_lzma,
                                test_file=test_file,
                                expected='texlive-core-patches-20.tar')

    def test_extract_archive_tar_lzma_1(self):
        test_file = 'archive/lzma_xz/coreutils-8.5-patches-1.tar.lzma'
        self.check_lzma_extract(extract_fun=archive.extract_lzma,
                                test_file=test_file,
                                expected='coreutils-8.5-patches-1.tar')

    def test_extract_archive_tar_lzma_2(self):
        test_file = 'archive/lzma_xz/orionsocket-1.0.9.tar.lzma'
        self.check_lzma_extract(extract_fun=archive.extract_lzma,
                        test_file=test_file,
                        expected='orionsocket-1.0.9.tar')

    def test_extract_archive_tar_lzma_3(self):
        test_file = 'archive/lzma_xz/MinGW-5.1.6.exe-src.tar.lzma'
        expected = 'MinGW-5.1.6.exe-src.tar'
        self.check_lzma_extract(extract_fun=archive.extract_lzma,
                        test_file=test_file,
                        expected=expected)


class TestDia(BaseArchiveTestCase):

    def test_extract_dia_basic(self):
        test_file = self.get_test_loc('archive/dia/dia.dia')
        test_dir = self.get_temp_dir()
        archive.uncompress_gzip(test_file, test_dir)
        result = os.path.join(test_dir, 'dia.dia-extract')
        assert os.path.exists(result)

    @pytest.mark.skipif(py3, reason='Fails for now on Python 3')
    def test_extract_dia_with_trailing_data_py2(self):
        test_file = self.get_test_loc('archive/dia/dia_trailing.dia')
        test_dir = self.get_temp_dir()
        archive.uncompress_gzip(test_file, test_dir)
        result = os.path.join(test_dir, 'dia_trailing.dia-extract')
        assert os.path.exists(result)

    @pytest.mark.xfail
    @pytest.mark.skipif(py2, reason='Fails for now on Python 3')
    def test_extract_dia_with_trailing_data_py3(self):
        test_file = self.get_test_loc('archive/dia/dia_trailing.dia')
        test_dir = self.get_temp_dir()
        archive.uncompress_gzip(test_file, test_dir)
        result = os.path.join(test_dir, 'dia_trailing.dia-extract')
        assert os.path.exists(result)

    def test_extract_dia_broken_1(self):
        test_file = self.get_test_loc('archive/dia/dia_broken.dia')
        test_dir = self.get_temp_dir()
        self.assertExceptionContains('CRC check failed',
            archive.uncompress_gzip, test_file, test_dir)

    def test_extract_dia_broken_2(self):
        test_file = self.get_test_loc('archive/dia/broken/PublisherUML.dia')
        test_dir = self.get_temp_dir()
        self.assertExceptionContains('invalid distance too far back',
            archive.uncompress_gzip, test_file, test_dir)

    def test_extract_dia_broken_3(self):
        test_file = self.get_test_loc('archive/dia/broken/schedulerClassDiagram.dia')
        test_dir = self.get_temp_dir()
        self.assertExceptionContains('invalid distance too far back',
            archive.uncompress_gzip, test_file, test_dir)

    def test_extract_dia_broken_4(self):
        test_file = self.get_test_loc('archive/dia/broken/ServletProxyGenerator.dia')
        test_dir = self.get_temp_dir()
        self.assertExceptionContains('invalid distance too far back',
            archive.uncompress_gzip, test_file, test_dir)

    def test_extract_can_get_extractor_and_uncompress_dia_files(self):
        test_file = self.get_test_loc('archive/dia/guess/infoset-doc.dia')
        test_dir = self.get_temp_dir()
        ext = archive.get_extractor(test_file)
        ext(test_file, test_dir)
        result = os.path.join(test_dir, 'infoset-doc.dia-extract')
        assert os.path.exists(result)


class TestTarZ(BaseArchiveTestCase):

    def test_extract_tarz_compress_basic(self):
        test_file = self.get_test_loc('archive/Z/tkWWW-0.11.tar.Z')
        test_dir = self.get_temp_dir()
        archive.extract_Z(test_file, test_dir)
        result = os.path.join(test_dir, 'tkWWW-0.11.tar')
        assert os.path.exists(result)

    def test_extract_z_compress_basic(self):
        test_file = self.get_test_loc('archive/Z/tr2tex.Z')
        test_dir = self.get_temp_dir()
        archive.extract_Z(test_file, test_dir)
        result = os.path.join(test_dir, 'tr2tex')
        assert os.path.exists(result)


class TestXar(BaseArchiveTestCase):

    def test_extract_xar_basic(self):
        test_file = self.get_test_loc('archive/xar/xar-1.4.xar')
        test_dir = self.get_temp_dir()
        archive.extract_Z(test_file, test_dir)
        result = os.path.join(test_dir, '[TOC].xml')
        assert os.path.exists(result)
        result = os.path.join(test_dir, 'xar-1.4', 'Makefile.in')
        assert os.path.exists(result)


class TestCb7(BaseArchiveTestCase):

    def test_get_extractor_cb7(self):
        test_file = self.get_test_loc('archive/cb7/t .cb7')
        result = archive.get_extractor(test_file)
        expected = archive.extract_7z
        assert expected == result

    def test_extract_cb7_basic_with_space_in_file_name(self):
        test_file = self.get_test_loc('archive/cb7/t .cb7')
        test_dir = self.get_temp_dir()
        archive.extract_7z(test_file, test_dir)
        extracted = self.collect_extracted_path(test_dir)
        expected = ['/t/', '/t/t.txt']
        assert expected == extracted

    def test_extract_cb7_basic_with_weird_filename_extension(self):
        test_file = self.get_test_loc('archive/cb7/t.cb7.foo')
        test_dir = self.get_temp_dir()
        archive.extract_7z(test_file, test_dir)
        extracted = self.collect_extracted_path(test_dir)
        expected = ['/t/', '/t/t.txt']
        assert expected == extracted


class TestCab(BaseArchiveTestCase):

    def test_get_extractor_cab(self):
        test_file = self.get_test_loc('archive/cab/basic.cab')
        result = archive.get_extractor(test_file)
        expected = archive.extract_cab
        assert expected == result

    def test_extract_cab_basic(self):
        test_file = self.get_test_loc('archive/cab/basic.cab')
        test_dir = self.get_temp_dir()
        archive.extract_cab(test_file, test_dir)
        extracted = self.collect_extracted_path(test_dir)
        expected = ['/TREEHELP.TXT']
        assert expected == extracted

    def test_extract_cab_basic_with_weird_filename_extension(self):
        test_file = self.get_test_loc('archive/cab/t.cab.foo')
        test_dir = self.get_temp_dir()
        archive.extract_cab(test_file, test_dir)
        extracted = self.collect_extracted_path(test_dir)
        expected = ['/t/', '/t/t.txt']
        assert expected == extracted


class TestCbr(BaseArchiveTestCase):

    def test_get_extractor_cbr(self):
        test_file = self.get_test_loc('archive/cbr/t.cbr')
        result = archive.get_extractor(test_file)
        # FIXME: we do not handle these rare extensions (this is a RAR)
        expected = None  # archive.extract_rar
        assert expected == result

    def test_extract_cbr_basic(self):
        test_file = self.get_test_loc('archive/cbr/t.cbr')
        test_dir = self.get_temp_dir()
        libarchive2.extract(test_file, test_dir)
        extracted = self.collect_extracted_path(test_dir)
        expected = ['/t/', '/t/t.txt']
        assert expected == extracted

    def test_extract_cbr_basic_with_weird_filename_extension(self):
        test_file = self.get_test_loc('archive/cbr/t.cbr.foo')
        test_dir = self.get_temp_dir()
        libarchive2.extract(test_file, test_dir)
        extracted = self.collect_extracted_path(test_dir)
        expected = ['/t/', '/t/t.txt']
        assert expected == extracted


class TestCbt(BaseArchiveTestCase):

    def test_get_extractor_cbt(self):
        test_file = self.get_test_loc('archive/cbt/t.cbt')
        result = archive.get_extractor(test_file)
        expected = archive.extract_tar
        assert expected == result

    def test_extract_cbt_basic(self):
        test_file = self.get_test_loc('archive/cbt/t.cbt')
        test_dir = self.get_temp_dir()
        archive.extract_tar(test_file, test_dir)
        extracted = self.collect_extracted_path(test_dir)
        expected = ['/t/', '/t/t.txt']
        assert expected == extracted

    def test_extract_cbt_basic_with_weird_filename_extension(self):
        test_file = self.get_test_loc('archive/cbt/t.cbt.foo')
        test_dir = self.get_temp_dir()
        archive.extract_tar(test_file, test_dir)
        extracted = self.collect_extracted_path(test_dir)
        expected = ['/t/', '/t/t.txt']
        assert expected == extracted


class TestCbz(BaseArchiveTestCase):

    def test_get_extractor_cbz(self):
        test_file = self.get_test_loc('archive/cbz/t.cbz', copy=True)
        result = archive.get_extractor(test_file)
        expected = archive.extract_zip
        assert expected == result

    def test_extract_cbz_basic(self):
        test_file = self.get_test_loc('archive/cbz/t.cbz')
        test_dir = self.get_temp_dir()
        archive.extract_zip(test_file, test_dir)
        extracted = self.collect_extracted_path(test_dir)
        expected = ['/t/', '/t/t.txt']
        assert expected == extracted

    def test_extract_cbz_basic_with_weird_filename_extension(self):
        test_file = self.get_test_loc('archive/cbz/t.cbz.foo')
        test_dir = self.get_temp_dir()
        archive.extract_zip(test_file, test_dir)
        extracted = self.collect_extracted_path(test_dir)
        expected = ['/t/', '/t/t.txt']
        assert expected == extracted


class TestLzip(BaseArchiveTestCase):

    pytestmark = pytest.mark.skipif(on_windows, reason='FIXME: lzip does not work on Windows')

    def test_extract_tarlzip_basic(self):
        test_file = self.get_test_loc('archive/lzip/sample.tar.lz')
        test_dir = self.get_temp_dir()
        archive.extract_tar(test_file, test_dir)
        result = os.path.join(test_dir, 'tst')
        assert ['empty', 'some'] == sorted(os.listdir(result))

    def test_uncompress_lzip_basic(self):
        test_file = self.get_test_loc('archive/lzip/some.lz')
        test_dir = self.get_temp_dir()
        archive.extract_lzip(test_file, test_dir)
        assert ['dfsdfsdfsdfsdfsdfsd_'] == os.listdir(test_dir)


class TestLz4(BaseArchiveTestCase):

    def test_extract_tarlz4_basic(self):
        test_file = self.get_test_loc('archive/lz4/sample.tar.lz4')
        test_dir = self.get_temp_dir()
        archive.extract_tar(test_file, test_dir)
        result = os.path.join(test_dir, 'tst')
        assert ['empty', 'some'] == sorted(os.listdir(result))

    def test_uncompress_lz4_basic(self):
        test_file = self.get_test_loc('archive/lz4/some.lz4')
        test_dir = self.get_temp_dir()
        archive.extract_lzip(test_file, test_dir)
        assert ['dfsdfsdfsdfsdfsdfsd_'] == os.listdir(test_dir)


class TestZstd(BaseArchiveTestCase):

    def test_extract_tarzstd_basic(self):
        test_file = self.get_test_loc('archive/zstd/sample.tar.zst')
        test_dir = self.get_temp_dir()
        archive.extract_tar(test_file, test_dir)
        result = os.path.join(test_dir, 'tst')
        assert ['empty', 'some'] == sorted(os.listdir(result))

    def test_uncompress_lzip_basic(self):
        test_file = self.get_test_loc('archive/zstd/some.zst')
        test_dir = self.get_temp_dir()
        archive.extract_lzip(test_file, test_dir)
        assert ['dfsdfsdfsdfsdfsdfsd_'] == os.listdir(test_dir)

################################################################################
# Note: The following series of test is not easy to grasp but unicode archives
# on multiple OS are hard to tests. So we have one test class for each
# libarchive and sevenzip on each of the three OSses which makes siz test
# classes each duplicated with eventually different expectations on each OS.
# Then each test class has a subclass with check_warnings set to True to tests
# only possible warnings separately. The code tries to avoid too much
# duplication, but this is at the cost of readability.
################################################################################


class ExtractArchiveWithIllegalFilenamesTestCase(BaseArchiveTestCase):

    def check_extract_weird_names(
            self, test_function, test_file, expected_suffix,
            expected_warnings=None,
            expected_exception=None,
            check_warnings=True, check_only_warnings=False,
            regen=False,
            ):
        """
        Run the extraction `test_function` on `test_file` checking that the paths
        listed in the `test_file.excepted` file exist in the extracted target
        directory. Regen expected file if True.
        """
        if not isinstance(test_file, compat.unicode):
            test_file = compat.unicode(test_file)
        test_file = self.get_test_loc(test_file)
        test_dir = self.get_temp_dir()

        warnings = []
        try:
            warnings = test_function(test_file, test_dir)
        except Exception as e:
            if expected_exception:
                assert expected_exception == e.args[0]
            else:
                raise

        if check_warnings and expected_warnings is not None:
            assert sorted(expected_warnings) == sorted(warnings)
            if check_only_warnings:
                return

        len_test_dir = len(test_dir)
        extracted = sorted(path[len_test_dir:] for path in fileutils.resource_iter(test_dir, with_dirs=False))
        extracted = [compat.unicode(p) for p in extracted]
        extracted = [to_posix(p) for p in extracted]

        if on_linux:
            os_suffix = 'linux'
        elif on_mac:
            os_suffix = 'mac'
        elif on_windows:
            os_suffix = 'win'

        expected_file = test_file + '_' + expected_suffix + '_' + os_suffix + '.expected'
        import json
        if regen:
            if py2:
                wmode = 'wb'
            if py3:
                wmode = 'w'
            with open(expected_file, wmode) as ef:
                ef.write(json.dumps(extracted, indent=2))

        expected = json.loads(open(expected_file).read())
        expected = [p for p in expected if p.strip()]
        try:
            assert expected == extracted
        except:
            # temporary CI debug
            if on_mac:
                print()
                print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                print(json.dumps(extracted, indent=2))
                print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                print()

            raise


@pytest.mark.skipif(on_windows, reason='Run only on POSIX because of specific test expectations.')
class TestExtractArchiveWithIllegalFilenamesWithLibarchiveOnPosix(ExtractArchiveWithIllegalFilenamesTestCase):

    def test_extract_7zip_with_weird_filenames_with_libarchive_posix(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.7z')
        self.check_extract_weird_names(
            libarchive2.extract, test_file, expected_warnings=[], expected_suffix='libarch')

    def test_extract_ar_with_weird_filenames_with_libarchive_posix(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.ar')
        test_dir = self.get_temp_dir()
        expected = Exception('Incorrect file header signature')
        self.assertRaisesInstance(expected, libarchive2.extract, test_file, test_dir)

    def test_extract_cpio_with_weird_filenames_with_libarchive_posix(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.cpio')
        self.check_extract_weird_names(
            libarchive2.extract, test_file, expected_warnings=[], expected_suffix='libarch')

    def test_extract_tar_with_weird_filenames_with_libarchive_posix(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.tar')
        self.check_extract_weird_names(
            libarchive2.extract, test_file, expected_warnings=[], expected_suffix='libarch')

    def test_extract_zip_with_weird_filenames_with_libarchive_posix(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.zip')
        self.check_extract_weird_names(
            libarchive2.extract, test_file, expected_warnings=[], expected_suffix='libarch')


@pytest.mark.skipif(not on_windows, reason='Run only on Windows because of specific test expectations.')
class TestExtractArchiveWithIllegalFilenamesWithLibarchiveOnWindows(ExtractArchiveWithIllegalFilenamesTestCase):

    def test_extract_7zip_with_weird_filenames_with_libarchive_win(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.7z')
        self.check_extract_weird_names(
            libarchive2.extract, test_file, expected_warnings=[], expected_suffix='libarch')

    def test_extract_ar_with_weird_filenames_with_libarchive_win(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.ar')
        try:
            self.check_extract_weird_names(
                libarchive2.extract, test_file, expected_warnings=[], expected_suffix='libarch')
            self.fail('Exception not raised.')
        except ArchiveError as ae:
            assert str(ae).startswith('Incorrect file header signature')

    def test_extract_cpio_with_weird_filenames_with_libarchive_win(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.cpio')
        self.check_extract_weird_names(
            libarchive2.extract, test_file, expected_warnings=[], expected_suffix='libarch')

    def test_extract_tar_with_weird_filenames_with_libarchive_win(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.tar')
        self.check_extract_weird_names(
            libarchive2.extract, test_file, expected_warnings=[], expected_suffix='libarch')

    def test_extract_zip_with_weird_filenames_with_libarchive_win(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.zip')
        self.check_extract_weird_names(
            libarchive2.extract, test_file, expected_warnings=[], expected_suffix='libarch')


@pytest.mark.skipif(on_windows or on_mac, reason='Do not run windows and mac because of specific test expectations.')
class TestExtractArchiveWithIllegalFilenamesWithSevenzipOnPosix(ExtractArchiveWithIllegalFilenamesTestCase):

    def test_extract_7zip_with_weird_filenames_with_sevenzip_posix(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.7z')
        self.check_extract_weird_names(
            sevenzip.extract, test_file, expected_warnings=[], expected_suffix='7zip')

    def test_extract_ar_with_weird_filenames_with_sevenzip_posix(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.ar')
        self.check_extract_weird_names(
            sevenzip.extract, test_file, expected_warnings=[], expected_suffix='7zip')

    def test_extract_cpio_with_weird_filenames_with_sevenzip_posix(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.cpio')
        self.check_extract_weird_names(
            sevenzip.extract, test_file, expected_warnings=[], expected_suffix='7zip')

    def test_extract_iso_with_weird_filenames_with_sevenzip_posix(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.iso')
        self.check_extract_weird_names(
            sevenzip.extract, test_file, expected_warnings=[], expected_suffix='7zip')

    @pytest.mark.xfail  # not a problem: we now use libarchive for these
    def test_extract_rar_with_weird_filenames_with_sevenzip_posix(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.rar')
        self.check_extract_weird_names(
            sevenzip.extract, test_file, expected_warnings=[], expected_suffix='7zip')

    def test_extract_tar_with_weird_filenames_with_sevenzip_posix(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.tar')
        self.check_extract_weird_names(
            sevenzip.extract, test_file, expected_warnings=[], expected_suffix='7zip')

    def test_extract_zip_with_weird_filenames_with_sevenzip_posix(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.zip')
        self.check_extract_weird_names(
            sevenzip.extract, test_file, expected_warnings=[], expected_suffix='7zip')


@pytest.mark.skipif(not on_mac, reason='Run only on macOS because of specific test expectations.')
class TestExtractArchiveWithIllegalFilenamesWithSevenzipOnMac(ExtractArchiveWithIllegalFilenamesTestCase):

    def test_extract_7zip_with_weird_filenames_with_sevenzip_macos(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.7z')
        expected_exception = {
            'weird_names/man\\1/..1.gz': u'Empty archive or incorrect arguments',
            'weird_names/man\\1/:\\.1': u'Empty archive or incorrect arguments',
            'weird_names/man\\1/[.1.gz': u'Empty archive or incorrect arguments',
            'weird_names/man\\1/[\\:*.1': u'Empty archive or incorrect arguments',
            'weird_names/man\\1/\\:.1.gz': u'Empty archive or incorrect arguments',
            "weird_names/some 'file": u'Empty archive or incorrect arguments',
            'weird_names/some \\file': u'Empty archive or incorrect arguments',
            'weird_names/some file': u'Empty archive or incorrect arguments',
            'weird_names/some"file': u'Empty archive or incorrect arguments',
            'weird_names/some\\"file': u'Empty archive or incorrect arguments',
            'weird_names/winchr/ab\t.t': u'Empty archive or incorrect arguments',
            'weird_names/winchr/ab\n.t': u'Empty archive or incorrect arguments',
            'weird_names/winchr/ab".t"': u'Empty archive or incorrect arguments',
            'weird_names/winchr/ab*.t*': u'Empty archive or incorrect arguments',
            'weird_names/winchr/ab<.t<': u'Empty archive or incorrect arguments',
            'weird_names/winchr/ab>.t>': u'Empty archive or incorrect arguments',
            'weird_names/winchr/ab?.t?': u'Empty archive or incorrect arguments',
            'weird_names/winchr/ab\\.t\\': u'Empty archive or incorrect arguments',
            'weird_names/winchr/ab|.t|': u'Empty archive or incorrect arguments',
        }

        self.check_extract_weird_names(
            sevenzip.extract,
            test_file,
            expected_warnings=[],
            expected_suffix='7zip',
            expected_exception=expected_exception, regen=False)

    def test_extract_ar_with_weird_filenames_with_sevenzip_macos(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.ar')
        expected_exception = {
            '\\:.1.gz': 'Empty archive or incorrect arguments',
            'ab*.t*': 'Empty archive or incorrect arguments',
            'some file': 'Empty archive or incorrect arguments',
            '[\\:*.1': 'Empty archive or incorrect arguments',
            'some"file': 'Empty archive or incorrect arguments',
            'ab\\.t\\': 'Empty archive or incorrect arguments',
            'some\\"file': 'Empty archive or incorrect arguments',
            'ab\t.t': 'Empty archive or incorrect arguments',
            'ab\n.t': 'Empty archive or incorrect arguments',
            "some 'file": 'Empty archive or incorrect arguments',
            'ab<.t<': 'Empty archive or incorrect arguments',
            'ab>.t>': 'Empty archive or incorrect arguments',
            'ab?.t?': 'Empty archive or incorrect arguments'
        }

        self.check_extract_weird_names(
            sevenzip.extract,
            test_file,
            expected_warnings=[],
            expected_suffix='7zip',
            expected_exception=expected_exception, regen=False)

    def test_extract_cpio_with_weird_filenames_with_sevenzip_macos(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.cpio')
        expected_exception = {
            'weird_names/man\\1/\\:.1.gz': 'Empty archive or incorrect arguments',
            'weird_names/winchr/ab*.t*': 'Empty archive or incorrect arguments',
            'weird_names/some file': 'Empty archive or incorrect arguments',
            'weird_names/man\\1/[\\:*.1': 'Empty archive or incorrect arguments',
            'weird_names/some"file': 'Empty archive or incorrect arguments',
            'weird_names/winchr/ab\\.t\\': 'Empty archive or incorrect arguments',
            'weird_names/some\\"file': 'Empty archive or incorrect arguments',
            'weird_names/winchr/ab\t.t': 'Empty archive or incorrect arguments',
            'weird_names/winchr/ab\n.t': 'Empty archive or incorrect arguments',
            "weird_names/some 'file": 'Empty archive or incorrect arguments',
            'weird_names/winchr/ab<.t<': 'Empty archive or incorrect arguments',
            'weird_names/winchr/ab>.t>': 'Empty archive or incorrect arguments',
            'weird_names/winchr/ab?.t?': 'Empty archive or incorrect arguments',
            'weird_names/some \\file': 'Empty archive or incorrect arguments',
            'weird_names/man\\1/..1.gz': 'Empty archive or incorrect arguments',
            'weird_names/winchr/ab".t"': 'Empty archive or incorrect arguments',
            'weird_names/man\\1/[.1.gz': 'Empty archive or incorrect arguments',
            'weird_names/winchr/ab|.t|': 'Empty archive or incorrect arguments',
            'weird_names/man\\1/:\\.1': 'Empty archive or incorrect arguments'
        }

        self.check_extract_weird_names(
            sevenzip.extract,
            test_file,
            expected_warnings=[],
            expected_suffix='7zip',
            expected_exception=expected_exception, regen=False)

    @pytest.mark.xfail
    def test_extract_rar_with_weird_filenames_with_sevenzip_macos(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.rar')
        self.check_extract_weird_names(
            sevenzip.extract,
            test_file,
            expected_warnings=[],
            expected_suffix='7zip',
            regen=False)

    def test_extract_iso_with_weird_filenames_with_sevenzip_macos(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.iso')
        expected_exception = {
            'weird_names/man_1/[.1.gz': 'Empty archive or incorrect arguments',
            'weird_names/man_1/[___.1': 'Empty archive or incorrect arguments',
            "weird_names/some 'file": 'Empty archive or incorrect arguments',
            'weird_names/some _file': 'Empty archive or incorrect arguments',
            'weird_names/some file': 'Empty archive or incorrect arguments',
            'weird_names/some"file': 'Empty archive or incorrect arguments',
            'weird_names/some_"file': 'Empty archive or incorrect arguments',
            'weird_names/winchr/ab".t"': 'Empty archive or incorrect arguments',
            'weird_names/winchr/ab<.t<': 'Empty archive or incorrect arguments',
            'weird_names/winchr/ab>.t>': 'Empty archive or incorrect arguments',
            'weird_names/winchr/ab|.t|': 'Empty archive or incorrect arguments'
        }

        self.check_extract_weird_names(
            sevenzip.extract,
            test_file,
            expected_warnings=[],
            expected_suffix='7zip',
            expected_exception=expected_exception, regen=False)

    def test_extract_tar_with_weird_filenames_with_sevenzip_macos(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.tar')
        expected_exception = {
            'weird_names/man\\1/\\:.1.gz': 'Empty archive or incorrect arguments',
            'weird_names/winchr/ab*.t*': 'Empty archive or incorrect arguments',
            'weird_names/some file': 'Empty archive or incorrect arguments',
            'weird_names/man\\1/[\\:*.1': 'Empty archive or incorrect arguments',
            'weird_names/some"file': 'Empty archive or incorrect arguments',
            'weird_names/winchr/ab\\.t\\': 'Empty archive or incorrect arguments',
            'weird_names/some\\"file': 'Empty archive or incorrect arguments',
            'weird_names/winchr/ab\t.t': 'Empty archive or incorrect arguments',
            'weird_names/winchr/ab\n.t': 'Empty archive or incorrect arguments',
            "weird_names/some 'file": 'Empty archive or incorrect arguments',
            'weird_names/winchr/ab<.t<': 'Empty archive or incorrect arguments',
            'weird_names/winchr/ab>.t>': 'Empty archive or incorrect arguments',
            'weird_names/winchr/ab?.t?': 'Empty archive or incorrect arguments',
            'weird_names/some \\file': 'Empty archive or incorrect arguments',
            'weird_names/man\\1/..1.gz': 'Empty archive or incorrect arguments',
            'weird_names/winchr/ab".t"': 'Empty archive or incorrect arguments',
            'weird_names/man\\1/[.1.gz': 'Empty archive or incorrect arguments',
            'weird_names/winchr/ab|.t|': 'Empty archive or incorrect arguments',
            'weird_names/man\\1/:\\.1': 'Empty archive or incorrect arguments',
        }

        self.check_extract_weird_names(
            sevenzip.extract,
            test_file,
            expected_warnings=[],
            expected_suffix='7zip',
            expected_exception=expected_exception, regen=False)

    def test_extract_zip_with_weird_filenames_with_sevenzip_macos(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.zip')
        expected_exception = {
            'weird_names/some \\file': 'Empty archive or incorrect arguments',
            "weird_names/some 'file": 'Empty archive or incorrect arguments',
            'weird_names/winchr/ab?.t?': 'Empty archive or incorrect arguments',
            'weird_names/winchr/ab\t.t': 'Empty archive or incorrect arguments',
            'weird_names/winchr/ab\n.t': 'Empty archive or incorrect arguments',
            'weird_names/winchr/ab>.t>': 'Empty archive or incorrect arguments',
            'weird_names/winchr/ab\\.t\\': 'Empty archive or incorrect arguments',
            'weird_names/winchr/ab<.t<': 'Empty archive or incorrect arguments',
            'weird_names/winchr/ab".t"': 'Empty archive or incorrect arguments',
            'weird_names/winchr/ab*.t*': 'Empty archive or incorrect arguments',
            'weird_names/winchr/ab|.t|': 'Empty archive or incorrect arguments',
            'weird_names/some\\"file': 'Empty archive or incorrect arguments',
            'weird_names/some file': 'Empty archive or incorrect arguments',
            'weird_names/some"file': 'Empty archive or incorrect arguments',
            'weird_names/man\\1/[\\:*.1': 'Empty archive or incorrect arguments',
            'weird_names/man\\1/\\:.1.gz': 'Empty archive or incorrect arguments',
            'weird_names/man\\1/[.1.gz': 'Empty archive or incorrect arguments',
            'weird_names/man\\1/:\\.1': 'Empty archive or incorrect arguments',
            'weird_names/man\\1/..1.gz': 'Empty archive or incorrect arguments',
        }

        self.check_extract_weird_names(
            sevenzip.extract,
            test_file,
            expected_warnings=[],
            expected_suffix='7zip',
            expected_exception=expected_exception, regen=False)


@pytest.mark.skipif(not on_windows, reason='Run only on Windows because of specific test expectations.')
class TestExtractArchiveWithIllegalFilenamesWithSevenzipOnWin(ExtractArchiveWithIllegalFilenamesTestCase):

    def test_extract_7zip_with_weird_filenames_with_sevenzip_win(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.7z')
        self.check_extract_weird_names(
            sevenzip.extract, test_file, expected_warnings=[], expected_suffix='7zip',
            check_warnings=False, check_only_warnings=False)

    @pytest.mark.xfail  # not a problem: we use libarchive for these
    def test_extract_ar_with_weird_filenames_with_sevenzip_win(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.ar')
        self.check_extract_weird_names(
            sevenzip.extract, test_file, expected_warnings=[], expected_suffix='7zip',
            check_warnings=False, check_only_warnings=False)

    @pytest.mark.xfail  # not a problem: we use libarchive for these
    def test_extract_cpio_with_weird_filenames_with_sevenzip_win(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.cpio')
        self.check_extract_weird_names(
            sevenzip.extract, test_file, expected_warnings=[], expected_suffix='7zip',
            check_warnings=False, check_only_warnings=False)

    def test_extract_iso_with_weird_filenames_with_sevenzip_win(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.iso')
        self.check_extract_weird_names(
            sevenzip.extract, test_file, expected_warnings=[], expected_suffix='7zip',
            check_warnings=False, check_only_warnings=False)

    @pytest.mark.xfail  # not a problem: we use libarchive for these
    def test_extract_rar_with_weird_filenames_with_sevenzip_win(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.rar')
        self.check_extract_weird_names(
            sevenzip.extract, test_file, expected_warnings=[], expected_suffix='7zip',
            check_warnings=False, check_only_warnings=False)

    def test_extract_tar_with_weird_filenames_with_sevenzip_win(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.tar')
        self.check_extract_weird_names(
            sevenzip.extract, test_file, expected_warnings=[], expected_suffix='7zip',
            check_warnings=False, check_only_warnings=False)

    @pytest.mark.xfail  # not a problem: we use libarchive for these
    def test_extract_zip_with_weird_filenames_with_sevenzip_win(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.zip')
        self.check_extract_weird_names(
            sevenzip.extract, test_file, expected_warnings=[], expected_suffix='7zip',
            check_warnings=False, check_only_warnings=False)


@pytest.mark.skipif(not on_windows, reason='Run only on Windows because of specific test expectations.')
class TestExtractArchiveWithIllegalFilenamesWithSevenzipOnWinWarning(ExtractArchiveWithIllegalFilenamesTestCase):

    if py2:

        # The results are not correct but not a problem: we use libarchive for these
        @pytest.mark.xfail
        def test_extract_7zip_with_weird_filenames_with_sevenzip_win(self):
            test_file = self.get_test_loc('archive/weird_names/weird_names.7z')
            self.check_extract_weird_names(
                sevenzip.extract, test_file, expected_warnings=[], expected_suffix='7zip',
                check_warnings=True, check_only_warnings=True)

    else:

        def test_extract_7zip_with_weird_filenames_with_sevenzip_win(self):
            test_file = self.get_test_loc('archive/weird_names/weird_names.7z')
            self.check_extract_weird_names(
                sevenzip.extract, test_file, expected_warnings=[], expected_suffix='7zip',
                check_warnings=True, check_only_warnings=True)

    if py2:

        @pytest.mark.xfail  # not a problem: we use libarchive for these
        def test_extract_ar_with_weird_filenames_with_sevenzip_win(self):
            test_file = self.get_test_loc('archive/weird_names/weird_names.ar')
            self.check_extract_weird_names(
                sevenzip.extract, test_file, expected_warnings=[], expected_suffix='7zip',
                check_warnings=True, check_only_warnings=True)

    else:

        def test_extract_ar_with_weird_filenames_with_sevenzip_win(self):
            test_file = self.get_test_loc('archive/weird_names/weird_names.ar')
            self.check_extract_weird_names(
                sevenzip.extract, test_file, expected_warnings=[], expected_suffix='7zip',
                check_warnings=True, check_only_warnings=True)

    if py2:

        @pytest.mark.xfail  # not a problem: we use libarchive for these
        def test_extract_cpio_with_weird_filenames_with_sevenzip_win(self):
            test_file = self.get_test_loc('archive/weird_names/weird_names.cpio')
            self.check_extract_weird_names(
                sevenzip.extract, test_file, expected_warnings=[], expected_suffix='7zip',
                check_warnings=True, check_only_warnings=True)

    else:

        def test_extract_cpio_with_weird_filenames_with_sevenzip_win(self):
            test_file = self.get_test_loc('archive/weird_names/weird_names.cpio')
            self.check_extract_weird_names(
                sevenzip.extract, test_file, expected_warnings=[], expected_suffix='7zip',
                check_warnings=True, check_only_warnings=True)

    def test_extract_iso_with_weird_filenames_with_sevenzip_win(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.iso')
        self.check_extract_weird_names(
            sevenzip.extract, test_file, expected_warnings=[], expected_suffix='7zip',
            check_warnings=True, check_only_warnings=True)

    @pytest.mark.xfail  # not a problem: we use libarchive for these
    def test_extract_rar_with_weird_filenames_with_sevenzip_win(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.rar')
        self.check_extract_weird_names(
            sevenzip.extract, test_file, expected_warnings=[], expected_suffix='7zip',
            check_warnings=True, check_only_warnings=True)

    def test_extract_tar_with_weird_filenames_with_sevenzip_win(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.tar')
        self.check_extract_weird_names(
            sevenzip.extract, test_file, expected_warnings=[], expected_suffix='7zip',
            check_warnings=True, check_only_warnings=True)

    if py2:

        @pytest.mark.xfail  # not a problem: we use libarchive for these
        def test_extract_zip_with_weird_filenames_with_sevenzip_win(self):
            test_file = self.get_test_loc('archive/weird_names/weird_names.zip')
            self.check_extract_weird_names(
                sevenzip.extract, test_file, expected_warnings=[], expected_suffix='7zip',
                check_warnings=True, check_only_warnings=True)

    else:

        def test_extract_zip_with_weird_filenames_with_sevenzip_win(self):
            test_file = self.get_test_loc('archive/weird_names/weird_names.zip')
            self.check_extract_weird_names(
                sevenzip.extract, test_file, expected_warnings=[], expected_suffix='7zip',
                check_warnings=True, check_only_warnings=True)


class TestZipSlip(BaseArchiveTestCase):
    pytestmark = pytest.mark.scanslow

    def test_extract_zipslip_zip_posix(self):
        test_file = self.get_test_loc('archive/zipslip/zip-slip.zip')
        test_dir = self.get_temp_dir()
        result = archive.extract_zip(test_file, test_dir)
        assert [] == result
        expected = [
            'dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/tmp/evil.txt',
            'good.txt'
        ]
        if on_windows:
            try:
                check_files(test_dir, expected)
            except AssertionError:
                expected = [u'good.txt', u'tmp/evil.txt']
                check_files(test_dir, expected)
        else:
            check_files(test_dir, expected)

    def test_extract_zipslip_zip_win(self):
        test_file = self.get_test_loc('archive/zipslip/zip-slip-win.zip')
        test_dir = self.get_temp_dir()
        result = archive.extract_zip(test_file, test_dir)
        assert [] == result
        expected = [
            'dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/Temp/evil.txt',
            'good.txt'
        ]
        if on_windows:
            try:
                check_files(test_dir, expected)
            except AssertionError:
                expected = [u'Temp/evil.txt', u'good.txt']
                check_files(test_dir, expected)
        else:
            check_files(test_dir, expected)

    @pytest.mark.skipif(on_windows, reason='Fails with WindowsError: [Error 206] The filename or extension is too long:')
    def test_extract_zipslip_tar_posix(self):
        test_file = self.get_test_loc('archive/zipslip/zip-slip.tar')
        test_dir = self.get_temp_dir()
        result = archive.extract_tar(test_file, test_dir)
        assert [] == result
        expected = [
            'dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/tmp/evil.txt',
            'good.txt'
        ]
        check_files(test_dir, expected)

    @pytest.mark.skipif(on_windows, reason='Fails with WindowsError: [Error 206] The filename or extension is too long:')
    def test_extract_zipslip_tar_win(self):
        test_file = self.get_test_loc('archive/zipslip/zip-slip-win.tar')
        test_dir = self.get_temp_dir()
        result = archive.extract_tar(test_file, test_dir)
        assert [] == result
        expected = [
            'dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/dotdot/Temp/evil.txt',
            'good.txt'
        ]
        check_files(test_dir, expected)
