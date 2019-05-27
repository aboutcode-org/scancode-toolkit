How to
======

Extract-archives
****************

ScanCode Toolkit provides archive extraction. This command can be used before running a scan over a codebase in order to ensure all archives are extracted. Archives found inside an extracted archive are extracted recursively. Extraction is done in-place in a directory and named ``-extract``

.. figure:: scancode-toolkit-extract.png
   :width: 700px

Usage:: 

    ./extractcode [OPTIONS] <input>

**Extraction example:**

Extract all archives found in the ``samples`` directory::

    ./extractcode samples

Run a Scan
**********

**Quickstart**

ScanCode results are provided as:

1. JSON file (default)
2. html (static html)
3. csv

The basic usage is::

    ./scancode [OPTIONS] <OUTPUT FORMAT(S)> <input>

  OUTPUT FORMAT(S)::
    --json FILE             Write scan output as compact JSON to FILE.
    --json-pp FILE          Write scan output as pretty-printed JSON to FILE.
    --json-lines FILE       Write scan output as JSON Lines to FILE.
    --csv FILE              Write scan output as CSV to FILE.
    --html FILE             Write scan output as HTML to FILE.
    --custom-output FILE    Write scan output to FILE formatted with the custom
                            Jinja template file.
    --custom-template FILE  Use this Jinja template FILE as a custom template.
    --spdx-rdf FILE         Write scan output as SPDX RDF to FILE.
    --spdx-tv FILE          Write scan output as SPDX Tag/Value to FILE.
    --html-app FILE         (DEPRECATED: use the ScanCode Workbench app instead
                            ) Write scan output as a mini HTML application to
                            FILE.

The ``<input>`` file or directory is what will be scanned for origin clues. The results will be saved to the ``FILE``.


The following example scans will show you how to run a scan with each of the result formats. For the scans, we will use the ``samples`` directory provided with the ScanCode Toolkit.


**JSON file output**

Scan the ``samples`` directory and save the scan to a sample JSON file::

    ./scancode --json samples.json samples


.. figure:: scancode-toolkit-json-output.png
   :width: 700px

**Static html output**

Scan the ``samples`` directory for licenses and copyrights and save the scan results to an HTML file.  When the scan is done, open ``samples.html`` in your web browser::

    ./scancode --html samples.html samples

.. figure:: scancode-toolkit-static-html1.png
   :width: 700px
.. figure:: scancode-toolkit-static-html2.png
   :width: 700px
