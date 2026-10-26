.. _cli-output-control-and-filter-options:

Controlling ScanCode output and filters
=======================================

Quick reference
---------------

.. include::  /rst-snippets/cli-output-control-and-filter-options.rst
   :start-line: 3

----

``--strip-root`` vs. ``--full-root``
------------------------------------

    For a default scan of the "samples" folder, this a comparison between the default,
    ``strip-root`` and ``full-root`` options.

    **Example**

    .. code-block:: shell

        scancode -cplieu --json-pp output.json samples --full-root

    These two changes only the "path" attribute of the file information. For this comparison we
    compare the "path" attributes of the file ``LICENSE`` inside ``JGroups`` directory.

    The default path

    .. code-block:: none

        "path": "samples/JGroups/LICENSE",

    For the ``--full-root`` option, the path relative to the Root of your local filesystem.

    .. code-block:: none

        "path": "/home/aboutcode/scancode-toolkit/samples/JGroups/LICENSE"


    For the ``--strip-root`` option, the root directory (here
    ``/home/aboutcode/scancode-toolkit/samples/``) is removed from path :

    .. code-block:: none

        "path": "JGroups/LICENSE"

    .. include::  /rst-snippets/note-snippets/cli-output-control-strip-full-root.rst

----

.. _ignore-author-option:

``--ignore-author <pattern>``
-----------------------------

    In a normal scan, all files inside the directory specified as an input argument is scanned and
    subsequently included in the scan report. But if you want to run the scan on only some selective
    files, with some specific **common author** then ``--ignore-author`` option can be used to do
    the same.

    This scan ignores all files with authors matching the string "Apache Software Foundation"

    .. code-block:: shell

        scancode -cplieu --json-pp output.json samples --ignore-author "Apache Software Foundation"

    More information on :ref:`glob-pattern-matching`.

    .. include::  /rst-snippets/warning-snippets/cli-output-control-ignore-author-copyright.rst

----

.. _ignore-copyright-holder-option:

``--ignore-copyright-holder <pattern>``
---------------------------------------

    In a normal scan, all files inside the directory specified as an input argument is scanned and
    subsequently included in the scan report. But if you want to run the scan on only some selective
    files, with some specific **common copyright holder** then ``--ignore-copyright-holder`` option
    can be used to do the same.

    This scan ignores all files with copyright holders matching
    the string "Free Software Foundation"

    .. code-block:: shell

        scancode -cplieu --json-pp output.json samples --ignore-copyright-holder "Free Software Foundation"

    More information on :ref:`glob-pattern-matching`.

----

.. _only-findings-option:

``--only-findings``
-------------------

    This option removes from the scan results, the files where nothing significant has been
    detected, like files which doesn't contain any licenses, copyrights, emails or urls (if
    requested in the scan options), and isn't a package.

    **Example**

    .. code-block:: shell

        scancode -cplieu --json-pp output.json samples --only-findings

    .. note::

        This also changes in the result displayed, the number of files scanned.

    For example, scanning the ``sample`` files (distributed by default with scancode-toolkit) without
    this option, displays in it's report information of 43 files. But after enabling this option, the
    result shows information for only 31 files.
