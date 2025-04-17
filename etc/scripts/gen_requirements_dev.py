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


def gen_dev_requirements():
    description = """
    Create or overwrite the `--dev-requirements-file` pip requirements FILE with
    all Python packages found installed in `--site-packages-dir`. Exclude
    package names also listed in the --main-requirements-file pip requirements
    FILE (that are assume to the production requirements and therefore to always
    be present in addition to the development requirements).
    """
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        "-s",
        "--site-packages-dir",
        type=pathlib.Path,
        required=True,
        metavar="DIR",
        help='Path to the "site-packages" directory where wheels are installed such as lib/python3.6/site-packages',
    )
    parser.add_argument(
        "-d",
        "--dev-requirements-file",
        type=pathlib.Path,
        metavar="FILE",
        default="requirements-dev.txt",
        help="Path to the dev requirements file to update or create.",
    )
    parser.add_argument(
        "-r",
        "--main-requirements-file",
        type=pathlib.Path,
        default="requirements.txt",
        metavar="FILE",
        help="Path to the main requirements file. Its requirements will be excluded "
        "from the generated dev requirements.",
    )
    args = parser.parse_args()

    utils_requirements.lock_dev_requirements(
        dev_requirements_file=args.dev_requirements_file,
        main_requirements_file=args.main_requirements_file,
        site_packages_dir=args.site_packages_dir,
    )


if __name__ == "__main__":
    gen_dev_requirements()
