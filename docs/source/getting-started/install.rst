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

- ScanCode supports Python 3.6 and higher and is tested on Linux, Mac, and Windows.
- ScanCode supports Python 3.6, 3.7, 3.8. and 3.9 when installed from ``pip``.
- When installing as an application from a release archive, Python 3.6 is required.

Make sure Python is installed first.


System Requirements
^^^^^^^^^^^^^^^^^^^

- Hardware : ScanCode will run best with a modern X86 processor and at least 4GB
  of RAM and 500MB of disk.

- Supported operating systems: ScanCode should run on these 64-bit OSes running
  X86_64 processors:

    #. Linux: on recent 64-bit Linux distributions,
    #. Mac: on recent 64-bit macOS (10.14 and up),
    #. Windows: on Windows 7 and up,


.. _install_prerequisites:

Prerequisites
^^^^^^^^^^^^^

ScanCode needs a Python 3.6 interpreter when installed as an application.

- **On Linux**:

    Use your package manager to install ``python3.6`` (*Recommended*).

    For ubuntu, it is ``sudo apt install python3.6-dev``

    - On Ubuntu 14, 16, 18 and 20 run:
      ``sudo apt install python3.6-dev bzip2 xz-utils zlib1g libxml2-dev libxslt1-dev libpopt0``

    - On Debian and Debian-based distros run:
      ``sudo apt-get install python3.6-dev libbz2-1.0 xz-utils zlib1g libxml2-dev libxslt1-devlibpopt0``

    - On RPM-based distros run:
      ``sudo yum install python3.6-devel zlib bzip2-libs xz-libs libxml2-devel libxslt-devellibpopt0``

    - On Fedora 22 and later run:
      ``sudo dnf install python3.6-devel xz-libs zlib libxml2-devel libxslt-devel bzip2-libs libpopt0``

    If these packages are not available from your package manager, you must
    compile them  from sources.

- **On Mac**:

    Download and install Python from this url:

    - Python 3.6.8: https://www.python.org/ftp/python/3.6.8/python-3.6.8-macosx10.6.pkg

- **On Windows**:

    Download and install Python from this url:

    - Python 3.6.8: https://www.python.org/ftp/python/3.6.8/python-3.6.8.exe

        Add python to PATH, as ScanCode uses the python from PATH. The last Python you install
        registers itself in the environment is the default, if you select the "Add to PATH" option
        while installing.

    .. Note::

      64-bit Python interpreters (x86-64) are the only interpreters supported by
      Scancode on all operating systems which means only 64-bit Windows is supported.

    See the :ref:`windows_app_install` section for more installation details.

.. Note::

    ScanCode comes with packaged with all dependencies, and so apart from downloading it as an
    application, only Python has to be downloaded and installed separately.

----

.. _app_install:

Installation as an Application: Downloading Releases
----------------------------------------------------

Installation on Linux and Mac
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Get the Scancode Toolkit tarball archive of a specific version and your
operating system by going to the `project releases page <https://github.com/nexB/scancode-toolkit/releases/>`_

For example, Version 21.3.31 archive can be obtained from
`Toolkit release 21.3.31 <https://github.com/nexB/scancode-toolkit/releases/tag/v21.3.31>`_
under assets options. Download the archive for your operating systen and extract
the archive from command line::

    tar -xvf scancode-toolkit-21.3.31_py36-linux.tar.xz


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

- In this window (aka a 'command prompt'), type 'cd' followed by a space and then Right-click in
  this window and select Paste. This will paste the path where you extracted ScanCode::

    cd path/to/extracted_ScanCode

- Press Enter.

- This will change the current location of your command prompt to the root directory where
  ScanCode is installed.

- Then type::

    scancode -h

- Press enter. This first command will configure your ScanCode installation.

- Several messages are displayed followed by the ScanCode command help.

- The installation is complete.


This uses the default Python present in the PATH environment variable i.e. the last Python
installed registers itself in the environment as the default. 


Un-installation
^^^^^^^^^^^^^^^

- Delete the directory in which you extracted ScanCode.
- Delete any temporary files created in your system temp directory under a ScanCode directory.

----

.. _docker_install:


Installation via Docker:
------------------------

You can install Scancode Toolkit by building a Docker image from the included Dockerfile.
The prerequisite is a working `docker installation <https://docs.docker.com/engine/install/>`_.

Download the ScanCode-Toolkit Source Code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Either download the Source Code for one of the releases ( :ref:`app_install` ) and unzip it.
- Or git clone the latest ( :ref:`source_code_install` ) Source Code.


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
----------------------------------------

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

    git checkout main

Here, ``main`` branch has the latest release of Scancode-Toolkit. You can also check out to any
of the following:

- Branches (Locally created or already present) [Example - ``main``]
- Tags (essentially version numbers) [Example - ``v21.2.25``, ``v21.3.31``]
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
- run ``source bin/activate``

On Windows:

- open a command prompt
- cd to the clone directory
- run ``configure``
- run ``Scripts\activate``

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

    For advanced usage, ``scancode-toolkit-mini`` is an alternative package with
    no default dependencies on pre-built binaries. This may come handy for some
    special use cases such as packaging for a Linux of FreeBSD distro.


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
