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

from plugincode.scan import ScanPlugin
from plugincode.scan import scan_impl
from scancode import CommandLineOption
from scancode import SCAN_GROUP


@scan_impl
class PackageScanner(ScanPlugin):
    """
    Scan a Resource for Package manifests and report these as "packages" at the
    right file or directory level.
    """

    resource_attributes = dict(packages=attr.ib(default=attr.Factory(list)))

    sort_order = 6

    options = [
        CommandLineOption(('-p', '--package',),
            is_flag=True, default=False,
            help='Scan <input> for package manifests and packages.',
            # yes, this is showed as a SCAN plugin in doc/help
            help_group=SCAN_GROUP,
            sort_order=20),
    ]

    def is_enabled(self, package, **kwargs):
        return package

    def get_scanner(self, **kwargs):
        from scancode.api import get_package_info
        return get_package_info

    def process_codebase(self, codebase, **kwargs):
        """
        Move package manifest scan information to the proper file or
        directory level for a package type.
        """
        from packagedcode import get_package_class

        if codebase.has_single_resource:
            # What if we scanned a single file and we do not have a root proper?
            return

        for resource in codebase.walk(topdown=False):
            # only files can have a manifest
            if not resource.is_file:
                continue

            if resource.is_root:
                continue

            packages_info = resource.packages
            if not packages_info:
                continue

            package_info = packages_info[0]

            package_class = get_package_class(package_info)
            new_package_root = package_class.get_package_root(resource, codebase)

            if not new_package_root:
                # this can happen if we scan a single resource that is a package manifest
                continue

            if new_package_root == resource:
                continue

            # here new_package_root != resource:

            # What if the target resource (e.g. a parent) is the root and we are in stripped root mode?
            if new_package_root.is_root and codebase.strip_root:
                continue

            # Determine if this package applies to more than just the manifest
            # file (typically it means the whole parent directory is the
            # package) and if yes: 1. fetch this resource 2. move the package
            # data to this new resource 3. set the manifest_path if needed. 4.
            # save.

            # NOTE: do not do this if the new_package_root is not an ancestor
            # FIXME: this may not holad at all times?
            ancestors = resource.ancestors(codebase)
            if new_package_root not in ancestors:
                continue
            # here we have a relocated Resource and we compute the manifest path
            # relative to the new package root
            new_package_root_path = new_package_root.path
            if new_package_root_path and new_package_root_path.strip('/'):
                _, _, manifest_path = resource.path.partition(new_package_root_path)
                # note we could have also deserialized and serialized again instead
                package_info['manifest_path'] = manifest_path.lstrip('/')

            new_package_root.packages.append(package_info)
            codebase.save_resource(new_package_root)
            resource.packages = []
            codebase.save_resource(resource)
