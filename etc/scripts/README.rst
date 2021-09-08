This directory contains the tools to:

- manage a directory of thirdparty Python package source, wheels and metadata:
  pin, build, update, document and publish to a PyPI-like repo (GitHub release)

- build and publish scancode releases as wheel, sources and OS-specific bundles.


NOTE: These are tested to run ONLY on Linux.


Thirdparty packages management scripts
======================================

Pre-requisites
--------------

* There are two run "modes":

  * To generate or update pip requirement files, you need to start with a clean
    virtualenv as instructed below (This is to avoid injecting requirements
    specific to the tools here in the main requirements).

  * For other usages, the tools here can run either in their own isolated
    virtualenv best or in the the main configured development virtualenv.
    These requireements need to be installed::

        pip install --requirement etc/release/requirements.txt

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
    python etc/release/gen_requirements.py --site-packages-dir <path to site-packages dir>

* You can optionally install or update extra main requirements after the
  ./configure step such that these are included in the generated main requirements.

* Optionally, generate a development pip requirements file by running these::

    ./configure --clean
    ./configure --dev
    python etc/release/gen_requirements_dev.py --site-packages-dir <path to site-packages dir>

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

* **fetch_requirements.py** will fetch package wheels, their ABOUT, LICENSE and
  NOTICE files to populate a local a thirdparty directory strictly from our
  remote repo and using only pinned packages listed in one or more pip
  requirements file(s). Fetch only requirements for specific python versions and
  operating systems. Optionally fetch the corresponding source distributions.

* **publish_files.py** will upload/sync a thirdparty directory of files to our
  remote repo. Requires a GitHub personal access token.

* **build_wheels.py** will build a package binary wheel for multiple OS and
  python versions. Optionally wheels that contain native code are built
  remotely. Dependent wheels are optionally included. Requires Azure credentials
  and tokens if building wheels remotely on multiple operatin systems.

* **fix_thirdparty.py** will fix a thirdparty directory with a best effort to
  add missing wheels, sources archives, create or fetch or fix .ABOUT, .NOTICE
  and .LICENSE files. Requires Azure credentials and tokens if requesting the
  build of missing wheels remotely on multiple operatin systems.

* **check_thirdparty.py** will check a thirdparty directory for errors.

* **bootstrap.py** will bootstrap a thirdparty directory from a requirements
  file(s) to add or build missing wheels, sources archives and create .ABOUT,
  .NOTICE and .LICENSE files. Requires Azure credentials and tokens if
  requesting the build of missing wheels remotely on multiple operatin systems.



Usage
~~~~~

See each command line --help option for details.

* (TODO) **add_package.py** will add or update a Python package including wheels,
  sources and ABOUT files and this for multiple Python version and OSes(for use
  with upload_packages.py afterwards) You will need an Azure personal access
  token for buidling binaries and an optional DejaCode API key to post and fetch
  new package versions there. TODO: explain how we use romp


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
