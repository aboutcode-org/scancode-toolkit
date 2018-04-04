#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function

import io
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext
import re
import sys

from setuptools import find_packages
from setuptools import setup


version = '2.9.1'


#### Small hack to force using a plain version number if the option
#### --plain-version is passed to setup.py

USE_DEFAULT_VERSION = False
try:
    sys.argv.remove('--use-default-version')
    USE_DEFAULT_VERSION = True
except ValueError:
    pass
####

def get_version(default=version, template='{tag}.{distance}.{commit}{dirty}',
                use_default=USE_DEFAULT_VERSION):
    """
    Return a version collected from git if possible or fall back to an
    hard-coded default version otherwise. If `use_default` is True,
    always use the default version.
    """
    if use_default:
        return default
    try:
        tag, distance, commit, dirty = get_git_version()
        if not distance and not dirty:
            # we are from a clean Git tag: use tag
            return tag

        distance = 'post{}'.format(distance)
        if dirty:
            time_stamp = get_time_stamp()
            dirty = '.dirty.' + get_time_stamp()
        else:
            dirty = ''

        return template.format(**locals())
    except:
        # no git data: use default version
        return default


def get_time_stamp():
    """
    Return a numeric UTC time stamp without microseconds.
    """
    from datetime import datetime
    return (datetime.isoformat(datetime.utcnow()).split('.')[0]
            .replace('T', '').replace(':', '').replace('-', ''))


def get_git_version():
    """
    Return version parts from Git or raise an exception.
    """
    from subprocess import check_output, STDOUT
    # this may fail with exceptions
    cmd = 'git', 'describe', '--tags', '--long', '--dirty',
    version = check_output(cmd, stderr=STDOUT).strip()
    dirty = version.endswith('-dirty')
    tag, distance, commit = version.split('-')[:3]
    # lower tag and strip V prefix in tags
    tag = tag.lower().lstrip('v ').strip()
    # strip leading g from git describe commit
    commit = commit.lstrip('g').strip()
    return tag, int(distance), commit, dirty


def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()


setup(
    name='scancode-toolkit',
    version=get_version(),
    license='Apache-2.0 with ScanCode acknowledgment and CC0-1.0 and others',
    description=
        'ScanCode is a tool to scan code for license, copyright, package '
        'and their documented dependencies and other interesting facts.',
    long_description=read('README.rst'),
    author='ScanCode',
    author_email='info@aboutcode.org',
    url='https://github.com/nexB/scancode-toolkit',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
    ],
    keywords=[
        'open source', 'scan', 'license', 'package', 'dependency',
        'copyright', 'filetype', 'author', 'extract', 'licensing',
    ],
    install_requires=[
        # cluecode
        # Some nltk version ranges are buggy
        'nltk >= 3.2, < 4.0',
        'publicsuffix2',
        'py2-ipaddress >= 2.0, <3.0',
        'url >= 0.1.4',
        'fingerprints >= 0.5.4',

        # extractcode
        'patch >= 1.15, < 1.20 ',
        # to work around bug http://bugs.python.org/issue19839
        # on multistream bzip2 files: this can removed in Python 3.
        'bz2file >= 0.98',

        # commoncode
        'backports.os == 0.1.1',
        'future >= 0.16.0, < 0.17.0',
        'text-unidecode >= 1.0, < 2.0',

        # licensedcode
        'bitarray >= 0.8.1, < 1.0.0',
        'intbitset >= 2.3.0,  < 3.0',
        'pyahocorasick >= 1.1, < 1.2',
        'PyYAML >= 3.0, <4.0',

        # textcode
        'Beautifulsoup >= 3.2.0, <4.0.0',
        'Beautifulsoup4 >= 4.3.0, <5.0.0',
        'html5lib',
        'six',
        'pdfminer.six >= 20170720',
        'pycryptodome >= 3.4',

        # typecode
        'binaryornot >= 0.4.0',
        'chardet >= 3.0.0, <4.0.0',
        'pygments >= 2.0.1, <3.0.0',

        # packagedcode
        'pymaven-patch >= 0.2.4',
        'requests >= 2.7.0, < 3.0.0',
        'schematics_patched',

        # scancode
        'click >= 6.0.0, < 7.0.0',
        'colorama >= 0.3.9',
        'pluggy >= 0.4.0, < 1.0',
        'attrs >=17.0, < 18.0',
        'typing >=3.6, < 3.7',

        # scancode outputs
        'jinja2 >= 2.7.0, < 3.0.0',
        'MarkupSafe >= 0.23',
        'simplejson',
        'spdx-tools >= 0.5.4',
        'unicodecsv',

        # ScanCode caching and locking
        'psutil >= 5.0.0, < 6.0.0',
        'yg.lockfile >= 2.0.1, < 3.0.0',
            # used by yg.lockfile
            'contextlib2', 'pytz', 'tempora', 'jaraco.timing',
        'zc.lockfile >= 1.0.0, < 2.0.1',


    ],
    extras_require={
        ':platform_system == "Windows"': ['lxml == 3.6.0'],
        ':platform_system == "Linux"': ['lxml == 3.6.4'],
        ':platform_system == "Darwin"': ['lxml == 3.6.4'],

    },
    entry_points={
        'console_scripts': [
            'scancode = scancode.cli:scancode',
            'extractcode = scancode.extract_cli:extractcode',
        ],

        # scancode_pre_scan is the entry point for pre_scan plugins executed
        # before the scans.
        #
        # Each entry hast this form:
        #   plugin-name = fully.qualified.module:PluginClass
        # where plugin-name must be a unique name for this entrypoint.
        #
        # See also plugincode.pre_scan module for details and doc.
        'scancode_pre_scan': [
            'ignore = scancode.plugin_ignore:ProcessIgnore',
        ],

        # scancode_scan is the entry point for scan plugins that run a scan
        # after the pre_scan plugins and before the post_scan plugins.
        #
        # Each entry has this form:
        #   plugin-name = fully.qualified.module:PluginClass
        # where plugin-name must be a unique name for this entrypoint.
        #
        # IMPORTANT: The plugin-name is also the "scan key" used in scan results
        # for this scanner.
        #
        # See also plugincode.scan module for details and doc.
        'scancode_scan': [
            'info = scancode.plugin_info:InfoScanner',
            'licenses = scancode.plugin_license:LicenseScanner',
            'copyrights = scancode.plugin_copyright:CopyrightScanner',
            'packages = scancode.plugin_package:PackageScanner',
            'emails = scancode.plugin_email:EmailScanner',
            'urls = scancode.plugin_url:UrlScanner',
        ],

        # scancode_post_scan is the entry point for post_scan plugins executed
        # after the scan plugins and before the output plugins.
        #
        # Each entry hast this form:
        #   plugin-name = fully.qualified.module:PluginClass
        # where plugin-name must be a unique name for this entrypoint.
        #
        # See also plugincode.post_scan module for details and doc.
        'scancode_post_scan': [
            'mark-source = scancode.plugin_mark_source:MarkSource',
            'copyrights-summary = scancode.plugin_copyrights_summary:CopyrightSummary',
            'license-policy = scancode.plugin_license_policy:LicensePolicy',
        ],

        # scancode_output_filter is the entry point for filter plugins executed
        # after the post-scan plugins and used by the output plugins to
        # exclude/filter certain files or directories from the codebase.
        #
        # Each entry hast this form:
        #   plugin-name = fully.qualified.module:PluginClass
        # where plugin-name must be a unique name for this entrypoint.
        #
        # See also plugincode.post_scan module for details and doc.
        'scancode_output_filter': [
            'only-findings = scancode.plugin_only_findings:OnlyFindings',
            'ignore-copyrights = scancode.plugin_ignore_copyrights:IgnoreCopyrights',
        ],

        # scancode_output is the entry point for output plugins that write a scan
        # output in a given format at the end of a scan.
        #
        # Each entry hast this form:
        #   plugin-name = fully.qualified.module:PluginClass
        # where plugin-name must be a unique name for this entrypoint.
        #
        # See also plugincode._output module for details and doc.
        'scancode_output': [
            'html = formattedcode.output_html:HtmlOutput',
            'html-app = formattedcode.output_html:HtmlAppOutput',
            'json = formattedcode.output_json:JsonCompactOutput',
            'json-pp = formattedcode.output_json:JsonPrettyOutput',
            'spdx-tv = formattedcode.output_spdx:SpdxTvOutput',
            'spdx-rdf = formattedcode.output_spdx:SpdxRdfOutput',
            'csv = formattedcode.output_csv:CsvOutput',
            'jsonlines = formattedcode.output_jsonlines:JsonLinesOutput',
            'template = formattedcode.output_html:CustomTemplateOutput',
        ],
    },
)
