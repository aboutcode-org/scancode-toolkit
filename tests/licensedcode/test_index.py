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
from itertools import chain
from operator import itemgetter
import os

from commoncode.testcase import FileBasedTesting

from licensedcode.whoosh_spans.spans import Span

from licensedcode import index
from licensedcode import models
from licensedcode import query


TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


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
        assert 4 == idx.frequencies_by_tid[idx.dictionary[u'redistribution']]
        assert 7 == idx.frequencies_by_tid[idx.dictionary[u'disclaimer']]
        assert 2 == len(idx.postings_by_rid)
        keys = chain(*[ridx.keys() for ridx in idx.postings_by_rid])
        assert 138 == len(set(keys))
        assert 1, 61 == idx.postings_by_rid[idx.dictionary['minimum']]

    def test__add_rules(self):
        test_rules = self.get_test_rules('index/bsd', ['bsd-new', 'bsd-no-mod'])
        idx = index.LicenseIndex()
        idx._add_rules(test_rules)
        assert 4 == idx.frequencies_by_tid[idx.dictionary[u'redistribution']]
        assert 7 == idx.frequencies_by_tid[idx.dictionary[u'disclaimer']]
        assert 2 == len(idx.postings_by_rid)
        keys = chain(*[ridx.keys() for ridx in idx.postings_by_rid])
        assert 138 == len(set(keys))
        assert 1, 61 == idx.postings_by_rid[idx.dictionary['minimum']]

    def test__add_rules_with_templates(self):
        test_rules = self.get_test_rules('index/bsd_templates2')
        idx = index.LicenseIndex()
        idx._add_rules(test_rules)
        assert 4 == idx.frequencies_by_tid[idx.dictionary[u'redistribution']]
        assert 7 == idx.frequencies_by_tid[idx.dictionary[u'disclaimer']]
        assert 2 == len(idx.postings_by_rid)
        keys = chain(*[ridx.keys() for ridx in idx.postings_by_rid])
        assert 137 == len(set(keys))

    def test_index_internals_with__add_rules(self):
        base = self.get_test_loc('index/tokens_count')
        keys = sorted(os.listdir(base))
        idx = index.LicenseIndex()
        rules = []
        for key in keys:
            rules.append(models.Rule(text_file=os.path.join(base, key)))

        idx._add_rules(rules)

        expected_index = [
            {5: array('h', [0])},
            {0: array('h', [1]), 5: array('h', [0])},
            {0: array('h', [1]), 5: array('h', [0]), 6: array('h', [2])},
            {0: array('h', [1]), 2: array('h', [3]), 5: array('h', [0]), 6: array('h', [2])},
            {0: array('h', [1]), 1: array('h', [4]), 2: array('h', [3]), 5: array('h', [0]), 6: array('h', [2])},
            {0: array('h', [1]), 1: array('h', [4, 6]), 2: array('h', [3]), 3: array('h', [5, 7]), 4: array('h', [9]), 5: array('h', [0]), 6: array('h', [2]), 7: array('h', [8])},
            {0: array('h', [1]), 5: array('h', [0])},
            {0: array('h', [1]), 5: array('h', [0]), 6: array('h', [2])},
            {0: array('h', [1]), 2: array('h', [3]), 5: array('h', [0]), 6: array('h', [2])},
            {0: array('h', [1, 2]), 2: array('h', [4]), 5: array('h', [0]), 6: array('h', [3])},
            {0: array('h', [1]), 1: array('h', [4]), 2: array('h', [3]), 5: array('h', [0]), 6: array('h', [2])},
            {0: array('h', [1]), 1: array('h', [4]), 2: array('h', [3]), 3: array('h', [5]), 5: array('h', [0]), 6: array('h', [2])},
            {0: array('h', [1]), 1: array('h', [4, 6]), 2: array('h', [3]), 3: array('h', [5]), 5: array('h', [0]), 6: array('h', [2])},
            {0: array('h', [1]), 1: array('h', [4, 6]), 2: array('h', [3]), 3: array('h', [5, 7]), 5: array('h', [0]), 6: array('h', [2])},
            {0: array('h', [1]), 1: array('h', [4, 6]), 2: array('h', [3]), 3: array('h', [5, 7]), 5: array('h', [0]), 6: array('h', [2]), 7: array('h', [8])}
        ]
        assert expected_index == idx.postings_by_rid

        expected_freqs = [15, 11, 10, 8, 1, 15, 12, 2]
        assert expected_freqs == idx.frequencies_by_tid

        expected_dict = [
            (u'is', 0),
            (u'all', 1),
            (u'for', 2),
            (u'and', 3),
            (u'thing', 4),
            (u'redistribution', 5),
            (u'allowed', 6),
            (u'any', 7)
        ]
        assert expected_dict == sorted(idx.dictionary.items(), key=itemgetter(1))

    def test_index_internals_humanized_with__add_rules(self):
        base = self.get_test_loc('index/tokens_count')
        keys = sorted(os.listdir(base))
        rules = [models.Rule(text_file=os.path.join(base, key)) for key in keys]
        idx = index.LicenseIndex(rules)

        expected_index = {
            'plain1': {u'redistribution': [0]},
            'plain2': {u'is': [1], u'redistribution': [0]},
            'plain3': {u'allowed': [2], u'is': [1], u'redistribution': [0]},
            'plain4': {u'allowed': [2], u'for': [3], u'is': [1], u'redistribution': [0]},
            'plain5': {u'all': [4], u'allowed': [2], u'for': [3], u'is': [1], u'redistribution': [0]},
            'tmpl10': {u'all': [4, 6], u'allowed': [2], u'and': [5, 7], u'any': [8], u'for': [3], u'is': [1], u'redistribution': [0], u'thing': [9]},
            'tmpl2': {u'is': [1], u'redistribution': [0]},
            'tmpl3': {u'allowed': [2], u'is': [1], u'redistribution': [0]},
            'tmpl4': {u'allowed': [2], u'for': [3], u'is': [1], u'redistribution': [0]},
            'tmpl5': {u'allowed': [3], u'for': [4], u'is': [1, 2], u'redistribution': [0]},
            'tmpl5_2': {u'all': [4], u'allowed': [2], u'for': [3], u'is': [1], u'redistribution': [0]},
            'tmpl6': {u'all': [4], u'allowed': [2], u'and': [5], u'for': [3], u'is': [1], u'redistribution': [0]},
            'tmpl7': {u'all': [4, 6], u'allowed': [2], u'and': [5], u'for': [3], u'is': [1], u'redistribution': [0]},
            'tmpl8': {u'all': [4, 6], u'allowed': [2], u'and': [5, 7], u'for': [3], u'is': [1], u'redistribution': [0]},
            'tmpl9': {u'all': [4, 6], u'allowed': [2], u'and': [5, 7], u'any': [8], u'for': [3], u'is': [1], u'redistribution': [0]}
        }
        assert expected_index == idx._as_dict()

        expected_freqs = {u'all': 11, u'allowed': 12, u'and': 8, u'any': 2, u'for': 10, u'is': 15, u'redistribution': 15, u'thing': 1}
        assert expected_freqs == {idx.tokens_by_tid[tok]: freq for tok, freq in enumerate(idx.frequencies_by_tid)}

        expected_dict = {
            u'is': 0,
            u'all': 1,
            u'for': 2,
            u'and': 3,
            u'thing': 4,
            u'redistribution': 5,
            u'allowed': 6,
            u'any': 7
        }
        assert expected_dict == idx.dictionary
        assert 8 == len(idx.tokens_by_tid)
        assert 5 == idx.len_junk

        expected_frequencies_by_rid = [
            {u'redistribution': 1},
            {u'is': 1, u'redistribution': 1},
            {u'allowed': 1, u'is': 1, u'redistribution': 1},
            {u'allowed': 1, u'for': 1, u'is': 1, u'redistribution': 1},
            {u'all': 1, u'allowed': 1, u'for': 1, u'is': 1, u'redistribution': 1},
            {u'all': 2, u'allowed': 1, u'and': 2, u'any': 1, u'for': 1, u'is': 1, u'redistribution': 1, u'thing': 1},
            {u'is': 1, u'redistribution': 1},
            {u'allowed': 1, u'is': 1, u'redistribution': 1},
            {u'allowed': 1, u'for': 1, u'is': 1, u'redistribution': 1},
            {u'allowed': 1, u'for': 1, u'is': 2, u'redistribution': 1},
            {u'all': 1, u'allowed': 1, u'for': 1, u'is': 1, u'redistribution': 1},
            {u'all': 1, u'allowed': 1, u'and': 1, u'for': 1, u'is': 1, u'redistribution': 1},
            {u'all': 2, u'allowed': 1, u'and': 1, u'for': 1, u'is': 1, u'redistribution': 1},
            {u'all': 2, u'allowed': 1, u'and': 2, u'for': 1, u'is': 1, u'redistribution':1},
            {u'all': 2, u'allowed': 1, u'and': 2, u'any': 1, u'for': 1, u'is': 1, u'redistribution': 1}
        ]
        assert expected_frequencies_by_rid == [{idx.tokens_by_tid[tok]: freq for tok, freq in rule_freq.items()} for rule_freq in idx.frequencies_by_rid]

    def test_renumber_tokens(self):
        test_rules = [
            u'a one a two a three licensed.',
            u'a four a five a six licensed.',
            u'one two three four five gpl',
            u'The rose is a rose mit',
            u'The license is GPL',
            u'The license is a GPL',
            u'a license is a rose',
            u'the gpl',
            u'the mit',
            u'the bsd',
            u'the lgpl',
        ]
        idx = index.LicenseIndex()
        tokens_by_rid = []
        rules = []
        for t in test_rules:
            rule = models.Rule(_text=t)
            rules.append(rule)
            tokens_by_rid.append(list(rule.tokens()))
        rules_tokens_ids = idx._add_rules(rules, optimize=False)

        renumbered = index.renumber_token_ids(rules_tokens_ids, idx.dictionary, idx.tokens_by_tid, idx.frequencies_by_tid, length=2, with_checks=True)
        old_to_new, len_junk, new_dictionary, new_tokens_by_tid, new_frequencies_by_tid = renumbered

        assert array('h', [0, 15, 8, 7, 10, 2, 14, 11, 13, 12, 6, 3, 9, 1, 5, 4]) == old_to_new
        assert 10 == len_junk

        xdict = {
            u'a': 0,
            u'the': 1,
            u'is': 2,
            u'rose': 3,
            u'two': 4,
            u'three': 5,
            u'one': 6,
            u'four': 7,
            u'five': 8,
            u'six': 9,
            u'gpl': 10,
            u'license': 11,
            u'mit': 12,
            u'licensed': 13,
            u'lgpl': 14,
            u'bsd': 15,
        }
        assert xdict == new_dictionary

        xtbi = [
            u'a',
            u'the',
            u'is',
            u'rose',
            u'two',
            u'three',
            u'one',
            u'four',
            u'five',
            u'six',
            u'gpl',
            u'license',
            u'mit',
            u'licensed',
            u'lgpl',
            u'bsd']
        assert xtbi == new_tokens_by_tid

        xtf = [10, 7, 4, 3, 2, 2, 2, 2, 2, 1, 4, 3, 2, 2, 1, 1]
        assert xtf == new_frequencies_by_tid

    def test_index_internals_with_template_rule(self):
        idx = index.LicenseIndex([models.Rule(_text=u'A one. A {{}}two. A three.')])
        expected = {'_tst_': {u'a': [0, 2, 4], u'one': [1], u'three': [5], u'two': [3]}}
        assert expected == idx._as_dict()


class TestMatchNoTemplates(IndexTesting):
    test_data_dir = TEST_DATA_DIR

    def test_match_exact_from_string(self):
        idx = index.LicenseIndex(self.get_test_rules('index/mini'))
        query = '''
            The
            Redistribution and use in source and binary forms, with or without modification, are permitted.
            
            Always'''

        result = idx.match(query=query, min_score=100)
        assert 1 == len(result)
        match = result[0]
        assert (Span(0, 13),) == match.qspans
        assert (Span(0, 13),) == match.ispans

    def test_match_exact_from_string_twice(self):
        rule = models.Rule()
        rule._text = u'name is joker, name is joker'
        #                 0  1     2     3  4     5
        rule.licenses = ['tst']

        idx = index.LicenseIndex([rule])
        query = u'Hi my name is joker, name is joker yes.'
        # match            0  1     2     3  4    5

        result = idx.match(query=query, min_score=0)
        assert 1 == len(result)
        match = result[0]
        assert (Span(0, 5),) == match.qspans
        assert (Span(0, 5),) == match.ispans

        # match again to ensure that there are no state side effects
        result = idx.match(query=query, min_score=100)
        assert 1 == len(result)
        match = result[0]
        assert (Span(0, 5),) == match.qspans
        assert (Span(0, 5),) == match.ispans

    def test_match_exact_from_file(self):
        idx = index.LicenseIndex(self.get_test_rules('index/mini'))
        query = self.get_test_loc('index/queryperfect-mini')

        result = idx.match(location=query, min_score=100)
        assert 1 == len(result)
        match = result[0]
        assert (Span(0, 13),) == match.qspans
        assert (Span(0, 13),) == match.ispans

    def test_match_exact_from_file_2(self):
        idx = index.LicenseIndex(self.get_test_rules('index/bsd'))
        query = self.get_test_loc('index/queryperfect')

        result = idx.match(location=query, min_score=100)
        assert 1 == len(result)
        match = result[0]
        assert (Span(0, 212),) == match.qspans
        assert (Span(0, 212),) == match.ispans

    def test_match_multiple(self):
        test_rules = self.get_test_rules('index/bsd')
        idx = index.LicenseIndex(test_rules)
        query = self.get_test_loc('index/querysimple')

        result = idx.match(location=query, min_score=100)
        assert 1 == len(result)
        expected = (Span(0, 212),), (Span(0, 212),)
        match = result[0]
        assert expected == (match.qspans, match.ispans)

    def test_match_return_correct_offsets(self):
        rule = models.Rule(licenses=['test'])
        rule._text = u'A GPL. A MIT. A LGPL.'
        #              0   1  2   3  4    5
        idx = index.LicenseIndex([rule])
        query = u'some junk. A GPL. A MIT. A LGPL.'
        #            0    1  2   3  4   5  6    7

        result = idx.match(query=query, min_score=100)
        assert 1 == len(result)
        assert (Span(0, 5),) == result[0].qspans
        assert (Span(0, 5),) == result[0].ispans


class TestMatchWithTemplates(IndexTesting):
    test_data_dir = TEST_DATA_DIR

    def test_match_with_template_and_multiple_rules(self):
        test_rules = self.get_test_rules('index/bsd_templates',)
        idx = index.LicenseIndex(test_rules)
        query_loc = self.get_test_loc('index/queryperfect_single_template')

        result = idx.match(location=query_loc, min_score=80)

        assert 1 == len(result)
        match = result[0]
        assert 100 == match.normalized_score()
        assert (Span(1, 72), Span(74, 212),) == match.qspans
        assert (Span(0, 210),) == match.ispans

    def test_match_to_indexed_template_with_few_tokens_around_gaps(self):
        # was failing when a gapped token (from a template) starts at a
        # beginning of an index doc

        rule = models.Rule(text_file=self.get_test_loc('index/templates/idx.txt'), licenses=['test'],)
        idx = index.LicenseIndex([rule])

        query_loc = self.get_test_loc('index/templates/query.txt')
        result = idx.match(location=query_loc, min_score=0)

        assert 1 == len(result)
        match = result[0]
        assert 99.5 < match.normalized_score()
        assert Span(2, 253) == match.qregion
        assert Span(1, 244) == match.iregion

    def test_match_with_templates_with_redundant_tokens_yield_single_exact_match(self):
        rule = models.Rule()
        rule._text = u'copyright reserved mit is license, {{}} copyright reserved mit is license'
        #                     0    1       2   3  4             5              6   7  8    9
        rule.licenses = ['tst']
        idx = index.LicenseIndex([rule], _ngram_length=2)
        querys = u'Hi my copyright reserved mit is license the copyright reserved mit is license yes.'
        #                 0          1      2  3       4        5            6     7  8   9
        result = idx.match(query=querys, min_score=0)
        assert 1 == len(result)

        match = result[0]
        assert Span(0, 9) == match.qregion
        assert Span(0, 9) == match.iregion
        assert 1 == match.score()
        qtext, itext = query.get_texts(match, query=querys, dictionary=idx.dictionary)
        assert 'copyright reserved mit is license <no-match> copyright reserved mit is license' == qtext
        assert 'copyright reserved mit is license copyright reserved mit is license' == itext
