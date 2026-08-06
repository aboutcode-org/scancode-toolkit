.. _cli-pre-scan-options:

Pre-scan options
================

Quick reference
---------------

.. include::  /rst-snippets/cli-pre-scan-options.rst
   :start-line: 3

----

.. _cli-facet-option:

``--facet <facet>=<pattern>``
-----------------------------

    .. admonition:: Sub-option

        The option ``--summary-by-facet`` is a sub-option of ``--facet``. ``--summary-by-facet`` is
        a post-scan option.

    Valid ``<facet>`` values are:

    - core,
    - dev,
    - tests,
    - docs,
    - data,
    - examples.

    You can use the ``--facet`` option in the following manner

    .. code-block:: none

        scancode -clpieu --json-pp sample_facet.json samples --facet dev="*.java" --facet dev="*.c"

    This adds to the header object, the following attribute

    .. code-block:: none

        "--facet": [
          "dev=*.java",
          "dev=*.c"
        ],

    Here in this example, ``.java`` and ``.c`` files are marked as it belongs to facet ``dev``.

    As a result, ``.java`` file has the following attribute added

    .. code-block:: json

          "facets": [
            "dev"
          ],

    .. include::  /rst-snippets/note-snippets/cli-pre-scan-facet-core.rst

    For each facet, the ``--facet`` option precedes the ``<facet>=<pattern>`` argument. For specifying
    multiple facets, this whole part is repeated, including the ``--facet`` option.

    See :ref:`facets` to learn more about what a facet is.
