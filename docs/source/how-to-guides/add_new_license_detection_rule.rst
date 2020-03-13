.. _add_new_license_det_rule:

How to Add New License Rules for Enhanced Detection
===================================================

ScanCode relies on license rules to detect licenses. A rule is a simple text file containing a
license text or notice or mention. And a small YAML text file that tells ScanCode which licenses
to report when the text is detected.

See the :ref:`faq` for a high level description of :ref:`add_new_license_det_rule`.

How to add a new license detection rule?
----------------------------------------

A license detection rule is a pair of files:

- a plain text rule file that is typically a variant of a license text, notice or license mention.
- a small text data file (in YAML format) documenting which license(s) should be detected for the
  rule text.

To add a new rule, you need to pick a unique base file name. As a convention, we like to include the
license key(s) that should be detected in that name to make it more descriptive. For example:
mit_and_gpl-2.0 is a good base name. Add a suffix to make it unique if there is already a rule
with this base name. Do not use spaces or special characters in that name.

Then create the rule file in the src/licensedcode/data/rules/ directory using this name, replacing
selected_base_name with the base name you selected::

    selected_base_name.RULE

Save your rule text in this file.

Then create the YAML data file in the src/licensedcode/data/rules/ directory using this name::

    selected_base_name.yml

For a simple mit and gpl-2.0 detection license keys detection, the content of this file can be
this YAML snippet::

    licenses:
        - mit
        - gpl-2.0

Save these two files in the ``src/licensedcode/data/licenses/`` directory and you are done!

See the ``src/licensedcode/data/rules/`` directory for examples.

More (advanced) rules options:

- you can use a notes: text field to document this rule.

- if no license should be detected for your .RULE text, do not add a list of license keys,
  just add a note.

- .RULE text can contain special text regions that can be ignored when scanning for licenses.
  You can mark a template region in your rule text using {{double curly braces}} and up to five
  words can vary and still match this rule. You must add this field in your .yml data file to mark
  this rule as a template

::

    template: yes

- By using a number after the opening braces, more than five words can be skipped.
  With {{10 double curly braces }} ten words would be skipped.

- To mark a rule as detecting a choice of licenses, add this field in your .yml file::

    license_choice: yes

See the `#257 issue <https://github.com/nexB/scancode-toolkit/issues/257>`_ and the related
`#258 pull request <https://github.com/nexB/scancode-toolkit/pull/258>`_ for an example:
this adds a new rule to detect a combination of MIT or GPL.
