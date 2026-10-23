#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from types import SimpleNamespace
from unittest import TestCase as TestCaseClass

import pytest

from click.testing import CliRunner
from licensedcode import required_phrases
from licensedcode.models import InvalidRule
from licensedcode.models import Rule
from licensedcode.required_phrases import IsRequiredPhrase
from licensedcode.required_phrases import add_license_attributes_as_required_phrases_to_rules_text
from licensedcode.required_phrases import add_required_phrase_markers
from licensedcode.required_phrases import add_required_phrases
from licensedcode.required_phrases import add_required_phrases_to_composite_rules
from licensedcode.required_phrases import find_phrase_spans_in_text
from licensedcode.required_phrases import get_required_phrases_by_key
from licensedcode.required_phrases import get_updatable_rules_by_expression
from licensedcode.required_phrases import update_composite_rules_using_required_phrases
from licensedcode.required_phrases import update_rules_using_is_required_phrases_rules
from licensedcode.required_phrases import update_rules_using_license_attributes
from licensedcode.spans import Span
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


def make_required_phrase_rule(expression, text, identifier):
    return SimpleNamespace(
        license_expression=expression,
        text=text,
        identifier=identifier,
        is_required_phrase=True,
    )


def make_license(is_generic=False):
    return SimpleNamespace(is_generic=is_generic)


class TestRequiredPhrasesByKey:

    def test_collects_single_key_required_phrases_longest_first(self):
        rules_by_expression = {
            "mit": [
                make_required_phrase_rule("mit", "MIT", "mit_1.RULE"),
                make_required_phrase_rule("mit", "MIT License", "mit_2.RULE"),
                SimpleNamespace(is_required_phrase=False),
            ],
        }
        licenses_by_key = {"mit": make_license()}

        required_phrases_by_key = get_required_phrases_by_key(
            rules_by_expression=rules_by_expression,
            licenses_by_key=licenses_by_key,
        )

        assert [
            phrase.required_phrase_text
            for phrase in required_phrases_by_key["mit"]
        ] == ["MIT License", "MIT"]

    def test_skips_composite_source_expressions(self):
        rules_by_expression = {
            "mit AND apache-2.0": [
                make_required_phrase_rule(
                    "mit AND apache-2.0",
                    "MIT and Apache",
                    "mit_and_apache_1.RULE",
                ),
            ],
        }
        licenses_by_key = {
            "mit": make_license(),
            "apache-2.0": make_license(),
        }

        required_phrases_by_key = get_required_phrases_by_key(
            rules_by_expression=rules_by_expression,
            licenses_by_key=licenses_by_key,
        )

        assert required_phrases_by_key == {}

    def test_skips_generic_license_keys(self):
        rules_by_expression = {
            "unknown": [
                make_required_phrase_rule("unknown", "Unknown License", "unknown_1.RULE"),
            ],
        }
        licenses_by_key = {"unknown": make_license(is_generic=True)}

        required_phrases_by_key = get_required_phrases_by_key(
            rules_by_expression=rules_by_expression,
            licenses_by_key=licenses_by_key,
        )

        assert required_phrases_by_key == {}


class TestCompositeRequiredPhrases:

    required_phrases_by_key = {
        "mit": [
            IsRequiredPhrase(
                rule=make_required_phrase_rule("mit", "MIT License", "mit_1.RULE"),
                required_phrase_text="MIT License",
            ),
        ],
        "apache-2.0": [
            IsRequiredPhrase(
                rule=make_required_phrase_rule(
                    "apache-2.0",
                    "Apache License",
                    "apache-2.0_1.RULE",
                ),
                required_phrase_text="Apache License",
            ),
        ],
        "bsd-new": [
            IsRequiredPhrase(
                rule=make_required_phrase_rule("bsd-new", "BSD License", "bsd-new_1.RULE"),
                required_phrase_text="BSD License",
            ),
        ],
    }

    def test_marks_each_key_when_all_required_phrases_match(self):
        rule = Rule(
            license_expression="mit AND apache-2.0",
            identifier="mit_and_apache-2.0_test.RULE",
            text="Licensed under the MIT License and the Apache License.",
            is_license_notice=True,
        )

        add_required_phrases_to_composite_rules(
            rules=[rule],
            license_keys=["mit", "apache-2.0"],
            required_phrases_by_key=self.required_phrases_by_key,
            dry_run=True,
        )

        assert "{{MIT License}}" in rule.text
        assert "{{Apache License}}" in rule.text

    def test_leaves_rule_unchanged_when_one_key_does_not_match(self):
        text = "Licensed under the MIT License."
        rule = Rule(
            license_expression="mit AND apache-2.0",
            identifier="mit_and_apache-2.0_test.RULE",
            text=text,
            is_license_notice=True,
        )

        add_required_phrases_to_composite_rules(
            rules=[rule],
            license_keys=["mit", "apache-2.0"],
            required_phrases_by_key=self.required_phrases_by_key,
            dry_run=True,
        )

        assert rule.text == text
        assert rule.source is None

    def test_marks_three_key_rule(self):
        rule = Rule(
            license_expression="mit AND apache-2.0 AND bsd-new",
            identifier="three_key_test.RULE",
            text="MIT License, Apache License, and BSD License apply.",
            is_license_notice=True,
        )

        add_required_phrases_to_composite_rules(
            rules=[rule],
            license_keys=["mit", "apache-2.0", "bsd-new"],
            required_phrases_by_key=self.required_phrases_by_key,
            dry_run=True,
        )

        assert "{{MIT License}}" in rule.text
        assert "{{Apache License}}" in rule.text
        assert "{{BSD License}}" in rule.text

    def test_keeps_existing_marker_and_marks_the_other_key(self):
        rule = Rule(
            license_expression="mit AND apache-2.0",
            identifier="existing_marker_test.RULE",
            text="Licensed under the {{MIT License}} and the Apache License.",
            is_license_notice=True,
        )

        add_required_phrases_to_composite_rules(
            rules=[rule],
            license_keys=["mit", "apache-2.0"],
            required_phrases_by_key=self.required_phrases_by_key,
            dry_run=True,
        )

        assert rule.text.count("{{MIT License}}") == 1
        assert "{{Apache License}}" in rule.text

    def test_keeps_marked_occurrence_of_partly_marked_phrase(self):
        rule = Rule(
            license_expression="mit AND apache-2.0",
            identifier="partly_marked_phrase_test.RULE",
            text=(
                "The {{MIT License}} applies to one part and the MIT License applies "
                "to another part under the Apache License."
            ),
            is_license_notice=True,
        )

        add_required_phrases_to_composite_rules(
            rules=[rule],
            license_keys=["mit", "apache-2.0"],
            required_phrases_by_key=self.required_phrases_by_key,
            dry_run=True,
        )

        assert rule.text.count("{{MIT License}}") == 1
        assert "{{Apache License}}" in rule.text

    def test_prefers_existing_marker_over_unmarked_candidate(self):
        text = (
            "Licensed under {{Apache License}} {{or the MIT License}} "
            "(LICENSE.mit)."
        )
        rule = Rule(
            license_expression="mit OR apache-2.0",
            identifier="existing_markers_test.RULE",
            text=text,
            is_license_notice=True,
        )
        required_phrases_by_key = dict(self.required_phrases_by_key)
        required_phrases_by_key["mit"] = [
            IsRequiredPhrase(
                rule=make_required_phrase_rule("mit", "License: MIT", "mit_1.RULE"),
                required_phrase_text="License: MIT",
            ),
            self.required_phrases_by_key["mit"][0],
        ]

        add_required_phrases_to_composite_rules(
            rules=[rule],
            license_keys=["mit", "apache-2.0"],
            required_phrases_by_key=required_phrases_by_key,
            dry_run=True,
        )

        assert rule.text == text

    def test_writes_once_after_all_required_phrases_are_added(self, tmp_path, monkeypatch):
        rule = Rule(
            license_expression="mit AND apache-2.0",
            identifier="write_once_test.RULE",
            text="Licensed under the MIT License and the Apache License.",
            is_license_notice=True,
        )
        original_dump = Rule.dump
        dump_calls = []

        def dump(rule, rules_data_dir):
            dump_calls.append(rule.identifier)
            original_dump(rule, rules_data_dir)

        monkeypatch.setattr(Rule, "dump", dump)
        monkeypatch.setattr(required_phrases, "rules_data_dir", str(tmp_path))

        add_required_phrases_to_composite_rules(
            rules=[rule],
            license_keys=["mit", "apache-2.0"],
            required_phrases_by_key=self.required_phrases_by_key,
            write_phrase_source=True,
        )

        saved_rule = Rule.from_file(str(tmp_path / rule.identifier))
        assert dump_calls == [rule.identifier]
        assert "{{MIT License}}" in saved_rule.text
        assert "{{Apache License}}" in saved_rule.text
        assert saved_rule.source == "mit_1.RULE apache-2.0_1.RULE"

    def test_dry_run_does_not_write_rule(self, monkeypatch):
        rule = Rule(
            license_expression="mit AND apache-2.0",
            identifier="dry_run_test.RULE",
            text="Licensed under the MIT License and the Apache License.",
            is_license_notice=True,
        )

        def dump(*args, **kwargs):
            pytest.fail("Rule.dump() called during a dry run")

        monkeypatch.setattr(Rule, "dump", dump)

        add_required_phrases_to_composite_rules(
            rules=[rule],
            license_keys=["mit", "apache-2.0"],
            required_phrases_by_key=self.required_phrases_by_key,
            dry_run=True,
        )

        assert "{{MIT License}}" in rule.text
        assert "{{Apache License}}" in rule.text

    def test_rolls_back_when_a_required_phrase_cannot_be_added(self, monkeypatch):
        text = "Licensed under the MIT License and the Apache License."
        source = "existing.RULE"
        rule = Rule(
            license_expression="mit AND apache-2.0",
            identifier="rollback_test.RULE",
            text=text,
            source=source,
            is_license_notice=True,
        )
        original_add_required_phrase = required_phrases.add_required_phrase_to_rule
        calls = []

        def add_required_phrase(*args, **kwargs):
            calls.append(kwargs["required_phrase"])
            if len(calls) == 2:
                return False
            return original_add_required_phrase(*args, **kwargs)

        monkeypatch.setattr(
            required_phrases,
            "add_required_phrase_to_rule",
            add_required_phrase,
        )

        add_required_phrases_to_composite_rules(
            rules=[rule],
            license_keys=["mit", "apache-2.0"],
            required_phrases_by_key=self.required_phrases_by_key,
            write_phrase_source=True,
            dry_run=True,
        )

        assert calls == ["MIT License", "Apache License"]
        assert rule.text == text
        assert rule.source == source

    def test_uses_next_candidate_when_first_candidate_overlaps(self):
        rule = Rule(
            license_expression="gpl-2.0 AND gpl-2.0-plus",
            identifier="overlapping_candidate_test.RULE",
            text=(
                "GNU General Public License version 2, or any later version."
            ),
            is_license_notice=True,
        )
        required_phrases_by_key = {
            "gpl-2.0": [
                IsRequiredPhrase(
                    rule=make_required_phrase_rule(
                        "gpl-2.0",
                        "GNU General Public License version 2",
                        "gpl-2.0_1.RULE",
                    ),
                    required_phrase_text="GNU General Public License version 2",
                ),
            ],
            "gpl-2.0-plus": [
                IsRequiredPhrase(
                    rule=make_required_phrase_rule(
                        "gpl-2.0-plus",
                        "General Public License version 2",
                        "gpl-2.0-plus_1.RULE",
                    ),
                    required_phrase_text="General Public License version 2",
                ),
                IsRequiredPhrase(
                    rule=make_required_phrase_rule(
                        "gpl-2.0-plus",
                        "any later version",
                        "gpl-2.0-plus_2.RULE",
                    ),
                    required_phrase_text="any later version",
                ),
            ],
        }

        add_required_phrases_to_composite_rules(
            rules=[rule],
            license_keys=["gpl-2.0", "gpl-2.0-plus"],
            required_phrases_by_key=required_phrases_by_key,
            dry_run=True,
        )

        assert "{{GNU General Public License version 2}}" in rule.text
        assert "{{any later version}}" in rule.text

    def test_retries_candidate_selected_for_earlier_key(self):
        rule = Rule(
            license_expression="license-a AND license-b",
            identifier="candidate_backtracking_test.RULE",
            text="Alpha Long License and Backup Terms.",
            is_license_notice=True,
        )
        required_phrases_by_key = {
            "license-a": [
                IsRequiredPhrase(
                    rule=make_required_phrase_rule(
                        "license-a",
                        "Alpha Long License",
                        "license-a_1.RULE",
                    ),
                    required_phrase_text="Alpha Long License",
                ),
                IsRequiredPhrase(
                    rule=make_required_phrase_rule(
                        "license-a",
                        "Backup Terms",
                        "license-a_2.RULE",
                    ),
                    required_phrase_text="Backup Terms",
                ),
            ],
            "license-b": [
                IsRequiredPhrase(
                    rule=make_required_phrase_rule(
                        "license-b",
                        "Long License",
                        "license-b_1.RULE",
                    ),
                    required_phrase_text="Long License",
                ),
            ],
        }

        add_required_phrases_to_composite_rules(
            rules=[rule],
            license_keys=["license-a", "license-b"],
            required_phrases_by_key=required_phrases_by_key,
            dry_run=True,
        )

        assert "{{Long License}}" in rule.text
        assert "{{Backup Terms}}" in rule.text
        assert "{{Alpha Long License}}" not in rule.text


class TestCompositeRequiredPhrasesCommand:

    def test_update_composite_rules_uses_single_key_required_phrases(self, monkeypatch):
        required_rules = {
            "mit": [make_required_phrase_rule("mit", "MIT License", "mit_1.RULE")],
            "apache-2.0": [
                make_required_phrase_rule(
                    "apache-2.0",
                    "Apache License",
                    "apache-2.0_1.RULE",
                ),
            ],
        }
        target = Rule(
            license_expression="mit AND apache-2.0",
            identifier="mit_and_apache-2.0_test.RULE",
            text="Licensed under the MIT License and the Apache License.",
            is_license_notice=True,
        )
        licenses_by_key = {
            "mit": make_license(),
            "apache-2.0": make_license(),
        }

        monkeypatch.setattr(required_phrases, "get_licenses_db", lambda: licenses_by_key)
        monkeypatch.setattr(
            required_phrases,
            "get_base_rules_by_expression",
            lambda license_expression=None: required_rules,
        )
        monkeypatch.setattr(
            required_phrases,
            "get_updatable_rules_by_expression",
            lambda license_expression=None, simple_expression=True: {
                "mit AND apache-2.0": [target],
            },
        )

        update_composite_rules_using_required_phrases(dry_run=True)

        assert "{{MIT License}}" in target.text
        assert "{{Apache License}}" in target.text

    def test_update_composite_rules_skips_generic_keys(self, monkeypatch):
        required_rules = {
            "mit": [make_required_phrase_rule("mit", "MIT License", "mit_1.RULE")],
            "unknown": [
                make_required_phrase_rule("unknown", "Unknown License", "unknown_1.RULE"),
            ],
        }
        target = Rule(
            license_expression="mit AND unknown",
            identifier="mit_and_unknown_test.RULE",
            text="Licensed under the MIT License and an Unknown License.",
            is_license_notice=True,
        )
        licenses_by_key = {
            "mit": make_license(),
            "unknown": make_license(is_generic=True),
        }

        monkeypatch.setattr(required_phrases, "get_licenses_db", lambda: licenses_by_key)
        monkeypatch.setattr(
            required_phrases,
            "get_base_rules_by_expression",
            lambda license_expression=None: required_rules,
        )
        monkeypatch.setattr(
            required_phrases,
            "get_updatable_rules_by_expression",
            lambda license_expression=None, simple_expression=True: {
                "mit AND unknown": [target],
            },
        )

        update_composite_rules_using_required_phrases(dry_run=True)

        assert "{{MIT License}}" in target.text
        assert "{{Unknown License}}" not in target.text

    def test_composite_cli_calls_the_composite_update(self, monkeypatch):
        called = []

        def update(**kwargs):
            called.append(kwargs)

        monkeypatch.setattr(
            required_phrases,
            "update_composite_rules_using_required_phrases",
            update,
        )

        result = CliRunner().invoke(add_required_phrases, ["--composite-rules", "--dry-run"])

        assert result.exit_code == 0
        assert called == [{
            "license_expression": None,
            "write_phrase_source": False,
            "dry_run": True,
            "verbose": False,
        }]

    @pytest.mark.parametrize(
        "update_options",
        [
            ["--from-other-rules", "--from-license-attributes"],
            ["--from-other-rules", "--composite-rules"],
            ["--from-license-attributes", "--composite-rules"],
            [
                "--from-other-rules",
                "--from-license-attributes",
                "--composite-rules",
            ],
        ],
    )
    def test_cli_rejects_multiple_update_modes(self, update_options, monkeypatch):
        def fail(*args, **kwargs):
            pytest.fail("An update handler was called for conflicting options")

        monkeypatch.setattr(
            required_phrases,
            "update_rules_using_is_required_phrases_rules",
            fail,
        )
        monkeypatch.setattr(
            required_phrases,
            "update_rules_using_license_attributes",
            fail,
        )
        monkeypatch.setattr(
            required_phrases,
            "update_composite_rules_using_required_phrases",
            fail,
        )
        monkeypatch.setattr(required_phrases, "validate_and_reindex", fail)

        result = CliRunner().invoke(
            add_required_phrases,
            [*update_options, "--dry-run"],
        )

        assert result.exit_code == 2
        assert "are mutually exclusive" in result.output


class TestLicenseAttributePrerequisite:

    def test_license_attribute_fields_are_used(self):
        license_object = SimpleNamespace(
            key="mit",
            name="MIT License",
            short_name="MIT License",
            spdx_license_key="MIT",
            other_spdx_license_keys=[],
        )
        rule = Rule(
            license_expression="mit",
            identifier="mit_test.RULE",
            text="Licensed under the MIT License.",
            is_license_notice=True,
        )

        add_license_attributes_as_required_phrases_to_rules_text(
            license_object=license_object,
            rules=[rule],
            dry_run=True,
        )

        assert "{{MIT License}}" in rule.text

    def test_simple_expression_filter_uses_each_expression(self, monkeypatch):
        single_rule = Rule(
            license_expression="mit",
            identifier="mit_test.RULE",
            text="MIT License",
            is_license_notice=True,
        )
        composite_rule = Rule(
            license_expression="mit AND apache-2.0",
            identifier="composite_test.RULE",
            text="MIT License and Apache License",
            is_license_notice=True,
        )

        monkeypatch.setattr(required_phrases, "get_index", lambda: None)
        monkeypatch.setattr(
            required_phrases,
            "get_base_rules_by_expression",
            lambda license_expression=None: {
                "mit": [single_rule],
                "mit AND apache-2.0": [composite_rule],
            },
        )

        rules_by_expression = get_updatable_rules_by_expression(simple_expression=True)

        assert list(rules_by_expression) == ["mit"]
