Comprehensive Installation
==========================


There are four main ways to install ScanCode.

- :ref:`app_install`

    The recommended method is to download the latest application release as an
    application and then configure and use directly. No knowledge of pip/git or
    other developer tools is necessary.

- :ref:`docker_install`

    An alternative to installing the latest Scancode Toolkit release natively is
    to build a Docker image from the included Dockerfile. The only prerequisite
    is a working Docker installation.

- :ref:`source_code_install`

    You can clone the git source code repository and then run a configure script
    to configure and install ScanCode.

- :ref:`pip_install`

    To use ScanCode as a library in your application, you can install it via
    ``pip``. This is recommended for developers/users familiar with Python.

----

Before Installing
-----------------

- ScanCode requires a Python version 3.7, 3.8, 3.9  or 3.10 and is
  tested on Linux, macOS, and Windows. It should work fine on FreeBSD.


System Requirements
^^^^^^^^^^^^^^^^^^^

- Hardware : ScanCode will run best with a modern X86 processor and at least 4GB
  of RAM and 500MB of disk. These are bare minimum requirements.

- Supported operating systems: ScanCode should run on these 64-bit OSes running
  X86_64 processors:

    #. Linux: on recent 64-bit Linux distributions,
    #. Mac: on recent 64-bit macOS (10.14 and up),
    #. Windows: on Windows 10 and up,
    #. FreeBSD,


.. _install_prerequisites:

Prerequisites
^^^^^^^^^^^^^

ScanCode needs a Python 3.7+ interpreter; We support all Python versions from
3.7 to 3.10.

- **On Linux**:

    Use your package manager to install ``python3``.

    For Ubuntu, it is ``sudo apt install python3-dev``

    - On Ubuntu 14, 16, 18 and 20 run::

          sudo apt install python-dev bzip2 xz-utils zlib1g libxml2-dev libxslt1-dev libpopt0

    - On Debian and Debian-based distros run::

          sudo apt-get install python3-dev libbz2-1.0 xz-utils zlib1g libxml2-dev libxslt1-dev libpopt0

    - On RPM-based distros run::

          sudo yum install python3.8-devel zlib bzip2-libs xz-libs libxml2-devel libxslt-devel libpopt0

    - On Fedora 22 and later run::

          sudo dnf install python3.8-devel xz-libs zlib libxml2-devel libxslt-devel bzip2-libs libpopt0


    If these packages are not available from your package manager, you must
    compile them  from sources.

- **On Mac**:

    Download and install Python 3.7 or higher from https://www.python.org/

- **On Windows**:

    Download and install Python 3.7 or higher from https://www.python.org/

    .. Note::

      64-bit Python interpreters (x86-64) are the only interpreters supported by
      Scancode on all operating systems which means only 64-bit Windows is supported.

    See the :ref:`windows_app_install` section for more installation details.

.. Note::

    ScanCode app archives come with packaged with all required dependencies except
    for Python that has to be downloaded and installed separately.

----

.. _app_install:

Installation as an Application: Downloading Releases
-----------------------------------------------------

Installation on Linux and Mac
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Get the Scancode Toolkit tarball archive of a specific version and your
operating system by going to the `project releases page <https://github.com/nexB/scancode-toolkit/releases/>`_

For example, Version 21.8.1 archive can be obtained from
`Toolkit release 21.8.1 <https://github.com/nexB/scancode-toolkit/releases/tag/v21.8.1>`_
under assets options. Download the archive for your operating systen and extract
the archive from command line::

    tar -xvf scancode-toolkit-21.8.1_py39-linux.tar.xz


Or, on Linux, right click and select "Extract Here".

Check whether the :ref:`install_prerequisites` are installed. Open a terminal
in the extracted directory and run::

    ./scancode --help

This will configure ScanCode and display the command line :ref:`cli_help_text`.


.. _windows_app_install:

Installation on Windows 10
^^^^^^^^^^^^^^^^^^^^^^^^^^

- Download the latest ScanCode release zip file for Windows from the latest
  version at https://github.com/nexB/scancode-toolkit/releases/

- In the File Explorer, select the downloaded ScanCode zip and right-click.

- In the pop-up menu select 'Extract All...'

- In the pop-up window 'Extract Compressed (Zipped) Folders' use the default options to extract.

- Once the extraction is complete, a new File Explorer window will pop up.

- In this Explorer window, select the new folder that was created and right-click.

.. note::

  On Windows 10, double-click the new folder, select one of the files inside the folder
  (e.g., 'setup.py'), and right-click.

- In the pop-up menu select 'Properties'.

- In the pop-up window 'Properties', select the Location value. Copy this to the clipboard and
  close the 'Properties' window.

- Press the start menu button, click the search box or search icon in the taskbar.

- In the search box type::

    cmd

- Select 'cmd.exe' or 'Command Prompt' listed in the search results.

- A new 'Command Prompt'pops up.

- In this window (aka a 'command prompt'), type 'cd' followed by a space and
  then Right-click in this window and select Paste. This will paste the path you
  copied before and is where you extracted ScanCode::

    cd path/to/extracted_ScanCode

- Press Enter.

- This will change the current location of your command prompt to the root directory where
  ScanCode is installed.

- Then type::

    scancode -h

- Press enter. This first command will configure your ScanCode installation.

- Several messages are displayed followed by the ScanCode command help.

- The installation is complete.


Un-installation
^^^^^^^^^^^^^^^

- Delete the directory in which you extracted ScanCode.
- Delete any temporary files created in your system temp and user temp directory
  under a scanCode-prefixed directory.

----

.. _docker_install:


Installation via Docker:
------------------------

You can install Scancode Toolkit by building a Docker image from the included Dockerfile.
The prerequisite is a working `docker installation <https://docs.docker.com/engine/install/>`_.


Download the ScanCode-Toolkit Source Code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Either download the Source Code for one of the releases ( :ref:`app_install` )
  and unzip it.
- Or ``git clone https://github.com/nexB/scancode-toolkit`` to get the latest
  ( :ref:`source_code_install` ) Source Code.


Build the Docker image
^^^^^^^^^^^^^^^^^^^^^^

The ``docker build`` command needs to run in the directory of the source code,
make sure to ``cd`` into the correct directory.::

    cd scancode-toolkit
    docker build -t scancode-toolkit .


Run using Docker
^^^^^^^^^^^^^^^^

The docker image will forward all arguments it receives directly to the ``scancode`` command.

Display help::

    docker run scancode-toolkit --help

Mount current working directory and run scan on mounted folder::

    docker run -v $PWD/:/project scancode-toolkit -clpeui --json-pp /project/result.json /project

This will mount your current working from the host into ``/project`` in the container
and then scan the contents. The output ``result.json`` will be written back to your
current working directory on the host.

Note that the parameters *before* ``scancode-toolkit`` are used for docker,
those after will be forwarded to scancode.

----


.. _source_code_install:

Installation from Source Code: Git Clone
-----------------------------------------

You can also download the Scancode Toolkit Source Code and build from it yourself. This is how you
would want to do it if:

- You are adding new patches to Scancode and want to test it. So you build ScanCode locally
  with your added changes.

- You want to test a specific version/checkpoint/branch from the VCS.


Download the ScanCode-Toolkit Source Code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you don't have the ScanCode Toolkit Source Code downloaded, get it from its
`official Repository <https://github.com/nexB/scancode-toolkit/>`_ (Downloaded as a .zip file)

Or you can run the following if you have `Git <https://git-scm.com/>`_ installed::

    git clone https://github.com/nexB/scancode-toolkit.git
    cd scancode-toolkit

Now, by default the files are checked out to the develop branch, but you can jump to any checkpoint
using the following command::

    git checkout develop

Here, ``develop`` branch has the latest release of Scancode-Toolkit.
You can also check out to any of the following:

- Branches (Locally created or already present) [Example - ``develop``]
- Tags (essentially version numbers) [Example - ``v21.8.1``, ``v21.5.31``]
- Commits (use the shortened commit hash) [Example - ``4502055``, ``f276398``]


Configure the build
^^^^^^^^^^^^^^^^^^^

ScanCode use the Configure scripts to install a virtualenv, install required packaged dependencies
as pip requirements and more configure tasks such that ScanCode can be installed in a
self-contained way with no network connectivity required.

On Linux/Mac:

- Open a terminal
- cd to the clone directory
- run ``./configure``
- run ``source venv/bin/activate``

On Windows:

- open a command prompt
- cd to the clone directory
- run ``configure``
- run ``venv\Scripts\activate``

Now you are ready to use the freshly configured scancode-toolkit.

.. NOTE::

    For use in development, run instead ``configure --dev``. If your face
    issues while configuring a previous version, ``configure --clean`` to
    clean and reset your enviroment. You will need to run ``configure`` again.


----

.. _pip_install:

Installation as a library: via ``pip``
--------------------------------------

ScanCode can be installed using ``pip``, the default Python Package Manager.
The steps are:

#. Create a Python virtual environment::

    /usr/bin/python3 -m venv venv

For more information on Python virtualenv, visit this
`page <https://docs.python-guide.org/dev/virtualenvs/#lower-level-virtualenv>`_.

#. Activate the virtual environment you just created::

    source venv/bin/activate

#. Run ``pip install --upgrade pip setuptools wheel`` to install the latest
   versions of base utilities.

#. Run ``pip install scancode-toolkit`` to install the latest version of ScanCode.

.. NOTE::

    For advanced usage, ``scancode-toolkit-mini`` is an alternative package with
    no default dependencies on pre-built binaries. This may come handy for some
    special use cases such as packaging for a Linux or FreeBSD distro.


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
