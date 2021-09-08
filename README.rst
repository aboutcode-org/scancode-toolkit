A Simple Python Project Skeleton
================================
This repo attempts to standardize our python repositories using modern python
packaging and configuration techniques. Using this `blog post`_ as inspiration, this
repository will serve as the base for all new python projects and will be adopted to all
our existing ones as well.

.. _blog post: https://blog.jaraco.com/a-project-skeleton-for-python-projects/

Usage
=====
Usage instructions can be found in ``docs/skeleton-usage.rst``.

Release Notes
=============

- 2021-09-03:
    - ``configure`` now requires pinned dependencies via the use of ``requirements.txt`` and ``requirements-dev.txt``
    - ``configure`` can now accept multiple options at once
    - Add utility scripts from scancode-toolkit/etc/release/ for use in generating project files
    - Rename virtual environment directory from ``tmp`` to ``venv``
    - Update README.rst with instructions for generating ``requirements.txt`` and ``requirements-dev.txt``,
      as well as collecting dependencies as wheels and generating ABOUT files for them.

- 2021-05-11:
    - Adopt new configure scripts from ScanCode TK that allows correct configuration of which Python version is used.
