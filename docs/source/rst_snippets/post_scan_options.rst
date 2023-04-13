All "Post-Scan" Options
-----------------------

--mark-source            Set the "is_source" flag to true for directories that
                         contain over 90% of source files as direct children
                         and descendants. Count the number of source files in a
                         directory as a new "source_file_counts" attribute

                         Sub-Option of: ``--url``

--consolidate            Group resources by Packages or license and
                         copyright holder and return those groupings
                         as a list of consolidated packages and a list
                         of consolidated components.
                         The --consolidate option will be deprecated in
                         a future version of scancode-toolkit as top level
                         packages now provide improved consolidated data.

                         Sub-Option of: ``--copyright``, ``--license`` and
                         ``--packages``.

--filter-clues           Filter redundant duplicated clues already
                         contained in detected licenses, copyright
                         texts and notices.

--license-clarity-score  Compute a summary license clarity score at
                         the codebase level.

                         Sub-Option of: ``--classify``.

--license-policy FILE    Load a License Policy file and apply it to
                         the scan at the Resource level.

--summary                Summarize scans by providing declared origin
                         information and other detected info at the
                         codebase attribute level.

--tallies                Summarize license, copyright and other scans
                         at the codebase level with occurrence counts.

                         Sub-Options:

                         - ``--tallies-by-facet``
                         - ``--tallies-key-files``
                         - ``--tallies-with-details``

--tallies-by-facet       Summarize license, copyright and other scans
                         and group the results by facet.

                         Sub-Option of: ``--tallies`` and ``--facet``.

--tallies-key-files      Summarize license, copyright and other scans
                         for key, top-level files, with occurrence counts.
                         Key files are top-level codebase files such as
                         COPYING, README and package manifests as reported
                         by the ``--classify`` option: "is_legal",
                         "is_readme", "is_manifest" and "is_top_level"
                         flags.

                         Sub-Option of: ``--classify`` and ``--summary``.

--tallies-with-details   Summarize license, copyright and other scans
                         at the codebase level with occurrence counts,
                         while also keeping intermediate details at
                         the file and directory level.
