.. _configuring-scan-detection:

Configuring what will be detected in scan
=========================================

ScanCode allows you to scan a codebase for license, copyright and other interesting information
that can be discovered in files. The following options are available for detection when using
ScanCode-Toolkit:

.. include::  /rst-snippets/cli-basic-options.rst

Different Scans
---------------

The following examples will use the ``samples`` directory that is provided with the `ScanCode
Toolkit code <https://github.com/aboutcode-org/scancode-toolkit/tree/develop/samples>`_. All examples will
be saved in the JSON format, which can be loaded into ScanCode Workbench for visualization. See
:ref:`visualizing-scan-results` for more information. Another output format option is a
static html file. See :ref:`cli-output-format-options` for more information.

Scan for all clues:
^^^^^^^^^^^^^^^^^^^

To scan for licenses, copyrights, urls, emails, package information, and file information

.. code-block:: shell

   scancode -clipeu --json output.json samples


Scan for license and copyright clues:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

   scancode -cl --json-pp output.json samples


Scan for emails and URLs:
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

   scancode -eu --json-pp output.json samples


Scan for package information:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

   scancode -p --json-pp output.json samples


Scan for file information:
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

   scancode -i --json-pp output.json samples


To see more example scans:
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

   scancode --examples

For more information, refer :ref:`cli-scancode`.
