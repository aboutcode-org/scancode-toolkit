Home
====

ScanCode does scan code to detect packages and dependencies, licenses,
copyrights and more.


Why ScanCode?
-------------

Discovering the origin and license for a software component is important, but it
is often much harder to accomplish than it should be because:

- A typical software project may reuse tens or thousands of third-party software components
- Software authors do not always provide copyright and license information
- Copyright and license information that is provided may be hard to find and interpret


ScanCode tries to address these issues by offering:

- A simple command line approach that runs on Windows, Linux, and macOS
- A comprehensive code scanner that can detect origin and license information in
  codebase files, including binaries
- A comprehensive set of package manifests and lockfile parsers to report direct
  and pinned dependencies
- Your choice of JSON or other output formats (YAML, SPDX, HTML, CSV) for
  integration with other tools
- Well-tested, easy to hack, and well-documented code
- A plugin system for easily adding new Functionality to Scans.
- Extensive documentation and support.
- We release of the code and reference data under permissive licenses (Apache
  2.0 and CC-BY-4.0)
- ScanCode.io to assemble scripted and specialized code analysis pipelines with
  a web-based analysis server
- ScanCode workbench for desktop-based scans visualization

ScanCode is recognized as the industry leading engine for license and copyright
detection and used as the basis of several open source compliance efforts in
open source projects and companies. Its detection engine is embedded in the
most advanced open source and commercial tools available today for Software
Composition Analysis.


What does ScanCode-Toolkit do?
------------------------------

ScanCode detects and normalizes origin, dependencies, licensing and other
related information in your code:

- by parsing package manifests and dependencies lock files to a normalized
  metadata model and assigning each an identifying `Package URL
  <https://github.com/package-url/purl-spec>`_,

- by detecting license tags, notices and texts in text and binaries using the
  world's most comprehensive database of license texts and notices and a unique
  combination of techniques,

- by recognizing copyright statements using an advanced natural language parsing
  grammar and detecting other origin clues (such as emails, urls, and authors)

Using this data you can:

- Discover the origin and license of the open source and third-party software
  components that you use,

- Discover direct dependent packages and indirect pinned or locked dependencies,

- Assemble a software component inventory of your codebase, and report the data
  using standard SBOM formats,

- Use this data as the input to:

  - open source license compliance obligations such as attribution and redistribution.
  - open source package vulnerability detection.


How does it work?
-----------------

Given a code directory, ScanCode will "scan code":

- Extract files from any archive using a `universal archive extractor
  <https://github.com/aboutcode-org/extractcode>`_

- Collect an inventory of the code files and classify the code using file types
- Extract texts from binary files as needed
- Use an extensible rules engine to detect open source license text, notices
  tags, mentions and license expressions with over 31,000 detection rules.

- Use a specialized natural language parser and grammar to capture copyright
  statements

- Identify packaged code and collect metadata from packages by parsing the
  manifest and lockfiles (and in some cases also the installed databases for
  system packages) for these package types: .ABOUT, Alpine Linux apk as packages
  or installed, Android apk, Autotools, Bazel, JS Bower, Buck, Msft Cab, Rust
  Cargo, Chef, Chrome, PHP Composer, Conda, Perl CPAN, R CRAN, Debian deb as
  packages or installed, Apple dmg, Java EAR, FreeBSD, Ruby Gem, Go modules,
  Haxe, InstallShield, iOS ipa, ISO disk images, Apache IVY, Java JAR, JBoss
  SAR, Maven, JS Meteor, Mozilla Extension, Msft MSI, JS npm, NSIS Installer,
  NuGet, Ocaml OPAM, Cocoapods, Dart Pub, Python PyPI wheel and related,
  structured README, RPMs as packages or installed, Shell archive, Squashfs,
  Java WAR, Msft Update Manifest, and Windows Executable.

- Report the results in the formats of your choice (JSON, YAML, CSV, SPDX, etc.)
  for integration with other tools


ScanCode is written in Python and also uses other open source packages.


Alternative?
--------------

There are several utilities that do some of what ScanCode does - for instance
you can grep files for copyright and license text. This may work well for simple
cases - e.g. at the single whole license text files and well structured
copyright statements, but we created ScanCode for ourselves because this
approach does not help you to see the recurring patterns of licenses and other
origin history clues at scale.

You can consider other tools such as:

- FOSSology (open source, written in C, Linux only, GPL-licensed)


History
-------

ScanCode was originally created by nexB to support our software audit consulting
services. We have used and continuously enhanced the underlying toolkit for over
12 years. We decided to release ScanCode as open source software to give
software development teams the opportunity to perform as much of the software
audit function as they like on their own.

Thank you for giving ScanCode a try!

.. include::  /rst_snippets/other_imp_doc.rst
