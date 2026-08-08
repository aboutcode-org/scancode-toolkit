# tests for add_ml_phrases.py
# no model and no network here, the tagger is stubbed out
import sys
from pathlib import Path

import click
import pytest

sys.path.insert(0, str(Path(__file__).parent))
import add_ml_phrases
from add_ml_phrases import inject
from add_ml_phrases import is_updatable
from add_ml_phrases import new_counts
from add_ml_phrases import phrases_from_tags
from add_ml_phrases import predict_phrases
from add_ml_phrases import process_rules
from add_ml_phrases import select_rules
from add_ml_phrases import words_from_text
from train_model import LABEL2ID

from licensedcode.models import Rule


class FakeRule:
    """Just the flags is_updatable looks at"""

    def __init__(self, text='some license text here', is_from_license=False,
                 is_approx_matchable=True, skip=False):
        self.text = text
        self.is_from_license = is_from_license
        self.is_approx_matchable = is_approx_matchable
        self.skip_for_required_phrase_generation = skip


class FakeEncoding(dict):

    def __init__(self, word_ids):
        super().__init__()
        self._word_ids = word_ids
        self['input_ids'] = [[0] * len(word_ids)]
        self['attention_mask'] = [[1] * len(word_ids)]

    def word_ids(self):
        return self._word_ids


class FakeTokenizer:
    """Maps every word to one subword, truncating at max_length"""

    def __call__(self, words, max_length=512, **kwargs):
        return FakeEncoding(list(range(len(words)))[:max_length])


class StubTagger:
    """Tags the first three words as one phrase"""

    def predict_words(self, input_ids, attention_mask, word_ids):
        count = len([w for w in word_ids if w is not None])
        tags = [LABEL2ID['B-REQ'], LABEL2ID['I-REQ'], LABEL2ID['E-REQ']]
        return (tags + [LABEL2ID['O']] * count)[:count]


class TestWordsFromText:

    def test_matches_the_dataset_tokenizer(self):
        assert words_from_text('Apache-2.0 License') == ['Apache', '2', '0', 'License']

    def test_normalizes_line_endings(self):
        assert words_from_text('one\r\ntwo\rthree') == ['one', 'two', 'three']

    def test_applies_nfkc(self):
        # the ﬁ ligature becomes two characters, otherwise it stays one token
        assert words_from_text('a\ufb01x') == ['afix']

    def test_empty(self):
        assert words_from_text('') == []


class TestPhrasesFromTags:

    def test_one_phrase(self):
        words = ['Apache', 'License', 'Version', 'x']
        tags = ['B-REQ', 'I-REQ', 'E-REQ', 'O']
        assert phrases_from_tags(tags, words) == ['Apache License Version']

    def test_longest_first_and_deduped(self):
        words = ['mit', 'license', 'mit', 'license']
        tags = ['B-REQ', 'E-REQ', 'S-REQ', 'O']
        assert phrases_from_tags(tags, words) == ['mit license', 'mit']

    def test_drops_a_span_cut_by_truncation(self):
        words = ['gnu', 'general', 'public']
        tags = ['O', 'B-REQ', 'I-REQ']
        assert phrases_from_tags(tags, words, truncated=True) == []
        assert phrases_from_tags(tags, words, truncated=False) == ['general public']

    def test_nothing_tagged(self):
        assert phrases_from_tags(['O', 'O'], ['a', 'b']) == []


class TestIsUpdatable:

    def test_plain_rule(self):
        assert is_updatable(FakeRule())

    def test_skips_rule_from_a_license(self):
        assert not is_updatable(FakeRule(is_from_license=True))

    def test_skips_long_text(self):
        assert not is_updatable(FakeRule(text='x' * 4001))

    def test_skips_not_approx_matchable(self):
        assert not is_updatable(FakeRule(is_approx_matchable=False))

    def test_skips_when_asked_to(self):
        assert not is_updatable(FakeRule(skip=True))

    def test_skips_rules_that_already_have_phrases(self):
        assert not is_updatable(FakeRule(text='under the {{mit license}} terms'))


def make_rule(text, source=None):
    rule = Rule(
        license_expression='mit',
        identifier='mit_test.RULE',
        text=text,
        is_license_reference=True,
        relevance=100,
    )
    rule.source = source
    return rule


def patch_selection(monkeypatch, rules):
    """Skip the real rule loading, it reads every rule file on disk"""
    monkeypatch.setattr(
        add_ml_phrases, 'select_rules',
        lambda license_expression=None: {'mit': rules},
    )


TEXT = 'Permission is granted under the MIT License to do things with this'


class TestInject:

    def test_marks_a_phrase_and_sets_the_source(self):
        rule = make_rule(TEXT)
        counts = new_counts()
        assert inject(rule, ['MIT License'], counts, dry_run=True)
        assert counts['injected'] == 1
        assert '{{MIT License}}' in rule.text
        assert rule.source == 'ml_model'

    def test_keeps_an_existing_source(self):
        rule = make_rule(TEXT, source='mit_1.RULE')
        inject(rule, ['MIT License'], new_counts(), dry_run=True)
        assert rule.source == 'mit_1.RULE ml_model'

    def test_rejects_a_phrase_is_good_does_not_like(self):
        rule = make_rule(TEXT)
        counts = new_counts()
        assert not inject(rule, ['is'], counts, dry_run=True)
        assert counts['rejected'] == 1
        assert '{{' not in rule.text

    def test_counts_a_phrase_that_is_not_in_the_text(self):
        rule = make_rule(TEXT)
        counts = new_counts()
        assert not inject(rule, ['Apache License'], counts, dry_run=True)
        assert counts['not_found'] == 1

    def test_marks_two_phrases_in_one_rule(self):
        rule = make_rule(TEXT)
        counts = new_counts()
        assert inject(rule, ['MIT License', 'do things'], counts, dry_run=True)
        assert counts['injected'] == 2
        assert rule.text.count('{{') == rule.text.count('}}') == 2

    def test_does_not_mark_the_same_phrase_twice(self):
        rule = make_rule(TEXT)
        counts = new_counts()
        inject(rule, ['MIT License'], counts, dry_run=True)
        inject(rule, ['MIT License'], counts, dry_run=True)
        assert counts['injected'] == 1
        assert counts['skipped'] == 1
        assert rule.text.count('{{') == 1


class TestPredictPhrases:

    def test_predicts_and_reports_no_truncation(self):
        words = words_from_text(TEXT)
        phrases, truncated = predict_phrases(StubTagger(), FakeTokenizer(), 512, words)
        assert phrases == [' '.join(words[:3])]
        assert not truncated

    def test_reports_truncation(self):
        words = ['word'] * 20
        phrases, truncated = predict_phrases(StubTagger(), FakeTokenizer(), 5, words)
        assert truncated

    def test_a_rule_with_no_words(self):
        # nothing to tag, and the tagger never gets as far as the backbone
        assert predict_phrases(StubTagger(), FakeTokenizer(), 512, []) == ([], False)


class TestSelectRules:

    def test_filters_and_groups(self, monkeypatch):
        rules = {
            'mit': [FakeRule(), FakeRule(is_from_license=True)],
            'bsd-new': [FakeRule(skip=True)],
        }
        monkeypatch.setattr(add_ml_phrases, 'get_rules_by_expression', lambda: rules)
        selected = select_rules()
        assert list(selected) == ['mit']
        assert len(selected['mit']) == 1

    def test_unknown_expression(self, monkeypatch):
        rules = {'mit': [FakeRule()]}
        monkeypatch.setattr(add_ml_phrases, 'get_rules_by_expression', lambda: rules)
        with pytest.raises(click.ClickException):
            select_rules('nope-1.0')


class TestProcessRules:

    def test_dry_run_marks_nothing_on_disk(self, monkeypatch):
        rule = make_rule(TEXT)
        patch_selection(monkeypatch, [rule])
        counts = process_rules(StubTagger(), FakeTokenizer(), 512, dry_run=True)
        assert counts['rules'] == 1
        assert counts['injected'] == 1

    def test_limit_stops_early(self, monkeypatch):
        patch_selection(monkeypatch, [make_rule(TEXT) for _ in range(5)])
        counts = process_rules(StubTagger(), FakeTokenizer(), 512, dry_run=True, limit=2)
        assert counts['rules'] == 2

    def test_counts_a_truncated_rule(self, monkeypatch):
        patch_selection(monkeypatch, [make_rule(TEXT)])
        counts = process_rules(StubTagger(), FakeTokenizer(), 4, dry_run=True)
        assert counts['truncated'] == 1
