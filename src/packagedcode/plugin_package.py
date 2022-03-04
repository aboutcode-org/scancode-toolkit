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

from packageurl import PackageURL
from packagedcode import get_package_instance
from packagedcode import PACKAGE_DATA_CLASSES
from packagedcode import PACKAGE_INSTANCES_BY_TYPE
from packagedcode.models import Dependency


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
    for package_cls in sorted(PACKAGE_DATA_CLASSES, key=lambda pc: (pc.default_type)):
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
    Scan a Resource for Package data and report these as "package_data" at the
    right file or directory level. Then create package instances with these and
    other package information and files, and report these as "packages" at the
    top level (codebase level).
    """
    resource_attributes = {}
    codebase_attributes = {}
    codebase_attributes['dependencies'] = attr.ib(default=attr.Factory(list), repr=False)
    codebase_attributes['packages'] = attr.ib(default=attr.Factory(list), repr=False)
    resource_attributes['package_data'] = attr.ib(default=attr.Factory(list), repr=False)
    resource_attributes['for_packages'] = attr.ib(default=attr.Factory(list), repr=False)

    sort_order = 6

    required_plugins = ['scan:licenses', ]

    options = [
        PluggableCommandLineOption(('-p', '--package',),
            is_flag=True, default=False,
            help='Scan <input> for package data and build scripts.',
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
        from scancode.api import get_package_data
        return get_package_data

    def process_codebase(self, codebase, **kwargs):
        """
        Populate top level `packages` with package instances.
        """
        create_package_and_dep_instances(codebase, **kwargs)


def create_package_and_dep_instances(codebase, **kwargs):
    """
    Create package instances from package data present in the codebase.
    """
    package_data_files = []
    package_instance_by_id = {}

    dependency_data_paths = []
    dependency_instance_by_id = {}

    for resource in codebase.walk(topdown=False):
        if not resource.package_data:
            continue

        # continue if this resource is already in a package_instance
        if resource.path in package_data_files:
            continue

        if TRACE:
            logger_debug(
                'create_package_and_dep_instances:',
                'location:', resource.location,
            )

        # Currently we assume there is only one PackageData 
        # ToDo: Do this for multiple PackageDatas per resource
        package_data = resource.package_data[0]

        # Check if the package data has all the mandatory attributes to create a pURL
        if not package_data.get("name"):

            # Check if package_data is from lockfile
            if package_data.get("dependencies"):
                dependency_data_paths.append(resource.path)
                for dependency_instance in create_dependency_instances(
                    resource.path,
                    package_data.get("dependencies")
                ):
                    dependency_instance_by_id[dependency_instance.dependency_uuid] = dependency_instance

            continue

        # Check if Package is implemented for this package type
        pk_instance_class = PACKAGE_INSTANCES_BY_TYPE.get(package_data["type"])
        if not pk_instance_class:
            continue

        # create a Package object of the package type which this manifest belongs to
        pk_instance = pk_instance_class()
        pk_instance_uuid = uuid.uuid4()
        package_instance_by_id[pk_instance_uuid] = pk_instance

        # use `get_other_package_data` to get other package_data files of this instance
        package_data_by_path = pk_instance.get_other_package_data(resource, codebase)
        package_data_by_path[resource.path] = package_data

        # populate Package with data from it's package_data files
        pk_instance.populate_package_data(package_data_by_path, uuid=pk_instance_uuid)

        if TRACE:
            logger_debug(
                'create_package_and_dep_instances:',
                'package_data_by_path:', package_data_by_path,
            )

        # add `path` into `package_data_files` for all package_datas
        for path, package_data in package_data_by_path.items():
            package_data_files.append(path)

            if package_data.get("dependencies"):
                if path in dependency_data_paths:
                    set_package_uuid_for_dependencies(
                        dependency_instance_by_id,
                        path,
                        pk_instance.package_uuid,
                    )
                    continue

                dependency_data_paths.append(path)
                for dep_instance in create_dependency_instances(
                    path,
                    package_data.get("dependencies")
                ):
                    dependency_instance_by_id[dep_instance.dependency_uuid] = dep_instance
                    dep_instance.for_package = pk_instance.package_uuid

        # get files for this Package
        pk_instance.files = tuple(pk_instance.get_package_files(resource, codebase))

        # add `package_uuid` to `for_packages` for all files of that package
        update_files_with_package_uuid(pk_instance.files, codebase, pk_instance.package_uuid)

        if TRACE:
            logger_debug(
                'create_package_and_dep_instances:',
                'pk_instance:', pk_instance,
            )

    if TRACE:
        logger_debug(
            'create_package_and_dep_instances:',
            'package_data_files:', package_data_files,
        )

    # Get unique Package objects from `package_instance_by_id`
    for package_instance in list(package_instance_by_id.values()):
        codebase.attributes.packages.append(package_instance.to_dict())

     # Get unique Dependency objects from `dependency_instance_by_id`
    for dependency_instance in list(dependency_instance_by_id.values()):
        codebase.attributes.dependencies.append(dependency_instance.to_dict())


def update_files_with_package_uuid(file_paths, codebase, package_uuid):
    """
    For the corresponding resources to a list of `file_paths` for a Package,
    set their `for_packages` with the `package_uuid`. 
    """
    for file_path in file_paths:
        resource = codebase.get_resource_from_path(file_path)
        resource.for_packages.append(package_uuid)
        resource.save(codebase)


def set_package_uuid_for_dependencies(dependency_instance_by_id, path, pk_instance_uuid):
    """
    For all dependency instances in `dependency_instance_by_id` which were collected from a
    specific `path` update their `for_package` attribute to `pk_instance_uuid`. 
    """
    for dep_instance in dependency_instance_by_id.values():
        if path is dep_instance.lockfile:
            dep_instance.for_package = pk_instance_uuid


def create_dependency_instances(path, dependencies):
    """
    Return a list of Dependency obejcts corresponding to
    each dependency in the `package_data` level `dependencies` list. 
    """
    dependency_instances = []

    for dependency in dependencies:
        purl = PackageURL.from_string(dependency['purl'])
        purl.qualifiers["uuid"] = str(uuid.uuid4())

        dependency_instances.append(
            Dependency(
                dependency_uuid=purl.to_string(),
                purl=dependency['purl'],
                requirement=dependency['requirement'],
                scope=dependency['scope'],
                is_runtime=dependency['is_runtime'],
                is_optional=dependency['is_optional'],
                is_resolved=dependency['is_resolved'],
                lockfile=path,
            )
        )

    return dependency_instances


def set_packages_root(resource, codebase):
    """
    Set the root_path attribute as the path to the root Resource for a given
    package package or build script that may exist in a `resource`.
    """
    # only files can have a package
    if not resource.is_file:
        return

    package_data_all = resource.package_data
    if not package_data_all:
        return
    # NOTE: we are dealing with a single file therefore there should be only be
    # a single package detected. But some package data can document more
    # than one package at a time such as multiple arches/platforms for a gempsec
    # or multiple sub package (with "%package") in an RPM .spec file.

    modified = False
    for package_data in package_data_all:
        package_instance = get_package_instance(package_data)
        package_root = package_instance.get_package_root(resource, codebase)
        if not package_root:
            # this can happen if we scan a single resource that is a package package
            continue
        # What if the target resource (e.g. a parent) is the root and we are in stripped root mode?
        if package_root.is_root and codebase.strip_root:
            continue
        package_data['root_path'] = package_root.path
        modified = True

    if modified:
        # we did set the root_path
        codebase.save_resource(resource)
    return resource
