# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import builtins
import json
from pathlib import Path
import sys
import types

import pytest
from click.testing import CliRunner

np = pytest.importorskip("numpy")

import export_onnx as export_module
import train_model as training
from export_onnx import check_viterbi_matches_crf
from export_onnx import export_crf_matrices
from export_onnx import export_onnx_emissions
from export_onnx import main
from export_onnx import _load_publishable_artifact
from export_onnx import OnnxDependencyError
from export_onnx import PARITY_CASES
from export_onnx import sha256
from export_onnx import viterbi_decode

LABELS = ("O", "B-REQ", "I-REQ", "E-REQ", "S-REQ")
ARTIFACT_SCHEMA = "test-artifact-v2"
CONSTRAINT_CONTRACT = "bioes-hard-v1"


def validate_bioes(labels):
    starts = {"O", "B-REQ", "S-REQ"}
    ends = {"O", "E-REQ", "S-REQ"}
    transitions = {
        "O": {"O", "B-REQ", "S-REQ"},
        "B-REQ": {"I-REQ", "E-REQ"},
        "I-REQ": {"I-REQ", "E-REQ"},
        "E-REQ": {"O", "B-REQ", "S-REQ"},
        "S-REQ": {"O", "B-REQ", "S-REQ"},
    }
    if labels[0] not in starts:
        return f"starts with {labels[0]}"
    for previous, current in zip(labels, labels[1:]):
        if current not in transitions[previous]:
            return f"contains invalid transition {previous} -> {current}"
    if labels[-1] not in ends:
        return f"ends with {labels[-1]}"
    return None


def make_masks(torch):
    start = torch.tensor([True, True, False, False, True])
    transition = torch.tensor(
        [
            [True, True, False, False, True],
            [False, False, True, True, False],
            [False, False, True, True, False],
            [True, True, False, False, True],
            [True, True, False, False, True],
        ]
    )
    end = torch.tensor([True, False, False, True, True])
    return start, transition, end


class FakeConstrainedCRF:
    def __init__(self, torch):
        self.torch = torch
        self.start_transitions = torch.nn.Parameter(torch.zeros(5))
        self.transitions = torch.nn.Parameter(torch.zeros((5, 5)))
        self.end_transitions = torch.nn.Parameter(torch.zeros(5))
        self.start_mask, self.transition_mask, self.end_mask = make_masks(torch)

    @property
    def effective_start_transitions(self):
        return self.start_transitions.masked_fill(~self.start_mask, -self.torch.inf)

    @property
    def effective_transitions(self):
        return self.transitions.masked_fill(~self.transition_mask, -self.torch.inf)

    @property
    def effective_end_transitions(self):
        return self.end_transitions.masked_fill(~self.end_mask, -self.torch.inf)

    def decode(self, emissions, mask):
        start = self.effective_start_transitions
        transitions = self.effective_transitions
        end = self.effective_end_transitions
        paths = []
        for row in range(emissions.shape[0]):
            length = int(mask[row].sum().item())
            score = start + emissions[row, 0]
            backpointers = []
            for step in range(1, length):
                candidates = score[:, None] + transitions
                score, sources = candidates.max(dim=0)
                score = score + emissions[row, step]
                backpointers.append(sources)
            best = int((score + end).argmax())
            path = [best]
            for sources in reversed(backpointers):
                best = int(sources[best])
                path.append(best)
            paths.append(list(reversed(path)))
        return paths


class FakeTagger:
    def __init__(self, torch):
        self.use_crf = True
        self.num_labels = len(LABELS)
        self.crf = FakeConstrainedCRF(torch)

    def eval(self):
        return self


def install_artifact_helpers(monkeypatch, model_dir, tagger):
    import train_model as training

    config = {
        "artifact_schema": ARTIFACT_SCHEMA,
        "constraint_contract": CONSTRAINT_CONTRACT,
        "labels": list(LABELS),
        "use_crf": True,
    }
    marker = {
        "schema": ARTIFACT_SCHEMA,
        "files": {"model.safetensors": "validated-test-hash"},
    }
    (model_dir / "train_config.json").write_text(json.dumps(config), encoding="utf-8")
    (model_dir / "SUCCESS.json").write_text(json.dumps(marker), encoding="utf-8")
    validation_calls = []

    def validate_publishable_model(path):
        validation_calls.append(path)

    def load_final_model(path, offline):
        assert path == model_dir
        assert offline is True
        return tagger, object()

    def write_json_atomic(path, value):
        path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")

    monkeypatch.setattr(training, "ARTIFACT_SCHEMA", ARTIFACT_SCHEMA, raising=False)
    monkeypatch.setattr(training, "CONSTRAINT_CONTRACT", CONSTRAINT_CONTRACT, raising=False)
    monkeypatch.setattr(training, "LABELS", LABELS)
    monkeypatch.setattr(training, "validate_bioes", validate_bioes)
    monkeypatch.setattr(
        training, "validate_publishable_model", validate_publishable_model, raising=False
    )
    monkeypatch.setattr(training, "load_final_model", load_final_model, raising=False)
    monkeypatch.setattr(training, "write_json_atomic", write_json_atomic, raising=False)
    return config, marker, validation_calls


def test_viterbi_with_zero_transitions_is_argmax():
    emissions = np.array(
        [
            [0.1, 0.9, 0.0, 0.0, 0.0],
            [0.7, 0.2, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.9],
        ]
    )
    transitions = np.zeros((5, 5))
    edges = np.zeros(5)

    assert viterbi_decode(emissions, edges, transitions, edges, 5) == [1, 0, 4]


def test_viterbi_obeys_transition_scores():
    emissions = np.array([[0.0, 1.0], [1.0, 0.0]])
    transitions = np.array([[0.0, 0.0], [-100.0, 0.0]])
    edges = np.zeros(2)

    path = viterbi_decode(emissions, edges, transitions, edges)

    assert path[0] == path[1]


def test_viterbi_ties_are_deterministic_and_forbidden_edges_cannot_win():
    emissions = np.zeros((2, 2), dtype=np.float32)
    transitions = np.array([[0.0, -np.inf], [0.0, 0.0]], dtype=np.float32)
    edges = np.zeros(2, dtype=np.float32)

    assert viterbi_decode(emissions, edges, transitions, edges) == [0, 0]


@pytest.mark.parametrize(
    ("argument", "value", "error"),
    [
        ("emissions", np.empty((0, 2)), "at least one token"),
        ("emissions", np.zeros((1, 2, 1)), "emissions must have shape"),
        ("emissions", [[0.0, 1.0]], "NumPy array"),
        ("emissions", np.zeros((1, 2), dtype=np.int64), "floating-point"),
        ("emissions", np.array([[np.nan, 0.0]]), "NaN"),
        ("start", np.zeros(3), "shape"),
        ("transitions", np.zeros((2, 3)), "shape"),
        ("end", np.zeros(3), "shape"),
    ],
)
def test_viterbi_rejects_malformed_inputs(argument, value, error):
    emissions = np.zeros((2, 2))
    start = np.zeros(2)
    transitions = np.zeros((2, 2))
    end = np.zeros(2)
    values = {
        "emissions": emissions,
        "start": start,
        "transitions": transitions,
        "end": end,
    }
    values[argument] = value

    with pytest.raises((TypeError, ValueError), match=error):
        viterbi_decode(
            values["emissions"],
            values["start"],
            values["transitions"],
            values["end"],
            num_labels=2,
        )


def test_viterbi_rejects_wrong_explicit_label_count():
    emissions = np.zeros((1, 2))
    edges = np.zeros(2)

    with pytest.raises(ValueError, match="expected 3"):
        viterbi_decode(emissions, edges, np.zeros((2, 2)), edges, num_labels=3)


def test_deterministic_adversarial_numpy_pytorch_parity(monkeypatch):
    torch = pytest.importorskip("torch")
    tagger = FakeTagger(torch)
    with torch.no_grad():
        tagger.crf.start_transitions.copy_(torch.tensor([0.7, -0.2, 0.4, 0.8, 1.1]))
        tagger.crf.end_transitions.copy_(torch.tensor([-0.3, 0.6, 0.2, -0.9, 0.5]))
    monkeypatch.setattr(
        "export_onnx._training_interfaces",
        lambda: (
            ARTIFACT_SCHEMA,
            CONSTRAINT_CONTRACT,
            LABELS,
            None,
            validate_bioes,
            None,
            None,
        ),
    )

    start, transitions, end = check_viterbi_matches_crf(tagger, len(LABELS))

    assert start.shape == (5,)
    assert transitions.shape == (5, 5)
    assert end.shape == (5,)


def test_crf_export_is_publishable_effective_and_manifested(tmp_path, monkeypatch):
    torch = pytest.importorskip("torch")
    model_dir = tmp_path / "final-model"
    output_dir = tmp_path / "export"
    model_dir.mkdir()
    tagger = FakeTagger(torch)
    _config, marker, validation_calls = install_artifact_helpers(monkeypatch, model_dir, tagger)

    matrix_path, manifest_path = export_crf_matrices(model_dir, output_dir)

    assert validation_calls == [model_dir]
    with np.load(matrix_path) as matrices:
        assert np.isneginf(matrices["start"][[2, 3]]).all()
        assert np.isneginf(matrices["transitions"][0, [2, 3]]).all()
        assert np.isneginf(matrices["end"][[1, 2]]).all()
        assert np.isfinite(matrices["start"][[0, 1, 4]]).all()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["artifact_schema"] == ARTIFACT_SCHEMA
    assert manifest["constraint_contract"] == CONSTRAINT_CONTRACT
    assert manifest["labels"] == list(LABELS)
    assert manifest["source_final_model"] == marker
    assert manifest["crf_transitions"] == sha256(matrix_path)
    assert manifest["parity"] == {"passed": True, "cases": list(PARITY_CASES)}
    assert "onnx_model" not in manifest


@pytest.mark.parametrize(
    ("field", "value", "error"),
    [
        ("artifact_schema", "old", "artifact schema"),
        ("labels", list(reversed(LABELS)), "label order"),
        ("constraint_contract", "old", "constraint contract"),
        ("use_crf", False, "with a CRF"),
    ],
)
def test_crf_export_rejects_unsupported_artifact(tmp_path, monkeypatch, field, value, error):
    torch = pytest.importorskip("torch")
    model_dir = tmp_path / "final-model"
    model_dir.mkdir()
    tagger = FakeTagger(torch)
    config, _marker, _calls = install_artifact_helpers(monkeypatch, model_dir, tagger)
    config[field] = value
    (model_dir / "train_config.json").write_text(json.dumps(config), encoding="utf-8")

    with pytest.raises(ValueError, match=error):
        export_crf_matrices(model_dir, tmp_path / "export")


def test_generic_publishable_load_allows_non_crf_onnx_artifacts(tmp_path, monkeypatch):
    torch = pytest.importorskip("torch")
    model_dir = tmp_path / "final-model"
    model_dir.mkdir()

    class NonCrfTagger:
        use_crf = False

        def eval(self):
            return self

    tagger = NonCrfTagger()
    config, _marker, _calls = install_artifact_helpers(monkeypatch, model_dir, tagger)
    config["use_crf"] = False
    (model_dir / "train_config.json").write_text(json.dumps(config), encoding="utf-8")

    loaded, _tokenizer, loaded_config, _marker = _load_publishable_artifact(model_dir)
    assert loaded is tagger
    assert loaded_config["use_crf"] is False
    with pytest.raises(ValueError, match="with a CRF"):
        _load_publishable_artifact(model_dir, require_crf=True)


def test_crf_export_rejects_output_inside_final_model(tmp_path, monkeypatch):
    torch = pytest.importorskip("torch")
    model_dir = tmp_path / "final-model"
    model_dir.mkdir()
    install_artifact_helpers(monkeypatch, model_dir, FakeTagger(torch))

    with pytest.raises(ValueError, match="outside the Final_Model"):
        export_crf_matrices(model_dir, model_dir / "export")

    assert not (model_dir / "export").exists()


def test_crf_export_rejects_a_nonempty_output_directory(tmp_path, monkeypatch):
    torch = pytest.importorskip("torch")
    model_dir = tmp_path / "final-model"
    output_dir = tmp_path / "export"
    model_dir.mkdir()
    output_dir.mkdir()
    (output_dir / "model.onnx").write_bytes(b"stale")
    install_artifact_helpers(monkeypatch, model_dir, FakeTagger(torch))

    with pytest.raises(ValueError, match="not empty"):
        export_crf_matrices(model_dir, output_dir)

    assert (output_dir / "model.onnx").read_bytes() == b"stale"
    assert not (output_dir / "crf_transitions.npz").exists()


def test_failed_crf_export_removes_staging_and_never_publishes(tmp_path, monkeypatch):
    torch = pytest.importorskip("torch")
    model_dir = tmp_path / "final-model"
    output_dir = tmp_path / "export"
    model_dir.mkdir()
    install_artifact_helpers(monkeypatch, model_dir, FakeTagger(torch))

    def fail_manifest(path, value):
        raise OSError("injected export manifest failure")

    monkeypatch.setattr(training, "write_json_atomic", fail_manifest)
    with pytest.raises(OSError, match="injected export manifest failure"):
        export_crf_matrices(model_dir, output_dir)

    assert not output_dir.exists()
    assert not output_dir.with_name("export.tmp").exists()


def test_crf_export_does_not_import_onnx_and_onnx_error_is_actionable(tmp_path, monkeypatch):
    torch = pytest.importorskip("torch")
    model_dir = tmp_path / "final-model"
    model_dir.mkdir()
    install_artifact_helpers(monkeypatch, model_dir, FakeTagger(torch))
    original_import = builtins.__import__

    def without_onnx(name, *args, **kwargs):
        if name in {"onnx", "onnxruntime"}:
            raise ImportError(f"blocked {name}")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", without_onnx)

    matrix_path, manifest_path = export_crf_matrices(model_dir, tmp_path / "crf")
    assert matrix_path.exists()
    assert manifest_path.exists()
    with pytest.raises(OnnxDependencyError, match=r"\[training,onnx\]"):
        export_onnx_emissions(model_dir, tmp_path / "onnx")


def test_onnx_export_validates_shape_and_publishes_transactionally(tmp_path, monkeypatch):
    torch = pytest.importorskip("torch")

    class Tokenizer:
        def __call__(self, text, return_tensors):
            assert return_tensors == "pt"
            return {
                "input_ids": torch.zeros((1, 3), dtype=torch.long),
                "attention_mask": torch.ones((1, 3), dtype=torch.long),
            }

    class Emissions:
        def __call__(self, input_ids, attention_mask):
            return torch.zeros((1, 3, len(LABELS)), dtype=torch.float32)

    runtime = types.ModuleType("onnxruntime")
    runtime.output = np.zeros((1, 1, len(LABELS)), dtype=np.float32)

    class Session:
        def __init__(self, path, providers):
            self.path = path
            self.providers = providers

        def run(self, names, feeds):
            return [runtime.output]

    runtime.InferenceSession = Session
    monkeypatch.setitem(sys.modules, "onnx", types.ModuleType("onnx"))
    monkeypatch.setitem(sys.modules, "onnxruntime", runtime)
    monkeypatch.setattr(
        export_module,
        "_load_publishable_artifact",
        lambda model_dir: (
            object(),
            Tokenizer(),
            {"resolved_model_revision": "a" * 40},
            {"schema": ARTIFACT_SCHEMA, "files": {}},
        ),
    )
    monkeypatch.setattr(export_module, "build_emissions_module", lambda tagger: Emissions())
    monkeypatch.setattr(
        torch.onnx,
        "export",
        lambda module, inputs, path, **kwargs: Path(path).write_bytes(b"onnx"),
    )
    model_dir = tmp_path / "final-model"
    model_dir.mkdir()

    failed_output = tmp_path / "failed-onnx"
    with pytest.raises(ValueError, match="shape"):
        export_onnx_emissions(model_dir, failed_output)
    assert not failed_output.exists()
    assert not failed_output.with_name("failed-onnx.tmp").exists()

    runtime.output = np.zeros((1, 3, len(LABELS)), dtype=np.float32)
    output_dir = tmp_path / "onnx"
    onnx_path, manifest_path = export_onnx_emissions(model_dir, output_dir, opset=17)
    assert onnx_path.is_file()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["onnx_model"] == sha256(onnx_path)
    assert manifest["opset"] == 17
    assert not output_dir.with_name("onnx.tmp").exists()


def test_cli_exposes_crf_and_onnx_as_separate_operations(tmp_path, monkeypatch):
    model_dir = tmp_path / "final-model"
    model_dir.mkdir()
    calls = []

    def export_crf(model, output):
        calls.append(("crf", model, output))
        return output / "crf_transitions.npz", output / "manifest.json"

    def export_onnx(model, output, opset):
        calls.append(("onnx", model, output, opset))
        return output / "model.onnx", output / "manifest.json"

    monkeypatch.setattr("export_onnx.export_crf_matrices", export_crf)
    monkeypatch.setattr("export_onnx.export_onnx_emissions", export_onnx)
    runner = CliRunner()

    crf_output = tmp_path / "crf"
    result = runner.invoke(
        main,
        ["--model-dir", str(model_dir), "--output-dir", str(crf_output)],
    )
    assert result.exit_code == 0
    assert calls == [("crf", model_dir, crf_output)]

    calls.clear()
    onnx_output = tmp_path / "onnx"
    result = runner.invoke(
        main,
        [
            "--model-dir",
            str(model_dir),
            "--output-dir",
            str(onnx_output),
            "--operation",
            "onnx",
            "--opset",
            "17",
        ],
    )
    assert result.exit_code == 0
    assert calls == [("onnx", model_dir, onnx_output, 17)]


def test_sha256_is_stable(tmp_path):
    path = tmp_path / "model.onnx"
    path.write_bytes(b"model")

    assert sha256(path) == "9372c470eeadd5ecd9c3c74c2b3cb633f8e2f2fad799250a0f70d652b6b825e4"
