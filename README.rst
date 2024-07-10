================
ScanCode toolkit
================

A typical software project often reuses hundreds of third-party packages.
License and packages, dependencies and origin information is not always easy to
find and not normalized: ScanCode discovers and normalizes this data for you.

Read more about ScanCode here: https://scancode-toolkit.readthedocs.io/.

Check out the code at https://github.com/nexB/scancode-toolkit

Discover also:

- The ScanCode.io server project here: https://scancodeio.readthedocs.io
- The ScanCode Workbench project for visualization of scancode results data:
  https://github.com/nexB/scancode-workbench 
- Other companion SCA projects for code origin, license and security analysis
  here: https://aboutcode.org


Build and tests status
======================

We run 30,000+ tests on each commit on multiple CIs to ensure a good platform
compabitility with multiple versions of Windows, Linux and macOS.

+------------+--------------+-------------------------+----------------------------+
| **Azure**  | **RTD Build**| **GitHub actions Docs** | **GitHub actions Release** |
+============+==============+=========================+============================+
|  |azure|   | |docs-rtd|   |  |docs-github-actions|  |  |release-github-actions|  |
+------------+--------------+-------------------------+----------------------------+


Why use ScanCode?
=================

- As a **standalone command-line tool**, ScanCode is **easy to install**, run,
  and embed in your CI/CD processing pipeline.
  It runs on **Windows, macOS, and Linux**.

- ScanCode is **used by several projects and organizations** such as
  the `Eclipse Foundation <https://www.eclipse.org>`_,
  `OpenEmbedded.org <https://www.openembedded.org>`_,
  the `FSFE <https://www.fsfe.org>`_,
  the `FSF <https://www.fsf.org>`_,
  `OSS Review Toolkit <http://oss-review-toolkit.org>`_, 
  `ClearlyDefined.io <https://clearlydefined.io/>`_,
  `RedHat Fabric8 analytics <https://github.com/fabric8-analytics>`_,
  and many more.

- ScanCode detects licenses, copyrights, package manifests, direct dependencies,
  and more both in **source code** and **binary** files and is considered as the
  best-in-class and reference tool in this domain, re-used as the core tools for
  software composition data collection by several open source tools.

- ScanCode provides the **most accurate license detection engine** and does a
  full comparison (also known as diff or red line comparison) between a database
  of license texts and your code instead of relying only on approximate regex
  patterns or probabilistic search, edit distance or machine learning.

- Written in Python, ScanCode is **easy to extend with plugins** to contribute
  new and improved scanners, data summarization, package manifest parsers, and
  new outputs.

- You can save your scan results as **JSON, YAML, HTML, CycloneDX or SPDX** or
  even create your own format with Jinja templates.

- You can also organize and run ScanCode server-side with the
  companion `ScanCode.io web app <https://github.com/nexB/scancode.io>`_
  to organize and store multiple scan projects including scripted scanning pipelines.

- ScanCode output data can be easily visualized and analysed using the
  `ScanCode Workbench <https://github.com/nexB/scancode-workbench>`_ desktop app.

- ScanCode is **actively maintained**, has a **growing users and contributors
  community**.

- ScanCode is heavily **tested** with an automated test suite of over **20,000 tests**.

- ScanCode has an extensive and growing documentation.

- ScanCode can process packages, build manifest and lockfile formats to collect
  Package URLs and extract metadata: Alpine packages, BUCK files, ABOUT files,
  Android apps, Autotools, Bazel, JavaScript Bower, Java Axis, MS Cab,
  Rust Cargo, Cocoapods, Chef Chrome apps, PHP Composer and composer.lock,
  Conda, CPAN, Debian, Apple dmg, Java EAR, WAR, JAR, FreeBSD packages,
  Rubygems gemspec, Gemfile and Gemfile.lock, Go modules, Haxe packages,
  InstallShield installers, iOS apps, ISO images, Apache IVY, JBoss Sar,
  R CRAN, Apache Maven, Meteor, Mozilla extensions, MSI installers,
  JavaScript npm packages, package-lock.json, yarn.lock, NSIS Installers,
  NugGet, OPam, Cocoapods, Python PyPI setup.py, setup.cfg, and 
  several related lockfile formats, semi structured README
  files such as README.android, README.chromium, README.facebook, README.google,
  README.thirdparty, RPMs, Shell Archives, Squashfs images, Java WAR, Windows
  executables and the Windows registry
  and a few more. See `all available package parsers <https://scancode-toolkit.readthedocs.io/en/stable/reference/available_package_parsers.html>`_
  for the exhaustive list.

See our `roadmap <https://scancode-toolkit.readthedocs.io/en/latest/contribute/roadmap.html>`_
for upcoming features.


Documentation
=============

The ScanCode documentation is hosted at
`scancode-toolkit.readthedocs.io <https://scancode-toolkit.readthedocs.io/en/latest/>`_.

If you are new to visualization of scancode results data, start with our
`newcomer <https://scancode-toolkit.readthedocs.io/en/latest/getting-started/newcomer.html>`_ page.

If you want to compare output changes between different versions of ScanCode, 
or want to look at  scans generated by ScanCode, review our
`reference scans <https://github.com/nexB/scancode-toolkit-reference-scans>`_.

Other Important Documentation Pages:

- A `synopsis <https://scancode-toolkit.readthedocs.io/en/latest/cli-reference/synopsis.html>`_ 
  of ScanCode command line options.

- Tutorials on:

  - `How to run a scan <https://scancode-toolkit.readthedocs.io/en/latest/tutorials/how_to_run_a_scan.html>`_
  - `How to visualize scan results <https://scancode-toolkit.readthedocs.io/en/latest/tutorials/how_to_visualize_scan_results.html>`_

- An exhaustive list of `all available options <https://scancode-toolkit.readthedocs.io/en/latest/cli-reference/list-options.html>`_

- Documentation on `Contributing to Code Development <https://scancode-toolkit.readthedocs.io/en/latest/contribute/contrib_dev.html>`_

- Documentation on `Plugin Architecture <https://scancode-toolkit.readthedocs.io/en/latest/plugins/plugin_arch.html>`_

- `FAQ <https://scancode-toolkit.readthedocs.io/en/latest/misc/faq.html>`_

See also https://aboutcode.org for related companion projects and tools.


Installation
============

Before installing ScanCode make sure that you have installed the prerequisites
properly. This means installing Python 3.8 for x86/64 architectures.
We support Python 3.8, 3.9, 3.10, 3.11 and 3.12.

See `prerequisites <https://scancode-toolkit.readthedocs.io/en/latest/getting-started/install.html#prerequisites>`_
for detailed information on the support platforms and Python versions.

There are a few common ways to `install ScanCode <https://scancode-toolkit.readthedocs.io/en/latest/getting-started/install.html>`_.

- `**Installation as an application: Install Python 3.8, download a release archive, extract and run**. 
  <https://scancode-toolkit.readthedocs.io/en/latest/getting-started/install.html#installation-as-an-application-downloading-releases>`_
  This is the recommended installation method.

- `Development installation from source code using a git clone
  <https://scancode-toolkit.readthedocs.io/en/latest/getting-started/install.html#installation-from-source-code-git-clone>`_

- `Development installation as a library with "pip install scancode-toolkit"
  <https://scancode-toolkit.readthedocs.io/en/latest/getting-started/install.html#pip-install>`_
  [Note that this is not supported on arm64 machines]

- `Run in a Docker container with a git clone and "docker run"
  <https://scancode-toolkit.readthedocs.io/en/latest/getting-started/install.html#installation-via-docker>`_

- In Fedora 40+ you can `dnf install scancode-toolkit`


Quick Start
===========

After ScanCode is installed successfully you can run an example scan printed on screen as JSON::

    scancode -clip --json-pp - samples

Follow the `How to Run a Scan <https://scancode-toolkit.readthedocs.io/en/latest/tutorials/how_to_run_a_scan.html>`_
tutorial to perform a basic scan on the ``samples`` directory distributed by
default with ScanCode.

See more command examples::

    scancode --examples

See `How to select what will be detected in a scan
<https://scancode-toolkit.readthedocs.io/en/latest/tutorials/how_to_set_what_will_be_detected_in_a_scan.html>`_
and `How to specify the output format <https://scancode-toolkit.readthedocs.io/en/latest/tutorials/how_to_format_scan_output.html>`_
for more information.

You can also refer to the `command line options synopsis
<https://scancode-toolkit.readthedocs.io/en/latest/cli-reference/synopsis.html>`_
and an exhaustive list of `all available command line options
<https://scancode-toolkit.readthedocs.io/en/latest/cli-reference/list-options.html>`_.


Archive extraction
==================

By default ScanCode does not extract files from tarballs, zip files, and
other archives as part of the scan. The archives that exist in a codebase
must be extracted before running a scan: `extractcode` is a bundled utility
behaving as a mostly-universal archive extractor. For example, this command will
recursively extract the mytar.tar.bz2 tarball in the mytar.tar.bz2-extract
directory::

    ./extractcode mytar.tar.bz2

See `all extractcode options <https://scancode-toolkit.readthedocs.io/en/latest/cli-reference/list-options.html#all-extractcode-options>`_
and `how to extract archives <https://scancode-toolkit.readthedocs.io/en/latest/tutorials/how_to_extract_archives.html>`_ for details.


Support
=======

If you have a problem, a suggestion or found a bug, please enter a ticket at:
https://github.com/nexB/scancode-toolkit/issues

For discussions and chats, we have:

* an official Gitter channel for `web-based chats
  <https://matrix.to/#/#aboutcode-org_discuss:gitter.im>`_.
  Gitter is now accessible through `Element <https://element.io/download>`_
  or an `IRC bridge <https://matrix-org.github.io/matrix-appservice-irc/latest/usage.html>`_.
  There are other AboutCode project-specific channels available there too.

* The discussion channel for `scancode <https://matrix.to/#/#aboutcode-org_scancode:gitter.im>`_
  specifically aimed at users and developers using scancode-toolkit.

Source code and downloads
=========================

* https://github.com/nexB/scancode-toolkit/releases
* https://github.com/nexB/scancode-toolkit.git
* https://pypi.org/project/scancode-toolkit/
* https://github.com/nexB/scancode-thirdparty-src.git
* https://github.com/nexB/scancode-plugins.git
* https://github.com/nexB/thirdparty-packages.git

License
=======

* Apache-2.0 as the overall license
* CC-BY-4.0 for reference datasets (initially was in the Public Domain).
* Multiple other secondary permissive or copyleft licenses (LGPL, MIT,
  BSD, GPL 2/3, etc.) for third-party components and test suite code and data.


See the NOTICE file and the .ABOUT files that document the origin and license of
the third-party code used in ScanCode for more details.


.. |azure| image:: https://dev.azure.com/nexB/scancode-toolkit/_apis/build/status/nexB.scancode-toolkit?branchName=develop
    :target: https://dev.azure.com/nexB/scancode-toolkit/_build/latest?definitionId=1&branchName=develop
    :alt: Azure tests status (Linux, macOS, Windows)

.. |docs-rtd| image:: https://readthedocs.org/projects/scancode-toolkit/badge/?version=latest
    :target: https://scancode-toolkit.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. |docs-github-actions| image:: https://github.com/nexB/scancode-toolkit/actions/workflows/docs-ci.yml/badge.svg?branch=develop
    :target: https://github.com/nexB/scancode-toolkit/actions/workflows/docs-ci.yml
    :alt: Documentation Tests

.. |release-github-actions| image:: https://github.com/nexB/scancode-toolkit/actions/workflows/scancode-release.yml/badge.svg?event=push
    :target: https://github.com/nexB/scancode-toolkit/actions/workflows/scancode-release.yml
    :alt: Release tests
