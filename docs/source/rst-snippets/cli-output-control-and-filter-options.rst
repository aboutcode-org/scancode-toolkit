**Controlling output and filters**
----------------------------------

--strip-root           Strip the root directory segment of all paths.

--full-root            Report full, absolute paths.

.. include::  /rst-snippets/note-snippets/cli-output-control-strip-full-root.rst

--ignore-author <pattern>       Ignore a file (and all its findings)
                                if an author contains a match to the
                                ``<pattern>`` regular expression.

--ignore-copyright-holder <pattern>
                                Ignore a file (and all its findings)
                                if a copyright holder contains a match
                                to the ``<pattern>`` regular expression.

.. include::  /rst-snippets/warning-snippets/cli-output-control-ignore-author-copyright.rst

--only-findings                 Only return files or directories with
                                findings for the requested scans.
                                Files and directories without findings
                                are omitted (file information is not
                                treated as findings).
