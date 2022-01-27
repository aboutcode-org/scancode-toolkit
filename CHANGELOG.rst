Changelog
=========

31.0.0 (next, roadmap)
-----------------------
Documentation Update
~~~~~~~~~~~~~~~~~~~~~~~~
- Changed scancode -clpieu --csv output.html samples to scancode -clpieu --html-app output.html samples to publish the result in [html-app] at
[output-format.html](https://scancode-toolkit.readthedocs.io/en/latest/cli-reference/output-format.html#html-app-file)
 

Important API changes:
~~~~~~~~~~~~~~~~~~~~~~~~

- Main package API function `get_package_infos` is now deprecated, and is replaced by
  `get_package_manifests`.

- The data structure of the JSON output has changed for copyrights, authors
  and holders: we now use proper name for attributes and not a generic "value".

- The data structure of the JSON output has changed for licenses: we now
  return match details once for each matched license expression rather than
  once for each license in a matched expression. There is a new top-level
  "license_references" attributes that contains the data details for each
  detected licenses only once. This data can contain the reference license text
  as an option.

- The data structure of the JSON output has changed for packages: we now
  return "package_manifests" package information at the manifest file-level
  rather than "packages". There is a a new top-level "packages" attribute
  that contains each package instance that can be aggregating data from
  multiple manifests for a single package instance.

- The data structure for HTML output has been changed to include emails and
  urls under the  "infos" object. Now HTML template will output holders,
  authors, emails, and urls into separate tables like "licenses" and "copyrights".

- The data structure for CSV output has been changed to rename the Resource
  column to "path". The "copyright_holder" has been ranmed to "holder"


Copyright detection:
~~~~~~~~~~~~~~~~~~~~

- The data structure in the JSON is now using consistently named attributes as
  opposed to a plain value.
- Several copyright detection bugs have been fixed.
- French and German copyright detection is improved.
- Some spurious trailing dots in holders are not stripped.


License detection:
~~~~~~~~~~~~~~~~~~~

- There have been significant license detection rules and licenses updates:

  - XX new licenses have been added, 
  - XX existing license metadata have been updated,
  - XXXX new license detection rules have been added, and
  - XXXX existing license rules have been updated.
  - XXXX existing false positive license rules have been removed (see below).
  - The SPDX license list has been updated to the latest v3.15

- The rule attribute "only_known_words" has been renamed to "is_continuous" and its
  meaning has been updated and expanded. A rule tagged as "is_continuous" can only
  be matched if there are no gaps between matched words, be they stopwords, extra
  unknown or known words. This improves several false positive license detections. 
  The processing for "is_continous" has been merged in "key phrases" processing
  below.

- Key phrases can now be defined in RULEs by surrounding one or more words with
  `{{` and `}}`. When defined a RULE will only match when the key phrases match
  exactly. When all the text of rule is a "key phrase", this is the same as being
  "is_continuous".

- The "--unknown-licenses" option now also detects unknown licenses using a
  simple and effective ngrams-based matching in area that are not matched or
  weakly matched. This helps detects things that look like a license but are not
  yet known as licenses.

- False positive detection of "license lists" like list seen in license and
  package management tools has been entirely reworked. Rather than using
  thousands of small false positive rules, there is now a new filter to detect
  long run of license references and tags that are typical of license lists.
  As a results, thousands of rules have been replaced by a simpler filter, and
  the license detection is both more accurate, faster and has fewer false
  positives.

- The new license flag "is_generic" tags licenses that are "generic" licenses
  such as "other-permissive" or "other-copyleft". This is not yet
  returned in the JSON API.

- When scanning binary files, the detection of single word rules is filtered when
  surrounded by gibberish or is using mixed case. For instance $#%$GpL$ is a false
  positive and is no longer reported.

- Several rules we tagged as is_license_notice incorrectly but were references
  and have been requalified as is_license_reference. All rules made of a single
  ord have been requalified as is_license_reference if they were not qualified
  this way.

- Matches to small license rules (with small defined as under 15 words)
  that are scattered on too many lines are now filtered as false matches.

- Small, two-words matches that overlap the previous or next match by
  by the word "license" and assimilated are now filtered as false matches.


Package detection:
~~~~~~~~~~~~~~~~~~

- We now support new package manifest formats:
  - OpenWRT packages.
  - Yocto/BitBake .bb recipes.

- Major changes in packages detection and reporting, codebase-level attribute `packages`
  with one or more "package_manifests" and files for the packages are reported.
  The specific changes made are:

  - The resource level attribute `packages` has been renamed to `package_manifests`,
    as these are really package manifests that are being detected.

  - A new top-level attribute `packages` has been added which contains package
    instances created from package_manifests detected in the codebase.

  - A new codebase level attribute `packages` has been added which contains package
    instances created from package_manifests detected in the codebase.


Outputs:
~~~~~~~~

 - Add new outputs for the CycloneDx format.
   The CLI now exposes options to produce CycloneDx BOMs in either JSON or XML format


Output version
--------------

Scancode Data Output Version is now 2.0.0.

Changes:

- rename resource level attribute `packages` to `package_manifests`.
- add top-level attribute `packages`.


30.1.0 - 2021-09-25
--------------------

This is a bug fix release for these bugs:

- https://github.com/nexB/scancode-toolkit/issues/2717

We now return the package in the summaries as before.

There is also a minor API change: we no longer return a count of "null" empty
values in the summaries for license, copyrights, etc.


Thank you to:
- Thomas Druez @tdruez 



30.0.1 - 2021-09-24
--------------------

This is a minor bug fix release for these bugs:

- https://github.com/nexB/commoncode/issues/31
- https://github.com/nexB/scancode-toolkit/issues/2713

We now correctly work with all supported Click versions. 

Thank you to:
- Konstantin Kochin @vznncv
- Thomas Druez @tdruez 



30.0.0 - 2021-09-23
--------------------

This is a major release with new features, and several bug fixes and
improvements including major updates to the license detection.

We have droped using calendar-based versions and are now switched back to semver
versioning. To ensure that there is no ambiguity, the new major version has been
updated from 21 to 30. The primary reason is that calver was not helping
integrators to track major version changes like semver does.

We also have introduced a new JSON output format version based on semver to
version the JSON output format data structure and have documented the new
versioning approach.


Package detection:
~~~~~~~~~~~~~~~~~~

- The Debian packages declared license detection in machine readable copyright
  files and unstructured copyright has been significantly improved with the
  tracking of the detection start and end line of a license match. This is not
  yet exposed outside of tests but has been essential to help improve detection.

- Debian copyright license detection has been significantly improved with new
  license detection rules.

- Support for Windows packages has been improved (and in particular the handling
  of Windows packages detection in the Windows registry).

- Support for Cocoapod packages has been significantly revamped and is now
  working as expected.

- Support for PyPI packages has been refined, in particular package descriptions.



Copyright detection:
~~~~~~~~~~~~~~~~~~~~

- The copyright detection accuracy has been improved and several bugs have been
  fixed.


License detection:
~~~~~~~~~~~~~~~~~~~

There have been some significant updates in license detection. We now track
34,164 license and license notices:

  - 84 new licenses have been added, 
  - 34 existing license metadata have been updated,
  - 2765 new license detection rules have been added, and
  - 2041 existing license rules have been updated.


- Several license detection bugs have fixed.

- The SPDX license list 3.14 is now supported and has been synced with the
  licensedb. We also include the version of the SPDX license list in the
  ScanCode YAML, JSON and the SPDX outputs, as well as display it with the
  "--version" command line option.

- Unknown licenses have a new flag "is_unknown" in their metadata to identify
  them explicitly. Before that we were just relying on the naming convention of
  having "unknown" as part of a license key.

- Rules that match at least one unknown license have a flag "has_unknown" set
  and returned in the match results.

- Experimental: License detection can now "follow" license mentions that
  reference another file such as "see license in COPYING" where we can relate
  this mention to the actual license detected in the COPYING file. Use the new
  "--unknown-licenses" command line option to test this new feature.
  This feature will evolve significantly in the next version(s).


Outputs:
~~~~~~~~

- The SPDX output now has the mandatory ids attribute per SPDX spec. And we
  support SPDX 2.2 and SPDX license list 3.14.


Miscellaneous
~~~~~~~~~~~~~~~

- There is a new "--no-check-version" CLI option to scancode to bypass live,
  remote outdated version check on PyPI

- The scan results and the CLI now display an outdated version warning when
  the installed ScanCode version is older than 90 days. This is to warn users
  that they are relying on outdated, likely buggy, insecure and inaccurate scan
  results and encourage them to update to a newer version. This is made entirely
  locally based on date comparisons.

- We now display again the command line progressbar counters correctly.

- A bug has been fixed in summarization.

- Generated code detection has been improved with several new keywords.


Thank you!
~~~~~~~~~~~~

Many thanks to the many contributors that made this release possible and in
particular:

- Akanksha Garg @akugarg
- Armijn Hemel @armijnhemel 
- Ayan Sinha Mahapatra @AyanSinhaMahapatra
- Bryan Sutula @sutula
- Chin-Yeung Li @chinyeungli
- Dennis Clark @DennisClark
- dyh @yunhua-deng
- Dr. Frank Heimes @FrankHeimes 
- gunaztar @gunaztar
- Helio Chissini de Castro @heliocastro
- Henrik Sandklef @hesa
- Jiyeong Seok @dd-jy
- John M. Horan @johnmhoran
- Jono Yang @JonoYang
- Joseph Heck @heckj
- Luis Villa @tieguy
- Konrad Weihmann @priv-kweihmann
- mapelpapel @mapelpapel
- Maximilian Huber @maxhbr
- Michael Herzog @mjherzog
- MMarwedel @MMarwedel
- Mikko Murto @mmurto
- Nishchith Shetty @inishchith 
- Peter Gardfjäll @petergardfjall
- Philippe Ombredanne @pombredanne
- Rainer Bieniek @rbieniek 
- Roshan Thomas @Thomshan
- Sadhana @s4-2
- Sarita Singh @itssingh
- Siddhant Khare @Siddhant-K-code
- Soim Kim @soimkim
- Thomas Druez @tdruez 
- Thorsten Godau @tgodau
- Yunus Rahbar @yns88


v21.8.4
---------

This is a minor bug fix release primarily for Windows installation.
There is no feature change.

Installation:
~~~~~~~~~~~~~~~~~~

- Application installation on Windows works again. This fixes #2610
- We now build and test app bundles on all supported Python versions: 3.6 to 3.9


Thank you to @gunaztar for reporting the #2610 bug

Documentation:
~~~~~~~~~~~~~~~~~~

- Documentation is updated to reference supported Python versions 3.6 to 3.9



v21.7.30
---------

This is a minor release with several bug fixes, major performance improvements
and support for new and improved package formats


Many thanks to every contributors that made this possible and in particular:

- Abhigya Verma @abhi27-web
- Ayan Sinha Mahapatra @AyanSinhaMahapatra
- Dennis Clark @DennisClark
- Jono Yang @JonoYang
- Mayur Agarwal @mrmayurgithub 
- Philippe Ombredanne @pombredanne
- Pierre Tardy @tardyp


Outputs:
~~~~~~~~

 - Add new YAML-formatted output. This is exactly the same data structure as for
   the JSON output
 - Add new Debian machine readable copyright output.
 - The CSV output "Resource" column has been renamed to "path".
 - The SPDX output now has the mandatory DocumentNamespace attribute per SPDX specs #2344


Copyright detection:
~~~~~~~~~~~~~~~~~~~~

 - The copyright detection speed has been significantly improved with the tests
   taking roughly 1/2 of the time to run. This is achieved mostly by replacing
   NLTK with a the minimal and simplified subset we need in a new library named
   pygmars.

License detection:
~~~~~~~~~~~~~~~~~~~

 - Add new licenses: now tracking 1763 licenses
 - Add new license detection rules: now tracking 29475 license detection rules
 - We have also improved license expression parsing and processing


Package detection:
~~~~~~~~~~~~~~~~~~

 - The Debian packages declared license detection has been significantly improved.
 - The Alpine packages declared license detection has been significantly improved.
 - There is new support for shell parsing and Alpine packages APKBUILD data collection.
 - There is new support for various Windows packages detection using multiple
   techniques including MSI, Windows registry and several more.
 - There is new support for Distroless Debian-like installed packages.
 - There is new support for Dart Pub package manifests.


v21.6.7
--------

This is a major new release with important security and bug fixes, as well as
significant improvement in license detection.


Many thanks to every contributors that made this possible and in particular:

- Akanksha Garg @akugarg
- Ayan Sinha Mahapatra @AyanSinhaMahapatra
- Dennis Clark @DennisClark
- François Granade @farialima
- Hanna Modica @hanna-modica
- Jelmer Vernooĳ @jelmer
- Jono Yang @JonoYang
- Konrad Weihmann @priv-kweihmann
- Philippe Ombredanne @pombredanne
- Pierre Tardy @tardyp
- Sarita Singh @itssingh
- Sebastian Thomas @sebathomas
- Steven Esser @majurg
- Till Jaeger @LeChasseur 
- Thomas Druez @tdruez



Breaking API changes:
~~~~~~~~~~~~~~~~~~~~~

 - The configure scripts for Linux, macOS and Windows have been entirely
   refactored and should be considered as new. These are now only native scripts
   (.bat on Windows and .sh on POSIX) and the Python script etc/configure.py
   has been removed. Use the PYTHON_EXECUTABLE environment variable to point to
   alternative non-default Python executable and this on all OSes.


Security updates:
~~~~~~~~~~~~~~~~~

 - Update minimum versions and pinned version of thirdparty dependencies
   to benefit from latest improvements and security fixes. This includes in
   particular this issues:

     - pkg:pypi/pygments: (low severity, limited impact) CVE-2021-20270, CVE-2021-27291
     - pkg:pypi/lxml: (low severity, likely no impact) CVE-2021-28957
     - pkg:pypi/nltk: (low severity, likely no impact) CVE-2019-14751
     - pkg:pypi/jinja2: (low severity, likely no impact) CVE-2020-28493, CVE-2019-10906
     - pkg:pypi/pycryptodome: (high severity) CVE-2018-15560 (dropped since no
       longer used by pdfminer)


Outputs:
~~~~~~~~

 - The JSON output packages section has a new "extra_data" attributes which is
   a JSON object that can contain arbitrary data that are specific to a package
   type.


License detection:
~~~~~~~~~~~~~~~~~~~

 - The SPDX license list has been update to 3.13

 - Add 42 new and update 45 existing licenses.

 - Over 14,300 new and improved license detection rules have been added. A large
   number of these (~13,400) are to avoid false positive detection.


Copyright detection:
~~~~~~~~~~~~~~~~~~~~

 - Improved speed and fixed some timeout issues. Fixed minor misc. bugs.

 - Allow calling copyright detection from text lines to ease integration


Package detection:
~~~~~~~~~~~~~~~~~~

 - A new "extra_data" dictionary is now part of the "packages" data in the
   returned JSON. This is used to store arbitrary type-specific data that do
   cannot be fit in the Package data structure.

 - The Debian copyright files license detection has been reworked and
   significantly improved.

 - The PyPI package detection and manifest parsing has been reworked and
   significantly improved.
   
 - The detection of Windows executables and DLLs metadata has been enabled.
   These metadata are returned as packages.


Other:
~~~~~~~
 - Most third-party libraries have been updated to their newer versions. Some
   dependency constraints have been relaxed to help some usage as a library.

 - The on-commit CI tests now validate that we can install from PyPI without
   problem.

 - Fix several installation issues.

 - Add new function to detect copyrights from lines.



v21.3.31
--------

This is a major version with no breaking API changes. Heads-up: the next version
will bring up some significant API changes summarized above.


Security:
~~~~~~~~~

 - Update dependency versions for security fixes.


License scanning:
~~~~~~~~~~~~~~~~~

 - Add 22 new licenses and update 71 existing licenses

 - Update licenses to include the SPDX license list 3.12

 - Improve license detection accuracy with over 2,300 new and updated license
   detection rules

 - Undeprecate the regexp license and deprecate the hs-regexp-orig license

 - Improve license db initial load time with caching for faster scancode
   start time

 - Add experimental SCANCODE_LICENSE_INDEX_CACHE environment variable to point
   to an alternative directory where the license index cache is stored (as
   opposed to store this as package data.)

 - Ensure that license short names are not more than 50 characters long

 - Thank you to:
    - Dennis Clark @DennisClark
    - Chin-Yeung Li @chinyeungli
    - Armijn Hemmel @armijnhemel
    - Sarita Singh @itssingh
    - Akanksha Garg @akugarg


Copyright scanning:
~~~~~~~~~~~~~~~~~~~

 - Detect SPDX-FileCopyrightText as defined by the FSFE Reuse project
   Thank you to Daniel Eder @daniel-eder

 - Fix bug when using the --filter-clues command line option
   Thank you to Van Lindberg @VanL

 - Fixed copyright truncation bug
   Thank you to Akanksha Garg @akugarg


Package scanning:
~~~~~~~~~~~~~~~~~

 - Add support for installed RPMs detection internally (not wired to scans)
   Thank you to Chin-Yeung Li @chinyeungli

 - Improve handling of Debian copyright files with faster and more
   accurate license detection
   Thank you to Thomas Druez @tdruez 
   
 - Add new built-in support for installed_files report. Only available when
   used as a library.

 - Improve support for RPM, npm, Debian, build scripts (Bazel) and Go packages
   Thank you to:
   - Divyansh Sharma @Divyansh2512
   - Jonothan Yang @JonoYang
   - Steven Esser @majurg

 - Add new support to collect information from semi-structured Readme files
   and related metadata files. 
   Thank you to Jonothan Yang @JonoYang and Steven Esser @majurg


Outputs:
~~~~~~~~~

 - Add new Debian copyright-formatted output.
   Thank you to Jelmer Vernooĳ @jelmer
   
 - Fix bug in --include where directories where not skipped correctly
   Thank you to Pierre Tardy @tardyp


Misc. and documentation improvements:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 - Update the way tests assertions are made
   Thank you to Aditya Viki @adityaviki

 - Thank you to Aryan Kenchappagol @aryanxk02


v21.2.25
--------

Installation:
~~~~~~~~~~~~~

 - Resolve reported installation issues on macOS, Windows and Linux
 - Stop using extras for a default wheel installation
 - Build new scancode-toolkit-mini package with limited dependencies for use
   when packaging in distros and similar
 - The new Dockerfile will create smaller images and containers.
   Thank you to Viktor Tiulpin @tiulpin

License scanning:
~~~~~~~~~~~~~~~~~

 - Over 150 new and updated licenses
 - Support the latest SPDX license list v3.11
 - Improve license detection accuracy with over 740 new and improved license
   detection rules
 - Fix license cache handling issues

Misc.:
~~~~~~
 - Update extractcode, typecode and their native dependencies for better support
   of latests versions of macOS.


v21.2.9
-------

Security:
~~~~~~~~~

 - Update vulnerable LXML to version 4.6.2 to fix
   https://nvd.nist.gov/vuln/detail/CVE-2020-27783
   This was detected thanks to https://github.com/nexb/vulnerablecode

Operating system support:
~~~~~~~~~~~~~~~~~~~~~~~~~

 - Drop support for Python 2  #295
 - Drop support for 32 bits on Windows #335
 - Add support for Python 64 bits on Windows 64 bits #335
 - Add support for Python 3.6, 37, 3.8 and 3.9 on Linux, Windows and macOS.
   These are now tested on Azure.
 - Add deprecation message for native Windows support #2366

License scanning:
~~~~~~~~~~~~~~~~~

 - Improve license detection accuracy with over 8400 new license detection rules
   added or updated
 - Remove the previously deprecated --license-diag option
 - Include pre-built license index in release archives to speed up start #988
 - Use SPDX LicenseRef-scancode namespace for all licenses keys not in SPDX
 - Replace DEJACODE_LICENSE_URL with SCANCODE_LICENSEDB_URL at
   https://scancode-licensedb.aboutcode.org #2165
 - Add new license flag in license detection results "is_license_intro" that
   is used to indicate that a license rule is a short license introduction
   statement (that typically may be reported as some unknown license)

Package scanning:
~~~~~~~~~~~~~~~~~

 - Add detection of package-installed files
 - Add analysis of system package installed databases for Debian, OpenWRT and
   Alpine Linux packages
 - Add support for Alpine Linux, Debian, OpenWRT.

Copyright scanning:
~~~~~~~~~~~~~~~~~~~

 - Improve detection with minor grammar fixes

Misc.:
~~~~~~

 - Adopt a new calendar date-based versioning for scancode-toolkit version numbers
 - Update thirdparty dependencies and built-in plugins
 - Allow installation without extractcode and typecode native plugins. Instead
   one can elect to install these or not to have a lighter footprint if needed.
 - Update configuration and bootstrap scripts to support a new PyPI-like
   repository at https://thirdparty.aboutcode.org/pypi/
 - Create new release scripts to populate released archives with just the
   required wheels of a given OS and Python version.
 - Updated scancode.bat to handle % signs in the arguments #1876


v3.2.3 (2020-10-27)
-------------------

Notable changes:
~~~~~~~~~~~~~~~~

 - Collect Windows executable metadata #652
 - Fix minor bugs
 - Add Dockerfile to build docker image from ScanCode sources #2265


v3.2.2rc3 (2020-09-21)
----------------------

Notable changes:
~~~~~~~~~~~~~~~~

 - Use commoncode, typecode and extractcode as external standalone packages #2233


v3.2.1rc2 (2020-09-11)
----------------------

Minor bug fixes:
~~~~~~~~~~~~~~~~

 - Do not fail if Debian status is missing #2224
 - Report correct detected license text in binary #2226 #2227


v3.2.0rc1 (2020-09-08)
----------------------

 - Improve copyright detection #2140
 - Add new license rules for "bad" licenses #1899 @viragumathe5
 - Improve copyright detection @WizardOhio24
 - Improve tests @hanif-ali
 - Add and improve support for package manifest for #2080 Go, Ruby gem gemspec, Cocoapod podspec, opam, Python PKG-INFO - Rohit Potter @rpotter12
 - Add and improve support for package lockfiles for Pipfile.lock, requirements.tx, Cargo.lock - Rohit Potter @rpotter12
 - Add new --max-depth option to limit sca depth - Hanif Ali @hanif-ali
 - Add initial Debian packaging - @aj4ayushjain
 - Add new documentation web site and documentation generation system 
 - The "headers" attribute in JSON outputs now contains a 'duration' field. #1942
 - Rework packaging and third-party support handling: Create new scripts and
   process to provision, install and manage third-party dependencies - Abhishek Kumar @Abhishek-Dev09
 - Improve CSV output and fix manifest path bug #1718 Aditya Viki8 
 - Add new documentation, as well as tools and process. Ayan Sinha Mahapatra
 - Add new license detection rules - Ayan Sinha Mahapatra
 - Improve license detection #1999 - Bryan Sutula
 - Correct CC0 license #1984 - Carmen Bianca Bakker
 - Add documentation for the usage of `cpp_includes` plugin - Chin Yeung Li
 - Improve andling of npm package-lock.json #1993 - Chin Yeung Li
 - Add new license detection rules - Gaupeng
 - Improve documentation - Issei Horie
 - Improve consolidation plugin - Jono Yang @JonoYang
 - Improve Python wheels detection #1749 - Jono Yang @JonoYang
 - Add support for BUCK and Bazel build scripts #1678 - Jono Yang @JonoYang
 - Improve handing of ignores #1748 - Jono Yang @JonoYang
 - Improved package models #1773 #1532 #1678 #1771 #1791 #1220 - Jono Yang @JonoYang
 - Parse package lock files for Composer #1850, Yarn #1220, Gemfile.lock #1885 - Jono Yang @JonoYang
 - Add parser for Alpine 'installed' file #2061 - Jono Yang @JonoYang
 - Add support for Debian packagesinstalled files  #2058 - Jono Yang @JonoYang
 - Add new licenses -@Pratikrocks
 - Improve support for DWARF, ELF and C++ include plugins #1712 #1752#1762 - Li Ha @licodeli
 - Add support for parsing java class files #1712 #1726- Li Ha @licodeli
 - Add new license detection rules - @MankaranSingh
 - Add new duration field to JSON output #1937 - @MankaranSingh
 - Add new rule for GPL historical note #1794 - Martin Petkov
 - Add --replace-originals flag to extractcode -Maximilian Huber
 - Improve Documentation - Michael Herzog
 - Add new checksum type for sha256 - Nitish @nitish81299
 - Improve documentation - Philippe Ombredanne
 - Add new license detection rules and improve detection #1777 #1720 #1734 #1486 #1757 #1749 #1283 #1795 #2214 #1978
 - Add new license detection rules and improve detection #2187 #2188 #2189 #1904 #2207 #1905 #419 #2190 #1910 #1911 
 - Add new license detection rules and improve detection #1841 #1913 #1795 #2124 #2145 #1800 #2200 #2206 #2186
 - Allow to call "run_scan" as a function #1780 
 - Update license data to SPDX 3.7 #1789
 - Collect matched license text correctly including with Turkish diacritics #1872
 - Detect SPDX license identifiers #2007
 - Add Windows 64 as supported platform #616
 - Add and improve support for archive with lzip, lz4 and zstd #245 #2044 #2045
 - Detect licenses in debian copyright files #2058
 - Improve copyright detections #2140
 - Improve FSF, unicode and Perl license detection - Qingmin Duanmu
 - Add COSLi and ethical licenses - Ravi @JRavi2
 - Add tests for extract.py and extract_cli.py - Ravi @JRavi2
 - Add a new copyright to grammar - Richard Menzies
 - Fix external URLs in documentation - Ritiek Malhotra
 - Improve doc - Rohit Potter
 - Correct configure on Windows and improve doc - Sebastian Schuberth
 - Improve license detection. Add tests for #1758 and #1691- Shankhadeep Dey
 - Improve tests of utility code - Shivam Chauhan
 - Improve tests and documentation - Shivam Sandbhor @sbs2001
 - Add new hippocratic license #1739 - Shivam Sandbhor
 - Add new and improved licenses - Steven Esser @majurg
 - Improve test suite - Steven Esser @majurg
 - Improve fingerprint plugin #1690 - Steven Esser @majurg
 - Add support for Debian packages #2058  - Steven Esser @majurg
 - Improve FreeBSD support - @aj4ayushjain
 - Add new plugins to get native code from install packages - @aj4ayushjain
 - Fix license name and data - Thomas Steenbergen
 - Improve runtime support for FreeBSD #1695  @knobix
 - Update macOS image on azure pipeline @TG1999
 - Improve documentation - @Vinay0001     


v3.1.1 (2019-09-04)
-------------------

Major new feature:

 - Complete port to Python 3.6+ #295 @Abhishek-Dev09

New features:

 - Improve package manifest support for #1643 RPMs, #1628 Cran, Python #1600, Maven #1649 Chef #1600 @licodeli @JonoYang
 - Add plugin to collect ELF and LKM clues #1685 @licodeli
 - Add runtime support for FreeBSD #1695  @knobix
 - Add support to extract lzip archives #245 #989
 - Add new consolidation plugin #1686 @JonoYang

Other features and fixes:

 - Improve license detection #1700 #1704 #1701
 - Improve copyright detection #1672
 - Improve handling of plugins for native binaries @aj4ayushjain
 - Add CODE OF CONDUCT @inishchith
 - Fix extractcode error #749
 - Add new version notification #111 #1688 @jdaguil 


v3.1.0 (2019-08-12)
-------------------

 - Add partial suport for Python 3.6+ #295 @Abhishek-Dev09
 - Add plugin to collect dwarf references #1167 @licodeli
 - Add fingerprint plugin #1651 @arnav-mandal1234
 - Add summary and consolidation plugin #1673
 - Improve license detection #1606 #1659 #1675 
 - Improve copyright detection #1672
 - Add owned files to package manifests #1554 @JonoYang
 - Improve package manifest support for Conda #1147, Bower and Python @licodeli
 - Add an option to include the original matched license text #1668 #260 @LemoShi


v3.0.2 (2019-02-15)
-------------------

Minor bug fixes:

 - A tracing flag was turned on in the summary module by mistake. Reported by @tdruez #1374
 - Correct a Maven parsing error. Reported and fixed by @linexb #1373
 - Set proper links in the README. Reported and fixed by @sschubert #1371
 - No changes from v3.0.1


v3.0.0 (2019-02-14)
-------------------

License detection:
 - Add new and improved licenses and license detection rules #1334 #1335 #1336 #1337 ##1357 
 - Fix-up the license text inside the `bsl-*.LICENSE` files #1338 by @fviernau
 - Add tests for commnon NuGet license bare URLs (until recently NuGet nupsec
   only had a license URL as licensing documentation) 
 - Add a license for the `PSK` contributions to OpenSSL #1341 by @fviernau
 - Improve License Match scoring and filtering for very short rules
 - Do not run license and copyright detection on media files: Media should not
   contain text #1347 #1348 
 - Detect scea-1.0 license correctly #1346
 - Do not detect warranty disclaimer as GPL #1345
 - Support quoted SPDX expressions and more comment marker prefixes
 - Use Free Restricted category for fraunhofer-fdk-aac-codec #1352 by @LeChasseur
 - Remove the spdx_license_key from here-proprietary #1360 by @sschuberth
 - Add new post-scan plugin to tag a file containing only license #1366
 - Add new license  #1365 and rules #1358

Packages:
 - Improve npm vcs_url handling #1314 by @majurg
 - Improve Maven POM license detection #1344
 - Add Maven POM URL detection 
 - Recognize .gem archives as packages 
 - Improve parsing of Pypi Python setup.py 
 - Improve package summaries. Add new plugin to improve package classification #1339

Other:
 - Fix doc typo by #1329 @farialima
 - Add new experimental pre-scan plugin to ignore binaries


v2.9.9 (2018-12-12)
-------------------

This is the penultimate pre-release of what will come up for 3.0 with some API change for packages.

API changes:
 - Streamline Package models #1226 #1324 and #1327. In particular the way checksums are managed has changed

Other changes:
 - Copyright detection improvements #1305 by @JonoYang
 - Correct CC-BY V3.0 and V4.0 license texts by correct one by @sschuberth #1320
 - Add new and improved licenses and license detection rules including the latest SPDX list 3.4 and #1322 #1324 
 - Rename proprietary license key to proprietary-license 
 - Rename commercial license key to commercial-license 
 - Improve npm package.json handling #1308 and #1314 by @majurg


v2.9.8 (2018-12-12)
-------------------

This is a close-to-final pre-release of what will come up for 3.0 with some API change for packages.

API changes:
 - In Package models, rename normalized_license to license_expression and 
   add license detection on the declared_license to populate the license_expression #1092 #1268 #1278

Outputs:
 - Do not open output files until the command lines are validated as correct #1266
 - The html-app output is marked as DEPRECATED. Use the AboutCode manager app instead #
 - Ensure HTML outputs can deal with non-ASCII file paths without crashsing #1292
 - JSON outputs now use a "headers" attributes for top-level scan headers #
 - SPDX output is now possible even without "--info" SHA1 checksums. This creates a partially valid document
 - LicenseRef for non-SPDX ScanCode licenses are named as "LicenseRef-scancode-<scancode key>" #
 - license_expression are correctly included in the CSV output #1238
 - do not crash with multiple outputs  #1199
 - Ensure CSV output include packages #1145

License detection:
 - Ensure license expressions are present in CSV output #1238
 - Fix 'license detection tests' collection on Windows #1182
 - An optional  "relevance" attribute has been added to the license YAML
   attributes. This is to store the relevance to e matched .LICENSE text when used
   as a rule.
 - Licenses have been synchronized with the latest v3.3 SPDX license list and the latest DejaCode licenses #1242
 - Duplicated SPDX keys have been fixed #1264
 - Add new and improved license detection rules #1313 #1306 #1302 #1298 #1293 
   #1291 #1289 #1270 #1269 #1192 #1186 #1170 #1164 #1128 #1124 #1112 #1110 #1108
   #1098 #1069 #1063 #1058 #1052 #1050 #1039 #987 #962 #929

Packages:
 - Add support for haxe "haxelib" package manifests #1227
 - Remove code_type attribute from Package models
 - In Package models, rename normalized_license  to license_expression and 
   add license detection on the declared_license to populate the license_expression #1092 #1268 #1278
 - Improve data returned for PHP Composer packages
 - Add PackageURL to top level output for packages
 - Report nuget as proper packages #1088

Summary:
 - improve summary and license score computation #1180

Misc:
 - Minor copyright detection improvements #1248 #1244 #1234 #1198 #1123 #1087
 - Ensure all temporary directories are prefixed with "scancode-"
 - Drop support for Linux 32 bits #1259
 - Do not attempt to scan encrypted PDF documents
 - Improve "data" files detection 
 - ScanCode can be installed from Pypi correctly #1214 #1183
 - Improve reporting of programming languages #1194 
 - Fix running post scan plugins #1141 

Command line:
 - Always delete temporary files when no longer needed. #1231
 - Add a new --keep-temp-files option to keep temp files which is false by default. #1231
 - Improve dependent plugin activation so it is done only when needed #1235

Internals:
 - Improve reusing resource.VirtualCode
 - Place all third-party packages under thirdparty #1219 and update ABOUT files


Credits: Many thanks to everyone that contributed to this release with code and bug reports

 - @nicoddemus
 - @chinyeungli
 - @johnmhoran
 - @jonasob
 - @DennisClark
 - @arthur657834
 - @JonoYang
 - @armijnhemel
 - @furuholm
 - @mjherzog
 - @sschuberth
 - @MartinPetkov
 - @jhgoebbert
 - @bobgob
 - @majurg
 - @tdruez
 - @tomeks666
 - @geneh
 - @jonassmedegaard

and many other that I may have missed. 



v2.9.7 (2018-10-25)
-------------------

No changes.



v2.9.6 (2018-10-25)
-------------------

 - Add declared license normalization #1092 
 - Add new and improved license rules
 - Add mising and clean up ABOUT files for all embedded third-party libraries
 - Improve npm package.json handling (better keuword support)
 - Update thirdparty libraries #1224

Credits: Many thanks to everyone that contributed to this release with code and bug reports


v2.9.5 (2018-10-22)
-------------------

This is a minor pre-release of what will come up for 3.0 with no API change.

 - Place all third-party packages under thirdparty #1219

Credits: Many thanks to everyone that contributed to this release with code and bug reports

 - @JonoYang


v2.9.4 (2018-10-19)
-------------------

This is a pre-release of what will come up for 3.0 with several API changes
related to packages.

 - Add Package URL field to top-level package output #1149
 - --package option should collect homepage URL for packages #645
 - Support installation from Pypi and update various third-parties to their
   latest version #1183 
 - Fix bug where multiple outputs with --html would crash scancode #
 - Add new and improved licenses and license detection rules #1192 #1186
 - Ensure that plugin failure trigger a proper error exit code #1199
 - Allow plugins to contribute codebase-level attributes in addition to
   resource-level attributes.
 - Output plugins can now be called from code #1148
 - Fix incorrect copyright detection #1198
 - Detect programming language more strictly and efficiently #1194
 - Use simpler list of source package URLs/purls #1206
 - Add purl to the packages data #1149 
 - Use direct attributes for package checksums #1189 
 - Remove package_manifest attribute for packages
 - Add new Package "manifest_path" attribute which is a relative path to
   the manifest file if any, such as a Maven .pom or a npm package.json.
 
Credits: Many thanks to everyone that contributed to this release with code and bug reports

 - @MartinPetkov 
 - @majurg
 - @JonoYang


v2.9.3 (2018-09-27)
-------------------

This is a pre-release of what will come up for 3.0 with an API change.

API change:
 - The returned copyright data structure has changed and is now simpler and less nested

Licenses:
 - Add new license and rules and improve licene rules #1186 #1108 #1124 #1171 #1173 #1039 #1098 #1111
 - Add new license clarity scoring #1180
   This is also for use in the ClearlyDefined project
 - Add is_exception to license scan results #1159 

Copyrights:
 - Copyright detection  has been improved #930 #965 #1103
 - Copyright data structure has been updated

Packages:
 - Add support for FreeBSD packages (ports) #1073
 - Add support for package root detection
 - Detect nuget packages correctly @1088

Misc:

 - Add facet, classification and summarizer plugins #357 
 - Fix file counts #1055
 - Fix corrupted license cache error
 - Upgrade all thridparty libraries #1070
 - De-vendor prebuilt binaries to ease packaging for Linux distros #469

Credits: Many thanks to everyone that contributed to this release with code and bug reports

 - @selmf
 - @paralax
 - @majurg
 - @mueller-ma
 - @MartinPetkov
 - @techytushar
 


v2.9.2 (2018-05-08)
-------------------
This is a major pre-release of what will come up for 3.0. with significant
packages and license API changes.

API changes:
 - Simplify output option names #789 
 - Update the packages data structure and introduce Package URLs #275
 - Add support for license expressions #74 with full exceptions support

Licenses:
 - Add support for license expressions #74 with full exceptions support
 - Enable SPDX license identifier match #81
 - Update and change handling of composite licenses now that we support expressions 
 - Symchronize licenses with latest from SPDX and DejaCode #41
 - Add new licenses ofr odds and ends: other-permissive and other-copyleft
 - refine license index cache handling
 - remove tests without value
 - Add new license policy plugin #214, #880

Packages:
 - Split packages from package_manifest #1027. This is experimental
   The packages scan return now a single package_manifest key (not a list)
   And a post_scan plugin (responding to the same --package) option perform
   a roll-up of the manifest informationat the proper level for a package
   type as the "packages" attribute (which is still a list). For instance
   a package.json "package_manifest" will end up having a "packages" entry
   in its parent directory.
 - Include and return Package URLs (purl) #805 and #275
 - Major rework of the package data structure #275
   - Rename asserted_license to declared_licensing #275
   - Add basic Godeps parsing support #275
   - Add basic gemspec and Rubygems parsing support #275
   - Add basic Gemfile.lock parsing support #275 
   - Add basic Win DLL parsing support #275
   - Replace MD5/SHA1 by a list of checksums #275 
   - Use a single download_url, not a list #275 
   - Add namespace to npm. Compute defaults URL #275 

Misc:
 - multiple minor bug fixes
 - do not ignore .repo files #881

Credits: Many thanks to everyone that contributed to this release with code and bug reports

 - @JonoYang
 - @majurg
 - @pombredanne
 - @yash-nisar
 - @ThorstenHarter


v2.9.1 (2018-03-22)
-------------------

This is a minor pre-release of what will come up for 3.0 with no API change.

Licenses:
 - There are new and improved licenses and license detection rules #994 #991 #695 #983 #998 #969

Copyrights:
 - Copyright detection  has been improved #930 #965
 
Misc:
 - Improve support for JavaScript map files: they may contain both debugging
   information and whole package source code.
 - multiple minor bug fixes

Credits: Many thanks to everyone that contributed to this release with code and bug reports

 - @haikoschol
 - @jamesward
 - @JonoYang
 - @DennisClark
 - @swinslow


v2.9.0b1 (2018-03-02)
---------------------

This is a major pre-release of what will come up for 3.0

This has a lot of new changes including improved plugins, speed and detection 
that are not yet fully documented but it can be used for testing.

API changes:
 - Command line API

  - `--diag` option renamed to `--license-diag`

  - `--format <format code>` option has been replaced by multiple options one
    for each format such as `--format-csv` `--format-json` and multiple formats
    can be requested at once

  - new experimental `--cache-dir` option and `SCANCODE_CACHE` environment variable
    and `--temp-dir` and `SCANCODE_TMP` environment variable to set the temp and
    cache directories.

 - JSON data output format: no major changes

 - programmatic API in scancode/api.py:

  - get_urls(location, threshold=50): new threshold argument

  - get_emails(location, threshold=50): new threshold argument

  - get_file_infos renamed to get_file_info

  - Resource moved to scancode.resource and significantly updated

  - get_package_infos renamed to get_package_info


Command line
 - You can select multiple outputs at once (e.g. JSON and CSV, etc.) #789
 - There is a new capability to reload a JSON scan to reprocess it with postcsan
   plugins and or converting a JSON scan to CSV or else.


Licenses:
 - There are several new and improved licenses and license detection rules #799 #774 #589
 - Licenses data now contains the full name as well as the short name.

 - License match have a notion of "coverage" which is the number of matched
   words compared to the number of words in the matched rule.
 - The license cache is not checked anymore for consistency once created which
   improved startup times. (unless you are using a Git checkout and you are 
   developping with a SCANCODE_DEV_MODE tag file present)
 - License catagory names have been improved

Copyrights:
 - Copyright detection in binary files has been improved
 - There are several improvements to the copyright detection quality fixing these
   tickets: #795 #677 #305 #795
 - There is a new post scan plugin that can be used to ignore certain copyright in
   the results

Summaries:
 - Add new support for  copyright summaries using smart holder deduplication #930

Misc:
 - Add options to limit the number of emails and urls that are collected from
   each file (with a default to 50) #384
 - When configuring in dev mode, VS Code settings are created
 - Archive detection has been improved
 - There is a new cache and temporary file configuration with --cache-dir and 
   --temp-dir CLI options. The --no-cache option has been removed
 - Add new --examples to show usage examples help
 - Move essential configuration to a scancode_config.py module
 - Only read a few pages from PDF files by default
 - Improve handling of files with weird characters in their names on all OSses
 - Improve detection of archive vs. comrpessed files
 - Make all copyright tests data driven using YAML files like for license tests
 

Plugins
 - Prescan plugins can now exclude files from the scans 
 - Plugins can now contribute arbitrary command line options #787 and #748
 - there is a new plugin stage called output_filter to optionally filter a scan before output.
   One example is to keep "only findings" #787
 - The core processing is centered now on a Codebase and Resource abstraction
   that represents the scanned filesystem in memory #717 #736
   All plugins operate on this abstraction
 - All scanners are also plugins #698 and now everything is a plugin including the scans
 - The interface for output plugins is the same as other plugins #715

 
Credits: Many thanks to everyone that contributed to this release with code and bug reports
(and this list is likely missing some)

 - @SaravananOffl
 - @jpopelka
 - @yashdsaraf
 - @haikoschol
 - @jdaguil
 - @ajeans
 - @DennisClark
 - @susg
 - @pombredane
 - @mjherzog
 - @Sidsharik
 - @nishakm
 - @yasharmaster
 - @techytushar
 - @JonoYang
 - @majurg
 - @aviral1701
 - @haikoschol
 - @chinyeungli
 - @vivonk
 - @Chaitya62
 - @inishchith


v2.2.1 (2017-10-05)
-------------------

This is a minor release with several bug fixes, one new feature
and one (minor) API change.

API change:
~~~~~~~~~~~

 - Licenses data now contains a new reference_url attribute instead of a
   dejacode_url attribute. This defaults to the public DejaCode URL and
   can be configured with the new --license-url-template command line
   option.

New feature:
~~~~~~~~~~~~~~~

 - There is a new "--format jsonlines" output format option.
   In this format, each line in the output is a valid JSON document. The
   first line contains a "header" object with header-level data such as
   notice, version, etc. Each line after the first contains the scan
   results for a single file formatted with the same structure as a
   whole scan results JSON documents but without any header-level
   attributes. See also http://jsonlines.org/

Other changes:
~~~~~~~~~~~~~~~

 - Several new and improved license detection rules have been added.
   The logic of detection has been refined to handle some rare corner
   cases. The underscore character "_" is treated as part of a license
   word and the handling of negative and false_positive license rules
   has been simplified.

 - Several issues with dealing with codebase with non-ASCII,
   non-UTF-decodable file paths and other filesystem encodings-related
   bug have been fixed.

 - Several copyright detection bugs have been fixed.
 - PHP Composer and RPM packages are now detected with --package
 - Several other package types are now detected with --package even
   though only a few attribute may be returned for now until full parser
   are added.
 - Several parsing NPM packages bugs have been fixed. 
 - There are some minor performance improvements when scanning some
   large file for licenses.


v2.1.0 (2017-09-22)
-------------------

This is a minor release with several new and improved features and bug
fixes but no significant API changes.

 - New plugin architecture by @yashdsaraf

  - we can now have pre-scan, post-scan and output format plugins
  - there is a new CSV output format and some example, experimental plugins
  - the CLI UI has changed to better support these plugins

 - New and improved licenses and license detection rules including
   support for EPL-2.0 and OpenJDK-related licensing and synchronization
   with the latest SPDX license list

 - Multiple bug fixes such as:

   - Ensure that authors are reported even if there is no copyright #669
   - Fix Maven package POM parsing infinite loop #721
   - Improve handling of weird non-unicode byte paths #688 and #706
   - Improve PDF parsing to avoid some crash #723

Credits: Many thanks to everyone that contributed to this release with code and bug reports
(and this list is likely missing some)

* @abuhman
* @chinyeungli
* @jimjag
* @JonoYang
* @jpopelka
* @majurg
* @mjherzog
* @pgier
* @pkajaba
* @pombredanne
* @scottctr
* @sschuberth
* @yahalom5776
* @yashdsaraf


v2.0.1 (2017-07-03)
-------------------

 This is a minor release with minor new and improved features and bug
 fixes.

 - New and improved license detection, including refined match scoring
   for #534
 - Bug fixed in License detection leading to a very long scan time for some
   rare JavaScript files. Reported by @jarnugirdhar
 - New "base_name" attribute returned with file information. Reported by
   @chinyeungli
 - Bug fixed in Maven POM package detection. Reported by @kalagp
 

v2.0.0 (2017-06-23)
-------------------

 This is a major release with several new and improved features and bug
 fixes.
 
 Some of the key highlights include:

License detection:
~~~~~~~~~~~~~~~~~~~

   - Brand new, faster and accurate detection engine using multiple
     techniques eventually doing multiple exhaustive comparisons of
     a scanned file content against all the license and rule texts.

   - Several new licenses and over 2500+ new and improved licenses
     detection rules have been added making the detection significantly
     better (and weirdly enough faster too as a side-effect of the new
     detection engine)

   - the matched license text can be optionally returned with the
     `--license-text` option

   - The detection accuracy has been benchmarked against other detection
     engine and ScanCode has shown to be more accurate and
     comprehensive than all the other engines reviewed.

   - improved scoring of license matches


Package and dependencies:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  - new and improved detection of multiple package formats: NPM, Maven,
    NuGet, PHP Composer, Python Pypi and RPM. In most cases direct,
    declared dependencies are also reported.

  - several additional package formats will be reported in the future
    version.

  - note: the structure of Packages data is evolving and should not be
    considered API at this stage


Scan outputs: 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  - New SPDX tag/values and RDF outputs.

  - new compact JSON format (the pretty printed format is still
    available with the the `json-pp` format).
    The JSON format has been changed significantly and is closer to a
    documented, standard format that we call the ABC data format.

  - Minor refinements on the html and html-app format. Note that the
    html-app format will be deprecated and replaced by the new AboutCode
    Manager desktop app (electron-based) in future versions.


 - Copyright: Improved copyright detection: several false positive are
   no longer returned and copyrights are more accurate


 - Archive: support for shallow extraction and support for new archive
   types (such as Spring boot shell archives)


Performance:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  - Everything is generally faster, and license detection performance
    has been significantly improved.

  - Scans can run on multiple processes in parallel with the new 
    `--processes` option speeding up things even further. A scan of a
    full Debian pool of source packages was reported to scan in about
    11 hours (on a rather beefy 144 cores, 256GB machine)

  - Reduced memory usage with the use of caching

Other notes:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   - This is the last release with Linux 32 bits architecture support
   - The scan of a file can be interrupted after a timeout with a 120
     seconds default
   - ScanCode is now available as a library on the Pypi Python package
     index for use as a library. The documentation for the library usage
     will follow in future versions
   - New `--ignore` option: You can optionally ignore certain file and
     paths during a scan
   - New `--diag option`: display additional debug and diagnostic data
   - The scanned file paths can now reported as relative, rooted or
     absolute with new command line options with a default to a rooted
     path. 


 Thank you to all contributors to this release and the 200+ stars
 and 60+ forks on GitHub!

Credits in alphabetical order:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  Alexander Lisianoi
  Avi Aryan
  Benedikt Spranger
  Chin Yeung
  Dennis Clark
  Hugo Jacob
  Jakub Wilk
  Jericho @attritionorg
  Jillian Daguil
  Jiri Popelka
  John M. Horan
  Jonathan "Jono" Yang
  Li Ha
  Michael Herzog
  Michael Rupprecht
  Nusrat Sultana
  Paul Kunz
  Philippe Ombredanne
  Rakesh Balusa
  Ranvir Singh
  Richard Fontana
  Sebastian Schuberth
  Steven Esser
  Thomas Gleixner
  Tisoga @forrestchang
  Yash D. Saraf
  Yash Sharma


v1.6.0 (2016-01-29)
-------------------

New features
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 - The HTML app now displays a copyright holder summary graphic
 - HTML app ui enhancements
 - File extraction fixes
 - New and improved license and detection rules
 - Other minor improvements and minor bug fixes


v1.5.0 (2015-12-15)
-------------------

New features
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 - The HTML app now display a license summary graphic
 - Copyright holders and Authors are now collected together with copyrights
 - New email and url scan options: scan for URLs and emails
 - New and improved license and detection rules

These scans are for now only available in the JSON output 


v1.4.3 (2015-12-03)
-------------------

Minor bug fix
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 - In the HTML app, the scanned path was hardcoded as
   scancode-toolkit2/scancode-toolkit/samples instead of displaying the path
   that was scanned.


v1.4.2 (2015-12-03)
-------------------

Minor features and bug fixes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 - The release archives were missing some code (packagedcode)
 - Improved --quiet option for command line operations
 - New support for custom Jinja templates for the HTML output.
   The template also has access to the whole License object to output full
   license texts or other data. Thanks to @ened Sebastian Roth for this.


v1.4.0 (2015-11-24)
-------------------

New features and bug fixes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 - Separated JSON data into a separate file for the html app.
   https://github.com/nexB/scancode-toolkit/issues/38
 - Added support for scanning package and file information.
 - Added file and package information to the html-app and html output.
   https://github.com/nexB/scancode-toolkit/issues/76
 - improved CSS for html format output
   https://github.com/nexB/scancode-toolkit/issues/12
 - New and improved licenses rules and licenses.
 - Added support for nuget .nupkg as archives.
 - Created new extractcode standalone command for
   https://github.com/nexB/scancode-toolkit/issues/52
   Extracting archives is no longer part of the scancode command.
 - Scancode can now be called from anywhere.
   https://github.com/nexB/scancode-toolkit/issues/55
 - Various minor improvements for copyright detection.


v1.3.1 (2015-07-27)
-------------------

Minor bug fixes.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 - fixed --verbose option https://github.com/nexB/scancode-toolkit/issues/37
 - Improved copyright and license detections (new rules, etc.)
 - other minor improvements and minor bug fixes:
   temptative fix for https://github.com/nexB/scancode-toolkit/issues/4
 - fixed for unsupported inclusion of Linux-32 bits pre-built binaries
   https://github.com/nexB/scancode-toolkit/issues/33


v1.3.0 (2015-07-24)
-------------------

New features and bug fixes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 - scancode now ignores version control directories by default (.svn, .git, etc)
 - Improved copyright and license detections (new rules, etc.)
 - other minor improvements and minor bug fixes.
 - experimental and unsupported inclusion of Linux-32 bits pre-built binaries


v1.2.4 (2015-07-22)
-------------------

Minor bug fixes.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 - Improved copyright detections.
 - can scan a single file located in the installation directory
 - other minor improvements and minor bug fixes.


v1.2.3 (2015-07-16)
-------------------

Major bug fixes on Windows.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 - This is a major bug fix release for Windows. 
   The -extract option was not working on Windows in previous 1.2.x pre-releases


v1.2.2 (2015-07-14)
-------------------

Minor bug fixes.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 - Support relative path when doing extract.


v1.2.1 (2015-07-13)
-------------------

Minor bug fixes.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 - Improper extract warning handling


v1.2.0 (2015-07-13)
-------------------

Major bug fixes.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 - Fixed issue #26: Slow --extract
 - Added support for progress during extraction (#27)


v1.1.0 (2015-07-06)
-------------------

Minor bug fixes.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 - Enforced exclusivity of --extract option
 - Improved command line help.
 - Added continuous testing with Travis and Appveyor and fixed tests


v1.0.0 (2015-06-30)
-------------------

Initial release.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 - support for scanning licenses and copyrights
 - simple command line with html, html-app and JSON formats output
