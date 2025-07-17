.. _cli_post_scan:

Post-Scan Options
=================

Post-Scan options activate their respective post-scan plugins which execute the task.

.. include:: /rst_snippets/post_scan_options.rst

To see all plugins available via command line help, use ``--plugins``.

.. include::  /rst_snippets/note_snippets/post_scan_plugins.rst

----

.. _mark_source_option:

``--mark-source`` Option
------------------------

    .. admonition:: Dependency

        The option ``--mark-source`` is a sub-option of and **requires** the option ``--info``.

    The ``mark-source`` option marks the ``is_source`` attribute of a directory to be ``True``, if more
    than 90% of the files under that directory is source files, and ``False`` otherwise.

    When the following command is executed to scan the ``samples`` directory with this option enabled::

        scancode -clpieu --json-pp output.json samples --mark-source

    Then, the following directories are marked as "Source", i.e. their ``is_source`` attribute is set
    to ``True``, as they contain mostly source code.

    - ``samples/JGroups/src``
    - ``samples/zlib/iostream2``
    - ``samples/zlib/gcc_gvmat64``
    - ``samples/zlib/ada``
    - ``samples/zlib/infback9``

----

.. _consolidate_option:

``--consolidate`` Option
------------------------

    .. admonition:: Dependency

        The option ``--consolidate`` is a sub-option of and **requires** the options ``--license``
        , ``--copyright`` and ``--package``.

    .. note::

        The ``--consolidate`` option will be deprecated in a future version of
        ScanCode-Toolkit as top level packages, dependencies and licenses
        now provide improved consolidated data.

    The JSON file containing scan results after using the ``--consolidate`` Plugin is structured as
    follows:

    An example Scan::

        scancode -clpieu --json-pp output.json samples --consolidate

    The JSON output file is structured as follows::

        {
          "headers": [...],
          "consolidated_components": [
            {
              "type": "license-holders",
              "identifier": "dmitriy_anisimkov_1",
              "consolidated_license_expression": "gpl-2.0-plus WITH ada-linking-exception",
              "consolidated_holders": [
                "Dmitriy Anisimkov"
              ],
              "consolidated_copyright": "Copyright (c) Dmitriy Anisimkov",
              "core_license_expression": "gpl-2.0-plus WITH ada-linking-exception",
              "core_holders": [
                "Dmitriy Anisimkov"
              ],
              "other_license_expression": null,
              "other_holders": [],
              "files_count": 1
            },
            {...
            }
          ],
          "consolidated_packages": [...],
          "files": [...]
        }

    Each consolidated component has the following information::

        "consolidated_components": [
        {
          "type": "license-holders",
          "identifier": "dmitriy_anisimkov_1",
          "consolidated_license_expression": "gpl-2.0-plus WITH ada-linking-exception",
          "consolidated_holders": [
            "Dmitriy Anisimkov"
          ],
          "consolidated_copyright": "Copyright (c) Dmitriy Anisimkov",
          "core_license_expression": "gpl-2.0-plus WITH ada-linking-exception",
          "core_holders": [
            "Dmitriy Anisimkov"
          ],
          "other_license_expression": null,
          "other_holders": [],
          "files_count": 1
        },

    In addition to this, in every file/directory where the consolidated part (i.e. License information)
    was present, a "consolidated_to" attribute is added pointing to the "identifier" of
    "consolidated_components"::

        "consolidated_to": [
            "dmitriy_anisimkov_1"
        ],

    Note that multiple files may have the same "consolidated_to" attribute.

----

.. _filter_clues_option:

``--filter-clues`` Option
-------------------------

    The ``--filter-clues`` Plugin filters redundant duplicated clues already contained in detected
    licenses, copyright texts and notices, authors.

    Consider the output of running the following scan (compared to running the scan without the
    ``--filter-clues`` option)::

        ./scancode -clpieu --json-pp sample_filter_clues.json samples --filter-clues

    When we run without the ``--filter-clues`` option, we have the following detections at
    ``"path": "samples/JGroups/src/FixedMembershipToken.java"``::

      {
        "authors": [
          {
            "author": "Chris Mills (millsy@jboss.com)",
            "start_line": 51,
            "end_line": 51
          }
        ],
        "emails": [
          {
            "email": "millsy@jboss.com",
            "start_line": 51,
            "end_line": 51
          }
        ]
      }

    And when we run a scan with the ``--filter-clues`` option::

      {
        "authors": [
          {
            "author": "Chris Mills (millsy@jboss.com)",
            "start_line": 51,
            "end_line": 51
          }
        ],
        "emails": []
      }

    Notice that when we run the scan with the ``--filter-clues`` option, we do not
    have the `millsy@jboss.com` in email detections as we already have it in
    author detections.

----

.. _license_clarity_score:

``--license-clarity-score`` Option
----------------------------------

    .. admonition:: Dependency

        The option ``--license-clarity-score`` is a sub-option of and requires the option
        ``--classify``.

    ..

      Keep this doc section in sync with docstrings at: ``src/summarycode/score.py::compute_license_score``

    The ``--license-clarity-score`` plugin when used in a scan, computes a
    summary license clarity score at the codebase level. The license clarity
    score is a value from 0-100 calculated by combining the weighted values
    determined for each of the scoring elements:

    Declared license:
      - When true, indicates that the software package licensing is documented at
        top-level or well-known locations in the software project, typically in a
        package manifest, NOTICE, LICENSE, COPYING or README file.
      - Scoring Weight = 40

    Identification precision:
      - Indicates how well the license statement(s) of the software identify known
        licenses that can be designated by precise keys (identifiers) as provided in
        a publicly available license list, such as the ScanCode LicenseDB, the SPDX
        license list, the OSI license list, or a URL pointing to a specific license
        text in a project or organization website.
      - Scoring Weight = 40

    License texts:
      - License texts are provided to support the declared license expression in
        files such as a package manifest, NOTICE, LICENSE, COPYING or README.
      - Scoring Weight = 10

    Declared copyright:
      - When true, indicates that the software package copyright is documented at
        top-level or well-known locations in the software project, typically in a
        package manifest, NOTICE, LICENSE, COPYING or README file.
      - Scoring Weight = 10

    Ambiguous compound licensing
      - When true, indicates that the software has a license declaration that
        makes it difficult to construct a reliable license expression, such as in
        the case of multiple licenses where the conjunctive versus disjunctive
        relationship is not well defined.
      - Scoring Weight = -10

    Conflicting license categories
      - When true, indicates the declared license expression of the software is in
        the permissive category, but that other potentially conflicting categories,
        such as copyleft and proprietary, have been detected in lower level code.
      - Scoring Weight = -20

    An example Scan::

        scancode -clpieu --json-pp output.json samples --classify --license-clarity-score

    The "license_clarity_score" will have the following attributes:

    .. hlist::
        :columns: 3

        - "score"
        - "declared_license"
        - "identification_precision
        - "has_license_text"
        - "declared_copyrights"
        - "conflicting_license_categories"
        - "ambiguous_compound_licensing"

    When the "license_clarity_score" is included, the entire JSON file is structured as follows::

        {
          "headers": [...],
          "summary": {
            "declared_license_expression": "mit",
            "license_clarity_score": {
              "score": 100,
              "declared_license": true,
              "identification_precision": true,
              "has_license_text": true,
              "declared_copyrights": true,
              "conflicting_license_categories": false,
              "ambiguous_compound_licensing": false
            }
          },
          "files": [...]
        }

    .. include:: /rst_snippets/note_snippets/post_license_clarity_score.rst

----

.. _license_policy_option:

``--license-policy FILE`` Option
--------------------------------

    .. include:: /rst_snippets/note_snippets/post_license_policy.rst

    The Policy file is a YAML (.yml) document with the following structure::

        license_policies:
        -   license_key: mit
            label: Approved License
            color_code: '#00800'
            icon: icon-ok-circle
        -   license_key: agpl-3.0
            label: Approved License
            color_code: '#008000'
            icon: icon-ok-circle


    .. include::  /rst_snippets/note_snippets/post_lic_pol_key.rst

    Applying License Policies during a ScanCode scan, using the ``--license-policy`` Plugin::

        scancode -clipeu --json-pp output.json samples --license-policy policy-file.yml

    This adds to every file/directory an object "license_policy", having as further attributes under it
    the fields as specified in the .YAML file. Here according to our example .YAML file, the attributes
    will be:

    .. hlist::
        :columns: 4

        - "license_key"
        - "label"
        - "color_code"
        - "icon"

    Here the ``samples`` directory is scanned, and the Scan Results for a sample file is as follows::

        {
          "path": "samples/JGroups/licenses/apache-2.0.txt",
          "license_detections": [
            "license_expression": "apache-2.0",
            "matches": {...}
            "identifier": "apache_2_0-9804422e-94ac-ad40-b53a-ee6f8ddb7a3b"
          ],
          "detected_license_expression": "apache-2.0",
          "detected_license_expression_spdx": "Apache-2.0",
          "license_policy": {
            "license_key": "apache-2.0",
            "label": "Approved License",
            "color_code": "#008000",
            "icon": "icon-ok-circle"
          },
          ...
        },

    More information on the :ref:`license_policy_plugin` and usage.

----

.. _license_references_option:

``--license-references`` Option
-------------------------------

    .. admonition:: Dependency

        The option ``--license-references`` is a sub-option of and requires the option
        ``--license``.

    Details about the matched license or license rule are not included with the license
    matches for license detections by default. These are instead reported optionally and
    separately as codebase-level reference data. There are two codebase-level attributes
    added with the ``--license-references`` option:

    - ``license_references`` with details from scancode licenses (which are each a
      ``.LICENSE`` file)
    - ``license_rule_references`` with details from scancode license rules
      (which are each a ``.RULE`` file)

    Consider a file ``mit.txt`` with the following license declaration::

      License: mit

    We run the following scan on this file::

      scancode -l --license-text --license-references mit.txt --json-pp mit.json

    See the results for this license scan with ``--license-references`` enabled::

      {
        "headers": [...],
        "license_detections": [
          {
            "identifier": "mit-3fce6ea2-8abd-6c6b-3ede-a37af7c6efee",
            "license_expression": "mit",
            "detection_count": 1
          }
        ],
        "license_references": [
          {
            "key": "mit",
            "language": "en",
            "short_name": "MIT License",
            "name": "MIT License",
            "category": "Permissive",
            "owner": "MIT",
            "homepage_url": "http://opensource.org/licenses/mit-license.php",
            "notes": "Per SPDX.org, this license is OSI certified.",
            "is_builtin": true,
            "is_exception": false,
            "is_unknown": false,
            "is_generic": false,
            "spdx_license_key": "MIT",
            "other_spdx_license_keys": [],
            "osi_license_key": null,
            "text_urls": [
              "http://opensource.org/licenses/mit-license.php"
            ],
            "osi_url": "http://www.opensource.org/licenses/MIT",
            "faq_url": "https://ieeexplore.ieee.org/document/9263265",
            "other_urls": [
              "https://opensource.com/article/18/3/patent-grant-mit-license",
              "https://opensource.com/article/19/4/history-mit-license",
              "https://opensource.org/licenses/MIT"
            ],
            "key_aliases": [],
            "minimum_coverage": 0,
            "standard_notice": null,
            "ignorable_copyrights": [],
            "ignorable_holders": [],
            "ignorable_authors": [],
            "ignorable_urls": [],
            "ignorable_emails": [],
            "text": "Permission is hereby granted, free of charge, to any person obtaining\na copy of this software and associated documentation files (the\n\"Software\"), to deal in the Software without restriction, including\nwithout limitation the rights to use, copy, modify, merge, publish,\ndistribute, sublicense, and/or sell copies of the Software, and to\npermit persons to whom the Software is furnished to do so, subject to\nthe following conditions:\n\nThe above copyright notice and this permission notice shall be\nincluded in all copies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND,\nEXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF\nMERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.\nIN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY\nCLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,\nTORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE\nSOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.",
            "scancode_url": "https://github.com/aboutcode-org/scancode-toolkit/tree/develop/src/licensedcode/data/licenses/mit.LICENSE",
            "licensedb_url": "https://scancode-licensedb.aboutcode.org/mit",
            "spdx_url": "https://spdx.org/licenses/MIT"
          }
        ],
        "license_rule_references": [
          {
            "license_expression": "mit",
            "identifier": "mit_30.RULE",
            "language": "en",
            "rule_url": "https://github.com/aboutcode-org/scancode-toolkit/tree/develop/src/licensedcode/data/rules/mit_30.RULE",
            "is_license_text": false,
            "is_license_notice": false,
            "is_license_reference": false,
            "is_license_tag": true,
            "is_license_intro": false,
            "is_continuous": false,
            "is_builtin": true,
            "is_from_license": false,
            "is_synthetic": false,
            "length": 2,
            "relevance": 100,
            "minimum_coverage": 100,
            "referenced_filenames": [],
            "notes": null,
            "ignorable_copyrights": [],
            "ignorable_holders": [],
            "ignorable_authors": [],
            "ignorable_urls": [],
            "ignorable_emails": [],
            "text": "License: MIT"
          }
        ],
        "files": [
          {
            "path": "mit.txt",
            "type": "file",
            "detected_license_expression": "mit",
            "detected_license_expression_spdx": "MIT",
            "license_detections": [
              {
                "license_expression": "mit",
                "matches": [
                  {
                    "score": 100.0,
                    "start_line": 1,
                    "end_line": 1,
                    "matched_length": 2,
                    "match_coverage": 100.0,
                    "matcher": "1-hash",
                    "license_expression": "mit",
                    "rule_identifier": "mit_30.RULE",
                    "rule_relevance": 100,
                    "rule_url": "https://github.com/aboutcode-org/scancode-toolkit/tree/develop/src/licensedcode/data/rules/mit_30.RULE",
                    "matched_text": "License: mit"
                  }
                ],
                "identifier": "mit-3fce6ea2-8abd-6c6b-3ede-a37af7c6efee"
              }
            ],
            "license_clues": [],
            "percentage_of_license_text": 100.0,
            "scan_errors": []
          }
        ]
      }

    See :ref:`reference_license_related_data` for more details on license references
    and a comparison with previous scancode output formats.

----

.. _summary_option:

``--summary`` Option
--------------------

    .. admonition:: Sub-Option

        The option ``--summary-by-facet``, ``--summary-key-files`` and
        ``--summary-with-details``are sub-options of ``--summary``. These Sub-Options are all
        Post-Scan Options.

    An example Scan::

        scancode -clpieu --json-pp output.json samples --summary

    The whole JSON file is structured as follows, when the ``--summary`` plugin is applied::

        {
          "headers": [...],
          "summary": {
            "declared_license_expression": null,
            "license_clarity_score": {...},
            "declared_holder": "",
            "primary_language": "C",
            "other_license_expressions": [...],
            "other_holders": [...]
            "other_languages": [...]
          },
          "files": [...]
        }

    Each attribute in ``other_license_expressions``, ``other_holders``, ``other_languages``
    has multiple entries each containing "value" and "count", with their values having
    the summary information inside them.

    See below a sample fully populated summary object::

      {
        "summary": {
        "declared_license_expression": "commercial-license AND other-permissive AND mit",
        "license_clarity_score": {
          "score": 100,
          "declared_license": true,
          "identification_precision": true,
          "has_license_text": true,
          "declared_copyrights": true,
          "conflicting_license_categories": false,
          "ambiguous_compound_licensing": false
        },
        "declared_holder": "Strapi Solutions SAS",
        "primary_language": "JavaScript",
        "other_license_expressions": [
          {
            "value": "commercial-license AND other-permissive AND mit",
            "count": 65
          },
          {
            "value": "mit",
            "count": 7
          },
          {
            "value": null,
            "count": 1
          },
          {
            "value": "apache-2.0",
            "count": 1
          },
          {
            "value": "generic-cla",
            "count": 1
          }
        ],
        "other_holders": [
          {
            "value": null,
            "count": 3572
          },
          {
            "value": "Jon Schlinkert",
            "count": 2
          }
        ],
        "other_languages": [
          {
            "value": "TypeScript",
            "count": 91
          },
          {
            "value": "GAS",
            "count": 28
          },
          {
            "value": "HTML",
            "count": 6
          },
          {
            "value": "Bash",
            "count": 5
          },
          {
            "value": "verilog",
            "count": 1
          }
        ]
      }

----

.. _tallies_option:

``--tallies`` Option
--------------------

    .. admonition:: Optional Dependency

        The ``--tallies`` option does not have any required CLI option dependencies,
        but as it contains license, copyright, holder, author, packages and
        programming language information, it is recommended to use this option with
        ``--license``, ``--package``, ``--copyright`` and ``--info`` options enabled,
        or there will not be any corresponding data for these.

    An example scan using the ``--tallies`` Plugin::

        scancode -clipeu --json-pp strapi.json strapi-main/ --tallies

    .. note:

      We have used the `github:strapi/strapi <https://github.com/strapi/strapi>`_ project to generate exmaple results for
      this and all associated CLI options below.

    The JSON file containing the ``--tallies`` scan results are as follows::

      {
        "headers": [...],
        "packages": [...],
        "dependencies": [...],
        "license_detections": [...],
        "tallies": {
          "detected_license_expression": [
            {
              "value": "commercial-license AND other-permissive AND mit",
              "count": 65
            },
            {
              "value": "mit",
              "count": 7
            },
            {
              "value": null,
              "count": 1
            },
            {
              "value": "apache-2.0",
              "count": 1
            },
            {
              "value": "generic-cla",
              "count": 1
            }
          ],
          "copyrights": [
            {
              "value": null,
              "count": 3572
            },
            {
              "value": "Copyright (c) Strapi Solutions SAS",
              "count": 31
            },
            {
              "value": "Copyright (c) Jon Schlinkert",
              "count": 2
            }
          ],
          "holders": [
            {
              "value": null,
              "count": 3572
            },
            {
              "value": "Strapi Solutions SAS",
              "count": 31
            },
            {
              "value": "Jon Schlinkert",
              "count": 2
            }
          ],
          "authors": [
            {
              "value": null,
              "count": 3567
            },
            {
              "value": "name' Strapi Solutions",
              "count": 30
            },
            {
              "value": "the community",
              "count": 4
            },
            {
              "value": "name' A Strapi developer",
              "count": 3
            },
            {
              "value": "name A Strapi",
              "count": 1
            },
            {
              "value": "name' Yurii Tykhomyrov",
              "count": 1
            }
          ],
          "programming_language": [
            {
              "value": "JavaScript",
              "count": 2854
            },
            {
              "value": "TypeScript",
              "count": 91
            },
            {
              "value": "GAS",
              "count": 28
            },
            {
              "value": "HTML",
              "count": 6
            },
            {
              "value": "Bash",
              "count": 5
            },
            {
              "value": "verilog",
              "count": 1
            }
          ],
          "packages": [...]
        },
        "files": [...]
      }

    This adds a top-level "tallius" attribute and the sub-attributes will be:

    .. hlist::
        :columns: 6

        - "detected_license_expression"
        - "copyrights"
        - "holders"
        - "authors"
        - "programming_language"
        - "packages"

    These are all lists with the corresponding "value" and their respective "count",
    basically tallies of all different values.

----

.. _tallies_by_facet_option:

``--tallies-by-facet`` Option
-----------------------------

    .. admonition:: Dependency

        The option ``--tallies-by-facet`` is a sub-option of and requires the options ``--facet``
        and ``--tallies``.

    For users who want to know :ref:`what_is_a_facet`.

    Running the scan with ``--tallies --tallies-by-facet`` Plugins creates individual summaries for
    all the facets with the same license, copyright and other scan information, at a codebase level
    (in addition to the codebase level general summary generated by ``--tallies`` Plugin).
    Once all files have been assigned a facet, files without a facet are assigned to
    the core facet.

    An example scan using the ``--tallies-by-facet`` Plugin::

        scancode -clipeu --json-pp strapi.json strapi-main/ --tallies --facet dev="*.js" --facet dev="*.ts" --tallies-by-facet

    We have used the `github:strapi/strapi <https://github.com/strapi/strapi>`_ project to generate exmaple results for
    this CLI option.

    .. include::  /rst_snippets/note_snippets/pre_facet_core.rst

    A sample "summary_by_facet" object generated by the previous scan (shortened)::

      {
        "headers": [...],
        "packages": [...],
        "dependencies": [...],
        "license_detections": [...],
        "tallies": {...}
        "tallies_by_facet": [
          {
            "facet": "core",
            "tallies": {
              "detected_license_expression": [
                {
                  "value": "commercial-license AND other-permissive AND mit",
                  "count": 65
                },
                {
                  "value": "mit",
                  "count": 5
                },
                {
                  "value": "generic-cla",
                  "count": 1
                }
              ],
              "copyrights": [
                {
                  "value": "Copyright (c) Strapi Solutions SAS",
                  "count": 31
                }
              ],
              "holders": [
                {
                  "value": "Strapi Solutions SAS",
                  "count": 31
                }
              ],
              "authors": [
                {
                  "value": "name' Strapi Solutions",
                  "count": 30
                },
                {
                  "value": "name' A Strapi developer",
                  "count": 3
                },
                {
                  "value": "name' Yurii Tykhomyrov",
                  "count": 1
                },
                {
                  "value": "the community",
                  "count": 1
                }
              ],
              "programming_language": [
                {
                  "value": "GAS",
                  "count": 28
                },
                {
                  "value": "TypeScript",
                  "count": 7
                },
                {
                  "value": "HTML",
                  "count": 6
                },
                {
                  "value": "Bash",
                  "count": 5
                },
                {
                  "value": "verilog",
                  "count": 1
                }
              ]
            }
          },
          {
            "facet": "dev",
            "tallies": {
              "detected_license_expression": [
                {
                  "value": "mit",
                  "count": 2
                },
                {
                  "value": "apache-2.0",
                  "count": 1
                }
              ],
              "copyrights": [
                {
                  "value": "Copyright (c) Jon Schlinkert",
                  "count": 2
                }
              ],
              "holders": [
                {
                  "value": "Jon Schlinkert",
                  "count": 2
                }
              ],
              "authors": [
                {
                  "value": "the community",
                  "count": 3
                },
                {
                  "value": "name A Strapi",
                  "count": 1
                }
              ],
              "programming_language": [
                {
                  "value": "JavaScript",
                  "count": 2854
                },
                {
                  "value": "TypeScript",
                  "count": 84
                }
              ]
            }
          },
          {
            "facet": "tests",
            "tallies": {
              "detected_license_expression": [],
              "copyrights": [],
              "holders": [],
              "authors": [],
              "programming_language": []
            }
          },
          {
            "facet": "docs",
            "tallies": {
              "detected_license_expression": [],
              "copyrights": [],
              "holders": [],
              "authors": [],
              "programming_language": []
            }
          },
          {
            "facet": "data",
            "tallies": {
              "detected_license_expression": [],
              "copyrights": [],
              "holders": [],
              "authors": [],
              "programming_language": []
            }
          },
          {
            "facet": "examples",
            "tallies": {
              "detected_license_expression": [],
              "copyrights": [],
              "holders": [],
              "authors": [],
              "programming_language": []
            }
          }
        ],
        "files": [...]
      }


    .. include::  /rst_snippets/note_snippets/post_summary_facet.rst

----

.. _tallies_key_files_option:

``--tallies-key-files`` Option
------------------------------

    .. admonition:: Dependency

        The option ``--tallies-key-files`` is a sub-option of and requires the options
        ``--classify`` and ``--tallies``.

    An example Scan::

        scancode -clipeu --json-pp strapi.json strapi-main/ --classify --tallies --tallies-key-files

    Running the scan with ``--tallies --tallies-key-files`` plugins creates summaries for key files
    with the same license, copyright and other scan information, at a codebase level (in addition
    to the codebase level general summary generated by ``--tallies`` Plugin).

    The resulting JSON file containing the scan results is structured as follows::

      {
        "headers": [...],
        "packages": [...],
        "dependencies": [...],
        "license_detections": [...],
        "tallies": {...},
        "tallies_of_key_files": {
          "license_expressions": [
            {
              "value": null,
              "count": 1
            }
          ],
          "copyrights": [
            {
              "value": null,
              "count": 1
            }
          ],
          "holders": [
            {
              "value": null,
              "count": 1
            }
          ],
          "authors": [
            {
              "value": null,
              "count": 1
            }
          ],
          "programming_language": [
            {
              "value": null,
              "count": 1
            }
          ]
        },
        "files": [...]
      }

    These following flags for each file/directory is also present (generated by ``--classify``)

    .. hlist::
        :columns: 3

        - "is_legal"
        - "is_manifest"
        - "is_readme"
        - "is_top_level"
        - "is_key_file"

    A key-file is a top-level file, that is either a legal (LICENSE/COPYING etc), manifest or a
    readme file.

----

.. _tallies_with_details_option:

``--tallies-with-details`` Option
---------------------------------

    The ``--tallies`` plugin summarizes license, copyright and other scan information at the
    codebase level. Now running the scan with the ``--tallies-with-details`` plugin instead creates
    summaries at individual file/directories with the same license, copyright and other scan
    information, but at a file/directory level (in addition to the the codebase level summary).

    An example Scan::

        scancode -clipeu --json-pp strapi.json strapi-main/ --tallies-with-details

    .. include::  /rst_snippets/note_snippets/post_summary_details.rst

    A sample scan result is structured as follows::

      {
        "headers": [...],
        "packages": [...],
        "dependencies": [...],
        "license_detections": [...],
        "tallies": {...},
        "files": [
          {
            "path": "strapi-main",
            "type": "directory",
            "name": "strapi-main",
            "base_name": "strapi-main",
            "extension": "",
            "size": 0,
            "date": null,
            "sha1": null,
            "md5": null,
            "sha256": null,
            "sha1_git": null,
            "mime_type": null,
            "file_type": null,
            "programming_language": null,
            "is_binary": false,
            "is_text": false,
            "is_archive": false,
            "is_media": false,
            "is_source": false,
            "is_script": false,
            "package_data": [],
            "for_packages": [],
            "detected_license_expression": null,
            "detected_license_expression_spdx": null,
            "license_detections": [],
            "license_clues": [],
            "percentage_of_license_text": 0,
            "copyrights": [],
            "holders": [],
            "authors": [],
            "emails": [],
            "urls": [],
            "facets": [],
            "is_legal": false,
            "is_manifest": false,
            "is_readme": false,
            "is_top_level": true,
            "is_key_file": false,
            "tallies": {
              "detected_license_expression": [
                {
                  "value": "commercial-license AND other-permissive AND mit",
                  "count": 65
                },
                {
                  "value": "mit",
                  "count": 7
                },
                {
                  "value": null,
                  "count": 1
                },
                {
                  "value": "apache-2.0",
                  "count": 1
                },
                {
                  "value": "generic-cla",
                  "count": 1
                }
              ],
              "copyrights": [
                {
                  "value": null,
                  "count": 3572
                },
                {
                  "value": "Copyright (c) Strapi Solutions SAS",
                  "count": 31
                },
                {
                  "value": "Copyright (c) Jon Schlinkert",
                  "count": 2
                }
              ],
              "holders": [
                {
                  "value": null,
                  "count": 3572
                },
                {
                  "value": "Strapi Solutions SAS",
                  "count": 31
                },
                {
                  "value": "Jon Schlinkert",
                  "count": 2
                }
              ],
              "authors": [
                {
                  "value": null,
                  "count": 3567
                },
                {
                  "value": "name' Strapi Solutions",
                  "count": 30
                },
                {
                  "value": "the community",
                  "count": 4
                },
                {
                  "value": "name' A Strapi developer",
                  "count": 3
                },
                {
                  "value": "name A Strapi",
                  "count": 1
                },
                {
                  "value": "name' Yurii Tykhomyrov",
                  "count": 1
                }
              ],
              "programming_language": [
                {
                  "value": "JavaScript",
                  "count": 2854
                },
                {
                  "value": "TypeScript",
                  "count": 91
                },
                {
                  "value": "GAS",
                  "count": 28
                },
                {
                  "value": "HTML",
                  "count": 6
                },
                {
                  "value": "Bash",
                  "count": 5
                },
                {
                  "value": "verilog",
                  "count": 1
                }
              ]
            },
            "files_count": 3604,
            "dirs_count": 1603,
            "size_count": 15175739,
            "scan_errors": []
          },
          {...}
        ]
      }
