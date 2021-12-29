ScanCode IO/TK Roadmap
========================

Top Issues
---------------

1. Primary license detection, top issue.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There is too much cruft in detected licenses, and we know too much without being
to distinguish the forest from the trees. Therefore reporting the primary
license detection is important: when we get SC results, we can often
get 30 license on a single a package and that's a problem.
It would make the logic of selection the primary license visible

Is this for SCIO or SCTK? Likely a bit a both.


2. Package files.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reporting the set of package files for each package instance is important as
it allows to naturally group these together in one unit.


3. Go to two-level reporting of detections to provide more effective detections
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*Packages*:

- manifest, file-level: package.json
- package: object of its own, and related set of files, not always in the same
  directory

*License*:

- many detections in a file at different location, could be merged in a single reported license
- same for primary licenses

*Copyright*:

- Copyrights and authors detection, which are tracked at the line level
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
- SCIO: add primary license field in DiscoveredPackage models and feed it with
  the data from packages
- SCIO: Do we track secondary? or is this just aggregated data on the fly.
- SCIO: Refine primary license based on license in "key files"  


2. Primary copyright detection for packages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- this is likely closely tied to the primary license detection and should focus
  on package manifests and key files. And on package first



3. Package files
~~~~~~~~~~~~~~~~~~~~~~~~~

- SCTK: See https://github.com/nexB/scancode-toolkit/projects/10
  - work on the model
  - work on updating the package code focus in npm, pypi, maven, go.
- SCIO: adopt the two levels manifests/package instances



4. Go to two-level reporting of detections for licenses
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- add top level reference licenses section in the JSON output
- report detections at the file level, one per matched rule
- multiple detections for one or more license expressions in a file, eventually
  grouping multiple detection in a single expression in a file


5. Go to two-level reporting of detections for holders
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Reported detections of Copyrights and authors detection, tracked at the line level in a file
- Holder would be for many copyright detections



6. License detection quality improvements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Finish and merge unknown license detection (this depends on having 4. Go to two-level reporting of detections for licenses done)
- Update scancode-analyze to the new  two-level reporting of license detections
- Revamp how common list of suprrious licenses are detected (this is a bug)
- Use important key phrases for license detection https://github.com/nexB/scancode-toolkit/issues/2637

