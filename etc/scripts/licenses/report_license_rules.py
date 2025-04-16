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
import csv

from commoncode.cliutils import PluggableCommandLineOption
from licensedcode.models import load_licenses
from licensedcode.models import load_rules


LICENSES_FIELDNAMES = [
    "key",
    "short_name",
    "name",
    "category",
    "owner",
    "text",
    "words_count",
    "notes",
    "minimum_coverage",
    "homepage_url",
    "is_exception",
    "language",
    "is_unknown",
    "spdx_license_key",
    "reference_url",
    "text_urls",
    "other_urls",
    "standard_notice",
    "license_filename",
    "faq_url",
    "ignorable_authors",
    "ignorable_copyrights",
    "ignorable_holders",
    "ignorable_urls",
    "ignorable_emails",
    "osi_license_key",
    "osi_url",
    "other_spdx_license_keys",
]


RULES_FIELDNAMES = [
    "identifier",
    "license_expression",
    "relevance",
    "text",
    "words_count",
    "category",
    "is_false_positive",
    "is_license_text",
    "is_license_notice",
    "is_license_tag",
    "is_license_reference",
    "is_license_intro",
    "is_license_clue",
    "is_required_phrase",
    "skip_for_required_phrase_generation",
    "is_deprecated",
    "has_unknown",
    "only_known_words",
    "notes",
    "referenced_filenames",
    "minimum_coverage",
    "ignorable_copyrights",
    "ignorable_holders",
    "ignorable_authors",
    "ignorable_urls",
    "ignorable_emails",
]


SCANCODE_LICENSEDB_URL = "https://scancode-licensedb.aboutcode.org/{}"


def write_data_to_csv(data, output_csv, fieldnames):

    with open(output_csv, "w") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for entry in data:
            w.writerow(entry)


def filter_by_attribute(data, attribute, required_key):
    """
    Filters by attribute, if value is required_key.
    Example `attribute`: `category`. Example `required_key`: `Permissive`.
    """
    return [entry for entry in data if entry.get(attribute, "None") == required_key]


def flatten_output(data):

    assert isinstance(data, list)

    output = []
    for entry in data:
        assert isinstance(entry, dict)

        output_entry = {}
        for key, value in entry.items():
            if value is None:
                continue

            if isinstance(value, list):
                value = " ".join(value)
            elif not isinstance(value, str):
                value = repr(value)

            output_entry[key] = value

        output.append(output_entry)

    return output


@click.command()
@click.option(
    "-l",
    "--licenses",
    type=click.Path(dir_okay=False, writable=True, readable=False),
    default=None,
    metavar="FILE",
    help="Write all Licenses data to the csv FILE.",
    cls=PluggableCommandLineOption,
)
@click.option(
    "-r",
    "--rules",
    type=click.Path(dir_okay=False, writable=True, readable=False),
    default=None,
    metavar="FILE",
    help="Write all Rules data to the csv FILE.",
    cls=PluggableCommandLineOption,
)
@click.option(
    "-c",
    "--category",
    type=str,
    default=None,
    metavar="STRING",
    help="An optional filter to only output licenses/rules of this category. "
    "Example STRING: `permissive`.",
    cls=PluggableCommandLineOption,
)
@click.option(
    "-k",
    "--license-key",
    type=str,
    default=None,
    metavar="STRING",
    help="An optional filter to only output licenses/rules which has this license key. "
    "Example STRING: `mit`.",
    cls=PluggableCommandLineOption,
)
@click.option(
    "-t",
    "--with-text",
    is_flag=True,
    default=False,
    help="Also include the license/rules texts (First 200 characters). "
    "Note that this increases the file size significantly.",
    cls=PluggableCommandLineOption,
)
@click.help_option("-h", "--help")
def cli(licenses, rules, category, license_key, with_text):
    """
    Write Licenses/Rules from scancode into a CSV file with all details.
    Output can be optionally filtered by category/license-key.
    """
    licenses_output = []
    rules_output = []

    licenses_data = load_licenses()

    if licenses:
        for lic in licenses_data.values():
            license_data = lic.to_dict()
            if with_text:
                license_data["text"] = lic.text[:200]
            license_data["is_unknown"] = lic.is_unknown
            license_data["length"] = len(lic.text)
            license_data["reference_url"] = SCANCODE_LICENSEDB_URL.format(lic.key)
            licenses_output.append(license_data)

        if category:
            licenses_output = filter_by_attribute(
                data=licenses_output, attribute="category", required_key=category
            )

        if license_key:
            licenses_output = filter_by_attribute(
                data=licenses_output,
                attribute="key",
                required_key=license_key,
            )

        licenses_output = flatten_output(data=licenses_output)
        write_data_to_csv(data=licenses_output, output_csv=licenses, fieldnames=LICENSES_FIELDNAMES)

    if rules:
        rules_data = list(load_rules())
        for rule in rules_data:
            rule_data = rule.to_dict()
            rule_data["identifier"] = rule.identifier
            rule_data["referenced_filenames"] = rule.referenced_filenames
            if with_text:
                rule_data["text"] = rule.text[:200]
            rule_data["has_unknown"] = rule.has_unknown
            rule_data["length"] = len(rule.text)
            try:
                rule_data["category"] = licenses_data[rule_data["license_expression"]].category
            except KeyError:
                pass
            rules_output.append(rule_data)

        if category:
            rules_output = filter_by_attribute(
                data=rules_output,
                attribute="category",
                required_key=category,
            )

        if license_key:
            rules_output = filter_by_attribute(
                data=rules_output,
                attribute="license_expression",
                required_key=license_key,
            )

        rules_output = flatten_output(rules_output)
        write_data_to_csv(data=rules_output, output_csv=rules, fieldnames=RULES_FIELDNAMES)


if __name__ == "__main__":
    cli()
