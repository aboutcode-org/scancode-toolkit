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

import io
import os
import json

from commoncode.testcase import FileBasedTesting

from licensedcode.spans import Span

from licensedcode import index
from licensedcode import match_seq
from licensedcode import models
from licensedcode.query import Query
from licensedcode.tracing import get_texts

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


class IndexTesting(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def get_test_rules(self, base, subset=None):
        base = self.get_test_loc(base)
        test_files = sorted(os.listdir(base))
        if subset:
            test_files = [t for t in test_files if t in subset]
        return [models.Rule(text_file=os.path.join(base, license_key), license_expression=license_key) for license_key in test_files]


class TestIndexing(IndexTesting):

    def check_index_as_dict(self, idx, expected, regen=False):
        as_dict = idx.to_dict()
        expected = self.get_test_loc(expected)
        if regen:
            with open(expected, 'wb') as jx:
                jx.write(json.dumps(as_dict, indent=2, separators=(',', ': ')))

        with io.open(expected, encoding='utf-8') as exp:
            expected_as_dict = json.load(exp)
        assert expected_as_dict == as_dict

    def test_init_with_rules(self):
        test_rules = self.get_test_rules('index/bsd', ['bsd-new', 'bsd-no-mod'])
        idx = index.LicenseIndex(test_rules)
        self.check_index_as_dict(idx, 'index/test_init_with_rules.json')

    def test__add_rules(self):
        test_rules = self.get_test_rules('index/bsd', ['bsd-new', 'bsd-no-mod'])
        idx = index.LicenseIndex()
        idx._add_rules(test_rules)
        self.check_index_as_dict(idx, 'index/test__add_rules.json')

    def test__add_rules_with_templates(self):
        test_rules = self.get_test_rules('index/bsd_templates2')
        idx = index.LicenseIndex()
        idx._add_rules(test_rules)
        self.check_index_as_dict(idx, 'index/test__add_rules_with_templates.json')

    def test_index_structures(self):
        # rule text, unique low/high len, low/high len
        test_rules = [
            (u'a one a two a three licensed.', (4, 1, 4, 1)),
            (u'a four a five a six licensed.', (4, 1, 4, 1)),
            (u'one two three four five gpl', (6, 1, 6, 1)),
            (u'The rose is a rose mit', (4, 0, 5, 0)),
            (u'The license is GPL', (4, 2, 4, 2)),
            (u'The license is this GPL', (5, 2, 5, 2)),
            (u'a license is a rose', (3, 1, 3, 1)),
            (u'the gpl', (2, 1, 2, 1)),
            (u'the mit', (2, 0, 2, 0)),
            (u'the bsd', (2, 1, 2, 1)),
            (u'the lgpl', (2, 1, 2, 1)),
        ]
        idx = index.LicenseIndex()
        rules = [models.Rule(stored_text=t[0]) for t in test_rules]
        idx._add_rules(rules)

        assert 11 == idx.len_junk
        expected_lengths = [r[1] for r in test_rules]
        results = [
            (rule.length_unique, rule.high_length_unique,
             rule.length, rule.high_length) for rule in rules]
        assert expected_lengths == results

        xdict = {
            'bsd': 15,
            'five': 5,
            'four': 4,
            'gpl': 11,
            'is': 1,
            'lgpl': 14,
            'license': 12,
            'licensed': 13,
            'mit': 8,
            'one': 7,
            'rose': 2,
            'six': 10,
            'the': 0,
            'this': 9,
            'three': 3,
            'two': 6
        }

        assert xdict == idx.dictionary

        xtbi = [
            u'the',
            u'is',
            u'rose',
            u'three',
            u'four',
            u'five',
            u'two',
            u'one',
            u'mit',
            u'this',
            u'six',
            u'gpl',
            u'license',
            u'licensed',
            u'lgpl',
            u'bsd']

        assert xtbi == idx.tokens_by_tid

        expected_as_dict = {
            u'_tst_29_0': {u'licensed': [3]},
            u'_tst_29_1': {u'licensed': [3]},
            u'_tst_27_2': {u'gpl': [5]},
            u'_tst_22_3': {},
            u'_tst_18_4': {u'gpl': [3], u'license': [1]},
            u'_tst_23_5': {u'gpl': [4], u'license': [1]},
            u'_tst_19_6': {u'license': [0]},
            u'_tst_7_7': {u'gpl': [1]},
            u'_tst_7_8': {},
            u'_tst_7_9': {u'bsd': [1]},
            u'_tst_8_10': {u'lgpl': [1]}
        }

        assert expected_as_dict == idx.to_dict()

    def test_index_structures_with__add_rules(self):
        base = self.get_test_loc('index/tokens_count')
        keys = sorted(os.listdir(base))
        idx = index.LicenseIndex()
        rules = []
        for key in keys:
            rules.append(models.Rule(
                text_file=os.path.join(base, key), license_expression='gpl-2.0'))

        idx._add_rules(rules)

        assert 6 == idx.len_junk

        expected_index = {
        'plain1_0': {u'redistribution': [0]},
        'plain2_1': {u'redistribution': [0], u'yes': [2]},
        'plain3_2': {u'redistribution': [0], u'yes': [3]},
        'plain4_3': {u'redistribution': [0], u'yes': [4]},
        'plain5_4': {u'redistribution': [0]},
        'tmpl10_5': {u'redistribution': [0], u'thing': [6]},
        'tmpl2_6': {u'redistribution': [0]},
        'tmpl3_7': {u'redistribution': [0]},
        'tmpl4_8': {u'redistribution': [0]},
        'tmpl5_2_9': {u'redistribution': [0], u'yes': [4]},
        'tmpl6_10': {u'redistribution': [0]},
        'tmpl7_11': {u'redistribution': [0]},
        'tmpl9_12': {u'redistribution': [0]}
        }

        assert expected_index == idx.to_dict()

        expected_dict = {
            'is': 0,
            'allowed': 1,
            'all': 2,
            'and': 3,
            'any': 5,
            'for': 4,
            'redistribution': 6,
            'thing': 8,
            'yes': 7}

        assert expected_dict == idx.dictionary

        expected_tids = [
            'is',
            'allowed',
            'all',
            'and',
            'for',
            'any',
            'redistribution',
            'yes',
            'thing']
        assert expected_tids == idx.tokens_by_tid

        expected_msets_by_rid = [
            {u'redistribution': 1},
            {u'is': 1, u'redistribution': 1, u'yes': 1},
            {u'allowed': 1, u'is': 1, u'redistribution': 1, u'yes': 1},
            {u'allowed': 1, u'for': 1, u'is': 1, u'redistribution': 1, u'yes': 1},
            {u'all': 1, u'allowed': 1, u'for': 1, u'is': 1, u'redistribution': 1},
            {u'all': 1,
             u'allowed': 1,
             u'and': 1,
             u'any': 1,
             u'is': 1,
             u'redistribution': 1,
             u'thing': 1},
            {u'is': 1, u'redistribution': 1},
            {u'allowed': 1, u'is': 1, u'redistribution': 1},
            {u'allowed': 1, u'for': 1, u'is': 1, u'redistribution': 1},
            {u'all': 1, u'allowed': 1, u'is': 1, u'redistribution': 1, u'yes': 1},
            {u'all': 1, u'allowed': 1, u'and': 1, u'is': 1, u'redistribution': 1},
            {u'all': 1, u'allowed': 1, u'is': 1, u'redistribution': 1},
            {u'all': 1,
             u'allowed': 1,
             u'and': 1,
             u'any': 1,
             u'is': 1,
             u'redistribution': 1}
            ]

        htmset = [{idx.tokens_by_tid[tok]: freq for (tok, freq) in tids_mset.items()}
                  for tids_mset in idx.msets_by_rid]
        assert expected_msets_by_rid == htmset

    def test_index_fails_on_duplicated_rules(self):
        rule_dir = self.get_test_loc('index/no_duplicated_rule')
        try:
            index.LicenseIndex(models.load_rules(rule_dir))
            self.fail('Exception on dupes not raised')
        except AssertionError as e:
            assert u'Duplicate rules' in str(e)


class TestMatchNoTemplates(IndexTesting):
    test_data_dir = TEST_DATA_DIR

    def test_match_exact_from_string_once(self):
        rule_text = 'Redistribution and use in source and binary forms, with or without modification, are permitted'
        idx = index.LicenseIndex([models.Rule(stored_text=rule_text, license_expression='bsd')])
        querys = '''
            The
            Redistribution and use in source and binary forms, with or without modification, are permitted.

            Always'''

        result = idx.match(query_string=querys)
        assert 1 == len(result)
        match = result[0]
        qtext, itext = get_texts(match)
        assert 'Redistribution and use in source and binary forms, with or without modification,\nare permitted.' == qtext
        assert 'redistribution and use in source and binary forms with or without modification\nare permitted' == itext

        assert Span(0, 13) == match.qspan
        assert Span(0, 13) == match.ispan

    def test_match_exact_from_string_twice_with_repeated_text(self):
        _stored_text = u'licensed under the GPL, licensed under the GPL'
        #                0    1   2   3         4      5   6   7
        license_expression = 'tst'
        rule = models.Rule(license_expression=license_expression, stored_text=_stored_text)

        idx = index.LicenseIndex([rule])
        querys = u'Hi licensed under the GPL, licensed under the GPL yes.'
        #          0        1   2   3     4       5     6    7   8   9

        result = idx.match(query_string=querys)
        assert 1 == len(result)
        match = result[0]
        qtext, itext = get_texts(match)
        assert 'licensed under the GPL, licensed under the GPL' == qtext
        assert 'licensed under the gpl licensed under the gpl' == itext

        assert Span(0, 7) == match.qspan
        assert Span(0, 7) == match.ispan

        # match again to ensure that there are no state side effects
        result = idx.match(query_string=querys)
        assert 1 == len(result)
        match = result[0]
        assert Span(0, 7) == match.qspan
        assert Span(0, 7) == match.ispan

        qtext, itext = get_texts(match)
        assert u'licensed under the GPL, licensed under the GPL' == qtext
        assert u'licensed under the gpl licensed under the gpl' == itext

    def test_match_exact_with_junk_in_between_good_tokens(self):
        _stored_text = u'licensed under the GPL, licensed under the GPL'
        license_expression = 'tst'
        rule = models.Rule(license_expression=license_expression, stored_text=_stored_text)

        idx = index.LicenseIndex([rule])
        querys = u'Hi licensed that under is the that GPL, licensed or under not the GPL by yes.'

        result = idx.match(query_string=querys)
        assert 1 == len(result)
        match = result[0]
        qtext, itext = get_texts(match)
        assert u'licensed [that] under [is] the [that] GPL, licensed [or] under [not] the GPL' == qtext
        assert u'licensed under the gpl licensed under the gpl' == itext

    def test_match_exact_from_file(self):
        idx = index.LicenseIndex(self.get_test_rules('index/mini'))
        query_loc = self.get_test_loc('index/queryperfect-mini')

        result = idx.match(location=query_loc)
        assert 1 == len(result)
        match = result[0]

        qtext, itext = get_texts(match)
        assert 'Redistribution and use in source and binary forms, with or without modification,\nare permitted.' == qtext
        assert 'redistribution and use in source and binary forms with or without modification\nare permitted' == itext

        assert Span(0, 13) == match.qspan
        assert Span(0, 13) == match.ispan

    def test_match_multiple(self):
        test_rules = self.get_test_rules('index/bsd')
        idx = index.LicenseIndex(test_rules)
        query = self.get_test_loc('index/querysimple')

        result = idx.match(location=query)
        assert 1 == len(result)
        match = result[0]
        assert Span(0, 211) == match.qspan
        assert Span(0, 211) == match.ispan

    def test_match_return_correct_offsets(self):
        # notes: A is a stopword. This and that are not
        _stored_text = u'This GPL. A MIT. That LGPL.'
        #                0    1    2 3    4    5

        license_expression = 'tst'
        rule = models.Rule(license_expression=license_expression, stored_text=_stored_text)
        idx = index.LicenseIndex([rule])
        querys = u'some junk. this GPL. A MIT. that LGPL.'
        #          0    1     2    3    4 5    6    7

        result = idx.match(query_string=querys)
        assert 1 == len(result)
        match = result[0]
        qtext, itext = get_texts(match)
        assert 'this GPL. A MIT. that LGPL.' == qtext
        assert 'this gpl mit that lgpl' == itext

        assert Span(0, 4) == match.qspan
        assert Span(0, 4) == match.ispan


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
        assert match_seq.MATCH_SEQ == match.matcher

        exp_qtext = u"""
            Redistribution and use in source and binary forms, with or without modification,
            are permitted provided that the following conditions are met:

                * Redistributions of source code must retain the above copyright notice,
                this list of conditions and the following disclaimer.

                * Redistributions in binary form must reproduce the above copyright notice,
                this list of conditions and the following disclaimer in the documentation
                and/or other materials provided with the distribution.

                * Neither the name of [nexB] [Inc]. nor the names of its contributors may be
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

            Neither the name of nor the names of its contributors may be
            used to endorse or promote products derived from this software
            without specific prior written permission

            THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
            AS IS AND ANY EXPRESS OR IMPLIED WARRANTIES INCLUDING BUT NOT
            LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
            PARTICULAR PURPOSE ARE DISCLAIMED IN NO EVENT SHALL THE COPYRIGHT
            OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT INDIRECT INCIDENTAL
            SPECIAL EXEMPLARY OR CONSEQUENTIAL DAMAGES INCLUDING BUT NOT LIMITED
            TO PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES LOSS OF USE DATA OR
            PROFITS OR BUSINESS INTERRUPTION HOWEVER CAUSED AND ON ANY THEORY OF
            LIABILITY WHETHER IN CONTRACT STRICT LIABILITY OR TORT INCLUDING
            NEGLIGENCE OR OTHERWISE ARISING IN ANY WAY OUT OF THE USE OF THIS
            SOFTWARE EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE
        """.lower().split()

        qtext, itext = get_texts(match)
        assert exp_qtext == qtext.split()
        assert exp_itext == itext.split()

        assert (Span(1, 72) | Span(74, 211)) == match.qspan

        assert Span(0, 209) == match.ispan
        assert 100 == match.coverage()

    def test_match_to_indexed_template_with_few_tokens_around_gaps(self):
        # Was failing when a gap in a template starts very close to the start of
        # a rule tokens seq. We may still skip that, but we capture a large
        # match anyway.

        rule = models.Rule(text_file=self.get_test_loc('index/templates/idx.txt'),
                           license_expression='test')
        idx = index.LicenseIndex([rule])

        query_loc = self.get_test_loc('index/templates/query.txt')
        result = idx.match(location=query_loc)
        assert 1 == len(result)
        match = result[0]

        exp_qtext = u"""
            All Rights Reserved.

             Redistribution and use of this software and associated documentation
             ("Software"), with or without modification, are permitted provided
             that the following conditions are met:

             1. Redistributions of source code must retain copyright
                statements and notices.  Redistributions must also contain a
                copy of this document.

             2. Redistributions in binary form must reproduce the
                above copyright notice, this list of conditions and the
                following disclaimer in the documentation and/or other
                materials provided with the distribution.

             3. The name "[groovy]" must not be used to endorse or promote
                products derived from this Software without prior written
                permission of [The] [Codehaus].  For written permission,
                please contact [info]@[codehaus].[org].

             4. Products derived from this Software may not be called "[groovy]"
                nor may "[groovy]" appear in their names without prior written
                permission of [The] [Codehaus]. "[groovy]" is a registered
                trademark of [The] [Codehaus].

             5. Due credit should be given to [The] [Codehaus] -
                [http]://[groovy].[codehaus].[org]/

             [THIS] [SOFTWARE] [IS] [PROVIDED] [BY] [THE] [CODEHAUS] AND CONTRIBUTORS
             ``AS IS'' AND ANY EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT
             NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
             FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL
             [THE] [CODEHAUS] OR ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
             INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
             (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
             SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
             HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
             STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
             ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
             OF THE [POSSIBILITY] [OF] [SUCH] DAMAGE.
        """.split()

        exp_itext = u"""
            All Rights Reserved

            Redistribution and use of this software and associated documentation
            Software with or without modification are permitted provided that
            the following conditions are met

            1 Redistributions of source code must retain copyright statements
            and notices Redistributions must also contain copy of this
            document

            2 Redistributions in binary form must reproduce the above copyright
            notice this list of conditions and the following disclaimer in the
            documentation and or other materials provided with the distribution

            3 The name must not be used to endorse or promote products
            derived from this Software without prior written permission of
            For written permission please contact

            4 Products derived from this Software may not be called nor
            may appear in their names without prior written permission of
            is registered trademark of

            5 Due credit should be given to

            <THIS> <SOFTWARE> <IS> <PROVIDED> <BY>
            AND CONTRIBUTORS AS IS AND ANY
            EXPRESSED OR IMPLIED WARRANTIES INCLUDING BUT NOT LIMITED TO THE
            IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR PARTICULAR
            PURPOSE ARE DISCLAIMED IN NO EVENT SHALL OR ITS CONTRIBUTORS
            BE LIABLE FOR ANY DIRECT INDIRECT INCIDENTAL SPECIAL EXEMPLARY OR
            CONSEQUENTIAL DAMAGES INCLUDING BUT NOT LIMITED TO PROCUREMENT OF
            SUBSTITUTE GOODS OR SERVICES LOSS OF USE DATA OR PROFITS OR BUSINESS
            INTERRUPTION HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY WHETHER
            IN CONTRACT STRICT LIABILITY OR TORT INCLUDING NEGLIGENCE OR
            OTHERWISE ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE EVEN IF
            ADVISED OF THE DAMAGE
        """.lower().split()
        qtext, itext = get_texts(match)
        assert exp_qtext == qtext.split()
        assert exp_itext == itext.split()
        assert match.coverage() > 97
        assert match_seq.MATCH_SEQ == match.matcher

    def test_match_with_templates_with_redundant_tokens_yield_single_exact_match(self):
        _stored_text = u'copyright reserved mit is license, {{}} copyright reserved mit is license'
        #                 0        1  2   3       4               5        6   7  8       9
        license_expression = 'tst'
        rule = models.Rule(license_expression=license_expression, stored_text=_stored_text)
        idx = index.LicenseIndex([rule])
        expected_idx = {u'_tst_73_0': {u'license': [4, 9], u'mit': [2, 7]}}
        assert expected_idx == idx.to_dict()

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
        assert 100 == match.coverage()
        qtext, itext = get_texts(match)
        assert 'copyright reserved mit is license [is] [the] copyright reserved mit is license' == qtext
        assert 'copyright reserved mit is license copyright reserved mit is license' == itext


class TestIndexDumpLoad(IndexTesting):
    test_data_dir = TEST_DATA_DIR

    def test_dumps_loads_default(self):
        test_rules = self.get_test_rules('index/dump_load')
        idx = index.LicenseIndex(test_rules)
        dumps = idx.dumps()
        idx2 = index.LicenseIndex.loads(dumps)
        expected = [
            u'and', u'are', u'as', u'binary', u'by', u'conditions',
            u'copyright', u'following', u'forms', u'holder', u'in', u'is',
            u'met', u'permitted', u'provided', u'redistribution', u'software',
            u'source', u'that', u'the', u'this', u'use']
        assert expected == sorted(idx2.dictionary)

    def test_dump_load_default(self):
        test_rules = self.get_test_rules('index/dump_load')
        idx = index.LicenseIndex(test_rules)
        test_dump = self.get_temp_file()
        with open(test_dump, 'wb') as td:
            idx.dump(td)
        with open(test_dump, 'rb') as td:
            idx2 = index.LicenseIndex.load(td)
        expected = [
            u'and', u'are', u'as', u'binary', u'by', u'conditions',
            u'copyright', u'following', u'forms', u'holder', u'in', u'is',
            u'met', u'permitted', u'provided', u'redistribution', u'software',
            u'source', u'that', u'the', u'this', u'use']
        assert expected == sorted(idx2.dictionary)

        with open(test_dump, 'rb') as td:
            idx3 = index.LicenseIndex.loads(td.read())
        assert expected == sorted(idx3.dictionary)

    def test_dumps_fast_loads_fast(self):
        test_rules = self.get_test_rules('index/dump_load')
        idx = index.LicenseIndex(test_rules)
        dumps = idx.dumps(fast=True)
        idx2 = index.LicenseIndex.loads(dumps, fast=True)
        expected = [
            u'and', u'are', u'as', u'binary', u'by', u'conditions',
            u'copyright', u'following', u'forms', u'holder', u'in', u'is',
            u'met', u'permitted', u'provided', u'redistribution', u'software',
            u'source', u'that', u'the', u'this', u'use']
        assert expected == sorted(idx2.dictionary)

    def test_dumps_slow_loads_slow(self):
        test_rules = self.get_test_rules('index/dump_load')
        idx = index.LicenseIndex(test_rules)
        dumps = idx.dumps(fast=False)
        idx2 = index.LicenseIndex.loads(dumps, fast=False)
        expected = [
            u'and', u'are', u'as', u'binary', u'by', u'conditions',
            u'copyright', u'following', u'forms', u'holder', u'in', u'is',
            u'met', u'permitted', u'provided', u'redistribution', u'software',
            u'source', u'that', u'the', u'this', u'use']
        assert expected == sorted(idx2.dictionary)

    def test_dumps_fast_loads_slow(self):
        test_rules = self.get_test_rules('index/dump_load')
        idx = index.LicenseIndex(test_rules)
        dumps = idx.dumps(fast=True)
        idx2 = index.LicenseIndex.loads(dumps, fast=False)
        expected = [
            u'and', u'are', u'as', u'binary', u'by', u'conditions',
            u'copyright', u'following', u'forms', u'holder', u'in', u'is',
            u'met', u'permitted', u'provided', u'redistribution', u'software',
            u'source', u'that', u'the', u'this', u'use']
        assert expected == sorted(idx2.dictionary)

    def test_dumps_slow_loads_fast(self):
        test_rules = self.get_test_rules('index/dump_load')
        idx = index.LicenseIndex(test_rules)
        dumps = idx.dumps(fast=False)
        idx2 = index.LicenseIndex.loads(dumps, fast=True)
        expected = [
            u'and', u'are', u'as', u'binary', u'by', u'conditions',
            u'copyright', u'following', u'forms', u'holder', u'in', u'is',
            u'met', u'permitted', u'provided', u'redistribution', u'software',
            u'source', u'that', u'the', u'this', u'use']
        assert expected == sorted(idx2.dictionary)

    def test_dump_fast_load_fast(self):
        test_rules = self.get_test_rules('index/dump_load')
        idx = index.LicenseIndex(test_rules)
        test_dump = self.get_temp_file()
        with open(test_dump, 'wb') as td:
            idx.dump(td, fast=True)
        with open(test_dump, 'rb') as td:
            idx2 = index.LicenseIndex.load(td, fast=True)
        expected = [
            u'and', u'are', u'as', u'binary', u'by', u'conditions',
            u'copyright', u'following', u'forms', u'holder', u'in', u'is',
            u'met', u'permitted', u'provided', u'redistribution', u'software',
            u'source', u'that', u'the', u'this', u'use']
        assert expected == sorted(idx2.dictionary)

    def test_dump_fast_load_slow(self):
        test_rules = self.get_test_rules('index/dump_load')
        idx = index.LicenseIndex(test_rules)
        test_dump = self.get_temp_file()
        with open(test_dump, 'wb') as td:
            idx.dump(td, fast=True)
        with open(test_dump, 'rb') as td:
            idx2 = index.LicenseIndex.load(td, fast=False)
        expected = [
            u'and', u'are', u'as', u'binary', u'by', u'conditions',
            u'copyright', u'following', u'forms', u'holder', u'in', u'is',
            u'met', u'permitted', u'provided', u'redistribution', u'software',
            u'source', u'that', u'the', u'this', u'use']
        assert expected == sorted(idx2.dictionary)

    def test_dump_slow_load_slow(self):
        test_rules = self.get_test_rules('index/dump_load')
        idx = index.LicenseIndex(test_rules)
        test_dump = self.get_temp_file()
        with open(test_dump, 'wb') as td:
            idx.dump(td, fast=False)
        with open(test_dump, 'rb') as td:
            idx2 = index.LicenseIndex.load(td, fast=False)
        expected = [
            u'and', u'are', u'as', u'binary', u'by', u'conditions',
            u'copyright', u'following', u'forms', u'holder', u'in', u'is',
            u'met', u'permitted', u'provided', u'redistribution', u'software',
            u'source', u'that', u'the', u'this', u'use']
        assert expected == sorted(idx2.dictionary)

    def test_dump_slow_load_fast(self):
        test_rules = self.get_test_rules('index/dump_load')
        idx = index.LicenseIndex(test_rules)
        test_dump = self.get_temp_file()
        with open(test_dump, 'wb') as td:
            idx.dump(td, fast=False)
        with open(test_dump, 'rb') as td:
            idx2 = index.LicenseIndex.load(td, fast=True)
        expected = [
            u'and', u'are', u'as', u'binary', u'by', u'conditions',
            u'copyright', u'following', u'forms', u'holder', u'in', u'is',
            u'met', u'permitted', u'provided', u'redistribution', u'software',
            u'source', u'that', u'the', u'this', u'use']
        assert expected == sorted(idx2.dictionary)
