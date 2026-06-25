.. _install-scancode:

Installing ScanCode
===================

.. toctree::
   :maxdepth: 2
   :hidden:

   install-scancode-from-release-archives
   install-scancode-using-docker
   install-scancode-from-source
   install-scancode-using-pip

.. note::

    ScanCode requires a Python version between 3.9 to 3.13 and is tested on Linux, macOS, and Windows

.. list-table::
   :width: 100%
   :header-rows: 1

   * - Method
     - Description
   * - :ref:`install-scancode-from-release-archives`
     - | Our **recommended method for new users** is to install Python, download and extract
       | the latest release archive to run ScanCode.
       | No knowledge of pip, git, or other developer tools is required for standard usage.
   * - :ref:`install-scancode-using-docker`
     - | Install ScanCode from its Git source code repository using Docker
       |
       | An alternative to installing the latest ScanCode-Toolkit release natively is
       | to build a Docker image from the included Dockerfile. The only prerequisite
       | is a working Docker installation.
   * - :ref:`install-scancode-from-source`
     - | Install ScanCode from its Git source code repository using the configure script
       |
       | Clone the git source code repository and then run the configure script
       | to configure and install ScanCode for local and development usage.
   * - :ref:`install-scancode-using-pip`
     - | Install ScanCode using pip from Python Package Index (PyPI)
       |
       | To use ScanCode as a library in your application, you can install it via
       | ``pip``. This is recommended for developers or users familiar with Python
       | that want to embed ScanCode as a library
   * - Install from Fedora’s repository
     - | ScanCode is part of main Fedora Linux repository in Fedora 40 and newer.
       | This is recommended for production deployments.
       |
       | Install ScanCode from the command line interface using:

       .. code-block:: shell

          dnf install scancode-toolkit

       To uninstall ScanCode, run:

       .. code-block:: shell

          dnf remove scancode-toolkit


.. _install-scancode-installation-prerequisites:

Installation prerequisites
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _install-scancode-system-requirements:

System requirements
^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Hardware : ScanCode will run best with a modern X86 64 bits processor and at
  least 8GB of RAM and 2GB of disk space. These are minimum requirements.

- Supported operating systems: ScanCode should run on these 64-bit OSes running
  X86_64 processors:

    - Linux: any recent 64-bit Linux distributions
    - Mac (Intel): x86 64-bit macOS 10.15 or newer
    - | Mac (Apple Silicon): use the X86 emulation mode on Apple ARM M1 CPUs.
      | (Note that `pip install` does not work on ARM CPUs)
    - Windows: Windows 10 or newer
    - FreeBSD

.. _install-scancode-required-packages:

Required packages
^^^^^^^^^^^^^^^^^

ScanCode needs a Python 3.9+ interpreter; We support all Python versions from
3.9 to 3.12. The default version for the application archives is Python 3.9

Linux
"""""

Use your package manager to install ``python3``.

For Ubuntu, it is ``sudo apt install python3-dev``

- On Ubuntu 16, 18, 20 ,22 and 24 run::

    sudo apt install python-dev bzip2 xz-utils zlib1g libxml2-dev libxslt1-dev libpopt0

- On Debian and Debian-based distros run::

    sudo apt-get install python3-dev libbz2-1.0 xz-utils zlib1g libxml2-dev libxslt1-dev libpopt0

- On RPM-based distros run::

    sudo yum install python3.9-devel zlib bzip2-libs xz-libs libxml2-devel libxslt-devel libpopt0

- On Fedora 22 and later run::

    sudo dnf install python3.9-devel xz-libs zlib libxml2-devel libxslt-devel bzip2-libs libpopt0

If these packages are not available from your package manager, you must
compile them  from sources.


MacOS
"""""

The default Python 3 provided with macOS is 3.9.
Alternatively you can download and install Python 3.9 from https://www.python.org/


Windows
"""""""

Download and install Python 3.9 from https://www.python.org/

.. Note::

    64-bit Python interpreters (x86-64) are the only interpreters supported by
    ScanCode on all operating systems which means only 64-bit Windows is supported.

See the :ref:`install-scancode-from-release-archives-windows` section for more installation details.
