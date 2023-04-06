This directory contains the tools to manage a directory of thirdparty Python
package source, wheels and metadata pin, build, update, document and publish to
a PyPI-like repo (GitHub release).

NOTE: These are tested to run ONLY on Linux.


Thirdparty packages management scripts
======================================

Pre-requisites
--------------

* There are two run "modes":

  * To generate or update pip requirement files, you need to start with a clean
    virtualenv as instructed below (This is to avoid injecting requirements
    specific to the tools used here in the main requirements).

  * For other usages, the tools here can run either in their own isolated
    virtualenv or in the the main configured development virtualenv.
    These requireements need to be installed::

        pip install --requirement etc/scripts/requirements.txt

TODO: we need to pin the versions of these tools



Generate or update pip requirement files
----------------------------------------

Scripts
~~~~~~~

**gen_requirements.py**: create/update requirements files from currently
  installed requirements.

**gen_requirements_dev.py** does the same but can subtract the main requirements
  to get extra requirements used in only development.


Usage
~~~~~

The sequence of commands to run are:


* Start with these to generate the main pip requirements file::

    ./configure --clean
    ./configure
    python etc/scripts/gen_requirements.py --site-packages-dir <path to site-packages dir>

* You can optionally install or update extra main requirements after the
  ./configure step such that these are included in the generated main requirements.

* Optionally, generate a development pip requirements file by running these::

    ./configure --clean
    ./configure --dev
    python etc/scripts/gen_requirements_dev.py --site-packages-dir <path to site-packages dir>

* You can optionally install or update extra dev requirements after the
  ./configure step such that these are included in the generated dev
  requirements.

Notes: we generate development requirements after the main as this step requires
the main requirements.txt to be up-to-date first. See **gen_requirements.py and
gen_requirements_dev.py** --help for details.

Note: this does NOT hash requirements for now.

Note: Be aware that if you are using "conditional" requirements (e.g. only for
OS or Python versions) in setup.py/setp.cfg/requirements.txt as these are NOT
yet supported.


Populate a thirdparty directory with wheels, sources, .ABOUT and license files
------------------------------------------------------------------------------

Scripts
~~~~~~~

* **fetch_thirdparty.py** will fetch package wheels, source sdist tarballs
  and their ABOUT, LICENSE and NOTICE files to populate a local directory from
  a list of PyPI simple URLs (typically PyPI.org proper and our self-hosted PyPI)
  using pip requirements file(s), specifiers or pre-existing packages files.
  Fetch wheels for specific python version and operating system combinations.

* **check_thirdparty.py** will check a thirdparty directory for errors.


Upgrade virtualenv app
----------------------

The bundled virtualenv.pyz has to be upgraded by hand and is stored under
etc/thirdparty

* Fetch https://github.com/pypa/get-virtualenv/raw/<latest tag>/public/virtualenv.pyz
  for instance https://github.com/pypa/get-virtualenv/raw/20.2.2/public/virtualenv.pyz
  and save to thirdparty and update the ABOUT and LICENSE files as needed.

* This virtualenv app contains also bundled pip, wheel and setuptools that are
  essential for the installation to work.


Other files
===========

The other files and scripts are test, support and utility modules used by the
main scripts documented here.
