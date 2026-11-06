# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Export a completed required phrase model for CPU inference."""

import hashlib
import json
import os
from pathlib import Path
import shutil

import click

os.environ.setdefault("USE_TF", "0")

EXPORT_SCHEMA = "scancode-required-phrases-export-v1"
PARITY_CASES = (
    "one-word-tie",
    "normal",
    "variable-length",
    "boundary",
    "extreme-forbidden",
)


class OnnxDependencyError(RuntimeError):
    """Raised when an explicitly requested ONNX export cannot run."""


def _require_float_array(name, value, shape=None):
    """Return a validated floating-point NumPy array."""
    import numpy as np

    if not isinstance(value, np.ndarray):
        raise TypeError(f"{name} must be a NumPy array")
    if not np.issubdtype(value.dtype, np.floating):
        raise TypeError(f"{name} must have a floating-point dtype")
    if shape is not None and value.shape != shape:
        raise ValueError(f"{name} must have shape {shape}, not {value.shape}")
    if np.isnan(value).any():
        raise ValueError(f"{name} contains NaN scores")
    return value


def viterbi_decode(
    emissions,
    start_transitions,
    transitions,
    end_transitions,
    num_labels=None,
):
    """Return the best tag path for one validated, non-empty sequence."""
    import numpy as np

    emissions = _require_float_array("emissions", emissions)
    if emissions.ndim != 2:
        raise ValueError("emissions must have shape (sequence_length, labels)")
    sequence_length, inferred_labels = emissions.shape
    if sequence_length == 0 or inferred_labels == 0:
        raise ValueError("emissions must contain at least one token and label")
    if num_labels is not None:
        if isinstance(num_labels, bool) or not isinstance(num_labels, int):
            raise TypeError("num_labels must be an integer")
        if num_labels <= 0 or num_labels != inferred_labels:
            raise ValueError(f"emissions have {inferred_labels} labels, expected {num_labels}")

    start_transitions = _require_float_array(
        "start_transitions", start_transitions, (inferred_labels,)
    )
    transitions = _require_float_array(
        "transitions", transitions, (inferred_labels, inferred_labels)
    )
    end_transitions = _require_float_array("end_transitions", end_transitions, (inferred_labels,))

    with np.errstate(invalid="ignore"):
        score = start_transitions + emissions[0]
    if np.isnan(score).any():
        raise ValueError("start and emission scores produce NaN")
    if np.isneginf(score).all():
        raise ValueError("no valid Viterbi path at token 0")

    backpointers = []
    for step in range(1, sequence_length):
        with np.errstate(invalid="ignore"):
            candidates = score[:, None] + transitions
            best_source = candidates.argmax(axis=0)
            score = candidates.max(axis=0) + emissions[step]
        if np.isnan(score).any():
            raise ValueError(f"scores produce NaN at token {step}")
        if np.isneginf(score).all():
            raise ValueError(f"no valid Viterbi path at token {step}")
        backpointers.append(best_source)

    with np.errstate(invalid="ignore"):
        score = score + end_transitions
    if np.isnan(score).any():
        raise ValueError("end and path scores produce NaN")
    if np.isneginf(score).all():
        raise ValueError("no valid Viterbi path reaches an end label")

    best = int(score.argmax())
    path = [best]
    for sources in reversed(backpointers):
        best = int(sources[best])
        path.append(best)
    path.reverse()
    return path


def sha256(path):
    """Return the hexadecimal SHA256 digest of a file."""
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _training_interfaces():
    """Import final-artifact interfaces without importing optional ONNX code."""
    from train_model import ARTIFACT_SCHEMA
    from train_model import CONSTRAINT_CONTRACT
    from train_model import LABELS
    from train_model import load_final_model
    from train_model import validate_bioes
    from train_model import validate_publishable_model
    from train_model import write_json_atomic

    return (
        ARTIFACT_SCHEMA,
        CONSTRAINT_CONTRACT,
        tuple(LABELS),
        load_final_model,
        validate_bioes,
        validate_publishable_model,
        write_json_atomic,
    )


def _load_publishable_artifact(model_dir, require_crf=False):
    """Validate and load one supported Final_Model entirely from local files."""
    (
        artifact_schema,
        constraint_contract,
        labels,
        load_final_model,
        _validate_bioes,
        validate_publishable_model,
        _write_json_atomic,
    ) = _training_interfaces()

    model_dir = Path(model_dir)
    validate_publishable_model(model_dir)

    config_path = model_dir / "train_config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if config.get("artifact_schema") != artifact_schema:
        raise ValueError("Final_Model uses an unsupported artifact schema")
    if tuple(config.get("labels", ())) != labels:
        raise ValueError("Final_Model labels do not match the supported label order")
    if config.get("constraint_contract") != constraint_contract:
        raise ValueError("Final_Model uses an unsupported constraint contract")
    if type(require_crf) is not bool:
        raise TypeError("require_crf must be a boolean")

    loaded = load_final_model(model_dir, offline=True)
    if not isinstance(loaded, tuple) or len(loaded) < 2:
        raise TypeError("load_final_model must return (model, tokenizer)")
    tagger, tokenizer = loaded[:2]
    if require_crf and (
        config.get("use_crf") is not True
        or not getattr(tagger, "use_crf", False)
        or not hasattr(tagger, "crf")
    ):
        raise ValueError("CRF matrix export requires a Final_Model with a CRF")

    marker_path = model_dir / "SUCCESS.json"
    marker = json.loads(marker_path.read_text(encoding="utf-8"))
    return tagger.eval(), tokenizer, config, marker


def _effective_crf_matrices(tagger):
    """Return effective constrained CRF matrices without mutating learned values."""
    import numpy as np
    import torch

    crf = tagger.crf
    values = (
        (
            "start_transitions",
            "start_mask",
            "effective_start_transitions",
            (tagger.num_labels,),
        ),
        (
            "transitions",
            "transition_mask",
            "effective_transitions",
            (tagger.num_labels, tagger.num_labels),
        ),
        (
            "end_transitions",
            "end_mask",
            "effective_end_transitions",
            (tagger.num_labels,),
        ),
    )
    effective = []
    for parameter_name, mask_name, effective_name, shape in values:
        parameter = getattr(crf, parameter_name, None)
        mask = getattr(crf, mask_name, None)
        constrained = getattr(crf, effective_name, None)
        if parameter is None or mask is None or constrained is None:
            raise ValueError(f"CRF is missing {parameter_name}, {mask_name}, or {effective_name}")
        if (
            tuple(parameter.shape) != shape
            or tuple(mask.shape) != shape
            or tuple(constrained.shape) != shape
        ):
            raise ValueError(f"CRF effective {parameter_name} shapes are invalid")
        if mask.dtype != torch.bool:
            raise TypeError(f"CRF {mask_name} must be boolean")
        if not torch.isfinite(parameter).all():
            raise ValueError(f"CRF {parameter_name} contains non-finite learned values")
        expected = parameter.masked_fill(~mask, -torch.inf)
        if not torch.equal(constrained, expected):
            raise ValueError(f"CRF {effective_name} does not apply the supported masks")
        array = constrained.detach().cpu().numpy().copy()
        if np.isnan(array).any():
            raise ValueError(f"effective CRF {parameter_name} contains NaN")
        effective.append(array)
    return tuple(effective)


def _parity_batches(num_labels):
    """Return deterministic normal, variable, boundary, and adversarial batches."""
    import numpy as np

    normal = np.zeros((3, num_labels), dtype=np.float32)
    normal[0, 1] = 4.0
    normal[1, 2] = 4.0
    normal[2, 3] = 4.0

    variable = np.arange(6 * num_labels, dtype=np.float32).reshape(6, num_labels)
    variable = (variable % 7.0) - 3.0
    variable_batch = np.stack((np.roll(variable, 1, axis=1), variable))

    boundary = np.zeros((4, num_labels), dtype=np.float32)
    boundary[0, 2] = 1_000.0
    boundary[1, 3] = 1_000.0
    boundary[-1, 1] = 1_000.0

    adversarial = np.full((5, num_labels), -10_000.0, dtype=np.float32)
    adversarial[:, 2] = 10_000.0
    adversarial[0, 3] = 20_000.0
    adversarial[-1, 1] = 20_000.0

    return (
        (PARITY_CASES[1], normal[None, :, :], (3,)),
        (PARITY_CASES[2], variable_batch, (2, 6)),
        (PARITY_CASES[3], boundary[None, :, :], (4,)),
        (PARITY_CASES[4], adversarial[None, :, :], (5,)),
    )


def _exact_one_word_tie(start, end):
    """Return emissions that produce an exact tie under exported edge scores."""
    import numpy as np

    legal = np.flatnonzero(np.isfinite(start) & np.isfinite(end))
    if legal.size < 2:
        raise ValueError("CRF constraints must permit at least two one-word paths")

    candidates_by_label = {}
    for label in legal:
        base = np.float32(-(np.float64(start[label]) + np.float64(end[label])))
        candidates = {}
        lower = upper = base
        for _step in range(16_385):
            for emission in (lower, upper):
                score = np.float32(np.float32(start[label] + emission) + end[label])
                candidates.setdefault(score.tobytes(), (emission, score))
            lower = np.float32(np.nextafter(lower, np.float32(-np.inf)))
            upper = np.float32(np.nextafter(upper, np.float32(np.inf)))
        candidates_by_label[int(label)] = candidates

    for left_index, left in enumerate(legal[:-1]):
        left = int(left)
        for right_value in legal[left_index + 1 :]:
            right = int(right_value)
            shared = set(candidates_by_label[left]).intersection(candidates_by_label[right])
            if not shared:
                continue
            score_key = min(shared)
            left_emission, tied_score = candidates_by_label[left][score_key]
            right_emission, right_score = candidates_by_label[right][score_key]
            if tied_score.tobytes() != right_score.tobytes():
                raise AssertionError("Constructed tie scores are not exactly equal")
            emissions = np.zeros((1, len(start)), dtype=np.float32)
            for label in legal:
                label = int(label)
                baseline = -(
                    np.float64(start[label]) + np.float64(end[label]) + 10_000.0
                )
                emissions[0, label] = np.float32(baseline)
            emissions[0, left] = left_emission
            emissions[0, right] = right_emission
            return emissions, tied_score
    raise AssertionError("Could not construct an exact tie from exported CRF edge scores")


def check_viterbi_matches_crf(tagger, num_tags):
    """Verify exact NumPy/PyTorch constrained paths on deterministic cases."""
    import numpy as np
    import torch

    (
        _artifact_schema,
        _constraint_contract,
        labels,
        _load_final_model,
        validate_bioes,
        _validate_publishable_model,
        _write_json_atomic,
    ) = _training_interfaces()
    if isinstance(num_tags, bool) or not isinstance(num_tags, int):
        raise TypeError("num_tags must be an integer")
    if num_tags != len(labels) or num_tags != tagger.num_labels:
        raise ValueError("Parity label count does not match the supported labels")

    start, transitions, end = _effective_crf_matrices(tagger)
    tie_emissions, tied_score = _exact_one_word_tie(start, end)
    terminal_scores = np.float32(np.float32(start + tie_emissions[0]) + end)
    if np.count_nonzero(terminal_scores == tied_score) < 2:
        raise AssertionError("Exported matrices did not produce the constructed exact tie")
    tie_tensor = torch.from_numpy(tie_emissions).unsqueeze(0)
    tie_mask = torch.ones((1, 1), dtype=torch.bool)
    tie_path = tagger.crf.decode(tie_tensor, mask=tie_mask)[0]
    numpy_tie_path = viterbi_decode(
        tie_emissions,
        start,
        transitions,
        end,
        num_labels=num_tags,
    )
    if numpy_tie_path != tie_path:
        raise AssertionError(
            f"NumPy Viterbi disagrees with PyTorch for exact tie: "
            f"{numpy_tie_path} != {tie_path}"
        )
    tie_error = validate_bioes([labels[tag] for tag in tie_path])
    if tie_error:
        raise AssertionError(f"Exact tie parity decoded {tie_error}")

    start, transitions, end = _effective_crf_matrices(tagger)
    for case_name, emissions, lengths in _parity_batches(num_tags):
        tensor = torch.from_numpy(emissions)
        mask = torch.arange(tensor.shape[1]).unsqueeze(0) < torch.tensor(lengths).unsqueeze(1)
        pytorch_paths = tagger.crf.decode(tensor, mask=mask)
        if len(pytorch_paths) != len(lengths):
            raise AssertionError(f"PyTorch returned an invalid batch for {case_name}")
        for row, length in enumerate(lengths):
            numpy_path = viterbi_decode(
                emissions[row, :length],
                start,
                transitions,
                end,
                num_labels=num_tags,
            )
            if numpy_path != pytorch_paths[row]:
                raise AssertionError(
                    f"NumPy Viterbi disagrees with PyTorch for {case_name} row {row}: "
                    f"{numpy_path} != {pytorch_paths[row]}"
                )
            path_error = validate_bioes([labels[tag] for tag in numpy_path])
            if path_error:
                raise AssertionError(f"Parity case {case_name} row {row} decoded {path_error}")
    return start, transitions, end


def _export_manifest(marker, matrix_path, onnx_path=None):
    """Return the export manifest for one validated Final_Model."""
    artifact_schema, constraint_contract, labels, *_unused = _training_interfaces()
    manifest = {
        "schema": EXPORT_SCHEMA,
        "artifact_schema": artifact_schema,
        "constraint_contract": constraint_contract,
        "labels": list(labels),
        "source_final_model": marker,
        "crf_transitions": sha256(matrix_path),
        "parity": {"passed": True, "cases": list(PARITY_CASES)},
    }
    if onnx_path is not None:
        manifest["onnx_model"] = sha256(onnx_path)
    return manifest


def _prepare_export_stage(model_dir, output_dir):
    """Return a new staging directory and absent final export destination."""
    model_dir = Path(model_dir).resolve()
    output_dir = Path(output_dir).resolve()
    if output_dir == model_dir or model_dir in output_dir.parents:
        raise ValueError("Export output must be outside the Final_Model directory")
    if output_dir.exists():
        if not output_dir.is_dir():
            raise ValueError(f"Export output is not a directory: {output_dir}")
        if any(output_dir.iterdir()):
            raise ValueError(f"Export output directory is not empty: {output_dir}")
        output_dir.rmdir()
    stage = output_dir.with_name(f"{output_dir.name}.tmp")
    if stage.exists():
        raise ValueError(f"Export staging directory already exists: {stage}")
    stage.parent.mkdir(parents=True, exist_ok=True)
    stage.mkdir()
    return stage, output_dir


def _promote_export(stage, output_dir):
    """Atomically publish one completely verified export directory."""
    os.replace(stage, output_dir)


def export_crf_matrices(model_dir, output_dir):
    """Export effective constrained matrices without importing ONNX packages."""
    import numpy as np

    tagger, _tokenizer, config, marker = _load_publishable_artifact(
        model_dir, require_crf=True
    )
    start, transitions, end = check_viterbi_matches_crf(tagger, len(config["labels"]))
    stage, output_dir = _prepare_export_stage(model_dir, output_dir)
    try:
        matrix_path = stage / "crf_transitions.npz"
        np.savez(matrix_path, start=start, transitions=transitions, end=end)
        manifest_path = stage / "manifest.json"
        *_interfaces, write_json_atomic = _training_interfaces()
        write_json_atomic(
            manifest_path,
            _export_manifest(marker, matrix_path),
        )
        _promote_export(stage, output_dir)
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise
    return output_dir / matrix_path.name, output_dir / manifest_path.name


def build_emissions_module(tagger):
    """Wrap only emissions computation for ONNX export."""
    import torch.nn as nn

    class EmissionsModule(nn.Module):
        def __init__(self):
            super().__init__()
            self.tagger = tagger

        def forward(self, input_ids, attention_mask):
            return self.tagger.emissions(input_ids, attention_mask)

    return EmissionsModule().eval()


def export_onnx_emissions(model_dir, output_dir, opset=14):
    """Export and verify optional ONNX emissions for a publishable model."""
    tagger, tokenizer, config, marker = _load_publishable_artifact(model_dir)
    try:
        import numpy as np
        import onnx
        import onnxruntime
        import torch
    except ImportError as error:
        raise OnnxDependencyError(
            "ONNX export requires scancode-required-phrases[training,onnx]"
        ) from error
    _ = onnx

    stage, output_dir = _prepare_export_stage(model_dir, output_dir)
    try:
        emissions_module = build_emissions_module(tagger)
        sample = tokenizer(
            "Licensed under the Apache License Version 2.0",
            return_tensors="pt",
        )
        inputs = sample["input_ids"], sample["attention_mask"]
        onnx_path = stage / "model.onnx"
        torch.onnx.export(
            emissions_module,
            inputs,
            str(onnx_path),
            input_names=["input_ids", "attention_mask"],
            output_names=["emissions"],
            dynamic_axes={
                "input_ids": {0: "batch", 1: "sequence"},
                "attention_mask": {0: "batch", 1: "sequence"},
                "emissions": {0: "batch", 1: "sequence"},
            },
            opset_version=opset,
            do_constant_folding=True,
        )

        session = onnxruntime.InferenceSession(
            str(onnx_path), providers=["CPUExecutionProvider"]
        )
        feeds = {
            "input_ids": sample["input_ids"].numpy(),
            "attention_mask": sample["attention_mask"].numpy(),
        }
        onnx_emissions = session.run(["emissions"], feeds)[0]
        torch_emissions = emissions_module(*inputs).detach().cpu().numpy()
        if not isinstance(onnx_emissions, np.ndarray):
            raise TypeError("ONNX emissions output must be a NumPy array")
        if onnx_emissions.shape != torch_emissions.shape:
            raise ValueError(
                f"ONNX emissions shape {onnx_emissions.shape} differs from "
                f"PyTorch {torch_emissions.shape}"
            )
        if onnx_emissions.dtype != torch_emissions.dtype:
            raise TypeError(
                f"ONNX emissions dtype {onnx_emissions.dtype} differs from "
                f"PyTorch {torch_emissions.dtype}"
            )
        if not np.issubdtype(onnx_emissions.dtype, np.floating):
            raise TypeError("ONNX emissions must have a floating-point dtype")
        if not np.isfinite(onnx_emissions).all() or not np.isfinite(torch_emissions).all():
            raise ValueError("ONNX and PyTorch emissions must contain only finite values")
        if not np.allclose(onnx_emissions, torch_emissions, atol=1e-3, rtol=1e-5):
            raise AssertionError("ONNX emissions differ from PyTorch emissions")
        manifest_path = stage / "manifest.json"
        (
            artifact_schema,
            constraint_contract,
            labels,
            _load_final_model,
            _validate_bioes,
            _validate_publishable_model,
            write_json_atomic,
        ) = _training_interfaces()
        write_json_atomic(
            manifest_path,
            {
                "schema": EXPORT_SCHEMA,
                "artifact_schema": artifact_schema,
                "constraint_contract": constraint_contract,
                "labels": list(labels),
                "source_final_model": marker,
                "onnx_model": sha256(onnx_path),
                "opset": opset,
                "source_model_revision": config["resolved_model_revision"],
            },
        )
        _promote_export(stage, output_dir)
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise
    return output_dir / onnx_path.name, output_dir / manifest_path.name


@click.command()
@click.option(
    "--model-dir",
    required=True,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Completed local Final_Model directory.",
)
@click.option(
    "--output-dir",
    required=True,
    type=click.Path(file_okay=False, path_type=Path),
    help="New or empty directory for this export operation.",
)
@click.option(
    "--operation",
    type=click.Choice(["crf", "onnx"]),
    default="crf",
    show_default=True,
    help="Artifact operation to run.",
)
@click.option("--opset", default=14, type=int, show_default=True)
def main(model_dir, output_dir, operation, opset):
    """Export constrained matrices or optional ONNX emissions."""
    try:
        if operation == "onnx":
            paths = export_onnx_emissions(model_dir, output_dir, opset)
        else:
            paths = export_crf_matrices(model_dir, output_dir)
    except OnnxDependencyError as error:
        raise click.ClickException(str(error)) from error
    for path in paths:
        click.echo(f"wrote {path}")


if __name__ == "__main__":
    main()
