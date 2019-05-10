Installation
============

Pre-requisites:

* On Windows, please follow the `Comprehensive Installation instructions
  <https://github.com/nexB/scancode-toolkit/wiki/Comprehensive-Installation>`_.
  Make sure you use Python 2.7 32 bits from
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

* See also the `Comprehensive Installation instructions 
  <https://github.com/nexB/scancode-toolkit/wiki/Comprehensive-Installation>`_
  for additional instructions.


Next, download and extract the latest ScanCode release from
https://github.com/nexB/scancode-toolkit/releases/


Open a terminal window and then `cd` to the extracted ScanCode directory and run
this command to display help. ScanCode will self-configure if needed::

    ./scancode --help

You can run an example scan printed on screen as JSON::

    ./scancode -clip --json-pp - samples

See more command examples::

    ./scancode --examples

