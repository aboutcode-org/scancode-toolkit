.. _dwarf-plugin:

Dwarf plugin
============

This plugin allows users to collect source code path/name from compilation units found in
ELF DWARFs.

Specification
-------------

This plugin will only work with non-stripped ELFs with debug symbols.

Using the plugin
----------------

User needs to use the ``--dwarf`` option.

The following command will collect all the dwarf references found in non-stripped ELFs

.. code-block:: shell

  scancode --dwarf /path/to/codebase/ --json-pp ~/path/to/scan-output.json

**Example**

 .. code-block:: none

    {
      "path": "project/stripped.ELF",
      "type": "file",
      "dwarf_source_path": [],
      "scan_errors": []
    },
    {
      "path": "project/non-stripped.ELF",
      "type": "file",
      "dwarf_source_path": ['/tmp/test.c],
      "scan_errors": []
    }
