#
# Copyright (c) nexB Inc. and others. All rights reserved.
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
from os.path import exists
from os.path import isdir

import attr

from commoncode import saneyaml
from plugincode.post_scan import PostScanPlugin
from plugincode.post_scan import post_scan_impl
from scancode import CommandLineOption
from scancode import POST_SCAN_GROUP


@post_scan_impl
class FilterURL(PostScanPlugin):
    """
    Filter URLs found in a white-list file.
    """

    options = [
        CommandLineOption(('--whitelisted-urls',),
            multiple=False,
            metavar='FILE',
            help='Load a list of white-listed URLs, one per line and remove URLs '
                 'that match any such URL from the scanned data.',
            required_options=['url'],
            help_group=POST_SCAN_GROUP,
        )
    ]

    def is_enabled(self, whitelisted_urls, **kwargs):
        return whitelisted_urls

    def process_codebase(self, codebase, whitelisted_urls, **kwargs):
        if not self.is_enabled(whitelisted_urls):

            return
        with open(whitelisted_urls) as wu:
            whitelisted = wu.read().splitlines(False)
        whitelisted = set(u for u in whitelisted if u and u.strip())
        if not whitelisted:
            return

        for resource in codebase.walk(topdown=True):
            if not resource.urls:
                continue

            filtered_urls = []
            for url in resource.urls:
                if url['url'] in whitelisted:
                    continue
                else:
                    filtered_urls.append(url)
 
            if filtered_urls != resource.urls:
                # save changes back.
                resource.urls = filtered_urls
                codebase.save_resource(resource)
