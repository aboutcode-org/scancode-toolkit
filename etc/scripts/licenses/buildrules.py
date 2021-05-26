# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import io

import attr
import click
import saneyaml

from licensedcode import cache
from licensedcode import models
from licensedcode import match_hash

"""
A script to generate license detection rules from a simple text data file.

Note that the .yml data files are validated and the script will report
errors and stop if a rule data is not valid.

Typicaly validation errors include:
- missing license expressions
- unknown license keys
- presence of multiple is_license_xxx: flags (only one is allowed)

The file buildrules-template.txt is an template of this data file.
The file buildrules-exmaples.txt is an example of this data file.
This file contains one or more block of data such as:

 ----------------------------------------
 license_expression: foo OR bar
 relevance: 100
 is_license_notice: yes
 ---
 This is licensed under a choice of foo or bar.
 ----------------------------------------

The first section (before ---) contains the data in valid YAML that
will be saved in the rule's .yml file.

The second section (after ---) contains the rule text saved in the
the .RULE text file.

If a RULE already exists, it is skipped.
"""


@attr.attrs(slots=True)
class RuleData(object):
    data_lines = attr.ib()
    text_lines = attr.ib()
    raw_data = attr.ib(default=None)
    data = attr.ib(default=None)
    text = attr.ib(default=None)

    def __attrs_post_init__(self, *args, **kwargs):
        self.raw_data = rdat = '\n'.join(self.data_lines).strip()
        self.text = '\n'.join(self.text_lines).strip()

        # validate YAML syntax
        try:
            self.data = saneyaml.load(rdat)
        except:
            print('########################################################')
            print('Invalid YAML:')
            print(rdat)
            print('########################################################')
            raise


def load_data(location='00-new-licenses.txt'):
    """
    Load rules metadata  and text from file at ``location``. Return a list of
    LicenseRulew.
    """
    with io.open(location, encoding='utf-8') as o:
        lines = o.read().splitlines(False)

    rules = []

    data_lines = []
    text_lines = []
    in_data = False
    in_text = False
    last_lines = []
    for ln, line in enumerate(lines, 1):
        last_lines.append(': '.join([str(ln), line]))
        if line == '----------------------------------------':
            if not (ln == 1 or in_text):
                raise Exception('Invalid structure: #{ln}: {line}\n'.format(**locals()) +
                                '\n'.join(last_lines[-10:]))

            in_data = True
            in_text = True
            if data_lines and ''.join(text_lines).strip():
                rules.append(RuleData(data_lines=data_lines, text_lines=text_lines))

            data_lines = []
            text_lines = []
            continue

        if line == '---':
            if not in_data:
                raise Exception(
                    'Invalid structure: #{ln}: {line}\n'.format(**locals()) +
                    '\n'.join(last_lines[-10:]))

            in_data = False
            in_text = True
            continue

        if in_data:
            data_lines.append(line)
            continue

        if in_text:
            text_lines.append(line)
            continue

    return rules


def rule_exists(text):
    """
    Return the matched rule identifier if the text is an existing rule matched
    exactly, False otherwise.
    """
    idx = cache.get_index()

    matches = idx.match(query_string=text)
    if not matches:
        return False
    if len(matches) > 1:
        return False
    match = matches[0]
    if match.matcher == match_hash.MATCH_HASH and match.score() == 100:
        return match.rule.identifier


def all_rule_tokens():
    """
    Return a set of tuples of tokens, one corresponding to every existing and
    added rules. Used to avoid duplicates.
    """
    rule_tokens = set()
    for rule in models.get_rules():
        rule_tokens.add(tuple(rule.tokens()))
    return rule_tokens


def find_rule_base_loc(license_expression):
    """
    Return a new, unique and non-existing base name location suitable to create
    a new rule using the a license_expression as a prefix.
    """
    return models.find_rule_base_location(
        license_expression, rules_directory=models.rules_data_dir)


@click.command()
@click.argument('licenses_file', type=click.Path(), metavar='FILE')
@click.help_option('-h', '--help')
def cli(licenses_file):
    """
    Create rules from a text file with delimited blocks of metadata and texts.

    As an example a file would contains one of more blocks such as this:

\b
        ----------------------------------------
        license_expression: lgpl-2.1
        relevance: 100
        is_license_notice: yes
        ---
        This program is free software; you can redistribute it and/or modify
        it under the terms of the GNU Lesser General Public License
        version 2.1 as published by the Free Software Foundation;
        ----------------------------------------
    """

    rules_data = load_data(licenses_file)
    rules_tokens = all_rule_tokens()

    licenses_by_key = cache.get_licenses_db()
    skinny_rules = []

    for rdata in rules_data:
        relevance = rdata.data.get('relevance')
        rdata.data['has_stored_relevance'] = bool(relevance)

        minimum_coverage = rdata.data.get('minimum_coverage')
        rdata.data['has_stored_minimum_coverage'] = bool(minimum_coverage)

        rl = models.BasicRule(**rdata.data)
        rl.stored_text = rdata.text
        skinny_rules.append(rl)

    models.validate_rules(skinny_rules, licenses_by_key, with_text=True)

    print()
    for rule in skinny_rules:
        existing = rule_exists(rule.text())
        if existing:
            print('Skipping existing rule:', existing, 'with text:\n', rule.text()[:50].strip(), '...')
            continue

        if rule.is_false_positive:
            base_name = 'false-positive'
        elif rule.is_license_intro:
            base_name = 'license-intro'
        else:
            base_name = rule.license_expression

        base_loc = find_rule_base_loc(base_name)

        rd = rule.to_dict()
        rd['stored_text'] = rule.stored_text
        rd['has_stored_relevance'] = rule.has_stored_relevance
        rd['has_stored_minimum_coverage'] = rule.has_stored_minimum_coverage

        rulerec = models.Rule(**rd)

        rulerec.data_file = base_loc + '.yml'
        rulerec.text_file = base_loc + '.RULE'

        rule_tokens = tuple(rulerec.tokens())

        if rule_tokens in rules_tokens:
            print('Skipping already added rule with text for:', base_name)
        else:
            rules_tokens.add(rule_tokens)
            rulerec.dump()
            models.update_ignorables(rulerec, verbose=False)
            print('Rule added:', 'file://' + rulerec.data_file, '\n', 'file://' + rulerec.text_file,)


if __name__ == '__main__':
    cli()
