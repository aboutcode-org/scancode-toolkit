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

from licensedcode import match_chunk
from licensedcode.models import Rule


TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


class IndexTesting(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_index_starters_no_gaps(self):
        rule_tokens = 'this is a simple rule'.split()
        gaps = set()
        result = match_chunk.index_starters(rule_tokens, gaps, _ngram_length=3)
        assert  [(('this', 'is', 'a',), 0)] == list(result)

    def test_index_starters_no_gaps_smaller_than_ngram_length(self):
        rule_tokens = 'this is'.split()
        gaps = set()
        result = match_chunk.index_starters(rule_tokens, gaps, _ngram_length=3)
        assert [] == list(result)

    def test_index_starters_with_one_gap(self):
        rule_tokens = 'this is a simple rule after the gap this is the end'.split()
        #                 0  1 2      3    4G    5   6   7    8  9  10  11
        gaps = {4, }
        result = match_chunk.index_starters(rule_tokens, gaps, _ngram_length=3)
        expected = [
            (('this', 'is', 'a',), 0),
            (('after', 'the', 'gap',), 5),
        ]
        assert expected == list(result)

    def test_index_starters_with_multiple_gaps(self):
        rule_tokens = 'this is a simple rule after the gap this is not but really end'.split()
        #                 0  1 2      3    4G    5   6   7    8  9G 10  11     12  13
        # gaps
        gaps = {4, 9}
        result = match_chunk.index_starters(rule_tokens, gaps, _ngram_length=3)
        expected = [
            (('this', 'is', 'a',), 0),
            (('after', 'the', 'gap',), 5),
            (('not', 'but', 'really',), 10),
        ]
        assert expected == list(result)

    def test_index_starters_with_multiple_gaps_and_chunks_shorter_than_ngram_length(self):
        rule_tokens = 'this is a simple rule after the gap this is not but really end'.split()
        #                 0  1 2      3    4G    5   6   7    8  9G 10  11     12  13
        # gaps
        gaps = {4, 9}
        result = match_chunk.index_starters(rule_tokens, gaps, _ngram_length=5)
        expected = [
            (('this', 'is', 'a', 'simple', 'rule',), 0),
            (('after', 'the', 'gap', 'this', 'is',), 5),
        ]
        assert expected == list(result)

    def test_index_starters_with_short_inter_gaps_shorter_than_ngram_length(self):
        rule_tokens = 'this is a simple rule after the gap this is not but really end'.split()
        #                 0  1 2      3    4G    5   6G   7    8  9G 10  11     12  13
        # gaps
        gaps = {4, 6, 9}
        result = match_chunk.index_starters(rule_tokens, gaps, _ngram_length=5)
        expected = [
            (('this', 'is', 'a', 'simple', 'rule',), 0),
        ]
        assert expected == list(result)

    def test_index_starters_with_inter_gap_equal_to_ngram_length(self):
        test_text = '''I hereby abandon any{{SAX 2.0 (the)}}, and release all of {{the SAX 2.0 }}source code of his'''
        rule = Rule(_text=test_text, licenses=['public-domain'])
        rule_tokens = list(rule.tokens())
        assert ['i', 'hereby', 'abandon', 'any', 'and', 'release', 'all', 'of', 'source', 'code', 'of', 'his'] == rule_tokens

        gaps = rule.gaps
        assert set([3, 7]) == gaps

        result = match_chunk.index_starters(rule_tokens, gaps, _ngram_length=4)
        expected = [
            (('i', 'hereby', 'abandon', 'any'), 0),
            (('and', 'release', 'all', 'of'), 4),
            (('source', 'code', 'of', 'his'), 8)
        ]
        assert expected == list(result)

    def test_index_starters_with_multiple_gaps_and_short_start(self):
        test_text = """
        Copyright {{10 Copyright}}. 
        All 
        Rights 
        Reserved.
        Redistribution
        materials 
        provided
        The
        name {{5 Author}} 
        must 
        not 
        be 
        used 
        to 
        endorse
        or
        promote {{5 Author}}.
        For 
        written
         permission, 
         please 
         contact {{5 Author Contact}}.
        4. 
        Products 
        derived 
        from 
        this 
        Software 
        may 
        not 
        be 
        called {{5 Product}}
        nor 
        may {{5 Product}} 
        appear 
        in 
        their 
        names 
        without 
        prior {{10 Author}}
        is 
        a 
        registered 
        trademark 
        of {{5 Author}}.
        5. 
        Due 
        credit 
        should
        be 
        given 
        to {{10 Author and URL}}
        THIS 
        SOFTWARE 
        IS 
        PROVIDED 
        BY {{10 org}}
        ``AS 
        IS'' 
        AND 
        ANY 
        EXPRESSED
         OR
          IMPLIED 
         IN 
         NO 
         EVENT 
         SHALL {{5 Author}} 
         OR 
         ITS 
         CONTRIBUTORS 
         BE 
         LIABLE {{tail gap}}"""
        rule = Rule(_text=test_text, licenses=['public-domain'])
        rule_tokens = list(rule.tokens())

        gaps = rule.gaps

        assert set([0, 8, 16, 21, 31, 33, 39, 44, 51, 56, 67]) == gaps

        result = match_chunk.index_starters(rule_tokens, gaps, _ngram_length=4)
        expected = [
            (('all', 'rights', 'reserved', 'redistribution'), 1),
            (('must', 'not', 'be', 'used'), 9),
            (('for', 'written', 'permission', 'please'), 17),
            (('4', 'products', 'derived', 'from'), 22),
            (('appear', 'in', 'their', 'names'), 34),
            (('is', 'a', 'registered', 'trademark'), 40),
            (('5', 'due', 'credit', 'should'), 45),
            (('this', 'software', 'is', 'provided'), 52),
            (('as', 'is', 'and', 'any'), 57),
            (('or', 'its', 'contributors', 'be'), 68)
        ]

        assert expected == list(result)
