# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import ast
import io
import logging
import os

import saneyaml
from packageurl import PackageURL

from packagedcode import models

"""
Handle conanfile recipes for conan packages
https://docs.conan.io/2/reference/conanfile.html
"""


SCANCODE_DEBUG_PACKAGE = os.environ.get("SCANCODE_DEBUG_PACKAGE", False)

TRACE = SCANCODE_DEBUG_PACKAGE


def logger_debug(*args):
    pass


logger = logging.getLogger(__name__)

if TRACE:
    import sys

    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(" ".join(isinstance(a, str) and a or repr(a) for a in args))


class ConanFileParser(ast.NodeVisitor):
    def __init__(self):
        self.name = None
        self.version = None
        self.description = None
        self.author = None
        self.homepage_url = None
        self.vcs_url = None
        self.license = []
        self.keywords = []
        self.requires = []

    def to_dict(self):
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "homepage_url": self.homepage_url,
            "vcs_url": self.vcs_url,
            "license": self.license,
            "keywords": self.keywords,
            "requires": self.requires,
        }

    def visit_Assign(self, node):
        if not node.targets or not isinstance(node.targets[0], ast.Name):
            return
        if not node.value or not (
            isinstance(node.value, ast.Constant) or isinstance(node.value, ast.Tuple)
        ):
            return

        attribute_mapping = {
            "name": "name",
            "version": "version",
            "description": "description",
            "author": "author",
            "homepage": "homepage_url",
            "url": "vcs_url",
            "license": "license",
            "topics": "keywords",
            "requires": "requires",
        }
        variable_name = node.targets[0].id
        values = node.value

        if variable_name in attribute_mapping:
            attribute_name = attribute_mapping[variable_name]
            if variable_name in ("topics", "requires", "license"):
                current_list = getattr(self, attribute_name)
                if isinstance(values, ast.Tuple):
                    current_list.extend(
                        [el.value for el in values.elts if isinstance(el, ast.Constant)]
                    )
                elif isinstance(values, ast.Constant):
                    current_list.append(values.value)
                setattr(self, attribute_name, current_list)
            else:
                setattr(self, attribute_name, values.value)

    def visit_Call(self, node):
        if not isinstance(node.func, ast.Attribute) or not isinstance(
            node.func.value, ast.Name
        ):
            return
        if node.func.value.id == "self" and node.func.attr == "requires":
            if node.args and isinstance(node.args[0], ast.Constant):
                self.requires.append(node.args[0].value)


class ConanFileHandler(models.DatafileHandler):
    datasource_id = "conan_conanfile_py"
    path_patterns = ("*/conanfile.py",)
    default_package_type = "conan"
    default_primary_language = "C++"
    description = "conan recipe"
    documentation_url = "https://docs.conan.io/2.0/reference/conanfile.html"

    @classmethod
    def _parse(cls, conan_recipe, package_only=False):
        try:
            tree = ast.parse(conan_recipe)
            recipe_class_def = next(
                (
                    node
                    for node in tree.body
                    if isinstance(node, ast.ClassDef)
                    and node.bases
                    and isinstance(node.bases[0], ast.Name)
                    and node.bases[0].id == "ConanFile"
                ),
                None,
            )

            parser = ConanFileParser()
            parser.visit(recipe_class_def)
        except SyntaxError as e:
            if TRACE:
                logger_debug(f"Syntax error in conan recipe: {e}")
            return

        if TRACE:
            logger_debug(f"ConanFileHandler: parse: package: {parser.to_dict()}")

        dependencies = get_dependencies(parser.requires)

        package_data = dict(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            primary_language=cls.default_primary_language,
            namespace=None,
            name=parser.name,
            version=parser.version,
            description=parser.description,
            homepage_url=parser.homepage_url,
            keywords=parser.keywords,
            extracted_license_statement=parser.license,
            dependencies=dependencies,
        )
        return models.PackageData.from_data(package_data, package_only)

    @classmethod
    def parse(cls, location, package_only=False):
        with io.open(location, encoding="utf-8") as loc:
            conan_recipe = loc.read()

        yield cls._parse(conan_recipe, package_only)


class ConanDataHandler(models.DatafileHandler):
    datasource_id = "conan_conandata_yml"
    path_patterns = ("*/conandata.yml",)
    default_package_type = "conan"
    default_primary_language = "C++"
    description = "conan external source"
    documentation_url = (
        "https://docs.conan.io/2/tutorial/creating_packages/"
        "handle_sources_in_packages.html#using-the-conandata-yml-file"
    )

    @classmethod
    def parse(cls, location, package_only=False):
        with io.open(location, encoding="utf-8") as loc:
            conan_data = loc.read()

        conan_data = saneyaml.load(conan_data)
        sources = conan_data.get("sources", {})

        for version, source in sources.items():
            sha256 = source.get("sha256", None)
            source_urls = source.get("url")
            if not source_urls:
                continue
            
            url = None
            if isinstance(source_urls, str):
                url = source_urls
            elif isinstance(source_urls, list):
                url = source_urls[0]

            package_data = dict(
                datasource_id=cls.datasource_id,
                type=cls.default_package_type,
                primary_language=cls.default_primary_language,
                namespace=None,
                version=version,
                download_url=url,
                sha256=sha256,
            )
            yield models.PackageData.from_data(package_data, package_only)
            

    @classmethod
    def assemble(
        cls, package_data, resource, codebase, package_adder=models.add_to_package
    ):
        """
        `conandata.yml` only contains the `version` and `download_url` use the conanfile.py
        to enhance the package metadata.
        """
        siblings = resource.siblings(codebase)
        conanfile_package_resource = [r for r in siblings if r.name == "conanfile.py"]
        package_data_dict = package_data.to_dict()

        if conanfile_package_resource:
            conanfile_package_resource = conanfile_package_resource[0]

            conanfile_package_data = conanfile_package_resource.package_data
            if conanfile_package_data:
                conanfile_package_data = conanfile_package_data[0]

                package_data_dict["name"] = conanfile_package_data.get("name")
                package_data_dict["description"] = conanfile_package_data.get(
                    "description"
                )
                package_data_dict["homepage_url"] = conanfile_package_data.get(
                    "homepage_url"
                )
                package_data_dict["keywords"] = conanfile_package_data.get("keywords")
                package_data_dict[
                    "extracted_license_statement"
                ] = conanfile_package_data.get("extracted_license_statement")

        datafile_path = resource.path
        pkg_data = models.PackageData.from_data(package_data_dict)

        if pkg_data.purl:
            package = models.Package.from_package_data(
                package_data=pkg_data,
                datafile_path=datafile_path,
            )
            package.datafile_paths.append(conanfile_package_resource.path)
            package.datasource_ids.append(ConanFileHandler.datasource_id)

            package.populate_license_fields()
            yield package

            cls.assign_package_to_resources(
                package=package,
                resource=resource,
                codebase=codebase,
                package_adder=package_adder,
            )
        yield resource


def is_constraint_resolved(constraint):
    """
    Checks if a constraint is resolved and it specifies an exact version.
    """
    range_characters = {">", "<", "[", "]", ">=", "<="}
    return not any(char in range_characters for char in constraint)


def get_dependencies(requires):
    dependent_packages = []
    for req in requires:
        name, constraint = req.split("/", 1)
        is_resolved = is_constraint_resolved(constraint)
        version = None
        if is_resolved:
            version = constraint
        purl = PackageURL(type="conan", name=name, version=version)
        dependent_packages.append(
            models.DependentPackage(
                purl=purl.to_string(),
                scope="install",
                is_runtime=True,
                is_optional=False,
                is_resolved=is_resolved,
                extracted_requirement=constraint,
            )
        )
    return dependent_packages
