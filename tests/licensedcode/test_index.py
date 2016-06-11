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
import json

from commoncode.testcase import FileBasedTesting

from licensedcode.whoosh_spans.spans import Span

from licensedcode import index
from licensedcode import models
from licensedcode.match import get_texts
from licensedcode.query import Query


TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


def print_matched_texts(match, location=None, query_string=None, idx=None):
    qtext, itext = get_texts(match, location=location, query_string=query_string, idx=idx)
    print()
    print('Matched qtext')
    print(qtext)
    print()
    print('Matched itext')
    print(itext)


class IndexTesting(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def get_test_rules(self, base, subset=None):
        base = self.get_test_loc(base)
        test_files = sorted(os.listdir(base))
        if subset:
            test_files = [t for t in test_files if t in subset]
        return [models.Rule(text_file=os.path.join(base, license_key), licenses=[license_key]) for license_key in test_files]


class TestIndexing(IndexTesting):

    def test_init_with_rules(self):
        test_rules = self.get_test_rules('index/bsd', ['bsd-new', 'bsd-no-mod'])
        idx = index.LicenseIndex(test_rules)
        expected_as_dict = json.load(open(self.get_test_loc('index/test_init_with_rules.json')))
        assert expected_as_dict == idx._as_dict()

    def test__add_rules(self):
        test_rules = self.get_test_rules('index/bsd', ['bsd-new', 'bsd-no-mod'])
        idx = index.LicenseIndex()
        idx._add_rules(test_rules)
        expected_as_dict = json.load(open(self.get_test_loc('index/test__add_rules.json')))
        assert expected_as_dict == idx._as_dict()

    def test__add_rules_with_templates(self):
        test_rules = self.get_test_rules('index/bsd_templates2')
        idx = index.LicenseIndex()
        idx._add_rules(test_rules)
        expected_as_dict = json.load(open(self.get_test_loc('index/test__add_rules_with_templates.json')))
        assert expected_as_dict == idx._as_dict()

    def test_index_structures(self):
        # rule text, unique low/high len, low/high len
        test_rules = [
            (u'a one a two a three licensed.', 4, 1, 6, 1),
            (u'a four a five a six licensed.', 4, 1, 6, 1),
            (u'one two three four five gpl', 5, 1, 5, 1),
            (u'The rose is a rose mit', 4, 1, 5, 1),
            (u'The license is GPL', 2, 2, 2, 2),
            (u'The license is a GPL', 3, 2, 3, 2),
            (u'a license is a rose', 3, 1, 4, 1),
            (u'the gpl', 1, 1, 1, 1),
            (u'the mit', 1, 1, 1, 1),
            (u'the bsd', 1, 1, 1, 1),
            (u'the lgpl', 1, 1, 1, 1),
        ]
        idx = index.LicenseIndex()
        rules = [models.Rule(_text=t[0]) for t in test_rules]
        idx._add_rules(rules)

        assert 10 == idx.len_junk

        for i, rule in enumerate(rules):
            lens = tuple(test_rules[i][1:])
            assert lens == (rule.low_unique, rule.high_unique, rule.low_length, rule.high_length)

        xdict = {
            u'a': 0,
            u'the': 1,
            u'is': 2,
            u'rose': 3,
            u'one': 4,
            u'two': 5,
            u'five': 6,
            u'four': 7,
            u'three': 8,
            u'six': 9,
            u'gpl': 10,
            u'license': 11,
            u'mit': 12,
            u'licensed': 13,
            u'bsd': 14,
            u'lgpl': 15,
        }
        assert xdict == idx.dictionary

        xtbi = [
            u'a',
            u'the',
            u'is',
            u'rose',
            u'one',
            u'two',
            u'five',
            u'four',
            u'three',
            u'six',
            u'gpl',
            u'license',
            u'mit',
            u'licensed',
            u'bsd',
            u'lgpl'
        ]
        assert xtbi == idx.tokens_by_tid

        expected_as_dict = {
            '_tst__0': {u'a': [0, 2, 4],
                        u'licensed': [6],
                        u'one': [1],
                        u'three': [5],
                        u'two': [3]},
            '_tst__1': {u'a': [0, 2, 4],
                        u'five': [3],
                        u'four': [1],
                        u'licensed': [6],
                        u'six': [5]},
            '_tst__2': {u'five': [4],
                        u'four': [3],
                        u'gpl': [5],
                        u'one': [0],
                        u'three': [2],
                        u'two': [1]},
            '_tst__3': {u'a': [3], u'is': [2], u'mit': [5], u'rose': [1, 4], u'the': [0]},
            '_tst__4': {u'gpl': [3], u'is': [2], u'license': [1], u'the': [0]},
            '_tst__5': {u'a': [3], u'gpl': [4], u'is': [2], u'license': [1], u'the': [0]},
            '_tst__6': {u'a': [0, 3], u'is': [2], u'license': [1], u'rose': [4]},
            '_tst__7': {u'gpl': [1], u'the': [0]},
            '_tst__8': {u'mit': [1], u'the': [0]},
            '_tst__9': {u'bsd': [1], u'the': [0]},
            '_tst__10': {u'lgpl': [1], u'the': [0]},
        }
        assert expected_as_dict == idx._as_dict()

    def test_index_structures_with__add_rules(self):
        base = self.get_test_loc('index/tokens_count')
        keys = sorted(os.listdir(base))
        idx = index.LicenseIndex()
        rules = []
        for key in keys:
            rules.append(models.Rule(text_file=os.path.join(base, key)))

        idx._add_rules(rules)

        assert 3 == idx.len_junk

        expected_index = {
                'plain1_0': {u'redistribution': [0]},
                'plain2_1': {u'is': [1], u'redistribution': [0], u'yes': [2]},
                'plain3_2': {u'allowed': [2],
                             u'is': [1], u'redistribution': [0], u'yes': [3]},
                'plain4_3': {u'allowed': [2],
                             u'for': [3], u'is': [1], u'redistribution': [0],
                             u'yes': [4]},
                'plain5_4': {u'all': [4],
                             u'allowed': [2], u'for': [3], u'is': [1],
                             u'redistribution': [0]},
                'tmpl10_5': {u'all': [4, 6],
                             u'allowed': [2], u'and': [5, 7], u'any': [8],
                             u'for': [3], u'is': [1], u'redistribution': [0],
                             u'thing': [9]},
                'tmpl2_6': {u'is': [1], u'redistribution': [0]},
                'tmpl3_7': {u'allowed': [2], u'is': [1], u'redistribution': [0]},
                'tmpl4_8': {u'allowed': [2], u'for': [3], u'is': [1], u'redistribution': [0]},
                'tmpl5_2_10': {u'all': [4],
                               u'allowed': [2], u'for': [3], u'is': [1],
                               u'redistribution': [0], u'yes': [5]},
                'tmpl5_9': {u'allowed': [3],
                            u'for': [4], u'is': [1, 2], u'redistribution': [0]},
                'tmpl6_11': {u'all': [4],
                             u'allowed': [2], u'and': [5], u'for': [3], u'is':
                             [1], u'redistribution': [0]},
                'tmpl7_12': {u'all': [4, 6],
                             u'allowed': [2], u'and': [5], u'for': [3], u'is':
                             [1], u'redistribution': [0]},
                'tmpl8_13': {u'all': [4, 6],
                             u'allowed': [2], u'and': [5, 7], u'for': [3],
                             u'is': [1], u'redistribution': [0]},
                'tmpl9_14': {u'all': [4, 6],
                             u'allowed': [2], u'and': [5, 7], u'any': [8],
                             u'for': [3], u'is': [1], u'redistribution': [0]}
            }

        assert expected_index == idx._as_dict()

        expected_dict = {
            u'all': 5,
            u'allowed': 4,
            u'and': 2,
            u'any': 7,
            u'for': 1,
            u'is': 0,
            u'redistribution': 3,
            u'thing': 8,
            u'yes': 6
        }
        assert expected_dict == idx.dictionary

        expected_tids = [u'is', u'for', u'and', u'redistribution', u'allowed', u'all', u'yes', u'any', u'thing']
        assert expected_tids == idx.tokens_by_tid

        expected_high_tids_msets_by_rid = [
            {u'redistribution': 1},
            {u'redistribution': 1, u'yes': 1},
            {u'allowed': 1, u'redistribution': 1, u'yes': 1},
            {u'allowed': 1, u'redistribution': 1, u'yes': 1},
            {u'all': 1, u'allowed': 1, u'redistribution': 1},
            {u'all': 2, u'allowed': 1, u'any': 1, u'redistribution': 1, u'thing': 1},
            {u'redistribution': 1},
            {u'allowed': 1, u'redistribution': 1},
            {u'allowed': 1, u'redistribution': 1},
            {u'allowed': 1, u'redistribution': 1},
            {u'all': 1, u'allowed': 1, u'redistribution': 1, u'yes': 1},
            {u'all': 1, u'allowed': 1, u'redistribution': 1},
            {u'all': 2, u'allowed': 1, u'redistribution': 1},
            {u'all': 2, u'allowed': 1, u'redistribution': 1},
            {u'all': 2, u'allowed': 1, u'any': 1, u'redistribution': 1}]

        low_tids_msets_by_rid, high_tids_msets_by_rid = zip(*idx.tids_msets_by_rid)

        assert expected_high_tids_msets_by_rid == [{idx.tokens_by_tid[tok]: freq for tok, freq in tids_mset.items()}
                                                   for tids_mset in high_tids_msets_by_rid]

        expected_low_tids_msets_by_rid = [
            {},
            {u'is': 1},
            {u'is': 1},
            {u'for': 1, u'is': 1},
            {u'for': 1, u'is': 1},
            {u'and': 2, u'for': 1, u'is': 1},
            {u'is': 1},
            {u'is': 1},
            {u'for': 1, u'is': 1},
            {u'for': 1, u'is': 2},
            {u'for': 1, u'is': 1},
            {u'and': 1, u'for': 1, u'is': 1},
            {u'and': 1, u'for': 1, u'is': 1},
            {u'and': 2, u'for': 1, u'is': 1},
            {u'and': 2, u'for': 1, u'is': 1}]
        assert expected_low_tids_msets_by_rid == [{idx.tokens_by_tid[tok]: freq for tok, freq in tids_mset.items()}
                                                  for tids_mset in low_tids_msets_by_rid]

    def test_index_fails_on_duplicated_rules(self):
        rule_dir = self.get_test_loc('index/no_duplicated_rule')
        try:
            index.LicenseIndex(models._rules_proper(rule_dir))
            self.fail('Exception on dupes not raised')
        except AssertionError, e:
            assert u'Duplicate rules' in e.message


class TestMatchNoTemplates(IndexTesting):
    test_data_dir = TEST_DATA_DIR

    def test_match_exact_from_string_once(self):
        rule_text = 'Redistribution and use in source and binary forms, with or without modification, are permitted'
        idx = index.LicenseIndex([models.Rule(_text=rule_text, licenses=['bsd'])])
        querys = '''
            The
            Redistribution and use in source and binary forms, with or without modification, are permitted.
            
            Always'''

        result = idx.match(query_string=querys)
        assert 1 == len(result)
        match = result[0]
        qtext, itext = get_texts(match, query_string=querys, idx=idx)
        assert 'Redistribution and use in source and binary forms with or without modification are permitted' == qtext
        assert 'Redistribution and use in source and binary forms with or without modification are permitted' == itext

        assert Span(0, 13) == match.qspan
        assert Span(0, 13) == match.ispan

    def test_match_exact_from_string_twice_with_repeated_text(self):
        rule = models.Rule()
        rule._text = u'licensed under the GPL, licensed under the GPL'
        #                     0    1   2   3         4      5   6   7
        rule.licenses = ['tst']

        idx = index.LicenseIndex([rule])
        querys = u'Hi licensed under the GPL, licensed under the GPL yes.'
        #          0        1   2   3     4       5     6    7   8   9

        result = idx.match(query_string=querys)
        assert 1 == len(result)
        match = result[0]
        qtext, itext = get_texts(match, query_string=querys, idx=idx)
        assert 'licensed under the GPL licensed under the GPL' == qtext
        assert 'licensed under the GPL licensed under the GPL' == itext

        assert Span(0, 7) == match.qspan
        assert Span(0, 7) == match.ispan

        # match again to ensure that there are no state side effects
        result = idx.match(query_string=querys)
        assert 1 == len(result)
        match = result[0]
        assert Span(0, 7) == match.qspan
        assert Span(0, 7) == match.ispan

        qtext, itext = get_texts(match, query_string=querys, idx=idx)
        assert u'licensed under the GPL licensed under the GPL' == qtext
        assert u'licensed under the GPL licensed under the GPL' == itext

    def test_match_exact_with_junk_in_between_good_tokens(self):
        rule = models.Rule()
        rule._text = u'licensed under the GPL, licensed under the GPL'
        rule.licenses = ['tst']

        idx = index.LicenseIndex([rule])
        querys = u'Hi licensed that under is the that GPL, licensed or under not the GPL by yes.'

        result = idx.match(query_string=querys)
        assert 1 == len(result)
        match = result[0]
        qtext, itext = get_texts(match, query_string=querys, idx=idx)
        assert u'licensed <no-match> under <no-match> the <no-match> GPL licensed <no-match> under <no-match> the GPL' == qtext
        assert u'licensed under the GPL licensed under the GPL' == itext

    def test_match_exact_from_file(self):
        idx = index.LicenseIndex(self.get_test_rules('index/mini'))
        query_loc = self.get_test_loc('index/queryperfect-mini')

        result = idx.match(location=query_loc)
        assert 1 == len(result)
        match = result[0]

        qtext, itext = get_texts(match, location=query_loc, idx=idx)
        assert 'Redistribution and use in source and binary forms with or without modification are permitted' == qtext
        assert 'Redistribution and use in source and binary forms with or without modification are permitted' == itext

        assert Span(0, 13) == match.qspan
        assert Span(0, 13) == match.ispan

    def test_match_multiple(self):
        test_rules = self.get_test_rules('index/bsd')
        idx = index.LicenseIndex(test_rules)
        query = self.get_test_loc('index/querysimple')

        result = idx.match(location=query)
        assert 1 == len(result)
        match = result[0]
        assert Span(0, 212) == match.qspan
        assert Span(0, 212) == match.ispan

    def test_match_return_correct_offsets(self):
        rule = models.Rule(licenses=['test'])
        rule._text = u'A GPL. A MIT. A LGPL.'
        #              0   1  2   3  4    5
        idx = index.LicenseIndex([rule])
        querys = u'some junk. A GPL. A MIT. A LGPL.'
        #             0    1  2   3  4   5  6    7

        result = idx.match(query_string=querys)
        assert 1 == len(result)
        match = result[0]
        qtext, itext = get_texts(match, query_string=querys, idx=idx)
        assert 'A GPL A MIT A LGPL' == qtext
        assert 'A GPL A MIT A LGPL' == itext

        assert Span(0, 5) == match.qspan
        assert Span(0, 5) == match.ispan


class TestMatchWithTemplates(IndexTesting):
    test_data_dir = TEST_DATA_DIR

    def test_match_with_template_and_multiple_rules(self):
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
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


Goodbye
No part of match        '''
        result = idx.match(query_string=querys)

        assert 1 == len(result)
        match = result[0]
        assert 'chunk' == match._type

        exp_qtext = u"""
            Redistribution and use in source and binary forms with or without
            modification are permitted provided that the following conditions
            are met
            
            Redistributions of source code must retain the above copyright
            notice this list of conditions and the following disclaimer

            Redistributions in binary form must reproduce the above copyright
            notice this list of conditions and the following disclaimer in the
            documentation and or other materials provided with the distribution
            
            Neither the name of <no-match> <no-match> nor the names of its
            contributors may be used to endorse or promote products derived from
            this software without specific prior written permission
            
            THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
            AS IS AND ANY EXPRESS OR IMPLIED WARRANTIES INCLUDING BUT NOT
            LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
            A PARTICULAR PURPOSE ARE DISCLAIMED IN NO EVENT SHALL THE COPYRIGHT
            OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT INDIRECT INCIDENTAL
            SPECIAL EXEMPLARY OR CONSEQUENTIAL DAMAGES INCLUDING BUT NOT LIMITED
            TO PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES LOSS OF USE DATA OR
            PROFITS OR BUSINESS INTERRUPTION HOWEVER CAUSED AND ON ANY THEORY OF
            LIABILITY WHETHER IN CONTRACT STRICT LIABILITY OR TORT INCLUDING
            NEGLIGENCE OR OTHERWISE ARISING IN ANY WAY OUT OF THE USE OF THIS
            SOFTWARE EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE
        """.split()

        exp_itext = u"""
            Redistribution and use in source and binary forms with or without
            modification are permitted provided that the following conditions
            are met
            
            Redistributions of source code must retain the above copyright
            notice this list of conditions and the following disclaimer
            
            Redistributions in binary form must reproduce the above copyright
            notice this list of conditions and the following disclaimer in the
            documentation and or other materials provided with the distribution
            
            Neither the name of <gap> nor the names of its contributors may be
            used to endorse or promote products derived from this software
            without specific prior written permission
            
            THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
            AS IS AND ANY EXPRESS OR IMPLIED WARRANTIES INCLUDING BUT NOT
            LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
            A PARTICULAR PURPOSE ARE DISCLAIMED IN NO EVENT SHALL THE COPYRIGHT
            OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT INDIRECT INCIDENTAL
            SPECIAL EXEMPLARY OR CONSEQUENTIAL DAMAGES INCLUDING BUT NOT LIMITED
            TO PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES LOSS OF USE DATA OR
            PROFITS OR BUSINESS INTERRUPTION HOWEVER CAUSED AND ON ANY THEORY OF
            LIABILITY WHETHER IN CONTRACT STRICT LIABILITY OR TORT INCLUDING
            NEGLIGENCE OR OTHERWISE ARISING IN ANY WAY OUT OF THE USE OF THIS
            SOFTWARE EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE
        """.split()
#         q = Query(query_string=querys, idx=idx)

#         print('######################')
#         print('######################')
#         print('q=', querys.lower().replace('*', ' ').replace('/', ' '). split())
#         print('q2=', [None if t is None else idx.tokens_by_tid[t] for t in q.tokens_with_unknowns()])
#         print('######################')


        qtext, itext = get_texts(match, query_string=querys, idx=idx)
        assert exp_qtext == qtext.split()
        assert exp_itext == itext.split()

        assert Span(Span(1, 72) | Span(74, 212)) == match.qspan

        assert Span(0, 210) == match.ispan
        assert 100 == match.score()

    def test_match_to_indexed_template_with_few_tokens_around_gaps(self):
        # Was failing when a gap in a template starts very close to the start of
        # a rule tokens seq. We may still skip that, but we capture a large
        # match anyway.

        rule = models.Rule(text_file=self.get_test_loc('index/templates/idx.txt'), licenses=['test'],)
        idx = index.LicenseIndex([rule])

        query_loc = self.get_test_loc('index/templates/query.txt')
        result = idx.match(location=query_loc)
        assert 1 == len(result)
        match = result[0]

        exp_qtext = u"""
            Copyright <no-match> <no-match> <no-match> <no-match> <no-match> <no-match> <no-match> 
            All Rights Reserved
            
            Redistribution and use of this software and associated documentation
            Software with or without modification are permitted provided that
            the following conditions are met
            
            1 Redistributions of source code must retain copyright statements
            and notices Redistributions must also contain a copy of this
            document
            
            2 Redistributions in binary form must reproduce the above copyright
            notice this list of conditions and the following disclaimer in the
            documentation and or other materials provided with the distribution
            
            3 The name <no-match> must not be used to endorse or promote
            products derived from this Software without prior written permission
            of <no-match> <no-match> For written permission please contact 
            <no-match> <no-match> <no-match>
            
            4 Products derived from this Software may not be called <no-match>
            nor may <no-match> appear in their names without prior written
            permission of <no-match> <no-match> <no-match> is a registered
            trademark of <no-match> <no-match>
            
            5 Due credit should be given to <no-match> <no-match> <no-match>
            <no-match> <no-match> <no-match>
            
            THIS SOFTWARE IS PROVIDED BY <no-match> <no-match> AND CONTRIBUTORS
            AS IS AND ANY EXPRESSED OR IMPLIED WARRANTIES INCLUDING BUT NOT
            LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
            A PARTICULAR PURPOSE ARE DISCLAIMED IN NO EVENT SHALL <no-match>
            <no-match> OR ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT INDIRECT
            INCIDENTAL SPECIAL EXEMPLARY OR CONSEQUENTIAL DAMAGES INCLUDING BUT
            NOT LIMITED TO PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES LOSS OF
            USE DATA OR PROFITS OR BUSINESS INTERRUPTION HOWEVER CAUSED AND ON
            ANY THEORY OF LIABILITY WHETHER IN CONTRACT STRICT LIABILITY OR TORT
            INCLUDING NEGLIGENCE OR OTHERWISE ARISING IN ANY WAY OUT OF THE USE
            OF THIS SOFTWARE EVEN IF ADVISED OF THE <no-match> <no-match> 
            <no-match> DAMAGE
        """.split()

        exp_itext = u"""
            Copyright <gap>
            All Rights Reserved 
            
            Redistribution and use of this software and associated documentation
            Software with or without modification are permitted provided that
            the following conditions are met
            
            1 Redistributions of source code must retain copyright statements
            and notices Redistributions must also contain a copy of this
            document
            
            2 Redistributions in binary form must reproduce the above copyright
            notice this list of conditions and the following disclaimer in the
            documentation and or other materials provided with the distribution
            
            3 The name <gap> must not be used to endorse or promote products
            derived from this Software without prior written permission of <gap>
            For written permission please contact <gap>
            
            4 Products derived from this Software may not be called <gap> nor
            may <gap> appear in their names without prior written permission of
            <gap> is a registered trademark of <gap>
            
            5 Due credit should be given to <gap>
            
            THIS SOFTWARE IS PROVIDED BY <gap> AND CONTRIBUTORS AS IS AND ANY
            EXPRESSED OR IMPLIED WARRANTIES INCLUDING BUT NOT LIMITED TO THE
            IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
            PURPOSE ARE DISCLAIMED IN NO EVENT SHALL <gap> OR ITS CONTRIBUTORS
            BE LIABLE FOR ANY DIRECT INDIRECT INCIDENTAL SPECIAL EXEMPLARY OR
            CONSEQUENTIAL DAMAGES INCLUDING BUT NOT LIMITED TO PROCUREMENT OF
            SUBSTITUTE GOODS OR SERVICES LOSS OF USE DATA OR PROFITS OR BUSINESS
            INTERRUPTION HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY WHETHER
            IN CONTRACT STRICT LIABILITY OR TORT INCLUDING NEGLIGENCE OR
            OTHERWISE ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE EVEN IF
            ADVISED OF THE <gap> DAMAGE
        """.split()
        qtext, itext = get_texts(match, location=query_loc, idx=idx)
        assert exp_qtext == qtext.split()
        assert exp_itext == itext.split()
        assert 100 == match.score()
        assert 'chunk' == match._type

    def test_match_with_templates_with_redundant_tokens_yield_single_exact_match(self):
        rule = models.Rule()
        rule._text = u'copyright reserved mit is license, {{}} copyright reserved mit is license'
        #                      0        1  2   3       4               5        6   7  8       9
        rule.licenses = ['tst']
        idx = index.LicenseIndex([rule], ngram_length=2)
        expected_idx = {
            '_tst__0': {
                u'copyright': [0, 5],
                u'is': [3, 8],
                u'license': [4, 9],
                u'mit': [2, 7],
                u'reserved': [1, 6]
                }
        }

        assert expected_idx == idx._as_dict()

        querys = u'Hi my copyright reserved mit is license is the copyright reserved mit is license yes.'
        #           0  1         2        3   4  5       6  7   8         9       10  11 12      13  14
        qry = Query(query_string=querys, idx=idx)

        # convert tid to actual token strings
        tks_as_str = lambda tks: [None if tid is None else idx.tokens_by_tid[tid] for tid in tks]

        expected = [None, None, u'copyright', u'reserved', u'mit', u'is', u'license', u'is', None, u'copyright', u'reserved', u'mit', u'is', u'license', None]
        #              0     1            2            3       4      5           6      7      8            9           10      11     12          13     14
        assert expected == tks_as_str(qry.tokens_with_unknowns())

        result = idx.match(query_string=querys)
        assert 1 == len(result)

        match = result[0]
        assert Span(0, 4) | Span(6, 10) == match.qspan
        assert Span(0, 9) == match.ispan
        assert 100 == match.score()
        qtext, itext = get_texts(match, query_string=querys, idx=idx)
        assert 'copyright reserved mit is license <no-match> <no-match> copyright reserved mit is license' == qtext
        assert 'copyright reserved mit is license <gap> copyright reserved mit is license' == itext
