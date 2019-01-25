#!/usr/bin/env python

from __future__ import absolute_import

from setuptools import find_packages
from setuptools import setup


long_desc = '''
This library helps you deal with boolean expressions and algebra with variables
and the boolean functions AND, OR, NOT.

You can parse expressions from strings and simplify and compare expressions.
You can also easily create custom tokenizers to handle custom expressions.  

For extensive documentation look either into the docs directory or view it online, at
https://booleanpy.readthedocs.org/en/latest/

https://github.com/bastikr/boolean.py

Copyright (c) 2009-2016 Sebastian Kraemer, basti.kr@gmail.com and others

Released under revised BSD license.
'''


setup(
    name='boolean.py',
    version='1.2',
    license='revised BSD license',
    description='Boolean Algreba',
    long_description=long_desc,
    author='Sebastian Kraemer',
    author_email='basti.kr@gmail.com',
    url='https://github.com/bastikr/boolean.py',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_loader='unittest:TestLoader',
    test_suite='boolean.test_boolean',
    keywords='boolean expression, boolean algebra, logic, expression parser',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Software Development :: Compilers',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
    ],
)
