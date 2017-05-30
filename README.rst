================
ScanCode toolkit
================


Build and tests status
======================

+-------+--------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+-----------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------+
|Branch |                                        **Coverage**                                  |                         **Linux (Travis)**                                  |                         **MacOSX (Travis)**                                 |                         **Windows (AppVeyor)**                                                |
+=======+======================================================================================+=============================================================================+=============================================================================+===============================================================================================+
|       |.. image:: https://codecov.io/gh/nexB/scancode-toolkit/branch/master/graph/badge.svg  |.. image:: https://api.travis-ci.org/nexB/scancode-toolkit.png?branch=master |.. image:: https://api.travis-ci.org/nexB/scancode-toolkit.png?branch=master |.. image:: https://ci.appveyor.com/api/projects/status/4webymu0l2ip8utr/branch/master?png=true |
|Master |   :target: https://codecov.io/gh/nexB/scancode-toolkit/branch/master                 |   :target: https://travis-ci.org/nexB/scancode-toolkit                      |   :target: https://travis-ci.org/nexB/scancode-toolkit                      |   :target: https://ci.appveyor.com/project/nexB/scancode-toolkit                              |
|       |   :alt: Linux Master branch test coverage                                            |   :alt: Linux Master branch tests status                                    |   :alt: MacOSX Master branch tests status                                   |   :alt: Windows Master branch tests status                                                    |
+-------+--------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+-----------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------+
|       |.. image:: https://codecov.io/gh/nexB/scancode-toolkit/branch/develop/graph/badge.svg |.. image:: https://api.travis-ci.org/nexB/scancode-toolkit.png?branch=develop|.. image:: https://api.travis-ci.org/nexB/scancode-toolkit.png?branch=develop|.. image:: https://ci.appveyor.com/api/projects/status/4webymu0l2ip8utr/branch/develop?png=true|
|Develop|   :target: https://codecov.io/gh/nexB/scancode-toolkit/branch/develop                |   :target: https://travis-ci.org/nexB/scancode-toolkit                      |   :target: https://travis-ci.org/nexB/scancode-toolkit                      |   :target: https://ci.appveyor.com/project/nexB/scancode-toolkit                              |
|       |   :alt: Linux Develop branch test coverage                                           |   :alt: Linux Develop branch tests status                                   |   :alt: MacOSX Develop branch tests status                                  |   :alt: Windows Develop branch tests status                                                   |
+-------+--------------------------------------------------------------------------------------+-----------------------------------------------------------------------------+-----------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------+


ScanCode is a suite of utilities used to scan a codebase for license,
copyright, packages dependencies and other interesting information that
can be discovered in source and binary code files.

A typical software project often reuses hundreds of third-party
components. License and origin information is often scattered and not
easy to find: ScanCode discovers this data for you.

ScanCode provides reasonably accurate scan results and the line position
where each result is found. The results can be formatted as JSON or
HTML, and ScanCode provides a simple HTML app for quick visualization of
scan results.

We are continuously working on new features, such as analysis of
dependencies or improving  performance for scanning of larger codebases.

See the roadmap for upcoming features:
https://github.com/nexB/scancode-toolkit/wiki/Roadmap

.. image:: samples/screenshot.png


Quick Start
===========

For Windows, please go to the 
`Comprehensive Installation <https://github.com/nexB/scancode-toolkit/wiki/Comprehensive-Installation>`_ 
section instead.

Make sure you have Python 2.7 installed:
 * Download and install Python 2.7 32 bits for Windows 
   https://www.python.org/ftp/python/2.7.13/python-2.7.13.msi
 * Download and install Python 2.7 for Mac 
   https://www.python.org/ftp/python/2.7.13/python-2.7.13-macosx10.6.pkg

On Linux install Python 2.7 "devel" and a few extra packages:
 
 * ``sudo apt-get install python-dev bzip2 xz-utils zlib1g libxml2-dev libxslt1-dev``
   for Ubuntu 12.04, 14.04 and 16.04

 * ``sudo apt-get install python-dev libbz2-1.0 xz-utils zlib1g libxml2-dev libxslt1-dev``
   for Debian and Debian-based distros
 
 * ``sudo yum install python-devel zlib bzip2-libs xz-libs libxml2-devel libxslt-devel``
   for RPM distros
 
 * See the Comprehensive Installation for additional details and other
   Linux installations: https://github.com/nexB/scancode-toolkit/wiki/Comprehensive-Installation

Next, download and extract the latest ScanCode release from::

    https://github.com/nexB/scancode-toolkit/releases/

Open a terminal, extract the downloaded release archive, then `cd` to
the extracted directory and run this command to display the command
help. ScanCode will self-configure if needed::

    ./scancode --help

Run a sample scan saved to the `samples.html` file::

    ./scancode --format html-app samples samples.html

Then open `samples.html` in your web browser to view the scan results. 

See more command examples::

    ./scancode --examples


Support
=======

If you have a problem, a suggestion or found a bug, please enter a ticket at:
https://github.com/nexB/scancode-toolkit/issues

For other questions, discussions, and chats, we have:

- a mailing list at https://lists.sourceforge.net/lists/listinfo/aboutcode-discuss

- an official Gitter channel at https://gitter.im/aboutcode-org/discuss
  Gitter also has an IRC bridge at https://irc.gitter.im/

- an official #aboutcode IRC channel on freenode (server chat.freenode.net)
  for scancode and other related tools. Note that this receives
  notifactions from repos so it can be a tad noisy. You can use your
  favorite IRC client or use the web chat at
  https://webchat.freenode.net/


About archives
==============

All code must be extracted before running ScanCode since ScanCode will
not extract files from tarballs, zip files, etc. However, the ScanCode
Toolkit comes with a utility called extractcode that does recursive
archive extraction. For example, this command will recursively extract
the mytar.tar.bz2 tarball in the mytar.tar.bz2-extract directory::

    ./extractcode mytar.tar.bz2


Source code
===========

* https://github.com/nexB/scancode-toolkit.git
* https://github.com/nexB/scancode-thirdparty-src.git


License
=======

* Apache-2.0 with an acknowledgement required to accompany the scan output.
* Public domain CC-0 for reference datasets.
* Multiple licenses (GPL2/3, LGPL, MIT, BSD, etc.) for third-party components. 

See the NOTICE file for more details.


Documentation & FAQ
===================

https://github.com/nexB/scancode-toolkit/wiki


Basic Usage
===========

Run this command for a list of options (On Windows use `scancode`
instead of `./scancode`)::

    ./scancode --help

Run this command for a list of command line examples::

    ./scancode --examples

To run a scan on sample data, first run this::

    ./scancode --format html-app samples samples.html

Then open samples.html in your web browser to see the results.
