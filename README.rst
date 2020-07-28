================
ScanCode toolkit
================

A typical software project often reuses hundreds of third-party packages.
License and origin information is not always easy to find and not normalized:
ScanCode discovers and normalizes this data for you.

Read more about ScanCode here: `scancode-toolkit.readthedocs.io <https://scancode-toolkit.readthedocs.io/en/latest/>`_.

Why use ScanCode?
=================

- As a **standalone command line tool**, ScanCode is **easy to install**, run
  and embed in your CI/CD processing pipeline. It runs on **Windows, macOS and Linux**.

- ScanCode is **used by several projects and organizations** such as the `Eclipse
  Foundation <https://www.eclipse.org>`_, `OpenEmbedded.org <https://www.openembedded.org>`_,
  the `FSF <https://www.fsf.org>`_, `OSS Review Toolkit <http://oss-review-toolkit.org>`_, 
  `ClearlyDefined.io <https://clearlydefined.io/>`_,
  `RedHat Fabric8 analytics <https://github.com/fabric8-analytics>`_ and many more.

- ScanCode detects licenses, copyrights, package manifests and direct dependencies
  and more both in **source code** and **binary** files.

- ScanCode provides the **most accurate license detection engine** and does a
  full comparison (also known as diff or red line comparison) between a database of license texts
  and your code instead of relying only on regex patterns or probabilistic
  search, edit distance or machine learning.

- Written in Python, ScanCode is **easy to extend with plugins** to contribute new
  and improved scanners, data summarization, package manifest parsers and new
  outputs.

- You can save your scan results as **JSON, HTML, CSV or SPDX**. And you can use the
  companion `ScanCode workbench GUI app <https://github.com/nexB/scancode-workbench>`_
  to review and display scan results, statistics and graphics.

- ScanCode is **actively maintained**, has a **growing community of users**.

- ScanCode is heavily **tested** with an automated test suite of over **8000 tests**.

- ScanCode has extensive and updated Documentation help for users.

See our `roadmap <https://scancode-toolkit.readthedocs.io/en/latest/contribute/roadmap.html>`_ for upcoming features.

Build and tests status
======================

+-------+--------------+-----------------+--------------+
|Branch | **Coverage** | **Linux/macOS** | **Windows**  |
+=======+==============+=================+==============+
|Master | |master-cov| | |master-posix|  | |master-win| |
+-------+--------------+-----------------+--------------+
|Develop| |devel-cov|  | |devel-posix|   | |devel-win|  |
+-------+--------------+-----------------+--------------+

Documentation Build
-------------------

+--------+--------------+
|Version | **RTD Build**|
+========+==============+
| Latest | |docs-rtd|   |
+--------+--------------+


Documentation
=============

The ScanCode documentation is hosted at `scancode-toolkit.readthedocs.io <https://scancode-toolkit.readthedocs.io/en/latest/>`_.

If you are new to Scancode, start `here <https://scancode-toolkit.readthedocs.io/en/latest/getting-started/newcomer.html>`_.

Other Important Documentation Pages:

- A `Synopsis <https://scancode-toolkit.readthedocs.io/en/latest/cli-reference/synopsis.html>`_ of ScanCode Command Line Options
- Tutorials on `How to Run a Scan <https://scancode-toolkit.readthedocs.io/en/latest/tutorials/how_to_run_a_scan.html>`_ and `How to Visualize Scan results <https://scancode-toolkit.readthedocs.io/en/latest/tutorials/how_to_visualize_scan_results.html>`_
- An exhaustive List of `All Available Options <https://scancode-toolkit.readthedocs.io/en/latest/cli-reference/list-options.html>`_
- Documentation on `Contributing to Code Development <https://scancode-toolkit.readthedocs.io/en/latest/contribute/contrib_dev.html>`_
- Documentation on `Plugin Architecture <https://scancode-toolkit.readthedocs.io/en/latest/plugins/plugin_arch.html>`_
- `FAQ <https://scancode-toolkit.readthedocs.io/en/latest/misc/faq.html>`_

See also https://aboutcode.org for related companion projects and tools.


Installation
============

Before installing ScanCode make sure you've installed the prerequisites properly. This mainly
refers to installing the required Python interpreter (Python 3.6 is recommended). Refer
`Prerequisites <https://scancode-toolkit.readthedocs.io/en/latest/getting-started/install.html#prerequisites>`_ for detailed information on all different platforms and Python Versions.

There are 3 main ways you can `install ScanCode <https://scancode-toolkit.readthedocs.io/en/latest/getting-started/install.html>`_.

- `Installation as an Application: Downloading Releases <https://scancode-toolkit.readthedocs.io/en/latest/getting-started/install.html#installation-as-an-application-downloading-releases>`_ *(Recommended)*
- `Installation from Source Code: Git Clone <https://scancode-toolkit.readthedocs.io/en/latest/getting-started/install.html#installation-from-source-code-git-clone>`_
- `Installation as a library: via pip <https://scancode-toolkit.readthedocs.io/en/latest/getting-started/install.html#pip-install>`_

Quick Start
===========

Note the `Commands Variation <https://scancode-toolkit.readthedocs.io/en/latest/getting-started/install.html#commands-variation>`_ across Installation methods and Platforms.

You can run an example scan printed on screen as JSON::

    ./scancode -clip --json-pp - samples

Follow the `How to Run a Scan <https://scancode-toolkit.readthedocs.io/en/latest/tutorials/how_to_run_a_scan.html>`_ Tutorial
to perform a basic scan on the ``samples`` directory distributed by default with Scancode.

See more command examples::

    ./scancode --examples

Refer `How to set what will be detected in Scan <https://scancode-toolkit.readthedocs.io/en/latest/tutorials/how_to_set_what_will_be_detected_in_a_scan.html>`_
and `How to specify Scancode Output Format <https://scancode-toolkit.readthedocs.io/en/latest/tutorials/how_to_format_scan_output.html>`_ for more information.

You can also refer to `Command Line Options Synopsis <https://scancode-toolkit.readthedocs.io/en/latest/cli-reference/synopsis.html>`_ and an exhaustive List of `All Available Options <https://scancode-toolkit.readthedocs.io/en/latest/cli-reference/list-options.html>`_.

Archive extraction
==================

The archives that exist in a codebase must be extracted before running a scan:
ScanCode does not extract files from tarballs, zip files, etc. as part of the
scan. The bundled utility `extractcode` is a mostly-universal archive extractor.
For example, this command will recursively extract the mytar.tar.bz2 tarball in
the mytar.tar.bz2-extract directory::

    ./extractcode mytar.tar.bz2

Refer `All Extractcode Options <https://scancode-toolkit.readthedocs.io/en/latest/cli-reference/list-options.html#all-extractcode-options>`_ and `How To Extract Archives <https://scancode-toolkit.readthedocs.io/en/latest/tutorials/how_to_extract_archives.html>`_ for more information.

Support
=======

If you have a problem, a suggestion or found a bug, please enter a ticket at:
https://github.com/nexB/scancode-toolkit/issues

For discussions and chats, we have:

* an official Gitter channel for web-based chats at https://gitter.im/aboutcode-org/discuss
  Gitter is also accessible via an IRC bridge at https://irc.gitter.im/

* an official `#aboutcode` IRC channel on freenode (server chat.freenode.net). 
  This channel receives build and commit notifications and can be a tad noisy.
  You can use your favorite IRC client or use the web chat at
  https://webchat.freenode.net/

* a Gitter channel to discuss Documentation at https://gitter.im/aboutcode-org/gsod-season-of-docs

Source code and downloads
=========================

* https://github.com/nexB/scancode-toolkit.git
* https://github.com/nexB/scancode-toolkit/releases
* https://pypi.org/project/scancode-toolkit/
* https://github.com/nexB/scancode-thirdparty-src.git


License
=======

* Apache-2.0 with an acknowledgement required to accompany the scan output.
* Public domain CC0-1.0 for reference datasets.
* Multiple licenses (GPL2/3, LGPL, MIT, BSD, etc.) for third-party components.

See the NOTICE file and the .ABOUT files that document the origin and license of
the third-party code used in ScanCode for more details.


.. |master-cov| image:: https://codecov.io/gh/nexB/scancode-toolkit/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/nexB/scancode-toolkit/branch/master
    :alt: Master branch test coverage (Linux)
.. |devel-cov| image:: https://codecov.io/gh/nexB/scancode-toolkit/branch/develop/graph/badge.svg
    :target: https://codecov.io/gh/nexB/scancode-toolkit/branch/develop
    :alt: Develop branch test coverage (Linux)

.. |master-posix| image:: https://api.travis-ci.org/nexB/scancode-toolkit.png?branch=master 
    :target: https://travis-ci.org/nexB/scancode-toolkit
    :alt: Linux Master branch tests status
.. |devel-posix| image:: https://api.travis-ci.org/nexB/scancode-toolkit.png?branch=develop
    :target: https://travis-ci.org/nexB/scancode-toolkit
    :alt: Linux Develop branch tests status

.. |master-win| image:: https://ci.appveyor.com/api/projects/status/4webymu0l2ip8utr/branch/master?png=true
    :target: https://ci.appveyor.com/project/nexB/scancode-toolkit
    :alt: Windows Master branch tests status
.. |devel-win| image:: https://ci.appveyor.com/api/projects/status/4webymu0l2ip8utr/branch/develop?png=true
    :target: https://ci.appveyor.com/project/nexB/scancode-toolkit
    :alt: Windows Develop branch tests status

.. |docs-rtd| image:: https://readthedocs.org/projects/scancode-toolkit/badge/?version=latest
    :target: https://scancode-toolkit.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
