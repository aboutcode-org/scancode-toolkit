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
import os
import posixpath
from unittest.case import skipIf
from unittest.case import expectedFailure

import commoncode.date
from commoncode.testcase import FileBasedTesting
from commoncode import fileutils
import typecode.contenttype

from extractcode_assert_utils import check_files
from extractcode_assert_utils import check_size

from extractcode import archive
from extractcode import libarchive2
from extractcode import sevenzip
from extractcode import ExtractErrorFailedToExtract


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


class TestSmokeTest(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_get_extractors(self):
        test_data = [
            ('archive/zip/basic.zip', [archive.extract_zip]),
            ('archive/rar/basic.rar', [archive.extract_rar]),
            ('archive/deb/adduser_3.112ubuntu1_all.deb', [archive.extract_ar]),
            ('archive/cpio/elfinfo-1.0-1.fc9.src.cpio', [archive.extract_cpio]),
            ('archive/rpm/elfinfo-1.0-1.fc9.src.rpm', [archive.extract_rpm, archive.extract_cpio]),
            ('archive/gzip/file_4.26-1.diff.gz', [archive.uncompress_gzip]),
            ('archive/ar/liby.a', [archive.extract_ar]),
            ('archive/bz2/single_file_not_tarred.bz2', [archive.uncompress_bzip2]),
            ('archive/tar/tarred.tar', [archive.extract_tar]),
            ('archive/tbz/tarred_bzipped.bz', [archive.uncompress_bzip2]),
            ('archive/tbz/tarred_bzipped.tar.bz2', [archive.extract_tar]),
            ('archive/tbz/tarred_bzipped.tbz', [archive.extract_tar]),
            ('archive/tgz/tarred_gzipped.gz', [archive.uncompress_gzip]),
            ('archive/tgz/tarred_gzipped.tar.gz', [archive.extract_tar]),
            ('archive/tgz/tarred_gzipped.tgz', [archive.extract_tar]),
            ('archive/7z/z.7z', [archive.extract_7z]),
            ('archive/Z/tr2tex.Z', [archive.extract_Z, ]),
            ('archive/Z/tkWWW-0.11.tar.Z', [archive.extract_Z, archive.extract_tar]),
        ]

        for test_file, expected in test_data:
            test_loc = self.get_test_loc(test_file)
            extractors = archive.get_extractors(test_loc)
            ft = typecode.contenttype.get_type(test_loc).filetype_file
            mt = typecode.contenttype.get_type(test_loc).mimetype_file
            fe = fileutils.file_extension(test_loc).lower()
            msg = (expected[0].__module__ + '.' + expected[0].__name__
                   + '!='
                   + extractors[0].__module__ + '.' + extractors[0].__name__
                   + ' for %(test_file)r') % locals()
            assert expected == extractors, msg

    def test_get_extractors_with_kinds(self):
        test_data = [
            ('archive/deb/adduser_3.112ubuntu1_all.deb', []),
            ('archive/rpm/elfinfo-1.0-1.fc9.src.rpm', []),
            ('archive/ar/liby.a', []),
            ('archive/tar/tarred.tar', [archive.extract_tar]),
            ('archive/tbz/tarred_bzipped.tar.bz2', []),
        ]

        kinds = (archive.regular, archive.file_system, archive.docs)
        for test_file, expected in test_data:
            test_loc = self.get_test_loc(test_file)
            extractors = archive.get_extractors(test_loc, kinds)

            ft = typecode.contenttype.get_type(test_loc).filetype_file
            mt = typecode.contenttype.get_type(test_loc).mimetype_file
            fe = fileutils.file_extension(test_loc).lower()
            msg = ('%(expected)r == %(extractors)r for %(test_file)s\n'
                   'with ft:%(ft)r, mt:%(mt)r, fe:%(fe)r' % locals())
            assert expected == extractors, msg

    def test_get_handlers(self):
        test_data = [
            ('archive/deb/adduser_3.112ubuntu1_all.deb', ['Debian package']),
            ('archive/rpm/elfinfo-1.0-1.fc9.src.rpm', ['RPM package']),
            ('archive/ar/liby.a', ['ar archive', 'Static Library', 'Debian package']),
            ('archive/tar/tarred.tar', ['Tar', 'Ruby Gem package']),
            ('archive/tbz/tarred_bzipped.tar.bz2', ['bzip2', 'Tar bzip2']),
            ('archive/tbz/tarred_bzipped.bz', ['bzip2', 'Tar bzip2']),
            ('archive/tgz/tarred_gzipped.gz', ['Tar gzip', 'Gzip', 'Dia diagram doc']),
        ]

        for test_file, expected in test_data:
            test_loc = self.get_test_loc(test_file)
            handlers = archive.get_handlers(test_loc)
            assert expected == [h[0].name for h in handlers]

    def test_score_handlers(self):
        test_data = [
            ('archive/deb/adduser_3.112ubuntu1_all.deb', [(31, 'Debian package')]),
            ('archive/rpm/elfinfo-1.0-1.fc9.src.rpm', [(32, 'RPM package')]),
            ('archive/ar/liby.a', [(31, 'Static Library'), (17, 'ar archive'), (11, 'Debian package')]),
            ('archive/tar/tarred.tar', [(29, 'Tar'), (19, 'Ruby Gem package')]),
            ('archive/tbz/tarred_bzipped.tar.bz2', [(30, 'Tar bzip2'), (29, 'bzip2')]),
            ('archive/tbz/tarred_bzipped.bz', [(29, 'bzip2'), (18, 'Tar bzip2')]),
            ('archive/tgz/tarred_gzipped.gz', [(29, 'Gzip'), (18, 'Tar gzip'), (16, 'Dia diagram doc')]),
        ]

        for test_file, expected in test_data:
            test_loc = self.get_test_loc(test_file)
            handlers = archive.get_handlers(test_loc)
            scored = archive.score_handlers(handlers)
            assert expected == sorted([(h[0], h[1].name) for h in scored], reverse=True)


class BaseArchiveTestCase(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def check_extract(self, test_file, test_function, expected):
        """
        Run the extraction test_function on test_file checking that a map of
        expected paths --> size exist in the extracted target directory.
        Does not test the presence of all files.
        """
        test_file = self.get_test_loc(test_file)
        test_dir = self.get_temp_dir()
        test_function(test_file, test_dir)
        for exp_path, exp_size in expected.items():
            exp_loc = os.path.join(test_dir, exp_path)
            msg = '''When extracting: %(test_file)s
                With function: %(test_function)r
                Failed to find expected path: %(exp_loc)s'''
            assert os.path.exists(exp_loc), msg % locals()
            if exp_size is not None:
                res_size = os.stat(exp_loc).st_size
                msg = '''When extracting: %(test_file)s
                    With function: %(test_function)r
                    Failed to assert the correct size %(exp_size)d
                    Got instead: %(res_size)d
                    for expected path: %(exp_loc)s'''
                assert exp_size == res_size, msg % locals()

    def collect_extracted_path(self, test_dir):
        result = []
        td = fileutils.as_posixpath(test_dir)
        for t, dirs, files in os.walk(test_dir):
            t = fileutils.as_posixpath(t)
            for d in dirs:
                nd = posixpath.join(t, d).replace(td, '') + '/'
                result.append(nd)
            for f in files:
                nf = posixpath.join(t, f).replace(td, '')
                result.append(nf)
        result = sorted(result)
        return result


    def assertExceptionContains(self, text, callableObj, *args, **kwargs):
        try:
            callableObj(*args, **kwargs)
        except Exception, e:
            if text not in str(e):
                raise self.failureException(
                       'Exception %(e)r raised, '
                       'it should contain the text %(text)r '
                       'and does not' % locals())
        else:
            raise self.failureException(
                   'Exception containing %(text)r not raised' % locals())


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
        expected = Exception("'Unrecognized archive format'")
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
        with codecs.open(exp_file, encoding='utf-8') as ef:
            expected_files = json.load(ef)
        check_files(test_dir, expected_files)

    def test_extract_targz_symlinks(self):
        test_file = self.get_test_loc('archive/tgz/symlink.tar.gz')
        test_dir = self.get_temp_dir()
        archive.extract_tar(test_file, test_dir)
        expected = [
            'z/x/a',
            # 'z/y/a': this is a symlink which is skipped by design
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


class TestGzip(BaseArchiveTestCase):
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
        assert 'f1content\nf2content\n' == open(result, 'rb').read()
        assert [] == warnings

    def test_uncompress_gzip_with_trailing_data(self):
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
        self.assertRaisesInstance(expected,
                                  archive.uncompress_gzip,
                                  test_file, test_dir)

    def test_uncompress_gzip_with_random_data(self):
        test_file = self.get_test_loc('archive/gzip/random_binary.data')
        test_dir = self.get_temp_dir()
        expected = Exception('Not a gzipped file')
        self.assertRaisesInstance(expected, archive.uncompress_gzip,
                                  test_file, test_dir)

    def test_uncompress_gzip_with_backslash_in_path(self):
        # weirdly enough, gzip keeps the original path/name
        test_file = self.get_test_loc('archive/gzip/backslash_path.gz')
        test_dir = self.get_temp_dir()
        archive.uncompress_gzip(test_file, test_dir)
        result = os.path.join(test_dir, 'backslash_path.gz-extract')
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
        expected = Exception("'bzip decompression failed'")
        self.assertRaisesInstance(expected, archive.extract_tar,
                                  test_file, test_dir)

    def test_extract_tar_bz2_absolute_path(self):
        assert not os.path.exists('/tmp/subdir')
        test_dir = self.get_temp_dir()
        test_file = self.get_test_loc('archive/tbz/absolute_path.tar.bz2')
        archive.extract_tar(test_file, test_dir)
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


class TestBz2(BaseArchiveTestCase):
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
        expected = Exception('invalid data stream')
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

class TestZip(BaseArchiveTestCase):
    def test_extract_zip_basic(self):
        test_file = self.get_test_loc('archive/zip/basic.zip')
        test_dir = self.get_temp_dir()
        archive.extract_zip(test_file, test_dir)
        result = os.path.join(test_dir, 'c/b/a.txt')
        assert os.path.exists(result)

    def test_extract_zip_broken(self):
        test_file = self.get_test_loc('archive/zip/zip_broken.zip')
        test_dir = self.get_temp_dir()
        self.assertRaises(Exception, archive.extract_zip, test_file, test_dir)
        # note: broken zip opens and extracts with 7z with exceptions sometimes
        # something is extracted in latest 7z
        # result = os.path.join(test_dir, 'a.txt')
        # print(test_dir)
        # assert os.path.exists(result)

    def test_extract_zip_with_invalid_path(self):
        test_file = self.get_test_loc('archive/zip/zip_invalidpath.zip')
        test_dir = self.get_temp_dir()
        archive.extract_zip(test_file, test_dir)
        result = os.path.join(test_dir, 'this/that')
        assert os.path.exists(result)

    @expectedFailure
    def test_extract_zip_with_trailing_data(self):
        test_file = self.get_test_loc('archive/zip/zip_trailing_data.zip')
        test_dir = self.get_temp_dir()
        try:
            archive.extract_zip(test_file, test_dir)
        except libarchive2.ArchiveError, ae:
            assert 'Invalid central directory signature' in str(ae)

        # fails because of https://github.com/libarchive/libarchive/issues/545
        result = os.path.join(test_dir, 'a.txt')
        assert os.path.exists(result)

    @expectedFailure
    def test_extract_zip_with_trailing_data2(self):
        # test archive created on cygwin with:
        # $ echo "test content" > f1
        # $ zip test f1
        # $ echo "some junk" >> test.zip
        test_file = self.get_test_loc('archive/zip/zip_trailing_data2.zip')
        test_dir = self.get_temp_dir()
        try:
            archive.extract_zip(test_file, test_dir)
        except libarchive2.ArchiveError, ae:
            assert 'Invalid central directory signature' in str(ae)
        # fails because of https://github.com/libarchive/libarchive/issues/545
        result = os.path.join(test_dir, 'f1')
        assert os.path.exists(result)

    def test_extract_zip_with_relative_path_simple(self):
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

    def test_extract_zip_with_relative_path_deeply_nested(self):
        test_file = self.get_test_loc('archive/zip/relative_nested.zip')
        test_dir = self.get_temp_dir()
        archive.extract_zip(test_file, test_dir)
        result = self.collect_extracted_path(test_dir)
        expected = [
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
        assert expected == result

    def test_extract_zip_with_password(self):
        test_file = self.get_test_loc('archive/zip/zip_password_nexb.zip')
        test_dir = self.get_temp_dir()
        try:
            archive.extract_zip(test_file, test_dir)
        except Exception, e:
            assert isinstance(e, libarchive2.ArchiveError)
            assert 'Encrypted file is unsupported' in str(e)
        # self.assertRaisesI(libarchive2.ArchiveError, archive.extract_zip, test_file, test_dir)

    def test_extract_zip_java_jar(self):
        test_file = self.get_test_loc('archive/zip/jar/simple.jar')
        test_dir = self.get_temp_dir()

        archive.extract_zip(test_file, test_dir)
        result = os.path.join(test_dir,
            'org/jvnet/glassfish/comms/sipagent/transport/SocketTransportListenerManager.class')
        assert os.path.exists(result)

    def test_extract_zip_with_duplicated_lowercase_paths(self):
        test_file = self.get_test_loc('archive/zip/dup_names.zip')
        expected = {'META-INF/license/': None,  # a directory
                    'META-INF/license/LICENSE.base64.txt': 1618,
                    'META-INF/LICENSE_1': 11366}
        self.check_extract(test_file, archive.extract_zip, expected)

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
        result = os.path.join(test_dir, 'scripts/AutomaticClose.int')
        assert os.path.exists(result)

    def test_extract_zip_with_backsplash_in_path_2(self):
        test_file = self.get_test_loc('archive/zip/backslash/AspectJTest.zip')
        test_dir = self.get_temp_dir()
        archive.extract_zip(test_file, test_dir)
        result = os.path.join(test_dir, 'AspectJTest/bin/p3/Flyable.class')
        assert os.path.exists(result)

    def test_extract_zip_with_backslash_in_path_3(self):
        test_file = self.get_test_loc('archive/zip/backslash/boo-0.3-src.zip')
        test_dir = self.get_temp_dir()
        archive.extract_zip(test_file, test_dir)
        result = os.path.join(test_dir, 'src/Boo.Lang.Compiler'
                                '/TypeSystem/InternalCallableType.cs')
        assert os.path.exists(result)


class TestLibarch(BaseArchiveTestCase):
    def test_extract_zip_with_relative_path_libarchive(self):
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
        expected = Exception("'Unrecognized archive format'")
        self.assertRaisesInstance(expected, archive.extract_tar,
                                  test_file, test_dir)

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
            # '1-LNKTYPE', links are skipped
            'S-SPARSE',
            'S-SPARSE-WITH-NULLS',
        ]
        check_files(test_dir, expected)
        assert [] == result

    # @skipIf(True, 'Unicode tar paths are not handled well yet')
    def test_extract_python_testtar_tar_archive_with_special_files(self):
        test_file = self.get_test_loc('archive/tar/testtar.tar')
        # this is from:
        # https://hg.python.org/cpython/raw-file/bff88c866886/Lib/test/testtar.tar
        test_dir = self.get_temp_dir()
        result = archive.extract_tar(test_file, test_dir)
        expected_warnings = ["pax/regtype4: Pathname can't be converted from UTF-8 to current locale."]
        assert sorted(expected_warnings) == sorted(result)

        expected = [
            'gnu/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/longname',
            'gnu/regtype-gnu-uid',
            'gnu/sparse',
            'gnu/sparse-0.0',
            'gnu/sparse-0.1',
            'gnu/sparse-1.0',
            'misc/eof',
            'misc/regtype-hpux-signed-chksum-\xc4\xd6\xdc\xe4\xf6\xfc\xdf',
            'misc/regtype-old-v7',
            'misc/regtype-old-v7-signed-chksum-\xc4\xd6\xdc\xe4\xf6\xfc\xdf',
            'misc/regtype-suntar',
            'misc/regtype-xstar',
            'pax/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/123/longname',
            'pax/hdrcharset-\xe4\xf6\xfc',
            'pax/regtype1',
            'pax/regtype2',
            'pax/regtype3',
            'pax/regtype4',
            'pax/regtype4_1',
            'pax/umlauts-\xc3\x84\xc3\x96\xc3\x9c\xc3\xa4\xc3\xb6\xc3\xbc\xc3\x9f',
            'ustar/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/12345/1234567/longname',
            'ustar/conttype',
            'ustar/linktest1/regtype',
            'ustar/regtype',
            'ustar/sparse',
            'ustar/umlauts-\xc4\xd6\xdc\xe4\xf6\xfc\xdf'
        ]

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

    def test_extract_ar_broken(self):
        test_file = self.get_test_loc('archive/ar/liby-corrupted.a')
        test_dir = self.get_temp_dir()
        result = archive.extract_ar(test_file, test_dir)
        expected = [
            '__.SYMDEF',
            'main.o',
            'main_1.o',
            'main_10.o',
            'main_11.o',
            'main_2.o',
            'main_3.o',
            'main_4.o',
            'main_5.o',
            'main_6.o',
            'main_7.o',
            'main_8.o',
            'main_9.o'
        ]
        check_files(test_dir, expected)
        assert ['main.o: Incorrect file header signature'] == result

    def test_extract_ar_with_invalid_path(self):
        test_file = self.get_test_loc('archive/ar/ar_invalidpath.ar')
        test_dir = self.get_temp_dir()
        result = archive.extract_ar(test_file, test_dir)
        expected = ['this/that']
        check_files(test_dir, expected)
        assert [] == result

    def test_extract_ar_with_relative_path_7z(self):
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
        result = archive.libarchive2.extract(test_file, test_dir)
        expected_warns = [
            '/: Invalid string table',
            "/: Invalid string table\nCan't find long filename for entry"
        ]
        assert expected_warns == result
        # inccorrect for now: need this: ['__.SYMDEF', 'release/init.obj']
        expected = ['file', 'file_1', 'file_2', 'file_3']
        check_files(test_dir, expected)

    def test_extract_ar_with_relative_path_and_backslashes_in_names_libarch(self):
        test_file = self.get_test_loc('archive/ar/winlib/freetype.lib')
        test_dir = self.get_temp_dir()
        result = archive.libarchive2.extract(test_file, test_dir)
        expected_warns = [
            '/: Invalid string table',
            "/: Invalid string table\nCan't find long filename for entry"
        ]
        assert expected_warns == result
        # 7zip is better, but has a security bug for now
        expected = [
            'file',
            'file_1',
            'file_10',
            'file_11',
            'file_12',
            'file_13',
            'file_14',
            'file_15',
            'file_16',
            'file_17',
            'file_18',
            'file_19',
            'file_2',
            'file_20',
            'file_21',
            'file_22',
            'file_23',
            'file_24',
            'file_25',
            'file_26',
            'file_27',
            'file_28',
            'file_29',
            'file_3',
            'file_30',
            'file_31',
            'file_32',
            'file_33',
            'file_34',
            'file_35',
            'file_4',
            'file_5',
            'file_6',
            'file_7',
            'file_8',
            'file_9'
        ]

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

    # @expectedFailure
    def test_extract_ar_with_permissions(self):
        # the behavious is not correct: 7z is better, but has sec flaws for now
        test_file = self.get_test_loc('archive/ar/winlib/zlib.lib')
        test_dir = self.get_temp_dir()
        result = archive.extract_ar(test_file, test_dir)
        assert [] == result
        expected = ['file', 'file_1']
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
        self.assertRaisesInstance(Exception('No error returned'), sevenzip.extract, test_file, test_dir)

    def test_extract_cpio_broken2(self):
        test_file = self.get_test_loc('archive/cpio/cpio_broken.cpio')
        test_dir = self.get_temp_dir()
        result = archive.extract_cpio(test_file, test_dir)
        assert ['elfinfo-1.0.tar.gz', 'elfinfo-1.0.tar_1.gz'] == sorted(os.listdir(test_dir))
        assert ['elfinfo-1.0.tar.gz: Skipped 72 bytes before finding valid header'] == result

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
        expected = Exception('No error returned')
        self.assertRaisesInstance(expected, archive.extract_rpm,
                                  test_file, test_dir)


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
        Exception('No error returned')
        archive.extract_rar(test_file, test_dir)
        result = os.path.join(test_dir, 'd', 'b', 'a.txt')
        assert os.path.exists(result)

    def test_extract_rar_broken(self):
        test_file = self.get_test_loc('archive/rar/broken.rar')
        test_dir = self.get_temp_dir()
        expected = Exception('No error returned')
        self.assertRaisesInstance(expected, archive.extract_rar,
                                  test_file, test_dir)

    def test_extract_rar_with_relative_path(self):
        # FIXME: this file may not have relative paths
        test_file = self.get_test_loc('archive/rar/rar_relative.rar')
        test_dir = self.get_temp_dir()
        archive.extract_rar(test_file, test_dir)
        result = os.path.abspath(test_file + '/../a_parent_folder.txt')
        assert not os.path.exists(result)

        result = os.path.join(test_dir, '2folder/relative_file')
        assert os.path.exists(result)

        result = os.path.join(test_dir, '2folder/3folder/relative_file')
        assert os.path.exists(result)

    def test_extract_rar_with_absolute_path(self):
        # FIXME: this file may not have absolute paths
        assert not os.path.exists('/home/li/Desktop/zip_folder')
        test_file = self.get_test_loc('archive/rar/rar_absolute.rar')
        test_dir = self.get_temp_dir()
        archive.extract_rar(test_file, test_dir)
        assert not os.path.exists('/home/li/Desktop/absolute_folder')
        result = os.path.join(test_dir, 'home/li/Desktop',
                                'absolute_folder/absolute_file')
        assert os.path.exists(result)

    def test_extract_rar_with_password(self):
        test_file = self.get_test_loc('archive/rar/rar_password.rar')
        test_dir = self.get_temp_dir()
        expected = Exception('Password protected archive, unable to extract')
        self.assertRaisesInstance(expected, archive.extract_rar,
                                  test_file, test_dir)

    def test_extract_rar_with_non_ascii_path(self):
        test_file = self.get_test_loc('archive/rar/non_ascii_corrupted.rar')
        # The bug only occurs if the path was given as Unicode !
        test_file = unicode(test_file)
        test_dir = self.get_temp_dir()
        # raise an exception but still extracts some
        expected = Exception('No error returned')
        self.assertRaisesInstance(expected, archive.extract_rar,
                                  test_file, test_dir)
        result = os.path.join(test_dir, 'EdoProject_java/WebContent'
                               '/WEB-INF/lib/cos.jar')
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
        msg = 'No error returned'
        self.assertRaisesInstance(ExtractErrorFailedToExtract(msg), sevenzip.extract, test_file, test_dir)

    def test_extract_7z_with_broken_archive(self):
        test_file = self.get_test_loc('archive/7z/corrupted7z.7z')
        test_dir = self.get_temp_dir()
        expected = libarchive2.ArchiveError()
        expected.msg = 'Damaged 7-Zip archive'
        self.assertRaisesInstance(expected, archive.extract_7z, test_file, test_dir)

    def test_extract_7z_with_non_existing_archive(self):
        test_file = 'archive/7z/I_DO_NOT_EXIST.zip'
        test_dir = self.get_temp_dir()
        msg = 'No error returned'
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
        expected = Exception("'The file content is encrypted, but currently not supported'")
        self.assertRaisesInstance(expected, archive.extract_7z, test_file, test_dir)


class TestIso(BaseArchiveTestCase):
    def test_extract_iso_basic(self):
        test_file = self.get_test_loc('archive/iso/fdbasecd.iso')
        test_dir = self.get_temp_dir()
        archive.extract_iso(test_file, test_dir)
        result = os.path.join(test_dir, 'autorun.inf')
        assert os.path.exists(result)
        result = os.path.join(test_dir, 'freedos/packages/base.end')
        assert os.path.exists(result)

    def test_get_extractor_not_iso_text_is_not_mistaken_for_an_iso_image(self):
        test_file = self.get_test_loc('archive/iso/ChangeLog')
        extractor = archive.get_extractor(test_file)
        assert not extractor


class TestXzLzma(BaseArchiveTestCase):
    def check_lzma_extract(self, extract_fun, test_file, expected):
        """
        Run the 'extract_fun' function using the 'test_file' file as an input
        and verifies that the 'expected' file has been extracted correctly.
        """
        test_file = self.get_test_loc(test_file)
        extract_dir = self.get_temp_dir()
        expected_file = os.path.join(extract_dir, expected)
        extract_fun(test_file, extract_dir)
        assert  os.path.exists(expected_file), (
                        '%(expected_file)s file was not extracted '
                        'correctly from archive %(test_file)s'
                        % locals())

    def test_extract_archive_tar_xz_1(self):
        test_file = 'archive/lzma_xz/basic/texlive-core-patches-20.tar.xz'
        self.check_lzma_extract(extract_fun=archive.extract_lzma,
                                test_file=test_file,
                                expected='texlive-core-patches-20.tar')

    def test_extract_archive_tar_xz_2(self):
        test_file = 'archive/lzma_xz/all/texlive-core-patches-20.tar.xz'
        expected = 'texlive-core-patches-20.tar'
        self.check_lzma_extract(extract_fun=archive.extract_lzma,
                                test_file=test_file,
                                expected=expected)

    def test_extract_archive_tar_xz_3(self):
        test_file = 'archive/lzma_xz/all/binutils-2.22.52.0.3-patches-1.0.tar.xz'
        expected = 'binutils-2.22.52.0.3-patches-1.0.tar'
        self.check_lzma_extract(extract_fun=archive.extract_lzma,
                        test_file=test_file,
                        expected=expected)

    def test_extract_archive_tar_xz_4(self):
        test_file = 'archive/lzma_xz/all/bdsup2sub-4.0.0.tar.xz'
        expected = 'bdsup2sub-4.0.0.tar'
        self.check_lzma_extract(extract_fun=archive.extract_lzma,
                        test_file=test_file,
                        expected=expected)

    def test_extract_archive_tar_xz_5(self):
        test_file = 'archive/lzma_xz/all/desktop-file-utils-0.19.tar.xz'
        expected = 'desktop-file-utils-0.19.tar'
        self.check_lzma_extract(extract_fun=archive.extract_lzma,
                        test_file=test_file,
                        expected=expected)

    def test_extract_archive_tar_lzma_1(self):
        test_file = 'archive/lzma_xz/basic/coreutils-8.5-patches-1.tar.lzma'
        expected = 'coreutils-8.5-patches-1.tar'
        self.check_lzma_extract(extract_fun=archive.extract_lzma,
                                test_file=test_file,
                                expected=expected)

    def test_extract_archive_tar_lzma_2(self):
        test_file = 'archive/lzma_xz/all/orionsocket-1.0.9.tar.lzma'
        expected = 'orionsocket-1.0.9.tar'
        self.check_lzma_extract(extract_fun=archive.extract_lzma,
                        test_file=test_file,
                        expected=expected)

    def test_extract_archive_tar_lzma_3(self):
        test_file = 'archive/lzma_xz/all/MinGW-5.1.6.exe-src.tar.lzma'
        expected = 'MinGW-5.1.6.exe-src.tar'
        self.check_lzma_extract(extract_fun=archive.extract_lzma,
                        test_file=test_file,
                        expected=expected)

    def test_extract_archive_tar_lzma_4(self):
        test_file = 'archive/lzma_xz/all/dnsmasq-2.57.tar.lzma'
        expected = 'dnsmasq-2.57.tar'
        self.check_lzma_extract(extract_fun=archive.extract_lzma,
                        test_file=test_file,
                        expected=expected)

    def test_extract_archive_lzma_1(self):
        test_file = 'archive/lzma_xz/all/cromwell-2.40-r3-cvs-fixes.patch.lzma'
        expected = 'cromwell-2.40-r3-cvs-fixes.patch'
        self.check_lzma_extract(extract_fun=archive.extract_lzma,
                        test_file=test_file,
                        expected=expected)

    def test_extract_archive_tar_lzma_5(self):
        test_file = 'archive/lzma_xz/all/coreutils-8.5-patches-1.tar.lzma'
        expected = 'coreutils-8.5-patches-1.tar'
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

    def test_extract_dia_with_trailing_data(self):
        test_file = self.get_test_loc('archive/dia/dia_trailing.dia')
        test_dir = self.get_temp_dir()
        archive.uncompress_gzip(test_file, test_dir)
        result = os.path.join(test_dir, 'dia_trailing.dia-extract')
        assert os.path.exists(result)

    def test_extract_dia_broken_1(self):
        test_file = self.get_test_loc('archive/dia/dia_broken.dia')
        test_dir = self.get_temp_dir()
        self.assertExceptionContains('CRC check failed',
                                     archive.uncompress_gzip,
                                     test_file,
                                     test_dir)

    def test_extract_dia_broken_2(self):
        test_file = self.get_test_loc('archive/dia/broken/PublisherUML.dia')
        test_dir = self.get_temp_dir()
        self.assertExceptionContains('invalid distance too far back',
                                     archive.uncompress_gzip,
                                     test_file,
                                     test_dir)

    def test_extract_dia_broken_3(self):
        test_file = self.get_test_loc('archive/dia/broken/schedulerClassDiagram.dia')
        test_dir = self.get_temp_dir()
        self.assertExceptionContains('invalid distance too far back',
                                     archive.uncompress_gzip,
                                     test_file,
                                     test_dir)

    def test_extract_dia_broken_4(self):
        test_file = self.get_test_loc('archive/dia/broken/ServletProxyGenerator.dia')
        test_dir = self.get_temp_dir()
        self.assertExceptionContains('invalid distance too far back',
                                     archive.uncompress_gzip,
                                     test_file,
                                     test_dir)

    def test_extract_can_get_extractor_and_uncompress_dia_files(self):
        test_file = self.get_test_loc('archive/dia/guess/infoset-doc.dia')
        test_dir = self.get_temp_dir()
        archive.get_extractor(test_file)(test_file, test_dir)
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
