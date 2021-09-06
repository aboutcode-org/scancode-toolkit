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

from commoncode.testcase import FileDrivenTesting
from scancode.cli_test_utils import run_scan_click
from formattedcode.output_cyclonedx import get_hashes_list, _get_set_of_known_licenses_and_spdx_license_ids

test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


def test_cyclonedx_xml():
    pass


def test_can_load_spdx_ids():
    licenses, spdx_keys = _get_set_of_known_licenses_and_spdx_license_ids()
    assert len(spdx_keys) > 0


def test_can_get_hashes_from_package():
    package = {
        "md5": "cc5ea2445954a282f622042252a6eef9",
        "sha1": "b754cee9a3d3501d32ae200e07f4e518cd8294b8",
        "sha256": "4795dae6518d60e4e5bd7103f50f5f86f8c07cbdc36aa76f410a0d534edc8ec5",
        "sha512": "f385a335b20e0bd933b3d59abc41e9b05f4333db6cd948b579b2562" +
                  "d617a6fa35e13ffa0c2eceae031afcf73c5fb7e1660fade207ddf2a0e312e006eb115e9b0"}
    hashes = get_hashes_list(package=package)
    assert len(hashes) == 4
    for hash_entry in hashes:
        assert hash_entry.content is not None


def test_cyclonedx_json():
    test_dir = test_env.get_test_loc('json/simple')
    result_file = test_env.get_temp_file('cyclonedx')
    args = ['-p', test_dir, '--cyclonedx-json', result_file]
    run_scan_click(args)
