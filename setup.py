#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import, print_function

import io
import os
import re
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import find_packages
from setuptools import setup


def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()


long_description = '%s\n%s' % (
    read('README.rst'), 
    re.sub(':obj:`~?(.*?)`', r'``\1``', read('CHANGELOG.rst'))
)

setup(
    name='scancode-toolkit',
    version='1.5.0',
    license='Apache-2.0 with ScanCode acknowledgment and CC0-1.0 and others',
    description='ScanCode is a tool to scan code for license, copyright and other interesting facts.',
    long_description=long_description,
    author='ScanCode',
    author_email='info@scancode.io',
    url='https://github.com/nexB/scancode-toolkit',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'License :: OSI Approved :: CC0',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
    ],
    keywords=[
        'license', 'filetype', 'urn', 'date', 'codec',
    ],
    install_requires=[
        # cluecode
        'py2-ipaddress >= 2.0, <3.0',
        'url >= 0.1.4',
        'publicsuffix2',
        # TODO: upgrade to nltk==3.0.1
        'nltk >= 2.0b4, <3.0.0',

        # extractcode
        'patch >= 1.14.2, < 1.15 ',
        # to work around bug http://bugs.python.org/issue19839
        # on multistream bzip2 files
        'bz2file >= 0.98',

        # licensedcode
        'PyYAML >= 3.0, <4.0',

        # textcode
        'Beautifulsoup >= 3.2.0, <4.0.0',
        'Beautifulsoup4 >= 4.3.0, <5.0.0',
        'html5lib',
        'six',

        # typecode and textcode
        'pygments >= 2.0.0, <3.0.0',
        'pdfminer >= 20140328',

        # typecode
        'chardet >= 2.1.1, <3.0.0',
        'binaryornot >= 0.4.0',

        # scancode and AboutCode
        'click >= 4.0.0, < 5.0.0',
        'jinja2 >= 2.7.0, < 3.0.0',
        'MarkupSafe >= 0.23',
        'colorama',

        # AboutCode
        'about-code-tool >= 0.9.0',

        # packagedcode
        'requests >= 2.7.0, < 3.0.0',
    ],

    extras_require={
        'base': [
            'certifi',
            'setuptools',
            'wheel',
            'pip',
            'wincertstore',
        ],
        'dev': [
            'pytest',
            'execnet',
            'py',
            'pytest-xdist',
            'bumpversion',
        ],

    },
    entry_points={
        'console_scripts': [
            'scancode = scancode.cli:scancode',
            'extractcode = scancode.extract_cli:extractcode',
        ],
    },
)
