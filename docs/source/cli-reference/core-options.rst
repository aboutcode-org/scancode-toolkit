`Core` Options
==============

.. _cli_core:

.. include::  /rst_snippets/core_options.rst

----

.. _quiet_verbose_options:

Comparing Progress Message Options
----------------------------------

    **Default Progress Message**::

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

    **Progress Message with ``--verbose``**::

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

    So, with ``--verbose`` enables, progress messages for individual files are shown.

    **With the ``--quiet`` option enabled**, nothing is printed on the Command Line.

----

.. _timeout_option:

``--timeout`` Option
--------------------

    This option sets scan timeout for **each file** (and not the entire scan). If some file scan
    exceeds the specified timeout, that file isn't scanned anymore and the next file scanning
    starts. This helps avoiding very large/long files, and saves time.

    Also the number (timeout in seconds) to be followed by this option can be a
    floating point number, i.e. 1.5467.

----

.. _from_json_option:

``--from-json`` Option
----------------------

    If you want to input scan results from a .json file, and run a scan again on those same files,
    with some other options/output format, you can do so using the ``--from-json`` option.

    An example scan command using ``--from-json``::

        scancode --from-json sample.json --json-pp sample_2.json --classify

    This inputs the scan results from ``sample.json``, runs the post-scan plugin ``--classify`` and
    outputs the results for this scan to ``sample_2.json``.

----

.. _max_in_memory_option:

``--max-in-memory`` Option
----------------------------------

    During a scan, as individual files are scanned, the scan details for those files are kept on
    memory till the scan is completed. Then after the scan is completed, they are written in the
    specified output format.

    Now, if the scan involves a very large number of files, they might not fit in the memory during
    the scan. For this reason, disk-caching can be used for some/all of the files.

    Some important INTEGER values of the ``--max-in-memory INTEGER`` option:

    - **0**     - Unlimited Memory, store all the file/directory scan results on memory
    - **-1**    - Use only Disk-Caching, store all the file/directory scan results on disk
    - **10000** - Default, store 10,000 file/directory scan results on memory and the rest on disk

    An example usage::

        scancode -clieu --json-pp sample.json samples --max-in-memory -1

----

.. _max_depth_option:

``--max_depth`` Option
----------------------------------

    Normally, the scan takes place upto the maximum level of nesting of directories possible. But
    using the ``--max-depth`` option, you can specify the maximum level of directories to scan,
    including and below the root location. This can reduce the time taken for the scan when deeper
    directories are not relevant.

    Note that the ``--max-depth`` option will be ignored if you are scanning from a JSON file using
    the ``--from-json`` option. In that case, the original depth is used.

    An example usage::

        scancode -clieu --json-pp results.json samples --max-depth 3

    This would scan the file ``samples/levelone/leveltwo/file`` but ignore
    ``samples/levelone/leveltwo/levelthree/file``
