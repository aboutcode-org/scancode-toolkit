.. _add_new_license_det_rule:

How to Add New License Rules for Enhanced Detection
===================================================

ScanCode relies on license rules to detect licenses. A rule is a simple text
file containing a license text or notice or mention; And a small companion YAML
text file that tells ScanCode which license expression to report when the text
is detected.

See the :ref:`faq` for a high level description of :ref:`add_new_license_det_rule`.

How to add a new license detection rule?
----------------------------------------

A license detection rule is a pair of files:

- a plain text rule file that is typically a variant of a license text, notice
  or license mention.

- a small text data file (in YAML format) documenting which license expression
  should be detected when the rule text is found in a codebase.

To add a new rule, you need to pick a unique base file name. As a convention, we
like to include the license expression that should be detected in that name to
make it more descriptive. For example: mit_and_gpl-2.0 is a good base name for a
rule that would detect an MIT and GPL-2.0 license combination at once. Add a
suffix to make it unique if there is already a rule with this base name. Do not
use spaces or special characters in that name.

Then create the rule file in the src/licensedcode/data/rules/ directory using
this name, replacing selected_base_name with the base name you selected::

    selected_base_name.RULE

Save your rule text in this file.

Then create the YAML data file in the src/licensedcode/data/rules/ directory
using this name::

    selected_base_name.yml

For a simple mit and gpl-2.0 license expression detection, the content of
this file can be this YAML snippet::

    license_expression: mit AND gpl-2.0
    is_license_notice: yes

Save these two files in the ``src/licensedcode/data/licenses/`` directory and
you are done!

See the ``src/licensedcode/data/rules/`` directory for many examples.

More (advanced) rules options:

- you can use a notes: text field to document this rule and explain where you
  found it first.

- if no license should be detected for your .RULE text, do not add a license expression,
  just add a ``notes`` field.

- Each rules needs have one flag such as is_license_notice. See the
  ``src/licensedcode/models.py`` directory for a list of all possible values and
  other options.

- you can specify key phrases by surrounding one or more words between the `{{`
  and `}}` tags. Key phrases are words that **must** be matched/present in order
  for a RULE to be considered a match.
