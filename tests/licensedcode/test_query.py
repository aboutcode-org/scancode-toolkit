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

from licensedcode import index
from licensedcode.models import Rule

from licensedcode.query import Query
from array import array
from licensedcode import models


TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


class IndexTesting(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def get_test_rules(self, base, subset=None):
        base = self.get_test_loc(base)
        test_files = sorted(os.listdir(base))
        if subset:
            test_files = [t for t in test_files if t in subset]

        return [Rule(text_file=os.path.join(base, license_key), licenses=[license_key])
                for license_key in test_files]


class TestQueryWithSingleRun(IndexTesting):

    def test_Query_tokens_by_line_from_string(self):
        rule_text = 'Redistribution and use in source and binary forms with or without modification are permitted'
        idx = index.LicenseIndex([Rule(_text=rule_text, licenses=['bsd'])])
        querys = '''
            The
            Redistribution and use in source and binary are permitted.
        
            Athena capital of Grece 
            Paris and Athene
            Always'''

        qry = Query(query_string=querys, idx=idx, _test_mode=True)
        result = list(qry.tokens_by_line())
        expected = [
            [],
            [None],
            [12, 0, 6, 3, 9, 0, 1, 2, 7],
            [],
            [None, None, None, None],
            [None, 0, None],
            [None],
        ]

        assert expected == result

        # convert tid to actual token strings
        qtbl_as_str = lambda qtbl: [[None if tid is None else idx.tokens_by_tid[tid] for tid in tids] for tids in qtbl]

        result_str = qtbl_as_str(result)
        expected_str = [
            [],
            [None],
            ['redistribution', 'and', 'use', 'in', 'source', 'and', 'binary', 'are', 'permitted'],
            [],
            [None, None, None, None],
            [None, 'and', None],
            [None],
        ]

        assert expected_str == result_str

        assert {1: 3, 2: 3, 3: 3, 4: 3, 5: 3, 6: 3, 7: 3, 8: 3, 9: 3, 15: 6} == qry.line_by_pos

        # convert tid to actual token strings
        lbp_as_str = lambda lbp, qs: [(qs[pos], lnum) for pos, lnum in lbp.items()]

        expected = [
            ('Redistribution', 3),
            ('and', 3),
            ('use', 3),
            ('in', 3),
            ('source', 3),
            ('and', 3),
            ('binary', 3),
            ('are', 3),
            ('permitted.', 3),
            ('and', 6)
        ]
        assert expected == lbp_as_str(qry.line_by_pos, querys.split())

        idx = index.LicenseIndex([Rule(_text=rule_text, licenses=['bsd'])])
        querys = 'and this is not a license'
        qry = Query(query_string=querys, idx=idx, _test_mode=True)
        result = list(qry.tokens_by_line())
        expected = [['and', None, None, None, None, None]]
        assert expected == qtbl_as_str(result)

    def test_Query_tokenize_from_string(self):
        rule_text = 'Redistribution and use in source and binary forms with or without modification are permitted'
        idx = index.LicenseIndex([Rule(_text=rule_text, licenses=['bsd'])])
        querys = '''
            The
            Redistribution and use in source and binary are permitted.
        
            Athena capital of Grece 
            Paris and Athene
            Always'''

        qry = Query(query_string=querys, idx=idx, _test_mode=True)
        qry.tokenize(qry.tokens_by_line())
        # convert tid to actual token strings
        tks_as_str = lambda tks: [None if tid is None else idx.tokens_by_tid[tid] for tid  in tks]

        expected = ['redistribution', 'and', 'use', 'in', 'source', 'and', 'binary', 'are', 'permitted', 'and']
        result = tks_as_str(qry.tokens)
        assert expected == result

        expected = [None, 'redistribution', 'and', 'use', 'in', 'source', 'and', 'binary', 'are', 'permitted', None, None, None, None, None, 'and', None, None]
        result = tks_as_str(qry.tokens_with_unknowns())
        assert expected == result

        assert 1 == len(qry.query_runs)
        qr1 = qry.query_runs[0]
        assert 0 == qr1.start
        assert 9 == qr1.end
        assert 10 == len(qr1)
        expected = ['redistribution', 'and', 'use', 'in', 'source', 'and', 'binary', 'are', 'permitted', 'and']
        result = tks_as_str(qr1.tokens)
        assert expected == result
        expected = [None, 'redistribution', 'and', 'use', 'in', 'source', 'and', 'binary', 'are', 'permitted', None, None, None, None, None, 'and']
        result = tks_as_str(qr1.tokens_with_unknowns())
        assert expected == result

    def test_QueryRuns_multigrams(self):
        rule_text = 'Redistribution and use in source and binary forms with or without modification are permitted'
        idx = index.LicenseIndex([Rule(_text=rule_text, licenses=['bsd'])])
        querys = '''
            The
            Redistribution and use in source and binary are permitted.
        
            Athena capital of Grece 
            Paris and Athene
            Always'''

        qry = Query(query_string=querys, idx=idx)
        assert set([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]) == qry.matchables

        assert 1 == len(qry.query_runs)
        qrun = qry.query_runs[0]

        # convert tid to actual token strings
        tks_as_str = lambda tks: [None if tid is None else idx.tokens_by_tid[tid] for tid  in tks]

        expected = ['redistribution', 'and', 'use', 'in', 'source', 'and', 'binary', 'are', 'permitted', 'and']
        assert expected == tks_as_str(qrun.tokens)

        expected = [None, 'redistribution', 'and', 'use', 'in', 'source', 'and', 'binary', 'are', 'permitted', None, None, None, None, None, 'and']
        assert expected == tks_as_str(qrun.tokens_with_unknowns())

        assert 0 == qrun.start
        assert 9 == qrun.end

        # convert ngrams to actual token strings
        ngs_as_str = lambda pos_ngs: [(start, ln, ' '.join(idx.tokens_by_tid[tid] for tid in array('h', ng))) for start, ln, ng in pos_ngs]

        result = ngs_as_str(qrun.multigrams())
        expected = [
            (0, 5, 'redistribution and use in source'),
            (1, 5, 'and use in source and'),
            (2, 5, 'use in source and binary'),
            (3, 5, 'in source and binary are'),
            (4, 5, 'source and binary are permitted'),
            (5, 5, 'and binary are permitted and'),
            (0, 4, 'redistribution and use in'),
            (1, 4, 'and use in source'),
            (2, 4, 'use in source and'),
            (3, 4, 'in source and binary'),
            (4, 4, 'source and binary are'),
            (5, 4, 'and binary are permitted'),
            (6, 4, 'binary are permitted and'),
            (0, 3, 'redistribution and use'),
            (1, 3, 'and use in'),
            (2, 3, 'use in source'),
            (3, 3, 'in source and'),
            (4, 3, 'source and binary'),
            (5, 3, 'and binary are'),
            (6, 3, 'binary are permitted'),
            (7, 3, 'are permitted and'),
            (0, 2, 'redistribution and'),
            (1, 2, 'and use'),
            (2, 2, 'use in'),
            (3, 2, 'in source'),
            (4, 2, 'source and'),
            (5, 2, 'and binary'),
            (6, 2, 'binary are'),
            (7, 2, 'are permitted'),
            (8, 2, 'permitted and'),
            (0, 1, 'redistribution'),
            (1, 1, 'and'),
            (2, 1, 'use'),
            (3, 1, 'in'),
            (4, 1, 'source'),
            (5, 1, 'and'),
            (6, 1, 'binary'),
            (7, 1, 'are'),
            (8, 1, 'permitted'),
            (9, 1, 'and')]
        assert expected == result

    def test_QueryRun_does_not_end_with_None(self):
        rule_text = 'Redistribution and use in source and binary forms, with or without modification, are permitted'
        idx = index.LicenseIndex([Rule(_text=rule_text, licenses=['bsd'])])

        querys = '''
            The
            Redistribution and use in source and binary forms, with or without modification, are permitted.
            
            Always
            
            
            
            bar
             modification
             foo
            '''

        # convert tid to actual token strings
        tks_as_str = lambda tks: [None if tid is None else idx.tokens_by_tid[tid] for tid  in tks]
        qry = Query(query_string=querys, idx=idx)
        expected = [
            None,
            'redistribution', 'and', 'use', 'in', 'source', 'and', 'binary',
            'forms', 'with', 'or', 'without', 'modification', 'are', 'permitted',
            None, None,
            'modification',
            None
        ]
        assert [x for x in expected if x] == tks_as_str(qry.tokens)
        assert expected == tks_as_str(qry.tokens_with_unknowns())

        assert 2 == len(qry.query_runs)
        qrun = qry.query_runs[0]
        expected = ['redistribution', 'and', 'use', 'in', 'source', 'and', 'binary', 'forms', 'with', 'or', 'without', 'modification', 'are', 'permitted']
        assert expected == tks_as_str(qrun.tokens)
        assert 0 == qrun.start
        assert 13 == qrun.end

        qrun = qry.query_runs[1]
        expected = ['modification']
        assert expected == tks_as_str(qrun.tokens)
        assert 14 == qrun.start
        assert 14 == qrun.end

    def test_Query_from_real_index_and_location(self):
        idx = index.LicenseIndex(self.get_test_rules('index/bsd'))
        query_loc = self.get_test_loc('index/querytokens')

        qry = Query(location=query_loc, idx=idx)
        runs = qry.query_runs
        assert len(runs) == 1
        query_run = runs[0]

        expected_lbp = {
            0: 4, 1: 4, 2: 4, 3: 4, 4: 4, 5: 4, 6: 4, 7: 4, 8: 6, 9: 6, 10: 6,
            11: 6, 12: 6, 13: 7, 14: 7, 15: 7, 16: 7, 17: 7, 20: 8, 22: 9,
            23: 9, 24: 9, 25: 9, 26: 9, 27: 11, 28: 11, 29: 11, 30: 11, 31: 11,
            32: 11, 33: 11, 34: 11, 35: 11, 36: 11, 37: 11, 38: 11, 39: 15
        }

        assert expected_lbp == query_run.line_by_pos

        expected_toks = [
            u'redistribution', u'and', u'use', u'in', u'source', u'and',
            u'binary', u'forms', u'redistributions', u'of', u'source', u'code',
            u'must', u'the', u'this', u'that', u'is', u'not', u'to',
            u'redistributions', u'in', u'binary', u'form', u'must', u'this',
            u'software', u'is', u'provided', u'by', u'the', u'copyright',
            u'holders', u'and', u'contributors', u'as', u'is',
            u'redistributions']

        assert expected_toks == [None if t is None else idx.tokens_by_tid[t] for t in query_run.tokens]

    def test_query_run_tokens_with_junk(self):
        ranked_toks = lambda : ['the', 'is', 'a']
        idx = index.LicenseIndex([Rule(_text='a is the binary')],
                                 _ranked_tokens=ranked_toks)
        assert 2 == idx.len_junk
        assert {'a': 0, 'the': 1, 'binary': 2, 'is': 3, } == idx.dictionary

        # two junks
        q = Query(query_string='a the', idx=idx)
        qrun = q.query_runs[0]
        assert qrun.line_by_pos
        assert [0, 1] == qrun.tokens
        assert {} == qrun.unknowns_by_pos

        # one junk
        q = Query(query_string='a binary', idx=idx)
        qrun = q.query_runs[0]
        assert qrun.line_by_pos
        assert [0, 2] == qrun.tokens
        assert {} == qrun.unknowns_by_pos

        # one junk
        q = Query(query_string='binary the', idx=idx)
        qrun = q.query_runs[0]
        assert qrun.line_by_pos
        assert [2, 1] == qrun.tokens
        assert {} == qrun.unknowns_by_pos

        # one unknown at start
        q = Query(query_string='that binary', idx=idx)
        qrun = q.query_runs[0]
        assert qrun.line_by_pos
        assert [2] == qrun.tokens
        assert {-1: 1} == qrun.unknowns_by_pos

        # one unknown at end
        q = Query(query_string='binary that', idx=idx)
        qrun = q.query_runs[0]
        assert qrun.line_by_pos
        assert [2] == qrun.tokens
        assert {0: 1} == qrun.unknowns_by_pos

        # onw unknown in the middle
        q = Query(query_string='binary that a binary', idx=idx)
        qrun = q.query_runs[0]
        assert qrun.line_by_pos
        assert [2, 0, 2] == qrun.tokens
        assert {0: 1} == qrun.unknowns_by_pos

        # onw unknown in the middle
        q = Query(query_string='a binary that a binary', idx=idx)
        qrun = q.query_runs[0]
        assert qrun.line_by_pos
        assert [0, 2, 0, 2] == qrun.tokens
        assert {1: 1} == qrun.unknowns_by_pos

        # two unknowns in the middle
        q = Query(query_string='binary that was a binary', idx=idx)
        qrun = q.query_runs[0]
        assert qrun.line_by_pos
        assert [2, 0, 2] == qrun.tokens
        assert {0: 2} == qrun.unknowns_by_pos

        # unknowns at start, middle and end
        q = Query(query_string='hello dolly binary that was a binary end really', idx=idx)
        #                         u     u           u    u            u    u
        qrun = q.query_runs[0]
        assert qrun.line_by_pos
        assert [2, 0, 2] == qrun.tokens
        assert {-1: 2, 0: 2, 2: 2} == qrun.unknowns_by_pos

    def test_query_tokens_are_same_for_different_text_formatting(self):

        test_files = [self.get_test_loc(f) for f in [
            'match_inv/queryformat/license2.txt',
            'match_inv/queryformat/license3.txt',
            'match_inv/queryformat/license4.txt',
            'match_inv/queryformat/license5.txt',
            'match_inv/queryformat/license6.txt',
        ]]

        rule_file = self.get_test_loc('match_inv/queryformat/license1.txt')
        idx = index.LicenseIndex([Rule(text_file=rule_file, licenses=['mit'])])

        q = Query(location=rule_file, idx=idx)
        assert 1 == len(q.query_runs)
        expected = q.query_runs[0]
        for tf in test_files:
            q = Query(tf, idx=idx)
            qr = q.query_runs[0]
            assert expected.tokens == qr.tokens

    def test_query_run_unknowns(self):
        idx = index.LicenseIndex([Rule(_text='a is the binary')])

        assert {'a': 0, 'binary': 1, 'is': 2, 'the': 3} == idx.dictionary
        assert 2 == idx.len_junk

        # multiple unknowns at start, middle and end
        q = Query(query_string='that new binary was sure a kind of the real mega deal', idx=idx)
        # known pos                      0               1         2
        # abs pos                  0   1 2      3   4    5 6    7  8   9    10   11
        expected = {
            - 1: 2,
            0: 2,
            1: 2,
            2: 3,
        }
        assert expected == dict(q.unknowns_by_pos)


class TestQueryWithMultipleRuns(IndexTesting):

    def test_query_runs_from_location(self):
        idx = index.LicenseIndex(self.get_test_rules('index/bsd'))
        query_loc = self.get_test_loc('index/querytokens')
        qry = Query(location=query_loc, idx=idx, line_threshold=3)
        result = [q._as_dict(brief=True) for q in qry.query_runs]

        expected = [
            {
             'start': 0,
             'end': 35,
             'tokens': u'redistribution and use in source ... holders and contributors as is'},
            {
             'start': 36,
             'end': 36,
             'tokens': u'redistributions'}
        ]
        assert expected == result

    def test_query_runs_three_runs(self):
        idx = index.LicenseIndex(self.get_test_rules('index/bsd'))
        query_loc = self.get_test_loc('index/queryruns')
        qry = Query(location=query_loc, idx=idx)
        expected = [
            {'end': 84,
             'start': 0,
             'tokens': u'the redistribution and use in ... 2 1 3 c 4'},
            {'end': 97,
             'start': 85,
             'tokens': u'this software is provided by ... holders and contributors as is'},
            {'end': 98, 'start': 98, 'tokens': u'redistributions'}
        ]

        result = [q._as_dict(brief=True) for q in qry.query_runs]
        assert expected == result

    def test_QueryRun(self):
        idx = index.LicenseIndex([Rule(_text='redistributions in binary form must redistributions in')])
        qry = Query(query_string='redistributions in binary form must redistributions in', idx=idx)
        qruns = qry.query_runs
        assert 1 == len(qruns)
        qr = qruns[0]
        # test
        result = [idx.tokens_by_tid[tid] for tid in qr.tokens]
        expected = ['redistributions', 'in', 'binary', 'form', 'must', 'redistributions', 'in']
        assert expected == result

    def test_query_runs_text_is_correct(self):
        test_rules = self.get_test_rules('query/full_text/idx',)
        idx = index.LicenseIndex(test_rules)
        query_loc = self.get_test_loc('query/full_text/query')
        qry = Query(location=query_loc, idx=idx, line_threshold=3)
        qruns = qry.query_runs
        result = [[u'<None>' if t is None else idx.tokens_by_tid[t] for t in qr.tokens_with_unknowns()] for qr in qruns]

        expected = [
            u'<None> <None> <None> this'.split(),

            u'''redistribution and use in source and binary forms with or
            without modification are permitted provided that the following
            conditions are met redistributions of source code must retain the
            above copyright notice this list of conditions and the following
            disclaimer redistributions in binary form must reproduce the above
            copyright notice this list of conditions and the following
            disclaimer in the documentation and or other materials provided with
            the distribution neither the name of <None> inc nor the names of its
            contributors may be used to endorse or promote products derived from
            this software without specific prior written permission this
            software is provided by the copyright holders and contributors as is
            and any express or implied warranties including but not limited to
            the implied warranties of merchantability and fitness for a
            particular purpose are disclaimed in no event shall the copyright
            owner or contributors be liable for any direct indirect incidental
            special exemplary or consequential damages including but not limited
            to procurement of substitute goods or services loss of use data or
            profits or business interruption however caused and on any theory of
            liability whether in contract strict liability or tort including
            negligence or otherwise arising in any way out of the use of this
            software even if advised of the possibility of such damage'''.split(),
            u'no <None> of'.split(),
        ]
        assert expected == result

    def test_query_runs_with_plain_rule(self):
        rule_text = u'''X11 License
            Copyright (C) 1996 X Consortium Permission is hereby granted, free
            of charge, to any person obtaining a copy of this software and
            associated documentation files (the "Software"), to deal in the
            Software without restriction, including without limitation the
            rights to use, copy, modify, merge, publish, distribute, sublicense,
            and/or sell copies of the Software, and to permit persons to whom
            the Software is furnished to do so, subject to the following
            conditions: The above copyright notice and this permission notice
            shall be included in all copies or substantial portions of the
            Software. THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
            KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
            WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
            NONINFRINGEMENT. IN NO EVENT SHALL THE X CONSORTIUM BE LIABLE FOR
            ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
            CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
            WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
            Except as contained in this notice, the name of the X Consortium
            shall not be used in advertising or otherwise to promote the sale,
            use or other dealings in this Software without prior written
            authorization from the X Consortium. X Window System is a trademark
            of X Consortium, Inc.
        '''
        rule = Rule(_text=rule_text, licenses=['x-consortium'])
        idx = index.LicenseIndex([rule])

        query_loc = self.get_test_loc('detect/simple_detection/x11-xconsortium_text.txt')
        qry = Query(location=query_loc, idx=idx)
        result = [q._as_dict(brief=True) for q in qry.query_runs]
        expected = [{
            'start': 0,
            'end': 216,
            'tokens': u'x11 license copyright c 1996 ... trademark of x consortium inc'
        }]
        assert 217 == len(qry.query_runs[0].tokens)
        assert expected == result

    def test_query_run_ngrams_are_correct_with_template_and_multiple_rules(self):
        test_rules = self.get_test_rules('index/bsd_templates',)
        idx = index.LicenseIndex(test_rules)
        querys = u'''
            
            
            Hello, what about this
            
            Redistribution and use in source and binary forms, with or without modification,
            are permitted provided that the following conditions are met:
            
                * Redistributions of source code must retain the above copyright notice,
                this list of conditions and the following disclaimer.
            
                * Redistributions in binary form must reproduce the above copyright notice,
                this list of conditions and the following disclaimer in the documentation
                and/or other materials provided with the distribution.
            
                * Neither the name of nexB Inc. nor the names of its contributors may be
                used to endorse or promote products derived from this software without
                specific prior written permission.
            
            THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
            ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
            
            
            Goodbye
            No part of match        '''

        qry = Query(query_string=querys, idx=idx)
        assert 2 == len(qry.query_runs)

        # convert ngrams to actual token strings
        ngs_as_str = lambda pos_ngs: [(start, ln, ' '.join(idx.tokens_by_tid[tid] for tid in array('h', ng))) for start, ln, ng in pos_ngs]

        assert [(0, 1, u'this')] == ngs_as_str(qry.query_runs[0].multigrams())

        expected = [
            (1, 5, u'redistribution and use in source'),
            (2, 5, u'and use in source and'),
            (3, 5, u'use in source and binary'),
            (4, 5, u'in source and binary forms'),
            (5, 5, u'source and binary forms with'),
            (6, 5, u'and binary forms with or'),
            (7, 5, u'binary forms with or without'),
            (8, 5, u'forms with or without modification'),
            (9, 5, u'with or without modification are'),
            (10, 5, u'or without modification are permitted'),
            (11, 5, u'without modification are permitted provided'),
            (12, 5, u'modification are permitted provided that'),
            (13, 5, u'are permitted provided that the'),
            (14, 5, u'permitted provided that the following'),
            (15, 5, u'provided that the following conditions'),
            (16, 5, u'that the following conditions are'),
            (17, 5, u'the following conditions are met'),
            (18, 5, u'following conditions are met redistributions'),
            (19, 5, u'conditions are met redistributions of'),
            (20, 5, u'are met redistributions of source'),
            (21, 5, u'met redistributions of source code'),
            (22, 5, u'redistributions of source code must'),
            (23, 5, u'of source code must retain'),
            (24, 5, u'source code must retain the'),
            (25, 5, u'code must retain the above'),
            (26, 5, u'must retain the above copyright'),
            (27, 5, u'retain the above copyright notice'),
            (28, 5, u'the above copyright notice this'),
            (29, 5, u'above copyright notice this list'),
            (30, 5, u'copyright notice this list of'),
            (31, 5, u'notice this list of conditions'),
            (32, 5, u'this list of conditions and'),
            (33, 5, u'list of conditions and the'),
            (34, 5, u'of conditions and the following'),
            (35, 5, u'conditions and the following disclaimer'),
            (36, 5, u'and the following disclaimer redistributions'),
            (37, 5, u'the following disclaimer redistributions in'),
            (38, 5, u'following disclaimer redistributions in binary'),
            (39, 5, u'disclaimer redistributions in binary form'),
            (40, 5, u'redistributions in binary form must'),
            (41, 5, u'in binary form must reproduce'),
            (42, 5, u'binary form must reproduce the'),
            (43, 5, u'form must reproduce the above'),
            (44, 5, u'must reproduce the above copyright'),
            (45, 5, u'reproduce the above copyright notice'),
            (46, 5, u'the above copyright notice this'),
            (47, 5, u'above copyright notice this list'),
            (48, 5, u'copyright notice this list of'),
            (49, 5, u'notice this list of conditions'),
            (50, 5, u'this list of conditions and'),
            (51, 5, u'list of conditions and the'),
            (52, 5, u'of conditions and the following'),
            (53, 5, u'conditions and the following disclaimer'),
            (54, 5, u'and the following disclaimer in'),
            (55, 5, u'the following disclaimer in the'),
            (56, 5, u'following disclaimer in the documentation'),
            (57, 5, u'disclaimer in the documentation and'),
            (58, 5, u'in the documentation and or'),
            (59, 5, u'the documentation and or other'),
            (60, 5, u'documentation and or other materials'),
            (61, 5, u'and or other materials provided'),
            (62, 5, u'or other materials provided with'),
            (63, 5, u'other materials provided with the'),
            (64, 5, u'materials provided with the distribution'),
            (65, 5, u'provided with the distribution neither'),
            (66, 5, u'with the distribution neither the'),
            (67, 5, u'the distribution neither the name'),
            (68, 5, u'distribution neither the name of'),
            (69, 5, u'neither the name of inc'),
            (70, 5, u'the name of inc nor'),
            (71, 5, u'name of inc nor the'),
            (72, 5, u'of inc nor the names'),
            (73, 5, u'inc nor the names of'),
            (74, 5, u'nor the names of its'),
            (75, 5, u'the names of its contributors'),
            (76, 5, u'names of its contributors may'),
            (77, 5, u'of its contributors may be'),
            (78, 5, u'its contributors may be used'),
            (79, 5, u'contributors may be used to'),
            (80, 5, u'may be used to endorse'),
            (81, 5, u'be used to endorse or'),
            (82, 5, u'used to endorse or promote'),
            (83, 5, u'to endorse or promote products'),
            (84, 5, u'endorse or promote products derived'),
            (85, 5, u'or promote products derived from'),
            (86, 5, u'promote products derived from this'),
            (87, 5, u'products derived from this software'),
            (88, 5, u'derived from this software without'),
            (89, 5, u'from this software without specific'),
            (90, 5, u'this software without specific prior'),
            (91, 5, u'software without specific prior written'),
            (92, 5, u'without specific prior written permission'),
            (93, 5, u'specific prior written permission this'),
            (94, 5, u'prior written permission this software'),
            (95, 5, u'written permission this software is'),
            (96, 5, u'permission this software is provided'),
            (97, 5, u'this software is provided by'),
            (98, 5, u'software is provided by the'),
            (99, 5, u'is provided by the copyright'),
            (100, 5, u'provided by the copyright holders'),
            (101, 5, u'by the copyright holders and'),
            (102, 5, u'the copyright holders and contributors'),
            (103, 5, u'copyright holders and contributors as'),
            (104, 5, u'holders and contributors as is'),
            (105, 5, u'and contributors as is and'),
            (106, 5, u'contributors as is and any'),
            (107, 5, u'as is and any express'),
            (108, 5, u'is and any express or'),
            (109, 5, u'and any express or implied'),
            (110, 5, u'any express or implied warranties'),
            (111, 5, u'express or implied warranties including'),
            (112, 5, u'or implied warranties including but'),
            (113, 5, u'implied warranties including but not'),
            (114, 5, u'warranties including but not limited'),
            (115, 5, u'including but not limited to'),
            (116, 5, u'but not limited to no'),
            (117, 5, u'not limited to no of'),
            (1, 4, u'redistribution and use in'),
            (2, 4, u'and use in source'),
            (3, 4, u'use in source and'),
            (4, 4, u'in source and binary'),
            (5, 4, u'source and binary forms'),
            (6, 4, u'and binary forms with'),
            (7, 4, u'binary forms with or'),
            (8, 4, u'forms with or without'),
            (9, 4, u'with or without modification'),
            (10, 4, u'or without modification are'),
            (11, 4, u'without modification are permitted'),
            (12, 4, u'modification are permitted provided'),
            (13, 4, u'are permitted provided that'),
            (14, 4, u'permitted provided that the'),
            (15, 4, u'provided that the following'),
            (16, 4, u'that the following conditions'),
            (17, 4, u'the following conditions are'),
            (18, 4, u'following conditions are met'),
            (19, 4, u'conditions are met redistributions'),
            (20, 4, u'are met redistributions of'),
            (21, 4, u'met redistributions of source'),
            (22, 4, u'redistributions of source code'),
            (23, 4, u'of source code must'),
            (24, 4, u'source code must retain'),
            (25, 4, u'code must retain the'),
            (26, 4, u'must retain the above'),
            (27, 4, u'retain the above copyright'),
            (28, 4, u'the above copyright notice'),
            (29, 4, u'above copyright notice this'),
            (30, 4, u'copyright notice this list'),
            (31, 4, u'notice this list of'),
            (32, 4, u'this list of conditions'),
            (33, 4, u'list of conditions and'),
            (34, 4, u'of conditions and the'),
            (35, 4, u'conditions and the following'),
            (36, 4, u'and the following disclaimer'),
            (37, 4, u'the following disclaimer redistributions'),
            (38, 4, u'following disclaimer redistributions in'),
            (39, 4, u'disclaimer redistributions in binary'),
            (40, 4, u'redistributions in binary form'),
            (41, 4, u'in binary form must'),
            (42, 4, u'binary form must reproduce'),
            (43, 4, u'form must reproduce the'),
            (44, 4, u'must reproduce the above'),
            (45, 4, u'reproduce the above copyright'),
            (46, 4, u'the above copyright notice'),
            (47, 4, u'above copyright notice this'),
            (48, 4, u'copyright notice this list'),
            (49, 4, u'notice this list of'),
            (50, 4, u'this list of conditions'),
            (51, 4, u'list of conditions and'),
            (52, 4, u'of conditions and the'),
            (53, 4, u'conditions and the following'),
            (54, 4, u'and the following disclaimer'),
            (55, 4, u'the following disclaimer in'),
            (56, 4, u'following disclaimer in the'),
            (57, 4, u'disclaimer in the documentation'),
            (58, 4, u'in the documentation and'),
            (59, 4, u'the documentation and or'),
            (60, 4, u'documentation and or other'),
            (61, 4, u'and or other materials'),
            (62, 4, u'or other materials provided'),
            (63, 4, u'other materials provided with'),
            (64, 4, u'materials provided with the'),
            (65, 4, u'provided with the distribution'),
            (66, 4, u'with the distribution neither'),
            (67, 4, u'the distribution neither the'),
            (68, 4, u'distribution neither the name'),
            (69, 4, u'neither the name of'),
            (70, 4, u'the name of inc'),
            (71, 4, u'name of inc nor'),
            (72, 4, u'of inc nor the'),
            (73, 4, u'inc nor the names'),
            (74, 4, u'nor the names of'),
            (75, 4, u'the names of its'),
            (76, 4, u'names of its contributors'),
            (77, 4, u'of its contributors may'),
            (78, 4, u'its contributors may be'),
            (79, 4, u'contributors may be used'),
            (80, 4, u'may be used to'),
            (81, 4, u'be used to endorse'),
            (82, 4, u'used to endorse or'),
            (83, 4, u'to endorse or promote'),
            (84, 4, u'endorse or promote products'),
            (85, 4, u'or promote products derived'),
            (86, 4, u'promote products derived from'),
            (87, 4, u'products derived from this'),
            (88, 4, u'derived from this software'),
            (89, 4, u'from this software without'),
            (90, 4, u'this software without specific'),
            (91, 4, u'software without specific prior'),
            (92, 4, u'without specific prior written'),
            (93, 4, u'specific prior written permission'),
            (94, 4, u'prior written permission this'),
            (95, 4, u'written permission this software'),
            (96, 4, u'permission this software is'),
            (97, 4, u'this software is provided'),
            (98, 4, u'software is provided by'),
            (99, 4, u'is provided by the'),
            (100, 4, u'provided by the copyright'),
            (101, 4, u'by the copyright holders'),
            (102, 4, u'the copyright holders and'),
            (103, 4, u'copyright holders and contributors'),
            (104, 4, u'holders and contributors as'),
            (105, 4, u'and contributors as is'),
            (106, 4, u'contributors as is and'),
            (107, 4, u'as is and any'),
            (108, 4, u'is and any express'),
            (109, 4, u'and any express or'),
            (110, 4, u'any express or implied'),
            (111, 4, u'express or implied warranties'),
            (112, 4, u'or implied warranties including'),
            (113, 4, u'implied warranties including but'),
            (114, 4, u'warranties including but not'),
            (115, 4, u'including but not limited'),
            (116, 4, u'but not limited to'),
            (117, 4, u'not limited to no'),
            (118, 4, u'limited to no of'),
            (1, 3, u'redistribution and use'),
            (2, 3, u'and use in'),
            (3, 3, u'use in source'),
            (4, 3, u'in source and'),
            (5, 3, u'source and binary'),
            (6, 3, u'and binary forms'),
            (7, 3, u'binary forms with'),
            (8, 3, u'forms with or'),
            (9, 3, u'with or without'),
            (10, 3, u'or without modification'),
            (11, 3, u'without modification are'),
            (12, 3, u'modification are permitted'),
            (13, 3, u'are permitted provided'),
            (14, 3, u'permitted provided that'),
            (15, 3, u'provided that the'),
            (16, 3, u'that the following'),
            (17, 3, u'the following conditions'),
            (18, 3, u'following conditions are'),
            (19, 3, u'conditions are met'),
            (20, 3, u'are met redistributions'),
            (21, 3, u'met redistributions of'),
            (22, 3, u'redistributions of source'),
            (23, 3, u'of source code'),
            (24, 3, u'source code must'),
            (25, 3, u'code must retain'),
            (26, 3, u'must retain the'),
            (27, 3, u'retain the above'),
            (28, 3, u'the above copyright'),
            (29, 3, u'above copyright notice'),
            (30, 3, u'copyright notice this'),
            (31, 3, u'notice this list'),
            (32, 3, u'this list of'),
            (33, 3, u'list of conditions'),
            (34, 3, u'of conditions and'),
            (35, 3, u'conditions and the'),
            (36, 3, u'and the following'),
            (37, 3, u'the following disclaimer'),
            (38, 3, u'following disclaimer redistributions'),
            (39, 3, u'disclaimer redistributions in'),
            (40, 3, u'redistributions in binary'),
            (41, 3, u'in binary form'),
            (42, 3, u'binary form must'),
            (43, 3, u'form must reproduce'),
            (44, 3, u'must reproduce the'),
            (45, 3, u'reproduce the above'),
            (46, 3, u'the above copyright'),
            (47, 3, u'above copyright notice'),
            (48, 3, u'copyright notice this'),
            (49, 3, u'notice this list'),
            (50, 3, u'this list of'),
            (51, 3, u'list of conditions'),
            (52, 3, u'of conditions and'),
            (53, 3, u'conditions and the'),
            (54, 3, u'and the following'),
            (55, 3, u'the following disclaimer'),
            (56, 3, u'following disclaimer in'),
            (57, 3, u'disclaimer in the'),
            (58, 3, u'in the documentation'),
            (59, 3, u'the documentation and'),
            (60, 3, u'documentation and or'),
            (61, 3, u'and or other'),
            (62, 3, u'or other materials'),
            (63, 3, u'other materials provided'),
            (64, 3, u'materials provided with'),
            (65, 3, u'provided with the'),
            (66, 3, u'with the distribution'),
            (67, 3, u'the distribution neither'),
            (68, 3, u'distribution neither the'),
            (69, 3, u'neither the name'),
            (70, 3, u'the name of'),
            (71, 3, u'name of inc'),
            (72, 3, u'of inc nor'),
            (73, 3, u'inc nor the'),
            (74, 3, u'nor the names'),
            (75, 3, u'the names of'),
            (76, 3, u'names of its'),
            (77, 3, u'of its contributors'),
            (78, 3, u'its contributors may'),
            (79, 3, u'contributors may be'),
            (80, 3, u'may be used'),
            (81, 3, u'be used to'),
            (82, 3, u'used to endorse'),
            (83, 3, u'to endorse or'),
            (84, 3, u'endorse or promote'),
            (85, 3, u'or promote products'),
            (86, 3, u'promote products derived'),
            (87, 3, u'products derived from'),
            (88, 3, u'derived from this'),
            (89, 3, u'from this software'),
            (90, 3, u'this software without'),
            (91, 3, u'software without specific'),
            (92, 3, u'without specific prior'),
            (93, 3, u'specific prior written'),
            (94, 3, u'prior written permission'),
            (95, 3, u'written permission this'),
            (96, 3, u'permission this software'),
            (97, 3, u'this software is'),
            (98, 3, u'software is provided'),
            (99, 3, u'is provided by'),
            (100, 3, u'provided by the'),
            (101, 3, u'by the copyright'),
            (102, 3, u'the copyright holders'),
            (103, 3, u'copyright holders and'),
            (104, 3, u'holders and contributors'),
            (105, 3, u'and contributors as'),
            (106, 3, u'contributors as is'),
            (107, 3, u'as is and'),
            (108, 3, u'is and any'),
            (109, 3, u'and any express'),
            (110, 3, u'any express or'),
            (111, 3, u'express or implied'),
            (112, 3, u'or implied warranties'),
            (113, 3, u'implied warranties including'),
            (114, 3, u'warranties including but'),
            (115, 3, u'including but not'),
            (116, 3, u'but not limited'),
            (117, 3, u'not limited to'),
            (118, 3, u'limited to no'),
            (119, 3, u'to no of'),
            (1, 2, u'redistribution and'),
            (2, 2, u'and use'),
            (3, 2, u'use in'),
            (4, 2, u'in source'),
            (5, 2, u'source and'),
            (6, 2, u'and binary'),
            (7, 2, u'binary forms'),
            (8, 2, u'forms with'),
            (9, 2, u'with or'),
            (10, 2, u'or without'),
            (11, 2, u'without modification'),
            (12, 2, u'modification are'),
            (13, 2, u'are permitted'),
            (14, 2, u'permitted provided'),
            (15, 2, u'provided that'),
            (16, 2, u'that the'),
            (17, 2, u'the following'),
            (18, 2, u'following conditions'),
            (19, 2, u'conditions are'),
            (20, 2, u'are met'),
            (21, 2, u'met redistributions'),
            (22, 2, u'redistributions of'),
            (23, 2, u'of source'),
            (24, 2, u'source code'),
            (25, 2, u'code must'),
            (26, 2, u'must retain'),
            (27, 2, u'retain the'),
            (28, 2, u'the above'),
            (29, 2, u'above copyright'),
            (30, 2, u'copyright notice'),
            (31, 2, u'notice this'),
            (32, 2, u'this list'),
            (33, 2, u'list of'),
            (34, 2, u'of conditions'),
            (35, 2, u'conditions and'),
            (36, 2, u'and the'),
            (37, 2, u'the following'),
            (38, 2, u'following disclaimer'),
            (39, 2, u'disclaimer redistributions'),
            (40, 2, u'redistributions in'),
            (41, 2, u'in binary'),
            (42, 2, u'binary form'),
            (43, 2, u'form must'),
            (44, 2, u'must reproduce'),
            (45, 2, u'reproduce the'),
            (46, 2, u'the above'),
            (47, 2, u'above copyright'),
            (48, 2, u'copyright notice'),
            (49, 2, u'notice this'),
            (50, 2, u'this list'),
            (51, 2, u'list of'),
            (52, 2, u'of conditions'),
            (53, 2, u'conditions and'),
            (54, 2, u'and the'),
            (55, 2, u'the following'),
            (56, 2, u'following disclaimer'),
            (57, 2, u'disclaimer in'),
            (58, 2, u'in the'),
            (59, 2, u'the documentation'),
            (60, 2, u'documentation and'),
            (61, 2, u'and or'),
            (62, 2, u'or other'),
            (63, 2, u'other materials'),
            (64, 2, u'materials provided'),
            (65, 2, u'provided with'),
            (66, 2, u'with the'),
            (67, 2, u'the distribution'),
            (68, 2, u'distribution neither'),
            (69, 2, u'neither the'),
            (70, 2, u'the name'),
            (71, 2, u'name of'),
            (72, 2, u'of inc'),
            (73, 2, u'inc nor'),
            (74, 2, u'nor the'),
            (75, 2, u'the names'),
            (76, 2, u'names of'),
            (77, 2, u'of its'),
            (78, 2, u'its contributors'),
            (79, 2, u'contributors may'),
            (80, 2, u'may be'),
            (81, 2, u'be used'),
            (82, 2, u'used to'),
            (83, 2, u'to endorse'),
            (84, 2, u'endorse or'),
            (85, 2, u'or promote'),
            (86, 2, u'promote products'),
            (87, 2, u'products derived'),
            (88, 2, u'derived from'),
            (89, 2, u'from this'),
            (90, 2, u'this software'),
            (91, 2, u'software without'),
            (92, 2, u'without specific'),
            (93, 2, u'specific prior'),
            (94, 2, u'prior written'),
            (95, 2, u'written permission'),
            (96, 2, u'permission this'),
            (97, 2, u'this software'),
            (98, 2, u'software is'),
            (99, 2, u'is provided'),
            (100, 2, u'provided by'),
            (101, 2, u'by the'),
            (102, 2, u'the copyright'),
            (103, 2, u'copyright holders'),
            (104, 2, u'holders and'),
            (105, 2, u'and contributors'),
            (106, 2, u'contributors as'),
            (107, 2, u'as is'),
            (108, 2, u'is and'),
            (109, 2, u'and any'),
            (110, 2, u'any express'),
            (111, 2, u'express or'),
            (112, 2, u'or implied'),
            (113, 2, u'implied warranties'),
            (114, 2, u'warranties including'),
            (115, 2, u'including but'),
            (116, 2, u'but not'),
            (117, 2, u'not limited'),
            (118, 2, u'limited to'),
            (119, 2, u'to no'),
            (120, 2, u'no of'),
            (1, 1, u'redistribution'),
            (2, 1, u'and'),
            (3, 1, u'use'),
            (4, 1, u'in'),
            (5, 1, u'source'),
            (6, 1, u'and'),
            (7, 1, u'binary'),
            (8, 1, u'forms'),
            (9, 1, u'with'),
            (10, 1, u'or'),
            (11, 1, u'without'),
            (12, 1, u'modification'),
            (13, 1, u'are'),
            (14, 1, u'permitted'),
            (15, 1, u'provided'),
            (16, 1, u'that'),
            (17, 1, u'the'),
            (18, 1, u'following'),
            (19, 1, u'conditions'),
            (20, 1, u'are'),
            (21, 1, u'met'),
            (22, 1, u'redistributions'),
            (23, 1, u'of'),
            (24, 1, u'source'),
            (25, 1, u'code'),
            (26, 1, u'must'),
            (27, 1, u'retain'),
            (28, 1, u'the'),
            (29, 1, u'above'),
            (30, 1, u'copyright'),
            (31, 1, u'notice'),
            (32, 1, u'this'),
            (33, 1, u'list'),
            (34, 1, u'of'),
            (35, 1, u'conditions'),
            (36, 1, u'and'),
            (37, 1, u'the'),
            (38, 1, u'following'),
            (39, 1, u'disclaimer'),
            (40, 1, u'redistributions'),
            (41, 1, u'in'),
            (42, 1, u'binary'),
            (43, 1, u'form'),
            (44, 1, u'must'),
            (45, 1, u'reproduce'),
            (46, 1, u'the'),
            (47, 1, u'above'),
            (48, 1, u'copyright'),
            (49, 1, u'notice'),
            (50, 1, u'this'),
            (51, 1, u'list'),
            (52, 1, u'of'),
            (53, 1, u'conditions'),
            (54, 1, u'and'),
            (55, 1, u'the'),
            (56, 1, u'following'),
            (57, 1, u'disclaimer'),
            (58, 1, u'in'),
            (59, 1, u'the'),
            (60, 1, u'documentation'),
            (61, 1, u'and'),
            (62, 1, u'or'),
            (63, 1, u'other'),
            (64, 1, u'materials'),
            (65, 1, u'provided'),
            (66, 1, u'with'),
            (67, 1, u'the'),
            (68, 1, u'distribution'),
            (69, 1, u'neither'),
            (70, 1, u'the'),
            (71, 1, u'name'),
            (72, 1, u'of'),
            (73, 1, u'inc'),
            (74, 1, u'nor'),
            (75, 1, u'the'),
            (76, 1, u'names'),
            (77, 1, u'of'),
            (78, 1, u'its'),
            (79, 1, u'contributors'),
            (80, 1, u'may'),
            (81, 1, u'be'),
            (82, 1, u'used'),
            (83, 1, u'to'),
            (84, 1, u'endorse'),
            (85, 1, u'or'),
            (86, 1, u'promote'),
            (87, 1, u'products'),
            (88, 1, u'derived'),
            (89, 1, u'from'),
            (90, 1, u'this'),
            (91, 1, u'software'),
            (92, 1, u'without'),
            (93, 1, u'specific'),
            (94, 1, u'prior'),
            (95, 1, u'written'),
            (96, 1, u'permission'),
            (97, 1, u'this'),
            (98, 1, u'software'),
            (99, 1, u'is'),
            (100, 1, u'provided'),
            (101, 1, u'by'),
            (102, 1, u'the'),
            (103, 1, u'copyright'),
            (104, 1, u'holders'),
            (105, 1, u'and'),
            (106, 1, u'contributors'),
            (107, 1, u'as'),
            (108, 1, u'is'),
            (109, 1, u'and'),
            (110, 1, u'any'),
            (111, 1, u'express'),
            (112, 1, u'or'),
            (113, 1, u'implied'),
            (114, 1, u'warranties'),
            (115, 1, u'including'),
            (116, 1, u'but'),
            (117, 1, u'not'),
            (118, 1, u'limited'),
            (119, 1, u'to'),
            (120, 1, u'no'),
            (121, 1, u'of')]

        assert expected == ngs_as_str(qry.query_runs[1].multigrams())

    def test_query_run_has_correct_offset(self):
        rule_dir = self.get_test_loc('query/runs/rules')
        rules = list(models._rules_proper(rule_dir))
        idx = index.LicenseIndex(rules)
        query_doc = self.get_test_loc('query/runs/query.txt')
        q = Query(location=query_doc, idx=idx)
        assert len(q.query_runs) == 2
        query_run = q.query_runs[0]
        assert 0 == query_run.start
        assert 0 == query_run.end
        assert [25] == query_run.tokens

        query_run = q.query_runs[1]
        assert 1 == query_run.start
        assert 123 == query_run.end


class TestQueryWithFullIndex(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_query_runs_from_rules_should_return_few_runs(self):
        # warning: this  is a long running function which builds ~ 4000 queries
        idx = index.get_index()
        rules_with_multiple_runs = 0
        for rule in idx.rules_by_rid:
            qry = Query(location=rule.text_file, idx=idx, line_threshold=4)
            if len(qry.query_runs) != 1:
                rules_with_multiple_runs += 1
        # uncomment to print which rules are a problem.
        #         print()
        #         print('Multiple runs for rule:', rule.identifier)
        #         for r in runs:
        #             print(r._as_dict(brief=True))
        # print('#Rules with Multiple runs:', rules_with_multiple_runs)
        assert rules_with_multiple_runs < 200

    def test_query_from_binary_lkms_1(self):
        location = self.get_test_loc('query/ath_pci.ko')
        idx = index.get_index()
        result = Query(location, idx=idx)
        assert 7 == len(result.query_runs)

    def test_query_from_binary_lkms_2(self):
        location = self.get_test_loc('query/eeepc_acpi.ko')
        idx = index.get_index()
        result = Query(location, idx=idx)
        assert 253 == len(result.query_runs)
        qr = result.query_runs[5]
        assert 'license gpl' in u' '.join(idx.tokens_by_tid[t] for t in qr.matchable_tokens())

    def test_query_from_binary_lkms_3(self):
        location = self.get_test_loc('query/wlan_xauth.ko')
        idx = index.get_index()
        result = Query(location, idx=idx)
        assert 485 == len(result.query_runs)

    def test_query_run_tokens(self):
        query_s = u' '.join(u'''
        3 unable to create proc entry license gpl description driver author eric depends 2 6 24 19 generic smp mod module acpi bus register driver proc acpi disabled acpi install notify acpi bus get status cache caches create proc entry bus generate proc event acpi evaluate object acpi remove notify remove proc entry acpi bus driver acpi acpi gcc gnu 4 2 3 ubuntu 4 2 3 gcc gnu 4 2 3 ubuntu 4 2 3 current stack pointer current stack pointer this module end usr src modules acpi include linux include asm include asm generic include acpi acpi c posix types 32 h types h types h h h h h
        '''.split())
        idx = index.get_index()
        result = Query(query_string=query_s, idx=idx)
        assert 1 == len(result.query_runs)
        qr = result.query_runs[0]
        assert query_s == u' '.join(idx.tokens_by_tid[t] for t in qr.tokens)

    def test_query_run_matchable_tokens(self):
        query_s = u' '.join(u'''
        3 unable to create proc entry license gpl description driver author eric depends 2 6 24 19 generic smp mod module acpi bus register driver proc acpi disabled acpi install notify acpi bus get status cache caches create proc entry bus generate proc event acpi evaluate object acpi remove notify remove proc entry acpi bus driver acpi acpi gcc gnu 4 2 3 ubuntu 4 2 3 gcc gnu 4 2 3 ubuntu 4 2 3 current stack pointer current stack pointer this module end usr src modules acpi include linux include asm include asm generic include acpi acpi c posix types 32 h types h types h h h h h
        '''.split())
        idx = index.get_index()
        result = Query(query_string=query_s, idx=idx)
        assert 1 == len(result.query_runs)
        qr = result.query_runs[0]
        assert query_s == u' '.join(idx.tokens_by_tid[t] for t in qr.tokens)
