#!/usr/bin/env python

import os
import sys

from setuptools import setup, find_packages

os.chdir(os.path.dirname(sys.argv[0]) or ".")

setup(
    name="pip2pi",
    version="0.1",
    url="https://github.com/wolever/pip2pi",
    author="David Wolever",
    author_email="david@wolever.net",
    description="pip2pi builds a PyPI-compatible package repository from pip requirements",
    packages=find_packages(),
    scripts=["pip2pi", "pip2tgz", "dir2pi"],
)
