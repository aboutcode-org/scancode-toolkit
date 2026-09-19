# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Review model-predicted required phrases before changing ScanCode rules."""

import difflib
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import tempfile

import click

sys.path.insert(0, str(Path(__file__).parent))

from licensedcode.models import Rule
from licensedcode.models import rules_data_dir
from licensedcode.required_phrases import add_required_phrase_to_rule
from licensedcode.required_phrases import find_phrase_spans_in_text
from licensedcode.required_phrases import RequiredPhraseRuleCandidate

from add_ml_phrases import inject as add_predicted_phrases
from add_ml_phrases import load_model
from add_ml_phrases import MIN_SINGLE_TOKEN_LEN
from add_ml_phrases import MIN_TOKENS
from add_ml_phrases import new_counts
from add_ml_phrases import predict_rule
from add_ml_phrases import select_rules


PENDING = "pending"
APPROVED = "approved"
REJECTED = "rejected"
DECISIONS = {PENDING, APPROVED, REJECTED}

RECORD_FIELDS = {
    "identifier",
    "license_expression",
    "text_sha256",
    "truncated",
    "phrases",
}
PHRASE_FIELDS = {
    "text",
    "predicted_text",
    "start_word",
    "end_word",
    "confidence",
    "decision",
}


def text_sha256(text):
    """Return a stable digest for rule text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def phrase_sort_key(phrase):
    """Return a stable display and injection order for a phrase entry."""
    return -len(phrase["text"]), phrase["text"], phrase["start_word"]


def prediction_record(rule, predictions, truncated):
    """Return one review record with the strongest occurrence of each phrase."""
    predictions_by_text = {}
    for prediction in predictions:
        existing = predictions_by_text.get(prediction.text)
        if existing is None or prediction.confidence > existing.confidence:
            predictions_by_text[prediction.text] = prediction

    phrases = [
        {
            "text": prediction.text,
            "predicted_text": prediction.text,
            "start_word": prediction.start_word,
            "end_word": prediction.end_word,
            "confidence": prediction.confidence,
            "decision": PENDING,
        }
        for prediction in predictions_by_text.values()
    ]
    phrases.sort(key=phrase_sort_key)
    return {
        "identifier": rule.identifier,
        "license_expression": rule.license_expression,
        "text_sha256": text_sha256(rule.text),
        "truncated": truncated,
        "phrases": phrases,
    }


def validate_phrase(phrase, path, line_number, phrase_number):
    """Validate and return one phrase entry from a review file."""
    location = f"{path} line {line_number}, phrase {phrase_number}"
    if type(phrase) is not dict:
        raise click.ClickException(f"{location}: phrase must be an object")
    if set(phrase) != PHRASE_FIELDS:
        raise click.ClickException(f"{location}: phrase fields are invalid")

    for field in ("text", "predicted_text", "decision"):
        if type(phrase[field]) is not str or not phrase[field]:
            raise click.ClickException(f"{location}: {field} must be a non-empty string")
    for field in ("start_word", "end_word"):
        if isinstance(phrase[field], bool) or not isinstance(phrase[field], int):
            raise click.ClickException(f"{location}: {field} must be an integer")
    if phrase["start_word"] < 0 or phrase["end_word"] < phrase["start_word"]:
        raise click.ClickException(f"{location}: word offsets are invalid")

    confidence = phrase["confidence"]
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
        raise click.ClickException(f"{location}: confidence must be a number")
    if not math.isfinite(confidence) or not 0.0 <= confidence <= 1.0:
        raise click.ClickException(f"{location}: confidence must be between 0 and 1")
    if phrase["decision"] not in DECISIONS:
        raise click.ClickException(f"{location}: decision is invalid")
    return phrase


def validate_record(record, path, line_number):
    """Validate and return one record from a review file."""
    location = f"{path} line {line_number}"
    if type(record) is not dict:
        raise click.ClickException(f"{location}: record must be an object")
    if set(record) != RECORD_FIELDS:
        raise click.ClickException(f"{location}: record fields are invalid")

    for field in ("identifier", "license_expression", "text_sha256"):
        if type(record[field]) is not str or not record[field]:
            raise click.ClickException(f"{location}: {field} must be a non-empty string")
    if Path(record["identifier"]).name != record["identifier"]:
        raise click.ClickException(f"{location}: identifier must be a rule filename")
    digest = record["text_sha256"]
    if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
        raise click.ClickException(f"{location}: text_sha256 is invalid")
    if type(record["truncated"]) is not bool:
        raise click.ClickException(f"{location}: truncated must be a boolean")
    if type(record["phrases"]) is not list or not record["phrases"]:
        raise click.ClickException(f"{location}: phrases must be a non-empty list")

    seen = set()
    for phrase_number, phrase in enumerate(record["phrases"], 1):
        validate_phrase(phrase, path, line_number, phrase_number)
        identity = (phrase["predicted_text"], phrase["start_word"], phrase["end_word"])
        if identity in seen:
            raise click.ClickException(f"{location}: duplicate predicted phrase")
        seen.add(identity)
    return record


def read_review_file(path):
    """Return all validated records from a JSONL review file."""
    records = []
    identifiers = set()
    try:
        lines = Path(path).open(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise click.ClickException(f"Cannot read review file {path}: {error}") from error

    with lines:
        for line_number, line in enumerate(lines, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                raise click.ClickException(
                    f"{path} line {line_number}: malformed JSON: {error.msg}"
                ) from error
            validate_record(record, path, line_number)
            if record["identifier"] in identifiers:
                raise click.ClickException(
                    f"{path} line {line_number}: duplicate rule identifier"
                )
            identifiers.add(record["identifier"])
            records.append(record)
    return records


def write_review_file(path, records):
    """Atomically replace a review file with records in JSONL format."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as output:
            for record in records:
                output.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n")
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def load_current_rule(record):
    """Return the unchanged rule named by record, or a stale reason."""
    rule_path = Path(rules_data_dir) / record["identifier"]
    if not rule_path.is_file():
        return None, "rule file is missing"
    rule = Rule.from_file(str(rule_path), is_builtin=True)
    if rule.license_expression != record["license_expression"]:
        return None, "license expression changed"
    if text_sha256(rule.text) != record["text_sha256"]:
        return None, "rule text changed"
    return rule, None


def preview_injection(rule, phrase):
    """Return the exact in-memory result of injecting phrase without saving."""
    original_text = rule.text
    original_source = rule.source
    changed = add_required_phrase_to_rule(
        rule=rule,
        required_phrase=phrase,
        source="ml_model",
        dry_run=True,
    )
    preview = rule.text
    rule.text = original_text
    rule.source = original_source
    return changed, preview


def render_diff(identifier, before, after):
    """Print a unified diff for one proposed rule update."""
    lines = difflib.unified_diff(
        before.splitlines(keepends=True),
        after.splitlines(keepends=True),
        fromfile=f"a/{identifier}",
        tofile=f"b/{identifier}",
    )
    colors = {"+": "green", "-": "red", "@": "cyan"}
    for line in lines:
        line = line.rstrip("\n")
        click.echo(click.style(line, fg=colors.get(line[:1])))


def is_candidate(rule, phrase):
    """Return whether phrase passes ScanCode's candidate and location checks."""
    candidate = RequiredPhraseRuleCandidate.create(rule.license_expression, phrase)
    return candidate.is_good(rule, MIN_TOKENS, MIN_SINGLE_TOKEN_LEN) and bool(
        find_phrase_spans_in_text(rule.text, phrase)
    )


def edit_phrase(rule, phrase):
    """Prompt for a valid replacement phrase, or return False to cancel."""
    click.echo("\nrule text")
    click.echo(rule.text)
    while True:
        replacement = click.prompt(
            "phrase, empty to cancel",
            default="",
            show_default=False,
        ).strip()
        if not replacement:
            return False
        if not is_candidate(rule, replacement):
            click.echo("The phrase is not a valid candidate in this rule.")
            continue
        changed, preview = preview_injection(rule, replacement)
        if not changed:
            click.echo("The phrase cannot be added to this rule.")
            continue
        render_diff(rule.identifier, rule.text, preview)
        phrase["text"] = replacement
        phrase["decision"] = APPROVED
        return True


def review_phrase(rule, phrase):
    """Prompt for one phrase decision and return False when review should stop."""
    while True:
        answer = click.prompt(
            "[y] approve  [n] reject  [e] edit  [q] quit",
            default="",
            show_default=False,
        ).strip().lower()
        if answer == "y":
            phrase["decision"] = APPROVED
            return True
        if answer == "n":
            phrase["decision"] = REJECTED
            return True
        if answer == "e":
            if edit_phrase(rule, phrase):
                return True
        elif answer == "q":
            return False
        else:
            click.echo("Enter y, n, e, or q.")


@click.group(name="review-model-required-phrases")
@click.help_option("-h", "--help")
def review_model_required_phrases():
    """Review model predictions before adding them to license rules."""


def predict_records(selected, tagger, tokenizer, max_length, limit=0, verbose=False):
    """Return review records and counts for selected rules."""
    records = []
    counts = {"rules": 0, "truncated": 0, "rejected": 0, "not_found": 0}
    for rules in selected.values():
        for rule in rules:
            if limit and counts["rules"] >= limit:
                return records, counts
            counts["rules"] += 1
            result = predict_rule(tagger, tokenizer, max_length, rule.text)
            if result.truncated:
                counts["truncated"] += 1

            predictions = []
            for prediction in result.phrases:
                candidate = RequiredPhraseRuleCandidate.create(
                    rule.license_expression,
                    prediction.text,
                )
                if not candidate.is_good(rule, MIN_TOKENS, MIN_SINGLE_TOKEN_LEN):
                    counts["rejected"] += 1
                elif not find_phrase_spans_in_text(rule.text, prediction.text):
                    counts["not_found"] += 1
                else:
                    predictions.append(prediction)
            if not predictions:
                continue

            record = prediction_record(rule, predictions, result.truncated)
            records.append(record)
            if verbose:
                click.echo(f"{rule.identifier}: {[phrase['text'] for phrase in record['phrases']]}")
    return records, counts


@review_model_required_phrases.command()
@click.option("--model", required=True, help="Final model directory or Hugging Face repository.")
@click.option(
    "--review-file",
    required=True,
    type=click.Path(dir_okay=False, path_type=Path),
    help="New JSONL file for predictions.",
)
@click.option("--license-expression", help="Only predict for this license expression.")
@click.option(
    "--limit",
    default=0,
    type=click.IntRange(min=0),
    help="Stop after this many rules; zero processes all rules.",
)
@click.option("-v", "--verbose", is_flag=True, help="Print predictions for each rule.")
@click.help_option("-h", "--help")
def predict(model, review_file, license_expression, limit, verbose):
    """Write validated model predictions for human review."""
    if review_file.exists():
        raise click.ClickException(f"Review file already exists: {review_file}")

    selected = select_rules(license_expression=license_expression)
    if not selected:
        click.echo("No eligible rules found")
        return
    tagger, tokenizer, max_length = load_model(
        model,
        hf_token=os.environ.get("HF_TOKEN"),
    )

    records, counts = predict_records(
        selected=selected,
        tagger=tagger,
        tokenizer=tokenizer,
        max_length=max_length,
        limit=limit,
        verbose=verbose,
    )
    write_review_file(review_file, records)
    filed = sum(len(record["phrases"]) for record in records)
    click.echo(f"rules processed : {counts['rules']}")
    click.echo(f"  truncated     : {counts['truncated']}")
    click.echo(f"phrases filed   : {filed}")
    click.echo(f"  rejected      : {counts['rejected']}")
    click.echo(f"  not found     : {counts['not_found']}")
    click.echo(f"review file     : {review_file}")


@review_model_required_phrases.command()
@click.option(
    "--review-file",
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="JSONL prediction file to review.",
)
@click.help_option("-h", "--help")
def review(review_file):
    """Approve, reject, or edit every pending prediction."""
    records = read_review_file(review_file)
    waiting = sum(
        phrase["decision"] == PENDING
        for record in records
        for phrase in record["phrases"]
    )
    if not waiting:
        click.echo("Nothing left to review")
        return

    click.echo(f"{waiting} phrases waiting")
    for record in records:
        pending = [phrase for phrase in record["phrases"] if phrase["decision"] == PENDING]
        if not pending:
            continue
        rule, stale_reason = load_current_rule(record)
        if stale_reason:
            click.echo(f"{record['identifier']}: stale review record ({stale_reason})")
            continue

        for phrase in pending:
            if not is_candidate(rule, phrase["text"]):
                phrase["decision"] = REJECTED
                write_review_file(review_file, records)
                click.echo(f"{record['identifier']}: phrase is no longer a valid candidate")
                continue
            changed, preview = preview_injection(rule, phrase["text"])
            if not changed:
                phrase["decision"] = REJECTED
                write_review_file(review_file, records)
                click.echo(f"{record['identifier']}: phrase can no longer be added")
                continue

            click.echo(f"\n{record['identifier']}  {record['license_expression']}")
            click.echo(f"phrase: {phrase['text']}  confidence: {phrase['confidence']:.1%}")
            render_diff(record["identifier"], rule.text, preview)
            if not review_phrase(rule, phrase):
                return
            write_review_file(review_file, records)


def prepare_apply(records):
    """Return validated rules and approved phrases before any mutation."""
    work = []
    for record in records:
        phrases = {
            phrase["text"]
            for phrase in record["phrases"]
            if phrase["decision"] == APPROVED
        }
        if not phrases:
            continue

        rule, stale_reason = load_current_rule(record)
        if stale_reason:
            raise click.ClickException(
                f"{record['identifier']}: stale review record ({stale_reason})"
            )
        for phrase in phrases:
            if not is_candidate(rule, phrase):
                raise click.ClickException(
                    f"{record['identifier']}: approved phrase is no longer a valid candidate: "
                    f"{phrase!r}"
                )
            changed, _preview = preview_injection(rule, phrase)
            if not changed:
                raise click.ClickException(
                    f"{record['identifier']}: approved phrase cannot be added: {phrase!r}"
                )
        work.append((rule, sorted(phrases, key=lambda phrase: (-len(phrase), phrase))))
    return work


@review_model_required_phrases.command()
@click.option(
    "--review-file",
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Reviewed JSONL prediction file to apply.",
)
@click.option("--dry-run", is_flag=True, help="Validate without saving rules.")
@click.option("-v", "--verbose", is_flag=True, help="Print phrases for each rule.")
@click.help_option("-h", "--help")
def apply(review_file, dry_run, verbose):
    """Add approved phrases after validating the current rules."""
    records = read_review_file(review_file)
    pending = sum(
        phrase["decision"] == PENDING
        for record in records
        for phrase in record["phrases"]
    )
    if pending:
        raise click.ClickException(f"{pending} phrases still need review")

    work = prepare_apply(records)
    counts = new_counts()
    for rule, phrases in work:
        counts["rules"] += 1
        if verbose:
            click.echo(f"{rule.identifier}: {phrases}")
        if add_predicted_phrases(rule, phrases, counts, dry_run=dry_run, verbose=verbose):
            counts["written"] += 1

    click.echo(f"rules processed  : {counts['rules']}")
    click.echo(f"phrases injected : {counts['injected']}")
    click.echo(f"  rejected       : {counts['rejected']}")
    click.echo(f"  not found      : {counts['not_found']}")
    click.echo(f"  nothing to add : {counts['skipped']}")
    click.echo(f"rules written    : {counts['written']}")
    if dry_run:
        click.echo("Dry run: no rules were saved")
    elif counts["written"]:
        click.echo("Run scancode-reindex-licenses to use the new required phrases")


if __name__ == "__main__":
    review_model_required_phrases()
