#!/usr/bin/env python3
# vim:fileencoding=utf-8

from setuptools import setup, find_packages
import nvchecker

setup(
  name = 'nvchecker',
  version = nvchecker.__version__,
  author = 'lilydjwg',
  author_email = 'lilydjwg@gmail.com',
  description = 'New version checker for software',
  license = 'MIT',
  keywords = 'new version build check',
  url = 'https://github.com/lilydjwg/nvchecker',
  long_description = open('README.rst', encoding='utf-8').read(),
  platforms = 'any',
  zip_safe = True,

  packages = find_packages(exclude=["tests"]),
  install_requires = ['tornado>=4.1', 'setuptools'],
  tests_require = [
    'pytest',
    'flaky',
  ],
  entry_points = {
    'console_scripts': [
      'nvchecker = nvchecker.main:main',
      'nvtake = nvchecker.tools:take',
      'nvcmp = nvchecker.tools:cmp',
    ],
  },
  package_data = {'nvchecker': ['source/vcs.sh']},

  classifiers = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Topic :: Internet",
    "Topic :: Internet :: WWW/HTTP",
    "Topic :: Software Development",
    "Topic :: System :: Archiving :: Packaging",
    "Topic :: System :: Software Distribution",
    "Topic :: Utilities",
  ],
)
