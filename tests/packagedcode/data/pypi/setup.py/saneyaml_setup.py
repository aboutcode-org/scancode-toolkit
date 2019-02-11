#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function

from glob import glob
import io
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import find_packages
from setuptools import setup


setup(
    name='saneyaml',
    version='0.2dev',
    license='Apache-2.0',
    description='Dump readable YAML and load safely any YAML preserving '
        'ordering and avoiding surprises of type conversions. '
        'This library is a PyYaml wrapper with sane behaviour to read and '
        'write readable YAML safely, typically when used for configuration.',
    long_description='',
    author='AboutCode authors and others.',
    author_email='info@nexb.com',
    url='http://aboutcode.org',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
        'Topic :: Utilities',
    ],
    keywords=[
        'yaml', 'block', 'flow', 'readable',
    ],
    install_requires=[
        'PyYAML >= 3.11, <= 3.13',
    ],
)
