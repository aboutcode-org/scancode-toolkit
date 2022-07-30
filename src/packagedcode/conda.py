#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import io

import saneyaml
from packageurl import PackageURL

from packagedcode import models
from packagedcode.pypi import BaseDependencyFileHandler

"""
Handle Conda manifests and metadata, see https://docs.conda.io/en/latest/
https://docs.conda.io/projects/conda-build/en/latest/resources/define-metadata.html

See https://repo.continuum.io/pkgs/free for examples.
"""

# TODO: there are likely other package data files for Conda
# TODO: report platform


class CondaYamlHandler(BaseDependencyFileHandler):
    # TODO: there are several other manifests worth adding
    datasource_id = 'conda_yaml'
    path_patterns = ('*conda.yaml', '*conda.yml',)
    default_package_type = 'pypi'
    default_primary_language = 'Python'
    description = 'Conda yaml manifest'
    documentation_url = 'https://docs.conda.io/'


class CondaMetaYamlHandler(models.DatafileHandler):
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
        # the root is either the parent or further up for yaml stored under
        # an "info" dir. We support extractcode extraction.
        # in a source repo it would be in <repo>/conda.recipe/meta.yaml
        paths = (
            'info/recipe.tar-extract/recipe/meta.yaml',
            'info/recipe/recipe/meta.yaml',
            'conda.recipe/meta.yaml',
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
    def parse(cls, location):
        metayaml = get_meta_yaml_data(location)
        package_element = metayaml.get('package') or {}
        name = package_element.get('name')
        if not name:
            return
        version = package_element.get('version')

        package = models.PackageData(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            name=name,
            version=version,
        )

        # FIXME: source is source, not download
        source = metayaml.get('source') or {}
        package.download_url = source.get('url')
        package.sha256 = source.get('sha256')

        about = metayaml.get('about') or {}
        package.homepage_url = about.get('home')
        package.declared_license = about.get('license')
        if package.declared_license:
            package.license_expression = cls.compute_normalized_license(package)
        package.description = about.get('summary')
        package.vcs_url = about.get('dev_url')

        requirements = metayaml.get('requirements') or {}
        for scope, reqs in requirements.items():
            # requirements format is like:
            # (u'run', [u'mccortex ==1.0', u'nextflow ==19.01.0', u'cortexpy
            # ==0.45.7', u'kallisto ==0.44.0', u'bwa', u'pandas',
            # u'progressbar2', u'python >=3.6'])])
            for req in reqs:
                name, _, requirement = req.partition(" ")
                purl = PackageURL(type=cls.default_package_type, name=name)
                package.dependencies.append(
                    models.DependentPackage(
                        purl=purl.to_string(),
                        extracted_requirement=requirement,
                        scope=scope,
                        is_runtime=True,
                        is_optional=False,
                    )
                )

        yield package


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
                    line = line.replace('{{ ' + variable + ' }}', value)
            yaml_lines.append(line)

    return saneyaml.load('\n'.join(yaml_lines))


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
