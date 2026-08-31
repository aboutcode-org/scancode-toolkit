# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Export a trained required phrase tagger for CPU inference."""

import hashlib
import json
import os
from pathlib import Path
from types import SimpleNamespace

import click

os.environ.setdefault("USE_TF", "0")


def viterbi_decode(emissions, start_transitions, transitions, end_transitions):
    """Return the best tag path for one sequence."""
    sequence_length = emissions.shape[0]
    score = start_transitions + emissions[0]
    backpointers = []

    for step in range(1, sequence_length):
        candidates = score[:, None] + transitions
        best_source = candidates.argmax(axis=0)
        score = candidates.max(axis=0) + emissions[step]
        backpointers.append(best_source)

    score = score + end_transitions
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


def build_emissions_module(tagger):
    """Wrap the trained backbone and classifier for ONNX export."""
    import torch.nn as nn

    class EmissionsModule(nn.Module):
        def __init__(self):
            super().__init__()
            self.backbone = tagger.backbone
            self.classifier = tagger.classifier

        def forward(self, input_ids, attention_mask):
            hidden = self.backbone(
                input_ids=input_ids,
                attention_mask=attention_mask,
            ).last_hidden_state
            return self.classifier(hidden)

    return EmissionsModule().eval()


def load_tagger(model_dir, train_config):
    """Rebuild a tagger and strictly load its saved weights."""
    import torch
    from safetensors.torch import load_file

    from phrase_model import PhraseTagger

    config = SimpleNamespace(
        model_name=train_config["model_name"],
        model_revision=train_config.get("model_revision"),
        use_crf=train_config["use_crf"],
        aux_ce_weight=0.0,
        label_weights=[1.0] * len(train_config["labels"]),
    )
    tagger = PhraseTagger(config)

    model_dir = Path(model_dir)
    safetensors_file = model_dir / "model.safetensors"
    pytorch_file = model_dir / "pytorch_model.bin"
    if safetensors_file.exists():
        state = load_file(str(safetensors_file))
    elif pytorch_file.exists():
        state = torch.load(pytorch_file, map_location="cpu", weights_only=True)
    else:
        raise FileNotFoundError(f"No model weights found in {model_dir}")

    # Checkpoints created before class weights became non-persistent contain
    # this training-only tensor.
    state.pop("class_weights", None)
    for name, tensor in state.items():
        if not torch.isfinite(tensor).all():
            raise ValueError(f"Checkpoint tensor {name!r} contains non-finite values")

    tagger.load_state_dict(state, strict=True)
    return tagger.eval()


def check_viterbi_matches_crf(tagger, num_tags):
    """Verify NumPy and pytorch-crf return identical paths."""
    import torch

    start = tagger.crf.start_transitions.detach().cpu().numpy()
    transitions = tagger.crf.transitions.detach().cpu().numpy()
    end = tagger.crf.end_transitions.detach().cpu().numpy()

    emissions = torch.randn(3, 14, num_tags)
    mask = torch.ones(3, 14, dtype=torch.bool)
    crf_paths = tagger.crf.decode(emissions, mask=mask)
    for row in range(emissions.size(0)):
        numpy_path = viterbi_decode(emissions[row].numpy(), start, transitions, end)
        if numpy_path != crf_paths[row]:
            raise AssertionError("NumPy Viterbi disagrees with pytorch-crf decoding")

    return start, transitions, end


def export(model_dir, output_dir, opset):
    """Export ONNX emissions, CRF transitions, and a checksum manifest."""
    import numpy as np
    import torch
    from transformers import AutoTokenizer

    model_dir = Path(model_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    config_path = model_dir / "train_config.json"
    if not config_path.exists():
        raise FileNotFoundError(f"No train_config.json found in {model_dir}")
    train_config = json.loads(config_path.read_text(encoding="utf-8"))
    labels = train_config["labels"]
    use_crf = train_config["use_crf"]

    tagger = load_tagger(model_dir, train_config)
    emissions_module = build_emissions_module(tagger)
    tokenizer = AutoTokenizer.from_pretrained(str(model_dir), use_fast=True)

    sample = tokenizer(
        "Licensed under the Apache License Version 2.0",
        return_tensors="pt",
    )
    inputs = sample["input_ids"], sample["attention_mask"]

    onnx_path = output_dir / "model.onnx"
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

    manifest = {
        "labels": labels,
        "onnx_model": sha256(onnx_path),
    }

    if use_crf:
        start, transitions, end = check_viterbi_matches_crf(tagger, len(labels))
        transitions_path = output_dir / "crf_transitions.npz"
        np.savez(
            transitions_path,
            start=start,
            transitions=transitions,
            end=end,
        )
        manifest["crf_transitions"] = sha256(transitions_path)

    import onnxruntime

    session = onnxruntime.InferenceSession(
        str(onnx_path),
        providers=["CPUExecutionProvider"],
    )
    feeds = {
        "input_ids": sample["input_ids"].numpy(),
        "attention_mask": sample["attention_mask"].numpy(),
    }
    onnx_emissions = session.run(["emissions"], feeds)[0]
    torch_emissions = emissions_module(*inputs).detach().numpy()
    if not np.allclose(onnx_emissions, torch_emissions, atol=1e-3):
        raise AssertionError("ONNX emissions differ from PyTorch emissions")

    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    click.echo(f"wrote {onnx_path}")
    if use_crf:
        click.echo(f"wrote {output_dir / 'crf_transitions.npz'}")
    click.echo(f"wrote {manifest_path}")


@click.command()
@click.option(
    "--model-dir",
    required=True,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Directory containing the trained model and train_config.json.",
)
@click.option(
    "--output-dir",
    default=None,
    type=click.Path(file_okay=False, path_type=Path),
    help="Output directory; defaults to the model directory.",
)
@click.option("--opset", default=14, type=int, show_default=True)
def main(model_dir, output_dir, opset):
    """Export a trained required phrase tagger to ONNX."""
    try:
        export(model_dir, output_dir or model_dir, opset)
    except ImportError as error:
        raise click.ClickException(
            f"{error}; install scancode-required-phrases[training,onnx]"
        ) from error


if __name__ == "__main__":
    main()
