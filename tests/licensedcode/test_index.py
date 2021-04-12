#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os

import pytest

from commoncode.testcase import FileBasedTesting
from licensedcode import index
from licensedcode import match_seq
from licensedcode import models
from licensedcode.query import Query
from licensedcode.spans import Span
from licensedcode.tracing import get_texts
from licensedcode_test_utils import mini_legalese  # NOQA


def MiniLicenseIndex(*args, **kwargs):
    return index.LicenseIndex(*args, _legalese=mini_legalese, **kwargs)


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

    def test_index_structures(self):
        # rule text, unique low/high len, low/high len
        test_rules = [
            (u'a one a two a three licensed.', (4, 1, 4, 1)),
            (u'a four a five a six licensed.', (4, 1, 4, 1)),
            (u'one two three four five gpl', (6, 0, 6, 0)),
            (u'The rose is a rose mit', (4, 0, 5, 0)),
            (u'The license is GPL', (4, 1, 4, 1)),
            (u'The license is this GPL', (5, 1, 5, 1)),
            (u'a license is a rose', (3, 1, 3, 1)),
            (u'the gpl', (2, 0, 2, 0)),
            (u'the mit', (2, 0, 2, 0)),
            (u'the bsd', (2, 0, 2, 0)),
            (u'the lgpl', (2, 0, 2, 0)),
        ]
        idx = MiniLicenseIndex()
        rules = [models.Rule(stored_text=t[0]) for t in test_rules]
        idx._add_rules(rules, _legalese=mini_legalese,)

        assert idx.len_legalese == 40
        expected_lengths = [r[1] for r in test_rules]
        results = [
            (rule.length_unique, rule.high_length_unique,
             rule.length, rule.high_length) for rule in rules]
        assert results == expected_lengths

        expected = set([
            'bsd',
            'five',
            'four',
            'gpl',
            'is',
            'lgpl',
            'mit',
            'one',
            'rose',
            'six',
            'the',
            'this',
            'three',
            'two'])

        xdict = {key for key, val in idx.dictionary.items() if val >= idx.len_legalese}

        assert xdict == expected

        xtbi = sorted([
            'one',
            'two',
            'three',
            'four',
            'five',
            'six',
            'gpl',
            'the',
            'rose',
            'is',
            'mit',
            'this',
            'bsd',
            'lgpl'])

        assert sorted([t for i, t in enumerate(idx.tokens_by_tid) if i >= idx.len_legalese]) == xtbi

    def test_index_structures_with__add_rules(self):
        base = self.get_test_loc('index/tokens_count')
        keys = sorted(os.listdir(base))
        idx = MiniLicenseIndex()
        rules = []
        for key in keys:
            rules.append(models.Rule(
                text_file=os.path.join(base, key), license_expression='gpl-2.0'))

        idx._add_rules(rules, _legalese=mini_legalese)

        assert idx.len_legalese == 40

        expected = set([
            'all',
            'allowed',
            'and',
            'any',
            'for',
            'is',
            'redistribution',
            'thing',
            'yes'])

        xdict = {key for key, val in idx.dictionary.items() if val >= idx.len_legalese}

        assert xdict == expected

        xtbi = sorted([
            'all',
            'allowed',
            'and',
            'any',
            'for',
            'is',
            'redistribution',
            'thing',
            'yes'
        ])

        assert sorted([t for i, t in enumerate(idx.tokens_by_tid) if i >= idx.len_legalese]) == xtbi

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
             u'redistribution': 1}]

        htmset = [{idx.tokens_by_tid[tok]: freq for (tok, freq) in tids_mset.items()}
                  for tids_mset in idx.msets_by_rid]
        assert htmset == expected_msets_by_rid

    def test_index_fails_on_duplicated_rules(self):
        rule_dir = self.get_test_loc('index/no_duplicated_rule')
        try:
            MiniLicenseIndex(models.load_rules(rule_dir))
            self.fail('Exception on dupes not raised')
        except AssertionError as e:
            assert u'Duplicate rules' in str(e)

    @pytest.mark.scanslow
    def test_index_does_not_fail_on_rules_with_similar_normalized_names(self):
        rules_dir = self.get_test_loc('index/similar_names/rules')
        lics_dir = self.get_test_loc('index/similar_names/licenses')
        rules = models.get_rules(licenses_data_dir=lics_dir, rules_data_dir=rules_dir)
        index.LicenseIndex(rules)


class TestMatchNoTemplates(IndexTesting):
    test_data_dir = TEST_DATA_DIR

    def test_match_exact_from_string_once(self):
        rule_text = 'Redistribution and use in source and binary forms, with or without modification, are permitted'
        idx = MiniLicenseIndex([models.Rule(stored_text=rule_text, license_expression='bsd')])
        querys = '''
            The
            Redistribution and use in source and binary forms, with or without modification, are permitted.

            Always'''

        result = idx.match(query_string=querys)
        assert len(result) == 1
        match = result[0]
        qtext, itext = get_texts(match)
        assert qtext == 'Redistribution and use in source and binary forms, with or without modification,\nare permitted.'
        assert itext == 'redistribution and use in source and binary forms with or without modification\nare permitted'

        assert match.qspan == Span(0, 13)
        assert match.ispan == Span(0, 13)

    def test_match_exact_from_string_twice_with_repeated_text(self):
        _stored_text = u'licensed under the GPL, licensed under the GPL'
        #                0    1   2   3         4      5   6   7
        license_expression = 'tst'
        rule = models.Rule(license_expression=license_expression, stored_text=_stored_text)

        idx = MiniLicenseIndex([rule])
        querys = u'Hi licensed under the GPL, licensed under the GPL yes.'
        #          0        1   2   3     4       5     6    7   8   9

        result = idx.match(query_string=querys)
        assert len(result) == 1
        match = result[0]
        qtext, itext = get_texts(match)
        assert qtext == 'licensed under the GPL, licensed under the GPL'
        assert itext == 'licensed under the gpl licensed under the gpl'

        assert match.qspan == Span(0, 7)
        assert match.ispan == Span(0, 7)

        # match again to ensure that there are no state side effects
        result = idx.match(query_string=querys)
        assert len(result) == 1
        match = result[0]
        assert match.qspan == Span(0, 7)
        assert match.ispan == Span(0, 7)

        qtext, itext = get_texts(match)
        assert qtext == u'licensed under the GPL, licensed under the GPL'
        assert itext == u'licensed under the gpl licensed under the gpl'

    def test_match_exact_with_junk_in_between_good_tokens(self):
        _stored_text = u'licensed under the GPL, licensed under the GPL'
        license_expression = 'tst'
        rule = models.Rule(license_expression=license_expression, stored_text=_stored_text)

        idx = MiniLicenseIndex([rule])
        querys = u'Hi licensed that under is the that GPL, licensed or under not the GPL by yes.'

        result = idx.match(query_string=querys)
        assert len(result) == 1
        match = result[0]
        qtext, itext = get_texts(match)
        assert qtext == u'licensed [that] under [is] the [that] GPL, licensed [or] under [not] the GPL'
        assert itext == u'licensed under the gpl licensed under the gpl'

    def test_match_exact_from_file(self):
        idx = MiniLicenseIndex(self.get_test_rules('index/mini'))
        query_loc = self.get_test_loc('index/queryperfect-mini')

        result = idx.match(location=query_loc)
        assert len(result) == 1
        match = result[0]

        qtext, itext = get_texts(match)
        assert qtext == 'Redistribution and use in source and binary forms, with or without modification,\nare permitted.'
        assert itext == 'redistribution and use in source and binary forms with or without modification\nare permitted'

        assert match.qspan == Span(0, 13)
        assert match.ispan == Span(0, 13)

    def test_match_multiple(self):
        test_rules = self.get_test_rules('index/bsd')
        idx = MiniLicenseIndex(test_rules)
        query = self.get_test_loc('index/querysimple')

        result = idx.match(location=query)
        assert len(result) == 1
        match = result[0]
        assert match.qspan == Span(0, 211)
        assert match.ispan == Span(0, 211)

    def test_match_return_correct_offsets(self):
        # notes: A is a stopword. This and that are not
        _stored_text = u'This GPL. A MIT. That LGPL.'
        #                0    1    2 3    4    5

        license_expression = 'tst'
        rule = models.Rule(license_expression=license_expression, stored_text=_stored_text)
        idx = MiniLicenseIndex([rule])
        querys = u'some junk. this GPL. A MIT. that LGPL.'
        #          0    1     2    3    4 5    6    7

        result = idx.match(query_string=querys)
        assert len(result) == 1
        match = result[0]
        qtext, itext = get_texts(match)
        assert qtext == 'this GPL. A MIT. that LGPL.'
        assert itext == 'this gpl mit that lgpl'

        assert match.qspan == Span(0, 4)
        assert match.ispan == Span(0, 4)


class TestMatchWithTemplates(IndexTesting):
    test_data_dir = TEST_DATA_DIR

    def test_match_with_template_and_multiple_rules(self):
        test_rules = self.get_test_rules('index/bsd_templates',)
        idx = MiniLicenseIndex(test_rules)
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
        print('here3')
        assert len(result) == 1
        match = result[0]
        assert match.matcher == match_seq.MATCH_SEQ

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
        assert qtext.split() == exp_qtext
        assert itext.split() == exp_itext

        assert match.qspan == (Span(1, 72) | Span(74, 211))

        assert match.ispan == Span(0, 209)
        assert match.coverage() == 100

    def test_match_to_indexed_template_with_few_tokens_around_gaps(self):
        # Was failing when a gap in a template starts very close to the start of
        # a rule tokens seq. We may still skip that, but we capture a large
        # match anyway.

        rule = models.Rule(text_file=self.get_test_loc('index/templates/idx.txt'),
                           license_expression='test')
        legalese = (
            mini_legalese
            | set(['permission', 'written', 'registered', 'derived', 'damage', 'due']))
        idx = index.LicenseIndex([rule], _legalese=legalese)

        query_loc = self.get_test_loc('index/templates/query.txt')
        result = idx.match(location=query_loc)
        assert len(result) == 1
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
        assert qtext.split() == exp_qtext
        assert itext.split() == exp_itext
        assert match.coverage() > 97
        assert match.matcher == match_seq.MATCH_SEQ

    def test_match_with_templates_with_redundant_tokens_yield_single_exact_match(self):
        _stored_text = u'copyright reserved mit is license, {{}} copyright reserved mit is license'
        #                 0        1  2   3       4               5        6   7  8       9
        license_expression = 'tst'
        rule = models.Rule(license_expression=license_expression, stored_text=_stored_text)
        idx = MiniLicenseIndex([rule])

        querys = u'Hi my copyright reserved mit is license is the copyright reserved mit is license yes.'
        #           0  1         2        3   4  5       6  7   8         9       10  11 12      13  14
        qry = Query(query_string=querys, idx=idx)

        # convert tid to actual token strings
        tks_as_str = lambda tks: [None if tid is None else idx.tokens_by_tid[tid] for tid in tks]

        expected = [None, None, u'copyright', u'reserved', u'mit', u'is', u'license', u'is', None, u'copyright', u'reserved', u'mit', u'is', u'license', None]
        #              0     1            2            3       4      5           6      7      8            9           10      11     12          13     14
        assert tks_as_str(qry.tokens_with_unknowns()) == expected

        result = idx.match(query_string=querys)
        assert len(result) == 1

        match = result[0]
        assert match.qspan == Span(0, 4) | Span(6, 10)
        assert match.ispan == Span(0, 9)
        assert match.coverage() == 100
        qtext, itext = get_texts(match)
        assert qtext == 'copyright reserved mit is license [is] [the] copyright reserved mit is license'
        assert itext == 'copyright reserved mit is license copyright reserved mit is license'
