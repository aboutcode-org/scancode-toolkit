#!/usr/bin/env python3

import subprocess
from os import path

from setuptools import Extension, setup


here = path.abspath(path.dirname(__file__))


def pkgconfig(package):
    result = {}
    for token in subprocess.check_output(['pkg-config', '--libs', '--cflags', package]).decode('utf-8').split():
        if token.startswith('-I'):
            result.setdefault('include_dirs', []).append(token[2:])
        elif token.startswith('-L'):
            result.setdefault('library_dirs', []).append(token[2:])
        elif token.startswith('-l'):
            result.setdefault('libraries', []).append(token[2:])
    return result


def get_version():
    with open(path.join(here, 'libversion', '__init__.py')) as source:
        for line in source:
            if line.startswith('__version__'):
                return line.strip().split(' = ')[-1].strip('\'')

    raise RuntimeError('Cannot determine package version from package source')


def get_long_description():
    try:
        return open(path.join(here, 'README.rst')).read()
    except:
        return None


setup(
    name='libversion',
    version=get_version(),
    description='Python bindings for libversion',
    long_description=get_long_description(),
    author='Dmitry Marakasov',
    author_email='amdmi3@amdmi3.ru',
    url='https://github.com/repology/py-libversion',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: C',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Version Control',
        'Topic :: System :: Archiving :: Packaging',
        'Topic :: System :: Software Distribution',
    ],
    packages=['libversion'],
    ext_modules=[
        Extension(
            'libversion._libversion',
            sources=['src/_libversion.c'],
            **pkgconfig('libversion')
        )
    ],
    test_suite='tests'
)
