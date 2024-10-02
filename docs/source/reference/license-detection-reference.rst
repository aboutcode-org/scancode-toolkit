License Detection Updates
=========================

References:

* `Issue <https://github.com/aboutcode-org/scancode-toolkit/issues/2878>`_
* `Pull Request <https://github.com/aboutcode-org/scancode-toolkit/pull/2961>`_
* `A presentation on this <https://github.com/aboutcode-org/scancode-toolkit/issues/2878#issuecomment-1079639973>`_


The Problem:
------------

The goal was to reduce false-positives in scancode license detection results, especially
`unknown-license-reference` detections and approximate detections reporting best-guess
license_expressions. To tackle this the following solution elements were discussed and
implemented:

1. Reporting the primary, declared license in a scan summary record
2. tagging mandatory portions in rules `#2773 <https://github.com/aboutcode-org/scancode-toolkit/pull/2773>`_
3. Adding license detections by combine multiple license matches `#2961 <https://github.com/aboutcode-org/scancode-toolkit/pull/2961>`_
4. Integrating the existing scancode-analyzer tool into SCTK to combine multiple matches
   based on statistics and heuristics `#2961 <https://github.com/aboutcode-org/scancode-toolkit/pull/2961>`_
5. Reporting license clues when the matched license rule data is not sufficient to
   create a LicenseDetection `#2961 <https://github.com/aboutcode-org/scancode-toolkit/pull/2961>`_
6. web app for efficient scan and review of a single license to ease
   reporting license detection issues `nexB/scancode.io#450 <https://github.com/aboutcode-org/scancode.io/pull/450>`_
7. also apply LicenseDetection to package license detections `#2961 <https://github.com/aboutcode-org/scancode-toolkit/pull/2961>`_
8. rename resource and package license fields `#2961 <https://github.com/aboutcode-org/scancode-toolkit/pull/2961>`_

Some other elements are still WIP, see `issue #3300 <https://github.com/aboutcode-org/scancode-toolkit/issues/3300>`_ for more details on this.

.. _what-is-a-licensedetection:

What is a LicenseDetection?
---------------------------

A detection which can have one or multiple LicenseMatch in them,
and creates a License Expression that we finally report.

Properties:

- A file can have multiple LicenseDetections (separated by non-legalese lines)
- This can be from a file directly or a package.
- We should be mostly certain of a proper license detection to report a
  LicenseDetection, i.e. we should have ideally gotten rid of false
  positives and wrong license matches, or improved them.
- One LicenseDetection can have matches from different files, in case of local license
  references.
- We don't remove any detection matches, but we add more matches only to rectify and
  correct the license_expression.

Also there are two levels of reporting license detections:

- File/package level License Detections
- Codebase level unique License Detections (summarized from the file/package level detections)

Examples
^^^^^^^^

A License Intro example:

Consider the following text::

 /*********************************************************************
 * Copyright (c) 2019 Red Hat, Inc.
 *
 * This program and the accompanying materials are made
 * available under the terms of the Eclipse Public License 2.0
 * which is available at https://www.eclipse.org/legal/epl-2.0/
 *
 * SPDX-License-Identifier: EPL-2.0
 **********************************************************************/


The text::

  "This program and the accompanying materials are made\n* available under the terms of the"

is detected as ``unknown-license-reference`` with ``is_license_intro`` as True,
and has several ``epl-2.0`` detections after that.

This can be considered as a single License Detection with its detected license-expression as
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


Chnagelog Summary
-----------------

- There is a new ``license_detections`` codebase level attribute with all the
  unique license detections in the whole scan, both in resources and packages.

- The data structure of the JSON output has changed for licenses at resource
  level, also with new attribute names, ``licenses`` -> ``license_detections``
  and ``license_expressions`` -> ``detected_license_expression`` also with a
  SPDX version of the same. As license detection attributes we have:
  ``license_expression``, ``identifier`` and ``matches``. We also have a
  ``detection_log`` (present optionally if the ``--license-diagnostics``
  option is enabled).

- There are ``license_detections`` now reported at packages, and the data
  structure of license attributes in ``package_data`` and the codebase level
  ``packages`` has been also updated:  ``license_expression`` ->
  ``declared_license_expression``, also with it's SPDX version,
  ``declared_license`` -> ``extracted_license_statement``, and also secondary
  license detections data in: ``other_license_expression`` and
  ``other_license_detections``.

- Instead of reporting one match for each license ``key`` of a matched
  license expression, we now report one single match for each matched
  license expression, avoiding data duplication. Inside each match, we also
  list each match and matched rule attributes directly to avoiding nesting.

- License and Rule reference data is not reported at match level in license
  detections and instead is reported at codebase-level with a new CLI option
  ``--license-references`` as new attributes: ``license_references`` and
  ``license_rule_references`` that list unique detected license and
  license rules with their details.


Change in License Data format: Resource
---------------------------------------

The data structure of the JSON output has changed for licenses at file level:

- The ``licenses`` attribute is deleted.

- A new ``license_detections`` attribute contains license detections in that file.
  This object has three attributes: ``license_expression``, ``detection_log``
  and ``matches``. ``matches`` is a list of license matches and is roughly
  the same as  ``licenses`` in the previous version with additional structure
  changes detailed below.

- A new attribute ``license_clues`` contains license matches with the
  same data structure as the ``matches`` attribute in ``license_detections``.
  This contains license matches that are mere clues and were not considered
  to be a proper conclusive license detection.

- The ``license_expressions`` list of license expressions is deleted and
  replaced by a ``detected_license_expression`` single expression.
  Similarly ``spdx_license_expressions`` was removed and replaced by
  ``detected_license_expression_spdx``.

See the before/after results for a file to compare the changes.

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
        "scancode_text_url": "https://github.com/aboutcode-org/scancode-toolkit/tree/develop/src/licensedcode/data/licenses/apache-2.0.LICENSE",
        "scancode_data_url": "https://github.com/aboutcode-org/scancode-toolkit/tree/develop/src/licensedcode/data/licenses/apache-2.0.yml",
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
          "matched_text": "license: apache 2.0"
        }
      ],
      "detection_log": [],
      "identifier": "apache_2_0-ec759ae0-ea5a-f138-793e-388520e080c0"
    }
  ],
  "license_clues": [],

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
          "matched_length": 4,
          "match_coverage": 100.0,
          "matcher": "1-hash",
          "license_expression": "mit",
          "rule_identifier": "mit_in_manifest.RULE",
          "rule_relevance": 100,
          "rule_url": "https://github.com/aboutcode-org/scancode-toolkit/tree/develop/src/licensedcode/data/rules/mit_in_manifest.RULE",
          "matched_text": ":type = MIT, :file = LICENSE"
        }
      ],
      "identifier": "mit-74f1df5b-f94d-2423-6bb8-3e4d809c26a5"
    }
  ],
  "other_license_expression": null,
  "other_license_expression_spdx": null,
  "other_license_detections": [],
  "extracted_license_statement": ":type = MIT, :file = LICENSE",

Previously in package data only the license_expression was present and it was very hard to debug
license detections. Now there's a ``license_detections`` field with the detections, same as
the resource ``license_detections``, with additional ``declared_license_expression`` and
``other_license_expression`` with their SPDX counterparts. The ``declared_license`` field
also has been renamed to ``extracted_license_statement``.

.. _license_detections_unique:

Codebase level Unique License Detection
-------------------------------------------

We now have a new codebase level attribute ``license_detections`` which has Unique
License Detection across the codebase, in both packages and resources. They are
linked by a common attribute ``identifier`` containing the ``license_expression``
and a UUID generated from the match content. The match level data is only present
at the resource level if needed, to look at details.

New codebase level attribute::

  {
    "license_detections": [
      {
        "identifier": "epl_1_0-583490fb-0b3a-f445-a1b9-1b96423b9ec3",
        "license_expression": "epl-1.0",
        "detection_count": 2,
        "detection_log": []
      }
    ]
  }

For the corresponding resource level license detection::

  "license_detections": [
    {
      "license_expression": "epl-1.0",
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
          "rule_relevance": 100,
          "rule_url": "https://github.com/aboutcode-org/scancode-toolkit/tree/develop/src/licensedcode/data/rules/epl-1.0_3.RULE",
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
          "rule_relevance": 100,
          "rule_url": "https://github.com/aboutcode-org/scancode-toolkit/tree/develop/src/licensedcode/data/rules/epl-1.0_7.RULE",
        }
      ],
      "detection_log": [],
      "identifier": "epl_1_0-583490fb-0b3a-f445-a1b9-1b96423b9ec3"
    }
  ]



LicenseMatch Result Data
------------------------

LicenseMatch data was based on a ``license key`` instead of being based
on a ``license-expression``.

So if there is a ``gpl-2.0 AND patent-disclaimer`` license expression detected
from a single LicenseMatch, there were two entries in the ``licenses`` list
for that resource, one for each license key, (here ``gpl-2.0`` and
``patent-disclaimer`` respectively). This repeats the match details as these
two entries have the same details except the license key.

We should only add one entry per match (and therefore per ``rule``) and here
the primary attribute should be the ``license-expression``, rather than the
``license-key``.

We also used to create a mapping inside a mapping in these license details
to refer to the license rule (and there are other inconsistencies in how we
report here). We are now just reporting a flat mapping here, and all the
rule details are also not present in the license match, and only available
as an optional reference.

See this before/after comparision to see how the license data in results has
evolved.

Before::

  "licenses": [
    {
      "key": "gpl-2.0",
      "score": 100.0,
      "name": "GNU General Public License 2.0",
      "short_name": "GPL 2.0",
      "category": "Copyleft",
      "is_exception": false,
      "is_unknown": false,
      "owner": "Free Software Foundation (FSF)",
      "homepage_url": "http://www.gnu.org/licenses/gpl-2.0.html",
      "text_url": "http://www.gnu.org/licenses/gpl-2.0.txt",
      "reference_url": "https://scancode-licensedb.aboutcode.org/gpl-2.0",
      "scancode_text_url": "https://github.com/aboutcode-org/scancode-toolkit/tree/develop/src/licensedcode/data/licenses/gpl-2.0.LICENSE",
      "scancode_data_url": "https://github.com/aboutcode-org/scancode-toolkit/tree/develop/src/licensedcode/data/licenses/gpl-2.0.yml",
      "spdx_license_key": "GPL-2.0-only",
      "spdx_url": "https://spdx.org/licenses/GPL-2.0-only",
      "start_line": 4,
      "end_line": 30,
      "matched_rule": {
        "identifier": "gpl-2.0_and_patent-disclaimer_3.RULE",
        "license_expression": "gpl-2.0 AND patent-disclaimer",
        "licenses": [
          "gpl-2.0",
          "patent-disclaimer"
        ],
        "referenced_filenames": [],
        "is_license_text": false,
        "is_license_notice": true,
        "is_license_reference": false,
        "is_license_tag": false,
        "is_license_intro": false,
        "has_unknown": false,
        "matcher": "2-aho",
        "rule_length": 185,
        "matched_length": 185,
        "match_coverage": 100.0,
        "rule_relevance": 100
      }
    },
    {
      "key": "patent-disclaimer",
      "score": 100.0,
      "name": "Generic patent disclaimer",
      "short_name": "Generic patent disclaimer",
      "category": "Permissive",
      "is_exception": false,
      "is_unknown": false,
      "owner": "Unspecified",
      "homepage_url": null,
      "text_url": "",
      "reference_url": "https://scancode-licensedb.aboutcode.org/patent-disclaimer",
      "scancode_text_url": "https://github.com/aboutcode-org/scancode-toolkit/tree/develop/src/licensedcode/data/licenses/patent-disclaimer.LICENSE",
      "scancode_data_url": "https://github.com/aboutcode-org/scancode-toolkit/tree/develop/src/licensedcode/data/licenses/patent-disclaimer.yml",
      "spdx_license_key": "LicenseRef-scancode-patent-disclaimer",
      "spdx_url": "https://github.com/aboutcode-org/scancode-toolkit/tree/develop/src/licensedcode/data/licenses/patent-disclaimer.LICENSE",
      "start_line": 4,
      "end_line": 30,
      "matched_rule": {
        "identifier": "gpl-2.0_and_patent-disclaimer_3.RULE",
        "license_expression": "gpl-2.0 AND patent-disclaimer",
        "licenses": [
          "gpl-2.0",
          "patent-disclaimer"
        ],
        "referenced_filenames": [],
        "is_license_text": false,
        "is_license_notice": true,
        "is_license_reference": false,
        "is_license_tag": false,
        "is_license_intro": false,
        "has_unknown": false,
        "matcher": "2-aho",
        "rule_length": 185,
        "matched_length": 185,
        "match_coverage": 100.0,
        "rule_relevance": 100
      }
    }
  ],
  "license_expressions": [
    "gpl-2.0 AND patent-disclaimer"
  ],



After::


  "license_detections": [
    {
      "license_expression": "gpl-2.0 AND patent-disclaimer",
      "matches": [
        {
          "score": 100.0,
          "start_line": 4,
          "end_line": 30,
          "matched_length": 185,
          "match_coverage": 100.0,
          "matcher": "2-aho",
          "license_expression": "gpl-2.0 AND patent-disclaimer",
          "rule_identifier": "gpl-2.0_and_patent-disclaimer_3.RULE",
          "rule_relevance": 100,
          "rule_url": "https://github.com/aboutcode-org/scancode-toolkit/tree/develop/src/licensedcode/data/rules/gpl-2.0_and_patent-disclaimer_3.RULE"
        }
      ],
      "identifier": "gpl_2_0_and_patent_disclaimer-3bb2602f-86f5-b9da-9bf5-b52e6920c8d1"
    }
  ],

.. _reference_license_related_data:

Only reference License related data
-----------------------------------

Before 32.x all license related data was inlined in each match, and this repeats
a lot of information. This repeatation exists in three levels:

- License-level Data (a license-key)
- Rule-level Data (a license rule)
- LicenseDetection Data (a license detection)

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
                "rule_url": "https://github.com/aboutcode-org/scancode-toolkit/tree/develop/src/licensedcode/data/rules/apache-2.0_65.RULE",
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
                    "scancode_url": "https://github.com/aboutcode-org/scancode-toolkit/tree/develop/src/licensedcode/data/licenses/apache-2.0.LICENSE",
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
        "rule_url": "https://github.com/aboutcode-org/scancode-toolkit/tree/develop/src/licensedcode/data/rules/apache-2.0_65.RULE",
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
                "rule_url": "https://github.com/aboutcode-org/scancode-toolkit/tree/develop/src/licensedcode/data/rules/apache-2.0_65.RULE"
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

This is referencing by LicenseDetections objects, and has one or multiple
license matches. This is linked to the resource level detections through
an ``identifier`` attribute present in both resource and codebase level
detections. See the :ref:`license_detections_unique` above for more
details on this.

There could be a list of ambiguous detections as a summary to review.
This is WIP, see `scancode-toolkit#3122 <https://github.com/aboutcode-org/scancode-toolkit/issues/3122>`_.
