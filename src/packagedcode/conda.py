#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import io
import json

import saneyaml
from packageurl import PackageURL

from packagedcode import models
from packagedcode.pypi import BaseDependencyFileHandler
from dparse2.parser import parse_requirement_line

"""
Handle Conda manifests and metadata, see https://docs.conda.io/en/latest/
https://docs.conda.io/projects/conda-build/en/latest/resources/define-metadata.html

See https://repo.continuum.io/pkgs/free for examples.
"""


class CondaBaseHandler(models.DatafileHandler):
    """
    Assemble package data and files present in conda manifests present in the
    usual structure of a conda installation. Here the manifests which are
    assembled together are:
    - Conda metadata JSON     (CondaMetaJsonHandler)
    - Conda meta.yaml recipe  (CondaMetaYamlHandler)

    Example paths for these manifests:
    /opt/conda/conda-meta/requests-2.32.3-py312h06a4308_1.json
    /opt/conda/pkgs/requests-2.32.3-py312h06a4308_1/info/recipe/meta.yaml
    """

    @classmethod
    def assemble(cls, package_data, resource, codebase, package_adder=models.add_to_package):

        if codebase.has_single_resource:
            yield from models.DatafileHandler.assemble(package_data, resource, codebase, package_adder)
            return

        # We do not have any package data detected here
        if not resource.package_data:
            return

        # If this is a Conda meta.yaml, try to find the corresponding metadata JSON
        # and if present, run assembly on the metadata resource
        if CondaMetaYamlHandler.is_datafile(resource.location):
            conda_meta_json = cls.find_conda_meta_json_resource(resource, codebase)
            if conda_meta_json:
                package_data_meta_json, = conda_meta_json.package_data
                yield from cls.assemble(
                    package_data=package_data_meta_json,
                    resource=conda_meta_json,
                    codebase=codebase,
                    package_adder=package_adder,
                )

            # corresponding metadata JSON does not exist, so handle this meta.yaml
            else:
                yield from cls.assemble_from_meta_yaml_only(
                    package_data=package_data,
                    resource=resource,
                    codebase=codebase,
                    package_adder=package_adder,
                )

            return

        if not package_data.purl:
            yield resource
            return

        package = models.Package.from_package_data(
            package_data=package_data,
            datafile_path=resource.path,
        )
        yield from cls.get_and_assmeble_from_meta_yaml(
            package=package,
            resource=resource,
            codebase=codebase,
            package_adder=package_adder,
        )

        package.populate_license_fields()
        yield package

        cls.assign_package_to_resources(
            package=package,
            resource=resource,
            codebase=codebase,
            package_adder=package_adder,
        )

        # we yield this as we do not want this further processed
        yield resource

        cls.assign_packages_to_resources_from_metadata_json(
            package=package,
            package_data=package_data,
            resource=resource,
            codebase=codebase,
            package_adder=package_adder,
        )

    @classmethod
    def assign_packages_to_resources_from_metadata_json(
        cls,
        package,
        package_data,
        resource,
        codebase,
        package_adder=models.add_to_package,
    ):
        """
        Get the file paths present in the `package_data` of a metadata JSON `resource`
        and assign them to the `package` created from the manifest.
        """
        extracted_package_dir = package_data.extra_data.get('extracted_package_dir')
        files = package_data.extra_data.get('files')

        if not extracted_package_dir or not files:
            return

        conda_metadata_dir = resource.parent(codebase)
        if not conda_metadata_dir:
            return

        conda_root_dir = conda_metadata_dir.parent(codebase)
        if not conda_root_dir:
            return
    
        root_path_segment, _, package_dir = extracted_package_dir.rpartition("/pkgs/")
        if not conda_root_dir.path.endswith(root_path_segment):
            return

        package_dir_path = f"{conda_root_dir.path}/pkgs/{package_dir}"
        package_dir_resource = codebase.get_resource(path=package_dir_path)
        if package_dir_resource:
            cls.assign_package_to_resources(
                package=package,
                resource=package_dir_resource,
                codebase=codebase,
                package_adder=package_adder,
            )

        conda_package_path = f"{conda_root_dir.path}/pkgs/{package_dir}.conda"
        conda_package_resource = codebase.get_resource(path=conda_package_path)
        if conda_package_resource:
            cls.assign_package_to_resources(
                package=package,
                resource=conda_package_resource,
                codebase=codebase,
                package_adder=package_adder,
            )

        for file_path in files:
            full_file_path = f"{conda_root_dir.path}/{file_path}"
            file_resource = codebase.get_resource(path=full_file_path)
            if file_resource:
                cls.assign_package_to_resources(
                    package=package,
                    resource=file_resource,
                    codebase=codebase,
                    package_adder=package_adder,
                )

    @classmethod
    def get_and_assmeble_from_meta_yaml(cls, package, resource, codebase, package_adder=models.add_to_package):
        """
        For a conda metadata JSON `resource`, try to find the corresponding meta.yaml and
        update the `package` from it. Also yield dependencies present in the meta.yaml,
        and the `resource` to complete assembling from this manifest.
        """
        conda_meta_yaml = cls.find_conda_meta_yaml_resource(resource, codebase)

        if conda_meta_yaml:
            conda_meta_yaml_package_data, = conda_meta_yaml.package_data
            package.update(
                package_data=conda_meta_yaml_package_data,
                datafile_path=conda_meta_yaml.path,
            )
            cls.assign_package_to_resources(
                package=package,
                resource=conda_meta_yaml,
                codebase=codebase,
                package_adder=package_adder,
            )
            meta_yaml_package_data = models.PackageData.from_dict(conda_meta_yaml_package_data)
            if meta_yaml_package_data.dependencies:
                yield from models.Dependency.from_dependent_packages(
                    dependent_packages=meta_yaml_package_data.dependencies,
                    datafile_path=conda_meta_yaml.path,
                    datasource_id=meta_yaml_package_data.datasource_id,
                    package_uid=package.package_uid,
                )

            yield conda_meta_yaml

    @classmethod
    def assemble_from_meta_yaml_only(cls, package_data, resource, codebase, package_adder=models.add_to_package):
        """
        Assemble and yeild package, dependencies and the meta YAML `resource` from
        it's `package_data`, and also assign resources to the package.
        """
        if not package_data.purl:
            return

        package = models.Package.from_package_data(
            package_data=package_data,
            datafile_path=resource.path,
        )
        package.populate_license_fields()
        yield package

        dependent_packages = package_data.dependencies
        if dependent_packages:
            yield from models.Dependency.from_dependent_packages(
                dependent_packages=dependent_packages,
                datafile_path=resource.path,
                datasource_id=package_data.datasource_id,
                package_uid=package.package_uid,
            )

        CondaMetaYamlHandler.assign_package_to_resources(
            package=package,
            resource=resource,
            codebase=codebase,
            package_adder=package_adder,
        )
        yield resource

    @classmethod
    def check_valid_packages_dir_name(cls, package_dir_resource, resource, codebase):
        """
        Return the name of the `package_dir_resource`, if it is valid, i.e.
        the package (name, version) data present in `resource` matches the
        directory name, and the package directory is present in it's usual
        location in a conda installation.
        """
        package_dir_parent = package_dir_resource.parent(codebase)

        meta_yaml_package_data, = resource.package_data
        name = meta_yaml_package_data.get("name")
        version = meta_yaml_package_data.get("version")
        if f"{name}-{version}" in package_dir_resource.name and (
            package_dir_parent and "pkgs" in package_dir_parent.name
        ):
            return package_dir_resource.name

    @classmethod
    def find_conda_meta_json_resource(cls, resource, codebase):
        """
        Given a resource for a conda meta.yaml resource, find if it has any
        corresponding metadata JSON located inside the conda-meta/ directory,
        and return the resource if they exist, else return None.
        """
        package_dir_resource = CondaMetaYamlHandler.get_conda_root(resource, codebase)
        if not package_dir_resource or not resource.package_data:
            return

        package_dir_name = cls.check_valid_packages_dir_name(
            package_dir_resource=package_dir_resource,
            resource=resource,
            codebase=codebase,
        )
        if not package_dir_name:
            return

        root_resource = package_dir_resource.parent(codebase).parent(codebase)
        if not root_resource:
            return

        root_resource_path = root_resource.path
        conda_meta_path = f"{root_resource_path}/conda-meta/{package_dir_name}.json"
        conda_meta_resource = codebase.get_resource(path=conda_meta_path)

        if conda_meta_resource and conda_meta_resource.package_data:
            return conda_meta_resource

    @classmethod
    def find_conda_meta_yaml_resource(cls, resource, codebase):
        """
        Given a resource for a metadata JSON located inside the conda-meta/
        directory, find if it has any corresponding conda meta.yaml, and return
        the resource if they exist, else return None.
        """
        package_dir_name, _json, _ = resource.name.rpartition(".json")
        parent_resource = resource.parent(codebase)
        if not parent_resource and not parent_resource.name == "conda-meta":
            return

        root_resource = parent_resource.parent(codebase)
        if not root_resource:
            return

        root_resource_path = root_resource.path
        package_dir_path = f"{root_resource_path}/pkgs/{package_dir_name}/"
        package_dir_resource = codebase.get_resource(path=package_dir_path)
        if not package_dir_resource:
            return

        meta_yaml_path = f"{package_dir_path}info/recipe/meta.yaml"
        meta_yaml_resource = codebase.get_resource(path=meta_yaml_path)
        if meta_yaml_resource and meta_yaml_resource.package_data:
            return meta_yaml_resource


class CondaMetaJsonHandler(CondaBaseHandler):
    datasource_id = 'conda_meta_json'
    path_patterns = ('*conda-meta/*.json',)
    default_package_type = 'conda'
    default_primary_language = 'Python'
    description = 'Conda metadata JSON in rootfs'
    documentation_url = 'https://docs.conda.io/'

    @classmethod
    def parse(cls, location, package_only=False):
        with io.open(location, encoding='utf-8') as loc:
            conda_metadata = json.load(loc)

        name = conda_metadata.get('name')
        version = conda_metadata.get('version')
        extracted_license_statement = conda_metadata.get('license')
        download_url = conda_metadata.get('url')

        extra_data_fields = ['requested_spec', 'channel']
        package_file_fields = ['extracted_package_dir', 'files', 'package_tarball_full_path']
        other_package_fields = ['size', 'md5', 'sha256']

        extra_data = {}
        for metadata_field in extra_data_fields + package_file_fields:
            extra_data[metadata_field] = conda_metadata.get(metadata_field)

        package_data = dict(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            name=name,
            version=version,
            extracted_license_statement=extracted_license_statement,
            download_url=download_url,
            extra_data=extra_data,
        )
        for package_field in other_package_fields:
            package_data[package_field] = conda_metadata.get(package_field)
        yield models.PackageData.from_data(package_data, package_only)


class CondaYamlHandler(BaseDependencyFileHandler):
    datasource_id = 'conda_yaml'
    path_patterns = ('*conda*.yaml', '*env*.yaml', '*environment*.yaml')
    default_package_type = 'conda'
    default_primary_language = 'Python'
    description = 'Conda yaml manifest'
    documentation_url = 'https://docs.conda.io/'

    @classmethod
    def parse(cls, location, package_only=False):
        with open(location) as fi:
            conda_data = saneyaml.load(fi.read())
        dependencies = get_conda_yaml_dependencies(conda_data=conda_data)
        name = conda_data.get('name')
        extra_data = {}
        channels = conda_data.get('channels')
        if channels:
            extra_data['channels'] = channels
        if name or dependencies:
            package_data = dict(
                datasource_id=cls.datasource_id,
                type=cls.default_package_type,
                name=name,
                primary_language=cls.default_primary_language,
                dependencies=dependencies,
                extra_data=extra_data,
                is_private=True,
            )
            yield models.PackageData.from_data(package_data, package_only)


class CondaMetaYamlHandler(CondaBaseHandler):
    datasource_id = 'conda_meta_yaml'
    default_package_type = 'conda'
    path_patterns = ('*/meta.yaml',)
    description = 'Conda meta.yml manifest'
    documentation_url = 'https://docs.conda.io/'

    @classmethod
    def get_conda_root(cls, resource, codebase):
        """
        Return a root Resource given a meta.yaml ``resource``.
        """
        if not resource:
            return

        # the root is either the parent or further up for yaml stored under
        # an "info" dir. We support extractcode extraction.
        # in a source repo it would be in <repo>/conda.recipe/meta.yaml
        paths = (
            'info/recipe.tar-extract/recipe/meta.yaml',
            'info/recipe/recipe/meta.yaml',
            'conda.recipe/meta.yaml',
            'info/recipe/meta.yaml',
        )
        res = resource
        for pth in paths:
            if not res.path.endswith(pth):
                continue
            for _seg in pth.split('/'):
                res = res.parent(codebase)
                if not res:
                    break

            return res

        return resource.parent(codebase)

    @classmethod
    def assign_package_to_resources(cls, package, resource, codebase, package_adder):
        return models.DatafileHandler.assign_package_to_resources(
            package=package,
            resource=cls.get_conda_root(resource, codebase),
            codebase=codebase,
            package_adder=package_adder,
        )

    @classmethod
    def parse(cls, location, package_only=False):
        metayaml = get_meta_yaml_data(location)
        package_element = metayaml.get('package') or {}
        package_name = package_element.get('name')
        package_version = package_element.get('version')

        # FIXME: source is source, not download
        source = metayaml.get('source') or {}
        download_url = source.get('url')
        sha256 = source.get('sha256')

        about = metayaml.get('about') or {}
        homepage_url = about.get('home')
        extracted_license_statement = about.get('license')
        description = about.get('summary')
        vcs_url = about.get('dev_url')

        dependencies = []
        extra_data = {}
        requirements = metayaml.get('requirements') or {}
        for scope, reqs in requirements.items():
            # requirements format is like:
            # (u'run', [u'mccortex ==1.0', u'nextflow ==19.01.0', u'cortexpy
            # ==0.45.7', u'kallisto ==0.44.0', u'bwa', u'pandas',
            # u'progressbar2', u'python >=3.6'])])
            for req in reqs:
                name, _, requirement = req.partition(" ")
                version = None
                if requirement.startswith("=="):
                    _, version = requirement.split("==") 

                # requirements may have namespace, version too
                # - conda-forge::numpy=1.15.4
                namespace = None
                if "::" in name:
                    namespace, name = name.split("::")

                is_pinned = False
                if "=" in name:
                    name, version = name.split("=")
                    is_pinned = True
                    requirement = f"={version}"

                if name in ('pip', 'python'):
                    if not scope in extra_data:
                        extra_data[scope] = [req]
                    else:
                        extra_data[scope].append(req)
                    continue

                purl = PackageURL(
                    type=cls.default_package_type,
                    name=name,
                    namespace=namespace,
                    version=version,
                )
                if "run" in scope:
                    is_runtime = True
                    is_optional = False
                else:
                    is_runtime = False
                    is_optional = True

                dependencies.append(
                    models.DependentPackage(
                        purl=purl.to_string(),
                        extracted_requirement=requirement,
                        scope=scope,
                        is_runtime=is_runtime,
                        is_optional=is_optional,
                        is_pinned=is_pinned,
                        is_direct=True,
                    )
                )

        package_data = dict(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            name=package_name,
            version=package_version,
            download_url=download_url,
            homepage_url=homepage_url,
            vcs_url=vcs_url,
            description=description,
            sha256=sha256,
            extracted_license_statement=extracted_license_statement,
            dependencies=dependencies,
            extra_data=extra_data,
        )
        yield models.PackageData.from_data(package_data, package_only)


def get_conda_yaml_dependencies(conda_data):
    """
    Return a list of DependentPackage mappins from conda and pypi
    dependencies present in a `conda_data` mapping.
    """
    dependencies = conda_data.get('dependencies') or []
    deps = []
    for dep in dependencies:
        if isinstance(dep, str):
            namespace = None
            specs = None
            is_pinned = False

            if "::" in dep:
                namespace, dep = dep.split("::")
                if "/" in namespace or ":" in namespace:
                    namespace = None

            req = parse_requirement_line(dep)
            if req:
                name = req.name
                version = None

                specs = str(req.specs)
                if '==' in specs:
                    version = specs.replace('==','')
                    is_pinned = True
                purl = PackageURL(type='pypi', name=name, version=version)
            else:
                if "=" in dep:
                    dep, version = dep.split("=")
                    is_pinned = True
                    specs = f"={version}"

                purl = PackageURL(
                    type='conda',
                    namespace=namespace,
                    name=dep,
                    version=version,
                )

            if purl.name in ('pip', 'python'):
                continue

            deps.append(
                models.DependentPackage(
                    purl=purl.to_string(),
                    extracted_requirement=specs,
                    scope='dependencies',
                    is_runtime=True,
                    is_optional=False,
                    is_pinned=is_pinned,
                    is_direct=True,
                ).to_dict()
            )

        elif isinstance(dep, dict):
            for line in dep.get('pip', []):
                req = parse_requirement_line(line)
                if req:
                    name = req.name
                    version = None
                    is_pinned = False
                    specs = str(req.specs)
                    if '==' in specs:
                        version = specs.replace('==','')
                        is_pinned = True
                    purl = PackageURL(type='pypi', name=name, version=version)
                    deps.append(
                        models.DependentPackage(
                            purl=purl.to_string(),
                            extracted_requirement=specs,
                            scope='dependencies',
                            is_runtime=True,
                            is_optional=False,
                            is_pinned=is_pinned,
                            is_direct=True,
                        ).to_dict()
                    )

    return deps


def get_meta_yaml_data(location):
    """
    Return a mapping of conda metadata loaded from a meta.yaml files. The format
    support Jinja-based templating and we try a crude resolution of variables
    before loading the data as YAML.
    """
    # FIXME: use Jinja to process these
    variables = get_variables(location)
    yaml_lines = []
    with io.open(location, encoding='utf-8') as metayaml:
        for line in metayaml:
            if not line:
                continue
            pure_line = line.strip()
            if (
                pure_line.startswith('{%')
                and pure_line.endswith('%}')
                and '=' in pure_line
            ):
                continue

            # Replace the variable with the value
            if '{{' in line and '}}' in line:
                for variable, value in variables.items():
                    if "|lower" in line:
                        line = line.replace('{{ ' + variable + '|lower' + ' }}', value.lower())
                    else:
                        line = line.replace('{{ ' + variable + ' }}', value)
            yaml_lines.append(line)

    # Cleanup any remaining complex jinja template lines
    # as the yaml load fails otherwise for unresolved jinja
    cleaned_yaml_lines = [
        line
        for line in yaml_lines
        if not "{{" in line
    ]

    return saneyaml.load(''.join(cleaned_yaml_lines))


def get_variables(location):
    """
    Conda yaml will have variables defined at the beginning of the file, the
    idea is to parse it and return a dictionary of the variable and value

    For example:
    {% set version = "0.45.0" %}
    {% set sha256 = "bc7512f2eef785b037d836f4cc6faded457ac277f75c6e34eccd12da7c85258f" %}
    """
    result = {}
    with io.open(location, encoding='utf-8') as loc:
        for line in loc.readlines():
            if not line:
                continue
            line = line.strip()
            if line.startswith('{%') and line.endswith('%}') and '=' in line:
                line = line.lstrip('{%').rstrip('%}').strip().lstrip('set').lstrip()
                parts = line.split('=')
                result[parts[0].strip()] = parts[-1].strip().strip('"')
    return result
