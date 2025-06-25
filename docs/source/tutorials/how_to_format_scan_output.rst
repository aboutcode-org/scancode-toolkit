.. _how_to_specify_output_format:

How to specify ScanCode Output Format
=====================================

A basic overview of formatting ScanCode Output is presented here.

More information on :ref:`cli_output_format`.

JSON
----

If you want JSON output of ScanCode results, you can pass the ``--json`` argument to ScanCode.
The following commands will output scan results in a formatted json file:

* ``scancode --json /path/to/output.json /path/to/target/dir``

* ``scancode --json-pp /path/to/output.json /path/to/target/dir``

* ``scancode --json-lines /path/to/output.json /path/to/target/dir``

To compare the JSON output in different formats refer :ref:`comparing_json`.

.. include::  /rst_snippets/stdout.rst


HTML
----

If you want HTML output of ScanCode results, you can pass the ``--html`` argument to ScanCode.
The following commands will output scan results in a formatted HTML page or simple web application:

* ``scancode --html /path/to/output.html /path/to/target/dir``

* ``scancode --html-app /path/to/output.html /path/to/target/dir``

For more details on the HTML output format refer :ref:`output_html`.

.. WARNING::

    The ``--html-app`` option has been deprecated, use ScanCode Workbench instead.

.. include::  /rst_snippets/custom_output_format.rst
