"""
setup.py contains a function named setup.

When writing software that works with python packages it is very
inconvenient to retrieve the package metadata from setup.py. This package
makes it easy, just point it at setup.py and get a dict.

>>> import setupreader, json
>>> foo = setupreader.load('setup.py')
>>> print json.dumps(foo, indent=4)
{
    "description": "retrieve package specification from setup,py", 
    "install_requires": [
        "setuptools", 
        "mock"
    ], 
    "zip_safe": false, 
    "keywords": "", 
    "packages": [], 
    "classifiers": [], 
    "entry_points": {
        "console_scripts": [
            "read-setup = setupreader:main"
        ]
    }, 
    "name": "setupreader", 
    "license": "", 
    "author": "Lars van de Kerkhof", 
    "url": "", 
    "include_package_data": true, 
    "py_modules": [
        "setupreader"
    ], 
    "long_description": "", 
    "author_email": "lars@permanentmarkers.nl", 
    "version": "0.0.1"
}
"""

from setuptools import setup, find_packages

__version__ = "0.0.3"


setup(
    # package name in pypi
    name='setupreader',
    # extract version from module.
    version=__version__,
    description="retrieve package specification from setup.py",
    long_description=__doc__,
    classifiers=[],
    keywords='',
    author='Lars van de Kerkhof',
    author_email='lars@permanentmarkers.nl',
    url='https://github.com/specialunderwear/setupreader',
    license='GPL',
    # include all packages in the egg, except the test package.
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    py_modules=['setupreader'],
    # include non python files
    include_package_data=True,
    zip_safe=False,
    # specify dependencies
    install_requires=[
        'setuptools',
        'mock'
    ],
    # generate scripts
    entry_points={
        'console_scripts':[
            'setupreader = setupreader:main',
        ]
    }
)
