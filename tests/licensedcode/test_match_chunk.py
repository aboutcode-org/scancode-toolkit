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

from array import array
import os

from commoncode.testcase import FileBasedTesting

from licensedcode import match_chunk
from licensedcode import index
from licensedcode.match import get_texts
from licensedcode.models import Rule
from licensedcode.models import rules
from unittest.case import expectedFailure
from licensedcode import frequent_tokens


TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


class IndexNgramTest(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_ngrams_to_slices(self):
        rule_tokens = 'this is a simple rule after the gap this is the end'.split()
        #                 0  1 2      3    4G    5   6   7    8  9  10  11
        ngram_length = 3
        ngrams = {
            ('this', 'is', 'a'): array('h', [0]),
            ('is', 'a', 'simple'): array('h', [1]),
            ('a', 'simple', 'rule'): array('h', [2]),
            ('after', 'the', 'gap'): array('h', [5]),
            ('the', 'gap', 'this'): array('h', [6]),
            ('gap', 'this', 'is'): array('h', [7]),
            ('this', 'is', 'the'): array('h', [8]),
            ('is', 'the', 'end'): array('h', [9]),
        }
        for ngram, start in ngrams.items():
            start = start[0]
            assert ngram == tuple(rule_tokens[start:start + ngram_length])

    @expectedFailure
    def test_index_multigrams_no_gaps(self):
        rule_text = 'this is a simple rule'
        rule = Rule(_text=rule_text, licenses=['test'],)
        idx = index.LicenseIndex([rule], ngram_length=5)
        assert not rule.gaps
        rule_tokens = idx.tids_by_rid[0]
        result = match_chunk.index_multigrams(rule_tokens, rule.gaps, len_junk=idx.len_junk, ngram_length=5)
        expected = [{u'rule': [4]}]
        assert expected == self.index_multigrams_as_str(result, idx)

    @expectedFailure
    def test_index_multigrams_no_gaps_smaller_than_ngram_length(self):
        rule_text = 'this must is'
        rule = Rule(_text=rule_text, licenses=['public-domain'])
        idx = index.LicenseIndex([rule])
        assert set([]) == rule.gaps
        rule_tokens = idx.tids_by_rid[0]
        result = match_chunk.index_multigrams(rule_tokens, rule.gaps, len_junk=idx.len_junk)
        assert [{u'must': [1], u'this': [0]}, {u'this must': [0]}] == self.index_multigrams_as_str(result, idx)

    @expectedFailure
    def test_index_multigrams_with_multiple_gaps_and_chunks_shorter_than_ngram_length(self):
        rule_text = 'this is a simple rule{{}} after the gap this is{{}} not but really end'
        #                 0  1 2      3    4G        5   6   7    8  9G    10  11     12  13
        rule = Rule(_text=rule_text, licenses=['test'],)
        idx = index.LicenseIndex([rule], ngram_length=5)
        assert {4, 9} == rule.gaps
        rule_tokens = idx.tids_by_rid[0]

        result = match_chunk.index_multigrams(rule_tokens, rule.gaps, len_junk=idx.len_junk, ngram_length=5)
        expected = [
            {
             u'simple': [3],
             u'rule': [4],
             u'after': [5],
             u'gap': [7],
             u'not': [10],
             u'but': [11],
             u'really': [12],
             u'end': [13],
            },
            {
             u'simple rule': [3],
             u'but really': [11],
             u'not but': [10],
             u'really end': [12],
             },
            {
             u'after the gap': [5],
             u'not but really': [10],
             u'but really end': [11],
            },
            {u'not but really end': [10]}
        ]
        assert expected == self.index_multigrams_as_str(result, idx)

    # convert index to strings
    def index_multigrams_as_str(self, res, idx):
        tks_as_str = lambda tks: u' '.join(idx.tokens_by_tid[tid] for tid  in array('h', tks))
        ret = []
        for l, posts_by_multigram in enumerate(res):
            if l == 0:
                continue
            if posts_by_multigram == 0:
                continue
            ret.append({tks_as_str(mgram): list(posts) for mgram, posts in posts_by_multigram.items()})
        return ret

    @expectedFailure
    def test_index_multigrams_with_short_inter_gaps_shorter_than_ngram_length(self):
        rule_text = 'this is a simple rule{{}} after the{{}} gap this is{{}} not but really end'
        #               0  1 2      3      4G     5       6G   7    8     9G  10  11     12  13
        # gaps
        rule = Rule(_text=rule_text, licenses=['test'],)
        idx = index.LicenseIndex([rule], ngram_length=5)
        gaps = {4, 6, 9}
        assert rule.gaps == gaps
        rule_tokens = idx.tids_by_rid[0]

        result = match_chunk.index_multigrams(rule_tokens, gaps, len_junk=idx.len_junk, ngram_length=5)

        expected = [
            {u'after': [5],
             u'but': [11],
             u'end': [13],
             u'gap': [7],
             u'not': [10],
             u'really': [12],
             u'rule': [4],
             u'simple': [3]},
            {u'but really': [11],
             u'not but': [10],
             u'really end': [12],
             u'simple rule': [3]},
            {u'but really end': [11], u'not but really': [10]},
            {u'not but really end': [10]}
        ]

        assert expected == self.index_multigrams_as_str(result, idx)

    @expectedFailure
    def test_index_multigrams_with_inter_gap_equal_to_ngram_length(self):
        test_text = '''I hereby abandon any{{SAX 2.0 (the)}}, and release all of {{the SAX 2.0 }}source code of his'''
        rule = Rule(_text=test_text, licenses=['public-domain'])
        idx = index.LicenseIndex([rule], ngram_length=5)
        gaps = {3, 7}
        assert rule.gaps == gaps
        rule_tokens = idx.tids_by_rid[0]

        result = match_chunk.index_multigrams(rule_tokens, gaps, len_junk=idx.len_junk, ngram_length=5)
        expected = [{u'abandon': [2], u'hereby': [1], u'source': [8]}, {u'hereby abandon': [1]}]
        assert expected == self.index_multigrams_as_str(result, idx)

    @expectedFailure
    def test_index_multigrams_with_multiple_gaps_and_short_start(self):
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
        idx = index.LicenseIndex([rule], ngram_length=5)
        gaps = set([0, 8, 16, 21, 31, 33, 39, 44, 51, 56, 67])
        assert rule.gaps == gaps
        rule_tokens = idx.tids_by_rid[0]

        result = match_chunk.index_multigrams(rule_tokens, gaps, len_junk=idx.len_junk, ngram_length=5)
        expected = [
            {u'appear': [34],
             u'called': [31],
             u'contact': [21],
             u'contributors': [70],
             u'credit': [47],
             u'derived': [24],
             u'endorse': [14],
             u'expressed': [61],
             u'implied': [63],
             u'liable': [72],
             u'materials': [5],
             u'must': [9],
             u'permission': [19],
             u'products': [23],
             u'promote': [16],
             u'provided': [6, 55],
             u'redistribution': [4],
             u'registered': [42],
             u'shall': [67],
             u'software': [27, 53],
             u'trademark': [43],
             u'used': [12],
             u'written': [18]},
            {u'materials provided': [5],
             u'products derived': [23],
             u'redistribution materials': [4],
             u'registered trademark': [42],
             u'written permission': [18]},
            {u'contributors be liable': [70],
             u'endorse or promote': [14],
             u'expressed or implied': [61],
             u'permission please contact': [19],
             u'redistribution materials provided': [4],
             u'software is provided': [53],
             u'used to endorse': [12]},
            {u'derived from this software': [24],
             u'must not be used': [9],
             u'written permission please contact': [18]},
            {u'implied in no event shall': [63],
             u'products derived from this software': [23],
             u'software may not be called': [27],
             u'used to endorse or promote': [12]}
        ]
        assert expected == self.index_multigrams_as_str(result, idx)


class TestMatchChunk(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_match_template_with_few_tokens_around_gaps_is_wholly_chunk_matched(self):
        # was failing when a gapped token (from a template) starts at a
        # beginning of an index doc. We may still skip that, but capture a large match anyway.

        rule_text = u'''
            Copyright {{some copyright}} 
            THIS IS FROM {{THE CODEHAUS}} AND CONTRIBUTORS
            IN NO EVENT SHALL {{THE CODEHAUS}} OR ITS CONTRIBUTORS BE LIABLE
            EVEN IF ADVISED OF THE {{POSSIBILITY OF SUCH}} DAMAGE
        '''

        rule = Rule(_text=rule_text, licenses=['test'],)
        idx = index.LicenseIndex([rule])

        querys = u'''
            Copyright 2003 (C) James. All Rights Reserved.
            THIS IS FROM THE CODEHAUS AND CONTRIBUTORS
            IN NO EVENT SHALL THE CODEHAUS OR ITS CONTRIBUTORS BE LIABLE
            EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
        '''
        result = idx.match(query_string=querys)
        assert 1 == len(result)
        match = result[0]
        assert 'multigram_chunk' == match._type

        exp_qtext = u"""
            Copyright <no-match> <no-match> <no-match> <no-match> <no-match> <no-match>

            THIS IS FROM <no-match> <no-match> 
            AND CONTRIBUTORS
            IN NO EVENT SHALL <no-match> <no-match> OR ITS CONTRIBUTORS BE LIABLE 
            EVEN IF ADVISED OF THE <no-match> <no-match> <no-match> DAMAGE
        """.split()

        exp_itext = u"""
            Copyright <gap>
            THIS IS FROM <gap>
            AND CONTRIBUTORS
            IN NO EVENT SHALL <gap> OR ITS CONTRIBUTORS BE LIABLE 
            EVEN IF ADVISED OF THE <gap> DAMAGE
        """.split()
        qtext, itext = get_texts(match, query_string=querys, idx=idx)
        assert exp_qtext == qtext.split()
        assert exp_qtext == qtext.split()
        assert exp_itext == itext.split()
        assert 99 <= match.score()

    def test_match_chunk_are_correct_on_apache(self):
        rule_dir = self.get_test_loc('match_chunk/rules')
        idx = index.LicenseIndex(rules(rule_dir))

        query_loc = self.get_test_loc('match_chunk/query')
        matches = idx.match(location=query_loc)

        assert 1 == len(matches)
        qtext, _itext = get_texts(matches[0], location=query_loc, idx=idx)
        expected = u'''Redistribution and use in source and binary forms with or without modification are permitted provided that the following
conditions are met 1 Redistributions of source code must retain the above copyright notice this list of conditions and
the following disclaimer 2 Redistributions in binary form must reproduce the above copyright notice this list of
conditions and the following disclaimer in the documentation and or other materials provided with the distribution 3 The
end user documentation included with the redistribution if any must include the following acknowledgment <no-match> This
product includes software developed by the OpenSymphony Group http www opensymphony com <no-match> Alternately this
acknowledgment may appear in the software itself if and wherever such third party acknowledgments normally appear
<no-match> names <no-match> and The OpenSymphony <no-match> must not be used to endorse or promote products derived from
this software without prior written permission For written permission please contact license opensymphony com Products
derived from this software may not be called OpenSymphony or <no-match> nor may OpenSymphony or <no-match> appear in
their name without prior written permission of the OpenSymphony Group THIS SOFTWARE IS PROVIDED AS IS AND ANY EXPRESSED
OR IMPLIED WARRANTIES INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED IN NO EVENT SHALL THE APACHE SOFTWARE FOUNDATION OR ITS CONTRIBUTORS BE LIABLE FOR ANY
DIRECT INDIRECT INCIDENTAL SPECIAL EXEMPLARY OR CONSEQUENTIAL DAMAGES INCLUDING BUT NOT LIMITED TO PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES LOSS OF USE DATA OR PROFITS OR BUSINESS INTERRUPTION HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY WHETHER IN CONTRACT STRICT LIABILITY OR TORT INCLUDING NEGLIGENCE OR OTHERWISE ARISING IN ANY WAY OUT OF THE
USE OF THIS SOFTWARE EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE'''

        assert expected == qtext


def print_matched_texts(match, location=None, query_string=None, idx=None):
    """
    Convenience function to print matched texts for tracing and debugging tests.
    """
    qtext, itext = get_texts(match, location=location, query_string=query_string, idx=idx)
    print()
    print('Matched qtext:')
    print(qtext)
    print()
    print('Matched itext:')
    print(itext)
