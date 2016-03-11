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
from licensedcode.query import query_data
from licensedcode.query import query_ngrams


TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


class IndexTesting(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def get_test_rules(self, base, subset=None):
        base = self.get_test_loc(base)
        test_files = sorted(os.listdir(base))
        if subset:
            test_files = [t for t in test_files if t in subset]

        return [Rule(text_file=os.path.join(base, license_key), licenses=[license_key]) for license_key in test_files]


class TestQueryVector(IndexTesting):

    def test_iterlines_from_location(self):
        query = self.get_test_loc('index/queryperfect-mini')
        expected = [
            (2, u'The'),
            (3, u'Redistribution and use in source and binary forms, with or without modification, are permitted.'),
            (5, u'Always')
        ]
        result = list(iterlines(location=query))
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

        result = list(iterlines(query=query_string))
        assert expected == result

    def test_iterlines_complex(self):
        query = self.get_test_loc('index/querytokens')
        expected = [
            (4, u'Redistribution and use in source and binary forms,'),
            (6, u'* Redistributions of source code must'),
            (7, u'The this that is not there'),
            (8, u'Welcom to Jamaica'),
            (9, u'* Redistributions in binary form must'),
            (11, u'THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"'),
            (14, u'Redistributions')
        ]
        result = list(iterlines(location=query))
        assert expected == result


class TestQueryData(IndexTesting):

    def test_query_data_from_index_and_string(self):
        idx = index.LicenseIndex(self.get_test_rules('index/mini'))
        query = '''
            The
            Redistribution and use in source and binary are permitted.
        
            Athena capital of Grece 
            Paris and Athene
            Always'''.splitlines(False)

        line_by_pos, vector, tokens = query_data(location=query, dictionary=idx.dictionary)

        expected_lbp = {0: 3, 1: 3, 2: 3, 3: 3, 4: 3, 5: 3, 6: 3, 7: 3, 8: 3, 9: 6}
        assert expected_lbp == line_by_pos

        expected_qv = [
            (u'and', 0, [1, 5, 9]),
            (u'use', 3, [2]),
            (u'source', 4, [4]),
            (u'redistribution', 5, [0]),
            (u'permitted', 6, [8]),
            (u'in', 9, [3]),
            (u'binary', 11, [6]),
            (u'are', 12, [7])
        ]

        assert expected_qv == [(idx.tokens_by_tid[i], i, p) for i, p in enumerate(vector) if p]

        expected_toks = [
            (u'redistribution', 5),
            (u'and', 0),
            (u'use', 3),
            (u'in', 9),
            (u'source', 4),
            (u'and', 0),
            (u'binary', 11),
            (u'are', 12),
            (u'permitted', 6),
            (u'and', 0)
        ]
        assert expected_toks == [(idx.tokens_by_tid[t], t) for t in tokens]

    def test_query_data_from_index_and_location(self):
        idx = index.LicenseIndex(self.get_test_rules('index/bsd'))
        query = self.get_test_loc('index/querytokens')
        line_by_pos, vector, tokens = query_data(location=query, dictionary=idx.dictionary)

        expected_lbp = {0: 4, 1: 4, 2: 4, 3: 4, 4: 4, 5: 4, 6: 4, 7: 4, 8: 6,
                        9: 6, 10: 6, 11: 6, 12: 6, 13: 7, 14: 7, 15: 7, 16: 7,
                        17: 7, 18: 8, 19: 9, 20: 9, 21: 9, 22: 9, 23: 9, 24: 11,
                        25: 11, 26: 11, 27: 11, 28: 11, 29: 11, 30: 11, 31: 11,
                        32: 11, 33: 11, 34: 11, 35: 11, 36: 14}

        assert expected_lbp == line_by_pos

        expected_qv = [
            (u'the', 0, [13, 29]),
            (u'of', 1, [9]),
            (u'and', 2, [1, 5, 32]),
            (u'in', 3, [3, 20]),
            (u'to', 4, [18]),
            (u'is', 6, [16, 26, 35]),
            (u'this', 15, [14, 24]),
            (u'copyright', 16, [30]),
            (u'use', 18, [2]),
            (u'software', 19, [25]),
            (u'provided', 23, [27]),
            (u'must', 25, [12, 23]),
            (u'binary', 27, [6, 21]),
            (u'source', 29, [4, 10]),
            (u'redistributions', 30, [8, 19, 36]),
            (u'not', 31, [17]),
            (u'contributors', 35, [33]),
            (u'redistribution', 43, [0]),
            (u'by', 46, [28]),
            (u'that', 53, [15]),
            (u'forms', 79, [7]),
            (u'form', 80, [22]),
            (u'code', 90, [11]),
            (u'as', 93, [34]),
            (u'holders', 102, [31])
        ]

        assert expected_qv == [(idx.tokens_by_tid[i], i, p) for i, p in enumerate(vector) if p]

        expected_toks = [
            (u'redistribution', 43),
            (u'and', 2),
            (u'use', 18),
            (u'in', 3),
            (u'source', 29),
            (u'and', 2),
            (u'binary', 27),
            (u'forms', 79),
            (u'redistributions', 30),
            (u'of', 1),
            (u'source', 29),
            (u'code', 90),
            (u'must', 25),
            (u'the', 0),
            (u'this', 15),
            (u'that', 53),
            (u'is', 6),
            (u'not', 31),
            (u'to', 4),
            (u'redistributions', 30),
            (u'in', 3),
            (u'binary', 27),
            (u'form', 80),
            (u'must', 25),
            (u'this', 15),
            (u'software', 19),
            (u'is', 6),
            (u'provided', 23),
            (u'by', 46),
            (u'the', 0),
            (u'copyright', 16),
            (u'holders', 102),
            (u'and', 2),
            (u'contributors', 35),
            (u'as', 93),
            (u'is', 6),
            (u'redistributions', 30)
        ]
        assert expected_toks == [(idx.tokens_by_tid[t], t) for t in tokens]

    def test_query_data_solo(self):
        # setup, no index involved
        query = 'redistributions in binary form must redistributions in'
        tok_by_id = query.split()
        tok_dict = {}
        for tid, tok in enumerate(tok_by_id):
            if tok not in tok_dict:
                tok_dict[tok] = tid

        lines_by_pos, vector, tokens = query_data(query=query, dictionary=tok_dict)
        assert {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1} == lines_by_pos
        expected = [
            ('redistributions', [0, 5]),
            ('in', [1, 6]),
            ('binary', [2]),
            ('form', [3]),
            ('must', [4])
        ]
        result = [(tok_by_id[tid], posts) for tid, posts in enumerate(vector)]
        assert expected == result

        expected_toks = [
            ('redistributions', 0),
            ('in', 1),
            ('binary', 2),
            ('form', 3),
            ('must', 4),
            ('redistributions', 0),
            ('in', 1)
        ]
        assert expected_toks == [(tok_by_id[t], t) for t in tokens]

    def test_query_data_junk(self):
        tok_dict = {'binary':0, 'must':1}

        # two junks
        lines_by_pos, vector, tokens = query_data(query='binary must', dictionary=tok_dict)
        assert lines_by_pos
        len_junk = 1
        assert any(tid >= len_junk for tid, posts in enumerate(vector) if posts)
        assert [0, 1] == tokens

        # one junk
        lines_by_pos, vector, tokens = query_data(query='in binary', dictionary=tok_dict)
        assert lines_by_pos
        len_junk = 1
        assert not any(tid >= len_junk for tid, posts in enumerate(vector) if posts)
        assert [0] == tokens

        # one junk
        lines_by_pos, vector, tokens = query_data(query='binary is', dictionary=tok_dict)
        assert lines_by_pos
        len_junk = 0
        assert any(tid >= len_junk for tid, posts in enumerate(vector) if posts)
        assert [0] == tokens

    def test_query_data_vectors_are_same_for_different_query_formattings(self):
        test_files = [self.get_test_loc(f) for f in [
            'match_inv/queryformat/license2.txt',
            'match_inv/queryformat/license3.txt',
            'match_inv/queryformat/license4.txt',
            'match_inv/queryformat/license5.txt',
            'match_inv/queryformat/license6.txt',
        ]]

        rule_file = self.get_test_loc('match_inv/queryformat/license1.txt')
        idx = index.LicenseIndex([Rule(text_file=rule_file, licenses=['mit'])])
        _lbp, expected, _tokens = query_data(rule_file, dictionary=idx.dictionary)
        for tf in test_files:
            _lbp, result, _toks = query_data(tf, dictionary=idx.dictionary)
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


class TestQueryWithFullIndex(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_query_data_in_binary_lkms_1(self):
        location = self.get_test_loc('query/ath_pci.ko')
        idx = index.get_index()
        result = query_data(location, dictionary=idx.dictionary)
        assert result

    def test_query_data_in_binary_lkms_2(self):
        location = self.get_test_loc('query/eeepc_acpi.ko')
        idx = index.get_index()
        result = query_data(location, dictionary=idx.dictionary)
        assert result

    def test_query_data_in_binary_lkms_3(self):
        location = self.get_test_loc('query/wlan_xauth.ko')
        idx = index.get_index()
        result = query_data(location, dictionary=idx.dictionary)
        assert result

    def test_all_query_vectors_from_rules_should_not_create_any_all_junk_vector(self):
        # NOTE: we use high bitvectors as a proxy for query vectors
        idx = index.get_index()
        for rule_high_bv in idx.high_bitvectors_by_rid:
            assert rule_high_bv.any()
