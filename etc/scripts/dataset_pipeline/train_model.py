# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Train a DeBERTa BIOES tagger for required phrase spans."""

from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from functools import partial
import hashlib
import importlib.metadata
import inspect
import json
import math
from numbers import Integral
import os
from pathlib import Path
import platform
import random
import re
import subprocess
import tempfile
from types import SimpleNamespace
from urllib.parse import urlsplit
from urllib.parse import urlunsplit

import click

os.environ.setdefault("USE_TF", "0")


LABELS = ("O", "B-REQ", "I-REQ", "E-REQ", "S-REQ")
LABEL2ID = {label: index for index, label in enumerate(LABELS)}
ID2LABEL = {index: label for index, label in enumerate(LABELS)}
IGNORE_INDEX = -100
ARTIFACT_SCHEMA = "scancode-required-phrases-model-v2"
CONSTRAINT_CONTRACT = "bioes-hard-v1"
H0_SERIALIZER = "raw-bytes-v1"
H1_SERIALIZER = "validated-records-canonical-json-v1"
H2_SERIALIZER = "effective-examples-canonical-json-v1"
MANIFEST_SCHEMA = "scancode-required-phrases-run-v2"
REQUIRED_ARTIFACT_FILES = {
    "config.json",
    "model.safetensors",
    "special_tokens_map.json",
    "tokenizer_config.json",
    "train_config.json",
    "run_manifest.json",
}
TOKENIZER_MODEL_FILES = {"tokenizer.json", "spiece.model", "sentencepiece.bpe.model"}

MODEL_NAME = "microsoft/deberta-v3-large"
MAX_LENGTH = 512
IMMUTABLE_REVISION = re.compile(r"^[0-9a-fA-F]{40}$")
RECORD_FIELDS = (
    "identifier",
    "license_expression",
    "rule_type",
    "text",
    "tokens",
    "bioes_labels",
)
START_LABELS = {"O", "B-REQ", "S-REQ"}
END_LABELS = {"O", "E-REQ", "S-REQ"}
VALID_TRANSITIONS = {
    "O": {"O", "B-REQ", "S-REQ"},
    "B-REQ": {"I-REQ", "E-REQ"},
    "I-REQ": {"I-REQ", "E-REQ"},
    "E-REQ": {"O", "B-REQ", "S-REQ"},
    "S-REQ": {"O", "B-REQ", "S-REQ"},
}


@dataclass
class Config:
    """Settings for one training run."""

    data_dir: Path
    output_dir: Path
    model_name: str = MODEL_NAME
    model_revision: str | None = None
    max_length: int = MAX_LENGTH

    epochs: int = 8
    batch_size: int = 1
    grad_accum: int = 16
    base_lr: float = 2e-5
    head_lr: float = 1e-4
    layer_decay: float = 0.98
    weight_decay: float = 0.01
    warmup_ratio: float = 0.1
    max_grad_norm: float = 0.5
    adam_epsilon: float = 1e-6
    early_stopping_patience: int = 3
    optimizer: str = "adamw"
    precision: str = "fp32"

    limit: int = 0
    resume: bool = False
    use_crf: bool = True
    aux_ce_weight: float = 0.3
    evaluate_test: bool = False
    with_isr: bool = False
    seed: int = 42

    label_weights: list = field(default_factory=lambda: [1.0, 2.0, 1.5, 1.5, 2.0])


@dataclass(frozen=True)
class RecordLocation:
    split: str
    path: Path
    line: int

    def __str__(self):
        return f"{self.split} split, {self.path} line {self.line}"


@dataclass(frozen=True)
class ValidatedRecord:
    record: dict
    location: RecordLocation

    @property
    def identifier(self):
        return self.record["identifier"]


class AlignmentError(ValueError):
    """Raised when tokenizer coverage cannot preserve a record safely."""

    def __init__(self, reason, detail):
        super().__init__(detail)
        self.reason = reason


def _require_exact_type(name, value, expected):
    if type(value) is not expected:
        raise TypeError(f"{name} must be {expected.__name__}, not {type(value).__name__}")


def _require_finite_number(name, value, minimum=None, maximum=None, minimum_open=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a number")
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    if minimum is not None:
        invalid = value <= minimum if minimum_open else value < minimum
        if invalid:
            comparator = "greater than" if minimum_open else "at least"
            raise ValueError(f"{name} must be {comparator} {minimum}")
    if maximum is not None and value > maximum:
        raise ValueError(f"{name} must be at most {maximum}")


def validate_config(config, check_paths=True):
    """Validate every setting before loading a tokenizer or model."""
    if type(config) is not Config:
        raise TypeError("config must be a Config instance")
    if type(check_paths) is not bool:
        raise TypeError("check_paths must be a boolean")
    for name in ("data_dir", "output_dir"):
        value = getattr(config, name)
        if not isinstance(value, Path):
            raise TypeError(f"{name} must be a pathlib.Path")
    if check_paths and not config.data_dir.is_dir():
        raise ValueError(f"Data directory does not exist: {config.data_dir}")
    if check_paths:
        for filename in ("train.jsonl", "val.jsonl", "test.jsonl"):
            path = config.data_dir / filename
            if not path.is_file():
                raise ValueError(f"Required split file does not exist: {path}")
    if check_paths and config.output_dir.exists():
        if not config.output_dir.is_dir():
            raise ValueError(f"Output path is not a directory: {config.output_dir}")
        if any(config.output_dir.iterdir()):
            raise ValueError(f"Output directory is not empty: {config.output_dir}")

    for name in ("model_name", "model_revision", "optimizer", "precision"):
        value = getattr(config, name)
        if not isinstance(value, str) or not value:
            raise ValueError(f"{name} must be a non-empty string")
    if not IMMUTABLE_REVISION.fullmatch(config.model_revision):
        raise ValueError("model_revision must be a full immutable 40-character commit")
    if config.optimizer not in {"adamw", "adamw-8bit"}:
        raise ValueError(f"Unsupported optimizer: {config.optimizer}")
    if config.precision not in {"fp32", "bf16"}:
        raise ValueError(f"Unsupported precision: {config.precision}")

    for name in (
        "max_length", "epochs", "batch_size", "grad_accum",
        "early_stopping_patience", "limit", "seed",
    ):
        value = getattr(config, name)
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{name} must be an integer")
    if not 3 <= config.max_length <= MAX_LENGTH:
        raise ValueError(f"max_length must be between 3 and {MAX_LENGTH}")
    count_bounds = {
        "epochs": 1_000,
        "batch_size": 1_024,
        "grad_accum": 65_536,
        "early_stopping_patience": 1_000,
    }
    for name, maximum in count_bounds.items():
        value = getattr(config, name)
        if not 1 <= value <= maximum:
            raise ValueError(f"{name} must be between 1 and {maximum}")
    if not 0 <= config.limit <= 100_000_000:
        raise ValueError("limit must be between 0 and 100000000")
    if config.seed < 0 or config.seed > 2**32 - 1:
        raise ValueError("seed must be between 0 and 2**32 - 1")

    _require_finite_number("base_lr", config.base_lr, 0, 1, minimum_open=True)
    _require_finite_number("head_lr", config.head_lr, 0, 1, minimum_open=True)
    _require_finite_number("layer_decay", config.layer_decay, 0, 1, minimum_open=True)
    _require_finite_number("weight_decay", config.weight_decay, 0, 1)
    _require_finite_number("warmup_ratio", config.warmup_ratio, 0, 1)
    _require_finite_number("max_grad_norm", config.max_grad_norm, 0, 1_000_000, minimum_open=True)
    _require_finite_number("adam_epsilon", config.adam_epsilon, 0, 1, minimum_open=True)
    _require_finite_number("aux_ce_weight", config.aux_ce_weight, 0, 100)

    for name in ("resume", "use_crf", "evaluate_test", "with_isr"):
        if type(getattr(config, name)) is not bool:
            raise TypeError(f"{name} must be a boolean")
    if config.resume:
        raise ValueError("Resume is unsupported for final hardened training")
    if config.with_isr and not config.evaluate_test:
        raise ValueError("ISR evaluation requires --evaluate-test")
    if type(config.label_weights) is not list or len(config.label_weights) != len(LABELS):
        raise ValueError(f"label_weights must contain exactly {len(LABELS)} values")
    for index, weight in enumerate(config.label_weights):
        _require_finite_number(
            f"label_weights[{index}]", weight, 0, 1_000_000, minimum_open=True
        )


def prepare_output_dir(output_dir, resume=False):
    """Create an absent or empty output directory; resume is unsupported."""
    if type(resume) is not bool:
        raise TypeError("resume must be a boolean")
    if resume:
        raise ValueError("Resume is unsupported for final hardened training")
    output_dir = Path(output_dir)
    if output_dir.exists() and (not output_dir.is_dir() or any(output_dir.iterdir())):
        raise ValueError(f"Output directory is not empty: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)


def set_seed(seed):
    """Seed Python, NumPy, and PyTorch."""
    import numpy as np
    import torch

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def load_jsonl(path):
    """Yield parsed non-empty records with contextual malformed-JSON errors."""
    path = Path(path)
    try:
        with path.open(encoding="utf-8") as lines:
            for line_number, line in enumerate(lines, 1):
                if not line.strip():
                    continue
                try:
                    yield line_number, json.loads(line)
                except json.JSONDecodeError as error:
                    raise ValueError(f"{path} line {line_number}: malformed JSON: {error.msg}") from error
    except (OSError, UnicodeError) as error:
        raise ValueError(f"Cannot read split file {path}: {error}") from error


def validate_bioes(labels):
    """Return an error for an invalid BIOES sequence, or None."""
    if not labels:
        return "has no labels"
    if any(type(label) is not str for label in labels):
        return "contains a non-string label"
    unknown = sorted(set(labels) - set(LABELS))
    if unknown:
        return f"contains unknown labels: {unknown}"
    if labels[0] not in START_LABELS:
        return f"starts with {labels[0]}"
    for previous, current in zip(labels, labels[1:]):
        if current not in VALID_TRANSITIONS[previous]:
            return f"contains invalid transition {previous} -> {current}"
    if labels[-1] not in END_LABELS:
        return f"ends with {labels[-1]}"
    return None


def validate_record(record, path, line_number):
    """Validate one positive raw record exactly without changing its content."""
    location = f"{path} line {line_number}"
    if type(record) is not dict:
        raise TypeError(f"{location}: record must be an object")
    for field_name in RECORD_FIELDS:
        if field_name not in record:
            raise ValueError(f"{location}: missing {field_name!r}")
    for field_name in ("identifier", "license_expression", "rule_type", "text"):
        value = record[field_name]
        if type(value) is not str:
            raise TypeError(f"{location}: {field_name} must be a string")
        if not value:
            raise ValueError(f"{location}: empty {field_name.replace('_', ' ')}")

    identifier = record["identifier"]
    tokens = record["tokens"]
    labels = record["bioes_labels"]
    if type(tokens) is not list:
        raise TypeError(f"{location} ({identifier}): tokens must be a list")
    if type(labels) is not list:
        raise TypeError(f"{location} ({identifier}): bioes_labels must be a list")
    if not tokens:
        raise ValueError(f"{location} ({identifier}): no tokens")
    for index, token in enumerate(tokens):
        if type(token) is not str or not token:
            raise ValueError(
                f"{location} ({identifier}): token {index} must be a non-empty string"
            )
    for index, label in enumerate(labels):
        if type(label) is not str or not label:
            raise ValueError(
                f"{location} ({identifier}): label {index} must be a non-empty string"
            )
    if len(tokens) != len(labels):
        raise ValueError(
            f"{location} ({identifier}): {len(tokens)} tokens and {len(labels)} labels"
        )
    error = validate_bioes(labels)
    if error:
        raise ValueError(f"{location} ({identifier}): {error}")
    if all(label == "O" for label in labels):
        raise ValueError(f"{location} ({identifier}): record has no required phrase labels")
    return record


def _canonical_bytes(value):
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _versioned_hash(version, value):
    digest = hashlib.sha256()
    digest.update(version.encode("ascii") + b"\n")
    digest.update(_canonical_bytes(value))
    return digest.hexdigest()


def validate_raw_split_hashes(paths, expected_h0):
    """Require every raw split to retain its initial byte hash."""
    if set(paths) != set(expected_h0):
        raise ValueError("Raw split paths and initial hashes differ")
    for split, path in paths.items():
        expected = expected_h0[split].get("sha256")
        actual = sha256(path)
        if actual != expected:
            raise ValueError(
                f"{split} split changed during the run: {actual} != {expected}"
            )


def report_content_duplicates(records_by_split):
    """Return exact token and label duplicate groups without changing records."""
    token_groups = {}
    label_groups = {}
    for records in records_by_split.values():
        for validated in records:
            item = {
                "identifier": validated.identifier,
                "split": validated.location.split,
                "path": str(validated.location.path),
                "line": validated.location.line,
            }
            token_groups.setdefault(tuple(validated.record["tokens"]), []).append(item)
            label_groups.setdefault(tuple(validated.record["bioes_labels"]), []).append(item)

    def duplicates(groups):
        return [
            {"value": list(value), "records": locations}
            for value, locations in groups.items()
            if len(locations) > 1
        ]

    return {"tokens": duplicates(token_groups), "labels": duplicates(label_groups)}


def load_and_validate_splits(paths):
    """Load every raw split, validate all records, and return pre-selection hashes."""
    if set(paths) != {"train", "validation", "test"}:
        raise ValueError("paths must contain train, validation, and test splits")
    records_by_split = {}
    h0 = {}
    for split, path_value in paths.items():
        path = Path(path_value)
        if not path.is_file():
            raise ValueError(f"Missing {split} split file: {path}")
        try:
            raw = path.read_bytes()
        except OSError as error:
            raise ValueError(f"Cannot read {split} split file {path}: {error}") from error
        if not raw:
            raise ValueError(f"{split} split file is empty: {path}")
        h0[split] = {
            "serializer": H0_SERIALIZER,
            "path": str(path),
            "sha256": hashlib.sha256(raw).hexdigest(),
        }
        records = []
        for line_number, unvalidated in load_jsonl(path):
            record = validate_record(unvalidated, path, line_number)
            location = RecordLocation(split, path, line_number)
            records.append(ValidatedRecord(record, location))
        if not records:
            raise ValueError(f"{split} split has no Current_Record: {path}")
        records_by_split[split] = records

    seen = {}
    for records in records_by_split.values():
        for validated in records:
            identifier = validated.identifier
            if identifier in seen:
                raise ValueError(
                    f"Duplicate identifier {identifier!r}: "
                    f"{seen[identifier]} and {validated.location}"
                )
            seen[identifier] = validated.location

    h1 = {}
    for split, records in records_by_split.items():
        material = {
            "split": split,
            "count": len(records),
            "records": [validated.record for validated in records],
        }
        h1[split] = {
            "serializer": H1_SERIALIZER,
            "count": len(records),
            "sha256": _versioned_hash(H1_SERIALIZER, material),
        }
    report = {
        "h0": h0,
        "h1": h1,
        "duplicates": report_content_duplicates(records_by_split),
        "raw_counts": {split: len(records) for split, records in records_by_split.items()},
    }
    return records_by_split, report


def _validated_word_ids(encoding, word_count, context, special_ids, vocab_size=None):
    try:
        word_ids = list(encoding.word_ids())
        input_ids = list(encoding["input_ids"])
        attention_mask = list(encoding["attention_mask"])
    except (AttributeError, KeyError, TypeError) as error:
        raise AlignmentError(
            "missing-word-ids", f"{context}: tokenizer returned incomplete model inputs"
        ) from error
    if len(word_ids) != len(input_ids) or len(word_ids) != len(attention_mask):
        raise AlignmentError(
            "shape-mismatch", f"{context}: word IDs, input IDs, and attention mask lengths differ"
        )
    if any(isinstance(value, bool) or not isinstance(value, int) or value < 0 for value in input_ids):
        raise AlignmentError("invalid-input-id", f"{context}: input IDs must be non-negative integers")
    if vocab_size is not None and any(value >= vocab_size for value in input_ids):
        raise AlignmentError("invalid-input-id", f"{context}: input ID is outside tokenizer vocabulary")
    if any(type(value) is not int or value != 1 for value in attention_mask):
        raise AlignmentError("invalid-attention-mask", f"{context}: attention mask must be active and binary")
    covered_positions = [
        index for index, word_id in enumerate(word_ids) if word_id is not None
    ]
    if not covered_positions:
        raise AlignmentError("zero-coverage", f"{context}: tokenizer covered no dataset words")
    first_covered = covered_positions[0]
    last_covered = covered_positions[-1]
    if first_covered == 0 or last_covered == len(word_ids) - 1:
        raise AlignmentError(
            "missing-special-token", f"{context}: required boundary special tokens are absent"
        )
    boundary_positions = list(range(first_covered)) + list(
        range(last_covered + 1, len(word_ids))
    )
    if not special_ids or any(input_ids[index] not in special_ids for index in boundary_positions):
        raise AlignmentError(
            "missing-special-token", f"{context}: boundary IDs are not tokenizer special tokens"
        )
    if any(word_ids[index] is None for index in range(first_covered, last_covered + 1)):
        raise AlignmentError(
            "coverage-gap", f"{context}: special-token gap occurs inside word coverage"
        )
    covered = [word_ids[index] for index in covered_positions]
    if any(type(word_id) is not int for word_id in covered):
        raise AlignmentError("invalid-word-id", f"{context}: tokenizer returned a non-integer word ID")
    if any(word_id < 0 or word_id >= word_count for word_id in covered):
        raise AlignmentError("out-of-range-word-id", f"{context}: tokenizer returned an out-of-range word ID")
    distinct = []
    previous = None
    for word_id in covered:
        if previous is None or word_id != previous:
            distinct.append(word_id)
            if previous is not None and word_id != previous + 1:
                raise AlignmentError(
                    "noncontiguous-coverage",
                    f"{context}: tokenizer word IDs are missing, decreasing, or noncontiguous",
                )
        previous = word_id
    if distinct[0] != 0:
        raise AlignmentError("coverage-gap", f"{context}: tokenizer coverage does not start at word 0")
    return word_ids, covered


def _coverage_counts(word_ids):
    counts = {}
    for word_id in word_ids:
        if word_id is not None:
            counts[word_id] = counts.get(word_id, 0) + 1
    return counts


def align_labels(tokens, word_labels, tokenizer, max_length):
    """Align unchanged labels to a tokenizer-verified complete word prefix."""
    if type(tokens) is not list or type(word_labels) is not list:
        raise TypeError("tokens and word_labels must be lists")
    if len(tokens) != len(word_labels) or not tokens:
        raise ValueError("tokens and word_labels must have equal non-zero lengths")
    if validate_bioes(word_labels):
        raise ValueError("word_labels must be a valid BIOES sequence")
    if getattr(tokenizer, "is_fast", True) is not True:
        raise ValueError("Training requires a fast tokenizer with word IDs")

    call = {
        "is_split_into_words": True,
        "add_special_tokens": True,
    }
    special_ids = set(getattr(tokenizer, "all_special_ids", ()))
    vocab_size = getattr(tokenizer, "vocab_size", None)
    if isinstance(vocab_size, bool) or (
        vocab_size is not None and (not isinstance(vocab_size, int) or vocab_size <= 0)
    ):
        raise ValueError("Tokenizer vocab_size must be a positive integer")
    full = tokenizer(tokens, truncation=False, **call)
    full_word_ids, _full_covered = _validated_word_ids(
        full, len(tokens), "full encoding", special_ids, vocab_size
    )
    full_counts = _coverage_counts(full_word_ids)
    expected_ids = list(range(len(tokens)))
    if sorted(full_counts) != expected_ids or any(full_counts[index] < 1 for index in expected_ids):
        missing = [index for index in expected_ids if index not in full_counts]
        raise AlignmentError(
            "zero-coverage",
            f"full encoding: dataset words have zero subwords at positions {missing}",
        )

    encoding = tokenizer(
        tokens,
        truncation=True,
        max_length=max_length,
        **call,
    )
    word_ids, covered = _validated_word_ids(
        encoding, len(tokens), "retained encoding", special_ids, vocab_size
    )
    retained_counts = _coverage_counts(word_ids)
    covered_words = max(covered) + 1
    complete_words = covered_words
    for word_id in range(covered_words):
        if retained_counts.get(word_id, 0) != full_counts[word_id]:
            if word_id != covered_words - 1:
                raise AlignmentError(
                    "partial-word-coverage",
                    f"retained encoding partially covers dataset word {word_id} before a later word",
                )
            complete_words = word_id

    omitted_positions = list(range(complete_words, len(tokens)))
    omitted_required = [
        position for position in omitted_positions if word_labels[position] != "O"
    ]
    if omitted_required:
        raise AlignmentError(
            "omitted-non-o",
            f"truncation omits non-O labels at positions {omitted_required}",
        )
    if not complete_words:
        raise AlignmentError(
            "zero-complete-word-prefix",
            "retained encoding contains no complete dataset word",
        )

    if complete_words != covered_words:
        encoding = tokenizer(tokens[:complete_words], truncation=False, **call)
        word_ids, _covered = _validated_word_ids(
            encoding,
            complete_words,
            "complete-prefix encoding",
            special_ids,
            vocab_size,
        )
        prefix_counts = _coverage_counts(word_ids)
        if any(
            prefix_counts.get(word_id, 0) != full_counts[word_id]
            for word_id in range(complete_words)
        ):
            raise AlignmentError(
                "partial-word-coverage",
                "complete-prefix encoding changed retained word coverage",
            )

    if len(encoding["input_ids"]) > max_length:
        raise AlignmentError("length-overflow", "complete-prefix encoding exceeds max_length")
    if len(encoding["attention_mask"]) != len(encoding["input_ids"]):
        raise AlignmentError("shape-mismatch", "tokenizer input and attention lengths differ")

    label_ids = []
    previous_word = None
    for word_id in word_ids:
        if word_id is None:
            label_ids.append(IGNORE_INDEX)
        elif word_id != previous_word:
            label_ids.append(LABEL2ID[word_labels[word_id]])
        else:
            label_ids.append(IGNORE_INDEX)
        previous_word = word_id
    encoding["labels"] = label_ids
    return encoding, bool(omitted_positions), False


def first_subword_positions(word_ids):
    """Return positions that start each contiguous tokenizer word."""
    positions = []
    previous = None
    for index, word_id in enumerate(word_ids):
        if word_id is None:
            previous = None
            continue
        if word_id != previous:
            positions.append(index)
        previous = word_id
    return positions


class PhraseDataset:
    """Hold selected effective examples for one validated split."""

    def __init__(self, records, tokenizer, max_length, limit=0):
        self.examples = []
        self.identifiers = []
        self.effective_inventory = []
        self.rejections = []
        self.truncations = []
        self.truncated = 0
        self.cut_phrases = 0

        for validated in records:
            if type(validated) is not ValidatedRecord:
                raise TypeError("PhraseDataset requires ValidatedRecord instances")
            record = validated.record
            try:
                encoding, truncated, _unused = align_labels(
                    record["tokens"], record["bioes_labels"], tokenizer, max_length
                )
            except AlignmentError as error:
                rejection = {
                    "identifier": validated.identifier,
                    "split": validated.location.split,
                    "path": str(validated.location.path),
                    "line": validated.location.line,
                    "reason": error.reason,
                    "message": str(error),
                }
                self.rejections.append(rejection)
                if error.reason == "omitted-non-o":
                    self.cut_phrases += 1
                continue

            example = {
                "input_ids": list(encoding["input_ids"]),
                "attention_mask": list(encoding["attention_mask"]),
                "labels": list(encoding["labels"]),
            }
            inventory = {
                "identifier": validated.identifier,
                **example,
                "truncated": truncated,
                "location": {
                    "split": validated.location.split,
                    "path": str(validated.location.path),
                    "line": validated.location.line,
                },
                "selected": False,
            }
            self.effective_inventory.append(inventory)
            if truncated:
                self.truncated += 1
                self.truncations.append(
                    {"identifier": validated.identifier, **inventory["location"]}
                )

        selected_count = limit or len(self.effective_inventory)
        for inventory in self.effective_inventory[:selected_count]:
            inventory["selected"] = True
            self.identifiers.append(inventory["identifier"])
            self.examples.append(
                {name: inventory[name] for name in ("input_ids", "attention_mask", "labels")}
            )

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, index):
        return self.examples[index]


def validate_splits(datasets):
    """Require every selected split to contain an effective example."""
    for split_name, dataset in datasets.items():
        if not dataset:
            raise ValueError(f"{split_name} split has no selected Effective_Example")


def build_effective_datasets(records_by_split, tokenizer, max_length, limit=0):
    """Build all effective inventories before applying the smoke-run limit."""
    datasets = {
        split: PhraseDataset(records, tokenizer, max_length, limit)
        for split, records in records_by_split.items()
    }
    validate_splits(datasets)
    h2 = {}
    for split, dataset in datasets.items():
        material = {
            "split": split,
            "limit": limit,
            "effective": dataset.effective_inventory,
            "rejections": dataset.rejections,
        }
        h2[split] = {
            "serializer": H2_SERIALIZER,
            "effective_count": len(dataset.effective_inventory),
            "selected_count": len(dataset),
            "rejected_count": len(dataset.rejections),
            "sha256": _versioned_hash(H2_SERIALIZER, material),
        }
    return datasets, h2


def extract_spans(tags):
    """Return inclusive spans from an already valid BIOES sequence."""
    error = validate_bioes(tags)
    if error:
        raise ValueError(f"Cannot extract spans from invalid BIOES: {error}")
    spans = set()
    start = None
    for index, tag in enumerate(tags):
        if tag == "S-REQ":
            spans.add((index, index))
        elif tag == "B-REQ":
            start = index
        elif tag == "E-REQ":
            spans.add((start, index))
            start = None
    return spans


def _integer_id(name, value, row, column, allowed):
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise TypeError(f"{name} at row {row}, column {column} is not an integer ID")
    converted = int(value)
    if converted not in allowed:
        raise ValueError(f"Unknown {name} ID {value!r} at row {row}, column {column}")
    return converted


def decode_row(pred_row, label_row, row=0):
    """Strictly map equal-length active prediction and gold IDs to BIOES tags."""
    if len(pred_row) != len(label_row):
        raise ValueError(f"Prediction and label row {row} lengths differ")
    predicted = []
    actual = []
    for column in range(len(label_row)):
        label = _integer_id(
            "gold label", label_row[column], row, column, set(ID2LABEL) | {IGNORE_INDEX}
        )
        if label == IGNORE_INDEX:
            continue
        prediction = _integer_id(
            "prediction", pred_row[column], row, column, set(ID2LABEL)
        )
        actual.append(ID2LABEL[label])
        predicted.append(ID2LABEL[prediction])
    if not actual:
        raise ValueError(f"Metric row {row} has no active gold labels")
    return predicted, actual


def _metric_matrix(name, value):
    if hasattr(value, "detach"):
        value = value.detach().cpu().tolist()
    elif hasattr(value, "tolist"):
        value = value.tolist()
    if not isinstance(value, (list, tuple)):
        raise TypeError(f"{name} must be a rank-two integer array")
    if not value:
        raise ValueError("Metrics require at least one row")
    rows = []
    width = None
    for row, values in enumerate(value):
        if not isinstance(values, (list, tuple)):
            raise ValueError(f"{name} must have rank 2; row {row} is not a row")
        if width is None:
            width = len(values)
        elif len(values) != width:
            raise ValueError(f"{name} rows must have equal lengths")
        rows.append(list(values))
    if width == 0:
        raise ValueError(f"{name} rows must not be empty")
    return rows


def _validate_crf_metric_padding(pred_row, label_row, row):
    """Require packed CRF rows to use one left-aligned active prefix."""
    padding_started = False
    for column in range(len(label_row)):
        label = _integer_id(
            "gold label", label_row[column], row, column, set(ID2LABEL) | {IGNORE_INDEX}
        )
        prediction = _integer_id(
            "prediction", pred_row[column], row, column, set(ID2LABEL) | {IGNORE_INDEX}
        )
        if label == IGNORE_INDEX:
            padding_started = True
            if prediction != IGNORE_INDEX:
                raise ValueError(
                    f"CRF prediction padding at row {row}, column {column} must be IGNORE_INDEX"
                )
        elif padding_started:
            raise ValueError(f"CRF metric row {row} padding must be left aligned")
        elif prediction == IGNORE_INDEX:
            raise ValueError(
                f"CRF active prediction at row {row}, column {column} is IGNORE_INDEX"
            )


def compute_metrics(eval_pred, use_crf=False):
    """Return strict span metrics with explicit invalid-path accounting."""
    if type(use_crf) is not bool:
        raise TypeError("use_crf must be a boolean")
    predictions, labels = eval_pred
    predictions = _metric_matrix("Predictions", predictions)
    labels = _metric_matrix("Labels", labels)
    if len(predictions) != len(labels):
        raise ValueError("Prediction and label batch sizes differ")
    if len(predictions[0]) != len(labels[0]):
        raise ValueError("Prediction and label row lengths differ")

    true_positive = false_positive = false_negative = 0
    exact = invalid_paths = 0
    for row in range(len(predictions)):
        if use_crf:
            _validate_crf_metric_padding(predictions[row], labels[row], row)
        predicted, actual = decode_row(predictions[row], labels[row], row)
        actual_error = validate_bioes(actual)
        if actual_error:
            raise ValueError(f"Invalid gold BIOES path in row {row}: {actual}; {actual_error}")
        actual_spans = extract_spans(actual)
        prediction_error = validate_bioes(predicted)
        if prediction_error:
            if use_crf:
                raise ValueError(
                    f"Invalid CRF BIOES path in row {row}: {predicted}; {prediction_error}"
                )
            invalid_paths += 1
            false_negative += len(actual_spans)
            continue

        predicted_spans = extract_spans(predicted)
        true_positive += len(predicted_spans & actual_spans)
        false_positive += len(predicted_spans - actual_spans)
        false_negative += len(actual_spans - predicted_spans)
        if predicted_spans == actual_spans:
            exact += 1

    precision_denominator = true_positive + false_positive
    recall_denominator = true_positive + false_negative
    precision = true_positive / precision_denominator if precision_denominator else 0.0
    recall = true_positive / recall_denominator if recall_denominator else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "f1": f1,
        "precision": precision,
        "recall": recall,
        "exact_match": exact / len(predictions),
        "predicted_spans": true_positive + false_positive,
        "gold_spans": true_positive + false_negative,
        "invalid_paths": invalid_paths,
    }


def evaluate_isr(records, model, tokenizer, max_length):
    """Return predicted-phrase locatability; this is not injection success."""
    import torch
    from licensedcode.required_phrases import find_phrase_spans_in_text

    device = next(model.parameters()).device
    model.eval()
    total = locatable = 0
    for item in records:
        record = item.record if isinstance(item, ValidatedRecord) else item
        try:
            encoding, _truncated, _unused = align_labels(
                record["tokens"], record["bioes_labels"], tokenizer, max_length
            )
        except AlignmentError:
            continue
        inputs = {
            "input_ids": torch.tensor([encoding["input_ids"]], device=device),
            "attention_mask": torch.tensor([encoding["attention_mask"]], device=device),
            "labels": torch.tensor([encoding["labels"]], device=device),
        }
        with torch.no_grad():
            output = model(**inputs)
        tags, _actual = decode_row(
            output["predictions"][0].tolist(),
            output["word_labels"][0].tolist(),
        )
        error = validate_bioes(tags)
        if error:
            if model.use_crf:
                raise ValueError(f"Invalid CRF ISR path: {tags}; {error}")
            continue
        for start, end in extract_spans(tags):
            if end >= len(record["tokens"]):
                continue
            phrase = " ".join(record["tokens"][start : end + 1])
            total += 1
            if find_phrase_spans_in_text(record["text"], phrase):
                locatable += 1
    return locatable / total if total else 0.0


def sha256(path):
    """Return the hexadecimal SHA256 digest of a file."""
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def installed_version(package_name):
    """Return an installed package version, or None."""
    try:
        return importlib.metadata.version(package_name)
    except importlib.metadata.PackageNotFoundError:
        return None


def serializable_config(config):
    """Return the complete training configuration with string paths."""
    values = asdict(config)
    values["data_dir"] = str(values["data_dir"])
    values["output_dir"] = str(values["output_dir"])
    return values


def write_json_atomic(path, value):
    """Durably replace one JSON file without exposing partial content."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=False, allow_nan=False, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        try:
            directory = os.open(path.parent, os.O_RDONLY)
        except (AttributeError, OSError):
            directory = None
        if directory is not None:
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
    finally:
        if temporary.exists():
            temporary.unlink()


def write_failure_manifest(
    manifest_path, pre_run_manifest, phase, error, completed_checks, retained_artifacts
):
    """Atomically record a failed phase without environment or traceback capture."""
    failure_manifest = {
        **pre_run_manifest,
        "state": "failure",
        "failed_phase": phase,
        "exception": {"type": type(error).__name__, "message": str(error)},
        "completed_checks": list(completed_checks),
        "retained_artifacts": [str(path) for path in retained_artifacts if Path(path).exists()],
    }
    write_json_atomic(manifest_path, failure_manifest)
    return failure_manifest


def _run_git(repo_dir, *arguments):
    result = subprocess.run(
        ["git", "-C", str(repo_dir), *arguments],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="strict",
    )
    if result.returncode:
        raise RuntimeError(f"Cannot collect source provenance with git {' '.join(arguments)}")
    return result.stdout.rstrip("\n")


def _redacted_repository_identity(value):
    if "://" not in value:
        return value.split("@", 1)[-1] if "@" in value else value
    parsed = urlsplit(value)
    hostname = parsed.hostname or ""
    if parsed.port:
        hostname = f"{hostname}:{parsed.port}"
    return urlunsplit((parsed.scheme, hostname, parsed.path, "", ""))


def collect_source_provenance(repo_dir=None):
    """Return narrow repository identity without reading environment variables."""
    repo_dir = Path(repo_dir or Path(__file__).resolve().parents[2])
    root = Path(_run_git(repo_dir, "rev-parse", "--show-toplevel")).resolve()
    branch = _run_git(root, "branch", "--show-current") or "DETACHED"
    commit = _run_git(root, "rev-parse", "HEAD")
    if not IMMUTABLE_REVISION.fullmatch(commit):
        raise RuntimeError("Source commit is not an immutable full identity")
    repository = _redacted_repository_identity(
        _run_git(root, "config", "--get", "remote.origin.url")
    )
    return {
        "repository": repository,
        "root": str(root),
        "branch": branch,
        "commit": commit,
        "dirty": bool(_run_git(root, "status", "--porcelain")),
    }


def _optimizer_provenance(name):
    if name == "adamw":
        from torch.optim import AdamW

        implementation = AdamW
        package = "torch"
    elif name == "adamw-8bit":
        try:
            from bitsandbytes.optim import AdamW8bit
        except ImportError as error:
            raise RuntimeError(
                "adamw-8bit requires bitsandbytes; install the training-8bit extra"
            ) from error
        implementation = AdamW8bit
        package = "bitsandbytes"
    else:
        raise ValueError(f"Unsupported optimizer: {name}")
    return {
        "configured": name,
        "implementation": f"{implementation.__module__}.{implementation.__qualname__}",
        "package": package,
        "version": installed_version(package),
    }


def collect_runtime_provenance(optimizer, precision):
    """Return runtime API provenance without capturing environment variables."""
    import torch
    import transformers

    cuda_available = torch.cuda.is_available()
    return {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "package": installed_version("scancode-required-phrases"),
        "scancode_toolkit": installed_version("scancode-toolkit"),
        "torch": torch.__version__,
        "transformers": transformers.__version__,
        "pytorch_crf": installed_version("pytorch-crf"),
        "cuda_available": cuda_available,
        "cuda": torch.version.cuda,
        "cudnn": torch.backends.cudnn.version(),
        "device": torch.cuda.get_device_name(0) if cuda_available else "cpu",
        "optimizer": _optimizer_provenance(optimizer),
        "precision": precision,
    }


def validate_state_structure(expected, actual, expected_name="expected", actual_name="actual"):
    """Require ordered keys, shapes, dtypes, and finite tensor values."""
    import torch

    expected_keys = list(expected)
    actual_keys = list(actual)
    if expected_keys != actual_keys:
        missing = [name for name in expected_keys if name not in actual]
        unexpected = [name for name in actual_keys if name not in expected]
        raise ValueError(
            f"State key mismatch for {expected_name} and {actual_name}; "
            f"missing={missing}, unexpected={unexpected}"
        )
    for name in expected_keys:
        left = expected[name].detach().cpu()
        right = actual[name].detach().cpu()
        if left.shape != right.shape:
            raise ValueError(
                f"Tensor {name!r} shape mismatch: {tuple(left.shape)} != {tuple(right.shape)}"
            )
        if left.dtype != right.dtype:
            raise ValueError(f"Tensor {name!r} dtype mismatch: {left.dtype} != {right.dtype}")
        if not torch.isfinite(left).all() or not torch.isfinite(right).all():
            raise ValueError(f"Tensor {name!r} contains non-finite values")


def validate_state_dicts(expected, actual, expected_name="expected", actual_name="actual"):
    """Require exact ordered state structure and tensor values."""
    import torch

    validate_state_structure(expected, actual, expected_name, actual_name)
    for name in expected:
        left = expected[name].detach().cpu()
        right = actual[name].detach().cpu()
        if not torch.equal(left, right):
            raise ValueError(f"Tensor {name!r} values differ")


def _canonical_state_dict(state):
    return {name: state[name] for name in sorted(state)}


def _load_state_file(model_path):
    import torch

    model_path = Path(model_path)
    if model_path.suffix == ".safetensors":
        from safetensors.torch import load_file
        return load_file(str(model_path))
    return torch.load(model_path, map_location="cpu", weights_only=True)


def validate_saved_state(model, model_path):
    """Require one saved model state to equal the in-memory state exactly."""
    saved = _load_state_file(model_path)
    validate_state_dicts(
        _canonical_state_dict(model.state_dict()),
        _canonical_state_dict(saved),
        "in-memory",
        str(model_path),
    )


def _artifact_config(config, resolved_revision):
    values = serializable_config(config)
    values.update(
        {
            "artifact_schema": ARTIFACT_SCHEMA,
            "constraint_contract": CONSTRAINT_CONTRACT,
            "labels": list(LABELS),
            "requested_model_revision": config.model_revision,
            "resolved_model_revision": resolved_revision,
            "model_revision": resolved_revision,
        }
    )
    return values


def _validate_artifact_config(values):
    if type(values) is not dict:
        raise TypeError("train_config.json must contain an object")
    config_fields = set(Config.__dataclass_fields__)
    contract_fields = {
        "artifact_schema",
        "constraint_contract",
        "labels",
        "requested_model_revision",
        "resolved_model_revision",
    }
    expected_fields = config_fields | contract_fields
    if set(values) != expected_fields:
        missing = sorted(expected_fields - set(values))
        unexpected = sorted(set(values) - expected_fields)
        raise ValueError(
            f"Artifact configuration fields differ; missing={missing}, unexpected={unexpected}"
        )
    if values["artifact_schema"] != ARTIFACT_SCHEMA:
        raise ValueError(
            f"Unsupported artifact schema; expected {ARTIFACT_SCHEMA}. Old artifacts must be retrained."
        )
    if type(values["labels"]) is not list or tuple(values["labels"]) != LABELS:
        raise ValueError("Artifact label order does not match the supported LABELS")
    if values["constraint_contract"] != CONSTRAINT_CONTRACT:
        raise ValueError("Artifact constraint contract is unsupported")
    revision = values["resolved_model_revision"]
    if not isinstance(revision, str) or not IMMUTABLE_REVISION.fullmatch(revision):
        raise ValueError("Artifact has no immutable resolved model revision")
    if values["requested_model_revision"] != revision or values["model_revision"] != revision:
        raise ValueError("Requested, resolved, and configured artifact revisions differ")

    config_values = {name: values[name] for name in config_fields}
    for name in ("data_dir", "output_dir"):
        if type(config_values[name]) is not str or not config_values[name]:
            raise ValueError(f"Artifact {name} must be a non-empty path string")
        config_values[name] = Path(config_values[name])
    validate_config(Config(**config_values), check_paths=False)
    return values


def _load_local_model(model_dir, offline=True):
    """Strictly reconstruct a supported model and tokenizer from local files only."""
    import torch
    from transformers import AutoConfig
    from transformers import AutoModel
    from transformers import AutoTokenizer

    from phrase_model import PhraseTagger

    if offline is not True:
        raise ValueError("Final_Model loading is local-only")
    model_dir = Path(model_dir)
    config_path = model_dir / "train_config.json"
    try:
        values = _validate_artifact_config(json.loads(config_path.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Cannot read supported artifact configuration: {error}") from error
    local_config = AutoConfig.from_pretrained(str(model_dir), local_files_only=True)
    backbone = AutoModel.from_config(local_config)
    tagger_config = SimpleNamespace(**values)
    model = PhraseTagger(tagger_config, backbone=backbone)
    state_path = model_dir / "model.safetensors"
    if not state_path.is_file():
        raise ValueError(f"Final_Model is missing {state_path.name}")
    state = _load_state_file(state_path)
    validate_state_structure(
        _canonical_state_dict(model.state_dict()),
        _canonical_state_dict(state),
        "constructed",
        "saved",
    )
    model.load_state_dict(state, strict=True)
    validate_state_dicts(
        _canonical_state_dict(state),
        _canonical_state_dict(model.state_dict()),
        "saved",
        "loaded",
    )
    tokenizer = AutoTokenizer.from_pretrained(
        str(model_dir), use_fast=True, local_files_only=True
    )
    if not tokenizer.is_fast:
        raise ValueError("Final_Model tokenizer is not fast")
    if any(not torch.isfinite(tensor).all() for tensor in model.state_dict().values()):
        raise ValueError("Final_Model contains non-finite tensors")
    return model.eval(), tokenizer


def load_final_model(model_dir, offline=True):
    """Validate publication and load one supported Final_Model locally."""
    validate_publishable_model(model_dir)
    return _load_local_model(model_dir, offline=offline)


def _all_file_hashes(directory):
    directory = Path(directory)
    return {
        path.relative_to(directory).as_posix(): sha256(path)
        for path in sorted(directory.rglob("*"))
        if path.is_file() and path.name != "SUCCESS.json"
    }


def validate_publishable_model(model_dir):
    """Require a supported Success_Marker and exact Final_Model file hashes."""
    model_dir = Path(model_dir)
    marker_path = model_dir / "SUCCESS.json"
    try:
        marker = json.loads(marker_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Final_Model has no valid Success_Marker: {error}") from error
    if marker.get("schema") != ARTIFACT_SCHEMA:
        raise ValueError("Success_Marker uses an unsupported artifact schema")
    if marker.get("constraint_contract") != CONSTRAINT_CONTRACT:
        raise ValueError("Success_Marker uses an unsupported constraint contract")
    selected = marker.get("selected_checkpoint")
    if not isinstance(selected, str) or not selected:
        raise ValueError("Success_Marker has no Selected_Checkpoint")
    files = marker.get("files")
    if type(files) is not dict or not files:
        raise ValueError("Success_Marker has no required file inventory")
    actual_files = _all_file_hashes(model_dir)
    missing_required = sorted(REQUIRED_ARTIFACT_FILES - set(actual_files))
    if missing_required:
        raise ValueError(f"Final_Model is missing required files: {missing_required}")
    if not TOKENIZER_MODEL_FILES.intersection(actual_files):
        raise ValueError("Final_Model is missing a complete fast-tokenizer model file")
    if set(files) != set(actual_files):
        raise ValueError("Final_Model file inventory does not match Success_Marker")
    for name, digest in files.items():
        if not isinstance(digest, str) or digest != actual_files[name]:
            raise ValueError(f"Final_Model hash mismatch for {name}")
    manifest_path = model_dir / "run_manifest.json"
    if marker.get("run_manifest_sha256") != sha256(manifest_path):
        raise ValueError("Success_Marker run manifest hash does not match")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        config = json.loads((model_dir / "train_config.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Final_Model metadata is malformed: {error}") from error
    required_manifest_fields = {
        "schema",
        "state",
        "config",
        "contracts",
        "dataset",
        "model_identity",
        "source",
        "runtime",
        "completed_checks",
        "selected_checkpoint",
        "best_validation_f1",
        "validation_metrics",
        "ordered_validation",
        "test_metrics",
        "artifact_files",
        "log_history",
    }
    if set(manifest) != required_manifest_fields:
        raise ValueError("Final_Model run manifest fields are incomplete or unsupported")
    if manifest["schema"] != MANIFEST_SCHEMA or manifest["state"] != "success":
        raise ValueError("Final_Model run manifest is not a supported success manifest")
    if manifest["selected_checkpoint"] != selected:
        raise ValueError("Success_Marker Selected_Checkpoint does not match the manifest")
    if manifest["config"] != {name: config[name] for name in Config.__dataclass_fields__}:
        raise ValueError("Final_Model manifest and artifact configurations differ")
    expected_contracts = {
        "artifact_schema": ARTIFACT_SCHEMA,
        "constraint_contract": CONSTRAINT_CONTRACT,
        "labels": list(LABELS),
    }
    if manifest["contracts"] != expected_contracts:
        raise ValueError("Final_Model manifest contracts are unsupported")
    dataset = manifest["dataset"]
    if type(dataset) is not dict or not {"paths", "h0", "h1", "h2", "report"} <= set(dataset):
        raise ValueError("Final_Model manifest dataset provenance is incomplete")
    if type(manifest["source"]) is not dict or not {
        "repository", "root", "branch", "commit", "dirty"
    } <= set(manifest["source"]):
        raise ValueError("Final_Model source provenance is incomplete")
    if type(manifest["runtime"]) is not dict or not {
        "python", "platform", "torch", "transformers", "optimizer", "precision"
    } <= set(manifest["runtime"]):
        raise ValueError("Final_Model runtime provenance is incomplete")
    if not isinstance(manifest["completed_checks"], list) or not manifest["completed_checks"]:
        raise ValueError("Final_Model completed checks are missing")
    if not isinstance(manifest["best_validation_f1"], (int, float)) or not math.isfinite(
        manifest["best_validation_f1"]
    ):
        raise ValueError("Final_Model best validation F1 is invalid")
    for name in ("validation_metrics", "ordered_validation"):
        if type(manifest[name]) is not dict:
            raise ValueError(f"Final_Model {name} is invalid")
    expected_components = {
        name: digest for name, digest in actual_files.items() if name != "run_manifest.json"
    }
    if manifest["artifact_files"] != expected_components:
        raise ValueError("Final_Model manifest artifact hashes do not match")
    _validate_artifact_config(config)
    return marker


def _checkpoint_state_path(checkpoint, output_dir):
    checkpoint = Path(checkpoint).resolve()
    output_root = Path(output_dir).resolve()
    for filename in ("model.safetensors", "pytorch_model.bin"):
        candidate = checkpoint / filename
        if candidate.is_file():
            resolved = candidate.resolve()
            if output_root not in resolved.parents or checkpoint not in resolved.parents:
                raise ValueError("Selected_Checkpoint state resolves outside the run output")
            return resolved
    raise ValueError(f"Selected_Checkpoint has no model state: {checkpoint}")


def validate_selected_checkpoint(trainer, output_dir):
    """Return the trainer-selected best-F1 checkpoint contained by output_dir."""
    selected = trainer.state.best_model_checkpoint
    if not selected:
        raise ValueError("Trainer state has no Selected_Checkpoint")
    output_root = Path(output_dir).resolve()
    selected_path = Path(selected).resolve()
    if selected_path == output_root or output_root not in selected_path.parents:
        raise ValueError("Selected_Checkpoint must be a checkpoint directory inside run output")
    if not selected_path.is_dir():
        raise ValueError(f"Selected_Checkpoint does not exist: {selected_path}")
    if trainer.state.best_metric is None or not math.isfinite(float(trainer.state.best_metric)):
        raise ValueError("Trainer state has no finite best validation F1")
    return selected_path


def stage_final_model(output_dir, model, tokenizer, artifact_config):
    """Save one new self-contained local Final_Model staging directory."""
    from safetensors.torch import save_file

    output_dir = Path(output_dir)
    stage = output_dir / "final-model.tmp"
    destination = output_dir / "final-model"
    if stage.exists() or destination.exists():
        raise ValueError("Final_Model staging and destination must both be absent")
    stage.mkdir()
    model.backbone.config.save_pretrained(str(stage))
    tokenizer.save_pretrained(str(stage))
    state = {
        name: tensor.detach().cpu().contiguous()
        for name, tensor in model.state_dict().items()
    }
    save_file(state, str(stage / "model.safetensors"))
    write_json_atomic(stage / "train_config.json", artifact_config)
    return stage


def _pad_metric_rows(predictions, labels):
    if len(predictions) != len(labels) or not predictions:
        raise ValueError("Ordered validation predictions and labels must be non-empty and equal")
    width = max(len(row) for row in labels)
    padded_predictions = []
    padded_labels = []
    for row, (prediction, label) in enumerate(zip(predictions, labels)):
        if len(prediction) != len(label):
            raise ValueError(f"Ordered validation row {row} lengths differ")
        padded_predictions.append(list(prediction) + [IGNORE_INDEX] * (width - len(prediction)))
        padded_labels.append(list(label) + [IGNORE_INDEX] * (width - len(label)))
    return padded_predictions, padded_labels


def collect_ordered_validation_result(model, dataset, use_crf):
    """Return exact discrete results and strict metrics in dataset order."""
    import torch

    try:
        device = next(model.parameters()).device
    except StopIteration:
        device = torch.device("cpu")
    model.eval()
    predictions = []
    labels = []
    for example in dataset.examples:
        inputs = {
            name: torch.tensor([example[name]], device=device)
            for name in ("input_ids", "attention_mask", "labels")
        }
        with torch.no_grad():
            output = model(**inputs)
        if type(output) is not dict or "predictions" not in output or "word_labels" not in output:
            raise ValueError("Ordered validation output must contain predictions and word_labels")
        prediction_tensor = output["predictions"]
        actual_tensor = output["word_labels"]
        if not isinstance(prediction_tensor, torch.Tensor) or not isinstance(
            actual_tensor, torch.Tensor
        ):
            raise TypeError("Ordered validation predictions and labels must be tensors")
        if prediction_tensor.dim() != 2 or actual_tensor.dim() != 2:
            raise ValueError("Ordered validation predictions and labels must have rank 2")
        if prediction_tensor.shape != actual_tensor.shape or prediction_tensor.size(0) != 1:
            raise ValueError(
                "Ordered validation predictions and labels must have equal single-row shapes"
            )
        if prediction_tensor.dtype != torch.long or actual_tensor.dtype != torch.long:
            raise TypeError("Ordered validation predictions and labels must use torch.long IDs")
        prediction = prediction_tensor[0].detach().cpu().tolist()
        actual = actual_tensor[0].detach().cpu().tolist()
        predictions.append(prediction)
        labels.append(actual)
    metric_predictions, metric_labels = _pad_metric_rows(predictions, labels)
    metrics = compute_metrics((metric_predictions, metric_labels), use_crf=use_crf)
    return {
        "prediction_ids": predictions,
        "label_ids": labels,
        "invalid_paths": metrics["invalid_paths"],
        "metrics": metrics,
    }


def compare_ordered_validation_results(selected, staged):
    """Require exact ordered predictions, labels, invalid counts, and metrics."""
    for name in ("prediction_ids", "label_ids", "invalid_paths", "metrics"):
        if selected.get(name) != staged.get(name):
            raise ValueError(f"Ordered validation {name} differs after staged reload")


def _resolved_commit(component, name):
    candidates = [
        getattr(component, "_commit_hash", None),
        getattr(getattr(component, "config", None), "_commit_hash", None),
        getattr(component, "init_kwargs", {}).get("_commit_hash")
        if isinstance(getattr(component, "init_kwargs", None), dict)
        else None,
    ]
    values = {value for value in candidates if value}
    if len(values) != 1:
        raise ValueError(f"{name} has no single resolved immutable revision")
    value = values.pop()
    if not isinstance(value, str) or not IMMUTABLE_REVISION.fullmatch(value):
        raise ValueError(f"{name} resolved revision is not a full immutable commit")
    return value


def resolve_tokenizer_revision(model_name, requested):
    """Return the Hub revision for the tokenizer's requested model commit."""
    from huggingface_hub import model_info

    tokenizer_revision = model_info(model_name, revision=requested).sha
    if not isinstance(tokenizer_revision, str) or not IMMUTABLE_REVISION.fullmatch(
        tokenizer_revision
    ):
        raise ValueError("Tokenizer Hub revision is not a full immutable commit")
    return tokenizer_revision


def resolve_model_identity(requested, tokenizer_revision, backbone_config):
    """Require tokenizer and backbone identities to match the requested commit."""
    backbone_revision = _resolved_commit(backbone_config, "backbone")
    if tokenizer_revision != requested or backbone_revision != requested:
        raise ValueError(
            "Requested, tokenizer, and backbone revisions are absent or inconsistent: "
            f"{requested}, {tokenizer_revision}, {backbone_revision}"
        )
    return requested


def promote_final_model(
    stage,
    destination,
    marker,
    manifest_path=None,
    final_manifest=None,
):
    """Atomically promote a stage, write SUCCESS last, and roll back failures."""
    stage = Path(stage)
    destination = Path(destination)
    if not stage.is_dir():
        raise ValueError(f"Final_Model stage does not exist: {stage}")
    if destination.exists():
        raise ValueError(f"Final_Model destination already exists: {destination}")
    if (manifest_path is None) != (final_manifest is None):
        raise ValueError("manifest_path and final_manifest must be provided together")
    os.replace(stage, destination)
    try:
        if manifest_path is not None:
            write_json_atomic(manifest_path, final_manifest)
        write_json_atomic(destination / "SUCCESS.json", marker)
        validate_publishable_model(destination)
    except Exception:
        success_marker = destination / "SUCCESS.json"
        if success_marker.exists():
            success_marker.unlink()
        os.replace(destination, stage)
        raise


def validate_precision(precision):
    """Validate the selected training precision."""
    import torch

    if precision == "bf16" and not (
        torch.cuda.is_available() and torch.cuda.is_bf16_supported()
    ):
        raise ValueError("bf16 requires a CUDA device with BF16 support")


def run_training(config):
    """Validate, train, verify, and transactionally publish a Final_Model."""
    import torch
    from transformers import AutoConfig
    from transformers import AutoTokenizer
    from transformers import DataCollatorForTokenClassification
    from transformers import EarlyStoppingCallback
    from transformers import TrainingArguments

    from phrase_model import PhraseTagger
    from phrase_model import PhraseTrainer
    from phrase_model import build_optimizer

    validate_config(config)
    validate_precision(config.precision)
    paths = {
        "train": config.data_dir / "train.jsonl",
        "validation": config.data_dir / "val.jsonl",
        "test": config.data_dir / "test.jsonl",
    }
    records_by_split, raw_report = load_and_validate_splits(paths)

    tokenizer = AutoTokenizer.from_pretrained(
        config.model_name,
        revision=config.model_revision,
        use_fast=True,
    )
    if not tokenizer.is_fast:
        raise RuntimeError("Training requires a fast tokenizer with word IDs")
    tokenizer_revision = resolve_tokenizer_revision(
        config.model_name, config.model_revision
    )
    backbone_config = AutoConfig.from_pretrained(
        config.model_name,
        revision=config.model_revision,
    )
    resolved_revision = resolve_model_identity(
        config.model_revision, tokenizer_revision, backbone_config
    )
    datasets, h2 = build_effective_datasets(
        records_by_split, tokenizer, config.max_length, config.limit
    )
    validate_raw_split_hashes(paths, raw_report["h0"])
    dataset_report = {
        **raw_report,
        "h2": h2,
        "effective": {
            split: {
                "accepted": len(dataset.effective_inventory),
                "selected": len(dataset),
                "truncations": dataset.truncations,
                "rejections": dataset.rejections,
            }
            for split, dataset in datasets.items()
        },
    }

    prepare_output_dir(config.output_dir, config.resume)
    source_provenance = collect_source_provenance()
    runtime_provenance = collect_runtime_provenance(config.optimizer, config.precision)
    report_path = config.output_dir / "dataset_report.json"
    manifest_path = config.output_dir / "run_manifest.json"
    write_json_atomic(report_path, dataset_report)
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "state": "pre-run",
        "config": serializable_config(config),
        "contracts": {
            "artifact_schema": ARTIFACT_SCHEMA,
            "constraint_contract": CONSTRAINT_CONTRACT,
            "labels": list(LABELS),
        },
        "dataset": {
            "paths": {name: str(path) for name, path in paths.items()},
            "h0": raw_report["h0"],
            "h1": raw_report["h1"],
            "h2": h2,
            "report": {"path": str(report_path), "sha256": sha256(report_path)},
        },
        "model_identity": {
            "name": config.model_name,
            "requested_revision": config.model_revision,
            "resolved_tokenizer_revision": resolved_revision,
            "resolved_backbone_revision": resolved_revision,
        },
        "source": source_provenance,
        "runtime": runtime_provenance,
        "completed_checks": [
            "configuration",
            "raw-splits",
            "identifier-uniqueness",
            "content-duplicate-report",
            "h0-h1",
            "immutable-model-identity",
            "effective-examples-h2",
        ],
    }
    write_json_atomic(manifest_path, manifest)

    completed_checks = list(manifest["completed_checks"])
    phase = "model-construction"
    stage = config.output_dir / "final-model.tmp"
    destination = config.output_dir / "final-model"
    try:
        set_seed(config.seed)
        model = PhraseTagger(config)
        actual_revision = _resolved_commit(model.backbone.config, "constructed backbone")
        if actual_revision != resolved_revision:
            raise ValueError("Constructed backbone revision differs from the resolved revision")
        completed_checks.append("model-construction")
        collator = DataCollatorForTokenClassification(
            tokenizer,
            label_pad_token_id=IGNORE_INDEX,
        )
        arguments = TrainingArguments(
            output_dir=str(config.output_dir),
            num_train_epochs=config.epochs,
            per_device_train_batch_size=config.batch_size,
            per_device_eval_batch_size=config.batch_size,
            gradient_accumulation_steps=config.grad_accum,
            learning_rate=config.base_lr,
            weight_decay=config.weight_decay,
            warmup_ratio=config.warmup_ratio,
            lr_scheduler_type="cosine",
            max_grad_norm=config.max_grad_norm,
            eval_strategy="epoch",
            save_strategy="epoch",
            save_total_limit=2,
            load_best_model_at_end=True,
            metric_for_best_model="f1",
            greater_is_better=True,
            bf16=config.precision == "bf16",
            fp16=False,
            logging_steps=50,
            report_to="none",
            seed=config.seed,
            data_seed=config.seed,
            dataloader_num_workers=2,
            save_safetensors=True,
        )
        trainer_kwargs = {
            "model": model,
            "args": arguments,
            "train_dataset": datasets["train"],
            "eval_dataset": datasets["validation"],
            "data_collator": collator,
            "compute_metrics": partial(compute_metrics, use_crf=config.use_crf),
            "optimizers": (build_optimizer(config, model), None),
            "callbacks": [
                EarlyStoppingCallback(
                    early_stopping_patience=config.early_stopping_patience,
                )
            ],
        }
        if "processing_class" in inspect.signature(PhraseTrainer.__init__).parameters:
            trainer_kwargs["processing_class"] = tokenizer
        else:
            trainer_kwargs["tokenizer"] = tokenizer

        phase = "training"
        trainer = PhraseTrainer(**trainer_kwargs)
        trainer.train()
        validate_raw_split_hashes(paths, raw_report["h0"])
        completed_checks.extend(["training", "post-training-dataset-hashes"])

        phase = "selected-checkpoint"
        selected_checkpoint = validate_selected_checkpoint(trainer, config.output_dir)
        checkpoint_state = _load_state_file(
            _checkpoint_state_path(selected_checkpoint, config.output_dir)
        )
        validate_state_dicts(
            _canonical_state_dict(checkpoint_state),
            _canonical_state_dict(model.state_dict()),
            "Selected_Checkpoint",
            "selected in-memory model",
        )
        completed_checks.extend(["selected-checkpoint", "checkpoint-in-memory-comparison"])
        selected_result = collect_ordered_validation_result(
            model, datasets["validation"], config.use_crf
        )
        selected_f1 = selected_result["metrics"]["f1"]
        if float(trainer.state.best_metric) != selected_f1:
            raise ValueError(
                "Selected_Checkpoint best metric does not equal strict validation F1: "
                f"{trainer.state.best_metric} != {selected_f1}"
            )
        trainer.remove_callback(EarlyStoppingCallback)
        validation_metrics = trainer.evaluate(
            datasets["validation"], metric_key_prefix="validation"
        )
        test_metrics = None
        if config.evaluate_test:
            test_metrics = trainer.evaluate(datasets["test"], metric_key_prefix="test")
            if config.with_isr:
                test_metrics["test_isr"] = evaluate_isr(
                    records_by_split["test"], model, tokenizer, config.max_length
                )
                test_metrics["test_isr_scope"] = (
                    "predicted-phrase locatability only; injection gates and rule mutation "
                    "are outside this metric"
                )

        phase = "staging"
        artifact_config = _artifact_config(config, resolved_revision)
        stage = stage_final_model(
            config.output_dir, model, tokenizer, artifact_config
        )
        staged_state = _load_state_file(stage / "model.safetensors")
        validate_state_dicts(
            _canonical_state_dict(model.state_dict()),
            _canonical_state_dict(staged_state),
            "selected in-memory model",
            "staged model",
        )
        completed_checks.extend(["staging", "in-memory-staged-comparison"])

        phase = "offline-reload"
        staged_model, _staged_tokenizer = _load_local_model(stage, offline=True)
        validate_state_dicts(
            _canonical_state_dict(model.state_dict()),
            _canonical_state_dict(staged_model.state_dict()),
            "selected in-memory model",
            "offline staged model",
        )
        staged_result = collect_ordered_validation_result(
            staged_model, datasets["validation"], config.use_crf
        )
        compare_ordered_validation_results(selected_result, staged_result)
        completed_checks.extend(["offline-reload", "ordered-validation-comparison"])

        phase = "final-manifest"
        component_hashes = _all_file_hashes(stage)
        completed_checks.append("artifact-hashes")
        success_manifest = {
            **manifest,
            "state": "success",
            "completed_checks": completed_checks + ["final-manifest"],
            "selected_checkpoint": str(selected_checkpoint),
            "best_validation_f1": trainer.state.best_metric,
            "validation_metrics": validation_metrics,
            "ordered_validation": selected_result,
            "test_metrics": test_metrics,
            "artifact_files": component_hashes,
            "log_history": trainer.state.log_history,
        }
        write_json_atomic(stage / "run_manifest.json", success_manifest)
        artifact_hashes = _all_file_hashes(stage)
        marker = {
            "schema": ARTIFACT_SCHEMA,
            "constraint_contract": CONSTRAINT_CONTRACT,
            "selected_checkpoint": str(selected_checkpoint),
            "run_manifest_sha256": sha256(stage / "run_manifest.json"),
            "files": artifact_hashes,
        }

        phase = "promotion"
        promote_final_model(
            stage,
            destination,
            marker,
            manifest_path=manifest_path,
            final_manifest=success_manifest,
        )
        phase = "success-marker"
    except Exception as error:
        if destination.exists():
            if stage.exists():
                raise RuntimeError(
                    "Both failed Final_Model destination and staging directory exist"
                ) from error
            success_marker = destination / "SUCCESS.json"
            if success_marker.exists():
                success_marker.unlink()
            os.replace(destination, stage)
        retained_artifacts = [config.output_dir, report_path, stage]
        retained_artifacts.extend(sorted(config.output_dir.glob("checkpoint-*")))
        write_failure_manifest(
            manifest_path,
            manifest,
            phase,
            error,
            completed_checks,
            retained_artifacts,
        )
        raise

    click.echo(f"best checkpoint: {selected_checkpoint}")
    click.echo(f"best validation F1: {trainer.state.best_metric}")
    click.echo(f"validation: {validation_metrics}")
    if test_metrics is not None:
        click.echo(f"test: {test_metrics}")
    return {
        "validation": validation_metrics,
        "test": test_metrics,
        "final_model": destination,
    }


@click.command()
@click.option(
    "--data-dir",
    required=True,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Directory containing train.jsonl, val.jsonl, and test.jsonl.",
)
@click.option(
    "--output-dir",
    default="model-output",
    type=click.Path(file_okay=False, path_type=Path),
    help="New or empty directory for this run.",
)
@click.option("--model-name", default=MODEL_NAME, help="Base model to fine-tune.")
@click.option(
    "--model-revision",
    required=True,
    help="Full immutable model and tokenizer commit revision.",
)
@click.option(
    "--max-length", default=MAX_LENGTH,
    type=click.IntRange(min=3, max=MAX_LENGTH), show_default=True,
)
@click.option("--epochs", default=8, type=click.IntRange(min=1), show_default=True)
@click.option("--batch-size", default=1, type=click.IntRange(min=1), show_default=True)
@click.option("--grad-accum", default=16, type=click.IntRange(min=1), show_default=True)
@click.option("--base-lr", default=2e-5, type=click.FloatRange(min=0, min_open=True), show_default=True)
@click.option("--head-lr", default=1e-4, type=click.FloatRange(min=0, min_open=True), show_default=True)
@click.option("--aux-ce-weight", default=0.3, type=click.FloatRange(min=0), show_default=True)
@click.option(
    "--optimizer", type=click.Choice(["adamw", "adamw-8bit"]),
    default="adamw", show_default=True,
)
@click.option(
    "--precision", type=click.Choice(["fp32", "bf16"]),
    default="fp32", show_default=True,
)
@click.option("--no-crf", is_flag=True, default=False, help="Train without the CRF head.")
@click.option("--evaluate-test", is_flag=True, help="Evaluate test data after selection.")
@click.option(
    "--with-isr", is_flag=True,
    help="Report predicted-phrase locatability during final test evaluation.",
)
@click.option("--limit", default=0, type=click.IntRange(min=0), help="Limit effective examples per split.")
@click.option("--resume", is_flag=True, hidden=True, help="Unsupported.")
@click.option("--seed", default=42, type=click.IntRange(min=0), show_default=True)
def main(
    data_dir, output_dir, model_name, model_revision, max_length, epochs,
    batch_size, grad_accum, base_lr, head_lr, aux_ce_weight, optimizer,
    precision, no_crf, evaluate_test, with_isr, limit, resume, seed,
):
    """Train the required phrase tagger from a positive BIOES dataset."""
    if with_isr and not evaluate_test:
        raise click.UsageError("--with-isr requires --evaluate-test")
    if resume:
        raise click.UsageError("--resume is unsupported for final hardened training")
    config = Config(
        data_dir=data_dir,
        output_dir=output_dir,
        model_name=model_name,
        model_revision=model_revision,
        max_length=max_length,
        epochs=epochs,
        batch_size=batch_size,
        grad_accum=grad_accum,
        base_lr=base_lr,
        head_lr=head_lr,
        aux_ce_weight=aux_ce_weight,
        optimizer=optimizer,
        precision=precision,
        use_crf=not no_crf,
        evaluate_test=evaluate_test,
        with_isr=with_isr,
        limit=limit,
        resume=resume,
        seed=seed,
    )
    try:
        run_training(config)
    except ImportError as error:
        raise click.ClickException(
            f"{error}; install scancode-required-phrases[training]"
        ) from error


if __name__ == "__main__":
    main()
