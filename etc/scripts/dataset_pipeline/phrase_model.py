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


def build_constraint_masks():
    """Return deterministic BIOES start, transition, and end masks."""
    label_ids = {label: index for index, label in enumerate(LABELS)}
    expected = {"O", "B-REQ", "I-REQ", "E-REQ", "S-REQ"}
    if set(label_ids) != expected or len(label_ids) != len(LABELS):
        raise ValueError(f"Unsupported BIOES labels: {LABELS!r}")

    start_mask = torch.zeros(len(LABELS), dtype=torch.bool)
    transition_mask = torch.zeros((len(LABELS), len(LABELS)), dtype=torch.bool)
    end_mask = torch.zeros(len(LABELS), dtype=torch.bool)

    for label in ("O", "B-REQ", "S-REQ"):
        start_mask[label_ids[label]] = True
    for label in ("O", "E-REQ", "S-REQ"):
        end_mask[label_ids[label]] = True

    allowed_transitions = {
        "O": ("O", "B-REQ", "S-REQ"),
        "B-REQ": ("I-REQ", "E-REQ"),
        "I-REQ": ("I-REQ", "E-REQ"),
        "E-REQ": ("O", "B-REQ", "S-REQ"),
        "S-REQ": ("O", "B-REQ", "S-REQ"),
    }
    for previous, following_labels in allowed_transitions.items():
        for following in following_labels:
            transition_mask[label_ids[previous], label_ids[following]] = True

    return start_mask, transition_mask, end_mask


class ConstrainedCRF(CRF):
    """CRF with hard BIOES constraints and finite learned parameters."""

    def __init__(self, num_tags, batch_first=False):
        if num_tags != len(LABELS):
            raise ValueError(
                f"ConstrainedCRF needs {len(LABELS)} tags, received {num_tags}"
            )
        super().__init__(num_tags, batch_first=batch_first)
        start_mask, transition_mask, end_mask = build_constraint_masks()
        self.register_buffer("start_mask", start_mask, persistent=False)
        self.register_buffer("transition_mask", transition_mask, persistent=False)
        self.register_buffer("end_mask", end_mask, persistent=False)
        self.o_tag_id = LABELS.index("O")

    @property
    def effective_start_transitions(self):
        return self.start_transitions.masked_fill(~self.start_mask, -torch.inf)

    @property
    def effective_transitions(self):
        return self.transitions.masked_fill(~self.transition_mask, -torch.inf)

    @property
    def effective_end_transitions(self):
        return self.end_transitions.masked_fill(~self.end_mask, -torch.inf)

    def _validate_learned_scores(self):
        for name, scores in (
            ("start_transitions", self.start_transitions),
            ("transitions", self.transitions),
            ("end_transitions", self.end_transitions),
        ):
            if not torch.isfinite(scores).all():
                raise FloatingPointError(f"CRF {name} contains a non-finite value")

    def _validate_inputs(self, emissions, tags=None, mask=None):
        if emissions.dim() != 3:
            raise ValueError(
                f"emissions must have rank 3, received shape {tuple(emissions.shape)}"
            )
        if emissions.size(2) != self.num_tags:
            raise ValueError(
                f"emissions last dimension must be {self.num_tags}, "
                f"received {emissions.size(2)}"
            )

        batch_size = emissions.size(0 if self.batch_first else 1)
        sequence_length = emissions.size(1 if self.batch_first else 0)
        if batch_size == 0 or sequence_length == 0:
            raise ValueError("CRF emissions must contain a non-empty sequence batch")
        if not emissions.is_floating_point() or not torch.isfinite(emissions).all():
            raise FloatingPointError("CRF emissions must contain only finite scores")

        expected_shape = emissions.shape[:2]
        if mask is None:
            mask = torch.ones(expected_shape, dtype=torch.bool, device=emissions.device)
        elif mask.shape != expected_shape:
            raise ValueError(
                f"mask shape {tuple(mask.shape)} does not match {tuple(expected_shape)}"
            )
        elif mask.dtype != torch.bool:
            raise TypeError("CRF mask must be a boolean tensor")
        elif mask.device != emissions.device:
            raise ValueError("CRF mask and emissions must be on the same device")

        batch_mask = mask if self.batch_first else mask.transpose(0, 1)
        if not batch_mask[:, 0].all():
            raise ValueError("CRF mask must include the first position of every row")
        if (batch_mask[:, 1:] & ~batch_mask[:, :-1]).any():
            raise ValueError("CRF mask must be left aligned")

        if tags is not None:
            if tags.shape != expected_shape:
                raise ValueError(
                    f"tag shape {tuple(tags.shape)} does not match {tuple(expected_shape)}"
                )
            if tags.dtype != torch.long:
                raise TypeError("CRF tags must be a torch.long tensor")
            if tags.device != emissions.device:
                raise ValueError("CRF tags and emissions must be on the same device")
            active_tags = tags[mask]
            if ((active_tags < 0) | (active_tags >= self.num_tags)).any():
                raise ValueError("CRF active tags must be valid label IDs")
            self._validate_gold_paths(tags, mask)

        self._validate_learned_scores()
        return mask

    def _validate_gold_paths(self, tags, mask):
        batch_tags = tags if self.batch_first else tags.transpose(0, 1)
        batch_mask = mask if self.batch_first else mask.transpose(0, 1)
        for row in range(batch_tags.size(0)):
            length = int(batch_mask[row].sum().item())
            path = batch_tags[row, :length]
            if not self.start_mask[path[0]] or not self.end_mask[path[-1]]:
                raise ValueError(f"Invalid BIOES gold path in row {row}: {path.tolist()}")
            if length > 1 and not self.transition_mask[path[:-1], path[1:]].all():
                raise ValueError(f"Invalid BIOES gold path in row {row}: {path.tolist()}")

    def forward(self, emissions, tags, mask=None, reduction="sum"):
        """Return constrained conditional log likelihood for valid gold paths."""
        if reduction not in ("none", "sum", "mean", "token_mean"):
            raise ValueError(f"invalid reduction: {reduction}")
        mask = self._validate_inputs(emissions, tags=tags, mask=mask)
        tags = tags.masked_fill(~mask, self.o_tag_id)

        if self.batch_first:
            emissions = emissions.transpose(0, 1)
            tags = tags.transpose(0, 1)
            mask = mask.transpose(0, 1)

        numerator = self._compute_constrained_score(emissions, tags, mask)
        denominator = self._compute_constrained_normalizer(emissions, mask)
        likelihood = numerator - denominator

        if reduction == "none":
            return likelihood
        if reduction == "sum":
            return likelihood.sum()
        if reduction == "mean":
            return likelihood.mean()
        return likelihood.sum() / mask.sum()

    def decode(self, emissions, mask=None):
        """Return the highest-scoring valid BIOES path for each batch row."""
        mask = self._validate_inputs(emissions, mask=mask)
        if self.batch_first:
            emissions = emissions.transpose(0, 1)
            mask = mask.transpose(0, 1)
        return self._constrained_viterbi_decode(emissions, mask)

    def _compute_constrained_score(self, emissions, tags, mask):
        sequence_length, batch_size = tags.shape
        batch_index = torch.arange(batch_size, device=tags.device)
        score = self.effective_start_transitions[tags[0]]
        score = score + emissions[0, batch_index, tags[0]]

        for position in range(1, sequence_length):
            step_score = self.effective_transitions[tags[position - 1], tags[position]]
            step_score = step_score + emissions[position, batch_index, tags[position]]
            score = torch.where(mask[position], score + step_score, score)

        sequence_ends = mask.long().sum(dim=0) - 1
        last_tags = tags.gather(0, sequence_ends.unsqueeze(0)).squeeze(0)
        return score + self.effective_end_transitions[last_tags]

    def _compute_constrained_normalizer(self, emissions, mask):
        score = self.effective_start_transitions + emissions[0]
        for position in range(1, emissions.size(0)):
            next_score = score.unsqueeze(2) + self.effective_transitions.unsqueeze(0)
            next_score = next_score + emissions[position].unsqueeze(1)
            next_score = torch.logsumexp(next_score, dim=1)
            score = torch.where(mask[position].unsqueeze(1), next_score, score)
        return torch.logsumexp(score + self.effective_end_transitions, dim=1)

    def _constrained_viterbi_decode(self, emissions, mask):
        score = self.effective_start_transitions + emissions[0]
        history = []

        for position in range(1, emissions.size(0)):
            next_score = score.unsqueeze(2) + self.effective_transitions.unsqueeze(0)
            next_score, indices = next_score.max(dim=1)
            next_score = next_score + emissions[position]
            score = torch.where(mask[position].unsqueeze(1), next_score, score)
            history.append(indices)

        score = score + self.effective_end_transitions
        sequence_ends = mask.long().sum(dim=0) - 1
        best_paths = []
        for row in range(emissions.size(1)):
            best_last_tag = int(score[row].argmax().item())
            best_path = [best_last_tag]
            for indices in reversed(history[: int(sequence_ends[row].item())]):
                best_last_tag = int(indices[row, best_last_tag].item())
                best_path.append(best_last_tag)
            best_path.reverse()
            best_paths.append(best_path)
        return best_paths


class PhraseTagger(nn.Module):
    """DeBERTa backbone with a word-level token classifier and optional CRF."""

    def __init__(self, config, backbone=None):
        super().__init__()
        self.use_crf = config.use_crf
        self.aux_ce_weight = config.aux_ce_weight
        self.num_labels = len(LABELS)

        if backbone is None:
            backbone = AutoModel.from_pretrained(
                config.model_name,
                revision=config.model_revision,
            )
        self.backbone = backbone.float()
        self.backbone.gradient_checkpointing_enable(
            gradient_checkpointing_kwargs={"use_reentrant": False}
        )

        hidden_size = self.backbone.config.hidden_size
        dropout = getattr(self.backbone.config, "hidden_dropout_prob", 0.1)
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(hidden_size, self.num_labels)

        if self.use_crf:
            self.crf = ConstrainedCRF(self.num_labels, batch_first=True)

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
        if (lengths == 0).any():
            raise ValueError("CRF word sequences must not be empty")
        width = int(lengths.max().item())

        word_emissions = emissions.new_zeros((batch, width, num_labels))
        o_tag_id = LABELS.index("O")
        crf_tags = labels.new_full((batch, width), o_tag_id)
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
            raise ValueError("Inference word sequence must not be empty")

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
        if not torch.isfinite(loss).all():
            raise FloatingPointError("Training produced a non-finite loss")
        return (loss, outputs) if return_outputs else loss

    def prediction_step(self, model, inputs, prediction_loss_only, ignore_keys=None):
        inputs = self._prepare_inputs(inputs)
        with torch.no_grad():
            outputs = model(**inputs)
            loss = outputs.get("loss")
            if loss is not None:
                loss = loss.mean().detach()
        if prediction_loss_only:
            return loss, None, None
        return loss, outputs["predictions"], outputs["word_labels"]
