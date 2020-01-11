.. _cpp_includes_plugin:

CPP Includes Plugin
===================

This plugin allows users to collect the #includes statements in C/C++ files.

Using the Plugin
----------------

User needs to use the ``--cpp-includes`` option.

The following command will collect the #includes statements from C/C++ files.::

  $ scancode --cpp-includes /path/to/codebase/ --json-pp ~/path/to/scan-output.json

Example Output
--------------

Here is an sample output::

    {
      "path": "zlib_deflate/deflate.c",
      "type": "file",
      "cpp_includes": [
        "<linux/module.h",
        "<linux/zutil.h",
        "\"defutil.h"
      ],
      "scan_errors": []
    },
    {
      "path": "zlib_deflate/deflate_syms.c",
      "type": "file",
      "cpp_includes": [
        "<linux/module.h",
        "<linux/init.h",
        "<linux/zlib.h"
      ],
      "scan_errors": []
    }
