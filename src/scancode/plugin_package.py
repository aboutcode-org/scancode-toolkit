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

import attr

from plugincode.post_scan import PostScanPlugin
from plugincode.post_scan import post_scan_impl
from plugincode.scan import ScanPlugin
from plugincode.scan import scan_impl
from scancode import CommandLineOption
from scancode import SCAN_GROUP


@scan_impl
class PackageManifestScanner(ScanPlugin):
    """
    Scan a Resource for Package manifests.
    """

    attributes = dict(package_manifest=attr.ib(default=None))

    sort_order = 6

    options = [
        CommandLineOption(('-p', '--package',),
            is_flag=True, default=False,
            help='Scan <input> for package manifests and packages.',
            help_group=SCAN_GROUP,
            sort_order=20),
    ]

    def is_enabled(self, package, **kwargs):
        return package

    def get_scanner(self, **kwargs):
        from scancode.api import get_package_info
        return get_package_info


@post_scan_impl
class PackageRootSummarizer(PostScanPlugin):
    """
    Copy package manifest scan information to the proper file or directory level
    as "packages".
    """

    # NOTE: this post scan plugin does NOT declare any option: instead it relies
    # on the PackageManifestScanner options to be enbaled and always runs when
    # package scanning is requested.
    attributes = dict(packages=attr.ib(default=attr.Factory(list)))

    def is_enabled(self, package, **kwargs):
        return package

    def process_codebase(self, codebase, package, **kwargs):
        """
        Copy package manifest information at the proper file or directory level.
        """
        from packagedcode import get_package_class

        for resource in codebase.walk(topdown=False):
            # only files can have a manifest
            if not resource.is_file or not resource.package_manifest:
                continue
            # determine if the manifest points to another or directory.
            # fetch that resource , set a package then update and save.
            package_class = get_package_class(resource.package_manifest)
            package_target = package_class.get_package_root(resource, codebase)
            if not package_target:
                # this can happen if we scan a single resource that is a package manifest
                package_target = resource
            package_target.packages.append(resource.package_manifest)
            codebase.save_resource(package_target)
