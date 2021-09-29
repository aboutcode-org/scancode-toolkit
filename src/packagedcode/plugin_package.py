#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#


import attr
import click

from plugincode.scan import ScanPlugin
from plugincode.scan import scan_impl
from commoncode.cliutils import PluggableCommandLineOption
from commoncode.cliutils import DOC_GROUP
from commoncode.cliutils import SCAN_GROUP

from packagedcode import get_package_instance
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

    resource_attributes = {}
    codebase_attributes = {}
    resource_attributes['package_manifests'] = attr.ib(default=attr.Factory(list), repr=False)
    codebase_attributes['packages'] = attr.ib(default=attr.Factory(list), repr=False)

    sort_order = 6

    required_plugins = ['scan:licenses', ]

    options = [
        PluggableCommandLineOption(('-p', '--package',),
            is_flag=True, default=False,
            help='Scan <input> for package manifests and build scripts.',
            help_group=SCAN_GROUP,
            sort_order=20),

        PluggableCommandLineOption(
            ('--list-packages',),
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
        from scancode.api import get_package_manifests
        return get_package_manifests

    def process_codebase(self, codebase, **kwargs):
        """
        Set the package root given a package "type".
        """
        create_packages_from_manifests(codebase, **kwargs)

        if codebase.has_single_resource:
            # What if we scanned a single file and we do not have a root proper?
            return

        for resource in codebase.walk(topdown=False):
            set_packages_root(resource, codebase)


def create_packages_from_manifests(codebase, **kwargs):
    """
    Create package instances from package manifests present in the codebase.
    """
    package_manifests = []

    for resource in codebase.walk(topdown=False):
        if resource.package_manifests:
            package_manifests.extend(resource.package_manifests)

    codebase.attributes.packages.extend(package_manifests)


def set_packages_root(resource, codebase):
    """
    Set the root_path attribute as the path to the root Resource for a given
    package package or build script that may exist in a `resource`.
    """
    # only files can have a package
    if not resource.is_file:
        return

    package_manifests = resource.package_manifests
    if not package_manifests:
        return
    # NOTE: we are dealing with a single file therefore there should be only be
    # a single package detected. But some package manifests can document more
    # than one package at a time such as multiple arches/platforms for a gempsec
    # or multiple sub package (with "%package") in an RPM .spec file.

    modified = False
    for package_manifest in package_manifests:
        package_instance = get_package_instance(package_manifest)
        package_root = package_instance.get_package_root(resource, codebase)
        if not package_root:
            # this can happen if we scan a single resource that is a package package
            continue
        # What if the target resource (e.g. a parent) is the root and we are in stripped root mode?
        if package_root.is_root and codebase.strip_root:
            continue
        package_manifest['root_path'] = package_root.path
        modified = True

    if modified:
        # we did set the root_path
        codebase.save_resource(resource)
    return resource
