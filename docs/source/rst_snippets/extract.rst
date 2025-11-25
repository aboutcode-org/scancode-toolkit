``extractcode`` Usage
---------------------

Usage: extractcode [OPTIONS] <input>

  extract archives and compressed files in the <input> file or directory tree.

  Archives found inside an extracted archive are extracted recursively. Use
  --shallow for a shallow extraction. Extraction for each archive is done in-
  place in a new directory named '<archive file name>-extract' created side-
  by-side with an archive.

Options:

.. _cli_extract:

  --verbose            Print verbose file-by-file progress messages.
  --quiet              Do not print any summary or progress message.
  --shallow            Do not extract recursively nested archives in archives.
  --replace-originals  Replace extracted archives by the extracted content.
  --ignore TEXT        Ignore files/directories matching this glob pattern.
  --all-formats        Extract archives from all known formats. The default is
                       to extract only the common format of these kinds:
                       "regular", "regular_nested" and "package". To show all
                       supported formats use the option --list-formats .
  --list-formats       Show the list of supported archive and compressed file
                       formats and exit.
  -h, --help           Show this message and exit.
  --about              Show information about ExtractCode and its licensing
                       and exit.
  --version            Show the version and exit.

Examples:

  (Note for Windows: use '\' backslash instead of '/' slash for paths.)

  Extract all archives found in the 'samples' directory tree:

      extractcode samples

  Note: If an archive contains other archives, all contained archives will be
  extracted recursively. Extraction is done directly in the 'samples'
  directory, side-by-side with each archive. Files are extracted in a
  directory named after the archive with an '-extract' suffix added to its
  name, created side-by-side with the corresponding archive file.

  Extract a single archive. Files are extracted in the directory
  'samples/arch/zlib.tar.gz-extract/':

      extractcode samples/arch/zlib.tar.gz

This is intended to be used as an input preparation step, before running the scan. Archives found
in an extracted archive are extracted **recursively** by default. Extraction is done in-place
in a directory named '-extract' side-by-side with an archive.

To extract the packages in the ``samples`` directory

::

    extractcode samples

This extracts the zlib.tar.gz package:

.. image::  /rst_snippets/data/extractcode.png
