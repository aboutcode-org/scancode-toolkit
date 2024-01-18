# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
import click

from license_expression import Licensing
from licensedcode import TINY_RULE

from commoncode.cliutils import PluggableCommandLineOption
from licensedcode.models import get_rules_by_expression
from licensedcode.models import load_licenses
from licensedcode.models import InvalidRule
from licensedcode.models import rules_data_dir
from licensedcode.models import Rule

from licensedcode.spans import Span
from licensedcode.tokenize import key_phrase_tokenizer
from licensedcode.tokenize import return_spans_for_key_phrase_in_text
from licensedcode.tokenize import get_ignorable_spans
from licensedcode.tokenize import get_non_overlapping_spans
from licensedcode.tokenize import add_key_phrase_markers
from licensedcode.tokenize import KEY_PHRASE_OPEN
from licensedcode.tokenize import KEY_PHRASE_CLOSE



def get_key_phrase_spans(text):
    """
    Yield Spans of key phrase token positions found in the rule ``text``.
    Tokens form a key phrase when enclosed in {{double curly braces}}.

    For example:

    >>> text = 'This is enclosed in {{double curly braces}}'
    >>> #       0    1  2        3    4      5     6
    >>> x = list(get_key_phrase_spans(text))
    >>> assert x == [Span(4, 6)], x

    >>> text = 'This is {{enclosed}} a  {{double curly braces}} or not'
    >>> #       0    1    2          SW   3      4     5        6  7
    >>> x = list(get_key_phrase_spans(text))
    >>> assert x == [Span(2), Span(3, 5)], x

    >>> text = 'This {{is}} enclosed a  {{double curly braces}} or not'
    >>> #       0    1      2        SW   3      4     5        6  7
    >>> x = list(get_key_phrase_spans(text))
    >>> assert x == [Span([1]), Span([3, 4, 5])], x

    >>> text = '{{AGPL-3.0  GNU Affero General Public License v3.0}}'
    >>> #         0    1 2  3   4      5       6      7       8  9
    >>> x = list(get_key_phrase_spans(text))
    >>> assert x == [Span(0, 9)], x

    >>> assert list(get_key_phrase_spans('{This}')) == []

    >>> def check_exception(text):
    ...     try:
    ...         return list(get_key_phrase_spans(text))
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
    ipos = 0
    in_key_phrase = False
    key_phrase = []
    for token in key_phrase_tokenizer(text):
        if token == KEY_PHRASE_OPEN:
            if in_key_phrase:
                raise InvalidRule('Invalid rule with nested key phrase {{ {{ braces', text)
            in_key_phrase = True

        elif token == KEY_PHRASE_CLOSE:
            if in_key_phrase:
                if key_phrase:
                    yield Span(key_phrase)
                    key_phrase.clear()
                else:
                    raise InvalidRule('Invalid rule with empty key phrase {{}} braces', text)
                in_key_phrase = False
            else:
                raise InvalidRule(f'Invalid rule with dangling key phrase missing closing braces', text)
            continue
        else:
            if in_key_phrase:
                key_phrase.append(ipos)
            ipos += 1

    if key_phrase or in_key_phrase:
        raise InvalidRule(f'Invalid rule with dangling key phrase missing final closing braces', text)


def add_key_phrases_for_license_fields(licence_object, rules):

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

            # Reload from file as there could be changes from other license fields
            rule_file = os.path.join(rules_data_dir, rule.identifier)
            reloaded_rule = Rule.from_file(rule_file)

            # we get spans for name/short_name if they exist
            new_key_phrase_spans = return_spans_for_key_phrase_in_text(
                text=reloaded_rule.text,
                key_phrase=license_field_value
            )

            # we get spans for already existing key phrases and ignorables
            ignorable_spans = get_ignorable_spans(reloaded_rule)
            old_key_phrase_spans = reloaded_rule.build_key_phrase_spans()

            # we verify whether there are spans which overlap with the
            # already present key phrases or ignorables
            spans_to_add = list(
                get_non_overlapping_spans(
                    old_key_phrase_spans=old_key_phrase_spans + ignorable_spans,
                    new_key_phrase_spans=new_key_phrase_spans
                )
            )

            text_rule = reloaded_rule.text
            
            # we add key phrase markers for the non-overlapping spans
            for span_to_add in spans_to_add:
                text_rule = add_key_phrase_markers(
                    text=text_rule,
                    key_phrase_span=span_to_add
                )

            # write the rule on disk if there are any updates
            if text_rule != reloaded_rule.text:
                click.echo(f"Updating rule: {reloaded_rule.identifier}")
                reloaded_rule.text = text_rule
                reloaded_rule.dump(rules_data_dir)


def add_required_phrases_to_rules(license_expression=None, reindex=False, cli=False):
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

        add_key_phrases_for_license_fields(licence_object=licence_object, rules=rules)

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
@click.help_option("-h", "--help")
def add_required_phrases(license_expression, reindex):
    """
    For all rules with the `license_expression`, add required phrases from the
    license fields.
    """
    add_required_phrases_to_rules(
        license_expression=license_expression,
        reindex=reindex,
        cli=True
    )

