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

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import codecs
from collections import OrderedDict
import itertools
import os
from time import time

from commoncode.testcase import FileBasedTesting

from licensedcode.tokenize import query_lines
from licensedcode.tokenize import query_tokenizer
from licensedcode.tokenize import word_splitter

from licensedcode.tokenize import rule_tokenizer
from licensedcode.tokenize import ngrams

from licensedcode.tokenize import matched_query_text_tokenizer
from licensedcode.tokenize import tokens_and_non_tokens

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


class TestTokenizers(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_word_splitter(self):
        text = u'Redistribution and use in source and binary forms, with or without modification, are permitted.'
        result = list(word_splitter(text))
        expected = [
            u'Redistribution',
            u'and',
            u'use',
            u'in',
            u'source',
            u'and',
            u'binary',
            u'forms',
            u'with',
            u'or',
            u'without',
            u'modification',
            u'are',
            u'permitted']
        assert expected == result

    def test_query_lines_from_location(self):
        query_loc = self.get_test_loc('index/queryperfect-mini')
        expected = [
             u'',
             u'The',
             u'Redistribution and use in source and binary forms, with or without modification, are permitted.',
             u'',
             u'Always',
        ]
        result = list(query_lines(location=query_loc))
        assert expected == result

    def test_query_lines_from_string(self):
        query_string = '''
            The   
            Redistribution and use in source and binary forms, with or without modification, are permitted.
            
            Always  
            is
 '''
        expected = [
             u'',
             u'The',
             u'Redistribution and use in source and binary forms, with or without modification, are permitted.',
             u'',
             u'Always',
             u'is',
             u'',
        ]

        result = list(query_lines(query_string=query_string))
        assert expected == result

    def test_query_lines_complex(self):
        query_loc = self.get_test_loc('index/querytokens')
        expected = [
             u'',
             u'',
             u'',
             u'Redistribution and use in source and binary forms,',
             u'',
             u'* Redistributions of source code must',
             u'The this that is not there',
             u'Welcom to Jamaica',
             u'* Redistributions in binary form must',
             u'',
             u'THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"',
             u'',
             u'',
             u'',
             u'Redistributions',
        ]
        result = list(query_lines(location=query_loc))
        assert expected == result

    def test_query_tokenizer_handles_empty_string(self):
        text = ''
        result = list(query_tokenizer(text))
        assert [] == result

    def test_query_tokenizer_handles_blank_lines(self):
        text = u' \n\n\t  '
        result = list(query_tokenizer(text))
        assert [] == result

    def test_query_tokenizer_can_split(self):
        text = u'abc def \n GHI'
        result = list(query_tokenizer(text))
        expected = [
            u'abc',
            u'def',
            u'ghi',
        ]
        assert expected == result

    def test_query_tokenizer(self):
        text = u'''Redistribution and use in source and binary forms, with or
        without modification, are permitted provided that the following
        conditions are met:
        Redistributions of source code must retain the above
        copyright notice, this list of conditions and the following
        disclaimer.'''

        result = list(query_tokenizer(text))
        assert 39 == len(result)

        expected = u'''redistribution and use in source and binary forms with or
        without modification are permitted provided that the following
        conditions are met redistributions of source code must retain the above
        copyright notice this list of conditions and the following
        disclaimer'''.split()
        assert expected == result

    def test_rule_and_query_tokenizer_have_the_same_behavior1(self):
        text , expected = 'MODULE_LICENSE("Dual BSD/GPL");', ['module_license', 'dual', 'bsd', 'gpl']
        assert expected == list(rule_tokenizer(text)) == list(query_tokenizer(text))

    def test_rule_and_query_tokenizer_have_the_same_behavior2(self):
        text , expected = 'Dual BSD/GPL', ['dual', 'bsd', 'gpl']
        assert expected == list(rule_tokenizer(text)) == list(query_tokenizer(text))

    def test_rule_and_query_tokenizer_have_the_same_behavior3(self):
        text , expected = 'license=Dual BSD/GPL', ['license', 'dual', 'bsd', 'gpl']
        assert expected == list(rule_tokenizer(text)) == list(query_tokenizer(text))

    def test_rule_and_query_tokenizer_have_the_same_behavior4(self):
        text , expected = 'license_Dual+BSD-GPL', ['license_dual+bsd', 'gpl']
        assert expected == list(rule_tokenizer(text)) == list(query_tokenizer(text))

    def test_rule_and_query_tokenizer_have_the_same_behavior_from_file(self):
        test_file = self.get_test_loc('tokenize/freertos/gpl-2.0-freertos.RULE')
        with codecs.open(test_file, encoding='utf-8') as test:
            text = test.read()
            assert list(rule_tokenizer(text)) == list(query_tokenizer(text))


class TestRuleTokenizer(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_rule_tokenizer_handles_empty_string(self):
        text = ''
        result = list(rule_tokenizer(text))
        assert [] == result

    def test_rule_tokenizer_handles_blank_lines(self):
        text = ' \n\t  '
        result = list(rule_tokenizer(text))
        assert [] == result

    def test_rule_tokenizer_can_split(self):
        text = u'abc def \n GHI'
        result = list(rule_tokenizer(text))
        assert [u'abc', u'def', u'ghi'] == result

    def test_rule_tokenizer_can_split_templates(self):
        text = u'abc def \n {{temp}} GHI'
        result = list(rule_tokenizer(text))
        expected = [u'abc', u'def', u'ghi', ]
        assert expected == result

    def test_rule_tokenizer_merges_contiguous_gaps(self):
        text = u'abc{{temp}}{{xzy}}def'
        result = list(rule_tokenizer(text))
        expected = [u'abc', u'def']
        assert expected == result

    def test_rule_tokenizer_does_not_return_leading_and_trailing_gaps(self):
        text = u'{{xzy}}{{xzy}}abc{{temp}}def{{xzy}}{{xzy}}'
        result = list(rule_tokenizer(text))
        expected = [u'abc', u'def']
        assert expected == result

    def test_rule_tokenizer_handles_empty_templates(self):
        text = u'ab{{}}cd'
        expected = [u'ab', u'cd']
        assert expected == list(rule_tokenizer(text))

    def test_rule_tokenizer_handles_multi_word_templates(self):
        text = u'ab{{10 nexb Company}}cd'
        expected = [u'ab', u'cd']
        assert expected == list(rule_tokenizer(text))

    def test_rule_tokenizer_handles_digits_templates(self):
        text = u'ab{{10}}cd'
        expected = [u'ab', u'cd']
        assert expected == list(rule_tokenizer(text))

    def test_rule_tokenizer_handles_template_with_spaces(self):
        text = u'ab{{       10 }}cd'
        expected = [u'ab', u'cd']
        assert expected == list(rule_tokenizer(text))

    def test_rule_tokenizer_can_process_multiple_templatized_parts(self):
        text = u'ab{{nexb Company}}cd {{second}}ef'
        expected = [u'ab', u'cd', u'ef', ]
        assert expected == list(rule_tokenizer(text))

    def test_rule_tokenizer_can_process_multiple_templatized_parts_strip_multiple_contig_templates_and_leading_and_trailing(self):
        text = u'''{{nexb}}{{nexb}}ab{{nexb Company}}{{nexb}}cd {{second}} {{nexb}}
        {{nexb}}
        {{nexb}}ef
        {{nexb}}
        '''
        expected = [u'ab', u'cd', u'ef', ]
        assert expected == list(rule_tokenizer(text))

    def test_rule_tokenizer_can_process_multiple_templatized_parts_with_default_gap_and_custom_gaps(self):
        text = u'ab{{nexb Company}}cd{{12 second}}ef{{12 second}}gh'
        expected = [u'ab', u'cd', u'ef', u'gh']
        assert expected == list(rule_tokenizer(text))

    def test_rule_tokenizer_handles_empty_lines(self):
        text = u'\n\n'
        expected = []
        assert expected == list(rule_tokenizer(text))

    def test_rule_tokenizer_can_parse_simple_line(self):
        text = u'Licensed by {{12 nexB}} to you '
        expected = [u'licensed', u'by', u'to', u'you']
        assert expected == list(rule_tokenizer(text))

    def test_rule_tokenizer_does_not_throw_exception_for_illegal_pystache_templates(self):
        text = u'''Permission to use, copy, modify, and {{ /or : the
                    text exist without or }} distribute this software...'''
        assert list(rule_tokenizer(text))

    def test_rule_tokenizer_handles_unicode_text_correctly(self):
        expected = [
            u'ist', u'freie', u'software', u'sie', u'k\xf6nnen', u'es',
            u'unter', u'den', u'bedingungen', u'der', u'gnu', u'general', u'n',
            u'public', u'license', u'wie', u'von', u'der', u'free', u'software',
            u'foundation', u'ver\xf6ffentlicht', u'weitergeben', u'und',
            u'oder', u'n', u'modifizieren', u'entweder', u'gem\xe4\xdf',
            u'version', u'3', u'der', u'lizenz', u'oder', u'nach', u'ihrer',
            u'option', u'jeder', u'sp\xe4teren', u'n', u'version', u'n', u'n',
            u'die', u'ver\xf6ffentlichung', u'von', u'erfolgt', u'in',
            u'der', u'hoffnung', u'da\xdf', u'es', u'ihnen', u'von', u'nutzen',
            u'n', u'sein', u'wird', u'aber', u'ohne', u'irgendeine',
            u'garantie', u'sogar', u'ohne', u'die', u'implizite', u'garantie',
            u'der', u'marktreife', u'n', u'oder', u'der', u'verwendbarkeit',
            u'f\xfcr', u'einen', u'bestimmten', u'zweck', u'details', u'finden',
            u'sie', u'in', u'der', u'gnu', u'general', u'n', u'public',
            u'license', u'n', u'n', u'sie', u'sollten', u'ein', u'exemplar',
            u'der', u'gnu', u'general', u'public', u'license', u'zusammen',
            u'mit', u'n', u'erhalten', u'haben', u'falls',
            u'nicht', u'schreiben', u'sie', u'an', u'die', u'free', u'software',
            u'foundation', u'n', u'inc', u'51', u'franklin', u'st', u'fifth',
            u'floor', u'boston', u'ma', u'02110', u'usa',
        ]

        test_file = self.get_test_loc('tokenize/unicode/12180.atxt')
        with codecs.open(test_file, encoding='utf-8') as test:
            assert expected == list(rule_tokenizer(test.read()))

    def test_rule_tokenizer_can_handle_long_text(self):
        expected = [
            u'ist', u'freie', u'software', u'sie', u'k\xf6nnen', u'es',
            u'unter', u'den', u'bedingungen', u'der', u'gnu', u'general', u'n',
            u'public', u'license', u'wie', u'von', u'der', u'free', u'software',
            u'foundation', u'ver\xf6ffentlicht', u'weitergeben', u'und',
            u'oder', u'n', u'modifizieren', u'entweder', u'gem\xe4\xdf',
            u'version', u'3', u'der', u'lizenz', u'oder', u'nach', u'ihrer',
            u'option', u'jeder', u'sp\xe4teren', u'n', u'version', u'n', u'n',
            u'die', u'ver\xf6ffentlichung', u'von', u'erfolgt', u'in',
            u'der', u'hoffnung', u'da\xdf', u'es', u'ihnen', u'von', u'nutzen',
            u'n', u'sein', u'wird', u'aber', u'ohne', u'irgendeine',
            u'garantie', u'sogar', u'ohne', u'die', u'implizite', u'garantie',
            u'der', u'marktreife', u'n', u'oder', u'der', u'verwendbarkeit',
            u'f\xfcr', u'einen', u'bestimmten', u'zweck', u'details', u'finden',
            u'sie', u'in', u'der', u'gnu', u'general', u'n', u'public',
            u'license', u'n', u'n', u'sie', u'sollten', u'ein', u'exemplar',
            u'der', u'gnu', u'general', u'public', u'license', u'zusammen',
            u'mit', u'n', u'erhalten', u'haben', u'falls', u'nicht',
            u'schreiben', u'sie', u'an', u'die', u'free', u'software',
            u'foundation', u'n', u'inc', u'51', u'franklin', u'st', u'fifth',
            u'floor', u'boston', u'ma', u'02110', u'usa',
        ]
        test_file = self.get_test_loc('tokenize/unicode/12180.txt')
        with codecs.open(test_file, encoding='utf-8') as test:
            assert expected == list(rule_tokenizer(test.read()))

    def test_rule_tokenizer_does_not_crash_on_unicode_rules_text_1(self):
        test_file = self.get_test_loc('tokenize/unicode/12290.txt')
        with codecs.open(test_file, encoding='utf-8') as test:
            list(rule_tokenizer(test.read()))

    def test_rule_tokenizer_does_not_crash_on_unicode_rules_text_2(self):
        test_file = self.get_test_loc('tokenize/unicode/12319.txt')
        with codecs.open(test_file, encoding='utf-8') as test:
            list(rule_tokenizer(test.read()))

    def test_rule_tokenizer_does_not_crash_on_unicode_rules_text_3(self):
        test_file = self.get_test_loc('tokenize/unicode/12405.txt')
        with codecs.open(test_file, encoding='utf-8') as test:
            list(rule_tokenizer(test.read()))

    def test_rule_tokenizer_does_not_crash_on_unicode_rules_text_4(self):
        test_file = self.get_test_loc('tokenize/unicode/12407.txt')
        with codecs.open(test_file, encoding='utf-8') as test:
            list(rule_tokenizer(test.read()))

    def test_rule_tokenizer_does_not_crash_on_unicode_rules_text_5(self):
        test_file = self.get_test_loc('tokenize/unicode/12420.txt')
        with codecs.open(test_file, encoding='utf-8') as test:
            list(rule_tokenizer(test.read()))

    def test_rule_tokenizer_does_not_crash_with_non_well_formed_templatized_parts(self):
        text = u'abcd{{ddd'
        assert [u'abcd', u'ddd'] == list(rule_tokenizer(text))

    def test_rule_tokenizer_can_parse_ill_formed_template_from_file(self):
        test_file = self.get_test_loc('tokenize/ill_formed_template/text.txt')
        with codecs.open(test_file, 'rb', encoding='utf-8') as text:
            result = list(rule_tokenizer(text.read()))
        expected_file = self.get_test_loc('tokenize/ill_formed_template/expected.json')

        import json
        regen = False
        if regen:
            with codecs.open(expected_file, 'wb', encoding='utf-8') as ex:
                json.dump(result, ex, indent=2, separators=(',', ': '))

        with codecs.open(expected_file, encoding='utf-8') as ex:
            expected = json.load(ex, object_pairs_hook=OrderedDict)

        assert expected == result

    def test_rule_tokenizer_handles_combination_of_well_formed_and_ill_formed_templates(self):
        text = u'ab{{c}}d}}ef'
        expected = [u'ab', u'd', u'ef']
        assert expected == list(rule_tokenizer(text))

    def test_rule_tokenizer_handles_combination_of_well_formed_and_ill_formed_templates_2(self):
        text = u'}}{{{{abcd}}ddd}}{{'
        assert [u'ddd'] == list(rule_tokenizer(text))

    def test_tokenizers_regex_do_not_choke_on_some_text(self):
        # somehow this text was making the regex choke.
        tf = self.get_test_loc('tokenize/parser.js')
        with codecs.open(tf, 'rb', encoding='utf-8') as text:
            content = text.read()

        start = time()
        list(rule_tokenizer(content))
        duration = time() - start
        assert duration < 5

        start = time()
        list(query_tokenizer(content))
        duration = time() - start
        assert duration < 5

        start = time()
        list(matched_query_text_tokenizer(content))
        duration = time() - start
        assert duration < 5


class TestNgrams(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_ngrams(self):
        tokens = '''
            Redistribution and use in source and binary are permitted.
            '''.split()

        result = list(ngrams(tokens, ngram_length=4))
        expected = [
            ('Redistribution', 'and', 'use', 'in'),
            ('and', 'use', 'in', 'source'),
            ('use', 'in', 'source', 'and'),
            ('in', 'source', 'and', 'binary'),
            ('source', 'and', 'binary', 'are'),
            ('and', 'binary', 'are', 'permitted.')
        ]
        assert expected == result

    def test_ngrams_with_None(self):
        tokens = ['Redistribution', 'and', 'use', None, 'in', 'source', 'and', 'binary', 'are', None]
        result = list(ngrams(tokens, ngram_length=4))
        expected = [
            ('Redistribution', 'and', 'use', None),
            ('and', 'use', None, 'in'),
            ('use', None, 'in', 'source'),
            (None, 'in', 'source', 'and'),
            ('in', 'source', 'and', 'binary'),
            ('source', 'and', 'binary', 'are'),
            ('and', 'binary', 'are', None)]
        assert expected == result

    def test_ngrams_with_None_length_three(self):
        tokens = ['Redistribution', 'and', 'use', None, 'in', 'source', 'and', 'binary', 'are', None]
        result = list(ngrams(tokens, ngram_length=3))
        expected = [
            ('Redistribution', 'and', 'use'),
            ('and', 'use', None),
            ('use', None, 'in'),
            (None, 'in', 'source'),
            ('in', 'source', 'and'),
            ('source', 'and', 'binary'),
            ('and', 'binary', 'are'),
            ('binary', 'are', None)]
        assert expected == result

    def test_ngrams2(self):
        tokens = '''
            Redistribution and use in source and binary are permitted.
            '''.split()

        result = list(ngrams(tokens, ngram_length=4))
        expected = [
            ('Redistribution', 'and', 'use', 'in'),
            ('and', 'use', 'in', 'source'),
            ('use', 'in', 'source', 'and'),
            ('in', 'source', 'and', 'binary'),
            ('source', 'and', 'binary', 'are'),
            ('and', 'binary', 'are', 'permitted.')]

        assert expected == result


class MatchedTextTokenizer(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_tokens_and_non_tokens_yield_properly_all_texts(self):
        text = u'''Redistribution+ ;and use in! 2003 source and binary forms, 
        ()with or without modification, are permitted.\t\n
        \r'''
        result = [m.groupdict() for m in tokens_and_non_tokens(text)]
        expected = [
            {u'punct': None, u'token': u'Redistribution+'},
            {u'punct': u' ;', u'token': None},
            {u'punct': None, u'token': u'and'},
            {u'punct': u' ', u'token': None},
            {u'punct': None, u'token': u'use'},
            {u'punct': u' ', u'token': None},
            {u'punct': None, u'token': u'in'},
            {u'punct': u'! ', u'token': None},
            {u'punct': None, u'token': u'2003'},
            {u'punct': u' ', u'token': None},
            {u'punct': None, u'token': u'source'},
            {u'punct': u' ', u'token': None},
            {u'punct': None, u'token': u'and'},
            {u'punct': u' ', u'token': None},
            {u'punct': None, u'token': u'binary'},
            {u'punct': u' ', u'token': None},
            {u'punct': None, u'token': u'forms'},
            {u'punct': u', \n        ()', u'token': None},
            {u'punct': None, u'token': u'with'},
            {u'punct': u' ', u'token': None},
            {u'punct': None, u'token': u'or'},
            {u'punct': u' ', u'token': None},
            {u'punct': None, u'token': u'without'},
            {u'punct': u' ', u'token': None},
            {u'punct': None, u'token': u'modification'},
            {u'punct': u', ', u'token': None},
            {u'punct': None, u'token': u'are'},
            {u'punct': u' ', u'token': None},
            {u'punct': None, u'token': u'permitted'},
            {u'punct': u'.\t\n\n        \r', u'token': None}
        ]
        assert expected == result

        result_as_text = u''.join(itertools.chain.from_iterable([v for v in m.groupdict().values() if v] for m in tokens_and_non_tokens(text)))
        assert text == result_as_text

    def matched_query_text_tokenizer_yield_properly_all_texts(self):
        text = u'''Redistribution+ ;and use in! 2003 source and binary forms, 
        ()with or without modification, are permitted.\t\n
        \r'''
        result = list(matched_query_text_tokenizer(text))
        expected = [
            (True, u'Redistribution+'),
            (False, u' ;'),
            (True, u'and'),
            (False, u' '),
            (True, u'use'),
            (False, u' '),
            (True, u'in'),
            (False, u'! '),
            (True, u'2003'),
            (False, u' '),
            (True, u'source'),
            (False, u' '),
            (True, u'and'),
            (False, u' '),
            (True, u'binary'),
            (False, u' '),
            (True, u'forms'),
            (False, u', \n        ()'),
            (True, u'with'),
            (False, u' '),
            (True, u'or'),
            (False, u' '),
            (True, u'without'),
            (False, u' '),
            (True, u'modification'),
            (False, u', '),
            (True, u'are'),
            (False, u' '),
            (True, u'permitted'),
            (False, u'.\t\n\n        \r')
        ]
        assert expected == result

        result_as_text = u''.join(v for _t, v in result)
        assert text == result_as_text
