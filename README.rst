================
ScanCode toolkit
================

A typical software project often reuses hundreds of third-party packages.
License and origin information is often scattered, not easy to find and not
normalized: ScanCode discovers and normalizes this data for you.

ScanCode is a suite of command line utilities to reliably scan a codebase for
license, copyright, package manifests and direct dependencies and other
interesting origin and licensing information discovered in source and binary
code files.

ScanCode is used by several projects and organizations such as the Eclipse
Foundation, Here.com Open Source Review Toolkit, ClearlyDefined and RedHat
Fabric8 analytics.

ScanCode provides comprehensive scan results that you can save as JSON, HTML,
CSV or SPDX. And you can use the companion `AboutCode Manager GUI app
<https://github.com/nexB /aboutcode-manager>`_ to review, search and display
scan results, statistics and graphics.

ScanCode is programed primarily in Python (with some C/C++ when performance is
critical). License and copyright detection use multiple techniques borrowed from
NLP, ML and information retrieval such as feature extraction, probabilistic
searches using inverted indexes, multi-patterns automatons and multiple local
sequence alignments for comprehensive, accurate and reasonably fast scanning.
ScanCode is easily extensible with plugins to contribute new and improved
scanner, data summarization and outputs.

As a command line application returning JSON, ScanCode is easy to integrate in
a code analysis pipeline and Ci/CD.

We are continuously working on new features, such as detecting more package
manifests or improving scanning accuracy and performance and welcome
contributions.

See our roadmap for upcoming features:
https://github.com/nexB/scancode-toolkit/wiki/Roadmap

Build and tests status
======================

+-------+--------------+-----------------+--------------+
|Branch | **Coverage** | **Linux/macOS** | **Windows**  |
+=======+==============+=================+==============+
|Master | |master-cov| | |master-posix|  | |master-win| |
+-------+--------------+-----------------+--------------+
|Develop| |devel-cov|  | |devel-posix|   | |devel-win|  |
+-------+--------------+-----------------+--------------+


Quick Start
===========

Install Python 2.7 then download and extract the latest ScanCode release
https://github.com/nexB/scancode-toolkit/releases/ 

Then run `./scancode -h` for help.


Installation
============

Pre-requisites:

* On Windows, please follow the `Comprehensive Installation instructions
  <https://github.com/nexB/scancode-toolkit/wiki/Comprehensive-Installation>`_.
  Make sure you use Python 2.7 32 bits from
  https://www.python.org/ftp/python/2.7.14/python-2.7.14.msi

* On macOS, install Python 2.7 from
  https://www.python.org/ftp/python/2.7.14/python-2.7.14-macosx10.6.pkg

  Next, download and extract the latest ScanCode release from
  https://github.com/nexB/scancode-toolkit/releases/

* On Linux install the Python 2.7 "devel" and these packages using your
  distribution package manager:

  * On Ubuntu 14.04 and 16.04 use:
    ``sudo apt-get install python-dev bzip2 xz-utils zlib1g libxml2-dev libxslt1-dev``

  * On Debian and Debian-based distros use:
    ``sudo apt-get install python-dev libbz2-1.0 xz-utils zlib1g libxml2-dev libxslt1-dev``

  * On RPM distros use:
    ``sudo yum install python-devel zlib bzip2-libs xz-libs libxml2-devel libxslt-devel``

  * On Fedora 22 and later use:
    ``sudo dnf install python-devel zlib bzip2-libs xz-libs libxml2-devel libxslt-devel``

* See also the `Comprehensive Installation instructions 
  <https://github.com/nexB/scancode-toolkit/wiki/Comprehensive-Installation>`_
  for additional instructions.


Next, download and extract the latest ScanCode release from
https://github.com/nexB/scancode-toolkit/releases/

Open a terminal window and then `cd` to the extracted ScanCode directory and run
this command to display help. ScanCode will self-configure if needed::

    ./scancode --help

You can run an example scan printed on screen as JSON::

    ./scancode --clip --json-pp - samples

See more command examples::

    ./scancode --examples


Archives extraction
===================

The archives that exist in a codebase must be extracted before running a scan:
ScanCode does not extract files from tarballs, zip files, etc. as part of the
scan. The bundled utility `extractcode` is a mostly-universal archive extractor.
For example, this command will recursively extract the mytar.tar.bz2 tarball in
the mytar.tar.bz2-extract directory::

    ./extractcode mytar.tar.bz2


Documentation & FAQ
===================

https://github.com/nexB/scancode-toolkit/wiki

See also https://aboutcode.org for related companion projects and tools.


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

* a mailing list at https://lists.sourceforge.net/lists/listinfo/aboutcode-discuss


Source code and downloads
=========================

* https://github.com/nexB/scancode-toolkit.git
* https://github.com/nexB/scancode-toolkit/releases
* https://pypi.org/project/scancode-toolkit/
* https://github.com/nexB/scancode-thirdparty-src.git


License
=======

* Apache-2.0 with an acknowledgement required to accompany the scan output.
* Public domain CC-0 for reference datasets.
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
