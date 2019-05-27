.. _installation:

Installation
============

Pre-requisites:

* On Windows, please follow the :ref:`Comprehensive Installation instructions
  <Comprehensive Installation>`.
  Make sure you use **Python 2.7 32 bits** from
  https://www.python.org/ftp/python/2.7.15/python-2.7.15.msi

* On macOS, install Python 2.7 from
  https://www.python.org/ftp/python/2.7.15/python-2.7.15-macosx10.6.pkg

  Next, download and extract the latest ScanCode release from
  https://github.com/nexB/scancode-toolkit/releases/

* On Linux install the Python 2.7 "devel" and these packages using your
  distribution package manager:

  * On Ubuntu 14, 16 and 18 use:
    ``sudo apt-get install python-dev xz-utils zlib1g libxml2-dev libxslt1-dev bzip2``

  * On Debian and Debian-based distros use:
    ``sudo apt-get install python-dev xz-utils zlib1g libxml2-dev libxslt1-dev libbz2-1.0``

  * On RPM distros use:
    ``sudo yum install python-devel xz-libs zlib libxml2-devel libxslt-devel bzip2-libs``

  * On Fedora 22 and later use:
    ``sudo dnf install python-devel xz-libs zlib libxml2-devel libxslt-devel bzip2-libs``

* See also the :ref:`Comprehensive Installation instructions
  <Comprehensive Installation>` for additional instructions.


Next, download and extract the latest ScanCode release from
https://github.com/nexB/scancode-toolkit/releases/


Open a terminal window and then `cd` to the extracted ScanCode directory and run
this command to display help. ScanCode will self-configure if needed::

    ./scancode --help

You can run an example scan printed on screen as JSON::

    ./scancode -clip --json-pp - samples

See more command examples::

    ./scancode --examples

.. _Comprehensive Installation:

Comprehensive Installation
**************************
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

* **On Linux**:

Use your package manager to install **python2.7**.
If Python 2.7 is not available from your package manager, you must compile it from sources.

For instance, visit https://github.com/dejacode/about-code-tool/wiki/BuildingPython27OnCentos6
for instructions to compile Python from sources on Centos.

  * On Ubuntu 12.04, 14.04 and 16.04, you will need to install these packages first: ``python-dev bzip2 xz-utils zlib1g libxml2-dev libxslt1-dev``

  * On Debian and Debian-based distros you will need to install these packages first: ``python-dev libbz2-1.0 xz-utils zlib1g libxml2-dev libxslt1-dev``

  * On RPM-based distros, you will need to install these packages first: ``python-devel zlib bzip2-libs xz-libs libxml2-devel libxslt-devel``

* **On Windows**:

Use the Python 2.7 32-bit (e.g. the Windows x86 MSI installer) for X86 regardless of whether you run Windows on 32-bit or 64-bit. **DO NOT USE Python X86_64 installer** even if you run 64 bit Windows.
Download Python from this url: https://www.python.org/ftp/python/2.7.13/python-2.7.13.msi

Install Python on the c: drive and **use all default installer options** (scancode will try to find python just in c:\python27\python.exe).
See the Windows installation section for more installation details.


* **On Mac**:

Download and install Python from this url:
https://www.python.org/ftp/python/2.7.13/python-2.7.13-macosx10.6.pkg

* **Do not use Unicode, non-ASCII in your installation Path**


There is a bug in underlying libraries that prevent this.


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

* In Windows Explorer (called File Explorer on Windows 10), select the downloaded ScanCode zip and right-click.
* In the pop-up menu select 'Extract All...'
* In the pop-up window 'Extract zip folders' ('Extract Compressed (Zipped) Folders' on Windows 10) use the default options to extract.
* Once the extraction is complete, a new Windows Explorer/File Explorer window will pop up.
* In this Explorer window, select the new folder that was created and right-click.
  * On Windows 10, double-click the new folder, select one of the files inside the folder (e.g., 'setup.py'), and right-click.
* In the pop-up menu select 'Properties'.
* In the pop-up window 'Properties', select the Location value. Copy this to the clipboard and close the 'Properties' window.
* Press the start menu button.  (On Windows 10, click the search box or search icon in the taskbar.)
* In the search box type:

        cmd

* Select 'cmd.exe' listed in the search results.  (On Windows 10, you may see 'Command Prompt' instead -- select that.)
* A new 'cmd.exe' window ('Command Prompt' on Windows 10) pops up.
* In this window (aka a 'command prompt'), type the following (i.e., 'cd' followed by a space):

       cd
* Right-click in this window and select Paste. This will paste the path where you extracted ScanCode.
* Press Enter.
* This will change the current location of your command prompt to the root directory where scancode is installed.
* Then type::
        scancode -h
* Press enter. This will configure your ScanCode installation.
* Several messages are displayed followed by the scancode command help.
* The installation is complete.

Un-installation
***************
* Delete the directory in which you extracted ScanCode.
* Delete any temporary files created in your system temp directory under a
  scancode_<xxx> directory.
