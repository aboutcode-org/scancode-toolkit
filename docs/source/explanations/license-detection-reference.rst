License Detection Updates
=========================

References:

* `Issue <https://github.com/nexB/scancode-toolkit/issues/2878>`_
* `Pull Request <https://github.com/nexB/scancode-toolkit/pull/2961>`_
* `A presentation on this <https://github.com/nexB/scancode-toolkit/issues/2878#issuecomment-1079639973>`_


The Problem:
------------

There was a lot of false-positives in scancode license results, specially
`unknown-license-reference` detections and to tackle this the following
solution elements were discussed:

1. Reporting the primary, declared license in a scan summary record
2. tagging mandatory portions in rules `#2773 <https://github.com/nexB/scancode-toolkit/pull/2773>`_
3. Adding license detections by combine multiple license matches `#2961 <https://github.com/nexB/scancode-toolkit/pull/2961>`_
4. Integrating the existing scancode-analyzer tool into SCTK to combine multiple matches
   based on statistics and heuristics `#2961 <https://github.com/nexB/scancode-toolkit/pull/2961>`_
5. Reporting license clues when the matched license rule data is not sufficient to
   create a LicenseDetection `#2961 <https://github.com/nexB/scancode-toolkit/pull/2961>`_
6. web app for efficient scan and review of a single license to ease
   reporting license detection issues `nexB/scancode.io#450 <https://github.com/nexB/scancode.io/pull/450>`_
7. also apply LicenseDetection to package license detections `#2961 <https://github.com/nexB/scancode-toolkit/pull/2961>`_
8. rename resource and package license fields `#2961 <https://github.com/nexB/scancode-toolkit/pull/2961>`_

What is a LicenseDetection?
---------------------------

A detection which can have one or multiple LicenseMatch in them,
and creates a License Expression that we finally report.

Properties:

- A file can have multiple LicenseDetections (seperated by non-legalese lines)
- This can be from a file directly or a package.
- We should be mostly certain of a proper detection to create a LicenseDetection.
- One LicenseDetection can have matches from different files, in case of local license
  references.

Examples
^^^^^^^^

A License Intro example::

 /*********************************************************************
 * Copyright (c) 2019 Red Hat, Inc.
 *
 * This program and the accompanying materials are made
 * available under the terms of the Eclipse Public License 2.0
 * which is available at https://www.eclipse.org/legal/epl-2.0/
 *
 * SPDX-License-Identifier: EPL-2.0
 **********************************************************************/


The text ``"This program and the accompanying materials are made\n* available under the terms
of the",`` is detected as ``unknown-license-reference`` with ``is_license_intro`` as True,
and has several ``epl-2.0`` detections after that.

This can be considered as a single License Detection with it's detected license-expression as
``epl-2.0``. The matches of this license detection would also have the matches with the
``unknown-license-reference``, but they will not be present in the final license_expression.


A License Reference example:

Consider the two following files:

file.py::

  This is free software. See COPYING for details.

COPYING::

  license: apache 2.0

Here there will be a ``unknown-license-reference`` detected in ``file.py`` and this
actually references the license detected in ``COPYING`` which is ``apache-2.0``.

This can be considered a single LicenseDetection with both the license matches from both
files, and a concluded license_expression ``apache-2.0`` instead of the
``unknown-license-reference``.


Change in License Data format: Resource
---------------------------------------

To move into the new LicenseDetection concept, the license data in scancode outputs has
undergone a major change. See the before/after results for a file to compare the
changes.

Before::

  {
    "licenses": [
      {
        "key": "apache-2.0",
        "score": 100.0,
        "name": "Apache License 2.0",
        "short_name": "Apache 2.0",
        "category": "Permissive",
        "is_exception": false,
        "is_unknown": false,
        "owner": "Apache Software Foundation",
        "homepage_url": "http://www.apache.org/licenses/",
        "text_url": "http://www.apache.org/licenses/LICENSE-2.0",
        "reference_url": "https://scancode-licensedb.aboutcode.org/apache-2.0",
        "scancode_text_url": "https://github.com/nexB/scancode-toolkit/tree/develop/src/licensedcode/data/licenses/apache-2.0.LICENSE",
        "scancode_data_url": "https://github.com/nexB/scancode-toolkit/tree/develop/src/licensedcode/data/licenses/apache-2.0.yml",
        "spdx_license_key": "Apache-2.0",
        "spdx_url": "https://spdx.org/licenses/Apache-2.0",
        "start_line": 1,
        "end_line": 1,
        "matched_rule": {
          "identifier": "apache-2.0_65.RULE",
          "license_expression": "apache-2.0",
          "licenses": [
            "apache-2.0"
          ],
          "referenced_filenames": [],
          "is_license_text": false,
          "is_license_notice": false,
          "is_license_reference": false,
          "is_license_tag": true,
          "is_license_intro": false,
          "has_unknown": false,
          "matcher": "1-hash",
          "rule_length": 4,
          "matched_length": 4,
          "match_coverage": 100.0,
          "rule_relevance": 100,
          "is_builtin": true
        },
        "matched_text": "License: Apache-2.0"
      }
    ],
    "license_expressions": [
      "apache-2.0"
    ]
  }


After::

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
  }

Change in License Data format: Package
--------------------------------------

License data attributes has also changed in packages:

Before::

  {
    "type": "cocoapods",
    "namespace": null,
    "name": "LoadingShimmer",
    "version": "1.0.3",
    "license_expression": "mit AND unknown",
    "declared_license": ":type = MIT, :file = LICENSE",
    "datasource_id": "cocoapods_podspec",
    "purl": "pkg:cocoapods/LoadingShimmer@1.0.3"
  }

After::

  {
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
            "matched_length": 4,
            "match_coverage": 100.0,
            "matcher": "1-hash",
            "license_expression": "mit",
            "rule_identifier": "mit_in_manifest.RULE",
            "rule_url": "https://github.com/nexB/scancode-toolkit/tree/develop/src/licensedcode/data/rules/mit_in_manifest.RULE",
            "referenced_filenames": [
              "LICENSE"
            ],
            "is_license_text": false,
            "is_license_notice": false,
            "is_license_reference": true,
            "is_license_tag": false,
            "is_license_intro": false,
            "rule_length": 4,
            "rule_relevance": 100,
            "matched_text": ":type = MIT, :file = LICENSE",
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
    "extracted_license_statement": ":type = MIT, :file = LICENSE",
  }

Previously in package data only the license_expression was present and it was very hard to debug
license detections. Now there's a ``license_detections`` field with the detections, same as
the resource ``license_detections``, with additional ``declared_license_expression`` and
``other_license_expression`` with their SPDX counterparts. The ``declared_license`` field
also has been renamed to ``extracted_license_statement``.



New codebase level Unique License Detection
-------------------------------------------


We now have a new codebase level attribute ``license_detections`` which has Unique
license detection across the codebase, in both packages and resources. There is also
a new resource level attribute to reference to the codebase level unique license
detections, which is ``for_license_detections``.

New codebase level attribute::

  {
    "license_detections": [
      {
        "identifier": "epl_1_0-1867eafe-a258-cbb4-408f-2bd33d02ee23",
        "license_expression": "epl-1.0",
        "count": 2,
        "detection_log": [
          "not-combined"
        ],
        "matches": [
          {
            "score": 99.34,
            "start_line": 12,
            "end_line": 25,
            "matched_length": 150,
            "match_coverage": 99.34,
            "matcher": "3-seq",
            "license_expression": "epl-1.0",
            "rule_identifier": "epl-1.0_3.RULE",
            "rule_url": "https://github.com/nexB/scancode-toolkit/tree/develop/src/licensedcode/data/rules/epl-1.0_3.RULE"
          },
          {
            "score": 100.0,
            "start_line": 17,
            "end_line": 17,
            "matched_length": 8,
            "match_coverage": 100.0,
            "matcher": "2-aho",
            "license_expression": "epl-1.0",
            "rule_identifier": "epl-1.0_7.RULE",
            "rule_url": "https://github.com/nexB/scancode-toolkit/tree/develop/src/licensedcode/data/rules/epl-1.0_7.RULE"
          }
        ]
      }
    ]
  }

New resource level attribute::

  {
    "files": [
      {
        "for_license_detections": [
          "epl_1_0-1867eafe-a258-cbb4-408f-2bd33d02ee23"
        ]
      }
    ]
  }


LicenseMatch Result Data
------------------------

LicenseMatch data was based on a ``license key`` instead of being based
on an ``license-expression``.

So if there is a ``mit and apache-2.0`` license expression detected from a single
LicenseMatch, there was two entries in the ``licenses`` list for that
resource, one for each license key, (here ``mit`` and ``apache-2.0`` respectively).
This repeats the match details as these two entries have the same details except the
license key. And this is wrong.

We should only add one entry per match (and therefore per ``rule``) and here the
primary attribute should be the ``license-expression``, rather than the ``license-key``.

We also create a mapping inside a mapping in these license details to refer to the
license rule (and there are other incosistencies in how we report here). We should
just report a flat mapping here, (with a list at last for each of the license keys).

See this before/after comparision to see how the license data in results has
eveolved.

Before::

  {
    "key": "apache-2.0",
    "score": 100.0,
    "name": "Apache License 2.0",
    "short_name": "Apache 2.0",
    "category": "Permissive",
    "is_exception": false,
    "is_unknown": false,
    "owner": "Apache Software Foundation",
    "homepage_url": "http://www.apache.org/licenses/",
    "text_url": "http://www.apache.org/licenses/LICENSE-2.0",
    "reference_url": "https://scancode-licensedb.aboutcode.org/apache-2.0",
    "scancode_text_url": "https://github.com/nexB/scancode-toolkit/tree/develop/src/licensedcode/data/licenses/apache-2.0.LICENSE",
    "scancode_data_url": "https://github.com/nexB/scancode-toolkit/tree/develop/src/licensedcode/data/licenses/apache-2.0.yml",
    "spdx_license_key": "Apache-2.0",
    "spdx_url": "https://spdx.org/licenses/Apache-2.0",
    "start_line": 1,
    "end_line": 1,
    "matched_rule": {
      "identifier": "apache-2.0_65.RULE",
      "license_expression": "apache-2.0",
      "licenses": [
        "apache-2.0"
      ],
      "referenced_filenames": [],
      "is_license_text": false,
      "is_license_notice": false,
      "is_license_reference": false,
      "is_license_tag": true,
      "is_license_intro": false,
      "has_unknown": false,
      "matcher": "1-hash",
      "rule_length": 4,
      "matched_length": 4,
      "match_coverage": 100.0,
      "rule_relevance": 100,
      "is_builtin": true
    },
    "matched_text": "License: Apache-2.0"
  }



After::


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



Only reference License related Data
-----------------------------------

Before 32.x all license related data was inlined in each match, and this repeats
a lot of information. This repeatation exists in three levels:

- License-level Data (a license-key)
- Rule-level Data (a license rule)
- LicenseDetection Data

License Data
^^^^^^^^^^^^

This is referencing data related to whole licenses, references by their license key.

Example: ``apache-2.0``

Other attributes are it's full test, links to origin, licenseDB, spdx, osi etc.


Rule Data
^^^^^^^^^

This is referencing data related to a LicenseDB entry.
I.e. the identifier is a `RULE` or a `LICENSE` file.

Example: ``apache-2.0_2.RULE``

Other attributes are it's license-expression, the boolean fields, length, relevance etc.


CLI option
^^^^^^^^^^

This is now default with the CLI option ``--license``, which references from
the match License-level Data and LicenseDB-level Data, and removes the actual data from
the matches, and adds them to two top-level lists.

Comparision: Before/After license references
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To compare how the license output data changes between when license references are not collected
vs when they are collected (which is default from version 32.x), check out the before/after
comparision below.

Before::

  {
    "files": [
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
      }
    ]
  }

After::

  {
    "license_references": [
      {
        "key": "apache-2.0",
        "short_name": "Apache 2.0",
        "name": "Apache License 2.0",
        "category": "Permissive",
        "owner": "Apache Software Foundation",
        "homepage_url": "http://www.apache.org/licenses/",
        "notes": "Per SPDX.org, this version was released January 2004 This license is OSI\ncertified\n",
        "is_builtin": true,
        "spdx_license_key": "Apache-2.0",
        "other_spdx_license_keys": [
          "LicenseRef-Apache",
          "LicenseRef-Apache-2.0"
        ],
        "osi_license_key": "Apache-2.0",
        "text_urls": [
          "http://www.apache.org/licenses/LICENSE-2.0"
        ],
        "osi_url": "http://opensource.org/licenses/apache2.0.php",
        "faq_url": "http://www.apache.org/foundation/licence-FAQ.html",
        "other_urls": [
          "http://www.opensource.org/licenses/Apache-2.0",
          "https://opensource.org/licenses/Apache-2.0",
          "https://www.apache.org/licenses/LICENSE-2.0"
        ],
        "text": "Apache License\nVersion 2.0, {Truncated text}"
      }
    ],
    "license_rule_references": [
      {
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
        "rule_text": "license: Apache-2.0"
      }
    ],
    "files": [
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
                "matched_text": "License: Apache-2.0",
                "rule_url": "https://github.com/nexB/scancode-toolkit/tree/develop/src/licensedcode/data/rules/apache-2.0_65.RULE"
              }
            ]
          }
        ],
        "license_clues": [],
      }
    ]
  }


LicenseDetection Data
^^^^^^^^^^^^^^^^^^^^^

This is referencing by LicenseDetections, and has one or multiple license Matches.
This is not referenced to a top-level list, but there could be a list of ambiguous
detections as a summary to review. This is WIP, see
`scancode-toolkit#3122 <https://github.com/nexB/scancode-toolkit/issues/3122>`_.
