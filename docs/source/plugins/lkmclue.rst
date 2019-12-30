.. _lkmclue_plugin:

LKMClue Plugin
==============

This plugin allows users to collect LKM module clues and type indicating a
possible Linux Kernel Module.

Using the Plugin
----------------

User needs to use the ``--lkmclue`` option.

The following command will collect the LKM module clues from the input location::

  $ scancode --lkmclue /path/to/codebase/ --json-pp ~/path/to/scan-output.json

Example Output
--------------

Here is an sample output::

    {
      "path": "zlib_deflate/deflate.c",
      "type": "file",
      "lkm_clue": {
        "lkm-header-include": [
          "include <linux/module.h>"
        ]
      },
      "scan_errors": []
    },
    {
      "path": "zlib_deflate/deflate_syms.c",
      "type": "file",
      "lkm_clue": {
        "lkm-header-include": [
          "include <linux/module.h>"
        ],
        "lkm-license": [
          "GPL"
        ]
      },
      "scan_errors": []
    }
