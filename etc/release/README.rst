This directory contains the tools to:
- build and publish scancode releases, as wheel, sources and OS-specific bundles
- manage thirdparty dependencies: pin, build, document publish to own PyPI-like repo


Pre-requisites
==============

* Runs ONLY on Linux
* Run in the main configured scancode virtualenv
* Start by installing required tools and libraries::

    pip install --requirement etc/release/requirements.txt

TODO: we need to pin the versions of these tools


Release scripts
===============

 * scancode_release.sh: This is the main script: use this to build the release archives
   of scancode-toolkit (wheels, sdists, tarball, installers)

 * test_-*.sh: various test scripts for installation and release, launched when running
   scancode_release --test


 * TODO: scancode_publish.sh: use this to publish the built releases scancode-toolkit


Dependencies and thirdparty management scripts
==============================================

* dependencies_fetch.py will fetch packages and populate locally a thirdparty
  directory from a remote repo based on a requirements.txt file.

* packages_publish.py will publish a local thirdparty directory of Python
  packages, license and ABOUT files to a remote repo.
  You will need a GitHub personal access token for this.


Future a utilities:

* package_build.py will build on Python package version on multiple
  Python version and OSes and retrieve the results locally (for upload to a
  remote repo afterwards)
  Notes: you will need an Azure personal access token for this.
  TODO: explain ow to use romp

* requirements_gen.py: Generate locked requirements file from the current
  installed environment.


Plugins scripts
===============

TODO: these are outdated

 * plugins+build.sh: to build  multiple plugins
 * plugins_bump.sh: to bump the version of multiple plugins
