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
        self.license = None
        self.keywords = []
        self.requires = []
    
    def to_dict(self):
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'author':self.author,
            'homepage_url':self.homepage_url,
            'vcs_url':self.vcs_url,
            'license':self.license,
            'keywords':self.keywords,
            'requires':self.requires,
        }


    def visit_Assign(self, node):
        if not node.targets or not isinstance(node.targets[0], ast.Name):
            return
        if not node.value or not (isinstance(node.value, ast.Constant) or isinstance(node.value, ast.Tuple)):
            return
        variable_name = node.targets[0].id
        values = node.value
        if variable_name == "name":
            self.name = values.value
        elif variable_name == "version":
            self.version = values.value
        elif variable_name == "description":
            self.description = values.value
        elif variable_name == "author":
            self.author = values.value
        elif variable_name == "homepage":
            self.homepage_url = values.value
        elif variable_name == "url":
            self.vcs_url = values.value
        elif variable_name == "license":
            self.license = values.value
        elif variable_name == "topics":
            self.keywords.extend(
                [el.value for el in values.elts if isinstance(el, ast.Constant)]
            )
        elif variable_name == "requires":
            if isinstance(values, ast.Tuple):
                self.requires.extend(
                    [el.value for el in values.elts if isinstance(el, ast.Constant)]
                )
            elif isinstance(values, ast.Constant):
                self.requires.append(values.value)

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
    def parse(cls, location):
        with io.open(location, encoding="utf-8") as loc:
            conan_recipe = loc.read()

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

        yield models.PackageData(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            primary_language=cls.default_primary_language,
            namespace=None,
            name=parser.name,
            version=parser.version,
            description=parser.description,
            homepage_url=parser.homepage_url,
            vcs_url=parser.vcs_url,
            keywords=parser.keywords,
            declared_license_expression=parser.license,
            dependencies=dependencies,
        )

def is_constraint_resolved(constraint):
    range_characters = {'>', '<', '[', ']', '>=','<='}
    return not any(char in range_characters for char in constraint)

def get_dependencies(requires):
    dependent_packages=[]
    for req in requires:
        name, constraint = req.split('/', 1)
        is_resolved = is_constraint_resolved(constraint)
        purl = PackageURL(type='conan', name=name)
        dependent_packages.append(
            models.DependentPackage(
                purl=purl.to_string(),
                scope='install',
                is_runtime=True,
                is_optional=False,
                is_resolved=is_resolved,
                extracted_requirement=constraint
            )
        )
    return dependent_packages
