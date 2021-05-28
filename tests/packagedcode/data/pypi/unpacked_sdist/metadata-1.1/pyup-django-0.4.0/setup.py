#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = [
    'packaging',
    'requests'
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='pyup-django',
    version='0.4.0',
    description="pyup-django checks your installed dependencies for known security vulnerabilities and displays them in the admin area.",
    long_description=readme,
    author="pyup.io",
    author_email='support@pyup.io',
    url='https://github.com/pyupio/pyup-django',
    packages=[
        'pyup_django',
    ],
    package_dir={'pyup_django':
                 'pyup_django'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='pyup_django',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
