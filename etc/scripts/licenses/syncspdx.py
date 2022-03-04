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
import synclic

"""
Update DejaCode licenses SPDX ids with the ScanCode licenses SPDX ids.
Run python syncspdx.py -h for help.
"""

TRACE = True


@click.command()
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Do not perform actual updates.",
)
@click.option("-t", "--trace", is_flag=True, default=False, help="Print execution trace.")
@click.help_option("-h", "--help")
def cli(
    dry_run,
    trace,
):
    """
    Update DejaCode SPDX ids with ScanCode ids.

    The ScanCode licenses are collected from the current installation.

    When using the dejacode source your need to set the 'DEJACODE_API_URL' and
    'DEJACODE_API_KEY' environment variables with your credentials.
    """
    global TRACE
    TRACE = trace

    deja = synclic.DejaSource()
    scancode_licenses = synclic.ScanCodeLicenses()
    sc_by_key = scancode_licenses.by_key

    for license_key, spdx_license_key, api_url in deja.fetch_spdx_license_details(
        scancode_licenses
    ):
        if spdx_license_key:
            continue
        if TRACE or dry_run:
            print(f"Processing DejaCode  key: {license_key}, SPDX: {spdx_license_key}")

        sc_license = sc_by_key.get(license_key)
        if not sc_license:
            print(f"   Not a ScanCode key: {license_key}")
            # FIXME: should we always create an SPDX?
            continue

        spdx_license_key = sc_license.spdx_license_key
        if not spdx_license_key:
            print(f"   ScanCode has no spdx_license_key: {license_key} , {spdx_license_key}")
            # FIXME: should we always create an SPDX?
            continue

        if not dry_run:
            print(f"   Updating DejaCode key: {license_key} with SPDX: {spdx_license_key}")
            deja.patch_spdx_license(api_url, license_key, spdx_license_key)


if __name__ == "__main__":
    cli()
