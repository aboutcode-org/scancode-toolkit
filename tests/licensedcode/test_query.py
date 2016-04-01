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

from licensedcode.query import iterlines
from licensedcode.query import query_ngrams
from licensedcode.query import Query


TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


class IndexTesting(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def get_test_rules(self, base, subset=None):
        base = self.get_test_loc(base)
        test_files = sorted(os.listdir(base))
        if subset:
            test_files = [t for t in test_files if t in subset]

        return [Rule(text_file=os.path.join(base, license_key), licenses=[license_key]) for license_key in test_files]


class TestQueryText(IndexTesting):

    def test_iterlines_from_location(self):
        query_loc = self.get_test_loc('index/queryperfect-mini')
        expected = [
            (2, u'The'),
            (3, u'Redistribution and use in source and binary forms, with or without modification, are permitted.'),
            (5, u'Always')
        ]
        result = list(iterlines(location=query_loc))
        assert expected == result

    def test_iterlines_from_string(self):
        query_string = '''
            The   
            Redistribution and use in source and binary forms, with or without modification, are permitted.
            
            Always  
            is
 '''
        expected = [
            (2, 'The'),
            (3, 'Redistribution and use in source and binary forms, with or without modification, are permitted.'),
            (5, 'Always'),
            (6, 'is'),
        ]

        result = list(iterlines(query_string=query_string))
        assert expected == result

    def test_iterlines_complex(self):
        query_loc = self.get_test_loc('index/querytokens')
        expected = [
            (4, u'Redistribution and use in source and binary forms,'),
            (6, u'* Redistributions of source code must'),
            (7, u'The this that is not there'),
            (8, u'Welcom to Jamaica'),
            (9, u'* Redistributions in binary form must'),
            (11, u'THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"'),
            (15, u'Redistributions')
        ]
        result = list(iterlines(location=query_loc))
        assert expected == result

    def test_query_ngrams(self):
        query_tokens = '''
            Redistribution and use in source and binary are permitted.
            '''.split()

        result = list(query_ngrams(query_tokens, _ngram_length=4))
        expected = [
            (('Redistribution', 'and', 'use', 'in'), 0),
            (('and', 'use', 'in', 'source'), 1),
            (('use', 'in', 'source', 'and'), 2),
            (('in', 'source', 'and', 'binary'), 3),
            (('source', 'and', 'binary', 'are'), 4),
            (('and', 'binary', 'are', 'permitted.'), 5)]

        assert expected == result

    def test_query_ngrams_with_None(self):
        query_tokens = ['Redistribution', 'and', 'use', None, 'in', 'source', 'and', 'binary', 'are', None]
        result = list(query_ngrams(query_tokens, _ngram_length=4))
        expected = [
            (('in', 'source', 'and', 'binary'), 4),
            (('source', 'and', 'binary', 'are'), 5)
        ]
        assert expected == result


class TestQueryWithSingleRun(IndexTesting):

    def test_query_from_index_and_string(self):
        idx = index.LicenseIndex(self.get_test_rules('index/mini'))
        querys = '''
            The
            Redistribution and use in source and binary are permitted.
        
            Athena capital of Grece 
            Paris and Athene
            Always'''

        qry = Query(query_string=querys, idx=idx)
        runs = list(qry.query_runs(1000))
        assert len(runs) == 1
        query_run = runs[0]

        expected_lbp = {0: 3, 1: 3, 2: 3, 3: 3, 4: 3, 5: 3, 6: 3, 7: 3, 8: 3, 9: 6}
        assert expected_lbp == query_run.line_by_pos

        expected_qv = [
            (u'and', 0, [1, 5, 9]),
            (u'in', 3, [3]),
            (u'are', 4, [7]),
            (u'redistribution', 6, [0]),
            (u'source', 8, [4]),
            (u'permitted', 10, [8]),
            (u'use', 11, [2]),
            (u'binary', 12, [6])]
        assert expected_qv == [(idx.tokens_by_tid[i], i, p) for i, p in enumerate(query_run.vector()) if p]

        expected_toks = [
            (u'redistribution', 6),
            (u'and', 0),
            (u'use', 11),
            (u'in', 3),
            (u'source', 8),
            (u'and', 0),
            (u'binary', 12),
            (u'are', 4),
            (u'permitted', 10),
            (u'and', 0)]
        assert expected_toks == [(idx.tokens_by_tid[t], t) for t in query_run.tokens]

    def test_query_from_index_and_location(self):
        idx = index.LicenseIndex(self.get_test_rules('index/bsd'))
        query_loc = self.get_test_loc('index/querytokens')

        qry = Query(location=query_loc, idx=idx)
        runs = list(qry.query_runs(1000))
        assert len(runs) == 1
        query_run = runs[0]


        expected_lbp = {0: 4, 1: 4, 2: 4, 3: 4, 4: 4, 5: 4, 6: 4, 7: 4, 8: 6,
                        9: 6, 10: 6, 11: 6, 12: 6, 13: 7, 14: 7, 15: 7, 16: 7,
                        17: 7, 18: 8, 19: 9, 20: 9, 21: 9, 22: 9, 23: 9, 24: 11,
                        25: 11, 26: 11, 27: 11, 28: 11, 29: 11, 30: 11, 31: 11,
                        32: 11, 33: 11, 34: 11, 35: 11, 36: 15}

        assert expected_lbp == query_run.line_by_pos

        expected_qv = [
            (u'the', 0, [13, 29]),
            (u'of', 1, [9]),
            (u'and', 3, [1, 5, 32]),
            (u'in', 4, [3, 20]),
            (u'this', 5, [14, 24]),
            (u'to', 7, [18]),
            (u'is', 9, [16, 26, 35]),
            (u'not', 12, [17]),
            (u'by', 19, [28]),
            (u'as', 22, [34]),
            (u'that', 23, [15]),
            (u'copyright', 52, [30]),
            (u'use', 54, [2]),
            (u'software', 55, [25]),
            (u'provided', 59, [27]),
            (u'must', 60, [12, 23]),
            (u'binary', 62, [6, 21]),
            (u'contributors', 63, [33]),
            (u'redistributions', 64, [8, 19, 36]),
            (u'source', 66, [4, 10]),
            (u'redistribution', 71, [0]),
            (u'form', 86, [22]),
            (u'forms', 107, [7]),
            (u'code', 111, [11]),
            (u'holders', 118, [31])]

        assert expected_qv == [(idx.tokens_by_tid[i], i, p) for i, p in enumerate(query_run.vector()) if p]

        expected_toks = [
            (u'redistribution', 71),
            (u'and', 3),
            (u'use', 54),
            (u'in', 4),
            (u'source', 66),
            (u'and', 3),
            (u'binary', 62),
            (u'forms', 107),
            (u'redistributions', 64),
            (u'of', 1),
            (u'source', 66),
            (u'code', 111),
            (u'must', 60),
            (u'the', 0),
            (u'this', 5),
            (u'that', 23),
            (u'is', 9),
            (u'not', 12),
            (u'to', 7),
            (u'redistributions', 64),
            (u'in', 4),
            (u'binary', 62),
            (u'form', 86),
            (u'must', 60),
            (u'this', 5),
            (u'software', 55),
            (u'is', 9),
            (u'provided', 59),
            (u'by', 19),
            (u'the', 0),
            (u'copyright', 52),
            (u'holders', 118),
            (u'and', 3),
            (u'contributors', 63),
            (u'as', 22),
            (u'is', 9),
            (u'redistributions', 64)]

        assert expected_toks == [(idx.tokens_by_tid[t], t) for t in query_run.tokens]

    def test_query_junk(self):
        idx = index.LicenseIndex([Rule(_text='a is the binary')])

        assert {'the': 0, 'is': 1, 'a': 2, 'binary': 3} == idx.dictionary
        assert 3 == idx.len_junk

        # two junks
        q = Query(query_string='is a', idx=idx)
        qrun = list(q.query_runs(1000))[0]
        assert qrun.line_by_pos
        assert [[], [0], [1], []] == qrun.vector()
        assert [1, 2] == qrun.tokens

        # one junk
        q = Query(query_string='is binary', idx=idx)
        qrun = list(q.query_runs(1000))[0]
        assert qrun.line_by_pos
        assert [[], [0], [], [1]] == qrun.vector()
        assert [1, 3] == qrun.tokens

        # one junk
        q = Query(query_string='binary a', idx=idx)
        qrun = list(q.query_runs(1000))[0]
        assert qrun.line_by_pos
        assert [[], [], [1], [0]] == qrun.vector()
        assert [3, 2] == qrun.tokens

        # one unknown
        q = Query(query_string='that binary', idx=idx)
        qrun = list(q.query_runs(1000))[0]
        assert qrun.line_by_pos
        assert [[], [] , [], [0]] == qrun.vector()
        assert [3] == qrun.tokens

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
        expected = list(q.query_runs(1000))[0]
        for tf in test_files:
            q = Query(tf, idx=idx)
            qr = list(q.query_runs(1000))[0]
            assert expected.vector() == qr.vector()


class TestQueryWithMultipleRuns(IndexTesting):

    def test_query_runs_from_location(self):
        idx = index.LicenseIndex(self.get_test_rules('index/bsd'))
        query_loc = self.get_test_loc('index/querytokens')
        qry = Query(location=query_loc, idx=idx)
        runs = qry.query_runs(3)
        result = [q._as_dict(brief=True) for q in runs]

        expected = [
            {'lines': (4, 11),
             'matchable': True,
             'start': 0,
             'tokens': u'redistribution and use in source ... holders and contributors as is'},
            {'lines': (15, 15),
             'matchable': True,
             'start': 36,
             'tokens': u'redistributions'}]

        assert expected == result

    def test_QueryRun_vector(self):
        idx = index.LicenseIndex([Rule(_text= 'redistributions in binary form must redistributions in')])
        qry = Query(query_string='redistributions in binary form must redistributions in', idx=idx)
        qruns = list(qry.query_runs())
        assert 1== len(qruns)
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

    def test_QueryRun_copy(self):
        idx = index.LicenseIndex([Rule(_text= 'redistributions in binary form must redistributions in')])
        qry = Query(query_string='redistributions in binary form must redistributions in', idx=idx)
        qruns = list(qry.query_runs())
        assert 1== len(qruns)
        qr = qruns[0]
        from copy import copy
        qr2= copy(qr)
        assert qr is not qr2
        assert qr == qr2

    
    def test_query_runs2(self):
        idx = index.LicenseIndex(self.get_test_rules('index/bsd'))
        query_loc = self.get_test_loc('index/queryruns')
        expected = [
            {'lines': (4, 12),
              'matchable': True,
              'start': 0,
              'tokens': u'the redistribution and use in ... 2 1 3 c 4'},
             {'lines': (14, 14),
              'matchable': True,
              'start': 85,
              'tokens': u'this software is provided by ... holders and contributors as is'},
             {'lines': (21, 21),
              'matchable': True,
              'start': 98,
              'tokens': u'redistributions'}]

        qry = Query(location=query_loc, idx=idx)
        qruns = list(qry.query_runs())
        result = [q._as_dict(brief=True) for q in qruns]
        assert expected == result

    def test_query_runs_from_rules_should_return_few_runs(self):
        # warning: this  is a long running function
        idx = index.get_index()
        rules_with_multiple_runs = 0
        for rule in idx.rules_by_rid:
            qry = Query(location=rule.text_file, idx=idx)
            runs = list(qry.query_runs(4))
            if len(runs) != 1:
                rules_with_multiple_runs += 1
        # uncomment to print which rules are a problem.
        #         print()
        #         print('Multiple runs for rule:', rule.identifier())
        #         for r in runs:
        #             print(r._as_dict(brief=True))
        # print('#Rules with Multiple runs:', rules_with_multiple_runs)
        assert 100 > rules_with_multiple_runs


class TestQueryWithFullIndex(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_query_from_binary_lkms_1(self):
        location = self.get_test_loc('query/ath_pci.ko')
        idx = index.get_index()
        result = Query(location, idx=idx)
        result = list(result.query_runs())
        assert result

    def test_query_from_binary_lkms_2(self):
        location = self.get_test_loc('query/eeepc_acpi.ko')
        idx = index.get_index()
        result = Query(location, idx=idx)
        result = list(result.query_runs())
        assert result

    def test_query_from_binary_lkms_3(self):
        location = self.get_test_loc('query/wlan_xauth.ko')
        idx = index.get_index()
        result = Query(location, idx=idx)
        result = list(result.query_runs())
        assert result
