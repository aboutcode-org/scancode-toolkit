#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/skeleton for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
import re
import subprocess

"""
Utilities to manage requirements files and call pip.
NOTE: this should use ONLY the standard library and not import anything else
because this is used for boostrapping with no requirements installed.
"""


def load_requirements(requirements_file="requirements.txt", with_unpinned=False):
    """
    Yield package (name, version) tuples for each requirement in a `requirement`
    file. Only accept requirements pinned to an exact version.
    """
    with open(requirements_file) as reqs:
        req_lines = reqs.read().splitlines(False)
    return get_required_name_versions(req_lines, with_unpinned=with_unpinned)


def get_required_name_versions(requirement_lines, with_unpinned=False):
    """
    Yield required (name, version) tuples given a`requirement_lines` iterable of
    requirement text lines. Only accept requirements pinned to an exact version.
    """

    for req_line in requirement_lines:
        req_line = req_line.strip()
        if not req_line or req_line.startswith("#"):
            continue
        if req_line.startswith("-") or (not with_unpinned and not "==" in req_line):
            print(f"Requirement line is not supported: ignored: {req_line}")
            continue
        yield get_required_name_version(requirement=req_line, with_unpinned=with_unpinned)


def get_required_name_version(requirement, with_unpinned=False):
    """
    Return a (name, version) tuple given a`requirement` specifier string.
    Requirement version must be pinned. If ``with_unpinned`` is True, unpinned
    requirements are accepted and only the name portion is returned.

    For example:
    >>> assert get_required_name_version("foo==1.2.3") == ("foo", "1.2.3")
    >>> assert get_required_name_version("fooA==1.2.3.DEV1") == ("fooa", "1.2.3.dev1")
    >>> assert get_required_name_version("foo==1.2.3", with_unpinned=False) == ("foo", "1.2.3")
    >>> assert get_required_name_version("foo", with_unpinned=True) == ("foo", "")
    >>> assert get_required_name_version("foo>=1.2", with_unpinned=True) == ("foo", ""), get_required_name_version("foo>=1.2")
    >>> try:
    ...   assert not get_required_name_version("foo", with_unpinned=False)
    ... except Exception as e:
    ...   assert "Requirement version must be pinned" in str(e)
    """
    requirement = requirement and "".join(requirement.lower().split())
    assert requirement, f"specifier is required is empty:{requirement!r}"
    name, operator, version = split_req(requirement)
    assert name, f"Name is required: {requirement}"
    is_pinned = operator == "=="
    if with_unpinned:
        version = ""
    else:
        assert is_pinned and version, f"Requirement version must be pinned: {requirement}"
    return name, version


def lock_requirements(requirements_file="requirements.txt", site_packages_dir=None):
    """
    Freeze and lock current installed requirements and save this to the
    `requirements_file` requirements file.
    """
    with open(requirements_file, "w") as fo:
        fo.write(get_installed_reqs(site_packages_dir=site_packages_dir))


def lock_dev_requirements(
    dev_requirements_file="requirements-dev.txt",
    main_requirements_file="requirements.txt",
    site_packages_dir=None,
):
    """
    Freeze and lock current installed development-only requirements and save
    this to the `dev_requirements_file` requirements file. Development-only is
    achieved by subtracting requirements from the `main_requirements_file`
    requirements file from the current requirements using package names (and
    ignoring versions).
    """
    main_names = {n for n, _v in load_requirements(main_requirements_file)}
    all_reqs = get_installed_reqs(site_packages_dir=site_packages_dir)
    all_req_lines = all_reqs.splitlines(False)
    all_req_nvs = get_required_name_versions(all_req_lines)
    dev_only_req_nvs = {n: v for n, v in all_req_nvs if n not in main_names}

    new_reqs = "\n".join(f"{n}=={v}" for n, v in sorted(dev_only_req_nvs.items()))
    with open(dev_requirements_file, "w") as fo:
        fo.write(new_reqs)


def get_installed_reqs(site_packages_dir):
    """
    Return the installed pip requirements as text found in `site_packages_dir`
    as a text.
    """
    if not os.path.exists(site_packages_dir):
        raise Exception(f"site_packages directory: {site_packages_dir!r} does not exists")
    # Also include these packages in the output with --all: wheel, distribute,
    # setuptools, pip
    args = ["pip", "freeze", "--exclude-editable", "--all", "--path", site_packages_dir]
    return subprocess.check_output(args, encoding="utf-8")


comparators = (
    "===",
    "~=",
    "!=",
    "==",
    "<=",
    ">=",
    ">",
    "<",
)

_comparators_re = r"|".join(comparators)
version_splitter = re.compile(rf"({_comparators_re})")


def split_req(req):
    """
    Return a three-tuple of (name, comparator, version) given a ``req``
    requirement specifier string. Each segment may be empty. Spaces are removed.

    For example:
    >>> assert split_req("foo==1.2.3") == ("foo", "==", "1.2.3"), split_req("foo==1.2.3")
    >>> assert split_req("foo") == ("foo", "", ""), split_req("foo")
    >>> assert split_req("==1.2.3") == ("", "==", "1.2.3"), split_req("==1.2.3")
    >>> assert split_req("foo >= 1.2.3 ") == ("foo", ">=", "1.2.3"), split_req("foo >= 1.2.3 ")
    >>> assert split_req("foo>=1.2") == ("foo", ">=", "1.2"), split_req("foo>=1.2")
    """
    assert req
    # do not allow multiple constraints and tags
    assert not any(c in req for c in ",;")
    req = "".join(req.split())
    if not any(c in req for c in comparators):
        return req, "", ""
    segments = version_splitter.split(req, maxsplit=1)
    return tuple(segments)
