Comprehensive Installation
==========================

The fastest way to install Scancode-Toolkit is by using ``pip``. You can also install
ScanCode-Toolkit by compiling it from source or by Downloading and Configuring the
latest release from GitHub.

- :ref:`pip_install`
- :ref:`latest_release_download_install`
- :ref:`source_configure_install`

.. NOTE::

    After ``pip install``, you can perform a scan using only::

        scancode [OPTIONS] <OUTPUT FORMAT OPTION(s)> <SCAN INPUT>

    This is unlike other install methods where path to scancode is provided by using
    ``path/to/scancode``, or by using ``./scancode`` inside the Scancode install directory.

---

Before Installing
-----------------

ScanCode requires either Python 3.6.x or Python 2.7.x and is tested on Linux, Mac, and Windows.
Make sure Python 2.7 or Python 3.6 is installed first.

System Requirements
^^^^^^^^^^^^^^^^^^^

- Hardware : ScanCode will run best with a modern X86 processor and at least 2GB of RAM and
  250MB of disk.

- Supported operating systems : ScanCode should run on these OSes:

    #. Linux: on most recent 64-bit Linux distributions (32-bit distros are
       only partially supported),
    #. Mac: on recent Mac OSX (10.6.8 and up),
    #. Windows: on Windows 7 and up (32- or 64-bit) using a 32-bit Python.

.. _install_prerequisites:

Prerequisites
^^^^^^^^^^^^^

ScanCode needs a Python 3.6 or a Python 2.7 interpreter.

.. Note::

    ScanCode currently doesn't support Python 3.7.x, though support will be added soon.

- On Linux: Use your package manager to install ``python2.7`` or ``python3.6``. If they are not
  available from your package manager, you must compile it from sources. For instance, visit
  https://github.com/dejacode/about-code-tool/wiki/BuildingPython27OnCentos6 for instructions
  to compile Python 2.7 from sources on Centos.

- On Ubuntu 12.04, 14.04 and 16.04, you will need to install these packages first:
  ``python-dev bzip2 xz-utils zlib1g libxml2-dev libxslt1-dev``

- On Debian and Debian-based distros you will need to install these packages first:
  ``python-dev libbz2-1.0 xz-utils zlib1g libxml2-dev libxslt1-dev``

- On RPM-based distros, you will need to install these packages first:
  ``python-devel zlib bzip2-libs xz-libs libxml2-devel libxslt-devel``

- **On Windows**:

    Use the Python 2.7 32-bit (e.g. The Windows x86 MSI installer) for X86 regardless of whether
    you run Windows on 32-bit or 64-bit. DO NOT USE Python X86_64 installer even if you run 64 bit
    Windows. Download Python from this url:
    https://www.python.org/ftp/python/2.7.13/python-2.7.13.msi

    Install Python on the c: drive and use all default installer options (scancode will try to find
    python just in c:\python27\python.exe). See the Windows installation section for more
    installation details.

.. Note::

    64-bit Python interpreters (x86) are currently not supported by Scancode for Python 2.7 in
    Windows. Use 32-bit Python isntead, even with 64-bit Windows.

- On Mac: Download and install Python from this url:
  https://www.python.org/ftp/python/2.7.13/python-2.7.13-macosx10.6.pkg

.. WARNING::

    Do not use Unicode, non-ASCII in your installation Path if you are using a Python 2.7 interpreter.

---

.. _pip_install:

Installation by ``pip``
-----------------------

Scancode Toolkit can be easily installed using ``pip``. The steps are:

#. Create a Python 2.7 or Python 3.6 Virtual Environment::

    virtualenv -p /usr/bin/python3.6 venv-scancode

#. Activate the Virtual Environment you just created::

    source venv-scancode/bin/activate

#. Run ``pip install scancode-toolkit`` to Install Scancode.

.. NOTE::

    If you use Python 2.7, scancode-toolkit Version 3.0.2 is installed by default. For Python 3
    the latest version of Scancode Toolkit is installed by default.

.. WARNING::

    Requesting a specific version through ``pip install`` for Python 3 will give Errors if the
    Version isn't 3.1.x or later.

To uninstall, run ``pip uninstall scancode-toolkit``.

---

.. _latest_release_download_install:

Download and Configure latest Release
-------------------------------------

Installation on Linux and Mac
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Get the Scancode Toolkit tarball or zip archive of a specific Version by going to the
`GitHub Release Page <https://github.com/nexB/scancode-toolkit/releases/>`_

For example, Version 3.1.1 tarball or .zip archive can be obtained from
`Toolkit Release 3.1.1 <https://github.com/nexB/scancode-toolkit/releases/tag/v3.1.1>`_
under assets options. Download and extract the Archive from command line:

For ``.zip`` archive::

    unzip scancode-toolkit-3.1.1.zip

For ``.tar.bz2`` archive::

    tar -xvf scancode-toolkit-3.1.1.tar.bz2

Or Right Click and select "Extract Here".

Check whether the :ref:`install_prerequisites` are installed. Open a terminal in the extracted
directory and run::

    ./scancode --help

This will configure ScanCode and display the command line :ref:`cli_help_text`.

Installation on Windows
^^^^^^^^^^^^^^^^^^^^^^^

- Download the latest ScanCode release zip file from
  https://github.com/nexB/scancode-toolkit/releases/

- In Windows Explorer (called File Explorer on Windows 10), select the downloaded ScanCode zip
  and right-click.

- In the pop-up menu select 'Extract All...'

- In the pop-up window 'Extract zip folders' ('Extract Compressed (Zipped) Folders' on Windows 10)
  use the default options to extract.

- Once the extraction is complete, a new Windows Explorer/File Explorer window will pop up.

- In this Explorer window, select the new folder that was created and right-click.

.. note::

  On Windows 10, double-click the new folder, select one of the files inside the folder
  (e.g., 'setup.py'), and right-click.

- In the pop-up menu select 'Properties'.

- In the pop-up window 'Properties', select the Location value. Copy this to the clipboard and
  close the 'Properties' window.

- Press the start menu button (On Windows 10, click the search box or search icon in the taskbar.)

- In the search box type::

    cmd

- Select 'cmd.exe' listed in the search results.
  (On Windows 10, you may see 'Command Prompt' instead -- select that.)

- A new 'cmd.exe' window ('Command Prompt' on Windows 10) pops up.

- In this window (aka a 'command prompt'), type the following (i.e., 'cd' followed by a space)::

    cd

- Right-click in this window and select Paste.
  This will paste the path where you extracted ScanCode.

- Press Enter.

- This will change the current location of your command prompt to the root directory where
  ScanCode is installed.

- Then type::

    scancode -h

- Press enter. This will configure your ScanCode installation.

- Several messages are displayed followed by the scancode command help.

- The installation is complete.

Un-installation
^^^^^^^^^^^^^^^

- Delete the directory in which you extracted ScanCode.
- Delete any temporary files created in your system temp directory under a ScanCode directory.

---

.. _source_configure_install:

Build From Source
-----------------

You can also download the Scancode Toolkit Source Code and build from it yourself. This is how you
would want to do it if:

- You are Adding new patches to Scancode and want to test it.
- You want to test a specific Version/Checkpoint/Branch from the VCS


Download the ScanCode-Toolkit Source Code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you don't have the ScanCode Toolkit Source Code downloaded, get it from it's official Repository
(Downloaded as a .zip file) or run the following::

    git clone https://github.com/nexB/scancode-toolkit.git
    cd scancode-toolkit

Now, by default the files are checked out to the develop branch, but you can jump to any checkpoint
using the following command::

    git checkout master

Here, ``master`` branch has the latest release of Scancode-Toolkit. You can also check out to any
of the following:

- Branches (Locally created or already present)
- Tags (essentially Version Numbers) [Example - ``v3.1.1``, ``v3.1.0`` etc]
- Commits (use the shortened commit hash) [Example - ``4502055``, ``f276398`` etc]

Configure the build
^^^^^^^^^^^^^^^^^^^

ScanCode use the Configure scripts to install a virtualenv, install required packaged dependencies
as pip requirements and more configure tasks such that ScanCode can be installed in a
self-contained way with no network connectivity required.

Open a terminal, clone the scancode-toolkit repository, cd to the clone directory and run::

    ./configure

On Windows open a command prompt, cd to the clone directory and run instead::

    configure

Now you are ready to use the freshly configured scancode-toolkit.
