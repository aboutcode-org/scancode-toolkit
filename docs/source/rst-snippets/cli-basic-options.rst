**Basic options**
-----------------

Option lists are two-column lists of command-line options and descriptions,
documenting a program's options. For example:

-c, --copyright              Scan ``<input>`` for copyrights.

                             Sub-options:

                             - ``--consolidate``

-l, --license                Scan ``<input>`` for licenses.

                             Sub-options:

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

                             Sub-options:

                             - ``--consolidate``

--system-package             Scan ``<input>`` for installed system package
                             databases.

--package-in-compiled        Scan compiled executable binaries such as ELF,
                             WinpE and Mach-O files, looking for structured
                             package and dependency metadata. Note that looking for
                             packages in binaries makes package scan slower.
                             Currently supported compiled binaries: Go, Rust.

--package-only               Faster package scan, scanning ``<input>`` for
                             system and application packages, only for package
                             metadata. This option is skipping
                             - license and copyright detection for package metadata
                             - package assembly

-e, --email                  Scan ``<input>`` for emails.

                             Sub-options:

                             - ``--max-email INT``

-u, --url                    Scan ``<input>`` for urls.

                             Sub-options:

                             - ``--max-url INT``

-i, --info                   Scan for and include information such as:

                             - Size,
                             - Type,
                             - Date,
                             - Programming language,
                             - sha1 and md5 hashes,
                             - binary/text/archive/media/source/script flags
                             - Additional options through more CLI options

                             Sub-options:

                             - ``--mark-source``

.. include::  /rst-snippets/note-snippets/cli-basic-options-clpieu.rst

--generated                  Classify automatically generated code files with a flag.

--max-email INT              Report only up to INT emails found in a
                             file. Use 0 for no limit.

                             Default: ``50``

                             Sub-option of: ``--email``

--max-url INT                Report only up to INT urls found in a
                             file. Use 0 for no limit.

                             Default: ``50``

                             Sub-option of: ``--url``

--license-score INTEGER

          Do not return license matches with scores lower than this score.
          A number between 0 and 100.

          Default: ``0`` (i.e. we return all license matches by default).

          Here, a bigger number means a better match, i.e. Setting a higher license score
          translates to a higher threshold (with equal or smaller number of matches).

          Sub-option of: ``--license``

--license-text

          Include the matched text for the detected licenses in the output report.

          Sub-option of: ``--license``

          Sub-options:

          - ``--license-text-diagnostics``

--license-url-template TEXT

          Set the template URL used for the license reference URLs.

          In a template URL, curly braces ({}) are replaced by the license key.

          Default: ``https://scancode-licensedb.aboutcode.org/{}``

          Sub-option of: ``--license``

--license-text-diagnostics

          In the matched license text, include diagnostic highlights surrounding with
          square brackets [] words that are not matched.

          Sub-option of: ``--license`` and ``--license-text``

--license-diagnostics

          In license detections, include diagnostic details to figure out the
          license detection post processing steps applied.

          Sub-option of: ``--license``

--unknown-licenses

          [EXPERIMENTAL] Detect unknown licenses.

          Sub-option of: ``--license``
