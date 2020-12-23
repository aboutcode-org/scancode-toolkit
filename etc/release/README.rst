This directory contains the tools to:
- build and publish scancode releases, as wheel, sources and OS-specific bundles
- manage thirdparty packages: pin, build, document publish to own PyPI-like repo


Pre-requisites
==============

* Runs ONLY on Linux
* Run in the main configured scancode virtualenv
* Start by installing required tools and libraries ::

    pip install --requirement etc/release/requirements.txt

TODO: we need to pin the versions of these tools


Release scripts
===============

 * **scancode_release.sh**: This is the main script to build the release
   archives for scancode-toolkit (wheels, sdists, tarball, installers). It may
   optional call **scancode_release_tests.sh** to run minimal smoke tests on the
   built release archives.

 * test_-*.sh: various test scripts for installation and release, launched when
   running scancode_release --test

 * TODO: scancode_publish.sh: use this to publish the built releases scancode-toolkit


Thirdparty packages management scripts
======================================

* **fetch_required_wheels.py and fetch_required_sources.py** will fetch packages
  and their license/ABOUT files to populate a local a thirdparty directory
  strictly from our remote repo and using only packages listed in a
  requirements.txt file.

* **upload_packages.py** will upload a local thirdparty directory of files to
  our remote repo. Requires a GitHub personal access token.

* **gen_requirements.py and gen_requirements_dev.py**: create/update
  requirements files from currently installed requirements. Note that this does
  not hash requirements for now and should be used with care as it does not deal
  with conditional requirements for some OS or Python versions. The sequence is
  to:

  * first run ./configure --clean then ./configure then run *gen_requirements.py** 

  * then run ./configure --dev then run **gen_requirements_dev.py** as this
    requires the main requirements.txt to be up-to-date first.

* **fix_thirdparty_dir.py** will fix a thirdparty directory with a best effort
  to add missing wheels, sources archives, create and fix .ABOUT, .NOTICE and
  .LICENSE files

* (TODO) **add_package.py** will add or update a Python package including wheels,
  sources and ABOUT files and this for multiple Python version and OSes(for use
  with upload_packages.py afterwards) You will need an Azure personal access
  token for buidling binaries and an optional DejaCode API key to post and fetch
  new package versions there. TODO: explain how we use romp


The other files and scripts and support and utility modules used by the main
scripts documented here.
 