.. _faq:

FAQ
===

Why ScanCode?
-------------

We could not find an existing tool (open source or commercial) meeting our needs:

- usable from the command line or as library
- running on Linux, Mac and Windows
- written in a higher level language such as Python
- easy to extend and evolve
- accurately detecting most licenses and copyrights


How is ScanCode different from Debian licensecheck?
-------------------------------------------------------

At a high level, ScanCode detects more licenses and copyrights than licensecheck
does, reporting more details about the matches. It is likely slower.

In more details: ScanCode is a Python app using a data-driven approach (as
opposed to carefully crafted regex like licensecheck uses):

- for license scan, the detection is based on a (large) number of license full
  texts (~2100) and license notices, mentions and variants (~32,000) and is data-
  driven as opposed to regex-driven. It detects and reports exactly where
  license text is found in a file. Just throw in more license texts to improve
  the detection.

- for copyright scan, the approach is natural language parsing grammar; it has a
  few thousand tests.

- licenses and copyrights are detected in texts and binaries

- licenses and copyrights are also detected in structured package manifests


Licensecheck (available here for reference:
https://metacpan.org/pod/App::Licensecheck ) is a Perl script using hand-
crafted regex patterns to find typical copyright statements and about 50 common
licenses. There are about 50 license detection tests.

A quick test (in July 2015, before a major refactoring, but for this may still
be still valid) shows several things that are not detected by licensecheck that
are detected by ScanCode.


How can I integrate ScanCode in my application?
-----------------------------------------------

More specifically, does this tool provide an API which can be used by us for the
integration with my system to trigger the license check and to use the result?

In terms of API, there are two stable entry points:

- The JSON output when you use it as a command line tool from any language
  or when you call the scancode.cli.scancode function from a Python script.

- Otherwise the scancode.cli.api module provides a simple function if you
  are only interested in calling a certain service on a given file (such as
  license detection or copyright detection)


Can I install ScanCode in a Unicode path?
-----------------------------------------

Yes and this is fully supported and tested. See
https://github.com/aboutcode-org/scancode-toolkit/issues/867
for a previous bug that was preventing this.

There was a bug in virtualenv https://github.com/pypa/virtualenv/issues/457 that
is now fixed and has been extensively tested for ScanCode.


The line numbers for a copyright found in a binary are weird. What do they mean?
--------------------------------------------------------------------------------

When scanning binaries, the line numbers are just a relative indication of where
a detection was found: there is no such thing as lines in a binary. The numbers
reported are based on the strings extracted from the binaries, typically broken
as new lines with each NULL character.


How does ``--license-text`` for ScanCode works exactly?
-------------------------------------------------------------

Is the matched text that gets included into the result exactly the lines of text
from the input file that are covered by the ``start_line`` and ``end_line``
fields of the result? I.e., if I would post-process the input file and extract
``start_line`` to ``end_line`` from it, would I get exactly the ``matched_text``
contents? Or is there some more "magic" involved when populating the
``matched_text`` field?

ScanCode is a bit smarter than just start and end line, as matching is based on
words, not lines of the actual scanned text. And a whole line may not always be matched.

For instance with this command::

    $ echo "Foo is a wonder piece of code. Licensed under the GPL. " \
        "For support contact foo@bar.com " > tst
    $ scancode --license --license-text --license-text-diagnostics --yaml - tst
    ...
        license_detections:
            -   license_expression: gpl-1.0-plus
                license_expression_spdx: GPL-1.0-or-later
                matches:
                    -   license_expression: gpl-1.0-plus
                        license_expression_spdx: GPL-1.0-or-later
                        from_file: tst
                        start_line: 1
                        end_line: 1
                        matcher: 2-aho
                        score: '100.0'
                        matched_length: 4
                        match_coverage: '100.0'
                        rule_relevance: 100
                        rule_identifier: gpl_85.RULE
                        rule_url: https://github.com/nexB/scancode-toolkit/tree/develop/src/licensedcode/data/rules/gpl_85.RULE
                        matched_text: Foo is a wonder piece of code. Licensed under the GPL.
                            For support contact foo@bar.com
                        matched_text_diagnostics: Licensed under the GPL.
    ...

then:

- ``matched_text`` is based on ``start_line`` and ``end_line``
- ``matched_text_diagnostics`` is based on the exact matched words

Note that ``matched_text_diagnostics`` also includes "tagged" gaps or extra
unmatched words highlighted between the matched words.

