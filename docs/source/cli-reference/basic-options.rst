`Basic` Options
===============

.. include::  /rst_snippets/basic_options.rst

----

.. _copyright_option:

``--copyright`` Option
-----------------------

    The ``--copyright`` option detects copyright statements in files.

    It adds the following resource-level attributes:

    1. ``copyrights``: This is a data mapping with the following attributes: ``copyright``
       containing the whole copyright value, with ``start_line`` and ``end_line`` containing
       the line numbers in the file where this copyright value was detected.

    2. ``holders``: This is a data mapping with the following attributes: ``holder``
       containing the whole copyright holder value, with ``start_line`` and ``end_line``
       containing the line numbers in the file where this copyright value was detected.

    3. ``authors``: This is a data mapping with the following attributes: ``author``
       containing the whole copyright author value, with ``start_line`` and ``end_line``
       containing the line numbers in the file where this copyright value was detected.

    Example::

        #
        # Copyright (c) 2010 Patrick McHardy All rights reserved.
        # Authors:     Patrick McHardy <kaber@trash.net>

    The above lines when scanned for copyrights generates the following results for the discussed attributes::

        {
            "copyrights": [
                {
                    "copyright": "Copyright (c) 2010 Patrick McHardy",
                    "start_line": 2,
                    "end_line": 2
                }
            ],
            "holders": [
                {
                    "holder": "Patrick McHardy",
                    "start_line": 2,
                    "end_line": 2
                }
            ],
            "authors": [
                {
                    "author": "Patrick McHardy <kaber@trash.net>",
                    "start_line": 3,
                    "end_line": 3
                }
            ],
        }

----

.. _license_option:

``--license`` Option
--------------------

    The ``--license`` option detects various kinds of license texts, notices, tags, references
    and other specialized license declarations like the SPDX license identifier in files.

    It adds the following attributes to the file data:

    1. ``license_detections``: This has a mapping of license detection data with the license
       expression, detection log and license matches. And the license matches contain the
       license expression for the match, score, more details for the license detected
       and the rule detected, along with the match text optionally.
    2. ``license_clues``: This is a list of license matches, same as ``matches`` in
       ``license_detections``. These are mere license clues and not perfect detections.
    3. ``detected_license_expression``: This is a scancode license expression string.
    4. ``detected_license_expression_spdx``: This is the SPDX version of
       ``detected_license_expression``.
    5. ``percentage_of_license_text``: This has a percentage number which denotes what percentage
       of the resource scanned has legalese words.

    Example::

        License: Apache-2.0

    If we run license detection (with ``--license-text``) on the above text we get the following
    result for the resource attributes added by the license detection::

        {
            "path": "apache-2.0.txt",
            "type": "file",
            "detected_license_expression": "apache-2.0",
            "detected_license_expression_spdx": "Apache-2.0",
            "license_detections": [
                {
                    "license_expression": "apache-2.0",
                    "matches": [
                        {
                            "score": 100.0,
                            "start_line": 1,
                            "end_line": 1,
                            "matched_length": 4,
                            "match_coverage": 100.0,
                            "matcher": "1-hash",
                            "license_expression": "apache-2.0",
                            "rule_identifier": "apache-2.0_65.RULE",
                            "rule_relevance": 100,
                            "rule_url": "https://github.com/aboutcode-org/scancode-toolkit/tree/develop/src/licensedcode/data/rules/apache-2.0_65.RULE",
                            "matched_text": "License: Apache-2.0"
                        }
                    ],
                    "identifier": "apache_2_0-ec759ae0-ea5a-f138-793e-388520e080c0"
                }
            ],
            "license_clues": [],
            "percentage_of_license_text": 100.0,
            "scan_errors": []
        }

    We also have top level unique license detections with the same identifier
    referencing all occurrences of this license detection and counts::

        {
            "license_detections": [
                {
                    "identifier": "apache_2_0-ec759ae0-ea5a-f138-793e-388520e080c0",
                    "license_expression": "apache-2.0",
                    "detection_count": 1
                }
            ]
        }


----

.. _package_option:

``--package`` Option
--------------------

    The ``--package`` option detects various package manifests, lockfiles and package-like
    data and then assembles codebase level packages and dependencies from these
    package data detected at files. Also tags files if they are part of the packages.

    It adds the following attributes to the file data:

    1. ``package_data``: This is a mapping of package data parsed and retrieved from
       the file, with the fields for the package URL, license detections, copyrights,
       dependencies, and the various URLs.

    2. ``for_packages``: This is a list of strings pointing to the packages that the
       files is a part of. The string is basically a packageURL with an UUID as a qualifier.

    It adds the following attributes to the top-level in results:

    1. ``packages``: This is a mapping of package data with all the atrributes
       present in file level ``package_data`` with the following extra attributes:
       ``package_uid``, ``datafile_paths`` and ``datasource_ids``.

    2. ``dependencies``: This is a mapping of dependency data from all the lockfiles
       or package manifests in the scan.

    Example:

    The following scan result was generated from scanning a package manifest::

        {
            "dependencies": [
                {
                    "purl": "pkg:bower/get-size",
                    "extracted_requirement": "~1.2.2",
                    "scope": "dependencies",
                    "is_runtime": true,
                    "is_optional": false,
                    "is_pinned": false,
                    "is_direct": true,
                    "resolved_package": {},
                    "extra_data": {},
                    "dependency_uid": "pkg:bower/get-size?uuid=fixed-uid-done-for-testing-5642512d1758",
                    "for_package_uid": "pkg:bower/blue-leaf?uuid=fixed-uid-done-for-testing-5642512d1758",
                    "datafile_path": "bower.json",
                    "datasource_id": "bower_json"
                }
            ],
            "packages": [
                {
                    "type": "bower",
                    "namespace": null,
                    "name": "blue-leaf",
                    "version": null,
                    "qualifiers": {},
                    "subpath": null,
                    "primary_language": null,
                    "description": "Physics-like animations for pretty particles",
                    "release_date": null,
                    "parties": [
                        {
                        "type": null,
                        "role": "author",
                        "name": "Betty Beta <bbeta@example.com>",
                        "email": null,
                        "url": null
                        }
                    ],
                    "keywords": [
                        "motion",
                        "physics",
                        "particles"
                    ],
                    "homepage_url": null,
                    "download_url": null,
                    "size": null,
                    "sha1": null,
                    "md5": null,
                    "sha256": null,
                    "sha512": null,
                    "bug_tracking_url": null,
                    "code_view_url": null,
                    "vcs_url": null,
                    "copyright": null,
                    "declared_license_expression": "mit",
                    "declared_license_expression_spdx": "MIT",
                    "license_detections": [
                        {
                            "license_expression": "mit",
                            "matches": [
                                {
                                    "score": 100.0,
                                    "start_line": 1,
                                    "end_line": 1,
                                    "matched_length": 1,
                                    "match_coverage": 100.0,
                                    "matcher": "1-spdx-id",
                                    "license_expression": "mit",
                                    "rule_identifier": "spdx-license-identifier: mit",
                                    "rule_url": null,
                                    "rule_relevance": 100,
                                    "matched_text": "MIT"
                                }
                            ],
                            "identifier": "apache_2_0-ec759abc-ea5a-2a38-793e-312340e080c0"
                        }
                    ],
                    "other_license_expression": null,
                    "other_license_expression_spdx": null,
                    "other_license_detections": [],
                    "extracted_license_statement": "MIT",
                    "notice_text": null,
                    "source_packages": [],
                    "extra_data": {},
                    "repository_homepage_url": null,
                    "repository_download_url": null,
                    "api_data_url": null,
                    "package_uid": "pkg:bower/blue-leaf?uuid=fixed-uid-done-for-testing-5642512d1758",
                    "datafile_paths": [
                        "bower.json"
                    ],
                    "datasource_ids": [
                        "bower_json"
                    ],
                    "purl": "pkg:bower/blue-leaf"
                }
            ],
            "files": [
                {
                    "path": "bower.json",
                    "type": "file",
                    "package_data": [
                        {
                            "type": "bower",
                            "namespace": null,
                            "name": "blue-leaf",
                            "version": null,
                            "qualifiers": {},
                            "subpath": null,
                            "primary_language": null,
                            "description": "Physics-like animations for pretty particles",
                            "release_date": null,
                            "parties": [
                                {
                                    "type": null,
                                    "role": "author",
                                    "name": "Betty Beta <bbeta@example.com>",
                                    "email": null,
                                    "url": null
                                }
                            ],
                            "keywords": [
                                "motion",
                                "physics",
                                "particles"
                            ],
                            "homepage_url": null,
                            "download_url": null,
                            "size": null,
                            "sha1": null,
                            "md5": null,
                            "sha256": null,
                            "sha512": null,
                            "bug_tracking_url": null,
                            "code_view_url": null,
                            "vcs_url": null,
                            "copyright": null,
                            "declared_license_expression": "mit",
                            "declared_license_expression_spdx": "MIT",
                            "license_detections": [
                                {
                                    "license_expression": "mit",
                                    "matches": [
                                        {
                                            "score": 100.0,
                                            "start_line": 1,
                                            "end_line": 1,
                                            "matched_length": 1,
                                            "match_coverage": 100.0,
                                            "matcher": "1-spdx-id",
                                            "license_expression": "mit",
                                            "rule_identifier": "spdx-license-identifier: mit",
                                            "rule_url": null,
                                            "rule_relevance": 100,
                                            "matched_text": "MIT"
                                        }
                                    ],
                                    "identifier": "apache_2_0-ec759abc-ea5a-2a38-793e-312340e080c0"
                                }
                            ],
                            "other_license_expression": null,
                            "other_license_expression_spdx": null,
                            "other_license_detections": [],
                            "extracted_license_statement": "MIT",
                            "notice_text": null,
                            "source_packages": [],
                            "file_references": [],
                            "extra_data": {},
                            "dependencies": [
                                {
                                    "purl": "pkg:bower/get-size",
                                    "extracted_requirement": "~1.2.2",
                                    "scope": "dependencies",
                                    "is_runtime": true,
                                    "is_optional": false,
                                    "is_pinned": false,
                                    "is_direct": true,
                                    "resolved_package": {},
                                    "extra_data": {}
                                }
                            ],
                            "repository_homepage_url": null,
                            "repository_download_url": null,
                            "api_data_url": null,
                            "datasource_id": "bower_json",
                            "purl": "pkg:bower/blue-leaf"
                        }
                    ],
                    "for_packages": [
                        "pkg:bower/blue-leaf?uuid=fixed-uid-done-for-testing-5642512d1758"
                    ],
                    "scan_errors": []
                }
            ]
        }

----

.. _info_option:

``--info`` Option
-----------------

    The ``--info`` option obtains miscellaneous information about the file being
    scanned such as mime/filetype, checksums, programming language, and various
    boolean flags.

    It adds the following attributes to the file data:

    1. ``date``: last modified data of the file.
    2. ``sha1``, ``md5`` and ``sha256``: file checksums of various algorithms.
    3. ``mime_type`` and ``file_type``: basic file type and mime type/subtype
       information obtained from libmagic.
    4. ``programming_language``: programming language based on extensions.
    5. ``is_binary``, ``is_text``, ``is_archive``, ``is_media``, ``is_source``,
       and ``is_script``: various boolean flags with misc. information about the file.

----

.. _email_option:

``--email`` Option
------------------

    The ``--email`` option detects and reports email adresses present in scanned files.

    It adds the ``emails`` attribute to the file data with the following attributes:
    ``email`` with the actual email that was present in the file, ``start_line`` and
    ``end_line`` to be able to locate where the email was detected in the file.

----

.. _url_option:

``--url`` Option
----------------

    The ``--url`` option detects and reports URLs present in scanned files.

    It adds the  ``urls`` attribute to the file data with the following attributes:
    ``url`` with the actual URL that was present in the file, ``start_line`` and
    ``end_line`` to be able to locate where the URL was detected in the file.


----

.. _generated_option:

``--generated`` Option
----------------------

    The ``--generated`` option classifies automatically generated code files with a flag.

    An example of using ``--generated`` in a scan::

        scancode -clpieu --json-pp output.json samples --generated

    In the results, for each file the following attribute is added with it's corresponding
    ``true``/``false`` value ::

        "is_generated": true

    Classification of a file being generated or not is done based on the first few lines
    having usually encountered generated keywords.

----

.. _max_email_option:

``--max-email`` Option
----------------------

    .. admonition:: Dependency

        The option ``--max-email`` is a sub-option of and requires the option ``--email``.

    If in the files that are scanned, in individual files, there are a lot of emails (i.e lists) which
    are unnecessary and clutter the scan results, ``--max-email`` option can be used to report emails
    only up to a limit in individual files.

    Some important INTEGER values of the ``--max-email INTEGER`` option:

    - 0  - No limit, include all emails.
    - 50 - Default.

    An example usage::

        scancode -clpieu --json-pp output.json samples --max-email 5

    This only reports 5 email addresses per file and ignores the rest.

----

.. _max_url_option:

``--max-url`` Option
--------------------

    .. admonition:: Dependency

        The option ``--max-url`` is a sub-option of and requires the option ``--url``.

    If in the files that are scanned, in individual files, there are a lot of links to other websites
    (i.e url lists) which are unnecessary and clutter the scan results, ``--max-url`` option can be
    used to report urls only up to a limit in individual files.

    Some important INTEGER values of the ``--max-url INTEGER`` option:

    - 0  - No limit, include all urls.
    - 50 - Default.

    An example usage::

        scancode -clpieu --json-pp output.json samples --max-url 10

    This only reports 10 urls per file and ignores the rest.

----

.. _license_score_option:

``--license-score`` Option
--------------------------

    .. admonition:: Dependency

        The option ``--license-score`` is a sub-option of and requires the option ``--license``.

    License matching strictness, i.e. How closely matched licenses are detected in a scan, can be
    modified by using this ``--license-score`` option.

    Some important INTEGER values of the ``--license-score INTEGER`` option:

    - **0**     - Default and Lowest Value, All matches are reported.
    - **100**    - Highest Value, Only licenses with a much better match are reported

    Here, a bigger number means a better match, i.e. Setting a higher license score translates to a
    higher threshold for matching licenses (with equal or less number of license matches).

    An example usage::

        scancode -clpieu --json-pp output.json samples --license-score 70

    Here's the license results on setting the integer value to 100, Vs. the default value 0. This is
    visualized using ScanCode workbench in the License Info Dashboard.

    .. list-table:: License scan results of Samples Directory.

        * - .. figure:: data/core_lic_score_0.png

               License Score 0 (Default).

          - .. figure:: data/core_lic_score_100.png

               License Score 100.

----

.. _license_text_option:

``--license-text`` Option
-------------------------

    .. admonition:: Dependency

        The option ``--license-text`` is a sub-option of and requires the option ``--license``.

    .. admonition:: Sub-Option

        The option ``--license-text-diagnostics`` is a sub-option of ``--license-text``.

    .. admonition:: Attention

        The option ``--license-text`` will not work with the ``--csv``
        output as outputting full license texts in a CSV file doesn't serve
        a practical purpose.

    With the ``--license-text`` option, the scan results attribute "matched text" includes the matched text
    for the detected license.

    An example Scan::

        scancode -cplieu --json-pp output.json samples --license-text

    An example matched text included in the results is as follows::

        "matched_text":
         "  This software is provided 'as-is', without any express or implied
         warranty.  In no event will the authors be held liable for any damages
         arising from the use of this software.
         Permission is granted to anyone to use this software for any purpose,
         including commercial applications, and to alter it and redistribute it
         freely, subject to the following restrictions:
         1. The origin of this software must not be misrepresented; you must not
         claim that you wrote the original software. If you use this software
         in a product, an acknowledgment in the product documentation would be
         appreciated but is not required.
         2. Altered source versions must be plainly marked as such, and must not be
         misrepresented as being the original software.
         3. This notice may not be removed or altered from any source distribution.

         Jean-loup Gailly        Mark Adler
         jloup@gzip.org          madler@alumni.caltech.edu"

    - The file in which this license was detected: ``samples/arch/zlib.tar.gz-extract/zlib-1.2.8/zlib.h``
    - License name: "ZLIB License"

----

.. _license_url_template_option:

``--license-url-template`` Option
---------------------------------

    .. admonition:: Dependency

        The option ``--license-url-template`` is a sub-option of and requires the option
        ``--license``.

    The ``--license-url-template`` option sets the template URL used for the license reference URLs.

    The default template URL is : [https://scancode-licensedb.aboutcode.org/{}]
    In a template URL, curly braces ({}) are replaced by the license key.

    So, by default the license reference URL points to the LicenseDB page for that license.

    A scan example using the ``--license-url-template TEXT`` option ::

        scancode -clpieu --json-pp output.json samples --license-url-template https://github.com/aboutcode-org/scancode-toolkit/tree/develop/src/licensedcode/data/licenses/{}.LICENSE

    In a normal scan, reference url for "ZLIB License" is as follows::

        "reference_url": "https://scancode-licensedb.aboutcode.org/zlib",

    After using the option in the following manner::

        ``--license-url-template https://github.com/aboutcode-org/scancode-toolkit/tree/develop/src/licensedcode/data/licenses/{}.LICENSE``

    the reference URL changes to this `zlib.LICENSE file <https://github.com/aboutcode-org/scancode-toolkit/blob/develop/src/licensedcode/data/licenses/zlib.LICENSE>`_::

        "reference_url": "https://github.com/aboutcode-org/scancode-toolkit/blob/develop/src/licensedcode/data/licenses/zlib.LICENSE",

    The reference URL changes for all detected licenses in the scan, across the scan result file.

----

.. _license_text_diagnostics_option:

``--license-text-diagnostics`` Option
-------------------------------------

    .. admonition:: Dependency

        The option ``--license-text-diagnostics`` is a sub-option of and requires the options
        ``--license`` and ``--license-text``.

    This adds a new attribute like the matched license text, but includes diagnostic highlights
    surrounding with square brackets ``[]`` for words that are not matched.

    In a normal scan, whole lines of text are included in the matched license text, including parts
    that are possibly unmatched.

    An example Scan::

        scancode -cplieu --json-pp output.json samples --license-text --license-text-diagnostics

    Running a scan on the samples directory with ``--license-text --license-text-diagnostics`` options,
    causes the following difference in the scan result of the file
    ``samples/JGroups/licenses/bouncycastle.txt``.

    Without Diagnostics::

        "matched_text":
        "License Copyright (c) 2000 - 2006 The Legion Of The Bouncy Castle
        (http://www.bouncycastle.org) Permission is hereby granted, free of charge, to any person
        obtaining a copy of this software and associated documentation files (the \"Software\"),
        to deal in the Software without restriction

    With Diagnostics on (new attribute with the matched text diagnostics)::

        "matched_text":
        "License Copyright (c) 2000 - 2006 The Legion Of The Bouncy Castle
        (http://www.bouncycastle.org) Permission is hereby granted, free of charge, to any person
        obtaining a copy of this software and associated documentation files (the \"Software\"),
        to deal in the Software without restriction
        "matched_text_diagnostics":
        "License [Copyright] ([c]) [2000] - [2006] [The] [Legion] [Of] [The] [Bouncy] [Castle]
        ([http]://[www].[bouncycastle].[org]) Permission is hereby granted, free of charge, to any person
        obtaining a copy of this software and associated documentation files (the \"Software\"),
        to deal in the Software without restriction,

----

.. _license_diagnostics_option:

``--license-diagnostics`` Option
-------------------------------------

    .. admonition:: Dependency

        The option ``--license-diagnostics`` is a sub-option of and requires the option
        ``--license``

    On using the ``--license-diagnostics`` option on a license scan there is the
    ``detection_log`` attribute added to license detections with diagnostics information
    about the license detection post-processing steps which are used to create license
    detections from license matches.

    Consider the following text::

        ## License
        All code, unless stated otherwise, is dual-licensed under
        [`WTFPL`](http://www.wtfpl.net/txt/copying/) and
        [`MIT`](https://opensource.org/licenses/MIT).

    If we run a license scan with the ``--license-diagnostics`` option enabled,
    we have the following license detection results::

        {
            "path": "README.md",
            "type": "file",
            "detected_license_expression": "wtfpl-2.0 AND mit",
            "detected_license_expression_spdx": "WTFPL AND MIT",
            "license_detections": [
                {
                    "license_expression": "wtfpl-2.0 AND mit",
                    "matches": [
                        {
                            "score": 100.0,
                            "start_line": 43,
                            "end_line": 43,
                            "matched_length": 3,
                            "match_coverage": 100.0,
                            "matcher": "2-aho",
                            "license_expression": "unknown-license-reference",
                            "rule_identifier": "lead-in_unknown_30.RULE",
                            "rule_relevance": 100,
                            "rule_url": "https://github.com/aboutcode-org/scancode-toolkit/tree/develop/src/licensedcode/data/rules/lead-in_unknown_30.RULE",
                            "matched_text": "dual-licensed under [`
                        },
                        {
                            "score": 50.0,
                            "start_line": 43,
                            "end_line": 43,
                            "matched_length": 1,
                            "match_coverage": 100.0,
                            "matcher": "2-aho",
                            "license_expression": "wtfpl-2.0",
                            "rule_identifier": "spdx_license_id_wtfpl_for_wtfpl-2.0.RULE",
                            "rule_relevance": 50,
                            "rule_url": "https://github.com/aboutcode-org/scancode-toolkit/tree/develop/src/licensedcode/data/rules/spdx_license_id_wtfpl_for_wtfpl-2.0.RULE",
                            "matched_text": "WTFPL"
                        },
                        {
                            "score": 100.0,
                            "start_line": 43,
                            "end_line": 43,
                            "matched_length": 3,
                            "match_coverage": 100.0,
                            "matcher": "2-aho",
                            "license_expression": "wtfpl-2.0",
                            "rule_identifier": "wtfpl-2.0_27.RULE",
                            "rule_relevance": 100,
                            "rule_url": "https://github.com/aboutcode-org/scancode-toolkit/tree/develop/src/licensedcode/data/rules/wtfpl-2.0_27.RULE",
                            "matched_text": "www.wtfpl.net/"
                        },
                        {
                            "score": 100.0,
                            "start_line": 43,
                            "end_line": 43,
                            "matched_length": 6,
                            "match_coverage": 100.0,
                            "matcher": "2-aho",
                            "license_expression": "mit",
                            "rule_identifier": "mit_64.RULE",
                            "rule_relevance": 100,
                            "rule_url": "https://github.com/aboutcode-org/scancode-toolkit/tree/develop/src/licensedcode/data/rules/mit_64.RULE",
                            "matched_text": "MIT`](https://opensource.org/licenses/MIT)."
                        }
                    ],
                    "detection_log": [
                        "unknown-intro-followed-by-match"
                    ],
                    "identifier": "wtfpl_2_0_and_mit-e5642b07-705c-9730-80ab-f5ed0565be28"
                }
            ],
            "license_clues": [],
            "percentage_of_license_text": 8.18,
            "scan_errors": []
        }

    Here from the ``"detection_log": ["unknown-intro-followed-by-match"]`` added diagnostics
    information we learn that there was an unknown intro license match, followed by
    proper detections, so we conclude the unknown intro to be an introduction to the
    following license and hence conclude the license from the license matches after the
    unknown detection.
