#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from unittest import TestCase as TestCaseClass

import pytest

from licensedcode.models import InvalidRule
from licensedcode.models import Rule
from licensedcode.required_phrases import update_rules_using_is_required_phrases_rules
from licensedcode.required_phrases import update_rules_using_license_attributes
from licensedcode.required_phrases import IsRequiredPhrase
from licensedcode.required_phrases import add_required_phrase_markers
from licensedcode.spans import Span
from licensedcode.required_phrases import find_phrase_spans_in_text
from licensedcode.tokenize import get_existing_required_phrase_spans


class TestIsRequiredPhraseCanSort(TestCaseClass):

    required_phrase_texts = [
        "mit",
        "the MIT License",
        "MIT License with Disclaimer",
        "licenses: mit",
        "MIT license",
    ]
    is_required_phrases = [
        IsRequiredPhrase(
            required_phrase_text=text,
            rule=Rule(
                license_expression="mit",
                identifier="mit_231.RULE",
                text=text,
                is_required_phrase=True,
                is_license_tag=True,
            )
        )
        for text in required_phrase_texts
    ]

    def test_sort_is_required_phrases_works(self):
        srps = IsRequiredPhrase.sorted(self.is_required_phrases)
        results = [srp.required_phrase_text for srp in srps]

        expected = [
            "MIT License with Disclaimer",
            "the MIT License",
            "licenses: mit",
            "MIT license",
            "mit",
        ]
        assert results == expected


class TestFindPhraseInText:

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

    def test_find_phrase_spans_in_text_with_behaves_same_as_get_existing_required_phrase_spans(self):
        spans_with_phrase = find_phrase_spans_in_text(
            text=self.text_with_stopwords,
            phrase_text="usr share common licenses gpl 2",
        )

        spans_with_find = get_existing_required_phrase_spans(
            text=self.text_with_stopwords_and_marked_required_phrases,
        )

        assert spans_with_phrase == spans_with_find

    def test_find_phrase_spans_in_text_and_add_required_phrase_matches(self):

        spans = find_phrase_spans_in_text(
            text=self.text_with_stopwords,
            phrase_text="usr share common licenses gpl 2",
        )

        text = self.text_with_stopwords
        for span in spans:
            text = add_required_phrase_markers(
                text=text,
                required_phrase_span=span,
            )

        assert text == self.text_with_stopwords_and_marked_required_phrases


class TestFindSpansInText:

    text_with_articles = (
        "A copy of the GNU General Public License is available as "
        "/usr/share/common-licenses/GPL-2 in the Debian GNU/Linux distribution. "
        "A copy of the GNU General Public License is available as "
        "/usr/share/common-licenses/GPL-2 in the Debian GNU/Linux distribution."
    )

    text_with_articles_and_marked_required_phrases = (
        "A copy of the GNU General Public License is available as "
        "/{{usr/share/common-licenses/GPL-2}} in the Debian GNU/Linux distribution. "
        "A copy of the GNU General Public License is available as "
        "/{{usr/share/common-licenses/GPL-2}} in the Debian GNU/Linux distribution."
    )

    text_with_extra_characters = (
        "This is the http://www.opensource.org/licenses/mit-license.php MIT "
        "Software License which is OSI-certified, and GPL-compatible."
    )

    text_with_extra_characters_and_marked_required_phrases = (
        "This is the http://www.opensource.org/licenses/mit-license.php {{MIT "
        "Software License}} which is OSI-certified, and GPL-compatible."
    )

    def test_find_phrase_spans_in_text(self):
        text = "is released under the MIT license. See the LICENSE"
        spans = find_phrase_spans_in_text(text=text, phrase_text="mit license")
        assert spans == [Span(4, 5)]

    def test_find_phrase_spans_in_text_multiple(self):
        spans = find_phrase_spans_in_text(
            text=self.text_with_articles,
            phrase_text="usr share common licenses gpl 2",
        )
        assert spans == [Span(10, 15), Span(32, 37)]

    def test_find_phrase_spans_in_text_then_add_with_multiple_spans(self):
        spans = find_phrase_spans_in_text(
            text=self.text_with_articles,
            phrase_text="usr share common licenses gpl 2",
        )
        text = self.text_with_articles
        for span in spans:
            text = add_required_phrase_markers(
                text=text,
                required_phrase_span=span,
            )

        assert text == self.text_with_articles_and_marked_required_phrases

    def test_add_required_phrase_markers_in_text_with_extra_characters(self):
        spans = find_phrase_spans_in_text(
            text=self.text_with_extra_characters,
            phrase_text="mit software license",
        )
        text = self.text_with_extra_characters
        for span in spans:
            text = add_required_phrase_markers(
                text=text,
                required_phrase_span=span,
            )

        assert text == self.text_with_extra_characters_and_marked_required_phrases


class TestKeyPhrasesCanBeMarked(TestCaseClass):

    @pytest.mark.scanslow
    def test_update_rules_using_is_required_phrases_rules(self):
        update_rules_using_is_required_phrases_rules(verbose=True, dry_run=True)

    @pytest.mark.scanslow
    def test_update_rules_using_license_attributes(self):
        update_rules_using_license_attributes(verbose=True, dry_run=True)
