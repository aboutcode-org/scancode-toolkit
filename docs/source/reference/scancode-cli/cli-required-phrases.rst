.. _cli-required-phrases:

scancode required phrases related CLI commands
==============================================

Required phrases are words that **must** be matched/present
in order for a RULE to be considered a match.

Due to the large number of rules present and a large
volume of rules being added regularly to the licecedb, these
CLI options automatically mark and propagate required phrases
in rules and add these required phrases as individual rules
to be used in scancode license detection.

**Quick Reference**
-------------------

Usage: add-required-phrases [OPTIONS]

  Update license detection rules with new "required phrases" to improve rules
  detection accuracy.

Options:
  -o, --from-other-rules          Propagate existing required phrases from
                                  other rules to all selected rules. Mutually
                                  exclusive with --from-license-attributes.
  -a, --from-license-attributes   Propagate license attributes as required
                                  phrases to all selected rules. Mutually
                                  exclusive with --from-other-rule.
  -l, --license-expression STRING
                                  Optional license expression filter. If
                                  provided, only consider the rules that are
                                  using this expression. Otherwise, process
                                  all rules. Example: `apache-2.0`.
  --validate                      Validate that all rules and licenses and
                                  rules are consistent, for all rule
                                  languages. For this validation, run a mock
                                  indexing. The regenerated index is not saved
                                  to disk.
  -r, --reindex                   Recreate and cache the licenses index  with
                                  updated rules add the end.
  -w, --write-phrase-source       In modified rule files, write the source
                                  field to trace the source of required
                                  phrases applied to that rule.
  -d, --delete-phrase-source      In rule files, delete the source extra debug
                                  data used to trace source of phrases.
  --dry-run                       Do not save rules.
  -v, --verbose                   Print verbose logging information.
  -h, --help                      Show this message and exit.

Usage: gen-new-required-phrases-rules [OPTIONS]

  Create new license detection rules from "required phrases" in existing
  rules. Also update existing rules with "is_required_phrase" if they are
  "required phrases" but are not tagged as such.

Options:
  -l, --license-expression STRING
                                  Optional license expression filter. If
                                  provided, only consider the rules that are
                                  using this expression. Otherwise, process
                                  all rules. Example: `apache-2.0`.
  --max-count INT                 Optional maximum count of rules to process.
                                  If provided as a non-zero value, stop after
                                  processing this count of rules.
  -r, --reindex                   Recreate and cache the licenses index  with
                                  updated rules add the end.
  --validate                      Validate that all rules and licenses and
                                  rules are consistent, for all rule
                                  languages. For this validation, run a mock
                                  indexing. The regenerated index is not saved
                                  to disk.
  --min-tokens INT                Minimum number of tokens in the text used to
                                  generate a 'good' new rule.
  --min-single-token-len INT      Minimum length of the token in a single-word
                                  rule text used to generate a 'good' new
                                  rule.
  --update-only                   Do not create new rules, only update
                                  existing rules.
  -v, --verbose                   Print verbose logging information.
  -h, --help                      Show this message and exit
