All "Basic" Scan Options
------------------------

Option lists are two-column lists of command-line options and descriptions,
documenting a program's options. For example:

-c, --copyright              Scan ``<input>`` for copyrights.

                             Sub-Options:

                             - ``--consolidate``

-l, --license                Scan ``<input>`` for licenses.

                             Sub-Options:

                             - ``--license-references``
                             - ``--license-text``
                             - ``--license-text-diagnostics``
                             - ``--license-diagnostics``
                             - ``--license-url-template TEXT``
                             - ``--license-score INT``
                             - ``--license-clarity-score``
                             - ``--consolidate``
                             - ``--unknown-licenses``

-p, --package                Scan ``<input>`` for packages.

                             Sub-Options:

                             - ``--consolidate``

--system-package             Scan ``<input>`` for installed system package
                             databases.

--package-only               Scan ``<input>`` for system and application
                             only for package metadata, without license/
                             copyright detection and package assembly.

-e, --email                  Scan ``<input>`` for emails.

                             Sub-Options:

                             - ``--max-email INT``

-u, --url                    Scan ``<input>`` for urls.

                             Sub-Options:

                             - ``--max-url INT``

-i, --info                   Scan for and include information such as:

                             - Size,
                             - Type,
                             - Date,
                             - Programming language,
                             - sha1 and md5 hashes,
                             - binary/text/archive/media/source/script flags
                             - Additional options through more CLI options

                             Sub-Options:

                             - ``--mark-source``

.. include::  /rst_snippets/note_snippets/basic_clpieu.rst

--generated                  Classify automatically generated code files with a flag.

--max-email INT              Report only up to INT emails found in a
                             file. Use 0 for no limit.  [Default: 50]

                             Sub-Option of: ``--email``

--max-url INT                Report only up to INT urls found in a
                             file. Use 0 for no limit.  [Default: 50]

                             Sub-Option of: ``--url``

--license-score INTEGER

          Do not return license matches with scores lower than this score.
          A number between 0 and 100.  [Default: 0]
          Here, a bigger number means a better match, i.e. Setting a higher license score
          translates to a higher threshold (with equal or smaller number of matches).

          Sub-Option of: ``--license``

--license-text

          Include the matched text for the detected licenses in the output report.

          Sub-Option of: ``--license``

          Sub-Options:

          - ``--license-text-diagnostics``

--license-url-template TEXT

          Set the template URL used for the license reference URLs.

          In a template URL, curly braces ({}) are replaced by the license key.
          [Default: default: https://scancode-licensedb.aboutcode.org/{}]

          Sub-Option of: ``--license``

--license-text-diagnostics

          In the matched license text, include diagnostic highlights surrounding with
          square brackets [] words that are not matched.

          Sub-Option of: ``--license`` and ``--license-text``

--license-diagnostics

          In license detections, include diagnostic details to figure out the
          license detection post processing steps applied.

          Sub-Option of: ``--license``

--unknown-licenses

          [EXPERIMENTAL] Detect unknown licenses.

          Sub-Option of: ``--license``
