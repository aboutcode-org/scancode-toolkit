#!/usr/bin/env python

import os
import sys

from setuptools import setup, find_packages

os.chdir(os.path.dirname(sys.argv[0]) or ".")

setup(
    name="pip2pi",
    version="0.1.1",
    url="https://github.com/wolever/pip2pi",
    author="David Wolever",
    author_email="david@wolever.net",
    description="""
        pip2pi builds a PyPI-compatible package repository from pip
        requirements
    """,
    long_desc=open("README.rst", "U").read(),
    packages=find_packages(),
    scripts=["pip2pi", "pip2tgz", "dir2pi"],
    license="BSD",
    classifiers=[ x.strip() for x in """
        Development Status :: 4 - Beta
        Environment :: Console
        Intended Audience :: Developers
        Intended Audience :: System Administrators
        License :: OSI Approved :: BSD License
        Natural Language :: English
        Operating System :: OS Independent
        Programming Language :: Python
        Topic :: Software Development
        Topic :: Utilities
    """.split() if x.strip() ],
)
