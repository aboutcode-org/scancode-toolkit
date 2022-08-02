
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

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


class BaseGoModuleHandler(models.DatafileHandler):

    @classmethod
    def assemble(cls, package_data, resource, codebase, package_adder):
        """
        Always use go.mod first then go.sum
        """
        yield from cls.assemble_from_many_datafiles(
            datafile_name_patterns=('go.mod', 'go.sum',),
            directory=resource.parent(codebase),
            codebase=codebase,
            package_adder=package_adder,
        )


class GoModHandler(BaseGoModuleHandler):
    datasource_id = 'go_mod'
    path_patterns = ('*/go.mod',)
    default_package_type = 'golang'
    default_primary_language = 'Go'
    description = 'Go modules file'
    documentation_url = 'https://go.dev/ref/mod'

    @classmethod
    def parse(cls, location):
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
                    is_resolved=False,
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
                    is_resolved=False,
                )
            )

        name = gomods.name
        namespace = gomods.namespace

        homepage_url = f'https://pkg.go.dev/{gomods.namespace}/{gomods.name}'
        vcs_url = f'https://{gomods.namespace}/{gomods.name}.git'

        repository_homepage_url = None
        if namespace and name:
            repository_homepage_url = f'https://pkg.go.dev/{namespace}/{name}'

        yield models.PackageData(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            name=name,
            namespace=namespace,
            vcs_url=vcs_url,
            homepage_url=homepage_url,
            repository_homepage_url=repository_homepage_url,
            dependencies=dependencies,
            primary_language=cls.default_primary_language,
        )


class GoSumHandler(BaseGoModuleHandler):
    datasource_id = 'go_sum'
    path_patterns = ('*/go.sum',)
    default_package_type = 'golang'
    default_primary_language = 'Go'
    description = 'Go module cheksums file'
    documentation_url = 'https://go.dev/ref/mod#go-sum-files'

    @classmethod
    def parse(cls, location):
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
                    is_resolved=True,
                )
            )

        yield models.PackageData(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            dependencies=package_dependencies,
            primary_language=cls.default_primary_language,
        )
