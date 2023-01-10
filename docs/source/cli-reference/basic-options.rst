`Basic` Options
===============

.. include::  /rst_snippets/basic_options.rst

----

.. include::  /rst_snippets/note_snippets/synopsis_install_quickstart.rst

----

``--copyright`` Option
-----------------------

    The ``--copyright`` option detects copyright statements in files.

    It adds the following file attributes:

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
                "start_line": 11,
                "end_line": 11
                }
            ],
        }

----

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

    If we run license detection (with --license-text) on the above text we get the following
    result for the attributes added by the license detection::

        {
            "detected_license_expression": "apache-2.0",
            "detected_license_expression_spdx": "Apache-2.0",
            "license_detections": [
                {
                    "license_expression": "apache-2.0",
                    "detection_log": [
                        "not-combined"
                    ],
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
                            "rule_url": "https://github.com/nexB/scancode-toolkit/tree/develop/src/licensedcode/data/rules/apache-2.0_65.RULE",
                            "referenced_filenames": [],
                            "is_license_text": false,
                            "is_license_notice": false,
                            "is_license_reference": false,
                            "is_license_tag": true,
                            "is_license_intro": false,
                            "rule_length": 4,
                            "rule_relevance": 100,
                            "matched_text": "License: Apache-2.0",
                            "licenses": [
                                {
                                    "key": "apache-2.0",
                                    "name": "Apache License 2.0",
                                    "short_name": "Apache 2.0",
                                    "category": "Permissive",
                                    "is_exception": false,
                                    "is_unknown": false,
                                    "owner": "Apache Software Foundation",
                                    "homepage_url": "http://www.apache.org/licenses/",
                                    "text_url": "http://www.apache.org/licenses/LICENSE-2.0",
                                    "reference_url": "https://scancode-licensedb.aboutcode.org/apache-2.0",
                                    "scancode_url": "https://github.com/nexB/scancode-toolkit/tree/develop/src/licensedcode/data/licenses/apache-2.0.LICENSE",
                                    "spdx_license_key": "Apache-2.0",
                                    "spdx_url": "https://spdx.org/licenses/Apache-2.0"
                                }
                            ]
                        }
                    ]
                }
            ],
            "license_clues": [],
            "percentage_of_license_text": 100.0,
        }

----

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
                    "is_resolved": false,
                    "resolved_package": {},
                    "extra_data": {},
                    "dependency_uid": "pkg:bower/get-size?uuid=fixed-uid-done-for-testing-5642512d1758",
                    "for_package_uid": "pkg:bower/blue-leaf?uuid=fixed-uid-done-for-testing-5642512d1758",
                    "datafile_path": "bower.json",
                    "datasource_id": "bower_json"
                },
                {
                    "purl": "pkg:bower/eventEmitter",
                    "extracted_requirement": "~4.2.11",
                    "scope": "dependencies",
                    "is_runtime": true,
                    "is_optional": false,
                    "is_resolved": false,
                    "resolved_package": {},
                    "extra_data": {},
                    "dependency_uid": "pkg:bower/eventEmitter?uuid=fixed-uid-done-for-testing-5642512d1758",
                    "for_package_uid": "pkg:bower/blue-leaf?uuid=fixed-uid-done-for-testing-5642512d1758",
                    "datafile_path": "bower.json",
                    "datasource_id": "bower_json"
                },
                {
                    "purl": "pkg:bower/qunit",
                    "extracted_requirement": "~1.16.0",
                    "scope": "devDependencies",
                    "is_runtime": false,
                    "is_optional": true,
                    "is_resolved": false,
                    "resolved_package": {},
                    "extra_data": {},
                    "dependency_uid": "pkg:bower/qunit?uuid=fixed-uid-done-for-testing-5642512d1758",
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
                            "detection_log": [
                                "not-combined"
                            ],
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
                                    "referenced_filenames": [],
                                    "is_license_text": false,
                                    "is_license_notice": false,
                                    "is_license_reference": false,
                                    "is_license_tag": true,
                                    "is_license_intro": false,
                                    "rule_length": 1,
                                    "rule_relevance": 100,
                                    "matched_text": "MIT",
                                    "licenses": [
                                        {
                                            "key": "mit",
                                            "name": "MIT License",
                                            "short_name": "MIT License",
                                            "category": "Permissive",
                                            "is_exception": false,
                                            "is_unknown": false,
                                            "owner": "MIT",
                                            "homepage_url": "http://opensource.org/licenses/mit-license.php",
                                            "text_url": "http://opensource.org/licenses/mit-license.php",
                                            "reference_url": "https://scancode-licensedb.aboutcode.org/mit",
                                            "scancode_url": "https://github.com/nexB/scancode-toolkit/tree/develop/src/licensedcode/data/licenses/mit.LICENSE",
                                            "spdx_license_key": "MIT",
                                            "spdx_url": "https://spdx.org/licenses/MIT"
                                        }
                                    ]
                                }
                            ]
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
                                    "detection_log": [
                                        "not-combined"
                                    ],
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
                                            "referenced_filenames": [],
                                            "is_license_text": false,
                                            "is_license_notice": false,
                                            "is_license_reference": false,
                                            "is_license_tag": true,
                                            "is_license_intro": false,
                                            "rule_length": 1,
                                            "rule_relevance": 100,
                                            "matched_text": "MIT",
                                            "licenses": [
                                                {
                                                    "key": "mit",
                                                    "name": "MIT License",
                                                    "short_name": "MIT License",
                                                    "category": "Permissive",
                                                    "is_exception": false,
                                                    "is_unknown": false,
                                                    "owner": "MIT",
                                                    "homepage_url": "http://opensource.org/licenses/mit-license.php",
                                                    "text_url": "http://opensource.org/licenses/mit-license.php",
                                                    "reference_url": "https://scancode-licensedb.aboutcode.org/mit",
                                                    "scancode_url": "https://github.com/nexB/scancode-toolkit/tree/develop/src/licensedcode/data/licenses/mit.LICENSE",
                                                    "spdx_license_key": "MIT",
                                                    "spdx_url": "https://spdx.org/licenses/MIT"
                                                }
                                            ]
                                        }
                                    ]
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
                                    "is_resolved": false,
                                    "resolved_package": {},
                                    "extra_data": {}
                                },
                                {
                                    "purl": "pkg:bower/eventEmitter",
                                    "extracted_requirement": "~4.2.11",
                                    "scope": "dependencies",
                                    "is_runtime": true,
                                    "is_optional": false,
                                    "is_resolved": false,
                                    "resolved_package": {},
                                    "extra_data": {}
                                },
                                {
                                    "purl": "pkg:bower/qunit",
                                    "extracted_requirement": "~1.16.0",
                                    "scope": "devDependencies",
                                    "is_runtime": false,
                                    "is_optional": true,
                                    "is_resolved": false,
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

``--email`` Option
------------------

    The ``--email`` option detects and reports email adresses present in scanned files.

    It adds the ``emails`` attribute to the file data with the following attributes:
    ``email`` with the actual email that was present in the file, ``start_line`` and
    ``end_line`` to be able to locate where the email was detected in the file.

----

``--url`` Option
----------------

    The ``--url`` option detects and reports URLs present in scanned files.

    It adds the  ``urls`` attribute to the file data with the following attributes:
    ``url`` with the actual URL that was present in the file, ``start_line`` and
    ``end_line`` to be able to locate where the URL was detected in the file.


----

``--generated`` Option
----------------------

    The ``--generated`` option classifies automatically generated code files with a flag.

    An example of using ``--generated`` in a scan::

        scancode -clpieu --json-pp output.json samples --generated

    In the results, for each file the following attribute is added with it's corresponding
    ``true``/``false`` value ::

        "is_generated": true

    In the samples folder, the following files have a true value for their is_generated attribute::

        "samples/zlib/dotzlib/LICENSE_1_0.txt"
        "samples/JGroups/licenses/apache-2.0.txt"

    ..
        [ToDo] Research and Write Better

----

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

``--license-score`` Option
--------------------------

    .. admonition:: Dependency

        The option ``--license-score`` is a sub-option of and requires the option ``--license``.

    ..
        [ToDo] Research and Write License Matching Better

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

``--license-text`` Option
-------------------------

    .. admonition:: Dependency

        The option ``--license-text`` is a sub-option of and requires the option ``--license``.

    .. admonition:: Sub-Option

        The option ``--license-text-diagnostics`` and ``--is-license-text`` are sub-options of
        ``--license-text``. ``--is-license-text`` is a Post-Scan Option.

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

``--license-url-template`` Option
---------------------------------

    .. admonition:: Dependency

        The option ``--license-url-template`` is a sub-option of and requires the option
        ``--license``.

    The ``--license-url-template`` option sets the template URL used for the license reference URLs.

    The default template URL is : [https://enterprise.dejacode.com/urn/urn:dje:license:{}]
    In a template URL, curly braces ({}) are replaced by the license key.

    So, by default the license reference URL points to the dejacode page for that license.

    A scan example using the ``--license-url-template TEXT`` option ::

        scancode -clpieu --json-pp output.json samples --license-url-template https://github.com/nexB/scancode-toolkit/tree/develop/src/licensedcode/data/licenses/{}.yml

    In a normal scan, reference url for "ZLIB License" is as follows::

        "reference_url": "https://enterprise.dejacode.com/urn/urn:dje:license:zlib",

    After using the option in the following manner::

        ``--license-url-template https://github.com/nexB/scancode-toolkit/tree/develop/src/licensedcode/data/licenses/{}``

    the reference URL changes to this `zlib.yml file <https://github.com/nexB/scancode-toolkit/blob/develop/src/licensedcode/data/licenses/zlib.yml>`_::

        "reference_url": "https://github.com/nexB/scancode-toolkit/tree/develop/src/licensedcode/data/licenses/zlib.yml",

    The reference URL changes for all detected licenses in the scan, across the scan result file.

----

``--license-text-diagnostics`` Option
-------------------------------------

    .. admonition:: Dependency

        The option ``--license-text-diagnostics`` is a sub-option of and requires the options
        ``--license`` and ``--license-text``.

    In the matched license text, include diagnostic highlights surrounding with square brackets []
    words that are not matched.

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

    With Diagnostics on::

        "matched_text":
        "License [Copyright] ([c]) [2000] - [2006] [The] [Legion] [Of] [The] [Bouncy] [Castle]
        ([http]://[www].[bouncycastle].[org]) Permission is hereby granted, free of charge, to any person
        obtaining a copy of this software and associated documentation files (the \"Software\"),
        to deal in the Software without restriction,
