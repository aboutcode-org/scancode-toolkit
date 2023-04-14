#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from commoncode.datautils import Boolean
from plugincode.pre_scan import PreScanPlugin
from plugincode.pre_scan import pre_scan_impl
from commoncode.cliutils import PluggableCommandLineOption
from commoncode.cliutils import PRE_SCAN_GROUP

from summarycode.classify import set_classification_flags

"""
Tag files as "key" or important and top-level files.
"""

# Tracing flag
TRACE = False


def logger_debug(*args):
    pass


if TRACE:
    import logging
    import click

    class ClickHandler(logging.Handler):
        _use_stderr = True

        def emit(self, record):
            try:
                msg = self.format(record)
                click.echo(msg, err=self._use_stderr)
            except Exception:
                self.handleError(record)

    logger = logging.getLogger(__name__)
    logger.handlers = [ClickHandler()]
    logger.propagate = False
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, str) and a or repr(a) for a in args))


@pre_scan_impl
class FileClassifier(PreScanPlugin):
    """
    Classify a file such as a COPYING file or a package manifest with a flag.
    """
    resource_attributes = dict([
        ('is_legal',
         Boolean(help='True if this file is likely a "legal", license-related'
                      'file such as a COPYING or LICENSE file.')),

        ('is_manifest',
         Boolean(help='True if this file is likely a package manifest file such '
                      'as a Maven pom.xml or an npm package.json')),

        ('is_readme',
         Boolean(help='True if this file is likely a README file.')),

        ('is_top_level',
         Boolean(help='True if this file is "top-level" file located either at '
                      'the root of a package or in a well-known common location.')),

        ('is_key_file',
         Boolean(help='True if this file is "top-level" file and either a '
                      'legal, readme or manifest file.')),

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
#
#         we have an is_data attribute
#         ('is_data',
#          Boolean(help='True if this file is likely data file.')),

    ])

    sort_order = 30

    options = [
        PluggableCommandLineOption(('--classify',),
            is_flag=True, default=False,
            help='Classify files with flags indicating whether the file is a '
                 'legal, readme, test or similar file.',
            help_group=PRE_SCAN_GROUP,
            sort_order=50,
        )
    ]

    def is_enabled(self, classify, **kwargs):
        return classify

    def process_codebase(self, codebase, classify, **kwargs):
        # find the real root directory
        real_root = codebase.lowest_common_parent()
        if not real_root:
            real_root = codebase.root
        real_root_dist = real_root.distance(codebase)

        for resource in codebase.walk(topdown=True):
            real_dist = resource.distance(codebase) - real_root_dist
            # this means this is either a child of the root dir or the root itself.
            resource.is_top_level = (real_dist < 2)
            if resource.is_file:
                # TODO: should we do something about directories? for now we only consider files
                set_classification_flags(resource)
            resource.save(codebase)
