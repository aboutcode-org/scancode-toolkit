# -*- coding: utf-8 -*-
import os
import sys
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.1.1'

long_description = (
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' +
    read('README.rst')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' + 
    read('CHANGES.txt')
    + '\n' +
    'Contributors\n' 
    '************\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    )
install_requires=['setuptools']

extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

setup(name='ntfsutils',
      version=version,
      description="A Python module to manipulate NTFS hard links and junctions.",
      long_description=long_description,
      classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        ],
      keywords='windows ntfs hardlink junction',
      author='Siddharth Agarwal',
      author_email='sid.bugzilla@gmail.com',
      url='https://github.com/sid0/ntfs',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      **extra
      )
