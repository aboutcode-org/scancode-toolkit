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
import click

import utils_thirdparty


@click.command()
@click.option(
    "-d",
    "--dest_dir",
    type=click.Path(exists=True, readable=True, path_type=str, file_okay=False),
    required=True,
    help="Path to the thirdparty directory to check.",
)
@click.option(
    "-w",
    "--wheels",
    is_flag=True,
    help="Check missing wheels.",
)
@click.option(
    "-s",
    "--sdists",
    is_flag=True,
    help="Check missing source sdists tarballs.",
)
@click.help_option("-h", "--help")
def check_thirdparty_dir(
    dest_dir,
    wheels,
    sdists,
):
    """
    Check a thirdparty directory for problems and print these on screen.
    """
    # check for problems
    print(f"==> CHECK FOR PROBLEMS")
    utils_thirdparty.find_problems(
        dest_dir=dest_dir,
        report_missing_sources=sdists,
        report_missing_wheels=wheels,
    )


if __name__ == "__main__":
    check_thirdparty_dir()
