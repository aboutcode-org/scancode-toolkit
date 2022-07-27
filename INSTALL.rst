============
Installation
============

There are a few ways you can `install ScanCode <https://scancode-toolkit.readthedocs.io/en/latest/getting-started/install.html>`_.

- Recommended standard install for everyone: Use a release download and install as an application

- Advanced installation options:
 - pip install a Python PyPI package
 - from source code using a git clone
 - using Docker


Prerequisites
-------------

Before installing ScanCode make sure you have  installed these prerequisites.
The main one is to have Python installed version 3.7, 3.8, 3.9 or 3.10

- For Linux(Ubuntu): ``sudo apt install python3.8-dev bzip2 xz-utils zlib1g libxml2-dev libxslt1-dev``
- For MacOS: Install Python 3.x from https://www.python.org/
- For Windows: Install Python 3.x from https://www.python.org/  using the 64 bits amd64 variant
- For FreeBSD: (this needs to be documented)

Refer `Prerequisites <https://scancode-toolkit.readthedocs.io/en/latest/getting-started/install.html#prerequisites>`_
for detailed information on all different operating systems and Python versions.


Use a release download and install as an application
----------------------------------------------------

- Download and extract the latest ScanCode release from
  https://github.com/nexB/scancode-toolkit/releases/

- Open a terminal window (or command prompt on Windows) and then `cd` to the
  extracted ScanCode directory. 

- Run this command to self-configure and display the initial command line help:

    - Linux/Mac : ``./scancode --help``
    - Windows : ``scancode --help``


Advanced installation: pip install a Python PyPI package
--------------------------------------------------------

- Create a virtual environment for Python 3.x and activate it::

    virtualenv -p python3 venv && source venv/bin/activate

- Run ``pip install scancode-toolkit[full]``

Note that the ``[full]`` extra option is required to get a working installation
except in some advanced use cases.



Advanced installation: using Docker
-----------------------------------

- Download the Source Code as an archive from the `GitHub releases
  <https://github.com/nexB/scancode-toolkit/releases>`_ and unzip it, or via
  `git clone`.

- Build the docker image from the `scancode-toolkit` directory::

    docker build -t scancode-toolkit .

- Mount current working directory and run a scan the mounted folder::

    docker run -v $PWD/:/project scancode-toolkit -clpeui --json-pp /project/result.json /project

Note that the parameters *before* ``scancode-toolkit`` are used by docker and
those after will be forwarded to scancode.


Advanced installation: from source code using a git clone
---------------------------------------------------------

- Download the Source Code or Use Git Clone::

    git clone https://github.com/nexB/scancode-toolkit.git
    cd scancode-toolkit

- Run the configure script for development usage:

  - On Linux/Mac: ``./configure --dev``
  - On Windows: ``configure --dev``


If this displays the `help text
<https://scancode-toolkit.readthedocs.io/en/latest/cli-reference/help-text-options.html#help-text>`_,
you are all set to start using ScanCode.
