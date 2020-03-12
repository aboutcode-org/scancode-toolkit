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
import os.path

import click
click.disable_unicode_literals_warning = True

from plugincode.scan import ScanPlugin
from plugincode.scan import scan_impl
from scancode import CommandLineOption
from scancode import DOC_GROUP
from scancode import SCAN_GROUP
from commoncode.fileutils import parent_directory

from packagedcode import PACKAGE_TYPES


def print_packages(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    for package_cls in sorted(PACKAGE_TYPES, key=lambda pc: (pc.default_type)):
        click.echo('--------------------------------------------')
        click.echo('Package: {self.default_type}'.format(self=package_cls))
        click.echo(
            '  class: {self.__module__}:{self.__name__}'.format(self=package_cls))
        if package_cls.metafiles:
            click.echo('  metafiles: ', nl=False)
            click.echo(', '.join(package_cls.metafiles))
        if package_cls.extensions:
            click.echo('  extensions: ', nl=False)
            click.echo(', '.join(package_cls.extensions))
        if package_cls.filetypes:
            click.echo('  filetypes: ', nl=False)
            click.echo(', '.join(package_cls.filetypes))
        click.echo('')
    ctx.exit()


@scan_impl
class PackageScanner(ScanPlugin):
    """
    Scan a Resource for Package manifests and report these as "packages" at the
    right file or directory level.
    """

    resource_attributes = dict(packages=attr.ib(default=attr.Factory(list), repr=False))

    sort_order = 6

    required_plugins = ['scan:licenses', ]

    options = [
        CommandLineOption(('-p', '--package',),
            is_flag=True, default=False,
            help='Scan <input> for package manifests and packages.',
            # yes, this is showed as a SCAN plugin in doc/help
            help_group=SCAN_GROUP,
            sort_order=20),

        CommandLineOption(
            ( '--list-packages',),
            is_flag=True, is_eager=True,
            callback=print_packages,
            help='Show the list of supported package types and exit.',
            help_group=DOC_GROUP),
    ]

    def is_enabled(self, package, **kwargs):
        return package

    def get_scanner(self, **kwargs):
        """
        Return a scanner callable to scan a Resource for packages.
        """
        from scancode.api import get_package_info
        return get_package_info

    def process_codebase(self, codebase, **kwargs):
        """
        Move package manifest scan information to the proper file or
        directory level given a package type.
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

            # NOTE: we are dealing with a single file therefore there should be
            # only be a single package detected. But some package manifests can
            # document more than one package at a time such as multiple
            # arches/platforms for a gempsec or multiple sub package (with
            # "%package") in an RPM .spec file.
            for package_info in packages_info:
                # Break if this Resource has already been set as a new Package root
                manifest_path = package_info.get('manifest_path')
                if manifest_path and manifest_path != resource.path:
                    break

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
                # package) and if yes:
                # 1. fetch this resource
                # 2. move the package data to this new resource
                # 3. set the manifest_path if needed.
                # 4. save.

                # TODO: this is a hack for the ABOUT file Package parser, ABOUT files are kept alongside
                # the resource its for
                if new_package_root.is_file and resource.path.endswith('.ABOUT'):
                    new_manifest_path = os.path.join(parent_directory(new_package_root.path), resource.name)
                else:
                    # here we have a relocated Resource and we compute the manifest path
                    # relative to the new package root
                    # TODO: We should have codebase relative paths for manifests
                    new_package_root_path = new_package_root.path and new_package_root.path.strip('/')
                    if new_package_root_path:
                        _, _, new_manifest_path = resource.path.partition(new_package_root_path)
                        # note we could have also deserialized and serialized again instead
                package_info['manifest_path'] = new_manifest_path.lstrip('/')

                new_package_root.packages.append(package_info)
                codebase.save_resource(new_package_root)
                resource.packages = []
                codebase.save_resource(resource)

