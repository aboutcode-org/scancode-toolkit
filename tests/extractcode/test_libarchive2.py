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
import ntpath
import os
import posixpath
from unittest.case import expectedFailure
from unittest.case import skipIf

import commoncode.date
from commoncode.testcase import FileBasedTesting
from commoncode import compat
from commoncode import filetype
from commoncode import fileutils
from commoncode.system import on_linux
from commoncode.system import on_mac
from commoncode.system import on_windows
from commoncode.system import py2
import typecode.contenttype

from extractcode_assert_utils import check_files
from extractcode_assert_utils import check_size

import extractcode

from extractcode import archive
from extractcode import libarchive2
from extractcode import sevenzip

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

import pytest
pytestmark = pytest.mark.scanpy3  # NOQA

class TestExtractorTest(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')
    
    def check_get_extractors(self, test_file, expected, kinds=()):
        test_loc = self.get_test_loc(test_file)
        if kinds:
            extractors = archive.get_extractors(test_loc, kinds)
        else:
            extractors = archive.get_extractors(test_loc)

        #ft = 'TODO' or typecode.contenttype.get_type(test_loc).filetype_file
        #mt = 'TODO' or typecode.contenttype.get_type(test_loc).mimetype_file
        fe = fileutils.file_extension(test_loc).lower()
        em = ', '.join(e.__module__ + '.' + e.__name__ for e in extractors)
        #msg = ('%(expected)r == %(extractors)r for %(test_file)s\n'
               #'with ft:%(ft)r, mt:%(mt)r, fe:%(fe)r, em:%(em)s' % locals())
        #assert expected == extractors, msg

    def test_get_extractor_with_kinds_rpm_2(self):
        test_file = 'archive/rpm/elfinfo-1.0-1.fc9.src.rpm'
        kinds = (archive.regular, archive.file_system, archive.docs, archive.package)
        expected = [sevenzip.extract, libarchive2.extract]
        self.check_get_extractors(test_file, expected, kinds)

    def test_libarchive_extract_can_extract_to_relative_paths(self):
        # The setup is a tad complex because we want to have a relative dir
        # to the base dir where we run tests from, ie the scancode-toolkit/ dir
        # To use relative paths, we use our tmp dir at the root of the code tree
        from os.path import dirname, join, abspath
        import tempfile
        import shutil
        from extractcode.libarchive2 import extract

        test_file = self.get_test_loc('archive/relative_path/basic.zip')
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

class BaseArchiveTestCase(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def check_extract(self, test_function, test_file, expected, expected_warnings=None, check_all=False):
        """
        Run the extraction `test_function` on `test_file` checking that a map of
        expected paths --> size exist in the extracted target directory.
        Does not test the presence of all files unless `check_all` is True.
        """
        test_file = self.get_test_loc(test_file)
        test_dir = self.get_temp_dir()
        warnings = test_function(test_file, test_dir)
        if expected_warnings is not None:
            assert expected_warnings == warnings

        if check_all:
            len_test_dir = len(test_dir)
            extracted = {path[len_test_dir:]: filetype.get_size(path) for path in fileutils.resource_iter(test_dir, with_dirs=False)}
            expected = {os.path.join(test_dir, exp_path): exp_size for exp_path, exp_size in expected.items()}
            assert sorted(expected.items()) == sorted(extracted.items())
        else:
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
        except Exception as e:
            if text not in str(e):
                raise self.failureException(
                       'Exception %(e)r raised, '
                       'it should contain the text %(text)r '
                       'and does not' % locals())
        else:
            raise self.failureException(
                   'Exception containing %(text)r not raised' % locals())

class TestZip(BaseArchiveTestCase):

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
    
    def test_extract_zip_with_relative_path_deeply_nested_with_libarchive(self):
        test_file = self.get_test_loc('archive/zip/relative_nested.zip')
        test_dir = self.get_temp_dir()
        libarchive2.extract(test_file, test_dir)
        result = self.collect_extracted_path(test_dir)
        assert self.expected_deeply_nested_relative_path == result

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

    def test_extract_ar_with_relative_path_libarch(self):
        test_file = self.get_test_loc('archive/ar/winlib/htmlhelp.lib')
        test_dir = self.get_temp_dir()
        result = archive.libarchive2.extract(test_file, test_dir)
        if py2:
            expected_warns = [
            "'//': \nInvalid string table",
            "'/0': \nCan't find long filename for entry"
        ]
        else:
            expected_warns = [
            "b'//': \nInvalid string table",
            "b'/0': \nCan't find long filename for entry"
        ]        
        assert expected_warns == result
        # inccorrect for now: need this: ['__.SYMDEF', 'release/init.obj']
        expected = ['0', 'dot', 'dot_1', 'dot_2']
        check_files(test_dir, expected)

    def test_extract_ar_with_relative_path_and_backslashes_in_names_libarch(self):
        test_file = self.get_test_loc('archive/ar/winlib/freetype.lib')
        test_dir = self.get_temp_dir()
        result = archive.libarchive2.extract(test_file, test_dir)
        if py2:
            expected_warns = [
            u"'//': \nInvalid string table",
            u"'/0': \nCan't find long filename for entry",
            u"'/34': \nCan't find long filename for entry",
            u"'/68': \nCan't find long filename for entry",
            u"'/104': \nCan't find long filename for entry",
            u"'/137': \nCan't find long filename for entry",
            u"'/173': \nCan't find long filename for entry",
            u"'/205': \nCan't find long filename for entry",
            u"'/239': \nCan't find long filename for entry",
            u"'/275': \nCan't find long filename for entry",
            u"'/311': \nCan't find long filename for entry",
            u"'/344': \nCan't find long filename for entry",
            u"'/375': \nCan't find long filename for entry",
            u"'/406': \nCan't find long filename for entry",
            u"'/442': \nCan't find long filename for entry",
            u"'/477': \nCan't find long filename for entry",
            u"'/512': \nCan't find long filename for entry",
            u"'/545': \nCan't find long filename for entry",
            u"'/577': \nCan't find long filename for entry",
            u"'/611': \nCan't find long filename for entry",
            u"'/645': \nCan't find long filename for entry",
            u"'/681': \nCan't find long filename for entry",
            u"'/717': \nCan't find long filename for entry",
            u"'/750': \nCan't find long filename for entry",
            u"'/784': \nCan't find long filename for entry",
            u"'/818': \nCan't find long filename for entry",
            u"'/853': \nCan't find long filename for entry",
            u"'/888': \nCan't find long filename for entry",
            u"'/923': \nCan't find long filename for entry",
            u"'/957': \nCan't find long filename for entry",
            u"'/993': \nCan't find long filename for entry",
            u"'/1027': \nCan't find long filename for entry",
            u"'/1058': \nCan't find long filename for entry",
            u"'/1089': \nCan't find long filename for entry"
        ]
        else:
            expected_warns = [
            "b'//': \nInvalid string table",
            "b'/0': \nCan't find long filename for entry",
            "b'/34': \nCan't find long filename for entry",
            "b'/68': \nCan't find long filename for entry",
            "b'/104': \nCan't find long filename for entry",
            "b'/137': \nCan't find long filename for entry",
            "b'/173': \nCan't find long filename for entry",
            "b'/205': \nCan't find long filename for entry",
            "b'/239': \nCan't find long filename for entry",
            "b'/275': \nCan't find long filename for entry",
            "b'/311': \nCan't find long filename for entry",
            "b'/344': \nCan't find long filename for entry",
            "b'/375': \nCan't find long filename for entry",
            "b'/406': \nCan't find long filename for entry",
            "b'/442': \nCan't find long filename for entry",
            "b'/477': \nCan't find long filename for entry",
            "b'/512': \nCan't find long filename for entry",
            "b'/545': \nCan't find long filename for entry",
            "b'/577': \nCan't find long filename for entry",
            "b'/611': \nCan't find long filename for entry",
            "b'/645': \nCan't find long filename for entry",
            "b'/681': \nCan't find long filename for entry",
            "b'/717': \nCan't find long filename for entry",
            "b'/750': \nCan't find long filename for entry",
            "b'/784': \nCan't find long filename for entry",
            "b'/818': \nCan't find long filename for entry",
            "b'/853': \nCan't find long filename for entry",
            "b'/888': \nCan't find long filename for entry",
            "b'/923': \nCan't find long filename for entry",
            "b'/957': \nCan't find long filename for entry",
            "b'/993': \nCan't find long filename for entry",
            "b'/1027': \nCan't find long filename for entry",
            "b'/1058': \nCan't find long filename for entry",
            "b'/1089': \nCan't find long filename for entry"
        ]
        assert expected_warns == result
        # 7zip is better, but has a security bug for now
        # GNU ar works fine otherwise, but there are portability issues
        expected = [
            '0',
            '1027',
            '104',
            '1058',
            '1089',
            '137',
            '173',
            '205',
            '239',
            '275',
            '311',
            '34',
            '344',
            '375',
            '406',
            '442',
            '477',
            '512',
            '545',
            '577',
            '611',
            '645',
            '68',
            '681',
            '717',
            '750',
            '784',
            '818',
            '853',
            '888',
            '923',
            '957',
            '993',
            'dot',
            'dot_1',
            'dot_2'
        ]

        if on_linux and py2:
            expected = [bytes(e) for e in expected]

        check_files(test_dir, expected)

    def test_extract_7zip_libarchive_with_unicode_path_extracts_with_errors(self):
        test_file = self.get_test_loc('archive/7z/7zip_unicode.7z')
        test_dir = self.get_temp_dir()
        try:
            archive.extract_7z(test_file, test_dir)
        except libarchive2.ArchiveError as e:
            assert 'Damaged 7-Zip archive' in e.msg

class TestCbr(BaseArchiveTestCase):

    def test_get_extractor_cbr(self):
        test_file = self.get_test_loc('archive/cbr/t.cbr')
        result = archive.get_extractor(test_file)
        # we do not handle these rare extensions (this is a RAR)
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

def is_posixpath(location):
    """
    Return True if the `location` path is likely a POSIX-like path using POSIX path
    separators (slash or "/")or has no path separator.

    Return False if the `location` path is likely a Windows-like path using backslash
    as path separators (e.g. "\").
    """
    has_slashes = '/' in location
    has_backslashes = '\\' in location
    # windows paths with drive
    if location:
        drive, _ = ntpath.splitdrive(location)
        if drive:
            return False

    # a path is always POSIX unless it contains ONLY backslahes
    # which is a rough approximation (it could still be posix)
    is_posix = True
    if has_backslashes and not has_slashes:
        is_posix = False
    return is_posix

def to_posix(path):
    """
    Return a path using the posix path separator given a path that may contain posix
    or windows separators, converting \ to /. NB: this path will still be valid in
    the windows explorer (except as a UNC or share name). It will be a valid path
    everywhere in Python. It will not be valid for windows command line operations.
    """
    is_unicode = isinstance(path, compat.unicode)
    ntpath_sep = is_unicode and u'\\' or '\\'
    posixpath_sep = is_unicode and u'/' or '/'
    if is_posixpath(path):
        if on_windows:
            return path.replace(ntpath_sep, posixpath_sep)
        else:
            return path
    return path.replace(ntpath_sep, posixpath_sep)
    


class ExtractArchiveWithIllegalFilenamesTestCase(BaseArchiveTestCase):

    check_only_warnings = False

    def assertRaisesInstance(self, excInstance, callableObj,
                                 *args, **kwargs):
        """
        This assertion accepts an instance instead of a class for refined
        exception testing.
        """
        excClass = excInstance.__class__
        try:
            callableObj(*args, **kwargs)
        except excClass as e:
            self.assertEqual(str(excInstance), str(e))
        else:
            if hasattr(excClass, '__name__'):
                excName = excClass.__name__
            else:
                excName = str(excClass)
            raise self.failureException('%s not raised' % excName)

    def check_extract(self, test_function, test_file, expected_suffix, expected_warnings=None, regen=False):
        """
        Run the extraction `test_function` on `test_file` checking that the paths
        listed in the `test_file.excepted` file exist in the extracted target
        directory. Regen expected file if True.
        """
        if not isinstance(test_file, compat.unicode):
            test_file = compat.unicode(test_file)
        test_file = self.get_test_loc(test_file)
        test_dir = self.get_temp_dir()
        warnings = test_function(test_file, test_dir)

        # shortcut if check of warnings are requested
        if self.check_only_warnings and expected_warnings is not None:
            assert sorted(expected_warnings) == sorted(warnings)
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
            with open(expected_file, 'wb') as ef:
                ef.write(json.dumps(extracted, indent=2))

        expected = json.loads(open(expected_file).read())
        expected = [p for p in expected if p.strip()]
        assert expected == extracted


@skipIf(not on_linux, 'Run only on Linux because of specific test expectations.')
class TestExtractArchiveWithIllegalFilenamesWithLibarchiveOnLinux(ExtractArchiveWithIllegalFilenamesTestCase):
    check_only_warnings = False

    def test_extract_7zip_with_weird_filenames_with_libarchive(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.7z')
        self.check_extract(libarchive2.extract, test_file, expected_warnings=[], expected_suffix='libarch')

    def test_extract_ar_with_weird_filenames_with_libarchive(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.ar')
        warns = ['None: \nIncorrect file header signature']
        self.check_extract(libarchive2.extract, test_file, expected_warnings=warns, expected_suffix='libarch')

    def test_extract_cpio_with_weird_filenames_with_libarchive(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.cpio')
        self.check_extract(libarchive2.extract, test_file, expected_warnings=[], expected_suffix='libarch')

    def test_extract_tar_with_weird_filenames_with_libarchive(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.tar')
        self.check_extract(libarchive2.extract, test_file, expected_warnings=[], expected_suffix='libarch')

    def test_extract_zip_with_weird_filenames_with_libarchive(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.zip')
        self.check_extract(libarchive2.extract, test_file, expected_warnings=[], expected_suffix='libarch')


@skipIf(not on_linux, 'Run only on Linux because of specific test expectations.')
class TestExtractArchiveWithIllegalFilenamesWithLibarchiveOnLinuxWarnings(TestExtractArchiveWithIllegalFilenamesWithLibarchiveOnLinux):
    check_only_warnings = True


@skipIf(not on_mac, 'Run only on Mac because of specific test expectations.')
class TestExtractArchiveWithIllegalFilenamesWithLibarchiveOnMac(ExtractArchiveWithIllegalFilenamesTestCase):
    check_only_warnings = False

    def test_extract_7zip_with_weird_filenames_with_libarchive(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.7z')
        self.check_extract(libarchive2.extract, test_file, expected_warnings=[], expected_suffix='libarch')

    def test_extract_ar_with_weird_filenames_with_libarchive(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.ar')
        warns = ['None: \nIncorrect file header signature']
        self.check_extract(libarchive2.extract, test_file, expected_warnings=warns, expected_suffix='libarch')

    def test_extract_cpio_with_weird_filenames_with_libarchive(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.cpio')
        self.check_extract(libarchive2.extract, test_file, expected_warnings=[], expected_suffix='libarch')

    def test_extract_tar_with_weird_filenames_with_libarchive(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.tar')
        self.check_extract(libarchive2.extract, test_file, expected_warnings=[], expected_suffix='libarch')

    def test_extract_zip_with_weird_filenames_with_libarchive(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.zip')
        self.check_extract(libarchive2.extract, test_file, expected_warnings=[], expected_suffix='libarch')


@skipIf(not on_mac, 'Run only on Mac because of specific test expectations.')
class TestExtractArchiveWithIllegalFilenamesWithLibarchiveOnMacWarnings(TestExtractArchiveWithIllegalFilenamesWithLibarchiveOnMac):
    check_only_warnings = True


@skipIf(not on_windows, 'Run only on Windows because of specific test expectations.')
class TestExtractArchiveWithIllegalFilenamesWithLibarchiveOnWindows(ExtractArchiveWithIllegalFilenamesTestCase):
    check_only_warnings = False

    def test_extract_7zip_with_weird_filenames_with_libarchive(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.7z')
        self.check_extract(libarchive2.extract, test_file, expected_warnings=[], expected_suffix='libarch')

    def test_extract_ar_with_weird_filenames_with_libarchive(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.ar')
        warns = [u'None: \nIncorrect file header signature']
        self.check_extract(libarchive2.extract, test_file, expected_warnings=warns, expected_suffix='libarch')

    def test_extract_cpio_with_weird_filenames_with_libarchive(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.cpio')
        self.check_extract(libarchive2.extract, test_file, expected_warnings=[], expected_suffix='libarch')

    def test_extract_tar_with_weird_filenames_with_libarchive(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.tar')
        self.check_extract(libarchive2.extract, test_file, expected_warnings=[], expected_suffix='libarch')

    def test_extract_zip_with_weird_filenames_with_libarchive(self):
        test_file = self.get_test_loc('archive/weird_names/weird_names.zip')
        self.check_extract(libarchive2.extract, test_file, expected_warnings=[], expected_suffix='libarch')
