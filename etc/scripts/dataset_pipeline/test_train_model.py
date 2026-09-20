# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import json
from pathlib import Path
import types

from click.testing import CliRunner
import pytest

import train_model as training
from train_model import align_labels
from train_model import AlignmentError
from train_model import ARTIFACT_SCHEMA
from train_model import build_effective_datasets
from train_model import compare_ordered_validation_results
from train_model import compute_metrics
from train_model import Config
from train_model import CONSTRAINT_CONTRACT
from train_model import decode_row
from train_model import extract_spans
from train_model import first_subword_positions
from train_model import IGNORE_INDEX
from train_model import LABEL2ID
from train_model import LABELS
from train_model import load_and_validate_splits
from train_model import main
from train_model import prepare_output_dir
from train_model import promote_final_model
from train_model import resolve_model_identity
from train_model import resolve_tokenizer_revision
from train_model import serializable_config
from train_model import sha256
from train_model import validate_bioes
from train_model import validate_config
from train_model import validate_publishable_model
from train_model import validate_record
from train_model import validate_saved_state
from train_model import validate_raw_split_hashes
from train_model import validate_state_dicts
from train_model import validate_state_structure
from train_model import write_failure_manifest
from train_model import write_json_atomic

REVISION = "a" * 40


class FakeEncoding(dict):
    def __init__(self, word_ids):
        super().__init__()
        self._word_ids = word_ids
        self["input_ids"] = [
            (0 if index == 0 else 1) if word_id is None else 10 + word_id
            for index, word_id in enumerate(word_ids)
        ]
        self["attention_mask"] = [1] * len(word_ids)

    def word_ids(self):
        return self._word_ids


class FakeTokenizer:
    is_fast = True
    all_special_ids = [0, 1]
    vocab_size = 100

    def __init__(self, full_ids=None, retained_ids=None):
        self.full_ids = full_ids
        self.retained_ids = retained_ids

    def __call__(self, tokens, truncation=False, max_length=512, **kwargs):
        default = [None, *range(len(tokens)), None]
        ids = self.full_ids if not truncation else self.retained_ids
        ids = list(ids if ids is not None else default)
        if truncation and self.retained_ids is None:
            ids = ids[:max_length]
        return FakeEncoding(ids)


def make_record(identifier="mit_1.RULE", tokens=None, labels=None):
    return {
        "identifier": identifier,
        "license_expression": "mit",
        "rule_type": "is_license_notice",
        "text": "MIT License terms apply",
        "tokens": tokens if tokens is not None else ["MIT", "License", "terms", "apply"],
        "bioes_labels": labels if labels is not None else ["B-REQ", "E-REQ", "O", "O"],
    }


def write_jsonl(path, records):
    path.write_text(
        "".join(json.dumps(record) + "\n" for record in records),
        encoding="utf-8",
    )


def make_split_paths(tmp_path, records=None):
    records = records or {
        "train": [make_record("train.RULE")],
        "validation": [make_record("val.RULE")],
        "test": [make_record("test.RULE")],
    }
    paths = {}
    for split, filename in (("train", "train.jsonl"), ("validation", "val.jsonl"), ("test", "test.jsonl")):
        path = tmp_path / filename
        write_jsonl(path, records[split])
        paths[split] = path
    return paths


def make_config(tmp_path, **changes):
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True)
    make_split_paths(data_dir)
    values = {
        "data_dir": data_dir,
        "output_dir": tmp_path / "model",
        "model_revision": REVISION,
    }
    values.update(changes)
    return Config(**values)


def test_contract_constants_are_exact():
    assert LABELS == ("O", "B-REQ", "I-REQ", "E-REQ", "S-REQ")
    assert ARTIFACT_SCHEMA == "scancode-required-phrases-model-v2"
    assert CONSTRAINT_CONTRACT == "bioes-hard-v1"


@pytest.mark.parametrize(
    "labels",
    [
        ["O"],
        ["S-REQ"],
        ["B-REQ", "E-REQ"],
        ["B-REQ", "I-REQ", "E-REQ", "O", "S-REQ"],
    ],
)
def test_validate_bioes_accepts_valid_sequences(labels):
    assert validate_bioes(labels) is None


@pytest.mark.parametrize(
    "labels",
    [[], ["I-REQ"], ["E-REQ"], ["B-REQ", "O"], ["O", "I-REQ"], ["B-REQ", "I-REQ"]],
)
def test_validate_bioes_rejects_invalid_sequences(labels):
    assert validate_bioes(labels)


def test_validate_record_requires_exact_non_empty_types_and_positive_labels():
    record = make_record()
    assert validate_record(record, "train.jsonl", 1) is record

    for field in ("identifier", "license_expression", "rule_type", "text"):
        invalid = make_record()
        invalid[field] = 1
        with pytest.raises(TypeError, match=field):
            validate_record(invalid, "train.jsonl", 2)

    invalid = make_record(tokens=["MIT", 1])
    invalid["bioes_labels"] = ["B-REQ", "E-REQ"]
    with pytest.raises(ValueError, match="token 1"):
        validate_record(invalid, "train.jsonl", 3)

    with pytest.raises(ValueError, match="no required phrase"):
        validate_record(make_record(labels=["O", "O", "O", "O"]), "train.jsonl", 4)


@pytest.mark.parametrize("field", training.RECORD_FIELDS)
def test_validate_record_rejects_missing_fields(field):
    record = make_record()
    del record[field]
    with pytest.raises(ValueError, match=field):
        validate_record(record, "train.jsonl", 9)


def test_all_raw_splits_are_validated_and_duplicate_ids_report_both_locations(tmp_path):
    records = {
        "train": [make_record("same.RULE")],
        "validation": [make_record("same.RULE")],
        "test": [make_record("test.RULE")],
    }
    paths = make_split_paths(tmp_path, records)
    with pytest.raises(ValueError, match=r"same\.RULE.*train split.*validation split"):
        load_and_validate_splits(paths)


def test_malformed_late_raw_line_is_not_hidden_by_limit(tmp_path):
    paths = make_split_paths(tmp_path)
    with paths["test"].open("a", encoding="utf-8") as stream:
        stream.write("{bad json}\n")
    with pytest.raises(ValueError, match=r"test\.jsonl line 2: malformed JSON"):
        load_and_validate_splits(paths)


def test_raw_hashes_and_content_duplicate_reports_are_complete(tmp_path):
    duplicate = make_record("duplicate.RULE")
    records = {
        "train": [make_record("train.RULE")],
        "validation": [duplicate],
        "test": [make_record("test.RULE")],
    }
    paths = make_split_paths(tmp_path, records)
    loaded, report = load_and_validate_splits(paths)

    assert [record.identifier for record in loaded["validation"]] == ["duplicate.RULE"]
    assert report["h0"]["train"]["serializer"] == "raw-bytes-v1"
    assert report["h1"]["train"]["serializer"].startswith("validated-records")
    assert report["h0"]["train"]["sha256"] == sha256(paths["train"])
    assert len(report["duplicates"]["tokens"]) == 1
    assert len(report["duplicates"]["tokens"][0]["records"]) == 3
    assert len(report["duplicates"]["labels"]) == 1


def test_h0_changes_with_raw_bytes_and_h1_tracks_validated_content(tmp_path):
    paths = make_split_paths(tmp_path)
    _records, first = load_and_validate_splits(paths)
    validate_raw_split_hashes(paths, first["h0"])

    paths["train"].write_text(paths["train"].read_text() + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="train split changed during the run"):
        validate_raw_split_hashes(paths, first["h0"])

    _records, second = load_and_validate_splits(paths)
    assert first["h0"]["train"]["sha256"] != second["h0"]["train"]["sha256"]
    assert first["h1"]["train"]["sha256"] == second["h1"]["train"]["sha256"]


def test_align_labels_uses_first_subwords_and_full_coverage():
    tokenizer = FakeTokenizer(
        full_ids=[None, 0, 1, 1, None],
        retained_ids=[None, 0, 1, 1, None],
    )
    encoding, truncated, cut = align_labels(
        ["MIT", "License"], ["B-REQ", "E-REQ"], tokenizer, 8
    )
    assert encoding["labels"] == [
        IGNORE_INDEX,
        LABEL2ID["B-REQ"],
        LABEL2ID["E-REQ"],
        IGNORE_INDEX,
        IGNORE_INDEX,
    ]
    assert not truncated and not cut


@pytest.mark.parametrize(
    (
        "full_ids", "retained_ids", "reason"
    ),
    [
        ([None, 0, 1, 1, None], [None, 0, 1, None], "omitted-non-o"),
        ([None, 0, 2, None], [None, 0, 2, None], "noncontiguous-coverage"),
        ([None, 0, None], [None, 0, None], "zero-coverage"),
    ],
)
def test_align_labels_rejects_partial_gap_and_zero_coverage(full_ids, retained_ids, reason):
    tokens = ["a", "b"] if 2 not in full_ids else ["a", "b", "c"]
    labels = ["B-REQ", "E-REQ"] if len(tokens) == 2 else ["B-REQ", "I-REQ", "E-REQ"]
    with pytest.raises(AlignmentError) as caught:
        align_labels(tokens, labels, FakeTokenizer(full_ids, retained_ids), 8)
    assert caught.value.reason == reason


def test_align_labels_accepts_only_omitted_o_words():
    tokenizer = FakeTokenizer(
        full_ids=[None, 0, 1, 2, 3, None],
        retained_ids=[None, 0, 1, None],
    )
    encoding, truncated, _cut = align_labels(
        ["MIT", "License", "terms", "apply"],
        ["B-REQ", "E-REQ", "O", "O"],
        tokenizer,
        4,
    )
    assert truncated
    assert encoding["labels"] == [IGNORE_INDEX, 1, 3, IGNORE_INDEX]

    with pytest.raises(AlignmentError) as caught:
        align_labels(
            ["prefix", "GNU", "License"],
            ["O", "B-REQ", "E-REQ"],
            FakeTokenizer([None, 0, 1, 2, None], [None, 0, None]),
            3,
        )
    assert caught.value.reason == "omitted-non-o"
    assert "positions [1, 2]" in str(caught.value)


def test_align_labels_retokenizes_a_partial_o_boundary_to_a_complete_prefix():
    class PartialBoundaryTokenizer(FakeTokenizer):
        def __call__(self, tokens, truncation=False, max_length=512, **kwargs):
            if len(tokens) == 2:
                return FakeEncoding([None, 0, 1, None])
            if truncation:
                return FakeEncoding([None, 0, 1, 2, None])
            return FakeEncoding([None, 0, 1, 2, 2, 3, None])

    encoding, truncated, _cut = align_labels(
        ["MIT", "License", "longword", "tail"],
        ["B-REQ", "E-REQ", "O", "O"],
        PartialBoundaryTokenizer(),
        5,
    )

    assert truncated
    assert encoding.word_ids() == [None, 0, 1, None]
    assert encoding["labels"] == [
        IGNORE_INDEX,
        LABEL2ID["B-REQ"],
        LABEL2ID["E-REQ"],
        IGNORE_INDEX,
    ]


def test_effective_limit_is_applied_after_all_alignment_accounting(tmp_path):
    records = {
        "train": [make_record("first.RULE"), make_record("second.RULE")],
        "validation": [make_record("val.RULE")],
        "test": [make_record("test.RULE")],
    }
    paths = make_split_paths(tmp_path, records)
    loaded, _report = load_and_validate_splits(paths)
    tokenizer = FakeTokenizer()
    datasets, h2 = build_effective_datasets(loaded, tokenizer, 512, limit=1)
    assert datasets["train"].identifiers == ["first.RULE"]
    assert len(datasets["train"].effective_inventory) == 2
    assert h2["train"]["effective_count"] == 2
    assert h2["train"]["selected_count"] == 1
    assert h2["train"]["serializer"].startswith("effective-examples")


@pytest.mark.parametrize(
    ("tags", "expected"),
    [
        (["O", "B-REQ", "I-REQ", "E-REQ", "O"], {(1, 3)}),
        (["O", "S-REQ", "O"], {(1, 1)}),
        (["S-REQ", "O", "B-REQ", "E-REQ"], {(0, 0), (2, 3)}),
        (["O", "O"], set()),
    ],
)
def test_extract_spans_requires_valid_sequences(tags, expected):
    assert extract_spans(tags) == expected
    with pytest.raises(ValueError, match="invalid BIOES"):
        extract_spans(["I-REQ"])


def test_decode_row_is_strict_and_drops_only_ignored_gold_positions():
    predicted, actual = decode_row(
        [LABEL2ID["B-REQ"], 99, LABEL2ID["E-REQ"]],
        [LABEL2ID["B-REQ"], IGNORE_INDEX, LABEL2ID["E-REQ"]],
    )
    assert predicted == ["B-REQ", "E-REQ"]
    assert actual == ["B-REQ", "E-REQ"]
    with pytest.raises(ValueError, match="lengths differ"):
        decode_row([0], [0, 0])
    with pytest.raises(ValueError, match="Unknown prediction ID"):
        decode_row([99], [0])


def test_compute_metrics_scores_exact_spans_and_reports_invalid_count():
    predictions = [[LABEL2ID["B-REQ"], LABEL2ID["E-REQ"], LABEL2ID["O"]]]
    labels = [[LABEL2ID["B-REQ"], LABEL2ID["E-REQ"], LABEL2ID["O"]]]
    scores = compute_metrics((predictions, labels), use_crf=True)
    assert scores == {
        "f1": 1.0,
        "precision": 1.0,
        "recall": 1.0,
        "exact_match": 1.0,
        "predicted_spans": 1,
        "gold_spans": 1,
        "invalid_paths": 0,
    }


def test_non_crf_invalid_path_is_not_repaired_and_counts_all_gold_false_negative():
    predictions = [[LABEL2ID["I-REQ"], LABEL2ID["E-REQ"]]]
    labels = [[LABEL2ID["B-REQ"], LABEL2ID["E-REQ"]]]
    scores = compute_metrics((predictions, labels), use_crf=False)
    assert scores["invalid_paths"] == 1
    assert scores["predicted_spans"] == 0
    assert scores["gold_spans"] == 1
    assert scores["recall"] == 0
    assert scores["exact_match"] == 0

    with pytest.raises(ValueError, match="Invalid CRF BIOES path in row 0"):
        compute_metrics((predictions, labels), use_crf=True)


def test_metrics_reject_shapes_ids_invalid_gold_and_crf_padding():
    with pytest.raises(ValueError, match="rank 2"):
        compute_metrics(([0], [0]))
    with pytest.raises(ValueError, match="batch sizes"):
        compute_metrics(([[0]], [[0], [0]]))
    with pytest.raises(ValueError, match="row lengths"):
        compute_metrics(([[0, 0]], [[0]]))
    with pytest.raises(ValueError, match="Unknown prediction ID"):
        compute_metrics(([[9]], [[0]]))
    with pytest.raises(ValueError, match="Unknown gold label ID"):
        compute_metrics(([[0]], [[9]]))
    with pytest.raises(ValueError, match="Invalid gold BIOES path"):
        compute_metrics(([[0]], [[LABEL2ID["I-REQ"]]]))
    with pytest.raises(ValueError, match="padding must be left aligned"):
        compute_metrics(
            (
                [[LABEL2ID["B-REQ"], IGNORE_INDEX, LABEL2ID["E-REQ"]]],
                [[LABEL2ID["B-REQ"], IGNORE_INDEX, LABEL2ID["E-REQ"]]],
            ),
            use_crf=True,
        )
    with pytest.raises(ValueError, match="prediction padding"):
        compute_metrics(
            ([[LABEL2ID["O"], LABEL2ID["O"]]], [[LABEL2ID["O"], IGNORE_INDEX]]),
            use_crf=True,
        )


def test_first_subword_positions_skips_specials_and_continuations():
    assert first_subword_positions([None, 0, 1, 1, 2, None]) == [1, 2, 4]


def test_config_validation_is_exhaustive_and_requires_immutable_revision(tmp_path):
    validate_config(make_config(tmp_path))

    invalid = make_config(tmp_path / "bad-revision", model_revision="main")
    with pytest.raises(ValueError, match="full immutable"):
        validate_config(invalid)


@pytest.mark.parametrize(
    ("field", "value", "error"),
    [
        ("epochs", 0, "between"),
        ("batch_size", True, "integer"),
        ("base_lr", float("nan"), "finite"),
        ("head_lr", 0, "greater than"),
        ("layer_decay", 1.1, "at most"),
        ("warmup_ratio", -1, "at least"),
        ("max_grad_norm", 0, "greater than"),
        ("optimizer", "other", "Unsupported optimizer"),
        ("precision", "fp16", "Unsupported precision"),
        ("limit", -1, "between"),
        ("label_weights", [1.0], "exactly 5"),
        ("resume", True, "unsupported"),
    ],
)
def test_config_rejects_invalid_fields(tmp_path, field, value, error):
    config = make_config(tmp_path)
    setattr(config, field, value)
    with pytest.raises((TypeError, ValueError), match=error):
        validate_config(config)


def test_config_rejects_non_empty_output(tmp_path):
    config = make_config(tmp_path)
    config.output_dir.mkdir()
    (config.output_dir / "anything").write_text("x")
    with pytest.raises(ValueError, match="not empty"):
        validate_config(config)


def test_prepare_output_dir_is_empty_only_and_never_resumes(tmp_path):
    output = tmp_path / "model"
    prepare_output_dir(output)
    assert output.is_dir()
    with pytest.raises(ValueError, match="unsupported"):
        prepare_output_dir(output, resume=True)
    (output / "checkpoint-1").mkdir()
    with pytest.raises(ValueError, match="not empty"):
        prepare_output_dir(output)


def test_atomic_json_is_complete_and_leaves_no_temporary_file(tmp_path):
    path = tmp_path / "manifest.json"
    write_json_atomic(path, {"state": "pre-run", "value": 1})
    write_json_atomic(path, {"state": "success", "value": 2})
    assert json.loads(path.read_text()) == {"state": "success", "value": 2}
    assert list(tmp_path.iterdir()) == [path]


def test_serializable_config_contains_every_field_and_string_paths(tmp_path):
    config = make_config(tmp_path)
    values = serializable_config(config)
    assert set(values) == set(config.__dataclass_fields__)
    assert values["data_dir"] == str(config.data_dir)
    assert values["output_dir"] == str(config.output_dir)


def test_sha256_is_stable(tmp_path):
    path = tmp_path / "data.jsonl"
    path.write_bytes(b"required phrase\n")
    assert sha256(path) == "792616e2062f96efb6ae2f69e8637b834e2db74354eb4f51e78eda329038cc70"


def test_exact_state_comparison_and_saved_state(tmp_path):
    torch = pytest.importorskip("torch")
    safetensors = pytest.importorskip("safetensors.torch")
    model = torch.nn.Linear(2, 1)
    state = model.state_dict()
    reversed_state = dict(reversed(list(state.items())))
    with pytest.raises(ValueError, match="key mismatch"):
        validate_state_dicts(state, reversed_state)

    changed = dict(state)
    changed["weight"] = changed["weight"].clone()
    changed["weight"][0, 0] += 1
    validate_state_structure(state, changed)
    with pytest.raises(ValueError, match="values differ"):
        validate_state_dicts(state, changed)
    changed = dict(state)
    changed["unexpected"] = torch.ones(1)
    with pytest.raises(ValueError, match="key mismatch"):
        validate_state_dicts(state, changed)

    model_path = tmp_path / "model.safetensors"
    safetensors.save_file(state, str(model_path))
    validate_saved_state(model, model_path)


def test_ordered_validation_comparison_is_exact():
    result = {
        "prediction_ids": [[0, 4]],
        "label_ids": [[0, 4]],
        "invalid_paths": 0,
        "metrics": {"f1": 1.0},
    }
    compare_ordered_validation_results(result, dict(result))
    for field, value in (
        ("prediction_ids", [[4, 0]]),
        ("label_ids", [[4, 0]]),
        ("invalid_paths", 1),
        ("metrics", {"f1": 0.0}),
    ):
        changed = dict(result)
        changed[field] = value
        with pytest.raises(ValueError, match=field):
            compare_ordered_validation_results(result, changed)


def write_complete_artifact(directory, tmp_path, selected="checkpoint-1"):
    directory.mkdir(parents=True)
    files = {
        "config.json": "{}\n",
        "model.safetensors": "weights",
        "special_tokens_map.json": "{}\n",
        "tokenizer_config.json": "{}\n",
        "tokenizer.json": "{}\n",
    }
    for name, content in files.items():
        (directory / name).write_text(content, encoding="utf-8")
    config = make_config(tmp_path / "artifact-config")
    artifact_config = training._artifact_config(config, REVISION)
    write_json_atomic(directory / "train_config.json", artifact_config)
    manifest = {
        "schema": training.MANIFEST_SCHEMA,
        "state": "success",
        "config": serializable_config(config),
        "contracts": {
            "artifact_schema": ARTIFACT_SCHEMA,
            "constraint_contract": CONSTRAINT_CONTRACT,
            "labels": list(LABELS),
        },
        "dataset": {"paths": {}, "h0": {}, "h1": {}, "h2": {}, "report": {}},
        "model_identity": {
            "name": config.model_name,
            "requested_revision": REVISION,
            "resolved_tokenizer_revision": REVISION,
            "resolved_backbone_revision": REVISION,
        },
        "source": {
            "repository": "example/repository",
            "root": "repository",
            "branch": "test",
            "commit": REVISION,
            "dirty": False,
        },
        "runtime": {
            "python": "3",
            "platform": "test",
            "torch": "test",
            "transformers": "test",
            "optimizer": {"configured": "adamw"},
            "precision": "fp32",
        },
        "completed_checks": ["test"],
        "selected_checkpoint": selected,
        "best_validation_f1": 1.0,
        "validation_metrics": {"f1": 1.0},
        "ordered_validation": {"metrics": {"f1": 1.0}},
        "test_metrics": None,
        "artifact_files": training._all_file_hashes(directory),
        "log_history": [],
    }
    write_json_atomic(directory / "run_manifest.json", manifest)
    return {
        "schema": ARTIFACT_SCHEMA,
        "constraint_contract": CONSTRAINT_CONTRACT,
        "selected_checkpoint": selected,
        "run_manifest_sha256": sha256(directory / "run_manifest.json"),
        "files": training._all_file_hashes(directory),
    }


def make_publishable_model(tmp_path):
    model_dir = tmp_path / "final-model"
    marker = write_complete_artifact(model_dir, tmp_path)
    write_json_atomic(model_dir / "SUCCESS.json", marker)
    return model_dir


def test_publishability_requires_marker_exact_inventory_and_hashes(tmp_path):
    model_dir = make_publishable_model(tmp_path)
    assert validate_publishable_model(model_dir)["schema"] == ARTIFACT_SCHEMA

    (model_dir / "model.safetensors").write_bytes(b"tampered")
    with pytest.raises(ValueError, match="hash mismatch"):
        validate_publishable_model(model_dir)


def test_publishability_rejects_missing_marker_and_unrecorded_file(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(ValueError, match="Success_Marker"):
        validate_publishable_model(empty)

    model_dir = make_publishable_model(tmp_path / "nested")
    (model_dir / "extra").write_text("not recorded")
    with pytest.raises(ValueError, match="inventory"):
        validate_publishable_model(model_dir)


def test_cli_requires_revision_and_describes_isr_as_locatability(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, ["--data-dir", str(tmp_path), "--with-isr"])
    assert result.exit_code == 2
    assert "Missing option '--model-revision'" in result.output
    help_result = runner.invoke(main, ["--help"])
    assert "predicted-phrase locatability" in help_result.output
    assert "Resume" not in help_result.output


def test_cli_rejects_resume_and_isr_without_test(tmp_path):
    arguments = [
        "--data-dir", str(tmp_path), "--model-revision", REVISION,
    ]
    result = CliRunner().invoke(main, arguments + ["--with-isr"])
    assert result.exit_code == 2
    assert "--with-isr requires --evaluate-test" in result.output
    result = CliRunner().invoke(main, arguments + ["--resume"])
    assert result.exit_code == 2
    assert "--resume is unsupported" in result.output


def test_tokenizer_revision_uses_the_requested_hub_commit(monkeypatch):
    calls = []

    def get_model_info(model_name, revision):
        calls.append((model_name, revision))
        return types.SimpleNamespace(sha=REVISION)

    hub = types.ModuleType("huggingface_hub")
    hub.model_info = get_model_info
    monkeypatch.setitem(__import__("sys").modules, "huggingface_hub", hub)

    assert resolve_tokenizer_revision("model", REVISION) == REVISION
    assert calls == [("model", REVISION)]

    hub.model_info = lambda *args, **kwargs: types.SimpleNamespace(sha="main")
    with pytest.raises(ValueError, match="full immutable commit"):
        resolve_tokenizer_revision("model", REVISION)


def test_model_identity_requires_exact_tokenizer_and_backbone_commits():
    backbone = type("BackboneConfig", (), {"_commit_hash": REVISION})()
    assert resolve_model_identity(REVISION, REVISION, backbone) == REVISION

    backbone._commit_hash = "b" * 40
    with pytest.raises(ValueError, match="inconsistent"):
        resolve_model_identity(REVISION, REVISION, backbone)
    with pytest.raises(ValueError, match="inconsistent"):
        resolve_model_identity(REVISION, "b" * 40, backbone)


def test_source_provenance_uses_narrow_git_values_and_no_environment(monkeypatch, tmp_path):
    values = {
        ("rev-parse", "--show-toplevel"): str(tmp_path),
        ("branch", "--show-current"): "gsoc/training-pipeline",
        ("rev-parse", "HEAD"): REVISION,
        ("config", "--get", "remote.origin.url"): "https://secret@example.com/project.git",
        ("status", "--porcelain"): " M allowed.py",
    }
    monkeypatch.setattr(training, "_run_git", lambda _root, *args: values[args])
    monkeypatch.setenv("SECRET_TOKEN", "must-not-appear")
    provenance = training.collect_source_provenance(tmp_path)
    serialized = json.dumps(provenance)
    assert provenance["repository"] == "https://example.com/project.git"
    assert provenance["branch"] == "gsoc/training-pipeline"
    assert provenance["commit"] == REVISION
    assert provenance["dirty"] is True
    assert "SECRET_TOKEN" not in serialized
    assert "must-not-appear" not in serialized


def test_promotion_writes_marker_last_and_is_publishable(tmp_path):
    stage = tmp_path / "final-model.tmp"
    marker = write_complete_artifact(stage, tmp_path)
    destination = tmp_path / "final-model"
    promote_final_model(stage, destination, marker)
    assert not stage.exists()
    assert validate_publishable_model(destination) == marker


def test_promotion_marker_failure_rolls_back_and_leaves_no_final_model(
    monkeypatch, tmp_path
):
    stage = tmp_path / "final-model.tmp"
    stage.mkdir()
    (stage / "model.safetensors").write_bytes(b"weights")
    destination = tmp_path / "final-model"

    def fail_marker(path, value):
        raise OSError("injected marker failure")

    monkeypatch.setattr(training, "write_json_atomic", fail_marker)
    with pytest.raises(OSError, match="injected marker failure"):
        promote_final_model(stage, destination, {})
    assert stage.is_dir()
    assert not destination.exists()
    assert not (stage / "SUCCESS.json").exists()


class RejectingLateTokenizer(FakeTokenizer):
    def __call__(self, tokens, truncation=False, max_length=512, **kwargs):
        if tokens[0] == "bad":
            return FakeEncoding([None, 0, None])
        return super().__call__(tokens, truncation, max_length, **kwargs)


def test_limit_does_not_hide_late_alignment_rejections(tmp_path):
    records = {
        "train": [
            make_record("selected.RULE"),
            make_record(
                "rejected.RULE",
                tokens=["bad", "record"],
                labels=["B-REQ", "E-REQ"],
            ),
        ],
        "validation": [make_record("val.RULE")],
        "test": [make_record("test.RULE")],
    }
    loaded, _report = load_and_validate_splits(make_split_paths(tmp_path, records))
    datasets, h2 = build_effective_datasets(
        loaded, RejectingLateTokenizer(), max_length=512, limit=1
    )
    assert datasets["train"].identifiers == ["selected.RULE"]
    assert datasets["train"].rejections[0]["identifier"] == "rejected.RULE"
    assert datasets["train"].rejections[0]["reason"] == "zero-coverage"
    assert h2["train"]["rejected_count"] == 1


def test_split_with_no_effective_example_is_rejected(tmp_path):
    bad = make_record(
        "bad.RULE", tokens=["bad", "record"], labels=["B-REQ", "E-REQ"]
    )
    records = {
        "train": [bad],
        "validation": [make_record("val.RULE")],
        "test": [make_record("test.RULE")],
    }
    loaded, _report = load_and_validate_splits(make_split_paths(tmp_path, records))
    with pytest.raises(ValueError, match="train split has no selected Effective_Example"):
        build_effective_datasets(loaded, RejectingLateTokenizer(), 512)


def test_failure_manifest_is_atomic_scoped_and_reports_retained_paths(tmp_path):
    manifest_path = tmp_path / "run_manifest.json"
    retained = tmp_path / "dataset_report.json"
    retained.write_text("{}\n")
    value = write_failure_manifest(
        manifest_path,
        {"schema": "run-v2", "state": "pre-run"},
        "offline-reload",
        ValueError("state mismatch"),
        ["configuration", "training"],
        [retained, tmp_path / "absent"],
    )
    assert json.loads(manifest_path.read_text()) == value
    assert value["state"] == "failure"
    assert value["failed_phase"] == "offline-reload"
    assert value["exception"] == {"type": "ValueError", "message": "state mismatch"}
    assert value["completed_checks"] == ["configuration", "training"]
    assert value["retained_artifacts"] == [str(retained)]
    assert "environment" not in value


def test_duplicate_check_waits_until_every_raw_record_is_validated(tmp_path):
    records = {
        "train": [make_record("duplicate.RULE")],
        "validation": [make_record("duplicate.RULE")],
        "test": [make_record("test.RULE")],
    }
    paths = make_split_paths(tmp_path, records)
    with paths["test"].open("a", encoding="utf-8") as stream:
        stream.write("{malformed}\n")
    with pytest.raises(ValueError, match=r"test\.jsonl line 2: malformed JSON"):
        load_and_validate_splits(paths)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("epochs", 1_001),
        ("batch_size", 1_025),
        ("base_lr", 1.1),
        ("weight_decay", 1.1),
        ("aux_ce_weight", 101),
        ("label_weights", [1.0, 2.0, 1.5, 1.5, 1_000_001]),
    ],
)
def test_config_numeric_contracts_are_upper_bounded(tmp_path, field, value):
    config = make_config(tmp_path)
    setattr(config, field, value)
    with pytest.raises(ValueError):
        validate_config(config)


@pytest.mark.parametrize(
    ("full_ids", "retained_ids", "reason"),
    [
        ([0, 1, None], [0, 1, None], "missing-special-token"),
        ([None, 0, 1], [None, 0, 1], "missing-special-token"),
        ([None, 0, None, 1, None], [None, 0, None, 1, None], "coverage-gap"),
    ],
)
def test_alignment_requires_boundary_specials_and_no_internal_specials(
    full_ids, retained_ids, reason
):
    with pytest.raises(AlignmentError) as caught:
        align_labels(
            ["MIT", "License"],
            ["B-REQ", "E-REQ"],
            FakeTokenizer(full_ids, retained_ids),
            8,
        )
    assert caught.value.reason == reason


def test_alignment_rejects_word_id_and_model_input_shape_mismatch():
    class BadShapeTokenizer(FakeTokenizer):
        def __call__(self, tokens, **kwargs):
            encoding = FakeEncoding([None, 0, 1, None])
            encoding["attention_mask"].pop()
            return encoding

    with pytest.raises(AlignmentError) as caught:
        align_labels(
            ["MIT", "License"], ["B-REQ", "E-REQ"], BadShapeTokenizer(), 8
        )
    assert caught.value.reason == "shape-mismatch"


def test_publishability_requires_complete_reloadable_inventory(tmp_path):
    model_dir = make_publishable_model(tmp_path)
    (model_dir / "config.json").unlink()
    marker = json.loads((model_dir / "SUCCESS.json").read_text())
    marker["files"].pop("config.json")
    write_json_atomic(model_dir / "SUCCESS.json", marker)
    with pytest.raises(ValueError, match="missing required files"):
        validate_publishable_model(model_dir)


def test_publishability_rejects_unknown_artifact_configuration_fields(tmp_path):
    model_dir = make_publishable_model(tmp_path)
    config_path = model_dir / "train_config.json"
    config = json.loads(config_path.read_text())
    config["unknown"] = True
    write_json_atomic(config_path, config)
    marker = json.loads((model_dir / "SUCCESS.json").read_text())
    marker["files"]["train_config.json"] = sha256(config_path)
    write_json_atomic(model_dir / "SUCCESS.json", marker)
    with pytest.raises(ValueError, match="artifact hashes|configuration fields differ"):
        validate_publishable_model(model_dir)


def test_local_loader_loads_saved_values_after_structural_validation(
    monkeypatch, tmp_path
):
    torch = pytest.importorskip("torch")
    safetensors = pytest.importorskip("safetensors.torch")
    transformers = pytest.importorskip("transformers")
    import phrase_model as model_module

    model_dir = tmp_path / "model"
    model_dir.mkdir()
    config = make_config(tmp_path)
    write_json_atomic(
        model_dir / "train_config.json",
        training._artifact_config(config, REVISION),
    )
    safetensors.save_file(
        {"weight": torch.tensor([3.0])},
        str(model_dir / "model.safetensors"),
    )

    class LocalTagger(torch.nn.Module):
        def __init__(self, config, backbone=None):
            super().__init__()
            self.weight = torch.nn.Parameter(torch.tensor([0.0]))

    class LocalTokenizer:
        is_fast = True

    monkeypatch.setattr(model_module, "PhraseTagger", LocalTagger)
    monkeypatch.setattr(
        transformers.AutoConfig,
        "from_pretrained",
        lambda *args, **kwargs: object(),
    )
    monkeypatch.setattr(
        transformers.AutoModel,
        "from_config",
        lambda config: object(),
    )
    monkeypatch.setattr(
        transformers.AutoTokenizer,
        "from_pretrained",
        lambda *args, **kwargs: LocalTokenizer(),
    )

    loaded, tokenizer = training._load_local_model(model_dir)

    assert loaded.weight.item() == 3.0
    assert tokenizer.is_fast


def test_final_model_loader_rejects_unpublished_stage_before_local_loading(
    monkeypatch, tmp_path
):
    stage = tmp_path / "final-model.tmp"
    stage.mkdir()
    monkeypatch.setattr(
        training,
        "_load_local_model",
        lambda *args, **kwargs: pytest.fail("unpublished artifact must not load"),
    )
    with pytest.raises(ValueError, match="Success_Marker"):
        training.load_final_model(stage)


def test_repository_identity_removes_all_url_credentials():
    assert training._redacted_repository_identity(
        "https://user:password@example.com/repo.git?token=secret#credential"
    ) == "https://example.com/repo.git"
    assert training._redacted_repository_identity(
        "git@example.com:aboutcode/repo.git"
    ) == "example.com:aboutcode/repo.git"


def test_selected_checkpoint_must_be_a_child_directory(tmp_path):
    state = type("State", (), {"best_model_checkpoint": str(tmp_path), "best_metric": 1.0})()
    trainer = type("Trainer", (), {"state": state})()
    with pytest.raises(ValueError, match="inside run output"):
        training.validate_selected_checkpoint(trainer, tmp_path)

    outside = tmp_path.parent / "outside-checkpoint"
    outside.mkdir(exist_ok=True)
    state.best_model_checkpoint = str(outside)
    with pytest.raises(ValueError, match="inside run output"):
        training.validate_selected_checkpoint(trainer, tmp_path)


def test_run_training_validates_every_raw_line_before_tokenizer_loading(
    monkeypatch, tmp_path
):
    config = make_config(tmp_path)
    with (config.data_dir / "test.jsonl").open("a", encoding="utf-8") as stream:
        stream.write("{malformed}\n")
    calls = []

    class AutoTokenizer:
        @staticmethod
        def from_pretrained(*args, **kwargs):
            calls.append((args, kwargs))
            pytest.fail("tokenizer must not load before complete raw validation")

    fake_transformers = types.ModuleType("transformers")
    fake_transformers.AutoConfig = object
    fake_transformers.AutoTokenizer = AutoTokenizer
    fake_transformers.DataCollatorForTokenClassification = object
    fake_transformers.EarlyStoppingCallback = object
    fake_transformers.TrainingArguments = object
    fake_model = types.ModuleType("phrase_model")
    fake_model.PhraseTagger = object
    fake_model.PhraseTrainer = object
    fake_model.build_optimizer = object
    modules = __import__("sys").modules
    monkeypatch.setitem(modules, "transformers", fake_transformers)
    monkeypatch.setitem(modules, "torch", types.ModuleType("torch"))
    monkeypatch.setitem(modules, "phrase_model", fake_model)
    monkeypatch.setattr(training, "validate_precision", lambda precision: None)

    with pytest.raises(ValueError, match=r"test\.jsonl line 2: malformed JSON"):
        training.run_training(config)
    assert calls == []
    assert not config.output_dir.exists()


def test_run_training_records_offline_reload_failure_without_publication(
    monkeypatch, tmp_path
):
    config = make_config(tmp_path)
    raw_report = {
        "h0": {},
        "h1": {},
        "duplicates": {"tokens": [], "labels": []},
        "raw_counts": {"train": 1, "validation": 1, "test": 1},
    }
    records = {name: [] for name in ("train", "validation", "test")}

    class Dataset:
        examples = [{"input_ids": [1], "attention_mask": [1], "labels": [0]}]
        effective_inventory = examples
        rejections = []
        truncations = []
        truncated = 0
        cut_phrases = 0

        def __len__(self):
            return 1

    datasets = {name: Dataset() for name in records}
    h2 = {name: {"sha256": name} for name in records}

    class Tokenizer:
        is_fast = True
        init_kwargs = {"_commit_hash": REVISION}

    class AutoTokenizer:
        @staticmethod
        def from_pretrained(*args, **kwargs):
            return Tokenizer()

    class AutoConfig:
        @staticmethod
        def from_pretrained(*args, **kwargs):
            return types.SimpleNamespace(_commit_hash=REVISION)

    class TrainingArguments:
        def __init__(self, output_dir, **kwargs):
            self.output_dir = output_dir

    class EarlyStoppingCallback:
        def __init__(self, **kwargs):
            pass

    class PhraseTagger:
        def __init__(self, config):
            self.backbone = types.SimpleNamespace(
                config=types.SimpleNamespace(_commit_hash=REVISION)
            )

        def state_dict(self):
            return {"weight": object()}

    class PhraseTrainer:
        def __init__(self, model, args, **kwargs):
            self.model = model
            self.args = args
            self.state = types.SimpleNamespace(
                best_model_checkpoint=None,
                best_metric=1.0,
                log_history=[],
            )

        def train(self):
            checkpoint = Path(self.args.output_dir) / "checkpoint-1"
            checkpoint.mkdir()
            (checkpoint / "model.safetensors").write_bytes(b"checkpoint")
            self.state.best_model_checkpoint = str(checkpoint)

        def remove_callback(self, callback):
            pass

        def evaluate(self, dataset, metric_key_prefix):
            return {f"{metric_key_prefix}_f1": 1.0}

    fake_transformers = types.ModuleType("transformers")
    fake_transformers.AutoConfig = AutoConfig
    fake_transformers.AutoTokenizer = AutoTokenizer
    fake_transformers.DataCollatorForTokenClassification = lambda *args, **kwargs: object()
    fake_transformers.EarlyStoppingCallback = EarlyStoppingCallback
    fake_transformers.TrainingArguments = TrainingArguments
    fake_model = types.ModuleType("phrase_model")
    fake_model.PhraseTagger = PhraseTagger
    fake_model.PhraseTrainer = PhraseTrainer
    fake_model.build_optimizer = lambda config, model: None
    modules = __import__("sys").modules
    monkeypatch.setitem(modules, "torch", types.ModuleType("torch"))
    monkeypatch.setitem(modules, "transformers", fake_transformers)
    monkeypatch.setitem(modules, "phrase_model", fake_model)
    monkeypatch.setattr(training, "validate_precision", lambda precision: None)
    monkeypatch.setattr(
        training,
        "resolve_tokenizer_revision",
        lambda model_name, requested: REVISION,
    )
    monkeypatch.setattr(training, "validate_raw_split_hashes", lambda paths, hashes: None)
    monkeypatch.setattr(training, "set_seed", lambda seed: None)
    monkeypatch.setattr(
        training,
        "load_and_validate_splits",
        lambda paths: (records, raw_report),
    )
    monkeypatch.setattr(
        training,
        "build_effective_datasets",
        lambda records, tokenizer, max_length, limit: (datasets, h2),
    )
    monkeypatch.setattr(
        training,
        "collect_source_provenance",
        lambda: {
            "repository": "example/repository",
            "root": "repository",
            "branch": "test",
            "commit": REVISION,
            "dirty": False,
        },
    )
    monkeypatch.setattr(
        training,
        "collect_runtime_provenance",
        lambda optimizer, precision: {"optimizer": optimizer, "precision": precision},
    )
    monkeypatch.setattr(training, "_load_state_file", lambda path: {"weight": object()})
    monkeypatch.setattr(training, "validate_state_dicts", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        training,
        "collect_ordered_validation_result",
        lambda model, dataset, use_crf: {
            "prediction_ids": [[0]],
            "label_ids": [[0]],
            "invalid_paths": 0,
            "metrics": {"f1": 1.0},
        },
    )

    def stage_final_model(output_dir, model, tokenizer, artifact_config):
        stage = Path(output_dir) / "final-model.tmp"
        stage.mkdir()
        (stage / "model.safetensors").write_bytes(b"staged")
        return stage

    monkeypatch.setattr(training, "stage_final_model", stage_final_model)
    monkeypatch.setattr(
        training,
        "_load_local_model",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("offline failure")),
    )

    with pytest.raises(RuntimeError, match="offline failure"):
        training.run_training(config)

    manifest = json.loads((config.output_dir / "run_manifest.json").read_text())
    assert manifest["state"] == "failure"
    assert manifest["failed_phase"] == "offline-reload"
    assert str(config.output_dir / "checkpoint-1") in manifest["retained_artifacts"]
    assert str(config.output_dir / "final-model.tmp") in manifest["retained_artifacts"]
    assert not (config.output_dir / "final-model").exists()
    assert not (config.output_dir / "final-model.tmp" / "SUCCESS.json").exists()


def test_alignment_rejects_invalid_model_ids_and_inactive_masks():
    class InvalidModelInputTokenizer(FakeTokenizer):
        def __init__(self, input_ids=None, attention_mask=None):
            super().__init__()
            self.input_ids = input_ids
            self.attention_mask = attention_mask

        def __call__(self, tokens, **kwargs):
            encoding = super().__call__(tokens, **kwargs)
            if self.input_ids is not None:
                encoding["input_ids"] = self.input_ids
            if self.attention_mask is not None:
                encoding["attention_mask"] = self.attention_mask
            return encoding

    with pytest.raises(AlignmentError) as caught:
        align_labels(
            ["MIT", "License"],
            ["B-REQ", "E-REQ"],
            InvalidModelInputTokenizer(input_ids=[0, 100, 11, 1]),
            8,
        )
    assert caught.value.reason == "invalid-input-id"

    with pytest.raises(AlignmentError) as caught:
        align_labels(
            ["MIT", "License"],
            ["B-REQ", "E-REQ"],
            InvalidModelInputTokenizer(attention_mask=[0, 0, 0, 0]),
            8,
        )
    assert caught.value.reason == "invalid-attention-mask"


def test_publishability_rejects_rehashed_incomplete_success_manifest(tmp_path):
    model_dir = make_publishable_model(tmp_path)
    manifest_path = model_dir / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    del manifest["source"]
    write_json_atomic(manifest_path, manifest)
    marker_path = model_dir / "SUCCESS.json"
    marker = json.loads(marker_path.read_text())
    marker["run_manifest_sha256"] = sha256(manifest_path)
    marker["files"]["run_manifest.json"] = sha256(manifest_path)
    write_json_atomic(marker_path, marker)
    with pytest.raises(ValueError, match="manifest fields"):
        validate_publishable_model(model_dir)
