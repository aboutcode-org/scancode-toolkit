# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import json
from pathlib import Path
import sys

from click.testing import CliRunner
import pytest

sys.path.insert(0, str(Path(__file__).parent))

from train_model import align_labels
from train_model import compute_metrics
from train_model import Config
from train_model import decode_row
from train_model import extract_spans
from train_model import first_subword_positions
from train_model import IGNORE_INDEX
from train_model import LABEL2ID
from train_model import main
from train_model import PhraseDataset
from train_model import prepare_output_dir
from train_model import serializable_config
from train_model import sha256
from train_model import validate_bioes
from train_model import validate_config
from train_model import validate_record
from train_model import validate_saved_state
from train_model import validate_splits


class FakeEncoding(dict):
    def __init__(self, word_ids):
        super().__init__()
        self._word_ids = word_ids
        self["input_ids"] = [0] * len(word_ids)
        self["attention_mask"] = [1] * len(word_ids)

    def word_ids(self):
        return self._word_ids


class FakeTokenizer:
    def __call__(self, tokens, max_length=512, **kwargs):
        word_ids = [None, *range(len(tokens)), None]
        return FakeEncoding(word_ids[:max_length])


def make_record(identifier="mit_1.RULE", tokens=None, labels=None):
    return {
        "identifier": identifier,
        "license_expression": "mit",
        "rule_type": "is_license_notice",
        "text": "MIT License terms apply",
        "tokens": tokens or ["MIT", "License", "terms", "apply"],
        "bioes_labels": labels or ["B-REQ", "E-REQ", "O", "O"],
    }


def write_jsonl(path, records):
    path.write_text(
        "".join(json.dumps(record) + "\n" for record in records),
        encoding="utf-8",
    )


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
    [
        [],
        ["I-REQ"],
        ["E-REQ"],
        ["B-REQ", "O"],
        ["O", "I-REQ"],
        ["B-REQ", "I-REQ"],
    ],
)
def test_validate_bioes_rejects_invalid_sequences(labels):
    assert validate_bioes(labels)


def test_validate_record_accepts_a_complete_record():
    record = make_record()
    assert validate_record(record, "train.jsonl", 1) is record


@pytest.mark.parametrize(
    "field_name",
    ["identifier", "license_expression", "rule_type", "text", "tokens", "bioes_labels"],
)
def test_validate_record_rejects_a_missing_field(field_name):
    record = make_record()
    del record[field_name]
    with pytest.raises(ValueError, match=field_name):
        validate_record(record, "train.jsonl", 4)


def test_validate_record_rejects_mismatched_tokens_and_labels():
    record = make_record(labels=["S-REQ"])
    with pytest.raises(ValueError, match="tokens and"):
        validate_record(record, "train.jsonl", 2)


def test_validate_record_rejects_unknown_labels():
    record = make_record(labels=["B-REQ", "BAD", "O", "O"])
    with pytest.raises(ValueError, match="unknown labels"):
        validate_record(record, "train.jsonl", 2)


def test_align_labels_keeps_only_first_subwords():
    tokenizer = lambda tokens, **kwargs: FakeEncoding([None, 0, 1, 1, None])
    encoding, truncated, cut_phrase = align_labels(
        ["MIT", "License"],
        ["B-REQ", "E-REQ"],
        tokenizer,
        512,
    )
    assert encoding["labels"] == [
        IGNORE_INDEX,
        LABEL2ID["B-REQ"],
        LABEL2ID["E-REQ"],
        IGNORE_INDEX,
        IGNORE_INDEX,
    ]
    assert not truncated
    assert not cut_phrase


def test_align_labels_detects_a_phrase_cut_by_truncation():
    encoding, truncated, cut_phrase = align_labels(
        ["prefix", "GNU", "General", "Public", "License"],
        ["O", "B-REQ", "I-REQ", "I-REQ", "E-REQ"],
        FakeTokenizer(),
        4,
    )
    assert encoding["labels"][-1] == LABEL2ID["I-REQ"]
    assert truncated
    assert cut_phrase


def test_align_labels_allows_safe_truncation():
    _, truncated, cut_phrase = align_labels(
        ["MIT", "License", "terms", "apply"],
        ["B-REQ", "E-REQ", "O", "O"],
        FakeTokenizer(),
        4,
    )
    assert truncated
    assert not cut_phrase


def test_phrase_dataset_skips_a_cut_phrase(tmp_path):
    path = tmp_path / "train.jsonl"
    write_jsonl(
        path,
        [
            make_record(identifier="safe.RULE"),
            make_record(
                identifier="cut.RULE",
                tokens=["prefix", "GNU", "General", "Public", "License"],
                labels=["O", "B-REQ", "I-REQ", "I-REQ", "E-REQ"],
            ),
        ],
    )

    dataset = PhraseDataset(path, FakeTokenizer(), max_length=4)

    assert dataset.identifiers == ["safe.RULE"]
    assert dataset.truncated == 2
    assert dataset.cut_phrases == 1


def test_validate_splits_with_real_dataset_objects(tmp_path):
    paths = {}
    for name, identifier in (("train", "a.RULE"), ("validation", "b.RULE")):
        path = tmp_path / f"{name}.jsonl"
        write_jsonl(path, [make_record(identifier=identifier)])
        paths[name] = PhraseDataset(path, FakeTokenizer(), 512)
    validate_splits(paths)


def test_validate_splits_rejects_duplicate_identifiers(tmp_path):
    datasets = {}
    for name in ("train", "validation"):
        path = tmp_path / f"{name}.jsonl"
        write_jsonl(path, [make_record(identifier="same.RULE")])
        datasets[name] = PhraseDataset(path, FakeTokenizer(), 512)
    with pytest.raises(ValueError, match="both train and validation"):
        validate_splits(datasets)


@pytest.mark.parametrize(
    "tags, expected",
    [
        (["O", "B-REQ", "I-REQ", "E-REQ", "O"], {(1, 3)}),
        (["O", "S-REQ", "O"], {(1, 1)}),
        (["S-REQ", "O", "B-REQ", "E-REQ"], {(0, 0), (2, 3)}),
        (["O", "O"], set()),
    ],
)
def test_extract_spans(tags, expected):
    assert extract_spans(tags) == expected


def test_decode_row_drops_ignored_positions():
    predicted, actual = decode_row(
        [LABEL2ID["B-REQ"], 0, LABEL2ID["E-REQ"]],
        [LABEL2ID["B-REQ"], IGNORE_INDEX, LABEL2ID["E-REQ"]],
    )
    assert predicted == ["B-REQ", "E-REQ"]
    assert actual == ["B-REQ", "E-REQ"]


def test_compute_metrics_scores_exact_spans():
    predictions = [[LABEL2ID["B-REQ"], LABEL2ID["E-REQ"], LABEL2ID["O"]]]
    labels = [[LABEL2ID["B-REQ"], LABEL2ID["E-REQ"], LABEL2ID["O"]]]
    scores = compute_metrics((predictions, labels))
    assert scores["f1"] == 1.0
    assert scores["exact_match"] == 1.0
    assert scores["predicted_spans"] == scores["gold_spans"] == 1


def test_first_subword_positions_skips_specials_and_continuations():
    assert first_subword_positions([None, 0, 1, 1, 2, None]) == [1, 2, 4]


def test_sha256_is_stable(tmp_path):
    path = tmp_path / "data.jsonl"
    path.write_bytes(b"required phrase\n")
    assert sha256(path) == "792616e2062f96efb6ae2f69e8637b834e2db74354eb4f51e78eda329038cc70"


def test_serializable_config_converts_paths(tmp_path):
    config = Config(data_dir=tmp_path / "data", output_dir=tmp_path / "model")
    values = serializable_config(config)
    assert values["data_dir"] == str(tmp_path / "data")
    assert values["output_dir"] == str(tmp_path / "model")


def test_validate_config_accepts_the_default_training_settings(tmp_path):
    config = Config(data_dir=tmp_path / "data", output_dir=tmp_path / "model")
    validate_config(config)


def test_validate_config_rejects_invalid_settings(tmp_path):
    config = Config(
        data_dir=tmp_path / "data",
        output_dir=tmp_path / "model",
        aux_ce_weight=-1,
    )
    with pytest.raises(ValueError, match="cannot be negative"):
        validate_config(config)


def test_prepare_output_dir_refuses_to_overwrite_a_run(tmp_path):
    output_dir = tmp_path / "model"
    output_dir.mkdir()
    (output_dir / "model.safetensors").write_bytes(b"model")

    with pytest.raises(ValueError, match="not empty"):
        prepare_output_dir(output_dir, resume=False)


def test_prepare_output_dir_requires_a_checkpoint_to_resume(tmp_path):
    with pytest.raises(ValueError, match="No checkpoint"):
        prepare_output_dir(tmp_path / "model", resume=True)


def test_validate_saved_state_accepts_matching_tensors(tmp_path):
    torch = pytest.importorskip("torch")
    safetensors = pytest.importorskip("safetensors.torch")

    model = torch.nn.Linear(2, 1)
    path = tmp_path / "model.safetensors"
    safetensors.save_file(model.state_dict(), str(path))
    validate_saved_state(model, path)


def test_validate_saved_state_rejects_unexpected_keys(tmp_path):
    torch = pytest.importorskip("torch")
    safetensors = pytest.importorskip("safetensors.torch")

    model = torch.nn.Linear(2, 1)
    state = dict(model.state_dict())
    state["unexpected"] = torch.ones(1)
    path = tmp_path / "model.safetensors"
    safetensors.save_file(state, str(path))
    with pytest.raises(ValueError, match="key mismatch"):
        validate_saved_state(model, path)


def test_validate_saved_state_rejects_wrong_shapes(tmp_path):
    torch = pytest.importorskip("torch")
    safetensors = pytest.importorskip("safetensors.torch")

    model = torch.nn.Linear(2, 1)
    state = dict(model.state_dict())
    state["weight"] = torch.ones((1, 3))
    path = tmp_path / "model.safetensors"
    safetensors.save_file(state, str(path))
    with pytest.raises(ValueError, match="has shape"):
        validate_saved_state(model, path)


def test_validate_saved_state_rejects_non_finite_values(tmp_path):
    torch = pytest.importorskip("torch")
    safetensors = pytest.importorskip("safetensors.torch")

    model = torch.nn.Linear(2, 1)
    state = dict(model.state_dict())
    state["weight"] = torch.full_like(state["weight"], float("nan"))
    path = tmp_path / "model.safetensors"
    safetensors.save_file(state, str(path))
    with pytest.raises(ValueError, match="non-finite"):
        validate_saved_state(model, path)


def test_cli_requires_test_evaluation_for_isr(tmp_path):
    result = CliRunner().invoke(main, ["--data-dir", str(tmp_path), "--with-isr"])
    assert result.exit_code == 2
    assert "--with-isr requires --evaluate-test" in result.output
