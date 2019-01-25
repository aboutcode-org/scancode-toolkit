#!/usr/bin/env python

# Copyright (c) 2012-2013 SEOmoz, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from setuptools import setup


setup(
    name='urlpy',
    version='0.2.0.2',
    description='URL Parsing',
    long_description='''
Some helper functions for parsing URLs, sanitizing them, normalizing them in pure python.

This includes support for escaping, unescaping, punycoding, unpunycoding,
cleaning parameter and query strings, and a little more sanitization.

This version is a friendly fork of the upstream from Moz to keep a pure Python
version around to run on Python 2.7 and all OSes.
It also uses an alternate publicsuffix list provider package.

''',
    author='Dan Lecocq',
    author_email='dan@seomoz.org',
    url='http://github.com/nexB/url-py',
    py_modules=['urlpy'],
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP'],
    install_requires=[
        'publicsuffix2'
    ],
)
