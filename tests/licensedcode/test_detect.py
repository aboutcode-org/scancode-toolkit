#
# Copyright (c) 2018 nexB Inc. and others. All rights reserved.
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
from unittest.case import skip

from commoncode.testcase import FileBasedTesting

from licensedcode import cache
from licensedcode import index
from licensedcode import match_aho
from licensedcode import match_seq
from licensedcode.match import LicenseMatch
from licensedcode.models import load_rules
from licensedcode.models import Rule
from licensedcode.spans import Span
from licensedcode.tracing import get_texts
from license_test_utils import print_matched_texts

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

"""
Test the core license detection mechanics.
"""


class TestIndexMatch(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_match_does_not_return_matches_for_empty_query(self):
        idx = index.LicenseIndex([Rule(_text='A one. A two. license A three.')])

        matches = idx.match(query_string='')
        assert [] == matches
        matches = idx.match(query_string=None)
        assert [] == matches

    def test_match_does_not_return_matches_for_junk_queries(self):
        idx = index.LicenseIndex([Rule(_text='A one. a license two. license A three.')])

        assert [] == idx.match(query_string=u'some other junk')
        assert [] == idx.match(query_string=u'some junk')

    def test_match_return_one_match_with_correct_offsets(self):
        idx = index.LicenseIndex([Rule(_text='A one. a license two. A three.', licenses=['abc'])])

        querys = u'some junk. A one. A license two. A three.'
        #            0    1   2   3  4      5    6  7      8

        matches = idx.match(query_string=querys)
        assert 1 == len(matches)
        match = matches[0]
        qtext, itext = get_texts(match, query_string=querys, idx=idx)
        assert 'A one A license two A three' == qtext
        assert 'A one a license two A three' == itext

        assert Span(0, 6) == match.qspan
        assert Span(0, 6) == match.ispan

    def test_match_can_match_exactly_rule_text_used_as_query(self):
        test_file = self.get_test_loc('detect/mit/mit.c')
        rule = Rule(text_file=test_file, licenses=['mit'])
        idx = index.LicenseIndex([rule])

        matches = idx.match(test_file)
        assert 1 == len(matches)
        match = matches[0]
        assert rule == match.rule
        assert Span(0, 86) == match.qspan
        assert Span(0, 86) == match.ispan
        assert 100 == match.coverage()
        assert 100 == match.score()

    def test_match_matches_correctly_simple_exact_query_1(self):
        tf1 = self.get_test_loc('detect/mit/mit.c')
        ftr = Rule(text_file=tf1, licenses=['mit'])
        idx = index.LicenseIndex([ftr])

        query_doc = self.get_test_loc('detect/mit/mit2.c')
        matches = idx.match(query_doc)
        assert 1 == len(matches)
        match = matches[0]
        assert ftr == match.rule
        assert Span(0, 86) == match.qspan
        assert Span(0, 86) == match.ispan

    def test_match_matches_correctly_simple_exact_query_across_query_runs(self):
        tf1 = self.get_test_loc('detect/mit/mit.c')
        ftr = Rule(text_file=tf1, licenses=['mit'])
        idx = index.LicenseIndex([ftr])
        query_doc = self.get_test_loc('detect/mit/mit3.c')
        matches = idx.match(query_doc)
        assert 1 == len(matches)
        match = matches[0]

        qtext, itext = get_texts(match, location=query_doc, idx=idx)
        expected_qtext = u'''
            Permission is hereby granted free of charge to any person obtaining a
            copy of this software and associated documentation files the Software to
            deal in THE SOFTWARE WITHOUT RESTRICTION INCLUDING WITHOUT LIMITATION THE
            RIGHTS TO USE COPY MODIFY MERGE PUBLISH DISTRIBUTE SUBLICENSE AND OR SELL
            COPIES of the Software and to permit persons to whom the Software is
            furnished to do so subject to the following conditions The above
            copyright notice and this permission notice shall be included in all
            copies or substantial portions of the Software
        '''.split()
        assert expected_qtext == qtext.split()

        expected_itext = u'''
            Permission is hereby granted free of charge to any person obtaining a
            copy of this software and associated documentation files the Software to
            deal in the Software without restriction including without limitation
            the rights to use copy modify merge publish distribute sublicense and or
            sell copies of the Software and to permit persons to whom the Software
            is furnished to do so subject to the following conditions The above
            copyright notice and this permission notice shall be included in all
            copies or substantial portions of the Software
        '''.split()
        assert expected_itext == itext.split()

    def test_match_with_surrounding_junk_should_return_an_exact_match(self):
        tf1 = self.get_test_loc('detect/mit/mit.c')
        ftr = Rule(text_file=tf1, licenses=['mit'])
        idx = index.LicenseIndex([ftr])

        query_loc = self.get_test_loc('detect/mit/mit4.c')
        matches = idx.match(query_loc)
        assert len(matches) == 1
        match = matches[0]
        qtext, itext = get_texts(match, location=query_loc, idx=idx)
        expected_qtext = u'''
            Permission [add] [text] is hereby granted free of charge to any person
            obtaining a copy of this software and associated documentation files the
            Software to deal in the Software without restriction including without
            limitation the rights to use copy modify merge publish distribute
            sublicense and or sell copies of the Software and to permit persons to
            whom the Software is furnished to do so subject to the following
            conditions The above copyright [add] [text] notice and this permission
            notice shall be included in all copies or substantial portions of the
            Software
        '''.split()
        assert expected_qtext == qtext.split()

        expected_itext = u'''
            Permission is hereby granted free of charge to any person obtaining a
            copy of this software and associated documentation files the Software to
            deal in the Software without restriction including without limitation the
            rights to use copy modify merge publish distribute sublicense and or sell
            copies of the Software and to permit persons to whom the Software is
            furnished to do so subject to the following conditions The above
            copyright notice and this permission notice shall be included in all
            copies or substantial portions of the Software
        '''.split()
        assert expected_itext == itext.split()

        assert Span(0, 86) == match.qspan
        assert Span(0, 86) == match.ispan
        assert 95.6 == match.score()

    def test_match_can_match_approximately(self):
        rule_file = self.get_test_loc('approx/mit/mit.c')
        rule = Rule(text_file=rule_file, licenses=['mit'])
        idx = index.LicenseIndex([rule])

        query_doc = self.get_test_loc('approx/mit/mit4.c')
        matches = idx.match(query_doc)
        assert 2 == len(matches)
        m1 = matches[0]
        m2 = matches[1]
        assert rule == m1.rule
        assert rule == m2.rule
        assert 100 == m1.coverage()
        assert 100 == m2.coverage()
        assert 95.6 == m1.score()
        assert 93.55 == m2.score()

    def test_match_return_correct_positions_with_short_index_and_queries(self):
        idx = index.LicenseIndex([Rule(_text='MIT License', licenses=['mit'])])
        matches = idx.match(query_string='MIT License')
        assert 1 == len(matches)

        assert {'_tst_11_0': {'mit': [0]}} == idx.to_dict()

        qtext, itext = get_texts(matches[0], query_string='MIT License', idx=idx)
        assert 'MIT License' == qtext
        assert 'MIT License' == itext
        assert Span(0, 1) == matches[0].qspan
        assert Span(0, 1) == matches[0].ispan

        matches = idx.match(query_string='MIT MIT License')
        assert 1 == len(matches)

        qtext, itext = get_texts(matches[0], query_string='MIT MIT License', idx=idx)
        assert 'MIT License' == qtext
        assert 'MIT License' == itext
        assert Span(1, 2) == matches[0].qspan
        assert Span(0, 1) == matches[0].ispan

        query_doc1 = 'do you think I am a mit license MIT License, yes, I think so'
        # #                                  0       1   2       3
        matches = idx.match(query_string=query_doc1)
        assert 2 == len(matches)

        qtext, itext = get_texts(matches[0], query_string=query_doc1, idx=idx)
        assert 'mit license' == qtext
        assert 'MIT License' == itext
        assert Span(0, 1) == matches[0].qspan
        assert Span(0, 1) == matches[0].ispan

        qtext, itext = get_texts(matches[1], query_string=query_doc1, idx=idx)
        assert 'MIT License' == qtext
        assert 'MIT License' == itext
        assert Span(2, 3) == matches[1].qspan
        assert Span(0, 1) == matches[1].ispan

        query_doc2 = '''do you think I am a mit license
                        MIT License
                        yes, I think so'''
        matches = idx.match(query_string=query_doc2)
        assert 2 == len(matches)

        qtext, itext = get_texts(matches[0], query_string=query_doc2, idx=idx)
        assert 'mit license' == qtext
        assert 'MIT License' == itext
        assert Span(0, 1) == matches[0].qspan
        assert Span(0, 1) == matches[0].ispan

        qtext, itext = get_texts(matches[1], query_string=query_doc2, idx=idx)
        assert 'MIT License' == qtext
        assert 'MIT License' == itext
        assert Span(2, 3) == matches[1].qspan
        assert Span(0, 1) == matches[1].ispan

    def test_match_simple_rule(self):
        tf1 = self.get_test_loc('detect/mit/t1.txt')
        ftr = Rule(text_file=tf1, licenses=['bsd-original'])
        idx = index.LicenseIndex([ftr])

        query_doc = self.get_test_loc('detect/mit/t2.txt')
        matches = idx.match(query_doc)
        assert 1 == len(matches)
        match = matches[0]
        assert Span(0, 241) == match.qspan
        assert Span(0, 241) == match.ispan
        assert (1, 27,) == match.lines()
        assert 100 == match.coverage()
        assert 100 == match.score()

    def test_match_works_with_special_characters_1(self):
        test_file = self.get_test_loc('detect/specialcharacter/kerberos.txt')
        idx = index.LicenseIndex([Rule(text_file=test_file, licenses=['kerberos'])])
        assert 1 == len(idx.match(test_file))

    def test_match_works_with_special_characters_2(self):
        test_file = self.get_test_loc('detect/specialcharacter/kerberos1.txt')
        idx = index.LicenseIndex([Rule(text_file=test_file, licenses=['kerberos'])])
        assert 1 == len(idx.match(test_file))

    def test_match_works_with_special_characters_3(self):
        test_file = self.get_test_loc('detect/specialcharacter/kerberos2.txt')
        idx = index.LicenseIndex([Rule(text_file=test_file, licenses=['kerberos'])])
        assert 1 == len(idx.match(test_file))

    def test_match_works_with_special_characters_4(self):
        test_file = self.get_test_loc('detect/specialcharacter/kerberos3.txt')
        idx = index.LicenseIndex([Rule(text_file=test_file, licenses=['kerberos'])])
        assert 1 == len(idx.match(test_file))

    def test_overlap_detection1(self):
        #  test this containment relationship between test and index licenses:
        #   * Index licenses:
        #   +-license 2 --------+
        #   |  +-license 1 --+  |
        #   +-------------------+
        #
        #   * License texts to detect:
        #   +- license 3 -----------+
        #   | +-license 2 --------+ |
        #   | |  +-license 1 --+  | |
        #   | +-------------------+ |
        #   +-----------------------+
        #
        #   +-license 4 --------+
        #   |  +-license 1 --+  |
        #   +-------------------+

        # setup index
        license1 = '''Redistribution and use permitted.'''

        license2 = '''Redistributions of source must retain copyright.
        Redistribution and use permitted.
        Redistributions in binary form is permitted.'''

        license3 = '''
        this license source
        Redistributions of source must retain copyright.
        Redistribution and use permitted.
        Redistributions in binary form is permitted.
        has a permitted license'''

        license4 = '''My Redistributions is permitted.
        Redistribution and use permitted.
        Use is permitted too.'''

        rule1 = Rule(_text=license1, licenses=['overlap'])
        rule2 = Rule(_text=license2, licenses=['overlap'])
        rule3 = Rule(_text=license3, licenses=['overlap'])
        rule4 = Rule(_text=license4, licenses=['overlap'])
        idx = index.LicenseIndex([rule1, rule2, rule3, rule4])

        querys = 'Redistribution and use bla permitted.'
        # test : license1 is in the index and contains no other rule. should return rule1 at exact coverage.
        matches = idx.match(query_string=querys)
        assert 1 == len(matches)
        match = matches[0]
        assert Span(0, 3) == match.qspan
        assert rule1 == match.rule
        qtext, _itext = get_texts(match, query_string=querys, idx=idx)
        assert 'Redistribution and use [bla] permitted' == qtext

    def test_overlap_detection2(self):
        #  test this containment relationship between test and index licenses:
        #   * Index licenses:
        #   +-license 2 --------+
        #   |  +-license 1 --+  |
        #   +-------------------+

        # setup index
        license1 = '''Redistribution and use permitted.'''

        license2 = '''Redistributions of source must retain copyright.
        Redistribution and use permitted.
        Redistributions in binary form is permitted.'''

        rule1 = Rule(_text=license1, licenses=['overlap'])
        rule2 = Rule(_text=license2, licenses=['overlap'])
        idx = index.LicenseIndex([rule1, rule2])

        # test : license2 contains license1: return license2 as exact coverage

        querys = 'Redistribution and use bla permitted.'
        matches = idx.match(query_string=querys)
        assert 1 == len(matches)
        match = matches[0]
        assert rule1 == match.rule
        qtext, _itext = get_texts(match, query_string=querys, idx=idx)
        assert 'Redistribution and use [bla] permitted' == qtext

    def test_overlap_detection2_exact(self):
        #  test this containment relationship between test and index licenses:
        #   * Index licenses:
        #   +-license 2 --------+
        #   |  +-license 1 --+  |
        #   +-------------------+

        # setup index
        license1 = '''Redistribution and use permitted.'''

        license2 = '''Redistributions of source must retain copyright.
        Redistribution and use permitted.
        Redistributions in binary form is permitted.'''

        rule1 = Rule(_text=license1, licenses=['overlap'])
        rule2 = Rule(_text=license2, licenses=['overlap'])
        idx = index.LicenseIndex([rule1, rule2])

        # test : license2 contains license1: return license2 as exact coverage

        querys = 'Redistribution and use bla permitted.'
        matches = idx.match(query_string=querys)
        assert 1 == len(matches)
        match = matches[0]
        assert rule1 == match.rule
        qtext, _itext = get_texts(match, query_string=querys, idx=idx)
        assert 'Redistribution and use [bla] permitted' == qtext

    def test_overlap_detection3(self):
        #  test this containment relationship between test and index licenses:
        #   * Index licenses:
        #   +-license 2 --------+
        #   |  +-license 1 --+  |
        #   +-------------------+
        #
        #   * License texts to detect:
        #   +- license 3 -----------+
        #   | +-license 2 --------+ |
        #   | |  +-license 1 --+  | |
        #   | +-------------------+ |
        #   +-----------------------+
        #
        # setup index
        license1 = '''Redistribution and use permitted.'''

        license2 = '''Redistributions of source must retain copyright.
        Redistribution and use permitted.
        Redistributions in binary form is permitted.'''

        rule1 = Rule(_text=license1, licenses=['overlap'])
        rule2 = Rule(_text=license2, licenses=['overlap'])
        idx = index.LicenseIndex([rule1, rule2])

        querys = '''My source.
            Redistributions of source must retain copyright.
            Redistribution and use permitted.
            Redistributions in binary form is permitted.
            My code.'''

        # test : querys contains license2 that contains license1: return license2 as exact coverage
        matches = idx.match(query_string=querys)
        assert 1 == len(matches)
        match = matches[0]
        assert rule2 == match.rule
        qtext, _itext = get_texts(match, query_string=querys, idx=idx)
        expected = '''
            Redistributions of source must retain copyright
            Redistribution and use permitted
            Redistributions in binary form is permitted'''.split()
        assert expected == qtext.split()

    def test_overlap_detection4(self):
        #  test this containment relationship between test and index licenses:
        #   * Index licenses:
        #   +-license 2 --------+
        #   |  +-license 1 --+  |
        #   +-------------------+
        #
        #   +-license 4 --------+
        #   |  +-license 1 --+  |
        #   +-------------------+

        # setup index
        license1 = '''Redistribution and use permitted.'''

        license2 = '''Redistributions of source must retain copyright.
            Redistribution and use permitted.
            Redistributions in binary form is permitted.'''

        rule1 = Rule(_text=license1, licenses=['overlap'])
        rule2 = Rule(_text=license2, licenses=['overlap'])
        idx = index.LicenseIndex([rule1, rule2])

        querys = '''My source.
        Redistribution and use permitted.
        My code.'''

        # test : querys contains license1: return license1 as exact coverage
        matches = idx.match(query_string=querys)
        assert 1 == len(matches)
        match = matches[0]
        assert rule1 == match.rule
        qtext, _itext = get_texts(match, query_string=querys, idx=idx)
        assert 'Redistribution and use permitted' == qtext

    def test_overlap_detection5(self):
        #  test this containment relationship between test and index licenses:
        #   * Index licenses:
        #   +-license 2 --------+
        #   |  +-license 1 --+  |
        #   +-------------------+
        #
        #   +-license 4 --------+
        #   |  +-license 1 --+  |
        #   +-------------------+

        # setup index
        license1 = '''Redistribution and use permitted for MIT license.'''

        license2 = '''Redistributions of source must retain copyright.
        Redistribution and use permitted for MIT license.
        Redistributions in binary form is permitted.'''

        rule1 = Rule(_text=license1, licenses=['overlap'])
        rule2 = Rule(_text=license2, licenses=['overlap'])
        idx = index.LicenseIndex([rule1, rule2])

        querys = '''My source.
        Redistribution and use permitted for MIT license.
        My code.'''

        # test : querys contains license1: return license1 as exact coverage
        matches = idx.match(query_string=querys)
        assert 1 == len(matches)

        match = matches[0]
        assert rule1 == match.rule
        qtext, _itext = get_texts(match, query_string=querys, idx=idx)
        assert 'Redistribution and use permitted for MIT license' == qtext

    def test_fulltext_detection_works_with_partial_overlap_from_location(self):
        test_doc = self.get_test_loc('detect/templates/license3.txt')
        idx = index.LicenseIndex([Rule(text_file=test_doc, licenses=['mylicense'])])

        query_loc = self.get_test_loc('detect/templates/license4.txt')
        matches = idx.match(query_loc)

        assert 1 == len(matches)
        match = matches[0]
        assert Span(0, 41) == match.qspan
        assert Span(0, 41) == match.ispan
        assert 100 == match.coverage()
        assert 100 == match.score()
        qtext, _itext = get_texts(match, location=query_loc, idx=idx)
        expected = '''
            is free software you can redistribute it and or modify it under the terms
            of the GNU Lesser General Public License as published by the Free
            Software Foundation either version 2 1 of the License or at your option
            any later version
        '''.split()
        assert expected == qtext.split()


class TestIndexMatchWithTemplate(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_match_can_match_with_plain_rule_simple(self):
        tf1_text = u'''X11 License
        Copyright (C) 1996 X Consortium
        Permission is hereby granted, free of charge, to any person obtaining a copy
        of this software and associated documentation files (the "Software"), to deal
        in the Software without restriction, including without limitation the rights
        to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
        copies of the Software, and to permit persons to whom the Software is
        furnished to do so, subject to the following conditions: The above copyright
        notice and this permission notice shall be included in all copies or
        substantial portions of the Software. THE SOFTWARE IS PROVIDED "AS IS",
        WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
        TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
        NONINFRINGEMENT. IN NO EVENT SHALL THE X CONSORTIUM BE LIABLE FOR ANY CLAIM,
        DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
        OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
        OR OTHER DEALINGS IN THE SOFTWARE. Except as contained in this notice, the
        name of the X Consortium shall not be used in advertising or otherwise to
        promote the sale, use or other dealings in this Software without prior
        written authorization from the X Consortium. X Window System is a trademark
        of X Consortium, Inc.
        '''
        rule = Rule(_text=tf1_text, licenses=['x-consortium'])
        idx = index.LicenseIndex([rule])

        query_loc = self.get_test_loc('detect/simple_detection/x11-xconsortium_text.txt')
        matches = idx.match(query_loc)
        assert 1 == len(matches)

        match = matches[0]
        assert Span(0, 216) == match.qspan

    def test_match_can_match_with_plain_rule_simple2(self):
        rule_text = u'''X11 License
        Copyright (C) 1996 X Consortium
        Permission is hereby granted, free of charge, to any person obtaining a copy
        of this software and associated documentation files (the "Software"), to deal
        in the Software without restriction, including without limitation the rights
        to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
        copies of the Software, and to permit persons to whom the Software is
        furnished to do so, subject to the following conditions: The above copyright
        notice and this permission notice shall be included in all copies or
        substantial portions of the Software. THE SOFTWARE IS PROVIDED "AS IS",
        WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
        TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
        NONINFRINGEMENT. IN NO EVENT SHALL THE X CONSORTIUM BE LIABLE FOR ANY CLAIM,
        DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
        OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
        OR OTHER DEALINGS IN THE SOFTWARE. Except as contained in this notice, the
        name of the X Consortium shall not be used in advertising or otherwise to
        promote the sale, use or other dealings in this Software without prior
        written authorization from the X Consortium. X Window System is a trademark
        of X Consortium, Inc.
        '''
        rule = Rule(_text=rule_text, licenses=['x-consortium'])
        idx = index.LicenseIndex([rule])

        query_loc = self.get_test_loc('detect/simple_detection/x11-xconsortium_text.txt')
        matches = idx.match(location=query_loc)
        assert 1 == len(matches)

        expected_qtext = u'''
        X11 License Copyright C 1996 X Consortium Permission is hereby granted free
        of charge to any person obtaining a copy of this software and associated
        documentation files the Software to deal in the Software without restriction
        including without limitation the rights to use copy modify merge publish
        distribute sublicense and or sell copies of the Software and to permit
        persons to whom the Software is furnished to do so subject to the following
        conditions The above copyright notice and this permission notice shall be
        included in all copies or substantial portions of the Software THE SOFTWARE
        IS PROVIDED AS IS WITHOUT WARRANTY OF ANY KIND EXPRESS OR IMPLIED INCLUDING
        BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY FITNESS FOR A PARTICULAR
        PURPOSE AND NONINFRINGEMENT IN NO EVENT SHALL THE X CONSORTIUM BE LIABLE FOR
        ANY CLAIM DAMAGES OR OTHER LIABILITY WHETHER IN AN ACTION OF CONTRACT TORT OR
        OTHERWISE ARISING FROM OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
        OR OTHER DEALINGS IN THE SOFTWARE Except as contained in this notice the name
        of the X Consortium shall not be used in advertising or otherwise to promote
        the sale use or other dealings in this Software without prior written
        authorization from the X Consortium X Window System is a trademark of X
        Consortium Inc
        '''.split()
        match = matches[0]
        qtext, _itext = get_texts(match, location=query_loc, idx=idx)
        assert expected_qtext == qtext.split()

    def test_match_can_match_with_simple_rule_template2(self):
        rule_text = u'''
        IN NO EVENT SHALL THE {{X CONSORTIUM}}
        BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
        CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
        SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
        '''
        rule = Rule(_text=rule_text, licenses=['x-consortium'])
        idx = index.LicenseIndex([rule])

        query_string = u'''
        IN NO EVENT SHALL THE Y CORP
        BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
        CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
        SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
        '''

        matches = idx.match(query_string=query_string)
        assert 1 == len(matches)
        match = matches[0]
        qtext, itext = get_texts(match, query_string=query_string, idx=idx)

        expected_qtokens = u'''
        IN NO EVENT SHALL THE [Y] [CORP] BE LIABLE FOR ANY CLAIM DAMAGES OR OTHER
        LIABILITY WHETHER IN AN ACTION OF CONTRACT TORT OR OTHERWISE ARISING FROM OUT
        OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
        SOFTWARE
        '''.split()
        expected_itokens = u'''
        IN NO EVENT SHALL THE BE LIABLE FOR ANY CLAIM DAMAGES OR OTHER LIABILITY
        WHETHER IN AN ACTION OF CONTRACT TORT OR OTHERWISE ARISING FROM OUT OF OR IN
        CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE
        '''.split()
        assert expected_qtokens == qtext.split()
        assert expected_itokens == itext.split()

    def test_match_can_match_with_rule_template_with_inter_gap_of_2(self):
        # in this template text there are only 2 tokens between the two templates markers
        test_text = u'''Redistributions in binary form must
        {{}} reproduce the {{}}above copyright notice'''
        rule = Rule(_text=test_text, licenses=['mylicense'])
        idx = index.LicenseIndex([rule])

        querys = u'''Redistributions in binary form must nexB company
        reproduce the word for word above copyright notice.'''

        matches = idx.match(query_string=querys)
        assert 1 == len(matches)
        match = matches[0]
        assert 100 == match.coverage()
        assert 33.33 == match.score()
        assert Span(0, 9) == match.qspan
        assert Span(0, 9) == match.ispan

    def test_match_can_match_with_rule_template_with_inter_gap_of_3(self):
        # in this template there are 3 tokens between the two template markers
        test_text = u'''Redistributions in binary form must
        {{}} reproduce the stipulated {{}}above copyright notice'''
        rule = Rule(_text=test_text, licenses=['mylicense'])
        idx = index.LicenseIndex([rule])

        querys = u'''Redistributions in binary form must nexB company
        reproduce the stipulated word for word above copyright notice.'''

        matches = idx.match(query_string=querys)
        assert 1 == len(matches)

        match = matches[0]
        assert 100 == match.coverage()
        assert 37.81 == match.score()
        assert Span(0, 10) == match.qspan
        assert Span(0, 10) == match.ispan

    def test_match_can_match_with_rule_template_with_inter_gap_of_4(self):
        # in this template there are 4 tokens between the two templates markers
        test_text = u'''Redistributions in binary form must
        {{}} reproduce as is stipulated {{}}above copyright notice'''
        rule = Rule(_text=test_text, licenses=['mylicense'])
        idx = index.LicenseIndex([rule])

        querys = u'''Redistributions in binary form must nexB company
        reproduce as is stipulated the word for word above copyright notice.'''

        matches = idx.match(query_string=querys)
        assert 1 == len(matches)

        match = matches[0]
        assert Span(0, 11) == match.qspan
        assert Span(0, 11) == match.ispan

    def test_match_can_match_with_rule_template_for_public_domain(self):
        test_text = '''
        I hereby abandon any property rights to {{SAX 2.0 (the Simple API for
        XML)}}, and release all of {{the SAX 2.0 }} source code, compiled code,
        and documentation contained in this distribution into the Public Domain.
        '''
        rule = Rule(_text=test_text, licenses=['public-domain'])
        idx = index.LicenseIndex([rule])

        querys = '''
        SAX2 is Free!
        I hereby abandon any property rights to SAX 2.0 (the Simple API for
        XML), and release all of the SAX 2.0 source code, compiled code, and
        documentation contained in this distribution into the Public Domain. SAX
        comes with NO WARRANTY or guarantee of fitness for any purpose.
        SAX2 is Free!
        '''
        matches = idx.match(query_string=querys)

        assert 1 == len(matches)
        match = matches[0]

        qtext, itext = get_texts(match, query_string=querys, idx=idx)
        expected_qtext = u'''
        I hereby abandon any property rights to [SAX] [2] [0] <the> [Simple] [API] [for] [XML]
        <and> <release> <all> <of> <the> [SAX] [2] [0]
        source code compiled code and documentation contained in this distribution
        into the Public Domain
        '''.split()
        assert expected_qtext == qtext.split()

        expected_itext = u'''
        I hereby abandon any property rights to
        <and> <release> <all> <of>
        source code compiled code and documentation contained in this distribution
        into the Public Domain
        '''.split()
        assert expected_itext == itext.split()

        assert 84 == match.coverage()
        assert 84 == match.score()
        assert Span(0, 6) | Span(13, 26) == match.qspan
        assert Span(0, 6) | Span(11, 24) == match.ispan

    def test_match_can_match_with_rule_template_with_gap_near_start_with_few_tokens_before(self):
        # failed when a gapped token starts at a beginning of rule with few tokens before
        test_file = self.get_test_loc('detect/templates/license7.txt')
        rule = Rule(text_file=test_file, licenses=['lic'])
        idx = index.LicenseIndex([rule])

        qloc = self.get_test_loc('detect/templates/license8.txt')
        matches = idx.match(qloc)
        assert 1 == len(matches)

        match = matches[0]
        expected_qtokens = u"""
        All Rights Reserved Redistribution and use of this software and associated
        documentation Software with or without modification are permitted provided
        that the following conditions are met

        1 Redistributions of source code must retain copyright statements and notices
        Redistributions must also contain a copy of this document

        2 Redistributions in binary form must reproduce the above copyright notice
        this list of conditions and the following disclaimer in the documentation and
        or other materials provided with the distribution

        3 The name [groovy] must not be used to endorse or promote products derived
        from this Software without prior written permission of <The> [Codehaus] For
        written permission please contact [info] [codehaus] [org]

        4 Products derived from this Software may not be called [groovy] nor may
        [groovy] appear in their names without prior written permission of <The>
        [Codehaus]

        [groovy] is a registered trademark of <The> [Codehaus]

        5 Due credit should be given to <The> [Codehaus]
        [http] [groovy] [codehaus] [org]

        <THIS> <SOFTWARE> <IS> <PROVIDED> <BY> <THE> [CODEHAUS] <AND> <CONTRIBUTORS>
        AS IS AND ANY EXPRESSED OR IMPLIED WARRANTIES INCLUDING BUT NOT LIMITED TO
        THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
        PURPOSE ARE DISCLAIMED IN NO EVENT SHALL <THE> [CODEHAUS] OR ITS
        CONTRIBUTORS BE LIABLE FOR ANY DIRECT INDIRECT INCIDENTAL SPECIAL EXEMPLARY
        OR CONSEQUENTIAL DAMAGES INCLUDING BUT NOT LIMITED TO PROCUREMENT OF
        SUBSTITUTE GOODS OR SERVICES LOSS OF USE DATA OR PROFITS OR BUSINESS
        INTERRUPTION HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY WHETHER IN
        CONTRACT STRICT LIABILITY OR TORT INCLUDING NEGLIGENCE OR OTHERWISE ARISING
        IN ANY WAY OUT OF THE USE OF THIS SOFTWARE EVEN IF ADVISED OF THE POSSIBILITY
        OF SUCH DAMAGE
        """.split()

        expected_itokens = u''' All Rights Reserved Redistribution and use of this
        software and associated documentation Software with or without modification
        are permitted provided that the following conditions are met

        1 Redistributions of source code must retain copyright statements and notices
        Redistributions must also contain a copy of this document

        2 Redistributions in binary form must reproduce the above copyright notice
        this list of conditions and the following disclaimer in the documentation and
        or other materials provided with the distribution

        3 The name must not be used to endorse or promote products derived from this
        Software without prior written permission of For written permission please
        contact

        4 Products derived from this Software may not be called nor may appear in
        their names without prior written permission of is a registered trademark of

        5 Due credit should be given to


        <THIS> <SOFTWARE> <IS> <PROVIDED> <BY>

        AS IS AND ANY EXPRESSED OR IMPLIED WARRANTIES INCLUDING BUT NOT LIMITED TO
        THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
        PURPOSE ARE DISCLAIMED IN NO EVENT SHALL OR ITS CONTRIBUTORS BE LIABLE FOR
        ANY DIRECT INDIRECT INCIDENTAL SPECIAL EXEMPLARY OR CONSEQUENTIAL DAMAGES
        INCLUDING BUT NOT LIMITED TO PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES LOSS
        OF USE DATA OR PROFITS OR BUSINESS INTERRUPTION HOWEVER CAUSED AND ON ANY
        THEORY OF LIABILITY WHETHER IN CONTRACT STRICT LIABILITY OR TORT INCLUDING
        NEGLIGENCE OR OTHERWISE ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE
        EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE
        '''.split()

        qtext, itext = get_texts(match, location=qloc, idx=idx)
        assert expected_qtokens == qtext.split()
        assert expected_itokens == itext.split()

        assert 97.55 == match.coverage()
        assert 97.55 == match.score()
        expected = Span(2, 98) | Span(100, 125) | Span(127, 131) | Span(133, 139) | Span(149, 178) | Span(180, 253)
        assert expected == match.qspan
        assert  Span(1, 135) | Span(141, 244) == match.ispan

    def test_match_can_match_with_index_built_from_rule_directory_with_sun_bcls(self):
        rule_dir = self.get_test_loc('detect/rule_template/rules')
        idx = index.LicenseIndex(load_rules(rule_dir))

        # at line 151 the query has an extra "Software" word inserted to avoid hash matching
        query_loc = self.get_test_loc('detect/rule_template/query.txt')
        matches = idx.match(location=query_loc)
        assert 1 == len(matches)
        match = matches[0]
        assert Span(0, 958) | Span(960, 1756) == match.qspan
        assert match_seq.MATCH_SEQ == match.matcher


class TestMatchAccuracyWithFullIndex(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def check_position(self, test_path, expected, with_span=True, print_results=False):
        """
        Check license detection in file or folder against expected result.
        Expected is a list of (license, lines span, qspan span) tuples.
        """
        test_location = self.get_test_loc(test_path)
        results = []
        # FULL INDEX!!
        idx = cache.get_index()
        matches = idx.match(test_location)
        for match in matches:
            for detected in match.rule.licenses:
                if print_results:
                    print()
                    print(match)
                    print_matched_texts(match, location=test_location, idx=idx)
                results.append((detected, match.lines(), with_span and match.qspan or None))
        assert expected == results

    def test_match_has_correct_positions_basic(self):
        idx = cache.get_index()
        querys = u'''Licensed under the GNU General Public License (GPL).
                     Licensed under the GNU General Public License (GPL).
                     Licensed under the GNU General Public License (GPL).'''

        matches = idx.match(query_string=querys)

        rule = [r for r in idx.rules_by_rid if r.identifier == 'gpl_69.RULE'][0]
        m1 = LicenseMatch(rule=rule, qspan=Span(0, 7), ispan=Span(0, 7), start_line=1, end_line=1)
        m2 = LicenseMatch(rule=rule, qspan=Span(8, 15), ispan=Span(0, 7), start_line=2, end_line=2)
        m3 = LicenseMatch(rule=rule, qspan=Span(16, 23), ispan=Span(0, 7), start_line=3, end_line=3)
        assert [m1, m2, m3] == matches

    def test_match_has_correct_line_positions_for_query_with_repeats(self):
        expected = [
            # licenses, match.lines(), qtext,
            ([u'apache-2.0'], (1, 2), u'The Apache Software License Version 2 0 http www apache org licenses LICENSE 2 0 txt'),
            ([u'apache-2.0'], (3, 4), u'The Apache Software License Version 2 0 http www apache org licenses LICENSE 2 0 txt'),
            ([u'apache-2.0'], (5, 6), u'The Apache Software License Version 2 0 http www apache org licenses LICENSE 2 0 txt'),
            ([u'apache-2.0'], (7, 8), u'The Apache Software License Version 2 0 http www apache org licenses LICENSE 2 0 txt'),
            ([u'apache-2.0'], (9, 10), u'The Apache Software License Version 2 0 http www apache org licenses LICENSE 2 0 txt'),
        ]
        test_path = 'positions/license1.txt'

        test_location = self.get_test_loc(test_path)
        idx = cache.get_index()
        matches = idx.match(test_location)
        for i, match in enumerate(matches):
            ex_lics, ex_lines, ex_qtext = expected[i]
            qtext, _itext = get_texts(match, location=test_location, idx=idx)

            try:
                assert ex_lics == match.rule.licenses
                assert ex_lines == match.lines()
                assert ex_qtext == qtext
            except AssertionError:
                assert expected[i] == (match.rule.licenses, match.lines(), qtext)

    def test_match_does_not_return_spurious_match(self):
        expected = []
        self.check_position('positions/license2.txt', expected)

    def test_match_has_correct_line_positions_for_repeats(self):
        # we had a weird error where the lines were not computed correctly
        # when we had more than one file detected at a time
        expected = [
            # detected, match.lines(), match.qspan,
            (u'apache-2.0', (1, 2), Span(0, 15)),
            (u'apache-2.0', (3, 4), Span(16, 31)),
            (u'apache-2.0', (5, 6), Span(32, 47)),
            (u'apache-2.0', (7, 8), Span(48, 63)),
            (u'apache-2.0', (9, 10), Span(64, 79)),
        ]
        self.check_position('positions/license3.txt', expected)

    def test_match_works_for_apache_rule(self):
        idx = cache.get_index()
        querys = u'''I am not a license.

            The Apache Software License, Version 2.0
            http://www.apache.org/licenses/LICENSE-2.0.txt
            '''
        matches = idx.match(query_string=querys)

        assert 1 == len(matches)
        match = matches[0]
        assert 'apache-2.0_8.RULE' == match.rule.identifier
        assert match_aho.MATCH_AHO_EXACT == match.matcher

        qtext, _itext = get_texts(match, query_string=querys, idx=idx)
        assert u'The Apache Software License Version 2 0 http www apache org licenses LICENSE 2 0 txt' == qtext
        assert (3, 4) == match.lines()

    def test_match_does_not_detect_spurrious_short_apache_rule(self):
        idx = cache.get_index()
        querys = u'''
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
        <title>Apache log4j 1.2 - Continuous Integration</title>
        '''
        matches = idx.match(query_string=querys)
        assert [] == matches

    def test_match_handles_negative_rules_and_does_not_match_negative_regions_properly(self):
        # note: this test relies on the negative rule: not-a-license_busybox_2.RULE
        # with this text:
        # "libbusybox is GPL, not LGPL, and exports no stable API that might act as a copyright barrier."
        # and relies on the short rules that detect GPL and LGPL
        idx = cache.get_index()
        # lines 3 and 4 should NOT be part of any matches
        # they should match the negative "not-a-license_busybox_2.RULE"
        negative_lines_not_to_match = 3, 4
        querys = u'''
            licensed under the LGPL license
            libbusybox is GPL, not LGPL, and exports no stable API
            that might act as a copyright barrier.
            for the license
            license: dual BSD/GPL
            '''
        matches = idx.match(query_string=querys)

        for match in matches:
            for line in negative_lines_not_to_match:
                assert line not in match.lines()

    def test_match_has_correct_line_positions_in_automake_perl_file(self):
        # reported as https://github.com/nexB/scancode-toolkit/issues/88
        # note that this test is very sensitive to changes in the licenses data
        # set on purpose. Adding new license and/or frequent tokens will likely make it fail
        # in thsi case review the new not-frequent tokens that could be involved.
        # eventually update the rule-side Span offset if this looks acceptable
        expected = [
              # detected, match.lines(), match.qspan,
            (u'gpl-2.0-plus', (12, 25), Span(48, 159)),
            (u'fsf-mit', (231, 238), Span(834, 898)),
            (u'free-unknown', (306, 307), Span(1071, 1094))
        ]
        self.check_position('positions/automake.pl', expected)

    def test_score_is_not_100_for_exact_match_with_extra_words(self):
        idx = cache.get_index()
        test_loc = self.get_test_loc('detect/score/test.txt')
        matches = idx.match(location=test_loc)
        assert 1 == len(matches)
        match = matches[0]
        assert 99 < match.score() < 100

    def test_match_texts_with_short_lgpl_and_gpl_notices(self):
        idx = cache.get_index()
        test_loc = self.get_test_loc('detect/short_l_and_gpls')
        matches = idx.match(location=test_loc)
        assert 6 == len(matches)
        results = [m.matched_text(whole_lines=False) for m in matches]
        expected = [
            'GNU General Public License (GPL',
            'GNU Lesser General Public License (LGPL',
            'GNU General Public License (GPL',
            'GNU Lesser General Public (LGPL',
            'GNU Lesser General Public (LGPL',
            'GNU Lesser General Public (LGPL'
            ]
        assert expected == results


class TestMatchBinariesWithFullIndex(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_match_in_binary_lkms_1(self):
        idx = cache.get_index()
        qloc = self.get_test_loc('positions/ath_pci.ko')
        matches = idx.match(location=qloc)
        assert 1 == len(matches)
        match = matches[0]
        assert ['bsd-new', 'gpl-2.0'] == match.rule.licenses

        qtext, itext = get_texts(match, location=qloc, idx=idx)
        assert 'license Dual BSD GPL' == qtext
        assert 'license Dual BSD GPL' == itext

    def test_match_in_binary_lkms_2(self):
        idx = cache.get_index()
        qloc = self.get_test_loc('positions/eeepc_acpi.ko')
        matches = idx.match(location=qloc)
        assert 1 == len(matches)
        match = matches[0]
        assert ['gpl-1.0-plus'] == match.rule.licenses
        assert match.ispan == Span(0, 1)

        qtext, itext = get_texts(match, location=qloc, idx=idx)
        assert 'license GPL' == qtext
        assert 'License GPL' == itext

    def test_match_in_binary_lkms_3(self):
        idx = cache.get_index()
        qloc = self.get_test_loc('positions/wlan_xauth.ko')
        matches = idx.match(location=qloc)
        assert 1 == len(matches)
        match = matches[0]
        assert ['bsd-new', 'gpl-2.0'] == match.rule.licenses
        assert 100 == match.coverage()
        assert 20 == match.score()
        qtext, itext = get_texts(match, location=qloc, idx=idx)
        assert 'license Dual BSD GPL' == qtext
        assert 'license Dual BSD GPL' == itext
        assert Span(0, 3) == match.ispan


@skip('Needs review')
class TestToFix(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

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
