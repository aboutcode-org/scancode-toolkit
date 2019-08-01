# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 nexB Inc. and others. All rights reserved.
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

import click
click.disable_unicode_literals_warning = True
import saneyaml


from licensedcode.models import Rule
from licensedcode.models import update_ignorables


TRACE = True

def load_data(location='00-new-licenses.txt'):
    with io.open(location, encoding='utf-8') as o:
        lines = o.read().splitlines(False)

    rules = []

    data = []
    text = []
    in_data = False
    in_text = False
    for ln, line in enumerate(lines):
        if line == '----------------------------------------':
            if not (ln == 0 or in_text):
                raise Exception('Invalid structure: #{ln}: {line}'.format(**locals()))

            in_data = True
            in_text = True
            if data and ''.join(text).strip():
                rules.append((data, text))
            data = []
            text = []
            continue

        if line == '---':
            if not in_data:
                raise Exception('Invalid structure: #{ln}: {line}'.format(**locals()))

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
    Return the matched rule if the text is an existing rule matched exactly, False otherwise.
    """
    from licensedcode.cache import get_index
    from licensedcode.match_hash import MATCH_HASH
    idx = get_index()

    matches = idx.match(query_string=text)
    if len(matches) != 1:
        return False
    match = matches[0]
    if match.matcher == MATCH_HASH:
        return match.rule.identifier


def find_rule_base_loc(license_expression):
    """
    Return a new, unique and non-existing base name location suitable to create a new
    rule.
    """
    from licensedcode.models import rules_data_dir
    # existing_names = set(n.rsplit('.', 1)[0] for n in os.listdir(rules_data_dir) if n.endswith('.RULE'))
    template = license_expression.lower().strip().replace(' ', '_').replace('(', '').replace(')', '') + '_{}'
    idx = 1
    while True:
        base_name = template.format(idx)
        base_loc = os.path.join(rules_data_dir, base_name)
        if not os.path.exists(base_loc + '.RULE'):
            return base_loc
        idx += 1


@click.command()
@click.argument('licenses_file', type=click.Path(), metavar='FILE')
@click.help_option('-h', '--help')
def cli(licenses_file):
    """
    Create rules from a structured text file

    For instance:
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
    rule_data = load_data(licenses_file)
    rules_tokens = set()
    print()
    for data, text in rule_data:
        rdat = '\n'.join(data)
        rtxt = '\n'.join(text)
        existing = rule_exists(rtxt)
        if existing:
            print('Skipping existing rule:', existing, 'with text:\n', rtxt[:50], '...')
            continue

        # validate YAML syntax
        parsed = saneyaml.load(rdat)
        if parsed.get('is_negative'):
            license_expression = 'not-a-license'
        else:
            _, _, license_expression = data[0].partition(': ')
            license_expression = license_expression.strip()
            if not license_expression:
                raise Exception('Missing license_expression for text:', rtxt)
        base_loc = find_rule_base_loc(license_expression)

        data_file = base_loc + '.yml'
        with io.open(data_file, 'w', encoding='utf-8') as o:
            o.write(rdat)

        text_file = base_loc + '.RULE'
        with io.open(text_file, 'w', encoding='utf-8') as o:
            o.write(rtxt)
        rule = Rule(data_file=data_file, text_file=text_file)
        rule_tokens = tuple(rule.tokens())
        if rule_tokens in rules_tokens:
            # cleanup
            os.remove(text_file)
            os.remove(data_file)
            print('Skipping already added rule with text for:', license_expression)
        else:
            rules_tokens.add(rule_tokens)
            rule.dump()
            update_ignorables(rule, verbose=True)
            print('Rule added:', rule.identifier)


if __name__ == '__main__':
    cli()
