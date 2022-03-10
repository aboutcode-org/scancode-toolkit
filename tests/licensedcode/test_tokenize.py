# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import io
import itertools
import json
import os
from time import time

from commoncode.testcase import FileBasedTesting

from licensedcode.tokenize import index_tokenizer
from licensedcode.tokenize import key_phrase_tokenizer
from licensedcode.tokenize import matched_query_text_tokenizer
from licensedcode.tokenize import query_lines
from licensedcode.tokenize import query_tokenizer
from licensedcode.tokenize import ngrams
from licensedcode.tokenize import select_ngrams
from licensedcode.tokenize import tokens_and_non_tokens
from licensedcode.tokenize import word_splitter
from scancode_config import REGEN_TEST_FIXTURES


TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


def check_results(result, expected_file, regen=REGEN_TEST_FIXTURES):

    # we dumps/loads to normalize tuples/etc
    result = json.loads(json.dumps(result))

    if regen:
        with open(expected_file, 'w') as exc_test:
            json.dump(result , exc_test, indent=2)

    with io.open(expected_file, encoding='utf-8') as exc_test:
        expected = json.load(exc_test)

    assert result == expected


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
        assert result == expected

    def test_word_splitter_with_trailing_plus(self):
        text = u'gpl-3.0+'
        result = list(word_splitter(text))
        expected = [u'gpl', u'3', u'0+']
        assert result == expected

    def test_word_splitter_with_internal_plus(self):
        text = u'gpl-+3.0'
        result = list(word_splitter(text))
        expected = [u'gpl', u'3', u'0']
        assert result == expected

    def test_query_lines_from_location(self):
        query_loc = self.get_test_loc('index/queryperfect-mini')
        expected = [
             u'',
             u'The',
             u'Redistribution and use in source and binary forms, with or without modification, are permitted.',
             u'',
             u'Always',
        ]
        result = [l for _, l in query_lines(location=query_loc)]
        assert result == expected

    def test_query_lines_from_location_return_a_correct_number_of_lines(self):
        query_loc = self.get_test_loc('tokenize/correct_lines')
        # note that this is a single line (line number is 1)... broken in two.
        expected = [
            (1,
             u'Permission is hereby granted, free of charge, to any person '
             'obtaining a copy of this software and associated documentation '
             'files (the "Software"), to deal in the Software without restriction, '
             'including without limitation the rights to use, copy, modify, merge'
             ', , , sublicense, and/or  Software, ,'),
            (1, u'subject')]
        result = list(query_lines(location=query_loc))
        assert result == expected

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
        result = [l for _, l in query_lines(query_string=query_string)]
        assert result == expected

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
        result = [l for _, l in query_lines(location=query_loc)]
        assert result == expected

    def test_query_tokenizer_handles_empty_string(self):
        text = ''
        result = list(query_tokenizer(text))
        assert result == []

    def test_query_tokenizer_handles_blank_lines(self):
        text = u' \n\n\t  '
        result = list(query_tokenizer(text))
        assert result == []

    def test_query_tokenizer_handles_blank_lines2(self):
        text = ' \n\t  '
        result = list(query_tokenizer(text))
        assert result == []

    def test_query_tokenizer_handles_empty_lines(self):
        text = u'\n\n'
        expected = []
        assert list(query_tokenizer(text)) == expected

    def test_query_tokenizer_can_split(self):
        text = u'abc def \n GHI'
        result = list(query_tokenizer(text))
        assert result == [u'abc', u'def', u'ghi']

    def test_query_tokenizer(self):
        text = u'''Redistribution and use in source and binary forms, with or
        without modification, are permitted provided that the following
        conditions are met:
        Redistributions of source code must retain the above
        copyright notice, this list of conditions and the following
        disclaimer.'''

        result = list(query_tokenizer(text))

        expected = u'''redistribution and use in source and binary forms with or
        without modification are permitted provided that the following
        conditions are met redistributions of source code must retain the above
        copyright notice this list of conditions and the following
        disclaimer'''.split()
        assert result == expected

    def test_query_tokenizer_behavior1(self):
        text , expected = 'MODULE_LICENSE("Dual BSD/GPL");', ['module', 'license', 'dual', 'bsd', 'gpl']
        assert list(query_tokenizer(text)) == expected

    def test_query_tokenizer_behavior2(self):
        text , expected = 'Dual BSD/GPL', ['dual', 'bsd', 'gpl']
        assert list(query_tokenizer(text)) == expected

    def test_query_tokenizer_behavior3(self):
        text , expected = 'license=Dual BSD/GPL', ['license', 'dual', 'bsd', 'gpl']
        assert list(query_tokenizer(text)) == expected

    def test_query_tokenizer_behavior4(self):
        text , expected = 'license_Dual+BSD-GPL', ['license', 'dual+bsd', 'gpl']
        assert list(query_tokenizer(text)) == expected

    def test_query_tokenizer_behavior_from_file(self, regen=REGEN_TEST_FIXTURES):
        test_file = self.get_test_loc('tokenize/freertos/gpl-2.0-freertos.RULE')
        with io.open(test_file, encoding='utf-8') as test:
            text = test.read()
        result = list(query_tokenizer(text))
        expected_file = test_file + '.json'
        check_results(result, expected_file, regen=regen)

    def test_query_tokenizer_can_split_legacy_templates(self):
        text = u'abc def \n temp GHI'
        result = list(query_tokenizer(text))
        expected = [u'abc', u'def', u'temp', u'ghi', ]
        assert result == expected

    def test_query_tokenizer_merges_contiguous_gaps(self):
        text = u'abc temp xzy def'
        result = list(query_tokenizer(text))
        expected = [u'abc', u'temp', u'xzy', u'def']
        assert result == expected

    def test_query_tokenizer_handles_empty_legacy_templates(self):
        text = u'ab cd'
        expected = [u'ab', u'cd']
        assert list(query_tokenizer(text)) == expected

    def test_query_tokenizer_does_not_throw_exception_for_pystache_templates(self):
        text = u'''Permission to use, copy, modify, and  /or : the
                    text exist without or distribute this software...'''
        assert list(query_tokenizer(text))

    def test_query_tokenizer_handles_unicode_text_correctly(self):
        expected = [
            u'ist', u'freie', u'software', u'sie', u'k\xf6nnen', u'es',
            u'unter', u'den', u'bedingungen', u'der', u'gnu', u'general', u'n',
            u'public', u'license', u'wie', u'von', u'der', u'free', u'software',
            u'foundation', u'ver\xf6ffentlicht', u'weitergeben', u'und',
            u'oder', u'n', u'modifizieren', u'entweder', u'gem\xe4\xdf',
            u'version', u'3', u'der', u'lizenz', u'oder', u'nach', u'ihrer',
            u'option', u'jeder', u'sp\xe4teren', u'n', u'version', u'n', u'n',
            u'die', u'ver\xf6ffentlichung', u'von', u'pychess', u'erfolgt', u'in',
            u'der', u'hoffnung', u'da\xdf', u'es', u'ihnen', u'von', u'nutzen',
            u'n', u'sein', u'wird', u'aber', u'ohne', u'irgendeine',
            u'garantie', u'sogar', u'ohne', u'die', u'implizite', u'garantie',
            u'der', u'marktreife', u'n', u'oder', u'der', u'verwendbarkeit',
            u'f\xfcr', u'einen', u'bestimmten', u'zweck', u'details', u'finden',
            u'sie', u'in', u'der', u'gnu', u'general', u'n', u'public',
            u'license', u'n', u'n', u'sie', u'sollten', u'ein', u'exemplar',
            u'der', u'gnu', u'general', u'public', u'license', u'zusammen',
            u'mit', u'pychess', u'n', u'erhalten', u'haben', u'falls',
            u'nicht', u'schreiben', u'sie', u'an', u'die', u'free', u'software',
            u'foundation', u'n', u'inc', u'51', u'franklin', u'st', u'fifth',
            u'floor', u'boston', u'ma', u'02110', u'usa',
        ]

        test_file = self.get_test_loc('tokenize/unicode/12180.atxt')
        with io.open(test_file, encoding='utf-8') as test:
            assert list(query_tokenizer(test.read())) == expected

    def test_query_tokenizer_can_handle_long_text(self):
        expected = [
            u'pychess',
            u'ist', u'freie', u'software', u'sie', u'k\xf6nnen', u'es',
            u'unter', u'den', u'bedingungen', u'der', u'gnu', u'general', u'n',
            u'public', u'license', u'wie', u'von', u'der', u'free', u'software',
            u'foundation', u'ver\xf6ffentlicht', u'weitergeben', u'und',
            u'oder', u'n', u'modifizieren', u'entweder', u'gem\xe4\xdf',
            u'version', u'3', u'der', u'lizenz', u'oder', u'nach', u'ihrer',
            u'option', u'jeder', u'sp\xe4teren', u'n', u'version', u'n', u'n',
            u'die', u'ver\xf6ffentlichung', u'von', u'pychess', u'erfolgt', u'in',
            u'der', u'hoffnung', u'da\xdf', u'es', u'ihnen', u'von', u'nutzen',
            u'n', u'sein', u'wird', u'aber', u'ohne', u'irgendeine',
            u'garantie', u'sogar', u'ohne', u'die', u'implizite', u'garantie',
            u'der', u'marktreife', u'n', u'oder', u'der', u'verwendbarkeit',
            u'f\xfcr', u'einen', u'bestimmten', u'zweck', u'details', u'finden',
            u'sie', u'in', u'der', u'gnu', u'general', u'n', u'public',
            u'license', u'n', u'n', u'sie', u'sollten', u'ein', u'exemplar',
            u'der', u'gnu', u'general', u'public', u'license', u'zusammen',
            u'mit', u'pychess', u'n', u'erhalten', u'haben', u'falls', u'nicht',
            u'schreiben', u'sie', u'an', u'die', u'free', u'software',
            u'foundation', u'n', u'inc', u'51', u'franklin', u'st', u'fifth',
            u'floor', u'boston', u'ma', u'02110', u'usa',
        ]
        test_file = self.get_test_loc('tokenize/unicode/12180.txt')
        with io.open(test_file, encoding='utf-8') as test:
            assert list(query_tokenizer(test.read())) == expected

    def test_query_tokenizer_does_not_crash_on_unicode_rules_text_1(self):
        test_file = self.get_test_loc('tokenize/unicode/12290.txt')
        with io.open(test_file, encoding='utf-8') as test:
            list(query_tokenizer(test.read()))

    def test_query_tokenizer_does_not_crash_on_unicode_rules_text_2(self):
        test_file = self.get_test_loc('tokenize/unicode/12319.txt')
        with io.open(test_file, encoding='utf-8') as test:
            list(query_tokenizer(test.read()))

    def test_query_tokenizer_does_not_crash_on_unicode_rules_text_3(self):
        test_file = self.get_test_loc('tokenize/unicode/12405.txt')
        with io.open(test_file, encoding='utf-8') as test:
            list(query_tokenizer(test.read()))

    def test_query_tokenizer_does_not_crash_on_unicode_rules_text_4(self):
        test_file = self.get_test_loc('tokenize/unicode/12407.txt')
        with io.open(test_file, encoding='utf-8') as test:
            list(query_tokenizer(test.read()))

    def test_query_tokenizer_does_not_crash_on_unicode_rules_text_5(self):
        test_file = self.get_test_loc('tokenize/unicode/12420.txt')
        with io.open(test_file, encoding='utf-8') as test:
            list(query_tokenizer(test.read()))

    def test_query_tokenizer_does_not_crash_with_non_well_formed_legacy_templatized_parts(self):
        text = u'abcd{{ddd'
        assert list(query_tokenizer(text)) == [u'abcd', u'ddd']

    def test_query_tokenizer_can_parse_ill_formed_legacy_template_from_file(self, regen=REGEN_TEST_FIXTURES):
        test_file = self.get_test_loc('tokenize/ill_formed_template/text.txt')
        with io.open(test_file, encoding='utf-8') as text:
            result = list(query_tokenizer(text.read()))
        expected_file = self.get_test_loc('tokenize/ill_formed_template/expected.json')
        check_results(result, expected_file, regen=regen)

    def test_tokenizers_regex_do_not_choke_on_some_text(self):
        # somehow this text was making the regex choke.
        tf = self.get_test_loc('tokenize/parser.js')
        with io.open(tf, encoding='utf-8') as text:
            content = text.read()

        start = time()
        list(query_tokenizer(content))
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

    def test_query_tokenizer_handles_rarer_unicode_codepoints(self):
        # NOTE: we are not catching the heart as a proper token, but this is
        # rare enough that we do not care
        text = '♡ Copying Art is an act of love. Love is not subject to law.'
        expected = [u'copying', u'art', u'is', u'an', u'act', u'of', u'love',
            u'love', u'is', u'not', u'subject', u'to', u'law']
        assert list(query_tokenizer(text)) == expected

    def test_query_tokenizer_handles_rarer_unicode_typographic_quotes(self):
        text = 'a “bar” is “open„ not “closed” ‘free‚ not ‘foo’ „Gänsefüßchen“'
        expected = [
            'a', 'bar', 'is', 'open', 'not', 'closed',
            'free', 'not', 'foo', 'gänsefüßchen',
        ]
        assert list(query_tokenizer(text)) == expected

    def test_query_lines_on_html_like_texts(self, regen=REGEN_TEST_FIXTURES):
        test_file = self.get_test_loc('tokenize/htmlish.txt')
        expected_file = test_file + '.expected.query_lines.json'
        result = list(query_lines(test_file))
        check_results(result, expected_file, regen=regen)

    def test_query_lines_on_html_like_texts_2(self, regen=REGEN_TEST_FIXTURES):
        test_file = self.get_test_loc('tokenize/htmlish.html')
        expected_file = test_file + '.expected.query_lines.json'
        result = list(query_lines(test_file))
        check_results(result, expected_file, regen=regen)

    def test_query_tokenizer_on_html_like_texts(self, regen=REGEN_TEST_FIXTURES):
        test_file = self.get_test_loc('tokenize/htmlish.txt')
        expected_file = test_file + '.expected.query_tokenizer.json'
        lines = query_lines(test_file)
        result = [list(query_tokenizer(line)) for _ln, line in lines]
        check_results(result, expected_file, regen=regen)

    def test_query_tokenizer_lines_on_html_like_texts_2(self, regen=REGEN_TEST_FIXTURES):
        test_file = self.get_test_loc('tokenize/htmlish.html')
        expected_file = test_file + '.expected.query_tokenizer.json'
        lines = query_lines(test_file)
        result = [list(query_tokenizer(line)) for _ln, line in lines]
        check_results(result, expected_file, regen=regen)

    def test_index_tokenizer_on_html_like_texts(self, regen=REGEN_TEST_FIXTURES):
        test_file = self.get_test_loc('tokenize/htmlish.txt')
        expected_file = test_file + '.expected.index_tokenizer.json'
        lines = query_lines(test_file)
        result = [list(index_tokenizer(line)) for _ln, line in lines]
        check_results(result, expected_file, regen=regen)

    def test_index_tokenizer_lines_on_html_like_texts_2(self, regen=REGEN_TEST_FIXTURES):
        test_file = self.get_test_loc('tokenize/htmlish.html')
        expected_file = test_file + '.expected.index_tokenizer.json'
        lines = query_lines(test_file)
        result = [list(index_tokenizer(line)) for _ln, line in lines]
        check_results(result, expected_file, regen=regen)

    def test_key_phrase_tokenizer_on_html_like_texts(self, regen=REGEN_TEST_FIXTURES):
        test_file = self.get_test_loc('tokenize/htmlish.txt')
        expected_file = test_file + '.expected.key_phrase_tokenizer.json'
        lines = query_lines(test_file)
        result = [list(key_phrase_tokenizer(line)) for _ln, line in lines]
        check_results(result, expected_file, regen=regen)

    def test_key_phrase_tokenizer_lines_on_html_like_texts_2(self, regen=REGEN_TEST_FIXTURES):
        test_file = self.get_test_loc('tokenize/htmlish.html')
        expected_file = test_file + '.expected.key_phrase_tokenizer.json'
        lines = query_lines(test_file)
        result = [list(key_phrase_tokenizer(line)) for _ln, line in lines]
        check_results(result, expected_file, regen=regen)

    def test_key_phrase_tokenizer_handles_empty_string(self):
        text = ''
        result = list(key_phrase_tokenizer(text))
        assert result == []

    def test_key_phrase_tokenizer_handles_blank_lines(self):
        text = u' \n\n\t  '
        result = list(key_phrase_tokenizer(text))
        assert result == []

    def test_key_phrase_tokenizer_handles_blank_lines2(self):
        text = ' \n\t  '
        result = list(key_phrase_tokenizer(text))
        assert result == []

    def test_key_phrase_tokenizer_handles_empty_lines(self):
        text = u'\n\n'
        expected = []
        assert list(key_phrase_tokenizer(text)) == expected

    def test_key_phrase_tokenizer_does_not_crash_on_unicode_rules_text_1(self):
        test_file = self.get_test_loc('tokenize/unicode/12290.txt')
        with io.open(test_file, encoding='utf-8') as test:
            list(key_phrase_tokenizer(test.read()))

    def test_key_phrase_does_not_crash_on_unicode_rules_text_2(self):
        test_file = self.get_test_loc('tokenize/unicode/12319.txt')
        with io.open(test_file, encoding='utf-8') as test:
            list(key_phrase_tokenizer(test.read()))

    def test_key_phrase_does_not_crash_on_unicode_rules_text_3(self):
        test_file = self.get_test_loc('tokenize/unicode/12405.txt')
        with io.open(test_file, encoding='utf-8') as test:
            list(key_phrase_tokenizer(test.read()))

    def test_key_phrase_does_not_crash_on_unicode_rules_text_4(self):
        test_file = self.get_test_loc('tokenize/unicode/12407.txt')
        with io.open(test_file, encoding='utf-8') as test:
            list(key_phrase_tokenizer(test.read()))

    def test_key_phrase_does_not_crash_on_unicode_rules_text_5(self):
        test_file = self.get_test_loc('tokenize/unicode/12420.txt')
        with io.open(test_file, encoding='utf-8') as test:
            list(key_phrase_tokenizer(test.read()))

    def test_key_phrase_tokenizer_returns_same_word_tokens_as_index_tokenizer(self):
        """
        It is important that the `key_phrase_tokenizer` returns the same amount
        of tokens (excluding key_phrase markup) as the `index_tokenizer` so that
        they Span positions derived from the tokens line up.
        """
        text = 'Redistribution \n\n comma and   use in \n\t binary \xe4r till\xe5tet.'

        key_phrase_tokens = key_phrase_tokenizer(text)
        index_tokens = index_tokenizer(text)

        assert list(key_phrase_tokens) == list(index_tokens)

    def test_key_phrase_tokenizer_returns_key_phrase_markup_as_tokens_for_multiple_token_key_phrases(self):
        text = 'Redistribution and {{use in binary}} is permitted.'
        assert list(key_phrase_tokenizer(text)) == [
            'redistribution', 'and', '{{', 'use', 'in',
            'binary', '}}', 'is', 'permitted',
        ]

    def test_key_phrase_tokenizer_returns_key_phrase_markup_as_tokens_after_newline(self):
        text = '{{IS_RIGHT\nThis program is distributed under GPL\n}}IS_RIGHT'
        assert list(key_phrase_tokenizer(text)) == [
            '{{', 'is', 'right', 'this', 'program', 'is',
            'distributed', 'under', 'gpl', '}}', 'is', 'right'
        ]

    def test_key_phrase_tokenizer_returns_key_phrase_markup_as_tokens_when_separated_by_space(self):
        text = 'Redistribution {{ is }} permitted.'
        assert list(key_phrase_tokenizer(text)) == ['redistribution', '{{', 'is', '}}', 'permitted']

    def test_key_phrase_tokenizer_returns_key_phrase_markup_as_tokens_for_single_token_key_phrase(self):
        text = 'Redistribution {{is}} permitted.'
        assert list(key_phrase_tokenizer(text)) == ['redistribution', '{{', 'is', '}}', 'permitted']

    def test_key_phrase_tokenizer_returns_nested_key_phrase_markup_as_tokens(self):
        text = 'Redistribution {{is {{not}} really}} permitted.'
        assert list(key_phrase_tokenizer(text)) == [
            'redistribution', '{{', 'is', '{{', 'not', '}}',
            'really', '}}', 'permitted'
        ]

    def test_key_phrase_tokenizer_ignores_invalid_key_phrase_markup(self):
        text = 'Redistribution {{{is not really}}} { {permitted} }, I am {afraid}.'
        assert list(key_phrase_tokenizer(text)) == [
            'redistribution', '{{', 'is', 'not', 'really', '}}', 'permitted',
            'i', 'am', 'afraid'
        ]


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
        assert result == expected

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
        assert result == expected

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
        assert result == expected

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

        assert result == expected

    def test_select_ngrams_with_unicode_inputs(self):
        result = list(select_ngrams(x for x in [('b', 'ä', 'c'), ('ä', 'ä', 'c'), ('e', 'ä', 'c'), ('b', 'f', 'ä'), ('g', 'c', 'd')]))
        expected = [('b', 'ä', 'c'), ('ä', 'ä', 'c'), ('e', 'ä', 'c'), ('b', 'f', 'ä'), ('g', 'c', 'd')]
        assert result == expected


class MatchedTextTokenizer(FileBasedTesting):
    test_data_dir = TEST_DATA_DIR

    def test_tokens_and_non_tokens_yield_properly_all_texts(self):
        text = u'''Redistribution+ ;and use in! + 2003 source and +binary forms,
        ()with or without modifi+cation, are permitted with İrəli .\t\n
        \r'''
        result = [m.groupdict() for m in tokens_and_non_tokens(text)]
        expected = [
            {'punct': None, 'token': 'Redistribution+'},
            {'punct': ' ;', 'token': None},
            {'punct': None, 'token': 'and'},
            {'punct': ' ', 'token': None},
            {'punct': None, 'token': 'use'},
            {'punct': ' ', 'token': None},
            {'punct': None, 'token': 'in'},
            {'punct': '! + ', 'token': None},
            {'punct': None, 'token': '2003'},
            {'punct': ' ', 'token': None},
            {'punct': None, 'token': 'source'},
            {'punct': ' ', 'token': None},
            {'punct': None, 'token': 'and'},
            {'punct': ' +', 'token': None},
            {'punct': None, 'token': 'binary'},
            {'punct': ' ', 'token': None},
            {'punct': None, 'token': 'forms'},
            {'punct': ',\n        ()', 'token': None},
            {'punct': None, 'token': 'with'},
            {'punct': ' ', 'token': None},
            {'punct': None, 'token': 'or'},
            {'punct': ' ', 'token': None},
            {'punct': None, 'token': 'without'},
            {'punct': ' ', 'token': None},
            {'punct': None, 'token': 'modifi+cation'},
            {'punct': ', ', 'token': None},
            {'punct': None, 'token': 'are'},
            {'punct': ' ', 'token': None},
            {'punct': None, 'token': 'permitted'},
            {'punct': ' ', 'token': None},
            {'punct': None, 'token': 'with'},
            {'punct': ' ', 'token': None},
            {'punct': None, 'token': 'İrəli'},
            {'punct': ' .\t\n\n        \r', 'token': None}
        ]
        assert result == expected

        result_as_text = u''.join(itertools.chain.from_iterable(
            [v for v in m.groupdict().values() if v] for m in tokens_and_non_tokens(text)))
        assert result_as_text == text

    def test_matched_query_text_tokenizer_works_with_spdx_ids(self):
        text = u''' * SPDX-License-Identifier: GPL-2.0+    BSD-3-Clause
         * SPDX-License-Identifier: (BSD-3-Clause OR EPL-1.0 OR Apache-2.0 OR MIT)
        '''
        result = list(matched_query_text_tokenizer(text))
        expected = [
            (False, u' * '),
            (True, u'SPDX'),
            (False, u'-'),
            (True, u'License'),
            (False, u'-'),
            (True, u'Identifier'),
            (False, u': '),
            (True, u'GPL'),
            (False, u'-'),
            (True, u'2'),
            (False, u'.'),
            (True, u'0+'),
            (False, u'    '),
            (True, u'BSD'),
            (False, u'-'),
            (True, u'3'),
            (False, u'-'),
            (True, u'Clause'),
            (False, u'\n         * '),
            (True, u'SPDX'),
            (False, u'-'),
            (True, u'License'),
            (False, u'-'),
            (True, u'Identifier'),
            (False, u': ('),
            (True, u'BSD'),
            (False, u'-'),
            (True, u'3'),
            (False, u'-'),
            (True, u'Clause'),
            (False, u' '),
            (True, u'OR'),
            (False, u' '),
            (True, u'EPL'),
            (False, u'-'),
            (True, u'1'),
            (False, u'.'),
            (True, u'0'),
            (False, u' '),
            (True, u'OR'),
            (False, u' '),
            (True, u'Apache'),
            (False, u'-'),
            (True, u'2'),
            (False, u'.'),
            (True, u'0'),
            (False, u' '),
            (True, u'OR'),
            (False, u' '),
            (True, u'MIT'),
            (False, u')\n        ')
        ]

        assert result == expected

        result_as_text = u''.join(itertools.chain.from_iterable(
            [v for v in m.groupdict().values() if v] for m in tokens_and_non_tokens(text)))
        assert result_as_text == text

    def test_matched_query_text_tokenizer_and_query_tokenizer_should_yield_the_same_texts(self):
        text = u'''Redistribution+ ;and use in! + 2003 source and +binary forms,
        ()with or without modifi+cation, are permitted with İrəli .\t\n
        \r'''

        mqtt_result = [t for is_tok, t in matched_query_text_tokenizer(text) if is_tok]
        qt_result = list(query_tokenizer(text))
        mqtt_expected = [
            'Redistribution+',
            'and',
            'use',
            'in',
            '2003',
            'source',
            'and',
            'binary',
            'forms',
            'with',
            'or',
            'without',
            'modifi+cation',
            'are',
            'permitted',
            'with',
            'İrəli',
        ]

        qt_expected = [
            'redistribution+',
            'and',
            'use',
            'in',
            '2003',
            'source',
            'and',
            'binary',
            'forms',
            'with',
            'or',
            'without',
            'modifi+cation',
            'are',
            'permitted',
            'with',
            # this is NOT the same as above...
            # See https://github.com/nexB/scancode-toolkit/issues/1872
            'i',
            'rəli'
        ]
        assert mqtt_expected == mqtt_result
        assert qt_expected == qt_result
