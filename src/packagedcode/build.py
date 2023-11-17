#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
import logging
import ast
from collections import defaultdict

from commoncode import fileutils

from licensedcode.cache import build_spdx_license_expression
from licensedcode.cache import get_cache
from licensedcode.tokenize import query_tokenizer
from licensedcode.detection import detect_licenses
from licensedcode.detection import get_unknown_license_detection
from packagedcode import models
from packagedcode.licensing import get_mapping_and_expression_from_detections

"""
Detect as Packages common build tools and environment such as Make, Autotools,
Buck, Bazel, Pants, etc.
"""

TRACE = os.environ.get('SCANCODE_DEBUG_PACKAGE', False)


def logger_debug(*args):
    pass


logger = logging.getLogger(__name__)

if TRACE:
    import sys
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(
            ' '.join(isinstance(a, str) and a or repr(a) for a in args)
        )


class AutotoolsConfigureHandler(models.DatafileHandler):
    datasource_id = 'autotools_configure'
    path_patterns = ('*/configure', '*/configure.ac',)
    default_package_type = 'autotools'
    description = 'Autotools configure script'
    documentation_url = 'https://www.gnu.org/software/automake/'

    @classmethod
    def parse(cls, location):
        # we use the parent directory as a package name
        name = fileutils.file_name(fileutils.parent_directory(location))
        # we could use checksums as version in the future
        version = None

        # there is an optional array of license file names in targets that we could use
        # declared_license = None

        # there are dependencies we could use
        # dependencies = []

        yield models.PackageData(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            name=name,
            version=version,
        )

    @classmethod
    def assign_package_to_resources(cls, package, resource, codebase, package_adder):
        models.DatafileHandler.assign_package_to_parent_tree(
            package=package,
            resource=resource,
            codebase=codebase,
            package_adder=package_adder,
        )


def check_rule_name_ending(rule_name, starlark_rule_types=('binary', 'library')):
    """
    Return True if `rule_name` ends with a rule type from `starlark_rule_types`
    Return False otherwise
    """
    for rule_type in starlark_rule_types:
        if rule_name.endswith(rule_type):
            return True
    return False


class BaseStarlarkManifestHandler(models.DatafileHandler):
    """
    Common base class for Bazel and Buck that both use the Starlark syntax.
    """

    @classmethod
    def assemble(cls, package_data, resource, codebase, package_adder):
        """
        Given a ``package_data`` PackageData found in the ``resource`` datafile
        of the ``codebase``, assemble and yield a Package with its files and
        dependencies from one or more datafiles.
        """
        # do we have enough to create a package?
        if package_data.purl:
            package = models.Package.from_package_data(
                package_data=package_data,
                datafile_path=resource.path,
            )

            if TRACE:
                logger_debug(f"BaseStarlarkManifestHandler.assemble: package_data: {package_data.to_dict()}")

            package.license_detections, package.declared_license_expression = \
                get_license_detections_and_expression(
                    package=package_data,
                    resource=resource,
                    codebase=codebase,
                )
            if package.declared_license_expression:
                package.declared_license_expression_spdx = str(build_spdx_license_expression(
                    license_expression=package.declared_license_expression,
                    licensing=get_cache().licensing,
                ))

            cls.assign_package_to_resources(
                package=package,
                resource=resource,
                codebase=codebase,
                package_adder=package_adder
            )

            yield package


        # we yield this as we do not want this further processed
        yield resource

    @classmethod
    def parse(cls, location):

        # Thanks to Starlark being a Python dialect, we can use `ast` to parse it
        with open(location, 'rb') as f:
            tree = ast.parse(f.read())

        build_rules = defaultdict(list)
        for statement in tree.body:
            # We only care about function calls or assignments to functions whose
            # names ends with one of the strings in `rule_types`
            if (
                isinstance(statement, ast.Expr)
                or isinstance(statement, ast.Call)
                or isinstance(statement, ast.Assign)
                and isinstance(statement.value, ast.Call)
                and isinstance(statement.value.func, ast.Name)
            ):
                rule_name = statement.value.func.id
                # Ensure that we are only creating packages from the proper
                # build rules
                if not check_rule_name_ending(rule_name):
                    continue
                # Process the rule arguments
                args = {}
                for kw in statement.value.keywords:
                    arg_name = kw.arg
                    if isinstance(kw.value, ast.Str):
                        args[arg_name] = kw.value.s

                    if isinstance(kw.value, ast.List):
                        # We collect the elements of a list if the element is
                        # not a function call
                        args[arg_name] = [
                            elt.s for elt in kw.value.elts
                            if not isinstance(elt, ast.Call)
                        ]
                if args:
                    build_rules[rule_name].append(args)

        if build_rules:
            for rule_name, rule_instances_args in build_rules.items():
                for args in rule_instances_args:
                    name = args.get('name')

                    # FIXME: we could still return partial package data
                    if not name:
                        continue

                    license_files = args.get('licenses')

                    if TRACE:
                        logger_debug(f"build: parse: license_files: {license_files}")

                    package_data = models.PackageData(
                        datasource_id=cls.datasource_id,
                        type=cls.default_package_type,
                        name=name,
                    )

                    package_data.extracted_license_statement = license_files
                    yield package_data

        else:
            # If we don't find anything in the pkgdata file, we yield a Package
            # with the parent directory as the name
            yield models.PackageData(
                datasource_id=cls.datasource_id,
                type=cls.default_package_type,
                name=fileutils.file_name(fileutils.parent_directory(location))
            )

    @classmethod
    def assign_package_to_resources(cls, package, resource, codebase, package_adder, skip_name=None):
        package_uid = package.package_uid
        if not package_uid:
            return
        parent = resource.parent(codebase)
        for res in walk_build(resource=parent, codebase=codebase, skip_name=skip_name):
            package_adder(package_uid, res, codebase)


def walk_build(resource, codebase, skip_name):
    """
    Walk the ``codebase`` starting at ``resource`` and stop when ``skip_name``
    is found in a subdirectory. The idea is to avoid walking recursively sub-
    directories that contain a build script such as a Bazel or BUCK file as they
    define their own file tree.
    """
    for child in resource.children(codebase):
        yield child
        if not child.is_dir:
            continue
        if not any(r.name == skip_name for r in child.children(codebase)):
            for subchild in walk_build(child, codebase, skip_name=skip_name):
                yield subchild


def get_license_detections_and_expression(package, resource, codebase):
    """
    Return a normalized license expression string detected from a list of
    declared license items.
    """
    license_detections = []

    declared_licenses = package.extracted_license_statement
    if not declared_licenses:
        return license_detections, None

    if not isinstance(declared_licenses, str):
        declared_licenses = repr(declared_licenses)

    declared_licenses = list(query_tokenizer(declared_licenses))
    declared_licenses = set(declared_licenses)

    if TRACE:
        logger_debug(
            f"build: get_license_detections_and_expression:"
            f"declared_licenses: {declared_licenses}"
        )
        logger_debug(
            f"build: get_license_detections_and_expression:"
            f"type(declared_licenses): {type(declared_licenses)}"
        )

    parent = resource.parent(codebase)
    # FIXME: we should be able to get the path relatively to the ABOUT file resource
    for child in parent.children(codebase):
        if child.name.lower() in declared_licenses:
            detections = detect_licenses(location=child.location)
            if TRACE:
                logger_debug(
                    f"build: get_license_detections_and_expression:"
                    f"detections: {detections}"
                )

            if not detections:
                license_detections.append(
                    get_unknown_license_detection(declared_licenses)
                )
            else:
                license_detections.extend(detections)

    return get_mapping_and_expression_from_detections(
        license_detections=license_detections
    )


class BazelBuildHandler(BaseStarlarkManifestHandler):
    datasource_id = 'bazel_build'
    path_patterns = ('*/BUILD',)
    default_package_type = 'bazel'
    description = 'Bazel BUILD'
    documentation_url = 'https://bazel.build/'

    @classmethod
    def assign_package_to_resources(cls, package, resource, codebase, package_adder, skip_name='BUILD'):
        return super().assign_package_to_resources(
            package=package,
            resource=resource,
            codebase=codebase,
            package_adder=package_adder,
            skip_name=skip_name,
        )


class BuckPackageHandler(BaseStarlarkManifestHandler):
    datasource_id = 'buck_file'
    path_patterns = ('*/BUCK',)
    default_package_type = 'buck'
    description = 'Buck file'
    documentation_url = 'https://buck.build/'

    @classmethod
    def assign_package_to_resources(cls, package, resource, codebase, package_adder, skip_name='BUCK'):
        return super().assign_package_to_resources(
            package=package,
            resource=resource,
            codebase=codebase,
            package_adder=package_adder,
            skip_name=skip_name,
        )


class BuckMetadataBzlHandler(BaseStarlarkManifestHandler):
    datasource_id = 'buck_metadata'
    path_patterns = ('*/METADATA.bzl',)
    default_package_type = 'buck'
    description = 'Buck metadata file'
    documentation_url = 'https://buck.build/'

    @classmethod
    def parse(cls, location):

        with open(location, 'rb') as f:
            tree = ast.parse(f.read())

        metadata_fields = {}
        for statement in tree.body:
            if not (hasattr(statement, 'targets') and isinstance(statement, ast.Assign)):
                continue

            # We are looking for a dictionary assigned to the variable `METADATA`
            for target in statement.targets:
                if not (target.id == 'METADATA' and isinstance(statement.value, ast.Dict)):
                    continue
                # Once we find the dictionary assignment, get and store its contents
                statement_keys = statement.value.keys
                statement_values = statement.value.values
                for statement_k, statement_v in zip(statement_keys, statement_values):
                    if isinstance(statement_k, ast.Str):
                        key_name = statement_k.s
                    # The list values in a `METADATA.bzl` file seem to only contain strings
                    if isinstance(statement_v, ast.List):
                        value = []
                        for e in statement_v.elts:
                            if not isinstance(e, ast.Str):
                                continue
                            value.append(e.s)
                    if isinstance(statement_v, (ast.Str, ast.Constant)):
                        value = statement_v.s
                    metadata_fields[key_name] = value

        parties = []
        maintainers = metadata_fields.get('maintainers', []) or []
        for maintainer in maintainers:
            parties.append(
                models.Party(
                    type=models.party_org,
                    name=maintainer,
                    role='maintainer',
                )
            )

        if (
            'upstream_type'
            and 'name'
            and 'version'
            and 'licenses'
            and 'upstream_address'
            in metadata_fields
        ):
            # TODO: Create function that determines package type from download URL,
            # then create a package of that package type from the metadata info
            yield models.PackageData(
                datasource_id=cls.datasource_id,
                type=metadata_fields.get('upstream_type', cls.default_package_type),
                name=metadata_fields.get('name'),
                version=metadata_fields.get('version'),
                extracted_license_statement=metadata_fields.get('licenses', []),
                parties=parties,
                homepage_url=metadata_fields.get('upstream_address', ''),
                # TODO: Store 'upstream_hash` somewhere
            )

        if (
            'package_type'
            and 'name'
            and 'version'
            and 'license_expression'
            and 'homepage_url'
            and 'download_url'
            and 'vcs_url'
            and 'download_archive_sha1'
            and 'vcs_commit_hash'
            in metadata_fields
        ):
            yield models.PackageData(
                datasource_id=cls.datasource_id,
                type=metadata_fields.get('package_type', cls.default_package_type),
                name=metadata_fields.get('name'),
                version=metadata_fields.get('version'),
                extracted_license_statement=metadata_fields.get('license_expression', ''),
                parties=parties,
                homepage_url=metadata_fields.get('homepage_url', ''),
                download_url=metadata_fields.get('download_url', ''),
                vcs_url=metadata_fields.get('vcs_url', ''),
                sha1=metadata_fields.get('download_archive_sha1', ''),
                extra_data=dict(vcs_commit_hash=metadata_fields.get('vcs_commit_hash', ''))
            )

    @classmethod
    def assign_package_to_resources(cls, package, resource, codebase, package_adder):
        models.DatafileHandler.assign_package_to_parent_tree(
            package_=package,
            resource=resource,
            codebase=codebase,
            package_adder=package_adder,
        )
