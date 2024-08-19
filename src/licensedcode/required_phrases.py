# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import attr
import os
import click

from license_expression import Licensing
from licensedcode import TINY_RULE

from commoncode.cliutils import PluggableCommandLineOption
from licensedcode.models import map_rules_by_expression
from licensedcode.models import get_rules_by_identifier
from licensedcode.models import get_rules_by_expression
from licensedcode.models import load_licenses
from licensedcode.models import InvalidRule
from licensedcode.models import rules_data_dir
from licensedcode.models import Rule
from licensedcode.models import rule_exists
from licensedcode.models import find_rule_base_location

from licensedcode.spans import Span
from licensedcode.tokenize import required_phrase_tokenizer
from licensedcode.tokenize import return_spans_for_required_phrase_in_text
from licensedcode.tokenize import get_ignorable_spans
from licensedcode.tokenize import get_non_overlapping_spans
from licensedcode.tokenize import add_required_phrase_markers
from licensedcode.tokenize import REQUIRED_PHRASE_OPEN
from licensedcode.tokenize import REQUIRED_PHRASE_CLOSE

  
def get_required_phrase_spans(text):
    """
    Return a list of Spans representin required phrase token positions in the text
    for each required phrase found in the rule ``text``.

    For example:

    >>> text = 'This is enclosed in {{double curly braces}}'
    >>> #       0    1  2        3    4      5     6
    >>> x = get_required_phrase_spans(text)
    >>> assert x == [Span(4, 6)], x

    >>> text = 'This is enclosed in {{double curly braces}}'
    >>> #       0    1  2        3    4      5     6
    >>> x = get_required_phrase_spans(text)
    >>> assert x == ['double', 'curly', 'braces'], x

    >>> text = 'This is {{enclosed}} a  {{double curly braces}} or not'
    >>> #       0    1    2          SW   3      4     5        6  7
    >>> x = get_required_phrase_spans(text)
    >>> assert x == [Span(2), Span(3, 5)], x

    >>> text = 'This {{is}} enclosed a  {{double curly braces}} or not'
    >>> #       0    1      2        SW   3      4     5        6  7
    >>> x = get_required_phrase_spans(text)
    >>> assert x == [Span([1]), Span([3, 4, 5])], x

    >>> text = '{{AGPL-3.0  GNU Affero General Public License v3.0}}'
    >>> #         0    1 2  3   4      5       6      7       8  9
    >>> x = get_required_phrase_spans(text)
    >>> assert x == [Span(0, 9)], x

    >>> assert get_required_phrase_spans('{This}') == []

    >>> def check_exception(text):
    ...     try:
    ...         return get_required_phrase_spans(text)
    ...     except InvalidRule:
    ...         pass

    >>> check_exception('This {{is')
    >>> check_exception('This }}is')
    >>> check_exception('{{This }}is{{')
    >>> check_exception('This }}is{{')
    >>> check_exception('{{}}')
    >>> check_exception('{{This is')
    >>> check_exception('{{This is{{')
    >>> check_exception('{{This is{{ }}')
    >>> check_exception('{{{{This}}}}')
    >>> check_exception('}}This {{is}}')
    >>> check_exception('This }} {{is}}')
    >>> check_exception('{{This}}')
    [Span(0)]
    >>> check_exception('{This}')
    []
    >>> check_exception('{{{This}}}')
    [Span(0)]
    """
    return [
        required_phrase.span
        for required_phrase in get_required_phrases(text)
    ]


def get_required_phrase_texts(text):
    """
    Return a list of required phrase texts for each required phrase found
    in the rule ``text``.

    For example:

    >>> text = 'This is enclosed in {{double curly braces}}'
    >>> #       0    1  2        3    4      5     6
    >>> x = get_required_phrase_texts(text=text)
    >>> assert x == ['double', 'curly', 'braces'], x
    """
    return [
        required_phrase.text
        for required_phrase in get_required_phrases(text)
    ]


@attr.s
class RequiredPhraseInText:

    required_phrase_positions = attr.ib(
        default=attr.Factory(list),
        repr=False,
        metadata=dict(help='List of positions of a required phrase in a rule text.')
    )

    required_phrase_tokens = attr.ib(
        default=attr.Factory(list),
        metadata=dict(help='List of required phrase tokens for this rule.')
    )

    @property
    def text(self):
        """The full normalized text for this required phrase, built from its tokens."""
        return " ".join(self.required_phrase_tokens)

    @property
    def span(self):
        """A span representing the position of this required phrase in a rule text."""
        return Span(self.required_phrase_positions)

    def update(self, token, ipos):
        self.required_phrase_tokens.append(token)
        self.required_phrase_positions.append(ipos)


def get_required_phrases(text):
    """
    Yield RequiredPhraseInText objects with both required phrase positions
    and lists of tokens for each required phrase found in the rule ``text``.
    Tokens form a required phrase when enclosed in {{double curly braces}}.
    """
    ipos = 0
    in_required_phrase = False
    required_phrase = RequiredPhraseInText()
    for token in required_phrase_tokenizer(text):
        if token == REQUIRED_PHRASE_OPEN:
            if in_required_phrase:
                raise InvalidRule('Invalid rule with nested required phrase {{ {{ braces', text)
            in_required_phrase = True

        elif token == REQUIRED_PHRASE_CLOSE:
            if in_required_phrase:
                if required_phrase.required_phrase_tokens:
                    yield required_phrase
                    required_phrase = RequiredPhraseInText()
                else:
                    raise InvalidRule('Invalid rule with empty required phrase {{}} braces', text)
                in_required_phrase = False
            else:
                raise InvalidRule(f'Invalid rule with dangling required phrase missing closing braces', text)
            continue
        else:
            if in_required_phrase:
                required_phrase.update(token=token, ipos=ipos)
            ipos += 1

    if required_phrase.required_phrase_tokens or in_required_phrase:
        raise InvalidRule(f'Invalid rule with dangling required phrase missing final closing braces', text)


@attr.s
class RequiredPhraseDetails:

    license_expression = attr.ib(
        default=None,
        metadata=dict(
            help='A license expression string for this particular required phrase.')
    )

    rule = attr.ib(
        default=None,
        metadata=dict(
            help='The Rule object for this particular required phrase rule.')
    )

    required_phrase_text = attr.ib(
        default=None,
        metadata=dict(
            help='Normalized required phrase text.')
    )

    sources = attr.ib(
        default=attr.Factory(list),
        metadata=dict(
            help='List of all rule identifiers where this required phrase is present.'
        )
    )

    length = attr.ib(
        default=0,
        metadata=dict(
            help='Length of text for this required phrase text (used to sort).'
        )
    )

    @classmethod
    def create_required_phrase_details(
        cls,
        license_expression,
        rule,
        required_phrase_text,
        sources,
        length,
    ):

        base_name = f"{rule.license_expression}_required_phrase"
        base_loc = find_rule_base_location(name_prefix=base_name)
        identifier = f"{base_loc}.RULE"

        rule = Rule(
            license_expression=license_expression,
            identifier=identifier,
            text=required_phrase_text,
            is_required_phrase=True,
        )
        rule.dump(rules_data_dir)

        return cls(
            license_expression=license_expression,
            rule=rule,
            required_phrase_text=required_phrase_text,
            sources=sources,
            length=length,
        )

    def update_sources(self, source_identifier):
        if not source_identifier in self.sources:
            self.sources.append(source_identifier)


@attr.s
class ListOfRequiredPhrases:

    required_phrases = attr.ib(
        default=attr.Factory(list),
        metadata=dict(
            help='A list of RequiredPhraseDetails objects for all the required phrases.')
    )

    def match_required_phrase_present(self, required_phrase_text, rules_by_id=None):
        # check in all rules which are in the index
        rule_id = rule_exists(text=required_phrase_text)
        if not rule_id:
            # check in all rules which are in the collected list of required phrases
            for required_phrase in self.required_phrases:
                if required_phrase.required_phrase_text == required_phrase_text:
                    rule = required_phrase.rule
                    return rule

        if rule_id and rules_by_id:
            rule = rules_by_id.get(rule_id)
            return rule

    def update_required_phrase_sources(self, rule):

        for required_phrase in self.required_phrases:
            if required_phrase.rule.identifier == rule.identifier:
                required_phrase.update_sources(rule.identifier)
                return
        
        #TODO:
        # Update old rules which are required phrases

    def sort_required_phrases(self):
        self.required_phrases = sorted(
            self.required_phrases,
            key=lambda x: x.length,
            reverse=True,
        )


def collect_required_phrases_in_rules(
    rules_by_identifier,
    rules_by_expression,
    license_expression=None,
):

    # 
    required_phrases_by_expression = {}

    licensing = Licensing()

    # collect and create required phrase rules
    for license_expression, rules in rules_by_expression.items():

        license_keys = licensing.license_keys(license_expression)
        if len(license_keys) != 1:
            continue

        required_phrases_list = ListOfRequiredPhrases()

        for rule in rules:
            if rule.skip_collecting_required_phrases:
                continue

            required_phrase_texts_in_rule = get_required_phrase_texts(rule.text)

            for required_phrase_text in required_phrase_texts_in_rule:
                required_phrase_rule = required_phrases_list.match_required_phrase_present(
                    required_phrase_text=required_phrase_text,
                    rules_by_id=rules_by_identifier,
                )
                if not required_phrase_rule:
                    required_phrase_detail = RequiredPhraseDetails.create_required_phrase_details(
                        license_expression=license_expression,
                        required_phrase_text=required_phrase_text,
                        sources=[rule.identifier],
                        length=len(required_phrase_text),
                    )
                    required_phrases_list.required_phrases.append(required_phrase_detail)
                else:
                    required_phrases_list.update_required_phrase_sources(rule)

        required_phrases_list.sort_required_phrases()
        required_phrases_by_expression[license_expression] = required_phrases_list

    return required_phrases_by_expression


def update_required_phrases_from_other_rules(
    required_phrases_by_expression,
    rules_by_expression,
    write_required_phrases=False,
):

    # add required phrases to rules from other rules
    for license_expression, rules in rules_by_expression.items():

        if not license_expression in required_phrases_by_expression:
            continue

        required_phrases_for_expression = required_phrases_by_expression.get(license_expression)
        add_required_phrases_for_required_phrases(
            rules=rules,
            required_phrases=required_phrases_for_expression.required_phrases,
        )

    if write_required_phrases:
        for required_phrases_list in required_phrases_by_expression.values():
            for required_phrase_detail in required_phrases_list:
                if required_phrase_detail.sources:
                    required_phrase_detail.rule.dump(
                        rules_data_dir=rules_data_dir,
                        sources=required_phrase_detail.sources
                    )


def add_required_phrases_from_other_rules(
    license_expression=None,
    write_required_phrases=False,
):

    rules_by_identifier = get_rules_by_identifier()
    rules_by_expression = map_rules_by_expression(rules_by_identifier)

    if license_expression:
        rules_by_expression = {license_expression: rules_by_expression[license_expression]}
    else:
        rules_by_expression = rules_by_expression

    required_phrases_by_expression = collect_required_phrases_in_rules(
        license_expression=license_expression,
        rules_by_identifier=rules_by_identifier,
        rules_by_expression=rules_by_expression,
    )

    update_required_phrases_from_other_rules(
        required_phrases_by_expression=required_phrases_by_expression,
        rules_by_expression=rules_by_expression,
        write_required_phrases=write_required_phrases,
    )


def add_required_phrases_for_required_phrases(required_phrases, rules):

    for rule in rules:
        # skip small rules
        if len(rule.text) < TINY_RULE:
            continue

        for required_phrase in required_phrases:
            add_required_phrase_to_rule(
                rule=rule,
                required_phrase=required_phrase.required_phrase_text,
            )


def add_required_phrases_for_license_fields(licence_object, rules):

    license_fields_mapping_by_order = {
        "name": licence_object.name,
        "short_name": licence_object.short_name,
        #"key",
        #"spdx_license_key"
    }

    for rule in rules:
        # skip small rules
        if len(rule.text) < TINY_RULE:
            continue

        for license_field_value in license_fields_mapping_by_order.values():
            add_required_phrase_to_rule(rule=rule, required_phrase=license_field_value)


def add_required_phrase_to_rule(rule, required_phrase):

    # Reload from file as there could be changes from other license fields
    rule_file = os.path.join(rules_data_dir, rule.identifier)
    reloaded_rule = Rule.from_file(rule_file)

    # we get spans for name/short_name if they exist
    new_required_phrase_spans = return_spans_for_required_phrase_in_text(
        text=reloaded_rule.text,
        required_phrase=required_phrase,
    )

    # we get spans for already existing required phrases and ignorables
    ignorable_spans = get_ignorable_spans(reloaded_rule)
    old_required_phrase_spans = reloaded_rule.build_required_phrase_spans()

    # we verify whether there are spans which overlap with the
    # already present required phrases or ignorables
    spans_to_add = list(
        get_non_overlapping_spans(
            old_required_phrase_spans=old_required_phrase_spans + ignorable_spans,
            new_required_phrase_spans=new_required_phrase_spans
        )
    )

    text_rule = reloaded_rule.text
    
    # we add required phrase markers for the non-overlapping spans
    for span_to_add in spans_to_add:
        text_rule = add_required_phrase_markers(
            text=text_rule,
            required_phrase_span=span_to_add
        )

    # write the rule on disk if there are any updates
    if text_rule != reloaded_rule.text:
        click.echo(f"Updating rule: {reloaded_rule.identifier}")
        reloaded_rule.text = text_rule
        reloaded_rule.dump(rules_data_dir)


def add_required_phrases_from_license_fields(license_expression=None, reindex=False, cli=False):
    """
    For all rules with the `license_expression`, add required phrases from the
    license fields.
    """
    rules_by_expression = get_rules_by_expression()

    if license_expression:
        rules_by_expression_to_update = {license_expression: rules_by_expression[license_expression]}
    else:
        rules_by_expression_to_update = rules_by_expression

    licenses = load_licenses()
    licensing = Licensing()

    for license_expression, rules in rules_by_expression_to_update.items():

        license_keys = licensing.license_keys(license_expression)
        if len(license_keys) != 1:
            continue

        license_key = license_keys.pop()    
        licence_object = licenses[license_key]

        if cli:
            click.echo(f'Updating rules with required phrases for license_expression: {license_key}')

        add_required_phrases_for_license_fields(licence_object=licence_object, rules=rules)

    if reindex:
        from licensedcode.cache import get_index
        if cli:
            click.echo('Rebuilding the license index...')
        get_index(force=True)


@click.command(name='add-required-phrases')
@click.option(
    "-l",
    "--license-expression",
    type=str,
    default=None,
    metavar="STRING",
    help="The license expression, for which the rules will be updated with required phrases. "
    "Example STRING: `mit`. If this option is not used, add required_phrases for all rules.",
    cls=PluggableCommandLineOption,
)
@click.option(
    "-r",
    "--reindex",
    is_flag=True,
    default=False,
    help="Also reindex the license/rules to check for inconsistencies. ",
    cls=PluggableCommandLineOption,
)
@click.option(
    "-d",
    "--delete-required-phrases-debug",
    is_flag=True,
    default=False,
    help="Write into their corresponding rule files the sources for all required phrase rules.",
    cls=PluggableCommandLineOption,
)
@click.option(
    "-w",
    "--write-required-phrases",
    is_flag=True,
    default=False,
    help="Also reindex the license/rules to check for inconsistencies. ",
    cls=PluggableCommandLineOption,
)
@click.help_option("-h", "--help")
def add_required_phrases(license_expression, reindex, delete_required_phrases_debug, write_required_phrases):
    """
    For all rules with the `license_expression`, add required phrases from the
    license fields.
    """

    # creates a list of all required phrases and adds rule files for them
    add_required_phrases_from_other_rules(
        delete_required_phrases_debug=delete_required_phrases_debug,
        write_required_phrases=write_required_phrases,
    )

    # Marks required phrases in already present rules
    add_required_phrases_from_license_fields(
        license_expression=license_expression,
        reindex=reindex,
        cli=True
    )

