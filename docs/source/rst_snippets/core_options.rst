All "Core" Scan Options
-----------------------

-n, --processes INTEGER  Scan ``<input>`` using n parallel processes.
                         [Default: 1]

--verbose                Print verbose file-by-file progress messages.

--quiet                  Do not print summary or progress messages.

--timeout FLOAT          Stop scanning a file if scanning takes longer
                         than a timeout in seconds.  [Default: 120]

--reindex-licenses       Force a check and possible reindexing of the
                         cached license index.

--from-json              Load codebase from an existing JSON scan

--max-in-memory INTEGER  Maximum number of files and directories scan
                         details kept in memory during a scan.
                         Additional files and directories scan details
                         above this number are cached on-disk rather
                         than in memory. Use 0 to use unlimited memory
                         and disable on-disk caching. Use -1 to use
                         only on-disk caching.  [Default: 10000]

.. include:: /scancode-toolkit/rst_snippets/note_snippets/core_indep.rst
