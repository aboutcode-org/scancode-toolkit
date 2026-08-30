.. _cli-core-options:

`Core` options
==============

Quick reference
---------------

.. include::  /rst-snippets/cli-core-options.rst
   :start-line: 3

----

.. _cli-quiet-verbose-options:

Comparing progress message options
----------------------------------

    **Default progress message**

    By default a rolling progress bar and scanned file count is shown.

    .. code-block:: none

        Scanning files for: infos, licenses, copyrights, packages, emails, urls with 1 process(es)...
        Building license detection index...Done.
        Scanning files...
        [####################] 43
        Scanning done.
        Scan statistics: 43 files scanned in 33s.
        Scan options:    infos, licenses, copyrights, packages, emails, urls with 1 process(es).
        Scanning speed:  1.4 files per sec.
        Scanning time:   30s.
        Indexing time:   2s.
        Saving results.

    **Progress message with --verbose**

    When ``--verbose`` is enabled, progress messages for individual files are shown.

    .. code-block:: none

        Scanning files for: infos, licenses, copyrights, packages, emails, urls with 1 process(es)...
        Building license detection index...Done.
        Scanning files...
        Scanned: screenshot.png
        Scanned: README
        ...
        Scanned: zlib/dotzlib/ChecksumImpl.cs
        Scanned: zlib/dotzlib/readme.txt
        Scanned: zlib/gcc_gvmat64/gvmat64.S
        Scanned: zlib/ada/zlib.ads
        Scanned: zlib/infback9/infback9.c
        Scanned: zlib/infback9/infback9.h
        Scanned: arch/zlib.tar.gz
        Scanning done.
        Scan statistics: 43 files scanned in 29s.
        Scan options:    infos, licenses, copyrights, packages, emails, urls with 1 process(es).
        Scanning speed:  1.58 files per sec.
        Scanning time:   27s.
        Indexing time:   2s.
        Saving results.

    **With the ``--quiet`` option enabled**, nothing is printed on the command line.

----

.. _cli-timeout-option:

``--timeout``
-------------

    This option sets scan timeout for **each file** (and not the entire scan). If some file scan
    exceeds the specified timeout, that file isn't scanned anymore and the next file scanning
    starts. This helps avoiding very large/long files, and saves time.

    Also the number (timeout in seconds) to be followed by this option can be a
    floating point number, i.e. 1.5467.

----

.. _cli-from-json-option:

``--from-json``
---------------

    If you want to input scan results from a .json file, and run a scan again on those same files,
    with some other options/output format, you can do so using the ``--from-json`` option.

    **Example**

    .. code-block:: shell

        scancode --from-json sample.json --json-pp sample_2.json --classify

    This inputs the scan results from ``sample.json``, runs the post-scan plugin ``--classify`` and
    outputs the results for this scan to ``sample_2.json``.

----

.. _cli-max-in-memory-option:

``--max-in-memory INT``
-----------------------

    During a scan, as individual files are scanned, the scan details for those files are kept on
    memory till the scan is completed. Then after the scan is completed, they are written in the
    specified output format.

    Now, if the scan involves a very large number of files, they might not fit in the memory during
    the scan. For this reason, disk-caching can be used for some/all of the files.

    Some important INTEGER values of the ``--max-in-memory INTEGER`` option:

    - **0**     - Unlimited ,emory, store all the file/directory scan results on memory
    - **-1**    - Use only disk-caching, store all the file/directory scan results on disk
    - **10000** - Default, store 10,000 file/directory scan results on memory and the rest on disk

    **Example**

    .. code-block:: shell

        scancode -clieu --json-pp sample.json samples --max-in-memory -1

----

.. _cli-max-depth-option:

``--max_depth INT``
-------------------

    Normally, the scan takes place up to the maximum level of nesting of directories possible. But
    using the ``--max-depth`` option, you can specify the maximum level of directories to scan,
    including and below the root location. This can reduce the time taken for the scan when deeper
    directories are not relevant.

    Note that the ``--max-depth`` option will be ignored if you are scanning from a JSON file using
    the ``--from-json`` option. In that case, the original depth is used.

    **Example**

    .. code-block:: shell

        scancode -clieu --json-pp results.json samples --max-depth 3

    This would scan the file ``samples/levelone/leveltwo/file`` but ignore
    ``samples/levelone/leveltwo/levelthree/file``

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

.. _cli-config-option:

``--config-file <path>``
------------------------

    Path patterns which should be ignored in the scan can also be provided
    through a configuration file.

    **Example**

    .. code-block:: shell

        scancode --config-file scancode-config.yaml samples samples.json

    .. code-block:: yaml

        ignored_patterns:
        - '*.java'
        - '*/licenses/*'

    Here, ScanCode ignores files ending with `.java` and the `licenses` directory,
    and continues with other files as usual.

    This is also compatible with the `scancode.io configuration file <https://scancodeio.readthedocs.io/en/latest/project-configuration.html#ignored-patterns>`_.

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

