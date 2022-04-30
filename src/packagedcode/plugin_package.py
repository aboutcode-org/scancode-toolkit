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
import logging

from commoncode.cliutils import PluggableCommandLineOption
from commoncode.cliutils import DOC_GROUP
from commoncode.cliutils import SCAN_GROUP
from commoncode.resource import Resource
from plugincode.scan import scan_impl
from plugincode.scan import ScanPlugin

from packagedcode import get_package_handler
from packagedcode.models import Dependency
from packagedcode.models import Package
from packagedcode.models import PackageData

TRACE = os.environ.get('SCANCODE_DEBUG_PACKAGE', False)


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

    from packagedcode import PACKAGE_DATAFILE_HANDLERS

    for cls in sorted(
        PACKAGE_DATAFILE_HANDLERS, key=lambda pc: (pc.default_package_type or '', pc.datasource_id)
    ):
        pp = ', '.join(repr(p) for p in cls.path_patterns)
        click.echo('--------------------------------------------')
        click.echo(f'Package type:  {cls.default_package_type}')
        if cls.datasource_id is None:
            raise Exception(cls)
        click.echo(f'  datasource_id:     {cls.datasource_id}')
        click.echo(f'  documentation URL: {cls.documentation_url}')
        click.echo(f'  primary language:  {cls.default_primary_language}')
        click.echo(f'  description:       {cls.description}')
        click.echo(f'  path_patterns:    {pp}')
    ctx.exit()


@scan_impl
class PackageScanner(ScanPlugin):
    """
    Scan a Resource for Package data and report these as "package_data" at the
    file level. Then create "packages" from these "package_data" at the top
    level.
    """

    codebase_attributes = dict(
        # a list of dependencies
        dependencies=attr.ib(default=attr.Factory(list), repr=False),
        # a list of packages
        packages=attr.ib(default=attr.Factory(list), repr=False),
    )
    resource_attributes = dict(
        # a list of package data
        package_data=attr.ib(default=attr.Factory(list), repr=False),
        # a list of purls with UUID that a file belongs to
        for_packages=attr.ib(default=attr.Factory(list), repr=False),
    )

    required_plugins = ['scan:licenses']

    sort_order = 6

    options = [
        PluggableCommandLineOption(
            (
                '-p',
                '--package',
            ),
            is_flag=True,
            default=False,
            help='Scan <input> for package and dependency manifests, lockfiles and related data.',
            help_group=SCAN_GROUP,
            sort_order=20,
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

    def is_enabled(self, package, **kwargs):
        return package

    def get_scanner(self, **kwargs):
        """
        Return a scanner callable to scan a file for package data.
        """
        from scancode.api import get_package_data

        return get_package_data

    def process_codebase(self, codebase, **kwargs):
        """
        Populate the ``codebase`` top level ``packages`` and ``dependencies``
        with package and dependency instances, assembling parsed package data
        from one or more datafiles as needed.
        """
        create_package_and_deps(codebase, **kwargs)


def create_package_and_deps(codebase, **kwargs):
    """
    Create and save top-level Package and Dependency from the parsed
    package data present in the codebase.
    """
    # track resource ids that have been already processed
    seen_resource_ids = set()
    dependencies_top_level = []
    packages_top_level = []

    for resource in codebase.walk(topdown=False):
        if not resource.package_data:
            continue

        if resource.rid in seen_resource_ids:
            continue

        if TRACE:
            logger_debug('create_package_and_deps: location:', resource.location)

        for package_data in resource.package_data:
            try:
                package_data = PackageData.from_dict(package_data)

                if TRACE:
                    logger_debug('  create_package_and_deps: package_data:', package_data)

                # Find a handler for this package datasource to assemble collect
                # packages and deps
                handler = get_package_handler(package_data)
                if TRACE:
                    logger_debug('  create_package_and_deps: handler:', handler)
                click.echo(f'  create_package_and_deps: handler: {handler}')
 
                items = handler.assemble(
                    package_data=package_data,
                    resource=resource,
                    codebase=codebase,
                )

                for item in items:
                    if TRACE:
                        logger_debug('    create_package_and_deps: item:', item)

                    if isinstance(item, Package):
                        packages_top_level.append(item)

                    elif isinstance(item, Dependency):
                        dependencies_top_level.append(item)

                    elif isinstance(item, Resource):
                        seen_resource_ids.add(item.rid)
                        if TRACE:
                            logger_debug(
                                '    create_package_and_deps: seen_resource_ids:',
                                seen_resource_ids,
                            )

                    else:
                        raise Exception(f'Unknown package assembly item type: {item!r}')

            except Exception as e:
                msg = f'create_package_and_deps: Failed to assemble PackageData: {package_data}: \n {e}'
                resource.scan_errors.append(msg)
                resource.save(codebase)

                if TRACE:
                    import traceback
                    msg += traceback.format_exc()
                    raise Exception(msg) from e

    codebase.attributes.packages.extend(pkg.to_dict() for pkg in packages_top_level)
    codebase.attributes.dependencies.extend(dep.to_dict() for dep in dependencies_top_level)
