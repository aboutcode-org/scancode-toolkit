
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
import posixpath
from packagedcode import go_mod
from packagedcode import models

"""
Handle Go packages including go.mod and go.sum files.
"""

# FIXME: !!improve how we handle packages names vs. subpath.
# we need to have shorter names and use subpath

# TODO: go.mod file does not contain version number.
# valid download url need version number
# CHECK: https://forum.golangbridge.org/t/url-to-download-package/19811

# TODO: use the LICENSE file convention!
# TODO: support "vendor" and "workspace" layouts

# Tracing flags
TRACE = False or os.environ.get("SCANCODE_DEBUG_PACKAGE", False)


# Tracing flags
def logger_debug(*args):
    pass


if TRACE:
    import logging
    import sys

    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(" ".join(isinstance(a, str) and a or repr(a) for a in args))



class BaseGoModuleHandler(models.DatafileHandler):

    @classmethod
    def assemble(cls, package_data, resource, codebase, package_adder):
        """
        Always use go.mod first then go.sum
        """

        if not codebase.has_single_resource:
            cls.resolve_local_replacements(
                package_data=package_data,
                resource=resource,
                codebase=codebase,
            )

        resource.package_data[0] = package_data.to_dict()

        yield from cls.assemble_from_many_datafiles(
            datafile_name_patterns=('go.mod', 'go.sum',),
            directory=resource.parent(codebase),
            codebase=codebase,
            package_adder=package_adder,
        )

    @classmethod
    def resolve_local_replacements(cls, package_data, resource, codebase):
        """
        Resolve local paths present in replace directives
        """

        local_replacements = package_data.extra_data.get('local_replacements', [])
        if not local_replacements: 
            logger_debug(f"resolve_local_replacements: No local replacements found")
            return

        base_dir = resource.parent(codebase)
        base_path = base_dir.path

        for idx, replacement in enumerate(local_replacements):
            local_path = replacement. get('local_path')
            if not local_path:
                logger_debug(f"resolve_local_replacements:  Skipping replacement {idx + 1} - no local_path found")
                continue

            full_path = posixpath.normpath(
                posixpath.join(base_path, local_path)
            )

            local_resource = codebase.get_resource(full_path)
            if not local_resource:
                logger_debug(f"resolve_local_replacements:  Resource not found at {full_path}")
                continue

            local_gomod = None
            for child in local_resource. children(codebase):
                if child.name == 'go.mod':
                    local_gomod = child
                    break

            if not local_gomod or not local_gomod. package_data:
                logger_debug(f"resolve_local_replacements: No go.mod or package_data found in {full_path}")
                continue

            try:
                local_pkg_dict = local_gomod.package_data[0]
                local_pkg_data = models.PackageData.from_dict(local_pkg_dict)
            except (IndexError, KeyError, TypeError) as e:
                logger_debug(f"resolve_local_replacements: Failed to parse package data:  {e}")
                continue

            if not local_pkg_data. purl:
                logger_debug(f"resolve_local_replacements: No purl found in local package data")
                continue

            resolved_dependency = models.DependentPackage(
                purl=local_pkg_data.purl,
                extracted_requirement=local_pkg_data.version or None,
                resolved_package=local_pkg_data.to_dict(),
                scope='require',
                is_runtime=True,
                is_optional=False,
                extra_data={
                    'replaces':  replacement.get('replaces'),
                    'resolved_from_local':  True,
                    'local_path': local_path,
                    'local_resolved_path': full_path,
                }
            )

            if not any(dep.purl == resolved_dependency.purl for dep in package_data.dependencies):
                package_data.dependencies.append(resolved_dependency)
                logger_debug(f"resolve_local_replacements: Added dependency: {resolved_dependency.purl}")
            else:
                logger_debug(f"resolve_local_replacements: Dependency already exists, skipping: {resolved_dependency. purl}")

class GoModHandler(BaseGoModuleHandler):
    datasource_id = 'go_mod'
    path_patterns = ('*/go.mod',)
    default_package_type = 'golang'
    default_primary_language = 'Go'
    description = 'Go modules file'
    documentation_url = 'https://go.dev/ref/mod'

    @classmethod
    def parse(cls, location, package_only=False):
        gomods = go_mod.parse_gomod(location)

        dependencies = []
        require = gomods.require or []
        for gomod in require:
            dependencies.append(
                models.DependentPackage(
                    purl=gomod.purl(include_version=True),
                    extracted_requirement=gomod.version,
                    scope='require',
                    is_runtime=True,
                    is_optional=False,
                    is_pinned=False,
                )
            )

        exclude = gomods.exclude or []
        for gomod in exclude:
            dependencies.append(
                models.DependentPackage(
                    purl=gomod.purl(include_version=True),
                    extracted_requirement=gomod.version,
                    scope='exclude',
                    is_runtime=True,
                    is_optional=False,
                    is_pinned=False,
                )
            )

        extra_data = {
            'local_replacements': gomods.local_replacements
        }

        name = gomods.name
        namespace = gomods.namespace

        homepage_url = f'https://pkg.go.dev/{gomods.namespace}/{gomods.name}'
        vcs_url = f'https://{gomods.namespace}/{gomods.name}.git'

        repository_homepage_url = None
        if namespace and name:
            repository_homepage_url = f'https://pkg.go.dev/{namespace}/{name}'

        package_data = dict(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            name=name,
            namespace=namespace,
            vcs_url=vcs_url,
            homepage_url=homepage_url,
            repository_homepage_url=repository_homepage_url,
            dependencies=dependencies,
            extra_data=extra_data if gomods.local_replacements else {},
            primary_language=cls.default_primary_language,
        )
        yield models.PackageData.from_data(package_data, package_only)


class GoSumHandler(BaseGoModuleHandler):
    datasource_id = 'go_sum'
    path_patterns = ('*/go.sum',)
    default_package_type = 'golang'
    default_primary_language = 'Go'
    description = 'Go module cheksums file'
    documentation_url = 'https://go.dev/ref/mod#go-sum-files'

    @classmethod
    def parse(cls, location, package_only=False):
        gosums = go_mod.parse_gosum(location)
        package_dependencies = []
        for gosum in gosums:
            package_dependencies.append(
                models.DependentPackage(
                    purl=gosum.purl(),
                    extracted_requirement=gosum.version,
                    scope='dependency',
                    is_runtime=True,
                    is_optional=False,
                    is_pinned=True,
                )
            )

        package_data = dict(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            dependencies=package_dependencies,
            primary_language=cls.default_primary_language,
        )
        yield models.PackageData.from_data(package_data, package_only)
