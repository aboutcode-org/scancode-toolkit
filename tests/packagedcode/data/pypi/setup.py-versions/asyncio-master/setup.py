# Release procedure:
#  - run tox (to run runtests.py and run_aiotest.py)
#  - maybe test examples
#  - update version in setup.py
#  - hg ci
#  - hg tag VERSION
#  - hg push
#  - run on Linux: python setup.py register sdist upload
#  - run on Windows: python release.py VERSION
#  - increment version in setup.py
#  - hg ci && hg push

import os
import sys
try:
    from setuptools import setup, Extension
except ImportError:
    # Use distutils.core as a fallback.
    # We won't be able to build the Wheel file on Windows.
    from distutils.core import setup, Extension

if sys.version_info < (3, 3, 0):
    raise RuntimeError("asyncio requires Python 3.3.0+")

extensions = []
if os.name == 'nt':
    ext = Extension(
        'asyncio._overlapped', ['overlapped.c'], libraries=['ws2_32'],
    )
    extensions.append(ext)

with open("README.rst") as fp:
    long_description = fp.read()

setup(
    name="asyncio",
    version="3.4.4",

    description="reference implementation of PEP 3156",
    long_description=long_description,
    url="http://www.python.org/dev/peps/pep-3156/",

    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
    ],

    packages=["asyncio"],
    test_suite="runtests.runtests",

    ext_modules=extensions,
)
