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
from unittest.case import skip

from commoncode.testcase import FileBasedTesting

from licensedcode import index
from licensedcode import models
from licensedcode.models import Rule
from licensedcode.whoosh_spans.spans import Span
from licensedcode.query import get_texts
from licensedcode.match import LicenseMatch
from unittest.case import expectedFailure


TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


"""
Test the core license matching mechanics.
"""

class TestIndexMatch(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_match_does_not_return_matches_for_empty_query(self):
        idx = index.LicenseIndex([Rule(_text='A one. A two. A three.')])

        matches = idx.match(query='')
        assert [] == matches
        matches = idx.match(query=None)
        assert [] == matches

    def test_match_does_not_return_matches_for_junk_queries(self):
        idx = index.LicenseIndex([Rule(_text='A one. a license two. A three.')])

        assert [] == idx.match(query=u'some other junk')
        assert [] == idx.match(query=u'some junk')

    def test_match_return_one_match_with_correct_offsets(self):
        idx = index.LicenseIndex([Rule(_text='A one. a license two. A three.', licenses=['abc'])])

        querys = u'some junk. A one. A license two. A three.'
        #            t1   t2 t3  t4 t5      t6  t7 t8    t9

        matches = idx.match(query=querys, min_score=0)
        assert 1 == len(matches)
        match = matches[0]
        assert Span(0, 6) == match.qregion
        assert Span(0, 6) == match.iregion

    def test_match_can_match_exactly_rule_text_used_as_query(self):
        test_file = self.get_test_loc('detect/mit/mit.c')
        rule = Rule(text_file=test_file, licenses=['mit'])
        idx = index.LicenseIndex([rule])

        matches = idx.match(test_file, min_score=0)
        assert 1 == len(matches)
        match = matches[0]
        assert rule == match.rule
        assert Span(0, 86) == match.qregion
        assert Span(0, 86) == match.iregion
        assert 100 == match.normalized_score()

    def test_match_matches_correctly_simple_exact_query_1(self):
        tf1 = self.get_test_loc('detect/mit/mit.c')
        ftr = Rule(text_file=tf1, licenses=['mit'])
        idx = index.LicenseIndex([ftr])

        query_doc = self.get_test_loc('detect/mit/mit2.c')
        matches = idx.match(query_doc)
        assert 1 == len(matches)
        match = matches[0]
        assert ftr == match.rule
        assert Span(0, 86) == match.qregion
        assert Span(0, 86) == match.iregion

    def test_match_matches_correctly_simple_exact_query_2(self):
        tf1 = self.get_test_loc('detect/mit/mit.c')
        ftr = Rule(text_file=tf1, licenses=['mit'])
        idx = index.LicenseIndex([ftr])

        query_doc = self.get_test_loc('detect/mit/mit3.c')
        matches = idx.match(query_doc)
        assert 1 == len(matches)
        match = matches[0]
        assert ftr == match.rule
        assert Span(0, 86) == match.qregion

    def test_match_with_surrounding_junk_should_return_an_exact_match(self):
        tf1 = self.get_test_loc('detect/mit/mit.c')
        ftr = Rule(text_file=tf1, licenses=['mit'])
        idx = index.LicenseIndex([ftr])

        query_doc = self.get_test_loc('detect/mit/mit4.c')
        matches = idx.match(query_doc, min_score=100)
        assert len(matches) == 1
        match = matches[0]
        assert [Span(0, 86)] == Span.merge(match.qspans)
        assert [Span(0, 86)] == Span.merge(match.ispans)
        assert 100 == match.normalized_score()

    def test_match_can_match_approximately(self):
        rule_file = self.get_test_loc('approx/mit/mit.c')
        rule = Rule(text_file=rule_file, licenses=['mit'])
        idx = index.LicenseIndex([rule])

        query_doc = self.get_test_loc('approx/mit/mit4.c')
        matches = idx.match(query_doc, min_score=80)
        assert matches
        assert rule == matches[0].rule
        assert matches[0].normalized_score() > 95

    @expectedFailure
    def test_match_return_correct_query_positions_with_short_index_and_queries(self):
        idx = index.LicenseIndex([Rule(_text='MIT License', licenses=['mit'])])
        matches = idx.match(query='MIT License', min_score=0, min_length=2)

        assert 1 == len(matches)
        assert Span(0, 1) == matches[0].qregion
        assert Span(0, 1) == matches[0].iregion

        matches = idx.match(query='MIT MIT License', min_score=0, min_length=0)
        assert 1 == len(matches)
        assert Span(0, 2) == matches[0].qregion
        assert Span(0, 1) == matches[0].iregion
        assert (Span(0, 2),) == matches[0].qspans
        assert (Span(0, 1),) == matches[0].ispans

        query_doc1 = 'do you think I am a mit license MIT License, yes, I think so'
        # #                                  0       1   2       3
        matches = idx.match(query=query_doc1, min_score=0)
        assert 2 == len(matches)
        assert Span(0, 1) == matches[0].qregion
        assert Span(0, 1) == matches[0].iregion
        assert (Span(0, 1),) == matches[0].qspans
        assert (Span(0, 1),) == matches[0].ispans

        assert Span(2, 3) == matches[1].qregion
        assert Span(0, 1) == matches[1].iregion
        assert (Span(2, 3),) == matches[1].qspans
        assert (Span(0, 1),) == matches[1].ispans

        # FIXME: this is not right: too many matches
        query_doc2 = '''do you think I am a mit license 
                        MIT License
                        yes, I think so'''
        matches = idx.match(query=query_doc2, min_score=0)
        assert 2 == len(matches)
        assert Span(0, 1) == matches[0].qregion
        assert Span(0, 1) == matches[0].iregion
        assert (Span(0, 1),) == matches[0].qspans
        assert (Span(0, 1),) == matches[0].ispans

        assert Span(2, 3) == matches[1].qregion
        assert Span(0, 1) == matches[1].iregion
        assert (Span(2, 3),) == matches[1].qspans
        assert (Span(0, 1),) == matches[1].ispans

    def test_match_simple_rule(self):
        tf1 = self.get_test_loc('detect/mit/t1.txt')
        ftr = Rule(text_file=tf1, licenses=['bsd-original'])
        idx = index.LicenseIndex([ftr])

        query_doc = self.get_test_loc('detect/mit/t2.txt')
        matches = idx.match(query_doc)
        assert 1 == len(matches)
        match = matches[0]
        assert Span(0, 241) == match.qregion
        assert [Span(0, 241)] == Span.merge(match.qspans)
        assert Span(0, 241) == match.iregion
        assert [Span(0, 241)] == Span.merge(match.ispans)
        assert Span(1, 27) == match.lines
        assert 100 == match.normalized_score()

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
        doc1 = '''Redistribution and use permitted.'''

        doc2 = '''Redistributions of source must retain copyright.
        Redistribution and use permitted.
        Redistributions in binary form is permitted.'''

        rule1 = Rule(_text=doc1, licenses=['overlap'], text_file='r1')
        rule2 = Rule(_text=doc2, licenses=['overlap'], text_file='r2')
        idx = index.LicenseIndex([rule1, rule2])

        # test : doc1 is in the index and contains no other rule. should return 1 at exact score.
        matches = idx.match(query=doc1, min_score=0)
        assert 1 == len(matches)
        match = matches[0]
        assert Span(0, 3) == match.qregion
        assert rule1 == match.rule

    def test_overlap_detection2(self):
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
        doc1 = '''Redistribution and use permitted.'''

        doc2 = '''Redistributions of source must retain copyright.
        Redistribution and use permitted.
        Redistributions in binary form is permitted.'''

        rule1 = Rule(_text=doc1, licenses=['overlap'], text_file='r1')
        rule2 = Rule(_text=doc2, licenses=['overlap'], text_file='r2')
        idx = index.LicenseIndex([rule1, rule2])

        # test : doc2 contains doc1: return doc2 as exact score
        matches = idx.match(query=doc2, min_score=100)
        assert 1 == len(matches)
        match = matches[0]
        assert rule2 == match.rule

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
        #   +-license 4 --------+
        #   |  +-license 1 --+  |
        #   +-------------------+

        # setup index
        doc1 = '''Redistribution and use permitted.'''

        doc2 = '''Redistributions of source must retain copyright.
        Redistribution and use permitted.
        Redistributions in binary form is permitted.'''

        rule1 = Rule(_text=doc1, licenses=['overlap'], text_file='r1')
        rule2 = Rule(_text=doc2, licenses=['overlap'], text_file='r2')
        idx = index.LicenseIndex([rule1, rule2])

        doc3 = '''My source.
        Redistributions of source must retain copyright.
        Redistribution and use permitted.
        Redistributions in binary form is permitted.
        My code.'''

        # test : doc3 contains doc2 that contains doc1: return doc2 as exact score
        matches = idx.match(query=doc3, min_score=100)
        assert 1 == len(matches)
        match = matches[0]
        assert rule2 == match.rule

    def test_overlap_detection4(self):
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
        doc1 = '''Redistribution and use permitted.'''

        doc2 = '''Redistributions of source must retain copyright.
        Redistribution and use permitted.
        Redistributions in binary form is permitted.'''

        rule1 = Rule(_text=doc1, licenses=['overlap'], text_file='r1')
        rule2 = Rule(_text=doc2, licenses=['overlap'], text_file='r2')
        idx = index.LicenseIndex([rule1, rule2])

        doc4 = '''My source.
        Redistribution and use permitted.
        My code.'''

        # test : doc4 contains doc1: return doc1 as exact score
        matches = idx.match(query=doc4, min_score=100)
        assert 1 == len(matches)

        match = matches[0]
        assert rule1 == match.rule

    def test_fulltext_detection_works_with_partial_overlap_from_location(self):
        test_doc = self.get_test_loc('detect/templates/license3.txt')
        idx = index.LicenseIndex([Rule(text_file=test_doc, licenses=['mylicense'])])

        query_doc = self.get_test_loc('detect/templates/license4.txt')
        matches = idx.match(query_doc, min_score=0)

        assert 1 == len(matches)
        match = matches[0]
        assert Span(0, 41) == match.qregion
        assert Span(0, 41) == match.iregion
        assert 100 == match.normalized_score()


class TestIndexMatchWithTemplate(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_match_can_match_with_rule_template_simple(self):
        # setup
        tf1_text = u'''X11 License
        Copyright (C) 1996 X Consortium
        Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
        The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
        THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE X CONSORTIUM BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
        Except as contained in this notice, the name of the X Consortium shall not be used in advertising or otherwise to promote the sale, use or other dealings in this Software without prior written authorization from the X Consortium.
        X Window System is a trademark of X Consortium, Inc.
        '''
        rule = Rule(_text=tf1_text, licenses=['x-consortium'])
        idx = index.LicenseIndex([rule])

        matches = idx.match(self.get_test_loc('detect/simple_detection/x11-xconsortium_text.txt'), min_score=0)
        assert 1 == len(matches)
        match = matches[0]
        assert Span(0, 216) == match.qregion
        assert [Span(0, 216)] == Span.merge(match.qspans)

    def test_match_can_match_with_rule_template_with_inter_gap_of_2(self):
        # in this template text there are only 2 tokens between the two templates markers
        test_text = u'''Redistributions in binary form must
        {{}} reproduce the {{}}above copyright notice'''
        rule = Rule(_text=test_text, licenses=['mylicense'])
        idx = index.LicenseIndex([rule])

        querys = u'''Redistributions in binary form must nexB company
        reproduce the word for word above copyright notice.'''

        matches = idx.match(query=querys, min_score=0)
        assert 1 == len(matches)
        match = matches[0]
        assert 1 == match.score()
        assert Span(0, 9) == match.qregion
        assert Span(0, 9) == match.iregion

    def test_match_can_match_with_rule_template_with_inter_gap_of_3(self):
        # in this template there are 3 tokens between the two template markers
        test_text = u'''Redistributions in binary form must
        {{}} reproduce the stipulated {{}}above copyright notice'''
        rule = Rule(_text=test_text, licenses=['mylicense'])
        idx = index.LicenseIndex([rule])

        querys = u'''Redistributions in binary form must nexB company
        reproduce the stipulated word for word above copyright notice.'''

        matches = idx.match(query=querys, min_score=0)
        assert 1 == len(matches)

        match = matches[0]
        assert 1 == match.score()
        assert Span(0, 10) == match.qregion
        assert Span(0, 10) == match.iregion

    def test_match_can_match_with_rule_template_with_inter_gap_of_4(self):
        # in this template there are 4 tokens between the two templates markers
        test_text = u'''Redistributions in binary form must
        {{}} reproduce as is stipulated {{}}above copyright notice'''
        rule = Rule(_text=test_text, licenses=['mylicense'])
        idx = index.LicenseIndex([rule])

        querys = u'''Redistributions in binary form must nexB company
        reproduce as is stipulated the word for word above copyright notice.'''

        matches = idx.match(query=querys, min_score=25)
        assert 1 == len(matches)

        match = matches[0]
        assert Span(0, 11) == match.qregion
        assert Span(0, 11) == match.iregion

    def test_match_can_match_with_rule_template_for_public_domain(self):
        test_text = '''
        I hereby abandon any property rights to {{SAX 2.0 (the Simple API for
        XML)}}, and release all of {{the SAX 2.0 }}source code, compiled code,
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
        matches = idx.match(query=querys, min_score=10)
        assert 1 == len(matches)
        match = matches[0]
        assert 100 == match.normalized_score()
        assert Span(0, 26) == match.qregion
        assert Span(0, 24) == match.iregion

    def test_match_can_match_with_rule_template_with_gap_near_start_with_few_tokens_before(self):
        # failed when a gapped token starts at a beginning of rule with few tokens before
        test_file = self.get_test_loc('detect/templates/license7.txt')
        rule = Rule(text_file=test_file, licenses=['lic'])
        idx = index.LicenseIndex([rule])

        qloc = self.get_test_loc('detect/templates/license8.txt')
        matches = idx.match(qloc, min_score=10)
        assert 1 == len(matches)

        match = matches[0]
        qtext, itext = get_texts(match, location=qloc, dictionary=idx.dictionary)

        expected_qtokens = u"""
         All Rights Reserved Redistribution 
        and use of this software and associated documentation Software with or without modification 
        are permitted provided that the following conditions are met 1 Redistributions of source
        code must retain copyright statements and notices Redistributions must also contain a copy of this document 2
        Redistributions in binary form must reproduce the above copyright notice this list of conditions and the following
        disclaimer in the documentation and or other materials provided with the distribution 3 The name <no-match> must not be
        used to endorse or promote products derived from this Software without prior written permission of <no-match> <no-match>
        For written permission please contact <no-match> <no-match> <no-match> 4 Products derived from this Software may not be
        called <no-match> nor may <no-match> appear in their names without prior written permission of <no-match> <no-match>
        <no-match> is a registered trademark of <no-match> <no-match> 5 Due credit should be given to <no-match> <no-match>
        <no-match> <no-match> <no-match> <no-match> THIS SOFTWARE IS PROVIDED BY <no-match> <no-match> <no-match> <no-match> AS
        IS AND ANY EXPRESSED OR IMPLIED WARRANTIES INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
        FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED IN NO EVENT SHALL <no-match> <no-match> OR ITS CONTRIBUTORS BE LIABLE
        FOR ANY DIRECT INDIRECT INCIDENTAL SPECIAL EXEMPLARY OR CONSEQUENTIAL DAMAGES INCLUDING BUT NOT LIMITED TO PROCUREMENT
        OF SUBSTITUTE GOODS OR SERVICES LOSS OF USE DATA OR PROFITS OR BUSINESS INTERRUPTION HOWEVER CAUSED AND ON ANY THEORY OF
        LIABILITY WHETHER IN CONTRACT STRICT LIABILITY OR TORT INCLUDING NEGLIGENCE OR OTHERWISE ARISING IN ANY WAY OUT OF THE
        USE OF THIS SOFTWARE EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE
        """.split()
        assert expected_qtokens == qtext.split()

        expected_itokens = u"""
        All Rights Reserved Redistribution and use of this software and associated documentation Software with or without
        modification are permitted provided that the following conditions are met 1 Redistributions of source code must retain
        copyright statements and notices Redistributions must also contain a copy of this document 2 Redistributions in binary
        form must reproduce the above copyright notice this list of conditions and the following disclaimer in the documentation
        and or other materials provided with the distribution 3 The name must not be used to endorse or promote products derived
        from this Software without prior written permission of For written permission please contact 4 Products derived from
        this Software may not be called nor may appear in their names without prior written permission of is a registered
        trademark of 5 Due credit should be given to THIS SOFTWARE IS PROVIDED BY AS IS AND ANY EXPRESSED OR IMPLIED WARRANTIES
        INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
        DISCLAIMED IN NO EVENT SHALL OR ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT INDIRECT INCIDENTAL SPECIAL EXEMPLARY OR
        CONSEQUENTIAL DAMAGES INCLUDING BUT NOT LIMITED TO PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES LOSS OF USE DATA OR
        PROFITS OR BUSINESS INTERRUPTION HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY WHETHER IN CONTRACT STRICT LIABILITY OR
        TORT INCLUDING NEGLIGENCE OR OTHERWISE ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE EVEN IF ADVISED OF THE
        POSSIBILITY OF SUCH DAMAGE
        """.split()
        assert expected_itokens == itext.split()

        assert 99.5 < match.normalized_score()
        assert Span(2, 253) == match.qregion
        assert Span(1, 244) == match.iregion

    def test_match_can_match_with_index_built_from_rule_directory_with_sun_bcls(self):
        rule_dir = self.get_test_loc('detect/rule_template/rules')
        rules = models.rules(rule_dir)
        idx = index.LicenseIndex(rules)

        matches = idx.match(self.get_test_loc('detect/rule_template/query.txt'), min_score=0)
        assert 1 == len(matches)
        match = matches[0]
        assert (Span(0, 1755),) == match.qspans
        assert Span(0, 1755) == match.qregion


class TestMatchAccuracyWithFullIndex(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def check_position(self, test_path, expected, min_score=100):
        """
        Check license detection in file or folder against expected result.
        Expected is a list of (license, lines span, qregion span) tuples.
        """
        test_location = self.get_test_loc(test_path)
        results = []
        # FULL INDEX!!
        idx = index.get_index()
        matches = idx.match(test_location, min_score=100)
        for match in matches:
            for detected in match.rule.licenses:
                results.append((detected, match.lines, match.qregion,))
        assert expected == results

    def test_match_has_correct_positions_basic(self):
        idx = index.get_index()
        querys = u'''Licensed under the GNU General Public License (GPL).
                     Licensed under the GNU General Public License (GPL).
                     Licensed under the GNU General Public License (GPL).'''
        matches = idx.match(query=querys, min_score=0)

        rule = [r for r in idx.rules_by_rid if r.identifier() == 'gpl-2.0_49.RULE'][0]
        m1 = LicenseMatch(rule=rule, _type='chunk1', qspans=[Span(0, 7)], ispans=[Span(0, 7)])
        m1.lines = Span(1, 1)
        m2 = LicenseMatch(rule=rule, _type='chunk2', qspans=[Span(8, 15)], ispans=[Span(0, 7)])
        m2.lines = Span(2, 2)
        m3 = LicenseMatch(rule=rule, _type='chunk3', qspans=[Span(16, 23)], ispans=[Span(0, 7)])
        m3.lines = Span(3, 3)

        assert [m1, m2, m3] == matches

    def test_match_has_correct_positions_1(self):
        expected = [
            # detected, match.lines, match.qregion,
            ('apache-2.0', Span(1, 2), Span(0, 15)),
            ('apache-2.0', Span(3, 4), Span(16, 31)),
            ('apache-2.0', Span(5, 6), Span(32, 47)),
            ('apache-2.0', Span(7, 8), Span(48, 63)),
            ('apache-2.0', Span(9, 10), Span(64, 79)),
        ]
        test_path = 'positions/license1.txt'

        test_location = self.get_test_loc(test_path)
        results = []
        idx = index.get_index()
        matches = idx.match(test_location, min_score=100)
        for match in matches:
            for detected in match.rule.licenses:
                results.append((detected, match.lines, match.qregion,))
        assert expected == results


    def test_match_has_correct_positions_2(self):
        expected = []
        self.check_position('positions/license2.txt', expected)

    def test_match_has_correct_positions_3(self):
        # we had a weird error where the lines were not computed correctly
        # when we had more than one files detected at a time
        expected = [
            # detected, match.lines, match.qregion,
            ('apache-2.0', Span(1, 2), Span(0, 15)),
            ('apache-2.0', Span(3, 4), Span(16, 31)),
            ('apache-2.0', Span(5, 6), Span(32, 47)),
            ('apache-2.0', Span(7, 8), Span(48, 63)),
            ('apache-2.0', Span(9, 10), Span(64, 79)),
        ]
        self.check_position('positions/license3.txt', expected)

    def test_match_works_for_apache_rule(self):
        idx = index.get_index()
        querys = u'''I am not a license.
            The Apache Software License, Version 2.0
            http://www.apache.org/licenses/LICENSE-2.0.txt
            '''
        matches = idx.match(query=querys, min_score=100)

        rule = [r for r in idx.rules_by_rid if r.identifier() == 'apache-2.0_8.RULE'][0]
        m1 = LicenseMatch(rule=rule, _type='chunk1', qspans=[Span(5, 20)], ispans=[Span(0, 15)])
        m1.lines = Span(2, 3)
        assert [m1] == matches

    def test_match_does_not_detect_spurrious_short_apache_rule(self):
        idx = index.get_index()
        querys = u'''
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
        <title>Apache log4j 1.2 - Continuous Integration</title>
        '''
        matches = idx.match(query=querys, min_score=100)
        assert [] == matches


class TestMatchBinariesWithFullIndex(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_match_in_binary_lkms_1(self):
        idx = index.get_index()
        qloc = self.get_test_loc('positions/ath_pci.ko')
        matches = idx.match(location=qloc, min_score=99)
        assert 1 == len(matches)
        match = matches[0]
        assert ['bsd-new', 'gpl-2.0'] == match.rule.licenses

    def test_match_in_binary_lkms_2(self):
        idx = index.get_index()
        qloc = self.get_test_loc('positions/eeepc_acpi.ko')
        matches = idx.match(location=qloc, min_score=100)
        assert 1 == len(matches)
        match = matches[0]
        assert ['gpl-2.0'] == match.rule.licenses
        assert match.qregion == Span(65, 66)
        assert match.iregion == Span(0, 1)
        assert match.lines == Span(24, 24)

    def test_match_in_binary_lkms_3(self):
        idx = index.get_index()
        qloc = self.get_test_loc('positions/wlan_xauth.ko')
        matches = idx.match(location=qloc, min_score=100)
        assert 1 == len(matches)
        match = matches[0]
        assert ['bsd-new', 'gpl-2.0'] == match.rule.licenses
        assert match.qregion == Span(2, 5)
        assert match.iregion == Span(0, 3)
        assert match.lines == Span(3, 3)


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
