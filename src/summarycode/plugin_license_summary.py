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

from collections import Counter
from collections import OrderedDict

import attr

from plugincode.post_scan import PostScanPlugin
from plugincode.post_scan import post_scan_impl
from scancode import CommandLineOption
from scancode import POST_SCAN_GROUP

# Tracing flags
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


@post_scan_impl
class LicenseSummary(PostScanPlugin):
    """
    Summarize license expressions.
    """

    attributes = dict(license_summary=attr.ib(default=attr.Factory(list)))

    sort_order = 10

    options = [
        CommandLineOption(('--license-summary',),
            is_flag=True, default=False,
            help='Summarize license expressions at the file and directory level.'
            'Requires license_expression.',
            help_group=POST_SCAN_GROUP)
    ]

    def is_enabled(self, license_summary, **kwargs):  # NOQA
        return license_summary

    def process_codebase(self, codebase, license_summary, **kwargs):
        """
        Populate a license_summary list of mappings such as
        {value: "some expression", count: "count of occurences"}
        sorted by decreasing count.
        The original expressions have this form:
            "license_expressions": ["mit", "gpl-2.0 OR apache-2.0"]
        The licenses_summary has this form:
            "license_summary": [
                {"value": "gpl-2.0 OR apache-2.0", "count": 8},
                {"value": "mit", "count": 1},
            ]
        """
        for resource in codebase.walk(topdown=False):
            if not hasattr(resource, 'license_expressions'):
                continue
            expressions = Counter()
            exp = resource.license_expressions or []
            expressions.update(exp)

            # Collect direct children expression summaries
            for child in resource.children(codebase):
                for summary in child.license_summary:
                    expressions.update({summary['value']: summary['count']})
            if TRACE:
                logger_debug('process_codebase:expressions:', expressions)
            summaries = []
            for expression, count in expressions.most_common():
                item = OrderedDict([
                    ('value', expression),
                    ('count', count),
                ])
                summaries.append(item)
            resource.license_summary = summaries
            codebase.save_resource(resource)
