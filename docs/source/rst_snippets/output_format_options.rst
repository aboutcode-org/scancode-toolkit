All Scan Output Options
-----------------------

--json FILE             Write scan output as compact JSON to FILE.

--json-pp FILE          Write scan output as pretty-printed JSON to
                        FILE. This is one of the recommended output
                        formats and contains all the data scancode
                        can show along with the YAML output format.

--json-lines FILE       Write scan output as JSON Lines to FILE.

--yaml FILE             Write scan output as YAML to FILE.
                        This is one of the recommended output
                        formats and contains all the data scancode
                        can show along with the JSON output format.

--csv FILE              DEPRECATED: Write scan output as CSV to FILE.
                        This option is deprecated and will be replaced by
                        new CSV and tabular output formats in the next
                        ScanCode release. Visit this issue for details,
                        and to provide input and feedback:
                        https://github.com/aboutcode-org/scancode-toolkit/issues/3043

--html FILE             Write scan output as HTML to FILE.

--custom-output         Write scan output to FILE formatted with the
                        custom Jinja template file.

                        Mandatory Sub-option:

                        - ``--custom-template FILE``

--custom-template FILE  Use this Jinja template FILE as a custom
                        template.

                        Sub-Option of: ``--custom-output``

--debian FILE           Write scan output in machine-readable Debian copyright
                        format to FILE.

--spdx-rdf FILE         Write scan output as SPDX RDF to FILE.

--spdx-tv FILE          Write scan output as SPDX Tag/Value to FILE.

--html-app FILE         [DEPRECATED] Use ``scancode-workbench``
                        instead. Write scan output as a mini HTML
                        application to FILE.

--cyclonedx FILE        Write scan output as a CycloneDx 1.3 BOM
                        in pretty-printed JSON format to FILE

--cyclonedx-xml FILE    Write scan output as a CycloneDx 1.3 BOM
                        in pretty-printed XML format to FILE

.. include::  /rst_snippets/warning_snippets/output_htmlapp_dep.rst
