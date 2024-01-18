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

from license_expression import Licensing

from commoncode.cliutils import PluggableCommandLineOption
from licensedcode.models import load_licenses
from licensedcode.models import get_rules_by_expression
from licensedcode.models import add_key_phrases_for_license_fields


@click.command()
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
def cli(license_expression, reindex):
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

        click.echo(f'Updating rules with required phrases for license_expression: {license_key}')

        add_key_phrases_for_license_fields(licence_object=licence_object, rules=rules)

    if reindex:
        from licensedcode.cache import get_index
        click.echo('Rebuilding the license index...')
        get_index(force=True)


if __name__ == "__main__":
    cli()
