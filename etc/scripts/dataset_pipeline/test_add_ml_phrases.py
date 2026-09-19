import json
import sys
from pathlib import Path
from types import SimpleNamespace

import click
import pytest
from click.testing import CliRunner

sys.path.insert(0, str(Path(__file__).parent))

import add_ml_phrases
from add_ml_phrases import encode_words
from add_ml_phrases import inject
from add_ml_phrases import is_updatable
from add_ml_phrases import load_model
from add_ml_phrases import main
from add_ml_phrases import new_counts
from add_ml_phrases import phrases_from_tags
from add_ml_phrases import predict_phrases
from add_ml_phrases import predict_rule
from add_ml_phrases import process_rules
from add_ml_phrases import select_rules
from add_ml_phrases import words_from_text
from train_model import LABEL2ID

from licensedcode.models import Rule


class FakeRule:
    def __init__(
        self,
        text="some license text here",
        is_from_license=False,
        is_approx_matchable=True,
        skip=False,
    ):
        self.text = text
        self.is_from_license = is_from_license
        self.is_approx_matchable = is_approx_matchable
        self.skip_for_required_phrase_generation = skip


class FakeEncoding(dict):
    def __init__(self, word_ids):
        super().__init__(
            input_ids=list(range(len(word_ids))),
            attention_mask=[1] * len(word_ids),
        )
        self._word_ids = word_ids

    def word_ids(self):
        return list(self._word_ids)


class FakeTokenizer:
    """Tokenize words with configurable subword counts."""

    is_fast = True

    def __init__(self, subwords=None):
        self.subwords = subwords or {}

    def __call__(self, words, truncation, max_length=None, **kwargs):
        word_ids = [None]
        for index, word in enumerate(words):
            word_ids.extend([index] * self.subwords.get(word, 1))
        word_ids.append(None)
        if truncation and len(word_ids) > max_length:
            word_ids = word_ids[: max_length - 1] + [None]
        return FakeEncoding(word_ids)


class StubTagger:
    def __init__(self, labels):
        self.labels = labels
        self.calls = 0

    def predict_words(self, input_ids, attention_mask, word_ids):
        self.calls += 1
        count = len(set(word_id for word_id in word_ids if word_id is not None))
        labels = self.labels + [LABEL2ID["O"]] * count
        return labels[:count]


class TestLoadModel:
    def test_loads_a_valid_local_final_model(self, tmp_path, monkeypatch):
        config = tmp_path / "train_config.json"
        config.write_text(json.dumps({"max_length": 256}), encoding="utf-8")
        tagger = object()
        tokenizer = object()
        calls = []

        def load_final_model(model_dir, offline):
            calls.append((model_dir, offline))
            return tagger, tokenizer

        monkeypatch.setattr(add_ml_phrases, "load_final_model", load_final_model)
        assert load_model(tmp_path) == (tagger, tokenizer, 256)
        assert calls == [(tmp_path, True)]

    def test_downloads_before_using_the_strict_loader(self, tmp_path, monkeypatch):
        model_dir = tmp_path / "snapshot"
        model_dir.mkdir()
        (model_dir / "train_config.json").write_text(
            json.dumps({"max_length": 512}), encoding="utf-8"
        )
        downloads = []
        hub = SimpleNamespace(
            snapshot_download=lambda repo_id, token: downloads.append((repo_id, token))
            or str(model_dir)
        )
        monkeypatch.setitem(sys.modules, "huggingface_hub", hub)
        monkeypatch.setattr(
            add_ml_phrases,
            "load_final_model",
            lambda path, offline: (object(), object()),
        )

        load_model("owner/model", hf_token="secret")
        assert downloads == [("owner/model", "secret")]


class TestWordsFromText:
    def test_uses_dataset_tokenization(self):
        assert words_from_text("Apache-2.0 License") == ["Apache", "2", "0", "License"]

    def test_normalizes_line_endings_and_unicode(self):
        assert words_from_text("a\ufb01x\r\ntwo\rthree") == ["afix", "two", "three"]


class TestEncodeWords:
    def test_keeps_all_complete_words(self):
        encoding, truncated = encode_words(FakeTokenizer(), ["one", "two"], 10)
        assert encoding.word_ids() == [None, 0, 1, None]
        assert not truncated

    def test_removes_a_partially_truncated_word(self):
        tokenizer = FakeTokenizer({"many": 3})
        encoding, truncated = encode_words(tokenizer, ["one", "many", "three"], 4)
        assert encoding.word_ids() == [None, 0, None]
        assert truncated

    def test_rejects_when_no_complete_word_fits(self):
        with pytest.raises(ValueError, match="no complete words"):
            encode_words(FakeTokenizer({"many": 4}), ["many"], 3)


class TestPhrasesFromTags:
    def test_returns_longest_unique_phrases_first(self):
        words = ["mit", "license", "mit", "other"]
        tags = ["B-REQ", "E-REQ", "S-REQ", "O"]
        assert phrases_from_tags(tags, words) == ["mit license", "mit"]

    def test_rejects_invalid_bioes(self):
        with pytest.raises(ValueError, match="invalid BIOES"):
            phrases_from_tags(["B-REQ", "O"], ["one", "two"])


class TestPredictPhrases:
    def test_predicts_from_complete_words(self):
        labels = [LABEL2ID["B-REQ"], LABEL2ID["E-REQ"], LABEL2ID["O"]]
        phrases, truncated = predict_phrases(
            StubTagger(labels), FakeTokenizer(), 10, ["MIT", "License", "text"]
        )
        assert phrases == ["MIT License"]
        assert not truncated

    def test_keeps_a_valid_span_at_the_truncation_boundary(self):
        labels = [LABEL2ID["O"], LABEL2ID["S-REQ"]]
        phrases, truncated = predict_phrases(
            StubTagger(labels), FakeTokenizer(), 4, ["one", "two", "three"]
        )
        assert phrases == ["two"]
        assert truncated

    @pytest.mark.parametrize("label", [99, 1.5, True])
    def test_rejects_an_invalid_label_id(self, label):
        with pytest.raises(ValueError, match="invalid label ID"):
            predict_phrases(StubTagger([label]), FakeTokenizer(), 10, ["one"])

    def test_rejects_the_wrong_number_of_labels(self):
        tagger = StubTagger([])
        tagger.predict_words = lambda *args: []
        with pytest.raises(ValueError, match="different number"):
            predict_phrases(tagger, FakeTokenizer(), 10, ["one"])

    def test_empty_text_does_not_call_the_model(self):
        tagger = StubTagger([])
        assert predict_phrases(tagger, FakeTokenizer(), 10, []) == ([], False)
        assert tagger.calls == 0


class TestPredictRule:
    def test_returns_scored_phrase_offsets(self):
        torch = pytest.importorskip("torch")
        from phrase_model import ConstrainedCRF

        class Tagger(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.crf = ConstrainedCRF(5, batch_first=True)
                with torch.no_grad():
                    for parameter in self.crf.parameters():
                        parameter.zero_()

            def emissions(self, input_ids, attention_mask):
                emissions = torch.zeros((1, input_ids.shape[1], 5))
                emissions[0, 2, LABEL2ID["B-REQ"]] = 9.0
                emissions[0, 3, LABEL2ID["E-REQ"]] = 9.0
                return emissions

        result = predict_rule(
            Tagger(),
            FakeTokenizer(),
            20,
            "under the MIT License terms",
        )

        assert [phrase.text for phrase in result.phrases] == ["the MIT"]
        assert result.phrases[0].start_word == 1
        assert result.phrases[0].end_word == 2
        assert 0.0 <= result.phrases[0].confidence <= 1.0
        assert not result.truncated

    def test_empty_text_does_not_run_model(self):
        assert predict_rule(object(), FakeTokenizer(), 20, "").phrases == ()


class TestIsUpdatable:
    @pytest.mark.parametrize(
        "rule",
        [
            FakeRule(is_from_license=True),
            FakeRule(text="x" * 4001),
            FakeRule(is_approx_matchable=False),
            FakeRule(skip=True),
            FakeRule(text="under the {{mit license}} terms"),
        ],
    )
    def test_excludes_ineligible_rules(self, rule):
        assert not is_updatable(rule)

    def test_accepts_a_plain_rule(self):
        assert is_updatable(FakeRule())


class TestSelectRules:
    def test_filters_and_groups_rules(self, monkeypatch):
        monkeypatch.setattr(
            add_ml_phrases,
            "get_base_rules_by_expression",
            lambda expression: {
                "mit": [FakeRule(), FakeRule(is_from_license=True)],
                "bsd-new": [FakeRule(skip=True)],
            },
        )
        selected = select_rules()
        assert list(selected) == ["mit"]
        assert len(selected["mit"]) == 1

    def test_forwards_the_expression_filter(self, monkeypatch):
        expressions = []

        def get_rules(expression):
            expressions.append(expression)
            return {expression: [FakeRule()]}

        monkeypatch.setattr(add_ml_phrases, "get_base_rules_by_expression", get_rules)
        assert list(select_rules("mit")) == ["mit"]
        assert expressions == ["mit"]

    def test_reports_an_unknown_expression(self, monkeypatch):
        def get_rules(expression):
            raise KeyError(expression)

        monkeypatch.setattr(add_ml_phrases, "get_base_rules_by_expression", get_rules)
        with pytest.raises(click.ClickException, match="No rules"):
            select_rules("unknown")


def make_rule(text, source=None):
    rule = Rule(
        license_expression="mit",
        identifier="mit_test.RULE",
        text=text,
        is_license_reference=True,
        relevance=100,
    )
    rule.source = source
    return rule


TEXT = "Permission is granted under the MIT License to do things with this"


class TestInject:
    def test_marks_two_phrases_and_preserves_source(self):
        rule = make_rule(TEXT, source="mit_1.RULE")
        counts = new_counts()
        assert inject(rule, ["MIT License", "do things"], counts, dry_run=True)
        assert counts["injected"] == 2
        assert rule.text.count("{{") == rule.text.count("}}") == 2
        assert rule.source == "mit_1.RULE ml_model"

    def test_rejects_an_unsuitable_phrase(self):
        rule = make_rule(TEXT)
        counts = new_counts()
        assert not inject(rule, ["is"], counts, dry_run=True)
        assert counts["rejected"] == 1
        assert "{{" not in rule.text

    def test_counts_a_phrase_not_found_in_the_rule(self):
        rule = make_rule(TEXT)
        counts = new_counts()
        assert not inject(rule, ["Apache License"], counts, dry_run=True)
        assert counts["not_found"] == 1

    def test_writes_a_rule_once(self, monkeypatch):
        rule = make_rule(TEXT)
        writes = []
        monkeypatch.setattr(Rule, "dump", lambda self, directory: writes.append(directory))
        assert inject(rule, ["MIT License", "do things"], new_counts())
        assert writes == [add_ml_phrases.rules_data_dir]

class TestProcessRules:
    def test_processes_selected_rules(self):
        rule = make_rule(TEXT)
        labels = [LABEL2ID["B-REQ"], LABEL2ID["I-REQ"], LABEL2ID["E-REQ"]]
        counts = process_rules(
            selected={"mit": [rule]},
            tagger=StubTagger(labels),
            tokenizer=FakeTokenizer(),
            max_length=50,
            dry_run=True,
        )
        assert counts["rules"] == 1
        assert counts["injected"] == 1
        assert counts["written"] == 1

    def test_limit_stops_before_another_rule(self):
        rules = [make_rule(TEXT) for _ in range(3)]
        labels = [LABEL2ID["B-REQ"], LABEL2ID["I-REQ"], LABEL2ID["E-REQ"]]
        counts = process_rules(
            {"mit": rules}, StubTagger(labels), FakeTokenizer(), 50, dry_run=True, limit=2
        )
        assert counts["rules"] == 2


class TestCommand:
    def test_does_not_load_a_model_when_no_rules_are_eligible(self, monkeypatch):
        monkeypatch.setattr(add_ml_phrases, "select_rules", lambda **kwargs: {})

        def fail(*args, **kwargs):
            raise AssertionError("model should not load")

        monkeypatch.setattr(add_ml_phrases, "load_model", fail)
        result = CliRunner().invoke(main, ["--model", "unused"])
        assert result.exit_code == 0
        assert "No eligible rules found" in result.output

    def test_wires_selection_loading_and_processing(self, monkeypatch, tmp_path):
        selected = {"mit": [object()]}
        tagger = object()
        tokenizer = object()
        calls = []
        monkeypatch.setattr(add_ml_phrases, "select_rules", lambda **kwargs: selected)
        monkeypatch.setattr(
            add_ml_phrases, "load_model", lambda *args, **kwargs: (tagger, tokenizer, 256)
        )

        def process(**kwargs):
            calls.append(kwargs)
            return new_counts()

        monkeypatch.setattr(add_ml_phrases, "process_rules", process)
        result = CliRunner().invoke(
            main,
            ["--model", str(tmp_path), "--license-expression", "mit", "--dry-run"],
        )
        assert result.exit_code == 0
        assert calls[0]["selected"] is selected
        assert calls[0]["tagger"] is tagger
        assert calls[0]["tokenizer"] is tokenizer
        assert calls[0]["max_length"] == 256
        assert calls[0]["dry_run"] is True
