#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function

from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext
import re
import sys

from setuptools import find_packages
from setuptools import setup

version = '20.10.27'


def read(*names, **kwargs):
    import os
    return open(
        os.path.join(os.path.dirname(__file__), *names),
        # encoding=kwargs.get('encoding', 'utf8')
    ).read()


setup(
    name='scancode-toolkit',
    version=version,
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
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Utilities',
    ],
    keywords=[
        'open source', 'scan', 'license', 'package', 'dependency',
        'copyright', 'filetype', 'author', 'extract', 'licensing',
    ],
    python_requires='>=3.6.*, <4',
    install_requires=[

        # cluecode
        # Some nltk version ranges are buggy
        'nltk >= 3.2, < 4.0',
        'urlpy',
        'publicsuffix2',
        'fingerprints >= 0.6.0, < 1.0.0',

        # commoncode
        'commoncode >= 20.09',

        'future >= 0.16.0',
        'saneyaml',

        # plugincode
        'plugincode',

        # licensedcode
        'bitarray >= 0.8.1, < 1.0.0',
        'intbitset >= 2.3.0,  < 3.0',
        'boolean.py >= 3.5,  < 4.0',
        'license_expression >= 0.99',
        'pyahocorasick >= 1.4, < 1.5',

        # multiple
        'lxml >= 4.0.0, < 5.0.0',

        # textcode
        'Beautifulsoup4 >= 4.0.0, <5.0.0',
        'html5lib',
        'six',
        'pdfminer.six >= 20170720',
        'pycryptodome >= 3.4',
        'chardet >= 3.0.0, <4.0.0',

        # typecode
        'typecode',

        # packagedcode
        'debut >= 0.9.4',
        'pefile >= 2018.8.8',
        'pymaven_patch >= 0.2.8',
        'requests >= 2.7.0, < 3.0.0',
        'packageurl_python >= 0.7.0',
        'xmltodict >= 0.11.0',
        'javaproperties >= 0.5',
        'toml >= 0.10.0',
        'gemfileparser >= 0.7.0',
        'pkginfo >= 1.5.0.1',
        'dparse2',
        'pygments >= 2.4.2, <2.5.1',

        # used to fix mojibake in Windows PE
        # for now we use the evrsion that works on both Python 2 and 3
        'ftfy <  5.0.0',

        # scancode
        # Click 7.0 is broken https://github.com/pallets/click/issues/1125
        'click >= 6.7, !=7.0',
        'colorama >= 0.3.9',
        'pluggy >= 0.4.0, < 1.0',
        'attrs >= 18.1, !=20.1.0',
        'typing >=3.6, < 3.7',

        # scancode outputs
        'jinja2 >= 2.7.0, < 3.0.0',
        'MarkupSafe >= 0.23',
        'simplejson',
        'spdx_tools >= 0.6.0',
        'unicodecsv',

        # ScanCode caching and locking
        'yg.lockfile >= 2.3, < 3.0.0',
        # used by yg.lockfile
        'contextlib2',
        'pytz',
        'tempora',
        'jaraco.functools',
        'zc.lockfile >= 2.0.0, < 3.0.0',
    ],

    extras_require={
        'full': [
            'extractcode',
            'extractcode_7z',
            'extractcode_libarchive',
            'typecode_libmagic',
        ],
    },

    entry_points={
        'console_scripts': [
            'scancode = scancode.cli:scancode',
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
            'facet = summarycode.facet:AddFacet',
            'classify = summarycode.classify:FileClassifier',
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
            'licenses = licensedcode.plugin_license:LicenseScanner',
            'copyrights = cluecode.plugin_copyright:CopyrightScanner',
            'packages = packagedcode.plugin_package:PackageScanner',
            'emails = cluecode.plugin_email:EmailScanner',
            'urls = cluecode.plugin_url:UrlScanner',
            'generated = summarycode.generated:GeneratedCodeDetector',
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
            'summary = summarycode.summarizer:ScanSummary',
            'summary-keeping-details = summarycode.summarizer:ScanSummaryWithDetails',
            'summary-key-files = summarycode.summarizer:ScanKeyFilesSummary',
            'summary-by-facet = summarycode.summarizer:ScanByFacetSummary',
            'license-clarity-score = summarycode.score:LicenseClarityScore',
            'license-policy = licensedcode.plugin_license_policy:LicensePolicy',
            'mark-source = scancode.plugin_mark_source:MarkSource',
            'classify-package = summarycode.classify:PackageTopAndKeyFilesTagger',
            'is-license-text = licensedcode.plugin_license_text:IsLicenseText',
            'filter-clues = cluecode.plugin_filter_clues:RedundantCluesFilter',
            'consolidate = summarycode.plugin_consolidate:Consolidator',
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
            'ignore-copyrights = cluecode.plugin_ignore_copyrights:IgnoreCopyrights',
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
