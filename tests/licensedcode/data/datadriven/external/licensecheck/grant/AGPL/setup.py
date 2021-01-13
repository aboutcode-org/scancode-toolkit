#!/usr/bin/python -W default
import warnings; warnings.simplefilter('default')

import distutils.sysconfig
import os 
import sys

try:
  from setuptools import setup, Extension
except ImportError:
  from distutils.core import setup, Extension

long_description = """\
Embeds the Python interpreter into PAM \
so PAM modules can be written in Python"""

classifiers = [
  "Development Status :: 4 - Beta",
  "Intended Audience :: Developers",
  "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
  "Natural Language :: English",
  "Operating System :: Unix",
  "Programming Language :: C",
  "Programming Language :: Python",
  "Topic :: Software Development :: Libraries :: Python Modules",
  "Topic :: System :: Systems Administration :: Authentication/Directory"]
