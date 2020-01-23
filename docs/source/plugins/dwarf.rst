.. _dwarf_plugin:

Dwarf Plugin
============

This plugin allows users to collect source code path/name from compilation units found in
ELF DWARFs.

Specification
-------------

This plugin will only work with non-stripped ELFs with debug symbols.

Using the Plugin
----------------

User needs to use the ``--dwarf`` option.

The following command will collect all the dwarf references found in non-stripped ELFs::

  $ scancode --dwarf /path/to/codebase/ --json-pp ~/path/to/scan-output.json

Example Output
--------------

Here is an sample output::

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
