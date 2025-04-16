#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/aboutcode-org/skeleton for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#
import argparse
import pathlib

import utils_requirements

"""
Utilities to manage requirements files.
NOTE: this should use ONLY the standard library and not import anything else
because this is used for boostrapping with no requirements installed.
"""


def gen_requirements():
    description = """
    Create or replace the `--requirements-file` file FILE requirements file with all
    locally installed Python packages.all Python packages found installed in `--site-packages-dir`
    """
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        "-s",
        "--site-packages-dir",
        dest="site_packages_dir",
        type=pathlib.Path,
        required=True,
        metavar="DIR",
        help="Path to the 'site-packages' directory where wheels are installed such as lib/python3.6/site-packages",
    )
    parser.add_argument(
        "-r",
        "--requirements-file",
        type=pathlib.Path,
        metavar="FILE",
        default="requirements.txt",
        help="Path to the requirements file to update or create.",
    )

    args = parser.parse_args()

    utils_requirements.lock_requirements(
        site_packages_dir=args.site_packages_dir,
        requirements_file=args.requirements_file,
    )


if __name__ == "__main__":
    gen_requirements()
