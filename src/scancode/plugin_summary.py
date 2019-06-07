#
# Copyright (c) 2019 nexB Inc. and others. All rights reserved.
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

from packagedcode.utils import combine_expressions
from plugincode.post_scan import PostScanPlugin
from plugincode.post_scan import post_scan_impl
from scancode import CommandLineOption
from scancode import POST_SCAN_GROUP


# Tracing flags
TRACE = True


def logger_debug(*args):
    pass


if TRACE:
    import logging
    import sys

    logger = logging.getLogger(__name__)
    # logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(
            ' '.join(isinstance(a, unicode) and a or repr(a) for a in args))


@post_scan_impl
class OriginSummary(PostScanPlugin):
    """
    Rolls up copyright and license results to the directory level if a copyright or license
    is detected in 50% or more of total files in a directory
    """
    resource_attributes = dict(
        origin_summary=attr.ib(default=attr.Factory(OrderedDict)),
        summarized_to=attr.ib(default=None, type=str)
    )

    sort_order = 8

    options = [
        CommandLineOption(('--origin-summary',),
            is_flag=True, default=False,
            help='Origin summary',
            help_group=POST_SCAN_GROUP)
    ]

    def is_enabled(self, origin_summary, **kwargs):
        return origin_summary

    def process_codebase(self, codebase, **kwargs):
        root = codebase.get_resource(0)
        if not hasattr(root, 'copyrights') or not hasattr(root, 'licenses'):
            # TODO: Raise warning(?) if these fields are not there
            return

        for resource in codebase.walk(topdown=False):
            # TODO: Consider facets for later
            # TODO: Group summarizations by copyright holders and license expressions

            if resource.is_file:
                continue

            children = resource.children(codebase)
            if not children:
                continue

            # TODO: Consider using a list of resource id's to avoid walking a codebase multiple times
            origin_count = Counter()

            for child in children:
                if child.is_file:
                    license_expression = combine_expressions(child.license_expressions)
                    holders = tuple(h['value'] for h in child.holders if h['value'])
                    if not license_expression or not holders:
                        continue
                    origin = holders, license_expression
                    origin_count[origin] += 1
                else:
                    # We are in a subdirectory
                    child_origin_count = child.extra_data.get('origin_count', {})
                    origin_count.update(child_origin_count)

            if origin_count:
                resource.extra_data['origin_count'] = origin_count
                resource.save(codebase)
                (holders, license_expression), top_count = origin_count.most_common(1)[0]
                # TODO: Check for contradictions when performing summarizations
                if is_majority(top_count, resource.files_count):
                    resource.origin_summary['license_expression'] = license_expression
                    resource.origin_summary['holders'] = holders
                    resource.origin_summary['count'] = top_count
                    codebase.save_resource(resource)

                    for descendant in resource.walk(codebase, topdown=True):
                        if descendant.is_file:
                            d_license_expression = combine_expressions(descendant.license_expressions)
                            d_holders = tuple(h['value'] for h in descendant.holders)
                        else:
                            d_license_expression = descendant.origin_summary.get('license_expression')
                            d_holders  = descendant.origin_summary.get('holders')
                        if (d_holders, d_license_expression) == (holders, license_expression):
                            descendant.summarized_to = resource.path
                            descendant.save(codebase)


def is_majority(count, files_count):
    """
    Return True is this resource is a whatever directory with at least over 75% of whatever at full depth.
    """
    # TODO: Increase this and test with real codebases
    return count / files_count >= 0.75
