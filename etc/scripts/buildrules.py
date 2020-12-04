# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/scancode-toolkit/
# The ScanCode software is licensed under the Apache License version 2.0.
# Data generated with ScanCode require an acknowledgment.
# ScanCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# When you publish or redistribute any data created with ScanCode or any ScanCode
# derivative work, you must accompany this data with the following acknowledgment:
#
#  Generated with ScanCode and provided on an "AS IS" BASIS, WITHOUT WARRANTIES
#  OR CONDITIONS OF ANY KIND, either express or implied. No content created from
#  ScanCode should be considered or used as legal advice. Consult an Attorney
#  for any legal advice.
#  ScanCode is a free software code scanning tool from nexB Inc. and others.
#  Visit https://github.com/nexB/scancode-toolkit/ for support and download.

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import io
import os

import attr
import click
click.disable_unicode_literals_warning = True
from license_expression import Licensing
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
class LicenseRule(object):
    data = attr.ib()
    text = attr.ib()
    raw_data = attr.ib(default=None)

    def __attrs_post_init__(self, *args, **kwargs):
        self.raw_data = rdat = '\n'.join(self.data).strip()
        self.text = '\n'.join(self.text).strip()

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
    with io.open(location, encoding='utf-8') as o:
        lines = o.read().splitlines(False)

    rules = []

    data = []
    text = []
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
            if data and ''.join(text).strip():
                rules.append(LicenseRule(data, text))
            data = []
            text = []
            continue

        if line == '---':
            if not in_data:
                raise Exception('Invalid structure: #{ln}: {line}\n'.format(**locals()) +
                                '\n'.join(last_lines[-10:]))

            in_data = False
            in_text = True
            continue

        if in_data:
            data.append(line)
            continue

        if in_text:
            text.append(line)
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
    if match.matcher == match_hash.MATCH_HASH:
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
    Return a new, unique and non-existing base name location suitable to create a new
    rule.
    """
    template = (license_expression
        .lower()
        .strip()
        .replace(' ', '_')
        .replace('(', '')
        .replace(')', '')
        +'_{}')
    idx = 1
    while True:
        base_name = template.format(idx)
        base_loc = os.path.join(models.rules_data_dir, base_name)
        if not os.path.exists(base_loc + '.RULE'):
            return base_loc
        idx += 1


def validate_license_rules(rules_data, licensing):
    """
    Checks all rules and return a list of errors
    """
    errors = []
    for rule in rules_data:
        is_negative = rule.data.get('is_negative')
        is_false_positive = rule.data.get('is_false_positive')
        fp_flags = [f for f in [is_negative, is_false_positive] if f]
        if len(fp_flags) > 1:
            msg = 'Invalid rule with mutually exclusive false positive/negative flags: {}'.format(rule)
            errors.append(msg)
        if is_negative:
            continue

        relevance = rule.data.get('relevance', 0) or 0
        relevance = float(relevance)
        if relevance < 0 or relevance > 100:
            msg = 'Invalid rule relevance: {}'.format(rule)
            errors.append(msg)

        minimum_coverage = rule.data.get('minimum_coverage', 0) or 0
        minimum_coverage = float(minimum_coverage)
        if minimum_coverage < 0 or minimum_coverage > 100:
            msg = 'Invalid rule minimum_coverage: {}'.format(rule)
            errors.append(msg)

        is_license_notice = rule.data.get('is_license_notice')
        is_license_text = rule.data.get('is_license_text')
        is_license_reference = rule.data.get('is_license_reference')
        is_license_tag = rule.data.get('is_license_tag')

        type_flags = [f for f in [is_license_notice, is_license_text, is_license_tag, is_license_reference] if f]
        if len(type_flags) != 1:
            msg = 'Invalid rule is_license_* flags. Only one allowed. At least one needed: {}'.format(rule)
            errors.append(msg)

        license_expression = rule.data.get('license_expression')
        if not license_expression:
            msg = 'Missing license_expression for rule: {}'.format(rule)
            errors.append(msg)

        try:
            licensing.parse(license_expression, validate=True, simple=True)
        except Exception as e:
            msg = 'Invalid license_expression for rule: {}\n{}'.format(rule, str(e))
            errors.append(msg)

    return errors


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

    licenses = cache.get_licenses_db()
    licensing = Licensing(licenses.values())

    print()
    errors = validate_license_rules(rules_data, licensing)
    if errors:
        print('Invalid rules: exiting....')
        for error in errors:
            print(error)
            print()

        raise Exception('Invalid rules: exiting....')

    print()
    for rule in rules_data:
        is_negative = rule.data.get('is_negative')
        is_false_positive = rule.data.get('is_false_positive')
        existing = rule_exists(rule.text)
        if existing and not is_negative:
            print('Skipping existing non-negative rule:', existing, 'with text:\n', rule.text[:50].strip(), '...')
            continue

        if is_negative:
            base_name = 'not-a-license'
        else:
            license_expression = rule.data.get('license_expression')
            license_expression = str(licensing.parse(license_expression, validate=True, simple=True))
            base_name = license_expression
            if is_false_positive:
                base_name = 'false-positive_' + base_name

        base_loc = find_rule_base_loc(base_name)

        data_file = base_loc + '.yml'
        with io.open(data_file, 'w', encoding='utf-8') as o:
            o.write(rule.raw_data)

        text_file = base_loc + '.RULE'
        with io.open(text_file, 'w', encoding='utf-8') as o:
            o.write(rule.text)

        rulerec = models.Rule(data_file=data_file, text_file=text_file)
        rule_tokens = tuple(rulerec.tokens())
        if rule_tokens in rules_tokens:
            # cleanup
            os.remove(text_file)
            os.remove(data_file)
            print('Skipping already added rule with text for:', base_name)
        else:
            rules_tokens.add(rule_tokens)
            rulerec.dump()
            models.update_ignorables(rulerec, verbose=False)
            print('Rule added:', 'file://' + rulerec.data_file, '\n', 'file://' + rulerec.text_file,)


if __name__ == '__main__':
    cli()
