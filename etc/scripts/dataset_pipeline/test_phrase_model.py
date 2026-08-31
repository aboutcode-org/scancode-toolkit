# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import os
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

os.environ.setdefault("USE_TF", "0")
sys.path.insert(0, str(Path(__file__).parent))

torch = pytest.importorskip("torch")
pytest.importorskip("torchcrf")
pytest.importorskip("transformers")

import phrase_model as model_module
from phrase_model import build_optimizer
from phrase_model import PhraseTagger
from train_model import LABEL2ID
from train_model import LABELS


class FakeBackbone(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.config = SimpleNamespace(
            hidden_size=4,
            hidden_dropout_prob=0.1,
            num_hidden_layers=1,
        )
        self.encoder = torch.nn.Module()
        self.encoder.layer = torch.nn.ModuleList([torch.nn.Linear(4, 4)])
        self.embeddings = torch.nn.Linear(4, 4)

    def gradient_checkpointing_enable(self):
        pass

    def enable_input_require_grads(self):
        pass


@pytest.fixture
def config():
    return SimpleNamespace(
        model_name="fake-model",
        model_revision="revision",
        use_crf=True,
        aux_ce_weight=0.3,
        label_weights=[1.0] * len(LABELS),
        optimizer="adamw",
        base_lr=2e-5,
        head_lr=1e-4,
        layer_decay=0.98,
        weight_decay=0.01,
        adam_epsilon=1e-6,
    )


def test_class_weights_are_not_saved(monkeypatch, config):
    monkeypatch.setattr(
        model_module.AutoModel,
        "from_pretrained",
        lambda *args, **kwargs: FakeBackbone(),
    )

    tagger = PhraseTagger(config)

    assert tagger.class_weights is not None
    assert "class_weights" not in tagger.state_dict()


def test_model_revision_is_passed_to_the_backbone(monkeypatch, config):
    calls = []

    def from_pretrained(*args, **kwargs):
        calls.append((args, kwargs))
        return FakeBackbone()

    monkeypatch.setattr(model_module.AutoModel, "from_pretrained", from_pretrained)
    PhraseTagger(config)

    assert calls == [(("fake-model",), {"revision": "revision"})]


def test_build_optimizer_uses_explicit_adamw(monkeypatch, config):
    monkeypatch.setattr(
        model_module.AutoModel,
        "from_pretrained",
        lambda *args, **kwargs: FakeBackbone(),
    )
    tagger = PhraseTagger(config)

    optimizer = build_optimizer(config, tagger)

    assert isinstance(optimizer, torch.optim.AdamW)
    learning_rates = {group["lr"] for group in optimizer.param_groups}
    assert config.head_lr in learning_rates
    assert any(rate < config.base_lr for rate in learning_rates)


def make_crf_tagger():
    from torchcrf import CRF

    tagger = PhraseTagger.__new__(PhraseTagger)
    torch.nn.Module.__init__(tagger)
    tagger.use_crf = True
    tagger.num_labels = len(LABELS)
    tagger.crf = CRF(len(LABELS), batch_first=True)
    with torch.no_grad():
        for parameter in tagger.crf.parameters():
            parameter.zero_()
    return tagger


def test_predict_words_uses_first_subwords():
    tagger = make_crf_tagger()
    emissions = torch.zeros((1, 5, len(LABELS)))
    emissions[0, 1, LABEL2ID["B-REQ"]] = 9.0
    emissions[0, 2, LABEL2ID["E-REQ"]] = 9.0
    emissions[0, 3, LABEL2ID["S-REQ"]] = 9.0
    tagger.emissions = lambda input_ids, attention_mask: emissions

    input_ids = torch.zeros((1, 5), dtype=torch.long)
    tags = tagger.predict_words(
        input_ids,
        input_ids,
        [None, 0, 1, 1, None],
    )

    assert tags == [LABEL2ID["B-REQ"], LABEL2ID["E-REQ"]]


def test_predict_words_does_not_run_for_an_empty_sequence():
    tagger = make_crf_tagger()
    tagger.emissions = lambda *args: pytest.fail("emissions should not be computed")
    input_ids = torch.zeros((1, 2), dtype=torch.long)

    assert tagger.predict_words(input_ids, input_ids, [None, None]) == []
