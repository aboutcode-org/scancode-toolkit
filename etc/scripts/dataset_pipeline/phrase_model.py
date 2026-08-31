# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""DeBERTa model and Trainer support for required phrase tagging."""

import os

os.environ.setdefault("USE_TF", "0")

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim import AdamW
from torchcrf import CRF
from transformers import AutoModel
from transformers import Trainer

from train_model import first_subword_positions
from train_model import IGNORE_INDEX
from train_model import LABELS


class PhraseTagger(nn.Module):
    """DeBERTa backbone with a word-level token classifier and optional CRF."""

    def __init__(self, config):
        super().__init__()
        self.use_crf = config.use_crf
        self.aux_ce_weight = config.aux_ce_weight
        self.num_labels = len(LABELS)

        self.backbone = AutoModel.from_pretrained(
            config.model_name,
            revision=config.model_revision,
        ).float()
        self.backbone.gradient_checkpointing_enable()
        self.backbone.enable_input_require_grads()

        hidden_size = self.backbone.config.hidden_size
        dropout = getattr(self.backbone.config, "hidden_dropout_prob", 0.1)
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(hidden_size, self.num_labels)

        if self.use_crf:
            self.crf = CRF(self.num_labels, batch_first=True)

        if self.aux_ce_weight > 0:
            self.register_buffer(
                "class_weights",
                torch.tensor(config.label_weights, dtype=torch.float),
                persistent=False,
            )
        else:
            self.class_weights = None

    def emissions(self, input_ids, attention_mask):
        """Return per-subword label scores."""
        hidden = self.backbone(
            input_ids=input_ids,
            attention_mask=attention_mask,
        ).last_hidden_state
        return self.classifier(self.dropout(hidden))

    def token_cross_entropy(self, emissions, labels):
        """Return weighted cross entropy over labeled subwords."""
        return F.cross_entropy(
            emissions.reshape(-1, self.num_labels),
            labels.reshape(-1),
            weight=self.class_weights,
            ignore_index=IGNORE_INDEX,
        )

    def gather_words(self, emissions, labels):
        """Pack first-subword emissions and labels into word-level sequences."""
        batch, _, num_labels = emissions.shape
        is_word = labels.ne(IGNORE_INDEX)
        lengths = is_word.sum(dim=1)
        width = int(lengths.max().item())

        word_emissions = emissions.new_zeros((batch, width, num_labels))
        crf_tags = labels.new_zeros((batch, width))
        eval_tags = labels.new_full((batch, width), IGNORE_INDEX)
        mask = torch.zeros((batch, width), dtype=torch.bool, device=emissions.device)

        for row in range(batch):
            positions = is_word[row].nonzero(as_tuple=True)[0]
            count = positions.numel()
            word_emissions[row, :count] = emissions[row, positions]
            tags = labels[row, positions]
            crf_tags[row, :count] = tags
            eval_tags[row, :count] = tags
            mask[row, :count] = True

        return word_emissions, crf_tags, eval_tags, mask

    def forward(self, input_ids, attention_mask, labels=None):
        emissions = self.emissions(input_ids, attention_mask)
        result = {}

        if not self.use_crf:
            if labels is not None:
                result["loss"] = self.token_cross_entropy(emissions, labels)
                result["word_labels"] = labels
            if not self.training:
                result["predictions"] = emissions.argmax(dim=-1)
            return result

        if labels is None:
            raise ValueError("CRF head needs labels to locate words")

        word_emissions, crf_tags, eval_tags, mask = self.gather_words(emissions, labels)
        word_emissions = word_emissions.float()

        log_likelihood = self.crf(word_emissions, crf_tags, mask=mask, reduction="mean")
        loss = -log_likelihood
        if self.aux_ce_weight > 0:
            loss = loss + self.aux_ce_weight * self.token_cross_entropy(emissions, labels)

        result["loss"] = loss
        result["word_labels"] = eval_tags

        if not self.training:
            decoded = self.crf.decode(word_emissions, mask=mask)
            result["predictions"] = self.pad_decoded(decoded, mask.size(1), emissions.device)

        return result

    def predict_words(self, input_ids, attention_mask, word_ids):
        """Return one label ID per word for a single rule."""
        positions = first_subword_positions(word_ids)
        if not positions:
            return []

        emissions = self.emissions(input_ids, attention_mask)
        word_emissions = emissions[0, positions].unsqueeze(0).float()
        if not self.use_crf:
            return word_emissions.argmax(dim=-1)[0].tolist()

        mask = torch.ones(word_emissions.shape[:2], dtype=torch.bool, device=emissions.device)
        return self.crf.decode(word_emissions, mask=mask)[0]

    @staticmethod
    def pad_decoded(decoded, width, device):
        """Return variable-length decoded paths as a padded tensor."""
        predictions = torch.full(
            (len(decoded), width),
            IGNORE_INDEX,
            dtype=torch.long,
            device=device,
        )
        for row, path in enumerate(decoded):
            if path:
                predictions[row, : len(path)] = torch.tensor(
                    path,
                    dtype=torch.long,
                    device=device,
                )
        return predictions


def build_optimizer(config, model):
    """Return the configured AdamW optimizer with layer-wise learning rates."""
    num_layers = model.backbone.config.num_hidden_layers
    no_decay = ("bias", "LayerNorm.weight", "layer_norm.weight")

    def rate_for(name):
        if name.startswith("classifier") or name.startswith("crf"):
            return config.head_lr
        if ".encoder.layer." in name:
            layer = int(name.split(".encoder.layer.")[1].split(".")[0])
            return config.base_lr * (config.layer_decay ** (num_layers - layer))
        return config.base_lr * (config.layer_decay ** (num_layers + 1))

    groups = []
    for name, parameter in model.named_parameters():
        if not parameter.requires_grad:
            continue
        decay = 0.0 if any(part in name for part in no_decay) else config.weight_decay
        groups.append(
            {
                "params": [parameter],
                "lr": rate_for(name),
                "weight_decay": decay,
            }
        )

    optimizer_args = {
        "lr": config.base_lr,
        "eps": config.adam_epsilon,
        "betas": (0.9, 0.999),
    }
    if config.optimizer == "adamw":
        return AdamW(groups, **optimizer_args)

    if config.optimizer == "adamw-8bit":
        try:
            from bitsandbytes.optim import AdamW8bit
        except ImportError as error:
            raise RuntimeError(
                "adamw-8bit requires bitsandbytes; install the training dependencies"
            ) from error
        return AdamW8bit(groups, **optimizer_args)

    raise ValueError(f"Unsupported optimizer: {config.optimizer}")


class PhraseTrainer(Trainer):
    """Trainer adapter for PhraseTagger output dictionaries."""

    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        outputs = model(**inputs)
        loss = outputs["loss"]
        if not torch.isfinite(loss):
            raise FloatingPointError("Training produced a non-finite loss")
        return (loss, outputs) if return_outputs else loss

    def prediction_step(self, model, inputs, prediction_loss_only, ignore_keys=None):
        inputs = self._prepare_inputs(inputs)
        with torch.no_grad():
            outputs = model(**inputs)
            loss = outputs.get("loss")
            if loss is not None:
                loss = loss.detach()
        if prediction_loss_only:
            return loss, None, None
        return loss, outputs["predictions"], outputs["word_labels"]
