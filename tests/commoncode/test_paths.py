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

from unittest import TestCase

from commoncode import paths


class TestPortablePath(TestCase):

    def test_safe_path(self):
        # tuples of test data, expected results
        tests = [
         # mixed slashes
        (r'C:\Documents and Settings\Boki\Desktop\head\patches\drupal6/drupal.js',
          'c_/documents_and_settings/boki/desktop/head/patches/drupal6/drupal.js'),
         # mixed slashes and spaces
        (r'C:\Documents and Settings\Boki\Desktop\head\patches\parallel uploads/drupal.js',
          'c_/documents_and_settings/boki/desktop/head/patches/parallel_uploads/drupal.js'),
         # windows style
        (r'C:\Documents and Settings\Administrator\Desktop\siftDemoV4_old\defs.h',
          'c_/documents_and_settings/administrator/desktop/siftdemov4_old/defs.h'),
         # windows style, mixed slashes, no spaces
        (r'C:\Documents and Settings\Boki\Desktop\head\patches\imagefield/imagefield.css',
          'c_/documents_and_settings/boki/desktop/head/patches/imagefield/imagefield.css'),
         # windows style, spaces
        (r'C:\Documents and Settings\Boki\Desktop\head\patches\js delete\imagefield.css',
          'c_/documents_and_settings/boki/desktop/head/patches/js_delete/imagefield.css'),
         # windows style, posix slashes
        (r'C:/Documents and Settings/Alex Burgel/workspace/Hibernate3.2/test/org/hibernate/test/AllTests.java',
          'c_/documents_and_settings/alex_burgel/workspace/hibernate3.2/test/org/hibernate/test/alltests.java'),
         # windows style, relative
        (r'includes\webform.components.inc',
          'includes/webform.components.inc'),
         # windows style, absolute, trailing slash
        ('\\includes\\webform.components.inc\\',
          'includes/webform.components.inc'),
         # posix style, relative
        (r'includes/webform.components.inc',
          'includes/webform.components.inc'),
         # posix style, absolute, trailing slash
        (r'/includes/webform.components.inc/',
          'includes/webform.components.inc'),
         # posix style, french char
        ('/includes/webform.compon\xc3nts.inc/',
          'includes/webform.compon_nts.inc'),
         # posix style, chinese char
        ('/includes/webform.compon\xd2\xaants.inc/',
          'includes/webform.compon__nts.inc'),
         # windows style, dots
        ('\\includes\\..\\webform.components.inc\\',
          'webform.components.inc'),
         # windows style, many dots
        ('.\\includes\\.\\..\\..\\..\webform.components.inc\\.',
          'dotdot/dotdot/webform.components.inc'),
         # posix style, dots
        (r'includes/../webform.components.inc',
          'webform.components.inc'),
         # posix style, many dots
        (r'./includes/./../../../../webform.components.inc/.',
          'dotdot/dotdot/dotdot/webform.components.inc'),
        ]
        for tst, expected in tests:
            assert expected == paths.safe_path(tst)

    def test_resolve(self):
        # tuples of test data, expected results
        tests = [
        ('C:\\..\\./drupal.js',
         'drupal.js'),
        ('\\includes\\..\\webform.components.inc\\',
        'webform.components.inc'),
        ('includes/../webform.components.inc',
         'webform.components.inc'),
        ('////.//includes/./../..//..///../webform.components.inc/.',
        'dotdot/dotdot/dotdot/webform.components.inc'),
        (u'////.//includes/./../..//..///../webform.components.inc/.',
         u'dotdot/dotdot/dotdot/webform.components.inc'),
        ('includes/../',
        '.'),
        ]
        for tst, expected in tests:
            assert expected == paths.resolve(tst)


class TestCommonPath(TestCase):

    def test_common_path_prefix1(self):
        test = paths.common_path_prefix('/a/b/c', '/a/b/c')
        assert ('a/b/c', 3) == test

    def test_common_path_prefix2(self):
        test = paths.common_path_prefix('/a/b/c', '/a/b')
        assert ('a/b', 2) == test

    def test_common_path_prefix3(self):
        test = paths.common_path_prefix('/a/b', '/a/b/c')
        assert ('a/b', 2) == test

    def test_common_path_prefix4(self):
        test = paths.common_path_prefix('/a', '/a')
        assert ('a', 1) == test

    def test_common_path_prefix_path_root(self):
        test = paths.common_path_prefix('/a/b/c', '/')
        assert (None, 0) == test

    def test_common_path_prefix_root_path(self):
        test = paths.common_path_prefix('/', '/a/b/c')
        assert (None, 0) == test

    def test_common_path_prefix_root_root(self):
        test = paths.common_path_prefix('/', '/')
        assert (None, 0) == test

    def test_common_path_prefix_path_elements_are_similar(self):
        test = paths.common_path_prefix('/a/b/c', '/a/b/d')
        assert ('a/b', 2) == test

    def test_common_path_prefix_no_match(self):
        test = paths.common_path_prefix('/abc/d', '/abe/f')
        assert (None, 0) == test

    def test_common_path_prefix_ignore_training_slashes(self):
        test = paths.common_path_prefix('/a/b/c/', '/a/b/c/')
        assert ('a/b/c', 3) == test

    def test_common_path_prefix8(self):
        test = paths.common_path_prefix('/a/b/c/', '/a/b')
        assert ('a/b', 2) == test

    def test_common_path_prefix10(self):
        test = paths.common_path_prefix('/a/b/c.txt', '/a/b/b.txt')
        assert ('a/b', 2) == test

    def test_common_path_prefix11(self):
        test = paths.common_path_prefix('/a/b/c.txt', '/a/b.txt')
        assert ('a', 1) == test

    def test_common_path_prefix12(self):
        test = paths.common_path_prefix('/a/c/e/x.txt', '/a/d/a.txt')
        assert ('a', 1) == test

    def test_common_path_prefix13(self):
        test = paths.common_path_prefix('/a/c/e/x.txt', '/a/d/')
        assert ('a', 1) == test

    def test_common_path_prefix14(self):
        test = paths.common_path_prefix('/a/c/e/', '/a/d/')
        assert ('a', 1) == test

    def test_common_path_prefix15(self):
        test = paths.common_path_prefix('/a/c/e/', '/a/c/a.txt')
        assert ('a/c', 2) == test

    def test_common_path_prefix16(self):
        test = paths.common_path_prefix('/a/c/e/', '/a/c/f/')
        assert ('a/c', 2) == test

    def test_common_path_prefix17(self):
        test = paths.common_path_prefix('/a/a.txt', '/a/b.txt/')
        assert ('a', 1) == test

    def test_common_path_prefix18(self):
        test = paths.common_path_prefix('/a/c/', '/a/')
        assert ('a', 1) == test

    def test_common_path_prefix19(self):
        test = paths.common_path_prefix('/a/c.txt', '/a/')
        assert ('a', 1) == test

    def test_common_path_prefix20(self):
        test = paths.common_path_prefix('/a/c/', '/a/d/')
        assert ('a', 1) == test

    def test_common_path_suffix(self):
        test = paths.common_path_suffix('/a/b/c', '/a/b/c')
        assert ('a/b/c', 3) == test

    def test_common_path_suffix_absolute_relative(self):
        test = paths.common_path_suffix('a/b/c', '/a/b/c')
        assert ('a/b/c', 3) == test

    def test_common_path_suffix_find_subpath(self):
        test = paths.common_path_suffix('/z/b/c', '/a/b/c')
        assert ('b/c', 2) == test

    def test_common_path_suffix_handles_relative_path(self):
        test = paths.common_path_suffix('a/b', 'a/b')
        assert ('a/b', 2) == test

    def test_common_path_suffix_handles_relative_subpath(self):
        test = paths.common_path_suffix('zsds/adsds/a/b/b/c',
                                                     'a//a/d//b/c')
        assert ('b/c', 2) == test

    def test_common_path_suffix_ignore_and_strip_trailing_slash(self):
        test = paths.common_path_suffix('zsds/adsds/a/b/b/c/',
                                                     'a//a/d//b/c/')
        assert ('b/c', 2) == test

    def test_common_path_suffix_return_None_if_no_common_suffix(self):
        test = paths.common_path_suffix('/a/b/c', '/')
        assert (None, 0) == test

    def test_common_path_suffix_return_None_if_no_common_suffix2(self):
        test = paths.common_path_suffix('/', '/a/b/c')
        assert (None, 0) == test

    def test_common_path_suffix_match_only_whole_segments(self):
        # only segments are honored, commonality within segment is ignored
        test = paths.common_path_suffix(
            'this/is/aaaa/great/path', 'this/is/aaaaa/great/path')
        assert ('great/path', 2) == test

    def test_common_path_suffix_two_root(self):
        test = paths.common_path_suffix('/', '/')
        assert (None, 0) == test

    def test_common_path_suffix_empty_root(self):
        test = paths.common_path_suffix('', '/')
        assert (None, 0) == test

    def test_common_path_suffix_root_empty(self):
        test = paths.common_path_suffix('/', '')
        assert (None, 0) == test

    def test_common_path_suffix_empty_empty(self):
        test = paths.common_path_suffix('', '')
        assert (None, 0) == test
