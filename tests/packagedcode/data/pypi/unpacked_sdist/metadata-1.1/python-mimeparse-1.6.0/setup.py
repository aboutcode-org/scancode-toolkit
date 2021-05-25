#!/usr/bin/env python

import codecs
import os
import re
from setuptools import setup


def get_version(filename):
    """
    Return package version as listed in `__version__` in 'filename'.
    """
    with open(filename) as fp:
        contents = fp.read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", contents).group(1)

version = get_version('mimeparse.py')
if not version:
    raise RuntimeError('Cannot find version information')


def read(fname):
    path = os.path.join(os.path.dirname(__file__), fname)
    with codecs.open(path, encoding='utf-8') as fp:
        return fp.read()


setup(
    name="python-mimeparse",
    py_modules=["mimeparse"],
    version=version,
    description=("A module provides basic functions for parsing mime-type "
                 "names and matching them against a list of media-ranges."),
    author="DB Tsai",
    author_email="dbtsai@dbtsai.com",
    url="https://github.com/dbtsai/python-mimeparse",
    download_url=("https://github.com/dbtsai/python-mimeparse/tarball/" +
                  version),
    keywords=["mime-type"],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    long_description=read('README.rst')
)
