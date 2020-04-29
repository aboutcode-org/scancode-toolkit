#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function

from glob import glob
from os.path import basename
from os.path import join
from os.path import splitext

from setuptools import find_packages
from setuptools import setup


desc = '''A ScanCode path provider plugin to provide a prebuilt native libmagic binary and database.'''

setup(
    name='typecode_libmagic',
    version='5.22.4',
    license='bsd-simplified',
    description=desc,
    long_description=desc,
    author='nexB',
    author_email='info@aboutcode.org',
    url='https://github.com/nexB/scancode-toolkit',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ],
    keywords=[
        'open source', 'typecode', 'libmagic'
    ],
    entry_points={
        'scancode_location_provider': [
            'typecode_libmagic = typecode_libmagic:LibmagicPaths',
        ],
    },
)
