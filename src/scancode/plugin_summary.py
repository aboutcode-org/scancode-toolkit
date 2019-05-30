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


@post_scan_impl
class OriginSummary(PostScanPlugin):
    """
    Rolls up copyright and license results to the directory level if a copyright or license
    is detected in 80% or more of total files in a directory
    """
    sort_order = 8

    options = [
        CommandLineOption(('--origin-summary',),
            is_flag=True, default=False,
            required_options=['copyright','license'],
            help='Origin summary',
            help_group=POST_SCAN_GROUP)
    ]

    def is_enabled(self, origin_summary, copyright, license, **kwargs):
        return origin_summary and copyright and license

    def process_codebase(self, codebase, **kwargs):
        for resource in codebase.walk(topdown=False):
            if resource.is_file:
                continue

            children = resource.children(codebase)
            if not children:
                continue

            dir_licenses_count = Counter()
            dir_licenses = OrderedDict()
            dir_copyrights_count = Counter()
            child_dir_file_count = 0

            for child in children:
                child_file_count = child.files_count
                child_dir_file_count += child_file_count
                # TODO: Figure out a better way to keep track of how many Resources had what license
                # or copyright
                count = child_file_count * 0.8 if not child.is_file else 1
                for license in child.licenses:
                    license_key = license['key']
                    dir_licenses_count.update({license_key: count})
                    dir_licenses[license_key] = license
                for copyright in child.copyrights:
                    dir_copyrights_count.update({copyright['value']: count})

            total_file_count = resource.files_count + child_dir_file_count
            license_expressions = set()

            for k, v in dir_licenses_count.items():
                if is_majority(v, total_file_count):
                    license = dir_licenses[k]
                    resource.licenses.append(license)
                    codebase.save_resource(resource)
                    license_expressions.add(license['matched_rule']['license_expression'])
            resource.license_expressions = list(license_expressions)
            codebase.save_resource(resource)

            for k, v in dir_copyrights_count.items():
                if is_majority(v, total_file_count):
                    resource.copyrights.append(OrderedDict(value=k, start_line=None, end_line=None))
                    codebase.save_resource(resource)


def is_majority(count, files_count):
    """
    Return True is this resource is a whatever directory with at least over 80% of whatever at full depth.
    """
    return count / files_count >= 0.8
