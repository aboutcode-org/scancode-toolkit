===============================
ScanCode toolkit
===============================

ScanCode is a suite of utilities used to scan a codebase for license, copyright
and other interesting information that can be discovered in files.

A typical software project often reuses hundreds of thirdparty components. 
License and origin information is often scattered and not easy to find:
ScanCode discovers this data for you.

ScanCode provides reasonably accurate scan results and the line position where
each result is found. The results can be formatted as JSON or HTML, and ScanCode
provides a simple HTML app for quick visualization of scan results.

This initial release of ScanCode scans only for exact license and copyright text.
We are working on new features, such as analysis of dependencies or improving 
performance for scanning of larger codebases.
See the roadmap for upcoming features:
https://github.com/nexB/scancode-toolkit/wiki/Roadmap

.. image:: samples/screenshot.png


Quick Start
===========

For Windows, please go to the Comprehensive Installation section instead.

Get Python 2.7 then download and extract the latest ScanCode release from::

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


Build and tests status
======================

+-------+-----------------------------------------------------------------------------+-----------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------+
|Branch |                         **Linux (Travis)**                                  |                         **MacOSX (Travis)**                                 |                         **Windows (AppVeyor)**                                                |
+=======+=============================================================================+=============================================================================+===============================================================================================+
|       |.. image:: https://api.travis-ci.org/nexB/scancode-toolkit.png?branch=master |.. image:: https://api.travis-ci.org/nexB/scancode-toolkit.png?branch=master |.. image:: https://ci.appveyor.com/api/projects/status/o3wl8mu4x18nropv/branch/master?png=true |
|Master |   :target: https://travis-ci.org/nexB/scancode-toolkit                      |   :target: https://travis-ci.org/nexB/scancode-toolkit                      |   :target: https://ci.appveyor.com/project/nexB/scancode-toolkit                              |
|       |   :alt: Linux Master branch tests status                                    |   :alt: MacOSX Master branch tests status                                   |   :alt: Windows Master branch tests status                                                    |
+-------+-----------------------------------------------------------------------------+-----------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------+
|       |.. image:: https://api.travis-ci.org/nexB/scancode-toolkit.png?branch=develop|.. image:: https://api.travis-ci.org/nexB/scancode-toolkit.png?branch=develop|.. image:: https://ci.appveyor.com/api/projects/status/o3wl8mu4x18nropv/branch/develop?png=true|
|Develop|   :target: https://travis-ci.org/nexB/scancode-toolkit                      |   :target: https://travis-ci.org/nexB/scancode-toolkit                      |   :target: https://ci.appveyor.com/project/nexB/scancode-toolkit                              |
|       |   :alt: Linux Develop branch tests status                                   |   :alt: MacOSX Develop branch tests status                                  |   :alt: Windows Develop branch tests status                                                   |
+-------+-----------------------------------------------------------------------------+-----------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------+


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


Support
=======

If you have a question, a suggestion or find a bug, enter a ticket at:
https://github.com/nexB/scancode-toolkit/issues


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
ScanCode will run best with a modern X86 processor and at least 2GB or Ram and 250MB of disk.

**Supported operating systems** : ScanCode should run on these OSes:

* Linux: on most recent 64-bit Linux distributions (32-bit distros are not supported for now),
* Mac: on recent Mac OSX (10.6.8 and up),
* Windows: on Windows 7 and up (32- or 64-bit) using a 32-bit Python.

Prerequisites
-------------

ScanCode needs a Python 2.7 interpreter.
 
- **On Linux**:

  Use your package manager to install `python2.7`.
  If Python 2.7 is not available from your package manager, you must compile it from sources.

  For instance, visit https://github.com/dejacode/about-code-tool/wiki/BuildingPython27OnCentos6
  for instruction to compile Python from sources on Centos.

  * On Debian/Ubuntu distros, you may need to install these packages: `libbz2 xzutils zlib1g`.
  * On RPM-based distros, you may need to install these packages: `zlib bzip2-libs xz-libs`.

- **On Windows**:

  Use the Python 2.7 (Windows x86 MSI installer) for X86 regardless of whether you run Windows
  on 32-bit or 64-bit. DO NOT USE Python X86_64 even if you run 64 bit Windows.

  Download Python from this url:
  https://www.python.org/ftp/python/2.7.10/python-2.7.10.msi

  Install Python on the c: drive and use all default installer options.
  See the Windows installation section for more installation details.


- **On Mac**:

  Download and install Python from this url:
  https://www.python.org/ftp/python/2.7.10/python-2.7.10-macosx10.6.pkg


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



===
FAQ
===

Why ScanCode?
=============

We could not find an existing tool (open source or commercial) meeting our needs:

* usable from the command line or as library
* running on Linux, Mac and Windows
* written in a higher level language such as Python
* easy to extend and evolve


How does ScanCode work?
=======================

For license detection, ScanCode uses a (large) number of license texts and license
detection 'rules' that are compiled in a search index. When scanning, the text of
the target file is extracted and used to query the license search index and find
license matches.

For copyright detection, ScanCode uses a grammar that defines the most common and
less common forms of copyright statements. When scanning, the target file text
is extracted and 'parsed' with this grammar to extract copyright statements.

Scan results are provided in various formats:

* a JSON file,
* a simple HTML 'app' that allows visualization in a local browser with a file tree,
  search, sort, and filters, and
* a simple unformatted HTML file that can opened in browser or as a spreadsheet.
 
For each scanned file, the result contains:

* its location in the codebase,
* the detected licenses and copyright statements,
* the start and end line numbers identifying where the license or copyright was found 
  in the scanned file, and
* reference information for the detected license.

For archive extraction, ScanCode uses a combination of Python modules, 7zip 
and libarchive/bsdtar to detect archive types and extract these recursively.

Several other utility modules are used such as libmagic for file and mime type
detection.


How to add a new license for detection?
=======================================
To add new license, you first need to select a new and unique license key (mit and gpl-2.0
are some of the existing license keys). All licenses are stored as plain text files in
the src/licensedcode/data/licenses directory using their key as part of the file names.

You need to create a pair of files:

* a file with the text of the license saved in a plain text file named `key`.LICENSE
* a small text data file (in YAML format) named `key`.yml that contains license information such as::

    key: my-license
    name: My License

The key name can contain only these symbols:

* lowercase letters from a to z,
* numbers from 0 to 9,and
* dash `-` and `.` period signs. No spaces.

Save these two files in the ``src/licensedcode/data/licenses/`` directory.

`Done!`

See the src/licensedcode/data/licenses/ directory for examples.


How to add a new license detection rule?
========================================
A license detection rule is a pair of files:

* a plain text rule file that is typically a variant of a license text, notice or license mention.
* a small text data file (in YAML format) documenting which license(s) should be detected for 
  the rule text. 

To add new rule, you need to pick a unique base file name. As a convention we like to include
the license key(s) that should be detected in that name to make it more descriptive.
For example: `mit_and_gpl-2.0` is a good base name. Add a suffix to make it unique if there is
already a rule with this base name. Do not use spaces or special characters in that name.

Then create the rule file in the src/licensedcode/data/rules/ directory using this name replacing 
`selected_base_name` with the base name you selected::

    selected_base_name.RULE

Save your rule text in this file.

Then create the YAML data file in the src/licensedcode/data/rules/ directory using this name::

    selected_base_name.yml

For a simple mit and gpl-2.0 detection license keys detection, the content of this file can be
this YAML snippet::

    licenses:
        - mit
        - gpl-2.0

Save these two files in the src/licensedcode/data/licenses/ directory and your are `done!`

See the src/licensedcode/data/rules/ directory for examples.


More (advanced) rules options:

* you can use a ``notes:`` text field to  document this rule.
* if no license should be detected for your .RULE text, do not add a list of license keys, just add a note.
  You can also use the special ``not-a-license`` license key as a single `licenses:` item.
* .RULE text can contain special text regions that can be ignored when scanning for licenses. 
  You can mark a template region in your rule text using {{double curly braces}} and up to five words can
  vary and still match this rule. You must add this field in your .yml data file to mark this rule as a `template`::

      template: yes

* By using a number after the opening braces, more than five words can be skipped. With `{{10 double curly braces }}`
  ten words would be skipped.
* To mark a rule as detecting a choice of licenses, add this field in your .yml file::

      license_choice: yes


How to get started with development?
====================================

ScanCode is primarily developed in Python with Python 2.7.

Source code is at:

* https://github.com/nexB/scancode-toolkit.git
* https://github.com/nexB/scancode-thirdparty-src.git

Open a terminal, clone the `scancode-toolkit` repository, cd to the clone directory and run::

    source configure

On Windows open a command prompt, cd to the clone directory and run instead::

    configure

The configure script creates an isolated Python virtual environment ready for
development usage. Rerun ``configure`` or ``source bin/activate`` when opening
a new terminal. Rerun ``configure`` after a pull or a branch merge.

To run the all tests run this command. Be patient: there are thousands of tests! ::

    py.test

To run the tests faster on four processors in parallel run::

    py.test -n 4


More info:

* Source code and license datasets are in the /src/ directory.
* Test code and test data are in the /tests/ directory.
* Datasets and test data are in /data/ sub-directories.
* Third-party components are vendored in the /thirdparty/ directory.
  ScanCode is self contained and should not require network access for installation or configuration 
  of third-part libraries.
* Additional pre-compiled vendored binaries are stored in bin/ sub-directories of the /src/ directory with
  their sources in this repo: https://github.com/nexB/scancode-thirdparty-src/
* Porting ScanCode to other  OS (FreeBSD, etc.) is possible. Enter an issue for help.
* Bugs and pull requests are welcomed.
* See the wiki and CONTRIBUTING.rst for more info.
