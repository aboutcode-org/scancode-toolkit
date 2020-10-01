#!/usr/bin/env python
# coding: utf-8

from setuptools import setup

with open('README.md', 'r') as fin:
    long_description = fin.read()

setup(
    name='pytoml',
    version='0.1.21',

    description='A parser for TOML-0.4.0',
    long_description=long_description,
    long_description_content_type='text/markdown',

    author='Martin Vejnár',
    author_email='vejnar.martin@gmail.com',
    url='https://github.com/avakar/pytoml',
    license='MIT',
    packages=['pytoml'],
    classifiers=[
        # Supported python versions
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',

        # License
        'License :: OSI Approved :: MIT License',

        # Topics
        'Topic :: Software Development :: Libraries',
    ]
)
