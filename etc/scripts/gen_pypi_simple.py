#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: BSD-2-Clause-Views AND MIT
# Copyright (c) 2010 David Wolever <david@wolever.net>. All rights reserved.
# originally from https://github.com/wolever/pip2pi

import hashlib
import os
import re
import shutil
from collections import defaultdict
from html import escape
from pathlib import Path
from typing import NamedTuple

"""
Generate a PyPI simple index froma  directory.
"""


class InvalidDistributionFilename(Exception):
    pass


def get_package_name_from_filename(filename):
    """
    Return the package name extracted from a package ``filename``.
    Optionally ``normalize`` the name according to distribution name rules.
    Raise an ``InvalidDistributionFilename`` if the ``filename`` is invalid::

    >>> get_package_name_from_filename("foo-1.2.3_rc1.tar.gz")
    'foo'
    >>> get_package_name_from_filename("foo-bar-1.2-py27-none-any.whl")
    'foo-bar'
    >>> get_package_name_from_filename("Cython-0.17.2-cp26-none-linux_x86_64.whl")
    'cython'
    >>> get_package_name_from_filename("python_ldap-2.4.19-cp27-none-macosx_10_10_x86_64.whl")
    'python-ldap'
    >>> get_package_name_from_filename("foo.whl")
    Traceback (most recent call last):
        ...
    InvalidDistributionFilename: ...
    >>> get_package_name_from_filename("foo.png")
    Traceback (most recent call last):
        ...
    InvalidFilePackageName: ...
    """
    if not filename or not filename.endswith(dist_exts):
        raise InvalidDistributionFilename(filename)

    filename = os.path.basename(filename)

    if filename.endswith(sdist_exts):
        name_ver = None
        extension = None

        for ext in sdist_exts:
            if filename.endswith(ext):
                name_ver, extension, _ = filename.rpartition(ext)
                break

        if not extension or not name_ver:
            raise InvalidDistributionFilename(filename)

        name, _, version = name_ver.rpartition("-")

        if not (name and version):
            raise InvalidDistributionFilename(filename)

    elif filename.endswith(wheel_ext):

        wheel_info = get_wheel_from_filename(filename)

        if not wheel_info:
            raise InvalidDistributionFilename(filename)

        name = wheel_info.group("name")
        version = wheel_info.group("version")

        if not (name and version):
            raise InvalidDistributionFilename(filename)

    elif filename.endswith(app_ext):
        name_ver, extension, _ = filename.rpartition(".pyz")

        if "-" in filename:
            name, _, version = name_ver.rpartition("-")
        else:
            name = name_ver

        if not name:
            raise InvalidDistributionFilename(filename)

    name = normalize_name(name)
    return name


def normalize_name(name):
    """
    Return a normalized package name per PEP503, and copied from
    https://www.python.org/dev/peps/pep-0503/#id4
    """
    return name and re.sub(r"[-_.]+", "-", name).lower() or name


def build_per_package_index(pkg_name, packages, base_url):
    """
    Return an HTML document as string representing the index for a package
    """
    document = []
    header = f"""<!DOCTYPE html>
<html>
  <head>
    <meta name="pypi:repository-version" content="1.0">
    <title>Links for {pkg_name}</title>
  </head>
  <body>"""
    document.append(header)

    for package in packages:
        document.append(package.simple_index_entry(base_url))

    footer = """  </body>
</html>
"""
    document.append(footer)
    return "\n".join(document)


def build_links_package_index(packages_by_package_name, base_url):
    """
    Return an HTML document as string which is a links index of all packages
    """
    document = []
    header = f"""<!DOCTYPE html>
<html>
  <head>
    <title>Links for all packages</title>
  </head>
  <body>"""
    document.append(header)

    for _name, packages in packages_by_package_name.items():
        for package in packages:
            document.append(package.simple_index_entry(base_url))

    footer = """  </body>
</html>
"""
    document.append(footer)
    return "\n".join(document)


class Package(NamedTuple):
    name: str
    index_dir: Path
    archive_file: Path
    checksum: str

    @classmethod
    def from_file(cls, name, index_dir, archive_file):
        with open(archive_file, "rb") as f:
            checksum = hashlib.sha256(f.read()).hexdigest()
        return cls(
            name=name,
            index_dir=index_dir,
            archive_file=archive_file,
            checksum=checksum,
        )

    def simple_index_entry(self, base_url):
        return (
            f'    <a href="{base_url}/{self.archive_file.name}#sha256={self.checksum}">'
            f"{self.archive_file.name}</a><br/>"
        )


def build_pypi_index(directory, base_url="https://thirdparty.aboutcode.org/pypi"):
    """
    Using a ``directory`` directory of wheels and sdists, create the a PyPI
    simple directory index at ``directory``/simple/ populated with the proper
    PyPI simple index directory structure crafted using symlinks.

    WARNING: The ``directory``/simple/ directory is removed if it exists.
    NOTE: in addition to the a PyPI simple index.html there is also a links.html
    index file generated which is suitable to use with pip's --find-links
    """

    directory = Path(directory)

    index_dir = directory / "simple"
    if index_dir.exists():
        shutil.rmtree(str(index_dir), ignore_errors=True)

    index_dir.mkdir(parents=True)
    packages_by_package_name = defaultdict(list)

    # generate the main simple index.html
    simple_html_index = [
        "<!DOCTYPE html>",
        "<html><head><title>PyPI Simple Index</title>",
        '<meta charset="UTF-8">' '<meta name="api-version" value="2" /></head><body>',
    ]

    for pkg_file in directory.iterdir():

        pkg_filename = pkg_file.name

        if (
            not pkg_file.is_file()
            or not pkg_filename.endswith(dist_exts)
            or pkg_filename.startswith(".")
        ):
            continue

        pkg_name = get_package_name_from_filename(
            filename=pkg_filename,
        )
        pkg_index_dir = index_dir / pkg_name
        pkg_index_dir.mkdir(parents=True, exist_ok=True)
        pkg_indexed_file = pkg_index_dir / pkg_filename

        link_target = Path("../..") / pkg_filename
        pkg_indexed_file.symlink_to(link_target)

        if pkg_name not in packages_by_package_name:
            esc_name = escape(pkg_name)
            simple_html_index.append(f'<a href="{esc_name}/">{esc_name}</a><br/>')

        packages_by_package_name[pkg_name].append(
            Package.from_file(
                name=pkg_name,
                index_dir=pkg_index_dir,
                archive_file=pkg_file,
            )
        )

    # finalize main index
    simple_html_index.append("</body></html>")
    index_html = index_dir / "index.html"
    index_html.write_text("\n".join(simple_html_index))

    # also generate the simple index.html of each package, listing all its versions.
    for pkg_name, packages in packages_by_package_name.items():
        per_package_index = build_per_package_index(
            pkg_name=pkg_name,
            packages=packages,
            base_url=base_url,
        )
        pkg_index_dir = packages[0].index_dir
        ppi_html = pkg_index_dir / "index.html"
        ppi_html.write_text(per_package_index)

    # also generate the a links.html page with all packages.
    package_links = build_links_package_index(
        packages_by_package_name=packages_by_package_name,
        base_url=base_url,
    )
    links_html = index_dir / "links.html"
    links_html.write_text(package_links)


"""
name: pip-wheel
version: 20.3.1
download_url: https://github.com/pypa/pip/blob/20.3.1/src/pip/_internal/models/wheel.py
copyright: Copyright (c) 2008-2020 The pip developers (see AUTHORS.txt file)
license_expression: mit
notes: the wheel name regex is copied from pip-20.3.1 pip/_internal/models/wheel.py

Copyright (c) 2008-2020 The pip developers (see AUTHORS.txt file)

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
get_wheel_from_filename = re.compile(
    r"""^(?P<namever>(?P<name>.+?)-(?P<version>.*?))
    ((-(?P<build>\d[^-]*?))?-(?P<pyvers>.+?)-(?P<abis>.+?)-(?P<plats>.+?)
    \.whl)$""",
    re.VERBOSE,
).match

sdist_exts = (
    ".tar.gz",
    ".tar.bz2",
    ".zip",
    ".tar.xz",
)

wheel_ext = ".whl"
app_ext = ".pyz"
dist_exts = sdist_exts + (wheel_ext, app_ext)

if __name__ == "__main__":
    import sys

    pkg_dir = sys.argv[1]
    build_pypi_index(pkg_dir)
