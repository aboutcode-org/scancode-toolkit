A Simple Python Project Skeleton
================================
This repo attempts to standardize our python repositories using modern python
packaging and configuration techniques. Using this `blog post`_ as inspiration, this
repository will serve as the base for all new python projects and will be adopted to all
our existing ones as well.

.. _blog post: https://blog.jaraco.com/a-project-skeleton-for-python-projects/

Usage
=====
A brand new project
-------------------
.. code-block:: bash

    git init my-new-repo
    cd my-new-repo
    git pull git@github.com:nexB/skeleton

    # Create the new repo on GitHub, then update your remote
    git remote set-url origin git@github.com:nexB/your-new-repo.git

From here, you can make the appropriate changes to the files for your specific project.

Update an existing project
---------------------------
.. code-block:: bash

    cd my-existing-project
    git remote add skeleton git@github.com:nexB/skeleton
    git fetch skeleton
    git merge skeleton/main --allow-unrelated-histories

This is also the workflow to use when updating the skeleton files in any given repository.

Customizing
-----------

You typically want to perform these customizations:

- remove or update the src/README.rst and tests/README.rst files
- check the configure and configure.bat defaults

Initializing a project
----------------------

All projects using the skeleton will be expected to pull all of it dependencies
from thirdparty.aboutcode.org/pypi or the local thirdparty directory, using
requirements.txt and/or requirements-dev.txt to determine what version of a
package to collect. By default, PyPI will not be used to find and collect
packages from.

In the case where we are starting a new project where we do not have
requirements.txt and requirements-dev.txt and whose dependencies are not yet on
thirdparty.aboutcode.org/pypi, we run the following command after adding and
customizing the skeleton files to your project:

.. code-block:: bash

    ./configure --init

This will initialize the virtual environment for the project, pull in the
dependencies from PyPI and add them to the virtual environment.

Generating requirements.txt and requirements-dev.txt
----------------------------------------------------

After the project has been initialized, we can generate the requirements.txt and
requirements-dev.txt files.

Ensure the virtual environment is enabled.

To generate requirements.txt:

.. code-block:: bash

    python etc/scripts/gen_requirements.py -s venv/lib/python<version>/site-packages/

Replace \<version\> with the version number of the Python being used, for example: ``venv/lib/python3.6/site-packages/``

To generate requirements-dev.txt after requirements.txt has been generated:

.. code-block:: bash
    ./configure --init --dev
    source venv/bin/activate
    python etc/scripts/gen_requirements_dev.py -s venv/lib/python<version>/site-packages/

Collecting and generating ABOUT files for dependencies
------------------------------------------------------

Once we have requirements.txt and requirements-dev.txt, we can fetch the project
dependencies as wheels and generate ABOUT files for them:

.. code-block:: bash

    python etc/scripts/bootstrap.py -r requirements.txt -r requirements-dev.txt --with-deps

There may be issues with the generated ABOUT files, which will have to be
corrected. You can check to see if your corrections are valid by running:

.. code-block:: bash

    python etc/scripts/check_thirdparty.py -d thirdparty

Once the wheels are collected and the ABOUT files are generated and correct,
upload them to thirdparty.aboutcode.org/pypi by placing the wheels and ABOUT
files from the thirdparty directory to the pypi directory at
https://github.com/nexB/thirdparty-packages


Release Notes
-------------

- 2021-05-11: adopt new configure scripts from ScanCode TK that allows correct
  configuration of which Python version is used.
