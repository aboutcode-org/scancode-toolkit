All "Pre-Scan" Options
----------------------

--ignore <pattern>           Ignore files matching ``<pattern>``.

--include <pattern>          Include files matching ``<pattern>``.

--classify                   Classify files with flags telling if the
                             file is a legal, or readme or test file,
                             etc.

                             Sub-Options:

                             - ``--license-clarity-score``
                             - ``--summary-key-files``

--facet <facet_pattern>      Here ``<facet_pattern>`` represents
                             ``<facet>=<pattern>``. Add the ``<facet>``
                             to files with a path matching ``<pattern>``.

                             Sub-Options:

                             - ``--summary-by-facet``
