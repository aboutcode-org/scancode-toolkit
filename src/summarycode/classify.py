#
# Copyright (c) 2018 nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/scancode-toolkit/
# The ScanCode software is licensed under the Apache License version 2.0.
# Data generated with ScanCode require an acknowledgment.
# ScanCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# When you publish or redistribute any data created with ScanCode or any ScanCode
# derivative work, you must accompany this data with the following acknowledgment:
#
#  Generated with ScanCode and provided on an "AS IS" BASIS, WITHOUT WARRANTIES
#  OR CONDITIONS OF ANY KIND, either express or implied. No content created from
#  ScanCode should be considered or used as legal advice. Consult an Attorney
#  for any legal advice.
#  ScanCode is a free software code scanning tool from nexB Inc. and others.
#  Visit https://github.com/nexB/scancode-toolkit/ for support and download.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import OrderedDict

from commoncode.datautils import Boolean
from plugincode.pre_scan import PreScanPlugin
from plugincode.pre_scan import pre_scan_impl
from scancode import CommandLineOption
from scancode import PRE_SCAN_GROUP

"""
Tag files as "key" or important and top-level files.
"""

# Tracing flag
TRACE = False


def logger_debug(*args):
    pass


if TRACE:
    import logging
    import sys

    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, unicode) and a or repr(a) for a in args))


@pre_scan_impl
class FileClassifier(PreScanPlugin):
    """
    Classify a file such as a COPYING file or a package manifest with a flag.
    """
    resource_attributes = OrderedDict([
        ('is_legal',
         Boolean(help='True if this file is likely a "legal"-related file such '
                      'as a COPYING or LICENSE file.')),

        ('is_manifest',
         Boolean(help='True if this file is likely a package manifest file such '
                      'as a Maven pom.xml or an npm package.json')),

        ('is_readme',
         Boolean(help='True if this file is likely a README file.')),

        ('is_top_level',
         Boolean(help='True if this file is "top-level" file located either at '
                      'the root of a package or in a well-known common location.')),

#         ('is_doc',
#          Boolean(help='True if this file is likely a documentation file.')),
#
#         ('is_test',
#          Boolean(help='True if this file is likely a test file.')),
#
#         ('is_generated',
#          Boolean(help='True if this file is likely an automatically generated file.')),
#
#         ('is_build',
#          Boolean(help='True if this file is likely a build script or file such as Makefile.')),

    ])

    sort_order = 50

    options = [
        CommandLineOption(('--classify',),
            is_flag=True, default=False,
            help='Classify files with flags telling if the file is a legal, '
                 'or readme or test file, etc.',
            help_group=PRE_SCAN_GROUP,
            sort_order=50,
            requires=['info']
        )
    ]

    def is_enabled(self, classify, **kwargs):
        return classify

    def process_codebase(self, codebase, classify, **kwargs):
        if not classify:
            return

        # find the real root directory
        root = codebase.root
        real_root = codebase.lowest_common_parent()
        if not real_root:
            real_root = root
        real_root_dist = real_root.distance(codebase)

        for resource in codebase.walk(topdown=True):
            real_dist = resource.distance(codebase) - real_root_dist
            resource.is_top_level = (real_dist < 2)
            if resource.is_file:
                # TODO: should we do something about directories? for now we only consider files
                set_classification_flags(resource)
            resource.save(codebase)


LEGAL_STARTS_ENDS = (
    'copying',
    'copyright',
    'copyrights',
    'notice',
    'license',
    'licenses',
    'licence',
    'licences',
    'legal',
    'eula',
    'agreement',
    'copyleft',
    'licensing',
    'licencing',
    'patent',
    'patents',
)

_MANIFEST_ENDS = {
    '.about': 'ABOUT file',
    '/bower.json': 'bower',
    '/project.clj': 'clojure',
    '.podspec': 'cocoapod',
    '/composer.json': 'composer',
    '/description': 'cran',
    '/elm-package.json': 'elm',
    '/+compact_manifest': 'freebsd',
    '+manifest': 'freebsd',
    '.gemspec': 'gem',
    '/metadata': 'gem',
    '/build.gradle': 'gradle',
    '.cabal': 'haskell',
    '/haxelib.json': 'haxelib',
    '.pom': 'maven',
    '/pom.xml': 'maven',
    '/package.json': 'npm',
    '.nuspec': 'nuget',
    '.pod': 'perl',
    '/meta.yml': 'perl',
    '/dist.ini': 'perl',
    '/pipfile': 'pypi',
    '/setup.cfg': 'pypi',
    '/setup.py': 'pypi',
    '.spec': 'rpm',
    '/cargo.toml': 'rust',
    '.spdx': 'spdx',

    # note that these two cannot be top-level for now
    '/debian/copyright': 'deb',
    '/meta-inf/manifest.mf': 'maven',
}

MANIFEST_ENDS = tuple(_MANIFEST_ENDS)

README_STARTS_ENDS = (
    'readme',
)


def set_classification_flags(resource,
        _LEGAL=LEGAL_STARTS_ENDS,
        _MANIF=MANIFEST_ENDS,
        _README=README_STARTS_ENDS):
    """
    Set classification flags on the `resource` Resource
    """
    name = resource.name.lower()
    path = resource.path.lower()

    resource.is_legal = name.startswith(_LEGAL) or name.endswith(_LEGAL)
    resource.is_readme = name.startswith(_README) or name.endswith(_README)
    resource.is_manifest = path.endswith(_MANIF)

    return resource
