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
from licensedcode.models import get_rules_by_expression
from licensedcode.models import load_licenses
from licensedcode.models import load_rules
from licensedcode.models import InvalidRule
from licensedcode.models import rules_data_dir
from licensedcode.models import Rule
from licensedcode.models import rule_exists
from licensedcode.models import find_rule_base_location

from licensedcode.spans import Span
from licensedcode.tokenize import required_phrase_tokenizer
from licensedcode.tokenize import index_tokenizer
from licensedcode.tokenize import return_spans_for_required_phrase_in_text
from licensedcode.tokenize import get_ignorable_spans
from licensedcode.tokenize import get_non_overlapping_spans
from licensedcode.tokenize import add_required_phrase_markers
from licensedcode.tokenize import REQUIRED_PHRASE_OPEN
from licensedcode.tokenize import REQUIRED_PHRASE_CLOSE
from licensedcode.tokenize import get_normalized_tokens


# Add the rule identifier here to trace required phrase collection or required
# phrase marking for a specific rule (Example: "mit_12.RULE")
TRACE_REQUIRED_PHRASE_FOR_RULES = []


def get_required_phrase_spans(text):
    """
    Return a list of Spans representin required phrase token positions in the text
    for each required phrase found in the rule ``text``.

    For example:

    >>> text = 'This is enclosed in {{double curly braces}}'
    >>> #       0    1  2        3    4      5     6
    >>> x = get_required_phrase_spans(text)
    >>> assert x == [Span(4, 6)], x

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
    >>> assert x == ['double curly braces'], x
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



def get_normalized_text(text, skip_required_phrase_markers=True):
    return " ".join(
        get_normalized_tokens(
            text=text,
            skip_required_phrase_markers=skip_required_phrase_markers,
        )
    )


def get_num_tokens(text):
    return len(get_normalized_tokens(text))

def is_text_license_reference(text):

    tokens = list(index_tokenizer(text=text))
    words_license_reference = ['http', 'https', 'io', 'com', 'txt', 'md', 'file']
    if any(
        True
        for word in words_license_reference
        if word in tokens
    ):
        return True

    return False


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

    # Generic licenses should not be dumped as required phrase rules
    has_generic_license = attr.ib(
        default=False,
        metadata=dict(
            help='Has a generic license key in its license expression'
        )
    )

    @classmethod
    def create_required_phrase_details(
        cls,
        license_expression,
        required_phrase_text,
        sources,
        length,
        has_generic_license=False,
    ):

        base_name = f"{license_expression}_required_phrase"
        base_loc = find_rule_base_location(name_prefix=base_name)
        file_path = f"{base_loc}.RULE"
        identifier = file_path.split('/')[-1]

        normalized_text = get_normalized_text(required_phrase_text)

        rule = Rule(
            license_expression=license_expression,
            identifier=identifier,
            text=normalized_text,
            is_required_phrase=True,
        )
        if is_text_license_reference(required_phrase_text):
            rule.is_license_reference = True
        else:
            rule.is_license_tag = True

        if not has_generic_license:
            rule.dump(rules_data_dir)

        return cls(
            license_expression=license_expression,
            rule=rule,
            required_phrase_text=normalized_text,
            sources=sources,
            length=length,
            has_generic_license=has_generic_license,
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

    def match_required_phrase_present(self, required_phrase_text):
        """
        Check if a required_phrase_text is present in the list of required_phrases
        or it is a rule in the index.
        Note: Order is important, as the list of required_phrases has both new rules which are
        not yet in the index and old rules also present in the index.
        """
        normalized_text = get_normalized_text(required_phrase_text)

        # check if this required_phrase_text is present in the collected list of required phrases
        for required_phrase in self.required_phrases:
            if required_phrase.required_phrase_text == normalized_text:
                rule = required_phrase.rule
                return rule

        # check if this required_phrase_text is present as a rule in the index
        rule = rule_exists(text=required_phrase_text)
        if rule:
            return rule

    def update_required_phrase_sources(self, rule, has_generic_license=False):
        """
        Given a rule update the required phrases list with this rule

        Note: this should only be called on a rule that is obtained from the
        match_required_phrase_present function so that the rule is present in the
        index/required phrases list. 
        """
        # if rule is present as a required phrase rule in the list then
        # add identifier to sources of the required phrase rule
        for required_phrase in self.required_phrases:
            if required_phrase.rule.identifier == rule.identifier:
                required_phrase.update_sources(rule.identifier)
                return

        if rule and (rule.is_license_intro or rule.is_license_clue):
            return 

        # if rule is present as a rule in the index, set the is_required_phrase flag
        # and add to the list of required phrase rules
        if not rule.is_required_phrase and not has_generic_license:
            rule.is_required_phrase = True
            rule.dump(rules_data_dir)

        normalized_text = get_normalized_text(rule.text) 
        required_phrase_detail = RequiredPhraseDetails(
            license_expression=rule.license_expression,
            rule=rule,
            required_phrase_text=normalized_text,
            sources=[rule.identifier],
            length=len(normalized_text),
            has_generic_license=has_generic_license,
        )
        self.required_phrases.append(required_phrase_detail)

    def sort_required_phrases(self):
        self.required_phrases = sorted(
            self.required_phrases,
            key=lambda x: x.length,
            reverse=True,
        )

    def add_variations_of_required_phrases(self, licenses_by_key):

        words_to_skip = ["the"]
        for required_phrase in self.required_phrases:
            required_phrase_tokens = list(index_tokenizer(text=required_phrase.required_phrase_text))
            skip_words_present = [
                skip_word
                for skip_word in words_to_skip
                if skip_word in required_phrase_tokens
            ]
            for skip_word in skip_words_present:
                required_phrase_tokens.remove(skip_word)
                required_phrase_without_skip_word = " ".join(required_phrase_tokens)
                matched_rule = self.match_required_phrase_present(required_phrase_without_skip_word)
                if matched_rule and matched_rule.skip_collecting_required_phrases:
                    continue

                has_generic_license = does_have_generic_licenses(
                    license_expression=required_phrase.license_expression,
                    licenses_by_key=licenses_by_key,
                )
                if not matched_rule:
                    required_phrase_detail = RequiredPhraseDetails.create_required_phrase_details(
                        license_expression=required_phrase.license_expression,
                        required_phrase_text=required_phrase_without_skip_word,
                        sources=[required_phrase.rule.identifier],
                        length=len(required_phrase_without_skip_word),
                        has_generic_license=has_generic_license,
                    )
                    self.required_phrases.append(required_phrase_detail)
                else:
                    self.update_required_phrase_sources(
                        rule=matched_rule,
                        has_generic_license=has_generic_license,
                    )


def does_have_generic_licenses(license_expression, licenses_by_key):
    licensing = Licensing()
    license_keys = licensing.license_keys(license_expression)
    has_generic_license = False
    for lic_key in license_keys:
        lic = licenses_by_key.get(lic_key)
        if lic and (
            lic.is_generic or lic.is_unknown
        ):
            has_generic_license = True
            break

    return has_generic_license


def collect_required_phrases_in_rules(
    rules_by_expression,
    licenses_by_key,
    license_expression=None,
    verbose=False,
):

    # A mapping of {license_expression: ListOfRequiredPhrases} for all applicable
    # license_expressions
    required_phrases_by_expression = {}

    licensing = Licensing()

    # collect and create required phrase rules
    for license_expression, rules in rules_by_expression.items():

        license_keys = licensing.license_keys(license_expression)
        if len(license_keys) != 1:
            continue

        if verbose:
            click.echo(f'Collecting required phrases for license_expression: {license_expression}')

        required_phrases_list = ListOfRequiredPhrases()

        for rule in rules:
            if rule.skip_collecting_required_phrases:
                continue

            if rule.is_license_intro or rule.is_license_clue:
                continue

            for required_phrase_text in get_required_phrase_texts(rule.text):
                if get_num_tokens(required_phrase_text) < 2:
                    if verbose:
                        click.echo(f'WARNING: single word required phrases in: {rule.identifier}, skipping.')
                    continue

                required_phrase_rule = required_phrases_list.match_required_phrase_present(
                    required_phrase_text=required_phrase_text,
                )

                debug = False
                if rule.identifier in TRACE_REQUIRED_PHRASE_FOR_RULES:
                    debug = True
                    click.echo(
                        f"Collecting from rule: {rule.identifier} "
                        f"Required phrase: '{required_phrase_text}' "
                        f"Matched rule: {required_phrase_rule}"
                    )

                if required_phrase_rule and required_phrase_rule.skip_collecting_required_phrases:
                    continue

                has_generic_license = does_have_generic_licenses(
                    license_expression=license_expression,
                    licenses_by_key=licenses_by_key,
                )
                if required_phrase_rule and required_phrase_rule.license_expression == license_expression:
                    required_phrases_list.update_required_phrase_sources(
                        rule=required_phrase_rule,
                        has_generic_license=has_generic_license,
                    )
                    if debug:
                        click.echo(f"Old required phrase updated, same license expression")

                elif not is_text_license_reference(required_phrase_text):
                    required_phrase_detail = RequiredPhraseDetails.create_required_phrase_details(
                        license_expression=license_expression,
                        required_phrase_text=required_phrase_text,
                        sources=[rule.identifier],
                        length=len(required_phrase_text),
                        has_generic_license=has_generic_license,
                    )
                    required_phrases_list.required_phrases.append(required_phrase_detail)
                    if debug:
                        click.echo(f"New required phrase : {required_phrase_detail} ")
                elif debug:
                    is_reference = is_text_license_reference(required_phrase_text)
                    click.echo(f"is_text_license_reference: {is_reference} ")

        # Add add new variations of the required phrases already present in the list
        required_phrases_list.add_variations_of_required_phrases(licenses_by_key)

        # We need to sort required phrases by length so we look for and mark the longest possible
        # required phrases before the shorter ones contained in the same (substrings)
        required_phrases_list.sort_required_phrases()
        required_phrases_by_expression[license_expression] = required_phrases_list

        if verbose:
            count = len(required_phrases_list.required_phrases)
            texts_with_source = {
                required_phrase.required_phrase_text: required_phrase.sources
                for required_phrase in required_phrases_list.required_phrases
            }
            click.echo(f'Collected {count} required phrases for license_expression: {license_expression}')
            click.echo('Collected required phrases texts: ')
            for text, sources in texts_with_source.items():
                click.echo(f'{text}: {sources}')

    return required_phrases_by_expression


def update_required_phrases_from_other_rules(
    required_phrases_by_expression,
    rules_by_expression,
    write_required_phrases=False,
    verbose=False,
):

    # add required phrases to rules from other rules
    for license_expression, rules in rules_by_expression.items():
        if not license_expression in required_phrases_by_expression:
            continue

        if verbose:
            click.echo(f'marking required phrases in rule texts for license_expression: {license_expression}')

        required_phrases_for_expression = required_phrases_by_expression.get(license_expression)
        add_required_phrases_for_required_phrases(
            rules=rules,
            required_phrases=required_phrases_for_expression.required_phrases,
            verbose=verbose,
        )

    if write_required_phrases:
        for license_expression, required_phrases_list in required_phrases_by_expression.items():
            if verbose:
                click.echo(f'Writing required phrases sources for license_expression: {license_expression}')

            for required_phrase_detail in required_phrases_list.required_phrases:
                if required_phrase_detail.sources and not required_phrase_detail.has_generic_license:
                    required_phrase_detail.rule.dump(
                        rules_data_dir=rules_data_dir,
                        sources=required_phrase_detail.sources
                    )


def add_required_phrases_from_other_rules(
    licenses_by_key,
    license_expression=None,
    write_required_phrases=False,
    verbose=False,
    can_mark_required_phrase_test=False,
):

    rules_by_expression = get_rules_by_expression()
    if license_expression:
        rules_by_expression = {license_expression: rules_by_expression[license_expression]}
    else:
        rules_by_expression = rules_by_expression

    required_phrases_by_expression = collect_required_phrases_in_rules(
        license_expression=license_expression,
        rules_by_expression=rules_by_expression,
        verbose=verbose,
        licenses_by_key=licenses_by_key,
    )

    update_required_phrases_from_other_rules(
        required_phrases_by_expression=required_phrases_by_expression,
        rules_by_expression=rules_by_expression,
        write_required_phrases=write_required_phrases,
        verbose=verbose,
    )


def add_required_phrases_for_required_phrases(required_phrases, rules, verbose=False):

    for rule in rules:
        # skip small rules
        if len(rule.text) < TINY_RULE:
            continue

        for required_phrase in required_phrases:
            debug = False
            if rule.identifier in TRACE_REQUIRED_PHRASE_FOR_RULES:
                click.echo(
                    f"Trying to updating rule: {rule.identifier} "
                    f"with required phrase: '{required_phrase.required_phrase_text}'."
                )
                debug = True

            add_required_phrase_to_rule(
                rule=rule,
                required_phrase=required_phrase.required_phrase_text,
                debug_data=required_phrase.sources,
                debug=debug,
            )


def add_required_phrases_for_license_fields(licence_object, rules, verbose=False):

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


def add_required_phrase_to_rule(rule, required_phrase, debug_data=None, debug=False):

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
    old_required_phrase_spans = get_required_phrase_spans(reloaded_rule.text)

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

    text_rule = reloaded_rule.text

    # we add required phrase markers for the non-overlapping spans
    for span_to_add in spans_to_add:
        text_rule = add_required_phrase_markers(
            text=text_rule,
            required_phrase_span=span_to_add,
        )

    # write the rule on disk if there are any updates
    if text_rule != reloaded_rule.text:
        if debug:
            click.echo(
                f"Updating rule: {reloaded_rule.identifier} "
                f"with required phrase: {required_phrase} "
                f"debug data: {debug_data} /n"
            )
        reloaded_rule.text = text_rule
        reloaded_rule.dump(rules_data_dir)


def add_required_phrases_from_license_fields(
    licenses_by_key,
    license_expression=None,
    verbose=False,
    can_mark_required_phrase_test=False,
):
    """
    For all rules with the `license_expression`, add required phrases from the
    license fields.
    """
    rules_by_expression = get_rules_by_expression()

    if license_expression:
        rules_by_expression_to_update = {license_expression: rules_by_expression[license_expression]}
    else:
        rules_by_expression_to_update = rules_by_expression

    licensing = Licensing()

    for license_expression, rules in rules_by_expression_to_update.items():

        license_keys = licensing.license_keys(license_expression)
        if len(license_keys) != 1:
            continue

        license_key = license_keys.pop()    
        licence_object = licenses_by_key[license_key]

        if verbose:
            click.echo(f'Updating rules with required phrases for license_expression: {license_key}')

        add_required_phrases_for_license_fields(licence_object=licence_object, rules=rules, verbose=verbose)


def delete_required_phrase_rules_debug(rules_data_dir):
    required_phrase_rules = [
        rule
        for rule in load_rules(rules_data_dir=rules_data_dir)
        if rule.is_required_phrase
    ]
    for rule in required_phrase_rules:
        rule.dump(rules_data_dir)


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
    help="Also reindex the license/rules to check for inconsistencies.",
    cls=PluggableCommandLineOption,
)
@click.option(
    "-w",
    "--write-required-phrase-origins",
    is_flag=True,
    default=False,
    help="Write into the rule file the sources for all required phrase rules. Deletes the temporary rule origins used to debug.",
    cls=PluggableCommandLineOption,
)
@click.option(
    "-d",
    "--delete-required-phrase-origins",
    is_flag=True,
    default=False,
    help="Delete the sources for all required phrase rules and exit. This is a debug option.",
    cls=PluggableCommandLineOption,
)
@click.option(
    "-o",
    "--from-other-rules",
    is_flag=True,
    default=False,
    help="Propagate required phrases from already marked required phrases in other rules.",
    cls=PluggableCommandLineOption,
)
@click.option(
    "-a",
    "--from-license-attributes",
    is_flag=True,
    default=False,
    help="Mark required phrases from license attributes.",
    cls=PluggableCommandLineOption,
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    default=False,
    help="Print logging information.",
    cls=PluggableCommandLineOption,
)
@click.help_option("-h", "--help")
def add_required_phrases(
    license_expression,
    verbose,
    reindex,
    from_other_rules,
    from_license_attributes,
    delete_required_phrase_origins,
    write_required_phrase_origins,
):
    """
    For all rules with the `license_expression`, add required phrases from the
    license fields.
    """
    licenses_by_key = load_licenses()

    if delete_required_phrase_origins:
        delete_required_phrase_rules_debug(rules_data_dir)
        return

    # create a list of all required phrases from existing rules, add
    # rule files for them and mark those required phrases if present in other rules
    if from_other_rules:
        add_required_phrases_from_other_rules(
            license_expression=license_expression,
            write_required_phrases=write_required_phrase_origins,
            verbose=verbose,
            licenses_by_key=licenses_by_key,
        )

    # marks required phrases in existing rules from license attributes like name,
    # short name and optionally license keys
    if from_license_attributes:
        add_required_phrases_from_license_fields(
            license_expression=license_expression,
            verbose=verbose,
            licenses_by_key=licenses_by_key,
        )

    if reindex:
        from licensedcode.cache import get_index
        if verbose:
            click.echo('Rebuilding the license index...')
        get_index(force=True)
