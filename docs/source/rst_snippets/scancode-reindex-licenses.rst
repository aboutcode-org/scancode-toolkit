``scancode-reindex-licenses`` Usage
-----------------------------------

Usage: ``scancode-reindex-licenses [OPTIONS]``

Reindex scancode licenses and exit

Options
-------

  --all-languages             [EXPERIMENTAL] Rebuild the license index
                              including texts all languages (and not only
                              English) and exit.
  --only-builtin              Rebuild the license index excluding any
                              additional license directory or additional
                              license plugins which were added previously, i.e.
                              with only builtin scancode license and rules.
  --additional-directory DIR  Include this directory with additional custom
                              licenses and license rules in the license
                              detection index.
  --load-dump                 Load all license and rules from their respective
                              files and then dump them back to those same files.
  -h, --help                  Shows the options and explanations.
