.. _cli_pre_scan:

Pre-Scan Options
================

.. include::  /rst_snippets/pre_scan_options.rst

----

``--ignore`` Option
-------------------

    In a scan, all files inside the directory specified as an input argument is scanned. But if
    there are some files which you don't want to scan, the ``--ignore`` option can be used to do
    the same.

    A sample usage::

        scancode --ignore "*.java" samples samples.json

    Here, ScanCode ignores files ending with `.java`, and continues with other files as usual.

    More information on :ref:`glob_pattern_matching`.

----

``--include`` Option
--------------------

    In a normal scan, all files inside the directory specified as an input argument is scanned. But
    if you want to run the scan on only some selective files, then ``--include`` option can be used
    to do the same.

    A sample usage::

        scancode --include "*.java" samples samples.json

    Here, ScanCode selectively scans files that has names ending with `.java`, and ignores all other files. This
    is basically complementary in behavior to the ``--ignore`` option.

    More information on :ref:`glob_pattern_matching`.

----

``--classify``
--------------

    .. admonition:: Sub-Option

        The options ``--license-clarity-score`` and ``--tallies-key-files`` are sub-options of
        ``--classify``. ``--license-clarity-score`` and ``--tallies-key-files`` are Post-Scan
        Options.

    The ``--classify`` option can be used like::

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

    As in, to the JSON object of each file scanned, these extra attributes are added::

      {
        "is_legal": false,
        "is_manifest": false,
        "is_readme": true,
        "is_top_level": true,
        "is_key_file": true
      }

----

``--facet`` Option
------------------

    .. admonition:: Sub-Option

        The option ``--summary-by-facet`` is a sub-option of ``--facet``. ``--summary-by-facet`` is
        a Post-Scan Option.

    Valid ``<facet>`` values are:

    - core,
    - dev,
    - tests,
    - docs,
    - data,
    - examples.

    You can use the ``--facet`` option in the following manner::

        scancode -clpieu --json-pp sample_facet.json samples --facet dev="*.java" --facet dev="*.c"

    This adds to the header object, the following attribute::

        "--facet": [
          "dev=*.java",
          "dev=*.c"
        ],

    Here in this example, ``.java`` and ``.c`` files are marked as it belongs to facet ``dev``.

    As a result, ``.java`` file has the following attribute added::

          "facets": [
            "dev"
          ],

    .. include::  /rst_snippets/note_snippets/pre_facet_core.rst

    For each facet, the ``--facet`` option precedes the ``<facet>=<pattern>`` argument. For specifying
    multiple facets, this whole part is repeated, including the ``--facet`` option.

    For users who want to know :ref:`what_is_a_facet`.

----

.. _glob_pattern_matching:

Glob Pattern Matching
---------------------

    All the Pre-Scan options use pattern matching, so the basics of Glob Pattern Matching is
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

    For more information on Glob pattern matching refer these resources:

        - `Linux Manual <http://man7.org/linux/man-pages/man7/glob.7.html>`_
        - `Wildcard Match Documentation <https://facelessuser.github.io/wcmatch/glob/>`_.

    You can also import these Python Libraries to practice UNIX style pattern matching:

    - `fnmatch <https://docs.python.org/2/library/fnmatch.html>`_ for File Name matching
    - `glob <https://docs.python.org/2/library/glob.html#module-glob>`_ for File Path matching

----

.. _what_is_a_facet:

What is a Facet?
----------------

    A facet is essentially a file purpose classification label.
    It is defined as follows (by ClearlyDefined):

    A facet of a component is a subset of the files related to the component. It's really just a
    grouping that helps us understand the shape of the project. Each facet is described by a set of
    glob expressions, essentially wildcard patterns that are matched against file names.

    Each facet definition can have zero or more glob expressions. A file can be captured by more
    than one facet. Any file found but not captured by a defined facet is automatically assigned to
    the core facet.

    - ``core`` - The files that go into making the release of the component. Note that the core
      facet is not explicitly defined. Rather, it is made up of whatever is not in any other facet.
      So, by default, all files are in the core facet unless otherwise specified.
    - ``data`` - The files included in any data distribution of the component.
    - ``dev`` - Files primarily used at development time (e.g., build utilities) and not
      distributed with the component
    - ``docs`` - Documentation files. Docs may be included with the executable component or
      separately or not at all.
    - ``examples`` -- Like docs, examples may be included in the main component release or
      separately.
    - ``tests`` -- Test files may include code, data and other artifacts.

    Important Links:

    - `Facets <https://github.com/clearlydefined/clearlydefined/blob/master/docs/clearly.md>`_
    - `ClearlyDefined <https://clearlydefined.io/about>`_
