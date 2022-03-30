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
- set project info and dependencies in setup.cfg
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

    ./configure

This will initialize the virtual environment for the project, pull in the
dependencies from PyPI and add them to the virtual environment.


Generating requirements.txt and requirements-dev.txt
----------------------------------------------------

After the project has been initialized, we can generate the requirements.txt and
requirements-dev.txt files.

Ensure the virtual environment is enabled.

.. code-block:: bash

    source venv/bin/activate

To generate requirements.txt:

.. code-block:: bash

    python etc/scripts/gen_requirements.py -s venv/lib/python<version>/site-packages/

Replace \<version\> with the version number of the Python being used, for example:
``venv/lib/python3.6/site-packages/``

To generate requirements-dev.txt after requirements.txt has been generated:

.. code-block:: bash

    ./configure --dev
    python etc/scripts/gen_requirements_dev.py -s venv/lib/python<version>/site-packages/

Note: on Windows, the ``site-packages`` directory is located at ``venv\Lib\site-packages\``

.. code-block:: bash

    python .\\etc\\scripts\\gen_requirements.py -s .\\venv\\Lib\\site-packages\\
    .\configure --dev
    python .\\etc\\scripts\\gen_requirements_dev.py -s .\\venv\\Lib\\site-packages\\


Collecting and generating ABOUT files for dependencies
------------------------------------------------------

Ensure that the dependencies used by ``etc/scripts/fetch_thirdparty.py`` are installed:

.. code-block:: bash

    pip install -r etc/scripts/requirements.txt

Once we have requirements.txt and requirements-dev.txt, we can fetch the project
dependencies as wheels and generate ABOUT files for them:

.. code-block:: bash

    python etc/scripts/fetch_thirdparty.py -r requirements.txt -r requirements-dev.txt

There may be issues with the generated ABOUT files, which will have to be
corrected. You can check to see if your corrections are valid by running:

.. code-block:: bash

    python etc/scripts/check_thirdparty.py -d thirdparty

Once the wheels are collected and the ABOUT files are generated and correct,
upload them to thirdparty.aboutcode.org/pypi by placing the wheels and ABOUT
files from the thirdparty directory to the pypi directory at
https://github.com/nexB/thirdparty-packages


Usage after project initialization
----------------------------------

Once the ``requirements.txt`` and ``requirements-dev.txt`` have been generated
and the project dependencies and their ABOUT files have been uploaded to
thirdparty.aboutcode.org/pypi, you can configure the project as needed, typically
when you update dependencies or use a new checkout.

If the virtual env for the project becomes polluted, or you would like to remove
it, use the ``--clean`` option:

.. code-block:: bash

    ./configure --clean

Then you can run ``./configure`` again to set up the project virtual environment.

To set up the project for development use:

.. code-block:: bash

    ./configure --dev

To update the project dependencies (adding, removing, updating packages, etc.),
update the dependencies in ``setup.cfg``, then run:

.. code-block:: bash

    ./configure --clean # Remove existing virtual environment
    source venv/bin/activate # Ensure virtual environment is activated
    python etc/scripts/gen_requirements.py -s venv/lib/python<version>/site-packages/ # Regenerate requirements.txt
    python etc/scripts/gen_requirements_dev.py -s venv/lib/python<version>/site-packages/ # Regenerate requirements-dev.txt
    pip install -r etc/scripts/requirements.txt # Install dependencies needed by etc/scripts/bootstrap.py
    python etc/scripts/fetch_thirdparty.py -r requirements.txt -r requirements-dev.txt # Collect dependency wheels and their ABOUT files

Ensure that the generated ABOUT files are valid, then take the dependency wheels
and ABOUT files and upload them to thirdparty.aboutcode.org/pypi.
