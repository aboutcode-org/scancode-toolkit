# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import click

from licensedcode import models

"""
A script to generate license detection rules from existing license rules by
replacing strings.
"""

from buildrules import find_rule_base_loc
from buildrules import rule_exists


def get_rules(source, replacement):
    """
    Yield tuple of (rule, new text) for non-false positive existing Rules with a
    text that contains source.
    """
    for rule in models.load_rules():
        if rule.is_false_positive:
            continue
        text = rule.text()
        if source in text:
            yield rule, text.replace(source, replacement)


@click.command()
@click.option("--source", metavar="SOURCE", type=str, help="The source, old string to replace.")
@click.option(
    "--replacement", metavar="REPLACEMENT", type=str, help="The replacement string to use."
)
@click.help_option("-h", "--help")
def cli(source, replacement):
    """
    Create new license detection rules from existing rules by replacing a SOURCE
    string by a REPLACEMENT string in any rule text that contains this SOURCE string.
    """

    for rule, new_text in get_rules(source, replacement):
        existing = rule_exists(new_text)
        if existing:
            continue

        if rule.is_license_intro:
            base_name = "license-intro"
        else:
            base_name = rule.license_expression

        base_loc = find_rule_base_loc(base_name)

        rd = rule.to_dict()
        rd["stored_text"] = new_text
        rd["has_stored_relevance"] = rule.has_stored_relevance
        rd["has_stored_minimum_coverage"] = rule.has_stored_minimum_coverage

        rulerec = models.Rule(**rd)

        # force recomputing relevance to remove junk stored relevance for long rules
        rulerec.set_relevance()

        rulerec.data_file = base_loc + ".yml"
        rulerec.text_file = base_loc + ".RULE"

        print("Adding new rule:")
        print("  file://" + rulerec.data_file)
        print(
            "  file://" + rulerec.text_file,
        )
        rulerec.dump()
        models.update_ignorables(rulerec, verbose=False)
        rulerec.dump()


if __name__ == "__main__":
    cli()
