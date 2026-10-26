.. _cli-extractcode:

ExtractCode CLI
===============

ExtractCode is be used as an input preparation step, before running a ScanCode scan.

Usage: ``extractcode [OPTIONS]``

Archives within an extracted archive are extracted **recursively** by default,
with the extraction occurring in a directory named "-extract" alongside the original archive.

**Quick Reference**
-------------------

--shallow   Do not extract recursively nested archives (e.g. Not
            archives in archives).

--verbose   Print verbose file-by-file progress messages.

--quiet     Do not print any summary or progress message.

-h, --help  Show the extractcode help message and exit.

--about     Show information about ScanCode and licensing and exit.

--version   Show the version and exit.
