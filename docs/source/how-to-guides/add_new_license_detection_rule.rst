.. _add_new_license_det_rule:

How to Add New License Rules for Enhanced Detection
===================================================

ScanCode relies on license rules to detect licenses. A rule is a simple text
file containing a license text or notice or mention with YAML frontmatter with data
attributes that tells ScanCode which license expression to report when the text
is detected, and other properties.

See the :ref:`faq` for a high level description of adding license detection rules.

How to add a new license detection rule?
----------------------------------------

A license detection rule is a file with:

- a plain text that is typically a variant of a license text, notice or license
  mention.

- data as YAML frontmatter documenting license expression and other
  rule attributes.

To add a new rule, you need to pick a unique base file name. As a convention, we
like to include the license expression that should be detected in that name to
make it more descriptive. For example: mit_and_gpl-2.0 is a good base name for a
rule that would detect an MIT and GPL-2.0 license combination at once. Add a
suffix (usually numeric) to make it unique if there is already a rule with
this base name. Do not use spaces or special characters in that name.

Then create the rule file in the `src/licensedcode/data/rules/` directory using
this name; for example a rule with `license_expression` as `mit AND apache-2.0`
might have a filename: `mit_and_apache-2.0_10.RULE`.

Save your rule text in this file; if there are specific words like company names,
projects or other, it is better to have rules with and without these so we have
better detection.

For a simple `mit AND apache-2.0` license expression detection, here is an example
rule file::


    ---
    license_expression: mit AND apache-2.0
    is_license_notice: yes
    relevance: 100
    referenced_filenames:
        - LICENSE
    ---

    ## License
    The MIT License (MIT) + Apache 2.0. Read [LICENSE](LICENSE).

See the ``src/licensedcode/data/rules/`` directory for many examples.

More (advanced) rules options:

- you can use a `notes` text field to document this rule and explain where you
  found it first.

- if no license should be detected for your .RULE text, do not add a license expression,
  just add a ``notes`` field.

- Each rule needs to have one flag to describe the type of license rule. The options are:

  - `is_license_notice`
  - `is_license_text`
  - `is_license_tag`
  - `is_license_reference`
  - `is_license_intro`

- There can also be false positive rules, which if detected in the file scanned, will not
  be present in the result license detections. These just have the license text and a
  `is_false_positive` flag set to True.

- you can specify required phrases by surrounding one or more words between the `{{`
  and `}}` tags. Key phrases are words that **must** be matched/present in order
  for a RULE to be considered a match.

See the ``src/licensedcode/models.py`` directory for a list of all possible values
and other options.

.. note::

    Add rules in a local developement installation and run `scancode-reindex-licenses`
    to make sure we reindex the rules and this validates the new licenses.
