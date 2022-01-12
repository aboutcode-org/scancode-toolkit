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
import click

import utils_thirdparty


@click.command()
@click.option(
    "--remote-build-log-file",
    type=click.Path(readable=True),
    metavar="LOG-FILE",
    help="Path to a remote builds log file.",
)
@click.option(
    "-d",
    "--thirdparty-dir",
    type=click.Path(exists=True, readable=True, path_type=str, file_okay=False),
    metavar="DIR",
    default=utils_thirdparty.THIRDPARTY_DIR,
    show_default=True,
    help="Path to the thirdparty directory to save built wheels.",
)
@click.option(
    "--no-wait",
    is_flag=True,
    default=False,
    help="Do not wait for build completion.",
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Provide verbose output.",
)
@click.help_option("-h", "--help")
def fetch_remote_wheels(
    remote_build_log_file,
    thirdparty_dir,
    no_wait,
    verbose,
):
    """
    Fetch to THIRDPARTY_DIR all the wheels built in the LOG-FILE JSON lines
    build log file.
    """
    utils_thirdparty.fetch_remotely_built_wheels(
        remote_build_log_file=remote_build_log_file,
        dest_dir=thirdparty_dir,
        no_wait=no_wait,
        verbose=verbose,
    )


if __name__ == "__main__":
    fetch_remote_wheels()
