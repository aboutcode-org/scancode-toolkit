.. _configuring-scan-output-formats:

Configuring scan output formats
===============================

A basic overview of formatting ScanCode output is presented here.

More information on :ref:`cli-output-format-options`.

JSON
----

If you want JSON output of ScanCode results, you can pass the ``--json`` argument to ScanCode.
The following commands will output scan results in a formatted json file:

* ``scancode --json /path/to/output.json /path/to/target/dir``

* ``scancode --json-pp /path/to/output.json /path/to/target/dir``

* ``scancode --json-lines /path/to/output.json /path/to/target/dir``

To compare the JSON output in different formats refer :ref:`cli-comparing-json-output-file-formats`.

.. include::  /rst-snippets/cli-output-to-stdout.rst


HTML
----

If you want HTML output of ScanCode results, you can pass the ``--html`` argument to ScanCode.
The following commands will output scan results in a formatted HTML page or simple web application:

* ``scancode --html /path/to/output.html /path/to/target/dir``

* ``scancode --html-app /path/to/output.html /path/to/target/dir``

For more details on the HTML output format refer :ref:`cli-html-option`.

.. WARNING::

    The ``--html-app`` option has been deprecated, use ScanCode Workbench instead.

.. include::  /rst-snippets/cli-output-custom-format.rst
