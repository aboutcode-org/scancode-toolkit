#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
from unittest import TestCase as TestCaseClass

import pytest

from licensedcode.required_phrases import get_required_phrases
from licensedcode.required_phrases import get_required_phrase_spans
from licensedcode.required_phrases import get_required_phrase_texts
from licensedcode.required_phrases import add_required_phrases_from_other_rules
from licensedcode.required_phrases import add_required_phrases_from_license_fields
from licensedcode.required_phrases import ListOfRequiredPhrases
from licensedcode.required_phrases import RequiredPhraseDetails
from licensedcode.required_phrases import return_spans_for_required_phrase_in_text
from licensedcode.required_phrases import add_required_phrase_markers
from licensedcode.tokenize import get_normalized_tokens
from licensedcode.tokenize import matched_query_text_tokenizer
from licensedcode.stopwords import STOPWORDS
from licensedcode.models import InvalidRule
from licensedcode.models import Rule
from licensedcode.spans import Span


class TestGetKeyPhrases(TestCaseClass):
    text = (
        'This released software is {{released}} by under {{the MIT license}}. '
        'Which is a license originating at Massachusetts Institute of Technology (MIT).'
    )

    def test_get_required_phrases_yields_spans(self):
        required_phrase_spans = get_required_phrase_spans(self.text)
        assert required_phrase_spans == [Span(4), Span(7, 9)]

    def test_get_required_phrases_yields_tokens(self):
        required_phrase_tokens = [
            required_phrase.required_phrase_tokens
            for required_phrase in get_required_phrases(text=self.text)
        ]
        assert required_phrase_tokens == [['released'], ['the', 'mit', 'license']]

    def test_get_required_phrase_texts(self):
        required_phrase_texts = get_required_phrase_texts(text=self.text)
        assert required_phrase_texts == ['released', 'the mit license']

    def test_get_required_phrases_raises_exception_required_phrase_markup_is_not_closed(self):
        text = 'This software is {{released by under the MIT license.'
        try:
            list(get_required_phrase_spans(text))
            raise Exception('Exception should be raised')
        except InvalidRule:
            pass

    def test_get_required_phrases_ignores_stopwords_in_positions(self):
        text = 'The word comma is a stop word so comma does not increase the span position {{MIT license}}.'
        required_phrase_spans = get_required_phrase_spans(text)
        assert required_phrase_spans == [Span(11, 12)]

    def test_get_required_phrases_yields_spans_without_stop_words(self):
        text = 'This released software is {{released span}} by under {{the MIT quot license}}.'
        required_phrase_spans = get_required_phrase_spans(text)
        assert required_phrase_spans == [Span(4), Span(7, 9)]

    def test_get_required_phrases_does_not_yield_empty_spans(self):
        text = 'This released software {{comma}} is {{}} by under {{the MIT license}}.'
        try:
            list(get_required_phrase_spans(text))
            raise Exception('Exception should be raised')
        except InvalidRule:
            pass

    def test_get_required_phrases_only_considers_outer_required_phrase_markup(self):
        text = 'This released {{{software under the MIT}}} license.'
        required_phrase_spans = get_required_phrase_spans(text)
        assert required_phrase_spans == [Span(2, 5)]

    def test_get_required_phrases_ignores_nested_required_phrase_markup(self):
        text = 'This released {{software {{under the}} MIT}} license.'
        try:
            list(get_required_phrase_spans(text))
            raise Exception('Exception should be raised')
        except InvalidRule:
            pass

    def test_get_required_phrase_texts_with_markup(self):
        text = (
            "Lua is free software distributed under the terms of the"
            "<A HREF='http://www.opensource.org/licenses/mit-license.html'>{{MIT license}}</A>"
            "reproduced below;"
        )
        required_phrase_texts = get_required_phrase_texts(text=text)
        assert required_phrase_texts == ['mit license']

    def test_get_required_phrase_spans_with_markup(self):
        text = (
            "Lua is free software distributed under the terms of the"
            "<A HREF='http://www.opensource.org/licenses/mit-license.html'>{{MIT license}}</A>"
            "reproduced below;"
        )
        required_phrase_spans = get_required_phrase_spans(text=text)
        assert required_phrase_spans == [Span(18, 19)]


class TestListOfRequiredPhrases(TestCaseClass):

    required_phrase_texts = [
        "mit",
        "the MIT License",
        "MIT License with Disclaimer",
        "licenses: mit",
        "MIT license",
    ]
    required_phrases = [
        RequiredPhraseDetails(
            required_phrase_text=text,
            license_expression="mit",
            length=len(text),
            rule=Rule(
                license_expression="mit",
                identifier="mit_231.RULE",
                text=text,
                is_required_phrase=True,
                is_license_tag=True,
            ),
            sources=["mit_231.RULE"],
        )
        for text in required_phrase_texts
    ]
    required_phrases_list = ListOfRequiredPhrases(required_phrases=required_phrases)

    def test_sort_required_phrases_works(self):
        self.required_phrases_list.sort_required_phrases()
        expected_sorted_texts = [
            "MIT License with Disclaimer",
            "the MIT License",
            "licenses: mit",
            "MIT license",
            "mit",
        ]
        assert [
            required_phrase.required_phrase_text
            for required_phrase in self.required_phrases_list.required_phrases
        ] == expected_sorted_texts


class TestRequiredPhraseSpansinText:

    text_with_stopwords = (
        "A copy of the GNU General Public License is available as "
        "/usr/share/common-licenses/GPL-2 in the Debian GNU/Linux distribution. "
        "A copy of the GNU General Public License is available as "
        "/usr/share/common-licenses/GPL-2 in the Debian GNU/Linux distribution."
    )

    text_with_stopwords_and_marked_required_phrases = (
        "A copy of the GNU General Public License is available as "
        "/{{usr/share/common-licenses/GPL-2}} in the Debian GNU/Linux distribution. "
        "A copy of the GNU General Public License is available as "
        "/{{usr/share/common-licenses/GPL-2}} in the Debian GNU/Linux distribution."
    )

    def test_get_required_phrase_spans_with_or_without_specified_texts_is_same(self):
        required_phrase_spans_specified = return_spans_for_required_phrase_in_text(
            text=self.text_with_stopwords,
            required_phrase="usr share common licenses gpl 2",
        )

        required_phrase_spans_unspecified = get_required_phrase_spans(
            text=self.text_with_stopwords_and_marked_required_phrases,
        )
        assert required_phrase_spans_specified == required_phrase_spans_unspecified

    def test_get_required_phrase_and_add_required_phrase_matches(self):

        required_phrase_spans_specified = return_spans_for_required_phrase_in_text(
            text=self.text_with_stopwords,
            required_phrase="usr share common licenses gpl 2",
        )

        text = self.text_with_stopwords
        for span in required_phrase_spans_specified:
            text = add_required_phrase_markers(
                text=text,
                required_phrase_span=span,
            )

        assert text == self.text_with_stopwords_and_marked_required_phrases

class TestKeyPhrasesCanBeMarked(TestCaseClass):

    @pytest.mark.scanslow
    def can_more_key_phrases_be_marked_from_other_rules(self):
        add_required_phrases_from_other_rules(can_mark_required_phrase_test=True)

    @pytest.mark.scanslow
    def can_more_key_phrases_be_marked_from_license_attribtues(self):
        add_required_phrases_from_license_fields(can_mark_required_phrase_test=True)
