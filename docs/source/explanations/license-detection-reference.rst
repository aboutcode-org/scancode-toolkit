License Detection and Reference Additions
=========================================

`Main Issue <https://github.com/nexB/scancode-toolkit/issues/2878>`_

`Main Pull Request <https://github.com/nexB/scancode-toolkit/pull/2961>`_

`A presentation on this <https://github.com/nexB/scancode-toolkit/issues/2878#issuecomment-1079639973>`_


Previous Work
-------------

- Akansha's GSoC work on unknown local references and unknown detection
  based on ngrams from LicenseDB texts.

- work from ``scancode-analyzer`` and ``debian copyright detection``
  which had the concept of a LicenseDetection, flat LicenseMatches and
  getting a unique detections across a scan referencing the details.

- work on primary-license and license scoring.

LicenseDetection
----------------

This aims to solve a few types of false positives commonly observed in
ScanCode license detection. These are:

The ``unknown`` cases
^^^^^^^^^^^^^^^^^^^^^

- Unknown Intros with Proper Detections after them
- Unknown references to local files

License Clues
^^^^^^^^^^^^^

Also this would introduce a ``license_clues`` list of LicenseMatches
which would have improper detections or other clues like urls which
cannot be marked as detections.

License Versions
^^^^^^^^^^^^^^^^

This would also simplify license-expressions for gpl/lgpl cases
with versioned/unversioned matches detected together.

Package License Detections
^^^^^^^^^^^^^^^^^^^^^^^^^^

License detections in package manifests now just have the license-expression
from the detection and this is different from licenses detected directly which
have details. So packages now would also have details.

Other Soulution Elements
^^^^^^^^^^^^^^^^^^^^^^^^

Merged:

- Key {{phrases}} in license text rules
- New license clarity scoring
- Report the primary license

Upcoming:

- Make it easier to report, review and curate license detections
  (GSoC Project in scancode.io)

- Fixing bugs and updating the heuristics.
  (This will be ongoing like the LicenseDB updates)

Examples
^^^^^^^^

An example from the eclipse foundation::

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
and has several ``"epl-2.0"`` detections after that.

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


LicenseMatch Result Data
------------------------

LicenseMatch data currently is based on a ``license key`` instead of being based
on an ``license-expression``.

So if there is a ``mit and apache-2.0`` license expression detected from a single
LicenseMatch, we currently add two entries in the ``licenses`` list for that
resource, one for each license key, (here ``mit`` and ``apache-2.0`` respectively).
This repeats the match details as these two entries have the same details except the
license key. And this is wrong.

We should only add one entry per match (and therefore per ``rule``) and here the
primary attribute should be the ``license-expression``, rather than the ``license-key``.

We also create a mapping inside a mapping in these license details to refer to the
license rule (and there are other incosistencies in how we report here). We should
just report a flat mapping here, (with a list at last for each of the license keys).


Only reference License related Data
-----------------------------------

Currently all license related data is inlined in each match, and this repeats
a lot of information. This repeatation exists in three levels:

- License Data
- LicenseDB Data
- LicenseDetection Data

If we introduce a new command line option ``--licenses-reference``, which of these
should we reference, just License/LicenseDB data, just LicenseDetection level data
or all of them?

License Data
^^^^^^^^^^^^

This is referencing data related to whole licenses, references by their license key.

Example: ``apache-2.0``

Other attributes are it's full test, links to origin, licenseDB, spdx, osi etc.


LicenseDB Data
^^^^^^^^^^^^^^

This is referencing data related to a LicenseDB entry.
I.e. the identifier is a `RULE` or a `LICENSE` file.

Example: ``apache-2.0_2.RULE``

Other attributes are it's license-expression, the boolean fields, length, relevance etc.


LicenseDetection Data
^^^^^^^^^^^^^^^^^^^^^

This is referencing by LicenseDetections. This has one or multiple license Matches.

Identifier is a hash/uuid field computed from a nested tuple of select attributes.

This will represent each LicenseDetection, if the same detection is present across multiple files.

Attributes will be:

- File Regions where these are found (File Path + Start and End line)
- Score, matched length, matcher (like ``1-hash``, ``2-aho``), and matched text.


What should be the default option?
----------------------------------

Two changes were long-planned and should be default:

- LicenseDetections in the results
- LicenseMatch being for a ``license-expression``

This is already a lot of change, so also having the referencing details as default doesn't
make sense IMHO.

- We need to have the details inlined as an option surely because otherwise it will be downstream
  tools resposibility to get this and inline them.

We can always make the details referenced as the default option in a later release after more
testing and feedback. So we can then have the ``--licenses-reference`` command line option
which removes the details and puts them in a top-level list. And the details inlined as
default.
