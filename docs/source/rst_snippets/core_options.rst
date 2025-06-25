All "Core" Scan Options
-----------------------

-n, --processes INTEGER  Scan ``<input>`` using n parallel processes.
                         [Default: (number of CPUs)-1]

-v, --verbose            Print verbose file-by-file progress messages.

-q, --quiet              Do not print summary or progress messages.

--timeout FLOAT          Stop scanning a file if scanning takes longer
                         than a timeout in seconds.  [Default: 120]

--from-json              Load codebase from one or more existing JSON scans.

--max-in-memory INTEGER  Maximum number of files and directories scan
                         details kept in memory during a scan.
                         Additional files and directories scan details
                         above this number are cached on-disk rather
                         than in memory. Use 0 to use unlimited memory
                         and disable on-disk caching. Use -1 to use
                         only on-disk caching.  [Default: 10000]

--max-depth INTEGER      Descend at most INTEGER levels of directories
                         including and below the starting point. INTEGER
                         must be positive or zero for no limit.
                         [Default: 0]
