How to
======

Extract-archives
****************

ScanCode Toolkit provides archive extraction. This command can be used before running a scan over a codebase in order to ensure all archives are extracted. Archives found inside an extracted archive are extracted recursively. Extraction is done in-place in a directory and named ``-extract``

.. image:: scancode-toolkit-extract.png
   :target: index.html

* Usage:: 

    ./extractcode [OPTIONS] <input>

## Extraction example:

Extract all archives found in the ``samples`` directory::

    ./extractcode samples


