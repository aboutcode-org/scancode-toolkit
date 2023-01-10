.. _cli_post_scan:

Post-Scan Options
=================

Post-Scan options activate their respective post-scan plugins which execute the task.

.. include:: /rst_snippets/post_scan_options.rst

----

.. include::  /rst_snippets/note_snippets/synopsis_install_quickstart.rst

To see all plugins available via command line help, use ``--plugins``.

.. include::  /rst_snippets/note_snippets/post_scan_plugins.rst

----

``--mark-source`` Option
------------------------

    .. admonition:: Dependency

        The option ``--mark-source`` is a sub-option of and **requires** the option ``--info``.

    The ``mark-source`` option marks the "is_source" attribute of a directory to be "True", if more
    than 90% of the files under that directory is source files, i.e. Their "is_source" attribute is
    "True".

    When the following command is executed to scan the ``samples`` directory with this option enabled::

        scancode -clpieu --json-pp output.json samples --mark-source

    Then, the following directories are marked as "Source", i.e. Their "is_source" attribute is changed
    from "false" to "True".

    - ``samples/JGroups/src``
    - ``samples/zlib/iostream2``
    - ``samples/zlib/gcc_gvmat64``
    - ``samples/zlib/ada``
    - ``samples/zlib/infback9``

----

``--consolidate`` Option
------------------------

    .. admonition:: Dependency

        The option ``--consolidate`` is a sub-option of and **requires** the options ``--license``
        , ``--copyright`` and ``--package``.

    .. note::

        The --consolidate option will be deprecated in a future version of
        scancode-toolkit as top level packages now provide a improved
        consolidated data.

    The JSON file containing scan results after using the ``--consolidate`` Plugin is structured as
    follows: (note: "..." in the image contains more data)

    An example Scan::

        scancode -clpieu --json-pp output.json samples --consolidate

    The JSON output file is structured as follows::

        {
          "headers": [
            {...}
          ],
          "consolidated_components": [
            {...
            },
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
          "consolidated_packages": [],
          "files": [
          ]
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

``--filter-clues`` Option
-------------------------

    The ``--filter-clues`` Plugin filters redundant duplicated clues already contained in detected
    licenses, copyright texts and notices.

    ..
        [ToDo] Resolve Error and then Add content
        [ERROR] Check https://github.com/nexB/scancode-toolkit/issues/1758

    .. WARNING::

        Running the following scan generates an error::

            ./scancode -clp --json-pp sample_filter_clues.json samples --filter-clues

----

``--is-license-text`` Option
----------------------------

    .. admonition:: Dependency

        The option ``--is-license-text`` is a sub-option of and requires the options
        ``--info`` and ``--license-text``.
        Also, the option ``--license-text`` is a sub-option of and requires the options
        ``--license``.

    If the ``--is-license-text`` is used, then the “is_license_text” flag is set to true for files that
    contain mostly license texts and notices. Here mostly means over 90% of the content of the file.

    An example Scan::

        scancode -clpieu --json-pp output.json samples --license-text --is-license-text

    If the samples directory is scanned with this plugin, the files containing mostly license texts
    will have the following attribute set to 'true'::

        "is_license_text": true,

    The files in samples that will have the "is_license_text" to be true are::

        samples/JGroups/EULA
        samples/JGroups/LICENSE
        samples/JGroups/licenses/apache-1.1.txt
        samples/JGroups/licenses/apache-2.0.txt
        samples/JGroups/licenses/bouncycastle.txt
        samples/JGroups/licenses/cpl-1.0.txt
        samples/JGroups/licenses/lgpl.txt
        samples/zlib/dotzlib/LICENSE_1_0.txt

    Note that the license objects for each detected license in the files already has "is_license_text"
    attributes by default, but not the file objects. They only have this attribute if the plugin is used.

    .. include:: /rst_snippets/warning_snippets/post_is_license_text.rst

----

``--license-clarity-score`` Option
----------------------------------

    .. admonition:: Dependency

        The option ``--license-clarity-score`` is a sub-option of and requires the option
        ``--classify``.

    The ``--license-clarity-score`` plugin when used in a scan, computes a summary license clarity
    score at the codebase level.

    An example Scan::

        scancode -clpieu --json-pp output.json samples --classify --license-clarity-score

    The "license_clarity_score" will have the following attributes:

    .. hlist::
        :columns: 3

        - "score"
        - "declared"
        - "discovered"
        - "consistency"
        - "spdx"
        - "license_texts"

    It whole JSON file is structured as follows, when it has "license_clarity_score"::

        {
          "headers": [
            { ...
            }
          ],
          "license_clarity_score": {
            "score": 17,
            "declared": false,
            "discovered": 0.69,
            "consistency": false,
            "spdx": false,
            "license_texts": false
          },
          "files": [
          ...
          ]
        }

    ..
        [ToDo] Research and Elaborate the attributes

----

``--license-policy FILE`` Option
--------------------------------

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

    .. include::  /rst_snippets/note_snippets/post_lic_pol_notsub.rst

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
          ...
          ...
          ...
          "licenses": [
          ...
          ...
          ...
          ],
          "license_expressions": [
            "apache-2.0"
          ],
          "copyrights": [],
          "holders": [],
          "authors": [],
          "packages": [],
          "emails": [],
          "license_policy": {
            "license_key": "apache-2.0",
            "label": "Approved License",
            "color_code": "#008000",
            "icon": "icon-ok-circle"
          },
          "urls": [],
          "files_count": 0,
          "dirs_count": 0,
          "size_count": 0,
          "scan_errors": []
        },

    More information on the :ref:`license_policy_plugin` and usage.

----

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
          "headers": [
            {
            ...
            }
          ],
          "summary": {
            "license_expressions": [ ...
            ],
            "copyrights": [ ...
            ],
            "holders": [ ...
            ],
            "authors": [ ...
            ],
            "programming_language": [ ...
            ],
            "packages": []
          },
          "files": [ ...
          ]
        }

    The Summary object has the following attributes.

    .. hlist::
        :columns: 3

        - "license_expressions"
        - "copyrights"
        - "holders"
        - "authors"
        - "programming_language"
        - "packages"

    Each attribute has multiple entries each containing "value" and "count", with their values having
    the summary information inside them.

    A sample summary object generated::

        "summary": {
        "license_expressions": [
          {
            "value": "zlib",
            "count": 13
          },
        ]
        ],
        "copyrights": [
          {
            "copyright": "Copyright (c) Mark Adler",
            "count": 4
          },
          {
            "copyright": "Copyright (c) Free Software Foundation, Inc.",
            "count": 2
          },
          {
            "copyright": "Copyright (c) The Apache Software Foundation",
            "count": 1
          },
          {
            "copyright": "Copyright Red Hat, Inc. and individual contributors",
            "count": 1
          }
        ],
        "holders": [
          {
            "holder": null,
            "count": 10
          },
          {
            "holder": "Mark Adler",
            "count": 4
          },
          {
            "holder": "Red Hat, Inc. and individual contributors",
            "count": 1
          },
          {
            "holder": "The Apache Software Foundation",
            "count": 1
          },
        ],
        "authors": [
          {
            "author": "Bela Ban",
            "count": 4
          },
          {
            "author": "Brian Stansberry",
            "count": 1
          },
          {
            "author": "the Apache Software Foundation (http://www.apache.org/)",
            "count": 1
          }
        ],
        "programming_language": [
          {
            "value": "C++",
            "count": 13
          },
          {
            "value": "Java",
            "count": 7
          },
        ],
        "packages": []

----

``--summary-by-facet`` Option
-----------------------------

    .. admonition:: Dependency

        The option ``--summary-by-facet`` is a sub-option of and requires the options ``--facet``
        and ``--summary``.

    Running the scan with ``--summary --summary-by-facet`` Plugins creates individual summaries for
    all the facets with the same license, copyright and other scan information, at a codebase level
    (in addition to the codebase level general summary generated by ``--summary`` Plugin)

    An example scan using the ``--summary-by-facet`` Plugin::

        scancode -clieu --json-pp output.json samples --summary --facet dev="*.java" --facet dev="*.c" --summary-by-facet

    .. include::  /rst_snippets/note_snippets/pre_facet_core.rst

    ..
        [ToDo] Remove this Warning when Issue solved.
        [ERROR] Issue at - https://github.com/nexB/scancode-toolkit/issues/1759

    .. WARNING::

        Running the same scan with ``./scancode -clpieu`` i.e. with ``-p`` generates an error.
        Avoid this.

    The JSON file containing scan results is structured as follows::

        {
          "headers": [ ...
          ],
          "summary": { ...
          },
          "summary_by_facet": [
            {
              "facet": "core",
              "summary": { ...
              }
            },
            {
              "facet": "dev",
              "summary": { ...
              }
            },
            {
              "facet": "tests",
              "summary": { ...
              }
            },
            {
              "facet": "docs",
              "summary": { ...
              }
            },
            {
              "facet": "data",
              "summary": { ...
              }
            },
            {
              "facet": "examples",
              "summary": { ...
              }
            }
          ],
          "files": [
        }

    A sample "summary_by_facet" object generated by the previous scan (shortened)::

        "summary_by_facet": [
          {
            "facet": "core",
            "summary": {
              "license_expressions": [
                {
                  "value": "mit",
                  "count": 1
                },
              ],
              "copyrights": [
                {
                  "value": "Copyright (c) Free Software Foundation, Inc.",
                  "count": 2
                },
              ],
              "holders": [
                {
                  "value": "The Apache Software Foundation",
                  "count": 1
                },
              "authors": [
                {
                  "value": "Gilles Vollant",
                  "count": 1
                },
              ],
              "programming_language": [
                {
                  "value": "C++",
                  "count": 8
                },
              ]
            }
          },
          {
            "facet": "dev",
            "summary": {
              "license_expressions": [
                {
                  "value": "zlib",
                  "count": 5
                },
              "copyrights": [
                {
                  "value": "Copyright Red Hat Middleware LLC, and individual contributors",
                  "count": 1
                },
              ],
              "holders": [
                {
                  "value": "Mark Adler",
                  "count": 3
                },
              ],
              "authors": [
                  "value": "Brian Stansberry",
                  "count": 1
                },
              ],
              "programming_language": [
                {
                  "value": "Java",
                  "count": 7
                },
                {
                  "value": "C++",
                  "count": 5
                }
              ]
            }
          },
        ],

    .. include::  /rst_snippets/note_snippets/post_summary_facet.rst

    For users who want to know :ref:`what_is_a_facet`.

----

``--summary-key-files`` Option
------------------------------

    .. admonition:: Dependency

        The option ``--summary-key-files`` is a sub-option of and requires the options
        ``--classify`` and ``--summary``.

    An example Scan::

        scancode -clpieu --json-pp output.json samples --classify --summary --summary-key-files

    Running the scan with ``--summary --summary-key-files`` Plugins creates summaries for key files
    with the same license, copyright and other scan information, at a codebase level (in addition
    to the codebase level general summary generated by ``--summary`` Plugin)

    The resulting JSON file containing the scan results is structured as follows::

        {
          "headers": [ ...
          ],
          "summary": {
            "license_expressions": [ ...
            ],
            "copyrights": [ ...
            ],
            "holders": [ ...
            ],
            "authors": [ ...
            ],
            "programming_language": [ ...
            ],
            "packages": []
          },
          "summary_of_key_files": {
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
          "files": [

    These following flags for each file/directory is also present (generated by ``--classify``)

    .. hlist::
        :columns: 3

        - "is_legal"
        - "is_manifest"
        - "is_readme"
        - "is_top_level"
        - "is_key_file"

----

``--summary-with-details`` Option
---------------------------------

    The ``--summary`` plugin summarizes license, copyright and other scan information at the
    codebase level. Now running the scan with the ``--summary-with-details`` plugin instead creates
    summaries at individual file/directories with the same license, copyright and other scan
    information, but at a file/directory level (in addition to the the codebase level summary).

    An example Scan::

        scancode -clpieu --json-pp output.json samples --summary-with-details

    .. include::  /rst_snippets/note_snippets/post_summary_details.rst

    A sample file object in the scan results (a directory level summary of ``samples/arch``) is
    structured as follows::

        {
          "path": "samples/arch",
          "type": "directory",
          "name": "arch",
          "base_name": "arch",
          "extension": "",
          "size": 0,
          "date": null,
          "sha1": null,
          "md5": null,
          "mime_type": null,
          "file_type": null,
          "programming_language": null,
          "is_binary": false,
          "is_text": false,
          "is_archive": false,
          "is_media": false,
          "is_source": false,
          "is_script": false,
          "licenses": [],
          "license_expressions": [],
          "copyrights": [],
          "holders": [],
          "authors": [],
          "packages": [],
          "emails": [],
          "urls": [],
          "is_legal": false,
          "is_manifest": false,
          "is_readme": false,
          "is_top_level": true,
          "is_key_file": false,
          "summary": {
            "license_expressions": [
              {
                "value": "zlib",
                "count": 3
              },
              {
                "value": null,
                "count": 1
              }
            ],
            "copyrights": [
              {
                "value": null,
                "count": 1
              },
              {
                "value": "Copyright (c) Jean-loup Gailly",
                "count": 1
              },
              {
                "value": "Copyright (c) Jean-loup Gailly and Mark Adler",
                "count": 1
              },
              {
                "value": "Copyright (c) Mark Adler",
                "count": 1
              }
            ],
            "holders": [
              {
                "value": null,
                "count": 1
              },
              {
                "value": "Jean-loup Gailly",
                "count": 1
              },
              {
                "value": "Jean-loup Gailly and Mark Adler",
                "count": 1
              },
              {
                "value": "Mark Adler",
                "count": 1
              }
            ],
            "authors": [
              {
                "value": null,
                "count": 4
              }
            ],
            "programming_language": [
              {
                "value": "C++",
                "count": 3
              },
              {
                "value": null,
                "count": 1
              }
            ]
          },
          "files_count": 4,
          "dirs_count": 2,
          "size_count": 127720,
          "scan_errors": []
        },

    These following flags for each file/directory is also present (generated by ``--classify``)

    .. hlist::
        :columns: 3

        - "is_legal"
        - "is_manifest"
        - "is_readme"
        - "is_top_level"
        - "is_key_file"
