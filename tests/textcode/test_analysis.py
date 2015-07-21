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

import json
import os
import codecs
import cPickle
from unittest.case import skipIf

from commoncode.testcase import FileBasedTesting

from textcode.analysis import DEFAULT_GAP
from textcode.analysis import NO_GAP
from textcode.analysis import InvalidGapError
from textcode.analysis import UnbalancedTemplateError

from textcode.analysis import Token

from textcode.analysis import word_splitter
from textcode.analysis import unigram_splitter
from textcode.analysis import unigram_tokenizer
from textcode.analysis import position_processor

from textcode.analysis import template_splitter
from textcode.analysis import template_processor

from textcode.analysis import ngram_to_token
from textcode.analysis import ngram_tokenizer
from textcode.analysis import tokens_ngram_processor

from textcode.analysis import doc_subset
from textcode.analysis import unicode_text_lines
from textcode.analysis import text_lines



#############################################################################
#
# Code style note:  lines are not wrapped to PEP8 line length on purpose
# to keep the tests more readable
#
#############################################################################


class TestDocsubset(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_doc_subset_single_line(self):
        doc = '''A simple test
        with multiple
        lines
        of text
        '''.splitlines()
        pos = Token(start=0, end=0, start_line=1, start_char=8, end_line=1, end_char=21)
        expected = '''with multiple'''

        tst = doc_subset(iter(doc), pos)
        result = '\n'.join(tst)
        assert expected == result

    def test_doc_subset_multilines(self):
        doc = '''0123456789\n0123456789\n'''.splitlines()
        pos = Token(start=0, end=0, start_line=0, start_char=0, end_line=0, end_char=10)
        expected = '0123456789'
        tst = doc_subset(iter(doc), pos)
        result = ''.join(tst)
        assert expected == result

    def test_doc_subset(self):
        doc = iter('''A simple test
        with multiple
        lines
        of text
        '''.splitlines())
        pos = Token(start=3, end=54, start_line=1, start_char=8, end_line=2, end_char=11)
        expected = u'''with multiple
        lin'''
        tst = doc_subset(iter(doc), pos)
        result = u'\n'.join(tst)
        assert expected == result


class TestAnalysis(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_text_lines_from_list_or_location_yield_same_results(self):
        test_file = self.get_test_loc('analysis/bsd-new')
        with open(test_file, 'rb') as inf:
            test_strings_list = inf.read().splitlines(True)

        # test when we are passing a location or a list
        from_loc = list(text_lines(location=test_file))
        from_list = list(text_lines(location=test_strings_list))
        assert from_loc == from_list


class TestUnigrams(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_unigrams_word_splitter_handles_empty_string(self):
        text = iter([''])
        result = list(unigram_splitter(text, splitter=word_splitter))
        assert [] == result

    def test_unigrams_word_splitter_handles_blank_lines(self):
        text = iter([u' ', u'', u'\t  '])
        result = list(unigram_splitter(text, splitter=word_splitter))
        assert [] == result

    def test_unigrams_word_splitter_can_split(self):
        text = iter(u'abc def \n GHI'.splitlines())
        result = list(unigram_splitter(text, splitter=word_splitter))
        expected = [
            Token(start_line=0, end_line=0, start_char=0, end_char=3, value=u'abc'),
            Token(start_line=0, end_line=0, start_char=4, end_char=7, value=u'def'),
            Token(start_line=1, end_line=1, start_char=1, end_char=4, value=u'ghi'),
        ]
        assert expected == result

    def test_unigrams_word_splitter_handles_empty_iterable(self):
        text = iter([])
        result = list(unigram_splitter(text, splitter=word_splitter))
        assert [] == result

    def test_unigrams_template_splitter_handles_empty_string(self):
        text = iter([''])
        result = list(unigram_splitter(text, splitter=template_splitter))
        assert [] == result

    def test_unigrams_template_splitter_handles_blank_lines(self):
        text = iter([' ', '', '\t  '])
        result = list(unigram_splitter(text, splitter=template_splitter))
        assert [] == result

    def test_unigrams_template_splitter_handles_empty_iterable(self):
        text = iter([])
        result = list(unigram_splitter(text, splitter=template_splitter))
        assert [] == result

    def test_unigrams_template_splitter_can_split(self):
        text = iter(u'abc def \n GHI'.splitlines())
        result = list(unigram_splitter(text, splitter=template_splitter))
        assert [u'abc', u'def', u'ghi'] == [x.value for x in result]

    def test_unigrams_template_splitter_can_split_templates(self):
        text = u'abc def \n {{temp}} GHI'.splitlines()
        result = list(unigram_splitter(text, splitter=template_splitter))
        expected = [
            Token(start_line=0, end_line=0, start_char=0, end_char=3, value=u'abc'),
            Token(start_line=0, end_line=0, start_char=4, end_char=7, value=u'def'),
            Token(start_line=1, end_line=1, start_char=1, end_char=3, value=u'{{'),
            Token(start_line=1, end_line=1, start_char=3, end_char=7, value=u'temp'),
            Token(start_line=1, end_line=1, start_char=7, end_char=9, value=u'}}'),
            Token(start_line=1, end_line=1, start_char=10, end_char=13, value=u'ghi'),
        ]
        assert expected == result

    def test_position_processor(self):
        tokens = [
            Token(value=u'abc'),
            Token(value=u'def'),
            Token(value=u'temp'),
            Token(value=u'ghi'),
        ]
        expected = [
            Token(value=u'abc', start=0, end=0),
            Token(value=u'def', start=1, end=1),
            Token(value=u'temp', start=2, end=2),
            Token(value=u'ghi', start=3, end=3),
        ]
        result = list(position_processor(tokens))
        assert expected == result

    def test_unigram_tokenizer(self):
        inp = u'''Redistribution and use in source and binary forms, with or
        without modification, are permitted provided that the following
        conditions are met:
        Redistributions of source code must retain the above
        copyright notice, this list of conditions and the following
        disclaimer.'''

        tst = list(unigram_tokenizer(inp.splitlines(True)))
        assert 39 == len(tst)

        expected = u'''redistribution and use in source and binary forms with or
        without modification are permitted provided that the following
        conditions are met redistributions of source code must retain the above
        copyright notice this list of conditions and the following
        disclaimer'''.split()

        result = [t.value for t in tst]
        assert expected == result



class TestTemplates(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def template_parsing(self, lines):
        if isinstance(lines, basestring):
            lines = lines.splitlines()
        unigrams = unigram_splitter(lines, splitter=template_splitter)
        return list(template_processor(unigrams))

    def test_process_template_handles_empty_templates_using_default_gap(self):
        lines = [u'ab{{}}cd']
        expected = [
            Token(start_line=0, end_line=0, start_char=0, end_char=2, value=u'ab', gap=DEFAULT_GAP),
            Token(start_line=0, end_line=0, start_char=6, end_char=8, value=u'cd', gap=NO_GAP)
        ]
        assert expected == self.template_parsing(lines)

    def test_process_template_recognizes_template_with_gap(self):
        lines = u'ab{{10 nexb Company}}cd'
        expected = [
            Token(start_line=0, end_line=0, start_char=0, end_char=2, value=u'ab', gap=10),
            Token(start_line=0, end_line=0, start_char=21, end_char=23, value=u'cd', gap=NO_GAP)
        ]
        assert expected == self.template_parsing(lines)

    def test_process_template_raise_invalid_gap_exception(self):
        lines = u'ab{{151 nexb Company}}cd'
        self.assertRaises(InvalidGapError, self.template_parsing, lines)

    def test_process_template_recognizes_template_with_maxgap(self):
        lines = u'ab{{150 nexb Company}}cd'
        expected = [
            Token(start_line=0, end_line=0, start_char=0, end_char=2, value=u'ab', gap=150),
            Token(start_line=0, end_line=0, start_char=22, end_char=24, value=u'cd', gap=NO_GAP)
        ]
        assert expected == self.template_parsing(lines)

    def test_process_template_recognizes_template_with_only_gap(self):
        lines = u'ab{{10}}cd'
        expected = [
            Token(start_line=0, end_line=0, start_char=0, end_char=2, value=u'ab', gap=10),
            Token(start_line=0, end_line=0, start_char=8, end_char=10, value=u'cd', gap=NO_GAP)
        ]
        assert expected == self.template_parsing(lines)

    def test_process_template_recognizes_template_with_only_gap_and_spaces(self):
        lines = u'ab{{       10 }}cd'
        expected = [
            Token(start_line=0, end_line=0, start_char=0, end_char=2, value=u'ab', gap=10),
            Token(start_line=0, end_line=0, start_char=16, end_char=18, value=u'cd', gap=NO_GAP)
        ]
        assert expected == self.template_parsing(lines)

    def test_process_template_set_default_gap_if_none_is_specified(self):
        lines = u'ab{{nexb Company}}cd'
        expected = [
            Token(start_line=0, end_line=0, start_char=0, end_char=2, value=u'ab', gap=DEFAULT_GAP),
            Token(start_line=0, end_line=0, start_char=18, end_char=20, value=u'cd', gap=NO_GAP)
        ]
        assert expected == self.template_parsing(lines)

    def test_process_template_set_default_gap_if_none_is_specified_ignoring_spaces(self):
        lines = u'ab{{  \sdsdnexb Companysd }}cd'
        expected = [
            Token(start_line=0, end_line=0, start_char=0, end_char=2, value=u'ab', gap=DEFAULT_GAP),
            Token(start_line=0, end_line=0, start_char=28, end_char=30, value=u'cd', gap=NO_GAP)
        ]
        assert expected == self.template_parsing(lines)

    def test_process_template_can_process_multiple_templatized_regions_with_default_gap(self):
        lines = u'ab{{nexb Company}}cd {{second}}ef'
        expected = [
            Token(start_line=0, end_line=0, start_char=0, end_char=2, value=u'ab', gap=DEFAULT_GAP),
            Token(start_line=0, end_line=0, start_char=18, end_char=20, value=u'cd', gap=DEFAULT_GAP),
            Token(start_line=0, end_line=0, start_char=31, end_char=33, value=u'ef', gap=NO_GAP),
        ]
        assert expected == self.template_parsing(lines)

    def test_process_template_can_process_multiple_templatized_regions_with_default_gap_and_custom_gaps(self):
        lines = u'ab{{nexb Company}}cd{{12 second}}ef{{12 second}}gh'
        expected = [
            Token(start_line=0, end_line=0, start_char=0, end_char=2, value=u'ab', gap=DEFAULT_GAP),
            Token(start_line=0, end_line=0, start_char=18, end_char=20, value=u'cd', gap=12),
            Token(start_line=0, end_line=0, start_char=33, end_char=35, value=u'ef', gap=12),
            Token(start_line=0, end_line=0, start_char=48, end_char=50, value=u'gh', gap=NO_GAP),
        ]
        assert expected == self.template_parsing(lines)

    def test_process_template_handles_combination_of_well_formed_and_ill_formed_templates(self):
        lines = u'ab{{c}}d}}ef'
        expected = [
            Token(start_line=0, end_line=0, start_char=0, end_char=2, value=u'ab', gap=DEFAULT_GAP),
            Token(start_line=0, end_line=0, start_char=7, end_char=8, value=u'd', gap=NO_GAP),
            Token(start_line=0, end_line=0, start_char=10, end_char=12, value=u'ef', gap=NO_GAP),
        ]
        assert expected == self.template_parsing(lines)

    def test_process_template_handles_empty_lines(self):
        lines = u'\n\n'
        expected = []
        assert expected == self.template_parsing(lines)

    def test_process_template_handles_None(self):
        lines = None
        expected = []
        assert expected == self.template_parsing(lines)

    def test_process_template_can_parse_simple_line(self):
        lines = u'Licensed by {{12 nexB}} to you '
        expected = u'licensed by to you'
        result = u' '.join(x.value for x in self.template_parsing(lines))
        assert expected == result

    def test_process_template_does_not_throw_exception_for_illegal_pystache_templates(self):
        lines = u'''Permission to use, copy, modify, and {{ /or : the
                    lines exist without or }} distribute this software...'''
        self.template_parsing(lines)

    def test_process_template_handles_unicode_text_correctly(self):
        expected = [
            Token(start_line=0, end_line=0, start_char=1, end_char=4, value=u'ist', gap=NO_GAP),
            Token(start_line=0, end_line=0, start_char=5, end_char=10, value=u'freie', gap=NO_GAP),
            Token(start_line=0, end_line=0, start_char=11, end_char=19, value=u'software', gap=NO_GAP),
            Token(start_line=0, end_line=0, start_char=21, end_char=24, value=u'sie', gap=NO_GAP),
            Token(start_line=0, end_line=0, start_char=25, end_char=31, value=u'k\xf6nnen', gap=NO_GAP),
            Token(start_line=0, end_line=0, start_char=32, end_char=34, value=u'es', gap=NO_GAP),
            Token(start_line=0, end_line=0, start_char=35, end_char=40, value=u'unter', gap=NO_GAP),
            Token(start_line=0, end_line=0, start_char=41, end_char=44, value=u'den', gap=NO_GAP),
            Token(start_line=0, end_line=0, start_char=45, end_char=56, value=u'bedingungen', gap=NO_GAP),
            Token(start_line=0, end_line=0, start_char=57, end_char=60, value=u'der', gap=NO_GAP),
            Token(start_line=0, end_line=0, start_char=61, end_char=64, value=u'gnu', gap=NO_GAP),
            Token(start_line=1, end_line=1, start_char=1, end_char=8, value=u'general', gap=NO_GAP),
            Token(start_line=1, end_line=1, start_char=10, end_char=11, value=u'n', gap=NO_GAP),
            Token(start_line=2, end_line=2, start_char=1, end_char=7, value=u'public', gap=NO_GAP),
            Token(start_line=2, end_line=2, start_char=8, end_char=15, value=u'license', gap=NO_GAP),
            Token(start_line=2, end_line=2, start_char=17, end_char=20, value=u'wie', gap=NO_GAP),
            Token(start_line=2, end_line=2, start_char=21, end_char=24, value=u'von', gap=NO_GAP),
            Token(start_line=2, end_line=2, start_char=25, end_char=28, value=u'der', gap=NO_GAP),
            Token(start_line=2, end_line=2, start_char=29, end_char=33, value=u'free', gap=NO_GAP),
            Token(start_line=2, end_line=2, start_char=34, end_char=42, value=u'software', gap=NO_GAP),
            Token(start_line=2, end_line=2, start_char=43, end_char=53, value=u'foundation', gap=NO_GAP),
            Token(start_line=2, end_line=2, start_char=54, end_char=68, value=u'ver\xf6ffentlicht', gap=NO_GAP),
            Token(start_line=3, end_line=3, start_char=1, end_char=12, value=u'weitergeben', gap=NO_GAP),
            Token(start_line=3, end_line=3, start_char=13, end_char=16, value=u'und', gap=NO_GAP),
            Token(start_line=3, end_line=3, start_char=17, end_char=21, value=u'oder', gap=NO_GAP),
            Token(start_line=3, end_line=3, start_char=23, end_char=24, value=u'n', gap=NO_GAP),
            Token(start_line=4, end_line=4, start_char=1, end_char=13, value=u'modifizieren', gap=NO_GAP),
            Token(start_line=4, end_line=4, start_char=15, end_char=23, value=u'entweder', gap=NO_GAP),
            Token(start_line=4, end_line=4, start_char=24, end_char=29, value=u'gem\xe4\xdf', gap=NO_GAP),
            Token(start_line=4, end_line=4, start_char=30, end_char=37, value=u'version', gap=NO_GAP),
            Token(start_line=4, end_line=4, start_char=38, end_char=39, value=u'3', gap=NO_GAP),
            Token(start_line=4, end_line=4, start_char=40, end_char=43, value=u'der', gap=NO_GAP),
            Token(start_line=4, end_line=4, start_char=44, end_char=50, value=u'lizenz', gap=NO_GAP),
            Token(start_line=4, end_line=4, start_char=51, end_char=55, value=u'oder', gap=NO_GAP),
            Token(start_line=4, end_line=4, start_char=57, end_char=61, value=u'nach', gap=NO_GAP),
            Token(start_line=4, end_line=4, start_char=62, end_char=67, value=u'ihrer', gap=NO_GAP),
            Token(start_line=4, end_line=4, start_char=68, end_char=74, value=u'option', gap=NO_GAP),
            Token(start_line=5, end_line=5, start_char=1, end_char=6, value=u'jeder', gap=NO_GAP),
            Token(start_line=5, end_line=5, start_char=7, end_char=15, value=u'sp\xe4teren', gap=NO_GAP),
            Token(start_line=5, end_line=5, start_char=17, end_char=18, value=u'n', gap=NO_GAP),
            Token(start_line=6, end_line=6, start_char=1, end_char=8, value=u'version', gap=NO_GAP),
            Token(start_line=6, end_line=6, start_char=10, end_char=11, value=u'n', gap=NO_GAP),
            Token(start_line=7, end_line=7, start_char=2, end_char=3, value=u'n', gap=NO_GAP),
            Token(start_line=8, end_line=8, start_char=1, end_char=4, value=u'die', gap=NO_GAP),
            Token(start_line=8, end_line=8, start_char=5, end_char=21, value=u'ver\xf6ffentlichung', gap=NO_GAP),
            Token(start_line=8, end_line=8, start_char=22, end_char=25, value=u'von', gap=DEFAULT_GAP),
            Token(start_line=8, end_line=8, start_char=38, end_char=45, value=u'erfolgt', gap=NO_GAP),
            Token(start_line=8, end_line=8, start_char=46, end_char=48, value=u'in', gap=NO_GAP),
            Token(start_line=8, end_line=8, start_char=49, end_char=52, value=u'der', gap=NO_GAP),
            Token(start_line=8, end_line=8, start_char=53, end_char=61, value=u'hoffnung', gap=NO_GAP),
            Token(start_line=8, end_line=8, start_char=63, end_char=66, value=u'da\xdf', gap=NO_GAP),
            Token(start_line=8, end_line=8, start_char=67, end_char=69, value=u'es', gap=NO_GAP),
            Token(start_line=8, end_line=8, start_char=70, end_char=75, value=u'ihnen', gap=NO_GAP),
            Token(start_line=8, end_line=8, start_char=76, end_char=79, value=u'von', gap=NO_GAP),
            Token(start_line=9, end_line=9, start_char=1, end_char=7, value=u'nutzen', gap=NO_GAP),
            Token(start_line=9, end_line=9, start_char=9, end_char=10, value=u'n', gap=NO_GAP),
            Token(start_line=10, end_line=10, start_char=1, end_char=5, value=u'sein', gap=NO_GAP),
            Token(start_line=10, end_line=10, start_char=6, end_char=10, value=u'wird', gap=NO_GAP),
            Token(start_line=10, end_line=10, start_char=12, end_char=16, value=u'aber', gap=NO_GAP),
            Token(start_line=10, end_line=10, start_char=17, end_char=21, value=u'ohne', gap=NO_GAP),
            Token(start_line=10, end_line=10, start_char=22, end_char=32, value=u'irgendeine', gap=NO_GAP),
            Token(start_line=10, end_line=10, start_char=33, end_char=41, value=u'garantie', gap=NO_GAP),
            Token(start_line=10, end_line=10, start_char=43, end_char=48, value=u'sogar', gap=NO_GAP),
            Token(start_line=10, end_line=10, start_char=49, end_char=53, value=u'ohne', gap=NO_GAP),
            Token(start_line=10, end_line=10, start_char=54, end_char=57, value=u'die', gap=NO_GAP),
            Token(start_line=10, end_line=10, start_char=58, end_char=67, value=u'implizite', gap=NO_GAP),
            Token(start_line=10, end_line=10, start_char=68, end_char=76, value=u'garantie', gap=NO_GAP),
            Token(start_line=11, end_line=11, start_char=1, end_char=4, value=u'der', gap=NO_GAP),
            Token(start_line=11, end_line=11, start_char=5, end_char=15, value=u'marktreife', gap=NO_GAP),
            Token(start_line=11, end_line=11, start_char=17, end_char=18, value=u'n', gap=NO_GAP),
            Token(start_line=12, end_line=12, start_char=1, end_char=5, value=u'oder', gap=NO_GAP),
            Token(start_line=12, end_line=12, start_char=6, end_char=9, value=u'der', gap=NO_GAP),
            Token(start_line=12, end_line=12, start_char=10, end_char=24, value=u'verwendbarkeit', gap=NO_GAP),
            Token(start_line=12, end_line=12, start_char=25, end_char=28, value=u'f\xfcr', gap=NO_GAP),
            Token(start_line=12, end_line=12, start_char=29, end_char=34, value=u'einen', gap=NO_GAP),
            Token(start_line=12, end_line=12, start_char=35, end_char=45, value=u'bestimmten', gap=NO_GAP),
            Token(start_line=12, end_line=12, start_char=46, end_char=51, value=u'zweck', gap=NO_GAP),
            Token(start_line=12, end_line=12, start_char=53, end_char=60, value=u'details', gap=NO_GAP),
            Token(start_line=12, end_line=12, start_char=61, end_char=67, value=u'finden', gap=NO_GAP),
            Token(start_line=12, end_line=12, start_char=68, end_char=71, value=u'sie', gap=NO_GAP),
            Token(start_line=12, end_line=12, start_char=72, end_char=74, value=u'in', gap=NO_GAP),
            Token(start_line=13, end_line=13, start_char=1, end_char=4, value=u'der', gap=NO_GAP),
            Token(start_line=13, end_line=13, start_char=5, end_char=8, value=u'gnu', gap=NO_GAP),
            Token(start_line=13, end_line=13, start_char=9, end_char=16, value=u'general', gap=NO_GAP),
            Token(start_line=13, end_line=13, start_char=18, end_char=19, value=u'n', gap=NO_GAP),
            Token(start_line=14, end_line=14, start_char=1, end_char=7, value=u'public', gap=NO_GAP),
            Token(start_line=14, end_line=14, start_char=8, end_char=15, value=u'license', gap=NO_GAP),
            Token(start_line=14, end_line=14, start_char=17, end_char=18, value=u'n', gap=NO_GAP),
            Token(start_line=15, end_line=15, start_char=2, end_char=3, value=u'n', gap=NO_GAP),
            Token(start_line=16, end_line=16, start_char=1, end_char=4, value=u'sie', gap=NO_GAP),
            Token(start_line=16, end_line=16, start_char=5, end_char=12, value=u'sollten', gap=NO_GAP),
            Token(start_line=16, end_line=16, start_char=13, end_char=16, value=u'ein', gap=NO_GAP),
            Token(start_line=16, end_line=16, start_char=17, end_char=25, value=u'exemplar', gap=NO_GAP),
            Token(start_line=16, end_line=16, start_char=26, end_char=29, value=u'der', gap=NO_GAP),
            Token(start_line=16, end_line=16, start_char=30, end_char=33, value=u'gnu', gap=NO_GAP),
            Token(start_line=16, end_line=16, start_char=34, end_char=41, value=u'general', gap=NO_GAP),
            Token(start_line=16, end_line=16, start_char=42, end_char=48, value=u'public', gap=NO_GAP),
            Token(start_line=16, end_line=16, start_char=49, end_char=56, value=u'license', gap=NO_GAP),
            Token(start_line=16, end_line=16, start_char=57, end_char=65, value=u'zusammen', gap=NO_GAP),
            Token(start_line=16, end_line=16, start_char=66, end_char=69, value=u'mit', gap=DEFAULT_GAP),
            Token(start_line=17, end_line=17, start_char=2, end_char=3, value=u'n', gap=NO_GAP),
            Token(start_line=18, end_line=18, start_char=1, end_char=9, value=u'erhalten', gap=NO_GAP),
            Token(start_line=18, end_line=18, start_char=10, end_char=15, value=u'haben', gap=NO_GAP),
            Token(start_line=18, end_line=18, start_char=17, end_char=22, value=u'falls', gap=NO_GAP),
            Token(start_line=18, end_line=18, start_char=23, end_char=28, value=u'nicht', gap=NO_GAP),
            Token(start_line=18, end_line=18, start_char=30, end_char=39, value=u'schreiben', gap=NO_GAP),
            Token(start_line=18, end_line=18, start_char=40, end_char=43, value=u'sie', gap=NO_GAP),
            Token(start_line=18, end_line=18, start_char=44, end_char=46, value=u'an', gap=NO_GAP),
            Token(start_line=18, end_line=18, start_char=47, end_char=50, value=u'die', gap=NO_GAP),
            Token(start_line=18, end_line=18, start_char=51, end_char=55, value=u'free', gap=NO_GAP),
            Token(start_line=18, end_line=18, start_char=56, end_char=64, value=u'software', gap=NO_GAP),
            Token(start_line=18, end_line=18, start_char=65, end_char=75, value=u'foundation', gap=NO_GAP),
            Token(start_line=19, end_line=19, start_char=2, end_char=3, value=u'n', gap=NO_GAP),
            Token(start_line=20, end_line=20, start_char=1, end_char=4, value=u'inc', gap=NO_GAP),
            Token(start_line=20, end_line=20, start_char=7, end_char=9, value=u'51', gap=NO_GAP),
            Token(start_line=20, end_line=20, start_char=10, end_char=18, value=u'franklin', gap=NO_GAP),
            Token(start_line=20, end_line=20, start_char=19, end_char=21, value=u'st', gap=NO_GAP),
            Token(start_line=20, end_line=20, start_char=23, end_char=28, value=u'fifth', gap=NO_GAP),
            Token(start_line=20, end_line=20, start_char=29, end_char=34, value=u'floor', gap=NO_GAP),
            Token(start_line=20, end_line=20, start_char=36, end_char=42, value=u'boston', gap=NO_GAP),
            Token(start_line=20, end_line=20, start_char=44, end_char=46, value=u'ma', gap=NO_GAP),
            Token(start_line=20, end_line=20, start_char=47, end_char=52, value=u'02110', gap=NO_GAP),
            Token(start_line=20, end_line=20, start_char=54, end_char=57, value=u'usa', gap=NO_GAP),
        ]

        test_file = self.get_test_loc('analysis/unicode/12180.atxt')
        with codecs.open(test_file, encoding='utf-8') as test:
            lines = test.read().splitlines()
            result = list(self.template_parsing(lines))
            assert expected == result

    def test_process_template_can_handle_long_text(self):
        expected = [
            Token(start_line=0, end_line=0, start_char=14, end_char=17, value=u'ist', gap=NO_GAP),
            Token(start_line=0, end_line=0, start_char=18, end_char=23, value=u'freie', gap=NO_GAP),
            Token(start_line=0, end_line=0, start_char=24, end_char=32, value=u'software', gap=NO_GAP),
            Token(start_line=0, end_line=0, start_char=34, end_char=37, value=u'sie', gap=NO_GAP),
            Token(start_line=0, end_line=0, start_char=38, end_char=44, value=u'k\xf6nnen', gap=NO_GAP),
            Token(start_line=0, end_line=0, start_char=45, end_char=47, value=u'es', gap=NO_GAP),
            Token(start_line=0, end_line=0, start_char=48, end_char=53, value=u'unter', gap=NO_GAP),
            Token(start_line=0, end_line=0, start_char=54, end_char=57, value=u'den', gap=NO_GAP),
            Token(start_line=0, end_line=0, start_char=58, end_char=69, value=u'bedingungen', gap=NO_GAP),
            Token(start_line=0, end_line=0, start_char=70, end_char=73, value=u'der', gap=NO_GAP),
            Token(start_line=0, end_line=0, start_char=74, end_char=77, value=u'gnu', gap=NO_GAP),
            Token(start_line=1, end_line=1, start_char=1, end_char=8, value=u'general', gap=NO_GAP),
            Token(start_line=1, end_line=1, start_char=10, end_char=11, value=u'n', gap=NO_GAP),
            Token(start_line=2, end_line=2, start_char=1, end_char=7, value=u'public', gap=NO_GAP),
            Token(start_line=2, end_line=2, start_char=8, end_char=15, value=u'license', gap=NO_GAP),
            Token(start_line=2, end_line=2, start_char=17, end_char=20, value=u'wie', gap=NO_GAP),
            Token(start_line=2, end_line=2, start_char=21, end_char=24, value=u'von', gap=NO_GAP),
            Token(start_line=2, end_line=2, start_char=25, end_char=28, value=u'der', gap=NO_GAP),
            Token(start_line=2, end_line=2, start_char=29, end_char=33, value=u'free', gap=NO_GAP),
            Token(start_line=2, end_line=2, start_char=34, end_char=42, value=u'software', gap=NO_GAP),
            Token(start_line=2, end_line=2, start_char=43, end_char=53, value=u'foundation', gap=NO_GAP),
            Token(start_line=2, end_line=2, start_char=54, end_char=68, value=u'ver\xf6ffentlicht', gap=NO_GAP),
            Token(start_line=3, end_line=3, start_char=1, end_char=12, value=u'weitergeben', gap=NO_GAP),
            Token(start_line=3, end_line=3, start_char=13, end_char=16, value=u'und', gap=NO_GAP),
            Token(start_line=3, end_line=3, start_char=17, end_char=21, value=u'oder', gap=NO_GAP),
            Token(start_line=3, end_line=3, start_char=23, end_char=24, value=u'n', gap=NO_GAP),
            Token(start_line=4, end_line=4, start_char=1, end_char=13, value=u'modifizieren', gap=NO_GAP),
            Token(start_line=4, end_line=4, start_char=15, end_char=23, value=u'entweder', gap=NO_GAP),
            Token(start_line=4, end_line=4, start_char=24, end_char=29, value=u'gem\xe4\xdf', gap=NO_GAP),
            Token(start_line=4, end_line=4, start_char=30, end_char=37, value=u'version', gap=NO_GAP),
            Token(start_line=4, end_line=4, start_char=38, end_char=39, value=u'3', gap=NO_GAP),
            Token(start_line=4, end_line=4, start_char=40, end_char=43, value=u'der', gap=NO_GAP),
            Token(start_line=4, end_line=4, start_char=44, end_char=50, value=u'lizenz', gap=NO_GAP),
            Token(start_line=4, end_line=4, start_char=51, end_char=55, value=u'oder', gap=NO_GAP),
            Token(start_line=4, end_line=4, start_char=57, end_char=61, value=u'nach', gap=NO_GAP),
            Token(start_line=4, end_line=4, start_char=62, end_char=67, value=u'ihrer', gap=NO_GAP),
            Token(start_line=4, end_line=4, start_char=68, end_char=74, value=u'option', gap=NO_GAP),
            Token(start_line=5, end_line=5, start_char=1, end_char=6, value=u'jeder', gap=NO_GAP),
            Token(start_line=5, end_line=5, start_char=7, end_char=15, value=u'sp\xe4teren', gap=NO_GAP),
            Token(start_line=5, end_line=5, start_char=17, end_char=18, value=u'n', gap=NO_GAP),
            Token(start_line=6, end_line=6, start_char=1, end_char=8, value=u'version', gap=NO_GAP),
            Token(start_line=6, end_line=6, start_char=10, end_char=11, value=u'n', gap=NO_GAP),
            Token(start_line=7, end_line=7, start_char=2, end_char=3, value=u'n', gap=NO_GAP),
            Token(start_line=8, end_line=8, start_char=1, end_char=4, value=u'die', gap=NO_GAP),
            Token(start_line=8, end_line=8, start_char=5, end_char=21, value=u'ver\xf6ffentlichung', gap=NO_GAP),
            Token(start_line=8, end_line=8, start_char=22, end_char=25, value=u'von', gap=DEFAULT_GAP),
            Token(start_line=8, end_line=8, start_char=38, end_char=45, value=u'erfolgt', gap=NO_GAP),
            Token(start_line=8, end_line=8, start_char=46, end_char=48, value=u'in', gap=NO_GAP),
            Token(start_line=8, end_line=8, start_char=49, end_char=52, value=u'der', gap=NO_GAP),
            Token(start_line=8, end_line=8, start_char=53, end_char=61, value=u'hoffnung', gap=NO_GAP),
            Token(start_line=8, end_line=8, start_char=63, end_char=66, value=u'da\xdf', gap=NO_GAP),
            Token(start_line=8, end_line=8, start_char=67, end_char=69, value=u'es', gap=NO_GAP),
            Token(start_line=8, end_line=8, start_char=70, end_char=75, value=u'ihnen', gap=NO_GAP),
            Token(start_line=8, end_line=8, start_char=76, end_char=79, value=u'von', gap=NO_GAP),
            Token(start_line=9, end_line=9, start_char=1, end_char=7, value=u'nutzen', gap=NO_GAP),
            Token(start_line=9, end_line=9, start_char=9, end_char=10, value=u'n', gap=NO_GAP),
            Token(start_line=10, end_line=10, start_char=1, end_char=5, value=u'sein', gap=NO_GAP),
            Token(start_line=10, end_line=10, start_char=6, end_char=10, value=u'wird', gap=NO_GAP),
            Token(start_line=10, end_line=10, start_char=12, end_char=16, value=u'aber', gap=NO_GAP),
            Token(start_line=10, end_line=10, start_char=17, end_char=21, value=u'ohne', gap=NO_GAP),
            Token(start_line=10, end_line=10, start_char=22, end_char=32, value=u'irgendeine', gap=NO_GAP),
            Token(start_line=10, end_line=10, start_char=33, end_char=41, value=u'garantie', gap=NO_GAP),
            Token(start_line=10, end_line=10, start_char=43, end_char=48, value=u'sogar', gap=NO_GAP),
            Token(start_line=10, end_line=10, start_char=49, end_char=53, value=u'ohne', gap=NO_GAP),
            Token(start_line=10, end_line=10, start_char=54, end_char=57, value=u'die', gap=NO_GAP),
            Token(start_line=10, end_line=10, start_char=58, end_char=67, value=u'implizite', gap=NO_GAP),
            Token(start_line=10, end_line=10, start_char=68, end_char=76, value=u'garantie', gap=NO_GAP),
            Token(start_line=11, end_line=11, start_char=1, end_char=4, value=u'der', gap=NO_GAP),
            Token(start_line=11, end_line=11, start_char=5, end_char=15, value=u'marktreife', gap=NO_GAP),
            Token(start_line=11, end_line=11, start_char=17, end_char=18, value=u'n', gap=NO_GAP),
            Token(start_line=12, end_line=12, start_char=1, end_char=5, value=u'oder', gap=NO_GAP),
            Token(start_line=12, end_line=12, start_char=6, end_char=9, value=u'der', gap=NO_GAP),
            Token(start_line=12, end_line=12, start_char=10, end_char=24, value=u'verwendbarkeit', gap=NO_GAP),
            Token(start_line=12, end_line=12, start_char=25, end_char=28, value=u'f\xfcr', gap=NO_GAP),
            Token(start_line=12, end_line=12, start_char=29, end_char=34, value=u'einen', gap=NO_GAP),
            Token(start_line=12, end_line=12, start_char=35, end_char=45, value=u'bestimmten', gap=NO_GAP),
            Token(start_line=12, end_line=12, start_char=46, end_char=51, value=u'zweck', gap=NO_GAP),
            Token(start_line=12, end_line=12, start_char=53, end_char=60, value=u'details', gap=NO_GAP),
            Token(start_line=12, end_line=12, start_char=61, end_char=67, value=u'finden', gap=NO_GAP),
            Token(start_line=12, end_line=12, start_char=68, end_char=71, value=u'sie', gap=NO_GAP),
            Token(start_line=12, end_line=12, start_char=72, end_char=74, value=u'in', gap=NO_GAP),
            Token(start_line=13, end_line=13, start_char=1, end_char=4, value=u'der', gap=NO_GAP),
            Token(start_line=13, end_line=13, start_char=5, end_char=8, value=u'gnu', gap=NO_GAP),
            Token(start_line=13, end_line=13, start_char=9, end_char=16, value=u'general', gap=NO_GAP),
            Token(start_line=13, end_line=13, start_char=18, end_char=19, value=u'n', gap=NO_GAP),
            Token(start_line=14, end_line=14, start_char=1, end_char=7, value=u'public', gap=NO_GAP),
            Token(start_line=14, end_line=14, start_char=8, end_char=15, value=u'license', gap=NO_GAP),
            Token(start_line=14, end_line=14, start_char=17, end_char=18, value=u'n', gap=NO_GAP),
            Token(start_line=15, end_line=15, start_char=2, end_char=3, value=u'n', gap=NO_GAP),
            Token(start_line=16, end_line=16, start_char=1, end_char=4, value=u'sie', gap=NO_GAP),
            Token(start_line=16, end_line=16, start_char=5, end_char=12, value=u'sollten', gap=NO_GAP),
            Token(start_line=16, end_line=16, start_char=13, end_char=16, value=u'ein', gap=NO_GAP),
            Token(start_line=16, end_line=16, start_char=17, end_char=25, value=u'exemplar', gap=NO_GAP),
            Token(start_line=16, end_line=16, start_char=26, end_char=29, value=u'der', gap=NO_GAP),
            Token(start_line=16, end_line=16, start_char=30, end_char=33, value=u'gnu', gap=NO_GAP),
            Token(start_line=16, end_line=16, start_char=34, end_char=41, value=u'general', gap=NO_GAP),
            Token(start_line=16, end_line=16, start_char=42, end_char=48, value=u'public', gap=NO_GAP),
            Token(start_line=16, end_line=16, start_char=49, end_char=56, value=u'license', gap=NO_GAP),
            Token(start_line=16, end_line=16, start_char=57, end_char=65, value=u'zusammen', gap=NO_GAP),
            Token(start_line=16, end_line=16, start_char=66, end_char=69, value=u'mit', gap=DEFAULT_GAP),
            Token(start_line=17, end_line=17, start_char=2, end_char=3, value=u'n', gap=NO_GAP),
            Token(start_line=18, end_line=18, start_char=1, end_char=9, value=u'erhalten', gap=NO_GAP),
            Token(start_line=18, end_line=18, start_char=10, end_char=15, value=u'haben', gap=NO_GAP),
            Token(start_line=18, end_line=18, start_char=17, end_char=22, value=u'falls', gap=NO_GAP),
            Token(start_line=18, end_line=18, start_char=23, end_char=28, value=u'nicht', gap=NO_GAP),
            Token(start_line=18, end_line=18, start_char=30, end_char=39, value=u'schreiben', gap=NO_GAP),
            Token(start_line=18, end_line=18, start_char=40, end_char=43, value=u'sie', gap=NO_GAP),
            Token(start_line=18, end_line=18, start_char=44, end_char=46, value=u'an', gap=NO_GAP),
            Token(start_line=18, end_line=18, start_char=47, end_char=50, value=u'die', gap=NO_GAP),
            Token(start_line=18, end_line=18, start_char=51, end_char=55, value=u'free', gap=NO_GAP),
            Token(start_line=18, end_line=18, start_char=56, end_char=64, value=u'software', gap=NO_GAP),
            Token(start_line=18, end_line=18, start_char=65, end_char=75, value=u'foundation', gap=NO_GAP),
            Token(start_line=19, end_line=19, start_char=2, end_char=3, value=u'n', gap=NO_GAP),
            Token(start_line=20, end_line=20, start_char=1, end_char=4, value=u'inc', gap=NO_GAP),
            Token(start_line=20, end_line=20, start_char=7, end_char=9, value=u'51', gap=NO_GAP),
            Token(start_line=20, end_line=20, start_char=10, end_char=18, value=u'franklin', gap=NO_GAP),
            Token(start_line=20, end_line=20, start_char=19, end_char=21, value=u'st', gap=NO_GAP),
            Token(start_line=20, end_line=20, start_char=23, end_char=28, value=u'fifth', gap=NO_GAP),
            Token(start_line=20, end_line=20, start_char=29, end_char=34, value=u'floor', gap=NO_GAP),
            Token(start_line=20, end_line=20, start_char=36, end_char=42, value=u'boston', gap=NO_GAP),
            Token(start_line=20, end_line=20, start_char=44, end_char=46, value=u'ma', gap=NO_GAP),
            Token(start_line=20, end_line=20, start_char=47, end_char=52, value=u'02110', gap=NO_GAP),
            Token(start_line=20, end_line=20, start_char=54, end_char=57, value=u'usa', gap=NO_GAP),
        ]
        test_file = self.get_test_loc('analysis/unicode/12180.txt')
        with codecs.open(test_file, encoding='utf-8') as test:
            result = list(self.template_parsing(test))
            assert expected == result

    def test_process_template_does_not_crash_on_unicode_rules_text_1(self):
        test_file = self.get_test_loc('analysis/unicode/12290.txt')
        with codecs.open(test_file, encoding='utf-8') as test:
            list(self.template_parsing(test))

    def test_process_template_does_not_crash_on_unicode_rules_text_2(self):
        test_file = self.get_test_loc('analysis/unicode/12319.txt')
        with codecs.open(test_file, encoding='utf-8') as test:
            list(self.template_parsing(test))

    def test_process_template_does_not_crash_on_unicode_rules_text_3(self):
        test_file = self.get_test_loc('analysis/unicode/12405.txt')
        with codecs.open(test_file, encoding='utf-8') as test:
            list(self.template_parsing(test))

    def test_process_template_does_not_crash_on_unicode_rules_text_4(self):
        test_file = self.get_test_loc('analysis/unicode/12407.txt')
        with codecs.open(test_file, encoding='utf-8') as test:
            list(self.template_parsing(test))

    def test_process_template_does_not_crash_on_unicode_rules_text_5(self):
        test_file = self.get_test_loc('analysis/unicode/12420.txt')
        with codecs.open(test_file, encoding='utf-8') as test:
            list(self.template_parsing(test))

    def test_process_template_detects_non_well_formed_templatized_regions(self):
        lines = u'abcd{{ef'
        self.assertRaises(UnbalancedTemplateError, self.template_parsing, lines)

    def test_process_template_handles_combination_of_well_formed_and_ill_formed_templates_2(self):
        lines = u'}}{{{{abc}}ddd}}{{'
        self.assertRaises(UnbalancedTemplateError, self.template_parsing, lines)

    def test_process_template_can_parse_ill_formed_template(self):
        tf = self.get_test_loc('analysis/ill_formed_template/text.txt')
        lines = unicode_text_lines(tf)
        result = list(self.template_parsing(lines))
        expected_gaps = [30, 10, 60, 70, 20]
        result_gaps = [x.gap for x in result if x.gap]
        assert expected_gaps == result_gaps

        et = self.get_test_loc('analysis/ill_formed_template/expected_grams.json')
        result_dicts = [t._asdict() for t in result]
        regen = False
        if regen:
            with codecs.open(et, 'w', encoding='utf-8') as out:
                json.dump(result_dicts, out, indent=2)
        with codecs.open(et, encoding='utf-8') as inp:
            expected = json.load(inp)
        assert expected == result_dicts

    def test_token_positions_are_kept_same_for_unigrams_and_ngrams_with_template(self):
        lines = u'some text is some text {{ }} in all cases\n \n'
        unigrams = unigram_tokenizer(iter([lines]), template=False)
        tunigrams = unigram_tokenizer(iter([lines]), template=True)
        ngrams = ngram_tokenizer(iter([lines]), ngram_len=3, template=False)
        tngrams = ngram_tokenizer(iter([lines]), ngram_len=3, template=True)
        expected_start_end = (0, 7,)

        def check_start_end(l):
            l = list(l)
            result = (l[0].start, l[-1].end,)
            assert expected_start_end == result

        check_start_end(unigrams)
        check_start_end(tunigrams)

        check_start_end(ngrams)
        check_start_end(tngrams)

    def test_plain_unigrams_from_templated_unigrams(self):
        lines = [u'My old tailor {{3 John Doe}} is quite very rich']
        unigrams = unigram_splitter(lines, splitter=template_splitter)
        result = list(template_processor(unigrams))
        expected = [
            Token(start=0, start_line=0, start_char=0, end_line=0, end_char=2, end=0, gap=0, value=u'my'),
            Token(start=0, start_line=0, start_char=3, end_line=0, end_char=6, end=0, gap=0, value=u'old'),
            Token(start=0, start_line=0, start_char=7, end_line=0, end_char=13, end=0, gap=3, value=u'tailor'),
            Token(start=0, start_line=0, start_char=29, end_line=0, end_char=31, end=0, gap=0, value=u'is'),
            Token(start=0, start_line=0, start_char=32, end_line=0, end_char=37, end=0, gap=0, value=u'quite'),
            Token(start=0, start_line=0, start_char=38, end_line=0, end_char=42, end=0, gap=0, value=u'very'),
            Token(start=0, start_line=0, start_char=43, end_line=0, end_char=47, end=0, gap=0, value=u'rich'),
        ]
        assert expected == result


class TestLegacyNgrams(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_plain_ngrams_processor(self):
        from collections import deque
        def ngram_processor(items, ngram_len):
            """
            Given a sequence or iterable of arbitrary items, return an iterator of
            item ngrams tuples of length ngram_len. Buffers at most ngram_len iterable
            items.

            For example::

            >>> list(ngram_processor([1, 2, 3, 4, 5], ngram_len=3))
            [(1, 2, 3), (2, 3, 4), (3, 4, 5)]
            """
            ngram = deque()
            current_len = 0
            for item in items:
                if current_len == ngram_len:
                    yield tuple(ngram)
                    ngram.popleft()
                    current_len -= 1
                ngram.append(item)
                current_len += 1
            yield tuple(ngram)

        text = (
            u'''/*COMMENT
            COMMENT COMMENT
            - COMMENT
            */
            public static boolean activateSearchResultView() {
            String defaultPerspectiveId= SearchUI.getDefaultPerspectiveId();
            if (defaultPerspectiveId != null) {
                IWorkbenchWindow window= SearchPlugin.getActiveWorkbenchWindow();
                if (window != null && window.getShell() != null && !window.getShell().isDisposed()) {
                    try {
                        PlatformUI.getWorkbench().showPerspective(defaultPerspectiveId, window);
                    } catch (WorkbenchException ex) {
                        // show view in current perspective
                    }
                }
            }''')

        expected = [
            (u'comment', u'comment', u'comment', u'comment', u'public', u'static'),
            (u'comment', u'comment', u'comment', u'public', u'static', u'boolean'),
            (u'comment', u'comment', u'public', u'static', u'boolean',
             u'activatesearchresultview'),
            (u'comment', u'public', u'static', u'boolean',
             u'activatesearchresultview', u'string'),
            (u'public', u'static', u'boolean', u'activatesearchresultview',
            u'string', u'defaultperspectiveid'),
            (u'static', u'boolean', u'activatesearchresultview', u'string',
            u'defaultperspectiveid', u'searchui'),
            (u'boolean', u'activatesearchresultview', u'string',
             u'defaultperspectiveid', u'searchui', u'getdefaultperspectiveid'),
            (u'activatesearchresultview', u'string', u'defaultperspectiveid',
             u'searchui', u'getdefaultperspectiveid', u'if'),
            (u'string', u'defaultperspectiveid', u'searchui',
             u'getdefaultperspectiveid', u'if', u'defaultperspectiveid'),
            (u'defaultperspectiveid', u'searchui', u'getdefaultperspectiveid',
             u'if', u'defaultperspectiveid', u'null'),
            (u'searchui', u'getdefaultperspectiveid', u'if',
             u'defaultperspectiveid', u'null', u'iworkbenchwindow'),
            (u'getdefaultperspectiveid', u'if', u'defaultperspectiveid', u'null',
             u'iworkbenchwindow', u'window'),
            (u'if', u'defaultperspectiveid', u'null', u'iworkbenchwindow',
             u'window', u'searchplugin'),
            (u'defaultperspectiveid', u'null', u'iworkbenchwindow', u'window',
             u'searchplugin', u'getactiveworkbenchwindow'),
            (u'null', u'iworkbenchwindow', u'window', u'searchplugin',
             u'getactiveworkbenchwindow', u'if'),
            (u'iworkbenchwindow', u'window', u'searchplugin',
             u'getactiveworkbenchwindow', u'if', u'window'),
            (u'window', u'searchplugin', u'getactiveworkbenchwindow', u'if',
             u'window', u'null'),
            (u'searchplugin', u'getactiveworkbenchwindow', u'if', u'window',
             u'null', u'window'),
            (u'getactiveworkbenchwindow', u'if', u'window', u'null', u'window',
             u'getshell'),
            (u'if', u'window', u'null', u'window', u'getshell', u'null'),
            (u'window', u'null', u'window', u'getshell', u'null', u'window'),
            (u'null', u'window', u'getshell', u'null', u'window', u'getshell'),
            (u'window', u'getshell', u'null', u'window', u'getshell', u'isdisposed'),
            (u'getshell', u'null', u'window', u'getshell', u'isdisposed', u'try'),
            (u'null', u'window', u'getshell', u'isdisposed', u'try', u'platformui'),
            (u'window', u'getshell', u'isdisposed', u'try', u'platformui',
             u'getworkbench'),
            (u'getshell', u'isdisposed', u'try', u'platformui', u'getworkbench',
             u'showperspective'),
            (u'isdisposed', u'try', u'platformui', u'getworkbench',
             u'showperspective', u'defaultperspectiveid'),
            (u'try', u'platformui', u'getworkbench', u'showperspective',
             u'defaultperspectiveid', u'window'),
            (u'platformui', u'getworkbench', u'showperspective',
             u'defaultperspectiveid', u'window', u'catch'),
            (u'getworkbench', u'showperspective', u'defaultperspectiveid',
             u'window', u'catch', u'workbenchexception'),
            (u'showperspective', u'defaultperspectiveid', u'window', u'catch',
             u'workbenchexception', u'ex'),
            (u'defaultperspectiveid', u'window', u'catch', u'workbenchexception',
             u'ex', u'show'),
            (u'window', u'catch', u'workbenchexception', u'ex', u'show', u'view'),
            (u'catch', u'workbenchexception', u'ex', u'show', u'view', u'in'),
            (u'workbenchexception', u'ex', u'show', u'view', u'in', u'current'),
            (u'ex', u'show', u'view', u'in', u'current', u'perspective'),
        ]
        unigrams = (x.value for x
                    in unigram_splitter(text.splitlines()))
        result = list(ngram_processor(unigrams, ngram_len=6))
        assert expected == result


class TestNgrams(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_tokens_ngram_processor_bigrams_from_unigrams(self):
        text = u'this is some text \n on multiple lines'
        unigrams = unigram_splitter(text.splitlines())
        result = list(tokens_ngram_processor(unigrams, ngram_len=2))
        expected = [
            (Token(start_line=0, start_char=0, end_line=0, end_char=4, value=u'this'),
             Token(start_line=0, start_char=5, end_line=0, end_char=7, value=u'is')),

            (Token(start_line=0, start_char=5, end_line=0, end_char=7, value=u'is'),
             Token(start_line=0, start_char=8, end_line=0, end_char=12, value=u'some')),

            (Token(start_line=0, start_char=8, end_line=0, end_char=12, value=u'some'),
             Token(start_line=0, start_char=13, end_line=0, end_char=17, value=u'text')),

            (Token(start_line=0, start_char=13, end_line=0, end_char=17, value=u'text'),
             Token(start_line=1, start_char=1, end_line=1, end_char=3, value=u'on')),

            (Token(start_line=1, start_char=1, end_line=1, end_char=3, value=u'on'),
             Token(start_line=1, start_char=4, end_line=1, end_char=12, value=u'multiple')),

            (Token(start_line=1, start_char=4, end_line=1, end_char=12, value=u'multiple'),
             Token(start_line=1, start_char=13, end_line=1, end_char=18, value=u'lines'))
        ]
        assert expected == result

    def test_tokens_ngram_processor_n2_with_2_tokens(self):
        text = u'this is'
        unigrams = list(unigram_splitter(text.splitlines()))
        expected = [
            (Token(start_line=0, start_char=0, end_line=0, end_char=4, value=u'this'),
             Token(start_line=0, start_char=5, end_line=0, end_char=7, value=u'is')),
        ]
        result = list(tokens_ngram_processor(iter(unigrams), ngram_len=2))
        assert expected == result

    def test_tokens_ngram_processor_n3_with_2_tokens(self):
        text = u'this is'
        unigrams = list(unigram_splitter(text.splitlines()))
        expected = [
            (Token(start_line=0, start_char=0, end_line=0, end_char=4, value=u'this'),
             Token(start_line=0, start_char=5, end_line=0, end_char=7, value=u'is')),
        ]
        result = list(tokens_ngram_processor(iter(unigrams), ngram_len=3))
        assert expected == result

    def test_tokens_ngram_processor_n4_with_2_tokens(self):
        text = u'this is'
        unigrams = list(unigram_splitter(text.splitlines()))
        expected = [
            (Token(start_line=0, start_char=0, end_line=0, end_char=4, value=u'this'),
             Token(start_line=0, start_char=5, end_line=0, end_char=7, value=u'is')),
        ]
        result = list(tokens_ngram_processor(iter(unigrams), ngram_len=4))
        assert expected == result

    def test_tokens_ngram_processor_n10_with_2_tokens(self):
        text = u'this is'
        unigrams = list(unigram_splitter(text.splitlines()))
        expected = [
            (Token(start_line=0, start_char=0, end_line=0, end_char=4, value=u'this'),
             Token(start_line=0, start_char=5, end_line=0, end_char=7, value=u'is')),
        ]
        result = list(tokens_ngram_processor(iter(unigrams), ngram_len=10))
        assert expected == result

    def test_tokens_ngram_processor_n1_with_2_tokens(self):
        text = u'this is'
        unigrams = list(unigram_splitter(text.splitlines()))
        expected = [
            (Token(start_line=0, start_char=0, end_line=0, end_char=4, value=u'this'),),
            (Token(start_line=0, start_char=5, end_line=0, end_char=7, value=u'is'),),
        ]
        result = list(tokens_ngram_processor(iter(unigrams), ngram_len=1))
        assert expected == result

    def test_tokens_ngram_processor_3grams_from_unigrams_on_multilines(self):
        text = u'this is some text \n on multiple lines'
        unigrams = unigram_splitter(text.splitlines())
        result = list(tokens_ngram_processor(unigrams, ngram_len=3))
        expected = [
            (Token(start_line=0, start_char=0, end_line=0, end_char=4, value=u'this'),
             Token(start_line=0, start_char=5, end_line=0, end_char=7, value=u'is'),
             Token(start_line=0, start_char=8, end_line=0, end_char=12, value=u'some')),

            (Token(start_line=0, start_char=5, end_line=0, end_char=7, value=u'is'),
             Token(start_line=0, start_char=8, end_line=0, end_char=12, value=u'some'),
             Token(start_line=0, start_char=13, end_line=0, end_char=17, value=u'text')),

            (Token(start_line=0, start_char=8, end_line=0, end_char=12, value=u'some'),
             Token(start_line=0, start_char=13, end_line=0, end_char=17, value=u'text'),
             Token(start_line=1, start_char=1, end_line=1, end_char=3, value=u'on')),

            (Token(start_line=0, start_char=13, end_line=0, end_char=17, value=u'text'),
             Token(start_line=1, start_char=1, end_line=1, end_char=3, value=u'on'),
             Token(start_line=1, start_char=4, end_line=1, end_char=12, value=u'multiple')),

            (Token(start_line=1, start_char=1, end_line=1, end_char=3, value=u'on'),
             Token(start_line=1, start_char=4, end_line=1, end_char=12, value=u'multiple'),
             Token(start_line=1, start_char=13, end_line=1, end_char=18, value=u'lines'))
        ]
        assert expected == result

    def test_tokens_ngram_processor_with_template_gaps_basic(self):
        lines = [u'My old {{3 John Doe}} is rich']
        unigrams = unigram_splitter(lines, splitter=template_splitter)
        templated = template_processor(unigrams)
        result = list(tokens_ngram_processor(templated, ngram_len=3))
        expected = [
            (Token(start=0, start_line=0, start_char=0, end_line=0, end_char=2, end=0, gap=0, value=u'my'),
             Token(start=0, start_line=0, start_char=3, end_line=0, end_char=6, end=0, gap=3, value=u'old'),
            ),
            (Token(start=0, start_line=0, start_char=22, end_line=0, end_char=24, end=0, gap=0, value=u'is'),
             Token(start=0, start_line=0, start_char=25, end_line=0, end_char=29, end=0, gap=0, value=u'rich'),
            )
        ]
        assert expected == result

    def test_tokens_ngram_processor_with_template_gaps_merged(self):
        lines = [u'My old tailor {{3 John Doe}} is quite very rich']
        unigrams = unigram_splitter(lines, splitter=template_splitter)
        templated = template_processor(unigrams)
        ngram_len = 3
        ngrams_tuples = tokens_ngram_processor(templated, ngram_len=ngram_len)
        result = list(ngram_to_token(ngrams_tuples))
        expected = [
            Token(start_line=0, start_char=0, end_line=0, end_char=13, gap=ngram_len, value=(u'my', u'old', u'tailor')),
            Token(start_line=0, start_char=29, end_line=0, end_char=42, gap=0, value=(u'is', u'quite', u'very')),
            Token(start_line=0, start_char=32, end_line=0, end_char=47, gap=0, value=(u'quite', u'very', u'rich')),
        ]
        assert expected == result

    def test_tokens_ngram_processor_with_gaps_merged_short_grams(self):
        lines = [u'My {{3 tailor Joe}} is quite {{ pleasant and }} very rich']
        unigrams = unigram_splitter(lines, splitter=template_splitter)
        templated = template_processor(unigrams)
        ngram_len = 3
        ngrams_tuples = tokens_ngram_processor(templated, ngram_len=ngram_len)
        result = list(ngram_to_token(ngrams_tuples))
        expected = [
            Token(start=0, start_line=0, start_char=0, end_line=0, end_char=2, end=0, gap=3, value=(u'my',)),
            Token(start=0, start_line=0, start_char=20, end_line=0, end_char=28, end=0, gap=5, value=(u'is', u'quite')),
            Token(start=0, start_line=0, start_char=48, end_line=0, end_char=57, end=0, gap=0, value=(u'very', u'rich'))
        ]
        assert expected == result

    def test_tokens_ngram_processor_with_gaps_merged_short_and_long_grams(self):
        lines = [u'My {{3 tailor Joe}} is quite {{ pleasant and }} very rich really rich']
        unigrams = unigram_splitter(lines, splitter=template_splitter)
        templated = template_processor(unigrams)
        ngram_len = 3
        ngrams_tuples = tokens_ngram_processor(templated, ngram_len=ngram_len)
        result = list(ngram_to_token(ngrams_tuples))
        expected = [
            Token(start=0, start_line=0, start_char=0, end_line=0, end_char=2, end=0, gap=3, value=(u'my',)),
            Token(start=0, start_line=0, start_char=20, end_line=0, end_char=28, end=0, gap=5, value=(u'is', u'quite')),
            Token(start=0, start_line=0, start_char=48, end_line=0, end_char=64, end=0, gap=0, value=(u'very', u'rich', u'really')),
            Token(start=0, start_line=0, start_char=53, end_line=0, end_char=69, end=0, gap=0, value=(u'rich', u'really', u'rich'))
        ]
        assert expected == result

    def test_ngram_to_token_processor_with_gaps_at_the_end(self):
        lines = [u'My {{3 tailor Joe}} is quite {{ pleasant and }}']
        unigrams = unigram_splitter(lines, splitter=template_splitter)
        templated = template_processor(unigrams)
        ngram_len = 3
        ngrams_tuples = tokens_ngram_processor(templated, ngram_len=ngram_len)
        result = list(ngram_to_token(ngrams_tuples))
        expected = [
            Token(start=0, start_line=0, start_char=0, end_line=0, end_char=2, end=0, gap=3, value=(u'my',)),
            Token(start=0, start_line=0, start_char=20, end_line=0, end_char=28, end=0, gap=5, value=(u'is', u'quite'))
        ]
        assert expected == result

    def test_tokens_ngram_processor_with_gaps_at_the_end_does_yield_empty_tuples(self):
        lines = [u'My {{3 tailor Joe}} is quite {{ pleasant and }}']
        unigrams = unigram_splitter(lines, splitter=template_splitter)
        templated = template_processor(unigrams)
        ngram_len = 3
        result = list(tokens_ngram_processor(templated, ngram_len=ngram_len))
        assert (None, None, None,) != result[-1]
        expected = [
            (Token(start=0, start_line=0, start_char=0, end_line=0, end_char=2, end=0, gap=3, value=u'my'),),
            (Token(start=0, start_line=0, start_char=20, end_line=0, end_char=22, end=0, gap=0, value=u'is'),
             Token(start=0, start_line=0, start_char=23, end_line=0, end_char=28, end=0, gap=5, value=u'quite'),
            )
        ]
        assert expected == result

    def test_ngrams_tokenizer_does_not_yield_4grams_for_3grams(self):
        lines = u'''Neither the name of {{10 the ORGANIZATION}} nor {{}}the names {{}}of its contributors may
                materials provided with the distribution.'''.splitlines()
        result = list(ngram_tokenizer(iter(lines), ngram_len=3, template=True))
        expected = [
            Token(start=0, start_line=0, start_char=0, end_line=0, end_char=16, end=2, gap=0, value=(u'neither', u'the', u'name')),
            Token(start=1, start_line=0, start_char=8, end_line=0, end_char=19, end=3, gap=10, value=(u'the', u'name', u'of')),
            Token(start=4, start_line=0, start_char=44, end_line=0, end_char=47, end=4, gap=5, value=(u'nor',)),
            Token(start=5, start_line=0, start_char=52, end_line=0, end_char=61, end=6, gap=5, value=(u'the', u'names')),
            Token(start=7, start_line=0, start_char=66, end_line=0, end_char=85, end=9, gap=0, value=(u'of', u'its', u'contributors')),
            Token(start=8, start_line=0, start_char=69, end_line=0, end_char=89, end=10, gap=0, value=(u'its', u'contributors', u'may')),
            Token(start=9, start_line=0, start_char=73, end_line=1, end_char=25, end=11, gap=0, value=(u'contributors', u'may', u'materials')),
            Token(start=10, start_line=0, start_char=86, end_line=1, end_char=34, end=12, gap=0, value=(u'may', u'materials', u'provided')),
            Token(start=11, start_line=1, start_char=16, end_line=1, end_char=39, end=13, gap=0, value=(u'materials', u'provided', u'with')),
            Token(start=12, start_line=1, start_char=26, end_line=1, end_char=43, end=14, gap=0, value=(u'provided', u'with', u'the')),
            Token(start=13, start_line=1, start_char=35, end_line=1, end_char=56, end=15, gap=0, value=(u'with', u'the', u'distribution'))
        ]
        assert expected == result

    def test_tokens_ngram_processor_with_gaps_merged_always_returns_3grams_when_requested(self):
        lines = u'''Neither the name of {{10 the ORGANIZATION}} nor {{}}the
                   names {{}}of its contributors may materials provided with
                   the distribution.'''.splitlines()
        unigrams = unigram_splitter(lines, splitter=template_splitter)
        templated = template_processor(unigrams)
        result = list(tokens_ngram_processor(templated, ngram_len=3))
        expected = [
            (Token(start=0, start_line=0, start_char=0, end_line=0, end_char=7, end=0, gap=0, value=u'neither'),
             Token(start=0, start_line=0, start_char=8, end_line=0, end_char=11, end=0, gap=0, value=u'the'),
             Token(start=0, start_line=0, start_char=12, end_line=0, end_char=16, end=0, gap=0, value=u'name')),
            (Token(start=0, start_line=0, start_char=8, end_line=0, end_char=11, end=0, gap=0, value=u'the'),
             Token(start=0, start_line=0, start_char=12, end_line=0, end_char=16, end=0, gap=0, value=u'name'),
             Token(start=0, start_line=0, start_char=17, end_line=0, end_char=19, end=0, gap=10, value=u'of')),
            (Token(start=0, start_line=0, start_char=44, end_line=0, end_char=47, end=0, gap=5, value=u'nor'),),
            (Token(start=0, start_line=0, start_char=52, end_line=0, end_char=55, end=0, gap=0, value=u'the'),
             Token(start=0, start_line=1, start_char=19, end_line=1, end_char=24, end=0, gap=5, value=u'names')),
            (Token(start=0, start_line=1, start_char=29, end_line=1, end_char=31, end=0, gap=0, value=u'of'),
             Token(start=0, start_line=1, start_char=32, end_line=1, end_char=35, end=0, gap=0, value=u'its'),
             Token(start=0, start_line=1, start_char=36, end_line=1, end_char=48, end=0, gap=0, value=u'contributors')),
            (Token(start=0, start_line=1, start_char=32, end_line=1, end_char=35, end=0, gap=0, value=u'its'),
             Token(start=0, start_line=1, start_char=36, end_line=1, end_char=48, end=0, gap=0, value=u'contributors'),
             Token(start=0, start_line=1, start_char=49, end_line=1, end_char=52, end=0, gap=0, value=u'may')),
            (Token(start=0, start_line=1, start_char=36, end_line=1, end_char=48, end=0, gap=0, value=u'contributors'),
             Token(start=0, start_line=1, start_char=49, end_line=1, end_char=52, end=0, gap=0, value=u'may'),
             Token(start=0, start_line=1, start_char=53, end_line=1, end_char=62, end=0, gap=0, value=u'materials')),
            (Token(start=0, start_line=1, start_char=49, end_line=1, end_char=52, end=0, gap=0, value=u'may'),
             Token(start=0, start_line=1, start_char=53, end_line=1, end_char=62, end=0, gap=0, value=u'materials'),
             Token(start=0, start_line=1, start_char=63, end_line=1, end_char=71, end=0, gap=0, value=u'provided')),
            (Token(start=0, start_line=1, start_char=53, end_line=1, end_char=62, end=0, gap=0, value=u'materials'),
             Token(start=0, start_line=1, start_char=63, end_line=1, end_char=71, end=0, gap=0, value=u'provided'),
             Token(start=0, start_line=1, start_char=72, end_line=1, end_char=76, end=0, gap=0, value=u'with')),
            (Token(start=0, start_line=1, start_char=63, end_line=1, end_char=71, end=0, gap=0, value=u'provided'),
             Token(start=0, start_line=1, start_char=72, end_line=1, end_char=76, end=0, gap=0, value=u'with'),
             Token(start=0, start_line=2, start_char=19, end_line=2, end_char=22, end=0, gap=0, value=u'the')),
            (Token(start=0, start_line=1, start_char=72, end_line=1, end_char=76, end=0, gap=0, value=u'with'),
             Token(start=0, start_line=2, start_char=19, end_line=2, end_char=22, end=0, gap=0, value=u'the'),
             Token(start=0, start_line=2, start_char=23, end_line=2, end_char=35, end=0, gap=0, value=u'distribution'))
        ]
        assert expected == result

    def test_tokens_ngram_processor_with_gaps_merged_always_returns_4grams_when_requested(self):
        lines = u'''Neither the name of {{10 the ORGANIZATION}} nor {{}}the
                   names {{}}of its contributors may materials provided with
                   the distribution.'''.splitlines()
        unigrams = unigram_splitter(lines, splitter=template_splitter)
        templated = template_processor(unigrams)
        result = list(tokens_ngram_processor(templated, ngram_len=4))
        expected = [
            (Token(start=0, start_line=0, start_char=0, end_line=0, end_char=7, end=0, gap=0, value=u'neither'),
             Token(start=0, start_line=0, start_char=8, end_line=0, end_char=11, end=0, gap=0, value=u'the'),
             Token(start=0, start_line=0, start_char=12, end_line=0, end_char=16, end=0, gap=0, value=u'name'),
             Token(start=0, start_line=0, start_char=17, end_line=0, end_char=19, end=0, gap=10, value=u'of')),
            (Token(start=0, start_line=0, start_char=44, end_line=0, end_char=47, end=0, gap=5, value=u'nor'),),
            (Token(start=0, start_line=0, start_char=52, end_line=0, end_char=55, end=0, gap=0, value=u'the'),
             Token(start=0, start_line=1, start_char=19, end_line=1, end_char=24, end=0, gap=5, value=u'names')),
            (Token(start=0, start_line=1, start_char=29, end_line=1, end_char=31, end=0, gap=0, value=u'of'),
             Token(start=0, start_line=1, start_char=32, end_line=1, end_char=35, end=0, gap=0, value=u'its'),
             Token(start=0, start_line=1, start_char=36, end_line=1, end_char=48, end=0, gap=0, value=u'contributors'),
             Token(start=0, start_line=1, start_char=49, end_line=1, end_char=52, end=0, gap=0, value=u'may')),
            (Token(start=0, start_line=1, start_char=32, end_line=1, end_char=35, end=0, gap=0, value=u'its'),
             Token(start=0, start_line=1, start_char=36, end_line=1, end_char=48, end=0, gap=0, value=u'contributors'),
             Token(start=0, start_line=1, start_char=49, end_line=1, end_char=52, end=0, gap=0, value=u'may'),
             Token(start=0, start_line=1, start_char=53, end_line=1, end_char=62, end=0, gap=0, value=u'materials')),
            (Token(start=0, start_line=1, start_char=36, end_line=1, end_char=48, end=0, gap=0, value=u'contributors'),
             Token(start=0, start_line=1, start_char=49, end_line=1, end_char=52, end=0, gap=0, value=u'may'),
             Token(start=0, start_line=1, start_char=53, end_line=1, end_char=62, end=0, gap=0, value=u'materials'),
             Token(start=0, start_line=1, start_char=63, end_line=1, end_char=71, end=0, gap=0, value=u'provided')),
            (Token(start=0, start_line=1, start_char=49, end_line=1, end_char=52, end=0, gap=0, value=u'may'),
             Token(start=0, start_line=1, start_char=53, end_line=1, end_char=62, end=0, gap=0, value=u'materials'),
             Token(start=0, start_line=1, start_char=63, end_line=1, end_char=71, end=0, gap=0, value=u'provided'),
             Token(start=0, start_line=1, start_char=72, end_line=1, end_char=76, end=0, gap=0, value=u'with')),
            (Token(start=0, start_line=1, start_char=53, end_line=1, end_char=62, end=0, gap=0, value=u'materials'),
             Token(start=0, start_line=1, start_char=63, end_line=1, end_char=71, end=0, gap=0, value=u'provided'),
             Token(start=0, start_line=1, start_char=72, end_line=1, end_char=76, end=0, gap=0, value=u'with'),
             Token(start=0, start_line=2, start_char=19, end_line=2, end_char=22, end=0, gap=0, value=u'the')),
            (Token(start=0, start_line=1, start_char=63, end_line=1, end_char=71, end=0, gap=0, value=u'provided'),
             Token(start=0, start_line=1, start_char=72, end_line=1, end_char=76, end=0, gap=0, value=u'with'),
             Token(start=0, start_line=2, start_char=19, end_line=2, end_char=22, end=0, gap=0, value=u'the'),
             Token(start=0, start_line=2, start_char=23, end_line=2, end_char=35, end=0, gap=0, value=u'distribution'))
        ]
        assert expected == result

    def test_tokens_ngram_processor_with_gaps_can_handle_contiguous_template_regions(self):
        lines = u'''Neither the name of {{10 the ORGANIZATION}} nor {{}}
                   {{6 }}of its contributors may materials provided with the
                   distribution.'''.splitlines()
        unigrams = unigram_splitter(lines, splitter=template_splitter)
        templated = template_processor(unigrams)
        result = list(tokens_ngram_processor(templated, ngram_len=4))
        expected = [
            (Token(start=0, start_line=0, start_char=0, end_line=0, end_char=7, end=0, gap=0, value=u'neither'),
             Token(start=0, start_line=0, start_char=8, end_line=0, end_char=11, end=0, gap=0, value=u'the'),
             Token(start=0, start_line=0, start_char=12, end_line=0, end_char=16, end=0, gap=0, value=u'name'),
             Token(start=0, start_line=0, start_char=17, end_line=0, end_char=19, end=0, gap=10, value=u'of')),
            (Token(start=0, start_line=0, start_char=44, end_line=0, end_char=47, end=0, gap=5, value=u'nor'),),
            (Token(start=0, start_line=1, start_char=25, end_line=1, end_char=27, end=0, gap=0, value=u'of'),
             Token(start=0, start_line=1, start_char=28, end_line=1, end_char=31, end=0, gap=0, value=u'its'),
             Token(start=0, start_line=1, start_char=32, end_line=1, end_char=44, end=0, gap=0, value=u'contributors'),
             Token(start=0, start_line=1, start_char=45, end_line=1, end_char=48, end=0, gap=0, value=u'may')),
            (Token(start=0, start_line=1, start_char=28, end_line=1, end_char=31, end=0, gap=0, value=u'its'),
             Token(start=0, start_line=1, start_char=32, end_line=1, end_char=44, end=0, gap=0, value=u'contributors'),
             Token(start=0, start_line=1, start_char=45, end_line=1, end_char=48, end=0, gap=0, value=u'may'),
             Token(start=0, start_line=1, start_char=49, end_line=1, end_char=58, end=0, gap=0, value=u'materials')),
            (Token(start=0, start_line=1, start_char=32, end_line=1, end_char=44, end=0, gap=0, value=u'contributors'),
             Token(start=0, start_line=1, start_char=45, end_line=1, end_char=48, end=0, gap=0, value=u'may'),
             Token(start=0, start_line=1, start_char=49, end_line=1, end_char=58, end=0, gap=0, value=u'materials'),
             Token(start=0, start_line=1, start_char=59, end_line=1, end_char=67, end=0, gap=0, value=u'provided')),
            (Token(start=0, start_line=1, start_char=45, end_line=1, end_char=48, end=0, gap=0, value=u'may'),
             Token(start=0, start_line=1, start_char=49, end_line=1, end_char=58, end=0, gap=0, value=u'materials'),
             Token(start=0, start_line=1, start_char=59, end_line=1, end_char=67, end=0, gap=0, value=u'provided'),
             Token(start=0, start_line=1, start_char=68, end_line=1, end_char=72, end=0, gap=0, value=u'with')),
            (Token(start=0, start_line=1, start_char=49, end_line=1, end_char=58, end=0, gap=0, value=u'materials'),
             Token(start=0, start_line=1, start_char=59, end_line=1, end_char=67, end=0, gap=0, value=u'provided'),
             Token(start=0, start_line=1, start_char=68, end_line=1, end_char=72, end=0, gap=0, value=u'with'),
             Token(start=0, start_line=1, start_char=73, end_line=1, end_char=76, end=0, gap=0, value=u'the')),
            (Token(start=0, start_line=1, start_char=59, end_line=1, end_char=67, end=0, gap=0, value=u'provided'),
             Token(start=0, start_line=1, start_char=68, end_line=1, end_char=72, end=0, gap=0, value=u'with'),
             Token(start=0, start_line=1, start_char=73, end_line=1, end_char=76, end=0, gap=0, value=u'the'),
             Token(start=0, start_line=2, start_char=19, end_line=2, end_char=31, end=0, gap=0, value=u'distribution'))
        ]
        assert expected == result

    def test_ngram_tokenizer_can_handle_gaps_at_end_of_text(self):
        lines = [u'Neither the name of {{10 the ORGANIZATION}} ']
        ngram_len = 2
        result = list(ngram_tokenizer(lines, ngram_len, template=True))
        expected = [
            Token(start=0, start_line=0, start_char=0, end_line=0, end_char=11, end=1, gap=0, value=(u'neither', u'the')),
            Token(start=1, start_line=0, start_char=8, end_line=0, end_char=16, end=2, gap=0, value=(u'the', u'name')),
            Token(start=2, start_line=0, start_char=12, end_line=0, end_char=19, end=3, gap=10, value=(u'name', u'of'))
        ]
        assert expected == result

    def test_ngram_tokenizer_returns_correct_offsets_n3(self):
        lines = [u'X11 License']
        ngram_len = 3
        result = list(ngram_tokenizer(lines, ngram_len))
        assert lines == list(doc_subset(lines, result[0]))

        expected = [Token(start=0, start_line=0, start_char=0, end_line=0, end_char=11, end=1, gap=0, value=(u'x11', u'license'))]
        assert expected == result

    def test_ngram_tokenizer_returns_correct_offsets_n1(self):
        lines = [u'X11 License']
        ngram_len = 1
        result = list(ngram_tokenizer(lines, ngram_len))
        expected = [
            Token(start=0, start_line=0, start_char=0, end_line=0, end_char=3, end=0, gap=0, value=(u'x11',)),
            Token(start=1, start_line=0, start_char=4, end_line=0, end_char=11, end=1, gap=0, value=(u'license',)),
        ]
        assert expected == result

    def test_ngram_tokenizer_returns_correct_offsets_template(self):
        lines = [u'X11 License']
        ngram_len = 3
        result = list(ngram_tokenizer(lines, ngram_len, template=True))
        assert lines == list(doc_subset(lines, result[0]))

        expected = [Token(start=0, start_line=0, start_char=0, end_line=0, end_char=11, end=1, gap=0, value=(u'x11', u'license'))]
        assert expected == result

    def test_unicode_text_lines_handles_weird_xml_encodings(self):
        test_file = self.get_test_loc('analysis/weird_encoding/easyconf-0.9.0.pom')
        result = list(unicode_text_lines(test_file))
        expected_file = self.get_test_loc('analysis/weird_encoding/easyconf-0.9.0.pom.expected')
        with open(expected_file, 'rb') as tf:
            expected = cPickle.load(tf)
        assert expected == result


class TestMultigrams(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')
    # TODO: add more tests beyond the simple doctests that exist in the code


@skipIf(True, 'Performance tests only')
class TestAnalysisPerformance(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_splitter_perf(self):
        test_file = self.get_test_loc('perf/test.txt')
        text = open(test_file).read() * 100
        utext = unicode(text)
        setup1 = '''
import re
from textcode import analysis

unicode_ws = analysis.word_splitter
plain_ws =re.compile(r'[^\W_]+').finditer
unicode_ts = analysis.template_splitter
plain_ts= re.compile(r'(?:[^\W_])+|(?:\{\{)|(?:\}\})').finditer

text = %r
utext = %r''' % (text, utext)
        def check_perf(setup):
            from timeit import timeit
            stmt = 'list(w for w in %s(%s))'
            print()
            print('Unicode template')
            print(timeit(stmt % ('unicode_ts', 'utext'), setup=setup, number=1000))
            print('Plain template')
            print(timeit(stmt % ('plain_ts', 'text'), setup=setup, number=1000))
            print('Unicode words')
            print(timeit(stmt % ('unicode_ws', 'utext'), setup=setup, number=1000))
            print('Plain words')
            print(timeit(stmt % ('plain_ws', 'text'), setup=setup, number=1000))
            print('Plain split')
            print(timeit('text.split()', setup=setup, number=1000))
            print('Unicode split')
            print(timeit('utext.split()', setup=setup, number=1000))
            print('Line split')
            print(timeit('text.splitlines(False)', setup=setup, number=1000))
            print('Line split with ends')
            print(timeit('text.splitlines(True)', setup=setup, number=1000))

        check_perf(setup=setup1)
        setup2 = '''
import re
from textcode import analysis

unicode_ws = analysis.word_splitter
plain_ws =re.compile(r'[^\W_]+').finditer
unicode_ts = analysis.template_splitter
plain_ts= re.compile(r'(?:[^\W_])+|(?:\{\{)|(?:\}\})').finditer

text = %r
utext = %r''' % (text, utext)
        check_perf(setup=setup2)
