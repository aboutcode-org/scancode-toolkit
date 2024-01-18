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

from licensedcode.required_phrases import get_key_phrase_spans
from licensedcode.models import InvalidRule
from licensedcode.spans import Span


class TestGetKeyPhrases(TestCaseClass):

    def test_get_key_phrases_yields_spans(self):
        text = (
            'This released software is {{released}} by under {{the MIT license}}. '
            'Which is a license originating at Massachusetts Institute of Technology (MIT).'
        )

        key_phrase_spans = get_key_phrase_spans(text)
        assert list(key_phrase_spans) == [Span(4), Span(7, 9)]

    def test_get_key_phrases_raises_exception_key_phrase_markup_is_not_closed(self):
        text = 'This software is {{released by under the MIT license.'
        try:
            list(get_key_phrase_spans(text))
            raise Exception('Exception should be raised')
        except InvalidRule:
            pass

    def test_get_key_phrases_ignores_stopwords_in_positions(self):
        text = 'The word comma is a stop word so comma does not increase the span position {{MIT license}}.'
        key_phrase_spans = get_key_phrase_spans(text)
        assert list(key_phrase_spans) == [Span(11, 12)]

    def test_get_key_phrases_yields_spans_without_stop_words(self):
        text = 'This released software is {{released span}} by under {{the MIT quot license}}.'
        key_phrase_spans = get_key_phrase_spans(text)
        assert list(key_phrase_spans) == [Span(4), Span(7, 9)]

    def test_get_key_phrases_does_not_yield_empty_spans(self):
        text = 'This released software {{comma}} is {{}} by under {{the MIT license}}.'
        try:
            list(get_key_phrase_spans(text))
            raise Exception('Exception should be raised')
        except InvalidRule:
            pass

    def test_get_key_phrases_only_considers_outer_key_phrase_markup(self):
        text = 'This released {{{software under the MIT}}} license.'
        key_phrase_spans = get_key_phrase_spans(text)
        assert list(key_phrase_spans) == [Span(2, 5)]

    def test_get_key_phrases_ignores_nested_key_phrase_markup(self):
        text = 'This released {{software {{under the}} MIT}} license.'
        try:
            list(get_key_phrase_spans(text))
            raise Exception('Exception should be raised')
        except InvalidRule:
            pass
