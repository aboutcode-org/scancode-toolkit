.. _how_to_extract_archives:

How To Extract Archives
=======================

ScanCode-Toolkit provides archive extraction. This command can be used before running a scan over
a codebase in order to ensure all archives are extracted. Archives found inside an extracted
archive are extracted recursively. Extraction is done in-place in a directory and named after the
archive with ``'-extract'`` appended.

.. image:: data/scancode-toolkit-extract.png

Usage:
------

::

   extractcode [OPTIONS] <input>

.. include::  /rst_snippets/extract.rst
