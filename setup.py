#!/usr/bin/env python

import os
import sys

from setuptools import setup, find_packages

os.chdir(os.path.dirname(sys.argv[0]) or ".")

try:
    long_description = open("README.rst", "U").read()
except IOError:
    long_description = "See https://github.com/wolever/pip2pi"

import libpip2pi
version = "%s.%s.%s" %libpip2pi.__version__

setup(
    name="pip2pi",
    version=version,
    url="https://github.com/wolever/pip2pi",
    author="David Wolever",
    author_email="david@wolever.net",
    description="""
        pip2pi builds a PyPI-compatible package repository from pip
        requirements
    """,
    long_description=long_description,
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
    """.split("\n") if x.strip() ],
)
