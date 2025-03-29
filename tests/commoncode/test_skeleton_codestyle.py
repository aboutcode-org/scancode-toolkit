#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/aboutcode-org/skeleton for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import configparser
import subprocess
import unittest

class BaseTests(unittest.TestCase):
    def test_skeleton_codestyle(self):
        # This test shouldn't run in proliferated repositories.

        # TODO: update with switch to pyproject.toml
        setup_cfg = configparser.ConfigParser()
        setup_cfg.read("setup.cfg")
        if setup_cfg["metadata"]["name"] != "skeleton":
            return

        commands = [
            ["venv/bin/ruff", "--check"],
            ["venv/bin/ruff", "format", "--check"],
        ]
        command = None
        try:
            for command in commands:
                subprocess.check_output(command)  # noqa: S603
        except subprocess.CalledProcessError as e:
            print("===========================================================")
            print(e.output)
            print("===========================================================")
            raise Exception(
                f"Code style and linting command check failed: {' '.join(command)!r}.\n"
                "You can check and format the code using:\n"
                "  make valid\n",
                "OR:\n  ruff format\n",
                "  ruff check --fix\n",
                e.output,
            ) from e
