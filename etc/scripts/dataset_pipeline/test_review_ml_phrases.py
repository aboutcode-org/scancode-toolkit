# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import json

import click
from click.testing import CliRunner
import pytest

from licensedcode.models import Rule

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import add_ml_phrases
from add_ml_phrases import PhrasePrediction
from add_ml_phrases import PredictionResult
import review_ml_phrases as review_module
from review_ml_phrases import apply
from review_ml_phrases import APPROVED
from review_ml_phrases import PENDING
from review_ml_phrases import predict_records
from review_ml_phrases import prediction_record
from review_ml_phrases import read_review_file
from review_ml_phrases import REJECTED
from review_ml_phrases import review_model_required_phrases
from review_ml_phrases import text_sha256
from review_ml_phrases import validate_record
from review_ml_phrases import write_review_file


TEXT = "Permission is granted under the MIT License to do things with this software"


def make_rule(identifier="mit_test.RULE", text=TEXT, source=None):
    return Rule(
        identifier=identifier,
        license_expression="mit",
        text=text,
        source=source,
        is_license_reference=True,
        relevance=100,
    )


def make_prediction(text="MIT License", start=5, end=6, confidence=0.9):
    return PhrasePrediction(
        text=text,
        start_word=start,
        end_word=end,
        confidence=confidence,
    )


def make_record(rule=None, predictions=None):
    rule = rule or make_rule()
    predictions = predictions or [make_prediction()]
    return prediction_record(rule, predictions, truncated=False)


def use_rules_directory(monkeypatch, tmp_path):
    monkeypatch.setattr(review_module, "rules_data_dir", str(tmp_path))
    monkeypatch.setattr(add_ml_phrases, "rules_data_dir", str(tmp_path))


def test_prediction_record_is_pending_and_sorted_longest_first():
    record = prediction_record(
        make_rule(),
        [make_prediction("MIT", 5, 5, 0.8), make_prediction("MIT License", 5, 6, 0.9)],
        truncated=True,
    )

    assert [phrase["text"] for phrase in record["phrases"]] == ["MIT License", "MIT"]
    assert all(phrase["decision"] == PENDING for phrase in record["phrases"])
    assert record["truncated"] is True
    assert record["text_sha256"] == text_sha256(TEXT)


def test_prediction_record_keeps_the_strongest_repeated_phrase():
    record = prediction_record(
        make_rule(text="MIT License and MIT License"),
        [make_prediction("MIT License", 0, 1, 0.6), make_prediction("MIT License", 3, 4, 0.9)],
        truncated=False,
    )

    assert len(record["phrases"]) == 1
    assert record["phrases"][0]["confidence"] == 0.9
    assert record["phrases"][0]["start_word"] == 3


def test_review_file_round_trip_and_atomic_replacement(tmp_path):
    path = tmp_path / "review.jsonl"
    records = [make_record()]

    write_review_file(path, records)
    first = path.read_bytes()
    write_review_file(path, read_review_file(path))

    assert path.read_bytes() == first
    assert not list(tmp_path.glob("*.tmp"))


def test_failed_review_file_replacement_keeps_existing_file(tmp_path, monkeypatch):
    path = tmp_path / "review.jsonl"
    write_review_file(path, [make_record()])
    before = path.read_bytes()
    monkeypatch.setattr(review_module.os, "replace", lambda *args: (_ for _ in ()).throw(OSError()))

    with pytest.raises(OSError):
        write_review_file(path, [make_record()])

    assert path.read_bytes() == before
    assert not list(tmp_path.glob("*.tmp"))


@pytest.mark.parametrize(
    "change,error",
    [
        (lambda record: record.pop("truncated"), "record fields"),
        (lambda record: record.update(identifier="../mit.RULE"), "rule filename"),
        (lambda record: record.update(text_sha256="bad"), "text_sha256"),
        (lambda record: record.update(truncated=1), "boolean"),
        (lambda record: record.update(phrases=[]), "non-empty list"),
        (lambda record: record["phrases"][0].update(confidence=float("nan")), "confidence"),
        (lambda record: record["phrases"][0].update(decision="auto"), "decision"),
    ],
)
def test_validate_record_rejects_invalid_data(change, error):
    record = make_record()
    change(record)

    with pytest.raises(click.ClickException, match=error):
        validate_record(record, "review.jsonl", 1)


def test_read_review_file_rejects_malformed_json_and_duplicate_rules(tmp_path):
    malformed = tmp_path / "malformed.jsonl"
    malformed.write_text("{bad}\n", encoding="utf-8")
    with pytest.raises(click.ClickException, match="line 1"):
        read_review_file(malformed)

    duplicate = tmp_path / "duplicate.jsonl"
    record = make_record()
    duplicate.write_text(json.dumps(record) + "\n" + json.dumps(record) + "\n")
    with pytest.raises(click.ClickException, match="duplicate rule"):
        read_review_file(duplicate)


def test_load_current_rule_requires_same_expression_and_text(tmp_path, monkeypatch):
    use_rules_directory(monkeypatch, tmp_path)
    rule = make_rule()
    rule.dump(str(tmp_path))
    record = make_record(rule)

    loaded, reason = review_module.load_current_rule(record)
    assert loaded.identifier == rule.identifier
    assert reason is None

    record["license_expression"] = "apache-2.0"
    assert review_module.load_current_rule(record)[1] == "license expression changed"
    record["license_expression"] = "mit"
    record["text_sha256"] = "0" * 64
    assert review_module.load_current_rule(record)[1] == "rule text changed"


def test_preview_is_exact_and_does_not_mutate_rule():
    rule = make_rule(source="existing")

    changed, preview = review_module.preview_injection(rule, "MIT License")

    assert changed
    assert "{{MIT License}}" in preview
    assert rule.text == TEXT
    assert rule.source == "existing"


class FakePredictor:
    def predict(self, text):
        return PredictionResult(
            words=tuple(text.split()),
            phrases=(
                make_prediction(),
                make_prediction("is", 1, 1, 0.99),
            ),
            truncated=True,
        )


def test_predict_records_validates_candidates_and_honors_limit(monkeypatch):
    rules = [make_rule(identifier=f"mit_{index}.RULE") for index in range(3)]

    monkeypatch.setattr(review_module, "predict_rule", lambda *args: FakePredictor().predict(args[-1]))

    records, counts = predict_records(
        selected={"mit": rules},
        tagger=object(),
        tokenizer=object(),
        max_length=512,
        limit=2,
    )

    assert [record["identifier"] for record in records] == ["mit_0.RULE", "mit_1.RULE"]
    assert counts == {
        "rules": 2,
        "truncated": 2,
        "rejected": 2,
        "not_found": 0,
    }
    assert all(len(record["phrases"]) == 1 for record in records)


def test_predict_command_writes_only_valid_candidates(tmp_path, monkeypatch):
    review_file = tmp_path / "review.jsonl"
    rule = make_rule()
    monkeypatch.setattr(review_module, "select_rules", lambda **kwargs: {"mit": [rule]})
    monkeypatch.setattr(
        review_module,
        "load_model",
        lambda *args, **kwargs: (object(), object(), 512),
    )
    monkeypatch.setattr(review_module, "predict_rule", lambda *args: FakePredictor().predict(args[-1]))

    result = CliRunner().invoke(
        review_model_required_phrases,
        ["predict", "--model", "unused", "--review-file", str(review_file)],
    )

    assert result.exit_code == 0, result.output
    records = read_review_file(review_file)
    assert [phrase["text"] for phrase in records[0]["phrases"]] == ["MIT License"]
    assert records[0]["phrases"][0]["decision"] == PENDING
    assert "rejected      : 1" in result.output
    assert "truncated     : 1" in result.output


def test_predict_checks_selection_before_loading_model(tmp_path, monkeypatch):
    monkeypatch.setattr(review_module, "select_rules", lambda **kwargs: {})
    monkeypatch.setattr(
        review_module,
        "load_model",
        lambda *args, **kwargs: pytest.fail("model must not load"),
    )

    result = CliRunner().invoke(
        review_model_required_phrases,
        ["predict", "--model", "unused", "--review-file", str(tmp_path / "review.jsonl")],
    )

    assert result.exit_code == 0
    assert "No eligible rules" in result.output


def test_predict_refuses_to_replace_an_existing_review_file(tmp_path, monkeypatch):
    path = tmp_path / "review.jsonl"
    path.write_text("keep\n", encoding="utf-8")
    monkeypatch.setattr(
        review_module,
        "select_rules",
        lambda **kwargs: pytest.fail("selection must not run"),
    )

    result = CliRunner().invoke(
        review_model_required_phrases,
        ["predict", "--model", "unused", "--review-file", str(path)],
    )

    assert result.exit_code != 0
    assert path.read_text() == "keep\n"


def prepare_review(tmp_path, monkeypatch, phrases=None):
    use_rules_directory(monkeypatch, tmp_path)
    rule = make_rule()
    rule.dump(str(tmp_path))
    path = tmp_path / "review.jsonl"
    record = make_record(rule, phrases)
    write_review_file(path, [record])
    return path


def test_review_approves_and_rejects_predictions_resumably(tmp_path, monkeypatch):
    path = prepare_review(
        tmp_path,
        monkeypatch,
        [make_prediction(), make_prediction("do things", 8, 9, 0.7)],
    )

    first = CliRunner().invoke(
        review_model_required_phrases,
        ["review", "--review-file", str(path)],
        input="y\nq\n",
    )
    assert first.exit_code == 0, first.output
    assert [phrase["decision"] for phrase in read_review_file(path)[0]["phrases"]] == [
        APPROVED,
        PENDING,
    ]

    second = CliRunner().invoke(
        review_model_required_phrases,
        ["review", "--review-file", str(path)],
        input="n\n",
    )
    assert second.exit_code == 0, second.output
    assert [phrase["decision"] for phrase in read_review_file(path)[0]["phrases"]] == [
        APPROVED,
        REJECTED,
    ]


def test_review_edits_a_phrase_and_preserves_prediction(tmp_path, monkeypatch):
    path = prepare_review(tmp_path, monkeypatch)

    result = CliRunner().invoke(
        review_model_required_phrases,
        ["review", "--review-file", str(path)],
        input="e\nMIT License to\n",
    )

    assert result.exit_code == 0, result.output
    phrase = read_review_file(path)[0]["phrases"][0]
    assert phrase["text"] == "MIT License to"
    assert phrase["predicted_text"] == "MIT License"
    assert phrase["decision"] == APPROVED


def test_review_leaves_a_stale_record_pending(tmp_path, monkeypatch):
    path = prepare_review(tmp_path, monkeypatch)
    rule_path = tmp_path / "mit_test.RULE"
    rule_path.write_text(rule_path.read_text().replace("Permission", "Permission now"))

    result = CliRunner().invoke(
        review_model_required_phrases,
        ["review", "--review-file", str(path)],
    )

    assert result.exit_code == 0
    assert "rule text changed" in result.output
    assert read_review_file(path)[0]["phrases"][0]["decision"] == PENDING


def test_apply_refuses_pending_predictions(tmp_path, monkeypatch):
    path = prepare_review(tmp_path, monkeypatch)

    result = CliRunner().invoke(apply, ["--review-file", str(path)])

    assert result.exit_code != 0
    assert "still need review" in result.output
    assert "{{" not in Rule.from_file(str(tmp_path / "mit_test.RULE")).text


def test_apply_writes_only_approved_phrases_once(tmp_path, monkeypatch):
    path = prepare_review(
        tmp_path,
        monkeypatch,
        [make_prediction(), make_prediction("do things", 8, 9, 0.7)],
    )
    records = read_review_file(path)
    records[0]["phrases"][0]["decision"] = APPROVED
    records[0]["phrases"][1]["decision"] = REJECTED
    write_review_file(path, records)

    result = CliRunner().invoke(apply, ["--review-file", str(path)])

    assert result.exit_code == 0, result.output
    saved = Rule.from_file(str(tmp_path / "mit_test.RULE"))
    assert "{{MIT License}}" in saved.text
    assert "{{do things}}" not in saved.text
    assert saved.source == "ml_model"
    assert "rules written    : 1" in result.output


def test_apply_dry_run_does_not_write(tmp_path, monkeypatch):
    path = prepare_review(tmp_path, monkeypatch)
    records = read_review_file(path)
    records[0]["phrases"][0]["decision"] = APPROVED
    write_review_file(path, records)
    rule_path = tmp_path / "mit_test.RULE"
    before = rule_path.read_bytes()

    result = CliRunner().invoke(apply, ["--review-file", str(path), "--dry-run"])

    assert result.exit_code == 0, result.output
    assert rule_path.read_bytes() == before
    assert "Dry run" in result.output


def test_apply_refuses_a_stale_rule_without_mutation(tmp_path, monkeypatch):
    path = prepare_review(tmp_path, monkeypatch)
    records = read_review_file(path)
    records[0]["phrases"][0]["decision"] = APPROVED
    write_review_file(path, records)
    rule_path = tmp_path / "mit_test.RULE"
    rule_path.write_text(rule_path.read_text().replace("Permission", "Changed"))
    before = rule_path.read_bytes()

    result = CliRunner().invoke(apply, ["--review-file", str(path), "--verbose"])

    assert result.exit_code != 0
    assert rule_path.read_bytes() == before
    assert "stale review record" in result.output


def test_apply_preflights_every_rule_before_writing(tmp_path, monkeypatch):
    use_rules_directory(monkeypatch, tmp_path)
    first = make_rule(identifier="mit_first.RULE")
    second = make_rule(identifier="mit_second.RULE")
    first.dump(str(tmp_path))
    second.dump(str(tmp_path))
    records = [make_record(first), make_record(second)]
    for record in records:
        record["phrases"][0]["decision"] = APPROVED
    path = tmp_path / "review.jsonl"
    write_review_file(path, records)
    second_path = tmp_path / second.identifier
    second_path.write_text(second_path.read_text().replace("Permission", "Changed"))
    first_path = tmp_path / first.identifier
    before = first_path.read_bytes()

    result = CliRunner().invoke(apply, ["--review-file", str(path)])

    assert result.exit_code != 0
    assert first_path.read_bytes() == before
    assert "stale review record" in result.output


def test_command_group_exposes_all_stages():
    result = CliRunner().invoke(review_model_required_phrases, ["--help"])

    assert result.exit_code == 0
    assert "predict" in result.output
    assert "review" in result.output
    assert "apply" in result.output
