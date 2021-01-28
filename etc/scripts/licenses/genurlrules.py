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

from commoncode import fetch

from licensedcode.cache import get_index
from licensedcode.match_hash import MATCH_HASH
from licensedcode.models import Rule


TRACE = True


def fetch_text(url):
    """
    Fetch and return a temp file from the content at `url`.
    """
    if 'raw' in url:
        fetchable = url
    elif 'github.com' in url and '/blob/' in url:
        fetchable = url.replace('/blob/', '/raw/')
    else:
        fetchable = url
    print('  Fetching:', fetchable)
    return fetch.download_url(fetchable, timeout=120)


def get_license_expression(location):
    """
    Return the matched license expression for a file at location.
    """
    matches = get_license_matches(location=location)
    if matches:
        expressions = [m.rule.license_expression for m in matches]
        return combine_expressions(expressions)
    else:
        return 'unknown'


def get_license_matches(location=None, query_string=None):
    """
    Return a list of matches for text or location.
    """
    idx = get_index()
    return idx.match(location=location, query_string=query_string)


def get_existing_rule(text):
    """
    Return the matched rule if the text is an existing rule matched exactly,
    False otherwise.
    """
    matches = get_license_matches(query_string=text)
    if len(matches) == 1:
        match = matches[0]
        if match.matcher == MATCH_HASH:
            return match.rule


def combine_expressions(expressions, relation='AND', licensing=Licensing()):
    """
    Return a combined license expression string with relation, given a list of
    license expressions strings.

    For example:
    >>> a = 'mit'
    >>> b = 'gpl'
    >>> combine_expressions([a, b])
    'mit AND gpl'
    >>> assert 'mit' == combine_expressions([a])
    >>> combine_expressions([])
    >>> combine_expressions(None)
    >>> combine_expressions(('gpl', 'mit', 'apache',))
    'gpl AND mit AND apache'
    """
    if not expressions:
        return

    if not isinstance(expressions, (list, tuple)):
        raise TypeError(
            'expressions should be a list or tuple and not: {}'.format(
                type(expressions)))

    # Remove duplicate element in the expressions list
    expressions = dict((x, True) for x in expressions).keys()

    if len(expressions) == 1:
        return expressions[0]

    expressions = [licensing.parse(le, simple=True) for le in expressions]
    if relation == 'OR':
        return str(licensing.OR(*expressions))
    else:
        return str(licensing.AND(*expressions))


def find_rule_base_loc(license_expression):
    """
    Return a new, unique and non-existing base name location suitable to create a new
    rule.
    """
    from licensedcode.models import rules_data_dir
    template = (
        license_expression.lower().strip()
            .replace(' ', '_')
            .replace('(', '').replace(')', '')
            +'_url_{}'
    )
    idx = 1
    while True:
        base_name = template.format(idx)
        base_loc = os.path.join(rules_data_dir, base_name)
        if not os.path.exists(base_loc + '.RULE'):
            return base_loc
        idx += 1


def gen_rules(urls):
    """
    Create rules from license URLs listed in FILE (one URL per line)

    Each line can be a single URL or a URL|license-expression.
    If a single URL, download the content at URL and run license detection,
    then generate a rule for each URL using the detected license.
    If the license expression in provided, use this for the generated rule.
    """

    errors = []
    seen = set()
    with open(urls) as uf:
        for i, url in enumerate(uf):
            url = url.strip()
            if not url or url.startswith('#'):
                continue
            if url in seen:
                continue
            else:
                seen.add(url)
 
            has_exp = False
            print('Processing:', i, repr(url))
            if '|' in url:
                url, has_exp, license_expression = url.partition('|')
            if not url:
                continue

            existing = get_existing_rule(url)
            if existing:
                print('  Rule already exists, skipping')
                continue

            if url and not has_exp:
                try:
                    fetched = fetch_text(url)
                    license_expression = get_license_expression(fetched)
                except Exception as e:
                    print('  Failed:', repr(e))
                    errors.append(url)
                    continue

            base_loc = find_rule_base_loc(license_expression)
            data_file = base_loc + '.yml'
            text_file = base_loc + '.RULE'
            with open(text_file, 'w') as o:
                o.write(url)

            rule = Rule(
                license_expression=license_expression,
                is_license_reference=True,
                relevance=95,
                text_file=text_file
            )
            rule.data_file = data_file
            rule.dump()
            print('  Rule added:', rule.identifier)

    if errors:
        print('Failed to process these URLs:')
        for r in errors:
            print(r)


@click.command()
@click.argument('urls', type=click.Path(), metavar='FILE')
@click.help_option('-h', '--help')
def cli(urls):
    """
    Create rules from license URLs listed in FILE (one URL per line)

    Each line can be a single URL or a URL|license-expression.
    If a single URL, download the content at URL and run license detection,
    then generate a rule for each URL using the detected license.
    If the license expression in provided, use this for the generated rule.
    """
    gen_rules(urls)



if __name__ == '__main__':
    cli()
