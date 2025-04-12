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
import click
import saneyaml

from licensedcode import cache
from licensedcode import models
from licensedcode import frontmatter
from licensedcode.models import get_rule_id_for_text
from license_expression import Licensing

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
        self.raw_data = rdat = "\n".join(self.data_lines).strip()
        self.text = "\n".join(self.text_lines).strip() + "\n"

        # validate YAML syntax
        try:
            self.data = saneyaml.load(rdat)
        except:
            print("########################################################")
            print("Invalid YAML:")
            print(rdat)
            print("########################################################")
            raise
        if "referenced_filenames" in self.data and not self.data["referenced_filenames"]:
            self.data.pop("referenced_filenames")
        self.data = {
            k: v for k, v in self.data.items()
            if v is not None 
            or (v is None and k == "license_expression")
        }


def load_data(location="00-new-licenses.txt"):
    """
    Load rules metadata  and text from file at ``location``. Return a list of
    RuleData.
    """
    with open(location) as o:
        lines = o.read().splitlines(False)

    rules = []

    data_lines = []
    text_lines = []
    in_data = False
    in_text = False
    last_lines = []
    for ln, line in enumerate(lines, 1):
        last_lines.append(": ".join([str(ln), line]))
        if line == "----------------------------------------":
            if not (ln == 1 or in_text):
                raise Exception(
                    "Invalid structure: #{ln}: {line}\n".format(**locals())
                    +"\n".join(last_lines[-10:])
                )

            in_data = True
            in_text = True
            if data_lines and "".join(text_lines).strip():
                rules.append(RuleData(data_lines=data_lines, text_lines=text_lines))

            data_lines = []
            text_lines = []
            continue

        if line == "---":
            if not in_data:
                raise Exception(
                    "Invalid structure: #{ln}: {line}\n".format(**locals())
                    +"\n".join(last_lines[-10:])
                )

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


def all_rule_by_tokens():
    """
    Return a mapping of {(tuple of token id): rule id}, with one item for each
    existing and added rules. Used to avoid duplicates.
    """
    rule_tokens = {}
    for rule in models.get_rules():
        try:
            rule_tokens[tuple(rule.tokens())] = rule.identifier
        except Exception as e:
            rf = f"  file://{rule.rule_file()}"
            raise Exception(
                f"Failed to get tokens from rule:: {rule.identifier}\n" f"{rf}"
            ) from e
    return rule_tokens


def find_rule_base_loc(license_expression):
    """
    Return a new, unique and non-existing base name location suitable to create
    a new rule using the a license_expression as a prefix.
    """
    return models.find_rule_base_location(
        name_prefix=license_expression,
        rules_directory=models.rules_data_dir,
    )


def validate_and_dump_rules(rules, licenses_by_key, licenses_file_path):
    valid_rules_text, invalid_rules_text = validate_rules_with_details(rules, licenses_by_key)
    if invalid_rules_text:
        valid_rules_file = licenses_file_path + ".valid"
        with open(valid_rules_file, "w") as o:
            o.write(valid_rules_text)

        invalid_rules_file = licenses_file_path + ".invalid"
        with open(invalid_rules_file, "w") as o:
            o.write(invalid_rules_text)

        message = [
            'Errors while validating rules:',
            f'See valid rules file: {valid_rules_file}',
            f'See invalid rules file: {invalid_rules_file}',
        ]
        raise models.InvalidRule('\n'.join(message))


def validate_rules_with_details(rules, licenses_by_key):
    """
    Return a tuple of (text of valid rules, text of invalid rules) in the format
    expected by this tool. Invalid rules have a YAML comment text added to their
    metadata section that describes the issue.
    """

    licensing = Licensing(symbols=licenses_by_key.values())

    valid_rules_texts = []
    invalid_rules_texts = []

    for rule in rules:
        error_messages = list(rule.validate(licensing, thorough=True))
        rule_as_text = dump_skinny_rule(rule, error_messages=error_messages)

        if error_messages:
            invalid_rules_texts.append(rule_as_text)
        else:
            valid_rules_texts.append(rule_as_text)

    valid_rules_text = "\n".join(valid_rules_texts) + start_delimiter

    if invalid_rules_texts:
        invalid_rules_text = "\n".join(invalid_rules_texts) + start_delimiter
    else:
        invalid_rules_text = ""

    return valid_rules_text, invalid_rules_text


SKINNY_RULE_TEMPLATE = """\
{start_delimiter}
{metadata}
{end_delimiter}
{content}
"""

start_delimiter = "----------------------------------------"


def dump_skinny_rule(rule, error_messages=()):
    """
    Return a string that dumps the ``rule`` Rule in the input format used by
    this tool. Add a comment with the ``error_message`` to the metadata if any.
    """
    metadata = rule.to_dict()
    if error_messages:
        # add missing metadata for sanity
        if "license_expression" not in metadata:
            m = {"license_expression": None}
            m.update(metadata)
            metadata = m

        if "notes" not in metadata:
            metadata["notes"] = None

        if "referenced_filenames" not in metadata:
            metadata["referenced_filenames"] = None

        msgs = "\n".join(f"# {m}" for m in error_messages)
        end_delimiter = f"{msgs}\n---"
    else:
        end_delimiter = "---"

    return frontmatter.dumps_frontmatter(
        content=rule.text,
        metadata=metadata,
        template=SKINNY_RULE_TEMPLATE,
        start_delimiter=start_delimiter,
        end_delimiter=end_delimiter)


@click.command()
@click.argument(
    "licenses_file", type=click.Path(), metavar="FILE",
)
@click.option(
    "-d", "--dump-to-file-on-errors",
    is_flag=True,
    default=False,
    help="On errors, dump the valid rules and the invalid rules in text files "
        "named after the input FILE with a .valid and a .invalid extension.",
)

@click.help_option("-h", "--help")
def cli(licenses_file, dump_to_file_on_errors=False):
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
            license_expression: lgpl-2.1
            relevance: 100
            is_license_reference: yes
            ---
            LGPL-2.1
            ----------------------------------------
    """

    rules_data = load_data(licenses_file)
    rule_by_tokens = all_rule_by_tokens()

    licenses_by_key = cache.get_licenses_db()
    skinny_rules = []

    for rdata in rules_data:
        relevance = rdata.data.get("relevance")
        rdata.data["has_stored_relevance"] = bool(relevance)

        license_expression = rdata.data.get("license_expression")
        if license_expression:
            rdata.data["license_expression"] = license_expression.lower().strip()

        minimum_coverage = rdata.data.get("minimum_coverage")
        rdata.data["has_stored_minimum_coverage"] = bool(minimum_coverage)

        rl = models.BasicRule(text=rdata.text, **rdata.data)
        skinny_rules.append(rl)

    # these will raise an exception and exit on errors
    if not dump_to_file_on_errors:
        models.validate_rules(rules=skinny_rules, licenses_by_key=licenses_by_key, with_text=True, thorough=True)
    else:
        validate_and_dump_rules(rules=skinny_rules, licenses_by_key=licenses_by_key, licenses_file_path=licenses_file)

    print()
    for rule in skinny_rules:

        if rule.is_false_positive:
            base_name = "false-positive"
        elif rule.is_license_intro:
            base_name = "license-intro"
        elif rule.is_license_clue:
            base_name = f"license-clue_{rule.license_expression}"
        else:
            base_name = rule.license_expression

        base_loc = find_rule_base_loc(base_name)
        identifier = f"{base_loc}.RULE"

        text = rule.text

        existing_rule = get_rule_id_for_text(text)
        skinny_text = " ".join(text[:80].split()).replace("{", " ").replace("}", " ")

        existing_msg = (
            f"Skipping dupe rule for: {base_name!r}, "
            "dupe of: {existing_rule} "
            f"with text: {skinny_text!r}..."
        )

        if existing_rule:
            print(existing_msg.format(**locals()))
            continue

        rd = rule.to_dict(include_text=True)
        rd["has_stored_relevance"] = rule.has_stored_relevance
        rd["has_stored_minimum_coverage"] = rule.has_stored_minimum_coverage
        rd["identifier"] = identifier
        rulerec = models.Rule(**rd)

        # force recomputing relevance to remove junk stored relevance for long rules
        rulerec.set_relevance()

        rule_tokens = tuple(rulerec.tokens())

        existing_rule = rule_by_tokens.get(rule_tokens)
        if existing_rule:
            print(existing_msg.format(**locals()))
            continue
        else:
            print(f"Adding new rule at: file://{identifier}")
            rl = models.update_ignorables(rulerec, verbose=False)
            rl.dump(rules_data_dir=models.rules_data_dir)

            rule_by_tokens[rule_tokens] = base_name


if __name__ == "__main__":
    cli()
