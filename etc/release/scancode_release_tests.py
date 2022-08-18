#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
import shutil
import subprocess
import sys

on_windows = "win32" in str(sys.platform).lower()


def run_app_smoke_tests(app_archive):
    """
    Run basic "smoke" scancode tests for the app release archive `app_archive`
    """
    # Extract app archive which has this namin pattern:
    # scancode-toolki-21.1.21_py36-linux.tar.xz
    # or scancode-toolkit-21.1.21_py36-windows.zip
    # We split the name on "_" to extract the laft hand side which is name of
    # the root directory inside the archive e.g. "scancode-toolkit-21.1.21"
    # where the archive gest extracted

    _base, _, fn = app_archive.partition("/")
    extract_dir, _, _py_ver_ext = fn.partition("_")
    print("run_app_smoke_tests: cwd:", os.getcwd())
    print("run_app_smoke_tests:", "extracting archive:", app_archive, "to:", extract_dir)
    shutil.unpack_archive(app_archive)

    extract_loc = os.path.normpath(os.path.abspath(os.path.expanduser(extract_dir)))
#     print("run_app_smoke_tests: extract_loc:", extract_loc)
#     for f in os.listdir(extract_loc):
#         print("  ", f)
#     print()

    os.chdir(extract_loc)

    with open("some.file", "w") as sf:
        sf.write("license: gpl-2.0")

    print(f"Configuring scancode for release: {app_archive}")
    cpath = os.path.join(extract_loc, "configure")

    run_command([cpath])

    # minimal tests: update when new scans are available
    scpath = os.path.join(extract_loc, "scancode")

    args = [
        scpath,
        "--license",
        "--license-text",
        "--license-clarity-score",

        "--copyright",
        "--info",
        "--email",
        "--url",
        "--generated",

        "--package",
        "--system-package",

        "--summary",
        "--tallies",
        "--classify",
        "--consolidate",

        "--verbose",

        "--yaml", "test_scan.yml",
        "--json", "test_scan.json",
        "--json-lines", "test_scan.json-lines",
        "--csv", "test_scan.csv",
        "--html", "test_scan.html",
        "--cyclonedx", "test_scan.cdx",
        "--cyclonedx-xml", "test_scan.cdx.xml",
        "--spdx-tv", "test_scan.spdx",
        "--spdx-rdf", "test_scan.rdf.spdx",

        "--debian", "test_scan.debian.copyright",
        "--json-pp", "-",
        "some.file"
    ]

    print(f"Testing scancode release: {app_archive}")
    run_command(args)


def run_command(args):
    """
    Run a command list of `args` in a subprocess. Print the output. Exit on
    error.
    """
    cmd = " ".join(args)
    print()
    print(f"Running command: {cmd}")
    try:
        output = subprocess.check_output(args, encoding="utf-8", shell=on_windows)
        print(f"Success to run command: {cmd}")
        print(output)

    except subprocess.CalledProcessError as cpe:
        print(f"Failure to run command: {cmd}")
        print(cpe.output)
        sys.exit(128)


if __name__ == "__main__":
    args = sys.argv[1:]
    archive = args[0]
    run_app_smoke_tests(archive)
