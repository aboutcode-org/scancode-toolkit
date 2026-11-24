.. _how-to-add-new-license-detection-rule:

How to add new license rules for enhanced detection
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

.. _license-rule-is-continuous:

Continuous matching with ``is_continuous``
------------------------------------------

``is_continuous`` is an active boolean rule attribute, not a removed feature.
It defaults to ``no``. Set ``is_continuous: yes`` in a rule's YAML frontmatter
when extra words inside a matched sequence would change its meaning and could
cause a false positive.

A continuous match must have no gaps between its matched words. Extra unmatched
words break continuity, whether they are known to ScanCode's license dictionary,
unknown words, or stopwords. Stopwords already present in the rule must match
those in the scanned text. This is a word-based constraint, not a requirement
for byte-for-byte equality of whitespace or punctuation.

For example, a rule can require the following notice to match continuously::

    ---
    license_expression: mit
    is_license_notice: yes
    is_continuous: yes
    minimum_coverage: 100
    ---
    Licensed under the MIT License.

``Licensed under the MIT License.`` satisfies the continuity requirement.
``Licensed under the MIT or Apache License.`` does not, because extra words
interrupt the matched sequence. Words before or after the matched sequence do
not break continuity.

Continuity and coverage are separate constraints: ``is_continuous`` controls
extra words *inside* a match, while ``minimum_coverage: 100`` requires all of the
rule's words to be matched. Do not use ``is_continuous`` alone to request full
rule coverage.

Relationship to required phrases
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Mark a part of a rule with ``{{`` and ``}}`` when that phrase must be present
  and uninterrupted, while the rest of the rule can be matched approximately.
- When one required phrase covers the whole rule text, ScanCode automatically
  sets ``is_continuous`` during rule tokenization. This applies the same
  continuity constraint as setting ``is_continuous: yes`` explicitly.
- ``is_required_phrase: yes`` applies the same continuity check during match
  filtering, but it has an additional purpose: the required-phrase update tools
  collect these rules as phrases to mark in other rules with the same license
  expression. ``is_continuous: yes`` alone does not mark a rule for that
  collection. These flags are therefore not interchangeable as rule metadata.

The older attribute ``only_known_words`` was renamed to ``is_continuous`` and
its meaning was expanded to reject gaps from extra known words and stopwords
as well as unknown words. Use ``is_continuous`` in new rule data, not the old
name.

For implementation details, see ``Rule.is_continuous`` and
``Rule._set_continuous()`` in ``src/licensedcode/models.py``,
``LicenseMatch.is_continuous()`` and
``filter_matches_missing_required_phrases()`` in ``src/licensedcode/match.py``,
and ``collect_is_required_phrase_from_rules()`` in
``src/licensedcode/required_phrases.py``.

See ``src/licensedcode/models.py`` for all rule attributes and other options.

.. note::

    Add rules in a local developement installation and run `scancode-reindex-licenses`
    to make sure we reindex the rules and this validates the new licenses.
