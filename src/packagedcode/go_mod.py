# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import io
import re

import attr
from packageurl import PackageURL


@attr.s()
class GoWorkspace(object):
    """
    Represents a parsed go.work file for a Go workspace.
    A workspace is a collection of multiple Go modules that can be edited together.
    See https://go.dev/ref/mod#go-work-files for details.
    """
    go_version = attr.ib(default=None)
    use = attr.ib(default=attr.Factory(list))
    require = attr.ib(default=attr.Factory(list))


@attr.s()
class GoModule(object):
    namespace = attr.ib(default=None)
    name = attr.ib(default=None)
    version = attr.ib(default=None)
    module = attr.ib(default=None)
    require = attr.ib(default=None)
    exclude = attr.ib(default=None)

    def purl(self, include_version=True):
        version = None
        if include_version:
            version = self.version
        return PackageURL(
                    type='golang',
                    namespace=self.namespace,
                    name=self.name,
                    version=version
                ).to_string()


# Regex expressions to parse different types of go.mod file dependency
parse_module = re.compile(
    r'(?P<type>[^\s]+)'
    r'(\s)+'
    r'(?P<ns_name>[^\s]+)'
    r'\s?'
    r'(?P<version>(.*))'
).match

parse_dep_link = re.compile(
    r'.*?'
    r'(?P<ns_name>[^\s]+)'
    r'\s+'
    r'(?P<version>(.*))'
).match


def preprocess(line):
    """
    Return line string after removing commented portion and excess spaces.
    """
    if "//" in line:
        line = line[:line.index('//')]
    line = line.strip()
    return line


def parse_gomod(location):
    """
    Return a dictionary containing all the important go.mod file data.

    Handle go.mod files from Go.
    See https://golang.org/ref/mod#go.mod-files for details

    For example:

        module example.com/my/thing

        go 1.12

        require example.com/other/thing v1.0.2
        require example.com/new/thing v2.3.4
        exclude example.com/old/thing v1.2.3
        require (
            example.com/new/thing v2.3.4
            example.com/old/thing v1.2.3
        )
        require (
            example.com/new/thing v2.3.4
            example.com/old/thing v1.2.3
        )

    Each module line is in the form
        require github.com/davecgh/go-spew v1.1.1
    or
        exclude github.com/davecgh/go-spew v1.1.1
    or
        module github.com/alecthomas/participle

    For example::

        >>> p = parse_module('module github.com/alecthomas/participle')
        >>> assert p.group('type') == ('module')
        >>> assert p.group('ns_name') == ('github.com/alecthomas/participle')

        >>> p = parse_module('require github.com/davecgh/go-spew v1.1.1')
        >>> assert p.group('type') == ('require')
        >>> assert p.group('ns_name') == ('github.com/davecgh/go-spew')
        >>> assert p.group('version') == ('v1.1.1')

    A line for require or exclude can be in the form:

        github.com/davecgh/go-spew v1.1.1

    For example::

        >>> p = parse_dep_link('github.com/davecgh/go-spew v1.1.1')
        >>> assert p.group('ns_name') == ('github.com/davecgh/go-spew')
        >>> assert p.group('version') == ('v1.1.1')
    """
    with io.open(location, encoding='utf-8', closefd=True) as data:
        lines = data.readlines()

    gomods = GoModule()
    require = []
    exclude = []

    for i, line in enumerate(lines):
        line = preprocess(line)

        if 'require' in line and '(' in line:
            for req in lines[i + 1:]:
                req = preprocess(req)
                if ')' in req:
                    break
                parsed_dep_link = parse_dep_link(req)
                ns_name = parsed_dep_link.group('ns_name')
                namespace, _, name = ns_name.rpartition('/')
                if parsed_dep_link:
                    require.append(GoModule(
                            namespace=namespace,
                            name=name,
                            version=parsed_dep_link.group('version')
                        )
                    )
            continue

        if 'exclude' in line and '(' in line:
            for exc in lines[i + 1:]:
                exc = preprocess(exc)
                if ')' in exc:
                    break
                parsed_dep_link = parse_dep_link(exc)
                ns_name = parsed_dep_link.group('ns_name')
                namespace, _, name = ns_name.rpartition('/')
                if parsed_dep_link:
                    exclude.append(GoModule(
                            namespace=namespace,
                            name=name,
                            version=parsed_dep_link.group('version')
                        )
                    )
            continue

        parsed_module_name = parse_module(line)
        if parsed_module_name:
            ns_name = parsed_module_name.group('ns_name')
            namespace, _, name = ns_name.rpartition('/')

        if 'module' in line:
            gomods.namespace = namespace
            gomods.name = name
            continue

        if 'require' in line:
            require.append(GoModule(
                    namespace=namespace,
                    name=name,
                    version=parsed_module_name.group('version')
                )
            )
            continue

        if 'exclude' in line:
            exclude.append(GoModule(
                    namespace=namespace,
                    name=name,
                    version=parsed_module_name.group('version')
                )
            )
            continue

    gomods.require = require
    gomods.exclude = exclude

    return gomods


# Regex expressions to parse go.sum file dependency
# dep example: github.com/BurntSushi/toml v0.3.1 h1:WXkYY....
get_dependency = re.compile(
    r'(?P<ns_name>[^\s]+)'
    r'\s+'
    r'(?P<version>[^\s]+)'
    r'\s+'
    r'h1:(?P<checksum>[^\s]*)'
).match


def parse_gosum(location):
    """
    Return a list of GoSum from parsing the go.sum file at `location`.

    Handles go.sum file from Go.

    See https://blog.golang.org/using-go-modules for details

    A go.sum file contains pinned Go modules checksums of two styles:

    For example::

    github.com/BurntSushi/toml v0.3.1 h1:WXkYYl6Yr3qBf1K79EBnL4mak0OimBfB0XUf9Vl28OQ=
    github.com/BurntSushi/toml v0.3.1/go.mod h1:xHWCNGjB5oqiDr8zfno3MHue2Ht5sIBksp03qcyfWMU=

    ... where the line with /go.mod is for a check of that go.mod file
    and the other line contains a dirhash for that path as documented as
    https://pkg.go.dev/golang.org/x/mod/sumdb/dirhash

    For example::

        >>> p = get_dependency('github.com/BurntSushi/toml v0.3.1 h1:WXkYYl6Yr3qBf1K79EBnL4mak0OimBfB0XUf9Vl28OQ=')
        >>> assert p.group('ns_name') == ('github.com/BurntSushi/toml')
        >>> assert p.group('version') == ('v0.3.1')
        >>> assert p.group('checksum') == ('WXkYYl6Yr3qBf1K79EBnL4mak0OimBfB0XUf9Vl28OQ=')
    """
    with io.open(location, encoding='utf-8', closefd=True) as data:
        lines = data.readlines()

    gosums = []

    for line in lines:
        line = line.replace('/go.mod', '')
        parsed_dep = get_dependency(line)

        ns_name = parsed_dep.group('ns_name')
        namespace, _, name = ns_name.rpartition('/')

        dep = GoModule(
                namespace=namespace,
                name=name,
                version=parsed_dep.group('version')
            )

        if dep in gosums:
            continue

        gosums.append(dep)

    return gosums


def parse_gowork(location):
    """
    Return a GoWorkspace parsed from a go.work file at ``location``.

    Handle go.work files from Go workspaces introduced in Go 1.18.
    See https://go.dev/ref/mod#go-work-files for details.

    A go.work file specifies a workspace containing multiple modules with:
    - ``go`` directive: Go version
    - ``use`` directives: paths to local modules in the workspace
    - ``require`` directives: external module requirements (like go.mod)

    For example::

        go 1.18

        use (
            ./mymodule
            ./tools
        )

        require (
            github.com/some/dep v1.2.3
        )
    """
    with io.open(location, encoding='utf-8', closefd=True) as data:
        lines = data.readlines()

    workspace = GoWorkspace()
    use_dirs = []
    require = []

    for i, line in enumerate(lines):
        line = preprocess(line)

        if not line:
            continue

        # Parse 'go <version>' directive
        if line.startswith('go '):
            workspace.go_version = line[3:].strip()
            continue

        # Parse multi-line 'use ( ... )' block
        if line == 'use (' or line.startswith('use ('):
            for use_line in lines[i + 1:]:
                use_line = preprocess(use_line)
                if ')' in use_line:
                    break
                if use_line:
                    use_dirs.append(use_line)
            continue

        # Parse inline 'use ./path'
        if line.startswith('use ') and '(' not in line:
            path = line[4:].strip()
            if path:
                use_dirs.append(path)
            continue

        # Parse multi-line 'require ( ... )' block
        if line == 'require (' or (line.startswith('require') and '(' in line):
            for req_line in lines[i + 1:]:
                req_line = preprocess(req_line)
                if ')' in req_line:
                    break
                if not req_line:
                    continue
                parsed_dep = parse_dep_link(req_line)
                if parsed_dep:
                    ns_name = parsed_dep.group('ns_name')
                    namespace, _, name = ns_name.rpartition('/')
                    version = parsed_dep.group('version')
                    require.append(GoModule(
                        namespace=namespace,
                        name=name,
                        version=version,
                    ))
            continue

        # Parse inline 'require module version'
        if line.startswith('require ') and '(' not in line:
            parsed = parse_module(line)
            if parsed:
                ns_name = parsed.group('ns_name')
                namespace, _, name = ns_name.rpartition('/')
                version = parsed.group('version').strip()
                require.append(GoModule(
                    namespace=namespace,
                    name=name,
                    version=version,
                ))
            continue

    workspace.use = use_dirs
    workspace.require = require
    return workspace
