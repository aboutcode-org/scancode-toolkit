===============================
ScanCode toolkit
===============================


Build and tests status
======================

+-------+-----------------------------------------------------------------------------+-----------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------+
|Branch |                         **Linux (Travis)**                                  |                         **MacOSX (Travis)**                                 |                         **Windows (AppVeyor)**                                                |
+=======+=============================================================================+=============================================================================+===============================================================================================+
|       |.. image:: https://api.travis-ci.org/nexB/scancode-toolkit.png?branch=master |.. image:: https://api.travis-ci.org/nexB/scancode-toolkit.png?branch=master |.. image:: https://ci.appveyor.com/api/projects/status/4webymu0l2ip8utr/branch/master?png=true |
|Master |   :target: https://travis-ci.org/nexB/scancode-toolkit                      |   :target: https://travis-ci.org/nexB/scancode-toolkit                      |   :target: https://ci.appveyor.com/project/nexB/scancode-toolkit                              |
|       |   :alt: Linux Master branch tests status                                    |   :alt: MacOSX Master branch tests status                                   |   :alt: Windows Master branch tests status                                                    |
+-------+-----------------------------------------------------------------------------+-----------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------+
|       |.. image:: https://api.travis-ci.org/nexB/scancode-toolkit.png?branch=develop|.. image:: https://api.travis-ci.org/nexB/scancode-toolkit.png?branch=develop|.. image:: https://ci.appveyor.com/api/projects/status/4webymu0l2ip8utr/branch/develop?png=true|
|Develop|   :target: https://travis-ci.org/nexB/scancode-toolkit                      |   :target: https://travis-ci.org/nexB/scancode-toolkit                      |   :target: https://ci.appveyor.com/project/nexB/scancode-toolkit                              |
|       |   :alt: Linux Develop branch tests status                                   |   :alt: MacOSX Develop branch tests status                                  |   :alt: Windows Develop branch tests status                                                   |
+-------+-----------------------------------------------------------------------------+-----------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------+



ScanCode is a suite of utilities used to scan a codebase for license, copyright
and other interesting information that can be discovered in files.

A typical software project often reuses hundreds of thirdparty components. 
License and origin information is often scattered and not easy to find:
ScanCode discovers this data for you.

ScanCode provides reasonably accurate scan results and the line position where
each result is found. The results can be formatted as JSON or HTML, and ScanCode
provides a simple HTML app for quick visualization of scan results.

We are continuously working on new features, such as analysis of dependencies or
improving  performance for scanning of larger codebases.

See the roadmap for upcoming features:
https://github.com/nexB/scancode-toolkit/wiki/Roadmap

.. image:: samples/screenshot.png


Quick Start
===========

For Windows, please go to the Comprehensive Installation section instead.

Make sure you have Python 2.7 installed:
 * Download and install Python 2.7 32 bits for Windows https://www.python.org/ftp/python/2.7.12/python-2.7.12.msi
 * Download and install Python 2.7 for Mac https://www.python.org/ftp/python/2.7.12/python-2.7.12-macosx10.6.pkg

On Linux install Python 2.7 "devel" and a few extra packages:
 * ``sudo apt-get install python-dev libbz2 xzutils zlib1g libxml2-dev libxslt1-dev`` for most Debian/Ubuntu
 * ``sudo apt-get install python-dev libbz2-1.0 xz-utils zlib1g libxml2-dev libxslt1-dev`` for Debian Jessie/8
 * ``sudo yum install python-devel zlib bzip2-libs xz-libs libxml2-devel libxslt-devel`` for RPM distros
 * See the Comprehensive Installation bwlow for additional details and other Linux installation

Then download and extract the latest ScanCode release from::

    https://github.com/nexB/scancode-toolkit/releases/latest

Open a terminal, extract the downloaded release archive, then `cd` to the extracted
directory and run this command to display the command help. ScanCode will
self-configure if needed::

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

For other questions, discussions and chats, we have:

- a mailing list at https://lists.sourceforge.net/lists/listinfo/aboutcode-discuss

- an official #aboutcode IRC channel on freenode 
  (server chat.freenode.net) for scancode and other related tools. 
  You can use your favorite IRC client or use the web chat at 
  https://webchat.freenode.net/

- an official Gitter channel at https://gitter.im/aboutcode-org/discuss
  Gitter also has an IRC bridge at https://irc.gitter.im/


About archives
==============
All code must be extracted before running ScanCode since ScanCode will not extract files from tarballs, zip files, etc.  However, the ScanCode Toolkit comes with a utility called extractcode that does recursive archive extraction.
For example, this command will recursively extract the mytar.tar.bz2 tarball in the mytar.tar.bz2-extract directory::
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


Documentation
=============

https://github.com/nexB/scancode-toolkit/wiki


Basic Usage
===========

Run this command for a list of options (On Windows use `scancode` instead of `./scancode`)::

    ./scancode --help

Run this command for a list of command line examples::

    ./scancode --examples

To run a scan on sample data, run this::

    ./scancode --format html-app samples samples.html

Then open samples.html in your web browser.



Comprehensive Installation
==========================
ScanCode requires Python 2.7.x and is tested on Linux, Mac, and Windows. 
Make sure Python 2.7 is installed first.

System Requirements
-------------------

**Hardware** : 
ScanCode will run best with a modern X86 processor and at least 2GB of RAM and 250MB of disk.

**Supported operating systems** : ScanCode should run on these OSes:

* Linux: on most recent 64-bit Linux distributions (32-bit distros are only partially supported),
* Mac: on recent Mac OSX (10.6.8 and up),
* Windows: on Windows 7 and up (32- or 64-bit) using a 32-bit Python.

Prerequisites
-------------

ScanCode needs a Python 2.7 interpreter.
 
- **On Linux**:

  Use your package manager to install `python2.7`.
  If Python 2.7 is not available from your package manager, you must compile it from sources.

  For instance, visit https://github.com/dejacode/about-code-tool/wiki/BuildingPython27OnCentos6
  for instructions to compile Python from sources on Centos.

  * On Ubuntu 16.04 and later, you will need to install these packages first: ``python-dev bzip2 xz-utils zlib1g libxml2-dev libxslt1-dev``
  * On most Debian/Ubuntu distros, you will need to install these packages first: ``python-dev libbz2 xzutils zlib1g libxml2-dev libxslt1-dev``
* On Debian 8 (Jessie), you will need to install these packages first: ``python-dev libbz2-1.0 xz-utils zlib1g libxml2-dev libxslt1-dev``
  * On RPM-based distros, you will need to install these packages first: ``python-devel zlib bzip2-libs xz-libs libxml2-devel libxslt-devel``

- **On Windows**:

  Use the Python 2.7 32-bit (e.g. the Windows x86 MSI installer) for X86 regardless of whether you run Windows
  on 32-bit or 64-bit. **DO NOT USE Python X86_64 installer** even if you run 64 bit Windows.

  Download Python from this url:
  https://www.python.org/ftp/python/2.7.12/python-2.7.12.msi

  Install Python on the c: drive and use all default installer options.
  See the Windows installation section for more installation details.


- **On Mac**:

  Download and install Python from this url:
  https://www.python.org/ftp/python/2.7.12/python-2.7.12-macosx10.6.pkg


Installation on Linux and Mac
-----------------------------

Download and extract the latest ScanCode release from:
https://github.com/nexB/scancode-toolkit/releases/latest


Open a terminal in the extracted directory and run::

    ./scancode --help

This will configure ScanCode and display the command line help.


Installation on Windows
-----------------------

Download the latest ScanCode release zip file from:
https://github.com/nexB/scancode-toolkit/releases/latest

* In Windows Explorer, select the downloaded ScanCode zip and right-click.
* In the pop-up menu select 'Extract All...'
* In the pop-up window 'Extract zip folders' use the default options to extract.
* Once the extraction is complete, a new Windows Explorer window will pop-up.
* In this Explorer window, select the new folder that was created and right-click.
* In the pop-up menu select 'Properties'
* In the pop-up window 'Properties', select the Location value. Copy this in clipboard.
* Press the start menu button.
* In the search box type::

        cmd

* Select 'cmd.exe' listed in the search results.
* A new 'cmd.exe' window pops-up.
* In this window (aka. a command prompt), type this (this is 'cd' followed by a space)::

       cd 

* then right-click in this window and select Paste. This will paste the path where you extracted ScanCode.
* Press Enter.
* This will change the current location of your command prompt to the root directory where scancode is installed.
* Then type::

        scancode -h

* Press enter. This will configure your ScanCode installation.
* Several messages are displayed followed by the scancode command help.
* The installation is complete.


Un-installation
===============
* Delete the directory in which you extracted ScanCode.
* Delete any temporary files created in your system temp directory under a
  scancode_<xxx> directory.
