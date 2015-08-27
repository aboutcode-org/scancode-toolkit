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

from textcode import analysis
from textcode .analysis import Token

from licensedcode import detect
from licensedcode.detect import LicenseMatch
from licensedcode.models import Rule
from licensedcode import models
from unittest.case import skipIf

"""
Tests the core detection mechanics.
"""

class TestLicenseMatch(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_single_contained_matche_is_filtered(self):
        r1 = Rule(licenses=['apache-2.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, query_position=analysis.Token(start=0, end=5))
        contained = LicenseMatch(rule=r1, query_position=analysis.Token(start=1, end=4))
        m5 = LicenseMatch(rule=r1, query_position=analysis.Token(start=1, end=6))

        test = detect.filter_matches([m1, contained, m5])
        self.assertEqual([m1, m5], test)

    def test_multiple_contained_matches_are_filtered(self):
        r1 = Rule(licenses=['apache-2.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, query_position=analysis.Token(start=0, end=5))
        contained1 = LicenseMatch(rule=r1, query_position=analysis.Token(start=1, end=2))
        contained2 = LicenseMatch(rule=r1, query_position=analysis.Token(start=3, end=4))
        m5 = LicenseMatch(rule=r1, query_position=analysis.Token(start=1, end=6))

        test = detect.filter_matches([m1, contained1, contained2, m5])
        self.assertEqual([m1, m5], test)

    def test_multiple_nested_contained_matches_are_filtered(self):
        r1 = Rule(licenses=['apache-2.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, query_position=analysis.Token(start=0, end=5))
        contained = LicenseMatch(rule=r1, query_position=analysis.Token(start=1, end=4))
        in_contained = LicenseMatch(rule=r1, query_position=analysis.Token(start=2, end=3))
        m5 = LicenseMatch(rule=r1, query_position=analysis.Token(start=1, end=6))

        test = detect.filter_matches([m1, contained, in_contained, m5])
        self.assertEqual([m1, m5], test)

    def test_overlapping_matches_are_filtered(self):
        r1 = Rule(licenses=['apache-2.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, query_position=analysis.Token(start=0, end=5))
        same_span = LicenseMatch(rule=r1, query_position=analysis.Token(start=1, end=6))
        same_span_too = LicenseMatch(rule=r1, query_position=analysis.Token(start=1, end=6))

        test = detect.filter_matches([m1, same_span, same_span_too])
        self.assertEqual([m1, same_span], test)

    def test_contiguous_non_overlapping_matches_are_not_filtered(self):
        r1 = Rule(licenses=['apache-2.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, query_position=analysis.Token(start=0, end=2))
        m2 = LicenseMatch(rule=r1, query_position=analysis.Token(start=3, end=6))
        m5 = LicenseMatch(rule=r1, query_position=analysis.Token(start=1, end=6))

        self.assertEqual([m1, m5], detect.filter_matches([m1, m2, m5]))

    def test_non_contiguous_matches_are_not_filtered(self):
        r1 = Rule(licenses=['apache-2.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, query_position=analysis.Token(start=0, end=2))
        m2 = LicenseMatch(rule=r1, query_position=analysis.Token(start=4, end=6))
        m5 = LicenseMatch(rule=r1, query_position=analysis.Token(start=1, end=6))

        self.assertEqual([m1, m5], detect.filter_matches([m1, m2, m5]))

    def test_non_contiguous_or_overlapping_contained_matches_are_filtered(self):
        r1 = Rule(licenses=['apache-2.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, query_position=analysis.Token(start=1, end=2))
        m2 = LicenseMatch(rule=r1, query_position=analysis.Token(start=3, end=6))
        m3 = LicenseMatch(rule=r1, query_position=analysis.Token(start=1, end=6))
        m4 = LicenseMatch(rule=r1, query_position=analysis.Token(start=0, end=7))
        m5 = LicenseMatch(rule=r1, query_position=analysis.Token(start=1, end=6))

        self.assertEqual([m4], detect.filter_matches([m1, m2, m3, m4, m5]))

    def test_non_contiguous_or_overlapping_contained_matches_touching_boundaries_are_filtered(self):
        r1 = Rule(licenses=['apache-2.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, query_position=analysis.Token(start=0, end=2))
        m2 = LicenseMatch(rule=r1, query_position=analysis.Token(start=3, end=7))
        m3 = LicenseMatch(rule=r1, query_position=analysis.Token(start=0, end=6))
        m6 = LicenseMatch(rule=r1, query_position=analysis.Token(start=1, end=7))
        m4 = LicenseMatch(rule=r1, query_position=analysis.Token(start=0, end=7))
        m5 = LicenseMatch(rule=r1, query_position=analysis.Token(start=1, end=6))

        self.assertEqual([m4], detect.filter_matches([m1, m2, m3, m4, m5, m6]))

    def test_matches_with_same_span_are_kept_if_licenses_are_different(self):
        r1 = Rule(licenses=['apache-2.0'])
        m1 = LicenseMatch(rule=r1, query_position=analysis.Token(start=0, end=2))
        r2 = Rule(licenses=['apache-1.1'])
        m2 = LicenseMatch(rule=r2, query_position=analysis.Token(start=0, end=2))
        m5 = LicenseMatch(rule=r1, query_position=analysis.Token(start=1, end=6))

        self.assertEqual([m1, m2, m5], detect.filter_matches([m1, m2, m5]))

    def test_matches_with_same_span_are_filtered_if_licenses_are_the_same(self):
        r1 = Rule(licenses=['apache-2.0'])
        m1 = LicenseMatch(rule=r1, query_position=analysis.Token(start=0, end=2))
        r2 = Rule(licenses=['apache-2.0'])
        m2 = LicenseMatch(rule=r2, query_position=analysis.Token(start=0, end=2))
        m5 = LicenseMatch(rule=r1, query_position=analysis.Token(start=1, end=6))

        self.assertEqual([m1, m5], detect.filter_matches([m1, m2, m5]))

    def test_matches_with_same_span_are_filtered_if_licenses_are_the_same2(self):
        r1 = Rule(licenses=['apache-2.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, query_position=analysis.Token(start=0, end=2))
        r2 = Rule(licenses=['gpl', 'apache-2.0'])
        m2 = LicenseMatch(rule=r2, query_position=analysis.Token(start=0, end=2))
        m5 = LicenseMatch(rule=r1, query_position=analysis.Token(start=1, end=6))

        self.assertEqual([m1, m5], detect.filter_matches([m1, m2, m5]))

    def test_matches_with_partially_overlapping_spans_are_merged_if_license_are_the_same(self):
        r1 = Rule(licenses=['apache-1.1'])
        r2 = Rule(licenses=['gpl', 'apache-2.0'])

        m1 = LicenseMatch(rule=r1, query_position=analysis.Token(start=0, end=10))
        m2 = LicenseMatch(rule=r1, query_position=analysis.Token(start=1, end=6))

        m3 = LicenseMatch(rule=r2, query_position=analysis.Token(start=5, end=15))

        self.assertEqual([m1, m3], detect.filter_matches([m1, m2, m3]))

    def test_match_is_same(self):
        r1 = Rule(licenses=['apache-2.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, query_position=analysis.Token(start=0, end=2))
        r2 = Rule(licenses=['gpl', 'apache-2.0'])
        m2 = LicenseMatch(rule=r2, query_position=analysis.Token(start=0, end=2))

        self.assertTrue(m1.is_same(m2))
        self.assertTrue(m2.is_same(m1))

    def test_match_is_not_same(self):
        r1 = Rule(licenses=['apache-1.0', 'gpl'])
        m1 = LicenseMatch(rule=r1, query_position=analysis.Token(start=0, end=2))
        r2 = Rule(licenses=['gpl', 'apache-2.0'])
        m2 = LicenseMatch(rule=r2, query_position=analysis.Token(start=0, end=2))

        self.assertFalse(m1.is_same(m2))
        self.assertFalse(m2.is_same(m1))

        r3 = Rule(licenses=['apache-1.0', 'gpl'])
        m3 = LicenseMatch(rule=r3, query_position=analysis.Token(start=0, end=2))

        self.assertTrue(m1.is_same(m3))
        self.assertTrue(m3.is_same(m1))

        r4 = Rule(licenses=['apache-1.0', 'gpl'])
        m4 = LicenseMatch(rule=r4, query_position=analysis.Token(start=1, end=2))

        self.assertFalse(m1.is_same(m4))
        self.assertFalse(m4.is_same(m1))


class TestDetectLicenseRule(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def create_test_file(self, text):
        tf = self.get_temp_file()
        with open(tf, 'wb') as of:
            of.write(text)
        return tf

    def test_match_with_empty_query_does_not_return_matches(self):
        ftr = Rule(text_file=self.create_test_file('A one. A two. A three.'))
        index = detect.LicenseIndex([ftr])
        matches = index.match([''])
        self.assertEqual([], matches)

    def test_match_does_not_return_incorrect_matches(self):
        ftr = Rule(text_file=self.create_test_file('A one. A two. A three.'))
        index = detect.LicenseIndex([ftr])
        docs = [
            u'some other path', u'some junk',
            u'some path', u'some other junk'
        ]
        for d in docs:
            matches = index.match([d])
            self.assertEqual([], matches)

    def test_match_index_return_one_match_with_correct_offsets(self):
        ftr = Rule(text_file=self.create_test_file('A one. A two. A three.'))
        index = detect.LicenseIndex([ftr])
        doc1 = (u'/some/path/', u'some junk. A one. A two. A three.')
        #                                    1111111111222222222233
        #                         012345678901234567890123456789012

        matches = index.match([doc1[1]])
        self.assertEqual(1, len(matches))

        self.assertEqual(11, matches[0].query_position.start_char)
        self.assertEqual(32, matches[0].query_position.end_char)

    def test_simple_detection_against_same_text(self):
        tf1 = self.get_test_loc('detect/mit/mit.c')
        ftr = Rule(text_file=tf1, licenses=['mit'])
        index = detect.LicenseIndex([ftr])

        matches = index.match(tf1)
        assert 1 == len(matches)
        match = matches[0]
        assert ftr == match.rule
        assert 0 == match.span.start
        assert 86 == match.span.end

    def test_simple_detection1(self):
        tf1 = self.get_test_loc('detect/mit/mit.c')
        ftr = Rule(text_file=tf1, licenses=['mit'])
        index = detect.LicenseIndex([ftr])

        tf2 = self.get_test_loc('detect/mit/mit2.c')
        matches = index.match(tf2)
        assert 1 == len(matches)
        match = matches[0]
        assert ftr == match.rule
        assert 5 == match.span.start
        assert 91 == match.span.end

    def test_simple_detection2(self):
        tf1 = self.get_test_loc('detect/mit/mit.c')
        ftr = Rule(text_file=tf1, licenses=['mit'])
        index = detect.LicenseIndex([ftr])

        tf2 = self.get_test_loc('detect/mit/mit3.c')
        matches = index.match(tf2)
        assert 1 == len(matches)
        match = matches[0]
        assert ftr == match.rule
        assert 0 == match.span.start
        assert 86 == match.span.end

    def test_simple_detection_no_result(self):
        tf1 = self.get_test_loc('detect/mit/mit.c')
        ftr = Rule(text_file=tf1, licenses=['mit'])
        index = detect.LicenseIndex([ftr])

        tf2 = self.get_test_loc('detect/mit/mit4.c')
        matches = index.match(tf2)
        assert not matches

    def test_simple_detection_text_shorter_than_ngram_len_using_trigrams(self):
        tf1 = self.get_test_loc('detect/string/mit.txt')
        ftr = Rule(text_file=tf1, licenses=['mit'])
        index = detect.LicenseIndex([ftr])  # default to ngram_len=3

        tf2 = self.get_test_loc('detect/string/mit2.txt')
        tf3 = self.get_test_loc('detect/string/mit3.txt')
        tf4 = self.get_test_loc('detect/string/mit4.txt')

        docs = [
            (tf1, 1, [Token(start=0, start_line=1, start_char=0, end_line=1, end_char=11, end=1)]),
            (tf4, 1, [Token(start=1, start_line=1, start_char=4, end_line=1, end_char=15, end=2)]),
            (tf2, 2, [Token(start=6, start_line=1, start_char=20, end_line=1, end_char=31, end=7),
                      Token(start=8, start_line=1, start_char=32, end_line=1, end_char=43, end=9)]),
            (tf3, 2, [Token(start=6, start_line=1, start_char=20, end_line=1, end_char=31, end=7),
                      Token(start=8, start_line=2, start_char=0, end_line=2, end_char=11, end=9)]),
        ]

        for loc, expect_mlen, expect_matches_posits in docs:
            matches = list(index.match(loc, perfect=True))
            self.assertEqual(expect_mlen, len(matches))
            for i, m in enumerate(matches):
                expected_pos = expect_matches_posits[i]
                assert expected_pos == m.query_position

    def test_bsd_rule_detection(self):
        tf1 = self.get_test_loc('detect/mit/t1.txt')
        ftr = Rule(text_file=tf1, licenses=['bsd-original'])
        index = detect.LicenseIndex([ftr])

        test_doc = self.get_test_loc('detect/mit/t2.txt')
        matches = index.match(test_doc)
        self.assertEqual(1, len(matches))
        expected = Token(start=0, start_line=1, start_char=0, end_line=27, end_char=59, end=241)
        self.assertEqual(expected, matches[0].query_position)

    def check_detection(self, doc_file, rule_file, expected_matches):
        test_rule = self.get_test_loc(rule_file)
        ftr = Rule(text_file=test_rule, licenses=['mit'])
        index = detect.LicenseIndex([ftr])

        test_doc = self.get_test_loc(doc_file)
        matches = index.match(test_doc)
        self.assertEqual(1, len(matches))
        self.assertEqual(expected_matches, matches[0].query_position)

    def test_comment_format_1(self):
        expected = Token(start=0, start_line=1, start_char=2, end_line=9, end_char=52, end=86)
        self.check_detection('detect/commentformat/license2.txt', 'detect/commentformat/license1.txt', expected)

    def test_comment_format_2(self):
        expected = Token(start=0, start_line=1, start_char=3, end_line=9, end_char=53, end=86)
        self.check_detection('detect/commentformat/license3.txt', 'detect/commentformat/license1.txt', expected)

    def test_comment_format_3(self):
        expected = Token(start=0, start_line=1, start_char=3, end_line=9, end_char=53, end=86)
        self.check_detection('detect/commentformat/license4.txt', 'detect/commentformat/license1.txt', expected)

    def test_comment_format_4(self):
        expected = Token(start=0, start_line=1, start_char=0, end_line=10, end_char=50, end=86)
        self.check_detection('detect/commentformat/license5.txt', 'detect/commentformat/license1.txt', expected)

    def test_comment_format_5(self):
        expected = Token(start=0, start_line=1, start_char=2, end_line=9, end_char=52, end=86)
        self.check_detection('detect/commentformat/license6.txt', 'detect/commentformat/license1.txt', expected)

    def test_comment_format_6(self):
        expected = Token(start=0, start_line=1, start_char=2, end_line=9, end_char=52, end=86)
        self.check_detection('detect/commentformat/license6.txt', 'detect/commentformat/license3.txt', expected)

    def test_special_characters_detection(self):
        tf1 = self.get_test_loc('detect/specialcharacter/kerberos.txt')
        tf2 = self.get_test_loc('detect/specialcharacter/kerberos1.txt')
        tf3 = self.get_test_loc('detect/specialcharacter/kerberos2.txt')
        tf4 = self.get_test_loc('detect/specialcharacter/kerberos3.txt')
        docs = [
            tf1,
            tf2,
            tf3,
            tf4
        ]

        for loc in docs:
            ftr = Rule(text_file=loc, licenses=['kerberos'])
            index = detect.LicenseIndex([ftr])
            matches = index.match(loc)
            self.assertEqual(1, len(matches))

    def test_overlap_detection(self):
        #  test this containment relationship between test and index licenses:
        #   * Index licenses:
        #
        #   +-license 2 --------+
        #   |  +-license 1 --+  |
        #   |  +-------------+  |
        #   +-------------------+
        #
        #   * License texts to detect:
        #
        #   +- license 3 -----------+
        #   | +-license 2 --------+ |
        #   | |  +-license 1 --+  | |
        #   | |  +-------------+  | |
        #   | +-------------------+ |
        #   +-----------------------+
        #
        #   +-license 4 --------+
        #   |  +-license 1 --+  |
        #   |  +-------------+  |
        #   +-------------------+

        tf1 = self.get_test_loc('detect/overlap/license.txt')
        tf2 = self.get_test_loc('detect/overlap/license2.txt')
        tf3 = self.get_test_loc('detect/overlap/license3.txt')
        tf4 = self.get_test_loc('detect/overlap/license4.txt')

        # setup index
        ftr1 = Rule(text_file=tf1, licenses=['overlap_license'])
        ftr2 = Rule(text_file=tf2, licenses=['overlap_license'])
        index = detect.LicenseIndex([ftr1, ftr2])

        # test : 1 contains nothing: return 1
        matches = index.match(tf1)
        self.assertEqual(1, len(matches))
        match = matches[0]
        self.assertEqual(ftr1, match.rule)

        # test : 2 contains 1: return 2
        matches = index.match(tf2)
        self.assertEqual(1, len(matches))
        match = matches[0]
        self.assertEqual(ftr2, match.rule)

        # test : 3 contains 2 that contains 1: return 2
        matches = index.match(tf3)
        self.assertEqual(1, len(matches))
        match = matches[0]
        self.assertEqual(ftr2, match.rule)

        # test : 4 contains 1: return 1
        matches = index.match(tf4)
        self.assertEqual(1, len(matches))
        match = matches[0]
        self.assertEqual(ftr1, match.rule)

    def test_fulltext_detection_works_with_partial_overlap_from_location(self):
        # setup
        test_rule = self.get_test_loc('detect/templates/license3.txt')
        ftr = Rule(text_file=test_rule, licenses=['mylicense'])
        index = detect.LicenseIndex([ftr])
        # test
        test_doc = self.get_test_loc('detect/templates/license4.txt')
        matches = index.match(test_doc)
        self.assertEqual(1, len(matches))
        expected = Token(start=1, start_line=1, start_char=7, end_line=4, end_char=67, end=42)
        self.assertEqual(expected, matches[0].query_position)


class TestDetectLicenseRuleTemplate(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def create_test_file(self, text):
        tf = self.get_temp_file()
        with open(tf, 'wb') as of:
            of.write(text)
        return tf

    def test_index_template(self):
        ttr = Rule(text_file=self.create_test_file(u'A one. A {{}}two. A three.'), template=True)
        index = detect.LicenseIndex([ttr])
        expected = {
            1: {},
            2: {},
            3: {u'two a three':
                   {0: [Token(start=3, start_line=0, start_char=13, end_line=0, end_char=25, end=5, gap=0, value=u'two a three', length=3)]
                   },
               u'a one a':
                   {0: [Token(start=0, start_line=0, start_char=0, end_line=0, end_char=8, end=2, gap=5, value=u'a one a', length=3)]}},
            4: {},
        }
        assert expected == index.license_index.indexes

    def test_index_template2(self):
        ttr = Rule(text_file=self.create_test_file(u'A one. A {{10}}two. A three.'), template=True)
        index = detect.LicenseIndex([ttr])
        expected = {
            u'a one a':
                {0: [Token(start=0, start_line=0, start_char=0, end_line=0, end_char=8, end=2, gap=10, value=u'a one a')]},
            u'two a three':
                {0: [Token(start=3, start_line=0, start_char=15, end_line=0, end_char=27, end=5, gap=0, value=u'two a three')]}
        }
        assert expected == index.license_index.indexes[3]

    def test_simple_detection_xcon_crlf_template(self):
        # setup
        tf1_text = u'''X11 License
        Copyright (C) 1996 X Consortium
        Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
        The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
        THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE X CONSORTIUM BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
        Except as contained in this notice, the name of the X Consortium shall not be used in advertising or otherwise to promote the sale, use or other dealings in this Software without prior written authorization from the X Consortium.
        X Window System is a trademark of X Consortium, Inc.
        '''
        ttr = Rule(text_file=self.create_test_file(tf1_text), licenses=['x-consortium'], template=True)
        index = detect.LicenseIndex([ttr])

        # test
        doc = self.get_test_loc('detect/simple_detection/x11-xconsortium_text.txt')
        matches = index.match(doc)
        expected = Token(start=0, start_line=1, start_char=0, end_line=13, end_char=51, end=216)
        self.assertEqual(expected, matches[0].query_position)

    def test_detection_template_with_inter_gap_smaller_than_ngram_len(self):
        # in this template text there are only 2 tokens between the two
        # templates: this is smaller than the ngram_len of 3 and can never be
        # caught by this length
        tf1_text = u'''Redistributions in binary form must
        {{}} reproduce the {{}}above copyright notice'''
        ttr = Rule(text_file=self.create_test_file(tf1_text), licenses=['mylicense'], template=True)
        index = detect.LicenseIndex([ttr])  # default to ngram_len=3

        # test
        tf2 = u'''Redistributions in binary form must nexB company
        reproduce the word for word above copyright notice.'''.splitlines()
        matches = index.match(tf2)
        expected = Token(start=0, start_line=1, start_char=0, end_line=2, end_char=58, end=14)
        self.assertEqual(1, len(matches))
        self.assertEqual(expected, matches[0].query_position)

    def test_detection_template_with_inter_gap_equal_to_ngram_len(self):
        # in this template there are 3 tokens between the two templates: len is
        # same as ngram_len of 3
        tf1_text = u'''Redistributions in binary form must
        {{}} reproduce the stipulated {{}}above copyright notice'''
        ttr = Rule(text_file=self.create_test_file(tf1_text), licenses=['mylicense'], template=True)
        index = detect.LicenseIndex([ttr])  # default to ngram_len=3

        # test
        tf2_text = (u'''Redistributions in binary form must nexB company
        reproduce the stipulated word for word above copyright notice.'''
        .splitlines())
        matches = index.match(tf2_text)
        expected = Token(start=0, start_line=1, start_char=0, end_line=2, end_char=69, end=15)
        self.assertEqual(1, len(matches))
        self.assertEqual(expected, matches[0].query_position)

    def test_detection_template_with_inter_gap_bigger_than_ngram_len(self):
        # setup in this template there are only 4 tokens between the two
        # templates: this is bigger than the ngram_len of 3
        tf1_text = u'''Redistributions in binary form must
        {{}} reproduce as is stipulated {{}}above copyright notice'''
        ttr = Rule(text_file=self.create_test_file(tf1_text), licenses=['mylicense'], template=True)
        index = detect.LicenseIndex([ttr])  # default to ngram_len=3

        # test
        tf2_text = (u'''Redistributions in binary form must nexB company
        reproduce as is stipulated the word for word above copyright notice.'''
        .splitlines())
        matches = index.match(tf2_text)
        expected = Token(start=0, start_line=1, start_char=0, end_line=2, end_char=75, end=17)
        self.assertEqual(1, len(matches))
        self.assertEqual(expected, matches[0].query_position)

    def test_template_detection_publicdomain(self):
        # setup
        tf5 = self.get_test_loc('detect/templates/license5.txt')
        ttr = Rule(text_file=tf5, licenses=['public-domain'], template=True)
        index = detect.LicenseIndex([ttr])

        # test
        tf6 = self.get_test_loc('detect/templates/license6.txt')
        matches = index.match(tf6)
        self.assertEqual(1, len(matches))
        expected = Token(start=82, start_line=16, start_char=0, end_line=18, end_char=67, end=118)
        self.assertEqual(expected, matches[0].query_position)

    def test_template_detection_with_short_tokens_around_gaps(self):
        # failed when a gapped token starts at a beginning of rule and at a
        # position less than ngram length
        # setup
        tf7 = self.get_test_loc('detect/templates/license7.txt')
        ttr = Rule(text_file=tf7, template=True)

        # use quadri grams by default
        index = detect.LicenseIndex([ttr])

        # test the index
        quad_grams_index = index.license_index.indexes[4]
        self.assertEqual(205, len(quad_grams_index))
        self.assertTrue(u'software without prior written' in quad_grams_index)

        # test
        tf8 = self.get_test_loc('detect/templates/license8.txt')
        matches = index.match(tf8)
        self.assertEqual(1, len(matches))
        expected = Token(start=0, start_line=1, start_char=0, end_line=40, end_char=34, end=276)
        self.assertEqual(expected, matches[0].query_position)

    def test_template_detection_works_for_sun_bcl(self):
        # setup
        rule_dir = self.get_test_loc('detect/rule_template/rules')
        rules = models.load_rules(rule_dir)
        index = detect.get_license_index(rules)

        # test
        qdoc = self.get_test_loc('detect/rule_template/query.txt')
        matches = index.match(qdoc)
        assert 1 == len(matches)


class TestMatchPositionsAccuracy(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def check_position(self, test_path, expected):
        """
        Check license detection in file or folder against expected result.
        """
        test_location = self.get_test_loc(test_path)
        result = []
        for detected in detect.detect_license(test_location):
            dlicense, sline, eline, schar, echar, _rid, _score = detected
            keys = dlicense, sline, eline, schar, echar
            result.append(keys)
        assert expected == result

    def test_match_has_correct_positions_basic(self):
        expected = [
            ('gpl-2.0', 1, 1, 0, 50),
            ('gpl-2.0', 2, 2, 0, 50),
            ('gpl-2.0', 3, 3, 0, 50)
        ]
        self.check_position('positions/license.txt', expected)

    def test_match_has_correct_positions_1(self):
        expected = [
            ('apache-2.0', 1, 2, 0, 46),
            ('apache-2.0', 3, 4, 0, 46),
            ('apache-2.0', 5, 6, 0, 46),
            ('apache-2.0', 7, 8, 0, 46),
            ('apache-2.0', 9, 10, 0, 46)
        ]
        self.check_position('positions/license1.txt', expected)

    def test_match_has_correct_positions_2(self):
        expected = [
        ]
        self.check_position('positions//license2.txt', expected)

    def test_match_has_correct_positions_3(self):
        # we had a weird error where the lines were not computed correctly
        # when we had more than one files detected at a time
        expected = [
            ('apache-2.0', 1, 2, 0, 46),
            ('apache-2.0', 3, 4, 0, 46),
            ('apache-2.0', 5, 6, 0, 46),
            ('apache-2.0', 7, 8, 0, 46),
            ('apache-2.0', 9, 10, 0, 46)
        ]
        self.check_position('positions/license3.txt', expected)

    def test_match_has_correct_positions_4(self):
        expected = [
            ('apache-2.0', 3, 4, 0, 46),
        ]
        self.check_position('positions/license4.txt', expected)

    def test_match_has_correct_positions_in_binary_lkms_1(self):
        expected = [
            ('bsd-new', 26, 26, 0, 20),
            ('gpl-2.0', 26, 26, 0, 20),
        ]
        self.check_position('positions/ath_pci.ko', expected)

    def test_match_has_correct_positions_in_binary_lkms_2(self):
        expected = [
            ('gpl-2.0', 24, 24, 0, 11),
        ]
        self.check_position('positions/eeepc_acpi.ko', expected)

    def test_match_has_correct_positions_in_binary_lkms_3(self):
        expected = [
            ('bsd-new', 3, 3, 0, 20),
            ('gpl-2.0', 3, 3, 0, 20),
        ]
        self.check_position('positions/wlan_xauth.ko', expected)


class TestToFix(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    @skipIf(True, 'Needs review')
    def test_detection_in_complex_json(self):
        # NOTE: this test cannot pass as we do not have several of the licenses
        # listed in this JSON
        test_file = self.get_test_loc('detect/json/all.json')
        import json
        item_map = json.load(test_file)
        for item in item_map:
            itemid = item_map[item
        ]['id',
        ]
            content = itemid + ' \n ' + item_map[item
        ]['url',
        ] + ' \n ' + item_map[item
        ]['title',
        ]
            tmp_file = self.get_temp_file()
            fh = open(tmp_file, 'w')
            fh.write(content)
            fh.close()
