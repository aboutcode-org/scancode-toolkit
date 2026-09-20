# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import os
from types import SimpleNamespace

import pytest

os.environ.setdefault("USE_TF", "0")

torch = pytest.importorskip("torch")
pytest.importorskip("torchcrf")
pytest.importorskip("transformers")

import phrase_model as model_module
from phrase_model import build_constraint_masks
from phrase_model import build_optimizer
from phrase_model import ConstrainedCRF
from phrase_model import PhraseTagger
from phrase_model import PhraseTrainer
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
        self.gradient_checkpointing_kwargs = None

    def gradient_checkpointing_enable(self, gradient_checkpointing_kwargs=None):
        self.gradient_checkpointing_kwargs = gradient_checkpointing_kwargs


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
    tagger = PhraseTagger(config)

    assert calls == [(("fake-model",), {"revision": "revision"})]
    assert tagger.backbone.gradient_checkpointing_kwargs == {"use_reentrant": False}


def test_trainer_accepts_gathered_finite_losses_and_rejects_non_finite_losses():
    trainer = PhraseTrainer.__new__(PhraseTrainer)

    class Model:
        def __init__(self, loss):
            self.loss = loss

        def __call__(self, **inputs):
            return {"loss": self.loss}

    loss = torch.tensor([1.0, 2.0], requires_grad=True)
    assert torch.equal(trainer.compute_loss(Model(loss), {}), loss)

    with pytest.raises(FloatingPointError, match="non-finite loss"):
        trainer.compute_loss(Model(torch.tensor([1.0, torch.inf])), {})


def test_prediction_step_averages_a_gathered_loss(monkeypatch):
    trainer = PhraseTrainer.__new__(PhraseTrainer)
    monkeypatch.setattr(trainer, "_prepare_inputs", lambda inputs: inputs)

    class Model:
        def __call__(self, **inputs):
            return {
                "loss": torch.tensor([2.0, 4.0]),
                "predictions": torch.tensor([[0], [0]]),
                "word_labels": torch.tensor([[0], [0]]),
            }

    loss, _, _ = trainer.prediction_step(Model(), {}, prediction_loss_only=False)

    assert loss.ndim == 0
    assert loss.item() == 3.0


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
    tagger = PhraseTagger.__new__(PhraseTagger)
    torch.nn.Module.__init__(tagger)
    tagger.use_crf = True
    tagger.aux_ce_weight = 0
    tagger.num_labels = len(LABELS)
    tagger.crf = ConstrainedCRF(len(LABELS), batch_first=True)
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


def test_predict_words_rejects_an_empty_sequence():
    tagger = make_crf_tagger()
    tagger.emissions = lambda *args: pytest.fail("emissions should not be computed")
    input_ids = torch.zeros((1, 2), dtype=torch.long)

    with pytest.raises(ValueError, match="must not be empty"):
        tagger.predict_words(input_ids, input_ids, [None, None])


def test_forward_and_predict_words_share_constrained_decode():
    tagger = make_crf_tagger()
    tagger.eval()
    emissions = torch.zeros((1, 1, len(LABELS)))
    emissions[0, 0, LABEL2ID["I-REQ"]] = 1000.0
    tagger.emissions = lambda input_ids, attention_mask: emissions
    input_ids = torch.zeros((1, 1), dtype=torch.long)
    labels = torch.tensor([[LABEL2ID["O"]]])

    result = tagger(input_ids, input_ids, labels=labels)
    predicted = tagger.predict_words(input_ids, input_ids, [0])

    assert result["predictions"].tolist() == [[LABEL2ID["O"]]]
    assert predicted == [LABEL2ID["O"]]
    assert torch.isfinite(result["loss"])


def test_constraint_masks_match_exact_bioes_contract():
    start_mask, transition_mask, end_mask = build_constraint_masks()

    assert start_mask.tolist() == [True, True, False, False, True]
    assert end_mask.tolist() == [True, False, False, True, True]
    assert transition_mask.tolist() == [
        [True, True, False, False, True],
        [False, False, True, True, False],
        [False, False, True, True, False],
        [True, True, False, False, True],
        [True, True, False, False, True],
    ]


def test_constraint_masks_are_not_saved_and_learned_scores_stay_finite():
    crf = ConstrainedCRF(len(LABELS), batch_first=True)

    assert set(crf.state_dict()) == {
        "start_transitions",
        "transitions",
        "end_transitions",
    }
    assert all(parameter.requires_grad for parameter in crf.parameters())
    assert all(torch.isfinite(parameter).all() for parameter in crf.parameters())
    assert torch.isneginf(crf.effective_start_transitions[~crf.start_mask]).all()
    assert torch.isneginf(crf.effective_transitions[~crf.transition_mask]).all()
    assert torch.isneginf(crf.effective_end_transitions[~crf.end_mask]).all()


def test_constrained_decode_cannot_select_an_invalid_single_tag_path():
    crf = ConstrainedCRF(len(LABELS), batch_first=True)
    with torch.no_grad():
        for parameter in crf.parameters():
            parameter.zero_()
    emissions = torch.zeros((1, 1, len(LABELS)))
    emissions[0, 0, LABEL2ID["I-REQ"]] = 1000.0
    emissions[0, 0, LABEL2ID["E-REQ"]] = 900.0

    assert crf.decode(emissions) == [[LABEL2ID["O"]]]


def test_constrained_loss_rejects_an_invalid_gold_path():
    crf = ConstrainedCRF(len(LABELS), batch_first=True)
    emissions = torch.zeros((1, 1, len(LABELS)))
    tags = torch.tensor([[LABEL2ID["I-REQ"]]])

    with pytest.raises(ValueError, match="Invalid BIOES gold path in row 0"):
        crf(emissions, tags)


def test_constrained_crf_padding_is_ignored_without_non_finite_loss():
    crf = ConstrainedCRF(len(LABELS), batch_first=True)
    with torch.no_grad():
        for parameter in crf.parameters():
            parameter.zero_()
    active_emissions = torch.tensor(
        [
            [
                [0.0, 4.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 4.0, 0.0],
            ]
        ]
    )
    active_tags = torch.tensor([[LABEL2ID["B-REQ"], LABEL2ID["E-REQ"]]])
    active_mask = torch.ones((1, 2), dtype=torch.bool)

    padded_emissions = torch.cat(
        [active_emissions, torch.full((1, 1, len(LABELS)), 1000.0)],
        dim=1,
    )
    padded_tags = torch.tensor(
        [[LABEL2ID["B-REQ"], LABEL2ID["E-REQ"], len(LABELS) + 10]]
    )
    padded_mask = torch.tensor([[True, True, False]])

    active_likelihood = crf(
        active_emissions,
        active_tags,
        mask=active_mask,
        reduction="none",
    )
    padded_likelihood = crf(
        padded_emissions,
        padded_tags,
        mask=padded_mask,
        reduction="none",
    )

    assert torch.isfinite(padded_likelihood).all()
    assert torch.equal(active_likelihood, padded_likelihood)
    assert crf.decode(active_emissions, active_mask) == crf.decode(
        padded_emissions,
        padded_mask,
    )


def test_constrained_crf_rejects_invalid_inputs():
    crf = ConstrainedCRF(len(LABELS), batch_first=True)
    emissions = torch.zeros((1, 2, len(LABELS)))
    tags = torch.tensor([[LABEL2ID["B-REQ"], LABEL2ID["E-REQ"]]])

    with pytest.raises(ValueError, match="non-empty"):
        crf.decode(torch.zeros((1, 0, len(LABELS))))
    with pytest.raises(TypeError, match="boolean"):
        crf.decode(emissions, torch.ones((1, 2), dtype=torch.long))
    three_emissions = torch.zeros((1, 3, len(LABELS)))
    with pytest.raises(ValueError, match="left aligned"):
        crf.decode(three_emissions, torch.tensor([[True, False, True]]))
    with pytest.raises(ValueError, match="mask shape"):
        crf.decode(emissions, torch.ones((1, 1), dtype=torch.bool))
    with pytest.raises(ValueError, match="valid label IDs"):
        crf(emissions, torch.tensor([[LABEL2ID["B-REQ"], len(LABELS)]]))
    with pytest.raises(FloatingPointError, match="finite scores"):
        invalid_emissions = emissions.clone()
        invalid_emissions[0, 0, 0] = torch.nan
        crf.decode(invalid_emissions)

    with torch.no_grad():
        crf.transitions[0, 0] = torch.inf
    with pytest.raises(FloatingPointError, match="transitions"):
        crf(emissions, tags)


def test_gather_words_uses_o_for_padded_crf_tags():
    tagger = make_crf_tagger()
    emissions = torch.zeros((2, 3, len(LABELS)))
    labels = torch.tensor(
        [
            [LABEL2ID["S-REQ"], -100, -100],
            [LABEL2ID["B-REQ"], LABEL2ID["E-REQ"], -100],
        ]
    )

    _, crf_tags, _, mask = tagger.gather_words(emissions, labels)

    assert crf_tags.tolist() == [
        [LABEL2ID["S-REQ"], LABEL2ID["O"]],
        [LABEL2ID["B-REQ"], LABEL2ID["E-REQ"]],
    ]
    assert mask.tolist() == [[True, False], [True, True]]


def test_gather_words_rejects_an_empty_word_sequence():
    tagger = make_crf_tagger()
    emissions = torch.zeros((1, 2, len(LABELS)))
    labels = torch.full((1, 2), -100)

    with pytest.raises(ValueError, match="must not be empty"):
        tagger.gather_words(emissions, labels)


def test_phrase_tagger_accepts_an_already_constructed_backbone(monkeypatch, config):
    monkeypatch.setattr(
        model_module.AutoModel,
        "from_pretrained",
        lambda *args, **kwargs: pytest.fail("local construction must not load a model"),
    )
    backbone = FakeBackbone()

    tagger = PhraseTagger(config, backbone=backbone)

    assert tagger.backbone is backbone
    assert isinstance(tagger.crf, ConstrainedCRF)
