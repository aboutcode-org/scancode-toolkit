.. _how-to-add-modify-license-detection-rule:

How to add or modify license rules for enhanced detection
==========================================================

ScanCode relies on license rules to detect licenses. A rule is a simple text
file containing a license text or notice or mention with YAML frontmatter with data
attributes that tells ScanCode which license expression to report when the text
is detected, and other properties.

.. _adding_a_new_rule:

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

.. note::

    Add rules in a local developement installation and run `scancode-reindex-licenses`
    to make sure we reindex the rules and this validates the new licenses.

See the ``src/licensedcode/data/rules/`` directory for many examples.

The mandatory rules options are:

- Every rule (except `is_false_positive` rules) must have a `license-expression`
  field. The license keys used in the license expression must also be
  present in the scancode licenseDB as a `.LICENSE` file and these license
  keys can be joined by: `OR`, `AND`, `WITH` operators

- Each rule needs to have one flag to describe the type of license rule.
  You cannot use more than one flag for a rule. The options are:

  - `is_license_notice`
  - `is_license_text`
  - `is_license_tag`
  - `is_license_reference`
  - `is_license_intro`
  - `is_license_clue`
  - `is_false_positive`

Some more optional rule data fields:

- `minimum_coverage` is the percentage of rule text which must be present for
  this rule to match to a piece of text. Highly recommended to set these for
  rules which have high similarity to rules of another license.

- `relevance` is a license rule data which signifies how relevant/important a
  piece of rule text is, and eventually contributes to the match score.
  A lower relevance means lower confidence that the `license-expression`
  set for this rule is correct for this rule text. This is set to `100`
  as a default if the rule has atleast 18 words (or more), unless
  otherwise set explicitly. Relevance should be set when the text does not
  completely represent the given license-expression for the rule. For
  example some rules reference just `gpl` and not to a specific version
  of the gpl license, or some online references to a license might be
  modified and outdated in some cases.

- if a rule is being deprecated it should be marked with the `is_deprecated`
  data field being set to `True`. This can be because the license-expression
  is adjusted/changed for the rule or the rule is promoted to being a proper
  license text.

.. note::

  A rule should never be deleted entirely, only deprecated with the
  `is_deprecated` data field as older versions of scancode could still
  use and link to a particular rule and this is useful to debug license
  detections. If rules are deleted and the same identifier is assigned
  to another rule text then the same rule identifier might have different
  text for different versions of scancode and this is inconsistent data.

- you can use a `notes` text field to document this rule and explain where you
  found it first.

- if no license should be detected for your .RULE text (`is_false_positive` cases),
  do not add a license expression, just add a ``notes`` field.

- `is_continuous` should be set to `True` if a rule can only be matched as a
  continious piece of text and not as approximate or partial matches.

- `language` should be set as a two-letter ISO 639-1 language code if the rule
  text is a non-english language. See https://en.wikipedia.org/wiki/ISO_639-1

See the ``src/licensedcode/models.py`` directory for a list of all possible values
and other options.

False positive rules and license clues
--------------------------------------

`false-positive` rules
^^^^^^^^^^^^^^^^^^^^^^^

There can also be false positive rules, which if detected in the file scanned, will not
be present in the result license detections. These just have the license text and a
`is_false_positive` flag set to True. You must add some notes documenting where this
false positive rule was found as false positive rules often have a specific origin.

False positive rules must be very specific, and should contain as much words in the
rule text as possible, before and after the words which were matched wrongly. This
is to ensure we don't discard postentially correct matches at all. For example
sometimes `gpl` or other 3 letter license names are detected as a false-positive
in code as these are likely to appear and in this case we have to add a
false-positive rule with the entire symbol (like a function/variable name) or
entire lines of code, potentially with lines before/after.

`license-clue` rules
^^^^^^^^^^^^^^^^^^^^^

License clues are pieces of license text which are not directly related to
what the license is exactly for that piece of code, but a clue to what the
license terms could be.

Some cases of license clues are:

- generic permissive terms related to the license, but cannot be matched to
  a particular license
- references to non-legal entities/names which has certain license conditions
- certain statements which indicate that a license text/notice is present
  elsewhere, but does not say anything about what this license is

If a rule is categorized as a `license-clue` the effects of this are:

- This license key is not represented in the `detected_license_expression`
  for this file
- The license match is not present in the file-level or top-level
  `license_detections` data mapping, but present in a seperate file-level
  `license_clues` data mapping

But if these license clues are present in a package sepcific context, like
in a file/data mapping where package licenses are declared, this is detected
and reported as-is like other license detections.

selecting `is-false-positive` vs `is-license-clue`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If a piece of text/words is not related to the license of the
particular file/package it was found in at all, then this is
a `false-positive` rule. If this could be related but we cannot
be sure from just the text, this is a `license-clue`.

If a piece of license text references some code/module/package
which might or might not be present in the codebase, or license
conditions which might be optionally relevant, this could be
useful and therefore a `license-clue`.

For categorizing a rule as a `false-positive` license rule, we must
be sure that this piece of text cannot ever be related to the license
of the code where it could be found, otherwise this is a `license-clue`
or even other types of license rules.

See examples in scancode licenseDB of rules with these tags for
more details on these data fields.

Required phrases in rules
-------------------------

Required phrases are words that **must** be matched/present
in order for a RULE to be considered a match.

Required phrases are the most important parts of a license rule text,
and in case of a partial match, absence of the required phrases in the
matched part of the text in most cases will result in a wrong match
(or a false postive in some cases). In other words, to partially match
a piece of text with a license rule, we must check the presense of the
required phrases of the rule in that piece of text.

For example consider the following text:

  This program is free software: you can redistribute it and/or modify it
  under the terms of the {{GNU AGPL v3 License}} as published by
  the Free Software Foundation, version 3 of the License.

Here the text ``GNU AGPL v3 License`` is essential to be present exactly in
the text for a correct match, and otherwise this can match partially with
something which is almost the same text, but an entirely different license.
Like ``GNU GPL v3 License`` which is only a character/word different.

You can specify required phrases by surrounding one or more words between
the `{{` and `}}` tags. See the example above for a required phrase
marked in a rule.

Here are some guidelines on marking required phrases in a rule:

- Mark the entire essential part of the license text as a required phrase
- Always include numerical versions or distinguishing parts of the license text
  in the required phrase
- Required phrases are usually license names, alias names or other license references
- License references like named local files and links to webpages which contain the
  license name should also be marked as a required phrases
- If there are multiple occurances of the distinguishing parts, or the
  license names we must mark all of them as required phrases.


Marking required phrases automatically
--------------------------------------

Required phrases present in larger license texts are used in multiple ways on
their own in scancode:

- To mark the same required phrase present in other license texts
- Used as a seperate license detection step for partial/unknown matches
- Determine the license expression of a new piece of license text/rule to
  be added to licensedb

For these reasons there are the following console scripts to automatically:

- mark required phrases in rules propagated from other rules
- create individual new rules which are marked as required phrase in larger
  texts

See :ref:`cli-required-phrases` for the available options.


Helper scripts to add many license rules together
-------------------------------------------------

Adding many license rules at once from a single file with a script
is beneficial because:

- you don't need to create seperate files for each rule
- there is a numerical part to differentiate rules for the same
  license key, and this doesn't need to be determined
- rule validations (checking for inconsistent data fields) are
  performed and violations are displayed all at once
- ignorables (copyrights, references etc) are added automatically
- rules which are already present will be skipped automatically

This can be beneficial even if you're adding a single or just a couple
rules for the same reasons.

These are the locations of the rule template and script from the
root of the scancode source directory:

- the script: `etc/scripts/licenses/buildrules.py`
- the template: `etc/scripts/licenses/buildrules-template.txt`
- an example template file: `etc/scripts/licenses/buildrules-example.txt`

These are the steps to execute the script and create rules:

- start from a activated scancode developement virtualenv
  See :ref:`install-scancode-from-source`
- Populate the template file with rules
  see :ref:`adding_a_new_rule` for more info on adding rules
- Run the script from the activated virtualenv with:
  `python etc/scripts/licenses/buildrules.py etc/scripts/licenses/buildrules-template.txt`
- If there are any errors, fix them in the rule template and run the script again
- Run `scancode-reindex-licenses` to check if the rules are being indexed properly
  See :ref:`cli-scancode-reindex-licenses` for more details
