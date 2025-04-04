A Simple Python Project Skeleton
================================

This repo attempts to standardize the structure of the Python-based project's
repositories using modern Python packaging and configuration techniques.
Using this `blog post`_ as inspiration, this repository serves as the base for
all new Python projects and is mergeable in existing repositories as well.

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

More usage instructions can be found in ``docs/skeleton-usage.rst``.


Release Notes
=============

- 2025-03-31:

    - Use ruff as the main code formatting tool, add ruff rules to pyproject.toml

- 2025-03-29:

    - Add support for beta macOS-15
    - Add support for beta windows-2025

- 2025-02-14:

    - Drop support for Python 3.8, add support in CI for Python 3.13, use Python 3.12 as default
      version.

- 2025-01-17:

    - Drop support for macOS-12, add support for macOS-14
    - Add support in CI for ubuntu-24.04
    - Add support in CI for Python 3.12

- 2024-08-20:

    - Update references of ownership from nexB to aboutcode-org

- 2024-07-01:

    - Drop support for Python 3.8
    - Drop support for macOS-11, add support for macOS-14

- 2024-02-19:

    - Replace support in CI of default ubuntu-20.04 by ubuntu-22.04

- 2023-10-18:

    - Add dark mode support in documentation

- 2023-07-18:

    - Add macOS-13 job in azure-pipelines.yml

- 2022-03-04:

    - Synchronize configure and configure.bat scripts for sanity
    - Update CI operating system support with latest Azure OS images
    - Streamline utility scripts in etc/scripts/ to create, fetch and manage third-party
      dependencies. There are now fewer scripts. See etc/scripts/README.rst for details

- 2021-09-03:
    - ``configure`` now requires pinned dependencies via the use of ``requirements.txt``
      and ``requirements-dev.txt``
    - ``configure`` can now accept multiple options at once
    - Add utility scripts from scancode-toolkit/etc/release/ for use in generating project files
    - Rename virtual environment directory from ``tmp`` to ``venv``
    - Update README.rst with instructions for generating ``requirements.txt``
      and ``requirements-dev.txt``, as well as collecting dependencies as wheels and generating
      ABOUT files for them.

- 2021-05-11:
    - Adopt new configure scripts from ScanCode TK that allows correct configuration of which
      Python version is used.
