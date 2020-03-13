============
Installation
============

There are 3 main ways you can `install ScanCode <https://scancode-toolkit.readthedocs.io/en/latest/getting-started/install.html>`_.

- Installation as an Application: Downloading Releases (Recommended)
- Installation as a library: via pip
- Installation from Source Code: Git Clone

Prerequisites
-------------

Before installing ScanCode make sure you've installed the prerequisites properly. This mainly
refers to installing the required Python interpreter (Python 3.6 is recommended).

- For Linux(Ubuntu): ``sudo apt install python3.6-dev bzip2 xz-utils zlib1g libxml2-dev libxslt1-dev``
- For MacOS: Install Python 3.6.8 from https://www.python.org/ftp/python/3.6.8/python-3.6.8-macosx10.6.pkg
- For Windows: Install Python 3.6.8 from https://www.python.org/ftp/python/3.6.8/python-3.6.8.exe

Refer `Prerequisites <https://scancode-toolkit.readthedocs.io/en/latest/getting-started/install.html#prerequisites>`_ for detailed information on all different platforms and Python Versions.

Installation as an Application : Downloading Releases
-----------------------------------------------------

#. Download and extract the latest ScanCode release from https://github.com/nexB/scancode-toolkit/releases/

#. Open a terminal window and then `cd` to the extracted ScanCode directory. 

#. Run this command to self-configure and display the help-text.

    - Linux/Mac : ``./scancode --help``
    - Windows : ``scancode --help``

Installation as a library: via pip
----------------------------------

#. Create a Python 3.6 Virtual Environment and activate the same::

    virtualenv -p /usr/bin/python3.6 venv-scancode && source venv-scancode/bin/activate

#. Run ``pip install scancode-toolkit`` 

Installation from Source Code: Git Clone
----------------------------------------

#. Download the Source Code or Use Git Clone::

    git clone https://github.com/nexB/scancode-toolkit.git
    cd scancode-toolkit

#. You can jump to any checkpoint/Branch/Commit using the following command::

    git checkout master

#. Run the Configure Script

  - On Linux/Mac: ``./configure``
  - On Windows: ``configure``


Note the `Commands will vary <https://scancode-toolkit.readthedocs.io/en/latest/getting-started/install.html#commands-variation>`_ across different Installation methods and Platforms.

If this displays the `Help Text <https://scancode-toolkit.readthedocs.io/en/latest/cli-reference/help-text-options.html#help-text>`_, you are all set to start using ScanCode.