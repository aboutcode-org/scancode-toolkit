#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from setuptools import setup, find_packages

sys.path.insert(0, 'src')
from paho.mqtt import __version__

with open('README.rst', 'rb') as readme_file:
    readme = readme_file.read().decode('utf-8')

requirements = []
test_requirements = ['pytest', 'pylama', 'six']
needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
setup_requirements = ['pytest-runner'] if needs_pytest else []
extra_requirements = {'proxy': ['PySocks']}

if sys.version_info < (3, 0):
    test_requirements += ['mock']

setup(
    name='paho-mqtt',
    version=__version__,
    description='MQTT version 3.1.1 client class',
    long_description=readme,
    author='Roger Light',
    author_email='roger@atchoo.org',
    url='http://eclipse.org/paho',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=requirements,
    license='Eclipse Public License v1.0 / Eclipse Distribution License v1.0',
    zip_safe=False,
    keywords='paho',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Communications',
        'Topic :: Internet',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
    extras_require=extra_requirements
)
