#
# Copyright (c) nexB Inc. and others.
# SPDX-License-Identifier: Apache-2.0
#
# Visit https://aboutcode.org and https://github.com/nexB/ for support and download.
# ScanCode is a trademark of nexB Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from unittest import TestCase

from commoncode import paths


class TestPortablePath(TestCase):

    def test_safe_path_mixed_slashes(self):
        test = paths.safe_path('C:\\Documents and Settings\\Boki\\Desktop\\head\\patches\\drupal6/drupal.js')
        expected = 'C/Documents_and_Settings/Boki/Desktop/head/patches/drupal6/drupal.js'
        assert expected == test

    def test_safe_path_mixed_slashes_and_spaces(self):
        test = paths.safe_path('C:\\Documents and Settings\\Boki\\Desktop\\head\\patches\\parallel uploads/drupal.js')
        expected = 'C/Documents_and_Settings/Boki/Desktop/head/patches/parallel_uploads/drupal.js'
        assert expected == test

    def test_safe_path_windows_style(self):
        test = paths.safe_path('C:\\Documents and Settings\\Administrator\\Desktop\\siftDemoV4_old\\defs.h')
        expected = 'C/Documents_and_Settings/Administrator/Desktop/siftDemoV4_old/defs.h'
        assert expected == test

    def test_safe_path_windows_style_mixed_slashes_no_spaces(self):
        test = paths.safe_path('C:\\Documents and Settings\\Boki\\Desktop\\head\\patches\\imagefield/imagefield.css')
        expected = 'C/Documents_and_Settings/Boki/Desktop/head/patches/imagefield/imagefield.css'
        assert expected == test

    def test_safe_path_windows_style_spaces(self):
        test = paths.safe_path('C:\\Documents and Settings\\Boki\\Desktop\\head\\patches\\js delete\\imagefield.css')
        expected = 'C/Documents_and_Settings/Boki/Desktop/head/patches/js_delete/imagefield.css'
        assert expected == test

    def test_safe_path_windows_style_posix_slashes(self):
        test = paths.safe_path('C:/Documents and Settings/Alex Burgel/workspace/Hibernate3.2/test/org/hibernate/test/AllTests.java')
        expected = 'C/Documents_and_Settings/Alex_Burgel/workspace/Hibernate3.2/test/org/hibernate/test/AllTests.java'
        assert expected == test

    def test_safe_path_windows_style_relative(self):
        test = paths.safe_path('includes\\webform.components.inc')
        expected = 'includes/webform.components.inc'
        assert expected == test

    def test_safe_path_windows_style_absolute_trailing_slash(self):
        test = paths.safe_path('\\includes\\webform.components.inc\\')
        expected = 'includes/webform.components.inc'
        assert expected == test

    def test_safe_path_posix_style_relative(self):
        test = paths.safe_path('includes/webform.components.inc')
        expected = 'includes/webform.components.inc'
        assert expected == test

    def test_safe_path_posix_style_absolute_trailing_slash(self):
        test = paths.safe_path('/includes/webform.components.inc/')
        expected = 'includes/webform.components.inc'
        assert expected == test

    def test_safe_path_posix_style_french_char(self):
        test = paths.safe_path('/includes/webform.compon\xc3nts.inc/')
        expected = 'includes/webform.componAnts.inc'
        assert expected == test

    def test_safe_path_posix_style_chinese_char(self):
        test = paths.safe_path(b'/includes/webform.compon\xd2\xaants.inc/')
        expected = 'includes/webform.componS_nts.inc'
        assert expected == test

    def test_safe_path_windows_style_dots(self):
        test = paths.safe_path('\\includes\\..\\webform.components.inc\\')
        expected = 'webform.components.inc'
        assert expected == test

    def test_safe_path_windows_style_many_dots(self):
        test = paths.safe_path('.\\includes\\.\\..\\..\\..\\webform.components.inc\\.')
        expected = 'dotdot/dotdot/webform.components.inc'
        assert expected == test

    def test_safe_path_posix_style_dots(self):
        test = paths.safe_path('includes/../webform.components.inc')
        expected = 'webform.components.inc'
        assert expected == test

    def test_safe_path_posix_style_many_dots(self):
        test = paths.safe_path('./includes/./../../../../webform.components.inc/.')
        expected = 'dotdot/dotdot/dotdot/webform.components.inc'
        assert expected == test

    def test_resolve_mixed_slash(self):
        test = paths.resolve('C:\\..\\./drupal.js')
        expected = 'C/drupal.js'
        assert expected == test

    def test_resolve_2(self):
        test = paths.resolve('\\includes\\..\\webform.components.inc\\')
        expected = 'webform.components.inc'
        assert expected == test

    def test_resolve_3(self):
        test = paths.resolve('includes/../webform.components.inc')
        expected = 'webform.components.inc'
        assert expected == test

    def test_resolve_4(self):
        test = paths.resolve('////.//includes/./../..//..///../webform.components.inc/.')
        expected = 'dotdot/dotdot/dotdot/webform.components.inc'
        assert expected == test

    def test_resolve_5(self):
        test = paths.resolve(u'////.//includes/./../..//..///../webform.components.inc/.')
        expected = u'dotdot/dotdot/dotdot/webform.components.inc'
        assert expected == test

    def test_resolve_6(self):
        test = paths.resolve('includes/../')
        expected = '.'
        assert expected == test

    def test_portable_filename(self):
        expected = 'A___file__with_Spaces.mov'
        assert expected == paths.portable_filename("A:\\ file/ with Spaces.mov")

        # Unresolved relative paths will be treated as a single filename. Use
        # resolve instead if you want to resolve paths:
        expected = '___.._.._etc_passwd'
        assert expected == paths.portable_filename("../../../etc/passwd")

        # Unicode name are transliterated:
        expected = 'This_contain_UMLAUT_umlauts.txt'
        assert expected == paths.portable_filename(u'This contain UMLAUT \xfcml\xe4uts.txt')


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
        test = paths.common_path_suffix('zsds/adsds/a/b/b/c', 'a//a/d//b/c')
        assert ('b/c', 2) == test

    def test_common_path_suffix_ignore_and_strip_trailing_slash(self):
        test = paths.common_path_suffix('zsds/adsds/a/b/b/c/', 'a//a/d//b/c/')
        assert ('b/c', 2) == test

    def test_common_path_suffix_return_None_if_no_common_suffix(self):
        test = paths.common_path_suffix('/a/b/c', '/')
        assert (None, 0) == test

    def test_common_path_suffix_return_None_if_no_common_suffix2(self):
        test = paths.common_path_suffix('/', '/a/b/c')
        assert (None, 0) == test

    def test_common_path_suffix_match_only_whole_segments(self):
        # only segments are honored, commonality within segment is ignored
        test = paths.common_path_suffix('this/is/aaaa/great/path', 'this/is/aaaaa/great/path')
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
