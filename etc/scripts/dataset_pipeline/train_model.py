# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Train a DeBERTa BIOES tagger for required phrase spans."""

from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
import hashlib
import importlib.metadata
import inspect
import json
import os
from pathlib import Path
import platform
import random

import click

os.environ.setdefault("USE_TF", "0")


LABELS = ["O", "B-REQ", "I-REQ", "E-REQ", "S-REQ"]
LABEL2ID = {label: index for index, label in enumerate(LABELS)}
ID2LABEL = {index: label for index, label in enumerate(LABELS)}
IGNORE_INDEX = -100

MODEL_NAME = "microsoft/deberta-v3-large"
MAX_LENGTH = 512
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


def validate_config(config):
    """Validate settings before loading the tokenizer or model."""
    if config.optimizer not in {"adamw", "adamw-8bit"}:
        raise ValueError(f"Unsupported optimizer: {config.optimizer}")
    if config.precision not in {"fp32", "bf16"}:
        raise ValueError(f"Unsupported precision: {config.precision}")
    if config.epochs < 1 or config.batch_size < 1 or config.grad_accum < 1:
        raise ValueError("Epochs, batch size, and gradient accumulation must be positive")
    if config.base_lr <= 0 or config.head_lr <= 0:
        raise ValueError("Learning rates must be positive")
    if config.aux_ce_weight < 0:
        raise ValueError("Auxiliary loss weight cannot be negative")
    if len(config.label_weights) != len(LABELS):
        raise ValueError(f"Expected {len(LABELS)} label weights")


def prepare_output_dir(output_dir, resume):
    """Create a new output directory or validate a resumable one."""
    output_dir = Path(output_dir)
    checkpoints = list(output_dir.glob("checkpoint-*")) if output_dir.exists() else []
    if resume and not checkpoints:
        raise ValueError(f"No checkpoint found in {output_dir}")
    if not resume and output_dir.exists() and any(output_dir.iterdir()):
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
    """Yield parsed records from a JSONL file."""
    with open(path, encoding="utf-8") as lines:
        for line_number, line in enumerate(lines, 1):
            line = line.strip()
            if line:
                yield line_number, json.loads(line)


def validate_bioes(labels):
    """Return an error for an invalid BIOES sequence, or None."""
    if not labels:
        return "has no labels"
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


def validate_record(record, path, line_number):
    """Validate one dataset record and return it."""
    location = f"{path} line {line_number}"
    for field_name in RECORD_FIELDS:
        if field_name not in record:
            raise ValueError(f"{location}: missing {field_name!r}")

    identifier = record["identifier"]
    if not identifier:
        raise ValueError(f"{location}: empty identifier")
    if not record["license_expression"]:
        raise ValueError(f"{location} ({identifier}): empty license expression")
    if not record["rule_type"]:
        raise ValueError(f"{location} ({identifier}): empty rule type")

    tokens = record["tokens"]
    labels = record["bioes_labels"]
    if not tokens:
        raise ValueError(f"{location} ({identifier}): no tokens")
    if len(tokens) != len(labels):
        raise ValueError(
            f"{location} ({identifier}): {len(tokens)} tokens and {len(labels)} labels"
        )

    unknown = sorted(set(labels) - set(LABELS))
    if unknown:
        raise ValueError(f"{location} ({identifier}): unknown labels: {unknown}")

    error = validate_bioes(labels)
    if error:
        raise ValueError(f"{location} ({identifier}): {error}")
    return record


def align_labels(tokens, word_labels, tokenizer, max_length):
    """Tokenize words and label only the first subword of each word."""
    encoding = tokenizer(
        tokens,
        is_split_into_words=True,
        truncation=True,
        max_length=max_length,
    )

    word_ids = encoding.word_ids()
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
    kept_word_ids = [word_id for word_id in word_ids if word_id is not None]
    kept_words = max(kept_word_ids) + 1 if kept_word_ids else 0
    truncated = kept_words < len(tokens)
    cut_phrase = (
        truncated
        and kept_words
        and word_labels[kept_words - 1]
        in {
            "B-REQ",
            "I-REQ",
        }
    )
    return encoding, truncated, bool(cut_phrase)


def first_subword_positions(word_ids):
    """Return positions that start a tokenizer word."""
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
    """Read and encode one BIOES JSONL split."""

    def __init__(self, path, tokenizer, max_length, limit=0):
        self.examples = []
        self.identifiers = []
        self.truncated = 0
        self.cut_phrases = 0

        for line_number, unvalidated_record in load_jsonl(path):
            if limit and len(self.examples) >= limit:
                break
            record = validate_record(unvalidated_record, path, line_number)
            encoding, truncated, cut_phrase = align_labels(
                record["tokens"],
                record["bioes_labels"],
                tokenizer,
                max_length,
            )
            if truncated:
                self.truncated += 1
            if cut_phrase:
                self.cut_phrases += 1
                continue

            self.identifiers.append(record["identifier"])
            self.examples.append(
                {
                    "input_ids": encoding["input_ids"],
                    "attention_mask": encoding["attention_mask"],
                    "labels": encoding["labels"],
                }
            )

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, index):
        return self.examples[index]


def validate_splits(datasets):
    """Require non-empty splits with disjoint rule identifiers."""
    seen = {}
    for split_name, dataset in datasets.items():
        if not dataset:
            raise ValueError(f"{split_name} split has no usable examples")
        for identifier in dataset.identifiers:
            previous_split = seen.get(identifier)
            if previous_split:
                raise ValueError(
                    f"Rule {identifier!r} occurs in both {previous_split} and {split_name}"
                )
            seen[identifier] = split_name


def extract_spans(tags):
    """Return the set of inclusive word spans in a BIOES sequence."""
    spans = []
    start = None
    for index, tag in enumerate(tags):
        if tag == "S-REQ":
            spans.append((index, index))
            start = None
        elif tag == "B-REQ":
            if start is not None:
                spans.append((start, index - 1))
            start = index
        elif tag == "I-REQ":
            if start is None:
                start = index
        elif tag == "E-REQ":
            if start is None:
                start = index
            spans.append((start, index))
            start = None
        elif start is not None:
            spans.append((start, index - 1))
            start = None
    if start is not None:
        spans.append((start, len(tags) - 1))
    return set(spans)


def decode_row(pred_row, label_row):
    """Drop ignored positions and map label IDs to BIOES tags."""
    predicted = []
    actual = []
    for prediction, label in zip(pred_row, label_row):
        if int(label) == IGNORE_INDEX:
            continue
        actual.append(ID2LABEL[int(label)])
        predicted.append(ID2LABEL.get(int(prediction), "O"))
    return predicted, actual


def compute_metrics(eval_pred):
    """Return strict span-level micro metrics and rule-level exact match."""
    predictions, labels = eval_pred
    true_positive = false_positive = false_negative = 0
    exact = 0

    for pred_row, label_row in zip(predictions, labels):
        predicted, actual = decode_row(pred_row, label_row)
        predicted_spans = extract_spans(predicted)
        actual_spans = extract_spans(actual)
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
        "exact_match": exact / len(predictions) if len(predictions) else 0.0,
        "predicted_spans": true_positive + false_positive,
        "gold_spans": true_positive + false_negative,
    }


def evaluate_isr(records, model, tokenizer, max_length):
    """Return the fraction of predicted phrases ScanCode can locate."""
    import torch
    from licensedcode.required_phrases import find_phrase_spans_in_text

    device = next(model.parameters()).device
    model.eval()
    total = 0
    injectable = 0
    for record in records:
        encoding, _, cut_phrase = align_labels(
            record["tokens"],
            record["bioes_labels"],
            tokenizer,
            max_length,
        )
        if cut_phrase:
            continue
        inputs = {
            "input_ids": torch.tensor([encoding["input_ids"]], device=device),
            "attention_mask": torch.tensor([encoding["attention_mask"]], device=device),
            "labels": torch.tensor([encoding["labels"]], device=device),
        }
        with torch.no_grad():
            output = model(**inputs)
        tags, _ = decode_row(
            output["predictions"][0].tolist(),
            output["word_labels"][0].tolist(),
        )
        for start, end in extract_spans(tags):
            if end >= len(record["tokens"]):
                continue
            phrase = " ".join(record["tokens"][start : end + 1])
            total += 1
            if find_phrase_spans_in_text(record["text"], phrase):
                injectable += 1

    return injectable / total if total else 0.0


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
    """Return the training configuration with paths converted to strings."""
    values = asdict(config)
    values["data_dir"] = str(values["data_dir"])
    values["output_dir"] = str(values["output_dir"])
    return values


def validate_saved_state(model, model_path):
    """Validate the keys, shapes, and values in a saved safetensors model."""
    import torch
    from safetensors.torch import load_file

    saved = load_file(str(model_path))
    expected = model.state_dict()
    if set(saved) != set(expected):
        missing = sorted(set(expected) - set(saved))
        unexpected = sorted(set(saved) - set(expected))
        raise ValueError(f"Saved model key mismatch; missing={missing}, unexpected={unexpected}")

    for name, tensor in saved.items():
        if tensor.shape != expected[name].shape:
            raise ValueError(
                f"Saved tensor {name!r} has shape {tuple(tensor.shape)}, "
                f"expected {tuple(expected[name].shape)}"
            )
        if not torch.isfinite(tensor).all():
            raise ValueError(f"Saved tensor {name!r} contains non-finite values")


def validate_precision(precision):
    """Validate the selected training precision."""
    import torch

    if precision == "bf16" and not (torch.cuda.is_available() and torch.cuda.is_bf16_supported()):
        raise ValueError("bf16 requires a CUDA device with BF16 support")


def run_training(config):
    """Train, validate, and save a required phrase model."""
    import torch
    import transformers
    from transformers import AutoTokenizer
    from transformers import DataCollatorForTokenClassification
    from transformers import EarlyStoppingCallback
    from transformers import TrainingArguments

    from phrase_model import PhraseTagger
    from phrase_model import PhraseTrainer
    from phrase_model import build_optimizer

    if config.with_isr and not config.evaluate_test:
        raise ValueError("ISR evaluation requires --evaluate-test")

    validate_config(config)
    validate_precision(config.precision)
    prepare_output_dir(config.output_dir, config.resume)
    set_seed(config.seed)

    tokenizer = AutoTokenizer.from_pretrained(
        config.model_name,
        revision=config.model_revision,
        use_fast=True,
    )
    if not tokenizer.is_fast:
        raise RuntimeError("Training requires a fast tokenizer with word IDs")

    paths = {
        "train": config.data_dir / "train.jsonl",
        "validation": config.data_dir / "val.jsonl",
        "test": config.data_dir / "test.jsonl",
    }
    datasets = {
        name: PhraseDataset(path, tokenizer, config.max_length, config.limit)
        for name, path in paths.items()
    }
    validate_splits(datasets)

    for name, dataset in datasets.items():
        click.echo(
            f"{name}: {len(dataset)} examples, {dataset.truncated} truncated, "
            f"{dataset.cut_phrases} skipped with a cut phrase"
        )

    model = PhraseTagger(config)
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
        "compute_metrics": compute_metrics,
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

    trainer = PhraseTrainer(**trainer_kwargs)
    trainer.train(resume_from_checkpoint=config.resume or None)

    trainer.save_model(str(config.output_dir))
    tokenizer.save_pretrained(str(config.output_dir))

    resolved_revision = getattr(model.backbone.config, "_commit_hash", None)
    train_config = {
        "model_name": config.model_name,
        "model_revision": resolved_revision or config.model_revision,
        "use_crf": config.use_crf,
        "max_length": config.max_length,
        "labels": LABELS,
    }
    (config.output_dir / "train_config.json").write_text(
        json.dumps(train_config, indent=2),
        encoding="utf-8",
    )

    model_path = config.output_dir / "model.safetensors"
    validate_saved_state(model, model_path)

    validation_metrics = trainer.evaluate(
        datasets["validation"],
        metric_key_prefix="validation",
    )
    test_metrics = None
    if config.evaluate_test:
        test_metrics = trainer.evaluate(
            datasets["test"],
            metric_key_prefix="test",
        )
        if config.with_isr:
            test_records = [
                validate_record(record, paths["test"], line_number)
                for line_number, record in load_jsonl(paths["test"])
            ]
            test_metrics["test_isr"] = evaluate_isr(
                test_records,
                model,
                tokenizer,
                config.max_length,
            )

    manifest = {
        "config": serializable_config(config),
        "dataset": {
            name: {
                "path": str(path),
                "sha256": sha256(path),
                "examples": len(datasets[name]),
                "truncated": datasets[name].truncated,
                "cut_phrases": datasets[name].cut_phrases,
            }
            for name, path in paths.items()
        },
        "model_revision": resolved_revision or config.model_revision,
        "best_checkpoint": trainer.state.best_model_checkpoint,
        "best_validation_f1": trainer.state.best_metric,
        "validation_metrics": validation_metrics,
        "test_metrics": test_metrics,
        "log_history": trainer.state.log_history,
        "versions": {
            "python": platform.python_version(),
            "torch": torch.__version__,
            "transformers": transformers.__version__,
            "scancode_toolkit": installed_version("scancode-toolkit"),
            "pytorch_crf": installed_version("pytorch-crf"),
        },
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
    }
    (config.output_dir / "run_manifest.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )

    click.echo(f"best checkpoint: {trainer.state.best_model_checkpoint}")
    click.echo(f"best validation F1: {trainer.state.best_metric}")
    click.echo(f"validation: {validation_metrics}")
    if test_metrics is not None:
        click.echo(f"test: {test_metrics}")

    return {
        "validation": validation_metrics,
        "test": test_metrics,
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
    help="Directory for checkpoints and the final model.",
)
@click.option("--model-name", default=MODEL_NAME, help="Base model to fine-tune.")
@click.option("--model-revision", default=None, help="Optional model revision to pin.")
@click.option(
    "--max-length",
    default=MAX_LENGTH,
    type=click.IntRange(min=3, max=MAX_LENGTH),
    show_default=True,
)
@click.option("--epochs", default=8, type=click.IntRange(min=1), show_default=True)
@click.option("--batch-size", default=1, type=int, show_default=True)
@click.option("--grad-accum", default=16, type=int, show_default=True)
@click.option("--base-lr", default=2e-5, type=float, show_default=True)
@click.option("--head-lr", default=1e-4, type=float, show_default=True)
@click.option("--aux-ce-weight", default=0.3, type=float, show_default=True)
@click.option(
    "--optimizer",
    type=click.Choice(["adamw", "adamw-8bit"]),
    default="adamw",
    show_default=True,
)
@click.option(
    "--precision",
    type=click.Choice(["fp32", "bf16"]),
    default="fp32",
    show_default=True,
)
@click.option("--no-crf", is_flag=True, default=False, help="Train without the CRF head.")
@click.option(
    "--evaluate-test",
    is_flag=True,
    default=False,
    help="Evaluate the test split after training.",
)
@click.option(
    "--with-isr",
    is_flag=True,
    default=False,
    help="Report injection success rate with final test evaluation.",
)
@click.option("--limit", default=0, type=int, help="Limit examples per split; zero uses all.")
@click.option("--resume", is_flag=True, default=False, help="Resume from the latest checkpoint.")
@click.option("--seed", default=42, type=int, show_default=True)
def main(
    data_dir,
    output_dir,
    model_name,
    model_revision,
    max_length,
    epochs,
    batch_size,
    grad_accum,
    base_lr,
    head_lr,
    aux_ce_weight,
    optimizer,
    precision,
    no_crf,
    evaluate_test,
    with_isr,
    limit,
    resume,
    seed,
):
    """Train the required phrase tagger from a BIOES dataset."""
    if with_isr and not evaluate_test:
        raise click.UsageError("--with-isr requires --evaluate-test")

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
