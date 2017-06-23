#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function

import io
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext
import re
import sys

from setuptools import find_packages
from setuptools import setup


version = '2.0.1'


#### Small hack to force using a plain version number if the option
#### --plain-version is passed to setup.py

USE_DEFAULT_VERSION = False
try:
    sys.argv.remove('--use-default-version')
    USE_DEFAULT_VERSION = True
except ValueError:
    pass
####

def get_version(default=version, template='{tag}.{distance}.{commit}{dirty}',
                use_default=USE_DEFAULT_VERSION):
    """
    Return a version collected from git if possible or fall back to an
    hard-coded default version otherwise. If `use_default` is True,
    always use the default version.
    """
    if use_default:
        return default
    try:
        tag, distance, commit, dirty = get_git_version()
        if not distance and not dirty:
            # we are from a clean Git tag: use tag
            return tag

        distance = 'post{}'.format(distance)
        if dirty:
            time_stamp = get_time_stamp()
            dirty = '.dirty.' + get_time_stamp()
        else:
            dirty = ''

        return template.format(**locals())
    except:
        # no git data: use default version
        return default


def get_time_stamp():
    """
    Return a numeric UTC time stamp without microseconds.
    """
    from datetime import datetime
    return (datetime.isoformat(datetime.utcnow()).split('.')[0]
            .replace('T', '').replace(':', '').replace('-', ''))


def get_git_version():
    """
    Return version parts from Git or raise an exception.
    """
    from subprocess import check_output, STDOUT
    # this may fail with exceptions
    cmd = 'git', 'describe', '--tags', '--long', '--dirty',
    version = check_output(cmd, stderr=STDOUT).strip()
    dirty = version.endswith('-dirty')
    tag, distance, commit = version.split('-')[:3]
    # lower tag and strip V prefix in tags
    tag = tag.lower().lstrip('v ').strip()
    # strip leading g from git describe commit
    commit = commit.lstrip('g').strip()
    return tag, int(distance), commit, dirty


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
    version=get_version(),
    license='Apache-2.0 with ScanCode acknowledgment and CC0-1.0 and others',
    description='ScanCode is a tool to scan code for license, copyright and other interesting facts.',
    long_description=long_description,
    author='ScanCode',
    author_email='info@aboutcode.org',
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
        'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
    ],
    keywords=[
        'open source', 'scan', 'license', 'package',
        'copyright', 'filetype', 'urn', 'date', 'codec',
    ],
    install_requires=[
        # cluecode
        'py2-ipaddress >= 2.0, <3.0',
        'url >= 0.1.4',
        'publicsuffix2',
        # Some lntk version ranges were buggy
        'nltk >= 3.2, < 4.0',

        # extractcode
        'patch >= 1.15, < 1.20 ',
        # to work around bug http://bugs.python.org/issue19839
        # on multistream bzip2 files: this can removed in Python 3.
        'bz2file >= 0.98',
        'text-unidecode >= 1.0, < 2.0',

        # licensedcode
        'PyYAML >= 3.0, <4.0',
        'bitarray >= 0.8.1, < 1.0.0',
        'intbitset >= 2.3.0,  < 3.0',
        'pyahocorasick >= 1.1, < 1.2',
        'attrs >=16.0, < 17.0',

        # caching
        'zc.lockfile >= 1.0.0, < 2.0.1',
        'yg.lockfile >= 2.0.1, < 3.0.0',
            # used by yg.lockfile
            'contextlib2', 'pytz', 'tempora', 'jaraco.timing',
        'psutil >= 5.0.0, < 6.0.0',

        # textcode
        'Beautifulsoup >= 3.2.0, <4.0.0',
        'Beautifulsoup4 >= 4.3.0, <5.0.0',
        'html5lib',
        'six',

        # typecode and textcode
        'pygments >= 2.0.1, <3.0.0',
        'pdfminer >= 20140328',

        # pymaven
        'pymaven-patch >= 0.2.4',

        # typecode
        'chardet >= 3.0.0, <4.0.0',
        'binaryornot >= 0.4.0',

        # scancode and AboutCode
        'click >= 6.0.0, < 7.0.0',
        'jinja2 >= 2.7.0, < 3.0.0',
        'MarkupSafe >= 0.23',
        'colorama',
        'simplejson',
        'spdx-tools >= 0.5.1',

        # packagedcode
        'requests >= 2.7.0, < 3.0.0',
        'schematics_patched',

        # misc
        'unicodecsv',
    ],
    extras_require={
        ':platform_system == "Windows"': ['lxml == 3.6.0'],
        ':platform_system == "Linux"': ['lxml == 3.6.4'],
        ':platform_system == "Darwin"': ['lxml == 3.6.4'],

    },
    entry_points={
        'console_scripts': [
            'scancode = scancode.cli:scancode',
            'extractcode = scancode.extract_cli:extractcode',
        ],
    },
)
