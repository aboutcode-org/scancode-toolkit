.. _cli-pre-scan-options:

Pre-scan options
================

Quick reference
---------------

.. include::  /rst-snippets/cli-pre-scan-options.rst
   :start-line: 3

----

.. _cli-ignore-option:

``--ignore <pattern>``
----------------------

    In a scan, all files inside the directory specified as an input argument is scanned. But if
    there are some files which you don't want to scan, the ``--ignore`` option can be used to do
    the same.

    **Example**

    .. code-block:: shell

        scancode --ignore "*.java" samples samples.json

    Here, ScanCode ignores files ending with `.java`, and continues with other files as usual.

    More information on :ref:`glob-pattern-matching`.

----

.. _cli-include-option:

``--include <pattern>``
-----------------------

    In a normal scan, all files inside the directory specified as an input argument is scanned. But
    if you want to run the scan on only some selective files, then ``--include`` option can be used
    to do the same.

    **Example**

    .. code-block:: shell

        scancode --include "*.java" samples samples.json

    Here, ScanCode selectively scans files that has names ending with `.java`, and ignores all other files. This
    is basically complementary in behavior to the ``--ignore`` option.

    See also :ref:`glob-pattern-matching`.

----

.. _cli-classify-option:

``--classify``
--------------

    .. admonition:: Sub-option

        The options ``--license-clarity-score`` and ``--tallies-key-files`` are sub-options of
        ``--classify``. ``--license-clarity-score`` and ``--tallies-key-files`` are Post-Scan
        Options.

    **Example**

    .. code-block:: shell

        scancode -clpieu --json-pp sample_facet.json samples --classify

    This option makes ScanCode further classify scanned files/directories, to determine whether they
    fall in these following categories

    - legal
    - readme
    - top-level
    - manifest

        A manifest file in computing is a file containing metadata for a group of accompanying
        files that are part of a set or coherent unit.

    - key-file

        A KEY file serves as a keystone element, containing essential
        information about a software package — such as its dependencies,
        versioning, licensing, and more. It often contains the
        ``primary-license`` or the overall license of the package, among
        other package metadata which are general or ecosystem specific.

    As in, to the JSON object of each file scanned, these extra attributes are added.

    .. code-block:: json

      {
        "is_legal": false,
        "is_manifest": false,
        "is_readme": true,
        "is_top_level": true,
        "is_key_file": true
      }

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

----

.. _glob-pattern-matching:

Glob Pattern Matching
---------------------

    All the pre-scan options use pattern matching, so the basics of Glob Pattern Matching is
    discussed briefly below.

    Glob pattern matching is useful for matching a group of files, by using patterns in their
    names. Then using these patterns, files are grouped and treated differently as required.

    Here are some rules from the `Linux Manual <http://man7.org/linux/man-pages/man7/glob.7.html>`_
    on glob patterns. Refer the same for more detailed information.

    A string is a wildcard pattern if it contains one of the characters '?', '*' or '['.  Globbing
    is the operation that expands a wildcard pattern into the list of pathnames matching the
    pattern. Matching is defined by:

    - A '?' (not between brackets) matches any single character.

    - A '*' (not between brackets) matches any string, including the empty string.

    - An expression "[...]" where the first character after the leading '[' is not an '!' matches a
      single character, namely any of the characters enclosed by the brackets.

    - There is one special convention: two characters separated by '-' denote a range.

    - An expression "[!...]" matches a single character, namely any character that is not matched
      by the expression obtained by removing the first '!' from it.

    - A '/' in a pathname cannot be matched by a '?' or '*' wildcard, or by a range like "[.-0]".

    Note that wildcard patterns are not regular expressions, although they are a bit similar.

    For more information on glob pattern matching refer these resources:

        - `Linux Manual <http://man7.org/linux/man-pages/man7/glob.7.html>`_
        - `Wildcard Match Documentation <https://facelessuser.github.io/wcmatch/glob/>`_.

    You can also import these Python Libraries to practice UNIX style pattern matching:

    - `fnmatch <https://docs.python.org/2/library/fnmatch.html>`_ for File Name matching
    - `glob <https://docs.python.org/2/library/glob.html#module-glob>`_ for File Path matching

