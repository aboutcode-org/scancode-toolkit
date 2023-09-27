#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import functools
import logging
import os

import attr
import click

from commoncode.cliutils import PluggableCommandLineOption
from commoncode.cliutils import DOC_GROUP
from commoncode.cliutils import SCAN_GROUP
from commoncode.resource import Resource
from commoncode.resource import strip_first_path_segment
from plugincode.scan import scan_impl
from plugincode.scan import ScanPlugin

from licensedcode.cache import build_spdx_license_expression
from licensedcode.cache import get_cache
from licensedcode.detection import DetectionRule
from packagedcode import get_package_handler
from packagedcode.licensing import add_referenced_license_matches_for_package
from packagedcode.licensing import add_referenced_license_detection_from_package
from packagedcode.licensing import add_license_from_sibling_file
from packagedcode.licensing import get_license_detection_mappings
from packagedcode.licensing import get_license_expression_from_detection_mappings
from packagedcode.models import add_to_package
from packagedcode.models import Dependency
from packagedcode.models import Package
from packagedcode.models import PackageData
from packagedcode.models import PackageWithResources

TRACE = os.environ.get('SCANCODE_DEBUG_PACKAGE_API', False)


def logger_debug(*args):
    pass


logger = logging.getLogger(__name__)

if TRACE:
    import sys

    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, str) and a or repr(a) for a in args))


def print_packages(ctx, param, value):
    """
    Print the list of supported package manifests and datafile formats
    """
    if not value or ctx.resilient_parsing:
        return

    for package_data in get_available_package_parsers():
        click.echo('--------------------------------------------')
        click.echo(f'Package type:  {package_data["package_type"]}')
        click.echo(f'  datasource_id:     {package_data["datasource_id"]}')
        click.echo(f'  documentation URL: {package_data["documentation_url"]}')
        click.echo(f'  primary language:  {package_data["default_primary_language"]}')
        click.echo(f'  description:       {package_data["description"]}')
        click.echo(f'  path_patterns:    {package_data["path_patterns"]}')
    ctx.exit()


def get_available_package_parsers(docs=False):

    from packagedcode import ALL_DATAFILE_HANDLERS

    all_data_packages = []

    for cls in sorted(
        ALL_DATAFILE_HANDLERS,
        key=lambda pc: (pc.default_package_type or '', pc.datasource_id),
    ):
        if cls.datasource_id is None:
            raise Exception(cls)

        data_packages = {}
        if docs:
            path_patterns = '\n       '.join(f"``{p}``" for p in cls.path_patterns)
            if cls.default_package_type:
                data_packages['package_type'] = f"``{cls.default_package_type}``"
            else:
                data_packages['package_type'] = cls.default_package_type
            data_packages['datasource_id'] = f"``{cls.datasource_id}``"
        else:
            path_patterns = ', '.join(repr(p) for p in cls.path_patterns)
            data_packages['package_type'] = cls.default_package_type
            data_packages['datasource_id'] = cls.datasource_id

        data_packages['documentation_url'] = cls.documentation_url
        data_packages['default_primary_language'] = cls.default_primary_language
        data_packages['description'] = cls.description
        data_packages['path_patterns'] = path_patterns

        all_data_packages.append(data_packages)

    return all_data_packages



@scan_impl
class PackageScanner(ScanPlugin):
    """
    Scan a Resource for Package data and report these as "package_data" at the
    file level. Then create "packages" from these "package_data" at the top
    level.
    """

    codebase_attributes = dict(
        # a list of packages
        packages=attr.ib(default=attr.Factory(list), repr=False),
        # a list of dependencies
        dependencies=attr.ib(default=attr.Factory(list), repr=False),
    )
    resource_attributes = dict(
        # a list of package data
        package_data=attr.ib(default=attr.Factory(list), repr=False),
        # a list of purls with UUID that a file belongs to
        for_packages=attr.ib(default=attr.Factory(list), repr=False),
    )

    required_plugins = ['scan:licenses']

    run_order = 3
    sort_order = 3

    options = [
        PluggableCommandLineOption(
            (
                '-p',
                '--package',
            ),
            is_flag=True,
            default=False,
            help='Scan <input> for application package and dependency manifests, lockfiles and related data.',
            help_group=SCAN_GROUP,
            sort_order=20,
        ),
        PluggableCommandLineOption(
            (
                '--system-package',
            ),
            is_flag=True,
            default=False,
            help='Scan <input> for installed system package databases.',
            help_group=SCAN_GROUP,
            sort_order=21,
        ),
        PluggableCommandLineOption(
            (
                '--purl',
            ),
            is_flag=True,
            default=False,
            help='Only detect PURL fields in application package and dependency manifests, lockfiles and related data.',
            help_group=SCAN_GROUP,
            sort_order=22,
        ),
        PluggableCommandLineOption(
            ('--list-packages',),
            is_flag=True,
            is_eager=True,
            callback=print_packages,
            help='Show the list of supported package manifest parsers and exit.',
            help_group=DOC_GROUP,
        ),
    ]

    def is_enabled(self, package, system_package, purl, **kwargs):
        return package or system_package or purl

    def get_scanner(self, package=True, system_package=False, purl=False, **kwargs):
        """
        Return a scanner callable to scan a file for package data.
        """
        from scancode.api import get_package_data

        return functools.partial(
            get_package_data,
            application=package,
            system=system_package,
            purl_only=purl,
        )

    def process_codebase(self, codebase, strip_root=False, purl=False, **kwargs):
        """
        Populate the ``codebase`` top level ``packages`` and ``dependencies``
        with package and dependency instances, assembling parsed package data
        from one or more datafiles as needed.

        Also perform additional package license detection that depends on either
        file license detection or the package detections.
        """
        # If we only want purls, we want to skip both the package
        # assembly and the extra package license detection steps
        if purl:
            return

        has_licenses = hasattr(codebase.root, 'license_detections')

        # These steps add proper license detections to package_data and hence
        # this is performed before top level packages creation
        for resource in codebase.walk(topdown=False):
            if not has_licenses:
                #TODO: Add the steps where we detect licenses from files for only a package scan
                # in the multiprocessing get_package_data API function
                continue

            # If we don't detect license in package_data but there is license detected in file
            # we add the license expression from the file to a package
            modified = add_license_from_file(resource, codebase)
            if TRACE and modified:
                logger_debug(f'packagedcode: process_codebase: add_license_from_file: modified: {modified}')

            if codebase.has_single_resource:
                continue

            # If there is referenced files in a extracted license statement, we follow
            # the references, look for license detections and add them back
            modified = list(add_referenced_license_matches_for_package(resource, codebase))
            if TRACE and modified:
                logger_debug(f'packagedcode: process_codebase: add_referenced_license_matches_for_package: modified: {modified}')

            # If there is a LICENSE file on the same level as the manifest, and no license
            # is detected in the package_data, we add the license from the file
            modified = add_license_from_sibling_file(resource, codebase)
            if TRACE and modified:
                logger_debug(f'packagedcode: process_codebase: add_license_from_sibling_file: modified: {modified}')

        # Create codebase-level packages and dependencies
        create_package_and_deps(codebase, strip_root=strip_root, **kwargs)

        if has_licenses:
            # This step is dependent on top level packages
            for resource in codebase.walk(topdown=False):
                # If there is a unknown reference to a package we add the license
                # from the package license detection
                modified = list(add_referenced_license_detection_from_package(resource, codebase))
                if TRACE and modified:
                    logger_debug(f'packagedcode: process_codebase: add_referenced_license_matches_from_package: modified: {modified}')


def add_license_from_file(resource, codebase):
    """
    Given a Resource, check if the detected package_data doesn't have license detections
    and the file has license detections, and if so, populate the package_data license
    expression and detection fields from the file license.
    """
    if TRACE:
        logger_debug(f'packagedcode.plugin_package: add_license_from_file: resource: {resource.path}')

    if not resource.is_file:
        return

    license_detections_file = resource.license_detections

    if TRACE:
        logger_debug(f'add_license_from_file: license_detections_file: {license_detections_file}')
    if not license_detections_file:
        return

    package_data = resource.package_data
    if not package_data:
        return

    for pkg in package_data:
        license_detections_pkg = pkg["license_detections"]
        if TRACE:
            logger_debug(f'add_license_from_file: license_detections_pkg: {license_detections_pkg}')

        if not license_detections_pkg:
            pkg["license_detections"] = license_detections_file.copy()
            for detection in pkg["license_detections"]:
                if "detection_log" in detection:
                    detection["detection_log"].append(DetectionRule.PACKAGE_ADD_FROM_FILE.value)

            license_expression = get_license_expression_from_detection_mappings(
                detections=license_detections_file,
                valid_expression=True
            )
            pkg["declared_license_expression"] = license_expression
            pkg["declared_license_expression_spdx"] = str(build_spdx_license_expression(
                license_expression=license_expression,
                licensing=get_cache().licensing,
            ))

            codebase.save_resource(resource)
            return pkg


def get_installed_packages(root_dir, processes=2, **kwargs):
    """
    Detect and yield Package mappings with their assigned Resource in a ``resources``
    attribute as they are found in `root_dir`.
    """
    from scancode import cli

    _, codebase = cli.run_scan(
        input=root_dir,
        processes=processes,
        quiet=True,
        verbose=False,
        max_in_memory=0,
        return_results=False,
        return_codebase=True,
        system_package=True,
    )

    packages_by_uid = {}
    for package in codebase.attributes.packages:
        p = PackageWithResources.from_dict(package)
        packages_by_uid[p.package_uid] = p

    for resource in codebase.walk():
        for package_uid in resource.for_packages:
            p = packages_by_uid[package_uid]
            p.resources.append(resource)

    yield from packages_by_uid.values()


def create_package_and_deps(codebase, package_adder=add_to_package, strip_root=False, **kwargs):
    """
    Create and save top-level Package and Dependency from the parsed
    package data present in the codebase.
    """
    packages, dependencies = get_package_and_deps(
        codebase,
        package_adder=package_adder,
        strip_root=strip_root,
        **kwargs
    )
    codebase.attributes.packages.extend(pkg.to_dict() for pkg in packages)
    codebase.attributes.dependencies.extend(dep.to_dict() for dep in dependencies)


def get_package_and_deps(codebase, package_adder=add_to_package, strip_root=False, **kwargs):
    """
    Return a tuple of (Packages list, Dependency list) from the parsed package
    data present in the codebase files.package_data attributes.
    """
    packages = []
    dependencies = []

    seen_resource_paths = set()

    has_single_resource = codebase.has_single_resource
    # track resource ids that have been already processed
    for resource in codebase.walk(topdown=False):
        if not resource.package_data:
            continue

        if resource.path in seen_resource_paths:
            continue

        if TRACE:
            logger_debug('get_package_and_deps: location:', resource.location)

        for package_data in resource.package_data:
            try:
                package_data = PackageData.from_dict(mapping=package_data)

                if TRACE:
                    logger_debug('  get_package_and_deps: package_data:', package_data)

                # Find a handler for this package datasource to assemble collect
                # packages and deps
                handler = get_package_handler(package_data)
                if TRACE:
                    logger_debug('  get_package_and_deps: handler:', handler)

                items = handler.assemble(
                    package_data=package_data,
                    resource=resource,
                    codebase=codebase,
                    package_adder=package_adder,
                )

                for item in items:
                    if TRACE:
                        logger_debug('    get_package_and_deps: item:', item)

                    if isinstance(item, Package):
                        if strip_root and not has_single_resource:
                            item.datafile_paths = [
                                strip_first_path_segment(dfp)
                                for dfp in item.datafile_paths
                            ]
                        packages.append(item)

                    elif isinstance(item, Dependency):
                        if strip_root and not has_single_resource:
                            item.datafile_path = strip_first_path_segment(item.datafile_path)
                        dependencies.append(item)

                    elif isinstance(item, Resource):
                        seen_resource_paths.add(item.path)

                        if TRACE:
                            logger_debug(
                                '    get_package_and_deps: seen_resource_path:',
                                seen_resource_paths,
                            )

                    else:
                        raise Exception(f'Unknown package assembly item type: {item!r}')

            except Exception as e:
                import traceback
                msg = f'get_package_and_deps: Failed to assemble PackageData: {package_data}:\n'
                msg += traceback.format_exc()
                resource.scan_errors.append(msg)
                resource.save(codebase)

                if TRACE:
                    raise Exception(msg) from e

    return packages, dependencies
