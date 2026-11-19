Using ScanCode from Python
=========================

ScanCode Toolkit is primarily designed to be used as a command-line tool.
At present, it does **not** expose a stable, documented public Python API
for invoking scans programmatically.

However, ScanCode can still be integrated into Python-based workflows by
invoking its command-line interface from Python code. ScanCode modules
can also be imported, though execution-related APIs are considered internal
and subject to change.

Installation
------------

ScanCode Toolkit must be installed with all optional dependencies:

.. code-block:: bash

    pip install scancode-toolkit[full]


Using ScanCode via subprocess
-----------------------------

The recommended way to execute a ScanCode scan from Python is by invoking
the ScanCode command-line interface using the ``subprocess`` module.

.. code-block:: python

    import subprocess

    subprocess.run(
        [
            "scancode",
            "--license",
            "--json-pp",
            "results.json",
            "/path/to/scan",
        ],
        check=True,
    )


Importing ScanCode modules
--------------------------

ScanCode modules can be imported in Python. This can be useful for accessing
internal utilities or for exploratory purposes, but these APIs are not
considered stable for running scans.

.. code-block:: python

    import scancode
    import scancode.api


Notes
-----

- ScanCode does not currently provide a public Python function to run scans
  directly.
- Internal APIs may change without notice and should not be relied upon for
  production integrations.
- For full scan configuration options, refer to the ScanCode command-line
  documentation.
