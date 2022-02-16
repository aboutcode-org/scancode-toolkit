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
import os
import sys
import uuid

from plugincode.scan import ScanPlugin
from plugincode.scan import scan_impl
from commoncode.cliutils import PluggableCommandLineOption
from commoncode.cliutils import DOC_GROUP
from commoncode.cliutils import SCAN_GROUP

from packagedcode import get_package_instance
from packagedcode import PACKAGE_MANIFEST_TYPES
from packagedcode import PACKAGE_INSTANCES_BY_TYPE


TRACE = os.environ.get('SCANCODE_DEBUG_PACKAGE', False)

if TRACE:

    use_print = True

    if use_print:
        printer = print
    else:
        import logging

        logger = logging.getLogger(__name__)
        # logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
        logging.basicConfig(stream=sys.stdout)
        logger.setLevel(logging.DEBUG)
        printer = logger.debug

    def logger_debug(*args):
        return printer(' '.join(isinstance(a, str) and a or repr(a)
                                     for a in args))

def print_packages(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    for package_cls in sorted(PACKAGE_MANIFEST_TYPES, key=lambda pc: (pc.default_type)):
        click.echo('--------------------------------------------')
        click.echo('Package: {self.default_type}'.format(self=package_cls))
        click.echo(
            '  class: {self.__module__}:{self.__name__}'.format(self=package_cls))
        if package_cls.file_patterns:
            click.echo('  file_patterns: ', nl=False)
            click.echo(', '.join(package_cls.file_patterns))
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
    codebase_attributes['packages'] = attr.ib(default=attr.Factory(list), repr=False)
    resource_attributes['package_manifests'] = attr.ib(default=attr.Factory(list), repr=False)
    resource_attributes['for_packages'] = attr.ib(default=attr.Factory(list), repr=False)

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
        Populate top level `packages` with package instances.
        """
        for package_instance in create_packages_from_manifests(codebase, **kwargs):
            codebase.attributes.packages.append(package_instance.to_dict())


def create_packages_from_manifests(codebase, **kwargs):
    """
    Create package instances from package manifests present in the codebase.
    """
    package_instances_by_paths = {}
    package_instance_by_identifiers = {}

    for resource in codebase.walk(topdown=False):
        if not resource.package_manifests:
            continue

        # continue if resource.path already in `package_instances_by_paths`
        if resource.path in package_instances_by_paths:
            continue

        if TRACE:
            logger_debug(
                'create_packages_from_manifests:',
                'location:', resource.location,
            )

        # Currently we assume there is only one PackageManifest 
        # ToDo: Do this for multiple PackageManifests per resource
        manifest = resource.package_manifests[0]

        # Check if the package manifests has all the mandatory attributes to create a pURL
        if not manifest.get("name"):
            continue

        # Check if PackageInstance is implemented
        pk_instance_class = PACKAGE_INSTANCES_BY_TYPE.get(manifest["type"])
        if not pk_instance_class:
            continue

        # create a PackageInstance from the `default_type`
        pk_instance = pk_instance_class()
        pk_instance_uuid = uuid.uuid4()
        package_instance_by_identifiers[pk_instance_uuid] = pk_instance

        # use the get_other_manifests_for_instance to get other instances
        package_manifests_by_path = pk_instance.get_other_manifests_for_instance(resource, codebase)
        package_manifests_by_path[resource.path] = manifest

        if TRACE:
            logger_debug(
                'create_packages_from_manifests:',
                'package_manifests_by_path:', package_manifests_by_path,
            )

        # add `path: Instance` into `package_instances_by_paths` for all manifests
        for path in package_manifests_by_path.keys():
            package_instances_by_paths[path] = pk_instance

        # populate PackageInstance with data from manifests
        pk_instance.populate_instance_from_manifests(package_manifests_by_path, uuid=pk_instance_uuid)

        # get files for this PackageInstance
        pk_instance.files = tuple(pk_instance.get_package_files(resource, codebase))

        # add `package_uuid` to `for_packages` for all files of that package
        update_files_with_package_uuid(pk_instance.files, codebase, pk_instance.package_uuid)

        if TRACE:
            logger_debug(
                'create_packages_from_manifests:',
                'pk_instance:', pk_instance,
            )

    if TRACE:
        logger_debug(
            'create_packages_from_manifests:',
            'package_instances_by_paths:', package_instances_by_paths,
        )

    # Get unique PackageInstance objects from `package_instances_by_paths`
    return list(package_instance_by_identifiers.values())


def update_files_with_package_uuid(file_paths, codebase, package_uuid):
    """
    For the corresponding resources to a list of `file_paths` for a PackageInstance,
    set their `for_packages` with the `package_uuid`. 
    """
    for file_path in file_paths:
        resource = codebase.get_resource_from_path(file_path)
        resource.for_packages.append(package_uuid)
        resource.save(codebase)


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
