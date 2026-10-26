# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import re

from collections import defaultdict

import attr
import click

from commoncode.cliutils import PluggableCommandLineOption
from license_expression import Licensing

from licensedcode.cache import build_index
from licensedcode.cache import get_index
from licensedcode.cache import get_licenses_db
from licensedcode.models import find_rule_base_location
from licensedcode.models import get_ignorables
from licensedcode.models import get_normalized_ignorables
from licensedcode.models import get_rules_by_expression
from licensedcode.models import get_rules_by_identifier
from licensedcode.models import get_stopwords_in_short_text
from licensedcode.models import load_rules
from licensedcode.models import rules_data_dir
from licensedcode.models import Rule
from licensedcode.models import rule_exists
from licensedcode.models import update_ignorables
from licensedcode.spans import Span
from licensedcode.stopwords import STOPWORDS
from licensedcode.tokenize import REQUIRED_PHRASE_CLOSE
from licensedcode.tokenize import REQUIRED_PHRASE_OPEN
from licensedcode.tokenize import required_phrase_tokenizer
from licensedcode.tokenize import matched_query_text_tokenizer
from licensedcode.tokenize import get_existing_required_phrase_spans

"""
This is a utility module for "required phrases".
This is a designed to run as a command line tool with extensive debugging and tracing facilitues.

Usage:

- start with gen-new-required-phrases-rules: this will create new rules from existing "required
phrases" found in rules.

- regen the index

- then continue with add-required-phrases to update existing rules with required phrases found in
"is_required_phrase" rules and license attributes/fields.

"""

TRACE = False

# Add rule identifiers here to trace required phrase collection or required
# phrase marking for a specific rule (Example: "mit_12.RULE")
TRACE_REQUIRED_PHRASE_FOR_RULES = []

####################################################################################################
#
# Shared utilities
#
####################################################################################################


def get_normalized_tokens(text, skip_required_phrase_markers=True, preserve_case=False):
    """
    Return a list of normalized token strings in ``text``.
    """
    required_phrase_markers = [REQUIRED_PHRASE_CLOSE, REQUIRED_PHRASE_OPEN]
    tokens = list(required_phrase_tokenizer(text=text, preserve_case=preserve_case))
    if skip_required_phrase_markers:
        tokens = [
            token
            for token in tokens
            if token not in required_phrase_markers
        ]

    return tokens


def get_normalized_text(text, skip_required_phrase_markers=True):
    """
    Return the normalized text for ``text``. Optionally ``skip_required_phrase_markers``  double
    {{curly braces}}.
    """
    return " ".join(
        get_normalized_tokens(
            text=text,
            skip_required_phrase_markers=skip_required_phrase_markers,
        )
    )


def find_phrase_spans_in_text(text, phrase_text, preserve_case=False):
    """
    Return a list of Spans where the ``phrase_text`` exists in ``text``, or an empty list.
    """
    spans_with_required_phrase = []

    text_tokens = list(get_normalized_tokens(
        text=text,
        preserve_case=preserve_case,
        skip_required_phrase_markers=True,
    ))
    required_phrase_tokens = list(get_normalized_tokens(
        text=phrase_text,
        preserve_case=preserve_case,
        skip_required_phrase_markers=True,
    ))
    required_phrase_first_token = required_phrase_tokens[0]

    # Initial check to see if all tokens in the required phrase are present
    if all(
        required_phrase_token in text_tokens
        for required_phrase_token in required_phrase_tokens
    ):
        start_positions = [
            i
            for i, x in enumerate(text_tokens)
            if x == required_phrase_first_token
        ]

        for start_pos in start_positions:
            end_pos = start_pos + len(required_phrase_tokens)

            if (
                end_pos <= len(text_tokens)
                and text_tokens[start_pos:end_pos] == required_phrase_tokens
            ):
                spans_with_required_phrase.append(Span(start_pos, end_pos - 1))

    return spans_with_required_phrase


def get_non_overlapping_spans(old_required_phrase_spans, new_required_phrase_spans):
    """
    Given two list of spans `old_required_phrase_spans` and `new_required_phrase_spans`,
    return all the spans in `new_required_phrase_spans` that do not overlap with any
    of the spans in `old_required_phrase_spans`.

    The list of spans `old_required_phrase_spans` contains all the spans of required
    phrases or ignorables already present in a rule text, and the other list of spans
    `new_required_phrase_spans` contains the proposed new required phrases.
    """
    for new_span in new_required_phrase_spans:
        if old_required_phrase_spans:
            if any(old_span.overlap(new_span) != 0 for old_span in old_required_phrase_spans):
                continue

        yield new_span


def add_required_phrase_markers(text, required_phrase_span):
    """
    Given a ``text`` and a ``required_phrase_span`` Span, add required phrase
    curly brace markers to the ``text`` before the start and after the of the span.
    This is taking care of whitespace and stopwords.
    """
    tokens_tuples_with_markers = []
    token_index = 0

    for token_tuple in matched_query_text_tokenizer(text):

        is_word, token = token_tuple

        if is_word and token.lower() not in STOPWORDS:
            if token_index == required_phrase_span.start:
                tokens_tuples_with_markers.append((False, REQUIRED_PHRASE_OPEN))

            token_index += 1

        tokens_tuples_with_markers.append(token_tuple)

        if is_word and token.lower() not in STOPWORDS:
            if token_index == required_phrase_span.end + 1:
                tokens_tuples_with_markers.append((False, REQUIRED_PHRASE_CLOSE))

    return combine_tokens(tokens_tuples_with_markers)


def combine_tokens(token_tuples):
    """
    Returns a string `combined_text` combining token tuples from the list `token_tuples`,
    which are token tuples created by the tokenizer functions.
    """
    return ''.join(token for _, token in token_tuples)


@attr.s
class IsRequiredPhrase:
    """
    Represent a required phrase text and rule from an "is_required_phrase" Rule
    """

    rule = attr.ib(metadata=dict(help='Rule that contains this phrase'))
    required_phrase_text = attr.ib(metadata=dict(help='Normalized required phrase text.'))

    @property
    def license_expression(self):
        self.rule.license_expression

    @staticmethod
    def sorted(isrequiredphrases):
        """
        Return an ``isrequiredphrases`` list of IsRequiredPhrase sorted by decreasing text length.
        """
        sorter = lambda p: (len(p.rule.text), p.required_phrase_text)
        return sorted(isrequiredphrases, key=sorter, reverse=True)


def collect_is_required_phrase_from_rules(rules_by_expression, verbose=False):
    """
    Return a mapping of ``{license_expression: list of [IsRequiredPhrase, ...]`` collecting the
    texts of all rules in the ``rules_by_expression`` mapping if the "is_required_phrase"  is True..
    """
    is_required_phrases_by_expression = {}

    for license_expression, rules in rules_by_expression.items():
        if verbose:
            click.echo(f'Collecting required phrases for license_expression: {license_expression}')

        is_required_phrases = []

        for rule in rules:
            if not rule.is_required_phrase:
                continue

            if rule.identifier in TRACE_REQUIRED_PHRASE_FOR_RULES:
                click.echo(f"Collecting required phrase from rule: {rule.identifier}: {rule.text!r}")

            is_required_phrases.append(IsRequiredPhrase(rule=rule, required_phrase_text=rule.text))

        # We need to sort required phrases by decreasing length so we look for and mark the longest
        # possible required phrases before the shorter ones contained in the same text
        is_required_phrases = IsRequiredPhrase.sorted(is_required_phrases)
        is_required_phrases_by_expression[license_expression] = is_required_phrases

        if verbose:
            count = len(is_required_phrases)
            click.echo(f'Collected {count} required phrases for license_expression: {license_expression}')
            click.echo('Collected required phrases texts: ')
            for rqph in is_required_phrases:
                click.echo(f'     {rqph.required_phrase_text!r}: {rqph.rule.identifier}')

    return is_required_phrases_by_expression


def update_required_phrases_in_rules(
    required_phrases_by_expression,
    rules_by_expression,
    write_phrase_source=False,
    verbose=False,
    dry_run=False,
):
    """
    Update the text of rules in a ``rules_by_expression`` mapping with required phrases from the
    ``required_phrases_by_expression`` mapping.
    If ``write_phrase_source`` is True, include debug information in the saved rule source field.
    """
    for license_expression, rules in rules_by_expression.items():
        if license_expression not in required_phrases_by_expression:
            continue

        if verbose:
            click.echo(f'marking required phrases in rule texts for license_expression: {license_expression}')

        required_phrases = required_phrases_by_expression.get(license_expression)
        if not required_phrases:
            continue

        add_required_phrases_to_rules_text(
            required_phrases=required_phrases,
            rules=rules,
            write_phrase_source=write_phrase_source,
            dry_run=dry_run,
        )


def update_rules_using_is_required_phrases_rules(
    license_expression=None,
    write_phrase_source=False,
    verbose=False,
    dry_run=False,
):
    """
    Add required phrases to rules using is_required_phrase rules.
    Optionally filter rules with ``license_expression``.
    """
    rules_by_expression = get_base_rules_by_expression(license_expression=license_expression)

    required_phrases_by_expression = collect_is_required_phrase_from_rules(
        rules_by_expression=rules_by_expression,
        verbose=verbose,
    )
    if verbose:
        click.echo(f"update_rules_using_is_required_phrases_rules: required_phrases_by_expression # {len(required_phrases_by_expression)}")

    rules_by_expression = get_updatable_rules_by_expression(
        license_expression,
        simple_expression=False,
        verbose=verbose,
    )
    if verbose:
        click.echo(f"update_rules_using_is_required_phrases_rules: rules_by_expression # {len(rules_by_expression)}")

    update_required_phrases_in_rules(
        required_phrases_by_expression=required_phrases_by_expression,
        rules_by_expression=rules_by_expression,
        write_phrase_source=write_phrase_source,
        verbose=verbose,
        dry_run=dry_run,
    )


def get_base_rules_by_expression(license_expression=None):
    """
    Return a mapping of rules_by_expression, filtered for an optional ``license_expression``.
    """
    rules_by_expression = get_rules_by_expression()
    if license_expression:
        rules_by_expression = {license_expression: rules_by_expression[license_expression]}

    return rules_by_expression


def get_updatable_rules_by_expression(license_expression=None, simple_expression=True, verbose=False):
    """
    Return a mapping of rules_by_expression, filtered for an optional ``license_expression``.
    The rules are suitable to receive required phrase updates
    If simple_expression is True, only consider lincense rules with a single license key.
    """
    rules_by_expression = get_base_rules_by_expression(license_expression)

    index = get_index()
    licensing = Licensing()

    updatable_rules_by_expression = {}

    # filter rules to keep only updatable rules
    for expression, rules in rules_by_expression.items():
        if simple_expression:
            license_keys = licensing.license_keys(license_expression)
            if len(license_keys) != 1:
                continue

        updatable_rules = []
        if verbose:
            click.echo(f"get_updatable_rules_by_expression: rule_identifiers # {[rule.identifier for rule in rules]}")

        for rule in rules:
            if rule.is_from_license:
                if verbose:
                    click.echo(f"get_updatable_rules_by_expression: {rule.identifier} ignored because rule.is_from_license")
                continue

            # very long texts are best left alone
            if len(rule.text) > 4000:
                if verbose:
                    click.echo(f"get_updatable_rules_by_expression: {rule.identifier} ignored because rule.is_long")
                continue

            # skip required phrase, false positive, tiny and and more
            if not rule.is_approx_matchable:
                if verbose:
                    click.echo(f"get_updatable_rules_by_expression: {rule.identifier} ignored because rule.is_approx_matchable")
                continue

            # skip rules that ask to be skipped
            if rule.skip_for_required_phrase_generation:
                if verbose:
                    click.echo(f"get_updatable_rules_by_expression: {rule.identifier} ignored because rule.skip_for_required_phrase_generation")
                continue

            updatable_rules.append(rule)

        if updatable_rules:
            if verbose:
                click.echo(f"get_updatable_rules_by_expression: updatable_rules # {[rule.identifier for rule in updatable_rules]}")
            updatable_rules_by_expression[expression] = updatable_rules

    return updatable_rules_by_expression


def add_required_phrases_to_rules_text(
    required_phrases,
    rules,
    write_phrase_source=False,
    dry_run=False,
):
    """
    Add the ``required_phrases`` list of IsRequiredPhrase to each rule in a ``rules`` list of
    license Rule.
    """
    for rule in rules:
        for required_phrase in required_phrases:
            debug = False
            if rule.identifier in TRACE_REQUIRED_PHRASE_FOR_RULES:
                click.echo(
                    f"Trying to updating rule: {rule.identifier} "
                    f"with required phrase: '{required_phrase.required_phrase_text}'."
                )
                debug = True

            source = rule.source or ""
            if write_phrase_source:
                source += f" {required_phrase.rule.identifier}"

            add_required_phrase_to_rule(
                rule=rule,
                required_phrase=required_phrase.required_phrase_text,
                source=source,
                debug=debug,
                dry_run=dry_run,
            )


def add_license_attributes_as_required_phrases_to_rules_text(
    license_object,
    rules,
    write_phrase_source=False,
    dry_run=False,
):
    """
    Add new required phrases to the ``rules`` list of Rule using the ``license_object`` License
    fields for required phrases.
    """

    license_fields_mapping_by_order = {
        "name": [license_object.name],
        "short_name": [license_object.short_name],
        # "key",
        "spdx_license_key": [license_object.spdx_license_key],
        "other_spdx_license_keys": license_object.other_spdx_license_keys or [],
    }

    for rule in rules:
        for field_name, required_phrase_texts in license_fields_mapping_by_order.values():
            for required_phrase_text in required_phrase_texts:
                debug = False
                if rule.identifier in TRACE_REQUIRED_PHRASE_FOR_RULES:
                    click.echo(
                        f"Updating rule: {rule.identifier} "
                        f"with required phrase from license: {field_name!r}: {required_phrase_text!r}."
                    )
                    debug = True

                source = rule.source or ""
                if write_phrase_source:
                    source += f" {license_object.key}.LICENSE : {field_name}"

                add_required_phrase_to_rule(
                    rule=rule,
                    required_phrase=required_phrase_text,
                    source=source,
                    debug=debug,
                    dry_run=dry_run,
                )


def get_ignorable_spans(rule):
    """
    Return a list of ignorable Spans for the ``rule``.
    Ignorable spans are for URLs and referenced filenames present in a rule text. These should not
    be messed up with when injecting new required phrases in a rule text.
    """
    ignorable_spans = []
    ignorables = rule.referenced_filenames + rule.ignorable_urls
    for ignorable in ignorables:
        spans = find_phrase_spans_in_text(
            text=rule.text,
            phrase_text=ignorable,
            preserve_case=True)
        ignorable_spans.extend(
            spans
        )

    return ignorable_spans


def add_required_phrase_to_rule(rule, required_phrase, source, debug=False, dry_run=False):
    """
    Update and save the ``rule`` Rule tagging the text with the ``required_phrase`` text. Skip
    updating and saving the rule to disk under some conditions, like if ignorables would be changed.
    Return True if the rule was updated and False otherwise.
    """

    # These are candidate spans for new requriedf_phrases, if they exist
    new_required_phrase_spans = find_phrase_spans_in_text(
        text=rule.text,
        phrase_text=required_phrase,
    )

    # we get spans for already existing required phrases and ignorables
    ignorable_spans = get_ignorable_spans(rule)
    old_required_phrase_spans = get_existing_required_phrase_spans(rule.text)

    # we verify whether there are spans which overlap with the
    # already present required phrases or ignorables
    spans_to_add = list(
        get_non_overlapping_spans(
            old_required_phrase_spans=old_required_phrase_spans + ignorable_spans,
            new_required_phrase_spans=new_required_phrase_spans,
        )
    )

    if new_required_phrase_spans and debug:
        click.echo(f"New required phrase spans for {rule.identifier}: {new_required_phrase_spans}")
        click.echo(f"Old required phrase spans: {old_required_phrase_spans}")
        click.echo(f"Ignorable spans: {ignorable_spans}")
        click.echo(f"required phrase spans to add: {spans_to_add}")
        ignorable_debug = rule.referenced_filenames + rule.ignorable_urls
        click.echo(f"debug ignorables: {ignorable_debug}")

    # we add required phrase markers for the non-overlapping spans
    new_rule_text = rule.text
    for span_to_add in spans_to_add:
        new_rule_text = add_required_phrase_markers(
            text=new_rule_text,
            required_phrase_span=span_to_add,
        )

    # write the rule on disk if there are any updates
    if new_rule_text == rule.text:
        return False

    if has_ignorable_changes(rule=rule, updated_text=new_rule_text):
        if debug:
            click.echo(
                f"NOT Updating rule: {rule.identifier} "
                f"because IGNORABLES would change "
                f"with required phrase: {required_phrase} "
            )

        return False

    rule.source = source or None
    rule.text = new_rule_text
    if not dry_run:
        if debug:
            click.echo(
                f"UPDATE: Updating rule: {rule.identifier} "
                f"with required phrase: {required_phrase!r} "
                f"source: {source!r}"
            )
        rule.dump(rules_data_dir)
    return True


def has_ignorable_changes(rule, updated_text):
    """
    Return True if there would be changes in the "ignorable_*" attributes of a ``rule`` Rule if its
    text was to be updated with a new ``updated_text``.
    """
    existing_ignorables = get_normalized_ignorables(rule)
    updated_ignorables = get_ignorables(updated_text)
    return existing_ignorables != updated_ignorables


def update_rules_using_license_attributes(
    license_expression=None,
    write_phrase_source=False,
    verbose=False,
    dry_run=False,
):
    """
    Add required phrases found in the license fields.

    Iterate rules by license key, collect required phrases from the license attributes like name and
    short name. Add those as required phrases in all selected rules that are using the
    ``license_expression``.
    """
    rules_by_expression = get_updatable_rules_by_expression(license_expression, simple_expression=True)

    licenses_by_key = get_licenses_db()

    # license expression is alway  a single key here
    for license_key, rules in rules_by_expression.items():
        licence_object = licenses_by_key[license_key]
        if verbose:
            click.echo(f'Updating rules with required phrases for license_expression: {license_key}')

        add_license_attributes_as_required_phrases_to_rules_text(
            license_object=licence_object,
            rules=rules,
            write_phrase_source=write_phrase_source,
            dry_run=dry_run,
        )

####################################################################################################
#
# Inject new required phrase in rules
#
####################################################################################################


def delete_required_phrase_rules_source_debug(rules_data_dir):
    """
    Remove the "source" attribute from all rules.
    """
    for rule in load_rules(rules_data_dir=rules_data_dir):
        if rule.source:
            rule.source = None
            rule.dump(rules_data_dir)


@click.command(name='add-required-phrases')
@click.option(
    "-o",
    "--from-other-rules",
    is_flag=True,
    default=False,
    help="Propagate existing required phrases from other rules to all selected rules. "
    "Mutually exclusive with --from-license-attributes.",
    cls=PluggableCommandLineOption,
)
@click.option(
    "-a",
    "--from-license-attributes",
    is_flag=True,
    default=False,
    help="Propagate license attributes as required phrases to all selected rules. "
    "Mutually exclusive with --from-other-rule.",
    cls=PluggableCommandLineOption,
)
@click.option(
    "-l",
    "--license-expression",
    type=str,
    default=None,
    metavar="STRING",
    help="Optional license expression filter. If provided, only consider the rules that are using "
    "this expression. Otherwise, process all rules. Example: `apache-2.0`.",
    cls=PluggableCommandLineOption,
)
@click.option(
    "--validate",
    is_flag=True,
    default=False,
    help="Validate that all rules and licenses and rules are consistent, for all rule languages. "
    "For this validation, run a mock indexing. The regenerated index is not saved to disk.",
    cls=PluggableCommandLineOption,
)
@click.option(
    "-r",
    "--reindex",
    is_flag=True,
    default=False,
    help="Recreate and cache the licenses index  with updated rules add the end.",
    cls=PluggableCommandLineOption,
)
@click.option(
    "-w",
    "--write-phrase-source",
    is_flag=True,
    default=False,
    help="In modified rule files, write the source field to trace the source of required phrases "
    "applied to that rule.",
    cls=PluggableCommandLineOption,
)
@click.option(
    "-d",
    "--delete-phrase-source",
    is_flag=True,
    default=False,
    help="In rule files, delete the source extra debug data used to trace source of phrases.",
    cls=PluggableCommandLineOption,
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Do not save rules.",
    cls=PluggableCommandLineOption,
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    default=False,
    help="Print verbose logging information.",
    cls=PluggableCommandLineOption,
)
@click.help_option("-h", "--help")
def add_required_phrases(
    from_other_rules,
    from_license_attributes,
    license_expression,
    validate,
    reindex,
    delete_phrase_source,
    write_phrase_source,
    dry_run,
    verbose,
):
    """
    Update license detection rules with new "required phrases" to improve rules detection accuracy.
    """

    if delete_phrase_source:
        click.echo('Deleting rules phrase source debug data.')
        delete_required_phrase_rules_source_debug(rules_data_dir)
        return

    elif from_other_rules:
        click.echo('Updating rules from is_required_phrase rules.')
        update_rules_using_is_required_phrases_rules(
            license_expression=license_expression,
            write_phrase_source=write_phrase_source,
            dry_run=dry_run,
            verbose=verbose,
        )

    elif from_license_attributes:
        click.echo('Updating rules from license attributes.')
        update_rules_using_license_attributes(
            license_expression=license_expression,
            write_phrase_source=write_phrase_source,
            dry_run=dry_run,
            verbose=verbose,
        )

    validate_and_reindex(validate, reindex, verbose)


def validate_and_reindex(validate=True, reindex=True, verbose=False):
    if validate:
        if verbose:
            click.echo('Validate all rules and licenses for all languages...')
        build_index(index_all_languages=True)

    if reindex:
        if verbose:
            click.echo('Rebuilding and caching the license index...')
        get_index(force=True)

####################################################################################################
#
# Generate new required phrase rules from existing tagged required phrases
#
####################################################################################################


@click.command(name='gen-new-required-phrases-rules')
@click.option(
    "-l",
    "--license-expression",
    type=str,
    default=None,
    metavar="STRING",
    help="Optional license expression filter. If provided, only consider the rules that are using "
    "this expression. Otherwise, process all rules. Example: `apache-2.0`.",
    cls=PluggableCommandLineOption,
)
@click.option(
    "--max-count",
    type=int,
    default=0,
    metavar="INT",
    help="Optional maximum count of rules to process. If provided as a non-zero value, "
    "stop after processing this count of rules.",
    cls=PluggableCommandLineOption,
)
@click.option(
    "-r",
    "--reindex",
    is_flag=True,
    default=False,
    help="Recreate and cache the licenses index  with updated rules add the end.",
    cls=PluggableCommandLineOption,
)
@click.option(
    "--validate",
    is_flag=True,
    default=False,
    help="Validate that all rules and licenses and rules are consistent, for all rule languages. "
    "For this validation, run a mock indexing. The regenerated index is not saved to disk.",
    cls=PluggableCommandLineOption,
)
@click.option(
    "--min-tokens",
    type=int,
    default=2,
    metavar="INT",
    help="Minimum number of tokens in the text used to generate a 'good' new rule.",
    cls=PluggableCommandLineOption,
)
@click.option(
    "--min-single-token-len",
    type=int,
    default=5,
    metavar="INT",
    help="Minimum length of the token in a single-word rule text used to generate a 'good' new rule.",
    cls=PluggableCommandLineOption,
)
@click.option(
    "--update-only",
    is_flag=True,
    default=False,
    help="Do not create new rules, only update existing rules.",
    cls=PluggableCommandLineOption,
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    default=False,
    help="Print verbose logging information.",
    cls=PluggableCommandLineOption,
)
@click.help_option("-h", "--help")
def gen_required_phrases_rules(
    license_expression,
    validate,
    reindex,
    verbose,
    max_count,
    min_tokens,
    min_single_token_len,
    update_only,
):
    """
    Create new license detection rules from "required phrases" in existing rules.
    Also update existing rules with "is_required_phrase" if they are "required phrases" but are
    not tagged as such.
    """
    generate_new_required_phrase_rules(
        license_expression=license_expression,
        verbose=verbose,
        max_count=max_count,
        min_tokens=min_tokens,
        min_single_token_len=min_single_token_len,
        update_only=update_only,
    )

    validate_and_reindex(
        validate=validate,
        reindex=reindex,
        verbose=verbose,
    )


def generate_new_required_phrase_rules(
    license_expression=None,
    verbose=False,
    max_count=0,
    min_tokens=2,
    min_single_token_len=5,
    update_only=False,
):
    """
    Create new rules created from collecting unique required phrases accross all rules.

    As a side effect, also update existing rules matched to a required phrase text with the
    "is_required_phrase" flag.

    Consider only rules with the optional ``license_expression`` if provided.
    Process only up to ``max_count`` rules if provided.
    Use min_tokens and min_single_token_len minima to consider what is a long enough rule text.
    """
    if verbose:
        lex = license_expression or "all"
        click.echo(f'Collecting required phrases for {lex!r} license_expression.')
        if max_count:
            click.echo(f'Limiting to {max_count} rules.')

    index = get_index()
    licenses_by_key = get_licenses_db()

    # track text -> expressions to keep only a text that uniquely identifies a single expression
    phrases_by_normalized_phrase = defaultdict(list)

    requested_license_expression = license_expression

    for rules_count, rule in enumerate(index.rules_by_rid, 1):
        if max_count and rules_count == max_count:
            break

        if requested_license_expression and rule.license_expression != requested_license_expression:
            if TRACE:
                click.echo(f'Skipping rule for expression: {rule!r}')
            continue

        license_expression = rule.license_expression

        if (
            rule.is_required_phrase
            or rule.skip_for_required_phrase_generation
            or rule.is_license_intro
            or rule.is_license_clue
            or rule.is_false_positive
            or rule.is_generic(licenses_by_key)
        ):
            if TRACE:
                click.echo(f'Skipping rule: {rule!r}')
            continue

        if verbose:
            click.echo(f'Processing rule: {rule!r}')

        required_phrase_texts = []
        if rule.is_from_license:
            lic = licenses_by_key[license_expression]
            if not lic.is_exception:
                if "license" in lic.name.lower():
                    required_phrase_texts.append(lic.name)
                if "license" in lic.short_name.lower() and lic.short_name != lic.name:
                    required_phrase_texts.append(lic.short_name)
                if not "LicenseRef-scancode" in lic.spdx_license_key:
                    required_phrase_texts.append(lic.spdx_license_key)
                for other_spdx_lic in lic.other_spdx_license_keys:
                    if not "LicenseRef-scancode" in other_spdx_lic:
                        required_phrase_texts.append(other_spdx_lic)
        else:
            required_phrase_texts = get_required_phrase_verbatim(rule.text)
        
        if verbose:
            click.echo(f'Processing rule: {rule!r}: required phrases: {required_phrase_texts}')

        for required_phrase_text in required_phrase_texts:
            if verbose:
                click.echo(f'    Processing rule required_phrase_text: {required_phrase_text!r}')

            phrase = RequiredPhraseRuleCandidate.create(
                license_expression=license_expression,
                text=required_phrase_text,
            )

            if phrase.is_good(rule, min_tokens=min_tokens, min_single_token_len=min_single_token_len):
                phrases_by_normalized_phrase[phrase.normalized_text].append(phrase)

            # Add new variations of the required phrases already present in the list
            for variation in generate_required_phrase_variations(required_phrase_text):
                phrase_variant = RequiredPhraseRuleCandidate.create(
                    license_expression=license_expression,
                    text=variation,
                )
                if phrase_variant.is_good(rule, min_tokens=min_tokens, min_single_token_len=min_single_token_len):
                    phrases_by_normalized_phrase[phrase_variant.normalized_text].append(phrase_variant)

    current_rules_by_identifier = get_rules_by_identifier()

    for phrases in phrases_by_normalized_phrase.values():
        # keep only phrases pointing to the same expression
        if len(set(p.license_expression for p in phrases)) == 1:
            # keep the first one
            phrase = phrases[0]
        else:
            continue

        # check if we already have a rule we can match for this required phrase tag if needed
        matched_rule = rule_exists(text=phrase.raw_text)
        if matched_rule:
            if matched_rule.is_from_license:
                if TRACE and verbose:
                    click.echo(f'Skipping rule matched to license: {matched_rule.identifier}.')
                continue

            actual_rule = current_rules_by_identifier[matched_rule.identifier]
            if actual_rule.skip_for_required_phrase_generation:
                if TRACE and verbose:
                    click.echo(
                        f'WARNING: Skipping pre-existing required phrase rule '
                        f'"skip_for_required_phrase_generation": {actual_rule.identifier}.'
                    )
                continue

            modified = False

            if not actual_rule.is_required_phrase:
                # this combo does not work, make it a reference
                if actual_rule.is_license_intro or actual_rule.is_license_clue:
                    actual_rule.is_license_reference = True
                    actual_rule.is_license_intro = False
                    actual_rule.is_license_clue = False
                actual_rule.is_required_phrase = True
                modified = True

            # keep original text as-is, removing the curly braces
            new_text = actual_rule.text.replace('{{', ' ').replace('}}', ' ')
            if actual_rule.text != new_text:
                actual_rule.text = new_text
                modified = True

            if actual_rule.is_continuous:
                actual_rule.is_continuous = False
                modified = True

            if actual_rule.minimum_coverage:
                actual_rule.minimum_coverage = 0
                modified = True

            if modified:
                actual_rule.dump(rules_data_dir)
                if verbose:
                    click.echo(f'UPDATING existing rule with is_required_phrase flag and more: {actual_rule.identifier}.')
            else:
                if TRACE and verbose:
                    click.echo(f'WARNING: Skipping pre-existing required phrase rule: {actual_rule.identifier}.')
        else:
            if not update_only:
                # at last create a new rule
                rule = phrase.create_rule()
                if verbose:
                    click.echo(f'Creating required phrase new rule: {rule.identifier}.')


def is_long_enough(text, min_tokens, min_single_token_len):
    """
    Return True if ``text`` has at least ``min_tokens`` tokens and at least ``min_single_token_len``
    length if composed of only one token.
    """
    tokens = get_normalized_tokens(text)
    num_tokens = len(tokens)

    if num_tokens < min_tokens:
        return False

    if num_tokens == 1 and len(tokens[0]) < min_single_token_len:
        return False
    else:
        return True


@attr.s
class RequiredPhraseRuleCandidate:
    """
    A candidate phrase object with its license expression, raw text and normalized text. Used when
    generating new rules for requireqed phrases.
    """
    license_expression = attr.ib(metadata=dict(help='A license expression string.'))
    raw_text = attr.ib(metadata=dict(help='Raw, original required phrase text.'))
    normalized_text = attr.ib(metadata=dict(help='Normalized required phrase text.'))

    def is_good(self, rule, min_tokens, min_single_token_len):
        """
        Return True if this phrase is a minimally suitable to use as a required phrase.
        Use the original rule to ensure we skip when referenced_filenames could be damaged.
        Also skip short rules that would contain stopwords as they could not be detected correctly.
        """
        # long enough in words and length if one word
        text = self.normalized_text
        if not is_long_enough(
            text=text,
            min_tokens=min_tokens,
            min_single_token_len=min_single_token_len,
        ):
            return False

        to_ignore = set()
        # not a referenced filename
        to_ignore.update(map(get_normalized_text, rule.referenced_filenames))
        if text in to_ignore:
            return False

        # short rules cannot contain stopwords or else matching will be inaccurate
        stops_in_rule = get_stopwords_in_short_text(text=text)
        if stops_in_rule:
            return False

        return True

    @classmethod
    def create(cls, license_expression, text):
        return cls(
            license_expression=license_expression,
            raw_text=text,
            normalized_text=get_normalized_text(text),
        )

    def create_rule(self):
        """
        Create, save and return a new "required_phrase" Rule from this phrase.
        """
        base_name = f"{self.license_expression}_required_phrase"
        base_loc = find_rule_base_location(name_prefix=base_name)
        file_path = f"{base_loc}.RULE"
        identifier = file_path.split('/')[-1]

        rule = Rule(
            license_expression=self.license_expression,
            identifier=identifier,
            text=self.raw_text,
            is_required_phrase=True,
            is_license_reference=True,
            relevance=100,
        )
        update_ignorables(licensish=rule)
        rule.dump(rules_data_dir)
        return rule


_verbatim_required_phrase = r'{{([^}]+)}}'
collect_verbatim_required_phrase = re.compile(_verbatim_required_phrase, re.UNICODE).findall


def get_required_phrase_verbatim(text):
    """
    Yield required_phrase strings from a rule ``text`` excluding required phrases {{brace}} markers.

    This tokenizer behaves the same as as the ``index_tokenizer`` returning also
    REQUIRED_PHRASE_OPEN and REQUIRED_PHRASE_CLOSE as separate tokens so that they can be
    used to parse required phrases.

    >>> x = list(get_required_phrase_verbatim('bar {{ AGPL-3.0  GNU Affero License v3.0 }} foo'))
    >>> assert x == ['AGPL-3.0  GNU Affero License v3.0'], x

    >>> x = list(get_required_phrase_verbatim(' + {{ ++ AGPL-3.0/}} and {{ GNU Affero License v3.0  }}  '))
    >>> assert x == ['++ AGPL-3.0/', 'GNU Affero License v3.0'], x
    """
    if not text:
        return
    for phrase in collect_verbatim_required_phrase(text):
        phrase = phrase.strip()
        if phrase:
            yield phrase


def generate_required_phrase_variations(text):
    """
    Yield strings that are useful variations of the ``text``, used to generate rule variants.
    """
    words_to_skip = ["the"]
    required_phrase_words = text.split()
    for skip_word in words_to_skip:
        variant = [w for w in required_phrase_words if w.lower() != skip_word]
        yield " ".join(variant)

