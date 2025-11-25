.. _run_as_library:

Run as Library
==============

If you’ve installed ScanCode-Toolkit as a library (:ref:`pip_install`), you
can directly import it into your Python scripts.

ScanCode-Toolkit offers a wide range of callable functions. Each function
includes in-code documentation. Users can refer to it to understand the
purpose of each function, then import and use the ones they need.

While listing them all isn't feasible, here are a few sample use cases.

To Run a Scan
-------------

::

    from scancode.cli import run_scan


See https://github.com/aboutcode-org/scancode-toolkit/blob/develop/src/scancode/cli.py#L535


Get YAML Safe Text
------------------

::

    from licensedcode.models import get_yaml_safe_text


See https://github.com/aboutcode-org/scancode-toolkit/blob/develop/src/licensedcode/models.py#L777


.. NOTE::

    For more sample usages, refer https://github.com/nexB/scancode.io/blob/main/scanpipe/pipes/scancode.py
