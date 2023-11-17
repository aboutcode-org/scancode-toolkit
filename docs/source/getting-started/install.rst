.. _install:

Comprehensive Installation
==========================


The recommended way to install ScanCode is using app archives:

- :ref:`app_install`

    The recommended method is to download the latest application release as an
    application and then configure and use directly. No knowledge of pip/git or
    other developer tools is necessary. You only need to install Python then
    download and extract the ScanCode application archive to run ScanCode.
    For standard usage that's all you need.


For advanced usage and experienced users, you can also use any of these mode:

- :ref:`docker_install`

    An alternative to installing the latest Scancode Toolkit release natively is
    to build a Docker image from the included Dockerfile. The only prerequisite
    is a working Docker installation.

- :ref:`source_code_install`

    You can clone the git source code repository and then run the configure script
    to configure and install ScanCode for local and development usage.

- :ref:`pip_install`

    To use ScanCode as a library in your application, you can install it via
    ``pip``. This is recommended for developers or users familiar with Python
    that want to embed ScanCode as a library.

----

Before Installing
-----------------

- ScanCode requires a Python version 3.7, 3.8, 3.9  or 3.10 and is
  tested on Linux, macOS, and Windows. It should work fine on FreeBSD.

.. _system_requirements:

System Requirements
^^^^^^^^^^^^^^^^^^^

- Hardware : ScanCode will run best with a modern X86 64 bits processor and at
  least 8GB of RAM and 2GB of disk space. These are minimum requirements.

- Supported operating systems: ScanCode should run on these 64-bit OSes running
  X86_64 processors:

    #. Linux: on recent 64-bit Linux distributions,
    #. Mac: on recent x86 64-bit macOS (10.15 and up, including 11 and 12),
       Use the X86 emulation mode on Apple ARM M1 CPUs.
       (Note that `pip install` does not work on ARM CPUs)
    #. Windows: on Windows 10 and up,
    #. FreeBSD.


.. _install_prerequisites:

Prerequisites
^^^^^^^^^^^^^

ScanCode needs a Python 3.7+ interpreter; We support all Python versions from
3.7 to 3.10. The default version for the application archives is Python 3.8

- **On Linux**:

    Use your package manager to install ``python3``.

    For Ubuntu, it is ``sudo apt install python3-dev``

    - On Ubuntu 16, 18, 20 and 22 run::

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

    The default Python 3 provided with macOS is 3.8.
    Alternatively you can download and install Python 3.8 from https://www.python.org/


- **On Windows**:

    Download and install Python 3.8 from https://www.python.org/

    .. Note::

      64-bit Python interpreters (x86-64) are the only interpreters supported by
      Scancode on all operating systems which means only 64-bit Windows is supported.

    See the :ref:`windows_app_install` section for more installation details.

----

.. _app_install:

Installation as an Application: Downloading Releases
-----------------------------------------------------

Get the Scancode Toolkit tarball archive of a specific version and your
operating system by going to the `project releases page <https://github.com/nexB/scancode-toolkit/releases/>`_

For example, Version 30.0.1 archive can be obtained from
`Toolkit release 30.0.1 <https://github.com/nexB/scancode-toolkit/releases/tag/v30.0.1>`_
under assets options.

.. Note::

    ScanCode app archives come with packaged with all required dependencies except
    for Python that has to be downloaded and installed separately.
    On more recent versions of Ubuntu, you will have to install Python 3.8 manually.
    One possibility is to use the Deadsnakes PPA (Personal Package Archive) which is
    a project that provides older Python version builds for Debian and Ubuntu and is
    available at https://github.com/deadsnakes/ and https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa
    ::

        sudo apt-get update && sudo apt-get upgrade
        sudo add-apt-repository ppa:deadsnakes/ppa --yes
        sudo apt-get install python3.8 python3.8-distutils


Installation on Linux and Mac
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Download the archive for your operating systen and extract
the archive from command line::

    tar -xvf scancode-toolkit-30.0.1_py38-linux.tar.gz


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

    cd path/to/extracted/ScanCode

- Press Enter.

- This will change the current location of your command prompt to the root directory where
  ScanCode is installed.

- Then type::

    scancode -h

- Press enter. This first command will configure your ScanCode installation.
  Several messages are displayed followed by the ScanCode command help.

- The installation is complete.


Un-installation
^^^^^^^^^^^^^^^

- Delete the directory in which you extracted ScanCode.
- Delete any temporary files created in your system temp and user temp directory
  under a ScanCode-prefixed directory such as .scancode-tk or .cache/scancode-tk.


----

.. _docker_install:


Installation via Docker:
------------------------

You can install Scancode Toolkit by building a Docker image from the included Dockerfile.
The prerequisite is a working `docker installation <https://docs.docker.com/engine/install/>`_.


Download the ScanCode-Toolkit Source Code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- ``git clone https://github.com/nexB/scancode-toolkit`` to get the latest
  ( :ref:`source_code_install` ) source code.


Build the Docker image
^^^^^^^^^^^^^^^^^^^^^^

Run the ``docker build`` source code checkout directory.::

    cd scancode-toolkit
    docker build --tag scancode-toolkit --tag scancode-toolkit:$(git describe --tags) .


Run using Docker
^^^^^^^^^^^^^^^^

The docker image will forward all arguments it receives directly to the ``scancode`` command.

Display help::

    docker run scancode-toolkit --help

Mount current working directory as "/project" and run a scan on a file name
apache-2.0.LICENSE directory. The JSON results will be in scan-result.json::

    docker run -v $PWD/:/project scancode-toolkit -clipeu --json-pp /project/scan-result.json /project/apache-2.0.LICENSE

This will mount your current working from the host into ``/project`` in the container
and then scan the contents. The output ``result.json`` will be written back to your
current working directory on the host.

Note that the parameters *before* ``scancode-toolkit`` are used for docker,
those after will be forwarded to scancode.


----


.. _source_code_install:

Installation from Source Code: Git Clone
-----------------------------------------

You can download the Scancode Toolkit Source Code and build from it yourself.
This is what you would want to do it if:

- You are developing ScanCode or adding new patches or want to run tests.
- You want to test or run a specific version/checkpoint/branch from the version control.


Download the ScanCode-Toolkit Source Code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run the following once you have `Git <https://git-scm.com/>`_ installed::

    git clone https://github.com/nexB/scancode-toolkit.git
    cd scancode-toolkit


Configure the build
^^^^^^^^^^^^^^^^^^^

ScanCode use a configure scripts to create an isolated virtual environment,
install required packaged dependencies.

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

ScanCode can be installed from the public PyPI repository using ``pip`` which
the standard Python package management tool.

.. NOTE::

    Note that `pip` installation method does work on ARM chips, i.e. Linux/MacOS on
    Apple M1 chips, as some non-native dependencies do not have pre-built wheels
    for ARM (like py-ahocorasick, intbitset). See :ref:`system_requirements` for
    more information. See related issues for more info:

    - `Fallback pure-python deps <https://github.com/nexB/scancode-toolkit/issues/3210>`_
    - `pip install failing on M1 <https://github.com/nexB/scancode-toolkit/issues/3205>`_

The steps are:

#. Create a Python virtual environment::

    /usr/bin/python3 -m venv venv

For more information on Python virtualenv, visit this
`page <https://docs.python-guide.org/dev/virtualenvs/#lower-level-virtualenv>`_.

#. Activate the virtual environment you just created::

    source venv/bin/activate

#. Run pip to install the latest versions of base utilities::

    pip install --upgrade pip setuptools wheel

#. Install the latest version of ScanCode::

    pip install scancode-toolkit

.. NOTE::

    For advanced usage, ``scancode-toolkit-mini`` is an alternative package with
    no default dependencies on pre-built binaries. This may come handy for some
    special use cases such as packaging for a Linux or FreeBSD distro.


To uninstall, run::

    pip uninstall scancode-toolkit


----

.. _commands_variation:

Command Invocation Variations
-----------------------------

These are the commands to invoke ScanCode based on:

- your installation methods
- your operating systems

The two form of commands are:

- Use the scancode command directly, typically on Windows or in an activated virtualenv::

    scancode [OPTIONS] <OUTPUT FORMAT OPTION(s)> <SCAN INPUT>

- Use a path to the scancode command, typically with an application installation ::

    path/to/scancode [OPTIONS] <OUTPUT FORMAT OPTION(s)> <SCAN INPUT>

These variations are summed up in the following table:

.. list-table::
    :widths: 10 5 10 50
    :header-rows: 1

    * - Installation Methods
      - Application Install
      - Pip Install
      - Install from Source Code

    * - Linux
      - path: `./scancode`
      - direct: scancode
      - path: `./scancode` or direct: `scancode`

    * - Mac
      - path: `./scancode`
      - direct: scancode
      - path: `./scancode` or direct: `scancode`

    * - Windows
      - path: `scancode`
      - direct: scancode
      - path: `scancode` or direct: `scancode`
