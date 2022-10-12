#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from glob import glob
from os.path import basename
from os.path import splitext

from setuptools import find_packages
from setuptools import setup


desc = '''A ScanCode path provider plugin to provide a set of example external licenses that can be installed.'''

setup(
    name='licenses_to_install1',
    version='1.0',
    license=(
        'apache-2.0 AND bsd-simplified-darwin AND (bsd-simplified AND public-domain AND '
        'bsd-new AND isc AND (bsd-new OR gpl-1.0-plus) AND bsd-original)'
    ),
    description=desc,
    long_description=desc,
    author='nexB',
    author_email='info@aboutcode.org',
    url='https://github.com/nexB/scancode-plugins',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Utilities',
    ],
    keywords=[
        'open source', 'scancode_licenses',
    ],
    install_requires=[
        'scancode-toolkit',
    ],
    entry_points={
        'scancode_additional_license_location_provider': [
            'licenses_to_install1 = licenses_to_install1:LicensesToInstall1Paths',
        ],
    },
)