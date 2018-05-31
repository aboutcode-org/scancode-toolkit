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

import attr

from plugincode.post_scan import PostScanPlugin
from plugincode.post_scan import post_scan_impl
from scancode import CommandLineOption
from scancode import POST_SCAN_GROUP

# Tracing flags
TRACE = False
TRACE_DEEP = False


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


@post_scan_impl
class ScanSummary(PostScanPlugin):
    """
    Summarize a scan.
    """

    attributes = dict(summary=attr.ib(default=attr.Factory(OrderedDict)))

    sort_order = 12

    options = [
        CommandLineOption(('--summary',),
            is_flag=True, default=False,
            help='Summarize license, copyright and available scans at the file and '
                 'directory level.',
            help_group=POST_SCAN_GROUP)
    ]

    def is_enabled(self, summary, **kwargs):
        return summary

    def process_codebase(self, codebase, summary, **kwargs):
        """
        Populate a summary mapping for available scans at the file and directory levels.
        The summary has this high level form and is grouped first by facet and second by category:
            summary:
                facet: core
                    - category: source
                        - license_expression: (gpl-2.0 or bsd-new) and mit
                        - license_expressions:
                            - count: 10
                              value: gpl-2.0 or bsd-new
                            - count: 2
                              value: mit

                        - programming_language:
                            - count: 10
                              value: java
                            - count: 2
                              value: javascript

                        - copyright_holders:
                            - count: 10
                              value: RedHat Inc.
                            - count: 2
                              value: RedHat Inc.and others.

                    - category: toplevel
                        - license_expression: gpl-2.0
                        - license_expressions:
                            - count: 1
                              value: gpl-2.0

                        - copyright_holders:
                            - count: 1
                              value: RedHat Inc.

                facet: dev
                    - category: source
                        - license_expression: gpl-2.0
                        - license_expressions:
                            - count: 23
                              value: gpl-2.0
                            - count: 10
                              value: none
                        - copyright_holders:
                            - count: 20
                              value: RedHat Inc.
                            - count: 10
                              value: none

                        - programming_languages:
                            - count: 34
                              value: java

                    - category: data

        """
        for resource in codebase.walk(topdown=False):
            pass
