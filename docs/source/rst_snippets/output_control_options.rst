All "Output Control" Scan Options
---------------------------------

--strip-root           Strip the root directory segment of all paths.

--full-root            Report full, absolute paths.

.. include::  /scancode-toolkit/rst_snippets/note_snippets/control_strip_full_root.rst

--ignore-author <pattern>       Ignore a file (and all its findings)
                                if an author contains a match to the
                                ``<pattern>`` regular expression.

--ignore-copyright-holder <pattern>
                                Ignore a file (and all its findings)
                                if a copyright holder contains a match
                                to the ``<pattern>`` regular expression.

.. include::  /scancode-toolkit/rst_snippets/warning_snippets/control_ignore_author_copyright.rst

--only-findings                 Only return files or directories with
                                findings for the requested scans.
                                Files and directories without findings
                                are omitted (file information is not
                                treated as findings).
