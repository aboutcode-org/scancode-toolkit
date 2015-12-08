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

from commoncode.testcase import FileBasedTesting

from textcode import strings


class TestStrings(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_to_filter(self):
        assert strings.filter_string('aw w we ww ')
        assert not strings.filter_string('w as wew wee wew ')
        assert strings.filter_string('as we we we ', 2)
        assert not strings.filter_string('as we we we ', 1)
        assert not strings.filter_string('asw wew wee wew ')
        assert strings.filter_strict('asw wew wee wew ')
        assert strings.filter_string('aaaa')
        assert not strings.filter_strict('aaaaqa')

    def test_is_good(self):
        assert not strings.is_good('aw w we ww ')
        assert strings.is_good('ww asww wew wee wew ')
        assert not strings.is_good('asw wew wee wew ', strings.filter_strict)
        assert strings.is_good('gnu as')
        assert strings.is_good('gnu as', strings.filter_strict)
        assert not strings.is_good('aaqa', strings.filter_strict)
        assert strings.is_good('aaqa')

    def test_strings_in_file(self):
        expected = [
            u'__text',
            u'__TEXT',
            u'__cstring',
            u'__TEXT',
            u'__jump_table',
            u'__IMPORT',
            u'__textcoal_nt',
            u'__TEXT',
            u'_main',
            u'___i686.get_pc_thunk.bx',
            u'_setlocale',
            u'_yyparse',
            u'/sw/src/fink.build/bison-2.3-1002/bison-2.3/lib/',
            u'main.c',
            u'gcc2_compiled.',
            u'main:F(0,2)',
            u'int:t(0,2)=r(0,2);-2147483648;2147483647;'
        ]

        test_file = self.get_test_loc('strings/basic/main.o')
        result = list(strings.strings_in_file(test_file))
        assert expected == result

    def test_strings_in_file_does_fail_if_contains_ERROR_string(self):
        test_file = self.get_test_loc('strings/bin/file_stripped')
        list(strings.strings_in_file(test_file))

    def test_file_strings_is_good(self):
        expected = [
            u'__text',
            u'__TEXT',
            u'__cstring',
            u'__TEXT',
            u'__jump_table',
            u'__IMPORT',
            u'__textcoal_nt',
            u'__TEXT',
            u'_main',
            u'___i686.get_pc_thunk.bx',
            u'_setlocale',
            u'_yyparse',
            u'/sw/src/fink.build/bison-2.3-1002/bison-2.3/lib/',
            u'main.c',
            u'gcc2_compiled.',
            u'main:F(0,2)',
            u'int:t(0,2)=r(0,2);-2147483648;2147483647;'
        ]

        test_file = self.get_test_loc('strings/basic/main.o')
        result = [s for s in strings.file_strings(test_file)
                  if strings.is_good(s)]
        assert expected == result

    def test_strings_in_fonts(self):
        expected = self.get_test_loc('strings/font/DarkGardenMK.ttf.results')
        expected = open(expected, 'rb').read().splitlines()
        test_file = self.get_test_loc('strings/font/DarkGardenMK.ttf')
        result = [s for s in strings.file_strings(test_file)
                  if strings.is_good(s)]

        assert sorted(expected) == sorted(result)

    def test_strings_in_elf(self):
        test_file = self.get_test_loc('strings/elf/shash.i686')
        result = [s for s in strings.file_strings(test_file)
                  if strings.is_good(s)]
        expected = self.get_test_loc('strings/elf/shash.i686.results')
#         with open(expected, 'wb') as o:
#             o.write('\n'.join(result))
        expected = open(expected, 'rb').read().splitlines()
        assert sorted(expected) == sorted(result)

    def test_strings_in_obj(self):
        test_file = self.get_test_loc('strings/obj/test.o')
        result = [s for s in strings.file_strings(test_file)
                  if strings.is_good(s)]
        expected = self.get_test_loc('strings/obj/test.o.results')
#         with open(expected, 'wb') as o:
#             o.write('\n'.join(result))
        expected = open(expected, 'rb').read().splitlines()
        assert sorted(expected) == sorted(result)

    def test_strings_in_windows_pdb(self):
        test_file = self.get_test_loc('strings/pdb/QTMovieWin.pdb')
        result = list(strings.file_strings(test_file))
        expected = self.get_test_loc('strings/pdb/QTMovieWin.pdb.results')
#         with open(expected, 'wb') as o:
#             o.write('\n'.join(result))
        expected = open(expected, 'rb').read().splitlines()
        assert sorted(expected) == sorted(result)

    def test_strings_in_all_bin(self):
        test_dir = self.get_test_loc('strings/bin', copy=True)
        expec_dir = self.get_test_loc('strings/bin-expected')
        for tf in os.listdir(test_dir):
            result = list(strings.file_strings(os.path.join(test_dir, tf)))
            expected = os.path.join(expec_dir, tf + '.strings')
#             with open(expected, 'wb') as o:
#                 o.write('\n'.join(result))
            expected = open(expected, 'rb').read().splitlines()
            assert sorted(expected) == sorted(result)
