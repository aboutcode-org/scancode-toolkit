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


def abuild_mock_index(rule_text, len_junk=0):
    """
    Return a mock index with the few fields needed for query building using a
    string representing a single rule text.
    """
    from collections import namedtuple
    MockIndex = namedtuple('MockIndex', 'dictionary tokens_by_tid len_junk len_tokens')
    tokens_by_tid = sorted(set(rule_text.lower().split()))
    dictionary = {tok: tid for tid, tok in enumerate(tokens_by_tid)}
    len_tokens = len(tokens_by_tid)
    return MockIndex(dictionary, tokens_by_tid, len_junk, len_tokens)


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
            [6, 0, 11, 3, 8, 0, 12, 4, 10],
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

        expected = [None, 'redistribution', 'and', 'use', 'in', 'source', 'and', 'binary', 'are', 'permitted', None, None, None, None, None, 'and', None, None]
        result = tks_as_str(qry.tokens)
        assert expected == result

        assert 1 == len(qry.query_runs)
        qr1 = qry.query_runs[0]
        assert 1 == qr1.start
        assert 15 == qr1.end
        assert 15 == len(qr1)
        expected = ['redistribution', 'and', 'use', 'in', 'source', 'and', 'binary', 'are', 'permitted', None, None, None, None, None, 'and']
        result = tks_as_str(qr1.tokens)
        assert expected == result

    def test_QueryRuns_ngrams(self):
        rule_text = 'Redistribution and use in source and binary forms with or without modification are permitted'
        idx = index.LicenseIndex([Rule(_text=rule_text, licenses=['bsd'])])
        querys = '''
            The
            Redistribution and use in source and binary are permitted.
        
            Athena capital of Grece 
            Paris and Athene
            Always'''

        qry = Query(query_string=querys, idx=idx)
        assert set([1, 2, 3, 4, 5, 6, 7, 8, 9, 15]) == qry.matchable_positions

        assert 1 == len(qry.query_runs)
        qrun = qry.query_runs[0]

        # convert tid to actual token strings
        tks_as_str = lambda tks: [None if tid is None else idx.tokens_by_tid[tid] for tid  in tks]

        expected = ['redistribution', 'and', 'use', 'in', 'source', 'and', 'binary', 'are', 'permitted', None, None, None, None, None, 'and']
        assert expected == tks_as_str(qrun.tokens)

        assert 1 == qrun.start
        assert 15 == qrun.end
        assert 15 == qrun.end

        expected = ['redistribution', 'and', 'use', 'in', 'source', 'and', 'binary', 'are', 'permitted', None, None, None, None, None, 'and']
        result = tks_as_str(qrun.tokens)
        assert expected == result

        # convert ngrams to actual token strings
        ngs_as_str = lambda pos_ngs: [(pos, ' '.join(idx.tokens_by_tid[tid] for tid in ng)) for pos, ng in pos_ngs]

        result = ngs_as_str(qrun.ngrams())
        expected = [
            (1, 'redistribution and use in'),
            (2, 'and use in source'),
            (3, 'use in source and'),
            (4, 'in source and binary'),
            (5, 'source and binary are'),
            (6, 'and binary are permitted')
        ]
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
        assert expected == tks_as_str(qry.tokens)

        assert 2 == len(qry.query_runs)
        qrun = qry.query_runs[0]
        expected = ['redistribution', 'and', 'use', 'in', 'source', 'and', 'binary', 'forms', 'with', 'or', 'without', 'modification', 'are', 'permitted']
        assert expected == tks_as_str(qrun.tokens)
        assert 1 == qrun.start
        assert 14 == qrun.end

        qrun = qry.query_runs[1]
        expected = ['modification']
        assert expected == tks_as_str(qrun.tokens)
        assert 17 == qrun.start
        assert 17 == qrun.end

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

        expected_qv = [
            (u'the', 0, [13, 32]),
            (u'of', 1, [9]),
            (u'and', 3, [1, 5, 35]),
            (u'in', 4, [3, 23]),
            (u'this', 5, [14, 27]),
            (u'copyright', 6, [33]),
            (u'to', 8, [20]),
            (u'is', 10, [16, 29, 38]),
            (u'not', 12, [17]),
            (u'by', 19, [31]),
            (u'as', 22, [37]),
            (u'that', 23, [15]),
            (u'code', 31, [11]),
            (u'use', 56, [2]),
            (u'software', 57, [28]),
            (u'provided', 61, [30]),
            (u'must', 62, [12, 26]),
            (u'binary', 64, [6, 24]),
            (u'contributors', 65, [36]),
            (u'redistributions', 66, [8, 22, 39]),
            (u'source', 68, [4, 10]),
            (u'redistribution', 74, [0]),
            (u'form', 89, [25]),
            (u'forms', 110, [7]),
            (u'holders', 120, [34])]

        assert expected_qv == [(idx.tokens_by_tid[i], i, p) for i, p in enumerate(query_run.vector()) if p]

        expected_toks = [
            (u'redistribution', 74),
            (u'and', 3),
            (u'use', 56),
            (u'in', 4),
            (u'source', 68),
            (u'and', 3),
            (u'binary', 64),
            (u'forms', 110),
            (u'redistributions', 66),
            (u'of', 1),
            (u'source', 68),
            (u'code', 31),
            (u'must', 62),
            (u'the', 0),
            (u'this', 5),
            (u'that', 23),
            (u'is', 10),
            (u'not', 12),
            (None, None),
            (None, None),
            (u'to', 8),
            (None, None),
            (u'redistributions', 66),
            (u'in', 4),
            (u'binary', 64),
            (u'form', 89),
            (u'must', 62),
            (u'this', 5),
            (u'software', 57),
            (u'is', 10),
            (u'provided', 61),
            (u'by', 19),
            (u'the', 0),
            (u'copyright', 6),
            (u'holders', 120),
            (u'and', 3),
            (u'contributors', 65),
            (u'as', 22),
            (u'is', 10),
            (u'redistributions', 66)]

        assert expected_toks == [(None if t is None else idx.tokens_by_tid[t], t) for t in query_run.tokens]

    def test_query_run_vector_and_tokens_with_junk(self):
        idx = index.LicenseIndex([Rule(_text='a is the binary')])

        assert {'the': 0, 'is': 1, 'a': 2, 'binary': 3} == idx.dictionary
        assert 3 == idx.len_junk

        # two junks
        q = Query(query_string='is a', idx=idx)
        qrun = q.query_runs[0]
        assert qrun.line_by_pos
        assert [[], [0], [1], []] == qrun.vector()
        assert [1, 2] == qrun.tokens

        # one junk
        q = Query(query_string='is binary', idx=idx)
        qrun = q.query_runs[0]
        assert qrun.line_by_pos
        assert [[], [0], [], [1]] == qrun.vector()
        assert [1, 3] == qrun.tokens

        # one junk
        q = Query(query_string='binary a', idx=idx)
        qrun = q.query_runs[0]
        assert qrun.line_by_pos
        assert [[], [], [1], [0]] == qrun.vector()
        assert [3, 2] == qrun.tokens

        # one unknown
        q = Query(query_string='that binary', idx=idx)
        qrun = q.query_runs[0]
        assert qrun.line_by_pos
        assert [None, 3] == qrun.tokens
        assert [[], [] , [], [1]] == qrun.vector()

    def test_query_vectors_are_same_for_different_text_formatting(self):

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
            assert expected.vector() == qr.vector()


class TestQueryWithMultipleRuns(IndexTesting):

    def test_query_runs_from_location(self):
        idx = index.LicenseIndex(self.get_test_rules('index/bsd'))
        query_loc = self.get_test_loc('index/querytokens')
        qry = Query(location=query_loc, idx=idx, line_threshold=3)
        result = [q._as_dict(brief=True) for q in qry.query_runs]

        expected = [
            {'matchable': True,
             'start': 0,
             'end': 38,
             'tokens': u'redistribution and use in source ... holders and contributors as is'},
            {'matchable': True,
             'start': 39,
             'end': 39,
             'tokens': u'redistributions'}
        ]

        assert expected == result

    def test_query_runs_three_runs(self):
        idx = index.LicenseIndex(self.get_test_rules('index/bsd'))
        query_loc = self.get_test_loc('index/queryruns')
        qry = Query(location=query_loc, idx=idx)
        expected = [
            {'matchable': True,
             'start': 0,
             'end': 95,
             'tokens': u'the redistribution and use in ... 2 1 3 c 4'},
            {'matchable': True,
             'start': 96,
             'end': 108,
             'tokens': u'this software is provided by ... holders and contributors as is'},
            {'matchable': True,
             'start': 113,
             'end': 113,
             'tokens': u'redistributions'}
        ]

        result = [q._as_dict(brief=True) for q in qry.query_runs]
        assert expected == result

    def test_QueryRun_vector(self):
        idx = index.LicenseIndex([Rule(_text='redistributions in binary form must redistributions in')])
        qry = Query(query_string='redistributions in binary form must redistributions in', idx=idx)
        qruns = qry.query_runs
        assert 1 == len(qruns)
        qr = qruns[0]
        # test
        qv = qr.vector()
        result = [(idx.tokens_by_tid[tid], posts) for tid, posts in enumerate(qv)]
        expected = [
            ('in', [1, 6]),
            ('redistributions', [0, 5]),
            ('form', [3]),
            ('must', [4]),
            ('binary', [2])]
        assert expected == result

    def test_query_runs_text_is_correct(self):
        test_rules = self.get_test_rules('query/full_text/idx',)
        idx = index.LicenseIndex(test_rules)
        query_loc = self.get_test_loc('query/full_text/query')
        qry = Query(location=query_loc, idx=idx, line_threshold=3)
        qruns = qry.query_runs
        result = [u' '.join(u'<None>' if t is None else idx.tokens_by_tid[t] for t in qr.tokens) for qr in qruns]

        expected = [
            u'<None> <None> <None> this',

            u' '.join(u'''redistribution and use in source and binary forms with or
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
            software even if advised of the possibility of such damage'''.split()),
            u'no <None> of',
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
            'matchable': True,
            'start': 0,
            'end': 216,
            'tokens': u'x11 license copyright c 1996 ... trademark of x consortium inc'
        }]
        assert 217 == len(qry.query_runs[0].tokens)
        assert expected == result

    def test_query_run_ngrams_are_correct_with_template_and_multiple_rules(self):
        test_rules = self.get_test_rules('index/bsd_templates',)
        idx = index.LicenseIndex(test_rules)
        querys= u'''
            
            
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
        ngs_as_str = lambda pos_ngs: [(pos, ' '.join(idx.tokens_by_tid[tid] for tid in ng)) for pos, ng in pos_ngs]

        assert [] == list(qry.query_runs[0].ngrams())
        expected = [
            (4, u'redistribution and use in'),
            (5, u'and use in source'),
            (6, u'use in source and'),
            (7, u'in source and binary'),
            (8, u'source and binary forms'),
            (9, u'and binary forms with'),
            (10, u'binary forms with or'),
            (11, u'forms with or without'),
            (12, u'with or without modification'),
            (13, u'or without modification are'),
            (14, u'without modification are permitted'),
            (15, u'modification are permitted provided'),
            (16, u'are permitted provided that'),
            (17, u'permitted provided that the'),
            (18, u'provided that the following'),
            (19, u'that the following conditions'),
            (20, u'the following conditions are'),
            (21, u'following conditions are met'),
            (22, u'conditions are met redistributions'),
            (23, u'are met redistributions of'),
            (24, u'met redistributions of source'),
            (25, u'redistributions of source code'),
            (26, u'of source code must'),
            (27, u'source code must retain'),
            (28, u'code must retain the'),
            (29, u'must retain the above'),
            (30, u'retain the above copyright'),
            (31, u'the above copyright notice'),
            (32, u'above copyright notice this'),
            (33, u'copyright notice this list'),
            (34, u'notice this list of'),
            (35, u'this list of conditions'),
            (36, u'list of conditions and'),
            (37, u'of conditions and the'),
            (38, u'conditions and the following'),
            (39, u'and the following disclaimer'),
            (40, u'the following disclaimer redistributions'),
            (41, u'following disclaimer redistributions in'),
            (42, u'disclaimer redistributions in binary'),
            (43, u'redistributions in binary form'),
            (44, u'in binary form must'),
            (45, u'binary form must reproduce'),
            (46, u'form must reproduce the'),
            (47, u'must reproduce the above'),
            (48, u'reproduce the above copyright'),
            (49, u'the above copyright notice'),
            (50, u'above copyright notice this'),
            (51, u'copyright notice this list'),
            (52, u'notice this list of'),
            (53, u'this list of conditions'),
            (54, u'list of conditions and'),
            (55, u'of conditions and the'),
            (56, u'conditions and the following'),
            (57, u'and the following disclaimer'),
            (58, u'the following disclaimer in'),
            (59, u'following disclaimer in the'),
            (60, u'disclaimer in the documentation'),
            (61, u'in the documentation and'),
            (62, u'the documentation and or'),
            (63, u'documentation and or other'),
            (64, u'and or other materials'),
            (65, u'or other materials provided'),
            (66, u'other materials provided with'),
            (67, u'materials provided with the'),
            (68, u'provided with the distribution'),
            (69, u'with the distribution neither'),
            (70, u'the distribution neither the'),
            (71, u'distribution neither the name'),
            (72, u'neither the name of'),
            (77, u'inc nor the names'),
            (78, u'nor the names of'),
            (79, u'the names of its'),
            (80, u'names of its contributors'),
            (81, u'of its contributors may'),
            (82, u'its contributors may be'),
            (83, u'contributors may be used'),
            (84, u'may be used to'),
            (85, u'be used to endorse'),
            (86, u'used to endorse or'),
            (87, u'to endorse or promote'),
            (88, u'endorse or promote products'),
            (89, u'or promote products derived'),
            (90, u'promote products derived from'),
            (91, u'products derived from this'),
            (92, u'derived from this software'),
            (93, u'from this software without'),
            (94, u'this software without specific'),
            (95, u'software without specific prior'),
            (96, u'without specific prior written'),
            (97, u'specific prior written permission'),
            (98, u'prior written permission this'),
            (99, u'written permission this software'),
            (100, u'permission this software is'),
            (101, u'this software is provided'),
            (102, u'software is provided by'),
            (103, u'is provided by the'),
            (104, u'provided by the copyright'),
            (105, u'by the copyright holders'),
            (106, u'the copyright holders and'),
            (107, u'copyright holders and contributors'),
            (108, u'holders and contributors as'),
            (109, u'and contributors as is'),
            (110, u'contributors as is and'),
            (111, u'as is and any'),
            (112, u'is and any express'),
            (113, u'and any express or'),
            (114, u'any express or implied'),
            (115, u'express or implied warranties'),
            (116, u'or implied warranties including'),
            (117, u'implied warranties including but'),
            (118, u'warranties including but not'),
            (119, u'including but not limited'),
            (120, u'but not limited to'),
]
        
        assert expected == ngs_as_str(qry.query_runs[1].ngrams())


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
        #         print('Multiple runs for rule:', rule.identifier())
        #         for r in runs:
        #             print(r._as_dict(brief=True))
        # print('#Rules with Multiple runs:', rules_with_multiple_runs)
        assert rules_with_multiple_runs < 60

    def test_query_from_binary_lkms_1(self):
        location = self.get_test_loc('query/ath_pci.ko')
        idx = index.get_index()
        result = Query(location, idx=idx)
        assert 4 == len(result.query_runs)

    def test_query_from_binary_lkms_2(self):
        location = self.get_test_loc('query/eeepc_acpi.ko')
        idx = index.get_index()
        result = Query(location, idx=idx)
        assert 109 == len(result.query_runs)

    def test_query_from_binary_lkms_3(self):
        location = self.get_test_loc('query/wlan_xauth.ko')
        idx = index.get_index()
        result = Query(location, idx=idx)
        assert 291 == len(result.query_runs)
