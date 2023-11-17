AboutCode global Roadmap
========================

python-inspector
Support all package manifests beyond req and setup.py

SCIO: ScanCode.io, pipelines for SCA
-------------------------------------

Compositition analysis of Deployed binaries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Build pipelines for key tech stacks. For each of these automate the end-to-end
analysis of a package binaries mapping it back to it sources and matching it
upstream to its PurlDB origin:

- for Java
- for JavaScript, CSS
- for C/C++ ELFs
- for C/C++ WinPE
- for C/C++ Mach-O
- for .Net, C#
- for Golang
- for Android apk
- for Python
- for Rust
- for Ruby


Matching pipeline
~~~~~~~~~~~~~~~~~~

Build a dedicated pipeline to matching (client side)


Scan TODO/Review app
~~~~~~~~~~~~~~~~~~~~~

- Build an app in SCIO to automate flagging scan items that needs review or attention.
- Create a UI and backend to organize the scan review.
- Consider including and merging the "scantext" license detection review app


Pre-built container image(s)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Build and publish container images
- Consider building a single image for CLI deployments
- Consider publishe the app image for standalone CLI deployments

Package management
~~~~~~~~~~~~~~~~~~~~

- Adopt the two levels manifests/package instances
- Refactor dependencies as deps and requirements


Deploy free analysis public server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Consider sponsorship from Amazon/Google/Azure

Create and document standard CI/CD integrations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- GitHub
- GitLab
- Azure


SCTK: ScanCode Toolkit
-----------------------

License detection quality improvements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Include automatic key phrases in license detection rules
  Use important key phrases for license detection https://github.com/nexB/scancode-toolkit/issues/2637

- Add required phrase automatically + unknown detection in licenses plus testing
- More license detection bugs reported recently

- Detect summary for all packages, and populate more package fields correctly like copyright/holders

    - We can report the declared license and other licenses in the license summary
      of a full scan. The primary license is based; next is to do the
      same across each package found nested in a scanned codebase. And also compute
      an individual license clarity score for each these.


- license expression simplify and license expression category


Improve package detection
~~~~~~~~~~~~~~~~~~~~~~~~~~

- Create synthethic, private packages from non-packaged files based on license and copyright  
- Create simplified purl-only lightweight package detection
- Evolve model for dependencies towards requirements and true dependencies
- Track private non-published packages

Primary copyright detection for packages

- This is closely tied to the primary license detection and should focus
  on package manifests and key files. 
- Support copyright parsing from all package ecosystems.



Published improved release packagings/bundles/installers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Publish smaller wheels with a single focus for easier integration as a library

- Release self-contained app(s) for ease of use, bundled with a Python and everything on it:

  - extractcode
  - scancode proper
  - packagedcode only
  - licensedcode only
  - cluecode only

- Adopt Python 3.12
- Adopt macOS and Linux on ARM


ABCTK: AboutCode Toolkit
----------------------------

- add support for patterns for docoumented resources
- add support for exclude for docoumented resources
- document deployed resource for a development resource
 

PURLDB: PurlDB
----------------

- purl2all: On demand indexing for all supported package ecosystems
- purl2sym: Collect source and binary symbols
- index-time matching to find the true origin
- implement multi-tier indexing: purl/metadata/archive/files
- MatchCode matching engine

  - embed a SCIO with a matching pipeline for match a whole codebase at once
    - expore new endpoint for matching whole codebase
  - support multiple SCIO workers for indexing
  - implement proper ranking of matched code results
  - refactor directory matching to be a pre-matching step to file matching


VCIO: VulnerableCode.io
------------------------

- Adopt VulnTotal model throughout
- Log advisory history
- Add vulnerable code reachability
- Add vulnerable code required context/config 
- Add more upstream resources
- Deploy purlsync public pilot


PURL: purl and vers specs
--------------------------

- Merge and advertize vers spec.
- Standardize purl with ECMA


INSPECTORS: misc package and technology inspectors
----------------------------------------------------

- Universal Inspector/DependentCode

  - Resolve any purl dependencies
  - Non-vulnerable dependency resolution

- Inspector for Java and Android DEX

  - Decompile and collect binary symbols.
  - Collect source symbols
  - Resolve dependencies for Gradle, SBT and Maven. 

- Inspector for JavaScript, CSS

  - Decompile/deminify and collect bundled and minified symbols.
  - Analyze map files
  - Collect source symbols
  - Resolve dependencies for npm, yarn and pnpm. 

- Inspector for C/C++
  - Collect source symbols

- Inspector for ELFs

  - Decompile and collect binary symbols.
  - Collect DWARFs and ELFs section symbols
  - Resolve dependencies for pkgconfig and ldd

- Inspector for WinPE

  - Decompile and collect binary symbols.
  - Collect winpdb symbols

- Inspector for Mach-O

  - Decompile and collect binary symbols.
  - Collect DWARFs and ELFs section symbols

- Inspector for .Net, C#

  - Decompile and collect binary symbols from assemblies (see also WinPE)
  - Collect source symbols
  - Resolve dependencies for nuget/dotnet (completed)

- Inspector for Golang

  - Decompile and collect binary symbols from pclntab
  - Collect source symbols
  - Resolve dependencies

- Inspector for Python

  - Decompile and collect binary symbols from bytecode
  - Collect source symbols
  - Resolve dependencies (completed)

- Inspector for Rust

  - Decompile and collect binary symbols
  - Collect source symbols
  - Resolve dependencies

- Inspector for Swift

  - Decompile and collect binary symbols
  - Collect source symbols
  - Resolve dependencies

- Inspector for Dart/Flutter

  - Decompile and collect binary symbols
  - Collect source symbols
  - Resolve dependencies

- Inspector for Ruby

  - Collect source symbols
  - Resolve dependencies

- Inspector for Debian

  - Parse Debian formats (completed)
  - Parse installed database (completed)
  - Compare versions (completed)
  - Resolve dependencies

- Inspector for Alpine

  - Parse Alpine formats (completed)
  - Parse installed database (completed)
  - Compare versions (completed)
  - Resolve dependencies

- Inspector for RPM

  - Parse RPM formats (partially completed)
  - Parse installed database (completed)
  - Compare versions (completed)
  - Resolve dependencies

- Inspector for containers

  - Parse container images formats and manifests (completed)


Other libraries
-----------------

- FetchCode: support all supported package ecosystems, use in purlDB and SCIO
- univers: support all supported package ecosystems
- license-expression : update to support latest SPDX updates, auto-update bundled licenses

