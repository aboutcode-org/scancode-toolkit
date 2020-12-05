These scripts help handling provision, building and tracling dependencies and
requirements files as well as building releases.


Release management
==================

* Runs only on Linux
* The scripts are:
 * release.sh: use this to build the release archives of scancode-toolkit
 * build-plugins.sh: to build  multiple plugins (outdated)
 * bump-plugins.sh: to bump the version of multiple plugins (outdated)

Dependencies and requirements
=============================

* Runs only on Linux

* Start by installing requiredd third party tools and libraries::

    pip install --requirement etc/release/requirements.txt


TODO: we need to pin the versions of our tools


Build archives of dependencies 
==============================

* TODO: explain ow to use romp


Generate requirements file
==========================

* ``python etc/release/genreqs.py --help``


Upload dependency archives to our private PyPI
==============================================

* ``python etc/release/github_release.py --help``
