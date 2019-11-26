All Scan Output Options
-----------------------

--json FILE             Write scan output as compact JSON to FILE.

--json-pp FILE          Write scan output as pretty-printed JSON to
                        FILE.

--json-lines FILE       Write scan output as JSON Lines to FILE.

--csv FILE              Write scan output as CSV to FILE.

--html FILE             Write scan output as HTML to FILE.

--custom-output         Write scan output to FILE formatted with the
                        custom Jinja template file.

                        Mandatory Sub-option:

                        - ``--custom-template FILE``

--custom-template FILE  Use this Jinja template FILE as a custom
                        template.

                        Sub-Option of: ``--custom-output``

--spdx-rdf FILE         Write scan output as SPDX RDF to FILE.

--spdx-tv FILE          Write scan output as SPDX Tag/Value to FILE.

--html-app FILE         Write scan output as a mini HTML
                        application to FILE.

.. include::  /scancode-toolkit/rst_snippets/warning_snippets/output_htmlapp_dep.rst
