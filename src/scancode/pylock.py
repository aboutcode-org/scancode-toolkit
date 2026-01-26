#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import tomli

def parse_pylock(location):
    """
    Parse a pylock.toml file and return its content.
    """
    with open(location, "rb") as fp:
        data = tomli.load(fp)
    return data
