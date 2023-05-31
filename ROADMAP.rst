ScanCode IO/TK Roadmap
========================

SCIO: ScanCode.io 
SCTK: ScanCode Toolkit

Top Issues
---------------

1. Primary license detection, top issue.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There is too much cruft in detected licenses. We know too much without being
to distinguish the forest from the trees. Therefore reporting the primary
license detection is important: when we get scan results, we can often
get 30 licenses for a single a package and this volume is a problem
even if it is correct and it is technically correct.
The goal of this improvement is to:

- combine multiple related license matches in a single license detection

- in a license detection, expose a primary license expression in addition
  to the complete, full license expression.

- make the logic of selection of the primary license visible, at the minimum
  with a log of combination and primary license selection operations

This is for SCTK first.

Status: This has been completed in SCTK and also included in SCIO. We use
an updated --summary option and a new license clarity score for this.
We also have LicenseDetections for resources/packages and a top level
unique license detections as a summary.


2. Package files.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reporting the set of package files for each package instance is important because
it allows for natural grouping of these in one unit.

This has been completed in SCTK and also included in SCIO.


3. Go to two-level reporting of detections to provide more effective detections
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*Packages*:

- manifest, file-level: package.json
- package: object of its own, and related set of files, not always in the same
  directory

This is completed in SCTK.

*License*:

- many detections in a file at different locations, could be merged into a single reported license
- same for primary licenses

This is completed in SCTK.

*Copyright*:

- Copyright and author detection, which are tracked at the line level
- Holder would be for many copyright detections


4. Primary copyright holder
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the same issue as for primary license, but for holders



Roadmap
-------------------------

1. Support primary license for packages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- SCTK: add primary license field in package output and populate this based on
  package-type/ecosystem conventions.
- SCTK: also populate secondary license fields 
- SCIO: add primary license field in DiscoveredPackage models and feed it with
  the data from packages
- SCIO: Do we track secondary? or is this just data aggregated on the fly.
- SCIO: Refine primary license based on license in "key files"  


2. Primary copyright detection for packages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- This is closely tied to the primary license detection and should focus
  on package manifests and key files. 
- Support copyright parsing from all package ecosystems.

3. Package files
~~~~~~~~~~~~~~~~~~~~~~~~~

- SCTK: See https://github.com/nexB/scancode-toolkit/projects/10
  - Work on the model
  - Work on updating the package code focus in npm, pypi, maven, go.
- SCIO: adopt the two levels manifests/package instances


4. Go to two-level reporting for license detections
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Add top level reference licenses section in the JSON output
- Report detections at the file level, one per matched rule
- Report multiple detections for one or more license expressions in a file, eventually
  grouping multiple detection in a single expression in a file


5. Go to two-level reporting for copyright holder detections
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Reported detections of Copyrights and authors detection, tracked at the line level in a file
- Holder would be for many copyright detections


6. License detection quality improvements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Finish and merge unknown license detection (this depends on completion of 4. Go to two-level reporting of detections for license)
- Update scancode-analyze to the new two-level reporting of license detections
- Revamp how common list of suprrious licenses are detected (this is a bug)
- Use important key phrases for license detection https://github.com/nexB/scancode-toolkit/issues/2637

This is mostly completed, for follow up see https://github.com/nexB/scancode-toolkit/issues/2878.
