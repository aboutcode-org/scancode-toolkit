#!/usr/bin/env python

import os
import sys

from setuptools import setup
from setuptools import find_packages


setup(
    name="pip2pi",
    version="0.9.0",
    url="https://github.com/wolever/pip2pi",
    author="David Wolever",
    author_email="david@wolever.net",
    description="pip2pi builds a PyPI-compatible package repository from pip requirements",
    long_description=open("README.rst").read(),
    maintainer="Md Safiyat Reza",
    maintainer_email="safiyat@voereir.com",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'dir2pi = pip2pi:dir2pi',
            'pip2pi = pip2pi:pip2pi',
            'pip2tgz = pip2pi:pip2tgz',
        ],
    },
    python_requires=">=3.6",
    license="BSD-2-Clause-Views",
    classifiers=[ 
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Topic :: Utilities",
    ],
)
