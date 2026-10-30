.. _roadmap:

Roadmap
=======

This is a high level list of what we are working on and what is completed.

.. ToDo: Move this to Discussions or wikis as this is not used or updated
   regularly.

.. _note:

  This is not updated regularly, see the `milestones <https://github.com/aboutcode-org/scancode-toolkit/milestones>`_
  instead for updated shorter and longer term roadmaps.

Legend
------

|white_check_mark|	completed	|clock1030|	In progress	|white_large_square|	Planned, not started

Work in Progress
----------------

(see Completed features below)

Package manifest and dependency parsers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- |clock1030| Docker image base (as part of: https://github.com/pombredanne/conan ) #651
- |clock1030| RubyGems base and dependencies #650 (code in https://github.com/aboutcode-org/scancode-toolkit-contrib/ )
- |clock1030| Perl, CPAN (basic in https://github.com/aboutcode-org/scancode-toolkit-contrib/)
- |clock1030| Go : parsing for Godep in https://github.com/aboutcode-org/scancode-toolkit-contrib/
- |clock1030| Windows PE #652
- |white_large_square| RPM dependencies #649
- |white_large_square| Windows Nuget dependencies #648
- |white_check_mark| Bower packages #654
- |white_check_mark|  Python dependencies #653
- |white_check_mark| CRAN
- |white_check_mark| Plain packages
- |white_large_square| other Java-related meta files (SBT, Ivy, Gradle, etc.)
- |white_large_square| Debian debs
- |white_large_square| other JavaScript (jspm, etc.)
- |white_large_square| other Linux distro packages

License Detection
^^^^^^^^^^^^^^^^^

- |white_check_mark| support and detect license expressions (code in https://github.com/aboutcode-org/license-expression)
- |clock1030| support and detect composite licenses
- |white_check_mark| support custom licenses
- |white_large_square| move licenses data set to external separate repository
- |white_check_mark| Improved unknown license detection
- |white_check_mark| sync with external sources (DejaCode, SPDX, etc.)

Copyrights
^^^^^^^^^^

- |white_check_mark| speed up copyright detection
- |white_check_mark| improved detected lines range
- |white_check_mark| streamline grammar of copyright parser
- |white_check_mark| normalize holders and authors for summarizing
- |white_check_mark| normalize and streamline results data format

Core features
^^^^^^^^^^^^^

- |white_check_mark| pre scan filtering (ignore binaries, etc)
- |white_check_mark| pre/post/ouput plugins! (worked as part of the GSoC by @yadsharaf )
- |white_check_mark| scan plugins (e.g. plugins that run a scan to collect data)
- |white_check_mark| support Python 3 #295
- |clock1030| transparent archive extraction (as opposed to on-demand with extractcode)
- |white_large_square| scancode.yml configuration file for exclusions, defaults, scan
  failure conditions, etc.
- |white_large_square| support scan pipelines and rules to organize more complex scans
- |white_check_mark| scan baselining, delta scan and failure conditions (such as license change,
  etc) ( spawned as its the `DeltaCode <https://github.com/nexB/deltacode/>`_ project)
- |white_large_square| dedupe and similarities to avoid re-scanning. For now only identical files
  are scanned only once.
- |clock1030| Improved logging, tracing and error diagnostics
- |white_check_mark| native support for ABC Data (See :ref:`aboutcode_data` )

Classification, summarization and deduction
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- |clock1030| File classification #426
- |white_check_mark| summarize and aggregate data #377 at the top level

Source code support (some will be spawned as their own tool)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- |clock1030| symbols : parsing complete in https://github.com/aboutcode-org/scancode-toolkit-contrib/
- |clock1030| metrics : some elements in https://github.com/aboutcode-org/scancode-toolkit-contrib/

Compiled code support (will be spawned as their own tool)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- |clock1030| ELFs : parsing complete in https://github.com/aboutcode-org/scancode-toolkit-contrib/
- |clock1030| Java bytecode : parsing complete in https://github.com/aboutcode-org/scancode-toolkit-contrib/
- |clock1030| Windows PE : parsing complete in https://github.com/aboutcode-org/scancode-toolkit-contrib/
- |clock1030| Mach-O : parsing complete in in https://github.com/aboutcode-org/scancode-toolkit-contrib/
- |white_large_square| Dalvik/dex

Data exchange
^^^^^^^^^^^^^

- |white_check_mark| SPDX data conversion #338

Packaging
^^^^^^^^^

- |white_large_square| simpler installation, automated installer
- |white_check_mark| distro-friendly packaging
- |clock1030| unbundle and package as multiple libaries (commoncode, extractcode, etc)

Documentation
^^^^^^^^^^^^^

- |white_large_square| integration in a build/CI loop
- |white_large_square| end to end guide to analyze a codebase
- |white_large_square| hacking guides
- |white_large_square| API doc when using ScanCode as a library

CI integration
^^^^^^^^^^^^^^

- |white_large_square| Plugins for CI (Jenkins, etc)
- |white_large_square| Integration for CI (Travis, Appveyor, Drone, etc)


Other work in progress
----------------------

- |clock1030| ScanCode server: Separate project: https://github.com/nexB/scancode-server.
  Will include Integration / webhooks for Github, Bitbucket.
- |clock1030| VulnerableCode: NVD and CVE lookups: Separate project:
  https://github.com/aboutcode-org/vulnerablecode
- |white_check_mark| ScanCode Workbench: desktop app for scan review: Separate project:
  https://github.com/aboutcode-org/scancode-workbench
- |white_large_square| DependentCode: dynamic dependencies resolutions: Separate project:
  https://github.com/nexB/dependentcode

Package mining and matching
^^^^^^^^^^^^^^^^^^^^^^^^^^^

(Note that this will be a separate project)
Some code is in https://github.com/aboutcode-org/scancode-toolkit-contrib/

- |clock1030| exact matching
- |clock1030| attribute-based matching
- |clock1030| fuzzy matching
- |white_large_square| peer-reviewed meta packages repo
- |white_large_square| basic mining of package repositories

Other
^^^^^

- |white_large_square| Crypto code detection


Completed features
------------------

Core scans
^^^^^^^^^^

- |white_check_mark| exact license detection
- |white_check_mark| approximate license detection
- |white_check_mark| copyright detection
- |white_check_mark| file information (size, type, etc.)
- |white_check_mark| URLs, emails, authors

Outputs and UI
^^^^^^^^^^^^^^
- |white_check_mark| JSON compact and pretty
- |white_check_mark| plain HTML tables, also usable in a spreadsheet
- |white_check_mark| fancy HTML 'app' with a file tree navigation, and scan results filtering,
  search and sorting
- |white_check_mark| simple scan summary
- |white_check_mark| SPDX output

Package and dependencies
^^^^^^^^^^^^^^^^^^^^^^^^
- |white_check_mark| common model for package data
- |white_check_mark| basic support for common package format
- |white_check_mark| RPM package base
- |white_check_mark| NuGet package base
- |white_check_mark| Python package base
- |white_check_mark| PHP Composer package support with dependencies
- |white_check_mark| Java Maven POM package support with dependencies
- |white_check_mark| npm package support with dependencies

Speed!
^^^^^^
- |white_check_mark| accelerate license detection indexing and scanning; include caching
- |white_check_mark| scan using multiple processes to speed up overall scan
- |white_check_mark| cache per-file scan to disk and stream final results

Other
^^^^^
- |white_check_mark| archive extraction with extractcode
- |white_check_mark| conversion of scan results to CSV
- |white_check_mark| improved error handling, verbose and diagnostic output

.. |white_check_mark| image:: data/done.png
    :scale: 10 %
.. |white_large_square| image:: data/planned.png
    :scale: 10 %
.. |clock1030| image:: data/clock.png
    :scale: 10 %
