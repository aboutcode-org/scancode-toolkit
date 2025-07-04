.. _how_to_set_what_scan_detects:

How to set what will be detected in Scan
========================================

ScanCode allows you to scan a codebase for license, copyright and other interesting information
that can be discovered in files. The following options are available for detection when using
ScanCode-Toolkit:

.. include::  /rst_snippets/basic_options.rst

Different Scans
---------------

The following examples will use the ``samples`` directory that is provided with the `ScanCode
Toolkit code <https://github.com/aboutcode-org/scancode-toolkit/tree/develop/samples>`_. All examples will
be saved in the JSON format, which can be loaded into ScanCode Workbench for visualization. See
:ref:`how_to_visualize_scan_results` for more information. Another output format option is a
static html file. See :ref:`cli_output_format` for more information.

Scan for all clues:
^^^^^^^^^^^^^^^^^^^

To scan for licenses, copyrights, urls, emails, package information, and file information

::

   scancode -clipeu --json output.json samples


Scan for license and copyright clues:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

   scancode -cl --json-pp output.json samples


Scan for emails and URLs:
^^^^^^^^^^^^^^^^^^^^^^^^^

::

   scancode -eu --json-pp output.json samples


Scan for package information:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

   scancode -p --json-pp output.json samples


Scan for file information:
^^^^^^^^^^^^^^^^^^^^^^^^^^

::

   scancode -i --json-pp output.json samples


To see more example scans:
^^^^^^^^^^^^^^^^^^^^^^^^^^

::

   scancode --examples

For more information, refer :ref:`cli_list_options`.
