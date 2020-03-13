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

Can licenses be synchronized with the DejaCode license library?
---------------------------------------------------------------

The license keys are the same that are used in DejaCode. They are kept in sync by hand in the
short term. There is also a ticket to automate that sync with DejaCode and possibly other sources.
See https://github.com/nexB/scancode-toolkit/issues/41

How is ScanCode different from licensecheck?
--------------------------------------------

At a high level, ScanCode detects more licenses and copyrights than licensecheck does, reporting
more details about the matches. It is likely slower.

In more details: ScanCode is a Python app using a data-driven approach (as opposed to carefully
crafted regex):

- for license scan, the detection is based on a (large) number of license full texts (~900) and
  license notices/rules (~1800) and is data driven as opposed to regex-driven. It detects exactly
  where in a file a license text is found. Just throw in more license texts to improve the
  detection.
- for copyright scan, the approach is natural language parsing (using NLTK) with POS tagging and
  a grammar; it has a few thousand tests.
- licenses and copyrights are detected in texts and binaries

Licensecheck (available here for reference: /https://metacpan.org/release/App-Licensecheck )
is a Perl script using hand-crafted regex patterns to find typical copyright statements and
about 50 common licenses. There are about 50 license detection tests.

A quick test (in July 2015, before a major refactoring, but for this notice still valid) shows
several things that are not detected by licensecheck that are detected by ScanCode.

How can I integrate ScanCode in my application?
-----------------------------------------------

More specifically, does this tool provide an API which can be used by us for the integration
with my system to trigger the license check and to use the result?

In terms of API, there are two stable entry points:

#. The JSON output when you use it as a command line tool from any language or when you call
the scancode.cli.scancode function from a Python script.
#. Otherwise the scancode.cli.api module provides a simple function if you are only interested
in calling a certain service on a given file (such as license detection or copyright detection)

Can I install ScanCode in a Unicode path?
-----------------------------------------

Not for now. See https://github.com/nexB/scancode-toolkit/issues/867 There is a bug in virtualenv
on Python2 https://github.com/pypa/virtualenv/issues/457 At this stage and until we completed the
migration to Python 3 there is no way out but to use a path that contains only ASCII characters.

..
  [ToDo] Update from Python 2.x to Python 3.x

The line numbers for a copyright found in a binary are weird. What do they mean?
--------------------------------------------------------------------------------

When scanning binaries, the line numbers are just a relative indication of where a detection was
found: there is no such thing as lines in a binary. The numbers reported are based on the strings
extracted from the binaries, typically broken as new lines with each NULL character. They can be
safely ignored.
