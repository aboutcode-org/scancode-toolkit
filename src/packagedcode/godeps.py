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

from commoncode import datautils

from packagedcode import models
import attr
from packageurl import PackageURL

"""
Handle Godeps-like Go package dependency data.

Note: there are other dependency tools for Go beside Godeps, yet several use the
same format. Godeps (and glide, etc.) is mostly legacy today and replaced by Go
modules.
"""
# FIXME: update to use the latest vendor conventions.
# consider other legacy format?
# https://github.com/golang/dep/blob/master/Gopkg.lock
# https://github.com/golang/dep/blob/master/Gopkg.toml


class GodepsHandler(models.NonAssemblableDatafileHandler):
    datasource_id = 'godeps'
    default_package_type = 'golang'
    default_primary_language = 'Go'
    path_patterns = ('*/Godeps.json',)
    description = 'Go Godeps'
    documentation_url = 'https://github.com/tools/godep'

    @classmethod
    def parse(cls, location):
        godeps = Godep(location)

        if godeps.import_path:
            # we create a purl from the import path to parse ns/name nicely
            purl = PackageURL.from_string(f'pkg:golang/{godeps.import_path}')
            namespace = purl.namespace
            name = purl.name
        else:
            namespace = None
            name = None

        dependencies = []
        deps = godeps.dependencies or []
        for dep in deps:
            dependencies.append(
                models.DependentPackage(
                    purl=str(PackageURL.from_string(f'pkg:golang/{dep.import_path}')),
                    extracted_requirement=dep.revision,
                    scope='Deps',
                    is_runtime=True,
                    is_optional=False,
                    is_resolved=False,
                )
            )

        yield models.PackageData(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            namespace=namespace,
            name=name,
            primary_language=cls.default_primary_language,
            dependencies=dependencies,
         )

    @classmethod
    def assign_package_to_resources(cls, package, resource, codebase, package_adder):
        models.DatafileHandler.assign_package_to_parent_tree(package, resource, codebase, package_adder)


@attr.s
class Dep:
    import_path = datautils.String()
    revision = datautils.String()
    comment = datautils.String()

    def to_dict(self):
        return attr.asdict(self)


# map of Godep names to our own attribute names
NAMES = {
    'ImportPath': 'import_path',
    'GoVersion': 'go_version',
    'Packages': 'packages',
    'Deps': 'dependencies',
    'Comment': 'comment',
    'Rev': 'revision',
}


@attr.s
class Godep:
    """
    Represent JSON dep file with this structure:
        type Godeps struct {
            ImportPath string
            GoVersion  string   // Abridged output of 'go version'.
            Packages   []string // Arguments to godep save, if any.
            Deps       []struct {
                ImportPath string
                Comment    string // Description of commit, if present.
                Rev        string // VCS-specific commit ID.
            }
        }

    ImportPath
    GoVersion
    Packages
    Deps
        ImportPath
        Comment
        Rev
    """
    location = datautils.String()
    import_path = datautils.String()
    go_version = datautils.String()
    packages = datautils.List(item_type=str)
    dependencies = datautils.List(item_type=Dep)

    def __attrs_post_init__(self, *args, **kwargs):
        if self.location:
            self.load(self.location)

    def load(self, location):
        """
        Load self from a location string or a file-like object containing a
        Godeps JSON.
        """
        with io.open(location, encoding='utf-8') as godep:
            text = godep.read()
        return self.loads(text)

    def loads(self, text):
        """
        Load a Godeps JSON text.
        """
        data = json.loads(text)

        for key, value in data.items():
            name = NAMES.get(key)
            if name == 'dependencies':
                self.dependencies = self.parse_deps(value)
            else:
                setattr(self, name, value)
        return self

    def parse_deps(self, deps):
        """
        Return a list of Dep from a ``deps`` list of dependency mappings.
        """
        deps_list = []
        for dep in deps:
            data = dict((NAMES[key], value) for key, value in dep.items())
            deps_list.append(Dep(**data))
        return deps_list or []

    def to_dict(self):
        return {
            'import_path': self.import_path,
            'go_version': self.go_version,
            'packages': self.packages,
            'dependencies': [d.to_dict() for d in self.dependencies],
        }


def parse(location):
    """
    Return a mapping of parsed Godeps from the file at `location`.
    """
    return Godep(location).to_dict()
