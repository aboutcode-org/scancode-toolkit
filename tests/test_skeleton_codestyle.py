#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/skeleton for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import subprocess
import unittest
import configparser


class BaseTests(unittest.TestCase):
    def test_skeleton_codestyle(self):
        """
        This test shouldn't run in proliferated repositories.
        """
        setup_cfg = configparser.ConfigParser()
        setup_cfg.read("setup.cfg")
        if setup_cfg["metadata"]["name"] != "skeleton":
            return

        args = "venv/bin/black --check -l 100 setup.py etc tests"
        try:
            subprocess.check_output(args.split())
        except subprocess.CalledProcessError as e:
            print("===========================================================")
            print(e.output)
            print("===========================================================")
            raise Exception(
                "Black style check failed; please format the code using:\n"
                "  python -m black -l 100 setup.py etc tests",
                e.output,
            ) from e
