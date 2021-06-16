#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: BSD-2-Clause-Views AND MIT
# Copyright (c) 2010 David Wolever <david@wolever.net>. All rights reserved.
# originally from https://github.com/wolever/pip2pi

import os
import re
import shutil

from html import escape
from pathlib import Path

"""
name: pip compatibility tags
version: 20.3.1
download_url: https://github.com/pypa/pip/blob/20.3.1/src/pip/_internal/models/wheel.py
copyright: Copyright (c) 2008-2020 The pip developers (see AUTHORS.txt file)
license_expression: mit
notes: the weel name regex is copied from pip-20.3.1 pip/_internal/models/wheel.py

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
    re.VERBOSE
).match

sdist_exts = ".tar.gz", ".tar.bz2", ".zip", ".tar.xz",
wheel_ext = ".whl"
app_ext = ".pyz"
dist_exts = sdist_exts + (wheel_ext, app_ext)


class InvalidDistributionFilename(Exception):
    pass


def get_package_name_from_filename(filename, normalize=True):
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

        name, _, version = name_ver.rpartition('-')

        if not (name and version):
            raise InvalidDistributionFilename(filename)

    elif filename.endswith(wheel_ext):

        wheel_info = get_wheel_from_filename(filename)

        if not wheel_info:
            raise InvalidDistributionFilename(filename)

        name = wheel_info.group('name')
        version = wheel_info.group('version')

        if not (name and version):
            raise InvalidDistributionFilename(filename)

    elif filename.endswith(app_ext):
        name_ver, extension, _ = filename.rpartition(".pyz")

        if "-" in filename:
            name, _, version = name_ver.rpartition('-')
        else:
            name = name_ver

        if not name:
            raise InvalidDistributionFilename(filename)

    if normalize:
        name = name.lower().replace('_', '-')
    return name


def build_pypi_index(directory, write_index=False):
    """
    Using a ``directory`` directory of wheels and sdists, create the a PyPI simple
    directory index at ``directory``/simple/ populated with the proper PyPI simple
    index directory structure crafted using symlinks.

    WARNING: The ``directory``/simple/ directory is removed if it exists.
    """

    directory = Path(directory)

    index_dir = directory / "simple"
    if index_dir.exists():
        shutil.rmtree(str(index_dir), ignore_errors=True)

    index_dir.mkdir(parents=True)

    if write_index:
        simple_html_index = [
            "<html><head><title>PyPI Simple Index</title>",
            "<meta name='api-version' value='2' /></head><body>",
        ]

    package_names = set()
    for pkg_file in directory.iterdir():

        pkg_filename = pkg_file.name

        if (
            not pkg_file.is_file()
            or not pkg_filename.endswith(dist_exts)
            or pkg_filename.startswith(".")
        ):
            continue

        pkg_name = get_package_name_from_filename(pkg_filename)
        pkg_index_dir = index_dir / pkg_name
        pkg_index_dir.mkdir(parents=True, exist_ok=True)
        pkg_indexed_file = pkg_index_dir / pkg_filename
        link_target = Path("../..") / pkg_filename
        pkg_indexed_file.symlink_to(link_target)

        if write_index and pkg_name not in package_names:
            esc_name = escape(pkg_name)
            simple_html_index.append(f'<a href="{esc_name}/">{esc_name}</a><br/>')
            package_names.add(pkg_name)

    if write_index:
        simple_html_index.append("</body></html>")
        index_html = index_dir / "index.html"
        index_html.write_text("\n".join(simple_html_index))


if __name__ == "__main__":
    import sys
    pkg_dir = sys.argv[1]
    build_pypi_index(pkg_dir)
