#!/usr/bin/env python
# $Id: setup.py 8453 2020-01-12 13:28:32Z grubert $
# Copyright: This file has been placed in the public domain.

from __future__ import print_function

import sys
import os
import glob

try:
    import setuptools
except ImportError:
    print('Warning: Could not load package `setuptools`.')
    print('Actions requiring `setuptools` instead of `distutils` will fail')
try:
    from distutils.core import setup, Command
    from distutils.command.build import build
    from distutils.command.build_py import build_py
    from distutils.command.install_data import install_data
    from distutils.util import convert_path
    from distutils import log
except ImportError:
    print('Error: The "distutils" standard module, which is required for the ')
    print('installation of Docutils, could not be found.  You may need to ')
    print('install a package called "python-devel" (or similar) on your ')
    print('system using your package manager.')
    sys.exit(1)


class smart_install_data(install_data):
    # From <http://wiki.python.org/moin/DistutilsInstallDataScattered>,
    # by Pete Shinners.

    def run(self):
        # need to change self.install_dir to the library dir
        install_cmd = self.get_finalized_command('install')
        self.install_dir = getattr(install_cmd, 'install_lib')
        return install_data.run(self)


class build_data(Command):

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        build_py_cmd = self.get_finalized_command('build_py')
        data_files = self.distribution.data_files
        for f in data_files:
            dir = convert_path(f[0])
            dir = os.path.join(build_py_cmd.build_lib, dir)
            self.mkpath(dir)
            for data in f[1]:
                data = convert_path(data)
                self.copy_file(data, dir)


# let our build_data run
build.sub_commands.append(('build_data', lambda *a: True))


s5_theme_files = []
for dir in glob.glob('docutils/writers/s5_html/themes/*'):
    if os.path.isdir(dir):
        theme_files = glob.glob('%s/*' % dir)
        s5_theme_files.append((dir, theme_files))


package_data = {
    'name': 'docutils',
    'description': 'Docutils -- Python Documentation Utilities',
    'long_description': """\
Docutils is a modular system for processing documentation
into useful formats, such as HTML, XML, and LaTeX.  For
input Docutils supports reStructuredText, an easy-to-read,
what-you-see-is-what-you-get plaintext markup syntax.""",  # wrap at col 60
    'url': 'http://docutils.sourceforge.net/',
    'version': '0.16',
    'author': 'David Goodger',
    'author_email': 'goodger@python.org',
    'maintainer': 'docutils-develop list',
    'maintainer_email': 'docutils-develop@lists.sourceforge.net',
    'license': 'public domain, Python, 2-Clause BSD, GPL 3 (see COPYING.txt)',
    'platforms': 'OS-independent',
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
    'cmdclass': {
        'build_data': build_data,
        'install_data': smart_install_data,
    },
    'package_dir': {
        'docutils': 'docutils',
        'docutils.tools': 'tools'
    },
    'packages': [
        'docutils',
        'docutils.languages',
        'docutils.parsers',
        'docutils.parsers.rst',
        'docutils.parsers.rst.directives',
        'docutils.parsers.rst.languages',
        'docutils.readers',
        'docutils.transforms',
        'docutils.utils',
        'docutils.utils.math',
        'docutils.writers',
        'docutils.writers.html4css1',
        'docutils.writers.html5_polyglot',
        'docutils.writers.pep_html',
        'docutils.writers.s5_html',
        'docutils.writers.latex2e',
        'docutils.writers.xetex',
        'docutils.writers.odf_odt',
    ],
    'data_files': [
        ('docutils/parsers/rst/include',
         glob.glob('docutils/parsers/rst/include/*.txt')),
        ('docutils/writers/html5_polyglot', [
            'docutils/writers/html5_polyglot/minimal.css',
            'docutils/writers/html5_polyglot/plain.css',
            'docutils/writers/html5_polyglot/math.css',
            'docutils/writers/html5_polyglot/template.txt']),
        ('docutils/writers/html4css1', [
            'docutils/writers/html4css1/html4css1.css',
            'docutils/writers/html4css1/template.txt']),
        ('docutils/writers/latex2e', [
            'docutils/writers/latex2e/default.tex',
            'docutils/writers/latex2e/titlepage.tex',
            'docutils/writers/latex2e/xelatex.tex']),
        ('docutils/writers/pep_html', [
            'docutils/writers/pep_html/pep.css',
            'docutils/writers/pep_html/template.txt']),
        ('docutils/writers/s5_html/themes', [
            'docutils/writers/s5_html/themes/README.txt']),
        ('docutils/writers/odf_odt', ['docutils/writers/odf_odt/styles.odt']),
    ] + s5_theme_files,
    'scripts': [
        'tools/rst2html.py',
        'tools/rst2html4.py',
        'tools/rst2html5.py',
        'tools/rst2s5.py',
        'tools/rst2latex.py',
        'tools/rst2xetex.py',
        'tools/rst2man.py',
        'tools/rst2xml.py',
        'tools/rst2pseudoxml.py',
        'tools/rstpep2html.py',
        'tools/rst2odt.py',
        'tools/rst2odt_prepstyles.py',
    ],
    'classifiers': [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Other Audience',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: Public Domain',
        'License :: OSI Approved :: Python Software Foundation License',
        'License :: OSI Approved :: BSD License',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Documentation',
        'Topic :: Software Development :: Documentation',
        'Topic :: Text Processing',
        'Natural Language :: English',  # main/default language, keep first
        'Natural Language :: Afrikaans',
        'Natural Language :: Catalan',
        'Natural Language :: Chinese (Simplified)',
        'Natural Language :: Chinese (Traditional)',
        'Natural Language :: Czech',
        'Natural Language :: Danish',
        'Natural Language :: Dutch',
        'Natural Language :: Esperanto',
        'Natural Language :: Finnish',
        'Natural Language :: French',
        'Natural Language :: Galician',
        'Natural Language :: German',
        'Natural Language :: Hebrew',
        'Natural Language :: Italian',
        'Natural Language :: Japanese',
        'Natural Language :: Korean',
        'Natural Language :: Latvian',
        'Natural Language :: Lithuanian',
        'Natural Language :: Persian',
        'Natural Language :: Polish',
        'Natural Language :: Portuguese (Brazilian)',
        'Natural Language :: Russian',
        'Natural Language :: Slovak',
        'Natural Language :: Spanish',
        'Natural Language :: Swedish',
    ],
}
"""Distutils setup parameters."""


def do_setup():
    # Install data files properly.
    dist = setup(**package_data)
    return dist


if __name__ == '__main__':
    do_setup()
