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
from __future__ import unicode_literals

from functools import partial

from commoncode.fileset import match
from plugincode.pre_scan import PreScanPlugin
from plugincode.pre_scan import pre_scan_impl
from scancode import CommandLineOption
from scancode import PRE_SCAN_GROUP


@pre_scan_impl
class ProcessIgnore(PreScanPlugin):
    """
    Ignore files matching the supplied pattern.
    """

    options = [
        CommandLineOption(('--ignore',),
           multiple=True,
           metavar='<pattern>',
           help='Ignore files matching <pattern>.',
           sort_order=10,
           help_group=PRE_SCAN_GROUP)
    ]

    def is_enabled(self, ignore, **kwargs):
        return ignore

    def process_codebase(self, codebase, ignore=(), **kwargs):
        """
        Remove ignored Resources from the resource tree.
        """

        if not ignore:
            return

        ignores = {
            pattern: 'User ignore: Supplied by --ignore' for pattern in ignore
        }

        ignorable = partial(is_ignored, ignores=ignores)
        rids_to_remove = []
        remove_resource = codebase.remove_resource

        # First, walk the codebase from the top-down and collect the rids of
        # Resources that can be removed.
        for resource in codebase.walk(topdown=True):
            if ignorable(resource.path):
                for child in resource.children(codebase):
                    rids_to_remove.append(child.rid)
                rids_to_remove.append(resource.rid)

        # Then, walk bottom-up and remove the ignored Resources from the
        # Codebase if the Resource's rid is in our list of rid's to remove.
        for resource in codebase.walk(topdown=False):
            resource_rid = resource.rid
            if resource_rid in rids_to_remove:
                rids_to_remove.remove(resource_rid)
                remove_resource(resource)


def is_ignored(location, ignores):
    """
    Return a tuple of (pattern , message) if a file at location is ignored or
    False otherwise. `ignores` is a mappings of patterns to a reason.
    """
    return match(location, includes=ignores, excludes={})
