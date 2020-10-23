Comprehensive Installation
==========================

There are 4 main ways you can install ScanCode.

- :ref:`app_install`

    The recommended method for installing ScanCode is Downloading the latest release as an
    application and then configure and use directly. This is easy because no knowledge of pip/git
    or other developer tools is necessary.

- :ref:`docker_install`

    An alternative to installing the latest Scancode Toolkit release natively is to build
    a Docker image from the included Dockerfile. This is easy because the only prerequisite
    is a working Docker installation.

- :ref:`source_code_install`

    You can download/clone the source code repository via git/GitHub and then run a configure script
    to install ScanCode.

- :ref:`pip_install`

    To use ScanCode as a library in your application, you can install it via ``pip``. This is
    recommended for developers/users familiar with Package managers/virtualenv.

----

Before Installing
-----------------

ScanCode requires either Python 3.6.x or Python 2.7.x and is tested on Linux, Mac, and Windows.
Make sure Python 3.6 or Python 2.7 is installed first.

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

ScanCode needs a Python 3.6 (*highly recommended*) or a Python 2.7 interpreter.

.. Note::

    ScanCode currently doesn't support versions above Python 3.6.x, though support will be added soon.

- **On Linux**:

    Use your package manager to install ``python3.6`` (*Recommended*) or ``python2.7``.

    For ubuntu, it is ``sudo apt install python3.6-dev``

    - On Ubuntu 14, 16 and 18, run:
      ``sudo apt install python3.6-dev bzip2 xz-utils zlib1g libxml2-dev libxslt1-dev``

    - On Debian and Debian-based distros run:
      ``sudo apt-get install python3.6-dev libbz2-1.0 xz-utils zlib1g libxml2-dev libxslt1-dev``

    - On RPM-based distros run:
      ``sudo yum install python3.6-devel zlib bzip2-libs xz-libs libxml2-devel libxslt-devel``

    - On Fedora 22 and later run:
      ``sudo dnf install python3.6-devel xz-libs zlib libxml2-devel libxslt-devel bzip2-libs``

    If they are not available from your package manager, you must compile it from sources.
    For instance, visit this `wiki <https://github.com/dejacode/about-code-tool/wiki/BuildingPython27OnCentos6>`_
    for instructions to compile Python 2.7 from sources on Centos.

    To install Python 2.7 instead, replace ``python3.6-dev`` with ``python-dev`` (or ``devel``)
    according to your specific platform.

- **On Mac**:

    Download and install Python from this url:

    - Python 3.6.8 (*recommended*): https://www.python.org/ftp/python/3.6.8/python-3.6.8-macosx10.6.pkg
    - Python 2.7.17 : https://www.python.org/ftp/python/2.7.17/python-2.7.17-macosx10.6.pkg

- **On Windows**:

    Download and install Python from this url:

    - Python 3.6.8 (*recommended*): https://www.python.org/ftp/python/3.6.8/python-3.6.8.exe

        Add python to PATH, as ScanCode uses the python from PATH. The last Python you install
        registers itself in the environment is the default, if you select the "Add to PATH" option
        while installing.

    - Python 2.7.17 : https://www.python.org/ftp/python/2.7.17/python-2.7.17.msi

        Install Python on the c: drive and use all default installer options (ScanCode will try to
        find python just in c:python27python.exe).

    .. Note::

      64-bit Python interpreters (x86-64) are currently not supported by Scancode for Python 3.6/2.7
      in Windows. Use 32-bit Python instead, even with 64-bit Windows. For Python 2.7, use the
      32 bit MSI installer linked above.

    See the :ref:`windows_app_install` section for more installation details.

.. WARNING::

    Do not use Unicode, non-ASCII in your installation Path if you are using a Python 2.7 interpreter.

.. Note::

    ScanCode comes with packaged with all dependencies, and so apart from downloading it as an
    application, only Python has to be downloaded and installed separately.

----

.. _app_install:

Installation as an Application: Downloading Releases
----------------------------------------------------

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

Or, Right Click and select "Extract Here".

Check whether the :ref:`install_prerequisites` are installed. Open a terminal in the extracted
directory and run::

    ./scancode --help

This will configure ScanCode and display the command line :ref:`cli_help_text`.

.. _windows_app_install:

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

- In this window (aka a 'command prompt'), type 'cd' followed by a space and then Right-click in
  this window and select Paste. This will paste the path where you extracted ScanCode::

    cd path/to/extracted_ScanCode

- Press Enter.

- This will change the current location of your command prompt to the root directory where
  ScanCode is installed.

- Then type::

    scancode -h

- Press enter. This will configure your ScanCode installation.

- Several messages are displayed followed by the ScanCode command help.

- The installation is complete.

This uses the default Python present in the PATH environment variable i.e. the last Python
installed registers itself in the environment is the default. You can also use the ``configure``
script to explicitly provide the Python path to ScanCode.

- Follow the Instructions above till changing the current location of your command prompt to the
  root directory where ScanCode is installed.

- Run this command with the path to Python Executable::

    configure --python path/to/python

- You can also use ``path`` instead of ``path/to/python`` to use the python from PATH environment
  variable. More information is available at the `configure <https://github.com/nexB/scancode-toolkit/blob/develop/configure.bat>`_ script (L6-L15).

- Now you can run ``scancode -h`` to display the Help Text, and here the installation is complete.

Un-installation
^^^^^^^^^^^^^^^

- Delete the directory in which you extracted ScanCode.
- Delete any temporary files created in your system temp directory under a ScanCode directory.

----

.. _docker_install:

Installation via Docker:
------------------------

You can install Scancode Toolkit by building a Docker image from the included Dockerfile.

Download the ScanCode-Toolkit Source Code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Either download the Source Code for one of the releases ( :ref:`app_install` ) and unzip it.
- Or git clone the latest ( :ref:`source_code_install` ) Source Code.


Build the Docker image
^^^^^^^^^^^^^^^^^^^^^^

The ``docker build`` command needs to run in the directory of the source code,
make sure to ``cd`` into the correct directory.

    cd scancode-toolkit
    docker build -t scancode-toolkit .

Run using Docker
^^^^^^^^^^^^^^^^

The docker image will forward all arguments it receives directly to the ``scancode`` command.

Display help:

    docker run scancode-toolkit --help

Mount current working directory and run scan on mounted folder:

    docker run -v $PWD/:/project scancode-toolkit -clpeui --json-pp /project/result.json /project

This will mount your current working from the host into ``/project`` in the container
and then scan the contents. The output ``result.json`` will be written back to your
corrent working directory on the host.

Note that the parameters *before* ``scancode-toolkit`` are used for docker,
those after will be forwarded to scancode.

----

.. _source_code_install:

Installation from Source Code: Git Clone
----------------------------------------

You can also download the Scancode Toolkit Source Code and build from it yourself. This is how you
would want to do it if:

- You are Adding new patches to Scancode and want to test it. So you build ScanCode locally
  with your added changes.

- You want to test a specific Version/Checkpoint/Branch from the VCS.

Download the ScanCode-Toolkit Source Code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you don't have the ScanCode Toolkit Source Code downloaded, get it from its
`official Repository <https://github.com/nexB/scancode-toolkit/>`_ (Downloaded as a .zip file)

Or you can run the following if you have `Git <https://git-scm.com/>`_ installed::

    git clone https://github.com/nexB/scancode-toolkit.git
    cd scancode-toolkit

Now, by default the files are checked out to the develop branch, but you can jump to any checkpoint
using the following command::

    git checkout master

Here, ``master`` branch has the latest release of Scancode-Toolkit. You can also check out to any
of the following:

- Branches (Locally created or already present) [Example - ``master``, ``develop`` etc]
- Tags (essentially Version Numbers) [Example - ``v3.1.1``, ``v3.1.0`` etc]
- Commits (use the shortened commit hash) [Example - ``4502055``, ``f276398`` etc]

Configure the build
^^^^^^^^^^^^^^^^^^^

ScanCode use the Configure scripts to install a virtualenv, install required packaged dependencies
as pip requirements and more configure tasks such that ScanCode can be installed in a
self-contained way with no network connectivity required.

On Linux/Mac:

- Open a terminal
- cd to the clone directory
- run ``./configure``

On Windows:

- open a command prompt
- cd to the clone directory
- run instead ``configure``

Now you are ready to use the freshly configured scancode-toolkit.

----

.. _pip_install:

Installation as a library: via ``pip``
--------------------------------------

ScanCode can be installed using ``pip``, the default Python Package Manager. The steps are:

#. Create a Python 3.6 Virtual Environment::

    virtualenv -p /usr/bin/python3.6 venv-scancode

For more information on Python virtualenv, visit this `page <https://docs.python-guide.org/dev/virtualenvs/#lower-level-virtualenv>`_.

#. Activate the Virtual Environment you just created::

    source venv-scancode/bin/activate

#. Run ``pip install scancode-toolkit`` to install the latest version of Scancode.

.. NOTE::

    If you use Python 2.7, scancode-toolkit Version 3.0.2 is installed by default. For Python 3
    the latest version of Scancode Toolkit is installed by default. Requesting a specific version
    through ``pip install`` for Python 3 will give Errors if the Version isn't 3.1.x or later.

.. WARNING::

    Python 3.7.x and 3.8.x is not supported yet.

To uninstall, run ``pip uninstall scancode-toolkit``.

----

.. _commands_variation:

Commands Variation
------------------

The commands to run ScanCode varies for:

- Different Installation Methods
- OS used

The two types of commands are:

- ``scancode [OPTIONS] <OUTPUT FORMAT OPTION(s)> <SCAN INPUT>``
- ``path/to/scancode OPTIONS] <OUTPUT FORMAT OPTION(s)> <SCAN INPUT>``

In the second case, ``./scancode`` is used if already in the directory.

These variations are summed up in the following table:

.. list-table::
    :widths: 10 5 10 50
    :header-rows: 1

    * - Installation Methods
      - Application Install
      - Pip Install
      - Install from Source Code

    * - Linux
      - `./scancode`
      - `scancode`
      - `./scancode`

    * - Mac
      - `./scancode`
      - `scancode`
      - `./scancode`

    * - Windows
      - `scancode`
      - `scancode`
      - `scancode`

To sum it up, ``scancode`` is used in these two cases:

- If ``pip`` install is used.
- If the OS is Windows.

In all other cases, ``./scancode`` is used.
